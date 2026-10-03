"""Fit predicate (spec section 7).

Geometric criteria are computed for every (head, assembly, pose). Criteria needing physical
evidence that does not exist yet are reported "unevaluated", so `validated_fit` can never
pass in this exploratory toolchain; `geometric_feasible` is the cheaper result the
optimiser uses.

Distances: inside a convex shell the distance to the boundary equals the minimum over all
tangent planes, and each plane is an upper bound. We take the minimum over the tangent
planes at the k nearest shell samples (KD-tree) and the nearest-sample distance. Signs come
from the implicit inside test. Discretisation bounds added to the allowances:
  * shell sampling: see `sampling_bound`
  * head sampling: clearance is smooth along the head surface, so its sampled minimum
    exceeds the true minimum by at most r^2 / (2 R_h), r = covering radius of the head
    samples, R_h = smallest head radius of curvature measured on the run's heads.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

from . import liner as liner_mod
from .heads import HeadSet, ZONES
from .shells import Crown, Lower, allowances, shell_samples

# failure bits
HARD, LOOSE, TIGHT, PADSTEP, UNPADDED, EAR, ASYM = 1, 2, 4, 8, 16, 32, 64
EYE, FOV, NOSE, CHIN, COVER = 128, 256, 512, 1024, 2048
SKIPPED = 4096   # pose not verified by the pose search (treated as not feasible)
BITS = {"hard_contact": HARD, "pad_too_loose": LOOSE, "pad_too_tight": TIGHT,
        "pad_between_steps": PADSTEP, "unpadded_gap": UNPADDED, "ear": EAR, "pad_asymmetry": ASYM,
        "eye_line": EYE, "field_of_view": FOV, "nose": NOSE, "chin": CHIN, "chin_coverage": COVER,
        "pose_not_searched": SKIPPED}

CRITERIA = {
    "C1_no_hard_contact": "geometric",
    "C2_liner_present": "geometric",
    "C3_pad_fill_preload": "geometric",           # pressure from unmeasured foam -> screening only
    "C3_stability_translation_rotation": "unevaluated",
    "C4_compression_reserve": "geometric",
    "C4_protective_stack_validated": "unevaluated",
    "C5_eye_line": "geometric",
    "C5_field_of_view_vertical": "geometric",
    "C5_field_of_view_full": "unevaluated",
    "C6_nose_chin_clearance": "geometric",
    "C6_jaw_cheek_lateral": "unevaluated",
    "C6_motion_range_coverage": "unevaluated",
    "C7_retention": "unevaluated",
    "C8_seam_projection": "geometric",
    "C8_attachments": "unevaluated",
}


def sampling_bound(heads: HeadSet, cfg: dict) -> float:
    """Shell term: the tangent-plane minimum over neighbouring samples exceeds the true
    distance by about d (h / 2R)^2 / 2 (d depth, h spacing, R radius); with d <= 60 mm,
    h = 5 mm and R >= 25 mm that is < 0.6 mm; measured against a 0.7 mm dense reference it
    is far smaller (tests/test_core.py::test_distance_accuracy). Head term: r^2 / (2 R_h)."""
    sh = cfg["shell"]
    h = sh["sample_spacing"]
    shell = 60.0 * (h / (2 * sh["min_curvature_radius"])) ** 2 / 2
    return shell + heads.sample_spacing_max ** 2 / (2 * heads.min_radius)


@dataclass
class CrownResult:
    ok: np.ndarray        # (n_pose, N) bool
    fail: np.ndarray      # (n_pose, N) int bitmask
    stacks: np.ndarray    # (n_pose, N, n_zone) int stack index (-1 = none)
    gaps: np.ndarray      # (n_pose, N, n_zone) effective gap (mm)
    minc: np.ndarray       # (n_pose, N) smallest effective clearance (upper bound if pruned)


class Evaluator:
    def __init__(self, heads: HeadSet, cfg: dict):
        self.heads, self.cfg = heads, cfg
        self.kd_workers = -1
        self.liner = cfg["liner"]
        self.table = liner_mod.StackTable.from_config(self.liner)
        self.window = liner_mod.gap_window(self.table, self.liner)
        self.bound = sampling_bound(heads, cfg)
        self.allow = allowances(cfg, self.bound)
        pc = cfg["pose"]
        self.poses = np.array([(dy, dz) for dy in pc["dy"] for dz in pc["dz"]], float)
        if any(p != 0 for p in pc.get("pitch", [0])):
            raise NotImplementedError("pitch poses need oriented landmarks; surrogate heads have none")
        zone_ids = [ZONES.index(z) for z in self.liner["zones"]]
        self.zone_cols = [np.flatnonzero(heads.zone == k) for k in zone_ids]
        self.unpadded_cols = np.flatnonzero(~np.isin(heads.zone, zone_ids))

    # ------------------------------------------------------------------ crown
    def _ray_filter(self, crown: Crown, H: HeadSet) -> np.ndarray:
        """Heads that might fit at some pose. Exact rule: the distance from a point to the
        shell along any ray is an upper bound on its distance to the shell. Five extreme
        head points (front, back, top, left, right of the max-length plane) must all clear by
        the smallest acceptable clearance; the sampled-minimum bound is added as slack."""
        t = H.table
        ze, zero = t.z_eq.to_numpy(), np.zeros(len(t))
        pts = [np.stack([zero, t.a_front, ze], -1), np.stack([zero, -t.a_rear, ze], -1),
               np.stack([zero, zero, ze + t.c_up], -1), np.stack([t.b, zero, ze], -1),
               np.stack([-t.b, zero, ze], -1)]
        dirs = np.array([[0, 1, 0], [0, -1, 0], [0, 0, 1], [1, 0, 0], [-1, 0, 0]], float)
        need = min(self.window[0], self.liner["unpadded_min_gap"]) + self.allow - self.bound - 1e-6
        ok_any = np.zeros(len(t), bool)
        for dy, dz in self.poses:
            off = np.array([0.0, dy, dz])
            ok = np.ones(len(t), bool)
            for p, u in zip(pts, dirs):
                q = p + off
                inside = crown.sq.implicit(q) < 1
                lo, hi = np.zeros(len(t)), np.full(len(t), 300.0)
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    out = crown.sq.implicit(q + mid[:, None] * u) >= 1
                    hi = np.where(out, mid, hi)
                    lo = np.where(out, lo, mid)
                ok &= inside & (hi >= need)
            ok_any |= ok
        return ok_any

    def crown(self, crown: Crown, idx: np.ndarray | None = None, prune: bool = True,
              _filtered: bool = False) -> CrownResult:
        """Evaluate one crown against every head at every pose.

        With prune=True: heads that cannot fit at any pose are removed by an exact ray test
        (`_ray_filter`); the rest are evaluated at every pose through a precomputed distance
        field, with exact re-evaluation of any (head, pose) near a decision threshold.
        `prune=False` evaluates every pose by direct KD queries (reference; used by tests)."""
        H = self.heads if idx is None else self.heads.subset(idx)
        if prune and not _filtered:
            cand = self._ray_filter(crown, H)
            if not cand.all():
                full = CrownResult(np.zeros((len(self.poses), len(H)), bool),
                                   np.full((len(self.poses), len(H)), TIGHT, np.int32),
                                   np.full((len(self.poses), len(H), len(self.zone_cols)), -1, np.int16),
                                   np.full((len(self.poses), len(H), len(self.zone_cols)), np.nan, np.float32),
                                   np.full((len(self.poses), len(H)), np.nan, np.float32))
                base = np.arange(len(H)) if idx is None else np.asarray(idx)
                if cand.any():
                    sub = self.crown(crown, base[cand], prune=True, _filtered=True)
                    for a, b in ((full.ok, sub.ok), (full.fail, sub.fail), (full.stacks, sub.stacks),
                                 (full.gaps, sub.gaps), (full.minc, sub.minc)):
                        a[:, cand] = b
                return full
        cfg, sh = self.cfg, self.cfg["shell"]
        samples = shell_samples(crown, cfg)
        tree = cKDTree(samples)
        normals = crown.sq.normal(samples)
        bead = sh["seam_bead_height"]
        N, P = H.points.shape[:2]
        nP, nZ = len(self.poses), len(self.zone_cols)
        fail = np.zeros((nP, N), np.int32)
        stacks = np.full((nP, N, nZ), -1, np.int16)
        gaps = np.full((nP, N, nZ), np.nan, np.float32)
        minc = np.full((nP, N), np.nan, np.float32)
        reg = H.region
        flat_pts = H.points[reg]
        lin = self.liner
        h = sh["sample_spacing"]
        beta = h * h / (2 * sh["min_curvature_radius"])

        kn = sh.get("plane_neighbours", 24)

        def clear(q):
            # Inside a convex body the distance to the boundary is the minimum over its
            # tangent planes (each one is an upper bound); outside, the distance is the
            # maximum over separating tangent planes (each a lower bound). Both are taken over
            # the planes at the k nearest samples, which makes the estimate smooth.
            out = np.empty(len(q))
            for s0 in range(0, len(q), 200_000):
                qq = q[s0:s0 + 200_000]
                d, j = tree.query(qq, k=kn, workers=self.kd_workers)
                plane = np.einsum("ikj,ikj->ik", samples[j] - qq[:, None, :], normals[j])
                inside = crown.sq.implicit(qq) < 1.0
                d_in = np.minimum(d[:, 0], np.abs(plane).min(1))
                d_out = np.clip((-plane).max(1), 0, None)
                out[s0:s0 + len(qq)] = np.where(inside, d_in, -d_out)
            return out

        # Seam: the ground weld bead is modelled as a strip |x| < halfwidth on the shell. It is
        # applied to head points in that strip (x does not change with the dy/dz pose).
        seam_pts = np.abs(H.points[..., 0]) < sh["seam_bead_halfwidth"]
        bead_grid = np.where(seam_pts, bead, 0.0)

        def grid(c, mask=reg, fill=np.inf):
            C = np.full((N, P), fill)
            C[mask] = c
            return C

        ear = H.landmarks["ears"].reshape(-1, 3)
        ear_allow = self.allow - cfg["head_model"]["hair_allowance"]

        def ear_bits(off):
            ce = clear(ear + off)
            return np.where(((ce - ear_allow).reshape(N, 2) < lin["ear_min_clearance"]).any(-1), EAR, 0)

        def exact(k, rows_mask, point_mask=None):
            """Exact evaluation of pose k for heads in rows_mask; point_mask (N, P) limits
            the query to points that can affect the outcome (others are left at +inf)."""
            off = np.array([0.0, *self.poses[k]])
            m = reg & rows_mask[:, None]
            if point_mask is not None:
                m &= point_mask
            c = clear(H.points[m] + off)
            C = np.full((N, P), np.inf)
            C[m] = c - bead_grid[m] - self.allow
            f, zg, sidx = self._pad_bits(C[rows_mask])
            fail[k, rows_mask] = f | ear_bits(off)[rows_mask]
            gaps[k, rows_mask] = zg
            stacks[k, rows_mask] = sidx
            minc[k, rows_mask] = C[rows_mask].min(axis=1)

        if not prune:
            for k in range(nP):
                exact(k, np.ones(N, bool))
            return CrownResult(fail == 0, fail, stacks, gaps, minc)

        # Distance field: exact (KD) values on a grid in the band where heads can lie,
        # trilinear lookup for every head point at every pose. Any (head, pose) whose
        # outcome is within eps of a decision threshold is re-evaluated exactly, so the
        # result equals the exact evaluation provided the interpolation error is < eps; that
        # error is measured on random points for every crown and eps is raised if needed.
        fld = self._field(crown, clear)
        eps = fld["eps"]
        g0 = lin["unpadded_min_gap"]
        for k in range(nP):
            off = np.array([0.0, *self.poses[k]])
            q = flat_pts + off
            c, valid = self._lookup(fld, q)
            if not valid.all():
                c[~valid] = clear(q[~valid])
            C = grid(c) - bead_grid - self.allow
            f, zg, sidx = self._pad_bits(C)
            fail[k] = f | ear_bits(off)
            gaps[k], stacks[k], minc[k] = zg, sidx, C.min(1)
            near = self._near_threshold(C, zg, eps)
            if near.any():
                # exact values only where they can matter: possible zone minima and
                # unpadded points that might be under the limit
                pm = np.zeros((N, P), bool)
                for z, cols in enumerate(self.zone_cols):
                    pm[:, cols] = C[:, cols] <= zg[:, z:z + 1] + 2 * eps
                pm[:, self.unpadded_cols] = C[:, self.unpadded_cols] < g0 + eps
                exact(k, near, pm)
        return CrownResult(fail == 0, fail, stacks, gaps, minc)

    def _field_mask(self, hstep: float):
        """Grid nodes needed for trilinear lookup of every head point at every pose: the
        voxels touched by any (head point + pose offset), with their 8 corner nodes. Shared
        by all crowns, so computed once."""
        if getattr(self, "_fmask", None) is not None and self._fmask[0] == hstep:
            return self._fmask[1:]
        pts = self.heads.points[self.heads.region]
        offs = np.c_[np.zeros(len(self.poses)), self.poses]
        lo = pts.min(0) + offs.min(0) - 2 * hstep
        hi = pts.max(0) + offs.max(0) + 2 * hstep
        shape = tuple(np.ceil((hi - lo) / hstep).astype(int) + 1)
        mask = np.zeros(shape, bool)
        for o in offs:
            cell = np.floor((pts + o - lo) / hstep).astype(int)
            for dx in (0, 1):
                for dy in (0, 1):
                    for dz in (0, 1):
                        mask[cell[:, 0] + dx, cell[:, 1] + dy, cell[:, 2] + dz] = True
        self._fmask = (hstep, lo, mask)
        return lo, mask

    def _field(self, crown: Crown, clear) -> dict:
        sh = self.cfg["shell"]
        hstep = sh.get("field_spacing", 2.0)
        lo, mask = self._field_mask(hstep)
        idx = np.argwhere(mask)
        nodes = lo + idx * hstep
        val = np.full(mask.shape, np.nan, np.float32)
        val[mask] = clear(nodes)
        fld = {"origin": lo, "h": hstep, "val": val}
        # measure interpolation error on random head points at random poses
        H = self.heads
        rng = np.random.default_rng(0)
        pts = H.points[H.region]
        sel = pts[rng.choice(len(pts), size=min(4000, len(pts)), replace=False)]
        offs = self.poses[rng.integers(0, len(self.poses), len(sel))]
        q = sel + np.c_[np.zeros(len(sel)), offs]
        ci, ok = self._lookup(fld, q)
        ce = clear(q[ok])
        err = float(np.abs(ci[ok] - ce).max(initial=0))
        fld["err"] = err
        fld["eps"] = max(sh.get("field_eps", 0.1), 3 * err)
        return fld

    @staticmethod
    def _lookup(fld, q):
        from scipy.ndimage import map_coordinates
        u = ((q - fld["origin"]) / fld["h"]).T
        shp = np.array(fld["val"].shape)[:, None]
        inb = ((u >= 0) & (u <= shp - 1)).all(0)
        v = np.nan_to_num(fld["val"], nan=1e6)
        c = map_coordinates(v, u, order=1, mode="nearest")
        ok = inb & (c < 1e5)                    # every corner valid (an invalid corner dominates)
        return c, ok

    def _near_threshold(self, C, zg, eps) -> np.ndarray:
        """Heads whose pass/fail could flip under a perturbation of eps in any clearance."""
        lin = self.liner
        near = np.abs(C.min(1)) < eps
        near |= np.abs(C[:, self.unpadded_cols].min(1) - lin["unpadded_min_gap"]) < eps
        for a, b in self._intervals():
            near |= (np.abs(zg - a) < eps + 0.01).any(-1) | (np.abs(zg - b) < eps + 0.01).any(-1)
        if lin.get("max_pad_asymmetry") is not None:
            near |= True
        return near

    def _pad_bits(self, C):
        lin, gwin = self.liner, self.window
        zg = np.stack([C[:, cols].min(axis=1) for cols in self.zone_cols], -1)
        sidx, _ = liner_mod.choose(zg, self.table, lin)
        bad = sidx < 0
        f = np.where(C.min(axis=1) <= 0, HARD, 0)
        f |= np.where((bad & (zg > gwin[1])).any(-1), LOOSE, 0)
        f |= np.where((bad & (zg < gwin[0])).any(-1), TIGHT, 0)
        f |= np.where((bad & (zg >= gwin[0]) & (zg <= gwin[1])).any(-1), PADSTEP, 0)
        f |= np.where((C[:, self.unpadded_cols] < lin["unpadded_min_gap"]).any(-1), UNPADDED, 0)
        if lin.get("max_pad_asymmetry") is not None and {"left", "right"} <= set(lin["zones"]):
            il, ir = lin["zones"].index("left"), lin["zones"].index("right")
            Tl = np.where(sidx[:, il] >= 0, self.table.T[sidx[:, il]], np.nan)
            Tr = np.where(sidx[:, ir] >= 0, self.table.T[sidx[:, ir]], np.nan)
            f |= np.where(np.abs(Tl - Tr) > lin["max_pad_asymmetry"], ASYM, 0)
        return f, zg, sidx

    def _intervals(self):
        if not hasattr(self, "_iv"):
            g = np.round(np.arange(0, 80, 0.01), 2)
            ok = liner_mod.choose(g, self.table, self.liner)[0] >= 0
            edges = np.flatnonzero(np.diff(np.r_[0, ok.astype(int), 0]))
            self._iv = [(g[s], g[e - 1]) for s, e in zip(edges[::2], edges[1::2])]
        return self._iv

    def _in_fill(self, lo, hi):
        """[lo, hi] lies inside one fillable interval (0.01 mm grid, shrunk by one step)."""
        out = np.zeros(lo.shape, bool)
        for a, b in self._intervals():
            out |= (lo >= a + 0.01) & (hi <= b - 0.01)
        return out

    def _in_hole(self, lo, hi):
        """[lo, hi] lies strictly inside a gap between fillable intervals (within the window)."""
        iv = self._intervals()
        out = np.zeros(lo.shape, bool)
        for (_, b), (a, _) in zip(iv[:-1], iv[1:]):
            out |= (lo > b + 0.01) & (hi < a - 0.01)
        return out

    # ------------------------------------------------------------------ lower
    def lower(self, lower: Lower, idx: np.ndarray | None = None) -> np.ndarray:
        """(n_pose, N) failure bitmask for the lower component."""
        H = self.heads if idx is None else self.heads.subset(idx)
        lo = self.cfg["lower"]
        dy = self.poses[:, 0][:, None]
        dz = self.poses[:, 1][:, None]
        pup = H.landmarks["pupils"]
        pz = pup[:, :, 2].mean(1)[None] + dz
        py = pup[:, :, 1].mean(1)[None] + dy
        f = np.zeros((len(self.poses), len(H)), np.int32)
        f |= np.where(np.abs(pz - lower.eye_z) > lo["eye_band"], EYE, 0)
        depth = lower.face_y - py
        up = np.degrees(np.arctan2(lower.grille_top - pz, depth))
        down = np.degrees(np.arctan2(pz - lower.grille_bottom, depth))
        f |= np.where((up < lo["fov_up_min"]) | (down < lo["fov_down_min"]), FOV, 0)
        pr = H.landmarks["pronasale"]
        f |= np.where(lower.face_y - (pr[:, 1][None] + dy) - self.allow + self.cfg["head_model"]["hair_allowance"]
                      < lo["nose_clearance_min"], NOSE, 0)
        me = H.landmarks["menton"]
        chin_plate = lower.face_y - lo["chin_plate_setback"]
        f |= np.where(chin_plate - (me[:, 1][None] + dy) < lo["chin_clearance_min"], CHIN, 0)
        f |= np.where(lower.z_low > me[:, 2][None] + dz - lo["chin_coverage_margin"], COVER, 0)
        return f

    # ------------------------------------------------------------------ assembly
    def combine(self, cr: CrownResult, lower_fail: np.ndarray, lower: Lower,
                idx: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Per head: feasible?, chosen pose index (-1), failure bits at the 'least bad' pose."""
        H = self.heads if idx is None else self.heads.subset(idx)
        tot = cr.fail | lower_fail
        good = tot == 0
        pz = H.landmarks["pupils"][:, :, 2].mean(1)[None] + self.poses[:, 1][:, None]
        score = np.abs(pz - lower.eye_z) + 0.2 * np.abs(self.poses[:, 0])[:, None]
        score = np.where(good, score, np.inf)
        pose = np.argmin(score, axis=0)
        feas = np.isfinite(score.min(axis=0))
        nbits = _popcount(tot)
        worst = tot[np.argmin(nbits, axis=0), np.arange(tot.shape[1])]
        return feas, np.where(feas, pose, -1), np.where(feas, 0, worst)


def _popcount(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.int64)
    c = np.zeros_like(a)
    while a.any():
        c += a & 1
        a >>= 1
    return c


def criteria_status(feasible: bool, bits: int) -> dict:
    """Per-criterion pass/fail/unevaluated for one head-assembly pair."""
    st = {}
    fail = lambda *b: any(bits & x for x in b)
    for k, kind in CRITERIA.items():
        if kind == "unevaluated":
            st[k] = "unevaluated"
            continue
        m = {"C1_no_hard_contact": (HARD,), "C2_liner_present": (UNPADDED,),
             "C3_pad_fill_preload": (LOOSE, TIGHT, PADSTEP, ASYM), "C4_compression_reserve": (TIGHT,),
             "C5_eye_line": (EYE,), "C5_field_of_view_vertical": (FOV,),
             "C6_nose_chin_clearance": (NOSE, CHIN, COVER, EAR), "C8_seam_projection": (HARD,)}[k]
        st[k] = "fail" if fail(*m) else "pass"
    st["geometric_feasible"] = "pass" if feasible else "fail"
    st["validated_fit"] = "unevaluated" if feasible else "fail"
    return st


def decode(bits: int) -> str:
    return ";".join(k for k, v in BITS.items() if bits & v) or ""
