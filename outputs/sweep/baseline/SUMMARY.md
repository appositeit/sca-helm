# Run summary: baseline

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 30.0 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-27.5 mm
- Config hash `086af5ad4a77`, seed 20261003, runtime 744 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.489 | 0.489 | 0.535 | optimal | 0.000 |
| size_only | 2 | 0.621 | 0.604 | 0.653 | optimal | 0.000 |
| size_only | 3 | 0.697 | 0.668 | 0.750 | optimal | 0.000 |
| size_only | 4 | 0.730 | 0.725 | 0.763 | optimal | 0.000 |
| size_only | 5 | 0.762 | 0.754 | 0.792 | optimal | 0.000 |
| size_only | 6 | 0.789 | 0.776 | 0.770 | optimal | 0.000 |
| shape_integrated | 1 | 0.702 | 0.702 | 0.773 | optimal | 0.000 |
| shape_integrated | 2 | 0.844 | 0.811 | 0.855 | optimal | 0.000 |
| shape_integrated | 3 | 0.916 | 0.904 | 0.919 | optimal | 0.000 |
| shape_integrated | 4 | 0.951 | 0.928 | 0.964 | optimal | 0.000 |
| shape_integrated | 5 | 0.970 | 0.952 | 0.981 | optimal | 0.000 |
| shape_integrated | 6 | 0.979 | 0.967 | 0.981 | optimal | 0.000 |
| modular | 1 | 0.804 | 0.801 | 0.839 | optimal | 0.000 |
| modular | 2 | 0.957 | 0.905 | 0.951 | optimal | 0.000 |
| modular | 3 | 0.984 | 0.977 | 0.990 | optimal | 0.000 |
| modular | 4 | 0.991 | 0.987 | 0.974 | optimal | 0.000 |
| modular | 5 | 0.994 | 0.991 | 0.990 | optimal | 0.000 |
| modular | 6 | 0.994 | 0.994 | 0.974 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.904 | 0.924 |
| shape_integrated | 0.900 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.911 | 0.919 |
| shape_integrated | 0.950 | optimal | 0.000 | 192000.000 | 4 | 4 | 8 | 4 | 0.951 | 0.934 |
| modular | 0.850 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.852 | 0.863 |
| modular | 0.900 | optimal | 0.000 | 78000.000 | 2 | 2 | 4 | 4 | 0.903 | 0.884 |
| modular | 0.950 | optimal | 0.000 | 81000.000 | 2 | 2 | 4 | 6 | 0.957 | 0.951 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S11-L20, G055-L11, G055-L20, G055-L23`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S11 | 257.314 | 213.260 | 160.195 | 2.750 | EXPLORATORY |
| G055 | 267.000 | 216.000 | 174.000 | 2.930 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_tight | 15 |
| reason:pad_between_steps | 14 |
| reason:field_of_view | 13 |
| reason:nose | 10 |
| reason:pad_too_loose | 8 |
| reason:eye_line | 1 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
