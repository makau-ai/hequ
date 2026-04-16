"""Phase 13 composite problem runner.

Reads a composite.yaml from labs_v2/composites/<composite_id>/
and verifies it using the same v5 source_and_verify pipeline
as the Phase 12 canonical-problem runner — but the composite
comes with its OWN canonical problem (the composite problem
that tests the composite equation of motion), and the runner
writes the result to the ledger as a `composite_verification`
kind instead of a `canonical_problem_verification`.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/run_composite_problem.py \\
        newton_hooke_sho
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

COMPOSITES_ROOT = _LABS_V2 / "composites"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: run_composite_problem.py <composite-dir-name>",
              file=sys.stderr)
        return 2
    composite_dir = COMPOSITES_ROOT / argv[1]
    yaml_path = composite_dir / "composite.yaml"
    if not yaml_path.is_file():
        print(f"composite.yaml not found: {yaml_path}", file=sys.stderr)
        return 2
    with yaml_path.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)

    composite_id = doc["composite_id"]
    parents = doc["parents"]
    coupling = doc["coupling"]
    problem = doc["canonical_problem"]
    subs = {k: float(v) for k, v in problem["canonical_substitutions"].items()}
    ranges = {
        k: (float(v[0]), float(v[1]))
        for k, v in problem["variable_ranges"].items()
    }

    sym_locals = {n: sp.Symbol(n, positive=True) for n in subs}
    local_formula = sp.sympify(problem["local_formula"], locals=sym_locals)

    print("=" * 70)
    print("Phase 13 composite verification")
    print(f"Composite: {composite_id}")
    print(f"Parents:   {parents['eq_a']} + {parents['eq_b']}")
    print(f"Coupling:  {coupling['tier']} on {coupling['v_a']} ↔ {coupling['v_b']}")
    print(f"Transducer: {coupling.get('transducer_id', '(none)')}")
    print()
    print(f"Composite canonical form: {doc.get('composite_canonical_form')}")
    print(f"Canonical problem: {problem.get('id')}")
    print(f"Local formula: {local_formula}")
    print(f"Canonical substitutions: {subs}")
    expected = float(local_formula.subs(
        {sym_locals[k]: v for k, v in subs.items()}
    ).evalf(15))
    print(f"Expected answer (local sympy): {expected:.12f}")
    print("=" * 70)
    print()

    try:
        result = source_and_verify(
            problem_statement=problem["statement"],
            query_id=f"phase13_{problem['id']}",
            local_formula=local_formula,
            variable_ranges=ranges,
            canonical_substitutions=subs,
            include_grok=False,
            n_pbt_samples=int(problem["pbt"]["n_samples"]),
            pbt_seed=int(problem["pbt"]["seed"]),
        )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    print(f"Board formula:        {result.formula_symbolic}")
    print(f"Board citations:      {len(result.citations)} primary sources")
    for c in result.citations:
        print(f"  · {c}")
    print()
    print(f"LOCAL value (sympy 15d):  {result.value}")
    print(f"LOCAL value (mpmath 50d): "
          f"{result.__dict__.get('_high_precision_value','n/a')[:40]}...")
    bva = result.__dict__.get("_board_value_attempt")
    if bva is not None:
        rel = abs(bva - result.value) / (abs(result.value) + 1e-300)
        print(f"Board value_attempt (capability data): {bva}  (rel_err {rel:.2e})")
    print(f"Unit: {result.unit}")
    print()
    print(f"Verification status: {result.verification_status}")
    for c in result.checks:
        emoji = "✅" if c.passed else "❌"
        print(f"  {emoji} Check {c.name}: {c.detail}")
    print()

    outcome = (
        HypothesisOutcome.EMPIRICAL
        if result.verification_status == "VERIFIED"
        else HypothesisOutcome.REJECTED
    )
    ledger = DiscoveryLedger(LEDGER_PATH)
    hyp = Hypothesis(
        eq_a=parents["eq_a"],
        eq_b=parents["eq_b"],
        kind="composite_verification",
        outcome=outcome,
        substitution={
            "composite_id": composite_id,
            "tier": coupling["tier"],
            "v_a": coupling["v_a"],
            "v_b": coupling["v_b"],
            "transducer_id": coupling.get("transducer_id", "(none)"),
        },
        evidence={
            "problem_id": problem["id"],
            "verification": result.as_ledger_dict(),
            "emergent_properties_expected": doc.get("emergent_properties_expected", []),
            "architect_anchor_citations": doc.get("architect_anchor_citations", []),
        },
        rejection_criterion=(
            f"composite verification failed: {result.verification_status}"
            if result.verification_status != "VERIFIED" else None
        ),
        review_required=False,
    )
    ledger.record(hyp)
    print(f"Ledger record written: kind={hyp.kind}, outcome={hyp.outcome.value}")
    print()

    if result.verification_status == "VERIFIED":
        print(f"🟢 {composite_id}: VERIFIED")
        print(f"   Composite reference value {result.value} {result.unit} accepted.")
        print(f"   Parent equations: {parents['eq_a']} + {parents['eq_b']}")
        print(f"   Coupling: {coupling['tier']} on {coupling['v_a']} ↔ {coupling['v_b']}")
        return 0
    else:
        print(f"🔴 {composite_id}: {result.verification_status}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
