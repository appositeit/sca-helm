# Head-geometry data sources: access, licensing and fitness for purpose

Compiled 2026-10-03. The machine-readable version is `config/data_sources.yaml`. Anything marked *unverified* was not confirmed against a primary source. AUD figures are indicative and use the ECB rates for 2026-10-02 (1 EUR = 1.6176 AUD, 1 USD = 1.4411 AUD, 1 NZD = 0.80872 AUD).

Target population: adult SCA heavy-combat fighters in Lochac (Australia and New Zealand). Most are male but not all. They cover a broad adult age range and wear padding or arming caps under the helmet.

## 1. Summary register

| id | Source | Population / n | Data type | Scan coverage | Access | Licence | Cost (AUD) |
|---|---|---|---|---|---|---|---|
| ansur2_2012 | ANSUR II public working DB | US Army 2010–12; 4082 M / 1986 F; age 17–58 | Individual manual measurements, 93 dims | none public | public download | US Gov, "unlimited public release" | 0 |
| ansur1_1988 | ANSUR (I) public files | US Army 1988; 1774 M / 2208 F | Individual measurements (has bitragion coronal arc) | none | public download | US Gov (wording unverified) | 0 |
| niosh_2003_headface | NIOSH 2003 head-and-face survey | US respirator users; 2543 M / 1454 F; 3 age bands from 17/18 to 66 | Individual manual measurements, 19 head/face dims | none (scans not released) | public download (data.cdc.gov) | no explicit licence; US Gov work, presumed PD (unverified) | 0 |
| niosh_iso_digital_headforms | NIOSH/ISO 16900-5 digital headforms | 5 averaged headforms (5 subjects each) | STL + IGES meshes | full head, with constructed scalp | public download | as above | 0 |
| headspace_york | Headspace (Univ. of York) | UK; 1519 scans | 3dMD full-head scans in latex caps, OBJ, landmarks, metadata | full head | academic agreement, university staff signatory | non-commercial university research only | 0 |
| lyhm | Liverpool-York Head Model | 1212 Headspace subjects | 3DMM shape space | full head model | academic agreement | non-commercial | 0 |
| flame | FLAME / FLAME 2023 Open | >33k scans (orig.), incl. CAESAR | 3DMM | full head model (cranium quality unverified) | registration | 2023 Open: CC-BY-4.0; older: academic NC | 0 |
| caesar_wear | CAESAR via WEAR | NA/IT/NL civilians c. 2000, several thousand | Whole-body scans + landmarks + tables; unregistered | full body (head coarse, hair uncapped; unverified) | paid, posted drive | "do anything you like" | 1771 (962 WEAR member) |
| size_korea | Size Korea | Korean; >8500 head scans (secondary) | scans + tables | full head (reported) | unverified | unverified | unknown |
| sizeusa | SizeUSA ([TC]2) | US ~10,800 | body scans | full body | paid, on request | commercial | unknown |
| facebase_3dfn | FaceBase 3D Facial Norms | US, 3–40 y, 2454 | 3dMD face surfaces + calipers | face only | IRB-approved craniofacial research only | DUC | 0 |
| adf_awas_2012 | AUS Warfighter Anthropometry Survey (DSTO-TR-3006) | ADF Army 2012, n unverified | summary stats for 84 dims; body scans exist | none public | report public (DTIC 403 to this agent) | public release report | 0 |
| rmit_cyclists_2015 | RMIT Australian cyclists head scans | Melbourne; 176 M / 46 F; 34.6±12.5 y | handheld 3D head scans + hair-thickness offset | full head | papers only; data by request (unverified) | unverified | unknown |
| size_australia | Size Oz / Target–Alvanon 2012 | AU retail survey | body scans | proprietary | unavailable | – | – |
| en960_2006 | EN 960:2006 / BS EN 960:2006 | – | Headform geometry standard (sizes 445–645) | idealised | purchase | © CEN/BSI | ~136 (iTeh, USD 94.47) |
| iso_6220 | ISO/DIS 6220:1983 | – | Draft, withdrawn; basis of EN 960 | – | unavailable | – | – |
| asnzs_2512_1_2009 | AS/NZS 2512.1:2009 | – | Headforms A–Q, AA | idealised | purchase | © Standards Australia | 154.97 (web reader) / 172.02 (hardcopy) |
| pubmed_1996936 | Sippo & Belyavin 1991 | RAF aircrew 1970/71 survey (~2000) | Method paper | – | abstract public | – | – |

## 2. Detail on the key sources

### 2.1 ANSUR II (downloaded and stored)

- Landing page: https://www.openlab.psu.edu/ansur2/. The OpenLab site uses the `tools.openlab.psu.edu` host for downloads. The space-named `wp-content` URLs returned 404 or a connection reset.
- Licence: the NSRDEC memo of 14 Apr 2017 says the files were "reviewed and cleared for UNLIMITED PUBLIC RELEASE". **Decision:** keep the raw files unmodified in `data/raw/ansur2/`.

| File | URL | HTTP | Bytes | Rows × cols | sha256 |
|---|---|---|---|---|---|
| ANSUR_II_MALE_Public.csv | https://tools.openlab.psu.edu/publicData/ANSUR_II_MALE_Public.csv | 200 | 2,000,794 | 4082 × 108 | `0547aea0170e5293de519389981135e75803f02e6d40c77ace740decc0caac64` |
| ANSUR_II_FEMALE_Public.csv | https://tools.openlab.psu.edu/publicData/ANSUR_II_FEMALE_Public.csv | 200 | 976,573 | 1986 × 108 | `ed7e800aa97a4d42f8286b988be2fe1883a2e789588169db959864b707d1757a` |

**Head-related columns.** These are the exact names and are the same in both files:
`headcircumference`, `headlength`, `headbreadth`, `tragiontopofhead`, `bitragionchinarc`, `bitragionsubmandibulararc`, `bizygomaticbreadth`, `mentonsellionlength`, `earbreadth`, `earlength`, `earprotrusion`, `interpupillarybreadth`, `neckcircumference`, `neckcircumferencebase`.

**Not present:** sagittal arc, bitragion coronal arc, bitragion frontal arc, minimum frontal breadth, head height. ANSUR I has `BITR-CORONAL_ARC` and `BITR-CRINION_ARC`. NIOSH has `BITCOR` and `BITFRONT`.

Quirks:
- The ID column is `subjectid` in the male file and `SubjectId` in the female file.
- The male file has one Latin-1 byte, so read it with `encoding="latin-1"`.
- `weightkg` is measured body mass in units of 0.1 kg.
- **`Weightlbs` is self-reported body weight, not a sampling weight.** Its minimum is 0, which marks a missing value. `Heightin` is also self-reported.
- `interpupillarybreadth` values run from 510 to 770, which suggests units of 0.1 mm. The memo says all dimensions are in mm (*unverified*).

Sampling: the public files are the "working databases". Each is a stratified random subsample, drawn separately for each sex from the 7435 M / 3922 F measured. The strata are age, race/ethnicity and component, matched to the DMDC Army census of 30 Sep 2011. The files are therefore self-weighting for the 2011 Army, and **there is no weight column**. Female soldiers with braids or cornrows were measured *with* hair for head breadth, circumference, length and tragion–top of head.

Observed values, mean (SD) in mm:

| | headcircumference | headlength | headbreadth | tragiontopofhead |
|---|---|---|---|---|
| Male | 574.4 (16.0) | 199.5 (7.0) | 154.3 (5.5) | 131.1 (6.2) |
| Female | 561.1 (19.4) | 189.8 (7.4) | 147.8 (5.2) | 126.5 (6.5) |

ANSUR II also collected 3-D head, foot and whole-body scans. They are **not public**, for participant privacy.

### 2.2 NIOSH anthropometric data and ISO digital headforms

The archived CDC page links to `cdc.gov/niosh/data/datasets/rd-10130-2020-0`, which redirects to data.cdc.gov dataset `c2hx-eeis`. The dataset has a single zip file:
`https://data.cdc.gov/api/views/c2hx-eeis/files/4b4cb188-f59c-490a-8ab1-67528503554a?filename=rd-10130-2020-0.zip`. The download returned HTTP 200: 68,582,780 bytes, sha256 `f8633144d49cfd64aea2305edf8244d25d32bf12af596456e00f91ae1d5c5e8b`. It was downloaded for inspection and **not stored**, because only ANSUR files were authorised.

- **The individual-level 2003 table is public.** `datasets/RespiratorUsersData-all-subjects.csv` holds 3997 subjects (2543 M, 1454 F) with these columns: SUBNO, SEX, AGEGRP (3 bands), RACEGRP, WEIGHTKG, STATURE, HEADCIRC, BITCOR, BITFRONT, BITSUBN, BITCHIN, NECKCIRC, HEADBR, HEADLTH, MINFRBR, MAXFRBR, BIZYGOBR, BIGONLBR, NROOTBR, NOSEBR, LIPLTH, SUBNASAL, MENSELL, NOSEPRO, INTPUPBR. Missing values are coded -9,999, and some fields use thousands separators.
- `RespiratorUsers-scanned-subjects.csv` holds the same measurements for the 946 scanned subjects. **The individual scans themselves are not released.** The methods PDF says 1013 subjects were scanned and the CDC text says 947.
- The archived page says the 2D/3D data are available "for those who complete the data use agreements". The current zip contains the 2D table with no agreement step.
- Headforms: there are five symmetric STL and IGES meshes (small, medium, large, long/narrow, short/wide), each covering the full head and neck. The archived page mentions PLY files, but none are in the zip.
  - The face is an average of 5 subjects.
  - The **scalp is constructed**, scaled to the category's mean head length and breadth, because the subjects had hair or wore wig caps.
  - The ears are generic surfaces from a third party.
- Licence: none is stated (data.cdc.gov `license: null`). As a US federal work it is presumed public domain (*unverified*). The third-party ear surfaces are a residual uncertainty.
- Head circumference, mean (SD): male 576.1 (17.5) mm, female 558.7 (20.7) mm.

### 2.3 Full-head 3-D scan resources

| Source | What you get | Blocking issue for this project |
|---|---|---|
| Headspace (York) | 1519 capped full-head 3dMD scans (38 GB) with metadata | Needs a university academic signatory; non-commercial research only |
| LYHM | Morphable model built from Headspace | Same licence |
| FLAME 2023 Open | Morphable head model, CC-BY-4.0 (per site), requires registration | Cranial accuracy and training data *unverified*; built for faces |
| CAESAR (WEAR) | Unregistered whole-body scans, >33 GB, permissive use | Low head resolution and uncapped hair (*unverified*); €1095 (≈ AUD 1771) |
| RMIT cyclists | 222 Melbourne head scans with hair-offset correction | Data access unknown; contact the authors |
| Size Korea / SizeUSA | Scans | Population mismatch or price unknown; *unverified* |
| FaceBase 3DFN | Face scans | Face only, IRB-restricted |

### 2.4 Australian sources

- **AWAS 2012** (DSTO-TR-3006, Edwards et al., Aug 2014, approved for public release) gives summary values for 84 dimensions. Body scans were collected. Individual data are not public. The DTIC PDF returned 403 to this agent, so it needs to be fetched manually to confirm the head dimensions and sample size.
- **No national civilian head dataset exists.** Size Oz was never funded, and the Target/Alvanon 2012 survey is proprietary.

### 2.5 Helmet test headform standards

- **EN 960:2006** supersedes EN 960:1994/A1:1998. It derives from ISO/DIS 6220:1983, which was withdrawn as a draft, and ISO/R 1511.
  - It defines full, three-quarter and half headforms.
  - Size designation is the nominal circumference: **445–645 mm in 10 mm steps**.
  - Table 1 gives h, x, y and z. For example, h runs from 108.5 mm at size 445 to 150.5 mm at size 645 (from the public preview). Mass bands of 3100 ± 100 g up to 6100 ± 180 g also appear, but the size grouping is *unverified*.
  - Annex A gives the normative spherical coordinates for each size, in 15° steps. Annex B gives the radius equations for sizes 495–645.
  - No licensed CAD file was found. The geometry has to be rebuilt from Annex A.
  - Prices: iTeh USD 94.47 (≈ AUD 136). Standards NZ quotes NZD 605.25 (≈ AUD 489, *unverified*). The BSI GBP price is *unverified*.
- **AS/NZS 2512.1:2009** is Current in Australia. It defines headforms A–Q and AA. Prices: AUD 154.97 (web reader, 1 user) or AUD 172.02 (hardcopy), both including GST.

### 2.6 PubMed 1996936

Sippo AC, Belyavin AJ (RAF Institute of Aviation Medicine). *Determining aircrew helmet size design requirements using statistical analysis of anthropometric data.* Aviat Space Environ Med 1991;62(1):67–74.

- **Data:** the 1970/71 RAF survey of 2000 aircrew.
- **Method:** head length, breadth and pupil–vertex height were plotted for each subject, and the minimum number of sizes giving a reasonable fit was calculated.
- **Finding:** **nine sizes fit 93.5%** of subjects grouped around the mean. Fitting more people would need many more sizes or a looser fit.

## 3. Limitations for representing Lochac fighters

- None of the accessible individual-level datasets is Australian or New Zealander. ANSUR is a fit, young-skewed US military sample with a US racial mix. NIOSH covers US civilian workers aged 18–66; it is race-stratified rather than proportional, which affects reweighting.
- Manual caliper values compress hair and soft tissue a little. Scans with hair inflate breadths (NIOSH documents both effects).
- The cranial vault shape above the brow line is the key region for a helmet. It is described only by circumference, length, breadth, tragion–top (ANSUR II) and bitragion coronal arc (NIOSH, ANSUR I). No public dataset gives an individual cranial surface.
- SCA helmets are worn over padding and arming caps. An offset for this has to be modelled separately.

## Recommendation: what to use for a surrogate model now, and an acquisition plan for scans

**Use now, at no cost and with public licences:**

1. **The ANSUR II tables (stored) form the main statistical backbone.** Use `headcircumference`, `headlength`, `headbreadth` and `tragiontopofhead`, with `bizygomaticbreadth` and `mentonsellionlength` for face opening and visor clearance.
   - Model men and women separately.
   - Mix them in Lochac proportions as a user parameter. The real ratio is unknown, so treat it as an assumption.
   - To get closer to AU/NZ, reweight by `DODRace`/`SubjectNumericRace`, with a sensitivity analysis.
2. **The NIOSH 2003 individual table** (public; re-download from the URL above if it is approved for storage) is a civilian, older cross-check. It adds the bitragion coronal and frontal arcs (`BITCOR`, `BITFRONT`), which constrain crown height and shape. It has head circumference, length and breadth in common with ANSUR II, so the two can be compared and pooled.
3. **The NIOSH ISO digital headforms (STL)** serve as template meshes and face geometry. Morph them (e.g. RBF or landmark-driven) to the statistical L/B/height/circumference targets to make a family of synthetic heads, such as boundary manikins on a PCA of the head dimensions. Treat the vault shape as a low-confidence assumption, because the scalp was constructed.
4. **Use EN 960 size designations** (circumference in 10 mm steps) as the shell sizing and labelling scheme. Buy EN 960 (≈ AUD 136) only if the project needs compatibility with test headforms. Use Sippo & Belyavin's 9 sizes ≈ 93.5% as a benchmark when choosing the number of sizes.
5. **Check FLAME 2023 Open** (CC-BY-4.0, registration) as an openly licensed shape space. Verify its cranial coverage before relying on it.

**Acquisition plan for real full-head scans:**

1. **Short term, AUD 0.** Email the RMIT authors (Perret-Ellena, Subic, Pang) about access to the 222 Australian head scans and the derived headforms. Fetch DSTO-TR-3006 manually to get ADF Army head statistics for validating the surrogate.
2. **Academic route, AUD 0.** If a university collaborator in AU or NZ can sign, request Headspace and LYHM under the York agreement. Usage must stay non-commercial research, so check whether the project's output qualifies before relying on it.
3. **Paid route, ≈ AUD 1771 (WEAR member ≈ AUD 962).** CAESAR scans are permissively licensed, but the heads are low-resolution and uncapped. Use them only if 1 and 2 fail.
4. **Best long term: collect Lochac scans directly.**
   - Use a phone- or tablet-based structured-light or photogrammetry scanner. Scan each subject in a tight swim or latex cap, and again with their usual arming cap or padding, with consent and a de-identification protocol.
   - Add three tape measurements per subject for calibration: circumference, sagittal arc and coronal arc.
   - Even 50–100 fighters, sampled at events across kingdoms and baronies, would directly cover the target population and the padding offset.
