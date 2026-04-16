"""Submit the MITRE-style Equation Weakness Enumeration (EWE/ECP/EOE/EMP)
concept to the AI consensus board via the four-phase protocol.

This is a concept review, not a design-doc review: the board is asked
whether the framework is (a) novel, (b) well-decomposed, (c) a real
improvement over free-text as a RAG substrate, and (d) worth building
out across the 136-equation corpus at critical_equations_complete.csv.

Grok is included per user instruction.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "EWE_CONCEPT_REVIEW.md"


_CONCEPT = """\
# Equation Weakness Enumeration (EWE) — Concept Review

## Motivation
The MITRE security family (CWE, CAPEC, ATT&CK, D3FEND) turned free-text
vulnerability knowledge into a structured, relationship-aware, machine-
readable corpus that became the standard RAG substrate for defensive
tooling. hequ.ai proposes the same decomposition for *scientific
equations and their failure modes* — the things that break when an
equation is applied outside its assumption envelope.

The hequ corpus today is a 136-equation free-text dataset
(critical_equations_complete.csv) with columns Formula, Assumptions,
Negation/Failure, Derivation, Working Example. It is readable but not
queryable. A RAG over it cannot answer "what goes wrong when Newton II
is applied in a rotating frame" without hallucination risk, because the
failure modes live in prose, not in structured relationships.

## Proposed four-layer decomposition (MITRE analog)
- **EWE — Equation Weakness Enumeration** (like CWE)
  Catalogs specific ways an equation can be wrong when misapplied:
  assumption violation, regime violation, dimensional inconsistency,
  boundary-condition mismatch, linearization outside validity, frame
  violation, etc. Each entry has id, abstraction, description,
  modes_of_introduction, common_consequences, demonstrative_examples,
  observed_examples, potential_mitigations, detection_methods,
  relationships (ChildOf/ParentOf/PeerOf other EWE entries),
  taxonomy_mappings (QUDT, ISO 80000, canonical textbook citations).

- **ECP — Equation Composition Patterns** (like CAPEC)
  Catalogs *how* two or more equations are combined. Each pattern is
  a named coupling template with parent equations, coupling tier
  (tier1_equivalence, tier2_structural, tier3_hierarchical),
  transducer reference, joint assumption set, and worked composite
  example. The Newton+Hooke SHO, Newton+Work-Energy, and Fourier+Fick
  Soret composites already built are the first three ECP entries.

- **EOE — Equation Observed Evidence** (like ATT&CK)
  Catalogs real historical misapplications: which experiment, which
  year, which community-level error, and which EWE entries were
  triggered. Example: Foucault pendulum (1851) as an EOE entry
  triggering EWE-001 (Newton II in non-inertial frame without
  pseudoforces). The Mercury perihelion anomaly triggering EWE-005
  (Newton gravity in strong-field regime). Each EOE has primary-
  source citations and explicit EWE → EOE mapping.

- **EMP — Equation Mitigation Playbook** (like D3FEND)
  Catalogs countermeasures: what detection check, what assumption
  test, what alternative equation to use, and what telltale signal
  indicates you need to migrate. Each EMP entry has effectiveness
  rating, cost, and explicit mapping back to the EWE it mitigates.

## Worked example (EWE-001)
EWE-001: "Newton II applied in a rotating or accelerating frame without
pseudoforces"
  Abstraction: Base
  Status: Draft
  Description: F = ma assumes an inertial frame. In a rotating/
    accelerating frame, observed motion requires adding Coriolis,
    centrifugal, and Euler pseudoforces; omitting them yields
    incorrect trajectories.
  Modes_of_introduction: implicit frame assumption in pedagogy;
    coordinate convenience trumping physics; copy-paste from
    inertial-frame derivations.
  Common_consequences: trajectory error proportional to Rossby
    number; systematic bias in ballistics/oceanography; false
    attribution of the error to measurement noise.
  Demonstrative_examples: ball dropped from 100m tower deflects ~2cm
    east at 45° latitude; artillery shell lands kilometers off target
    over long range.
  Observed_examples (EOE refs): Foucault pendulum (1851), WWI German
    long-range artillery (1918), Halley's trade-wind observations
    (1693), ocean gyre circulation.
  Potential_mitigations (EMP refs): EMP-001 (compute Rossby number,
    flag if Ro < 1), EMP-002 (switch to rotating-frame Lagrangian),
    EMP-003 (use GR in extreme cases).
  Detection_methods: Rossby number check; residual-after-fit test.
  Relationships: ChildOf EWE-000 (Frame-dependent law misapplication),
    PeerOf EWE-002 (Newton gravity in strong field).
  Taxonomy_mappings: QUDT Force, ISO 80000-4, Goldstein Ch 4,
    Landau-Lifshitz Mechanics §39.

## RAG substrate claim
A RAG over free-text Negation/Failure columns returns plausible
paragraphs. A RAG over a structured EWE + EOE + EMP graph returns:
"This experiment matches EOE-017 which triggers EWE-001; the
recommended mitigation is EMP-002 with 0.94 historical effectiveness,
see [primary source]." That is the substrate upgrade.

## Proposed Phase 14 MVP scope
- Define schemas (JSON Schema + YAML frontmatter) for EWE, ECP, EOE,
  EMP entries.
- Seed 30 EWE entries drawn from the 136-equation corpus (focus on
  equations with richest Negation/Failure prose: Newton II, Newton
  gravity, Ohm, Fourier, Fick, Maxwell, Bernoulli, ideal gas,
  Arrhenius, Schrödinger).
- Seed 10 EOE entries from known historical incidents.
- Seed 10 EMP entries cross-linked to the EWE seeds.
- Index with chromadb or similar; wire into
  framework.failure_investigation.run_literature_prior_search().
- Site page /discovery/ewe rendered from the ledger, same pattern
  as /discovery/canonicals and /discovery/composites.

## Questions for the board
1. **Prior art**: Does a structured weakness/failure catalog for
   scientific equations already exist? Candidates to rule in/out:
   QUDT (vocabulary, not failure modes), ISO 80000 (definitions,
   not failure modes), NIST fundamental constants, CSDMS Standard
   Names (earth-system variables, not weaknesses), SBML/CellML
   (biological model exchange, not misapplication catalog),
   Modelica Standard Library (component reuse, not failure modes),
   MathWorld / DLMF (formula libraries, not weakness enumeration).
   Is any of these already doing what EWE proposes? Is there
   something in the physics-informed ML / benchmarking literature
   (AI Feynman, SciBench, PDE benchmarks) that overlaps? Is there
   an ontology in the philosophy-of-science or model-validation
   literature (V&V, NASA-STD-7009, ASME V&V 40, Oreskes 1994) that
   already covers this?
2. **Decomposition**: Is the four-layer CWE/CAPEC/ATT&CK/D3FEND
   mapping (EWE/ECP/EOE/EMP) the right decomposition, or is there
   a cleaner one for equations specifically?
3. **Schema shape**: Is the CWE-style field set (abstraction,
   relationships, modes_of_introduction, consequences, observed
   examples, mitigations, detection_methods, taxonomy_mappings)
   the right schema, or do equations need different fields
   (e.g. dimensional signature, regime bounds, order-of-magnitude
   of the small parameter)?
4. **RAG substrate**: Does the structured graph meaningfully
   outperform a well-embedded free-text corpus for the hequ use
   case (finding the right equation, the right failure mode, and
   the right mitigation given an observed anomaly), or is it a
   lot of hand-authoring work for a marginal retrieval gain?
5. **Corpus scale**: The hequ corpus is 136 equations. Should we
   aim to cover all 136 in EWE (with sparse entries for well-
   behaved equations), or only the ~30 equations that have rich
   failure-mode prose? Does "complete coverage" matter or does
   "rich coverage of high-leverage equations" matter more?
6. **Integration**: Should EWE be its own artifact class in the
   labs_v2 ledger (alongside canonical_problem_verification and
   composite_verification), or should it be attached to the
   existing equation.yaml files as an embedded section?
7. **Fatal flaws**: What are we missing? What is the strongest
   argument against building this at all?

Verdict requested: APPROVE / MODIFY / REJECT, with specific
attention to prior art and decomposition correctness.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of EWE concept "
                  "(Grok included, ~10 model calls, ~5-8 minutes)...")
            result = board.four_phase_query(
                query_id="ewe_concept_review_v1",
                review_subject=(
                    "a proposed MITRE-style structured knowledge "
                    "framework (EWE/ECP/EOE/EMP) for scientific "
                    "equations and their failure modes, as a RAG "
                    "substrate for the hequ.ai discovery engine"
                ),
                user_payload=_CONCEPT,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# EWE Concept Review — 4-Phase Academic Protocol\n")
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
            lines.append("**Required modifications:**")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
