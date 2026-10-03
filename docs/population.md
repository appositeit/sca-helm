# Population definition and surrogate model

Status: design decision plus assumptions. Revisit when a Lochac sample exists (Gate A).

## Denominator

**Target population:** adults who take part in Lochac armoured (rattan) combat, wearing their usual arming cap or padding.

No head data exists for this group. Every run therefore uses a **proxy** and says which one:

| Proxy | Used for | Why it is not the target population |
| --- | --- | --- |
| ANSUR II 2012 (US Army, 4082 M / 1986 F) | All population runs | Military, US, aged 17–58, with fitness and height screening. Body build and ethnic mix differ from AU/NZ. The public file is a stratified subsample, and it has no survey weights. |
| NIOSH 2003 (US respirator users, 3997) | Planned cross-check | Civilian and older, so arguably closer to SCA demographics. It is not ingested yet (see `data_sources.md`). |
| Synthetic fixture | Tests and the demo only | Generated numbers. **Never** report population coverage from it. |

**Weights.** ANSUR II has no sampling weights. The only re-weighting applied is post-stratification by sex, so the weighted female share equals `population.female_fraction`. The default of **0.15 is an assumption**; a marshal-roster count would replace it. Every run reports both weighted and unweighted held-out coverage.

**Splits.** Training and validation are split by participant, stratified by sex, with 30% held out. ANSUR has one row per person. The code rejects duplicate participant ids, so a future scan dataset with repeat scans cannot leak one person across the split.

## What the scalar tables give, and what is assumed

Each head is a smooth piecewise superquadric (`src/scahelm/geometry.py`), built in millimetres with the tragion mid-point as origin.

| Parameter | Source |
| --- | --- |
| Head length, head breadth (max-length plane) | Measured (`headlength`, `headbreadth`) |
| Tragion to vertex height | Measured (`tragiontopofhead`) |
| Horizontal squareness exponent | **Fitted** so the section perimeter equals measured `headcircumference` |
| Menton-sellion length, ear protrusion, interpupillary breadth | Measured. ANSUR stores IPD in 0.1 mm, which is converted. |
| Split of length in front of/behind tragion (`f_front`) | **Assumed** prior N(0.50, 0.02) |
| Height of max-length plane above tragion | **Assumed** N(32, 5) mm |
| Vertical squareness, occipital depth | **Assumed** priors |
| Pupil, sellion, pronasale and menton offsets | **Assumed** priors |

The assumed parameters are drawn **independently** of each other and of the measurements. In reality they are correlated, and this model leaves those correlations out. That is the main reason the results are labelled a *surrogate*. The sensitivity scenario `shape_prior_wide` doubles their spread to show how much the conclusions depend on them.

## Conclusions this model can and cannot support

| Can support (with stated assumptions) | Needs 3-D scans |
| --- | --- |
| How coverage scales with the number of size families, given the size distribution | Whether a given *shape* family fits real occipital or forehead contours |
| Rough ranking of the size-only, shape-variable and modular architectures | Local pressure points and hot spots |
| Which liner and tolerance assumptions coverage is most sensitive to | Eye-line position relative to the brow; nose and chin clearance (offsets are priors) |
| Boundary heads to recruit for physical fit tests | Any claim about Lochac population coverage |
