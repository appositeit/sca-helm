# Run summary: female_30

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 30.0 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-27.5 mm
- Config hash `89d3c34589ca`, seed 20261003, runtime 803 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.463 | 0.463 | 0.478 | optimal | 0.000 |
| size_only | 2 | 0.603 | 0.575 | 0.646 | optimal | 0.000 |
| size_only | 3 | 0.673 | 0.668 | 0.741 | optimal | 0.000 |
| size_only | 4 | 0.720 | 0.717 | 0.772 | optimal | 0.000 |
| size_only | 5 | 0.756 | 0.752 | 0.755 | optimal | 0.000 |
| size_only | 6 | 0.780 | 0.774 | 0.772 | optimal | 0.000 |
| shape_integrated | 1 | 0.676 | 0.676 | 0.754 | optimal | 0.000 |
| shape_integrated | 2 | 0.845 | 0.819 | 0.866 | optimal | 0.000 |
| shape_integrated | 3 | 0.910 | 0.902 | 0.933 | optimal | 0.000 |
| shape_integrated | 4 | 0.948 | 0.939 | 0.962 | optimal | 0.000 |
| shape_integrated | 5 | 0.965 | 0.960 | 0.978 | optimal | 0.000 |
| shape_integrated | 6 | 0.979 | 0.972 | 0.956 | optimal | 0.000 |
| modular | 1 | 0.779 | 0.778 | 0.885 | optimal | 0.000 |
| modular | 2 | 0.945 | 0.910 | 0.936 | optimal | 0.000 |
| modular | 3 | 0.981 | 0.974 | 0.978 | optimal | 0.000 |
| modular | 4 | 0.990 | 0.988 | 0.967 | optimal | 0.000 |
| modular | 5 | 0.995 | 0.993 | 0.972 | optimal | 0.000 |
| modular | 6 | 0.995 | 0.995 | 0.972 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.889 | 0.882 |
| shape_integrated | 0.900 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.902 | 0.922 |
| shape_integrated | 0.950 | optimal | 0.000 | 240000.000 | 5 | 5 | 10 | 5 | 0.954 | 0.956 |
| modular | 0.850 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.881 | 0.889 |
| modular | 0.900 | optimal | 0.000 | 78000.000 | 2 | 2 | 4 | 4 | 0.904 | 0.893 |
| modular | 0.950 | time_limit | 0.273 | 115500.000 | 3 | 3 | 6 | 5 | 0.953 | 0.939 |

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
