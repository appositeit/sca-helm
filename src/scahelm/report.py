"""Plots and the per-run markdown summary."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ARCH_STYLE = {"size_only": ("#7f7f7f", "Size-only (scaled single shape)"),
              "shape_integrated": ("#1f77b4", "Shape-variable, integrated lower"),
              "modular": ("#d62728", "Shape-variable crown + laser-cut lowers")}


def plots(sel: pd.DataFrame, F, assign: pd.DataFrame, outdir: Path):
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for arch, g in sel.groupby("architecture"):
        col, lab = ARCH_STYLE[arch]
        g = g.sort_values("families")
        ax.plot(g.families, g.train_cov, "-o", color=col, label=f"{lab}: training")
        ax.plot(g.families, g.val_cov, "--s", color=col, alpha=0.7, label="  held-out (selection fixed)")
        if "val_p05" in g:
            ax.fill_between(g.families, g.val_p05, g.val_p95, color=col, alpha=0.12)
    ax.axhline(0.9, color="k", lw=0.8, ls=":")
    ax.set_xlabel("Press-die families (crown die sets; integrated: assemblies)")
    ax.set_ylabel("Weighted geometric coverage")
    ax.set_ylim(0, 1)
    ax.set_title("Coverage vs tooling (geometric feasibility only; validated fit unevaluated)", fontsize=9)
    ax.legend(fontsize=7, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outdir / "coverage_vs_tooling.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 5))
    for status, col in (("geometric_feasible", "#2ca02c"), ("excluded", "#d62728")):
        g = assign[assign.status == status]
        ax.scatter(g.head_length, g.head_breadth, s=6, c=col, alpha=0.5, label=f"{status} ({len(g)})")
    ax.set_xlabel("Head length (mm)")
    ax.set_ylabel("Head breadth (mm)")
    ax.set_title("Recommended exploratory set: who is covered", fontsize=9)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(outdir / "covered_heads.png", dpi=150)
    plt.close(fig)


def _md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(f"{v:.3f}" if isinstance(v, float) else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def summary(outdir: Path, cfg, man, sel, mc, assign, excl, dims):
    s = sel.copy()
    keep = ["architecture", "families", "train_cov", "train_cov_greedy", "val_cov", "status", "mip_gap"]
    keep += [c for c in ("val_p05", "val_p95") if c in s]
    m = mc.drop(columns=["assemblies"])
    ex = excl[excl.status.str.startswith("reason:")][["status", "n"]]
    txt = f"""# Run summary: {man.get('scenario') or 'default'}

**{man['label']}**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: {man['n_heads']}; catalogue: {man['n_crowns']} crowns, {man['n_assemblies']} crown+lower assemblies
- Calibrated radial offset {man['radial_offset']:.1f} mm; allowances {man['allowances_mm']:.2f} mm
  (incl. sampling bound {man['sampling_bound_mm']:.2f} mm); fillable pad gap {man['pad_window_mm'][0]:.1f}-{man['pad_window_mm'][1]:.1f} mm
- Config hash `{man['config_hash']}`, seed {man['seed']}, runtime {man['runtime_s']:.0f} s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

{_md(s[keep])}

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

{_md(m)}

## Recommended exploratory set

{man['recommended_note']}: `{', '.join(man['recommended'])}`

{_md(dims[[c for c in ('crown_id', 'inner_length', 'inner_breadth', 'inner_height_above_tragion', 'crown_mass_kg_est', 'status') if c in dims]])}

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

{_md(ex)}

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
"""
    (outdir / "SUMMARY.md").write_text(txt)
