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
                if not len(cols):
                    break
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


@dataclass
class _Res:
    x: np.ndarray | None
    status: int          # 0 optimal, 1 time limit with incumbent, 2 failed
    mip_gap: float | None
    fun: float | None
    message: str = ""


def _solve(c, rows, nv, J, S, G, time_limit, gap, x0=None):
    """HiGHS MILP via highspy, warm-started from x0 (e.g. the greedy solution) when given."""
    import highspy
    M = vstack([r[0] for r in rows]).tocsc()
    lo = np.concatenate([np.broadcast_to(r[1], r[0].shape[0]) for r in rows]).astype(float)
    hi = np.concatenate([np.broadcast_to(r[2], r[0].shape[0]) for r in rows]).astype(float)
    inf = highspy.kHighsInf
    lo[np.isinf(lo)] = -inf
    hi[np.isinf(hi)] = inf
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = nv, M.shape[0]
    lp.col_cost_ = np.asarray(c, float)
    lp.col_lower_, lp.col_upper_ = np.zeros(nv), np.ones(nv)
    lp.row_lower_, lp.row_upper_ = lo, hi
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = M.indptr
    lp.a_matrix_.index_ = M.indices
    lp.a_matrix_.value_ = M.data.astype(float)
    lp.integrality_ = [highspy.HighsVarType.kInteger] * (J + S) + [highspy.HighsVarType.kContinuous] * G
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("mip_rel_gap", float(gap))
    h.setOptionValue("random_seed", 0)
    h.passModel(lp)
    if x0 is not None:
        sol = highspy.HighsSolution()
        sol.col_value = list(map(float, x0))
        sol.value_valid = True
        h.setSolution(sol)
    h.run()
    ms = h.getModelStatus()
    info = h.getInfo()
    x = np.array(h.getSolution().col_value) if info.primal_solution_status == 2 else None
    if ms == highspy.HighsModelStatus.kOptimal:
        st = 0
    elif x is not None:
        st = 1
    else:
        st = 2
    return _Res(x, st, float(info.mip_gap) if x is not None else None,
                float(info.objective_function_value) if x is not None else None, h.modelStatusToString(ms))


def _x0(sel_cols, A_d, crown_idx, J, S, G):
    x = np.zeros(J + S + G)
    x[list(sel_cols)] = 1
    x[J + np.unique(crown_idx[list(sel_cols)])] = 1
    if len(sel_cols):
        x[J + S:] = A_d[:, list(sel_cols)].any(1)
    return x


def _map_to_kept(A, crown_of, cols, chosen, integrated) -> list:
    """Positions (in `cols`) of a feasible replacement for each chosen column: itself if kept,
    otherwise a kept column covering a superset (same crown when modular)."""
    pos = {int(j): i for i, j in enumerate(cols)}
    out = []
    for j in chosen:
        if j in pos:
            out.append(pos[j])
            continue
        cand = np.arange(len(cols)) if integrated else np.flatnonzero(crown_of[cols] == crown_of[j])
        sup = cand[~(A[:, [j]] & ~A[:, cols[cand]]).any(0)]
        if len(sup):
            out.append(int(sup[0]))
    return sorted(set(out))


def prune_columns(A: np.ndarray, crown_of: np.ndarray, integrated: bool) -> np.ndarray:
    """Indices of columns that can appear in an optimal solution. Exact reductions only:
    empty columns are dropped, and a column whose covered set is a subset of another
    column's is dropped when the two cost the same and are interchangeable under the
    constraints (same crown for modular; any column for integrated). Ties keep the first."""
    nz = np.flatnonzero(A.any(0))
    if integrated:
        groups = [nz]
    else:
        groups = [nz[crown_of[nz] == c] for c in np.unique(crown_of[nz])]
    keep = []
    for g in groups:
        if len(g) == 1:
            keep += list(g)
            continue
        B = A[:, g].astype(np.float32)
        cnt = B.sum(0)
        alive = np.ones(len(g), bool)
        order = np.argsort(-cnt, kind="stable")
        notB = 1.0 - B
        for s0 in range(0, len(g), 2048):
            blk = order[s0:s0 + 2048]
            # outside[i, j] = number of rows covered by column i but not by column j
            outside = B[:, blk].T @ notB
            for r, i in enumerate(blk):
                sup = np.flatnonzero(outside[r] == 0)
                sup = sup[sup != i]
                # i is dominated by any superset j that is strictly larger, or equal and earlier
                dom = sup[(cnt[sup] > cnt[i]) | ((cnt[sup] == cnt[i]) & (sup < i))]
                if len(dom) and alive[dom].any():
                    alive[i] = False
        keep += list(g[alive])
    return np.array(sorted(keep), int)


def max_coverage(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, k: int, *,
                 lowers_per_crown: int = 1, integrated: bool = False,
                 time_limit: float = 60, mip_gap: float = 0.0, warm: Selection | None = None) -> Selection:
    cols = prune_columns(A, crown_of, integrated)
    if not len(cols):
        return Selection([], [], 0.0, "empty")
    Ap, cp = A[:, cols], crown_of[cols]
    Ad, wd, G, J, S, crowns, cidx, nv, rows = _model(Ap, w, cp, lowers_per_crown, integrated)
    budget = np.zeros(nv)
    if integrated:
        budget[:J] = 1
    else:
        budget[J:J + S] = 1
    rows.append((csr_matrix(budget), -np.inf, float(k)))
    c = np.r_[np.zeros(J + S), -wd]
    if warm is None:
        warm = greedy(A, w, crown_of, k, lowers_per_crown, integrated)
    x0 = _x0(_map_to_kept(A, crown_of, cols, warm.assemblies, integrated), Ad, cidx, J, S, G)
    res = _solve(c, rows, nv, J, S, G, time_limit, mip_gap, x0)
    if res.x is None:
        warm.status += "+solver_failed"
        return warm
    v = cols[np.flatnonzero(res.x[:J] > 0.5)]
    sel = Selection(list(v), list(np.unique(crown_of[v])), coverage_of(A, w, v),
                    "optimal" if res.status == 0 else "time_limit", gap=res.mip_gap)
    if warm.coverage > sel.coverage + 1e-12:      # cannot happen with a warm start; kept as a guard
        warm.status += "+solver_worse"
        return warm
    return sel


def min_cost(A: np.ndarray, w: np.ndarray, crown_of: np.ndarray, target: float, *,
             crown_cost: float, lower_cost: float, lowers_per_crown: int = 1,
             integrated: bool = False, time_limit: float = 60, mip_gap: float = 0.0) -> Selection:
    cols = prune_columns(A, crown_of, integrated)
    if not len(cols):
        return Selection([], [], 0.0, "infeasible_target")
    Ap, cp = A[:, cols], crown_of[cols]
    Ad, wd, G, J, S, crowns, cidx, nv, rows = _model(Ap, w, cp, lowers_per_crown, integrated)
    if wd.sum() < target * w.sum() - 1e-9:
        return Selection([], [], 0.0, "infeasible_target")
    rows.append((csr_matrix(np.r_[np.zeros(J + S), wd]), target * w.sum(), np.inf))
    if integrated:
        c = np.r_[np.full(J, crown_cost), np.zeros(S), np.zeros(G)]
    else:
        c = np.r_[np.full(J, lower_cost), np.full(S, crown_cost), np.zeros(G)]
    # warm start: greedy with increasing family counts until the target is met
    x0 = None
    for k in range(1, S + 1):
        g = greedy(Ap, w, cp, k, lowers_per_crown, integrated)
        if g.coverage >= target - 1e-12:
            x0 = _x0(g.assemblies, Ad, cidx, J, S, G)
            break
    res = _solve(c, rows, nv, J, S, G, time_limit, mip_gap, x0)
    if res.x is None:
        return Selection([], [], 0.0, f"failed:{res.message}")
    v = cols[np.flatnonzero(res.x[:J] > 0.5)]
    return Selection(list(v), list(np.unique(crown_of[v])), coverage_of(A, w, v),
                     "optimal" if res.status == 0 else "time_limit", gap=res.mip_gap, cost=float(res.fun))


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
