"""Piecewise superquadric surfaces used for both surrogate heads and candidate shells.

Frame: x lateral (+ = wearer's left), y anterior, z superior, millimetres.

A surface is defined by

    ((|x|/b)^nh + (|y|/a)^nh)^(nv/nh) + (|z - z_eq|/c)^nv = 1

with a = a_front for y >= 0, a_rear for y < 0, and c = c_up above the equator, c_low below.
Because the exponents are > 1 the halves join with matching first derivatives, so the
surface is smooth (C1) everywhere. For nh, nv >= 2 it is also convex, which keeps it
star-shaped and free of undercuts in the vertical draw direction.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np


def _spow(t: np.ndarray, e: float) -> np.ndarray:
    return np.sign(t) * np.abs(t) ** e


@dataclass(frozen=True)
class Superquadric:
    a_front: float
    a_rear: float
    b: float
    c_up: float
    c_low: float
    z_eq: float
    nh: float = 2.0
    nv: float = 2.0

    def as_dict(self) -> dict:
        return asdict(self)

    # -- implicit form ----------------------------------------------------------------
    def implicit(self, p: np.ndarray) -> np.ndarray:
        """< 1 inside, 1 on the surface, > 1 outside. p: (..., 3)."""
        x, y, z = p[..., 0], p[..., 1], p[..., 2] - self.z_eq
        a = np.where(y >= 0, self.a_front, self.a_rear)
        c = np.where(z >= 0, self.c_up, self.c_low)
        h = (np.abs(x) / self.b) ** self.nh + (np.abs(y) / a) ** self.nh
        return h ** (self.nv / self.nh) + (np.abs(z) / c) ** self.nv

    # -- parametric form --------------------------------------------------------------
    def point(self, eta: np.ndarray, omega: np.ndarray) -> np.ndarray:
        """eta: elevation in [-pi/2, pi/2]; omega: azimuth, 0 = anterior, +pi/2 = left."""
        e1, e2 = 2.0 / self.nv, 2.0 / self.nh
        ce = np.abs(np.cos(eta)) ** e1
        se = _spow(np.sin(eta), e1)
        cw, sw = _spow(np.cos(omega), e2), _spow(np.sin(omega), e2)
        a = np.where(np.cos(omega) >= 0, self.a_front, self.a_rear)
        c = np.where(np.sin(eta) >= 0, self.c_up, self.c_low)
        return np.stack([self.b * ce * sw, a * ce * cw, self.z_eq + c * se], axis=-1)

    def normal(self, p: np.ndarray, h: float = 1e-3) -> np.ndarray:
        """Outward unit normal from the implicit gradient (central differences)."""
        g = np.empty_like(p)
        for k in range(3):
            d = np.zeros(3)
            d[k] = h
            g[..., k] = self.implicit(p + d) - self.implicit(p - d)
        return g / np.linalg.norm(g, axis=-1, keepdims=True)

    def front_extent_at(self, z: float) -> float:
        """Anterior y of the surface on the mid-sagittal plane at height z (0 if outside)."""
        dz = z - self.z_eq
        c = self.c_up if dz >= 0 else self.c_low
        r = 1.0 - (abs(dz) / c) ** self.nv
        if r <= 0:
            return 0.0
        return self.a_front * r ** (1.0 / self.nv)

    def scaled(self, s: float) -> "Superquadric":
        return Superquadric(self.a_front * s, self.a_rear * s, self.b * s, self.c_up * s,
                            self.c_low * s, self.z_eq * s, self.nh, self.nv)

    def offset_approx(self, t: float) -> "Superquadric":
        """Same family with every semi-axis grown by t. Not a true offset surface; used only
        to make outer-surface previews and starting envelopes."""
        return Superquadric(self.a_front + t, self.a_rear + t, self.b + t, self.c_up + t,
                            self.c_low + t, self.z_eq, self.nh, self.nv)


def horizontal_perimeter(a_front: float, a_rear: float, b: float, nh: float, n: int = 720) -> float:
    w = np.linspace(0, 2 * np.pi, n, endpoint=False)
    e2 = 2.0 / nh
    a = np.where(np.cos(w) >= 0, a_front, a_rear)
    x = b * _spow(np.sin(w), e2)
    y = a * _spow(np.cos(w), e2)
    return float(np.sum(np.hypot(np.diff(np.r_[x, x[0]]), np.diff(np.r_[y, y[0]]))))


def fit_nh_to_perimeter(a_front: float, a_rear: float, b: float, perimeter: float,
                        lo: float = 1.6, hi: float = 3.5) -> tuple[float, bool]:
    """Find the horizontal exponent whose section perimeter matches a measured
    circumference. Returns (nh, ok); ok is False when the target is outside the bracket
    and the nearest bound is returned."""
    f = lambda n: horizontal_perimeter(a_front, a_rear, b, n) - perimeter
    flo, fhi = f(lo), f(hi)
    if flo > 0:
        return lo, False
    if fhi < 0:
        return hi, False
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), True


def param_grid(n_eta: int, n_omega: int, eta_min: float = -np.pi / 2 + 0.05,
               eta_max: float = np.pi / 2) -> tuple[np.ndarray, np.ndarray]:
    eta = np.linspace(eta_min, eta_max, n_eta)
    omega = np.linspace(-np.pi, np.pi, n_omega, endpoint=False)
    E, W = np.meshgrid(eta, omega, indexing="ij")
    return E.ravel(), W.ravel()


def sample_surface(sq: Superquadric, spacing: float, z_min: float | None = None) -> np.ndarray:
    """Roughly uniform point sampling at the given spacing (mm): oversample the parametric
    grid, then keep one point per spacing-sized voxel."""
    span = 2 * np.pi * max(sq.a_front, sq.a_rear, sq.b, sq.c_up)
    n = int(np.ceil(span / (spacing / 3)))
    E, W = param_grid(max(n // 2, 32), max(n, 64), eta_min=-np.pi / 2 + 1e-3)
    p = sq.point(E, W)
    if z_min is not None:
        p = p[p[:, 2] >= z_min]
    key = np.floor(p / spacing).astype(np.int64)
    _, idx = np.unique(key, axis=0, return_index=True)
    return p[np.sort(idx)]


def min_curvature_radius(sq: Superquadric, z_min: float, n: int = 120) -> float:
    """Smallest principal radius of curvature over the surface above z_min, estimated
    from the implicit Hessian. Used as a press-compatibility constraint."""
    E, W = param_grid(n, 2 * n, eta_min=-np.pi / 2 + 0.02, eta_max=np.pi / 2 - 0.02)
    p = sq.point(E, W)
    p = p[p[:, 2] >= z_min]
    h = 0.05
    F = sq.implicit
    grad = np.stack([(F(p + h * e) - F(p - h * e)) / (2 * h) for e in np.eye(3)], -1)
    H = np.empty(p.shape[:-1] + (3, 3))
    for i, ei in enumerate(np.eye(3)):
        for j, ej in enumerate(np.eye(3)):
            H[..., i, j] = (F(p + h * ei + h * ej) - F(p + h * ei - h * ej)
                            - F(p - h * ei + h * ej) + F(p - h * ei - h * ej)) / (4 * h * h)
    g = np.linalg.norm(grad, axis=-1)
    nrm = grad / g[:, None]
    P = np.eye(3)[None] - nrm[:, :, None] * nrm[:, None, :]
    S = P @ H @ P / g[:, None, None]
    k = np.linalg.eigvalsh(S)
    kmax = np.max(np.abs(k), axis=-1)
    return float(1.0 / np.max(kmax))


def mesh(sq: Superquadric, n_eta: int = 90, n_omega: int = 180, z_min: float | None = None):
    """Triangulated closed-or-open surface as (vertices, faces)."""
    eta_min = -np.pi / 2
    if z_min is not None:
        rel = (z_min - sq.z_eq) / (sq.c_low if z_min < sq.z_eq else sq.c_up)
        rel = np.clip(rel, -1, 1)
        eta_min = np.arcsin(np.sign(rel) * np.abs(rel) ** (sq.nv / 2))
    eta = np.linspace(eta_min, np.pi / 2, n_eta)
    omega = np.linspace(-np.pi, np.pi, n_omega, endpoint=False)
    E, W = np.meshgrid(eta[:-1], omega, indexing="ij")
    v = sq.point(E.ravel(), W.ravel())
    apex = sq.point(np.array([np.pi / 2]), np.array([0.0]))
    verts = np.vstack([v, apex])
    faces = []
    R, C = n_eta - 1, n_omega
    idx = lambda r, c: r * C + (c % C)
    for r in range(R - 1):
        for c in range(C):
            faces.append([idx(r, c), idx(r, c + 1), idx(r + 1, c + 1)])
            faces.append([idx(r, c), idx(r + 1, c + 1), idx(r + 1, c)])
    top = len(verts) - 1
    for c in range(C):
        faces.append([idx(R - 1, c), idx(R - 1, c + 1), top])
    return verts, np.asarray(faces)
