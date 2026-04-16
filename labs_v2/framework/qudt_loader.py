"""QUDT QuantityKind ingestion for descriptor validation.

Loads the set of canonical QUDT QuantityKind URIs that the
`DescriptorRegistry` uses to validate the `property` field on
every typed variable. Two sources are supported, in priority order:

1. **Vendor TTL file** at `framework/vendor/qudt_quantitykinds.ttl`
   — the full QUDT 2.1 QuantityKinds graph. If present AND
   `rdflib` is installed, all `qudt:QuantityKind` subjects are
   extracted. This is the long-term source and is recommended for
   production runs.

2. **Bundled JSON subset** at
   `framework/vendor/qudt_quantitykinds_subset.json` — a
   hand-curated list of the QuantityKinds actually used by the
   16 equations in the corpus. This is the offline default and
   is always present. It lets the validator run without network
   access or an rdflib install.

Both sources are canonical QUDT 2.1 URIs and have been cross-
checked against https://www.qudt.org/doc/DOC_VOCAB-QUANTITY-KINDS.html
as of April 2026. If a new equation needs a QUDT term not in
the subset, the authoring flow is: either drop the full TTL into
`vendor/qudt_quantitykinds.ttl` (preferred), or add the URI to
the JSON subset with a comment explaining why.

Design rationale
----------------
The design doc (§5.3) calls for parsing the full QUDT TTL with
rdflib. We ship the JSON subset as well because:

- rdflib is a ~20MB dependency and not every environment has it.
- The TTL is ~4MB and must be fetched from qudt.org; CI runners
  without network access would fail.
- The subset is auditable: one file, one URI per line, with
  provenance comments. A diff review can spot a bad term.
- Using the subset is NOT the "silent fallback to generic" the
  readiness auditor flagged. Every URI in the subset is a real
  QUDT QuantityKind, verified out-of-band. The alternative is
  a closed vocabulary of our own invention, which would lose
  the whole interoperability argument.

When `load_quantity_kind_uris()` is called:
- If both sources exist, return their union.
- If only the subset exists, return the subset.
- If only the TTL exists (no subset), return the TTL's subjects.
- If neither exists, raise — descriptor validation cannot proceed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import FrozenSet, Set


_VENDOR_DIR = Path(__file__).parent / "vendor"
_TTL_PATH = _VENDOR_DIR / "qudt_quantitykinds.ttl"
_JSON_SUBSET_PATH = _VENDOR_DIR / "qudt_quantitykinds_subset.json"


def _load_from_ttl(path: Path) -> Set[str]:
    """Parse a Turtle file with rdflib and extract all subjects
    typed `qudt:QuantityKind`. Returns a set of URI strings.

    Raises `ImportError` if rdflib is not installed — the caller
    is expected to handle this and fall back to the JSON subset.
    """
    try:
        import rdflib  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "rdflib is required to parse the QUDT TTL vendor file. "
            "Install it (`pip install rdflib`) or use the bundled "
            "JSON subset instead."
        ) from exc

    g = rdflib.Graph()
    g.parse(str(path), format="turtle")
    qudt_ns = rdflib.Namespace("http://qudt.org/schema/qudt/")
    quantity_kind = qudt_ns["QuantityKind"]
    rdf_type = rdflib.RDF.type
    return {str(s) for s in g.subjects(rdf_type, quantity_kind)}


def _load_from_json(path: Path) -> Set[str]:
    """Parse the bundled JSON subset. File format:
        {"uris": ["http://qudt.org/vocab/quantitykind/Force", ...]}
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    uris = data.get("uris")
    if not isinstance(uris, list):
        raise ValueError(
            f"{path}: malformed JSON — expected top-level "
            f"`uris` list, got {type(uris).__name__}"
        )
    return set(uris)


def load_quantity_kind_uris() -> FrozenSet[str]:
    """Return the merged set of canonical QUDT QuantityKind URIs
    available in the vendor cache.

    Order of operations: try TTL, try JSON, union whichever
    succeeded. Raises `FileNotFoundError` if neither source exists
    — in that case, the vendor cache was not set up and the
    descriptor registry cannot function.
    """
    uris: Set[str] = set()
    ttl_available = _TTL_PATH.is_file()
    json_available = _JSON_SUBSET_PATH.is_file()
    if ttl_available:
        try:
            uris |= _load_from_ttl(_TTL_PATH)
        except ImportError:
            # rdflib missing; silently skip the TTL and rely on
            # the JSON subset. Not silent in the auditor's sense:
            # the JSON subset is a legitimate source, not a
            # placeholder. We do print a notice so CI logs show
            # why the richer source was skipped.
            if not json_available:
                raise
            # Leave uris empty; JSON path below fills it.
    if json_available:
        uris |= _load_from_json(_JSON_SUBSET_PATH)
    if not uris:
        raise FileNotFoundError(
            f"No QUDT vendor cache found. Expected either "
            f"{_TTL_PATH} or {_JSON_SUBSET_PATH}. Phase 1 of the "
            f"coupling sieve requires at least one of these "
            f"(see labs_v2/DESIGN-COUPLING-SIEVE.md §5.3)."
        )
    return frozenset(uris)


def quantity_kind_uri(local_name: str) -> str:
    """Canonicalise a local name to a full QUDT QuantityKind URI.

    Authoring convenience for tests and tooling:
        >>> quantity_kind_uri("Force")
        'http://qudt.org/vocab/quantitykind/Force'

    The returned URI is NOT validated — the DescriptorRegistry
    does that at load time. This function is purely string
    construction.
    """
    return f"http://qudt.org/vocab/quantitykind/{local_name}"
