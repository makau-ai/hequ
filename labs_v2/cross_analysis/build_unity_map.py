"""Build the hequ.ai unity map from existing equation.yaml files.

Reads every equation.yaml in labs_v2/equations/, extracts each
variable's I-ADOPT descriptor tuple (property, object_of_interest,
context), and groups variables that share the same tuple across
different equations. Each shared group is a tier-1 equivalence
candidate — the place where cross-domain coupling can happen.

The output is a deterministic, pure-YAML artifact that makes
the "unity of equations" claim visible and testable.

Usage:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/build_unity_map.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
EQUATIONS_ROOT = _LABS_V2 / "equations"
OUTPUT_PATH = _LABS_V2 / "cross_analysis" / "unity_map.yaml"


def load_equations():
    """Load every equation.yaml under labs_v2/equations/."""
    entries = []
    for path in sorted(EQUATIONS_ROOT.rglob("equation.yaml")):
        with path.open("r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        entries.append((path, doc))
    return entries


def extract_descriptor_tuples(entries):
    """For every variable in every equation, emit a (descriptor_key,
    equation_id, variable_name, variable_meaning) record.
    The descriptor_key is (property_uri, object_of_interest) —
    the two fields that must match for a tier-1 equivalence.
    Context and constraint are noted but not required for the
    initial match; the coupling sieve refines from there.
    """
    records = []
    for path, doc in entries:
        eq_id = doc.get("id", path.parent.name)
        domain = doc.get("domain", "unknown")
        for var_name, var_def in (doc.get("variables") or {}).items():
            descriptor = (var_def or {}).get("descriptor") or {}
            prop = descriptor.get("property")
            obj = descriptor.get("object_of_interest")
            if prop is None:
                continue
            records.append({
                "key": (prop, obj),
                "eq_id": eq_id,
                "domain": domain,
                "variable": var_name,
                "context": descriptor.get("context"),
                "constraint": descriptor.get("constraint"),
                "meaning": var_def.get("meaning", ""),
            })
    return records


def group_by_descriptor(records):
    """Group variable occurrences by their descriptor key and
    keep only genuine cross-equation groups.

    A tier-1 equivalence candidate requires the same descriptor
    tuple to appear in ≥2 DIFFERENT equations. If all
    occurrences of a descriptor are in the same equation, it is
    an intra-equation repeat (e.g., v_i and v_f both tagged
    Speed/rigid_body in EQ-WORK-ENERGY) — not a coupling
    candidate, just a shared variable kind within one law.
    """
    groups = defaultdict(list)
    for rec in records:
        groups[rec["key"]].append(rec)
    result = {}
    for key, occurrences in groups.items():
        distinct_eqs = {o["eq_id"] for o in occurrences}
        if len(distinct_eqs) >= 2:
            result[key] = occurrences
    return result


def short_property(uri):
    """Turn http://qudt.org/vocab/quantitykind/Force into 'Force'."""
    if not uri:
        return None
    if "/" in uri:
        return uri.rsplit("/", 1)[-1]
    return uri


def build_unity_map(entries, groups):
    """Emit the unity map as a structured YAML document."""
    coupling_candidates = []
    for (prop_uri, obj), occurrences in sorted(
        groups.items(),
        key=lambda kv: (len(kv[1]), kv[0]),
        reverse=True,
    ):
        coupling_candidates.append({
            "descriptor_key": {
                "property": short_property(prop_uri),
                "property_uri": prop_uri,
                "object_of_interest": obj,
            },
            "n_equations_sharing": len(occurrences),
            "occurrences": [
                {
                    "equation": o["eq_id"],
                    "domain": o["domain"],
                    "variable": o["variable"],
                    "context": o["context"],
                    "constraint": o["constraint"],
                    "meaning": o["meaning"],
                }
                for o in occurrences
            ],
        })

    return {
        "generated_from": str(EQUATIONS_ROOT.relative_to(_LABS_V2)),
        "n_equations": len(entries),
        "n_coupling_candidates": len(coupling_candidates),
        "rule": (
            "Variables from different equations whose I-ADOPT "
            "descriptor tuple (property URI, object_of_interest) "
            "matches are tier-1 equivalence candidates — the "
            "places where a cross-domain composite can be built. "
            "Context and constraint further refine the match and "
            "become the basis for the composite's assumption set."
        ),
        "equations_in_corpus": sorted(d["id"] for _, d in entries),
        "coupling_candidates": coupling_candidates,
    }


def main() -> int:
    entries = load_equations()
    records = extract_descriptor_tuples(entries)
    groups = group_by_descriptor(records)
    doc = build_unity_map(entries, groups)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, width=120)
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Equations scanned:   {doc['n_equations']}")
    print(f"Coupling candidates: {doc['n_coupling_candidates']}")
    print()
    print("Top candidates (by number of equations sharing the descriptor):")
    for cand in doc["coupling_candidates"][:10]:
        prop = cand["descriptor_key"]["property"]
        obj = cand["descriptor_key"]["object_of_interest"]
        n = cand["n_equations_sharing"]
        eqs = ", ".join(sorted({o["equation"] for o in cand["occurrences"]}))
        print(f"  {prop:20s} / {str(obj):20s}  n={n}  [{eqs}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
