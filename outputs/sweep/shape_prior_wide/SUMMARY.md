# Run summary: shape_prior_wide

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 31.5 mm; allowances 8.18 mm
  (incl. sampling bound 2.68 mm); fillable pad gap 11.9-27.5 mm
- Config hash `4e25be73f9af`, seed 20261003, runtime 904 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.287 | 0.287 | 0.317 | optimal | 0.000 |
| size_only | 2 | 0.415 | 0.400 | 0.480 | optimal | 0.000 |
| size_only | 3 | 0.474 | 0.474 | 0.511 | optimal | 0.000 |
| size_only | 4 | 0.509 | 0.509 | 0.553 | optimal | 0.000 |
| size_only | 5 | 0.541 | 0.541 | 0.565 | optimal | 0.000 |
| size_only | 6 | 0.565 | 0.565 | 0.579 | optimal | 0.000 |
| shape_integrated | 1 | 0.536 | 0.536 | 0.477 | optimal | 0.000 |
| shape_integrated | 2 | 0.696 | 0.692 | 0.674 | optimal | 0.000 |
| shape_integrated | 3 | 0.787 | 0.765 | 0.786 | optimal | 0.000 |
| shape_integrated | 4 | 0.845 | 0.812 | 0.854 | optimal | 0.000 |
| shape_integrated | 5 | 0.873 | 0.845 | 0.871 | optimal | 0.000 |
| shape_integrated | 6 | 0.888 | 0.877 | 0.900 | optimal | 0.000 |
| modular | 1 | 0.663 | 0.648 | 0.750 | optimal | 0.000 |
| modular | 2 | 0.830 | 0.789 | 0.813 | optimal | 0.000 |
| modular | 3 | 0.885 | 0.868 | 0.862 | optimal | 0.000 |
| modular | 4 | 0.911 | 0.899 | 0.919 | optimal | 0.000 |
| modular | 5 | 0.929 | 0.920 | 0.943 | optimal | 0.000 |
| modular | 6 | 0.940 | 0.933 | 0.924 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 240000.000 | 5 | 5 | 10 | 5 | 0.859 | 0.840 |
| shape_integrated | 0.900 | optimal | 0.000 | 336000.000 | 6 | 7 | 14 | 7 | 0.903 | 0.909 |
| shape_integrated | 0.950 | optimal | 0.000 | 624000.000 | 12 | 13 | 26 | 13 | 0.951 | 0.926 |
| modular | 0.850 | optimal | 0.000 | 117000.000 | 3 | 3 | 6 | 6 | 0.854 | 0.841 |
| modular | 0.900 | optimal | 0.000 | 157500.000 | 4 | 4 | 8 | 9 | 0.903 | 0.899 |
| modular | 0.950 | optimal | 0.000 | 310500.000 | 8 | 8 | 16 | 15 | 0.950 | 0.952 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S09-L02, S09-L20, G055-L01, G055-L11, G055-L20, G070-L13, G070-L20, G075-L20, G075-L22`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S09 | 255.680 | 212.411 | 158.817 | 2.720 | EXPLORATORY |
| G055 | 270.000 | 219.000 | 175.500 | 2.980 | EXPLORATORY |
| G070 | 282.000 | 219.000 | 163.500 | 3.000 | EXPLORATORY |
| G075 | 282.000 | 231.000 | 175.500 | 3.170 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_tight | 21 |
| reason:pad_between_steps | 16 |
| reason:pad_too_loose | 11 |
| reason:field_of_view | 10 |
| reason:nose | 7 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
