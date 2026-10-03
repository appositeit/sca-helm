"""Convert source files into the canonical measurement table (see heads.REQUIRED).

Original files in data/raw are never modified; checksums are verified against
config/data_sources.yaml-style expectations passed in by the caller.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ANSUR2_FILES = {
    "M": ("ANSUR_II_MALE_Public.csv", "0547aea0170e5293de519389981135e75803f02e6d40c77ace740decc0caac64"),
    "F": ("ANSUR_II_FEMALE_Public.csv", "ed7e800aa97a4d42f8286b988be2fe1883a2e789588169db959864b707d1757a"),
}

# canonical name -> (ANSUR II column, scale to mm)
ANSUR2_MAP = {
    "head_length": ("headlength", 1.0),
    "head_breadth": ("headbreadth", 1.0),
    "head_circumference": ("headcircumference", 1.0),
    "tragion_top": ("tragiontopofhead", 1.0),
    "menton_sellion": ("mentonsellionlength", 1.0),
    "ear_protrusion": ("earprotrusion", 1.0),
    "interpupillary": ("interpupillarybreadth", 0.1),   # stored in tenths of a millimetre
    "bizygomatic": ("bizygomaticbreadth", 1.0),
    "bitragion_chin_arc": ("bitragionchinarc", 1.0),
}

# plausible adult ranges (mm) for unit and transcription checks, not for exclusion
PLAUSIBLE = {
    "head_length": (150, 240), "head_breadth": (115, 190), "head_circumference": (470, 680),
    "tragion_top": (95, 170), "menton_sellion": (80, 165), "ear_protrusion": (8, 45),
    "interpupillary": (45, 85),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_ansur2(raw_dir: Path) -> tuple[pd.DataFrame, dict]:
    frames, prov = [], {}
    for sex, (name, digest) in ANSUR2_FILES.items():
        path = raw_dir / name
        got = sha256(path)
        if got != digest:
            raise ValueError(f"{path}: sha256 {got} does not match the register ({digest})")
        df = pd.read_csv(path, encoding="latin-1")
        idcol = "subjectid" if "subjectid" in df else "SubjectId"
        out = pd.DataFrame({"pid": [f"ANSUR2-{sex}-{i}" for i in df[idcol]], "sex": sex,
                            "weight": 1.0, "source": "ansur2_2012"})
        for canon, (col, scale) in ANSUR2_MAP.items():
            out[canon] = df[col].astype(float) * scale
        out["age"] = df["Age"]
        frames.append(out)
        prov[name] = {"sha256": got, "rows": len(df)}
    return pd.concat(frames, ignore_index=True), prov


def quality_report(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col, (lo, hi) in PLAUSIBLE.items():
        if col not in t:
            rows.append({"measure": col, "present": False})
            continue
        v = t[col]
        z = (v - v.groupby(t.sex).transform("mean")) / v.groupby(t.sex).transform("std")
        rows.append({"measure": col, "present": True, "n": int(v.notna().sum()),
                     "missing": int(v.isna().sum()), "out_of_plausible_range": int(((v < lo) | (v > hi)).sum()),
                     "abs_z_gt_4": int((z.abs() > 4).sum()),
                     "mean_M": round(float(v[t.sex == "M"].mean()), 1),
                     "mean_F": round(float(v[t.sex == "F"].mean()), 1)})
    return pd.DataFrame(rows)


def stratified_subsample(t: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """Keep the source's sex proportions; weights are applied later, not by resampling."""
    if n >= len(t):
        return t.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    parts = []
    for _, g in t.groupby("sex"):
        k = int(round(n * len(g) / len(t)))
        parts.append(g.iloc[rng.choice(len(g), size=k, replace=False)])
    return pd.concat(parts).sort_values("pid").reset_index(drop=True)


def split_by_participant(t: pd.DataFrame, frac: float, seed: int) -> np.ndarray:
    """Boolean mask: True = validation. Split on participant id, stratified by sex, so no
    person (or any repeated scan of them) appears on both sides."""
    rng = np.random.default_rng(seed + 1)
    pids = t.pid.to_numpy()
    if len(set(pids)) != len(pids):
        raise ValueError("participant ids must be unique before splitting")
    val = np.zeros(len(t), bool)
    for _, g in t.groupby("sex"):
        idx = g.index.to_numpy()
        k = int(round(frac * len(idx)))
        val[rng.choice(idx, size=k, replace=False)] = True
    return val
