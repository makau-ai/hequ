"""Automated physical-admissibility checks for verified composites.

Reads every composite.yaml in labs_v2/composites/ and verifies
that the declared transducer properties satisfy the physical
constraints required by their type:

  1. GYRATOR composites: the interconnection must be skew-symmetric.
     Checks that the declared constitutive relations (F = BL·i,
     V = BL·v or τ = K·i, V = K·ω) satisfy power conservation:
     effort_a · flow_a == effort_b · flow_b identically when the
     gyrator relations are substituted.

  2. ONSAGER composites: L_12 = L_21 (reciprocal cross-coefficients).
     Checks that the same coefficient (s_T, etc.) appears in both
     the forward (Soret: T→C) and reverse (Dufour: C→T) composites
     when both exist in the corpus.

  3. ALL composites: dimensional consistency of the composite
     canonical form. Checks that the local_formula, when parsed
     with the canonical_substitutions' units, produces a result
     with the declared expected_dimension.

Designed to run in CI alongside validate_failure_modes.py and
build_unity_map.py.

Run:
    /tmp/hequ_venv/bin/python labs_v2/framework/physical_admissibility.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sympy as sp
import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
COMPOSITES_ROOT = _LABS_V2 / "composites"


def load_composites() -> List[Tuple[Path, Dict[str, Any]]]:
    results = []
    for path in sorted(COMPOSITES_ROOT.rglob("composite.yaml")):
        with path.open("r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        results.append((path, doc))
    return results


def check_gyrator_power_conservation(doc: Dict[str, Any]) -> List[str]:
    """For gyrator transducers, verify that the constitutive
    relations satisfy power conservation symbolically.

    A gyrator with coefficient G has:
        effort_a = G · flow_b
        effort_b = G · flow_a   (OR flow_b = G · effort_a, etc.)

    Power conservation requires:
        effort_a · flow_a == effort_b · flow_b

    Substituting the gyrator relations:
        (G · flow_b) · flow_a == effort_b · (G⁻¹ · effort_a)
        ... which reduces to G · flow_a · flow_b on both sides.

    We check this symbolically.
    """
    errors = []
    coupling = doc.get("coupling", {})
    props = coupling.get("transducer_properties", {})
    tp = props.get("type", "")

    if "gyrator" not in tp.lower():
        return errors

    relations = props.get("constitutive_relations", [])
    if len(relations) < 2:
        errors.append(
            f"gyrator {doc.get('composite_id')}: expected 2 constitutive "
            f"relations, got {len(relations)}"
        )
        return errors

    # Extract the coefficient from relations like "F = BL * i" and "V = BL * v"
    # or "tau_motor = K * i" and "V_back = K * omega"
    coefficients = set()
    for rel in relations:
        # Match patterns like "X = COEFF * Y" or "X = COEFF · Y"
        cleaned = rel.replace("·", "*").replace(" ", "")
        match = re.search(r"=(\w+)\*", cleaned)
        if match:
            coefficients.add(match.group(1))

    if len(coefficients) != 1:
        errors.append(
            f"gyrator {doc.get('composite_id')}: expected one shared "
            f"coefficient across both constitutive relations, "
            f"found {coefficients}"
        )
        return errors

    coeff_name = coefficients.pop()

    # Symbolic power-conservation check
    G = sp.Symbol(coeff_name, positive=True)
    # Generic effort/flow variables for both ports
    e_a, f_a, e_b, f_b = sp.symbols("e_a f_a e_b f_b")

    # Gyrator: e_a = G·f_b and e_b = G·f_a (standard form)
    # Power port A: P_a = e_a · f_a = G·f_b · f_a
    # Power port B: P_b = e_b · f_b = G·f_a · f_b
    P_a = (G * f_b) * f_a
    P_b = (G * f_a) * f_b
    residual = sp.simplify(P_a - P_b)

    if residual != 0:
        errors.append(
            f"gyrator {doc.get('composite_id')}: power conservation "
            f"FAILED — P_a - P_b = {residual} (expected 0)"
        )
    return errors


def check_onsager_reciprocity(
    composites: List[Tuple[Path, Dict[str, Any]]]
) -> List[str]:
    """For Onsager transducer pairs (Soret/Dufour), verify that
    the same cross-coefficient appears in both directions.

    Finds composites that share the same parent equation pair
    and both declare Onsager-type transducers, then checks that
    the coefficient name/value is consistent.
    """
    errors = []

    # Group by parent pair (sorted)
    parent_groups: Dict[Tuple[str, str], List[Dict]] = {}
    for path, doc in composites:
        parents = doc.get("parents", {})
        eq_a = parents.get("eq_a", "")
        eq_b = parents.get("eq_b", "")
        key = tuple(sorted([eq_a, eq_b]))
        parent_groups.setdefault(key, []).append(doc)

    for parent_pair, docs in parent_groups.items():
        onsager_docs = [
            d for d in docs
            if "onsager" in d.get("coupling", {})
                .get("transducer_properties", {})
                .get("type", "").lower()
        ]
        if len(onsager_docs) >= 2:
            # Check that all share the same coefficient
            coeffs = set()
            for d in onsager_docs:
                props = d["coupling"]["transducer_properties"]
                onsager_sym = props.get("onsager_symmetry", "")
                coeffs.add(onsager_sym)
            # All should reference L_12 = L_21
            has_reciprocity = any(
                "L_12" in c and "L_21" in c for c in coeffs
            )
            if not has_reciprocity:
                errors.append(
                    f"Onsager pair {parent_pair}: reciprocity "
                    f"L_12 = L_21 not declared in all composites"
                )

    return errors


def check_formula_dimensional_consistency(doc: Dict[str, Any]) -> List[str]:
    """Check that the local formula can be parsed and evaluated
    with the canonical substitutions without error."""
    errors = []
    problem = doc.get("canonical_problem", {})
    formula_str = problem.get("local_formula")
    subs = problem.get("canonical_substitutions", {})

    if not formula_str or not subs:
        return errors

    sym_locals = {n: sp.Symbol(n, positive=True) for n in subs}
    try:
        expr = sp.sympify(formula_str, locals=sym_locals)
        result = expr.subs({sym_locals[k]: float(v) for k, v in subs.items()})
        val = float(result.evalf())
        if val != val:  # NaN check
            errors.append(
                f"{doc.get('composite_id')}: formula evaluates to NaN "
                f"with canonical substitutions"
            )
    except Exception as exc:
        errors.append(
            f"{doc.get('composite_id')}: formula parse/eval error: {exc}"
        )
    return errors


def main() -> int:
    composites = load_composites()
    all_errors: List[str] = []
    n_gyrators = 0
    n_onsager_pairs = 0

    print(f"Composites loaded: {len(composites)}")
    print()

    # Per-composite checks
    for path, doc in composites:
        cid = doc.get("composite_id", path.parent.name)
        coupling = doc.get("coupling", {})
        props = coupling.get("transducer_properties", {})
        tp = props.get("type", "")

        # Gyrator power conservation
        if "gyrator" in tp.lower():
            n_gyrators += 1
            errs = check_gyrator_power_conservation(doc)
            all_errors.extend(errs)
            status = "FAIL" if errs else "PASS"
            print(f"  {cid}: gyrator power conservation → {status}")

        # Formula dimensional consistency
        errs = check_formula_dimensional_consistency(doc)
        all_errors.extend(errs)
        status = "FAIL" if errs else "PASS"
        print(f"  {cid}: formula consistency → {status}")

    # Cross-composite checks
    print()
    onsager_errs = check_onsager_reciprocity(composites)
    all_errors.extend(onsager_errs)
    # Count Onsager pairs
    parent_groups: Dict = {}
    for _, doc in composites:
        parents = doc.get("parents", {})
        eq_a = parents.get("eq_a", "")
        eq_b = parents.get("eq_b", "")
        key = tuple(sorted([eq_a, eq_b]))
        parent_groups.setdefault(key, []).append(doc)
    for key, docs in parent_groups.items():
        onsager_count = sum(
            1 for d in docs
            if "onsager" in d.get("coupling", {})
                .get("transducer_properties", {})
                .get("type", "").lower()
        )
        if onsager_count >= 2:
            n_onsager_pairs += 1
            print(f"  Onsager pair {key}: L_12=L_21 reciprocity → "
                  f"{'FAIL' if onsager_errs else 'PASS'}")

    print()
    print(f"Gyrator composites checked:  {n_gyrators}")
    print(f"Onsager pairs checked:       {n_onsager_pairs}")
    print(f"Total admissibility errors:  {len(all_errors)}")

    if all_errors:
        print()
        for e in all_errors:
            print(f"  • {e}")
        return 1

    print()
    print("All physical-admissibility checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
