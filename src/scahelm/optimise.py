"""Shell-family selection over a finite candidate catalogue (spec section 8).

Inputs: a feasibility matrix A (participants x assemblies), participant weights w, and the
crown each assembly uses. Two problem forms:

  max_coverage(k):  choose at most k crown families (each needing its own press dies) and at
                    most `lowers_per_crown` lower variants on each, maximising weighted
                    coverage.
  min_cost(target): reach weighted coverage >= target at minimum tooling cost.

Architectures differ only in how dies are counted:
  modular     one crown die set per family; lowers are laser-cut variants with their own
              (smaller) design cost.
  integrated  every distinct assembly is its own pressing, so it counts as a family.

Results are optimal *over this catalogue only*, never over all possible surfaces.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix, coo_matrix, vstack, hstack, identity


@dataclass
class Selection:
    assemblies: list            # selected assembly column indices
    crowns: list                # selected crown ids
    coverage: float             # weighted fraction covered (of the given participants)
    status: str                 # "optimal", "time_limit", "greedy", "exhaustive", ...
    gap: float | None = None    # relative MIP gap reported by the solver
    cost: float | None = None


def _dedupe(A: np.ndarray, w: np.ndarray):
    """Merge participants with identical feasibility rows (exact, weight-preserving)."""
    keep = A.any(axis=1)
    A2, w2 = A[keep], w[keep]
    if not len(A2):
        return A2, w2
    packed = np.packbits(A2, axis=1)
    _, inv = np.unique(packed, axis=0, return_inverse=True)
    inv = inv.ravel()
    W = np.bincount(inv, weights=w2)
    first = np.full(W.shape[0], -1)
    for i, g in enumerate(inv):
        if first[g] < 0:
            first[g] = i
    return A2[first], W


def coverage_of(A: np.ndarray, w: np.ndarray, cols) -> float:
    if not len(cols):
        return 0.0
    return float(w[A[:, cols].any(axis=1)].sum() / w.sum())


def greedy(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, k: int,
           lowers_per_crown: int, integrated: bool) -> Selection:
    """Greedy baseline: repeatedly add the family (crown + its best <= L lowers, chosen
    greedily within the family) with the largest marginal weighted coverage."""
    covered = np.zeros(A.shape[0], bool)
    chosen: list[int] = []
    crowns: list = []
    cand = np.unique(crown_of)
    for _ in range(k):
        best = (0.0, None, None)
        for c in cand:
            if c in crowns and not integrated:
                continue
            cols = np.flatnonzero(crown_of == c)
            pick, cov = [], covered.copy()
            for _ in range(1 if integrated else lowers_per_crown):
                gains = (A[:, cols] & ~cov[:, None]).T @ w
                if gains.max() <= 0:
                    break
                j = cols[int(np.argmax(gains))]
                pick.append(j)
                cov |= A[:, j]
                cols = cols[cols != j]
            g = w[cov & ~covered].sum()
            if g > best[0]:
                best = (g, c, pick)
        if best[1] is None:
            break
        crowns.append(best[1])
        chosen += best[2]
        for j in best[2]:
            covered |= A[:, j]
    return Selection(chosen, crowns, float(w[covered].sum() / w.sum()), "greedy")


def _model(A, w, crown_of, lowers_per_crown, integrated):
    Ad, wd = _dedupe(A, w)
    G, J = Ad.shape
    crowns = np.unique(crown_of)
    S = len(crowns)
    cidx = np.searchsorted(crowns, crown_of)
    # variables: [v_j (J) | z_s (S) | y_g (G)]
    nv = J + S + G
    rows = []
    # y_g - sum_j A_gj v_j <= 0
    Acov = hstack([-csr_matrix(Ad.astype(float)), csr_matrix((G, S)), identity(G, format="csr")])
    rows.append((Acov, -np.inf, 0.0))
    # v_j - z_s(j) <= 0
    link = coo_matrix((np.r_[np.ones(J), -np.ones(J)],
                       (np.r_[np.arange(J), np.arange(J)], np.r_[np.arange(J), J + cidx])), shape=(J, nv))
    rows.append((link.tocsr(), -np.inf, 0.0))
    if not integrated:
        # sum_{j in s} v_j - L z_s <= 0
        lim = coo_matrix((np.r_[np.ones(J), -lowers_per_crown * np.ones(S)],
                          (np.r_[cidx, np.arange(S)], np.r_[np.arange(J), J + np.arange(S)])), shape=(S, nv))
        rows.append((lim.tocsr(), -np.inf, 0.0))
    return Ad, wd, G, J, S, crowns, cidx, nv, rows


def _solve(c, rows, nv, J, S, G, time_limit, gap, extra=None):
    cons = [LinearConstraint(M, lo, hi) for M, lo, hi in rows]
    if extra:
        cons += extra
    integ = np.r_[np.ones(J + S), np.zeros(G)]
    res = milp(c, constraints=cons, integrality=integ, bounds=Bounds(0, 1),
               options={"time_limit": time_limit, "mip_rel_gap": gap, "disp": False})
    return res


def max_coverage(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, k: int, *,
                 lowers_per_crown: int = 1, integrated: bool = False,
                 time_limit: float = 60, mip_gap: float = 0.0, warm: Selection | None = None) -> Selection:
    Ad, wd, G, J, S, crowns, cidx, nv, rows = _model(A, w, crown_of, lowers_per_crown, integrated)
    if G == 0:
        return Selection([], [], 0.0, "empty")
    # family budget: crowns for modular, assemblies for integrated
    budget = np.zeros(nv)
    if integrated:
        budget[:J] = 1
    else:
        budget[J:J + S] = 1
    rows.append((csr_matrix(budget), -np.inf, float(k)))
    c = np.r_[np.zeros(J + S), -wd]
    res = _solve(c, rows, nv, J, S, G, time_limit, mip_gap)
    if res.x is None:
        return warm or Selection([], [], 0.0, f"failed:{res.message}")
    v = np.flatnonzero(res.x[:J] > 0.5)
    sel = Selection(list(v), list(crowns[np.unique(cidx[v])]), coverage_of(A, w, v),
                    "optimal" if res.status == 0 else "time_limit",
                    gap=getattr(res, "mip_gap", None))
    if warm is not None and warm.coverage > sel.coverage:
        warm.status += "+solver_worse"
        return warm
    return sel


def min_cost(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, target: float, *,
             crown_cost: float, lower_cost: float, lowers_per_crown: int = 1,
             integrated: bool = False, time_limit: float = 60, mip_gap: float = 0.0) -> Selection:
    Ad, wd, G, J, S, crowns, cidx, nv, rows = _model(A, w, crown_of, lowers_per_crown, integrated)
    if G == 0 or wd.sum() < target * w.sum() - 1e-9:
        return Selection([], [], 0.0, "infeasible_target")
    cov = np.r_[np.zeros(J + S), wd]
    rows.append((csr_matrix(cov), target * w.sum(), np.inf))
    if integrated:
        c = np.r_[np.full(J, crown_cost), np.zeros(S), np.zeros(G)]
    else:
        c = np.r_[np.full(J, lower_cost), np.full(S, crown_cost), np.zeros(G)]
    res = _solve(c, rows, nv, J, S, G, time_limit, mip_gap)
    if res.x is None:
        return Selection([], [], 0.0, f"failed:{res.message}")
    v = np.flatnonzero(res.x[:J] > 0.5)
    return Selection(list(v), list(crowns[np.unique(cidx[v])]), coverage_of(A, w, v),
                     "optimal" if res.status == 0 else "time_limit",
                     gap=getattr(res, "mip_gap", None), cost=float(res.fun))


def exhaustive(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, k: int, *,
               lowers_per_crown: int = 1, integrated: bool = False) -> Selection:
    """Brute force for small instances; used to check the MILP."""
    J = A.shape[1]
    best = Selection([], [], 0.0, "exhaustive")
    for r in range(1, (k if integrated else k * lowers_per_crown) + 1):
        for cols in itertools.combinations(range(J), r):
            cs = crown_of[list(cols)]
            u, n = np.unique(cs, return_counts=True)
            if integrated and r > k:
                continue
            if not integrated and (len(u) > k or n.max() > lowers_per_crown):
                continue
            cov = coverage_of(A, w, list(cols))
            if cov > best.coverage + 1e-12:
                best = Selection(list(cols), list(u), cov, "exhaustive")
    return best
