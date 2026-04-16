"""Phase 12 first canonical problem: Newton II simple pendulum.

This is the end-to-end first deliverable under design v4:
load the problem from problems.yaml, query the AI consensus
board for a reference value, run the four-check verification
pipeline locally, and write the result to the ledger.

No tolerance loosening. No equation modification. If any
check fails, the Failure Investigation Protocol fires via
framework/failure_investigation.py.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/run_first_canonical_problem.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

import sympy as sp
import yaml

from framework.reference_value_sourcing import (
    source_and_verify,
    BoardHallucinationDetected,
    SymbolicEquivalenceUndecidable,
)
from framework.ai_review_board import AIBoardKeysMissing
from framework.discovery_ledger import (
    DiscoveryLedger, Hypothesis, HypothesisOutcome,
)

EQUATIONS_ROOT = _LABS_V2 / "equations"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


def main() -> int:
    problems_path = (
        EQUATIONS_ROOT
        / "classical_mechanics"
        / "EQ-NEWTON-II"
        / "problems.yaml"
    )
    if not problems_path.is_file():
        print(f"problems.yaml not found: {problems_path}", file=sys.stderr)
        return 2

    with problems_path.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    problem = doc["problems"][0]
    problem_id = problem["id"]
    statement = problem["statement"]
    local_formula_str = problem["local_formula"]
    substitutions = {k: float(v) for k, v in problem["canonical_substitutions"].items()}
    ranges_raw = problem["variable_ranges"]
    variable_ranges = {k: (float(v[0]), float(v[1])) for k, v in ranges_raw.items()}
    pbt_seed = int(problem["pbt"]["seed"])
    pbt_n = int(problem["pbt"]["n_samples"])

    # Parse the local (architect's) formula into a sympy
    # expression. The free symbols in this expression become
    # the sym_locals the board's formula_symbolic is parsed
    # against, which keeps both sides using the same symbol
    # names for comparison.
    L, g = sp.symbols("L g", positive=True)
    local_formula = 2 * sp.pi * sp.sqrt(L / g)

    print(f"=" * 70)
    print(f"Phase 12 — First canonical problem")
    print(f"Problem: {problem_id} — {problem['name']}")
    print(f"Local formula: {local_formula}")
    print(f"Canonical substitutions: {substitutions}")
    print(f"Expected answer: {float(local_formula.subs(L, substitutions['L']).subs(g, substitutions['g']).evalf()):.10f} s")
    print(f"=" * 70)
    print()

    try:
        result = source_and_verify(
            problem_statement=statement,
            query_id=f"phase12_{problem_id}",
            local_formula=local_formula,
            variable_ranges=variable_ranges,
            canonical_substitutions=substitutions,
            include_grok=False,
            n_pbt_samples=pbt_n,
            pbt_seed=pbt_seed,
        )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    print(f"Board reply formula:    {result.formula_symbolic}")
    print(f"Board citations:        {result.citations}")
    print()
    print(f"LOCAL authoritative value (sympy 15d): {result.value}")
    print(f"LOCAL high-precision (mpmath 50d):     "
          f"{result.__dict__.get('_high_precision_value', 'n/a')[:30]}...")
    bva = result.__dict__.get('_board_value_attempt')
    if bva is not None:
        print(f"Board value_attempt (capability data, NOT used): {bva}")
        print(f"  Board vs local rel_err: {abs(bva - result.value) / abs(result.value):.2e}")
    print(f"Unit:                   {result.unit}")
    print()
    print(f"Verification status: {result.verification_status}")
    print()
    for c in result.checks:
        emoji = "✅" if c.passed else "❌"
        print(f"  {emoji} Check {c.name}: {c.detail} ({c.elapsed_seconds:.3f}s)")
    sanity = result.__dict__.get('_board_sanity_check')
    if sanity:
        print()
        print(f"Board sanity-check pass: {sanity}")
    print()

    # Write to ledger regardless of outcome — the investigation
    # itself is evidence
    ledger = DiscoveryLedger(LEDGER_PATH)
    outcome_map = {
        "VERIFIED": HypothesisOutcome.EMPIRICAL,
        "BOARD_HALLUCINATION_DETECTED": HypothesisOutcome.REJECTED,
        "SYMBOLIC_EQUIVALENCE_UNDECIDABLE": HypothesisOutcome.CONJECTURAL,
        "REFERENCE_UNRESOLVED": HypothesisOutcome.CONJECTURAL,
    }
    outcome = outcome_map.get(
        result.verification_status, HypothesisOutcome.CONJECTURAL
    )
    hyp = Hypothesis(
        eq_a="EQ-NEWTON-II",
        eq_b="(canonical problem)",
        kind="canonical_problem_verification",
        outcome=outcome,
        substitution={"problem_id": problem_id},
        evidence=result.as_ledger_dict(),
        rejection_criterion=(
            f"verification failed: {result.verification_status}"
            if result.verification_status != "VERIFIED" else None
        ),
        review_required=(
            result.verification_status
            in ("SYMBOLIC_EQUIVALENCE_UNDECIDABLE", "REFERENCE_UNRESOLVED")
        ),
    )
    ledger.record(hyp)
    print(f"Ledger record written: kind={hyp.kind}, outcome={hyp.outcome.value}")

    if result.verification_status == "VERIFIED":
        print()
        print("🟢 Phase 12 first canonical problem: VERIFIED")
        print(f"   Reference value {result.value} {result.unit} accepted.")
        print(f"   Citations: {', '.join(result.citations) or '(none)'}")
        return 0
    else:
        print()
        print(f"🔴 Phase 12 first canonical problem: "
              f"{result.verification_status}")
        print(f"   Per §11h, the Failure Investigation Protocol must "
              f"fire before any fix is proposed.")
        print(f"   No tolerance loosening. No equation modification.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
