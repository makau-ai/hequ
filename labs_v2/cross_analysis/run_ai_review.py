"""Phase 11 — real AI review board pass on the coupling sieve output.

Runs the Layer 5 coupling sieve against the live corpus, evaluates
each hypothesis against the Phase 6 physical constraint filter and
Phase 7 emergent analysis, then dispatches the hypotheses that need
human (AI-board) judgement to the three-model board for voting.

Target set — which hypotheses get reviewed
------------------------------------------
Per the design doc §12:
- Tier-1 couplings that PASSED the physical filter go to PROVED
  automatically (no review call); they only get a board pass if
  the filter was all-NA ("soft") rather than a clean PASS.
- Tier-2 couplings with physical-filter PASS go to EMPIRICAL and
  get a board pass too — the design doc requires the board to
  sign off on tier 2 before the hypothesis can be claimed a
  finding.
- Tier-2 / tier-3 couplings whose physical filter reported all-NA
  (no applicable check) are held at CONJECTURAL and go to the
  board.
- Hypotheses that FAILED the physical filter are already
  REJECTED; they are NOT sent to the board (the rejection is
  decisive).

Output
------
- Appends one new ledger record per reviewed hypothesis with
  `kind='coupling_reviewed'`, carrying the full BoardDecision
  verbatim in `evidence.ai_review`. The record's outcome
  reflects the board's decision (PROMOTE → PROVED, HOLD_*/DEMOTE
  → EMPIRICAL/CONJECTURAL/REJECTED accordingly).
- Writes a human-readable summary to
  `cross_analysis/AI_REVIEW_SUMMARY.md` with one section per
  reviewed hypothesis.

Usage
-----
Environment: requires gcloud to be authenticated against the
hequ-ai project so the AI review board module can fetch the
three vendor API keys from Secret Manager.

    /path/to/python run_ai_review.py [--dry-run] [--limit N]

--dry-run   Uses `ai_review_board.dry_run_board` (no API calls)
            so the full path is exercised without vendor credits.
--limit N   Only process the first N hypotheses (sorted
            deterministically by (eq_a, eq_b, var_a, var_b)).

The default run burns ~3 × (number of review-required hypotheses)
API calls, one per vendor per hypothesis. Typical cost on the
current 16-equation corpus: 3×6 = 18 calls total.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.ai_review_board import (
    AIBoardKeysMissing,
    BoardDecision,
    ReviewBoard,
    ReviewVerdict,
    dry_run_board,
)
from framework.couplings import CouplingHypothesis, CouplingTier
from framework.discovery_ledger import (
    DiscoveryLedger,
    Hypothesis,
    HypothesisOutcome,
)
from framework.emergent_analysis import analyse as analyse_emergent
from framework.layer5_coupling_sieve import run_coupling_sieve
from framework.physical_constraints import evaluate as evaluate_physical
from framework.typed_expression import load_all_equations


REPORT_PATH = _LABS_V2 / "cross_analysis" / "AI_REVIEW_SUMMARY.md"
LEDGER_PATH = _LABS_V2 / "cross_analysis" / "discovery_ledger.jsonl"


def _needs_review(
    coupling: CouplingHypothesis,
    physical_verdict,
) -> bool:
    """Return True iff this hypothesis should go to the AI board.

    Rules (mirror of §12 voting scope):
    - Always review tier 2 and tier 3 (the design doc is explicit
      that nothing past CONJECTURAL at these tiers is accepted
      without a vote).
    - For tier 1, only review when the physical filter returned
      all-NOT_APPLICABLE (soft pass). A tier-1 with a clean
      physical-check PASS is already PROVED; a tier-1 with a
      FAILED check is already REJECTED.
    """
    if coupling.tier != CouplingTier.TIER1_EQUIVALENCE:
        return True
    # Tier 1: only review if the physical filter was indecisive.
    return physical_verdict.all_not_applicable


def _board_outcome_to_ledger(
    decision: BoardDecision,
    coupling: CouplingHypothesis,
) -> HypothesisOutcome:
    """Translate a BoardDecision.outcome_hint to a ledger
    HypothesisOutcome, factoring in the coupling's tier.
    """
    hint = decision.outcome_hint
    if hint == "PROMOTE":
        # Unanimous approve → PROVED regardless of tier.
        return HypothesisOutcome.PROVED
    if hint == "HOLD_EMPIRICAL":
        return HypothesisOutcome.EMPIRICAL
    if hint == "DEMOTE":
        return HypothesisOutcome.REJECTED
    # HOLD_CONJECTURAL and any unrecognised hint.
    return HypothesisOutcome.CONJECTURAL


def _write_summary(records: List[Hypothesis]) -> None:
    lines: List[str] = []
    w = lines.append
    w("# AI Review Board — Phase 11 results\n")
    w(f"**Records produced this run:** {len(records)}  ")
    w(f"**Board members:** Claude Opus 4.6 · OpenAI GPT-5 · Gemini 2.5 Pro\n")
    w("Board verdicts were collected via the protocol in "
      "`framework/ai_review_board.py` §12. Every vote appears "
      "verbatim in the ledger; the Markdown below is a "
      "human-readable digest.\n")
    by_outcome: Dict[str, List[Hypothesis]] = {}
    for r in records:
        by_outcome.setdefault(r.outcome.value, []).append(r)
    for outcome in ("proved", "empirical", "conjectural", "rejected"):
        if outcome not in by_outcome:
            continue
        w(f"## Outcome: **{outcome.upper()}**  ({len(by_outcome[outcome])})\n")
        for r in by_outcome[outcome]:
            sub = r.substitution
            va = sub.get("v_a", {}).get("variable", "?") if isinstance(sub, dict) else "?"
            vb = sub.get("v_b", {}).get("variable", "?") if isinstance(sub, dict) else "?"
            w(f"### `{r.eq_a}` ↔ `{r.eq_b}` — `{va}` ↔ `{vb}`\n")
            ai_review = r.evidence.get("ai_review") or {}
            rationale = ai_review.get("rationale", "(no rationale)")
            w(f"- **Board rationale:** {rationale}")
            for vote in ai_review.get("votes", []):
                w(f"- **{vote['reviewer']}**: `{vote['verdict']}` — {vote['reason']}")
            w("")
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REPORT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Use dry_run_board (no API calls).")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only process the first N review targets.")
    args = parser.parse_args()

    equations = load_all_equations(_LABS_V2 / "equations")
    print(f"Loaded {len(equations)} equations")

    sieve_report = run_coupling_sieve(equations, emit_tier3=False)
    print(sieve_report.summary())

    targets: List[tuple[CouplingHypothesis, Any, Any]] = []
    for ch in sieve_report.hypotheses:
        verdict = evaluate_physical(ch, equations)
        emergent = analyse_emergent(ch, equations)
        if _needs_review(ch, verdict):
            targets.append((ch, verdict, emergent))

    if args.limit is not None:
        targets = targets[: args.limit]
    print(f"Review targets: {len(targets)}")
    for ch, _, _ in targets:
        print(f"  - {ch.eq_a_id}.{ch.var_a} <-> {ch.eq_b_id}.{ch.var_b} "
              f"[{ch.tier.value}]")

    if not targets:
        print("Nothing to review. Exiting.")
        return 0

    ledger = DiscoveryLedger(LEDGER_PATH)
    new_records: List[Hypothesis] = []

    def _process(ch: CouplingHypothesis, verdict, emergent, decide) -> None:
        decision = decide(ch, verdict.as_dict(), emergent.as_dict())
        outcome = _board_outcome_to_ledger(decision, ch)
        evidence = dict(ch.as_ledger_evidence())
        evidence["physical_constraint_check"] = verdict.as_dict()
        evidence["emergent_properties"] = emergent.as_dict()
        evidence["ai_review"] = decision.as_dict()
        rec = Hypothesis(
            eq_a=ch.eq_a_id,
            eq_b=ch.eq_b_id,
            kind="coupling_reviewed",
            outcome=outcome,
            substitution=ch.as_ledger_substitution(),
            evidence=evidence,
            review_required=(outcome == HypothesisOutcome.CONJECTURAL),
        )
        ledger.record(rec)
        new_records.append(rec)

    if args.dry_run:
        print("--dry-run: using dry_run_board (no API calls)")
        for ch, verdict, emergent in targets:
            _process(ch, verdict, emergent, dry_run_board)
    else:
        try:
            with ReviewBoard() as board:
                for i, (ch, verdict, emergent) in enumerate(targets, start=1):
                    print(f"[{i}/{len(targets)}] reviewing "
                          f"{ch.eq_a_id}.{ch.var_a} <-> "
                          f"{ch.eq_b_id}.{ch.var_b} ...", flush=True)
                    try:
                        _process(
                            ch, verdict, emergent,
                            lambda c, v, e: board.review(c, v, e),
                        )
                    except Exception as exc:
                        # Per-hypothesis isolation: a crash on
                        # one target (vendor timeout, JSON parse
                        # error, etc.) must not kill the rest of
                        # the batch. Record it as a board-level
                        # error and continue.
                        print(f"  ! crashed: {type(exc).__name__}: "
                              f"{exc}", flush=True)
                    # Tiny pacing delay so we don't trip aggressive
                    # rate-limits on any vendor during a burst run.
                    if i < len(targets):
                        time.sleep(0.5)
        except AIBoardKeysMissing as exc:
            print(f"AI board keys missing: {exc}", file=sys.stderr)
            print("Did you `gcloud auth login` and set the active "
                  "project to hequ-ai?", file=sys.stderr)
            return 2

    # Histogram + summary
    hist: Dict[str, int] = {}
    for r in new_records:
        hist[r.outcome.value] = hist.get(r.outcome.value, 0) + 1
    print()
    print(f"Reviewed {len(new_records)} hypotheses. Outcomes: {hist}")
    _write_summary(new_records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
