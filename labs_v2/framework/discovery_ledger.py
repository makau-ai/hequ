"""The discovery ledger — append-only record of every hypothesis tried.

One of the hardest lessons from v1 was that the system rewarded
*declaring* connections. v2 fixes that by making the ledger the
single source of truth for what the engine actually tried, with
outcomes, evidence, and rejection criteria. Nothing is deleted.

Outcome tiers (from the design doctrine):
    PROVED           — formal derivation checked (e.g. sympy simplify==0)
    EMPIRICAL        — survived numerical tests + dimensional checks
                        but no formal proof
    CONJECTURAL      — interesting signal, no rigour yet
    REJECTED         — failed a specific criterion; criterion recorded
    COINCIDENCE      — survived individual tests but failed the
                       multiple-comparisons baseline (Wigner's rule)

The ledger is persisted as a JSONL file so every run appends a new
block. A query over the ledger answers "what hypotheses about
cross-domain connection did the engine entertain, and what did we
learn from each?"
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# Schema version for the JSONL ledger on disk. Bumped whenever the
# Hypothesis record layout changes in a way that old readers wouldn't
# understand. Readers tolerate older versions by filling in missing
# fields; writers always stamp the current version.
#
# v1 — initial schema, no chain hash, no rich substitution
# v2 — SHA-256 hash chain, structured substitutions for CoV sieve
# v3 — reserved (never shipped; placeholder for the axiom-gate
#      outcome demotions that were folded into evidence in v2)
# v4 — Medium milestone 2 coupling-sieve fields: `review_required`,
#      `tier1_coupling` / `tier2_coupling` / `tier3_conjectural`
#      kinds, `ai_review` evidence block, `physical_constraint_check`
#      and `emergent_properties` evidence blocks. The dataclass
#      layout is unchanged because all v4 additions live inside
#      the flexible `evidence` dict; the schema bump is declarative
#      so readers can tell the difference.
SCHEMA_VERSION = 4


# Substitution value type. In v1 of the schema a substitution was a
# simple name→name map (pure variable rename). In v2 it may also be
# a structured substitution carrying an expression, its inverse, and
# a declared domain — used by the future change-of-variables sieve.
SubstitutionValue = Union[str, Dict[str, str]]


class HypothesisOutcome(Enum):
    PROVED = "proved"
    EMPIRICAL = "empirical"
    CONJECTURAL = "conjectural"
    REJECTED = "rejected"
    COINCIDENCE = "coincidence"


@dataclass
class Hypothesis:
    """One attempted cross-domain connection.

    Fields
    ------
    eq_a / eq_b:
        The equation ids being related.
    substitution:
        The proposed substitution mapping variables of eq_a to eq_b.
        Each value is either:
          - a string (pure variable rename, e.g. {"F": "V"}),  OR
          - a dict carrying a richer substitution with its inverse
            and domain, e.g.
              {"S": {"expr": "exp(x)", "inverse": "log(S)", "domain": "S > 0"}}
        The dict form is the schema v2 extension for non-rename
        substitutions (change of variables, Wick rotation, etc.).
        JSON-serialisable in both cases.
    kind:
        What kind of connection was proposed. Examples:
        'structural_rename', 'dimensional_multiset_match',
        'change_of_variables', 'wick_rotation'.
    outcome:
        The discrete result — see HypothesisOutcome.
    evidence:
        A bag of evidence: sympy residuals, numeric test scores,
        dimensional-signature matches, explicit counterexamples.
    rejection_criterion:
        If outcome is REJECTED or COINCIDENCE, the specific rule that
        killed the hypothesis. Enables auditing ("we rejected
        Fourier↔Fick because ..." is impossible; "we rejected X
        because the residual was 3.2e-2" is auditable).
    timestamp:
        When the hypothesis was evaluated.
    schema_version:
        Which ledger schema this record conforms to. Stamped at
        construction so old records remain readable after upgrades.
    """
    eq_a: str
    eq_b: str
    kind: str
    outcome: HypothesisOutcome
    substitution: Dict[str, SubstitutionValue] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    rejection_criterion: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    schema_version: int = SCHEMA_VERSION
    # v4 addition: explicitly flag hypotheses that need AI review
    # board sign-off before they can be promoted past CONJECTURAL.
    # Tier-3 conjectural couplings, tier-2 couplings whose
    # physical-constraint filter returned all-not-applicable, and
    # any coupling whose AI board votes have not yet been
    # collected set this to True. Defaults to False so v1-v3
    # records deserialize cleanly.
    review_required: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        d["outcome"] = self.outcome.value
        return d


class DiscoveryLedger:
    """Append-only file-backed record of discovery hypotheses."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._in_memory: List[Hypothesis] = []
        self._prev_hash = "0" * 64   # genesis value for empty ledger
        self._integrity_warnings: List[str] = []
        # Load existing ledger on construction so queries work before
        # the first new append. While loading we also verify the
        # hash-chain (each record's `_chain_hash` must equal
        # sha256(prev_chain_hash + canonical_json(record_without_chain_hash))).
        if self.path.exists():
            with self.path.open("r") as fh:
                for line_no, line in enumerate(fh, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    # Chain verification runs on the raw JSON record
                    # BEFORE any type conversion. Writer computed the
                    # hash over the dict with `outcome` as a plain
                    # string (from `to_dict()`), so the reader must
                    # hash the same string form. Pop the chain hash,
                    # verify, then do the enum conversion for the
                    # Hypothesis constructor.
                    chain_hash = rec.pop("_chain_hash", None)
                    if chain_hash is not None:
                        expected = self._compute_chain_hash(self._prev_hash, rec)
                        if chain_hash != expected:
                            self._integrity_warnings.append(
                                f"line {line_no}: chain hash mismatch "
                                f"(file may have been tampered with)"
                            )
                        self._prev_hash = chain_hash
                    else:
                        self._integrity_warnings.append(
                            f"line {line_no}: v1 record without chain hash "
                            f"(pre-integrity-enforcement)"
                        )
                    # Skip non-Hypothesis records (e.g.,
                    # descriptor_schema_freeze) that don't have
                    # the Hypothesis fields.
                    if "outcome" not in rec:
                        continue
                    # Now convert types for the dataclass constructor.
                    rec["outcome"] = HypothesisOutcome(rec["outcome"])
                    rec.setdefault("schema_version", 1)
                    self._in_memory.append(Hypothesis(**rec))

    @staticmethod
    def _compute_chain_hash(prev_hash: str, record_dict: dict) -> str:
        """SHA-256 of (prev_hash || canonical_json(record))."""
        payload = prev_hash + json.dumps(
            record_dict, default=str, sort_keys=True
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record(self, hyp: Hypothesis) -> None:
        """Append a hypothesis to the ledger with a SHA-256 chain hash.

        Each record's `_chain_hash` equals
        `sha256(prev_chain_hash || canonical_json(record_without_chain_hash))`,
        forming a hash chain that makes tampering detectable at read
        time. This is the file-integrity protection the architecture
        auditor asked for; it does not replace OS-level immutability
        (chmod 0444) — callers that need tamper-resistance beyond
        append-only-good-faith should `chmod` the file between runs.
        """
        self._in_memory.append(hyp)
        rec_dict = hyp.to_dict()
        chain_hash = self._compute_chain_hash(self._prev_hash, rec_dict)
        rec_dict["_chain_hash"] = chain_hash
        with self.path.open("a") as fh:
            fh.write(json.dumps(rec_dict, default=str) + "\n")
        self._prev_hash = chain_hash

    def integrity_warnings(self) -> List[str]:
        """Return any integrity warnings encountered during load."""
        return list(self._integrity_warnings)

    def all(self) -> List[Hypothesis]:
        return list(self._in_memory)

    def by_outcome(self, outcome: HypothesisOutcome) -> List[Hypothesis]:
        return [h for h in self._in_memory if h.outcome is outcome]

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for h in self._in_memory:
            counts[h.outcome.value] = counts.get(h.outcome.value, 0) + 1
        return counts

    def for_pair(self, eq_a: str, eq_b: str) -> List[Hypothesis]:
        """Return every hypothesis relating the two equations, in
        either direction."""
        return [
            h for h in self._in_memory
            if (h.eq_a, h.eq_b) in {(eq_a, eq_b), (eq_b, eq_a)}
        ]


# ---------------------------------------------------------------------------
# Ledger builders for Layer 5 coupling hypotheses (v4)
# ---------------------------------------------------------------------------


def hypothesis_from_coupling(
    coupling,
    physical_verdict=None,
    emergent=None,
) -> "Hypothesis":
    """Translate a Layer 5 `CouplingHypothesis` (+ optional Phase 6
    `FilterVerdict` + Phase 7 `EmergentAnalysis`) into a ledger
    `Hypothesis` record ready for `DiscoveryLedger.record`.

    Outcome mapping (v4):
    - Tier 1 + physical filter PASSED → PROVED
    - Tier 1 + physical filter all-NA or mixed → EMPIRICAL
    - Tier 2 + physical filter PASSED → EMPIRICAL
    - Tier 2 + physical filter FAILED → REJECTED
    - Tier 2 + all-NA → CONJECTURAL (review_required=True)
    - Tier 3 → CONJECTURAL (review_required=True)

    The outcome mapping is deliberately conservative: PROVED is
    reserved for tier-1 couplings that also passed a physical-
    plausibility check. Nothing in this module touches the AI
    review board — that's Phase 9, and its output appears in
    `evidence.ai_review` after the fact.
    """
    from .couplings import CouplingTier
    from .physical_constraints import FilterVerdict, ConstraintOutcome

    kind_map = {
        CouplingTier.TIER1_EQUIVALENCE: "tier1_coupling",
        CouplingTier.TIER2_SIMILARITY:  "tier2_coupling",
        CouplingTier.TIER3_CONJECTURAL: "tier3_conjectural",
    }
    kind = kind_map[coupling.tier]

    # Build the evidence block by composing the pieces.
    evidence: Dict[str, Any] = dict(coupling.as_ledger_evidence())
    if physical_verdict is not None:
        evidence["physical_constraint_check"] = physical_verdict.as_dict()
    if emergent is not None:
        evidence["emergent_properties"] = emergent.as_dict()

    # Outcome dispatch.
    review_required = False
    rejection_criterion: Optional[str] = None
    if coupling.tier == CouplingTier.TIER3_CONJECTURAL:
        outcome = HypothesisOutcome.CONJECTURAL
        review_required = True
    elif physical_verdict is None:
        # No physical check run → treat as empirical (tier1) or
        # conjectural (tier2) pending review.
        if coupling.tier == CouplingTier.TIER1_EQUIVALENCE:
            outcome = HypothesisOutcome.EMPIRICAL
        else:
            outcome = HypothesisOutcome.CONJECTURAL
            review_required = True
    else:
        if physical_verdict.passed:
            outcome = (
                HypothesisOutcome.PROVED
                if coupling.tier == CouplingTier.TIER1_EQUIVALENCE
                else HypothesisOutcome.EMPIRICAL
            )
        elif physical_verdict.all_not_applicable:
            outcome = (
                HypothesisOutcome.EMPIRICAL
                if coupling.tier == CouplingTier.TIER1_EQUIVALENCE
                else HypothesisOutcome.CONJECTURAL
            )
            if coupling.tier != CouplingTier.TIER1_EQUIVALENCE:
                review_required = True
        else:
            # Some check returned FAILED (not just NA).
            outcome = HypothesisOutcome.REJECTED
            failed = [
                r for r in physical_verdict.results
                if r.outcome == ConstraintOutcome.FAILED
            ]
            if failed:
                rejection_criterion = (
                    f"physical_constraint:{failed[0].check_name}: "
                    f"{failed[0].reasoning}"
                )

    return Hypothesis(
        eq_a=coupling.eq_a_id,
        eq_b=coupling.eq_b_id,
        kind=kind,
        outcome=outcome,
        substitution=coupling.as_ledger_substitution(),
        evidence=evidence,
        rejection_criterion=rejection_criterion,
        review_required=review_required,
    )
