"""`scahelm run`: the whole exploratory pipeline for one scenario, writing to outputs/<name>/."""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import export, fit, heads as heads_mod, ingest, optimise, pipeline, report, shells
from .geometry import mesh


def run(source: str, scenario: str | None, outdir: Path, n: int | None = None, processes: int = 4,
        bootstrap: int | None = None, cad: bool = True, overrides: dict | None = None) -> dict:
    t0 = time.time()
    outdir.mkdir(parents=True, exist_ok=True)
    logf = open(outdir / "run.log", "w")

    def log(msg):
        line = f"[{time.time() - t0:7.0f}s] {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    cfg = pipeline.load_config(scenario, overrides)
    if n:
        cfg["population"]["max_participants"] = n
    if bootstrap is not None:
        cfg["optimiser"]["bootstrap"] = bootstrap
    label = "SYNTHETIC FIXTURE - not a population result" if source == "synthetic" else \
        f"{source} surrogate (scalar measurements + assumed shape priors)"
    log(f"scenario={scenario or 'default'} source={source} label={label}")

    meas, prov = pipeline.load_measurements(source, cfg)
    if source != "synthetic":
        ingest.quality_report(meas).to_csv(outdir / "data_quality.csv", index=False)
    H = heads_mod.build(meas, cfg, seed=cfg["seed"])
    t = H.table
    w = heads_mod.sex_weights(t, cfg["population"]["female_fraction"])
    val = ingest.split_by_participant(t, cfg["population"]["validation_fraction"], cfg["seed"])
    train = ~val
    log(f"heads: {len(H)} ({(t.sex == 'F').sum()} F), train {train.sum()}, validation {val.sum()}; "
        f"{H.points.shape[1]} samples/head, covering radius {H.sample_spacing_max:.1f} mm, "
        f"min head radius {H.min_radius:.1f} mm, nh fit ok {t.nh_fit_ok.mean():.3f}")

    ev = fit.Evaluator(H, cfg)
    log(f"pad gap window {ev.window[0]:.2f}-{ev.window[1]:.2f} mm; allowances {ev.allow:.2f} mm "
        f"(sampling bound {ev.bound:.2f}); {len(ev.table.stacks)} stacks; {len(ev.poses)} poses")
    gap = shells.calibrate_gap(ev, cfg, pool=np.flatnonzero(train))
    crowns = shells.crown_catalogue(t[train], cfg, gap)
    log(f"calibrated radial offset {gap:.1f} mm; catalogue {len(crowns)} crowns "
        f"({sum(c.family == 'size_only' for c in crowns)} size-only)")

    cache = outdir / "crown_eval.npz"
    key = pipeline.config_hash({k: v for k, v in cfg.items() if k != "optimiser"}) + f"-{source}-{len(H)}"
    crown_fail = None
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        if str(z["key"]) == key:
            crown_fail = z["fail"].item()
            log("crown evaluation loaded from cache")
    if crown_fail is None:
        crown_fail = pipeline.evaluate_catalogue(ev, crowns, processes, log)
        np.savez_compressed(cache, key=key, fail=np.array(crown_fail, dtype=object))
    F = pipeline.feasibility(ev, crowns, crown_fail, cfg)
    np.savez_compressed(outdir / "feasibility.npz", A=F.A, pose=F.pose, crown_of=F.crown_of,
                        ids=np.array([a.id for a in F.assemblies]), pid=t.pid.to_numpy(), w=w, val=val)
    log(f"feasibility matrix {F.A.shape}; heads with >=1 feasible assembly: "
        f"{F.A.any(1).mean():.3f} (weighted {w[F.A.any(1)].sum() / w.sum():.3f})")

    sel = pipeline.select_all(F, w, train, cfg, log)
    sel.to_csv(outdir / "coverage_by_families.csv", index=False)
    targets = sorted({0.85, 0.90, 0.95, cfg["population"]["target_coverage"]})
    mc = pipeline.min_cost_table(F, w, train, cfg, targets)
    mc.to_csv(outdir / "min_cost_by_target.csv", index=False)
    log("min-cost table:\n" + mc.drop(columns=["assemblies"]).to_string(index=False))

    boots = []
    if cfg["optimiser"]["bootstrap"]:
        for arch in ("size_only", "size_only_modular", "shape_integrated", "modular"):
            boots.append(pipeline.bootstrap(F, w, train, cfg, arch, range(1, cfg["optimiser"]["max_families"] + 1),
                                            cfg["seed"], log))
        bt = pd.concat(boots)
        bt.to_csv(outdir / "bootstrap_validation.csv", index=False)
        ci = bt.groupby(["architecture", "families"]).val_cov.quantile([0.05, 0.5, 0.95]).unstack()
        ci.columns = ["val_p05", "val_p50", "val_p95"]
        sel = sel.merge(ci.reset_index(), on=["architecture", "families"], how="left")
        sel.to_csv(outdir / "coverage_by_families.csv", index=False)

    # recommended exploratory configuration: cheapest modular set reaching the target on train
    tgt = cfg["population"]["target_coverage"]
    rec = mc[(mc.architecture == "modular") & (np.isclose(mc.target, tgt))].iloc[0]
    if not rec.assemblies:
        best = sel[sel.architecture == "modular"].sort_values("train_cov").iloc[-1]
        rec_ids, rec_note = best.assemblies, f"target {tgt} unreachable; using best modular k={best.families}"
    else:
        rec_ids, rec_note = rec.assemblies, f"cheapest modular set reaching {tgt} on training heads"
    log(f"recommended set: {rec_note}: {rec_ids}")
    assign = assignments(ev, F, rec_ids, w, val, cfg)
    assign.to_csv(outdir / "assignments.csv", index=False)
    excl = exclusion_summary(assign)
    excl.to_csv(outdir / "excluded_characteristics.csv", index=False)

    chosen = [a for a in F.assemblies if a.id in set(rec_ids)]
    dims = dimension_tables(chosen, F, cfg, outdir)
    if cad:
        cad_exports(chosen, cfg, outdir / "cad")
    report.plots(sel, F, assign, outdir)
    man = pipeline.provenance(cfg, prov, {
        "source": source, "label": label, "scenario": scenario, "n_heads": len(H),
        "radial_offset": gap, "n_crowns": len(crowns), "n_assemblies": len(F.assemblies),
        "allowances_mm": ev.allow, "sampling_bound_mm": ev.bound, "pad_window_mm": ev.window,
        "recommended": rec_ids, "recommended_note": rec_note, "runtime_s": time.time() - t0,
        "criteria": fit.CRITERIA})
    (outdir / "manifest.json").write_text(json.dumps(man, indent=2, default=str))
    (outdir / "config_used.yaml").write_text(__import__("yaml").safe_dump(cfg, sort_keys=False))
    report.summary(outdir, cfg, man, sel, mc, assign, excl, dims)
    log("done")
    return man


def assignments(ev, F, rec_ids, w, val, cfg) -> pd.DataFrame:
    H = ev.heads
    cols = [j for j, a in enumerate(F.assemblies) if a.id in set(rec_ids)]
    crowns = {F.assemblies[j].crown.id: F.assemblies[j].crown for j in cols}
    detail = {cid: ev.crown(c) for cid, c in crowns.items()}
    zones = cfg["liner"]["zones"]
    rows = []
    for i in range(len(H)):
        r = H.table.iloc[i]
        base = {"pid": r.pid, "sex": r.sex, "weight": w[i], "set": "validation" if val[i] else "train",
                "head_length": r.head_length, "head_breadth": r.head_breadth,
                "head_circumference": r.head_circumference, "tragion_top": r.tragion_top,
                "menton_sellion": r.menton_sellion}
        fits = [j for j in cols if F.A[i, j]]
        if fits:
            j = fits[0]
            a = F.assemblies[j]
            k = int(F.pose[i, j])
            st = detail[a.crown.id].stacks[k, i]
            gp = detail[a.crown.id].gaps[k, i]
            base.update({"status": "geometric_feasible", "validated_fit": "unevaluated",
                         "assembly": a.id, "crown": a.crown.id, "pose_dy": ev.poses[k, 0], "pose_dz": ev.poses[k, 1],
                         "n_alternatives": len(fits) - 1, "fail_reasons": ""})
            for z, s, g in zip(zones, st, gp):
                base[f"pad_{z}"] = ev.table.stacks[s].label if s >= 0 else ""
                base[f"gap_{z}"] = round(float(g), 2)
        else:
            bits = F.worst[i, cols]
            nb = fit._popcount(bits)
            j = cols[int(np.argmin(nb))]
            base.update({"status": "excluded", "validated_fit": "fail", "assembly": F.assemblies[j].id,
                         "crown": F.assemblies[j].crown.id, "fail_reasons": fit.decode(int(F.worst[i, j])),
                         "fits_any_catalogue_assembly": bool(F.A[i].any())})
        rows.append(base)
    return pd.DataFrame(rows)


def exclusion_summary(assign: pd.DataFrame) -> pd.DataFrame:
    meas = ["head_length", "head_breadth", "head_circumference", "tragion_top", "menton_sellion"]
    rows = []
    for (sex, status), g in assign.groupby(["sex", "status"]):
        r = {"sex": sex, "status": status, "n": len(g)}
        for m in meas:
            r[f"{m}_mean"] = round(g[m].mean(), 1)
        rows.append(r)
    ex = assign[assign.status == "excluded"]
    reasons = ex.fail_reasons.str.split(";").explode().value_counts()
    for k, v in reasons.items():
        rows.append({"sex": "all", "status": f"reason:{k}", "n": int(v)})
    return pd.DataFrame(rows)


def dimension_tables(chosen, F, cfg, outdir: Path) -> pd.DataFrame:
    sh = cfg["shell"]
    rho, th = sh["material"]["density_g_cm3"], sh["material"]["thickness"]
    rows = []
    seen = set()
    import trimesh
    for a in chosen:
        if a.crown.id in seen:
            continue
        seen.add(a.crown.id)
        v, f = mesh(a.crown.sq, z_min=sh["crown_bottom_z"] - 25)
        area = trimesh.Trimesh(v, f).area
        r = a.crown.row()
        r.update({"status": "EXPLORATORY", "inner_area_mm2": round(area),
                  "crown_mass_kg_est": round(area * th * rho / 1e6, 2),
                  "min_curvature_radius_mm": None})
        rows.append(r)
    crown_tab = pd.DataFrame(rows)
    crown_tab.to_csv(outdir / "candidate_crowns.csv", index=False)
    pd.DataFrame([a.lower.row() | {"status": "EXPLORATORY"} for a in chosen]).to_csv(
        outdir / "candidate_lowers.csv", index=False)
    # compatibility: which catalogue lowers are geometrically realisable on which chosen crown,
    # and how many heads each (crown, lower) pair fits
    comp = []
    for cid in crown_tab.crown_id:
        for j, a in enumerate(F.assemblies):
            if a.crown.id == cid:
                comp.append({"crown": cid, "lower": a.lower.id, "eye_z": a.lower.eye_z,
                             "face_offset": a.lower.face_offset, "chin_drop": a.lower.eye_z - a.lower.z_low,
                             "interface_compatible": True, "heads_fitted": int(F.A[:, j].sum())})
    pd.DataFrame(comp).to_csv(outdir / "lower_compatibility.csv", index=False)
    return crown_tab


def cad_exports(chosen, cfg, cad: Path):
    sh = cfg["shell"]
    th = sh["material"]["thickness"]
    done, blanks = set(), []
    for a in chosen:
        if a.crown.id not in done:
            export.write_stl(a.crown, cad, th, z_min=sh["crown_bottom_z"] - 25)
            try:
                export.write_step(a.crown, cad / f"{a.crown.id}_inner.step", z_min=sh["crown_bottom_z"] - 25)
            except Exception as e:  # OCP missing or surface fit failure: STL still written
                (cad / f"{a.crown.id}_inner.step.FAILED.txt").write_text(str(e))
            done.add(a.crown.id)
        blanks.append(export.grille_blank(a.lower, a.crown, cfg, cad / f"{a.lower.id}_grille_blank.dxf"))
    pd.DataFrame(blanks).to_csv(cad / "grille_blanks.csv", index=False)
