# Liner foam and stack test protocol (Gate B)

Status: **protocol only, no measurements yet.** Every foam property in `config/default.yaml` is a placeholder with `measured: false`. While that holds, the fit evaluator reports stability and protective-stack criteria as *unevaluated*.

## 1. Materials

The test set is two candidate grades, configured as `soft` and `firm`. Record each in the property schema (section 4) by **material ID**: supplier, product code, lot, nominal density and cell type. Density alone does not describe a foam.

Test every combination of the cover fabric and attachment method (adhesive, hook-and-loop, snap) that the liner design might use.

## 2. Coupon tests (per grade, n ≥ 3 coupons per condition)

| Property | Method (indicative) | Conditions |
| --- | --- | --- |
| Quasi-static compression stress–strain to 80% | 50×50 mm coupon, at the catalogue thicknesses, using a universal tester or a calibrated weight-and-dial rig | 10 mm/min, then 100 mm/min, to show rate dependence |
| Hysteresis (loading and unloading loop) | Same rig, 5 cycles | Report cycle 1 and cycle 5 |
| Compression set | 25% (and 50%) strain held for 22 h, measured 30 min and 24 h after release. Use ISO 1856 / ASTM D3574 style. | 23 °C and 40 °C |
| Creep under fit preload | Constant 5 kPa and 10 kPa for 4 h | 23 °C |
| Shear stiffness G | Double-lap shear coupon | Small strain (< 20%) |
| Temperature sensitivity | Repeat the stress–strain test | 10 °C, 23 °C, 40 °C. Australian summer events matter. |
| Moisture and sweat | Soak in saline, drain, repeat the stress–strain test | Wet and dry |
| Ageing | Repeat compression set after 50 h at 70 °C | — |

Impact-rate behaviour belongs to Gate E. It needs a drop rig and qualified input, and is **not** covered here.

## 3. Stack-on-headform stability tests

1. **Headform.** A rigid headform close to the population median, such as a printed NIOSH/ISO medium form or an EN 960 J/M form if obtained, covered with a thin cap that matches the hair allowance.
2. **Shell.** A printed or formed shell from a candidate crown. Fit the pad recipe the evaluator predicts for that headform.
3. **Preload.** Install with the predicted compression and record the actual installed thickness at each pad.
4. **Lateral loads.** Apply forces of 20, 40 and 60 N (forward, rearward, left and right) through a fixture at brow height. Record shell translation relative to the headform in mm, using dial gauges or optical markers.
5. **Rotation.** Apply torques of 1, 2 and 3 N·m in pitch, yaw and roll. Record rotation in degrees.
6. **Creep and recovery.** Hold the largest load for 5 min and record recovery 1 min after release.
7. **Variants.** Repeat for each candidate stack (base plus fitting layers) and each attachment method.

**Allowable movement** is an engineering decision still to be made. Record the rationale with it. Start from these limits:

- the eye line stays inside the grille's clear band (config `lower.eye_band`);
- the face never closes to less than `lower.nose_clearance_min` from the grille;
- the occipital edge never uncovers.

Keep the normal-use limits separate from retention and roll-off tests, and from impact testing.

## 4. Property schema (import path)

Measured data goes in `data/raw/foam/<material_id>/` as CSV, one file per test. The columns are `test, coupon, condition, strain, stress_kPa, time_s, temperature_C, notes`.

A `config/materials/<material_id>.yaml` file then summarises:

```yaml
material_id: SUPPLIER-PRODUCT-LOT
measured: true
E_kPa_secant_10pct: ...      # replaces the linear placeholder in the screening model
stress_strain_curve: data/raw/foam/<id>/compression_10mm_min.csv
G_kPa: ...
densification_strain: ...
compression_set_pct_22h: ...
creep_strain_4h_at_5kPa: ...
temperature_factor_10C: ...
sources: [file list with sha256]
```

The current screening model (`src/scahelm/liner.py`) assumes linear, ideally bonded layers in series. Once curves exist, replace `choose()` with an interpolation of the measured stack curve. Keep the same check names so reports stay comparable.

## 5. What the bench data should settle first

These are ordered by how much they move the coverage results; see `outputs/sweep/sweep_summary.csv`:

1. The usable compression band for fitting, which sets the fillable gap window.
2. Maximum total liner depth before stability fails.
3. Whether firm fitting layers on a soft base resist shear better than a single thick soft pad. The spec's "soft impact layer, firm fitting layer" idea is **unproven**.
