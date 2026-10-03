"""Candidate crown shells and lower components."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd

from .geometry import Superquadric, min_curvature_radius, sample_surface


@dataclass(frozen=True)
class Crown:
    id: str
    family: str              # "size_only" | "grid"
    sq: Superquadric         # finished inner surface, shell frame

    def row(self) -> dict:
        d = {"crown_id": self.id, "family": self.family}
        d.update(self.sq.as_dict())
        d["inner_length"] = self.sq.a_front + self.sq.a_rear
        d["inner_breadth"] = 2 * self.sq.b
        d["inner_height_above_tragion"] = self.sq.z_eq + self.sq.c_up
        return d


@dataclass(frozen=True)
class Lower:
    id: str
    crown_id: str
    eye_z: float             # design eye line, shell frame
    face_y: float            # inner face-plate plane at nose level
    z_low: float             # lower edge of the face/jaw plate
    face_offset: float       # face_y beyond crown front extent at eye_z (interface rule)
    grille_top: float
    grille_bottom: float

    def row(self) -> dict:
        return asdict(self)


@dataclass
class Assembly:
    crown: Crown
    lower: Lower

    @property
    def id(self) -> str:
        return self.lower.id


def nominal_gap(cfg: dict, window: tuple[float, float]) -> float:
    """First guess at the radial offset from head to shell: middle of the fillable pad
    window plus allowances. Refined by `calibrate_gap`."""
    lo, hi = window
    allow = allowances(cfg, 0.0)
    return 0.5 * (lo + hi) + allow


def calibrate_gap(evaluator, cfg: dict, pool: np.ndarray | None = None) -> float:
    """Radial offset (added to each head semi-axis) at which a typical head's mean zone gap
    sits at the middle of the fillable window. Normal clearance between two non-similar
    convex surfaces is smaller than the difference in semi-axes, so the first guess is
    biased tight."""
    t = evaluator.heads.table
    pool = np.arange(len(t)) if pool is None else np.asarray(pool)
    t = t.iloc[pool]
    z = ((t[["head_length", "head_breadth", "tragion_top"]] - t[["head_length", "head_breadth", "tragion_top"]].median())
         / t[["head_length", "head_breadth", "tragion_top"]].std()).pow(2).sum(1)
    order = np.argsort(z.to_numpy())[:15]
    typical = pool[order]
    target = 0.5 * sum(evaluator.window)
    one = t.iloc[order]
    best, err = None, np.inf
    for g in np.arange(18.0, 42.0, 1.5):
        L, B, H = (float(one.head_length.median()) + 2 * g, float(one.head_breadth.median()) + 2 * g,
                   float(one.tragion_top.median()) + g)
        sq = _make(one, cfg, g)(L, B, H)
        res = evaluator.crown(Crown("cal", "cal", sq), idx=typical)
        k = np.argmin(np.abs(evaluator.poses).sum(1))
        g_k = res.gaps[k]
        if np.isnan(g_k).all():          # all heads rejected by the ray filter: far too tight
            continue
        e = abs(float(np.nanmean(g_k)) - target)
        if e < err:
            best, err = g, e
    return float(best)


def _make(t: pd.DataFrame, cfg: dict, gap: float):
    f_front = float(t.f_front.mean())
    z_eq = float(t.z_eq.mean())
    nh = float(t.nh.mean())
    low_frac = float((t.c_low / t.tragion_top).mean())
    nv = cfg["shell"]["n_vertical"]

    def make(L, B, H) -> Superquadric:
        return Superquadric(L * f_front, L * (1 - f_front), B / 2, H - z_eq,
                            low_frac * (H - gap) + gap, z_eq, nh, nv)
    return make


def allowances(cfg: dict, sampling_bound: float) -> float:
    sh = cfg["shell"]
    return (cfg["head_model"]["hair_allowance"] + sh["manufacturing_tolerance"]
            + sh["measurement_uncertainty"] + sampling_bound)


def crown_catalogue(heads_table: pd.DataFrame, cfg: dict, gap: float) -> list[Crown]:
    sh, cat = cfg["shell"], cfg["catalogue"]
    t = heads_table
    qlo, qhi = cat["quantile_range"]
    make = _make(t, cfg, gap)

    out: list[Crown] = []
    L0, B0, H0 = (float(t.head_length.median()) + 2 * gap, float(t.head_breadth.median()) + 2 * gap,
                  float(t.tragion_top.median()) + gap)
    base = make(L0, B0, H0)
    s_lo = (t.head_length.quantile(qlo) + 2 * gap) / L0
    s_hi = (t.head_length.quantile(qhi) + 2 * gap) / L0
    for i, s in enumerate(np.linspace(s_lo - 0.02, s_hi + 0.02, cat["size_only_scales"])):
        # scale about the tragion origin: proportions fixed, including the equator height
        out.append(Crown(f"S{i:02d}", "size_only", base.scaled(float(s))))

    rng = lambda col, pad, step: np.arange(t[col].quantile(qlo) + pad - step / 2,
                                           t[col].quantile(qhi) + pad + step, step)
    Ls = rng("head_length", 2 * gap, cat["length_steps"])
    Bs = rng("head_breadth", 2 * gap, cat["breadth_steps"])
    Hs = rng("tragion_top", gap, cat["height_steps"])
    k = 0
    for L in Ls:
        for B in Bs:
            if not (0.68 <= B / L <= 0.95):
                continue
            for H in Hs:
                out.append(Crown(f"G{k:03d}", "grid", make(float(L), float(B), float(H))))
                k += 1
    keep = []
    for c in out:
        r = min_curvature_radius(c.sq, sh["crown_bottom_z"])
        if r >= sh["min_curvature_radius"]:
            keep.append(c)
    return keep


def lowers_for(crown: Crown, cfg: dict) -> list[Lower]:
    lo = cfg["lower"]
    cmin, cmax = lo["compat_face_offset"]
    out = []
    k = 0
    for de in lo["eye_z_offsets"]:
        eye = lo["nominal_eye_z"] + de
        front = crown.sq.front_extent_at(eye)
        for off in lo["face_depth_offsets"]:
            if not (cmin <= off <= cmax):
                continue
            for drop in lo["chin_drops"]:
                out.append(Lower(f"{crown.id}-L{k:02d}", crown.id, eye, front + off, eye - drop, off,
                                 eye + lo["grille_top_above_eye"], eye - lo["grille_bottom_below_eye"]))
                k += 1
    return out


def default_lower(crown: Crown, cfg: dict) -> Lower:
    """The single lower used by the size-only (integrated) architecture: middle offsets."""
    ls = lowers_for(crown, cfg)
    lo = cfg["lower"]
    mid = lambda xs: sorted(xs)[len(xs) // 2]
    want = (lo["nominal_eye_z"] + mid(lo["eye_z_offsets"]), mid(lo["face_depth_offsets"]),
            mid(lo["chin_drops"]))
    for l in ls:
        if (abs(l.eye_z - want[0]) < 1e-9 and abs(l.face_offset - want[1]) < 1e-9
                and abs(l.eye_z - l.z_low - want[2]) < 1e-9):
            return l
    return ls[len(ls) // 2]


def shell_samples(crown: Crown, cfg: dict) -> np.ndarray:
    sh = cfg["shell"]
    return sample_surface(crown.sq, sh["sample_spacing"], z_min=sh["crown_bottom_z"] - 60)
