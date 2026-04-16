"""Pre-register (freeze) the descriptor schema for the current
equation corpus.

Walks labs_v2/equations/ and computes a SHA-256 hash of each
equation.yaml file, records the (equation_id, domain, file_path,
sha256, frozen_at_utc) tuple, and appends a single
`descriptor_schema_freeze` record to the discovery ledger.

This creates an **immutable provenance anchor** for every I-ADOPT
descriptor in the corpus at the time of freeze. Any later novelty
claim from the unity-map / Blind Discovery Test can cite the
freeze ledger record as proof that the descriptors were declared
before the composite search ran — directly addressing the
descriptor-circularity concern raised unanimously by the board in
the project meta-analysis.

Once a freeze record exists, any further modification to a frozen
equation.yaml is a descriptor schema change that must be tagged
with a NEW freeze event (with a different version), not silently
overwritten.

Run:
    /tmp/hequ_venv/bin/python labs_v2/cross_analysis/freeze_descriptor_schema.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_LABS_V2 = Path(__file__).resolve().parent.parent
EQUATIONS_ROOT = _LABS_V2 / "equations"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"
FREEZE_MANIFEST_PATH = _LABS_V2 / "cross_analysis" / "descriptor_schema_freeze.yaml"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_descriptor_provenance(path: Path) -> dict:
    """Pull the identifying fields from an equation.yaml for the
    freeze manifest."""
    with path.open("r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    var_descriptors = {}
    for name, body in (doc.get("variables") or {}).items():
        descriptor = (body or {}).get("descriptor") or {}
        var_descriptors[name] = {
            "property": descriptor.get("property"),
            "object_of_interest": descriptor.get("object_of_interest"),
            "context": descriptor.get("context"),
            "constraint": descriptor.get("constraint"),
        }
    return {
        "equation_id": doc.get("id") or path.parent.name,
        "name": doc.get("name"),
        "domain": doc.get("domain"),
        "file_path": str(path.relative_to(_LABS_V2)),
        "file_sha256": sha256_file(path),
        "variables_frozen": var_descriptors,
        "n_variables": len(var_descriptors),
    }


def build_freeze_manifest() -> dict:
    entries = [
        extract_descriptor_provenance(p)
        for p in sorted(EQUATIONS_ROOT.rglob("equation.yaml"))
    ]
    # Corpus-level aggregate hash — a single fingerprint for the
    # whole descriptor schema at freeze time. If any equation.yaml
    # changes, this aggregate changes.
    corpus_bytes = "\n".join(
        f"{e['equation_id']}:{e['file_sha256']}" for e in entries
    ).encode()
    corpus_sha256 = hashlib.sha256(corpus_bytes).hexdigest()
    return {
        "version": "descriptor-schema-freeze/v1",
        "frozen_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "purpose": (
            "Pre-register the I-ADOPT descriptor schema across the "
            "entire equation corpus at a specific point in time. "
            "Any later claim of novelty from the unity-map or the "
            "Blind Discovery Test can cite this record as proof "
            "that the descriptors were declared before the search "
            "ran — directly addressing the descriptor-circularity "
            "concern raised unanimously by the board in the "
            "project meta-analysis (PROJECT_META_ANALYSIS.md)."
        ),
        "n_equations": len(entries),
        "corpus_sha256": corpus_sha256,
        "equations": entries,
        "pre_registered_claims": [
            (
                "Any novelty candidate produced by the unity-map "
                "mechanism after this freeze timestamp must refer "
                "to the frozen descriptors. If any equation.yaml "
                "file's SHA-256 hash changes, that equation is "
                "considered de-frozen and a new freeze event must "
                "be issued before the novelty claim can be made."
            ),
            (
                "The pre-registered falsifiability protocol for "
                "the unity-map mechanism (precision >= 0.50, "
                "recall >= 0.80 at n >= 30 equations, "
                "Cohen's kappa >= 0.80 on a three-annotator "
                "ground-truth panel) is binding on this frozen "
                "descriptor set and any descriptor set derived "
                "from it."
            ),
            (
                "No additional physics-textbook equations will be "
                "added to the corpus without an explicit novelty-"
                "hypothesis justification. New entries must come "
                "from communities with minimal physics citation "
                "overlap, OR be selected specifically to test a "
                "novelty hypothesis articulated in NOVELTY_PATHWAY.md."
            ),
        ],
    }


def main() -> int:
    manifest = build_freeze_manifest()

    with FREEZE_MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, width=120)
    print(f"Wrote freeze manifest: {FREEZE_MANIFEST_PATH}")
    print(f"  n_equations:   {manifest['n_equations']}")
    print(f"  frozen_at_utc: {manifest['frozen_at_utc']}")
    print(f"  corpus_sha256: {manifest['corpus_sha256']}")
    print()

    # Append a single ledger record pointing at the manifest.
    # Intentionally minimal — the full manifest is the sibling file;
    # the ledger record is a pointer with enough identifying fields
    # to be standalone-useful in discovery_ledger.jsonl queries.
    ledger_record = {
        "timestamp_utc": manifest["frozen_at_utc"],
        "kind": "descriptor_schema_freeze",
        "version": manifest["version"],
        "n_equations": manifest["n_equations"],
        "corpus_sha256": manifest["corpus_sha256"],
        "manifest_path": str(FREEZE_MANIFEST_PATH.relative_to(_LABS_V2)),
        "equation_ids": [e["equation_id"] for e in manifest["equations"]],
    }
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ledger_record, sort_keys=True) + "\n")
    print(f"Appended ledger record: kind={ledger_record['kind']}, "
          f"corpus_sha256={ledger_record['corpus_sha256'][:12]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
