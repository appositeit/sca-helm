# Run summary: tolerance_tight

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 28.5 mm; allowances 5.07 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-27.5 mm
- Config hash `a52df3af4833`, seed 20261003, runtime 806 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.573 | 0.573 | 0.619 | optimal | 0.000 |
| size_only | 2 | 0.728 | 0.705 | 0.764 | optimal | 0.000 |
| size_only | 3 | 0.790 | 0.787 | 0.814 | optimal | 0.000 |
| size_only | 4 | 0.827 | 0.821 | 0.835 | optimal | 0.000 |
| size_only | 5 | 0.862 | 0.845 | 0.851 | optimal | 0.000 |
| size_only | 6 | 0.873 | 0.863 | 0.872 | optimal | 0.000 |
| shape_integrated | 1 | 0.683 | 0.683 | 0.735 | optimal | 0.000 |
| shape_integrated | 2 | 0.866 | 0.827 | 0.932 | optimal | 0.000 |
| shape_integrated | 3 | 0.925 | 0.903 | 0.929 | optimal | 0.000 |
| shape_integrated | 4 | 0.959 | 0.953 | 0.954 | optimal | 0.000 |
| shape_integrated | 5 | 0.974 | 0.968 | 0.983 | optimal | 0.000 |
| shape_integrated | 6 | 0.984 | 0.981 | 0.971 | optimal | 0.000 |
| modular | 1 | 0.826 | 0.826 | 0.871 | optimal | 0.000 |
| modular | 2 | 0.951 | 0.910 | 0.947 | optimal | 0.000 |
| modular | 3 | 0.990 | 0.984 | 0.978 | optimal | 0.000 |
| modular | 4 | 0.997 | 0.995 | 0.988 | optimal | 0.000 |
| modular | 5 | 1.000 | 0.999 | 0.988 | optimal | 0.000 |
| modular | 6 | 1.000 | 1.000 | 0.995 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | optimal | 0.000 | 240000.000 | 5 | 5 | 10 | 5 | 0.850 | 0.860 |
| size_only | 0.900 | optimal | 0.000 | 576000.000 | 12 | 12 | 24 | 12 | 0.901 | 0.932 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.852 | 0.869 |
| shape_integrated | 0.900 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.919 | 0.964 |
| shape_integrated | 0.950 | optimal | 0.000 | 192000.000 | 4 | 4 | 8 | 4 | 0.952 | 0.978 |
| modular | 0.850 | optimal | 0.000 | 75000.000 | 2 | 2 | 4 | 2 | 0.859 | 0.909 |
| modular | 0.900 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.901 | 0.935 |
| modular | 0.950 | optimal | 0.000 | 81000.000 | 2 | 2 | 4 | 6 | 0.951 | 0.947 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S13-L20, S13-L23, S20-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S13 | 258.924 | 214.071 | 161.573 | 2.780 | EXPLORATORY |
| S20 | 275.080 | 227.428 | 171.654 | 3.080 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_loose | 27 |
| reason:field_of_view | 19 |
| reason:pad_between_steps | 9 |
| reason:pad_too_tight | 8 |
| reason:nose | 3 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
