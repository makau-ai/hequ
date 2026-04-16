"""Negative tests for the failure_modes referential integrity
validator.

The positive path — validator passing on real live data — is
already exercised by running validate_failure_modes.py against
the repository. This file adds the negative path the board's
hardening mod 3 asked for: a deliberately broken equation.yaml
fixture that MUST produce a nonzero exit and specific error
messages. Without this, the validator only had positive tests
— it could silently regress and stop catching the exact bugs
it exists to catch.

Run:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/test_validate_failure_modes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from cross_analysis.validate_failure_modes import validate_one_equation


FAKE_CORPUS = {
    "EQ-NEWTON-II": Path("/fake/path/newton_ii/equation.yaml"),
    "EQ-HOOKE":     Path("/fake/path/hooke/equation.yaml"),
    # Intentionally omit EQ-NONEXISTENT so the broken fixture
    # references an ID the validator must reject.
}


def _broken_equation_doc() -> dict:
    """A deliberately broken equation.yaml in-memory.

    It breaks the validator in three distinct ways so one run
    exercises the full error surface:

      1. Envelope inequality references an unbound identifier
         (`mystery_var`) — should be caught by the DOV-DSL
         parser as an Unbound error.
      2. use_instead is a bare dict instead of a list — should
         trigger the v1→v2 schema-migration warning.
      3. use_instead target references EQ-NONEXISTENT — should
         fail the corpus-ID resolution check.
    """
    return {
        "id": "EQ-TEST-BROKEN",
        "variables": {
            "F": {"dimension": "[force]", "unit": "newton"},
        },
        "failure_modes": [
            {
                "id": "F1-broken",
                "name": "deliberately broken failure mode for CI test",
                "envelope_variables": {
                    "U": {"dimension": "[length]/[time]", "unit": "m/s"},
                },
                "validity_envelope": {
                    "inequalities": [
                        "U / mystery_var >= 1",
                    ],
                },
                # (2) bare dict instead of list
                "use_instead": {
                    # (3) nonexistent target
                    "target_equation": "EQ-NONEXISTENT",
                    "reason": "we just made this up",
                    "ranking": "primary",
                },
            },
        ],
    }


def test_broken_equation_produces_expected_errors() -> None:
    errs = validate_one_equation(
        Path("/fake/path/broken/equation.yaml"),
        _broken_equation_doc(),
        FAKE_CORPUS,
    )
    print(f"validator returned {len(errs)} error(s):")
    for e in errs:
        print(f"  • {e}")

    assert errs, "validator should have returned errors on the broken fixture"

    # (1) Unbound identifier
    unbound_found = any(
        "Unbound" in e and "mystery_var" in e for e in errs
    )
    assert unbound_found, (
        "expected an Unbound-identifier error mentioning "
        "'mystery_var', got: " + "; ".join(errs)
    )

    # (2) Single-dict use_instead must warn about v1→v2 migration
    migration_found = any(
        "use_instead must be a list" in e for e in errs
    )
    assert migration_found, (
        "expected a use_instead-must-be-a-list migration warning, "
        "got: " + "; ".join(errs)
    )

    # (3) Nonexistent target_equation must be flagged
    deadref_found = any(
        "EQ-NONEXISTENT" in e and "unknown equation" in e for e in errs
    )
    assert deadref_found, (
        "expected a dead-reference error citing EQ-NONEXISTENT, "
        "got: " + "; ".join(errs)
    )


def test_clean_equation_produces_no_errors() -> None:
    """Sanity check: a well-formed failure_modes entry passes."""
    clean = {
        "id": "EQ-TEST-CLEAN",
        "variables": {
            "F": {"dimension": "[force]", "unit": "newton"},
        },
        "failure_modes": [
            {
                "id": "F1-clean",
                "name": "clean entry for the sanity check",
                "envelope_variables": {
                    "U": {"dimension": "[length]/[time]", "unit": "m/s"},
                    "f": {"dimension": "1/[time]",        "unit": "rad/s"},
                    "L": {"dimension": "[length]",        "unit": "m"},
                },
                "validity_envelope": {
                    "named_groups": {
                        "Ro": {"definition": "U / (f * L)"},
                    },
                    "inequalities": ["Ro >= 1"],
                },
                "use_instead": [
                    {
                        "target_equation": "EQ-NEWTON-II",
                        "reason": "textbook alternative",
                        "ranking": "primary",
                    },
                ],
            },
        ],
    }
    errs = validate_one_equation(
        Path("/fake/path/clean/equation.yaml"),
        clean,
        FAKE_CORPUS,
    )
    assert not errs, f"clean fixture should not produce errors: {errs}"
    print("clean fixture produced zero errors — sanity check passed.")


def main() -> int:
    print("=" * 60)
    print("validate_failure_modes negative-test suite")
    print("=" * 60)
    test_broken_equation_produces_expected_errors()
    print()
    test_clean_equation_produces_no_errors()
    print()
    print("All validator negative/positive tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
