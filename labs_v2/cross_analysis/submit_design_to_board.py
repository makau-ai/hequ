"""Submit DESIGN-PHASE-12-20.md (v3) to the AI consensus board
using the four-phase academic protocol.

v3 uses framework.ai_consensus.AIConsensusBoard.four_phase_query
which runs:
  Phase A — independent drafts with specialist personas + COI
  Phase B — informed votes after seeing each other's reports
  Phase C — editor synthesis (binding verdict)

Includes Grok as an optional 4th reviewer for this one-off run,
per user request.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.ai_consensus import (
    AIConsensusBoard,
    DESIGN_RUBRIC_SCHEMA,
    DESIGN_REVIEW_PERSONAS,
)
from framework.ai_review_board import AIBoardKeysMissing

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "DESIGN_REVIEW_PHASE_12_20.md"


_SUMMARY = """\
# Realization-Grounded Coupling Engine — Architecture v3 Summary

## Thesis
The difference between a coincidence and a genuine cross-domain
coupling is **executable realization**. A real coupling admits a
physical system in which both equations hold simultaneously and
produce the same measurable answer. Every prior failed attempt
(AI Feynman, SINDy, PySR, SemGen, DARPA SKEMA) argued about
symbols and ignored execution.

## Evidence hierarchy (four levels, multiplicative confidence)
- **L1** canonical problem unit test passes (pytest, binary)
- **L2** composite notebook executes within tolerance of a
  board-sourced reference value, verified by orthogonal sympy
  evaluation + property-based randomized parameter sampling +
  cross-CAS (mpmath) high-precision check
- **L3** ≥2 of 3 board members produce independent primary-source
  citations (DOI-level independence required)
- **L4** live sensor agreement with Bayesian-updated posterior
  over rolling readings

Composite confidence C = c1·c2·c3·c4 (multiplicative).

**v3 promotion thresholds (monotonic in rigor):**
- `CONJECTURAL`: C < 0.30
- `EMPIRICAL`: C ≥ 0.30 AND ≥2 board APPROVE
- `PROVED`: C ≥ 0.60 AND unanimous board APPROVE
- `GROUNDED`: C ≥ 0.85 AND live-sensor c4 > 0.5
- `DUALITY` (sidebar): mathematical isomorphisms (Wick rotation,
  log-price) cannot exceed EMPIRICAL without independent L4
  evidence from both domains. Prevents misclassifying
  analytic-continuation equivalences as physical couplings.

## Architectural layers
L0 Typed canonical form · L1 Canonical problems (P12) ·
L2 Composite catalog (P13) · L3 Literature + transducers (P14) ·
L4 Coupling sieve · L5 Physical filter · L6 Realization
grounding (P14) · L7 AI board (P14, now 4-phase) · L8 Adversarial
pre-reg (P15) · L9 Live sensors (P16-17) · L10 Experiment
authority (P19) · L11 Quantum Rigetti/Braket (P20)

## Board-sourced references with 3-way verification (v3)
For each canonical problem the board is queried for
`{formula_symbolic, substitutions, value, citation}`. v3 now
runs THREE independent verification checks locally before
accepting the value:
1. **Symbolic equivalence**: `sp.simplify(board_formula -
   local_formula) == 0`
2. **Property-based randomized sampling**: N=50 unit-consistent
   parameter draws, all must match within tolerance
3. **Cross-CAS high-precision**: mpmath at 50 decimal places
   vs sympy single-precision

All three must pass. Single-point agreement alone is no longer
sufficient. Breaks OpenAI v2's "spurious formula can pass a
single-point check" concern.

## Automated composite notebook generation (v3)
Given (eq_a, eq_b, transducer): system assembly via transducer
substitution → board-queried parameterisation → board-queried
reference value → programmatic `nbformat` assembly → `nbclient`
execution IN A PINNED CONTAINER → ledger provenance. No hidden
human-in-the-loop.

## Container-sandboxed notebook execution (v3)
Every generated composite runs inside a Docker container with:
- `python:3.12-slim` pinned by SHA-256
- Frozen requirements.txt with hashes (pip `--require-hashes`)
- `--network=none` (no internet from notebook cells)
- `--read-only` root + `--tmpfs /workspace` ephemeral scratch
- Non-root UID 1000, memory/CPU cgroup limits
- Per-cell 60s timeout
- SHA-256 content hash of every notebook logged in ledger
Cost: zero, runs on local Docker/OrbStack/Podman. Phase 16+
optional Cloud Run path.

## Transducer library + conjectural proposals (v3 versioned)
- Named bond-graph transducers authored by board consensus
- **Catalog has a semver version**. Every Phase 12+ run reads
  the catalog ONCE, stamps the version into each hypothesis.
  Pre-registered tests pin to a specific catalog version.
- `ConjecturalTransducer` proposals when no catalogued entry
  fits — catalog grows organically through board review of
  sieve-proposed new transducers.

## Adversarial pre-registration (v3 unchanged)
30 items: 10 must-surface, 15 must-reject, 5 honest unknowns.
100% pass on must-surface AND must-reject required before
the sieve may emit on honest-unknowns.

## Four-phase AI review board (v3, academic mirror — NEW)
The voting protocol is upgraded from single-pass to four-phase,
modelled directly on real academic peer review:

- **Phase A — Independent drafts** with specialist personas
  per reviewer, rubric-scored (5 dimensions 1-5), and COI
  self-declaration. No cross-contamination.
- **Phase B — Informed rebuttal-aware votes** after each model
  reads a consolidated briefing showing the other two's Phase A
  reports. Each model must explicitly respond to the others'
  concerns.
- **Phase C — Editor synthesis** by a fourth distinct model
  call (Claude Opus in editor persona). The editor weights
  reasoning quality, not just vote count, and writes the
  binding decision.
- **Phase D — Bounded rebuttal** (max 2 cycles): if MODIFY,
  the submitter can revise and resubmit for a second Phase B+C.

Rubric (design review): thesis_soundness, technical_feasibility,
falsifiability, prior_art_awareness, honest_scope — each 1-5.

Specialist personas: senior software architect (Claude), senior
symbolic-AI+formal-methods researcher (OpenAI), senior physicist
with bond-graph expertise (Gemini), and for this run, senior
independent first-principles reviewer (Grok-4) as a 4th voice.

COI: each reviewer declares training-data exposure to the
specific formulation under review. Logged but non-disqualifying.

## Experiment authority (v3 unchanged)
Default READ-only. WRITE/ACTUATE requires ExperimentEnvelope
with time limit, magnitude bounds, rollback plan, board
unanimous approve + project-owner human gate. Accumulated-spend
kill switch in `EXPERIMENT_BUDGET.yaml`.

## Quantum specialist (v3 unchanged)
Phase 20: Rigetti 108-qubit via Amazon Braket. First use: VQE
on a small SHO Hamiltonian to measure E_0 = (1/2)ℏω and
validate Newton+Hooke AND Schrödinger simultaneously on quantum
hardware.

## What v3 specifically changed from v2
1. **§11a four-phase protocol** (NEW, user-directed): Phase A
   independent → Phase B informed → Phase C editor synthesis
   → Phase D bounded rebuttal. Plus rubric, specialist
   personas, COI self-declaration.
2. **§8a monotonic labels** (fixes OpenAI v2 non-monotonicity):
   CONJECTURAL < EMPIRICAL < PROVED < GROUNDED.
3. **§8a.1 DUALITY sidebar status** (fixes OpenAI v2
   analytic-continuation concern): mathematical isomorphisms
   cannot reach PROVED without independent physical L4
   evidence from both domains.
4. **§11b container sandbox** (fixes OpenAI v2 supply-chain
   risk): pinned image SHA, --network=none, content-hashed
   notebooks, no-host-mount.
5. **§11c property-based + cross-CAS verification** (fixes
   OpenAI v2 single-point brittleness): 50 randomized samples
   + mpmath high-precision + symbolic equivalence all required.
6. **§11d transducer catalog semver** (fixes OpenAI v2 catalog
   drift): pinned version per run, CATALOG_REGRESSION_DETECTED
   on must-surface failure.

## Six questions for the board
1. Is the four-phase protocol a real improvement over
   single-pass, or just extra latency?
2. Does the container sandbox adequately address the
   supply-chain / code-injection risk?
3. Does the three-way verification (sympy + property-based +
   mpmath) adequately address the "single-point can pass a
   bad formula" concern?
4. Is the DUALITY sidebar the right place to put mathematical
   isomorphisms, or should they be a top-level status?
5. Is the editor role (Phase C) appropriately empowered, or
   does it create a single point of failure?
6. What fatal flaw might we still not see?
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review (Phase A → B → C, "
                  "~10 model calls total, ~5-8 minutes)...")
            result = board.four_phase_query(
                query_id="design_phase_12_20_review_v3",
                review_subject=(
                    "a design document v3 for a cross-domain "
                    "equation coupling discovery engine, after "
                    "two prior board reviews raised specific "
                    "concerns that v3 addresses"
                ),
                user_payload=_SUMMARY,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    # --- write the binding decision record ---
    lines: list[str] = []
    lines.append(f"# Design Review v3 — 4-Phase Academic Protocol\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Include Grok:** {result.include_grok}  ")
    lines.append(f"**Editor verdict:** `{result.editor.verdict}`\n")

    lines.append("## Phase C — Editor synthesis (binding)\n")
    if result.editor.error:
        lines.append(f"**Status:** editor call failed ({result.editor.error})\n")
    else:
        lines.append(f"**Verdict:** `{result.editor.verdict}`\n")
        lines.append(f"**Rationale:**\n\n{result.editor.rationale}\n")
        if result.editor.required_modifications:
            lines.append("**Required modifications:**")
            for m in result.editor.required_modifications:
                lines.append(f"- {m}")
            lines.append("")
        if result.editor.reviewer_disagreement_flagged:
            lines.append("⚠ **Editor flagged reviewer disagreement on fundamentals.**\n")

    lines.append("## Phase B — Informed votes\n")
    for r in result.phase_b:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** Phase B failed ({r.error})\n")
            continue
        lines.append(f"**Verdict:** `{r.updated_verdict}`  ")
        lines.append(f"**Position change:** {r.position_change}  ")
        lines.append(f"**Headline:** {r.headline}\n")
        lines.append(f"**Updated rubric (mean {r.updated_rubric.total:.2f}):** "
                     f"{r.updated_rubric.dimension_scores}\n")
        lines.append(f"**Response to peers:**\n\n{r.response_to_peers}\n")

    lines.append("## Phase A — Independent drafts\n")
    for r in result.phase_a:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** Phase A failed ({r.error})\n")
            continue
        coi = f"⚠ {r.coi_note}" if r.coi_declared else "no COI"
        lines.append(f"**COI:** {coi}  ")
        lines.append(f"**Verdict:** `{r.verdict}`  ")
        lines.append(f"**Rubric (mean {r.rubric.total:.2f}):** "
                     f"{r.rubric.dimension_scores}\n")
        lines.append(f"**Headline:** {r.headline}\n")
        if r.strengths:
            lines.append("**Strengths:**")
            for s in r.strengths:
                lines.append(f"- {s}")
            lines.append("")
        if r.concerns:
            lines.append("**Concerns:**")
            for c in r.concerns:
                lines.append(f"- {c}")
            lines.append("")
        if r.required_modifications:
            lines.append("**Required modifications:**")
            for m in r.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor.verdict}")
    print(f"Gate met (editor rule): {result.gate_met('editor')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
