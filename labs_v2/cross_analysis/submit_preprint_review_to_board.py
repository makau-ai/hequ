"""Submit the preprint draft to the 4-phase board for
pre-publication quality review.

The board has seen every piece of this work individually
(composites, DOV-DSL, novelty generation, prior-art search).
This round asks them to evaluate the ASSEMBLED PAPER as a
whole — specifically whether the claims are calibrated to
the evidence and what a peer reviewer at a physics journal
would find objectionable.

NOT asking for APPROVE/MODIFY/REJECT on a design document.
Asking for: "would you submit this to a journal in its
current form, and if not, what specific changes would make
it submittable?"
"""

from __future__ import annotations

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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "PREPRINT_REVIEW.md"


_PAYLOAD = """\
# Preprint Pre-Publication Review

## What the board is being asked to do

Review the preprint "Photon-pressure-driven seepage in porous
media: a novel cross-domain prediction from automated equation
coupling" as if you were a peer reviewer at Physical Review
Letters, Nature Physics, or a comparable venue. The standard
is: would you recommend acceptance, revision, or rejection?

The preprint makes three claims:

**Claim 1 (method):** hequ.ai's combination of I-ADOPT
descriptors + multi-model AI board + local CAS verification
can produce cross-domain equation composites that are
numerically verified and independently cited.

**Claim 2 (novel prediction):** The composite of Darcy's law
and radiation-pressure momentum deposition produces a novel
prediction: photon-pressure-driven seepage velocity
u = kαI/(μc) ≈ 3.3 × 10⁻⁶ m/s at stated parameters, absent
from the published literature based on a 12-query prior-art
search.

**Claim 3 (methodology contribution):** The "board is not a
CAS" protocol, demonstrated by the 10⁷-fold Damköhler error,
is a publishable separation-of-concerns methodology for using
LLMs in scientific computation.

## Evidence summary

**For Claim 1:**
- 6 verified composites spanning 3 transducer types (identity,
  Onsager symmetric, skew-symmetric gyrator, compound
  dimensionless group)
- 7 verified canonical problems
- All pass 4-check verification: symbolic canonicalization,
  200-sample PBT, 50-digit mpmath, board-sourced formula
- Board citations independently match architect citations on
  every composite

**For Claim 2:**
- 12-query prior-art search: 0 direct hits on Darcy+RadPress
- Acoustic analog confirmed published (J. Fluid Mech.; PMC
  2018) — same mechanism, different wave type
- Optical-in-bulk-fluid published (Leonhardt, Phys. Rev. A 90,
  033801, 2014) — different geometry (no porous matrix)
- Photophoresis identified and ruled out (different mechanism:
  thermal, not momentum)
- 8 additional candidate intersections investigated; all were
  rediscoveries in specialist literature
- Descriptor schema frozen before candidate proposed
  (SHA-256 provenance)
- Falsification conditions stated: linear u∝I scaling,
  order-of-magnitude agreement, no prior publication
- Distinguishing experimental signature: u independent of ρ

**For Claim 3:**
- Board value_attempt data across 7 composites
- One catastrophic error: Damköhler Da = 725.4 vs board's
  7.24×10⁹ (rel_err 1.0×10⁷)
- Protocol caught it because local CAS was authoritative

## Known limitations stated in the preprint

1. One novel prediction, not a catalog
2. Corpus is small (n = 16)
3. No experimental verification
4. Descriptor circularity risk (mitigated by freeze, not
   eliminated)
5. AI board COI (training data includes textbook physics)
6. Single-transducer-type composites (no replication per type)

## Specific questions for the reviewers

1. **Overclaiming check:** Does the preprint claim more than
   the evidence supports? Specifically: is "novel prediction"
   too strong a claim for a result based on a literature
   search (which can have false negatives) rather than on
   demonstrated absence from a complete database?

2. **Physics soundness:** Is u = kαI/(μc) the correct
   formula for radiation-pressure body force entering the
   Darcy momentum balance? Are there corrections
   (Abraham-Minkowski momentum in the pore fluid,
   scattering vs absorption, poroelastic coupling) that the
   preprint should acknowledge as potential order-of-magnitude
   modifiers?

3. **Prior-art completeness:** Is there a peer-reviewed paper
   the 12-query search missed? Specifically: has anyone in
   the optofluidics, MEMS, or porous-media communities
   formalized this specific coupling? What search terms would
   you use that we did not try?

4. **Claim 3 significance:** Is the "board is not a CAS"
   result (one 10⁷-fold error across 7 composites) a
   publishable finding, or is the sample too small and too
   biased (textbook equations) to support a general
   methodology claim?

5. **Missing related work:** What published work should the
   preprint cite that it currently does not? Specifically:
   bond-graph/port-Hamiltonian composition literature,
   automated equation discovery (beyond AI Feynman/SINDy/
   PySR), knowledge-graph approaches to scientific equations.

6. **Journal fit:** Which venue is the right fit for this
   work? Physics journal (PRL, PRE, Phys. Rev. Fluids)?
   Methodology journal (PLOS Computational Biology, J. Comp.
   Physics)? AI-for-science (NeurIPS workshop, ICML workshop)?
   Interdisciplinary (PNAS, Science Advances)? The answer
   affects how the preprint should be framed.

7. **Fatal flaw:** Is there a reason this preprint should NOT
   be submitted in its current form? Not a "could be
   improved" concern — a "this would embarrass the authors"
   concern.

## Format of the response

For each reviewer, please provide:
- A 1-sentence overall assessment
- A verdict: SUBMIT / REVISE / DO NOT SUBMIT
- For REVISE: the specific changes required, ranked by
  priority
- Answers to the 7 specific questions above
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase preprint review "
                  "(Grok included, ~8-12 minutes)...")
            result = board.four_phase_query(
                query_id="preprint_review_v1",
                review_subject=(
                    "a preprint draft titled 'Photon-pressure-"
                    "driven seepage in porous media: a novel "
                    "cross-domain prediction from automated "
                    "equation coupling' — pre-publication quality "
                    "review asking whether the three claims "
                    "(method, novel prediction, methodology "
                    "contribution) are calibrated to the evidence "
                    "and what a peer reviewer at a physics journal "
                    "would find objectionable"
                ),
                user_payload=_PAYLOAD,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# Preprint Review — 4-Phase Board\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Include Grok:** {result.include_grok}  ")
    lines.append(f"**Editor verdict:** `{result.editor.verdict}`\n")
    lines.append(f"**All responded (Phase A):** {getattr(result, 'all_responded_a', 'n/a')}  ")
    lines.append(f"**All responded (Phase B):** {getattr(result, 'all_responded_b', 'n/a')}\n")

    lines.append("## Phase C — Editor synthesis\n")
    if result.editor.error:
        lines.append(f"**Status:** editor call failed ({result.editor.error})\n")
    else:
        lines.append(f"**Verdict:** `{result.editor.verdict}`\n")
        lines.append(f"**Rationale:**\n\n{result.editor.rationale}\n")
        if result.editor.required_modifications:
            lines.append("**Required revisions:**")
            for m in result.editor.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    lines.append("## Phase B — Informed votes\n")
    for r in result.phase_b:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** Phase B failed ({r.error})\n")
            continue
        lines.append(f"**Verdict:** `{r.updated_verdict}`  ")
        lines.append(f"**Position change:** {r.position_change}  ")
        lines.append(f"**Headline:** {r.headline}\n")
        lines.append(f"**Response to peers:**\n\n{r.response_to_peers}\n")

    lines.append("## Phase A — Independent reviews\n")
    for r in result.phase_a:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** Phase A failed ({r.error})\n")
            continue
        coi = f"⚠ {r.coi_note}" if r.coi_declared else "no COI"
        lines.append(f"**COI:** {coi}  ")
        lines.append(f"**Verdict:** `{r.verdict}`  ")
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
            lines.append("**Required revisions:**")
            for m in r.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor.verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
