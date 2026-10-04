"""CAD exports (all EXPLORATORY): STL meshes, STEP B-spline surfaces, DXF laser blanks.

Units are millimetres in every file. The shell frame is the analysis frame (x lateral,
y anterior, z superior). Onshape imports STEP/STL in that orientation with "Y up" off.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from .geometry import Superquadric, mesh
from .shells import Crown, Lower


def shell_meshes(crown: Crown, thickness: float, z_min: float) -> dict[str, trimesh.Trimesh]:
    """Inner surface, approximate outer surface (true normal offset of the inner mesh), and
    the left/right inner halves split on the sagittal plane x = 0."""
    v, f = mesh(crown.sq, z_min=z_min)
    inner = trimesh.Trimesh(v, f, process=True)
    trimesh.repair.fix_normals(inner)
    if inner.volume < 0:
        inner.invert()
    outer = inner.copy()
    outer.vertices = inner.vertices + thickness * inner.vertex_normals
    out = {"inner": inner, "outer": outer}
    for side, normal in (("left", [1, 0, 0]), ("right", [-1, 0, 0])):
        out[f"inner_{side}"] = inner.slice_plane([0, 0, 0], normal)
    return out


def write_stl(crown: Crown, outdir: Path, thickness: float, z_min: float) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, m in shell_meshes(crown, thickness, z_min).items():
        p = outdir / f"{crown.id}_{name}.stl"
        m.export(p)
        paths.append(p)
    return paths


def write_step(crown: Crown, path: Path, z_min: float, n_eta: int = 40, n_omega: int = 80) -> Path:
    """Inner surface as one periodic B-spline surface interpolated through the analytic
    superquadric. The apex row is dropped (a pole would make the surface degenerate), so the
    exported surface stops ~1 degree short of the crown; the gap is < 1 mm across."""
    try:                                   # OCP < 8
        from OCP.TColgp import TColgp_Array2OfPnt
    except ImportError:                    # OCP 8 exposes NCollection templates here
        from OCP.OCP.collections import Array2_gp_Pnt as TColgp_Array2OfPnt
    from OCP.gp import gp_Pnt
    from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.Interface import Interface_Static
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.GeomAbs import GeomAbs_C2

    sq = crown.sq
    rel = np.clip((z_min - sq.z_eq) / (sq.c_low if z_min < sq.z_eq else sq.c_up), -1, 1)
    eta0 = np.arcsin(np.sign(rel) * np.abs(rel) ** (sq.nv / 2))
    eta = np.linspace(eta0, np.radians(89.0), n_eta)
    omega = np.linspace(-np.pi, np.pi, n_omega)       # closed: first == last
    arr = TColgp_Array2OfPnt(1, n_eta, 1, n_omega)
    for i, e in enumerate(eta):
        pts = sq.point(np.full(n_omega, e), omega)
        pts[-1] = pts[0]
        for j, p in enumerate(pts):
            arr.SetValue(i + 1, j + 1, gp_Pnt(*map(float, p)))
    surf = GeomAPI_PointsToBSplineSurface(arr, 3, 8, GeomAbs_C2, 0.05).Surface()
    face = BRepBuilderAPI_MakeFace(surf, 1e-6).Face()
    w = STEPControl_Writer()
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w.Transfer(face, STEPControl_AsIs)
    path.parent.mkdir(parents=True, exist_ok=True)
    if w.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: {path}")
    return path


def grille_blank(lower: Lower, crown: Crown, cfg: dict, path: Path,
                 bar_width: float = 10.0, max_opening: float = 24.0) -> dict:
    """Flat laser-cut blank for the face plate (EXPLORATORY).

    The plate is treated as a band wrapped around the front of the crown at the face-plate
    depth, so its flat width is the arc length of a circle of that radius over the face
    angle. Openings are rectangles whose inscribed circle is below `max_opening`, chosen
    smaller than a 25.4 mm dowel (Society rule: a 1 inch dowel must not enter any opening).
    Whether a plate ligament of `bar_width` x sheet thickness is acceptable in place of a
    4.76 mm round bar is an OPEN marshal question; see docs/rules_matrix.md.
    """
    import ezdxf

    lo = cfg["lower"]
    half_angle = np.radians(cfg["shell"]["face_half_angle"] + 10)
    radius = lower.face_y
    width = 2 * radius * half_angle
    top = lower.grille_top + 12.0            # overlap onto the crown for the weld/rivet line
    bottom = lower.z_low
    height = top - bottom
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    for name, colour in (("CUT", 1), ("BEND", 3), ("NOTE", 7)):
        doc.layers.add(name, color=colour)
    x0 = -width / 2
    msp.add_lwpolyline([(x0, 0), (-x0, 0), (-x0, height), (x0, height)], close=True, dxfattribs={"layer": "CUT"})
    # grille openings between grille_bottom and grille_top
    gz0, gz1 = lower.grille_bottom - bottom, lower.grille_top - bottom
    # ceil, so that no opening exceeds max_opening in either direction
    n_cols = int(np.ceil((width - 2 * 15 + bar_width) / (max_opening + bar_width)))
    n_rows = int(np.ceil((gz1 - gz0 + bar_width) / (max_opening + bar_width)))
    n_cols, n_rows = max(n_cols, 1), max(n_rows, 1)
    ow = (width - 2 * 15 - (n_cols - 1) * bar_width) / n_cols
    oh = (gz1 - gz0 - (n_rows - 1) * bar_width) / n_rows
    count = 0
    for r in range(n_rows):
        for c in range(n_cols):
            xa = x0 + 15 + c * (ow + bar_width)
            za = gz0 + r * (oh + bar_width)
            msp.add_lwpolyline([(xa, za), (xa + ow, za), (xa + ow, za + oh), (xa, za + oh)], close=True,
                               dxfattribs={"layer": "CUT"})
            count += 1
    # vertical bend lines where the plate wraps from face to cheeks (+-35 deg)
    for s in (-1, 1):
        xb = s * radius * np.radians(35)
        msp.add_line((xb, 0), (xb, height), dxfattribs={"layer": "BEND"})
    msp.add_text(f"{lower.id} EXPLORATORY - not validated; t={cfg['shell']['material']['thickness']} mm; "
                 f"inscribed opening {min(ow, oh):.1f} mm", dxfattribs={"layer": "NOTE", "height": 4}
                 ).set_placement((x0, -10))
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return {"lower_id": lower.id, "flat_width": width, "flat_height": height, "openings": count,
            "opening_w": ow, "opening_h": oh, "inscribed_opening": min(ow, oh), "bar_width": bar_width,
            "dowel_rule_ok": min(ow, oh) < 25.4}
