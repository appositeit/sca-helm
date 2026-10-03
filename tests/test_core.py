import copy

import numpy as np
import pandas as pd
import pytest

from scahelm import export, fit, geometry, heads, ingest, liner, optimise, shells
from scahelm.pipeline import load_config

R_HEAD, Z0 = 50.0, 15.0


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def sphere_cfg(cfg):
    """Priors with zero spread so the surrogate head is an exact sphere of radius R_HEAD
    centred at (0, 0, Z0)."""
    c = copy.deepcopy(cfg)
    hm = c["head_model"]
    hm["f_front"] = [0.5, 0.0]
    hm["z_equator"] = [Z0, 0.0]
    hm["n_vertical"] = [2.0, 0.0]
    hm["c_low_frac"] = [R_HEAD / (R_HEAD + Z0), 0.0]
    hm["hair_allowance"] = 0.0
    c["shell"].update(manufacturing_tolerance=0.0, measurement_uncertainty=0.0, seam_bead_height=0.0,
                      crown_bottom_z=-20.0, brow_z=-100.0)
    return c


def sphere_heads(c, n=3):
    m = pd.DataFrame({"pid": [f"S{i}" for i in range(n)], "sex": "M", "weight": 1.0, "source": "test",
                      "head_length": 2 * R_HEAD, "head_breadth": 2 * R_HEAD,
                      "head_circumference": 2 * np.pi * R_HEAD, "tragion_top": Z0 + R_HEAD,
                      "menton_sellion": 100.0})
    return heads.build(m, c, seed=0)


# ------------------------------------------------------------------ geometry and units
def test_parametric_points_lie_on_implicit_surface():
    sq = geometry.Superquadric(100, 90, 75, 110, 70, 30, 2.4, 2.3)
    E, W = geometry.param_grid(30, 60)
    assert np.allclose(sq.implicit(sq.point(E, W)), 1.0, atol=1e-9)


def test_perimeter_fit_recovers_ellipse():
    nh, ok = geometry.fit_nh_to_perimeter(100, 100, 80, geometry.horizontal_perimeter(100, 100, 80, 2.0))
    assert ok and abs(nh - 2.0) < 1e-3


def test_head_extents_match_measurements(cfg):
    m = heads.synthetic_measurements(30, seed=3)
    H = heads.build(m, cfg, seed=4)
    for i in range(0, 30, 7):
        sq = H.superquadric(i)
        E, W = geometry.param_grid(200, 400, eta_min=-np.pi / 2)
        p = sq.point(E, W)
        r = H.table.iloc[i]
        assert p[:, 1].max() - p[:, 1].min() == pytest.approx(r.head_length, abs=0.5)
        assert p[:, 0].max() - p[:, 0].min() == pytest.approx(r.head_breadth, abs=0.5)
        assert p[:, 2].max() == pytest.approx(r.tragion_top, abs=0.5)        # z up, tragion at 0
        assert p[:, 1].max() == pytest.approx(r.a_front, abs=0.5)            # y anterior
        assert geometry.horizontal_perimeter(r.a_front, r.a_rear, r.b, r.nh) == pytest.approx(
            r.head_circumference, rel=1e-3)


def test_landmarks_oriented(cfg):
    H = heads.build(heads.synthetic_measurements(20, seed=5), cfg, seed=6)
    lm = H.landmarks
    assert (lm["pronasale"][:, 1] > lm["sellion"][:, 1]).all()          # nose forward of sellion
    assert (lm["menton"][:, 2] < lm["pronasale"][:, 2]).all()           # chin below nose
    assert (lm["pupils"][:, 0, 0] > 0).all() and (lm["pupils"][:, 1, 0] < 0).all()
    assert (lm["sellion"][:, 2] > 0).all()                              # above tragion plane


# ------------------------------------------------------------------ fit evaluation
def test_concentric_spheres_give_exact_clearance(cfg):
    c = sphere_cfg(cfg)
    H = sphere_heads(c)
    ev = fit.Evaluator(H, c)
    shell = shells.Crown("T", "test", geometry.Superquadric(70, 70, 70, 70, 70, Z0, 2.0, 2.0))
    res = ev.crown(shell, prune=False)
    k0 = int(np.flatnonzero((ev.poses == 0).all(1))[0])
    expect = 20.0 - ev.allow
    assert np.allclose(res.gaps[k0], expect, atol=0.3)
    # move the head up 6 mm: crown pad gap shrinks by 6 (to within sampling), front unchanged
    k_up = int(np.flatnonzero((ev.poses[:, 0] == 0) & (ev.poses[:, 1] == 6))[0])
    zi = c["liner"]["zones"]
    assert res.gaps[k_up][:, zi.index("crown")] == pytest.approx(expect - 6, abs=0.6)


def test_intrusion_is_detected(cfg):
    c = sphere_cfg(cfg)
    H = sphere_heads(c)
    ev = fit.Evaluator(H, c)
    small = shells.Crown("T", "test", geometry.Superquadric(45, 45, 45, 45, 45, Z0, 2.0, 2.0))
    res = ev.crown(small, prune=False)
    assert (res.fail & fit.HARD).all()
    assert not res.ok.any()


def test_pruning_is_exact(cfg):
    """The fast path (ray filter + distance field + near-threshold exact re-check) must give
    exactly the same feasibility as direct evaluation of every point at every pose."""
    H = heads.build(heads.synthetic_measurements(40, seed=7), cfg, seed=8)
    ev = fit.Evaluator(H, cfg)
    cat = shells.crown_catalogue(H.table, cfg, shells.nominal_gap(cfg, ev.window) + 6)
    tested = 0
    for crown in cat[::max(1, len(cat) // 8)]:
        a, b = ev.crown(crown, prune=True), ev.crown(crown, prune=False)
        assert (a.ok == b.ok).all(), crown.id
        tested += b.ok.any()
    assert tested >= 2          # at least two crowns that fit someone were compared


def test_pose_choice_within_bounds(cfg):
    H = heads.build(heads.synthetic_measurements(40, seed=11), cfg, seed=12)
    ev = fit.Evaluator(H, cfg)
    pc = cfg["pose"]
    assert ev.poses[:, 0].min() >= min(pc["dy"]) and ev.poses[:, 0].max() <= max(pc["dy"])
    assert ev.poses[:, 1].min() >= min(pc["dz"]) and ev.poses[:, 1].max() <= max(pc["dz"])
    crown = shells.crown_catalogue(H.table, cfg, shells.nominal_gap(cfg, ev.window) + 6)[10]
    cr = ev.crown(crown)
    for l in shells.lowers_for(crown, cfg)[:3]:
        feas, pose, _ = ev.combine(cr, ev.lower(l), l)
        assert ((pose >= 0) == feas).all()
        assert pose.max() < len(ev.poses)
        # the chosen pose really passes both crown and lower checks
        lf = ev.lower(l)
        for i in np.flatnonzero(feas):
            assert cr.fail[pose[i], i] == 0 and lf[pose[i], i] == 0


# ------------------------------------------------------------------ liner
def test_pad_choice_is_discrete_and_in_band(cfg):
    lin = cfg["liner"]
    tab = liner.StackTable.from_config(lin)
    allowed = {t for ts in lin["catalogue"].values() for t in ts}
    for s in tab.stacks:
        assert all(t in allowed for _, t in s.layers)
        assert s.layers[0][0] == lin["stack_rules"]["base_material"]
    g = np.linspace(0, 40, 801)
    idx, _ = liner.choose(g, tab, lin)
    lo, hi = lin["fit_strain"]
    for gi, i in zip(g, idx):
        if i < 0:
            continue
        T = tab.T[i]
        assert lo - 1e-9 <= (T - gi) / T <= hi + 1e-9
        assert T <= lin["max_liner_depth"] and T >= lin["min_padding"]
    assert (idx[g < 5] < 0).all()                    # nothing fills a 5 mm gap


def test_series_compliance():
    lin = {"materials": {"a": {"E_kPa": 100, "G_kPa": 50, "densification_strain": 0.5},
                         "b": {"E_kPa": 400, "G_kPa": 100, "densification_strain": 0.5}},
           "catalogue": {"a": [10.0], "b": [8.0]}, "stack_rules": {"base_material": "a", "max_fitting_layers": 1}}
    st = {s.label: s for s in liner.enumerate_stacks(lin)}
    assert st["a10+b8"].normal_compliance == pytest.approx(10 / 100 + 8 / 400)
    assert st["a10+b8"].shear_compliance == pytest.approx(10 / 50 + 8 / 100)


# ------------------------------------------------------------------ optimiser and counting
def test_milp_matches_exhaustive():
    rng = np.random.default_rng(0)
    for trial in range(6):
        A = rng.random((40, 8)) < 0.25
        w = rng.random(40) + 0.5
        crown_of = np.array(list("aabbccdd"))
        for integrated, L in ((False, 2), (True, 1)):
            for k in (1, 2):
                ex = optimise.exhaustive(A, w, crown_of, k, lowers_per_crown=L, integrated=integrated)
                mi = optimise.max_coverage(A, w, crown_of, k, lowers_per_crown=L, integrated=integrated)
                assert mi.coverage == pytest.approx(ex.coverage, abs=1e-9), (trial, integrated, k)
                gr = optimise.greedy(A, w, crown_of, k, L, integrated)
                assert gr.coverage <= ex.coverage + 1e-12


def test_family_counting():
    A = np.eye(4, dtype=bool)
    crown_of = np.array(["a", "a", "a", "b"])
    w = np.ones(4)
    # modular: one crown family with 3 lowers covers 3 people
    m = optimise.max_coverage(A, w, crown_of, 1, lowers_per_crown=3)
    assert m.coverage == pytest.approx(0.75) and m.crowns == ["a"]
    # integrated: every assembly is its own die set, so k=1 covers one person
    i = optimise.max_coverage(A, w, crown_of, 1, integrated=True)
    assert i.coverage == pytest.approx(0.25)
    c = optimise.min_cost(A, w, crown_of, 1.0, crown_cost=100, lower_cost=1, lowers_per_crown=3)
    assert c.cost == pytest.approx(2 * 100 + 4 * 1)


def test_dedupe_preserves_weight():
    A = np.array([[1, 0], [1, 0], [0, 1], [0, 0]], bool)
    w = np.array([1.0, 2.0, 3.0, 4.0])
    Ad, wd = optimise._dedupe(A, w)
    assert len(Ad) == 2 and wd.sum() == pytest.approx(6.0)


def test_duplicate_participants_rejected(cfg):
    m = heads.synthetic_measurements(5, seed=1)
    m.loc[1, "pid"] = m.loc[0, "pid"]
    with pytest.raises(ValueError):
        heads.build(m, cfg, seed=0)


def test_split_is_by_participant():
    t = heads.synthetic_measurements(500, seed=2)
    val = ingest.split_by_participant(t, 0.3, seed=1)
    assert not set(t.pid[val]) & set(t.pid[~val])
    assert abs(val.mean() - 0.3) < 0.01


def test_sex_weights_hit_target():
    t = heads.synthetic_measurements(400, seed=3, female_fraction=0.4)
    w = heads.sex_weights(t, 0.15)
    assert w[(t.sex == "F").to_numpy()].sum() / w.sum() == pytest.approx(0.15)


# ------------------------------------------------------------------ exports
def test_stl_dimensions(tmp_path):
    sq = geometry.Superquadric(120, 115, 100, 125, 90, 30, 2.4, 2.2)
    crown = shells.Crown("X", "test", sq)
    paths = export.write_stl(crown, tmp_path, thickness=2.0, z_min=-35)
    import trimesh
    inner = trimesh.load(tmp_path / "X_inner.stl")
    lo, hi = inner.bounds
    assert hi[1] == pytest.approx(120, abs=0.5) and lo[1] == pytest.approx(-115, abs=0.5)
    assert hi[0] == pytest.approx(100, abs=0.5)
    assert hi[2] == pytest.approx(155, abs=0.5) and lo[2] == pytest.approx(-35, abs=0.5)
    outer = trimesh.load(tmp_path / "X_outer.stl")
    assert outer.bounds[1][1] == pytest.approx(122, abs=0.6)


def test_dxf_openings_below_dowel(tmp_path, cfg):
    crown = shells.Crown("X", "test", geometry.Superquadric(120, 115, 100, 125, 90, 30, 2.4, 2.2))
    lower = shells.lowers_for(crown, cfg)[0]
    info = export.grille_blank(lower, crown, cfg, tmp_path / "g.dxf")
    assert info["dowel_rule_ok"] and info["inscribed_opening"] <= 24.0 + 1e-9
    import ezdxf
    doc = ezdxf.readfile(tmp_path / "g.dxf")
    assert doc.units == ezdxf.units.MM


def test_distance_accuracy(cfg):
    """Evaluator distances agree with a dense (0.7 mm) reference within the sampling bound,
    and never under-estimate clearance by more than the reference's own resolution."""
    from scipy.spatial import cKDTree
    H = heads.build(heads.synthetic_measurements(40, seed=13), cfg, seed=14)
    ev = fit.Evaluator(H, cfg)
    crown = shells.crown_catalogue(H.table, cfg, shells.nominal_gap(cfg, ev.window) + 6)[30]
    rng = np.random.default_rng(0)
    pts = H.points[H.region]
    q = pts[rng.choice(len(pts), 3000)] + np.c_[np.zeros(3000), ev.poses[rng.integers(0, len(ev.poses), 3000)]]
    q = q[crown.sq.implicit(q) < 1]
    ref = cKDTree(geometry.sample_surface(crown.sq, 0.7, z_min=-120)).query(q)[0]
    samples = shells.shell_samples(crown, cfg)
    tree, nrm = cKDTree(samples), crown.sq.normal(samples)
    d, j = tree.query(q, k=cfg["shell"].get("plane_neighbours", 24))
    plane = np.abs(np.einsum("ikj,ikj->ik", samples[j] - q[:, None, :], nrm[j])).min(1)
    est = np.minimum(d[:, 0], plane)
    shell_part = ev.bound - H.sample_spacing_max ** 2 / (2 * H.min_radius)
    assert (est - ref).max() <= shell_part + 0.05
    assert (ref - est).max() <= 0.4          # reference point cloud itself overestimates by <~ 0.35
