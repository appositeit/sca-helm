"""Discrete pad stacks and a linear series-spring screening model.

Normal compliance of a stack per unit area is sum(t_i / E_i); shear compliance is
sum(t_i / G_i). This assumes small strain, linear foam and ideal bonding. It ranks
candidate stacks for *installed fit*; it says nothing about impact attenuation. With
unmeasured materials, every stability/protection criterion is reported "unevaluated".
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Stack:
    layers: tuple            # ((material, thickness), ...), base layer first
    thickness: float         # uncompressed total (mm)
    normal_compliance: float  # sum(t/E) in mm/kPa
    shear_compliance: float
    crushable: float         # sum(t * densification_strain): crush distance before bottoming

    @property
    def label(self) -> str:
        return "+".join(f"{m}{t:g}" for m, t in self.layers)


def enumerate_stacks(liner: dict) -> list[Stack]:
    mats, cat, rules = liner["materials"], liner["catalogue"], liner["stack_rules"]
    base = rules["base_material"]
    fitting = [(m, t) for m, ts in cat.items() for t in ts]
    out = []
    for tb in cat[base]:
        for k in range(rules["max_fitting_layers"] + 1):
            for combo in itertools.combinations_with_replacement(fitting, k):
                layers = ((base, tb),) + combo
                T = sum(t for _, t in layers)
                nc = sum(t / mats[m]["E_kPa"] for m, t in layers)
                sc = sum(t / mats[m]["G_kPa"] for m, t in layers)
                cr = sum(t * mats[m]["densification_strain"] for m, t in layers)
                out.append(Stack(layers, T, nc, sc, cr))
    # de-duplicate stacks with identical layer multisets
    seen, uniq = set(), []
    for s in out:
        key = tuple(sorted(s.layers))
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return sorted(uniq, key=lambda s: (s.thickness, len(s.layers)))


@dataclass
class StackTable:
    stacks: list
    T: np.ndarray
    nc: np.ndarray
    crush: np.ndarray

    @classmethod
    def from_config(cls, liner: dict) -> "StackTable":
        st = enumerate_stacks(liner)
        return cls(st, np.array([s.thickness for s in st]), np.array([s.normal_compliance for s in st]),
                   np.array([s.crushable for s in st]))


def choose(gap: np.ndarray, table: StackTable, liner: dict) -> tuple[np.ndarray, dict]:
    """For each gap (mm, any shape) choose the stack whose installed strain is closest to
    the middle of the allowed band. Returns (stack index or -1, per-check pass arrays).

    Checks per candidate stack:
      thickness   T <= max_liner_depth
      padding     T (or the compressed gap) >= min_padding, per min_padding_basis
      strain      installed strain (T - gap)/T within fit_strain
      pressure    (T - gap)/sum(t/E) within contact_pressure_kPa
      reserve     remaining crush distance (crush - (T - gap)) >= compression_reserve_min
    """
    g = np.asarray(gap, dtype=float)[..., None]
    T, nc, cr = table.T, table.nc, table.crush
    delta = T - g
    strain = delta / T
    p = delta / nc
    lo, hi = liner["fit_strain"]
    plo, phi = liner["contact_pressure_kPa"]
    basis = liner["min_padding_basis"]
    pad_ok = (T >= liner["min_padding"]) if basis == "uncompressed" else (g >= liner["min_padding"])
    checks = {
        "thickness": np.broadcast_to(T <= liner["max_liner_depth"], strain.shape),
        "padding": np.broadcast_to(pad_ok, strain.shape),
        "strain": (strain >= lo) & (strain <= hi),
        "pressure": (p >= plo) & (p <= phi),
        "reserve": (cr - delta) >= liner["compression_reserve_min"],
    }
    ok = np.logical_and.reduce(list(checks.values()))
    score = np.where(ok, np.abs(strain - 0.5 * (lo + hi)), np.inf)
    idx = np.argmin(score, axis=-1)
    idx = np.where(np.isfinite(np.min(score, axis=-1)), idx, -1)
    # summarise which check is limiting: True if *some* stack passes that check
    any_pass = {k: v.any(axis=-1) for k, v in checks.items()}
    return idx, any_pass


def gap_window(table: StackTable, liner: dict) -> tuple[float, float]:
    """Smallest and largest gap any stack can fill. Used for conservative pre-filtering."""
    g = np.linspace(0, 80, 1601)
    idx, _ = choose(g, table, liner)
    ok = g[idx >= 0]
    if not len(ok):
        return (np.inf, -np.inf)
    return float(ok.min()), float(ok.max())
