# Run summary: liner_depth_35

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 33.0 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-32.2 mm
- Config hash `825050d1c390`, seed 20261003, runtime 701 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.531 | 0.531 | 0.602 | optimal | 0.000 |
| size_only | 2 | 0.670 | 0.631 | 0.685 | optimal | 0.000 |
| size_only | 3 | 0.730 | 0.715 | 0.734 | optimal | 0.000 |
| size_only | 4 | 0.755 | 0.746 | 0.743 | optimal | 0.000 |
| size_only | 5 | 0.773 | 0.765 | 0.777 | optimal | 0.000 |
| size_only | 6 | 0.784 | 0.783 | 0.782 | optimal | 0.000 |
| shape_integrated | 1 | 0.841 | 0.841 | 0.874 | optimal | 0.000 |
| shape_integrated | 2 | 0.934 | 0.913 | 0.962 | optimal | 0.000 |
| shape_integrated | 3 | 0.970 | 0.963 | 0.957 | optimal | 0.000 |
| shape_integrated | 4 | 0.989 | 0.981 | 0.976 | optimal | 0.000 |
| shape_integrated | 5 | 0.994 | 0.988 | 0.990 | optimal | 0.000 |
| shape_integrated | 6 | 0.997 | 0.994 | 0.976 | optimal | 0.000 |
| modular | 1 | 0.920 | 0.910 | 0.952 | optimal | 0.000 |
| modular | 2 | 0.988 | 0.960 | 0.981 | optimal | 0.000 |
| modular | 3 | 0.995 | 0.991 | 0.988 | optimal | 0.000 |
| modular | 4 | 0.997 | 0.995 | 0.997 | optimal | 0.000 |
| modular | 5 | 0.997 | 0.997 | 0.993 | optimal | 0.000 |
| modular | 6 | 0.997 | 0.997 | 0.993 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.907 | 0.935 |
| shape_integrated | 0.900 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.934 | 0.962 |
| shape_integrated | 0.950 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.951 | 0.971 |
| modular | 0.850 | optimal | 0.000 | 39000.000 | 1 | 1 | 2 | 2 | 0.879 | 0.916 |
| modular | 0.900 | optimal | 0.000 | 40500.000 | 1 | 1 | 2 | 3 | 0.910 | 0.943 |
| modular | 0.950 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.951 | 0.981 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S15-L11, S15-L13, S15-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S15 | 272.630 | 227.019 | 168.968 | 3.020 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_loose | 27 |
| reason:field_of_view | 22 |
| reason:pad_too_tight | 7 |
| reason:pad_between_steps | 2 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
