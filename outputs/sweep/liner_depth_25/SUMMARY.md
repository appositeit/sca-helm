# Run summary: liner_depth_25

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 27.0 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-22.8 mm
- Config hash `d917f9e7451b`, seed 20261003, runtime 1092 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.243 | 0.243 | 0.303 | optimal | 0.000 |
| size_only | 2 | 0.378 | 0.369 | 0.412 | optimal | 0.000 |
| size_only | 3 | 0.466 | 0.466 | 0.556 | optimal | 0.000 |
| size_only | 4 | 0.543 | 0.543 | 0.615 | optimal | 0.000 |
| size_only | 5 | 0.588 | 0.588 | 0.636 | optimal | 0.000 |
| size_only | 6 | 0.620 | 0.620 | 0.698 | optimal | 0.000 |
| shape_integrated | 1 | 0.368 | 0.368 | 0.394 | optimal | 0.000 |
| shape_integrated | 2 | 0.571 | 0.546 | 0.582 | optimal | 0.000 |
| shape_integrated | 3 | 0.668 | 0.668 | 0.680 | optimal | 0.000 |
| shape_integrated | 4 | 0.725 | 0.725 | 0.751 | optimal | 0.000 |
| shape_integrated | 5 | 0.772 | 0.768 | 0.791 | optimal | 0.000 |
| shape_integrated | 6 | 0.806 | 0.800 | 0.803 | optimal | 0.000 |
| modular | 1 | 0.499 | 0.499 | 0.602 | optimal | 0.000 |
| modular | 2 | 0.691 | 0.690 | 0.738 | optimal | 0.000 |
| modular | 3 | 0.801 | 0.794 | 0.803 | optimal | 0.000 |
| modular | 4 | 0.851 | 0.841 | 0.846 | optimal | 0.000 |
| modular | 5 | 0.893 | 0.882 | 0.895 | optimal | 0.000 |
| modular | 6 | 0.919 | 0.908 | 0.905 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 384000.000 | 8 | 8 | 16 | 8 | 0.852 | 0.871 |
| shape_integrated | 0.900 | optimal | 0.000 | 528000.000 | 11 | 11 | 22 | 11 | 0.900 | 0.854 |
| shape_integrated | 0.950 | optimal | 0.000 | 816000.000 | 13 | 17 | 34 | 17 | 0.950 | 0.904 |
| modular | 0.850 | time_limit | 0.292 | 195000.000 | 5 | 5 | 10 | 10 | 0.854 | 0.848 |
| modular | 0.900 | time_limit | 0.215 | 237000.000 | 6 | 6 | 12 | 14 | 0.901 | 0.895 |
| modular | 0.950 | time_limit | 0.139 | 355500.000 | 9 | 9 | 18 | 21 | 0.950 | 0.920 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S11-L20, S14-L02, S14-L20, S14-L23, S19-L13, S19-L20, S19-L23, G053-L02, G053-L19, G070-L11, G070-L22, G071-L01, G071-L10, G071-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S11 | 251.302 | 207.249 | 157.189 | 2.660 | EXPLORATORY |
| S14 | 258.208 | 212.944 | 161.509 | 2.780 | EXPLORATORY |
| S19 | 269.718 | 222.437 | 168.708 | 2.990 | EXPLORATORY |
| G053 | 261.000 | 210.000 | 147.000 | 2.720 | EXPLORATORY |
| G070 | 273.000 | 210.000 | 159.000 | 2.850 | EXPLORATORY |
| G071 | 273.000 | 210.000 | 171.000 | 2.910 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_tight | 28 |
| reason:pad_between_steps | 14 |
| reason:pad_too_loose | 9 |
| reason:nose | 8 |
| reason:field_of_view | 4 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
