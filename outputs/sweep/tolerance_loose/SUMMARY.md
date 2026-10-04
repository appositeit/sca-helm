# Run summary: tolerance_loose

**ansur2 surrogate (scalar measurements + assumed shape priors)**. All coverage figures are *geometric feasibility* under the configured
assumptions. `validated_fit` is **unevaluated** for every head because foam stability, retention,
protective-stack and motion-range criteria have no measured data yet (spec section 7).

- Heads: 600; catalogue: 97 crowns, 2619 crown+lower assemblies
- Calibrated radial offset 33.0 mm; allowances 10.82 mm
  (incl. sampling bound 1.82 mm); fillable pad gap 11.9-27.5 mm
- Config hash `b258fe7c998a`, seed 20261003, runtime 724 s
- Optimality is over this finite catalogue only; it is not a global optimum over surfaces.

## Coverage by number of press-die families

| architecture | families | train_cov | train_cov_greedy | val_cov | status | mip_gap |
|---|---|---|---|---|---|---|
| size_only | 1 | 0.318 | 0.318 | 0.372 | optimal | 0.000 |
| size_only | 2 | 0.436 | 0.427 | 0.452 | optimal | 0.000 |
| size_only | 3 | 0.509 | 0.502 | 0.493 | optimal | 0.000 |
| size_only | 4 | 0.557 | 0.557 | 0.530 | optimal | 0.000 |
| size_only | 5 | 0.599 | 0.587 | 0.592 | optimal | 0.000 |
| size_only | 6 | 0.620 | 0.611 | 0.589 | optimal | 0.000 |
| shape_integrated | 1 | 0.673 | 0.673 | 0.603 | optimal | 0.000 |
| shape_integrated | 2 | 0.810 | 0.803 | 0.857 | optimal | 0.000 |
| shape_integrated | 3 | 0.895 | 0.880 | 0.860 | optimal | 0.000 |
| shape_integrated | 4 | 0.926 | 0.915 | 0.936 | optimal | 0.000 |
| shape_integrated | 5 | 0.952 | 0.936 | 0.932 | optimal | 0.000 |
| shape_integrated | 6 | 0.969 | 0.955 | 0.946 | optimal | 0.000 |
| modular | 1 | 0.795 | 0.795 | 0.796 | optimal | 0.000 |
| modular | 2 | 0.917 | 0.878 | 0.938 | optimal | 0.000 |
| modular | 3 | 0.961 | 0.958 | 0.952 | optimal | 0.000 |
| modular | 4 | 0.982 | 0.976 | 0.971 | optimal | 0.000 |
| modular | 5 | 0.988 | 0.985 | 0.974 | optimal | 0.000 |
| modular | 6 | 0.990 | 0.989 | 0.957 | optimal | 0.000 |

`val_cov`: the training-selected set scored on held-out participants (participant-level split).
`val_p05/p95`: bootstrap interval that re-runs selection on resampled training heads.

## Cheapest tooling reaching each coverage target (training heads)

Tooling costs are placeholder AUD assumptions (config `costs`), for ranking only.

| architecture | target | status | mip_gap | tooling_cost_AUD | crown_families | press_die_sets | press_dies | complete_assemblies | train_cov | val_cov |
|---|---|---|---|---|---|---|---|---|---|---|
| size_only | 0.850 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.900 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| size_only | 0.950 | infeasible_target | nan | nan | 0 | 0 | 0 | 0 | 0.000 | 0.000 |
| shape_integrated | 0.850 | optimal | 0.000 | 144000.000 | 3 | 3 | 6 | 3 | 0.883 | 0.900 |
| shape_integrated | 0.900 | optimal | 0.000 | 192000.000 | 4 | 4 | 8 | 4 | 0.902 | 0.922 |
| shape_integrated | 0.950 | optimal | 0.000 | 240000.000 | 5 | 5 | 10 | 5 | 0.952 | 0.941 |
| modular | 0.850 | optimal | 0.000 | 76500.000 | 2 | 2 | 4 | 3 | 0.855 | 0.890 |
| modular | 0.900 | optimal | 0.000 | 79500.000 | 2 | 2 | 4 | 5 | 0.905 | 0.924 |
| modular | 0.950 | optimal | 0.000 | 118500.000 | 3 | 3 | 6 | 7 | 0.951 | 0.945 |

## Recommended exploratory set

cheapest modular set reaching 0.9 on training heads: `S13-L02, S13-L20, S13-L23, G075-L11, G075-L20`

| crown_id | inner_length | inner_breadth | inner_height_above_tragion | crown_mass_kg_est | status |
|---|---|---|---|---|---|
| S13 | 267.978 | 223.145 | 166.085 | 2.940 | EXPLORATORY |
| G075 | 285.000 | 234.000 | 177.000 | 3.220 | EXPLORATORY |

Exclusion reasons (heads not fitted by the recommended set; a head may have several):

| status | n |
|---|---|
| reason:pad_too_loose | 19 |
| reason:field_of_view | 15 |
| reason:pad_too_tight | 12 |
| reason:pad_between_steps | 8 |
| reason:nose | 5 |

Per-head assignment, pose and pad recipe: `assignments.csv`. Excluded-head characteristics:
`excluded_characteristics.csv`. CAD (EXPLORATORY): `cad/`.
