# Run summary: pressure_band_wide

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 30.0 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-27.5 mm
- Config hash `a3dc7ca45f05`, seed 20261003, runtime 669 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.672 | 0.672 | 0.720 | optimal | 0.000 |
| size_only | 2 | 0.802 | 0.767 | 0.801 | optimal | 0.000 |
| size_only | 3 | 0.844 | 0.843 | 0.863 | optimal | 0.000 |
| size_only | 4 | 0.866 | 0.857 | 0.882 | optimal | 0.000 |
| size_only | 5 | 0.879 | 0.869 | 0.887 | optimal | 0.000 |
| size_only | 6 | 0.889 | 0.878 | 0.887 | optimal | 0.000 |
| shape_integrated | 1 | 0.813 | 0.813 | 0.816 | optimal | 0.000 |
| shape_integrated | 2 | 0.922 | 0.889 | 0.941 | optimal | 0.000 |
| shape_integrated | 3 | 0.966 | 0.962 | 0.966 | optimal | 0.000 |
| shape_integrated | 4 | 0.987 | 0.980 | 0.978 | optimal | 0.000 |
| shape_integrated | 5 | 0.993 | 0.989 | 0.983 | optimal | 0.000 |
| shape_integrated | 6 | 0.997 | 0.993 | 0.993 | optimal | 0.000 |
| modular | 1 | 0.893 | 0.893 | 0.924 | optimal | 0.000 |
| modular | 2 | 0.987 | 0.954 | 0.985 | optimal | 0.000 |
| modular | 3 | 0.994 | 0.994 | 0.997 | optimal | 0.000 |
| modular | 4 | 0.997 | 0.997 | 0.997 | optimal | 0.000 |
| modular | 5 | 0.997 | 0.997 | 0.997 | optimal | 0.000 |
| modular | 6 | 0.997 | 0.997 | 0.997 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | optimal | 0.000 | 192000.000 | 4 | 4 | 8 | 4 | 0.852 | 0.877 |
| size_only | 0.900 | optimal | 0.000 | 480000.000 | 10 | 10 | 20 | 10 | 0.901 | 0.908 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.898 | 0.929 |
| shape_integrated | 0.900 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.922 | 0.941 |
| shape_integrated | 0.950 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.954 | 0.962 |
| modular | 0.850 | optimal | 0.000 | 40500.000 | 1 | 1 | 2 | 3 | 0.893 | 0.924 |
| modular | 0.900 | time_limit | 0.240 | 75000.000 | 2 | 2 | 4 | 2 | 0.900 | 0.901 |
| modular | 0.950 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.952 | 0.955 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S11-L20, S19-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S11 | 257.314 | 213.260 | 160.195 | 2.750 | EXPLORATORY |
| S19 | 275.826 | 228.603 | 171.720 | 3.090 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:nose | 21 |
| reason:field_of_view | 17 |
| reason:pad_too_tight | 10 |
| reason:pad_too_loose | 5 |
| reason:pad_between_steps | 2 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
