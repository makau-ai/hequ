"""Submit the novelty-generation brief to the 4-phase review board.

This is a DIFFERENT KIND of board submission. Prior rounds asked the
board to review, critique, or gate an artifact. This round asks the
board to generate. Each reviewer is asked to propose 2-3 concrete
candidate cross-domain couplings using their specialist perspective.

The board's role expands from 'verification oracle + critical
reviewer' to 'generative collaborator' — the user's commitment is
that novelty is the load-bearing claim and that the board should be
used not only to check our work but to propose novel directions.

The brief is structured so that each reviewer's personas push them
toward different parts of the cross-domain landscape, and the
review phases (A independent → B informed → C editor) encourage
generation first, cross-critique second, and synthesis third.
Critiquing each candidate happens in Phase B; generation happens in
Phase A.

Context this brief cites:
  - Five verified textbook composites (Newton+Hooke, Newton+WorkEnergy,
    Fourier+Fick/Soret, Newton+Ohm/gyrator, Arrhenius+Fick/Damköhler)
  - Descriptor schema freeze at corpus_sha256
    5b1af1679884de3f91cc65ad409a5dfe9749b9fad2fc2356fc5b95e8b4cd3633
    (frozen 2026-04-16T01:13:49 UTC)
  - Three novelty mechanisms articulated in NOVELTY_PATHWAY.md:
      A — cross-community isolation
      B — parameter-regime overlap
      C — structural-type matching
  - Unanimous board meta-analysis finding: the central discovery
    claim is unfalsified in the wrong direction because every
    existing composite rediscovers textbook couplings.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "NOVELTY_GENERATION_BRIEF.md"


_BRIEF = """\
# hequ.ai Novelty Generation Brief

## Context

The four-phase review board previously returned a unanimous
meta-analysis MODIFY on the hequ.ai project. The decisive
finding was that the central discovery claim is unfalsified
in the wrong direction: all five verified composites
rediscover textbook couplings, and the project has not yet
attempted to be right about anything it did not already
know. Claude's exact phrasing from that round: *"it cannot
yet be wrong because it has not yet tried to be right about
anything novel."*

The user has made a binding commitment in response: **novelty
is the load-bearing claim**, and the board's role expands
from "verification oracle and critic" to "generative
collaborator." Critique alone will not produce novelty. The
board is now asked to propose, not only review.

## The descriptor schema is frozen

Before this brief ran, the entire 16-equation corpus was
pre-registered with immutable SHA-256 hashes and a ledger
record of kind `descriptor_schema_freeze`. Corpus SHA-256:

    5b1af1679884de3f91cc65ad409a5dfe9749b9fad2fc2356fc5b95e8b4cd3633
    (frozen 2026-04-16T01:13:49 UTC)

Any novelty candidate the board surfaces in this brief is
therefore grounded in descriptors that were declared before
the candidate was proposed. No retroactive descriptor tuning
is possible without a new freeze event, which would itself
be visible in the ledger. This directly addresses the
descriptor-circularity concern the meta-analysis raised.

## The three novelty mechanisms (from NOVELTY_PATHWAY.md)

Each proposed candidate must be classifiable as one of:

**Mechanism A — Cross-community isolation.** Two scientific
communities study structurally similar equations in parallel
for decades without citing each other because their
vocabulary, venues, and training pipelines do not overlap.
Historical example: Fisher-KPP equation (1937 population
genetics) and reaction-diffusion combustion fronts (1940s
chemistry) were the same equation studied independently for
~30 years. A hequ.ai with both corpora could have flagged
the coupling.

**Mechanism B — Parameter-regime overlap.** Two equations
individually well-known, but their composite in a specific
parameter regime is unreported because the regime is
physically unusual or experimentally inaccessible until
recently. Candidate example: Arrhenius reaction kinetics at
relativistic temperatures (~10⁹ K, early-universe or
ultra-high-intensity laser plasma conditions), composing
`k(T) = A · exp(−E_a / (R · T · √(1 − v²/c²)))`.

**Mechanism C — Structural-type matching.** Equations from
different semantic domains share the same mathematical
structure (second-order parabolic PDE, stochastic DE,
integral equation). Some such matches are pure mathematical
dualities without physical coupling (Wick rotation); others
are real physical couplings through shared Green's functions
or asymptotic behavior. The hard part is telling these
apart without falling for dualities.

## What each reviewer is asked to do (Phase A)

**Propose 2-3 concrete candidate cross-domain couplings.**

Each candidate must:

1. Be **physically plausible** — not a pure mathematical
   duality. Wick rotation of the heat equation to the
   Schrödinger equation is not eligible; the Black-Scholes /
   heat-equation isomorphism is not eligible; analytic
   continuation tricks are not eligible. Only couplings that
   correspond to a physical system in which both equations
   hold simultaneously and produce the same measurable
   answer are eligible.
2. Be **absent from standard cross-reference texts.** The
   reference set for this check is: Landau-Lifshitz (all
   10 volumes), Feynman Lectures on Physics, Bird-Stewart-
   Lightfoot Transport Phenomena, Goldstein Classical
   Mechanics, de Groot & Mazur Non-Equilibrium
   Thermodynamics, Atkins Physical Chemistry, Jackson
   Classical Electrodynamics, Sakurai or Griffiths
   (Quantum), Pathria or Kardar (Statistical Mechanics),
   Weinberg (GR), Strogatz (Nonlinear Dynamics). If the
   coupling appears in any of these as a direct
   cross-reference or worked example, it is a rediscovery
   and not a novelty candidate. Edge case: if the coupling
   appears in a specialized research paper but not in the
   textbook cross-reference layer, that is still eligible
   and should be flagged as "specialist literature, not
   textbook" so the novelty claim can be graded honestly.
3. Be **verifiable with hequ.ai's current machinery or a
   small known extension.** Current machinery: canonical
   problem pipeline (Phase 12), composite verification
   pipeline with sympy + mpmath + Hypothesis PBT (Phase 13),
   DOV-DSL validity envelopes, port-Hamiltonian gyrator /
   Onsager cross-coefficient / compound dimensionless group
   transducer classes. Small extensions the user will
   support: cross-envelope intersection check, structural-
   type annotation (ODE / PDE_parabolic / stochastic_DE /
   etc.), Dufour-direction Onsager verification.
4. Be **classified under one of the three mechanisms (A, B,
   or C)** from NOVELTY_PATHWAY.md.

**For each proposed candidate, please provide:**

- `candidate_id`: short handle, e.g. `NOV-ECOL-NETWORK-01`
- `parents`: two (or more) equation names and domains
- `proposed_coupling`: a one-line description of how they
  would be composed (what shared variable or transducer)
- `mechanism`: A, B, or C
- `physical_plausibility`: 1 (implausible) to 5 (almost
  certainly real), with a one-sentence justification
- `literature_absence`: 1 (in every textbook) to 5
  (not in any cross-reference text I can think of), with
  a one-sentence justification pointing to where it would
  have shown up if it were common knowledge
- `verifiability`: 1 (not feasible to verify) to 5 (can be
  verified today with existing hequ.ai machinery), with a
  one-sentence note on which pipeline step would handle it
- `rediscovery_risk`: 1 (no risk — genuine candidate) to
  5 (probably already published but not yet noticed by me),
  with a one-sentence note on the most likely place it has
  been done before
- `specific_numerical_prediction`: if the coupling leads to
  a numerical quantity that could be computed from
  published measurements (even a rough order-of-magnitude
  prediction), state it. This is what separates a
  discovery candidate from a taxonomy exercise.
- `disconfirmation_path`: what experiment or calculation
  would prove the coupling wrong

**Specialist framing per reviewer.** Each of you has a
different specialist persona for this brief. Please use it
aggressively — the goal is diversity of search, not
consensus.

- **claude-opus-4-6 (senior software architect + formal
  methods)**: focus on Mechanism C (structural-type
  matching). Propose couplings where the mathematical
  structure (kernel, operator, boundary type) is shared
  across semantically distant domains. Filter hard against
  pure dualities.
- **openai-gpt-5 (senior symbolic-AI + formal-methods
  researcher)**: focus on Mechanism B (parameter-regime
  overlap). Propose couplings where two well-known
  equations coincide in an experimentally unusual regime
  (extreme temperature, extreme pressure, relativistic
  corrections to chemistry, quantum corrections to
  classical transport, etc.). Be specific about the regime
  boundary.
- **gemini-2.5-pro (senior physicist with bond-graph +
  port-Hamiltonian expertise)**: focus on Mechanism A
  (cross-community isolation), BUT with a specific
  physical-admissibility filter: only propose couplings
  where the port-Hamiltonian / bond-graph formalism would
  give a clean gyrator or transformer element. Your
  specialty is exactly the filter that tells real
  couplings from mathematical artifacts.
- **grok-4 (senior independent first-principles reviewer)**:
  focus on any of the three mechanisms, but your task is
  adversarial — after seeing the other three reviewers'
  proposals in Phase B, actively try to falsify them by
  pointing out where each one is likely already published.
  Your role in Phase A is to propose 2-3 candidates that
  the other reviewers are unlikely to propose (e.g., from
  biology, economics, geophysics, or social-science
  quantitative models), and in Phase B to red-team the
  field.

## Domain seeding (to help avoid groupthink)

Some under-covered domains where the corpus is thin or
absent and where cross-community isolation is plausible:

- **Quantitative ecology**: allometric scaling (Kleiber's
  law 3/4-power metabolism), metabolic theory of ecology,
  network epidemiology (SIS/SIR on graphs), Lotka-Volterra
  variants with stochasticity or spatial structure
- **Econophysics / quantitative finance**: Black-Scholes
  (already in corpus), heavy-tailed return distributions,
  order-book dynamics, Fisher information of market
  microstructure
- **Geophysics**: Darcy's law, Richards equation (unsaturated
  soil hydraulics), Budyko energy-balance climate models
- **Glassy dynamics**: mode-coupling theory, Kauzmann
  temperature, Adam-Gibbs relation
- **Active matter**: Toner-Tu hydrodynamics, run-and-tumble
  kinetics
- **Quantum information**: Holevo bound, entanglement
  entropy area law, quantum channel capacities
- **Neural dynamics**: Hodgkin-Huxley, Wilson-Cowan mean-field,
  Fokker-Planck of membrane voltage noise
- **Biochemical reaction networks**: Michaelis-Menten
  (already the hequ.ai v_max·[S]/(K_m+[S]) form), Hill
  functions, enzyme cascades

Feel free to propose couplings that include equations NOT
yet in the corpus — if a candidate is compelling, the user
will add the equation files and re-run the freeze. The
freeze ledger will record the new corpus state.

## Phase B instructions

After seeing the other three reviewers' Phase A proposals,
each of you should:

1. For each proposed candidate (yours and peers), score it
   on a **novelty-value rubric**:
   - physical plausibility × literature absence × verifiability
   - Flag any candidate where rediscovery_risk ≥ 4 as
     "likely already done, deprioritize."
2. Propose at most **one cross-reviewer combination** —
   a composite that uses one reviewer's proposed coupling
   as input and another reviewer's structural insight as
   the mechanism. This is where the 4-phase format produces
   more than the sum of independent suggestions.
3. If you have a genuine concern that a candidate, even one
   proposed by you, is actually a rediscovery, say so. The
   honest answer "I proposed this but on reflection it's
   in Landau-Lifshitz Volume 6 Chapter 7" is more valuable
   than silent endorsement.

## Phase C editor synthesis

The editor should produce a **ranked shortlist of 3-5
candidates** with:
- candidate_id and parents
- mechanism classification
- aggregate novelty-value score
- recommended next step for the project to actually build
  and verify the composite (which pipeline steps to run,
  which extensions if any are needed, which domain expert
  could act as an independent ground-truth check)

The editor should also note any candidate that is
compelling enough to warrant an **immediate Phase 13
composite build** vs any that need corpus expansion or new
machinery first.

## What we will do with the output

The user commits that at least one of the editor's
shortlisted candidates will be built and verified (or
rejected) through the standard Phase 13 composite
verification pipeline, within the constraints of Rule A9
(every worked example sympy-verified before submission).
The result — positive, negative, or "we tried and it
turned out to be already published" — will be recorded in
the discovery_ledger.jsonl under a new record kind
`novelty_generation_outcome` and reported back to the board
in a future retrospective.

This is therefore not an advisory-only round. It is a
generative round with a commitment to act on its output.

Please generate.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase NOVELTY GENERATION brief "
                  "(Grok included, ~8-12 minutes)...")
            result = board.four_phase_query(
                query_id="novelty_generation_brief_v1",
                review_subject=(
                    "a generative brief asking each board member "
                    "to propose 2-3 concrete candidate cross-"
                    "domain equation couplings that are physically "
                    "plausible, absent from standard cross-"
                    "reference texts, and verifiable with hequ.ai's "
                    "existing machinery — grounded in a frozen "
                    "descriptor schema (corpus_sha256 "
                    "5b1af1679884de3f91cc65ad409a5dfe9749b9fad2fc2"
                    "356fc5b95e8b4cd3633) and classified under one "
                    "of three novelty mechanisms from NOVELTY_"
                    "PATHWAY.md: cross-community isolation, "
                    "parameter-regime overlap, or structural-type "
                    "matching. The board's role expands from "
                    "verification oracle to generative "
                    "collaborator, per the user's commitment that "
                    "novelty is the load-bearing claim of the "
                    "project"
                ),
                user_payload=_BRIEF,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# hequ.ai Novelty Generation Brief — Board Output\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Include Grok:** {result.include_grok}  ")
    lines.append(f"**Editor verdict:** `{result.editor.verdict}`\n")
    lines.append(f"**All responded (Phase A):** {getattr(result, 'all_responded_a', 'n/a')}  ")
    lines.append(f"**All responded (Phase B):** {getattr(result, 'all_responded_b', 'n/a')}\n")

    lines.append("## Phase C — Editor synthesis (shortlist + ranking)\n")
    if result.editor.error:
        lines.append(f"**Status:** editor call failed ({result.editor.error})\n")
    else:
        lines.append(f"**Verdict:** `{result.editor.verdict}`\n")
        lines.append(f"**Rationale:**\n\n{result.editor.rationale}\n")
        if result.editor.required_modifications:
            lines.append("**Shortlisted candidates / recommended next steps:**")
            for m in result.editor.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    lines.append("## Phase B — Cross-reviewer critiques + combinations\n")
    for r in result.phase_b:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** Phase B failed ({r.error})\n")
            continue
        lines.append(f"**Verdict:** `{r.updated_verdict}`  ")
        lines.append(f"**Position change:** {r.position_change}  ")
        lines.append(f"**Headline:** {r.headline}\n")
        lines.append(f"**Response to peers:**\n\n{r.response_to_peers}\n")

    lines.append("## Phase A — Independent candidate proposals\n")
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
            lines.append("**Candidate proposals (strengths field):**")
            for s in r.strengths:
                lines.append(f"- {s}")
            lines.append("")
        if r.concerns:
            lines.append("**Concerns / self-flagged rediscovery risks:**")
            for c in r.concerns:
                lines.append(f"- {c}")
            lines.append("")
        if r.required_modifications:
            lines.append("**Recommended next steps:**")
            for m in r.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor.verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
