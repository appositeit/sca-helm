# Standardised pressed SCA helms: design and research specification

Version: 0.1 — 4 October 2026  
Status: engineering investigation and local-agent implementation brief; not a validated production design.

## 1. Objective

Design a manufacturable family of steel helms for adult SCA armoured combat, initially targeting Lochac. Minimise the number of expensive press forms while achieving acceptable fit for at least 90% of a defined target population. Fit must include liner stability, protective clearance, retention, vision and lower-head coverage, rather than merely containing the head.

The intended manufacturing approach is two pressed shell halves welded together, with a laser-cut grille and adaptable lower components. Investigate left/right halves joined along a sagittal seam as the working interpretation. Keep the split plane configurable: the original proposal did not establish it definitively. Compare this with a pressed crown plus fabricated lower assembly; do not silently substitute the latter architecture.

The initial deliverable is a reproducible research and optimisation toolchain, candidate dimensions and CAD geometry, and a physical validation plan. Do not assume that three or four forms will achieve 90% coverage; calculate it.

## 2. Design principles and scope

- Use adult external head geometry, including soft tissue, not bare bony skull geometry.
- Model size and shape jointly: length, breadth, height, occipital contour and forehead shape matter. Circumference and cephalic index are descriptive measurements, not sufficient fit criteria.
- Permit a small catalogue of foam materials and interchangeable pad thicknesses. Determine allowable shell oversize from measured displacement and liner behaviour.
- Separate crown geometry from lower face, jaw, eye-line and neck geometry where the manufacturing interface permits it.
- Optimise die cost, liner complexity and production effort together. Laser-cut variants still have assembly, stock and validation costs.
- Keep geometric fit, stability, impact performance and rules compliance as separate reported results.
- Preserve historically plausible appearance, with an open grille and good ventilation as initial preferences. Do not require one crown to support every historical helm type.

Out of scope for the first implementation: certifying protective performance, final press tooling manufacture, and claims about concussion prevention.

## 3. Evidence and rules register

Before fixing design limits, identify the current authoritative Lochac and Society requirements and record version, effective date, URL and relevant sections. Resolve superseded or conflicting documents. Maintain a machine-readable register linking each requirement to its source and verification method.

The official Lochac armour-requirements page retrieved for this brief states minimum completed steel thickness of 1.6 mm, resilient padding of at least 12.7 mm where the helm can contact the head unless an adequate suspension prevents injurious contact, and a separate retention requirement. These are research starting points pending verification against the applicable current handbook. Do not turn a padding-thickness rule directly into a geometric clearance rule without accounting for liner installation and compression.

Extract all applicable seam, face protection, opening, retention, screening, coverage and interior-projection rules. In particular, a laser-cut plate grille must be assessed as its actual geometry and material: a narrow rectangular ligament is not automatically equivalent to a permitted round bar. Distinguish ordinary armoured combat from missile-combat screening requirements.

The earlier discussion's 12.7–25 mm liner envelope, 5/10/15 mm fitting pads and estimated shell counts are hypotheses, not validated requirements. The suggestion that soft foam should be the impact layer and firm foam merely a fitting layer is also unproven: evaluate the whole stack.

## 4. Population and data acquisition

Define the denominator explicitly: ideally adults likely to participate in Lochac armoured combat. Public occupational or military samples are proxies. Report their limitations rather than claiming Australian population coverage from them.

Investigate these sources in order:

1. NIOSH anthropometric measurements and ISO digital headforms: establish exactly which individual records, cranial surfaces, weights and licences are downloadable.
2. Accessible military/civilian 3-D anthropometric collections, such as CAESAR or ANSUR-related resources: distinguish measurement tables from scans and check access/licensing.
3. EN 960 helmet-testing headforms as reproducible geometric references, subject to lawful access to the standard or licensed CAD. Standard headforms are test geometries, not a representative population sample.
4. A supplementary consenting local participant sample for checking population transfer and real fitting conditions.

Do not assume the complete NIOSH individual scan collection is public, or that respirator headforms fully describe cranial variation. Five representative forms cannot by themselves establish 90% coverage. If only scalar measurements are available, build an explicitly labelled surrogate model and identify which conclusions require scans.

For every source, record population, sample size, collection date, sampling method, exclusions, measurement definitions, scan coverage, units, licence, download URL and checksum. Preserve original files unmodified. Record missing or imputed measurements and avoid inventing independent combinations of marginal percentiles: correlation matters.

Use sample weights when justified; report unweighted results alongside weighted results. Include subgroup coverage and uncertainty where sample size supports it. Split training and validation by participant, never by scan. Repeated scans of one person must not inflate coverage.

## 5. Geometry and alignment

Use millimetres throughout. Define x as lateral, y as anterior, z as superior, with documented origin and anatomical landmarks. Preserve actual dimensions; no isotropic scale normalisation of heads. Establish a consistent anatomical orientation, then allow bounded rigid pose adjustment within the shell to model realistic fitting.

Clean and register meshes while retaining relevant asymmetry. Identify crown support zones, face exclusion regions, eyes, ears, jaw and neck landmarks. Incomplete cranial meshes must be flagged; do not reconstruct unseen crowns without reporting the assumption. Include hair/head covering and measurement uncertainty as configurable allowances.

Represent shell inner and outer surfaces separately. Fit uses the finished inner surface including seams, attachments and tolerances. Manufacturing starts from this finished shape, with sheet thickness, forming compensation and springback treated explicitly; an offset headform is not automatically a usable forming die.

A radial expression S(theta, phi) minus H(theta, phi) may be used for early visualisation only. It is not generally a true normal clearance and may fail for non-star-shaped regions. Use collision tests and surface distances with anatomically corresponding zones; report the direction and method. Sparse sampling must not miss local intrusions.

## 6. Liner material model and bench measurements

Start with two candidate foam grades, configurable by material ID; density alone is insufficient. Collect or measure compression stress–strain behaviour, rate dependence, hysteresis, compression set, creep, shear stiffness, temperature sensitivity, moisture response and attachment behaviour. Include the cover fabric and adhesive/fastener interfaces in assembly tests.

For a simple screening model, layers in series have approximate normal compliance sum(t_i / (E_i A)) and shear compliance sum(t_i / (G_i A)). This assumes small strain and ideal bonding. It is not a validated impact model. Real pads require nonlinear curves, contact changes and friction/slip behaviour.

Measure candidate stacks under defined preload and repeatable lateral forces/torques on a headform. Record translation in mm and rotation in degrees, creep duration and recovery. Define allowable movement through a documented engineering decision informed by eye-line, face clearance and practical use. Keep normal-use stability thresholds distinct from impact tests and retention/roll-off behaviour.

Treat pad thickness as discrete purchasable values. Account for compressed operating thickness, residual compression capacity, material variation and ageing. A thicker firm pad may reduce normal compression yet still permit shear or slip; prove its suitability experimentally.

Configuration must expose:

| Parameter | Initial status |
| --- | --- |
| Target population coverage | 0.90, configurable |
| Foam grades | Two candidate materials, properties to obtain |
| Minimum resilient padding | Rules-derived; verify current application |
| Maximum total liner depth | Unknown; derive from stack tests |
| Translation/rotation limits | Unknown; define and justify |
| Allowed pad catalogue and layouts | Candidate discrete choices |
| Fit preload and contact-pressure limits | To define |
| Head pose bounds | To define from eye-line and anatomy |
| Manufacturing and measurement allowances | To measure/estimate with provenance |

Run illustrative thickness sensitivity cases, including a provisional 12.7–25 mm total envelope, only when labelled as geometric scenarios. If material curves or movement limits are missing, report stability as unevaluated, not passed.

## 7. Fit predicate

For head h, shell s, lower component l, pad arrangement p and allowed pose q, define an acceptable assembly only if all relevant criteria pass:

1. No hard contact or intrusion, with tolerance and anatomical allowances included.
2. Required protective liner or valid suspension exists in every relevant contact region.
3. The permitted pad catalogue can fill support zones at acceptable preload and contact pressure without exceeding validated thickness or movement limits.
4. Adequate compression reserve and the separately validated protective-stack configuration are retained.
5. Eyes remain correctly positioned relative to the opening and grille through permitted movement; check field of view.
6. Nose, face, jaw and ears clear hard components; coverage remains compliant through the specified head/neck motion range.
7. The retention system works independently of snugness, and donning/removal remains practical.
8. Attachments, seam projections and lower interface do not create local failures.

Unpadded ventilation space need not have the same maximum distance as a supporting pad. Do not apply one universal upper-gap bound to the entire shell. Likewise, variation in pad thickness is not inherently a failure: evaluate stability, pressure distribution and manufacturability. A separate pad-asymmetry constraint may be explored as a heuristic, with its rationale stated.

The predicate must return pass/fail/unevaluated for each criterion, limiting zones, selected pose and exact pad recipe. Overall validated fit cannot pass when a required criterion is unevaluated. Maintain a cheaper geometric-feasibility result for exploratory optimisation.

## 8. Candidate shell family and optimisation

Build smooth, press-compatible candidate surfaces parameterised by cranial length, breadth, height, front/rear fullness and seam/interface geometry. Include scaled single-shape baselines and independently variable shape families. Impose minimum radii, die release, permitted draw direction and surface smoothness; do not export a jagged union of heads as a production surface.

An aligned union of padded head envelopes can initialise a candidate. Recheck it against every head after regularisation: enlarging the shell to fit one head may violate maximum usable padding for another.

For each candidate assembly j and participant i, precompute a feasibility matrix A_ij. With participant weights w_i, shell-selection variables x_j and coverage variables y_i, minimise selected tooling cost subject to:

    y_i <= sum_j A_ij * x_j
    sum_i w_i * y_i >= coverage_target * sum_i w_i

Use binary variables. Count shared dies separately from assembled variants: a left/right pair may require distinct tooling unless actual symmetry and press process permit reuse. Lower variants sharing a crown must not each count as another crown die, but must carry their own production costs.

Use greedy set cover as a baseline, then an integer solver for the finite candidate catalogue. Report whether optimality was proved, the solver gap and catalogue limitations. Do not call a catalogue optimum a global optimum over all possible surfaces. Consider iterative shape refinement, followed by independent validation.

Produce coverage curves for 1–6 shell families, extending if required. Compare size-only, shape-variable and modular-lower architectures. Report die count, complete assembly count, liner recipes, mass, estimated cost and excluded-head characteristics. Use sensitivity sweeps for foam limits, tolerances and coverage targets such as 85/90/95%. Report held-out coverage with confidence intervals; bootstrapping should account for the selection process.

## 9. Adaptive lower components

Define a repeatable crown-to-lower interface with datum surfaces, seam/joint details and a compatibility matrix. Explore lower variants for face length, jaw clearance, neck opening and eye-line. The attachment perimeter constrains which combinations are possible; do not assume an unrestricted cross-product.

Generate parametric laser-cut blanks for lower plates and grille with bend lines, radii, thickness, weld allowances and finish requirements. Check structural ligaments, attachments, face intrusion under deformation and applicable opening/screening requirements. Include gorget interaction and clearance while turning, looking up and looking down.

If using left/right pressed halves, compare integrating lower features into the pressing with trimming to a shared crown interface and adding separate lowers. Preserve the user's two-half welded construction as a candidate throughout the comparison.

## 10. Forming and fabrication investigation

Use nominal 2 mm mild steel as an initial material/process candidate, not a guarantee of adequate final thickness. Establish actual grade, ductility, thickness tolerance and forming limits. Investigate cold versus hot forming, staged draws, blank-holder requirements, lubrication, trimming, springback and weld distortion.

Estimate press force from a documented forming model and process assumptions. Do not select a press from projected area alone. Seek forming simulation or prototype evidence where useful. Record the number of operations and tooling pieces per shell family.

Measure finished thickness at the most strained regions, trim edges and ground seams. Validate seam quality, distortion and surface geometry. Define inspection methods and acceptance limits before production. Compare likely unit costs at explicitly stated batch volumes, including tooling amortisation, rejected parts, welding, finishing, liner assembly and inspection.

## 11. Local implementation and outputs

Prefer Python for data preparation, geometry evaluation and optimisation. Use an interchangeable geometry backend and an open solver where practical. Provide a documented command-line workflow; a web app is unnecessary. CAD output should be importable into Onshape: STEP for solid/surface geometry, STL for inspection/prototypes, DXF for laser-cut parts.

Suggested repository layout:

    README.md
    config/                 # units, rules, material models, scenarios
    data/raw/               # licensed source files or retrieval instructions
    data/processed/         # canonical measurements and meshes
    src/                    # ingest, align, fit, candidates, optimise, export
    tests/                  # meaningful numerical and geometric checks
    outputs/                # reports, tables, plots, candidate CAD
    docs/                   # sources, manufacturing and validation plans

Keep restricted datasets out of distributed repositories. Record dependency versions, seeds, solver configuration, dataset checksums and output provenance. Provide a small synthetic fixture that runs without restricted data, clearly labelled and excluded from population conclusions.

Required deliverables:

- Source/access/licensing register and current rules matrix.
- Explicit population definition and data-quality report.
- Foam test protocol, property schema and measured-data import path.
- Reproducible fit evaluator and coverage optimiser.
- Coverage-versus-tooling plots and per-head assignment/exclusion CSVs.
- Candidate dimension tables, pad recipes and CAD exports, each labelled exploratory or validated.
- Manufacturing comparison, lower compatibility matrix and cost assumptions.
- A recommendation explaining what is established, what is sensitive to assumptions and which measurements would most reduce uncertainty.

## 12. Verification and decision gates

Software checks must catch unit mistakes, incorrect mesh orientation, ignored collisions, pose-bound violations, discrete-pad errors and double-counted participants/tooling. Use known synthetic geometry and independently check a small optimiser instance by exhaustive enumeration. Confirm CAD export dimensions and that surface smoothing does not invalidate assignments.

Gate A — data: establish sufficient cranial information and defensible population coverage. If unavailable, deliver a surrogate feasibility study and a concrete acquisition plan.

Gate B — liner: measure the proposed stacks and establish justified normal-use movement limits. Recompute coverage with measured limits.

Gate C — geometry: build non-combat fit prototypes, checking boundary cases and deliberately excluded shapes. Compare predicted pad recipes and eye-line with observed fit.

Gate D — manufacture: form and weld steel prototypes, measure geometry and thickness, and inspect seams and grille construction.

Gate E — protection and use: develop appropriate instrumented impact, deformation, retention and repeat-impact tests with qualified input. Rules compliance and marshal inspection do not establish impact attenuation. Never use wearers as impact-test subjects. Validate complete assemblies, including liners and attachments, before recommending combat use.

## 13. Initial agent work sequence

1. Verify rules and source access; publish an evidence table without making shell-count claims.
2. Implement configuration, data schema and a synthetic end-to-end geometric example.
3. Ingest real measurements/scans where accessible; quantify missing cranial information.
4. Implement fit evaluation and candidate generation with provisional, explicitly labelled liner scenarios.
5. Produce initial coverage/tooling tradeoffs and identify boundary cases for foam and fit tests.
6. Integrate measured liner constraints, refine geometry and produce prototype-ready CAD when evidence permits.

Proceed through independent software/research tasks without requiring every unknown to be answered upfront. Keep unknown physical limits explicit and report blocked validation separately from completed exploratory work.

## 14. Reference starting points

- [Lochac armour requirements](https://sca.org.nz/wiki/index.php?title=Armoured_Combat:Armour_Requirements) — retrieved for this brief; verify current authority and effective rules.
- [Lochac Fighters' Handbook v3.4, July 2024](https://sca.org.nz/wiki/images/b/bc/Fighters_Handbook_v3.4_-_July_2024.pdf) — historical/versioned starting point; do not assume current.
- [NIOSH anthropometric data and ISO digital headforms](https://archive.cdc.gov/www_cdc_gov/niosh/npptl/topics/respirators/headforms/default.html) — archived official resource; investigate available files and their scope.
- [Helmet sizing research, PubMed record 1996936](https://pubmed.ncbi.nlm.nih.gov/1996936/) — research lead from the prior discussion; retrieve and verify methods and population before using numerical conclusions.
- EN 960, *Headforms for use in the testing of protective helmets* — locate the applicable edition and authorised geometry source; do not equate test-headform sizes with population coverage.

All implementation reports must distinguish retrieved facts, design decisions, provisional scenarios and experimental results.
