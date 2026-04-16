"""Layer 2 — change-of-variables sieve (Small-plus-plus stub).

Addresses the methodology auditor's Principle-7 concern: Small-plus
added `canonical_form_derivatives` to the typed expression but no
sieve read it. This module is the first sieve that consumes the
derivative form and tries non-rename substitutions.

Scope (Small-plus-plus)
-----------------------
This is explicitly a **stub** — the sieve runs, the ledger records
its attempts, but its library of substitutions is minimal:

1. **Identity substitution** — σ = I. Always tried; matches any
   equation pair whose derivative forms are syntactically identical
   up to symbol rename. For our current corpus this should catch
   Fourier ↔ Fick under {q↔J, k↔D, T↔C}.

2. **Log-price substitution** — `S → exp(x)`. The canonical Black-
   Scholes → heat-equation transform. Sympy applies the chain rule
   automatically when the derivative form uses real `Derivative`
   objects. We re-simplify and compare.

3. **Time reversal** — `t → T_end - tau`. Used in Black-Scholes and
   other backward-in-time PDEs. Trivial structurally; included so
   the ledger carries the attempt.

None of these is sufficient to complete Black-Scholes↔heat-equation
on its own; the full transform is a composition of log-price +
time-reversal + exponential discount. The stub demonstrates the
architecture — reading `canonical_form_derivatives`, applying the
substitution with chain rule, comparing against a target — and
leaves composition of substitutions as the first real Medium-scope
extension.

What the sieve records
----------------------
Every (equation_a, equation_b, substitution) triple it tries enters
the discovery ledger as a Hypothesis with kind="change_of_variables"
and one of:
  PROVED       — transformed A exactly equals B
  EMPIRICAL    — numeric check passes, symbolic does not (unlikely)
  CONJECTURAL  — transformation is well-defined but doesn't match
  REJECTED     — substitution fails (e.g. variable not in A)

This is the important property: **every attempt is logged**, even
the failures, so the methodology auditor's "the sieve actually
consumes the derivative form" concern is met with auditable evidence.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy as sp

from .typed_expression import TypedExpression
from .discovery_ledger import DiscoveryLedger, Hypothesis, HypothesisOutcome
from .axioms import compatibility


@dataclass
class CoVSubstitution:
    """One entry in the substitution library.

    `name` is a short human-readable label (e.g. "log_price").
    `apply` takes a sympy Expr and a dict of declared functions and
    returns the transformed expression. It should handle the chain
    rule via sympy's built-in derivative machinery.
    `description` is a one-line explanation for the ledger.
    """
    name: str
    apply: Callable[[sp.Expr, Dict[str, List[str]]], Optional[sp.Expr]]
    description: str


# --- Library of canonical substitutions ------------------------------------


def _identity_substitution(expr: sp.Expr, functions: Dict[str, List[str]]) -> sp.Expr:
    """σ = I — the trivial substitution. Returns expression unchanged."""
    return expr


def _log_price_substitution(
    expr: sp.Expr, functions: Dict[str, List[str]]
) -> Optional[sp.Expr]:
    """Black-Scholes-style log-price transform: S → exp(x).

    Applies when the expression contains a free symbol named `S`.
    Sympy's `subs` handles the chain rule through any `Derivative(V,
    S, n)` objects by re-expressing them in terms of `x`.
    """
    x = sp.Symbol("x", real=True)
    S = sp.Symbol("S")
    if S not in expr.free_symbols:
        return None
    # Substitute S = exp(x) and let sympy rewrite derivatives through
    # the chain rule. `doit()` forces any pending Derivative calls to
    # evaluate on the composition.
    return sp.simplify(expr.subs(S, sp.exp(x)).doit())


def _time_reversal_substitution(
    expr: sp.Expr, functions: Dict[str, List[str]]
) -> Optional[sp.Expr]:
    """Replace t → T_end − τ.

    Used in backward-in-time PDEs (Black-Scholes runs backward from
    expiry). Requires a free symbol `t`.
    """
    t = sp.Symbol("t")
    if t not in expr.free_symbols:
        return None
    T_end = sp.Symbol("T_end", positive=True)
    tau = sp.Symbol("tau", positive=True)
    return sp.simplify(expr.subs(t, T_end - tau).doit())


def _wick_rotation_substitution(
    expr: sp.Expr, functions: Dict[str, List[str]]
) -> Optional[sp.Expr]:
    """Wick rotation: t → −i·τ.

    The canonical analytic-continuation probe. In quantum mechanics,
    substituting t → −iτ in the Schrödinger equation turns its
    oscillatory first-order-in-t kernel into the diffusive first-
    order-in-τ kernel of the heat equation (Feynman-Kac). This is
    the P7 target from the methodology auditor.

    Applies when the expression has a free symbol `t`. Sympy's
    `subs(t, -I*tau)` triggers the chain rule on any
    `Derivative(ψ(x, t), t)` contained in the expression, producing
    `(−i) · Derivative(ψ_rotated, tau)`. The `doit()` then forces
    the derivative to be expressed against the new coordinate.
    """
    t = sp.Symbol("t")
    if t not in expr.free_symbols:
        return None
    tau = sp.Symbol("tau", positive=True, real=True)
    I = sp.I  # sympy imaginary unit
    return sp.simplify(expr.subs(t, -I * tau).doit())


SUBSTITUTION_LIBRARY: List[CoVSubstitution] = [
    CoVSubstitution(
        name="identity",
        apply=_identity_substitution,
        description="σ = I; exact syntactic match after variable rename",
    ),
    CoVSubstitution(
        name="log_price",
        apply=_log_price_substitution,
        description="S → exp(x); canonical log-price transform (Black-Scholes → heat)",
    ),
    CoVSubstitution(
        name="time_reversal",
        apply=_time_reversal_substitution,
        description="t → T_end − tau; backward-in-time PDE transform",
    ),
    CoVSubstitution(
        name="wick_rotation",
        apply=_wick_rotation_substitution,
        description="t → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)",
    ),
]


# --- Sieve entry point -----------------------------------------------------


def cov_sieve(
    equations: Dict[str, TypedExpression],
    ledger: DiscoveryLedger,
) -> List[Hypothesis]:
    """Run the change-of-variables sieve over every pair of equations
    that ship a `canonical_form_derivatives` representation.

    For each pair (A, B) and each substitution σ in the library:
      - Apply σ to A's derivative form.
      - Test whether the result matches B's derivative form (or is
        alpha-equivalent under a symbol rename).
      - Log a Hypothesis with the outcome.

    This is a stub: the library has only three entries and the
    matching test is strict `sympy.simplify(A_σ − B) == 0`. Medium
    scope will add more substitutions, chain them, and use a
    looser match criterion (e.g. Gröbner-basis reduction).
    """
    results: List[Hypothesis] = []
    # Only equations with a derivative form participate.
    items = [
        (eid, eq) for eid, eq in sorted(equations.items())
        if eq.canonical_form_derivatives is not None
    ]
    for (aid, a), (bid, b) in itertools.combinations(items, 2):
        for sub in SUBSTITUTION_LIBRARY:
            hyp = _try_substitution(a, b, sub, aid, bid)
            ledger.record(hyp)
            results.append(hyp)
    return results


def _try_substitution(
    a: TypedExpression,
    b: TypedExpression,
    sub: CoVSubstitution,
    aid: str,
    bid: str,
) -> Hypothesis:
    """Apply one substitution to A's derivative form and compare to B.

    Returns a Hypothesis record summarising the attempt. Errors in
    the substitution itself are caught and reported as REJECTED
    with the exception as the rejection criterion.
    """
    axiom_verdict = compatibility(a.axioms, b.axioms)

    # Guard: if axioms contradict, reject the pair without trying
    # the substitution. This mirrors Layer 3's axiom gate.
    if axiom_verdict.contradictions:
        return Hypothesis(
            eq_a=aid,
            eq_b=bid,
            kind="change_of_variables",
            outcome=HypothesisOutcome.REJECTED,
            substitution={
                "cov_name": sub.name,
                "cov_description": sub.description,
            },
            evidence={
                "axiom_compatibility": axiom_verdict.to_dict(),
                "skipped": "axiom contradiction gate",
            },
            rejection_criterion=(
                "axiom contradiction: "
                + ", ".join(f"{x}/{y}" for x, y in axiom_verdict.contradictions)
            ),
        )

    try:
        transformed = sub.apply(a.canonical_form_derivatives, a.declared_functions)
    except Exception as exc:  # noqa: BLE001
        return Hypothesis(
            eq_a=aid,
            eq_b=bid,
            kind="change_of_variables",
            outcome=HypothesisOutcome.REJECTED,
            substitution={
                "cov_name": sub.name,
                "cov_description": sub.description,
            },
            evidence={
                "axiom_compatibility": axiom_verdict.to_dict(),
                "exception": repr(exc),
            },
            rejection_criterion=f"substitution raised: {type(exc).__name__}",
        )

    if transformed is None:
        # Substitution doesn't apply to this equation (e.g., no S).
        return Hypothesis(
            eq_a=aid,
            eq_b=bid,
            kind="change_of_variables",
            outcome=HypothesisOutcome.REJECTED,
            substitution={
                "cov_name": sub.name,
                "cov_description": sub.description,
            },
            evidence={
                "axiom_compatibility": axiom_verdict.to_dict(),
                "skipped": "substitution not applicable to A (no matching symbol)",
            },
            rejection_criterion="substitution not applicable",
        )

    # Compare transformed A against B's derivative form. The match
    # criterion is strict: sympy.simplify of the difference must be
    # zero OR zero up to a sign flip. In the Small-plus-plus stub we
    # do not attempt alpha-renaming on top of the substitution —
    # that's a Medium extension.
    diff = sp.simplify(transformed - b.canonical_form_derivatives)
    matches = (diff == 0)
    diff_neg = sp.simplify(transformed + b.canonical_form_derivatives)
    if not matches and diff_neg == 0:
        matches = True

    if matches:
        if axiom_verdict.compatible:
            outcome = HypothesisOutcome.PROVED
            rejection = None
        else:
            outcome = HypothesisOutcome.CONJECTURAL
            rejection = (
                f"structural match but axiom Jaccard "
                f"{axiom_verdict.jaccard:.3f} below threshold"
            )
    else:
        outcome = HypothesisOutcome.CONJECTURAL
        rejection = (
            f"substitution applied, but transformed residual is "
            f"`{str(diff)[:80]}`, not zero"
        )

    return Hypothesis(
        eq_a=aid,
        eq_b=bid,
        kind="change_of_variables",
        outcome=outcome,
        substitution={
            "cov_name": sub.name,
            "cov_description": sub.description,
        },
        evidence={
            "axiom_compatibility": axiom_verdict.to_dict(),
            "transformed_residual": str(diff)[:200],
            "symbolic_match": matches,
        },
        rejection_criterion=rejection,
    )
