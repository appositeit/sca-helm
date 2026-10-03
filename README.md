# sca-helm: standardised pressed SCA helms

This is a research and optimisation toolchain for a small family of pressed-steel helms for SCA armoured combat, initially targeting Lochac. It implements work steps 1–5 of [`docs/design_spec_v0.1.md`](docs/design_spec_v0.1.md).

> **Status: exploratory.** Every result is *geometric feasibility* on a surrogate population under labelled assumptions. Nothing here is a validated design or a claim about protection. The protective-stack, stability, retention and motion-range criteria are reported as **unevaluated** until physical tests exist ([`docs/validation_plan.md`](docs/validation_plan.md)).

## What is here

| Deliverable (spec §11) | Where |
| --- | --- |
| Rules register and current rules matrix | [`config/rules_register.yaml`](config/rules_register.yaml), [`docs/rules_matrix.md`](docs/rules_matrix.md) |
| Source, access and licensing register | [`config/data_sources.yaml`](config/data_sources.yaml), [`docs/data_sources.md`](docs/data_sources.md) |
| Population definition and data-quality report | [`docs/population.md`](docs/population.md), `outputs/*/data_quality.csv` |
| Foam test protocol, property schema, import path | [`docs/foam_test_protocol.md`](docs/foam_test_protocol.md) |
| Fit evaluator and coverage optimiser | `src/scahelm/fit.py`, `src/scahelm/optimise.py` |
| Coverage-vs-tooling plots; per-head assignment and exclusion CSVs | `outputs/<run>/` |
| Candidate dimensions, pad recipes, CAD (STEP/STL/DXF), all labelled EXPLORATORY | `outputs/<run>/candidate_*.csv`, `assignments.csv`, `cad/` |
| Manufacturing comparison, lower compatibility matrix, cost assumptions | [`docs/manufacturing.md`](docs/manufacturing.md), `outputs/<run>/lower_compatibility.csv` |
| Recommendation | [`docs/findings.md`](docs/findings.md) |

## Quick start

```bash
pip install -e .[test,step]          # step = OpenCASCADE bindings for STEP export (optional)
python -m pytest                     # numerical and geometric checks (~5 min)

python -m scahelm run --source synthetic --n 400            # SYNTHETIC fixture, no data needed
python -m scahelm ingest                                     # verify ANSUR II checksums, canonicalise
python -m scahelm run --source ansur2 --n 2000               # surrogate population run
python -m scahelm sweep --source ansur2 --n 900              # sensitivity scenarios (config/scenarios.yaml)
```

Each run writes `outputs/<source>_<scenario>/` containing:

- `SUMMARY.md`
- `manifest.json`: config hash, seed, dataset checksums, package versions, solver
- `config_used.yaml`
- coverage and min-cost tables
- bootstrap intervals
- `assignments.csv`: per head, the assembly, pose and pad recipe, or the exclusion reasons
- plots
- CAD files

## How it works (one paragraph per stage)

1. **Heads** (`heads.py`). Each participant is modelled as a smooth piecewise superquadric. It is built from measured head length, breadth, tragion-to-top height and circumference (which sets the squareness), plus face landmarks. Shape parameters that the scalar tables lack are drawn from *labelled* priors; see `docs/population.md`. Units are mm. Axes: x lateral, y anterior, z superior, with the origin at mid-tragion.
2. **Candidate crowns** (`shells.py`). There are two families:
   - a scaled single-shape *size-only* family;
   - a *shape-variable* grid over inner length, breadth and height.

   Both are smooth convex surfaces, so they have no undercuts. The minimum radius of curvature is enforced. The head-to-shell offset is calibrated so a typical head's pad gaps sit mid-window. *Lower components* (eye line, face-plate depth, chin drop) are offsets from each crown's interface, so every lower can actually be built on its crown.
3. **Liner** (`liner.py`). Discrete pad stacks come from a purchasable catalogue: a protective soft base plus firm or soft fitting layers. A linear series-spring screening model checks installed strain, contact pressure, the 12.7 mm minimum padding, maximum depth and compression reserve. **All foam properties are placeholders**, so stability stays unevaluated.
4. **Fit predicate** (`fit.py`, spec §7). Each criterion returns pass, fail or unevaluated. The geometric checks are:
   - hard contact (intrusion);
   - pad fill in five support zones;
   - unpadded clearance;
   - ear clearance;
   - seam bead;
   - eye line and vertical field of view;
   - nose and chin clearance;
   - the rules-derived 25.4 mm coverage below the chin.

   Head pose is searched over a bounded translation grid. Clearances are true surface distances (minimum over tangent planes for the convex shell), not radial differences. Discretisation bounds are added to the allowances. The fast path (a distance field) re-checks every near-threshold case exactly, and the tests confirm it reproduces the exhaustive evaluation.
5. **Selection** (`optimise.py`). Greedy set cover is the baseline, with an exact MILP (HiGHS via `scipy.optimize.milp`) over the finite catalogue. Dies are counted per architecture:
   - modular: one crown die set per family, with laser-cut lower variants at their own design cost;
   - integrated: each assembly is its own pressing;
   - left and right halves are distinct dies unless configured otherwise.

   The MILP is checked against exhaustive enumeration in the tests. Validation is held out by participant. The bootstrap re-runs the selection, so intervals include selection variability. Results are optimal **over the catalogue only**.

## Labelling conventions

Reports separate **retrieved facts** (rules, dataset properties), **design decisions**, **provisional scenarios** (`config/scenarios.yaml`) and **experimental results**. There are no experimental results yet. Config values carry `[RULE]`, `[DATA]`, `[ASSUMPTION]` or `[DECISION]` tags.

## Data

ANSUR II public files are stored unmodified in `data/raw/ansur2/` (US Army, cleared for unlimited public release), and their sha256 is checked on load. Restricted datasets must never be committed; `data/raw/restricted/` is git-ignored.
