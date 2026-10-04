# Run summary: padding_compressed_basis

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 31.5 mm; allowances 7.32 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 15.0-27.5 mm
- Config hash `9c28bc4c6b0a`, seed 20261003, runtime 813 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.477 | 0.477 | 0.505 | optimal | 0.000 |
| size_only | 2 | 0.610 | 0.603 | 0.655 | optimal | 0.000 |
| size_only | 3 | 0.686 | 0.681 | 0.733 | optimal | 0.000 |
| size_only | 4 | 0.721 | 0.713 | 0.763 | optimal | 0.000 |
| size_only | 5 | 0.749 | 0.738 | 0.772 | optimal | 0.000 |
| size_only | 6 | 0.768 | 0.762 | 0.789 | optimal | 0.000 |
| shape_integrated | 1 | 0.691 | 0.691 | 0.710 | optimal | 0.000 |
| shape_integrated | 2 | 0.864 | 0.829 | 0.863 | optimal | 0.000 |
| shape_integrated | 3 | 0.912 | 0.906 | 0.898 | optimal | 0.000 |
| shape_integrated | 4 | 0.953 | 0.942 | 0.941 | optimal | 0.000 |
| shape_integrated | 5 | 0.970 | 0.960 | 0.978 | optimal | 0.000 |
| shape_integrated | 6 | 0.980 | 0.972 | 0.966 | optimal | 0.000 |
| modular | 1 | 0.809 | 0.809 | 0.821 | optimal | 0.000 |
| modular | 2 | 0.952 | 0.914 | 0.962 | optimal | 0.000 |
| modular | 3 | 0.977 | 0.972 | 0.983 | optimal | 0.000 |
| modular | 4 | 0.990 | 0.982 | 0.983 | optimal | 0.000 |
| modular | 5 | 0.995 | 0.991 | 0.988 | optimal | 0.000 |
| modular | 6 | 0.997 | 0.994 | 0.988 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 96000.000 | 2 | 2 | 4 | 2 | 0.855 | 0.872 |
| shape_integrated | 0.900 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.910 | 0.912 |
| shape_integrated | 0.950 | optimal | 0.000 | 192000.000 | 4 | 4 | 8 | 4 | 0.952 | 0.931 |
| modular | 0.850 | optimal | 0.000 | 75000.000 | 2 | 2 | 4 | 2 | 0.862 | 0.849 |
| modular | 0.900 | optimal | 0.000 | 78000.000 | 2 | 2 | 4 | 4 | 0.901 | 0.912 |
| modular | 0.950 | optimal | 0.000 | 81000.000 | 2 | 2 | 4 | 6 | 0.952 | 0.962 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S13-L11, S13-L14, S13-L20, G055-L11`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S13 | 264.960 | 220.121 | 164.581 | 2.890 | EXPLORATORY |
| G055 | 270.000 | 219.000 | 175.500 | 2.980 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_loose | 38 |
| reason:pad_too_tight | 20 |
| reason:field_of_view | 5 |
| reason:pad_between_steps | 2 |
| reason:nose | 2 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
