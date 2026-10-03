# Physical validation plan and decision gates

Each gate lists what it establishes, the work, and the exit criterion. Software verification is covered by `tests/`; this file covers the physical evidence.

## Gate A: data

- **Establishes:** enough cranial information and a defensible population.
- **Current state:** **not passed.** Only scalar proxies exist (ANSUR II). The model is a labelled surrogate.
- **Work:** follow the acquisition plan in `data_sources.md`: RMIT authors, then Headspace/LYHM via an academic partner, then a Lochac scan day. Ingest the NIOSH 2003 table as a civilian cross-check.
- **Exit:** at least 100 consenting Lochac fighters scanned with full cranium and their usual arming cap, plus a tape-measure check. Coverage predictions from the ANSUR surrogate are compared with predictions from those scans.

## Gate B: liner

- **Establishes:** measured foam behaviour and justified normal-use movement limits.
- **Work:** `foam_test_protocol.md`.
- **Exit:** both foam grades imported with `measured: true`; movement limits written down with their rationale; coverage recomputed. Stability criteria then move from *unevaluated* to pass/fail.

## Gate C: geometry (non-combat fit prototypes)

- **Work:**
  - 3-D print or vacuum-form the inner surfaces of the recommended crowns (STL in `outputs/*/cad`).
  - Recruit wearers from three groups in `assignments.csv`: near the edges of each family's coverage, just outside the selected set, and deliberately excluded (one per main exclusion reason).
  - Fit the predicted pad recipe.
  - Record the eye line relative to the grille, pad compression, hot spots, and movement under the Gate B loads.
- **Exit:** predicted and observed fit/no-fit agree on at least 90% of boundary cases, and pad recipes match within one catalogue step. Disagreements are traced to a model input.

## Gate D: manufacture

- **Work:** form and weld steel prototypes of one family, then run the inspection list in `manufacturing.md` section 6. Scan the formed geometry and re-run the fit evaluator on the as-formed inner surface.
- **Exit:** ≥ 1.6 mm everywhere, deviation within the assumed tolerance, sound seams, and every grille opening refusing the 25.4 mm dowel.

## Gate E: protection and use

- **Work:** with qualified input (e.g. a university impact lab), develop instrumented impact, deformation, retention and repeat-impact tests on **complete assemblies**, including liners and attachments. Base the protocol on a recognised helmet standard's apparatus, adapted to rattan-strike energies, which still need establishing. **Never use wearers as impact-test subjects.**
- **Exit:** a documented test report. Passing marshal inspection is rules compliance, not evidence of impact attenuation; keep the two separate.

## Order of measurements that most reduce uncertainty

This order is my engineering judgement, informed by the sweep:

1. Foam compression band and maximum liner depth (Gate B). This sets the fillable gap window that drives coverage.
2. Full-head scans of real fighters (Gate A). They replace the independent shape priors.
3. As-formed tolerance and springback (Gate D). Tolerance enters every clearance.
4. The Lochac sex mix and arming-cap thickness. They are cheap to collect at one event.
