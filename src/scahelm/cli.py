"""Command-line entry point: `python -m scahelm <command>`."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import ROOT


def main(argv=None):
    ap = argparse.ArgumentParser(prog="scahelm", description="SCA helm fit/coverage toolchain (exploratory)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="full pipeline for one scenario")
    r.add_argument("--source", default="synthetic",
                   help="synthetic | ansur2 | path to a canonical measurement CSV")
    r.add_argument("--scenario", default=None, help="name in config/scenarios.yaml")
    r.add_argument("--n", type=int, default=None, help="participants (stratified subsample)")
    r.add_argument("--out", default=None)
    r.add_argument("--processes", type=int, default=4)
    r.add_argument("--bootstrap", type=int, default=None)
    r.add_argument("--no-cad", action="store_true")

    q = sub.add_parser("ingest", help="verify and canonicalise ANSUR II; write data/processed + quality report")

    s = sub.add_parser("sweep", help="run every scenario in config/scenarios.yaml")
    s.add_argument("--source", default="ansur2")
    s.add_argument("--n", type=int, default=600)
    s.add_argument("--processes", type=int, default=4)
    s.add_argument("--step", type=float, default=12.0,
                   help="coarser catalogue grid step (mm) for sweeps; the main run uses config")

    a = ap.parse_args(argv)
    if a.cmd == "run":
        from .run import run
        name = a.scenario or "default"
        out = Path(a.out) if a.out else ROOT / "outputs" / f"{a.source if a.source in ('synthetic', 'ansur2') else 'custom'}_{name}"
        run(a.source, a.scenario, out, a.n, a.processes, a.bootstrap, cad=not a.no_cad)
    elif a.cmd == "ingest":
        from . import ingest
        t, prov = ingest.load_ansur2(ROOT / "data" / "raw" / "ansur2")
        d = ROOT / "data" / "processed"
        d.mkdir(parents=True, exist_ok=True)
        t.to_csv(d / "ansur2_canonical.csv", index=False)
        ingest.quality_report(t).to_csv(d / "ansur2_quality.csv", index=False)
        (d / "ansur2_provenance.json").write_text(json.dumps(prov, indent=2))
        print(ingest.quality_report(t).to_string(index=False))
    elif a.cmd == "sweep":
        import yaml
        from .run import run
        from .sweep import collect
        names = list(yaml.safe_load(open(ROOT / "config" / "scenarios.yaml")))
        coarse = {"catalogue": {"length_steps": a.step, "breadth_steps": a.step, "height_steps": a.step}}
        for nm in names:
            run(a.source, nm, ROOT / "outputs" / "sweep" / nm, a.n, a.processes, bootstrap=0, cad=False,
                overrides=coarse)
        collect(ROOT / "outputs" / "sweep")


if __name__ == "__main__":
    main()
