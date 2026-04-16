"""Referential-integrity validator for failure_modes blocks.

For every equation.yaml in labs_v2/equations/, this script
checks that its `failure_modes:` block (if present) satisfies:

  1. Every variable referenced in a failure mode's DOV-DSL
     validity_envelope (inequalities or named_groups) either
     (a) appears in the equation's `variables:` block, or
     (b) is declared in the envelope's own `named_groups:`.
     This is enforced by running the DOV-DSL parser, which
     raises on unbound identifiers.

  2. Every `target_equation` listed in a failure mode's
     `use_instead:` field resolves to an equation ID that
     actually exists under labs_v2/equations/.

This is the CI gate that prevents dead references from
accumulating in the corpus.

Exit codes:
    0  — all referential integrity checks passed
    1  — at least one equation.yaml has dead references

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/validate_failure_modes.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.dov_dsl import validate_envelope

EQUATIONS_ROOT = _LABS_V2 / "equations"


def load_corpus_ids() -> Dict[str, Path]:
    """Map equation ID → path of its equation.yaml."""
    out: Dict[str, Path] = {}
    for path in sorted(EQUATIONS_ROOT.rglob("equation.yaml")):
        with path.open("r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        eq_id = doc.get("id") or path.parent.name
        out[eq_id] = path
    return out


def validate_one_equation(
    path: Path,
    doc: dict,
    corpus_ids: Dict[str, Path],
) -> List[str]:
    """Return a list of error messages for this equation (empty
    if all checks passed)."""
    errors: List[str] = []
    eq_id = doc.get("id") or path.parent.name
    failure_modes = doc.get("failure_modes") or []
    if not failure_modes:
        # Nothing to validate — perfectly legal.
        return errors

    equation_variables = doc.get("variables") or {}

    for i, fm in enumerate(failure_modes):
        fm_id = fm.get("id") or f"(index {i})"
        envelope = fm.get("validity_envelope") or {}

        # --- (1) DOV-DSL parse + unbound-identifier check ---
        # Extra envelope variables are authored in the failure
        # mode itself (e.g., Rossby needs U, f, L even though
        # Newton II's canonical form has F, m, a). Merge them
        # with the equation's own variables for binding.
        envelope_extra_vars = fm.get("envelope_variables") or {}
        combined_vars = {**equation_variables, **envelope_extra_vars}
        result = validate_envelope(envelope, combined_vars)
        if not result.ok:
            for err in result.errors:
                errors.append(
                    f"[{eq_id} :: {fm_id}] validity_envelope: {err}"
                )

        # --- (2) use_instead referential integrity ---
        # v2 schema: use_instead is a list of {target_equation, reason}.
        use_instead = fm.get("use_instead") or []
        if isinstance(use_instead, dict):
            # Tolerate the v1 single-object form for now but
            # flag it so authors migrate.
            errors.append(
                f"[{eq_id} :: {fm_id}] use_instead must be a list "
                f"of objects in v2 schema (found a single dict). "
                f"Wrap it in a YAML list."
            )
            use_instead = [use_instead]
        for entry in use_instead:
            target = (entry or {}).get("target_equation")
            if not target:
                errors.append(
                    f"[{eq_id} :: {fm_id}] use_instead entry "
                    f"missing `target_equation` field"
                )
                continue
            if target not in corpus_ids:
                errors.append(
                    f"[{eq_id} :: {fm_id}] use_instead references "
                    f"unknown equation {target!r} (not found under "
                    f"labs_v2/equations/). Either add the target "
                    f"equation or fix the reference."
                )

    return errors


def main() -> int:
    corpus_ids = load_corpus_ids()
    total_errors: List[str] = []
    n_checked = 0
    n_with_failure_modes = 0
    for eq_id, path in corpus_ids.items():
        with path.open("r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        n_checked += 1
        if doc.get("failure_modes"):
            n_with_failure_modes += 1
        errs = validate_one_equation(path, doc, corpus_ids)
        total_errors.extend(errs)

    print(f"Equations checked:            {n_checked}")
    print(f"Equations with failure_modes: {n_with_failure_modes}")
    print(f"Referential integrity errors: {len(total_errors)}")
    if total_errors:
        print()
        for err in total_errors:
            print(f"  • {err}")
        return 1
    print()
    print("All referential integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
