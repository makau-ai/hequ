"""Layer 2 — unification sieves.

Given a loaded set of TypedExpression entries, Layer 2 emits two
kinds of candidate pair:

1. **Dimensional candidates** — pairs whose variables have the same
   multiset of pint dimensions, up to relabeling. Necessary
   condition for any *dimensional* analogy. Cheap to compute.

2. **Structural candidates** — pairs whose canonical forms are
   syntactically isomorphic as sympy expression trees under a
   variable permutation, without regard to units. Catches
   cross-domain identities where the algebraic shape is the same
   but the declared units differ (e.g., Fourier's q = −k∇T and
   Fick's J = −D∇C both have the form `flux + coupling*gradient`).

Neither sieve is a discovery engine by itself — each produces
candidates for Layer 3 to test with substitutions and numerical
agreement. Both sieves are empirical: they surface matches, never
"prove" them.

Complexity
----------
Dimensional sieve: O(N²) multiset comparisons over N equations.
Structural sieve: O(N² × V!) where V is the number of variables in
the equations being compared. V is small (3–6 for the canonical
corpus), so V! ≤ 720.

**Hash pre-filter.** `structural_signature` computes an alpha-renamed
sympy hash of each canonical form; pairs with different signatures
cannot possibly be identical under any rename and are skipped before
any permutation search. This is the scalability fix flagged by the
readiness audit: at N=30 with V=6 the unfiltered search is ~200k
simplify calls per run; with the hash pre-filter it drops by an
order of magnitude or more because most cross-domain pairs have
different shapes.
"""

from __future__ import annotations

import itertools
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import sympy as sp

from .typed_expression import TypedExpression


STRUCTURAL_SIEVE_V_CAP = 6
"""Variable-count cap for the O(V!) exact structural sieve.

The readiness auditor's Medium sequencing item: at V ≥ 7, both the
`structural_signature` and the `_find_permutation_match` inner search
scale as V! and become the wall-clock bottleneck (7! = 5040, 8! =
40320 simplify calls *per equation*). Equations with V > CAP use a
cheap polynomial-time signature that does not attempt alpha-canonical
ordering, and skip the permutation-based structural sieve entirely
(the CoV sieve and axiom gate still participate). Navier-Stokes is
the first Medium equation to trip this cap.
"""


def _cheap_signature(expr: sp.Expr) -> str:
    """Polynomial-time, rename-invariant fingerprint for large-V
    expressions.

    Normalizes by tagging every free symbol with the same placeholder
    name. This makes the signature non-discriminating across
    equations with different structure but the same op-count — it
    collapses more than it should — but it's O(1) to compute and
    avoids the V! exact search. Exact matches against large-V
    equations now have to survive a separate code path, not through
    Layer 2's rename sieve.
    """
    free = list(expr.free_symbols)
    if not free:
        return sp.srepr(expr)
    all_to_v0 = {s: sp.Symbol("_vany") for s in free}
    return sp.srepr(expr.subs(all_to_v0, simultaneous=True))


def structural_signature(expr: sp.Expr) -> str:
    """Return a rename-invariant signature used as a cheap pre-filter
    by the structural sieves.

    For expressions with V ≤ `STRUCTURAL_SIEVE_V_CAP` free symbols,
    we compute the true alpha-canonical form by enumerating all V!
    renamings and picking the lexicographically smallest `sp.srepr`.
    For V > CAP, we fall back to a polynomial-time collapsed
    signature (`_cheap_signature`) and the caller must NOT rely on
    the signature discriminating two structurally different
    expressions.

    The CAP exists because the exact search is O(V!) and 8! = 40320
    simplify calls per equation is the first thing that makes
    Medium-scope runs impractical (see readiness audit). Navier-
    Stokes (V=8) is the first equation in the corpus to use the
    fallback path.
    """
    free = sorted(expr.free_symbols, key=lambda s: s.name)
    if not free:
        return sp.srepr(sp.simplify(expr))
    V = len(free)
    if V > STRUCTURAL_SIEVE_V_CAP:
        # Large-V: use the cheap fallback. This collapses more
        # structure than the exact form, so V > CAP pairs will match
        # many things — but `structural_sieve` caps the permutation
        # inner search at CAP too, so this doesn't cause exponential
        # blowup downstream.
        return _cheap_signature(expr)
    placeholders = [sp.Symbol(f"_v{i}") for i in range(V)]
    best: Optional[str] = None
    for perm in itertools.permutations(placeholders):
        rename = dict(zip(free, perm))
        normalised = sp.simplify(expr.subs(rename, simultaneous=True))
        rep = sp.srepr(normalised)
        if best is None or rep < best:
            best = rep
    return best or ""


@dataclass
class DimensionalCandidate:
    """Two equations whose variable dimensions match as a multiset."""
    eq_a: str
    eq_b: str
    shared_multiset: Tuple[str, ...]


@dataclass
class StructuralCandidate:
    """Two equations whose canonical forms are syntactically identical
    under a specific variable permutation.

    `substitution` maps eq_a's variable names → eq_b's variable names.
    When applied, eq_a.canonical_form becomes eq_b.canonical_form (or
    its negation, since the implicit form lhs = 0 is invariant under
    sign flip).
    """
    eq_a: str
    eq_b: str
    substitution: Dict[str, str]
    sign: int  # +1 if identical, -1 if identical after sign flip


# ---------------------------------------------------------------------------
# Sieve 1: dimensional multiset
# ---------------------------------------------------------------------------


def dimensional_sieve(
    equations: Dict[str, TypedExpression],
) -> List[DimensionalCandidate]:
    """Return every pair of equations with matching dimension multisets.

    Uses the `dimension_multiset()` method, which ignores variable
    names but preserves the set of declared dimensions. Two equations
    that pass this sieve have, up to relabeling, the same dimensioned
    quantities — a necessary-not-sufficient condition for a genuine
    dimensional analogy.
    """
    candidates: List[DimensionalCandidate] = []
    items = sorted(equations.items())
    for (aid, a), (bid, b) in itertools.combinations(items, 2):
        if a.dimension_multiset() == b.dimension_multiset():
            candidates.append(DimensionalCandidate(
                eq_a=aid,
                eq_b=bid,
                shared_multiset=a.dimension_multiset(),
            ))
    return candidates


# ---------------------------------------------------------------------------
# Sieve 2: structural equality under variable permutation
# ---------------------------------------------------------------------------


def structural_sieve(
    equations: Dict[str, TypedExpression],
) -> List[StructuralCandidate]:
    """Return every pair of equations whose canonical forms are
    sympy-identical under some permutation of variable names.

    Algorithm:
    1. For each pair (A, B), consider only pairs with the same number
       of free symbols (necessary condition).
    2. Enumerate all bijections σ: vars(A) → vars(B).
    3. Substitute σ into A's canonical form and check whether
       sympy.simplify(A_σ − B) == 0 (identical form) or
       sympy.simplify(A_σ + B) == 0 (identical up to sign).
    4. Return the first matching σ, preserving registration order.

    For V = 3 variables, 6 permutations per pair; V = 4, 24 perms;
    V = 5, 120 perms; manageable for our corpus sizes.

    Equations with differing variable counts are skipped entirely
    (they cannot be structurally identical under a bijection).
    """
    candidates: List[StructuralCandidate] = []
    items = sorted(equations.items())
    # Pre-compute rename-invariant signatures once per equation.
    sigs = {eid: structural_signature(eq.canonical_form) for eid, eq in items}
    for (aid, a), (bid, b) in itertools.combinations(items, 2):
        a_vars = sorted(a.variables.keys())
        b_vars = sorted(b.variables.keys())
        if len(a_vars) != len(b_vars):
            continue
        # Hash pre-filter: if the rename-normalised signatures differ,
        # no permutation can make them equal.
        if sigs[aid] != sigs[bid]:
            continue
        # V cap: expressions with more than STRUCTURAL_SIEVE_V_CAP free
        # symbols skip the O(V!) inner permutation search. For those,
        # only the cheap-signature prefilter fires, and a real match
        # must survive the CoV sieve + axiom gate downstream.
        if len(a_vars) > STRUCTURAL_SIEVE_V_CAP:
            continue
        match = _find_permutation_match(a.canonical_form, b.canonical_form, a_vars, b_vars)
        if match is not None:
            substitution, sign = match
            candidates.append(StructuralCandidate(
                eq_a=aid,
                eq_b=bid,
                substitution=substitution,
                sign=sign,
            ))
    return candidates


def _find_permutation_match(
    expr_a: sp.Expr,
    expr_b: sp.Expr,
    vars_a: List[str],
    vars_b: List[str],
) -> Optional[Tuple[Dict[str, str], int]]:
    """Return (substitution, sign) if a permutation makes expr_a ≡ ±expr_b.

    Substitution is applied *rename-only*: we replace each sympy
    Symbol(name) in expr_a with Symbol(sigma(name)). If the result
    matches expr_b (possibly up to a sign flip), we return the
    permutation. Otherwise None.
    """
    for perm in itertools.permutations(vars_b):
        sigma: Dict[str, str] = dict(zip(vars_a, perm))
        subs_map = {sp.Symbol(src): sp.Symbol(dst) for src, dst in sigma.items()}
        relabelled = expr_a.subs(subs_map, simultaneous=True)
        diff_plus = sp.simplify(relabelled - expr_b)
        if diff_plus == 0:
            return (sigma, +1)
        diff_minus = sp.simplify(relabelled + expr_b)
        if diff_minus == 0:
            return (sigma, -1)
    return None


# ---------------------------------------------------------------------------
# Dimension-aware structural sieve (combines the two above)
# ---------------------------------------------------------------------------


def dimensionally_consistent_structural_sieve(
    equations: Dict[str, TypedExpression],
) -> List[StructuralCandidate]:
    """Stronger filter: only accept structural matches whose substitution
    pairs each variable with one of *matching* dimension.

    This is the sieve that catches Newton II ↔ Ohm's law correctly:
    both have the shape `extensive − coupling * intensive = 0`, and
    the substitution {F → V, m → R, a → I} pairs variables of
    matching dimensions *within each equation's declared units*.

    Use this instead of `structural_sieve` for candidate generation;
    the pure `structural_sieve` is kept for ablation and for catching
    cross-domain identities where the dimensions differ (Fourier ↔
    Fick).
    """
    candidates: List[StructuralCandidate] = []
    items = sorted(equations.items())
    for (aid, a), (bid, b) in itertools.combinations(items, 2):
        a_vars = sorted(a.variables.keys())
        b_vars = sorted(b.variables.keys())
        if len(a_vars) != len(b_vars):
            continue
        # Precompute dimensionality strings.
        a_dim = {name: str(a.variables[name].dimensionality()) for name in a_vars}
        b_dim = {name: str(b.variables[name].dimensionality()) for name in b_vars}
        match = _find_dim_aware_match(
            a.canonical_form, b.canonical_form, a_vars, b_vars, a_dim, b_dim
        )
        if match is not None:
            substitution, sign = match
            candidates.append(StructuralCandidate(
                eq_a=aid,
                eq_b=bid,
                substitution=substitution,
                sign=sign,
            ))
    return candidates


def _find_dim_aware_match(
    expr_a: sp.Expr,
    expr_b: sp.Expr,
    vars_a: List[str],
    vars_b: List[str],
    a_dim: Dict[str, str],
    b_dim: Dict[str, str],
) -> Optional[Tuple[Dict[str, str], int]]:
    """Only try permutations where paired variables have equal dimensionality."""
    # Group b's variables by dimensionality for quick pairing.
    b_by_dim: Dict[str, List[str]] = {}
    for name in vars_b:
        b_by_dim.setdefault(b_dim[name], []).append(name)
    # Check: can every a-variable be paired with a b-variable of the
    # same dimension? If the multisets disagree, no match is possible.
    a_multiset = Counter(a_dim[n] for n in vars_a)
    b_multiset = Counter(b_dim[n] for n in vars_b)
    if a_multiset != b_multiset:
        return None
    # Enumerate valid permutations by building them dimension-class by
    # dimension-class. For each dimension class, all bijections
    # between the corresponding a-variables and b-variables are valid.
    a_by_dim: Dict[str, List[str]] = {}
    for name in vars_a:
        a_by_dim.setdefault(a_dim[name], []).append(name)

    def class_permutations():
        """Generate all dim-preserving bijections as dicts."""
        keys = sorted(a_by_dim.keys())
        iters = [
            [
                dict(zip(a_by_dim[k], perm))
                for perm in itertools.permutations(b_by_dim[k])
            ]
            for k in keys
        ]
        for combo in itertools.product(*iters):
            merged: Dict[str, str] = {}
            for piece in combo:
                merged.update(piece)
            yield merged

    for sigma in class_permutations():
        subs_map = {sp.Symbol(src): sp.Symbol(dst) for src, dst in sigma.items()}
        relabelled = expr_a.subs(subs_map, simultaneous=True)
        diff_plus = sp.simplify(relabelled - expr_b)
        if diff_plus == 0:
            return (sigma, +1)
        diff_minus = sp.simplify(relabelled + expr_b)
        if diff_minus == 0:
            return (sigma, -1)
    return None
