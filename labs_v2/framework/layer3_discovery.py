"""Layer 3 — the discovery loop.

Consumes candidates from Layer 2 sieves and submits each one to a
stronger verification + logging pipeline. Outputs `Hypothesis`
records into the append-only `DiscoveryLedger`.

For each candidate pair (E_a, E_b, σ):
  1. **Symbolic confirmation.** Already done by Layer 2 for
     structural candidates; re-assert here with an explicit
     `sp.simplify` check so the ledger carries the symbolic evidence.
  2. **Numerical confirmation.** Generate N random valid inputs for
     E_a, compute its canonical-form residual (should be ≡ 0), then
     apply σ to get E_b-flavoured inputs, compute E_b's residual,
     and verify both are zero within tolerance. This is redundant
     for exact symbolic matches but catches any sympy bugs.
  3. **Null-hypothesis baseline.** Compute the probability that a
     random permutation of variables on a random pair would produce
     the observed algebraic identity. With V variables per equation,
     V! permutations; under the null, the probability of a match is
     (# simplifications to 0) / V!. For our corpus this is tiny,
     but reporting it explicitly is the Wigner rule from the
     methodology agent's report.
  4. **Ledger write.** Record outcome PROVED (exact symbolic match)
     or REJECTED (numerical mismatch) with full evidence.

This layer does NOT propose new substitutions beyond what Layer 2
generated. Proposing richer substitutions (change of variables,
log-price, Wick rotation) is a Layer 3.5 extension planned for
Medium scope. Small scope sticks to what Layer 2's structural
sieve produces.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

import sympy as sp

from .discovery_ledger import DiscoveryLedger, Hypothesis, HypothesisOutcome
from .layer2_sieves import (
    StructuralCandidate,
    dimensional_sieve,
    dimensionally_consistent_structural_sieve,
    structural_sieve,
)
from .typed_expression import TypedExpression


def _random_inputs(eq: TypedExpression, rng: random.Random) -> Dict[str, float]:
    """Generate a random dict of input values for eq's declared variables.

    We avoid zero because several equations have it as an edge case
    (division-by-zero, log(0)), and we avoid huge magnitudes to stay
    inside floating-point precision. Range [0.1, 10.0] is a good
    neighbourhood for most physics/chemistry/finance quantities.
    """
    return {
        name: rng.uniform(0.1, 10.0)
        for name in eq.variables
    }


def _symbolic_residual(eq: TypedExpression, subs: Dict[str, float]) -> float:
    """Substitute numeric inputs into the canonical form, return as float."""
    return _symbolic_residual_expr(eq.canonical_form, subs)


def _symbolic_residual_expr(expr: sp.Expr, subs: Dict[str, float]) -> float:
    """Evaluate an arbitrary sympy expression on numeric inputs."""
    result = expr.subs({sp.Symbol(k): v for k, v in subs.items()})
    try:
        return float(result)
    except (TypeError, ValueError):
        return float("inf")


def _per_pair_permutation_baseline(
    eq_a: TypedExpression,
    eq_b: TypedExpression,
) -> float:
    """Diagnostic: fraction of variable permutations on the given pair
    that produce a symbolic identity.

    For 3-variable multiplicatively symmetric forms (Newton II, Ohm's
    law), this is typically 2/6 = 0.333 due to commutativity, not
    because the identity is weak. The **corpus-level** baseline
    (`_corpus_null_baseline`) is the honest significance number;
    this one is only kept as a diagnostic.
    """
    import itertools
    a_vars = sorted(eq_a.variables.keys())
    b_vars = sorted(eq_b.variables.keys())
    if len(a_vars) != len(b_vars):
        return 1.0
    total = 0
    matches = 0
    for perm in itertools.permutations(b_vars):
        total += 1
        sigma = dict(zip(a_vars, perm))
        subs_map = {sp.Symbol(src): sp.Symbol(dst) for src, dst in sigma.items()}
        relabelled = eq_a.canonical_form.subs(subs_map, simultaneous=True)
        if sp.simplify(relabelled - eq_b.canonical_form) == 0:
            matches += 1
            continue
        if sp.simplify(relabelled + eq_b.canonical_form) == 0:
            matches += 1
    return matches / total if total > 0 else 1.0


def corpus_null_baseline(
    equations: Dict[str, TypedExpression],
    structural_hits: int,
    *,
    per_pair_coincidence_rate: float = 1 / 6,
) -> Dict[str, float]:
    """Corpus-level Wigner null-hypothesis baseline with Bonferroni
    multiple-comparisons correction.

    Medium milestone 1 addition: returns both the raw per-pair
    fraction AND the Bonferroni-corrected family-wise error rate
    (FWER). The raw fraction is the descriptive statistic; the
    corrected number is the inferential one.

    Model
    -----
    Treat each of the C(N,2) equation pairs as an independent
    Bernoulli trial with per-trial coincidence probability
    `per_pair_coincidence_rate` (default 1/6 — the fraction of
    random 3-variable permutations that produce an algebraic
    identity under commutative multiplication, derived in the
    methodology report).

    Under the null (no real structural relation), the expected number
    of "hit" pairs in the corpus is `C(N,2) * p`. The Bonferroni-
    corrected p-value for the observed hit count is:

        p_Bonferroni = min(1.0, C(N,2) * p_per_pair)

    where p_per_pair is the tail probability of observing at least one
    hit under the null on a single pair. For "at least one match in
    any of V! permutations", that's the per-pair coincidence rate.

    Interpretation
    --------------
    - `pair_count`: C(N,2), the search-space size
    - `structural_hits`: how many pairs the sieve returned
    - `per_pair_fraction`: structural_hits / pair_count — descriptive
    - `expected_under_null`: C(N,2) * p_per_pair — how many hits a
      random corpus would produce
    - `observed_vs_expected`: ratio; >1 means the corpus beats the
      null
    - `fwer_bonferroni`: the Bonferroni-corrected FWER. If it is <
      0.05, the corpus's hit rate is unlikely to be chance.
    """
    import math
    n = len(equations)
    pair_count = n * (n - 1) // 2
    if pair_count == 0:
        return {
            "pair_count": 0,
            "structural_hits": 0,
            "per_pair_fraction": 0.0,
            "expected_under_null": 0.0,
            "observed_vs_expected": 0.0,
            "fwer_bonferroni": 1.0,
            "note": "empty corpus",
        }
    expected_under_null = pair_count * per_pair_coincidence_rate
    observed_vs_expected = (
        structural_hits / expected_under_null
        if expected_under_null > 0 else 0.0
    )
    # Bonferroni: the FWER for observing ≥ 1 hit across pair_count
    # independent Bernoulli(p) trials, corrected for the number of
    # comparisons. Upper-bound 1.0.
    fwer_bonferroni = min(1.0, pair_count * per_pair_coincidence_rate)
    return {
        "pair_count": pair_count,
        "structural_hits": int(structural_hits),
        "per_pair_fraction": structural_hits / pair_count,
        "per_pair_coincidence_rate": per_pair_coincidence_rate,
        "expected_under_null": expected_under_null,
        "observed_vs_expected": observed_vs_expected,
        "fwer_bonferroni": fwer_bonferroni,
        "note": (
            f"Of {pair_count} candidate pairs in the {n}-equation "
            f"corpus, {structural_hits} produced a structural "
            f"identity. Under the null (p_per_pair = "
            f"{per_pair_coincidence_rate:.3f}), the expected hit "
            f"count is {expected_under_null:.2f}. "
            f"Observed/expected = {observed_vs_expected:.2f}. "
            f"Bonferroni-corrected FWER = {fwer_bonferroni:.3f} "
            f"(cap 1.0). Interpretation: a single pair's coincidence "
            f"probability is already ~1/6; at 10 equations the "
            f"Bonferroni bound is meaningless (~7.5), but at 30+ "
            f"equations this number becomes a real significance "
            f"gate."
        ),
    }


def verify_structural_candidate(
    cand: StructuralCandidate,
    eq_a: TypedExpression,
    eq_b: TypedExpression,
    ledger: DiscoveryLedger,
    rng: random.Random,
    num_trials: int = 20,
    tolerance: float = 1e-10,
) -> Hypothesis:
    """Run the symbolic + numerical + baseline verification for one
    structural candidate and append the resulting Hypothesis to the
    ledger. Returns the Hypothesis.
    """
    # 1. Re-assert symbolic identity (belt-and-braces).
    subs_map = {sp.Symbol(src): sp.Symbol(dst) for src, dst in cand.substitution.items()}
    relabelled = eq_a.canonical_form.subs(subs_map, simultaneous=True)
    if cand.sign == +1:
        residual_expr = sp.simplify(relabelled - eq_b.canonical_form)
    else:
        residual_expr = sp.simplify(relabelled + eq_b.canonical_form)
    symbolic_holds = (residual_expr == 0)

    # 2. Numerical confirmation.
    # If the symbolic check passes, the two canonical forms are
    # algebraically identical under σ and agree on every numeric
    # input by construction — the numerical loop is redundant but
    # we run it as a belt-and-braces smoke test against sympy bugs.
    # We feed inputs keyed by eq_b's variables (the target of σ) to
    # both the relabelled expression and eq_b's canonical form.
    num_pass = 0
    num_fail = 0
    max_num_residual = 0.0
    target_vars = sorted(str(s) for s in relabelled.free_symbols)
    for _ in range(num_trials):
        # Random values for eq_b's variables (since relabelled now lives
        # in eq_b's symbol space after σ renaming).
        inputs_b = {name: rng.uniform(0.1, 10.0) for name in target_vars}
        test_val = _symbolic_residual_expr(relabelled, inputs_b)
        b_val = _symbolic_residual_expr(eq_b.canonical_form, inputs_b)
        expected = b_val if cand.sign == +1 else -b_val
        diff = abs(test_val - expected)
        if diff <= tolerance or (not math.isfinite(diff) and not math.isfinite(expected)):
            num_pass += 1
        else:
            num_fail += 1
        if math.isfinite(diff) and diff > max_num_residual:
            max_num_residual = diff

    # 3. Per-pair permutation diagnostic (see _per_pair_permutation_baseline
    # docstring for why this is NOT the honest significance number).
    per_pair_fraction = _per_pair_permutation_baseline(eq_a, eq_b)

    # 4. **Axiom compatibility** — the Principle-3 filter added in
    # Small-plus-plus. A surviving structural match whose axioms
    # disagree is demoted or rejected here; a match whose axioms
    # agree carries the Jaccard score into the ledger for cross-run
    # comparison.
    from .axioms import compatibility
    axiom_verdict = compatibility(eq_a.axioms, eq_b.axioms)

    # 5. Decide outcome.
    #
    # Honest note on the "numerical confirmation": when `symbolic_holds`
    # is True the 20-trial numerical loop is a smoke test against sympy
    # bugs, not independent evidence.
    #
    # Axiom rules:
    #   - contradictions present  → REJECTED ("axiom contradiction")
    #   - axiom_verdict.compatible is False but no contradictions
    #     (Jaccard below MIN_JACCARD)  → demote to CONJECTURAL
    #   - axiom_verdict.compatible is True  → keep the symbolic
    #     outcome (PROVED / EMPIRICAL / REJECTED for numeric fail)
    if axiom_verdict.contradictions:
        outcome = HypothesisOutcome.REJECTED
        rejection = (
            "axiom contradiction: "
            + ", ".join(f"{a}/{b}" for a, b in axiom_verdict.contradictions)
        )
    elif symbolic_holds and num_fail == 0 and axiom_verdict.compatible:
        outcome = HypothesisOutcome.PROVED
        rejection = None
    elif symbolic_holds and num_fail == 0 and not axiom_verdict.compatible:
        # Structural match survives but axioms are too sparse to
        # justify PROVED — demote.
        outcome = HypothesisOutcome.CONJECTURAL
        rejection = (
            f"axiom Jaccard {axiom_verdict.jaccard:.3f} below "
            f"threshold; structural match is only conjectural"
        )
    elif num_fail == 0:
        outcome = HypothesisOutcome.EMPIRICAL
        rejection = "symbolic simplify did not collapse to 0"
    else:
        outcome = HypothesisOutcome.REJECTED
        rejection = f"{num_fail}/{num_trials} numerical residuals exceeded tolerance"

    hyp = Hypothesis(
        eq_a=cand.eq_a,
        eq_b=cand.eq_b,
        kind="structural_rename",
        outcome=outcome,
        substitution=cand.substitution,
        evidence={
            "sign": cand.sign,
            "symbolic_residual_expression": str(residual_expr),
            "symbolic_holds": symbolic_holds,
            "numerical_trials": num_trials,
            "numerical_pass": num_pass,
            "numerical_fail": num_fail,
            "numerical_note": (
                "Smoke test against sympy bugs — NOT independent evidence. "
                "Under symbolic_holds=True, the numerical loop is zero by "
                "construction. Medium scope will add an external-reference "
                "numerical check."
            ),
            "max_numerical_residual": max_num_residual,
            "per_pair_permutation_fraction": per_pair_fraction,
            "per_pair_note": (
                f"{per_pair_fraction:.4g} of variable permutations on THIS "
                f"pair produce an identity. For commutative-factor forms "
                f"this is typically 2/V! (not 1/V!). This is a diagnostic, "
                f"not a significance claim — see the corpus-level baseline "
                f"in the run summary."
            ),
            "axiom_compatibility": axiom_verdict.to_dict(),
        },
        rejection_criterion=rejection,
    )
    ledger.record(hyp)
    return hyp


def run_layer3(
    equations: Dict[str, TypedExpression],
    ledger: DiscoveryLedger,
    *,
    seed: int = 42,
    num_trials: int = 20,
) -> List[Hypothesis]:
    """Entry point: run Layer 2 sieves, then verify each candidate
    with Layer 3 and log results.

    Returns the list of Hypothesis records produced in this run.
    """
    rng = random.Random(seed)
    results: List[Hypothesis] = []

    # Structural candidates are where the real action is in v2 Small.
    struct_candidates = structural_sieve(equations)
    for cand in struct_candidates:
        hyp = verify_structural_candidate(
            cand,
            equations[cand.eq_a],
            equations[cand.eq_b],
            ledger,
            rng,
            num_trials=num_trials,
        )
        results.append(hyp)

    # Also log every dimensional-sieve candidate as CONJECTURAL (same
    # dimensions ≠ same equation; but worth recording for later review).
    for dcand in dimensional_sieve(equations):
        hyp = Hypothesis(
            eq_a=dcand.eq_a,
            eq_b=dcand.eq_b,
            kind="dimensional_multiset_match",
            outcome=HypothesisOutcome.CONJECTURAL,
            substitution={},
            evidence={
                "shared_multiset": list(dcand.shared_multiset),
                "note": (
                    "dimensions match as a multiset; structural identity "
                    "not tested here (would be redundant if the "
                    "structural sieve also fired)"
                ),
            },
        )
        ledger.record(hyp)
        results.append(hyp)

    return results
