"""End-to-end tests for the DOV-DSL parser and evaluator.

The centerpiece is the Rossby-number worked example for Newton
II's rotating-frame failure mode — the exact example the board
asked for in its required-modification #1. It proves the DSL is
not just spec: it parses, binds, and evaluates.

Run:
    /tmp/hequ_venv/bin/python labs_v2/framework/test_dov_dsl.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.dov_dsl import (
    DovDslParseError,
    EvaluationError,
    parse_inequality,
    parse_named_group,
    validate_envelope,
    evaluate,
)


def test_rossby_newton_ii_worked_example() -> None:
    """The worked example the board required.

    Newton II in a rotating/accelerating frame without
    pseudoforces is valid only when the Rossby number is large
    (inertial forces dominate Coriolis forces). Validity
    envelope: Ro := U / (f * L); require Ro >= 1.
    """
    # These are the variables authors would add to the
    # equation.yaml's `variables:` block for the rotating-frame
    # failure-mode envelope (not the equation's core variables).
    variables = {
        "U": {"dimension": "[length]/[time]", "unit": "m/s"},
        "f": {"dimension": "1/[time]",        "unit": "rad/s"},
        "L": {"dimension": "[length]",        "unit": "m"},
    }
    envelope = {
        "named_groups": {
            "Ro": {"definition": "U / (f * L)",
                   "dimensionless": True,
                   "interpretation": "Rossby number"},
        },
        "inequalities": [
            "Ro >= 1",
        ],
    }
    result = validate_envelope(envelope, variables)
    assert result.ok, f"envelope failed to validate: {result.errors}"
    assert "Ro" in result.named_groups
    assert len(result.inequalities) == 1
    ro_ast = result.inequalities[0]
    print(f"Parsed inequality: {ro_ast.source}")
    print(f"  lhs: {ro_ast.lhs}  op: {ro_ast.rel_op}  rhs: {ro_ast.rhs}")
    print(f"  free symbols: {[s.name for s in ro_ast.free_symbols]}")

    # Case A — a mid-latitude Earth atmosphere scenario.
    # U = 10 m/s, f = 1e-4 1/s (Coriolis parameter at 45°),
    # L = 100 m. Ro = 10/(1e-4 * 100) = 1000 >> 1, so
    # Newton II in the rotating frame's simple form is a
    # reasonable approximation — the envelope holds.
    sample_small_scale = {"U": 10.0, "f": 1.0e-4, "L": 100.0}
    ok_small = evaluate(ro_ast, sample_small_scale, result.named_groups)
    print(f"Sample (small scale, Ro=1000): envelope holds? {ok_small}")
    assert ok_small is True

    # Case B — synoptic-scale weather: same U and f, but
    # L = 1e6 m (1000 km). Ro = 10/(1e-4 * 1e6) = 0.1 << 1,
    # so Coriolis dominates — the simple form fails and the
    # author should switch to the rotating-frame formulation.
    sample_synoptic = {"U": 10.0, "f": 1.0e-4, "L": 1.0e6}
    ok_synoptic = evaluate(ro_ast, sample_synoptic, result.named_groups)
    print(f"Sample (synoptic scale, Ro=0.1): envelope holds? {ok_synoptic}")
    assert ok_synoptic is False


def test_unbound_identifier_rejected() -> None:
    variables = {"U": {}, "L": {}}
    envelope = {
        # `f` is not declared in variables or named_groups
        "inequalities": ["U / (f * L) >= 1"],
    }
    result = validate_envelope(envelope, variables)
    assert not result.ok
    assert any("f" in e and "Unbound" in e for e in result.errors), \
        f"expected Unbound error for f, got {result.errors}"
    print("unbound-identifier rejection: OK")


def test_quantifier_rejected() -> None:
    variables = {"x": {}}
    envelope = {
        "inequalities": ["forall x > 0"],
    }
    result = validate_envelope(envelope, variables)
    assert not result.ok
    assert any("pointwise" in e for e in result.errors), \
        f"expected pointwise-only error, got {result.errors}"
    print("quantifier rejection: OK")


def test_divide_by_zero_raises_evaluation_error() -> None:
    """Equatorial Coriolis test: at latitude=0, f = 2·Ω·sin(0) = 0,
    so the Rossby number U / (f · L) divides by zero. The board
    hardening mod 1 requires `evaluate()` to raise
    EvaluationError, not silently return False. This matters
    because silently returning False would tell the caller 'Newton
    II's validity envelope is broken at the equator' when the
    truth is 'the envelope cannot be decided at the equator — the
    diagnostic ratio itself is undefined there.' The caller must
    know the difference."""
    variables = {"U": {}, "f": {}, "L": {}}
    envelope = {
        "named_groups": {
            "Ro": {"definition": "U / (f * L)"},
        },
        "inequalities": ["Ro >= 1"],
    }
    result = validate_envelope(envelope, variables)
    assert result.ok, result.errors
    equatorial_sample = {"U": 10.0, "f": 0.0, "L": 100.0}
    try:
        evaluate(
            result.inequalities[0],
            equatorial_sample,
            result.named_groups,
        )
    except EvaluationError as exc:
        print(f"divide-by-zero correctly raised: {exc}")
        return
    raise AssertionError(
        "evaluate() did not raise EvaluationError on the "
        "equatorial f=0 case; silent False is forbidden."
    )


def test_nan_raises_evaluation_error() -> None:
    """log(0) case — natural log of zero evaluates to -oo, which
    should trip the infinity guard in _coerce_side. Confirms the
    second leg of the undefined-intermediate policy."""
    variables = {"x": {}}
    envelope = {
        "inequalities": ["log(x) >= 0"],
    }
    result = validate_envelope(envelope, variables)
    assert result.ok, result.errors
    try:
        evaluate(result.inequalities[0], {"x": 0.0})
    except EvaluationError as exc:
        print(f"log(0) correctly raised: {exc}")
        return
    raise AssertionError(
        "evaluate() did not raise on log(0); expected "
        "EvaluationError for the non-finite intermediate."
    )


def test_named_group_reuse() -> None:
    """A named group can be referenced by later inequalities."""
    variables = {"U": {}, "f": {}, "L": {}}
    envelope = {
        "named_groups": {
            "Ro": {"definition": "U / (f * L)"},
        },
        "inequalities": [
            "Ro >= 1",
            "Ro <= 1000",
        ],
    }
    result = validate_envelope(envelope, variables)
    assert result.ok, result.errors
    sample = {"U": 10.0, "f": 1.0e-4, "L": 100.0}
    assert evaluate(
        result.inequalities[0], sample, result.named_groups
    ) is True
    assert evaluate(
        result.inequalities[1], sample, result.named_groups
    ) is True
    # Push out of envelope on the upper side.
    big = {"U": 10.0, "f": 1.0e-5, "L": 1.0}
    # Ro = 10 / (1e-5 * 1) = 1e6 — violates upper bound.
    assert evaluate(
        result.inequalities[1], big, result.named_groups
    ) is False
    print("named-group reuse: OK")


def main() -> int:
    print("=" * 60)
    print("DOV-DSL end-to-end test: Rossby worked example")
    print("=" * 60)
    test_rossby_newton_ii_worked_example()
    print()
    test_unbound_identifier_rejected()
    test_quantifier_rejected()
    test_divide_by_zero_raises_evaluation_error()
    test_nan_raises_evaluation_error()
    test_named_group_reuse()
    print()
    print("All DOV-DSL tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
