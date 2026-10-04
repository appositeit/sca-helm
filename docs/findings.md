# Findings and recommendation (exploratory, 4 October 2026)

This page separates **retrieved facts**, **model results** (geometric feasibility on a surrogate population under labelled assumptions), **design decisions**, and **my opinions**. There are no experimental results yet. Nothing here says a helm protects anyone.

Main run: `outputs/ansur2_default/` (2,000 ANSUR II participants, 1,400 training and 600 held out, 255 crowns, 6,885 crown+lower assemblies). Sensitivity: `outputs/sweep/` (600 participants per scenario, coarser 12 mm catalogue).

## 1. Retrieved facts that constrain the design

The rules come from `rules_matrix.md`. The current documents are Lochac Fighters' Handbook v3.4 (in force since July 2024) and the Society Armored Combat Rattan Handbook V2026.0 (effective 22 September 2026). The Society text is newer and stricter in places, and kingdoms may not set lower standards without a variance. I found no Lochac variance for helms.

| Requirement | Governing value | Model use |
| --- | --- | --- |
| Finished steel thickness, face guard included | ≥ 1.6 mm at the thinnest point | Forming limit (see the manufacturing section) |
| Stock for a pressed or domed skull | ≥ 2.0 mm (Society "must") | Leaves at most 20% thinning |
| Resilient padding where the helm can contact the head | ≥ 12.7 mm | `liner.min_padding`. The basis (compressed or installed) is not stated, so both are swept. |
| Face guard extends below the chin and jaw | ≥ 25.4 mm | `lower.chin_coverage_margin` |
| 1 inch dowel must not enter any opening (Society) | Opening < 25.4 mm | DXF grille openings are ≤ 24 mm |
| Plate (laser-cut) grille in place of round bars | **No explicit rule. A marshal decision.** | Flagged; ask the Lochac Kingdom Armoured Combat Marshal (armoured@lochac.sca.org) |

**Data:**

- ANSUR II (US Army 2012) is the only public individual-level source with tragion-to-top height. It is stored and checksummed.
- NIOSH 2003 (civilian, n = 3,997) is public but lacks head height. It is a planned cross-check.
- No public full-cranium scan set covers this population. Headspace and LYHM need an academic signatory; CAESAR costs about AUD 1,770.
- **Gate A (data) is not passed.**

## 2. Model results: coverage vs tooling

Coverage is the weighted share of **held-out** heads that are geometrically feasible, with 15% female (an assumption). The numbers in brackets are bootstrap 5–95% intervals that re-run the selection.

| Press-die families | Size-only, one fixed lower | Size-only crowns + laser-cut lowers* | Shape-variable, lower pressed in | Shape-variable crowns + laser-cut lowers |
| --- | --- | --- | --- | --- |
| 1 | 0.45 [0.44–0.45] | 0.79 | 0.69 [0.68–0.69] | 0.79 [0.77–0.80] |
| 2 | 0.63 [0.56–0.63] | 0.95 | 0.85 [0.83–0.85] | 0.94 [0.87–0.90] |
| 3 | 0.67 [0.65–0.67] | 0.96 | 0.90 [0.89–0.92] | 0.97 [0.94–0.96] |
| 4 | 0.72 | 0.97 | 0.94 | 0.97 |
| 6 | 0.78 | 0.99 | 0.95 | 0.99 |

\*Computed from the saved feasibility matrix after the run, without a bootstrap.

On the bootstrap interval: when it lies below the point estimate (modular, k = 2), the full-sample selection did better on held-out heads than a typical re-selection. Use the interval, not the point estimate, as the expected out-of-sample figure.

**Cheapest tooling reaching each target** (training heads; tooling term only; AUD costs are placeholders, not quotes):

| Target | Modular: crown families / lowers / tooling | Integrated: families / tooling | Size-only, fixed lower |
| --- | --- | --- | --- |
| 85% | 2 / 2 / ~AUD 75k | 2 / AUD 96k | Unreachable (plateaus ~78%) |
| 90% | 2 / 4 / ~AUD 78k | 3 / AUD 144k | Unreachable |
| 95% | 3 / 6 / ~AUD 117k | 5 / AUD 240k | Unreachable |

Each family is a **pair** of dies (left and right halves). The modular min-cost solves stopped at the 60 s time limit, so they are the best solutions found, not proven minima. The integrated ones are proven optimal over the catalogue.

**Recommended exploratory set** (cheapest modular set reaching 90% on training heads; 91.8% held out):

| Crown | Inner length × breadth × height above tragion (mm) | Est. crown mass at 2 mm | Lower variants |
| --- | --- | --- | --- |
| S13 | 263 × 217 × 164 | 2.9 kg | 1 |
| G226 | 280 × 226 × 170 | 3.1 kg | 3 (eye line at 11 / 17 / 23 mm) |

- **Pads.** The typical installed gap is 21 mm. The common recipes are `soft12.7+soft12.7`, `soft19+firm10` and `soft19` (`assignments.csv` lists each head's recipe).
- **Coverage by sex.** Men 93% and women 83% (weighted). **Excluded women have smaller heads** (mean head length 184 mm, against 191 mm for included women). A third, smaller crown is the obvious remedy; the min-cost 95% solution adds one.
- **Why heads were excluded.** Field of view (71 heads), pad too loose (68), pad too tight (32), nose clearance (28), between pad steps (14).

## 3. What the results say, and how firmly

| Finding | Status | Reasoning |
| --- | --- | --- |
| A size-only family with one fixed lower cannot reach 85% | **Robust within the model**, and it holds in every sweep scenario (see section 4) | Face geometry (eye line, nose, chin) varies independently of skull size. A scaled lower cannot track it. |
| Laser-cut lower variants matter more than crown shape freedom | **Model result, sensitive to assumed face priors** | Size-only crowns with lowers match shape-variable crowns with lowers. Eye height, nose protrusion and chin set-back are *priors*, not measurements, so their spread decides how many lowers are needed. |
| Two or three crown families can cover about 90% of the proxy population geometrically | **Sensitive to the liner assumptions** | The fillable pad window (about 12–27.5 mm) lets one crown span roughly 15 mm of head size. The window comes from placeholder foam properties and pressure limits. |
| A modular architecture beats integrated on tooling cost at equal coverage | **Follows from the cost structure**, if laser-cut lowers really cost much less than pressed variants | The cost ratio is a placeholder |
| The ANSUR II proxy represents Lochac fighters | **Not established** | It is a military, US, aged 17–58, screened population. The sex mix is assumed. |

## 4. Sensitivity

SWEEP_TABLE_PLACEHOLDER

## 5. Recommendation

All of this is my opinion, based on the analysis above.

1. **Architecture.** Pursue left/right pressed crown halves trimmed to a shared interface, plus **laser-cut lower and grille variants** (the "modular" column). Keep the integrated pressing as a comparison only. In this model it costs about twice as much in tooling for the same coverage, and every eye-line or face-depth variant becomes a new die.
2. **Crown count.** Plan for **3 crown families** rather than 2. Two reach 90% on the proxy, but the third mainly serves smaller heads, which matters for women. The model figures also sit on unvalidated foam limits. Give each family 2–3 lower variants.
3. **Treat scaled crowns as a serious option.** If scaled versions of one master shape work as well as shape-variable ones, every die can share one design, one forming development and one inspection plan. Confirm with real cranial scans before committing.
4. **Do not cut tooling yet.** The two cheapest experiments with the biggest effect on the answer are:
   - **Foam bench tests** (`foam_test_protocol.md`). They set the fillable gap window, which drives crowns per family more than anything else in the sweep.
   - **A Lochac scan and measure day.** Roughly 50–100 fighters, full head with arming cap, plus eye height, nose and chin. This replaces the face priors that drive the lower-variant count, and fixes the sex mix.
5. **Ask the marshalate now.** Is a laser-cut plate grille acceptable, and with what ligament width and thickness? What is the occipital coverage expectation? Has Lochac adopted Society V2026.0? The answers change the lower design more than any geometry result.
6. **Next modelling steps:**
   - ingest the NIOSH table as a civilian cross-check (impute head height from the bitragion coronal arc);
   - replace independent shape priors with scan-derived correlations;
   - add pitch to the pose search once oriented landmarks exist.

## 6. Measurements that would most reduce uncertainty

This ranking is my judgement, informed by the sweep:

1. Foam compression and stability band, and maximum usable liner depth (Gate B).
2. Face landmarks relative to the cranium: pupil height above tragion, nose protrusion, chin set-back (Gate A scan day).
3. Formed-shell tolerance and springback (Gate D).
4. Lochac fighter sex mix and arming-cap thickness (one event, a clipboard).
