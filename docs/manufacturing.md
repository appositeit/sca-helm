# Forming and fabrication: comparison and assumptions

Status: **desk study.** Every number below is either cited, derived from a formula shown here, or marked [ASSUMPTION]. None of it has been validated by forming simulation or prototypes.

## 1. Rules that constrain the process

From `rules_matrix.md` (current Society V2026.0 and Lochac v3.4):

| Constraint | Consequence |
| --- | --- |
| Finished steel ≥ 1.6 mm everywhere, face guard included | Measure the thinnest point after forming and grinding, not the stock |
| A pressed or domed skull must start from ≥ 2.0 mm stock (Society "must"; Lochac "should") | 2.0 mm stock leaves at most **20% thinning** anywhere. This is the key forming limit. |
| Cold-rolled steel (Society 12.4.2.2, A1008 cited) | Use a drawing-quality cold-rolled grade (e.g. AS/NZS 1595 CA2S-E/CA3S-E, or DC04 equivalents). Confirm the supplier's elongation and r-value. |
| Rivet spacing and type (Society: no blind or pop rivets; spacing set by rivet diameter) | Applies to crown-to-lower joints if riveted rather than welded |
| 1 inch (25.4 mm) dowel must not enter any opening (Society); face guard ≥ 25.4 mm below the chin | Sets the grille opening size and the lower edge (`lower.chin_coverage_margin`) |

## 2. Architectures compared

| | A. Left/right halves, sagittal seam (working interpretation) | B. Front/back halves, coronal seam | C. Pressed crown dome + fabricated lower |
| --- | --- | --- | --- |
| Draw direction | Lateral (x) | Anterior/posterior (y) | Vertical (z) |
| Draw depth (median shell, from the catalogue) | ≈ half inner breadth, ~100–110 mm | ≈ front or rear semi-axis, ~120–130 mm | ≈ tragion-to-top height, ~150–160 mm (to the brow line) |
| Undercut-free for the convex crown? | Yes: each half projects one-to-one onto the sagittal plane | Yes | Yes, above the equator |
| Dies per family | **2** (mirror images) unless one die can be shown to form both halves, e.g. symmetric tooling with a flipped blank. The default `halves_share_die: false` counts 2. | 2 (front and rear differ) | 1 |
| Seam | Along the crest. A raised comb could hide or stiffen it, and the inner weld bead must be ground (config `seam_bead_height`). | Across the crown, in the strike zone | Crown-to-lower joint near the brow and occiput |
| Lower and face integration | Possible: each half can carry its face and cheek. Depth then grows and the draw becomes asymmetric. | Front half carries the face | Separate laser-cut and bent lower; many variants per crown |
| Effect on coverage (this toolchain) | `shape_integrated` if the lower is pressed in; `modular` if the halves are trimmed to a crown interface | Not modelled separately; same crown geometry | `modular` |

The two-half welded construction is the user's proposal, so it stays a candidate throughout. The toolchain evaluates the crown geometry independently of the split plane: the split changes die count and cost, not fit. The split plane is configurable through the cost model (`costs.halves_share_die`) and through `export.shell_meshes`, which slices on x = 0.

## 3. Press force: a first-order estimate

For a drawn shell with punch perimeter *L*, sheet thickness *t* and ultimate tensile strength *UTS*, a common first estimate of draw force is *F ≈ L · t · UTS · k*. Here *k* is between 0.6 and 1.0, depending on draw ratio. Blank-holder force adds roughly a further 30–40%. (These are textbook rules of thumb for drawing; Schuler, *Metal Forming Handbook*, ch. 4, gives this form. Treat the figures as order-of-magnitude.)

| Input | Value | Status |
| --- | --- | --- |
| Punch perimeter, architecture A (sagittal outline of a median crown, length ~250 × height ~190) | ≈ 750 mm | Derived from the catalogue geometry |
| t | 2.0 mm | Rule-driven stock |
| UTS, drawing-grade cold-rolled mild steel | 300–350 MPa | Typical datasheet range [ASSUMPTION until the grade is chosen] |
| k | 1.0 | Conservative |

The estimate is *F* ≈ 750 × 2.0 × 350 × 1.0 ≈ **525 kN**, plus about 35% for the blank holder, giving about **710 kN (~72 tonne-force)** per half. A press rated around **100–150 t** would leave margin. **This is not a press selection.** Spec section 10 requires a documented forming model: confirm with a forming simulation (e.g. AutoForm or PAM-STAMP via a toolmaker) or a prototype draw before buying or hiring a press.

## 4. Main forming risks

| Risk | Why it matters | How to settle it |
| --- | --- | --- |
| Thinning > 20% at the pole of each half (the side of the skull for A, the crown for C) | It would break the 1.6 mm finished rule | Circle-grid strain analysis on the first draws. Consider two-stage draws, draw beads and lubrication. Hot forming is a fallback. |
| Wrinkling in the flange or at the sagittal edge | Scrap and poor seam fit-up | Blank-holder pressure trials |
| Springback | Inner surface off-target, which eats into the fit tolerance (`shell.manufacturing_tolerance`, default 1.5 mm) | Scan formed parts, then compensate the die. **An offset headform is not a usable die surface** (spec section 5). |
| Weld distortion along a 400–500 mm seam | Asymmetric halves | Fixture with tack sequence and backstep welding; scan before and after welding |
| Grinding the seam flush | Local thinning below 1.6 mm | Measure ultrasonically at the seam; limit grind depth |

## 5. Cost model (placeholders)

The figures are in `config/default.yaml` under `costs`. They are **[ASSUMPTION] placeholders** used only to rank options, and must be replaced with toolmaker quotes.

| Item | Placeholder (AUD) |
| --- | --- |
| Die per pressed half | 18,000 |
| Extra die cost to integrate face and jaw into the pressing (per half) | 6,000 |
| Lower variant design (laser program, bend fixture, first-article check) | 1,500 |
| Crown unit cost (blank, press time, trim, weld, grind) | 260 |
| Lower unit cost (laser, bend, attach) | 120 |

**Unit cost at batch volume V per family:** (die set + Σ lower designs) / V + crown unit + lower unit + liner + inspection + rejects. Rejects and inspection are unquantified. The min-cost tables in each run's `SUMMARY.md` show the tooling term only.

## 6. Inspection (to define before production; Gate D)

- **Thickness:** ultrasonic gauge at the predicted most-strained points, trim edges and ground seams. Accept only at ≥ 1.6 mm at every point.
- **Geometry:** a structured-light scan of the inner surface compared with the CAD inner surface. Report the deviation map and accept within the tolerance assumed in the fit analysis.
- **Seams:** visual inspection plus a cut-and-etch macro on first articles. Specify the bead height after grinding.
- **Grille:** check every opening with a 25.4 mm dowel; measure ligament widths.
