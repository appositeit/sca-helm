"""Surrogate heads built from scalar anthropometry.

Canonical measurement columns (mm):
    pid, sex, weight, source,
    head_length, head_breadth, head_circumference, tragion_top, menton_sellion,
    ear_protrusion (optional), interpupillary (optional)

Everything a scalar table does not contain (front/rear split about tragion, height of the
max-length plane, crown squareness, face landmark offsets) is drawn from the priors in
config `head_model`. Those draws are independent of each other and of the measurements,
so the resulting heads are a *surrogate*: conclusions that depend on cranial shape rather
than overall size need 3-D scans.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .geometry import Superquadric, fit_nh_to_perimeter, param_grid, _spow

REQUIRED = ["pid", "sex", "head_length", "head_breadth", "head_circumference",
            "tragion_top", "menton_sellion"]

ZONES = ["crown", "forehead", "occiput", "left", "right"]


@dataclass
class HeadSet:
    table: pd.DataFrame          # one row per participant, measurements + derived params
    points: np.ndarray           # (N, P, 3) crown-region surface samples, head frame
    zone: np.ndarray             # (P,) int: index into ZONES, or -1 for unpadded
    region: np.ndarray           # (N, P) bool: point lies in the crown fit region
    landmarks: dict              # name -> (N, 3) or (N, 2, 3)
    sample_spacing_max: float    # covering radius of the samples over the fit region (mm)
    min_radius: float = 40.0     # smallest radius of curvature over checked heads (mm)

    def __len__(self) -> int:
        return len(self.table)

    def subset(self, idx: np.ndarray) -> "HeadSet":
        return HeadSet(self.table.iloc[idx].reset_index(drop=True), self.points[idx],
                       self.zone, self.region[idx],
                       {k: v[idx] for k, v in self.landmarks.items()},
                       self.sample_spacing_max, self.min_radius)

    def superquadric(self, i: int) -> Superquadric:
        r = self.table.iloc[i]
        return Superquadric(r.a_front, r.a_rear, r.b, r.c_up, r.c_low, r.z_eq, r.nh, r.nv)


def synthetic_measurements(n: int, seed: int = 0, female_fraction: float = 0.2) -> pd.DataFrame:
    """SYNTHETIC fixture. Plausible adult head dimensions with correlation, for tests and
    for running the pipeline without licensed data. Never use for population claims."""
    rng = np.random.default_rng(seed)
    sex = np.where(rng.random(n) < female_fraction, "F", "M")
    # means (M, F) and a shared correlation structure: L, B, H, MS
    mu = {"M": [197, 154, 132, 123], "F": [187, 147, 127, 113]}
    sd = np.array([7.0, 5.5, 6.0, 6.5])
    R = np.array([[1.0, 0.25, 0.35, 0.35],
                  [0.25, 1.0, 0.30, 0.20],
                  [0.35, 0.30, 1.0, 0.30],
                  [0.35, 0.20, 0.30, 1.0]])
    C = R * np.outer(sd, sd)
    X = np.empty((n, 4))
    for s in ("M", "F"):
        m = sex == s
        X[m] = rng.multivariate_normal(mu[s], C, size=int(m.sum()))
    L, B, H, MS = X.T
    circ = np.pi * (L + B) / 2 * 1.04 + rng.normal(0, 6, n)
    return pd.DataFrame({
        "pid": [f"SYN{i:05d}" for i in range(n)], "sex": sex, "weight": 1.0,
        "source": "synthetic", "head_length": L, "head_breadth": B,
        "head_circumference": circ, "tragion_top": H, "menton_sellion": MS,
    })


def _draw(rng, prior, n):
    mean, sd = prior
    return rng.normal(mean, sd, n)


def derive_parameters(meas: pd.DataFrame, hm: dict, seed: int) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in meas]
    if missing:
        raise ValueError(f"measurement table missing columns: {missing}")
    if meas["pid"].duplicated().any():
        raise ValueError("duplicate participant ids: one row per person is required")
    t = meas.copy().reset_index(drop=True)
    n = len(t)
    rng = np.random.default_rng(seed)
    t["f_front"] = np.clip(_draw(rng, hm["f_front"], n), 0.42, 0.58)
    t["z_eq"] = np.clip(_draw(rng, hm["z_equator"], n), 15, 50)
    t["nv"] = np.clip(_draw(rng, hm["n_vertical"], n), 2.0, 3.0)
    t["a_front"] = t.head_length * t.f_front
    t["a_rear"] = t.head_length - t.a_front
    t["b"] = t.head_breadth / 2
    t["c_up"] = t.tragion_top - t.z_eq
    t["c_low"] = np.clip(_draw(rng, hm["c_low_frac"], n), 0.35, 0.8) * t.tragion_top
    nh, ok = zip(*[fit_nh_to_perimeter(r.a_front, r.a_rear, r.b, r.head_circumference)
                   for r in t.itertuples()])
    t["nh"] = nh
    t["nh_fit_ok"] = ok
    t["pupil_z"] = _draw(rng, hm["pupil_z"], n)
    t["sellion_z"] = t.pupil_z + _draw(rng, hm["sellion_z_minus_pupil"], n)
    if "ear_protrusion" not in t or t["ear_protrusion"].isna().all():
        t["ear_protrusion"] = _draw(rng, hm["ear_protrusion_default"], n)
        t["ear_protrusion_imputed"] = True
    else:
        t["ear_protrusion_imputed"] = t["ear_protrusion"].isna()
        t.loc[t.ear_protrusion.isna(), "ear_protrusion"] = hm["ear_protrusion_default"][0]
    if "interpupillary" not in t or t["interpupillary"].isna().all():
        t["interpupillary"] = rng.normal(63.0, 3.5, n)
        t["interpupillary_imputed"] = True
    else:
        t["interpupillary_imputed"] = False
    t["nose_protrusion"] = _draw(rng, hm["nose_protrusion"], n)
    t["pupil_setback"] = _draw(rng, hm["pupil_setback"], n)
    t["chin_setback"] = _draw(rng, hm["chin_setback"], n)
    t["surrogate"] = True
    return t


def _points(t: pd.DataFrame, E: np.ndarray, W: np.ndarray) -> np.ndarray:
    col = lambda k: t[k].to_numpy()[:, None]
    e1, e2 = 2 / col("nv"), 2 / col("nh")
    ce = np.abs(np.cos(E))[None] ** e1
    se = _spow(np.sin(E)[None], e1)
    cw, sw = _spow(np.cos(W)[None], e2), _spow(np.sin(W)[None], e2)
    a = np.where(np.cos(W)[None] >= 0, col("a_front"), col("a_rear"))
    c = np.where(np.sin(E)[None] >= 0, col("c_up"), col("c_low"))
    return np.stack([col("b") * ce * sw, a * ce * cw, col("z_eq") + c * se], axis=-1)


ETA_MIN = -np.pi / 2 + 0.25


def sample_params(t: pd.DataFrame, spacing: float) -> tuple[np.ndarray, np.ndarray]:
    """One fixed set of (eta, omega) parameters shared by every head, chosen so that the
    *median* head is sampled at roughly uniform `spacing`. Shared parameters give every head
    the same point count and the same zone membership."""
    ref = t[["a_front", "a_rear", "b", "c_up", "c_low", "z_eq", "nh", "nv"]].median().to_frame().T
    E, W = param_grid(240, 480, eta_min=ETA_MIN)
    p = _points(ref, E, W)[0]
    key = np.floor(p / spacing).astype(np.int64)
    _, idx = np.unique(key, axis=0, return_index=True)
    idx = np.sort(idx)
    # the parameter grid never reaches the pole: add the vertex explicitly
    return np.r_[E[idx], np.pi / 2], np.r_[W[idx], 0.0]


def covering_radius(t: pd.DataFrame, E: np.ndarray, W: np.ndarray, region: np.ndarray,
                    sh: dict, n_check: int = 40) -> float:
    """Largest distance from any point of the (finely sampled) fit region to its nearest
    sample, over a spread of heads. Any surface bulge between samples is bounded by
    r^2 / (2 R) for this covering radius r."""
    from scipy.spatial import cKDTree
    Ef, Wf = param_grid(160, 320, eta_min=ETA_MIN)
    order = np.argsort(t.head_length.to_numpy() * t.head_breadth.to_numpy())
    pick = np.unique(order[np.linspace(0, len(t) - 1, min(n_check, len(t))).astype(int)])
    worst = 0.0
    for i in pick:
        row = t.iloc[[i]]
        s = _points(row, E, W)[0][region[i]]
        f = _points(row, Ef, Wf)[0]
        f = f[fit_region(f, Wf, sh)]
        d, _ = cKDTree(s).query(f)
        worst = max(worst, float(d.max(initial=0)))
    return worst


def fit_region(pts: np.ndarray, W: np.ndarray, sh: dict, grow: float = 0.0) -> np.ndarray:
    """Crown fit region: above crown_bottom_z, excluding the face (handled by the lower
    component) and the ear band (handled by the ear landmark check). `grow` (mm) dilates the
    region so that samples just outside its edge are evaluated too; the covering radius is
    then measured for the undilated region (conservative: more points are checked)."""
    z = pts[..., 2]
    deg_w = np.degrees(W)
    dw = np.degrees(grow / 90.0)              # ~ angular equivalent on a 90 mm radius
    face = (np.abs(deg_w) < sh["face_half_angle"] - dw) & (z < sh["brow_z"] - grow)
    ear_band = (np.abs(np.abs(deg_w) - 90) < 35 - dw) & (z < 20 - grow)
    return (z >= sh["crown_bottom_z"] - grow) & ~face & ~ear_band


def _front_extent(a, c_up, c_low, z_eq, nv, z):
    dz = z - z_eq
    c = np.where(dz >= 0, c_up, c_low)
    r = np.clip(1 - (np.abs(dz) / c) ** nv, 0, None)
    return a * r ** (1 / nv)


def build(meas: pd.DataFrame, cfg: dict, seed: int) -> HeadSet:
    hm, sh = cfg["head_model"], cfg["shell"]
    t = derive_parameters(meas, hm, seed)
    E, W = sample_params(t, hm["sample_spacing"])
    P = len(E)
    pts = _points(t, E, W)

    # zones are defined in parameter space so every head has identical point counts
    deg_e, deg_w = np.degrees(E), np.degrees(W)
    zone = np.full(P, -1)
    zone[deg_e > 55] = ZONES.index("crown")
    mid = (deg_e <= 55)
    zone[mid & (np.abs(deg_w) < 35) & (deg_e > 0)] = ZONES.index("forehead")
    zone[mid & (np.abs(deg_w) > 145)] = ZONES.index("occiput")
    side = mid & (deg_e > 5)
    zone[side & (deg_w > 60) & (deg_w < 120)] = ZONES.index("left")
    zone[side & (deg_w < -60) & (deg_w > -120)] = ZONES.index("right")

    region = fit_region(pts, W, sh, grow=hm["sample_spacing"])

    # landmarks
    zs = t.sellion_z.to_numpy()
    y_s = _front_extent(t.a_front.to_numpy(), t.c_up.to_numpy(), t.c_low.to_numpy(),
                        t.z_eq.to_numpy(), t.nv.to_numpy(), zs) - 6.0
    ms = t.menton_sellion.to_numpy()
    zero = np.zeros(len(t))
    sellion = np.stack([zero, y_s, zs], -1)
    pron = np.stack([zero, y_s + t.nose_protrusion.to_numpy(), zs - 0.38 * ms], -1)
    menton = np.stack([zero, y_s - t.chin_setback.to_numpy(), zs - ms], -1)
    ipd = t.interpupillary.to_numpy() / 2
    py = y_s - t.pupil_setback.to_numpy()
    pz = t.pupil_z.to_numpy()
    pupils = np.stack([np.stack([ipd, py, pz], -1), np.stack([-ipd, py, pz], -1)], 1)
    # lateral surface at tragion level, then ear protrusion outwards
    dz = -t.z_eq.to_numpy()
    side_x = t.b.to_numpy() * np.clip(1 - (np.abs(dz) / t.c_low.to_numpy()) ** t.nv.to_numpy(),
                                      0, None) ** (1 / t.nv.to_numpy())
    # ears fold under padding; only part of the measured protrusion remains
    ex = side_x + cfg["liner"]["ear_fold_factor"] * t.ear_protrusion.to_numpy()
    ears = np.stack([np.stack([ex, zero - 10, zero + 5], -1),
                     np.stack([-ex, zero - 10, zero + 5], -1)], 1)

    spacing = covering_radius(t, E, W, region, sh)
    from .geometry import min_curvature_radius
    sel = np.unique(np.linspace(0, len(t) - 1, min(25, len(t))).astype(int))
    order = np.argsort(t.nh.to_numpy())          # include the squarest heads
    sel = np.unique(np.r_[order[sel], order[-5:]])
    rmin = min(min_curvature_radius(Superquadric(*t.iloc[i][["a_front", "a_rear", "b", "c_up", "c_low",
                                                            "z_eq", "nh", "nv"]].astype(float)),
                                    sh["crown_bottom_z"], n=60) for i in sel)

    return HeadSet(t, pts, zone, region,
                   {"sellion": sellion, "pronasale": pron, "menton": menton,
                    "pupils": pupils, "ears": ears}, spacing, rmin)


def sex_weights(table: pd.DataFrame, female_fraction: float) -> np.ndarray:
    """Post-stratification weights so the weighted sex mix matches the target denominator."""
    w = np.ones(len(table))
    f = (table.sex == "F").to_numpy()
    nf, nm = f.sum(), (~f).sum()
    if nf and nm:
        w[f] = female_fraction / nf
        w[~f] = (1 - female_fraction) / nm
    w *= len(w) / w.sum()
    return w
