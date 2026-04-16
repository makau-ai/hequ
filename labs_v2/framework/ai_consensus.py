"""General-purpose AI review board consensus querying.

Phase 12+ foundation. The Phase 11 AI review board module
(`ai_review_board.py`) was coupling-specific: it took a
`CouplingHypothesis` and returned a `BoardDecision` about
whether to promote it. This module is the generalization:
take an arbitrary structured query, send it to Claude Opus +
OpenAI GPT-5 + Gemini 2.5 Pro, and aggregate their responses
with cross-validation.

Use cases
---------
1. **Architecture review** — submit a design document, ask for
   APPROVE/MODIFY/REJECT verdicts with per-model concerns.
2. **Reference-value sourcing** — for a canonical physics
   problem, ask each model to independently produce the
   closed-form answer + numerical value + citation, then
   triangulate. A reference value is only accepted when ≥2
   models agree within a user-supplied tolerance.
3. **Transducer library authoring** — ask each model to produce
   a structured list (e.g., bond-graph transducers) and take
   the cross-validated intersection / union.

Design contracts
----------------
- **Zero pip dependency.** Uses the same stdlib `urllib` HTTP
  layer as `ai_review_board.py`, reusing `_call_claude`,
  `_call_openai`, `_call_gemini`, and `_redact_key`.
- **Keys fetched via gcloud Secret Manager at entry-time only**,
  cleared on `__exit__`. Same pattern as `ReviewBoard`.
- **Structured JSON contract**. Every consensus query ships a
  prompt template that demands a JSON reply. Replies that fail
  to parse into the declared schema are recorded as ERROR, not
  silently dropped.
- **Per-model isolation**. One model crashing or timing out
  does not abort the query. The aggregator reports partial
  results honestly.

The Phase 11 observation stands: OpenAI is the strictest
reviewer on physical claims; Claude is the most permissive on
structural analogies; Gemini is the most willing to accept
pedagogical canon. Cross-validation is most valuable when the
three disagree — the disagreement is the signal.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence

from .ai_review_board import (
    AIBoardAPIError,
    AIBoardKeysMissing,
    ReviewBoardKeys,
    _call_claude,
    _call_gemini,
    _call_grok,
    _call_openai,
    _redact_key,
)


# ---------------------------------------------------------------------------
# Response types
# ---------------------------------------------------------------------------


@dataclass
class ConsensusResponse:
    """One reviewer's reply to a consensus query."""
    reviewer: str
    parsed: Optional[Dict[str, Any]]   # None if the model's reply
                                       # could not be parsed as JSON
    raw_response: str                  # verbatim text (for audit)
    timestamp: str                     # ISO8601 UTC
    error: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "reviewer": self.reviewer,
            "parsed": self.parsed,
            "timestamp": self.timestamp,
            "error": self.error,
        }


@dataclass
class ConsensusResult:
    """The aggregated result of one consensus query.

    Fields:
      `responses` — list of 3 ConsensusResponse (one per model)
      `agreement` — fraction of models that replied with
        `parsed is not None` (0.0-1.0)
      `schema_ok` — fraction of models whose parsed reply
        matched the requested schema
      `consensus` — a merged dict representing the agreed-on
        content, constructed by the caller-provided aggregator
        function (or None if no aggregator was given)
    """
    query_id: str
    responses: List[ConsensusResponse]
    agreement: float
    schema_ok: float
    consensus: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "agreement": self.agreement,
            "schema_ok": self.schema_ok,
            "consensus": self.consensus,
            "responses": [r.as_dict() for r in self.responses],
        }


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_json_response(raw: str) -> Optional[Dict[str, Any]]:
    """Extract a JSON object from a model reply. Tolerates
    markdown code fences, leading/trailing prose, and single
    surrounding braces. Returns None on failure.
    """
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Find the first top-level {...} block (greedy).
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return None


def _validate_schema(parsed: Dict[str, Any], required_keys: Sequence[str]) -> bool:
    """Return True if every required key is present at top-level
    in the parsed reply. Deliberately shallow — we trust the
    per-caller aggregator to validate deeper structure.
    """
    for key in required_keys:
        if key not in parsed:
            return False
    return True


# ---------------------------------------------------------------------------
# AIConsensusBoard — the general-purpose board
# ---------------------------------------------------------------------------


class AIConsensusBoard:
    """Context-managed general-purpose consensus querier.

    Usage:

        with AIConsensusBoard() as board:
            result = board.query(
                query_id="phase_12_design_review",
                system_instructions="You are a senior reviewer...",
                user_message="<full design doc>",
                required_keys=("verdict", "concerns"),
            )
            # result.consensus is set if ≥2 models parsed cleanly
            # and agree on the top-level `verdict` value.

    The board fetches keys at `__enter__` time and clears them at
    `__exit__` time. Mid-session re-queries are allowed and reuse
    the cached keys.
    """

    def __init__(self, include_grok: bool = False):
        self._keys: Optional[ReviewBoardKeys] = None
        self._include_grok = include_grok

    def __enter__(self) -> "AIConsensusBoard":
        opt = ("grok",) if self._include_grok else ()
        self._keys = ReviewBoardKeys.load(include_optional=opt)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._keys = None

    def query(
        self,
        query_id: str,
        system_instructions: str,
        user_message: str,
        required_keys: Sequence[str] = (),
        verdict_aggregator: Optional[Callable[[List[Dict[str, Any]]], Optional[Dict[str, Any]]]] = None,
    ) -> ConsensusResult:
        """Send the same prompt to all three models and aggregate.

        Parameters
        ----------
        query_id
            Stable identifier for this query. Used in logs and
            ledger entries.
        system_instructions
            The persona / task description; prepended to each
            model's request in that model's native system slot.
        user_message
            The actual question or payload. Kept separate so the
            system instructions can be reused across related
            queries.
        required_keys
            Keys the model's JSON reply MUST contain at top-level
            for the response to count as "schema ok". A reply
            missing a required key is recorded but flagged.
        verdict_aggregator
            Optional callable that takes the list of
            successfully-parsed replies and returns a merged
            consensus dict (or None if consensus fails). If not
            provided, the default aggregator is used: return the
            most common value of the `verdict` key if present.
        """
        if self._keys is None:
            raise RuntimeError(
                "AIConsensusBoard.query() called outside a `with` block; "
                "keys have not been loaded."
            )

        responses: List[ConsensusResponse] = []
        for reviewer, fn, key in (
            ("claude-opus-4-6", _call_claude, self._keys.anthropic),
            ("openai-gpt-5", _call_openai, self._keys.openai),
            ("gemini-2.5-pro", _call_gemini, self._keys.gemini),
        ):
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                raw = fn(key, user_message, system_override=system_instructions)
            except AIBoardAPIError as exc:
                msg = _redact_key(str(exc))
                responses.append(ConsensusResponse(
                    reviewer=reviewer,
                    parsed=None,
                    raw_response=f"AIBoardAPIError: {msg}",
                    timestamp=ts,
                    error=msg,
                ))
                continue
            except Exception as exc:
                responses.append(ConsensusResponse(
                    reviewer=reviewer,
                    parsed=None,
                    raw_response=f"{type(exc).__name__}: {_redact_key(str(exc))}",
                    timestamp=ts,
                    error=_redact_key(str(exc)),
                ))
                continue

            parsed = _parse_json_response(raw)
            responses.append(ConsensusResponse(
                reviewer=reviewer,
                parsed=parsed,
                raw_response=raw,
                timestamp=ts,
            ))

        parsed_replies = [r.parsed for r in responses if r.parsed is not None]
        agreement = len(parsed_replies) / len(responses) if responses else 0.0

        schema_ok_count = sum(
            1 for p in parsed_replies
            if _validate_schema(p, required_keys)
        ) if required_keys else len(parsed_replies)
        schema_ok = schema_ok_count / len(responses) if responses else 0.0

        consensus: Optional[Dict[str, Any]] = None
        if verdict_aggregator is not None:
            try:
                consensus = verdict_aggregator(parsed_replies)
            except Exception as exc:
                consensus = {"aggregator_error": str(exc)}
        elif parsed_replies:
            consensus = _default_verdict_aggregator(parsed_replies)

        return ConsensusResult(
            query_id=query_id,
            responses=responses,
            agreement=agreement,
            schema_ok=schema_ok,
            consensus=consensus,
        )

    def four_phase_query(
        self,
        query_id: str,
        review_subject: str,
        user_payload: str,
        rubric_schema: Dict[str, str],
        personas: Dict[str, str],
    ) -> "FourPhaseResult":
        """Run the academic-style 4-phase review protocol.

        Phase A — independent drafts with specialist personas + COI
        Phase B — informed votes after seeing each other's reports
        Phase C — editor synthesis (4th distinct model call)
        Phase D — (optional, not implemented for design reviews —
                   bounded rebuttal cycle for submitter revisions)

        `review_subject` is a short descriptor like
        "a design document for a cross-domain equation coupling
         engine" — it gets interpolated into reviewer personas.

        `user_payload` is the actual content under review (the
        design doc summary, the coupling hypothesis, etc.).

        `rubric_schema` is a {dimension_name: description} dict.
        The reviewers fill it with 1-5 scores.

        `personas` maps reviewer name → persona string. Missing
        reviewers fall back to the stock ones in
        DESIGN_REVIEW_PERSONAS.
        """
        if self._keys is None:
            raise RuntimeError(
                "AIConsensusBoard.four_phase_query() called outside a "
                "`with` block; keys have not been loaded."
            )

        # Determine which reviewers are in play.
        reviewer_triples: List[tuple[str, Any, str]] = [
            ("claude-opus-4-6", _call_claude, self._keys.anthropic),
            ("openai-gpt-5", _call_openai, self._keys.openai),
            ("gemini-2.5-pro", _call_gemini, self._keys.gemini),
        ]
        if self._include_grok and self._keys.grok:
            reviewer_triples.append(
                ("grok-4", _call_grok, self._keys.grok)
            )

        # ---- Phase A ----
        phase_a: List[PhaseAReply] = []
        for reviewer, fn, key in reviewer_triples:
            persona = personas.get(reviewer) or DESIGN_REVIEW_PERSONAS.get(reviewer, "")
            prompt = _build_phase_a_prompt(
                persona, rubric_schema, review_subject, user_payload,
            )
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                raw = fn(key, prompt, system_override=(
                    f"{persona}\n\nYou are in Phase A of a 4-phase "
                    f"review board. Produce only JSON."
                ))
            except Exception as exc:
                phase_a.append(PhaseAReply(
                    reviewer=reviewer, persona=persona,
                    coi_declared=False, coi_note="",
                    rubric=RubricScore(dimension_scores={}, total=0.0),
                    verdict="error", headline="(Phase A failed)",
                    strengths=[], concerns=[], required_modifications=[],
                    raw_response=_redact_key(str(exc)),
                    timestamp=ts, error=_redact_key(str(exc)),
                ))
                continue
            parsed = _parse_json_response(raw) or {}
            coi = parsed.get("coi") or {}
            phase_a.append(PhaseAReply(
                reviewer=reviewer, persona=persona,
                coi_declared=bool(coi.get("encountered_during_training")),
                coi_note=str(coi.get("specific_note", "")),
                rubric=RubricScore.from_dict(parsed.get("rubric")),
                verdict=str(parsed.get("verdict", "error")).lower().strip(),
                headline=str(parsed.get("headline", ""))[:500],
                strengths=list(parsed.get("strengths") or [])[:10],
                concerns=list(parsed.get("concerns") or [])[:10],
                required_modifications=list(
                    parsed.get("required_modifications") or []
                )[:10],
                raw_response=raw,
                timestamp=ts,
                error=None if parsed else "Failed to parse JSON",
            ))

        # ---- Build consolidation briefing ----
        briefing = _build_briefing(phase_a)

        # ---- Phase B ----
        phase_b: List[PhaseBReply] = []
        for reviewer, fn, key in reviewer_triples:
            persona = personas.get(reviewer) or DESIGN_REVIEW_PERSONAS.get(reviewer, "")
            prompt = _build_phase_b_prompt(
                persona, rubric_schema, review_subject, user_payload,
                briefing,
            )
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                raw = fn(key, prompt, system_override=(
                    f"{persona}\n\nYou are in Phase B of a 4-phase "
                    f"review board. Produce only JSON."
                ))
            except Exception as exc:
                phase_b.append(PhaseBReply(
                    reviewer=reviewer,
                    updated_verdict="error",
                    updated_rubric=RubricScore(dimension_scores={}, total=0.0),
                    position_change="unknown",
                    response_to_peers="(Phase B failed)",
                    headline="", raw_response=_redact_key(str(exc)),
                    timestamp=ts, error=_redact_key(str(exc)),
                ))
                continue
            parsed = _parse_json_response(raw) or {}
            phase_b.append(PhaseBReply(
                reviewer=reviewer,
                updated_verdict=str(parsed.get("updated_verdict", "error")).lower().strip(),
                updated_rubric=RubricScore.from_dict(parsed.get("updated_rubric")),
                position_change=str(parsed.get("position_change", "unknown")).lower().strip(),
                response_to_peers=str(parsed.get("response_to_peers", ""))[:2000],
                headline=str(parsed.get("headline", ""))[:500],
                raw_response=raw,
                timestamp=ts,
                error=None if parsed else "Failed to parse JSON",
            ))

        # ---- Phase C: editor synthesis ----
        editor_prompt = _build_editor_prompt(
            review_subject, user_payload, briefing, phase_b,
        )
        editor_persona = (
            "You are the editor of a rigorous scientific-software "
            "architecture board. You weight reasoning quality, not "
            "vote count. You override naive tallies when one "
            "reviewer's argument is visibly stronger. You explicitly "
            "resolve reviewer disagreement."
        )
        ts = datetime.now(tz=timezone.utc).isoformat()
        try:
            raw = _call_claude(
                self._keys.anthropic, editor_prompt,
                system_override=(
                    f"{editor_persona}\n\nYou are in Phase C (editor) "
                    f"of a 4-phase review board. Produce only JSON."
                ),
            )
            parsed = _parse_json_response(raw) or {}
            editor = EditorDecision(
                verdict=str(parsed.get("verdict", "error")).lower().strip(),
                rationale=str(parsed.get("rationale", ""))[:4000],
                required_modifications=list(
                    parsed.get("required_modifications") or []
                )[:20],
                reviewer_disagreement_flagged=bool(
                    parsed.get("reviewer_disagreement_flagged", False)
                ),
                raw_response=raw,
                timestamp=ts,
                error=None if parsed else "Failed to parse JSON",
            )
        except Exception as exc:
            editor = EditorDecision(
                verdict="error", rationale="(editor call failed)",
                required_modifications=[],
                reviewer_disagreement_flagged=False,
                raw_response=_redact_key(str(exc)),
                timestamp=ts, error=_redact_key(str(exc)),
            )

        non_responders_a = [r.reviewer for r in phase_a if r.error is not None]
        non_responders_b = [r.reviewer for r in phase_b if r.error is not None]
        all_responded_a = len(non_responders_a) == 0
        all_responded_b = len(non_responders_b) == 0

        # v4 enforcement: if any reviewer failed in either phase,
        # override editor verdict to `escalate` and record the
        # specific non-responders for the user.
        if not (all_responded_a and all_responded_b):
            non_responders_all = sorted(set(non_responders_a + non_responders_b))
            escalation = (
                f"Non-response from {len(non_responders_all)} reviewer(s): "
                f"{', '.join(non_responders_all)}. Per v4 'all must respond' "
                f"rule, non-response counts as dissent. The gate is NOT met. "
                f"Escalating to user."
            )
            editor = EditorDecision(
                verdict="escalate",
                rationale=escalation + (
                    "\n\n---\n\nOriginal editor synthesis (still recorded):\n\n"
                    + editor.rationale if editor.rationale else ""
                ),
                required_modifications=editor.required_modifications,
                reviewer_disagreement_flagged=editor.reviewer_disagreement_flagged,
                raw_response=editor.raw_response,
                timestamp=editor.timestamp,
                error=editor.error,
            )

        return FourPhaseResult(
            query_id=query_id,
            phase_a=phase_a,
            consolidation_briefing=briefing,
            phase_b=phase_b,
            editor=editor,
            include_grok=self._include_grok,
            all_responded_a=all_responded_a,
            all_responded_b=all_responded_b,
            non_responders_a=non_responders_a,
            non_responders_b=non_responders_b,
        )

    def discharge_round(
        self,
        query_id: str,
        round_number: int,
        review_subject: str,
        fcs: List[FrozenConcern],
        original_submission: str,
        submitter_revision: str,
        submitter_revision_summary: str,
        personas: Dict[str, str],
    ) -> "DischargeResult":
        """Scope-frozen Round 2+ discharge review.

        Critical invariant: **reviewers cannot raise new concerns**.
        They may only evaluate each concern in the FCS as
        addressed / partially_addressed / not_addressed and
        justify their assessment. Any attempt to introduce a new
        concern is recorded as a process_violation and escalated
        to the user.

        This is the formal-verification pattern: the FCS is the
        proof obligation list, and each round discharges
        obligations from it. Obligations cannot be added mid-
        proof.
        """
        if self._keys is None:
            raise RuntimeError(
                "discharge_round() called outside a `with` block."
            )

        reviewer_triples: List[tuple[str, Any, str]] = [
            ("claude-opus-4-6", _call_claude, self._keys.anthropic),
            ("openai-gpt-5", _call_openai, self._keys.openai),
            ("gemini-2.5-pro", _call_gemini, self._keys.gemini),
        ]
        if self._include_grok and self._keys.grok:
            reviewer_triples.append(
                ("grok-4", _call_grok, self._keys.grok)
            )

        # Build the FCS text
        fcs_text_lines = ["## Frozen Concern Set (FCS)\n"]
        for c in fcs:
            raised = ", ".join(c.raised_by)
            fcs_text_lines.append(
                f"**{c.concern_id}** (severity: {c.severity}; "
                f"originally raised by: {raised})\n"
                f"{c.headline}\n\n{c.detail}\n"
            )
        fcs_text = "\n".join(fcs_text_lines)

        # Run the discharge query on each reviewer
        replies: List[DischargeReply] = []
        for reviewer, fn, key in reviewer_triples:
            persona = personas.get(reviewer) or DESIGN_REVIEW_PERSONAS.get(reviewer, "")
            prompt = _build_discharge_prompt(
                persona, review_subject, fcs, original_submission,
                submitter_revision, submitter_revision_summary,
                round_number,
            )
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                raw = fn(key, prompt, system_override=(
                    f"{persona}\n\nYou are in Round {round_number} "
                    f"(DISCHARGE mode) of a formal scope-frozen "
                    f"review. You may not raise new concerns. "
                    f"Produce only JSON."
                ))
            except Exception as exc:
                replies.append(DischargeReply(
                    reviewer=reviewer, persona=persona, scores=[],
                    overall_verdict="error", headline="(discharge failed)",
                    new_concerns_attempted=0,
                    raw_response=_redact_key(str(exc)),
                    timestamp=ts, error=_redact_key(str(exc)),
                ))
                continue
            parsed = _parse_json_response(raw) or {}
            score_list = []
            for s in (parsed.get("discharge_scores") or []):
                if not isinstance(s, dict):
                    continue
                score_list.append(DischargeScore(
                    concern_id=str(s.get("concern_id", "")),
                    status=str(s.get("status", "not_addressed")).lower().strip(),
                    justification=str(s.get("justification", ""))[:2000],
                ))
            replies.append(DischargeReply(
                reviewer=reviewer, persona=persona,
                scores=score_list,
                overall_verdict=str(parsed.get("overall_verdict", "error")).lower().strip(),
                headline=str(parsed.get("headline", ""))[:500],
                new_concerns_attempted=int(parsed.get("new_concerns_attempted") or 0),
                raw_response=raw,
                timestamp=ts,
                error=None if parsed else "Failed to parse JSON",
            ))

        # Aggregate: which concerns are still unresolved?
        unresolved: List[str] = []
        for concern in fcs:
            statuses = [
                s.status for r in replies for s in r.scores
                if s.concern_id == concern.concern_id
            ]
            if not statuses:
                unresolved.append(concern.concern_id)
                continue
            # A concern is resolved iff ≥2 reviewers marked it
            # "addressed" (and none marked it "not_addressed")
            addressed = sum(1 for s in statuses if s == "addressed")
            not_addressed = sum(1 for s in statuses if s == "not_addressed")
            if addressed >= 2 and not_addressed == 0:
                continue
            unresolved.append(concern.concern_id)

        process_violations: List[str] = []
        for r in replies:
            if r.new_concerns_attempted > 0:
                process_violations.append(
                    f"{r.reviewer} attempted to raise "
                    f"{r.new_concerns_attempted} new concern(s) — "
                    f"out-of-scope in discharge mode"
                )

        # v4: Non-response = dissent. Compute all_responded and
        # build the non_responders list. If any reviewer failed,
        # the round cannot approve regardless of substantive
        # verdicts from the responders.
        non_responders = [r.reviewer for r in replies if r.error is not None]
        all_responded = len(non_responders) == 0

        # Editor synthesis of the discharge result
        editor_prompt = _build_discharge_editor_prompt(
            review_subject, fcs, original_submission,
            submitter_revision, replies, unresolved, process_violations,
            round_number,
        )
        editor_persona = (
            "You are the editor of a formal scope-frozen review "
            "board. A prior Round 1 produced a Frozen Concern Set "
            "(FCS). This Round is DISCHARGE: reviewers can only "
            "evaluate whether each FCS concern has been addressed. "
            "They cannot add new concerns. You must decide "
            "whether the submission now APPROVES (all high-severity "
            "concerns addressed, no reviewer blocks), MODIFIES "
            "(specific concerns still open), or escalates to the "
            "user with a Decision Matrix (reviewers fundamentally "
            "disagree after exhausting rounds)."
        )
        ts = datetime.now(tz=timezone.utc).isoformat()
        editor_verdict = "error"
        editor_rationale = ""
        decision_matrix_needed = False
        decision_matrix_options: Optional[List[Dict[str, Any]]] = None
        try:
            raw = _call_claude(
                self._keys.anthropic, editor_prompt,
                system_override=(
                    f"{editor_persona}\n\nProduce only JSON."
                ),
            )
            parsed = _parse_json_response(raw) or {}
            editor_verdict = str(parsed.get("verdict", "error")).lower().strip()
            editor_rationale = str(parsed.get("rationale", ""))[:4000]
            decision_matrix_needed = bool(
                parsed.get("escalate_to_user", False)
            )
            decision_matrix_options = parsed.get("decision_matrix_options")
        except Exception as exc:
            editor_verdict = "error"
            editor_rationale = f"(editor call failed: {_redact_key(str(exc))})"

        # v4 all-must-respond enforcement: if ANY reviewer
        # failed to produce a parseable reply, override the
        # editor's verdict to 'escalate' regardless of what the
        # responders said. The user is the only authority that
        # can accept a partial-quorum result.
        if not all_responded:
            escalation_reason = (
                f"non-response from {len(non_responders)} reviewer(s): "
                f"{', '.join(non_responders)}. "
                f"Per v4 'all must respond' rule, non-response counts "
                f"as dissent. The round cannot APPROVE with partial "
                f"quorum. Escalating to user for decision: retry the "
                f"failed reviewer(s), substitute, or proceed with "
                f"acknowledged risk."
            )
            editor_verdict = "escalate"
            if editor_rationale:
                editor_rationale = escalation_reason + "\n\n---\n\n" + editor_rationale
            else:
                editor_rationale = escalation_reason
            decision_matrix_needed = True
            if not decision_matrix_options:
                decision_matrix_options = [
                    {"option": "A", "name": "Retry failed reviewers",
                     "effect": "Re-run the board with exponential backoff on the non-responding reviewer(s)",
                     "residual_risk": "Vendor may still be unavailable; could loop"},
                    {"option": "B", "name": "Proceed with acknowledged dissent",
                     "effect": "Accept the partial-quorum verdict, ledger-record non-response as dissent",
                     "residual_risk": "Weaker evidence chain; one reviewer's perspective is missing from the record"},
                    {"option": "C", "name": "Wait for vendor",
                     "effect": "Pause the sprint, reschedule the round for a later time when the failing vendor recovers",
                     "residual_risk": "Sprint latency, but no rigor loss"},
                ]

        return DischargeResult(
            query_id=query_id,
            round_number=round_number,
            fcs=fcs,
            submitter_revision_summary=submitter_revision_summary,
            replies=replies,
            editor_verdict=editor_verdict,
            editor_rationale=editor_rationale,
            unresolved_concerns=unresolved,
            process_violations=process_violations,
            decision_matrix_needed=decision_matrix_needed,
            decision_matrix_options=decision_matrix_options,
            all_responded=all_responded,
            non_responders=non_responders,
        )

    @staticmethod
    def _wrap_system_into_user(system: str, user: str, reviewer: str) -> str:
        """Fold the system instructions into the user message.

        Reason: the underlying `_call_claude`, `_call_openai`, and
        `_call_gemini` helpers in `ai_review_board.py` already
        stamp a FIXED system instruction (the coupling-review
        persona). Passing a different system message would
        require extending those helpers with a system parameter.
        For simplicity in Phase 12, the general-consensus queries
        prepend the new system instructions to the user message
        and accept that the model sees both the coupling-review
        system prompt AND the Phase 12 instructions. The Phase 12
        instructions are clearly scoped so this doesn't confuse
        the models in practice.

        If this limitation becomes a problem, the long-term fix
        is to add a `system_override` parameter to each adapter
        and wire it through. Not in tonight's scope.
        """
        return (
            "[IMPORTANT: override any earlier persona. For this message, "
            "use the following instructions instead.]\n\n"
            f"{system}\n\n---\n\n{user}"
        )


def _default_verdict_aggregator(
    parsed_replies: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Default: return the most common `verdict` value across
    the parsed replies. If no `verdict` key is present, return
    the first reply's full dict as the consensus.
    """
    if not parsed_replies:
        return None
    verdicts = [
        str(r.get("verdict", "")).strip().lower()
        for r in parsed_replies
        if "verdict" in r
    ]
    if verdicts:
        counts: Dict[str, int] = {}
        for v in verdicts:
            counts[v] = counts.get(v, 0) + 1
        top = max(counts.items(), key=lambda x: x[1])
        return {
            "top_verdict": top[0],
            "top_verdict_count": top[1],
            "total_parsed": len(parsed_replies),
            "all_verdicts": verdicts,
        }
    return {
        "top_verdict": None,
        "total_parsed": len(parsed_replies),
        "note": "No `verdict` key in any reply",
    }


# ---------------------------------------------------------------------------
# Specialised aggregators — authored by caller, passed into .query()
# ---------------------------------------------------------------------------


@dataclass
class RubricScore:
    """Five-dimension structured score 1-5 produced by each
    reviewer in Phase A and Phase B. Keys are review-type-
    specific (design vs coupling); the reviewer's rubric
    schema is included in the prompt.
    """
    dimension_scores: Dict[str, int]       # {name: 1..5}
    total: float                           # weighted sum

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RubricScore":
        raw = d or {}
        scores: Dict[str, int] = {}
        for k, v in raw.items():
            if k == "total":
                continue
            try:
                scores[k] = max(1, min(5, int(v)))
            except (TypeError, ValueError):
                scores[k] = 1
        total = sum(scores.values()) / len(scores) if scores else 0.0
        return cls(dimension_scores=scores, total=total)


@dataclass
class PhaseAReply:
    """One reviewer's Phase A (independent draft) reply."""
    reviewer: str
    persona: str
    coi_declared: bool
    coi_note: str
    rubric: RubricScore
    verdict: str                           # approve/modify/reject
    headline: str
    strengths: List[str]
    concerns: List[str]
    required_modifications: List[str]
    raw_response: str
    timestamp: str
    error: Optional[str] = None


@dataclass
class PhaseBReply:
    """One reviewer's Phase B (informed, post-briefing) reply."""
    reviewer: str
    updated_verdict: str
    updated_rubric: RubricScore
    position_change: str                   # "unchanged"/"strengthened"/"moderated"
    response_to_peers: str                 # how this reviewer reacted to the briefing
    headline: str
    raw_response: str
    timestamp: str
    error: Optional[str] = None


@dataclass
class EditorDecision:
    """Phase C — editor synthesis."""
    verdict: str                           # binding verdict
    rationale: str
    required_modifications: List[str]
    reviewer_disagreement_flagged: bool
    raw_response: str
    timestamp: str
    error: Optional[str] = None


@dataclass
class FrozenConcern:
    """One concern in a Frozen Concern Set (FCS).

    Produced by the editor at the end of Round 1 (discovery).
    Immutable thereafter — Round 2+ (discharge) can only EVALUATE
    concerns in the FCS, never add new ones.
    """
    concern_id: str                        # e.g. "C1", "C2"
    headline: str                          # one-line summary
    raised_by: List[str]                   # reviewers who raised it in Round 1
    severity: str                          # "high" | "medium" | "low"
    detail: str                            # full description


@dataclass
class DischargeScore:
    """One reviewer's discharge assessment of one concern in
    the FCS during a scope-frozen Round 2+ review."""
    concern_id: str
    status: str                            # "addressed" | "partially_addressed" | "not_addressed"
    justification: str                     # why this status

    def as_dict(self) -> Dict[str, Any]:
        return {
            "concern_id": self.concern_id,
            "status": self.status,
            "justification": self.justification,
        }


@dataclass
class DischargeReply:
    """One reviewer's complete discharge report on the FCS.

    The reply is structurally constrained: the reviewer cannot
    raise new concerns. Any `new_concerns_attempted` > 0 triggers
    editor escalation to the user as a process violation.
    """
    reviewer: str
    persona: str
    scores: List[DischargeScore]
    overall_verdict: str                   # "approve" | "modify" | "reject"
    headline: str
    new_concerns_attempted: int            # should be 0; if >0, process violation
    raw_response: str
    timestamp: str
    error: Optional[str] = None


@dataclass
class DischargeResult:
    """Result of one Round 2+ scope-frozen discharge review."""
    query_id: str
    round_number: int                      # 2, 3, ... (Round 1 was Discovery)
    fcs: List[FrozenConcern]               # the frozen concern set under review
    submitter_revision_summary: str        # what the submitter claims to have changed
    replies: List[DischargeReply]
    editor_verdict: str                    # "approve" | "modify" | "reject" | "escalate_to_user"
    editor_rationale: str
    unresolved_concerns: List[str]         # concern_ids still open
    process_violations: List[str]          # e.g. "Grok attempted to raise new concern X"
    decision_matrix_needed: bool           # True → escalate to user
    decision_matrix_options: Optional[List[Dict[str, Any]]] = None
    all_responded: bool = False            # v4: non-response = dissent. True iff
                                           # every reviewer produced a parseable reply.
    non_responders: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "round_number": self.round_number,
            "fcs_ids": [c.concern_id for c in self.fcs],
            "submitter_revision_summary": self.submitter_revision_summary,
            "replies": [
                {
                    "reviewer": r.reviewer,
                    "overall_verdict": r.overall_verdict,
                    "headline": r.headline,
                    "scores": [s.as_dict() for s in r.scores],
                    "new_concerns_attempted": r.new_concerns_attempted,
                    "error": r.error,
                    "timestamp": r.timestamp,
                }
                for r in self.replies
            ],
            "editor_verdict": self.editor_verdict,
            "editor_rationale": self.editor_rationale,
            "unresolved_concerns": self.unresolved_concerns,
            "process_violations": self.process_violations,
            "decision_matrix_needed": self.decision_matrix_needed,
            "decision_matrix_options": self.decision_matrix_options,
        }


@dataclass
class FourPhaseResult:
    query_id: str
    phase_a: List[PhaseAReply]
    consolidation_briefing: str
    phase_b: List[PhaseBReply]
    editor: EditorDecision
    rebuttal_cycles: List[Dict[str, Any]] = field(default_factory=list)
    include_grok: bool = False
    all_responded_a: bool = False           # v4: Phase A all-respond check
    all_responded_b: bool = False           # v4: Phase B all-respond check
    non_responders_a: List[str] = field(default_factory=list)
    non_responders_b: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "include_grok": self.include_grok,
            "phase_a": [
                {
                    "reviewer": r.reviewer,
                    "persona": r.persona,
                    "coi_declared": r.coi_declared,
                    "coi_note": r.coi_note,
                    "rubric": r.rubric.dimension_scores,
                    "rubric_total": r.rubric.total,
                    "verdict": r.verdict,
                    "headline": r.headline,
                    "strengths": r.strengths,
                    "concerns": r.concerns,
                    "required_modifications": r.required_modifications,
                    "error": r.error,
                    "timestamp": r.timestamp,
                }
                for r in self.phase_a
            ],
            "consolidation_briefing": self.consolidation_briefing[:4000],
            "phase_b": [
                {
                    "reviewer": r.reviewer,
                    "updated_verdict": r.updated_verdict,
                    "updated_rubric": r.updated_rubric.dimension_scores,
                    "updated_rubric_total": r.updated_rubric.total,
                    "position_change": r.position_change,
                    "response_to_peers": r.response_to_peers,
                    "headline": r.headline,
                    "error": r.error,
                    "timestamp": r.timestamp,
                }
                for r in self.phase_b
            ],
            "editor": {
                "verdict": self.editor.verdict,
                "rationale": self.editor.rationale,
                "required_modifications": self.editor.required_modifications,
                "reviewer_disagreement_flagged": self.editor.reviewer_disagreement_flagged,
                "error": self.editor.error,
                "timestamp": self.editor.timestamp,
            },
            "rebuttal_cycles": self.rebuttal_cycles,
        }

    def gate_met(self, rule: str = "editor") -> bool:
        """Evaluate the approval gate.

        **v4 all-must-respond rule**: regardless of `rule`, the
        gate is NEVER met if any Phase A or Phase B reviewer
        failed to produce a parseable reply. Non-response counts
        as dissent.
        """
        if not self.all_responded_a or not self.all_responded_b:
            return False
        if rule == "editor":
            return self.editor.verdict == "approve"
        verdicts = [r.updated_verdict for r in self.phase_b if r.error is None]
        if not verdicts:
            return False
        approves = sum(1 for v in verdicts if v == "approve")
        if rule == "unanimous":
            return approves == len(verdicts)
        if rule == "2_of_n":
            return approves >= 2
        return False


# Cost-neutrality disclaimer (v3 §11a.5, user-directed).
#
# Every Phase A, Phase B, and editor prompt prepends this block
# so reviewers cannot penalise a submission for being ambitious,
# requiring "significant preparatory work," or representing a
# "paradigm shift that would take effort to implement." Those
# are not valid technical concerns. The human project owner has
# explicitly declared that time, effort, and engineering
# capacity are NOT constraints on the architecture.
#
# Reviewers that cite cost / schedule / effort as a reason to
# prefer a narrower or less-rigorous option are operating
# outside the bounds of their review authority. The editor is
# instructed to discount such reasoning in Phase C synthesis.
COST_NEUTRALITY_DISCLAIMER = """\
IMPORTANT — COST NEUTRALITY. Before you evaluate the submission
below, note that the project owner has explicitly declared that
**time, effort, implementation cost, and engineering capacity
are NOT constraints** on this architecture. You are forbidden
from using any of the following as reasons to prefer one option
over another or to recommend a narrower scope:

- "This would require significant preparatory work"
- "This is a paradigm shift that would take effort to implement"
- "This would delay shipping"
- "A simpler approach would be faster to build"
- "The scope is ambitious"
- "This is a lot of engineering work"
- "The human-in-the-loop cost is high"
- Any implicit framing in which 'doing less' is inherently better

Evaluate the submission on **technical merit alone**: correctness,
soundness, honesty of claims, rigor, falsifiability, prior-art
awareness, and whether the proposed mechanism is in principle
buildable and verifiable. If a design is ambitious but sound,
that is APPROVE-worthy. If a design is cheap but wrong, that
is REJECT-worthy. Cheap-and-wrong is never better than
ambitious-and-correct under this rubric.

If you find yourself wanting to cite effort, schedule, or
resource cost in your reasoning, stop and rewrite the reasoning
around the underlying technical question it is standing in for.
Often the technical question is "is this mechanism actually
needed?" — answer THAT question directly instead of hiding
behind cost.

---

"""


# Design-doc review rubric (v3 §11a.1)
DESIGN_RUBRIC_SCHEMA = {
    "thesis_soundness": "Is the core argument correct and novel?",
    "technical_feasibility": "Is the proposed mechanism buildable and sound?",
    "falsifiability": "Can the system be proven wrong? Are tests specified?",
    "prior_art_awareness": "Does it engage with existing work honestly?",
    "honest_scope": "Is it honest about what it can and cannot do?",
}

# Specialist personas for design-doc review (v3 §11a.2)
DESIGN_REVIEW_PERSONAS = {
    "claude-opus-4-6": (
        "You are a senior scientific-software architect with 20 "
        "years building research infrastructure at scale. You "
        "have shipped systems, seen every kind of failure, and "
        "know the difference between an elegant design and one "
        "that will survive contact with reality."
    ),
    "openai-gpt-5": (
        "You are a senior researcher in symbolic AI, formal "
        "methods, and equation discovery. You have published "
        "on the limitations of SINDy, PySR, and related "
        "symbolic-regression approaches, and you know where "
        "the hard problems actually live."
    ),
    "gemini-2.5-pro": (
        "You are a senior physicist with cross-domain modelling "
        "expertise. You have implemented bond-graph and port-"
        "Hamiltonian systems and you know which analogies are "
        "textbook and which are wishful thinking."
    ),
    "grok-4": (
        "You are a senior independent reviewer with a "
        "first-principles physics background, a strong bias "
        "toward falsifiability, and a habit of pushing back "
        "when claims exceed what the evidence supports."
    ),
}


def _build_phase_a_prompt(
    persona: str,
    rubric_schema: Dict[str, str],
    review_subject: str,
    user_payload: str,
) -> str:
    rubric_desc = "\n".join(f"- `{k}`: {v}" for k, v in rubric_schema.items())
    return (
        f"{COST_NEUTRALITY_DISCLAIMER}"
        f"{persona}\n\n"
        f"You are reviewing {review_subject} on a four-phase board. "
        f"This is PHASE A — your independent draft. You have NOT "
        f"seen the other reviewers' positions and must produce your "
        f"own unaided judgment.\n\n"
        f"Reply ONLY with a JSON object. No preamble, no fences, no "
        f"trailing text. Schema:\n\n"
        "{\n"
        '  "coi": {"encountered_during_training": true|false, "specific_note": "<free text>"},\n'
        '  "rubric": {\n'
        + "".join(f'    "{k}": <1-5 integer>,\n' for k in rubric_schema) +
        '  },\n'
        '  "verdict": "approve" | "modify" | "reject",\n'
        '  "headline": "<one sentence>",\n'
        '  "strengths": ["...", "..."],\n'
        '  "concerns": ["...", "..."],\n'
        '  "required_modifications": ["...", "..."]\n'
        "}\n\n"
        f"Rubric dimensions (score 1=reject, 5=excellent):\n"
        f"{rubric_desc}\n\n"
        "Be direct. If the submission is flawed, REJECT. If it needs "
        "changes, MODIFY with specifics. If it's sound, APPROVE.\n\n"
        "---\n\n"
        f"{user_payload}"
    )


def _build_briefing(phase_a: List[PhaseAReply]) -> str:
    """Consolidate 3-4 Phase A drafts into a single briefing doc
    for Phase B."""
    lines: List[str] = []
    lines.append("# Board briefing — Phase A reports\n")
    lines.append(
        "The following reports were produced INDEPENDENTLY by each "
        "reviewer in Phase A. You are now in Phase B: please review "
        "the other reviewers' positions and submit your FINAL "
        "verdict, explicitly addressing their concerns.\n"
    )
    for r in phase_a:
        lines.append(f"## Reviewer: {r.reviewer}\n")
        lines.append(f"**Persona:** {r.persona[:200]}\n")
        if r.error:
            lines.append(f"**Status:** PHASE A FAILED ({r.error})\n")
            continue
        coi_mark = (
            f"⚠ Training exposure declared: {r.coi_note}"
            if r.coi_declared else "no COI"
        )
        lines.append(f"**COI:** {coi_mark}\n")
        lines.append(f"**Rubric totals:** {r.rubric.dimension_scores} "
                     f"(mean {r.rubric.total:.2f})\n")
        lines.append(f"**Verdict:** `{r.verdict}` — {r.headline}\n")
        if r.strengths:
            lines.append("**Strengths:**")
            for s in r.strengths[:5]:
                lines.append(f"- {s}")
            lines.append("")
        if r.concerns:
            lines.append("**Concerns:**")
            for c in r.concerns[:5]:
                lines.append(f"- {c}")
            lines.append("")
        if r.required_modifications:
            lines.append("**Required modifications:**")
            for m in r.required_modifications[:5]:
                lines.append(f"- {m}")
            lines.append("")
    return "\n".join(lines)


def _build_phase_b_prompt(
    persona: str,
    rubric_schema: Dict[str, str],
    review_subject: str,
    user_payload: str,
    briefing: str,
) -> str:
    return (
        f"{COST_NEUTRALITY_DISCLAIMER}"
        f"{persona}\n\n"
        f"You are reviewing {review_subject} on a four-phase board. "
        f"This is PHASE B — the informed vote. You have now seen "
        f"the other reviewers' Phase A reports. Read them carefully, "
        f"then produce your UPDATED final verdict. If your position "
        f"is unchanged, say so. If a peer raised a concern that "
        f"persuades you, update. If a peer raised a concern you "
        f"disagree with, push back and explain why.\n\n"
        f"Reply ONLY with a JSON object:\n\n"
        "{\n"
        '  "updated_rubric": {\n'
        + "".join(f'    "{k}": <1-5 integer>,\n' for k in rubric_schema) +
        '  },\n'
        '  "updated_verdict": "approve" | "modify" | "reject",\n'
        '  "headline": "<one sentence>",\n'
        '  "position_change": "unchanged" | "strengthened" | "moderated",\n'
        '  "response_to_peers": "<how you reacted to each peer concern>"\n'
        "}\n\n"
        "---\n\n"
        f"## Original submission\n\n{user_payload}\n\n"
        f"---\n\n"
        f"## Board briefing (Phase A reports from your peers)\n\n{briefing}"
    )


def _build_editor_prompt(
    review_subject: str,
    user_payload: str,
    briefing: str,
    phase_b: List[PhaseBReply],
) -> str:
    b_lines: List[str] = []
    for r in phase_b:
        if r.error:
            b_lines.append(f"- {r.reviewer}: PHASE B FAILED ({r.error})")
            continue
        b_lines.append(
            f"- **{r.reviewer}** ({r.position_change}): "
            f"`{r.updated_verdict}` — {r.headline}  "
            f"(rubric mean {r.updated_rubric.total:.2f})"
        )
    b_summary = "\n".join(b_lines)
    return (
        f"{COST_NEUTRALITY_DISCLAIMER}"
        "You are the EDITOR of a scientific-software architecture "
        "board. Three reviewers (possibly four) have each produced "
        "a Phase A draft, seen each other's drafts, and submitted "
        "Phase B informed verdicts. Your job is to write the "
        "binding editorial decision.\n\n"
        "Weight the QUALITY of reviewer reasoning, not just the "
        "vote count. Override a naive tally if one reviewer's "
        "argument is visibly stronger. Explicitly resolve "
        "disagreements. If reviewers disagree on fundamentals, "
        "flag it.\n\n"
        "Reply ONLY with a JSON object:\n\n"
        "{\n"
        '  "verdict": "approve" | "modify" | "reject",\n'
        '  "rationale": "<paragraph explaining your decision>",\n'
        '  "required_modifications": ["...", "..."],\n'
        '  "reviewer_disagreement_flagged": true|false\n'
        "}\n\n"
        "---\n\n"
        f"## Submission under review\n\n{user_payload[:4000]}\n\n"
        "---\n\n"
        f"## Phase B verdicts summary\n\n{b_summary}\n\n"
        f"---\n\n"
        f"## Phase A briefing (full reports)\n\n{briefing[:6000]}"
    )


def _build_discharge_prompt(
    persona: str,
    review_subject: str,
    fcs: List[FrozenConcern],
    original_submission: str,
    submitter_revision: str,
    submitter_revision_summary: str,
    round_number: int,
) -> str:
    """Build the Round 2+ scope-frozen discharge prompt.

    Critical: the prompt explicitly forbids raising new concerns.
    The reviewer can only score the FCS items.
    """
    fcs_lines = []
    for c in fcs:
        raised = ", ".join(c.raised_by)
        fcs_lines.append(
            f"### {c.concern_id} — {c.headline}\n"
            f"- Severity: {c.severity}\n"
            f"- Originally raised by: {raised}\n"
            f"- Detail: {c.detail}\n"
        )
    fcs_text = "\n".join(fcs_lines)

    return (
        f"{COST_NEUTRALITY_DISCLAIMER}"
        f"{persona}\n\n"
        f"You are reviewing {review_subject}. This is "
        f"**Round {round_number} — DISCHARGE MODE**. A prior "
        f"Round 1 review produced a Frozen Concern Set (FCS) "
        f"below. The submitter has now revised the submission to "
        f"address those concerns. Your job is to score EACH "
        f"concern in the FCS as `addressed`, `partially_addressed`, "
        f"or `not_addressed`, with justification.\n\n"
        f"**CRITICAL RULE: You may NOT raise new concerns.** "
        f"The FCS is immutable. If you believe you have spotted "
        f"a new issue that is not in the FCS, do not include it "
        f"in your review. Instead, increment the "
        f"`new_concerns_attempted` counter in your reply. The "
        f"editor will escalate the fact that new concerns arose "
        f"to the human project owner, who is the only authority "
        f"that can reopen the FCS. Your role is discharge only.\n\n"
        f"**Your review produces a JSON object with this schema:**\n\n"
        "{\n"
        '  "discharge_scores": [\n'
        '    {\n'
        '      "concern_id": "<e.g., C1>",\n'
        '      "status": "addressed" | "partially_addressed" | "not_addressed",\n'
        '      "justification": "<short explanation — does the revision actually fix this concern?>"\n'
        '    },\n'
        '    ...\n'
        '  ],\n'
        '  "overall_verdict": "approve" | "modify" | "reject",\n'
        '  "headline": "<one sentence summary>",\n'
        '  "new_concerns_attempted": <integer count of new concerns you spotted but did not include, default 0>\n'
        "}\n\n"
        "---\n\n"
        f"## Frozen Concern Set\n\n{fcs_text}\n\n"
        "---\n\n"
        f"## Submitter's revision summary\n\n{submitter_revision_summary}\n\n"
        "---\n\n"
        f"## Original submission (Round 1)\n\n{original_submission}\n\n"
        "---\n\n"
        f"## Revised submission (Round {round_number})\n\n{submitter_revision}"
    )


def _build_discharge_editor_prompt(
    review_subject: str,
    fcs: List[FrozenConcern],
    original_submission: str,
    submitter_revision: str,
    replies: List["DischargeReply"],
    unresolved: List[str],
    process_violations: List[str],
    round_number: int,
) -> str:
    """Build the editor's Round 2+ synthesis prompt."""
    fcs_lines = []
    for c in fcs:
        fcs_lines.append(f"- **{c.concern_id}** ({c.severity}): {c.headline}")
    fcs_text = "\n".join(fcs_lines)

    reply_lines = []
    for r in replies:
        if r.error:
            reply_lines.append(
                f"### {r.reviewer}\n**Status:** DISCHARGE FAILED ({r.error})\n"
            )
            continue
        reply_lines.append(f"### {r.reviewer}\n")
        reply_lines.append(f"**Overall verdict:** `{r.overall_verdict}`  ")
        reply_lines.append(f"**Headline:** {r.headline}\n")
        if r.new_concerns_attempted > 0:
            reply_lines.append(
                f"**⚠ PROCESS VIOLATION:** attempted to raise "
                f"{r.new_concerns_attempted} new concern(s)\n"
            )
        for s in r.scores:
            reply_lines.append(
                f"- **{s.concern_id}** — `{s.status}`: {s.justification}"
            )
        reply_lines.append("")
    replies_text = "\n".join(reply_lines)

    unresolved_text = ", ".join(unresolved) if unresolved else "(none — all FCS concerns resolved)"
    violations_text = "\n".join(f"- {v}" for v in process_violations) if process_violations else "(none)"

    return (
        f"{COST_NEUTRALITY_DISCLAIMER}"
        f"You are the EDITOR of a formal scope-frozen review "
        f"board. This is Round {round_number} — DISCHARGE "
        f"synthesis. Reviewers evaluated each FCS item as "
        f"addressed/partially/not-addressed. Your job is to "
        f"decide the binding outcome.\n\n"
        f"Reply ONLY with a JSON object:\n\n"
        "{\n"
        '  "verdict": "approve" | "modify" | "reject" | "escalate",\n'
        '  "rationale": "<paragraph explaining your decision>",\n'
        '  "escalate_to_user": true|false,\n'
        '  "decision_matrix_options": [\n'
        '    {"option": "A", "name": "<short>", "effect": "<what happens>", "residual_risk": "<what we accept>"},\n'
        '    ...\n'
        '  ]\n'
        "}\n\n"
        "**Approve** if all high-severity FCS items are fully "
        "addressed AND no process violations occurred.\n"
        "**Modify** if some concerns remain partially addressed "
        "but convergence is plausible within one more round.\n"
        "**Reject** if the revision makes the submission worse "
        "or introduces a regression.\n"
        "**Escalate** if reviewers fundamentally disagree even "
        "after discharge, or if process_violations occurred and "
        "the new concerns warrant reopening the FCS (user-only "
        "authority).\n\n"
        "---\n\n"
        f"## FCS ({len(fcs)} concerns)\n\n{fcs_text}\n\n"
        f"## Unresolved after this round\n\n{unresolved_text}\n\n"
        f"## Process violations\n\n{violations_text}\n\n"
        f"## Reviewer discharge reports\n\n{replies_text}\n\n"
        "---\n\n"
        f"## Original submission (Round 1)\n\n{original_submission[:4000]}\n\n"
        f"---\n\n"
        f"## Revised submission (Round {round_number})\n\n{submitter_revision[:4000]}"
    )


def numerical_reference_aggregator(
    parsed_replies: List[Dict[str, Any]],
    *,
    field: str = "value",
    rel_tolerance: float = 0.01,
) -> Optional[Dict[str, Any]]:
    """Aggregator for reference-value queries. Accepts the
    numerical answer only if ≥2 models returned a number for
    `field` and they agree within `rel_tolerance` (relative).

    Used by Phase 12 when sourcing canonical problem reference
    values from the board. If Claude says the pendulum period
    is 2.006 s and OpenAI says 2.006 s, they agree and the
    value is accepted with `confidence=0.67` (2/3). If all three
    agree, confidence=1.0. If only one produces a number, no
    consensus and the caller must either author manually or
    re-query.
    """
    numerics: List[tuple[str, float]] = []
    for r in parsed_replies:
        val = r.get(field)
        if isinstance(val, (int, float)):
            numerics.append((r.get("reviewer", "unknown"), float(val)))
    if len(numerics) < 2:
        return {
            "agreed_value": None,
            "confidence": 0.0,
            "agreement_count": len(numerics),
            "note": f"only {len(numerics)} model(s) returned a numerical {field}",
        }
    # Pairwise agreement within relative tolerance.
    import math
    agreeing: List[float] = []
    for i, (_, vi) in enumerate(numerics):
        for j, (_, vj) in enumerate(numerics):
            if i >= j:
                continue
            if vi == 0 and vj == 0:
                agreeing.extend([vi, vj])
            elif max(abs(vi), abs(vj)) > 0 and abs(vi - vj) / max(abs(vi), abs(vj)) <= rel_tolerance:
                agreeing.extend([vi, vj])
    agreeing = list(dict.fromkeys(agreeing))  # dedup, preserve order
    if not agreeing:
        return {
            "agreed_value": None,
            "confidence": 0.0,
            "agreement_count": 0,
            "all_values": [v for _, v in numerics],
            "note": f"no two models agreed within rel_tol={rel_tolerance}",
        }
    mean_val = sum(agreeing) / len(agreeing)
    return {
        "agreed_value": mean_val,
        "confidence": len(agreeing) / 3.0,
        "agreement_count": len(agreeing),
        "all_values": [v for _, v in numerics],
    }
