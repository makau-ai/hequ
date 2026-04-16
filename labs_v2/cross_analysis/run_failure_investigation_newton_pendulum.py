"""Run the Failure Investigation Protocol on the first Phase 12
canonical run's BOARD_HALLUCINATION_DETECTED result.

No corner cuts: the protocol runs in full — state audit,
assumption audit, literature prior search, board failure
review, ledger record — before any "fix" is proposed.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.failure_investigation import investigate_failure
from framework.typed_expression import load_equation
from framework.discovery_ledger import DiscoveryLedger

EQUATIONS_ROOT = _LABS_V2 / "equations"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


def main() -> int:
    newton_yaml = (
        EQUATIONS_ROOT / "classical_mechanics" / "EQ-NEWTON-II" / "equation.yaml"
    )
    equation = load_equation(newton_yaml)

    # Failure context: what the first canonical run observed and
    # what the board claimed
    failure_context = {
        "problem_id": "PRB-NEWTON-II-001",
        "problem_name": "Simple pendulum period (small-angle)",
        "board_formula": "2*pi*sqrt(L/g)",
        "board_value": 2.0064092614,
        "local_mpmath_50digit_value": 2.00640929258904,
        "architect_sympy_value": 2.0064092926,
        "check_a_passed": True,
        "check_a_detail": "rational normalization collapsed to zero — board formula and local formula are mathematically identical",
        "check_b_passed": True,
        "check_b_detail": "200 stratified samples across L∈[0.01,100], g∈[0.1,30], all within 1e-6 tolerance",
        "check_c_passed": False,
        "check_c_detail": "mpmath 50-decimal=2.00640929258904 vs board=2.0064092614, rel_err=1.55e-8 > tolerance 1e-10",
        "check_d_passed": None,
        "check_d_detail": "python-flint not installed; Check D skipped (best-effort Phase 12)",
        "board_citations": [
            "Halliday, Resnick & Walker, Fundamentals of Physics, 10th ed., Chapter 15, Section 15-5, Eq. 15-28",
            "Kleppner & Kolenkow, An Introduction to Mechanics, 2nd ed., Chapter 10, Section 10.2",
        ],
        "observation": (
            "The board's SYMBOLIC formula and CITATIONS are correct. "
            "The board's NUMERICAL VALUE is imprecise at the 8th "
            "decimal place. This is a board-side precision "
            "limitation, not an equation-side failure. None of the "
            "three FIP verdicts (sensing_gap / assumption_violated "
            "/ equation_inadequate) classically fit the situation. "
            "The architect suspects the correct response is a "
            "protocol-level change: query the board for formula + "
            "citations ONLY, and compute the numerical reference "
            "value LOCALLY from the formula. The architect does "
            "NOT modify the equation or loosen any tolerances."
        ),
    }

    # Step 1 inputs — what variables were observed
    observed_values = {
        "F": None,   # not directly observed in the pendulum problem — it's a derived quantity
        "m": 1.0,    # implicit (massless rod, point mass)
        "a": None,   # not directly observed — it's the response
        # NOTE: the pendulum problem does NOT use F, m, a in the
        # simple pendulum closed form. The canonical form uses
        # L and g, which are not Newton II's declared variables.
        # This is itself a subtle finding — the canonical "Newton II"
        # problem is being tested via a derived scenario that lives
        # in a different variable space.
    }

    # Step 2 inputs — we don't know of any explicitly violated
    # assumptions. The small-angle approximation is satisfied
    # at the implied amplitude.
    explicitly_violated = []

    failure_signature = (
        "board_imprecision_8th_decimal_pendulum_period"
    )

    ledger = DiscoveryLedger(LEDGER_PATH)

    print("Running Failure Investigation Protocol (§11h)...")
    print(f"Equation: {equation.id}")
    print(f"Failure signature: {failure_signature}")
    print()
    result = investigate_failure(
        equation=equation,
        failure_context=failure_context,
        observed_values=observed_values,
        explicitly_violated_assumptions=explicitly_violated,
        failure_signature=failure_signature,
        equations_root=EQUATIONS_ROOT,
        ledger=ledger,
        include_grok=False,
    )

    print(f"Investigation ID: {result.investigation_id}")
    print()
    print("Step 1 — State audit")
    print(f"  Expected variables:   {result.state_audit.expected_variables}")
    print(f"  Observed variables:   {result.state_audit.observed_variables}")
    print(f"  Missing variables:    {result.state_audit.missing_variables}")
    print(f"  Sensing gap detected: {result.state_audit.sensing_gap_detected}")
    if result.state_audit.notes:
        print(f"  Notes: {result.state_audit.notes}")
    print()
    print("Step 2 — Assumption audit")
    print(f"  Declared assumptions: {len(result.assumption_audit.declared_assumptions)}")
    print(f"  Violated:             {result.assumption_audit.violated_assumptions}")
    print(f"  Violation detected:   {result.assumption_audit.violation_detected}")
    print()
    print("Step 3 — Literature prior search")
    print(f"  Failure modes file exists: {len(result.literature_prior.citations_found) > 0}")
    print(f"  Citations found: {len(result.literature_prior.citations_found)}")
    print(f"  Meets ≥3 threshold: {result.literature_prior.meets_threshold}")
    if result.literature_prior.notes:
        print(f"  Notes: {result.literature_prior.notes}")
    print()
    print("Step 4 — Board verdict")
    print(f"  Verdict:   {result.board_verdict}")
    print(f"  Rationale: {result.board_rationale}")
    print()
    print(f"User escalation required: {result.user_escalation_required}")
    print(f"Ledger recorded:          {result.ledger_recorded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
