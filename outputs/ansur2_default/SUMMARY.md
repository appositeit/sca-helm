# Run summary: default

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 2000; catalogue: 255 crowns, 6885 crown+lower assemblies
- Calibrated radial offset 30.0 mm; allowances 7.48 mm
  (incl. sampling bound 1.98 mm); fillable pad gap 11.9-27.5 mm
- Config hash `d9bbe896208a`, seed 20261003, runtime 2342 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap | val_p05 | val_p95 |
|---|---|---|---|---|---|---|---|---|
| size_only | 1 | 0.442 | 0.442 | 0.450 | optimal | 0.000 | 0.441 | 0.450 |
| size_only | 2 | 0.589 | 0.573 | 0.626 | optimal | 0.000 | 0.563 | 0.626 |
| size_only | 3 | 0.669 | 0.669 | 0.665 | optimal | 0.000 | 0.645 | 0.671 |
| size_only | 4 | 0.717 | 0.703 | 0.717 | optimal | 0.000 | 0.705 | 0.726 |
| size_only | 5 | 0.746 | 0.735 | 0.752 | optimal | 0.000 | 0.725 | 0.752 |
| size_only | 6 | 0.768 | 0.764 | 0.775 | optimal | 0.000 | 0.757 | 0.780 |
| shape_integrated | 1 | 0.693 | 0.693 | 0.690 | optimal | 0.000 | 0.683 | 0.691 |
| shape_integrated | 2 | 0.866 | 0.828 | 0.847 | optimal | 0.000 | 0.827 | 0.847 |
| shape_integrated | 3 | 0.916 | 0.914 | 0.903 | optimal | 0.000 | 0.892 | 0.916 |
| shape_integrated | 4 | 0.944 | 0.939 | 0.937 | time_limit | 0.006 | 0.910 | 0.931 |
| shape_integrated | 5 | 0.960 | 0.958 | 0.957 | time_limit | 0.012 | 0.926 | 0.945 |
| shape_integrated | 6 | 0.974 | 0.974 | 0.954 | time_limit | 0.008 | 0.942 | 0.956 |
| modular | 1 | 0.820 | 0.814 | 0.793 | optimal | 0.000 | 0.769 | 0.803 |
| modular | 2 | 0.943 | 0.904 | 0.936 | time_limit | 0.035 | 0.867 | 0.900 |
| modular | 3 | 0.971 | 0.971 | 0.968 | time_limit | 0.021 | 0.936 | 0.963 |
| modular | 4 | 0.986 | 0.984 | 0.972 | time_limit | 0.011 | 0.964 | 0.978 |
| modular | 5 | 0.992 | 0.992 | 0.988 | time_limit | 0.007 | 0.967 | 0.983 |
| modular | 6 | 0.996 | 0.996 | 0.988 | time_limit | 0.003 | 0.972 | 0.985 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.866 | 0.847 |
| shape_integrated | 0.900 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.912 | 0.873 |
| shape_integrated | 0.950 | optimal | 0.000 | 240000.000 | 5 | 5 | 10 | 5 | 0.958 | 0.947 |
| modular | 0.850 | time_limit | 0.560 | 75000.000 | 2 | 2 | 4 | 2 | 0.857 | 0.853 |
| modular | 0.900 | time_limit | 0.481 | 78000.000 | 2 | 2 | 4 | 4 | 0.910 | 0.918 |
| modular | 0.950 | time_limit | 0.500 | 117000.000 | 3 | 3 | 6 | 6 | 0.951 | 0.937 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S13-L20, G226-L01, G226-L11, G226-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S13 | 262.892 | 216.860 | 163.668 | 2.850 | EXPLORATORY |
| G226 | 280.000 | 226.000 | 170.000 | 3.080 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:field_of_view | 71 |
| reason:pad_too_loose | 68 |
| reason:pad_too_tight | 32 |
| reason:nose | 28 |
| reason:pad_between_steps | 14 |
| reason:unpadded_gap | 1 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.

## Addendum: size-only crowns with laser-cut lower variants

Added after the run, from the saved feasibility matrix (`feasibility.npz`, same heads, same split). These rows have no bootstrap interval. See `coverage_size_only_modular.csv`; they also appear as `size_only_modular` in `coverage_by_families.csv` and the plot.

| families | train_cov | val_cov | status |
|---|---|---|---|
| 1 | 0.820 | 0.793 | optimal |
| 2 | 0.943 | 0.951 | optimal |
| 3 | 0.972 | 0.959 | optimal |
| 4 | 0.986 | 0.972 | optimal |
| 5 | 0.991 | 0.975 | optimal |
| 6 | 0.993 | 0.985 | optimal |

Scaled single-shape crowns combined with lower variants match the shape-variable modular family. In this surrogate, the coverage gain comes from the lower variants, not from crown shape freedom.
