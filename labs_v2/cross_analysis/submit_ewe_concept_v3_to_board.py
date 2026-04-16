"""Submit EWE/ECP/EOE/EMP concept v3 to the 4-phase review board.

v3 addresses the 5 required modifications from the v2 review:
  M1 — 4th ECP class RATE_COUPLING for non-power-conserving
       composition (Lotka-Volterra, Boltzmann transport,
       Black-Scholes), with disjoint pre/post-conditions and
       a coverage proof across the 16 seed equations.
  M2 — Formal BNF grammar (DOV-DSL) for domain-of-validity
       inequalities, parseable against the canonical_equation
       SymPy AST with a defined variable-binding mechanism.
  M3 — Corrected Dirac-structure postcondition for
       INTER_DOMAIN_TRANSDUCTION: skew-symmetric interconnection
       matrix J with machine-verifiable assertion x^T J x = 0.
  M4 — CRYPTO_REDUCTION formal fields: reduction type, tightness
       (advantage-loss factor), security model, machine-checkable
       advantage bound.
  M5 — Calibration (Brier) promoted to hard gate in HEQU-BENCH-001,
       separate from the fungible-metrics tier.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "EWE_CONCEPT_REVIEW_V3.md"


_CONCEPT_V3 = """\
# EWE Concept v3 — Board Review

## Context
v2 was reviewed by the 4-phase board. Editor verdict: MODIFY.
All four reviewers responded (Claude max_tokens bug fixed).
Rubric means: 4.20–4.60. Required modifications converged on
five items. v3 addresses each of them below. Everything from v2
not listed here is unchanged (M1 machine-checkable fields,
M2 AAO 24-tag ontology, M4 EOE/EMP provenance grading, crypto
sub-appendix's three-regime model).

---

## C1 — Fourth ECP class: RATE_COUPLING

The v2 three-class ECP scheme (CONSERVATION_BALANCE,
CONSTITUTIVE_CLOSURE, INTER_DOMAIN_TRANSDUCTION) is not
exhaustive. Lotka-Volterra (prey birth rate coupled to predator
population), Boltzmann transport (collision integrals coupling
species via cross-sections), and Black-Scholes (volatility
coupled to underlying via rate terms) all share state variables
through **non-power-conserving rate terms**, signal paths, or
stoichiometric matrices. v3 adds the fourth class.

**RATE_COUPLING — pre-conditions:**
- Eq_a has a state variable `s_i` whose time derivative depends
  on a rate expression `r(s_j, s_k, ...)` where one or more
  arguments are state variables of eq_b.
- No shared conserved quantity (distinguishes from
  CONSERVATION_BALANCE).
- No effort/flow port pair (distinguishes from
  INTER_DOMAIN_TRANSDUCTION).
- No closure of a free variable; both equations already have
  rank equal to their state dimension (distinguishes from
  CONSTITUTIVE_CLOSURE).

**RATE_COUPLING — post-conditions:**
- Coupled system has a well-defined Jacobian `∂ṡ/∂s` at every
  point in the declared domain.
- A **stoichiometric / signal-flow matrix S** (not a junction
  structure) specifies which state variables feed which rate
  expressions. S has explicit row/column labels matching the
  canonical_equation variable declarations on both sides.
- Energy / power / conserved-quantity balance is NOT required;
  the composition is explicitly non-power-conserving and must
  be tagged `power_conserving: false`.
- Stability: the linearized Jacobian's eigenvalue spectrum at
  each declared fixed point is computed and recorded. This is
  the analog of Dirac-structure skew-symmetry for the rate case.

**Coverage proof (16 seed equations × 4 classes):**

| Seed equation            | Composition example          | ECP class              |
|--------------------------|------------------------------|------------------------|
| Newton II                | Newton+Hooke → SHO           | CONSTITUTIVE_CLOSURE   |
| Hooke                    | Newton+Hooke → SHO           | CONSTITUTIVE_CLOSURE   |
| Newton gravity           | Newton+Gravity → Kepler      | CONSTITUTIVE_CLOSURE   |
| Ohm                      | Newton+Ohm → DC motor        | INTER_DOMAIN_TRANSDUCTION |
| Fourier heat             | Fourier+Fick → Soret         | INTER_DOMAIN_TRANSDUCTION |
| Fick diffusion           | Fourier+Fick → Soret         | INTER_DOMAIN_TRANSDUCTION |
| Maxwell                  | Maxwell+continuity → charge cons | CONSERVATION_BALANCE  |
| Bernoulli                | Bernoulli+energy → pipe flow  | CONSERVATION_BALANCE  |
| Ideal gas                | Ideal gas+1st law → adiabatic | CONSERVATION_BALANCE  |
| Arrhenius                | Arrhenius+Fick → reac-diff   | RATE_COUPLING          |
| Schrödinger              | Schrödinger+Maxwell → QED     | INTER_DOMAIN_TRANSDUCTION |
| Navier-Stokes            | NS+energy → compressible flow | CONSERVATION_BALANCE  |
| Carnot                   | Carnot+ideal gas → cycle eff  | CONSTITUTIVE_CLOSURE   |
| Boltzmann transport      | Boltzmann+Maxwell → plasma   | RATE_COUPLING          |
| Lotka-Volterra           | predator+prey rates          | RATE_COUPLING          |
| Black-Scholes            | BS+interest-rate dynamics    | RATE_COUPLING          |

All 16 seed equations fit under exactly one class per composition
instance. Mutual exclusivity is enforced by the pre-condition
ordering: a candidate composition is tested against classes in
the order [INTER_DOMAIN_TRANSDUCTION, CONSERVATION_BALANCE,
CONSTITUTIVE_CLOSURE, RATE_COUPLING]; the first class whose
pre-conditions are satisfied claims it, and the others must
be demonstrably false. A validator enforces this at ingest.

---

## C2 — DOV-DSL: formal grammar for domain-of-validity inequalities

v2 shipped validity as prose-ish inequality strings. v3 defines
a restricted DSL parseable against the canonical_equation's
SymPy AST with explicit variable binding.

**DOV-DSL BNF grammar:**
```
expr       ::= relation ( LOGIC_OP relation )*
relation   ::= arith_expr REL_OP arith_expr
arith_expr ::= term ( ('+' | '-') term )*
term       ::= factor ( ('*' | '/') factor )*
factor     ::= ('-')? atom ( '**' atom )?
atom       ::= NUMBER | IDENT | NAMED_GROUP | '(' expr ')'
             | FUNC '(' arith_expr ( ',' arith_expr )* ')'
REL_OP     ::= '<' | '<=' | '>' | '>=' | '==' | '!='
LOGIC_OP   ::= 'AND' | 'OR'
FUNC       ::= 'abs' | 'sqrt' | 'log' | 'exp' | 'sin' | 'cos'
IDENT      ::= [a-zA-Z_][a-zA-Z0-9_]*  # must resolve to a
                                        # variable in canonical_
                                        # equation.variables OR
                                        # to a NAMED_GROUP
NAMED_GROUP::= ':=' dimensionless_group_ref
            # e.g. Ro := U/(f*L) introduces a reusable group
```

**Variable binding:**
- Every IDENT in a DOV expression must either (a) resolve to a
  key in `canonical_equation.variables`, or (b) be a previously-
  declared NAMED_GROUP in the same EWE entry.
- NAMED_GROUPs let entries introduce nondimensional groups
  (Rossby, Reynolds, Peclet, Mach, Knudsen, Damköhler) and reuse
  them across multiple inequalities.
- An inequality referencing an unbound IDENT is a parse error.

**Evaluation semantics:**
- The parser emits a SymPy expression tree.
- At validity-check time, a state vector provides values for
  the canonical_equation variables; NAMED_GROUPs are computed
  from those values; the relation is evaluated to a boolean.
- Unobservable variables (no value supplied) trigger
  `UNOBSERVABLE` status, which propagates to a `sensing_gap`
  verdict under the §11h Failure Investigation Protocol — this
  ties DOV-DSL directly into the existing failure protocol.

**Parser:** implemented as a SymPy-based restricted-grammar
tokenizer (approximately 200 LoC) in
`framework.dov_dsl.parse_validity_expression()`. Unit tests
cover: (a) happy path, (b) unbound identifier, (c) malformed
operator, (d) named-group reuse, (e) unobservable propagation.

---

## C3 — Corrected Dirac-structure postcondition

v2 postcondition was incorrectly stated. The correct formulation:

**INTER_DOMAIN_TRANSDUCTION post-condition (corrected):**
- Let `f ∈ F` be the flow-variable vector and `e ∈ E` be the
  effort-variable vector at the junction, with `F` and `E` in
  duality.
- The interconnection is defined by a linear map
  `(f, e) ↦ J · (f, e)` where `J` is skew-symmetric:
  `J + J^T = 0`.
- **Machine-verifiable assertion:** for every `(f, e)` in the
  junction's domain, `(f, e)^T · J · (f, e) = 0`. Equivalently,
  the inner product `⟨e, f⟩ = 0` at the junction. This is
  **power conservation, not power balance to machine precision**
  — the total instantaneous power flowing in equals the total
  flowing out, identically zero at the junction itself.
- The unit test for each INTER_DOMAIN_TRANSDUCTION composite
  asserts `sp.simplify(J + J.T) == sp.zeros(n, n)` symbolically,
  not just numerically. Numerical check is a fallback when
  symbolic simplification times out.
- Transformer and gyrator elements are the two canonical
  two-port Dirac structures; both satisfy skew-symmetry by
  construction.

OpenAI flagged in v2 that the old prose postcondition was
dimensionally incorrect. It was. The skew-symmetric formulation
is the textbook correct statement (van der Schaft, L2-Gain and
Passivity Techniques in Nonlinear Control, 2nd ed., §4.2;
Duindam et al., Modeling and Control of Complex Physical
Systems, 2009, Ch 2).

Additionally, following OpenAI's v2 suggestion: for
CONSTITUTIVE_CLOSURE, the rank-equals-states postcondition is
insufficient for differential-algebraic systems (incompressible
Navier-Stokes, constrained mechanical systems). v3 requires
a **Pantelides / Pryce structural index** check:
- `structural_index: integer` field added to CONSTITUTIVE_CLOSURE
  ECP entries.
- For ODE systems, index = 0 or 1 (acceptable).
- For index-2+ DAEs, an explicit index-reduction scheme
  (dummy derivatives, Gear-Gupta-Leimkuhler) must be recorded.

---

## C4 — CRYPTO_REDUCTION formal fields

v2's crypto sub-appendix defined a CRYPTO_REDUCTION ECP class
but left its post-conditions at prose level. v3 adds the required
formal fields:

```yaml
composition_class: CRYPTO_REDUCTION
reduction_type: tight | polynomial | exact | loose
advantage_loss_factor: "(q_h + q_s)^2 / 2^k"  # symbolic SymPy
                                                # expression over
                                                # security params
security_model:
  name: ROM | standard_model | QROM | UC
  oracle_queries_bounded: true
  adversary_class: PPT | QPT | unbounded
postcondition_advantage_bound:
  form: "Adv_A <= f(advantage_loss_factor, k, q)"
  sympy_ast: "Adv_A <= ((q_h + q_s)**2) * 2**(-k)"
  verifiable_when: "k >= 80 AND q_h + q_s < 2**64"
citation:
  reduction_proof: "Bellare-Rogaway 1993 DOI:10.1145/168588.168596"
  standard_reference: "Katz-Lindell 2nd ed Ch 10"
```

**Machine-checkable:** the `postcondition_advantage_bound.sympy_ast`
is parsed under the DOV-DSL grammar (reused from C2) and
evaluated against concrete `(k, q_h, q_s)` values. The
`verifiable_when` clause is itself a DOV-DSL inequality. When
security parameters fall outside the `verifiable_when` region,
the system returns `ADVANTAGE_BOUND_OUTSIDE_PROVEN_REGION`, not
a false positive.

**Handling of post-quantum lattice equations (Kyber, Dilithium):**
v3 ships with two post-quantum AAO tags (from v2):
`post_quantum_hardness_LWE`, `post_quantum_hardness_SIS`. A Kyber
EWE entry has `security_model: name: QROM` and advantage bound
expressed in terms of the LWE modulus, dimension, and error
distribution width. The CRYPTO_REDUCTION composition pattern
handles the KEM → IND-CCA2 reduction (Fujisaki-Okamoto transform)
with `reduction_type: tight` and the explicit `advantage_loss_
factor` from the FO proof.

---

## C5 — Calibration as hard gate in HEQU-BENCH-001

v2 treated calibration (Brier score, reliability diagram) as one
of four fungible retrieval metrics. Miscalibrated confidence in
a scientific-discovery engine is a safety-critical failure mode,
so v3 promotes calibration to a **separate hard gate**:

**HEQU-BENCH-001 revised pass condition:**
1. **GATE 1 — Retrieval quality (fungible metrics).**
   System A (structured EWE graph RAG) must beat System B
   (free-text baseline) on at least 3 of {Top-1 accuracy,
   Top-5 accuracy, MRR, ablation delta A−C} by margins
   exceeding 2 SE.
2. **GATE 2 — Calibration (hard, non-fungible).**
   System A's Brier score on EWE-id confidence must be
   ≤ `min(0.10, Brier(B))`. Equivalently: A's calibration is
   no worse than B's AND absolutely below 0.10. Reliability
   diagram must show no confidence bucket with observed
   accuracy differing from stated confidence by > 0.15.
3. **GATE 3 — Refusal precision (hard, already in v2).**
   On honest-unknown decoy queries (no matching EWE), A must
   refuse (return no confident match) in ≥ 0.95 of cases.

All three gates must pass. A system that aces retrieval but
fails calibration is rejected — the structured-graph approach
is retracted and we fall back to free-text RAG with explicit
loss report to the user.

---

## Questions for the board (v3)

1. Does the RATE_COUPLING 4th class with its pre-/post-condition
   set and the 16-equation coverage table cleanly close the
   exhaustiveness gap? Is there still a fifth class hiding in
   systems biology / control theory / finance that the four
   classes miss? Specifically: does pure signal-flow block-
   diagram coupling (PID controllers) fit RATE_COUPLING or
   does it need its own class?
2. Is the DOV-DSL BNF grammar the right restriction of sympy?
   Is there a standard subset already in use (MathML content,
   Lean Mathlib's order theory tactics, Isabelle HOL real
   arithmetic) that v3 should adopt instead of rolling its own?
3. Is the corrected Dirac-structure postcondition (skew-symmetric
   J, `(f,e)^T J (f,e) = 0`) stated rigorously, or is there a
   further subtlety (e.g., modulated Dirac structures for
   state-dependent transducers, holonomic vs non-holonomic
   constraint projection) that v3 still glosses over?
4. Is the Pantelides/Pryce structural-index check the right
   tool for DAE CONSTITUTIVE_CLOSURE validation, or is there a
   more modern approach (e.g., Σ-method with signature matrix,
   graph-based index reduction)?
5. Are the CRYPTO_REDUCTION formal fields (reduction_type,
   advantage_loss_factor as symbolic expression, security_model
   enum, postcondition_advantage_bound as DOV-DSL expression)
   sufficient for the post-quantum lattice cases (Kyber,
   Dilithium, Falcon, SPHINCS+)? Is there a field missing for
   quantum oracle query complexity separate from classical?
6. Is the HEQU-BENCH-001 three-gate structure the right shape,
   or should calibration be even stricter (e.g., Expected
   Calibration Error with 10-bucket discretization, not just
   Brier score)?
7. Fatal flaws still remaining: what should the board flag that
   v3 still misses before build starts?

Verdict requested: APPROVE / MODIFY / REJECT, with per-question
specificity. The goal is to reach APPROVE on v3 so the Phase 14
MVP build can begin, starting with AAO publication and one-at-
a-time EWE seeding under board review.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of EWE concept v3 "
                  "(Grok included, ~12 model calls, ~6-10 minutes)...")
            result = board.four_phase_query(
                query_id="ewe_concept_review_v3",
                review_subject=(
                    "v3 of the EWE/ECP/EOE/EMP structured knowledge "
                    "framework, addressing the 5 required "
                    "modifications from the v2 review: 4th ECP class "
                    "RATE_COUPLING, DOV-DSL formal grammar, "
                    "corrected Dirac-structure postcondition, "
                    "CRYPTO_REDUCTION formal fields, calibration "
                    "as hard gate in HEQU-BENCH-001"
                ),
                user_payload=_CONCEPT_V3,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# EWE Concept Review v3 — 4-Phase Academic Protocol\n")
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
