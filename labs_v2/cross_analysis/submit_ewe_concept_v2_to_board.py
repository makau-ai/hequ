"""Submit the EWE/ECP/EOE/EMP concept v2 to the AI consensus board.

v2 incorporates the 5 required modifications from the v1 review:
  M1 — machine-checkable fields (SymPy AST, QUDT units, dimless
       validity inequalities, small-parameter error scaling,
       BCs, frame/symmetry invariances)
  M2 — Assumption/Approximation Ontology (enumerated tags)
  M3 — ECP formal semantics (conservation / constitutive /
       transduction, with pre/post-conditions and port-Hamiltonian
       connector types)
  M4 — EOE/EMP provenance grading + algorithmic detection specs
  M5 — Pre-registered RAG evaluation protocol with gold set,
       baselines, metrics, ablations, and inter-annotator agreement

Also adds a cryptographic-equation sub-appendix: the compute-
regime equations (RSA/ECDLP/lattice-SVP/AES) break the v5
"local CAS computes reference value in <1s" assumption, so the
verification pipeline needs a distinct path for them.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "EWE_CONCEPT_REVIEW_V2.md"


_CONCEPT_V2 = """\
# Equation Weakness Enumeration (EWE) v2 — Board Review

## Context from v1
v1 was reviewed by the 4-phase board (Claude, OpenAI, Gemini,
Grok). Substantive verdict: 3 MODIFY + 1 APPROVE, unanimous on
novelty and soundness. Claude's Phase A failed due to a truncation
bug (max_tokens=2048 cut the JSON mid-response); that has been
fixed (bumped to 8192) for this v2 pass. The 5 required
modifications from v1 are addressed below, each explicitly tagged.

## Thesis (unchanged)
Scientific equations fail when applied outside their assumption
envelope. Those failures live in prose today. EWE/ECP/EOE/EMP
turns them into a structured, machine-checkable knowledge graph
that serves as a RAG substrate for hequ.ai's discovery engine,
by analogy with MITRE's CWE/CAPEC/ATT&CK/D3FEND.

## M1 — Machine-checkable fields in every EWE entry

Every EWE entry carries:

```yaml
id: EWE-001
canonical_equation:
  sympy_ast: "Eq(F, m*a)"
  openmath_cdbase: "http://www.openmath.org/cd/physics1.ocd"
  variables:
    F: {qudt: "qudt:Force",         role: dependent}
    m: {qudt: "qudt:Mass",          role: parameter}
    a: {qudt: "qudt:Acceleration",  role: state}
domain_of_validity:
  inequalities:
    - "Ro := U / (f * L) >= 1"       # Rossby number, inertial>Coriolis
    - "|v| / c < 0.1"                # non-relativistic
    - "a / (g * sin(theta_max)) < 1" # small-tilt pseudoforce bound
  small_parameters:
    - {name: "beta := v/c", error_scaling: "O(beta**2)"}
    - {name: "epsilon := omega*L/c", error_scaling: "O(epsilon**2)"}
boundary_conditions:
  - "inertial frame or explicit pseudoforce terms included"
frame_symmetry:
  frames: ["inertial"]
  galilean_invariant: true
  rotation_invariant: false
assumption_tags:
  - continuum_limit
  - weak_coupling
  - classical_regime
detection_methods:
  - id: DET-001
    algorithm: "compute Rossby number Ro = U/(fL); flag if Ro < 1"
    preconditions: "U, f, L all observable"
    false_positive_rate: 0.03  # empirical, from benchmark
relationships:
  ChildOf: EWE-000  # frame-dependent-law misapplication
  PeerOf: [EWE-002, EWE-003]
```

This is the minimum machine-readable record. No entry ships without
the canonical_equation / domain_of_validity / assumption_tags
blocks. A validator enforces this.

## M2 — Assumption / Approximation Ontology (AAO)

Enumerated, not free-text. Each tag has a formal definition and
at least one canonical reference. v2 seeds these 24 tags:

```
linearization               small_displacement
continuum_limit             ideal_gas
weak_coupling               dilute_limit
local_thermodynamic_equilib quasistatic
Markovianity                detailed_balance
scale_separation            ergodicity
classical_regime            non_relativistic
inertial_frame              isotropic_medium
homogeneous_medium          incompressible
inviscid                    adiabatic
isothermal                  mean_field
point_particle              rigid_body
```

Every EWE entry's `assumption_tags` must draw from this ontology.
Adding a new tag requires board review. The tag graph itself
carries ChildOf/PeerOf relationships — linearization ChildOf
small_displacement, mean_field ChildOf weak_coupling, etc.

## M3 — ECP formal semantics

Composition patterns classify into three **disjoint**, typed
categories with explicit pre/post-conditions:

1. **CONSERVATION_BALANCE** — two equations share a conserved
   quantity. Pre: compatible conserved quantity with identical
   QUDT type on both sides. Post: total-quantity balance equation
   is dimensionally consistent.
2. **CONSTITUTIVE_CLOSURE** — one equation provides the constitutive
   relation that closes the other's unknown. Pre: free variable
   in eq_a is the dependent variable of eq_b. Post: closed system
   has rank equal to number of state variables.
3. **INTER_DOMAIN_TRANSDUCTION** — two equations in different
   physical domains coupled by a port-Hamiltonian element.
   Pre: named transducer exists in TRANSDUCER-LIBRARY; effort
   and flow port types match on both sides; Dirac structure
   is power-conserving. Post: power balance equation
   `e·f = ė·ḟ` holds to machine precision in a unit test.

Each ECP entry specifies `port_mapping` using effort/flow variable
types (mechanical: force/velocity; electrical: voltage/current;
thermal: temperature/entropy-flow; hydraulic: pressure/volume-flow).
Transformers and gyrators are first-class.

ECP failures are NOT just unions of EWE triggers. An ECP-level
failure has a schema field `coupling_residual_class` with values:
`port_type_mismatch`, `non_power_conserving_junction`,
`missing_transducer`, `conserved_quantity_leak`. This is the
sharp boundary Gemini asked for.

## M4 — EOE / EMP provenance grading

Each EOE entry:

```yaml
id: EOE-017
ewe_refs: [EWE-001]
experiment: "Foucault pendulum at Panthéon, Paris"
year: 1851
primary_source: "Foucault, L. (1851). Comptes Rendus 32, 135-138."
evidence_level: primary_experiment  # enum: primary_experiment |
                                    # replication | meta_analysis |
                                    # textbook_consensus
mapping_confidence: 0.98            # independent board evaluation
mapping_notes: "Direct demonstration of rotating-frame inertial
  effects; historically the first unambiguous observation."
inter_annotator_agreement:
  raters: 4
  cohens_kappa: 0.94
```

Each EMP entry:

```yaml
id: EMP-002
mitigates: [EWE-001]
detection:
  algorithm: |
    def detect(state):
        Ro = state.U / (state.f * state.L)
        return Ro < 1.0
  preconditions: "U, f, L known"
  complexity: "O(1)"
effectiveness:
  point_estimate: 0.94
  ci_low: 0.89
  ci_high: 0.97
  n_cases: 147
  dataset: "HEQU-EOE-MVP-v1"
cost:
  authoring: low
  runtime: constant
```

Effectiveness estimates without a cited dataset are rejected.

## M5 — Pre-registered RAG evaluation protocol

Before EWE is accepted as a RAG substrate, it must beat a strong
free-text baseline on a **pre-registered** benchmark. The protocol:

**Gold set (HEQU-BENCH-001):**
- 300 diagnostic queries, each labeled with gold EWE id(s), gold
  EMP id(s), and ±1 mapping confidence annotated by ≥3 humans.
- Query types: (i) observed-anomaly descriptions ("ball dropped
  from 100m tower lands 2cm east"), (ii) regime descriptors
  ("v=0.3c, classical treatment"), (iii) composition failures
  ("Newton II applied to relativistic cart"), (iv) honest-unknown
  decoys (queries with NO matching EWE — system must refuse).
- Inter-annotator agreement Cohen's κ ≥ 0.80 on EOE↔EWE mappings
  before the set is sealed.

**Systems compared:**
- A — Structured-graph RAG over EWE/ECP/EOE/EMP
- B — Free-text embedding baseline over the same prose, using
      a strong commodity embedder (e.g., text-embedding-3-large)
- C — Ablated structured RAG with ONLY prose fields enabled
      (no canonical_equation, no domain_of_validity inequalities,
      no assumption_tags, no port types) — isolates the marginal
      value of the machine-checkable fields.

**Metrics:**
- Top-1 and Top-5 accuracy on EWE id retrieval
- MRR (mean reciprocal rank)
- Calibration: Brier score and reliability diagram
- Refusal precision on honest-unknown decoys (System must not
  return a confident match for a query outside its ontology)
- Ablation delta A − C (MUST be positive and statistically
  significant at p < 0.01, else the machine-checkable fields
  are not earning their complexity cost)

**Pass condition:**
A must beat B on at least 3 of {Top-1, Top-5, MRR, calibration}
by margins exceeding two SE, AND A − C must be positive-significant.
If EITHER gate fails, the structured-graph approach is retracted
and we fall back to free-text RAG with explicit loss-report to
the user. This is a falsifiable commitment.

## Phase 14 MVP scope (revised)

1. Publish the AAO (24 tags, formal definitions, references).
2. Publish JSON Schema for EWE/ECP/EOE/EMP with M1 fields required.
3. Seed 30 EWE entries from the 136-equation hequ corpus
   (critical_equations_complete.csv). Prioritize the ~20 equations
   with the richest Negation/Failure prose. Cover Newton II,
   Newton gravity, Ohm, Fourier, Fick, Maxwell, Bernoulli,
   ideal gas, Arrhenius, Schrödinger, Hooke, Navier-Stokes,
   Carnot, Boltzmann transport, Lotka-Volterra, Black-Scholes
   first.
4. Seed 10 EOE entries with primary-source citations.
5. Seed 10 EMP entries with algorithmic detection.
6. Seal HEQU-BENCH-001 (300 queries, ≥3 annotators).
7. Run the pre-registered evaluation. Report results regardless
   of outcome.
8. Wire EWE into framework.failure_investigation.run_literature_
   prior_search() only if the pre-registered evaluation passes.
9. Publish /discovery/ewe site page with ledger-sourced content.

## Cryptographic-equation sub-appendix

The hequ corpus will add cryptographic equations (RSA factoring,
ECDLP, lattice-SVP, AES S-box ANF, Shor's algorithm resource
estimates). These break v5's "local CAS computes reference value
in <1s" assumption and must be handled with a distinct regime:

**Compute-regime classification:**
- `REGIME-TRACTABLE` — closed-form or ≤1s CAS evaluation. Current
  v5 pipeline applies unchanged. All 136 current corpus equations.
- `REGIME-HEAVY` — polynomial-time but wall-clock >1s (e.g.,
  Shor resource estimate for RSA-2048 requires >10000 logical
  qubits; AES S-box Gröbner basis computation). Reference values
  come from published benchmarks (NIST, eBACS, ANSSI, NSA Suite B
  documents), not on-the-fly CAS. Verification pipeline substitutes
  "literature citation + multi-source cross-check" for Check A/B/C.
- `REGIME-INFEASIBLE` — exponential-time without known shortcut
  (classical RSA-2048 factoring, ECDLP on standardized curves).
  These cannot be "verified" in the classical sense; EWE entries
  treat `computational_infeasibility_assumption` as a first-class
  AAO tag, and the failure mode is "adversary has sufficient
  classical or quantum resources to violate the infeasibility
  assumption." No reference-value computation is attempted.

**New AAO tags for the crypto regime:**
- `computational_infeasibility_assumption`
- `random_oracle_model`
- `standard_model_security`
- `indistinguishability_IND_CPA`
- `indistinguishability_IND_CCA2`
- `post_quantum_hardness_LWE`
- `post_quantum_hardness_SIS`

**Distinct ECP pattern for crypto composites:**
`CRYPTO_REDUCTION` — when protocol security reduces to a hardness
assumption. Pre: reduction is tight or concrete. Post: advantage
bound proven in a specified model. Pre/post conditions here are
proof-theoretic, not power-conserving.

**Caution:** these equations MUST NOT be run in the container
sandbox for reference-value computation. The sandbox is sized for
<1s sympy/mpmath jobs. Attempting to factor RSA-2048 in the
sandbox would hit the 60s cell timeout and abort with no useful
signal. The runner has to route REGIME-HEAVY and REGIME-INFEASIBLE
equations to the literature-citation path from the outset.

## Questions for the board (v2)

1. Are the M1–M5 modifications sufficient to address the v1
   concerns, or is there a gap that still needs closing before
   build starts?
2. Is the AAO seed set of 24 tags the right vocabulary, or are
   there must-have additions / removals? Gemini and OpenAI are
   asked specifically because the tag list is the ontological
   foundation.
3. Is the three-way disjoint ECP classification (CONSERVATION_
   BALANCE / CONSTITUTIVE_CLOSURE / INTER_DOMAIN_TRANSDUCTION)
   exhaustive? Is there a fourth class we are missing? Specifically:
   does it handle signal-flow coupling (non-power-conserving
   block-diagram coupling) correctly, or does that need its own
   category?
4. Is HEQU-BENCH-001 (300 queries, 3 annotators, κ ≥ 0.80)
   sufficient as a pre-registered evaluation, or is the sample
   size / annotator count too thin to make the pass/fail decision
   credible?
5. Is the crypto sub-appendix approach (three compute regimes,
   literature citations for REGIME-HEAVY/INFEASIBLE, new AAO tags,
   CRYPTO_REDUCTION ECP) sound? Specifically: is there a way to
   handle post-quantum lattice equations (Kyber, Dilithium) that
   is cleaner than what's proposed?
6. Fatal flaws still remaining: what should the board flag that
   v2 still misses?

Verdict requested: APPROVE / MODIFY / REJECT, with per-question
specificity.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of EWE concept v2 "
                  "(Grok included, ~12 model calls, ~6-10 minutes)...")
            result = board.four_phase_query(
                query_id="ewe_concept_review_v2",
                review_subject=(
                    "v2 of the EWE/ECP/EOE/EMP structured knowledge "
                    "framework for scientific equations, addressing "
                    "the 5 required modifications from the v1 review "
                    "and adding a cryptographic-equation compute-"
                    "regime sub-appendix"
                ),
                user_payload=_CONCEPT_V2,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# EWE Concept Review v2 — 4-Phase Academic Protocol\n")
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
