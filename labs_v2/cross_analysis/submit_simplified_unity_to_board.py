"""Submit the simplified unity-of-equations proposal to the
4-phase review board.

After six rounds of iterating on the MITRE-analog four-layer
framework (EWE/ECP/EOE/EMP), the honest conclusion is that
the four-layer framing was over-engineered for hequ.ai's
actual use case. This submission collapses the proposal to
TWO concrete things, both built from data that already
exists in the project:

  1. ONE schema addition — a `failure_modes` block embedded
     in each existing equation.yaml (not a parallel catalog),
     carrying the machine-checkable validity-envelope work
     from EWE v6 that genuinely earned its design.

  2. ONE tangible graph artifact — unity_map.yaml, generated
     automatically from the existing I-ADOPT descriptors in
     every equation.yaml, listing descriptor tuples shared
     across two or more equations. These are the tier-1
     equivalence candidates — the places where cross-domain
     composites can be built.

The tangible validation: the unity map, run against the 16
equations currently in the corpus, auto-rediscovers exactly
the two composites we already independently verified as
working (Newton+Hooke on Force/rigid_body, Newton+WorkEnergy
on Mass/rigid_body). Ground-truth confirmation that the
descriptor-matching machinery is already detecting real
coupling structure before any schema expansion.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "SIMPLIFIED_UNITY_REVIEW.md"


_CONCEPT = """\
# Simplified Unity-of-Equations Proposal — Board Review

## Context — what we're walking back from

Over the last six rounds I submitted increasingly elaborate
versions of a MITRE-analog framework (EWE / ECP / EOE / EMP),
treating the four-layer decomposition as fixed architecture.
Each round closed old concerns and surfaced new ones at finer
resolution. v6 reached rubric 4.80–5.00 but was still MODIFY,
and the residual concerns were textbook-citation polish, not
structural defects.

An honest re-read tells me the four-layer framing was my
framing, not a requirement. MITRE has four catalogs because
it has four stakeholder communities (developers / attackers
/ defenders / detectors). hequ.ai has one stakeholder: the
discovery engine, and the human reading its output. One
catalog is enough. Four parallel catalogs with cross-links,
lifecycle states, provenance grades, and inter-annotator
agreement protocols was substantially more machinery than
the problem requires.

This submission collapses the proposal to **two concrete
things**, both grounded in data that already exists in the
repository.

---

## Proposal 1 — One schema addition, embedded in equation.yaml

Every equation in the corpus already has a rich
`equation.yaml` with I-ADOPT descriptors on each variable
(`property`, `object_of_interest`, `context`, `constraint`),
units, dimensions, assumptions, and derivations. The only
missing piece is structured failure-mode data: right now,
the 136-equation CSV has a free-text `Negation/Failure`
column but the `equation.yaml` files don't carry that
content at all.

Add a `failure_modes` block to each `equation.yaml`:

```yaml
# Added to existing equation.yaml files (sibling of `variables`,
# `assumptions`, `derivation_from`, etc.)
failure_modes:
  - id: F1
    name: "applied in rotating/accelerating frame without pseudoforces"
    assumption_violated: "inertial_frame"
    validity_envelope:
      # DOV-DSL inequalities over dimensionless groups or state
      inequalities:
        - "Ro := U / (f * L) >= 1"    # Rossby number ≥ 1
      named_groups:
        Ro: {definition: "U / (f * L)", dimensionless: true}
    detection:
      algorithm: "compute Rossby number Ro; flag if Ro < 1"
      preconditions: "U, f, L observable"
    use_instead:
      target_equation: EQ-NEWTON-II-ROTATING
      reason: "rotating-frame formulation with explicit
               Coriolis, centrifugal, Euler terms"
    historical_example:
      # OPTIONAL — not required for the entry to be valid
      description: "Foucault pendulum (Panthéon, Paris, 1851)"
      citation: "Foucault, L. (1851). Comptes Rendus 32, 135."
      evidence_level: primary_experiment
```

That's the whole schema. Roughly twenty lines of YAML per
failure mode, nested inside a file that already exists.

**What it replaces from the v6 EWE framework:**
- The machine-checkable validity envelope (inequalities over
  dimensionless groups) is carried forward. This is the
  part that genuinely earned its six rounds of design.
- `detection.algorithm` replaces the separate EMP catalog.
- `use_instead` replaces the EMP `alternative` field.
- `historical_example` replaces the entire EOE catalog,
  collapsed to an optional field on a failure mode.
- The lifecycle-state machine, red-team pass, relationship
  graph, automatic interconnection validator, and batch
  seeding order are all dropped. A failure mode is either
  present in `equation.yaml` or it isn't.
- ECP composition classes (CONSERVATION_BALANCE,
  INTER_DOMAIN_TRANSDUCTION, RATE_COUPLING,
  STOCHASTIC_COUPLING, etc.) don't belong on individual
  equations at all. They describe how *composites* are
  built, which means they live in `composite.yaml`, not
  here. That machinery is already in place in
  `labs_v2/composites/`.

**What this does NOT try to do:**
- No cross-equation relationship graph. Failure modes are
  local to their equation. If two equations share a failure
  mode category, that's visible through the descriptor match
  on the validity-envelope variables — i.e., through
  Proposal 2.
- No inter-annotator agreement protocol. Each failure mode
  cites a primary source; the architect is responsible for
  accuracy.
- No lifecycle states. An entry is either in the file or
  not in the file. If it's wrong, fix it in a commit.

---

## Proposal 2 — One tangible graph artifact, generated from
## existing data

The `unity_map.yaml` artifact already exists. I wrote the
generator (`labs_v2/cross_analysis/build_unity_map.py`)
while preparing this submission and ran it against the
current 16-equation corpus. The script reads every
`equation.yaml`, extracts each variable's I-ADOPT descriptor
tuple `(property_uri, object_of_interest)`, and groups
variables that share the same tuple across two or more
equations. Those groups are the tier-1 equivalence
candidates — the exact places where cross-domain composites
can be built.

**What it actually found (real output, not a mockup):**

```
Equations scanned:   16
Coupling candidates: 2

Top candidates (by number of equations sharing the descriptor):
  Mass   / rigid_body   n=2  [EQ-NEWTON-II, EQ-WORK-ENERGY]
  Force  / rigid_body   n=2  [EQ-HOOKE,      EQ-NEWTON-II]
```

**The crucial validation:** those two candidates are the
exact two composites we have already independently verified
through the Phase 13 pipeline:

- **CMP-NEWTON-HOOKE-SHO-001** — Newton + Hooke, coupled on
  `Force / rigid_body` → simple harmonic oscillator with
  period `T = 2π√(m/k)`. Verified numerically, symbolically,
  and against textbook reference. Ledger record exists.
- **CMP-NEWTON-WORKENERGY-001** — Newton + Work-Energy,
  coupled on `Mass / rigid_body` → `W = F·d = (1/2)m(v_f² −
  v_i²)`. Verified. Ledger record exists.

The unity-map script, running purely on descriptor metadata
with zero hand-tuning, independently rediscovers 2-of-2 of
the couplings that the Phase 13 pipeline already built. No
false positives and no false negatives on the current
corpus. This is strong evidence that the descriptor
machinery is already detecting real coupling structure —
which is the whole thesis of hequ.ai.

**What the artifact looks like (from the actual output file):**

```yaml
generated_from: equations
n_equations: 16
n_coupling_candidates: 2
rule: "Variables from different equations whose I-ADOPT
       descriptor tuple (property URI, object_of_interest)
       matches are tier-1 equivalence candidates — the
       places where a cross-domain composite can be built."
equations_in_corpus:
  - EQ-ARRHENIUS
  - EQ-BAYES
  - EQ-BEER-LAMBERT
  - EQ-BLACK-SCHOLES
  - EQ-EULER-LAGRANGE
  - EQ-FICK-DIFFUSION
  - EQ-FOURIER-HEAT
  - EQ-HOOKE
  - EQ-LORENTZ-FACTOR
  - EQ-LOTKA-VOLTERRA
  - EQ-NAVIER-STOKES
  - EQ-NEWTON-II
  - EQ-OHM
  - EQ-SCHRODINGER
  - EQ-SHANNON-ENTROPY
  - EQ-WORK-ENERGY
coupling_candidates:
  - descriptor_key:
      property: Mass
      property_uri: http://qudt.org/vocab/quantitykind/Mass
      object_of_interest: rigid_body
    n_equations_sharing: 2
    occurrences:
      - {equation: EQ-NEWTON-II,    domain: classical_mechanics, variable: m}
      - {equation: EQ-WORK-ENERGY,  domain: classical_mechanics, variable: m}
  - descriptor_key:
      property: Force
      property_uri: http://qudt.org/vocab/quantitykind/Force
      object_of_interest: rigid_body
    n_equations_sharing: 2
    occurrences:
      - {equation: EQ-HOOKE,        domain: classical_mechanics, variable: F_spring}
      - {equation: EQ-NEWTON-II,    domain: classical_mechanics, variable: F}
```

**This is the "tangible example of how to explore the
connectedness" the framework was missing.** Not an abstract
schema, not a hypothetical benchmark — a deterministic,
reproducible script that reads real data from the current
repository and emits a real ranked list of tier-1 coupling
candidates.

---

## What the two proposals mean together

- Proposal 1 tells each equation where its **envelope**
  breaks and what lives on the other side of the break.
- Proposal 2 tells us which equations are **connected** to
  each other through shared conceptual variables, generating
  the coupling-candidate graph from pure descriptor metadata.

When you sit the two together you get the hequ.ai thesis in
operational form:
1. Every equation is bounded (Proposal 1 makes the bound
   explicit and machine-checkable).
2. Every equation is connected (Proposal 2 makes the
   connections visible and testable).
3. Cross-domain discovery is the process of asking: at the
   boundary where equation A breaks (from its failure
   modes), does equation B — connected to A through a
   matched descriptor from the unity map — extend into that
   regime?

This is also how the Failure Investigation Protocol's
`run_literature_prior_search` step becomes concrete: when
a canonical problem fails verification, the runner reads
the failed equation's `failure_modes` block AND the
unity_map entries where that equation participates, and the
board is asked "does any of this explain the residual?"
No parallel catalog required.

---

## What is being dropped from the previous six rounds

- **EWE catalog** (as a parallel artifact) — content merged
  into `equation.yaml.failure_modes` per Proposal 1.
- **ECP catalog** — not needed; composition class lives on
  `composite.yaml` in `labs_v2/composites/`.
- **EOE catalog** — collapsed to an optional
  `historical_example` field on each failure mode.
- **EMP catalog** — collapsed to `detection.algorithm` and
  `use_instead` fields on each failure mode.
- **Lifecycle states** (PROPOSED → DRAFT → STABLE → …) —
  replaced by git history. A failure mode is either
  committed or not.
- **7-step authoring workflow with red-team pass** —
  replaced by ordinary PR review of commits to
  `equation.yaml` files.
- **Batch seeding order with 6 batches of ~30 entries** —
  replaced by "add failure modes opportunistically as we
  encounter real needs in composite verification and
  failure investigation."
- **JSON Schema validator for a parallel catalog** — replaced
  by a small schema addition to the existing
  `equation_schema.yaml` (wherever that lives) validating the
  `failure_modes` block structure.
- **Four-class ECP partition with decision tree and
  UNCLASSIFIED escape hatch** — stays where it already is,
  on composite.yaml, and only applies when we build a real
  composite. No parallel design doc.
- **All the heavy stochastic / modulated-Dirac / singularity
  / tensor-index machinery** — also stays attached to
  composite.yaml and fires only when a real composite hits
  those cases. The specs from v5 and v6 are archived as
  reference material for future composites, not promoted to
  required artifacts.

---

## Questions for the board

1. **Is this simplification correct?** Is there anything
   from the previous six rounds of EWE/ECP/EOE/EMP that the
   board believes cannot be collapsed into the
   `failure_modes` block plus the `unity_map.yaml` graph?
   If so, what and why?
2. **Is the tangible validation convincing?** The unity-map
   script auto-rediscovers 2-of-2 of the verified composites
   on the current 16-equation corpus. Does the board accept
   this as evidence that the descriptor-matching machinery
   is already detecting real coupling structure, or does the
   small corpus size leave room for a false-positive rate
   we can't estimate? What should the framework do
   differently if the corpus grows to 30, 50, 136 equations
   and the false-positive rate diverges?
3. **Is the `failure_modes` schema shape right?** Five
   fields per entry: `name`, `assumption_violated`,
   `validity_envelope`, `detection`, `use_instead`, plus
   optional `historical_example`. Is there a sixth field
   that is load-bearing for the use case? Or is one of the
   five redundant?
4. **Should the unity map be generated on every commit,
   or on demand?** Current plan: run
   `build_unity_map.py` on every `equation.yaml` change,
   commit the resulting `unity_map.yaml` as an artifact, and
   diff it in review so new couplings show up naturally in
   the git log. Is there a better pattern?
5. **Is there a second tangible example** the board wants
   to see before concept lock — e.g., an "energy unity map"
   showing all equations that reference Energy, or a
   validity-envelope worked example showing the `failure_
   modes` block authored for ONE real equation (Newton II)
   and how it catches a contrived out-of-envelope input?
6. **Fatal flaws in the simplification:** what am I missing
   by collapsing the four-layer framework to this? Is there
   a real use case I've accidentally orphaned?

**Verdict requested: APPROVE / MODIFY / REJECT.** The goal
is a clean APPROVE so we can stop concept review and start
authoring real content. If the verdict is MODIFY, the board
is asked to state what single concrete change would flip it
to APPROVE, so the next round can make exactly that change
without drift.

---

## What happens immediately after APPROVE

1. Add a `failure_modes` block to `labs_v2/equations/
   classical_mechanics/EQ-NEWTON-II/equation.yaml` —
   populated with the Rossby / rotating-frame failure mode
   as the first real entry. Sympy-verified before commit
   per Rule A9.
2. Wire `build_unity_map.py` into the pre-commit / CI path
   so `unity_map.yaml` is regenerated automatically and
   committed alongside any change to an `equation.yaml`.
3. Run the Phase 14 MVP with just those two changes as the
   entire "EWE system." Stop when we have five
   `failure_modes` entries committed across the corpus
   without needing a seventh round of the framework design.
4. Return to Phase 13 composite work with Newton + Ohm DC
   motor (electromechanical) and the other queued
   composites.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of the simplified "
                  "unity-of-equations proposal "
                  "(Grok included, ~12 model calls, ~6-10 minutes)...")
            result = board.four_phase_query(
                query_id="simplified_unity_review_v1",
                review_subject=(
                    "a simplified unity-of-equations proposal that "
                    "collapses the six rounds of EWE/ECP/EOE/EMP "
                    "concept design into two concrete artifacts: "
                    "(1) a failure_modes block embedded in each "
                    "existing equation.yaml, and (2) a "
                    "unity_map.yaml graph generator that "
                    "auto-identifies tier-1 coupling candidates "
                    "from existing I-ADOPT descriptor metadata. "
                    "The unity_map script, run on the current "
                    "16-equation corpus, auto-rediscovers 2-of-2 "
                    "of the composites that have already been "
                    "independently verified through the Phase 13 "
                    "pipeline — ground-truth confirmation that "
                    "the descriptor-matching machinery is already "
                    "detecting real coupling structure before any "
                    "schema expansion."
                ),
                user_payload=_CONCEPT,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# Simplified Unity-of-Equations Review — "
                 "4-Phase Academic Protocol\n")
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
