"""Pre-registered validation harness for the Layer 5 coupling sieve.

Walks the expectations in `PRE_REGISTERED_COUPLINGS.md` and
asserts every one against the sieve's output on the live
corpus. Prints a deterministic PASS/FAIL summary and returns
exit code 0 on full pass, 1 on any failure.

This is the Phase 10 acceptance test: Medium m2 does not ship
until this script returns 0.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.couplings import CouplingTier
from framework.layer5_coupling_sieve import run_coupling_sieve
from framework.typed_expression import load_all_equations


# ---------------------------------------------------------------------------
# Expectations (mirror of PRE_REGISTERED_COUPLINGS.md)
# ---------------------------------------------------------------------------


@dataclass
class PositiveExpectation:
    id: str
    eq_a: str
    eq_b: str
    var_a: str           # variable in eq_a as the sieve canonicalises
    var_b: str           # variable in eq_b
    expected_tier: CouplingTier
    description: str


@dataclass
class RejectionExpectation:
    id: str
    eq_a: str
    eq_b: str
    description: str


# The sieve sorts equation pairs alphabetically and the var_a /
# var_b slots follow that sort. We therefore record expectations
# in alphabetical order too so the harness can compare directly.

POSITIVES: List[PositiveExpectation] = [
    PositiveExpectation(
        id="PRE-C01",
        eq_a="EQ-HOOKE", eq_b="EQ-NEWTON-II",
        var_a="F_spring", var_b="F",
        expected_tier=CouplingTier.TIER1_EQUIVALENCE,
        description="Newton II + Hooke → SHO: force ↔ restoring force",
    ),
    PositiveExpectation(
        id="PRE-C02",
        eq_a="EQ-FICK-DIFFUSION", eq_b="EQ-FOURIER-HEAT",
        var_a="J", var_b="q",
        expected_tier=CouplingTier.TIER2_SIMILARITY,
        description="Fourier + Fick structural identity: molar flux ↔ heat flux",
    ),
    PositiveExpectation(
        id="PRE-C03",
        eq_a="EQ-NEWTON-II", eq_b="EQ-OHM",
        var_a="F", var_b="V",
        expected_tier=CouplingTier.TIER2_SIMILARITY,
        description="Newton + Ohm structural analogy: force ↔ voltage",
    ),
    PositiveExpectation(
        id="PRE-C04",
        eq_a="EQ-NEWTON-II", eq_b="EQ-WORK-ENERGY",
        var_a="m", var_b="m",
        expected_tier=CouplingTier.TIER1_EQUIVALENCE,
        description="Newton + Work-Energy: shared inertial mass",
    ),
]

REJECTIONS: List[RejectionExpectation] = [
    RejectionExpectation(
        id="PRE-R01",
        eq_a="EQ-NEWTON-II", eq_b="EQ-SHANNON-ENTROPY",
        description="classical_mechanics ↔ information_theory killed by Gate 2",
    ),
    RejectionExpectation(
        id="PRE-R02",
        eq_a="EQ-BLACK-SCHOLES", eq_b="EQ-LOTKA-VOLTERRA",
        description="quantitative_finance ↔ population_dynamics killed by Gate 2",
    ),
    RejectionExpectation(
        id="PRE-R03",
        eq_a="EQ-LORENTZ-FACTOR", eq_b="EQ-BAYES",
        description="special_relativity ↔ probability killed by Gate 2",
    ),
]


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


def _pair_key(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def main() -> int:
    eqs_root = _LABS_V2 / "equations"
    equations = load_all_equations(eqs_root)
    print(f"Loaded {len(equations)} equations from {eqs_root}")

    report = run_coupling_sieve(equations, emit_tier3=False)
    print(report.summary())
    print()

    emitted = report.hypotheses
    pair_to_hypotheses = {}
    for h in emitted:
        pair_to_hypotheses.setdefault(
            _pair_key(h.eq_a_id, h.eq_b_id), []
        ).append(h)

    failures: List[str] = []

    print("=== POSITIVE couplings ===")
    for exp in POSITIVES:
        candidates = pair_to_hypotheses.get(_pair_key(exp.eq_a, exp.eq_b), [])
        match: Optional[object] = None
        for h in candidates:
            # Normalise variable comparison: the sieve canonicalises
            # (eq_a, eq_b) alphabetically, so (var_a, var_b) pair
            # order is determined by that.
            if (h.eq_a_id, h.eq_b_id, h.var_a, h.var_b) == (
                min(exp.eq_a, exp.eq_b),
                max(exp.eq_a, exp.eq_b),
                exp.var_a if exp.eq_a <= exp.eq_b else exp.var_b,
                exp.var_b if exp.eq_a <= exp.eq_b else exp.var_a,
            ):
                match = h
                break
        if match is None:
            failures.append(
                f"{exp.id} NOT FOUND: expected "
                f"{exp.eq_a}.{exp.var_a} <-> {exp.eq_b}.{exp.var_b} at "
                f"{exp.expected_tier.value}"
            )
            print(f"  [FAIL] {exp.id} — {exp.description}")
            continue
        if match.tier != exp.expected_tier:
            failures.append(
                f"{exp.id} TIER MISMATCH: expected "
                f"{exp.expected_tier.value}, got {match.tier.value}"
            )
            print(
                f"  [FAIL] {exp.id} — tier {match.tier.value} "
                f"(expected {exp.expected_tier.value})"
            )
            continue
        print(f"  [PASS] {exp.id} — {exp.description}")

    print()
    print("=== REJECTIONS ===")
    for rej in REJECTIONS:
        candidates = pair_to_hypotheses.get(_pair_key(rej.eq_a, rej.eq_b), [])
        if candidates:
            failures.append(
                f"{rej.id} LEAKED: expected zero hypotheses, got "
                f"{len(candidates)}"
            )
            print(f"  [FAIL] {rej.id} — leaked {len(candidates)} hypotheses")
            for h in candidates:
                print(f"           {h.var_a} <-> {h.var_b} ({h.tier.value})")
            continue
        print(f"  [PASS] {rej.id} — {rej.description}")

    print()
    if failures:
        print(f"=== {len(failures)} FAILURE(S) ===")
        for f in failures:
            print(f"  {f}")
        return 1
    print("=== ALL PRE-REGISTERED EXPECTATIONS MET ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
