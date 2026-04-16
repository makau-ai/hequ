"""Failure Investigation Protocol (design v4 §11h, binding).

Phase 12 deliverable. When ANY evidence-level test fails —
a unit test, a composite execution, a sensor disagreement, or
a board rejection on physical grounds — this module is the
binding gate before any "fix" is proposed. The protocol is
exactly the sequence from §11h, no shortcuts:

  Step 1 — State audit
    Enumerate every variable the equation depends on. Is the
    engine observing each? A failure where a relevant variable
    is unobserved is a SENSING GAP, not an equation error.

  Step 2 — Assumption audit
    Re-read the equation's declared assumptions. Is any
    violated by the failing test's conditions? A failure under
    a violated assumption is an ASSUMPTION VIOLATION, not an
    equation error.

  Step 3 — Literature RAG for known failure modes
    Query the per-equation `failure_modes.md` index for
    documented failure modes from primary sources. Before any
    equation modification is proposed, this file must contain
    at least 3 citations from peer-reviewed primary sources
    discussing the specific observed failure.

  Step 4 — Board failure investigation
    Compile the state audit, assumption audit, and literature
    findings into a failure report. Query the AI review board
    with specialist personas and the cost-neutrality +
    academic-rigor disclaimers. Board returns one of:
      - sensing_gap
      - assumption_violated
      - equation_inadequate (GIGANTIC DEAL, escalates to user)

  Step 5 — Ledger entry
    Write the full investigation as `kind=failure_investigation`
    to the append-only hash-chained ledger.

Binding rule: an equation's `canonical_form` in
`equation.yaml` may not be edited except by a resolved
investigation with an `equation_inadequate` verdict that has
explicit user approval. Tolerance loosening on a reference
value requires the same procedure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ai_consensus import AIConsensusBoard, DESIGN_REVIEW_PERSONAS
from .ai_review_board import AIBoardKeysMissing
from .discovery_ledger import DiscoveryLedger, Hypothesis, HypothesisOutcome
from .typed_expression import TypedExpression


# ---------------------------------------------------------------------------
# Audit result types
# ---------------------------------------------------------------------------


@dataclass
class StateAudit:
    """Step 1 — State audit result.

    For each variable the equation depends on, did the failing
    test provide an observation? A variable without an
    observation is a sensing gap.
    """
    equation_id: str
    expected_variables: List[str]
    observed_variables: List[str]
    missing_variables: List[str]
    sensing_gap_detected: bool
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "equation_id": self.equation_id,
            "expected_variables": self.expected_variables,
            "observed_variables": self.observed_variables,
            "missing_variables": self.missing_variables,
            "sensing_gap_detected": self.sensing_gap_detected,
            "notes": self.notes,
        }


@dataclass
class AssumptionAudit:
    """Step 2 — Assumption audit result.

    For each assumption declared in the equation's YAML, was it
    satisfied by the failing test's conditions? A violated
    assumption means the test is outside the equation's declared
    domain, not that the equation is wrong.
    """
    equation_id: str
    declared_assumptions: List[str]
    violated_assumptions: List[str]
    violation_detected: bool
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "equation_id": self.equation_id,
            "declared_assumptions": self.declared_assumptions,
            "violated_assumptions": self.violated_assumptions,
            "violation_detected": self.violation_detected,
            "notes": self.notes,
        }


@dataclass
class LiteraturePriorSearch:
    """Step 3 — Literature RAG for known failure modes.

    For the specific equation and the specific observed
    failure, query the per-equation `failure_modes.md` index
    for documented prior art. v4 says: AT LEAST 3 citations
    from peer-reviewed primary sources must exist before any
    equation modification is proposed.
    """
    equation_id: str
    failure_signature: str            # short hash/key for the observed failure
    citations_found: List[str]        # DOI-level citations
    meets_threshold: bool             # len(citations_found) >= 3
    notes: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "equation_id": self.equation_id,
            "failure_signature": self.failure_signature,
            "citations_found": self.citations_found,
            "meets_threshold": self.meets_threshold,
            "notes": self.notes,
        }


@dataclass
class FailureInvestigationResult:
    """The complete investigation record. Written verbatim to
    the ledger with `kind="failure_investigation"`. The
    `board_verdict` determines what (if anything) happens next:

    - `sensing_gap` — no equation change; add the missing observable
    - `assumption_violated` — no equation change; reformulate the test
    - `equation_inadequate` — gigantic deal; user Decision Matrix

    The investigation itself is append-only and does not modify
    the equation.
    """
    investigation_id: str
    equation_id: str
    failure_context: Dict[str, Any]
    state_audit: StateAudit
    assumption_audit: AssumptionAudit
    literature_prior: LiteraturePriorSearch
    board_verdict: str                # one of the three
    board_rationale: str
    created_at: str
    user_escalation_required: bool = False
    ledger_recorded: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "investigation_id": self.investigation_id,
            "equation_id": self.equation_id,
            "failure_context": self.failure_context,
            "state_audit": self.state_audit.as_dict(),
            "assumption_audit": self.assumption_audit.as_dict(),
            "literature_prior": self.literature_prior.as_dict(),
            "board_verdict": self.board_verdict,
            "board_rationale": self.board_rationale,
            "user_escalation_required": self.user_escalation_required,
            "created_at": self.created_at,
            "ledger_recorded": self.ledger_recorded,
        }


# ---------------------------------------------------------------------------
# Step 1 — State audit
# ---------------------------------------------------------------------------


def run_state_audit(
    equation: TypedExpression,
    observed_values: Dict[str, Any],
) -> StateAudit:
    """Enumerate the equation's expected variables and compare
    against what the failing test actually observed. Missing
    variables flag a sensing gap.
    """
    expected = sorted(equation.variables.keys())
    observed = sorted(k for k in expected if k in observed_values)
    missing = [v for v in expected if v not in observed_values]
    notes = ""
    if missing:
        notes = (
            f"Sensing gap: the failing test did not observe "
            f"{len(missing)} variable(s) that the equation "
            f"depends on. Before any equation modification, the "
            f"test must be re-run with these variables included."
        )
    return StateAudit(
        equation_id=equation.id,
        expected_variables=expected,
        observed_variables=observed,
        missing_variables=missing,
        sensing_gap_detected=bool(missing),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Step 2 — Assumption audit
# ---------------------------------------------------------------------------


def run_assumption_audit(
    equation: TypedExpression,
    violated_explicitly: List[str],
) -> AssumptionAudit:
    """Check the failing test's conditions against each of the
    equation's declared assumptions. `violated_explicitly` is
    a caller-supplied list of assumption strings the caller
    believes were violated — the audit preserves the caller's
    identification verbatim and does not attempt to
    automatically detect violations (that would require a
    formal assumption language we haven't built yet; Phase 14+
    work).
    """
    declared = list(equation.assumptions)
    violated = [a for a in violated_explicitly if a in declared]
    unknown = [a for a in violated_explicitly if a not in declared]
    notes = ""
    if unknown:
        notes = (
            f"Caller identified violations that are not in the "
            f"equation's declared assumptions: {unknown}. These "
            f"may be implicit assumptions the equation YAML does "
            f"not yet capture — consider adding them."
        )
    return AssumptionAudit(
        equation_id=equation.id,
        declared_assumptions=declared,
        violated_assumptions=violated,
        violation_detected=bool(violated),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Step 3 — Literature prior search
# ---------------------------------------------------------------------------


def run_literature_prior_search(
    equation_id: str,
    failure_signature: str,
    equations_root: Path,
) -> LiteraturePriorSearch:
    """Look up the per-equation `failure_modes.md` file and
    extract citations relevant to the failure signature.

    For Phase 12 MVP: if the file doesn't exist or has fewer
    than 3 citations, the search returns
    `meets_threshold=False` and the investigation cannot
    propose any equation modification. The caller must
    populate `failure_modes.md` via board-driven literature
    search BEFORE reattempting the investigation.

    Phase 14+ (tracked): a real RAG index over the primary-
    source corpus (Feynman, OpenStax, NIST, etc.) with
    similarity-indexed passage retrieval. For now, the search
    is a plain-text grep over a flat per-equation file.
    """
    import re

    # Find the equation directory
    eq_dir = None
    for candidate in equations_root.rglob(f"{equation_id}/equation.yaml"):
        eq_dir = candidate.parent
        break
    if eq_dir is None:
        return LiteraturePriorSearch(
            equation_id=equation_id,
            failure_signature=failure_signature,
            citations_found=[],
            meets_threshold=False,
            notes=f"Equation directory not found for {equation_id}",
        )

    failure_modes_file = eq_dir / "failure_modes.md"
    if not failure_modes_file.is_file():
        return LiteraturePriorSearch(
            equation_id=equation_id,
            failure_signature=failure_signature,
            citations_found=[],
            meets_threshold=False,
            notes=(
                f"{failure_modes_file} does not exist. v4 §11h "
                f"requires ≥3 primary-source citations documenting "
                f"the observed failure before any equation "
                f"modification is proposed. Populate this file "
                f"via a board-driven literature search and retry "
                f"the investigation."
            ),
        )

    content = failure_modes_file.read_text(encoding="utf-8")
    # Extract anything that looks like a citation: DOI, arXiv,
    # ISBN, or "Author, Journal" patterns
    doi_pattern = re.compile(r"10\.\d{4,9}/[^\s\)]+")
    arxiv_pattern = re.compile(r"arXiv:\d{4}\.\d{4,5}")
    author_journal_pattern = re.compile(
        r"([A-Z][a-z]+(?: [&,] [A-Z][a-z]+)*?) \(?\d{4}\)?", re.MULTILINE
    )
    citations: List[str] = []
    citations.extend(doi_pattern.findall(content))
    citations.extend(arxiv_pattern.findall(content))
    citations.extend([m.group(0) for m in author_journal_pattern.finditer(content)])
    citations = list(dict.fromkeys(citations))  # dedup, preserve order

    return LiteraturePriorSearch(
        equation_id=equation_id,
        failure_signature=failure_signature,
        citations_found=citations,
        meets_threshold=len(citations) >= 3,
        notes=(
            f"Found {len(citations)} citation pattern(s) in "
            f"{failure_modes_file}"
        ),
    )


# ---------------------------------------------------------------------------
# Step 4 — Board failure investigation
# ---------------------------------------------------------------------------


_FAILURE_BOARD_SYSTEM = """\
You are a senior physicist specializing in cross-domain
equation analysis. A canonical problem for a specific equation
has failed its verification. Your job is to determine what
went wrong — NOT to propose a fix to the equation, but to
classify the failure into one of three categories so the
architect can respond appropriately.

The three allowed verdicts are:

- **`sensing_gap`** — the failing test did not observe all
  variables the equation depends on. The equation is fine;
  the experiment is incomplete. Response: add the missing
  observable and re-run the test.

- **`assumption_violated`** — the failing test ran under
  conditions that violate one of the equation's declared
  assumptions. The equation is fine; the test is outside its
  declared domain. Response: reformulate the test or move
  the problem to a different equation.

- **`equation_inadequate`** — after ruling out sensing gaps
  and assumption violations, you conclude the equation itself
  is wrong or incomplete. This is a GIGANTIC DEAL. The
  architect does NOT modify the equation on your word alone —
  your verdict triggers user escalation with a Decision Matrix.

Reply ONLY with a JSON object:

{
  "verdict": "sensing_gap" | "assumption_violated" | "equation_inadequate",
  "rationale": "<paragraph explaining the classification>",
  "evidence_cited": ["<specific state audit / assumption audit / literature finding>", ...],
  "user_escalation_required": true|false   // true only for equation_inadequate
}

IMPORTANT: the default hypothesis when theory and experiment
disagree is that the experiment is incomplete, not that the
theory is wrong. Do not jump to equation_inadequate unless the
state audit shows all variables observed AND the assumption
audit shows no violations AND the literature prior has ≥3
citations documenting this specific failure mode. These are
necessary but not sufficient preconditions.
"""


def run_board_failure_investigation(
    equation: TypedExpression,
    failure_context: Dict[str, Any],
    state_audit: StateAudit,
    assumption_audit: AssumptionAudit,
    literature_prior: LiteraturePriorSearch,
    include_grok: bool = False,
) -> Dict[str, Any]:
    """Query the AI review board with the full failure report
    and return their verdict dict."""
    payload = {
        "equation_id": equation.id,
        "equation_name": equation.name,
        "canonical_form": str(equation.canonical_form),
        "failure_context": failure_context,
        "state_audit": state_audit.as_dict(),
        "assumption_audit": assumption_audit.as_dict(),
        "literature_prior": literature_prior.as_dict(),
    }
    user_msg = (
        "A canonical problem verification has failed. The full "
        "audit chain is below. Classify the failure.\n\n"
        + json.dumps(payload, indent=2, default=str)
    )

    with AIConsensusBoard(include_grok=include_grok) as board:
        result = board.query(
            query_id=f"failure_investigation_{equation.id}",
            system_instructions=_FAILURE_BOARD_SYSTEM,
            user_message=user_msg,
            required_keys=("verdict", "rationale"),
        )
    # Prefer the first parseable reply for this MVP; Phase 13+
    # will route this through the four-phase board too.
    for resp in result.responses:
        if resp.parsed and "verdict" in resp.parsed:
            return resp.parsed
    return {
        "verdict": "error",
        "rationale": "No board member produced a parseable verdict.",
        "user_escalation_required": True,
    }


# ---------------------------------------------------------------------------
# Step 5 — Top-level investigation entry point
# ---------------------------------------------------------------------------


def investigate_failure(
    equation: TypedExpression,
    failure_context: Dict[str, Any],
    observed_values: Dict[str, Any],
    explicitly_violated_assumptions: List[str],
    failure_signature: str,
    equations_root: Path,
    ledger: Optional[DiscoveryLedger] = None,
    include_grok: bool = False,
) -> FailureInvestigationResult:
    """Run the full §11h Failure Investigation Protocol.

    Returns a `FailureInvestigationResult` with the three
    audits, the board verdict, and (if a ledger was provided)
    a record of the ledger write.

    The protocol does NOT modify the equation or loosen any
    tolerances. It classifies the failure. The caller is
    responsible for acting on the classification:
      - sensing_gap → add the missing observable, re-test
      - assumption_violated → reformulate or move the test
      - equation_inadequate → escalate to user, do NOT edit
    """
    # Step 1
    state_audit = run_state_audit(equation, observed_values)

    # Step 2
    assumption_audit = run_assumption_audit(
        equation, explicitly_violated_assumptions
    )

    # Step 3
    literature_prior = run_literature_prior_search(
        equation_id=equation.id,
        failure_signature=failure_signature,
        equations_root=equations_root,
    )

    # Step 4
    try:
        board_reply = run_board_failure_investigation(
            equation=equation,
            failure_context=failure_context,
            state_audit=state_audit,
            assumption_audit=assumption_audit,
            literature_prior=literature_prior,
            include_grok=include_grok,
        )
    except AIBoardKeysMissing as exc:
        board_reply = {
            "verdict": "error",
            "rationale": f"Board keys missing: {exc}",
            "user_escalation_required": True,
        }

    verdict = str(board_reply.get("verdict", "error")).strip().lower()
    rationale = str(board_reply.get("rationale", ""))
    # Equation inadequacy always requires user escalation.
    user_escalation = (
        verdict == "equation_inadequate"
        or verdict == "error"
        or bool(board_reply.get("user_escalation_required", False))
    )

    investigation_id = (
        f"{equation.id}_{failure_signature[:16]}_"
        f"{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    )

    result = FailureInvestigationResult(
        investigation_id=investigation_id,
        equation_id=equation.id,
        failure_context=failure_context,
        state_audit=state_audit,
        assumption_audit=assumption_audit,
        literature_prior=literature_prior,
        board_verdict=verdict,
        board_rationale=rationale,
        user_escalation_required=user_escalation,
        created_at=datetime.now(tz=timezone.utc).isoformat(),
    )

    # Step 5 — ledger record
    if ledger is not None:
        hyp = Hypothesis(
            eq_a=equation.id,
            eq_b="(failure_investigation)",
            kind="failure_investigation",
            outcome=HypothesisOutcome.CONJECTURAL,
            substitution={"investigation_id": investigation_id},
            evidence=result.as_dict(),
            rejection_criterion=None,
            review_required=user_escalation,
        )
        ledger.record(hyp)
        result.ledger_recorded = True

    return result
