"""Submit a meta-analysis / retrospective of the hequ.ai project
state to the 4-phase review board.

Unlike prior submissions that asked the board to approve a design
or gate a modification, this one asks the board to step back and
assess the PROJECT: what has been built, what does it prove, what
is the strategic next move, and what are the real risks. The
goal is external academic-peer scrutiny of the whole trajectory,
not just the latest artifact.

The submission is grounded in live ledger data (five verified
composites, seven verified canonical problems, two real
failure_modes entries, one APPROVE from the board on the
simplified unity proposal) so the reviewers work from facts
rather than claims.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "PROJECT_META_ANALYSIS.md"


_PAYLOAD = """\
# hequ.ai Project Meta-Analysis — Board Retrospective

## What the board is being asked to do

Step back from the artifact-of-the-week and assess the
project. Please treat this as external academic peer review
of the ENTIRE trajectory — not a gate on any single design
document. Where you believe the project is on a sound path,
say so plainly. Where you see fragility, dead weight,
over-engineering, or missed priorities, say that more
plainly. The standard is the Nobel-rigor bar previously
declared: external academic peer review, falsifiability,
primary-source citations, independent replication pathway.

The user has explicitly asked for this review to be an
honest retrospective, including criticism of the path we
took to get here. Please do not soften.

---

## Ledger state at the time of this submission

These numbers are extracted live from
`labs_v2/cross_analysis/discovery_ledger.jsonl`:

**Verified composites (5):**

| ID                            | Parents                   | Tier              | Transducer                 | Outcome   |
|-------------------------------|---------------------------|-------------------|----------------------------|-----------|
| CMP-NEWTON-HOOKE-SHO-001      | Newton II + Hooke         | tier-1 equivalence| TIER1_IDENTITY             | empirical |
| CMP-NEWTON-WORKENERGY-001     | Newton II + Work-Energy   | tier-1 equivalence| TIER1_IDENTITY             | empirical |
| CMP-FOURIER-FICK-SORET-001    | Fourier + Fick            | tier-2 structural | TRANSDUCER-SORET (Onsager) | empirical |
| CMP-NEWTON-OHM-MOTOR-001      | Newton II + Ohm           | tier-2 structural | TRANSDUCER-GYRATOR-MOTOR   | empirical |
| CMP-ARRHENIUS-FICK-001        | Arrhenius + Fick          | tier-2 structural | TRANSDUCER-DAMKOHLER       | empirical |

Every one of the five passed all four verification checks
(symbolic canonicalization, 200-sample property-based testing,
mpmath 50-digit high precision, python-flint interval is still
best-effort). All five have board-sourced formula + primary-source
citations that matched the architect's independent citations.
The three tier-2 composites each use a structurally different
kind of cross-coefficient:

- **SORET** — Onsager linear-transport cross-coefficient,
  thermodynamically dissipative, symmetric (L_12 = L_21).
- **GYRATOR-MOTOR** — port-Hamiltonian gyrator element,
  power-conserving, with K_t = K_e forced by skew-symmetry.
- **DAMKOHLER** — a computed dimensionless group derived
  from three independently measured quantities, not a
  physical constant. First "compound" transducer.

**Verified canonical problems (7):**
- PRB-NEWTON-II-001 (pendulum period)
- PRB-HOOKE-001 (spring force)
- PRB-FOURIER-001 (copper rod heat conduction)
- PRB-FICK-001 (dilute solute flux)
- PRB-OHM-001 (voltage drop)
- PRB-WORK-ENERGY-001 (net work)
- PRB-ARRHENIUS-001 (rate constant at 298.15 K)

All verified under the v5 "board is not a CAS" protocol:
board provides formula + citations, local sympy + mpmath
computes the authoritative number, board is asked for a
sanity value_attempt as LLM capability data. One
particularly crisp recent result: on the Arrhenius+Fick
composite, the board's value_attempt was 7.24e9 while the
true value is 725.41 — relative error 9.98e+06. The local
CAS was correct; the board was catastrophically wrong. This
is the protocol working exactly as designed.

**Failure modes (2 equations, 4 modes):**

- EQ-NEWTON-II
  - F1 rotating/accelerating frame (Rossby Ro ≥ 1), Foucault 1851
  - F2 relativistic regime (β = v/c < 0.1), Kaufmann 1906
- EQ-HOOKE
  - F1 past proportional limit, Tacoma Narrows 1940
  - F2 viscoelastic / rate-dependent (De < 0.1), Silly Putty

All four failure modes parse cleanly under the DOV-DSL
parser (`framework/dov_dsl.py`), all `use_instead` references
resolve against the live corpus, all historical examples
carry primary-source citations. The referential integrity
validator passes on the full 16-equation corpus.

**Board review history (the iteration log):**

- EWE concept rounds v1 → v6 (MITRE-analog four-layer
  framework): all MODIFY, rubric means climbed from ~3.5
  (v1) to 4.80–5.00 (v6). v6 had 5 remaining surgical
  concerns. The trajectory looked convergent but every
  round exposed new concerns at finer resolution, not
  fewer concerns overall.
- Simplified unity proposal v1: MODIFY with 4 concrete
  mods. Editor language: "architecturally sound and
  technically correct," concerns were "well-scoped schema
  or specification clarifications rather than structural
  redesigns."
- **Simplified unity proposal v2: APPROVE** (editor),
  2 APPROVE / 2 MODIFY (Phase B), all responded in both
  phases. Four hardening modifications required, all four
  addressed with real running code (not spec documents):
  `EvaluationError` + divide-by-zero handling with
  equatorial-Coriolis test, natural-log documentation,
  validator negative-test fixtures, Related Work section
  grounding the novelty claim against NIST DLMF, Modelica
  Standard Library, SysML, and QUDT.

---

## The key strategic move we want the board to assess

Between EWE v6 and the simplified unity v1, we **walked back
six rounds of concept design** for a four-layer MITRE-analog
framework (EWE + ECP + EOE + EMP) in favor of a single
embedded `failure_modes` block in each `equation.yaml` plus
a graph artifact (`unity_map.yaml`) generated from existing
I-ADOPT descriptors.

The user framed this directly: *"this entire thing was just
an idea."* The board is being asked to judge whether that
walk-back was the right call in hindsight, or whether the
six EWE rounds contained real design value that is now
being thrown away.

The case for the walk-back being correct:
- MITRE has four catalogs because it has four stakeholder
  communities. hequ.ai has one stakeholder. Four parallel
  catalogs was substantially more machinery than the
  problem requires.
- The validity-envelope work (DOV-DSL, AAO tags, machine-
  checkable inequalities) was retained — that was the
  part that genuinely earned its six rounds of design and
  is now shipped as a working parser.
- The stochastic / modulated-Dirac / singularity / tensor-
  index machinery from EWE v4–v6 stays attached to
  composite.yaml and fires only when a real composite hits
  those cases. The specs were not thrown away; they were
  re-scoped to a different artifact class.
- The `unity_map.yaml` generator rediscovers 2-of-2 of the
  verified cross-domain composites on the current corpus
  from pure I-ADOPT descriptor metadata. This is a ground-
  truth signal that the descriptor machinery is already
  detecting real coupling structure before any schema
  expansion. Of course n=16 makes this preliminary.

The case against the walk-back:
- We spent ~6 rounds of compute and human attention on a
  framework that we then discarded. A disciplined process
  would have reached the simplification sooner.
- The six rounds produced genuine technical content
  (STOCHASTIC_COUPLING class, non-hyperbolic fixed-point
  protocol, modulated Dirac structures, Pantelides index
  reduction, tensor rank consistency, CRYPTO_REDUCTION
  schema). Some of that content is probably load-bearing
  for specific future composites — we have deferred
  testing that claim rather than resolved it.
- Rubric means of 4.80–5.00 on v6 are the highest scores
  any board submission has achieved. Walking back from a
  near-APPROVE verdict to a reset is unusual; typically
  a project would land the APPROVE and refactor later.

**Questions on this specifically:**
1. Was the walk-back the right call, or was it premature?
2. If it was right, what should we do differently next time
   to avoid the six-round detour pattern?
3. If any of the deferred EWE content (stochastic, modulated
   Dirac, singularity handling) turns out to be needed, how
   should we re-introduce it without re-triggering the
   over-engineering loop?

---

## Pre-registered validation protocol that has NOT yet run

The simplified unity v2 submission pre-registered a
falsifiability protocol for the unity-map mechanism:
precision ≥ 0.50 and recall ≥ 0.80 at n ≥ 30 equations,
measured against a three-annotator Cohen's κ ≥ 0.80
ground-truth panel. The current corpus is n = 16. The
mechanism's 2-of-2 result is explicitly labeled a
preliminary consistency check, not evidence of validity.

**Questions on this:**
4. Is reaching n = 30 equations the right next milestone,
   or should we prioritize a different dimension (more
   failure_modes per equation; more tier-2 composites; a
   harder cross-domain pair like Schrödinger + Maxwell for
   light-matter coupling)?
5. Who should serve as the three-annotator ground-truth
   panel when the time comes? Board members themselves
   would have conflict-of-interest since they have already
   seen the mechanism. External human experts are the
   honest answer but expensive.

---

## What we think is the project's single biggest risk

**Composite coverage is too thin to falsify the discovery
engine's central claim.** Five verified composites across
13 distinct physical domains is a proof-of-concept, not a
scientific instrument. Two of the five are tier-1
equivalences (trivially correct because the variable
identity makes the composition nearly algebraic). The three
tier-2 composites each use a different kind of transducer,
which is good for architectural coverage but means we do
not yet have two independent composites that test the same
transducer type. A Fick+heat-generation composite via the
Soret coefficient would independently validate the Soret
machinery; another DC-machine variant (wound-field vs
permanent-magnet) would validate the gyrator machinery.

Without that, a single wrong composite would be hard to
distinguish from a systematic flaw in the verification
pipeline. We have no independent replication on any
transducer type.

**Questions on this:**
6. Is the "two independent composites per transducer type"
   standard the right target for Phase 13 completion, or
   too strict / too loose?
7. What is the minimum credible composite catalog size for
   a first published result (informal workshop note vs
   peer-reviewed preprint vs journal submission)?

---

## Other specific questions

8. The `failure_modes` schema has survived first contact
   with two real entries (Newton II, Hooke, four total
   modes). Before we scale it to 5 or 10 more equations,
   is there a schema change we should lock in now while
   the migration cost is still low? Specifically: should
   `assumption_violated` be drawn from a controlled
   vocabulary (similar to AAO tags) rather than free text?
9. The v5 "board is not a CAS" protocol has now captured
   multiple data points on LLM numerical capability. One
   data point on this run: board value_attempt for the
   Damköhler composite was 7.24e9 vs true 725.41 (rel_err
   1e7). Is it time to publish the LLM-math-capability
   dataset as a side result, or is the sample too small
   and too biased toward equations the board models have
   memorized from textbooks?
10. Does the board see a pathway from the current state
    to an actual scientific discovery — an equation
    coupling that is real but not yet catalogued in a
    physics textbook — or does the current machinery
    only rediscover known composites?

---

## What we are NOT asking

We are not asking for another schema redesign of
failure_modes. We are not asking for another ECP class.
We are not asking for more surgical technical objections
to the DOV-DSL grammar. All of those rounds are over and
the architectural shape is settled. The question is
strategic: where does hequ.ai actually go from here, and
what would let the project clear the Nobel-rigor bar vs
what would just add machinery.

---

## Verdict requested

Not APPROVE / MODIFY / REJECT this time. Instead, please
return:

- **A 1-3 sentence overall state assessment.**
- **The single biggest strength** of the project as it
  currently stands.
- **The single biggest weakness or risk** as it currently
  stands.
- **A ranked list of the next 3–5 priorities** the board
  would focus on if this were your own project.
- **One thing you would actively stop doing** if you were
  running it.
- **One thing you would prioritize that we have not
  mentioned.**

Be direct. The user wants to know.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board meta-analysis of hequ.ai "
                  "project state (Grok included, ~8-12 minutes)...")
            result = board.four_phase_query(
                query_id="project_meta_analysis_v1",
                review_subject=(
                    "a meta-analysis / retrospective of the hequ.ai "
                    "project state after five verified cross-domain "
                    "composites, seven verified canonical problems, "
                    "two real failure_modes entries, and a board-"
                    "APPROVED simplified unity proposal following a "
                    "six-round EWE concept-design detour that was "
                    "walked back. The board is asked to assess the "
                    "whole trajectory, the walk-back decision, the "
                    "strategic next priorities, and the pathway (or "
                    "lack thereof) from current state to a real "
                    "scientific discovery. External-peer-review "
                    "rigor required; no softening."
                ),
                user_payload=_PAYLOAD,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# hequ.ai Project Meta-Analysis — Board Retrospective\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Include Grok:** {result.include_grok}  ")
    lines.append(f"**Editor verdict:** `{result.editor.verdict}`\n")
    lines.append(f"**All responded (Phase A):** {getattr(result, 'all_responded_a', 'n/a')}  ")
    lines.append(f"**All responded (Phase B):** {getattr(result, 'all_responded_b', 'n/a')}\n")

    lines.append("## Phase C — Editor synthesis (binding)\n")
    if result.editor.error:
        lines.append(f"**Status:** editor call failed ({result.editor.error})\n")
    else:
        lines.append(f"**Verdict:** `{result.editor.verdict}`\n")
        lines.append(f"**Rationale:**\n\n{result.editor.rationale}\n")
        if result.editor.required_modifications:
            lines.append("**Required modifications / next-steps:**")
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

    lines.append("## Phase A — Independent drafts\n")
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
            lines.append("**Concerns / weaknesses:**")
            for c in r.concerns:
                lines.append(f"- {c}")
            lines.append("")
        if r.required_modifications:
            lines.append("**Recommended priorities:**")
            for m in r.required_modifications:
                lines.append(f"- {m}")
            lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor.verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
