"""End-to-end run: heads -> catalogue -> feasibility matrix -> selection -> reports."""
from __future__ import annotations

import copy
import hashlib
import json
import multiprocessing as mp
import platform
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import fit, heads as heads_mod, ingest, optimise, shells
from .fit import Evaluator

ROOT = Path(__file__).resolve().parents[2]


def deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(scenario: str | None = None, overrides: dict | None = None) -> dict:
    cfg = yaml.safe_load(open(ROOT / "config" / "default.yaml"))
    if scenario:
        sc = yaml.safe_load(open(ROOT / "config" / "scenarios.yaml"))[scenario]
        cfg = deep_merge(cfg, sc.get("overrides", {}))
        cfg["scenario"] = scenario
        cfg["scenario_label"] = sc.get("label", scenario)
    cfg = deep_merge(cfg, overrides or {})
    return cfg


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- heads
def load_measurements(source: str, cfg: dict) -> tuple[pd.DataFrame, dict]:
    if source == "synthetic":
        n = cfg["population"]["max_participants"]
        return heads_mod.synthetic_measurements(n, seed=cfg["seed"]), {"synthetic": {"seed": cfg["seed"]}}
    if source == "ansur2":
        t, prov = ingest.load_ansur2(ROOT / "data" / "raw" / "ansur2")
        t = ingest.stratified_subsample(t, cfg["population"]["max_participants"], cfg["seed"])
        return t, prov
    path = Path(source)
    return pd.read_csv(path), {str(path): {"sha256": ingest.sha256(path)}}


# ---------------------------------------------------------------- crown evaluation (parallel)
_EV: Evaluator | None = None


def _eval_crown(crown):
    res = _EV.crown(crown)
    return crown.id, res.fail.astype(np.int16)


def evaluate_catalogue(ev: Evaluator, crowns: list, processes: int = 4, log=print) -> dict:
    global _EV
    _EV = ev
    ev.kd_workers = 1 if processes > 1 else -1
    out = {}
    t0 = time.time()
    ctx = mp.get_context("fork")
    with ctx.Pool(processes) as pool:
        for i, (cid, fail) in enumerate(pool.imap_unordered(_eval_crown, crowns, chunksize=1)):
            out[cid] = fail
            if (i + 1) % 10 == 0 or i + 1 == len(crowns):
                log(f"  crowns evaluated: {i + 1}/{len(crowns)}  ({time.time() - t0:.0f} s)")
    return out


@dataclass
class Feasibility:
    A: np.ndarray            # (N, J) bool
    pose: np.ndarray         # (N, J) int8, chosen pose or -1
    worst: np.ndarray        # (N, J) int16, failure bits at least-bad pose
    assemblies: list         # list[shells.Assembly]
    crown_of: np.ndarray     # (J,) crown id per assembly


def feasibility(ev: Evaluator, crowns: list, crown_fail: dict, cfg: dict) -> Feasibility:
    asm, cols_A, cols_P, cols_W = [], [], [], []
    for c in crowns:
        cr = fit.CrownResult(crown_fail[c.id] == 0, crown_fail[c.id].astype(np.int32), None, None, None)
        for l in shells.lowers_for(c, cfg):
            lf = ev.lower(l)
            feas, pose, worst = ev.combine(cr, lf, l)
            asm.append(shells.Assembly(c, l))
            cols_A.append(feas)
            cols_P.append(pose.astype(np.int8))
            cols_W.append(worst.astype(np.int16))
    return Feasibility(np.stack(cols_A, 1), np.stack(cols_P, 1), np.stack(cols_W, 1), asm,
                       np.array([a.crown.id for a in asm]))


# ---------------------------------------------------------------- architectures
def architecture_columns(F: Feasibility, cfg: dict) -> dict:
    """Column subsets of the feasibility matrix for each architecture."""
    fam = np.array([a.crown.family for a in F.assemblies])
    default_ids = set()
    for a in F.assemblies:
        if a.crown.family == "size_only":
            default_ids.add(shells.default_lower(a.crown, cfg).id)
    lid = np.array([a.lower.id for a in F.assemblies])
    return {
        "size_only": {"cols": np.flatnonzero((fam == "size_only") & np.isin(lid, list(default_ids))),
                      "integrated": True, "label": "Size-only (one scaled shape, integrated lower)"},
        "size_only_modular": {"cols": np.flatnonzero(fam == "size_only"), "integrated": False,
                              "label": "Size-only crowns + laser-cut lower variants"},
        "shape_integrated": {"cols": np.arange(len(fam)), "integrated": True,
                             "label": "Shape-variable, lower integrated in the pressing"},
        "modular": {"cols": np.arange(len(fam)), "integrated": False,
                    "label": "Shape-variable crown + laser-cut lower variants"},
    }


def costs(cfg: dict) -> dict:
    c = cfg["costs"]
    halves = 1 if c["halves_share_die"] else 2
    return {"crown_die_set": halves * c["die_per_half"],
            "integrated_die_set": halves * (c["die_per_half"] + c["integrated_lower_die_extra"]),
            "lower_design": c["lower_design"]}


def select_all(F: Feasibility, w: np.ndarray, train: np.ndarray, cfg: dict, log=print) -> pd.DataFrame:
    oc = cfg["optimiser"]
    rows = []
    for arch, spec in architecture_columns(F, cfg).items():
        cols = spec["cols"]
        A = F.A[train][:, cols]
        crown_of = F.crown_of[cols]
        L = 1 if spec["integrated"] else oc["max_lowers_per_crown"]
        for k in range(1, oc["max_families"] + 1):
            g = optimise.greedy(A, w[train], crown_of, k, L, spec["integrated"])
            m = optimise.max_coverage(A, w[train], crown_of, k, lowers_per_crown=L,
                                      integrated=spec["integrated"], time_limit=oc["time_limit_s"],
                                      mip_gap=oc["mip_rel_gap"], warm=g)
            sel_cols = cols[m.assemblies]
            rows.append({"architecture": arch, "families": k, "train_cov_greedy": g.coverage,
                         "train_cov": m.coverage, "status": m.status, "mip_gap": m.gap,
                         "val_cov": optimise.coverage_of(F.A[~train], w[~train], sel_cols),
                         "val_cov_unweighted": optimise.coverage_of(F.A[~train], np.ones((~train).sum()), sel_cols),
                         "assemblies": [F.assemblies[j].id for j in sel_cols],
                         "crowns": sorted({F.assemblies[j].crown.id for j in sel_cols})})
            log(f"  {arch:17s} k={k}: train {m.coverage:.3f} (greedy {g.coverage:.3f}, {m.status}) "
                f"val {rows[-1]['val_cov']:.3f}")
    return pd.DataFrame(rows)


def bootstrap(F: Feasibility, w: np.ndarray, train: np.ndarray, cfg: dict, arch: str, ks, seed: int,
              log=print) -> pd.DataFrame:
    """Resample training participants (with replacement), re-run selection, score on the
    fixed validation set. The interval therefore includes selection variability."""
    oc = cfg["optimiser"]
    spec = architecture_columns(F, cfg)[arch]
    cols, L = spec["cols"], (1 if spec["integrated"] else oc["max_lowers_per_crown"])
    tr = np.flatnonzero(train)
    rng = np.random.default_rng(seed)
    out = []
    for b in range(oc["bootstrap"]):
        s = rng.choice(tr, size=len(tr), replace=True)
        A = F.A[s][:, cols]
        for k in ks:
            g = optimise.greedy(A, w[s], F.crown_of[cols], k, L, spec["integrated"])
            m = optimise.max_coverage(A, w[s], F.crown_of[cols], k, lowers_per_crown=L,
                                      integrated=spec["integrated"], time_limit=oc["bootstrap_time_limit_s"],
                                      warm=g)
            out.append({"architecture": arch, "families": k, "b": b,
                        "val_cov": optimise.coverage_of(F.A[~train], w[~train], cols[m.assemblies])})
    log(f"  bootstrap {arch}: {oc['bootstrap']} replicates")
    return pd.DataFrame(out)


def min_cost_table(F: Feasibility, w: np.ndarray, train: np.ndarray, cfg: dict, targets) -> pd.DataFrame:
    oc, cc = cfg["optimiser"], costs(cfg)
    rows = []
    for arch, spec in architecture_columns(F, cfg).items():
        cols = spec["cols"]
        for tgt in targets:
            r = optimise.min_cost(F.A[train][:, cols], w[train], F.crown_of[cols], tgt,
                                  crown_cost=cc["integrated_die_set"] if spec["integrated"] else cc["crown_die_set"],
                                  lower_cost=cc["lower_design"], integrated=spec["integrated"],
                                  lowers_per_crown=1 if spec["integrated"] else oc["max_lowers_per_crown"],
                                  time_limit=oc["time_limit_s"])
            sel = cols[r.assemblies] if r.assemblies else np.array([], int)
            n_crowns = len(r.crowns)
            rows.append({"architecture": arch, "target": tgt, "status": r.status, "mip_gap": r.gap,
                         "tooling_cost_AUD": r.cost, "crown_families": n_crowns,
                         "press_die_sets": (len(sel) if spec["integrated"] else n_crowns),
                         "press_dies": (len(sel) if spec["integrated"] else n_crowns) * (1 if cfg["costs"]["halves_share_die"] else 2),
                         "complete_assemblies": len(sel),
                         "train_cov": r.coverage,
                         "val_cov": optimise.coverage_of(F.A[~train], w[~train], sel) if len(sel) else 0.0,
                         "assemblies": [F.assemblies[j].id for j in sel]})
    return pd.DataFrame(rows)


def provenance(cfg: dict, prov: dict, extra: dict) -> dict:
    import scipy, numpy, trimesh as tm
    return {"created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "config_hash": config_hash(cfg),
            "seed": cfg["seed"], "data": prov, "python": platform.python_version(),
            "packages": {"numpy": numpy.__version__, "scipy": scipy.__version__,
                         "pandas": pd.__version__, "trimesh": tm.__version__},
            "solver": "HiGHS (highspy), greedy warm start, exact dominated-column pruning", **extra}
