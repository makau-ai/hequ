# EWE Development Process — v1 draft

**Status:** draft, pending board review after EWE concept v3 APPROVE.
**Purpose:** define the formal, repeatable, MITRE-style process by
which each EWE / ECP / EOE / EMP entry enters the hequ.ai database,
under 4-phase board review, with interconnection discipline
comparable to CWE/CAPEC/ATT&CK/D3FEND.

This document is the operating manual for building the first 30
seed entries and every subsequent entry. It is not the schema
(that lives in EWE_SCHEMA.yaml) and not the concept doc (that
lives in the v3 board review). It is the procedure.

---

## Guiding principles

1. **One entry at a time, under board review.** No batch ingest.
   Every entry is a hypothesis that the board inspects before
   the ledger records it. The MITRE CWE team works exactly this
   way: each CWE goes through a review cycle before promotion
   from Incomplete → Draft → Stable.
2. **Interconnection before population.** Isolated entries are
   worthless. Before any entry is marked Stable, its
   `relationships` field (ChildOf, ParentOf, PeerOf, CanPrecede,
   CanFollow) must be populated against at least the already-
   existing entries. The graph grows densely, not as scattered
   leaves.
3. **Reproducibility as a first-class artifact.** Every EWE entry
   ships with a reproducible demonstrator (simulation script,
   dataset, or pointer to a published experiment) that exhibits
   the failure and at least one EMP mitigation.
4. **Citations are load-bearing.** Every EOE entry cites a
   primary source. Every EWE entry cites the canonical textbook
   and at least one derivation reference. Effectiveness claims
   in EMP cite their supporting dataset.
5. **No entry is stable without adversarial review.** Before
   Stable status, at least one board member must be asked to
   try to *break* the entry — find a misclassification, a
   missing edge case, an incorrect citation, a failed
   demonstrator. This is the red-team pass.

---

## Lifecycle states (mirrors CWE)

```
PROPOSED  →  INCOMPLETE  →  DRAFT  →  REVIEWED  →  STABLE  →  DEPRECATED?
```

- **PROPOSED** — an idea exists (a row from the
  critical_equations_complete.csv corpus with a rich Negation
  column, a historical incident, a board-suggested failure
  mode). No schema fields filled in beyond `id` and `title`.
- **INCOMPLETE** — M1 machine-checkable fields are being
  filled in but are incomplete. Cannot be indexed for RAG.
- **DRAFT** — all schema fields populated. Parser validates
  DOV-DSL inequalities, assumption_tags resolve to AAO,
  canonical_equation AST parses. Demonstrator exists and runs.
  Ready for board review.
- **REVIEWED** — 4-phase board review completed. Editor verdict
  is APPROVE or MODIFY-with-fixes-accepted. Relationships
  populated against all existing STABLE entries.
- **STABLE** — red-team adversarial pass completed. Indexed
  for RAG. Used in failure-investigation queries.
- **DEPRECATED** — superseded by a more specific entry, merged
  into a ChildOf parent, or the underlying equation removed
  from the corpus. Never deleted; kept with a `deprecated_by`
  forward pointer.

Transitions are logged to `discovery_ledger.jsonl` as
`kind: ewe_entry_transition` records, same ledger machinery
as canonical-problem and composite verifications.

---

## The per-entry authoring workflow

For each new EWE entry, the process is:

### Step 1 — Proposal (architect)

The architect drafts a one-paragraph proposal identifying:
- Source row in `critical_equations_complete.csv` or historical
  incident or board-suggested failure.
- Working title (e.g., "Newton II applied in rotating frame
  without pseudoforces").
- Candidate `ChildOf` parent in the existing graph.
- Candidate ECP class if this failure is composition-related.
- Estimated effort (schema-rich vs schema-sparse).

The proposal becomes the PROPOSED state record in the ledger.

### Step 2 — Schema population (architect, local CAS, AAO)

The architect fills in the full M1 machine-checkable schema:
- `canonical_equation` block: SymPy AST, OpenMath CDBase,
  variable dictionary with QUDT URIs.
- `domain_of_validity` block: inequalities in DOV-DSL grammar,
  named dimensionless groups, small parameters with error
  scaling orders.
- `boundary_conditions`, `frame_symmetry`, `assumption_tags`
  (each tag must resolve to the published AAO).
- `detection_methods` with algorithmic specs, preconditions,
  and an empirical false-positive rate estimate.
- `relationships` against all existing STABLE entries.

The DOV-DSL parser, the AAO validator, and the SymPy AST
typechecker are run. Any parse error blocks transition to DRAFT.

### Step 3 — Demonstrator (architect, sandboxed notebook)

A reproducible notebook is written that:
- Instantiates the equation in a state where the validity
  inequalities are **satisfied** and runs — correct behavior
  demonstrated.
- Instantiates it in a state where one inequality is
  **violated** — failure demonstrated, matching the entry's
  `demonstrative_examples` prose.
- Runs the `detection_methods` algorithm on the violating
  state and confirms it flags.
- Runs a proposed EMP mitigation if one exists and confirms
  recovery.

Notebook runs in the pinned Docker sandbox
(`python:3.12-slim@sha256:…`, `--network=none`, 60s cell
timeout). SHA-256 hash of the notebook is logged alongside the
entry. This is the reproducibility guarantee.

### Step 4 — 4-phase board review (all reviewers, Grok included)

The entry, the demonstrator notebook hash, the schema validation
result, and the relationship graph against existing entries are
bundled into a `submit_ewe_entry_to_board.py` payload. The board
evaluates on rubric:
- `schema_correctness` — does the AST parse, do the DOV-DSL
  inequalities evaluate, do the assumption_tags resolve?
- `physical_soundness` — is the described failure mode real?
- `citation_quality` — are the primary sources correctly
  attributed? Are the textbook references on the right page?
- `relationship_completeness` — are the ChildOf / PeerOf
  links well-justified? Is there a missing relationship to
  an existing entry?
- `demonstrator_validity` — does the notebook actually
  demonstrate what the entry claims?

Editor verdict is binding. REJECT sends back to DRAFT with the
required modifications. APPROVE promotes to REVIEWED. All four
reviewers must respond; partial quorum blocks promotion.

### Step 5 — Red-team pass (one board member, adversarial)

One board member (rotated round-robin) is asked in isolation to
try to break the entry:
- Find a counter-example where the validity inequalities are
  satisfied but the equation still fails.
- Find a primary source citation that contradicts the entry.
- Propose a PeerOf link the entry missed.
- Demonstrate the notebook fails to reproduce on a different
  sympy version or a different random seed.

If the red-team pass produces zero substantive findings, the
entry promotes to STABLE. Any substantive finding demotes it to
REVIEWED for fixes and a second red-team.

### Step 6 — Interconnection pass (validator, automatic)

When an entry reaches STABLE, an automatic validator runs across
the entire existing STABLE set and re-evaluates whether the new
entry creates:
- New ParentOf / ChildOf links from the existing STABLE entries
  to the new one (the new entry may be a useful parent for
  older entries — the graph re-layers).
- New PeerOf links based on shared AAO tags.
- New CanPrecede / CanFollow links for failure-mode chains
  (e.g., linearization_outside_validity CanPrecede
  numerical_instability_amplified_by_stiff_solver).

Any automatic relationship proposal over a confidence threshold
is surfaced to the architect for accept/reject. Accepted links
are added to BOTH endpoint entries atomically.

### Step 7 — Site publication

The STABLE entry renders to `/discovery/ewe/<id>` as a ledger-
sourced page, same pattern as `/discovery/canonicals` and
`/discovery/composites`. The page shows:
- The full schema.
- The relationship graph (with clickable neighbors).
- The demonstrator notebook (rendered, not executed).
- The board review record (all four reviewers, editor verdict).
- The red-team findings (none, or fixes applied).
- Citations with DOI / URL resolvers.

---

## Formal interconnection rules (MITRE-style)

CWE/CAPEC/ATT&CK/D3FEND maintain interconnection integrity via
a few simple, strict rules. v1 adopts them:

1. **Every STABLE entry has at least one ChildOf edge** (the
   root of the graph is the PROPOSED abstract class
   "Equation-misapplication failure").
2. **ParentOf and ChildOf are strict inverses.** Stored on both
   sides; writes are atomic.
3. **PeerOf is symmetric.** If A PeerOf B, then B PeerOf A.
4. **CanPrecede and CanFollow form a DAG.** No cycles allowed;
   a validator checks this at every ingest.
5. **Taxonomy_mappings must resolve** — QUDT, ISO 80000, textbook
   reference pages must be live URLs or canonical bibliographic
   identifiers.
6. **Deprecated entries keep their relationships** — a forward
   `deprecated_by` pointer replaces the entry but edges pointing
   at it are rewritten to the successor automatically.
7. **Relationship proposals from the automatic validator always
   go through architect review** — the graph is not auto-grown.

---

## Batch seeding order for the first 30 entries

Seed order matters because relationships get richer as the graph
grows. Proposed order, justified by dependency:

**Batch 0: root and taxonomy foundations (2 entries)**
1. EWE-000 "Abstract equation-misapplication failure" (class
   root, ChildOf nothing).
2. EWE-001 "Frame-dependent law misapplication" (ChildOf
   EWE-000; itself will be the parent of many rotating-frame
   entries).

**Batch 1: classical mechanics (8 entries)**
3. Newton II in rotating/accelerating frame without pseudoforces
4. Newton gravity in strong-field regime (GR takes over)
5. Hooke's law beyond linear elastic regime
6. Newton II with variable mass naively treated
7. Conservation of angular momentum applied to open system
8. Euler-Lagrange with non-holonomic constraints
9. Hamilton's equations on a singular Legendre transform
10. Point-particle approximation applied to extended body

**Batch 2: thermodynamics and transport (6 entries)**
11. Fourier heat law with anisotropic k
12. Fick diffusion outside dilute limit
13. Ideal gas law near critical point
14. Carnot efficiency claimed outside quasi-static limit
15. Equation-of-state extrapolation beyond calibration data
16. Boltzmann transport outside scale-separation regime

**Batch 3: electromagnetism and quantum (6 entries)**
17. Ohm's law on non-Ohmic conductors
18. Maxwell equations with explicit magnetic monopoles assumed absent
19. Ampère's law without Maxwell correction term
20. Schrödinger equation on strongly coupled / relativistic regime
21. Dipole approximation beyond near-field
22. Wavefunction collapse treated classically (measurement problem)

**Batch 4: chemistry / biology / fluids (5 entries)**
23. Arrhenius rate law at very low temperature (tunneling)
24. Lotka-Volterra with stochastic noise ignored
25. Navier-Stokes with compressibility ignored
26. Bernoulli applied along non-streamline
27. Reaction-diffusion with explicit spatial inhomogeneity ignored

**Batch 5: finance / crypto (3 entries, flagged HIGH-CAUTION)**
28. Black-Scholes with constant volatility assumed
29. RSA security assumed under classical factoring hardness
30. Lattice-based KEM (Kyber) with parameter choices below
    NIST Level-1 threshold

Each batch must complete fully (all entries reach STABLE,
interconnection pass executed) before the next batch begins.
This ensures the graph grows densely from the start.

---

## Failure modes of THIS process itself

The process above is itself subject to drift and corner-cutting.
Explicit anti-drift rules:

1. **No entry skips the red-team pass** even under schedule
   pressure. A STABLE entry without red-team is labeled
   REVIEWED, not STABLE.
2. **No entry skips the interconnection pass** — an isolated
   entry is worse than no entry.
3. **No entry is authored by a single architect without board
   review.** The architect cannot self-approve.
4. **No relationship is created by the automatic validator
   alone.** Architect must accept each.
5. **No citation is accepted without a live URL or canonical
   ID resolution check.**
6. **When the process itself conflicts with the five memory
   rules (no time estimates, no corner-cutting, Nobel rigor,
   all must respond, board is not a CAS), the memory rules
   win.**

---

## Open questions for the board (to be reviewed alongside this doc)

- Is the 7-step per-entry workflow the right shape, or is it
  too heavy? What could be skipped without loss of rigor?
- Is the batch seeding order sensible, or should the order be
  driven by a different criterion (e.g., prioritize equations
  whose failure modes are most commonly observed in real
  incidents, regardless of discipline)?
- Is the red-team pass strong enough, or does it need to be
  multi-reviewer (parallel adversarial pass from all four
  board members)?
- Should the relationship ontology be richer (add CanConfuseWith,
  HasAlternativeEquation, TransducesThrough) or stay lean?
- Is the CWE lifecycle (PROPOSED → INCOMPLETE → DRAFT → REVIEWED
  → STABLE → DEPRECATED) the right lifecycle, or should hequ
  add a WITHDRAWN state for entries that turn out to be wrong?
