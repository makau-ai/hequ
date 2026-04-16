"""Generic Phase 12 canonical-problem runner.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/run_canonical_problem.py \\
        EQ-NEWTON-II PRB-NEWTON-II-001
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/run_canonical_problem.py \\
        EQ-HOOKE PRB-HOOKE-001

Takes an equation id and a problem id, loads the problem from
the equation's `problems.yaml`, runs `source_and_verify` with
the v5 'board is not a CAS' protocol, and writes the result to
the ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

import sympy as sp
import yaml

from framework.reference_value_sourcing import source_and_verify
from framework.ai_review_board import AIBoardKeysMissing
from framework.discovery_ledger import (
    DiscoveryLedger, Hypothesis, HypothesisOutcome,
)

EQUATIONS_ROOT = _LABS_V2 / "equations"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


_STATUS_TO_OUTCOME = {
    "VERIFIED": HypothesisOutcome.EMPIRICAL,
    "BOARD_HALLUCINATION_DETECTED": HypothesisOutcome.REJECTED,
    "SYMBOLIC_EQUIVALENCE_UNDECIDABLE": HypothesisOutcome.CONJECTURAL,
    "REFERENCE_UNRESOLVED": HypothesisOutcome.CONJECTURAL,
}


def _find_problems_yaml(equation_id: str) -> Path:
    """Walk equations/ to find the problems.yaml for the named
    equation id."""
    for yaml_file in EQUATIONS_ROOT.rglob(f"{equation_id}/problems.yaml"):
        return yaml_file
    raise FileNotFoundError(
        f"problems.yaml not found for equation {equation_id} "
        f"under {EQUATIONS_ROOT}"
    )


def _load_problem(problems_path: Path, problem_id: str) -> dict:
    with problems_path.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    for prob in doc.get("problems", []):
        if prob.get("id") == problem_id:
            return prob
    raise KeyError(f"problem {problem_id} not found in {problems_path}")


def run_problem(equation_id: str, problem_id: str) -> int:
    problems_path = _find_problems_yaml(equation_id)
    problem = _load_problem(problems_path, problem_id)

    statement = problem["statement"]
    local_formula_str = problem["local_formula"]
    substitutions = {
        k: float(v) for k, v in problem["canonical_substitutions"].items()
    }
    variable_ranges = {
        k: (float(v[0]), float(v[1]))
        for k, v in problem["variable_ranges"].items()
    }
    pbt_seed = int(problem["pbt"]["seed"])
    pbt_n = int(problem["pbt"]["n_samples"])

    # Parse the local formula with positive-real symbols for
    # the variables declared in substitutions. This gives sympy
    # the assumptions it needs to simplify expressions like
    # sqrt(L/g) → sqrt(L)/sqrt(g) cleanly.
    sym_locals = {
        name: sp.Symbol(name, positive=True) for name in substitutions
    }
    local_formula = sp.sympify(local_formula_str, locals=sym_locals)

    print("=" * 70)
    print(f"Phase 12 canonical problem")
    print(f"Equation: {equation_id}")
    print(f"Problem:  {problem_id} — {problem['name']}")
    print(f"Local formula: {local_formula}")
    print(f"Canonical substitutions: {substitutions}")
    # Compute the expected answer for the header just for display
    expected = float(local_formula.subs(
        {sym_locals[k]: v for k, v in substitutions.items()}
    ).evalf(15))
    print(f"Expected answer (local sympy): {expected:.10f}")
    print("=" * 70)
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

    print(f"Board formula:       {result.formula_symbolic}")
    print(f"Board citations:     {len(result.citations)} primary sources")
    for c in result.citations:
        print(f"  · {c}")
    print()
    print(f"LOCAL authoritative value (sympy 15d): {result.value}")
    print(f"LOCAL high-precision (mpmath 50d):     "
          f"{result.__dict__.get('_high_precision_value', 'n/a')[:40]}...")
    bva = result.__dict__.get("_board_value_attempt")
    if bva is not None:
        rel = abs(bva - result.value) / (abs(result.value) + 1e-300)
        print(f"Board value_attempt (capability data, NOT used): {bva}")
        print(f"  Board vs local rel_err: {rel:.2e}")
    print(f"Unit: {result.unit}")
    print()
    print(f"Verification status: {result.verification_status}")
    print()
    for c in result.checks:
        emoji = "✅" if c.passed else "❌"
        print(f"  {emoji} Check {c.name}: {c.detail} ({c.elapsed_seconds:.3f}s)")
    sanity = result.__dict__.get("_board_sanity_check")
    if sanity:
        print()
        print(f"Board sanity-check summary: {sanity}")
    print()

    outcome = _STATUS_TO_OUTCOME.get(
        result.verification_status, HypothesisOutcome.CONJECTURAL
    )
    ledger = DiscoveryLedger(LEDGER_PATH)
    hyp = Hypothesis(
        eq_a=equation_id,
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
    print()

    if result.verification_status == "VERIFIED":
        print(f"🟢 {equation_id} / {problem_id}: VERIFIED")
        print(f"   Reference value {result.value} {result.unit} accepted.")
        return 0
    else:
        print(f"🔴 {equation_id} / {problem_id}: "
              f"{result.verification_status}")
        print(f"   Per §11h, the Failure Investigation Protocol must "
              f"fire before any fix is proposed.")
        return 1


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "usage: run_canonical_problem.py <EQUATION-ID> <PROBLEM-ID>",
            file=sys.stderr,
        )
        return 2
    return run_problem(argv[1], argv[2])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
