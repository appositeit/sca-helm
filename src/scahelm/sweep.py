"""Collect sensitivity-sweep runs into one table."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def collect(root: Path) -> pd.DataFrame:
    rows = []
    for d in sorted(p for p in root.iterdir() if (p / "manifest.json").exists()):
        man = json.loads((d / "manifest.json").read_text())
        sel = pd.read_csv(d / "coverage_by_families.csv")
        mc = pd.read_csv(d / "min_cost_by_target.csv")
        r = {"scenario": d.name, "allowances_mm": round(man["allowances_mm"], 2),
             "radial_offset": man["radial_offset"]}
        for arch in ("size_only", "modular"):
            g = sel[sel.architecture == arch].set_index("families")
            for k in (1, 2, 3, 4, 6):
                if k in g.index:
                    r[f"{arch}_k{k}_val"] = round(g.loc[k, "val_cov"], 3)
            m = mc[(mc.architecture == arch) & (mc.target.round(2) == 0.90)]
            if len(m):
                r[f"{arch}_dies_for_90"] = m.press_die_sets.iloc[0] if m.status.iloc[0] != "infeasible_target" else "unreachable"
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(root / "sweep_summary.csv", index=False)
    return df
