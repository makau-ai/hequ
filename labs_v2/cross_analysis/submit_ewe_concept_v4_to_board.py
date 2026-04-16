"""Submit EWE concept v4 to the 4-phase review board.

v4 addresses the 4 required modifications from v3:
  M1 — RATE_COUPLING user-declared fixed points + UNDETERMINED
       fallback, and finite-dim ODE normative scope with a PDE
       kinetic annex for Boltzmann transport / reaction-diffusion.
  M2 — Modulated Dirac structures J(x) with symbolic
       skew-symmetry check on free state symbols, plus numerical
       fallback and an implicit junction-form alternative.
  M3 — DOV-DSL pointwise-only scope declaration, pint-based
       machine-checkable dimensional analysis, QROM quantum
       query parameters required when security_model == QROM.
  M4 — ECP exhaustiveness via constructive partition over
       coupling modalities, with composite-classification
       mechanism for FSI and DAE algebraic-constraint coupling.
Plus Gate 2 calibration refined to 10-decile ECE.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "EWE_CONCEPT_REVIEW_V4.md"


_CONCEPT_V4 = """\
# EWE Concept v4 — Board Review

## Context
v3 was reviewed by the 4-phase board. Editor verdict: MODIFY.
All four reviewers responded. Substantive vote: 3 MODIFY
(Claude, OpenAI, Gemini) + 1 APPROVE (Grok, without engaging
the technical objections). Rubric means: 4.20–4.60. Four
required modifications converged. v4 addresses each below.
Everything from v3 not listed here is unchanged.

---

## C1 — RATE_COUPLING: user-declared fixed points + ODE scope

**Problem (v3):** The postcondition required computing
eigenvalue spectra at "each declared fixed point" but left
fixed-point enumeration undefined. For general nonlinear
systems, fixed-point enumeration is undecidable. The
postcondition was not machine-checkable for the systems
that motivated the class.

**v4 resolution — explicit protocol:**

```yaml
composition_class: RATE_COUPLING
stability_protocol:
  declared_fixed_points:
    - {label: "coexistence",
       state_values: {N_prey: "K*d/(c*b)",
                      N_pred: "b*(1-d/(c*b*K))/c"}}
    - {label: "extinction",
       state_values: {N_prey: 0, N_pred: 0}}
  verification_strategy: symbolic_first_numeric_fallback
  eigenvalue_spectrum:
    - fixed_point: "coexistence"
      symbolic_result: "center (pure imaginary)"
      status: VERIFIED
    - fixed_point: "extinction"
      symbolic_result: "saddle, eigenvalues {b, -d}"
      status: VERIFIED
  symbolic_timeout_seconds: 10
  on_timeout: UNDETERMINED
  stability_status: ASSESSED  # or NOT_ASSESSED if zero declared
```

**Rules:**
- `declared_fixed_points` is authored by the architect, not
  auto-discovered. Zero declared points is valid and sets
  `stability_status: NOT_ASSESSED`.
- Each Jacobian is computed symbolically via SymPy with state
  variables as free symbols. If `sp.simplify(J.eigenvals())`
  times out at `symbolic_timeout_seconds`, the result is
  `UNDETERMINED` and a numerical fallback samples random
  perturbations around the point in the declared validity
  domain.
- The validator rejects entries with `stability_status:
  ASSESSED` but any fixed point at `UNDETERMINED` unless a
  numerical fallback was run and recorded.

**Finite-dim ODE scope + PDE annex (OpenAI/Gemini v3 concern):**
RATE_COUPLING is normatively scoped to **finite-dimensional
ODE systems with C¹ right-hand sides**. Infinite-dimensional
cases (Boltzmann transport, reaction-diffusion PDEs,
stochastic rate equations) are routed through an explicit
`pde_kinetic_annex`:

```yaml
pde_kinetic_annex:
  discretization_scheme: finite_volume_128_cells
  truncation_obligation: "converge under grid halving to tol=1e-4"
  citation: "Chapman-Enskog expansion, Cercignani 1988"
```

The annex must cite a published discretization scheme and
declare the convergence obligation under refinement.

---

## C2 — Modulated Dirac structures J(x)

**Problem (v3):** Constant-J postcondition silently
mis-verifies state-dependent J(x). Claude and Gemini both
flagged this as "the standard case, not an edge case" —
robot arms, Euler equations on SO(3), configuration-
dependent mass matrices all require J(x).

**v4 resolution — two-mode verification:**

**Mode A: explicit symbolic check on J(x)**
```yaml
composition_class: INTER_DOMAIN_TRANSDUCTION
dirac_structure:
  form: explicit_matrix
  J_sympy: "Matrix([[0, -g*sin(theta)], [g*sin(theta), 0]])"
  state_symbols: [theta]
  modulated: true
  skew_symmetry_check:
    method: symbolic
    expression: "sp.simplify(J + J.T) == sp.zeros(n, n)"
    result: VERIFIED
  numerical_fallback:
    required_when: UNVERIFIED_SYMBOLICALLY
    sample_count: 1000
    sample_domain: "theta in [-pi, pi]"
    tolerance: 1e-12
    status: VERIFIED_NUMERICALLY
```

The symbolic check runs first with state variables as free
SymPy symbols. If `sp.simplify(J(x) + J(x).T)` does not
reduce to the zero matrix (timeout, unsupported functions,
non-simplifiable) the result is `UNVERIFIED_SYMBOLICALLY`
and the numerical fallback is **mandatory, not optional**.
The fallback Latin-hypercube samples the state domain at
1000 points and reports max absolute violation. Default
tolerance 1e-12; entries can tighten but not loosen.

**Mode B: implicit junction form (bond-graph style)**
```yaml
composition_class: INTER_DOMAIN_TRANSDUCTION
dirac_structure:
  form: implicit_junction
  junction_type: MTF | MGY | zero_junction | one_junction
  constitutive_map: "f_2 = n(theta)*f_1, e_1 = n(theta)*e_2"
  power_conservation_check:
    method: symbolic_inner_product
    expression: "sp.simplify(e_1*f_1 - e_2*f_2) == 0"
    result: VERIFIED
```

The implicit form asserts that the constitutive map at the
junction preserves the inner product `⟨e, f⟩`, equivalent
to skew-symmetry of J but without forming J explicitly.
Accepted forms: MTF (modulated transformer), MGY (modulated
gyrator), 0-junction (common effort), 1-junction (common flow).

Both modes are legal; entries declare which they use via
`dirac_structure.form`.

**Citations:** van der Schaft, *L2-Gain and Passivity
Techniques in Nonlinear Control*, 2nd ed., §4.2; Duindam
et al., *Modeling and Control of Complex Physical Systems*
(2009), Ch 2.

---

## C3 — DOV-DSL scope + dimensional analysis + QROM queries

Three sub-items, each required.

### C3a — DOV-DSL pointwise-only scope declaration

v4 DOV-DSL is declared pointwise-evaluable only:

> An expression in DOV-DSL is a function
> `f: StateSpace → Bool` that evaluates given a concrete
> assignment of all canonical_equation variables. Universal,
> existential, and integral quantifications are out of
> scope for DOV-DSL.

Quantified conditions route to a separate provenance field:

```yaml
domain_of_validity:
  inequalities:  # DOV-DSL pointwise
    - "Ro := U / (f * L) >= 1"
    - "|v|/c < 0.1"
validity_meta:
  quantified_conditions:
    - statement: "∃ Lyapunov function V: X→R with V̇ ≤ 0 on D"
      evidence: "Khalil, Nonlinear Systems 3rd ed §4.2 Thm 4.2"
      verification_method: textbook_reference
      confidence: 0.95
```

The parser emits a parse error on `forall`, `exists`, `∀`,
`∃`, `sum`, `integrate`, or unbound loop indices; these
route to `quantified_conditions`.

### C3b — Machine-checkable dimensional analysis (pint-based)

Every DOV-DSL inequality passes dimensional consistency
before entering the validator's accepted set:

```yaml
canonical_equation:
  variables:
    F: {qudt: "qudt:Force",         pint_unit: "newton"}
    m: {qudt: "qudt:Mass",          pint_unit: "kilogram"}
    a: {qudt: "qudt:Acceleration",  pint_unit: "meter/second**2"}
```

The parser uses **pint** (already pinned in the exec sandbox:
`pint==0.24.4`) to assign dimensions to every IDENT in
DOV-DSL expressions from the `canonical_equation.variables`
block. Every relation must be dimensionally consistent on
both sides. Every named dimensionless group must simplify
to `dimensionless` under pint.

A dimensionally-inconsistent inequality is a **parse error**.
This addresses Gemini's v3 "non-negotiable" call: composing
physical equations without dimensional consistency is a
fundamental-error attractor and we do not allow it.

### C3c — QROM quantum query parameters

```yaml
composition_class: CRYPTO_REDUCTION
security_model:
  name: QROM  # or ROM / standard_model / UC
quantum_query_parameters:
  q_quantum: "q_quantum"                  # SymPy symbol
  superposition_queries_bounded: true
  required_when: "security_model.name == QROM"
advantage_loss_factor: "(q_classical + q_quantum)**2 / 2**k"
postcondition_advantage_bound:
  sympy_ast: "Adv_A <= (q_classical + q_quantum)**2 * 2**(-k)"
```

When `security_model.name == QROM`, both `q_quantum` and
`superposition_queries_bounded` are required, and the
advantage expressions must reference `q_quantum`. The
validator rejects QROM entries that omit quantum query
bounds — no more silent omission for post-quantum lattice
cases (Kyber, Dilithium, Falcon, SPHINCS+).

---

## C4 — ECP exhaustiveness via constructive partition

**Problem (v3):** The 16-example coverage table argued
four-class exhaustiveness by example, which is insufficient.
FSI (shared-boundary coupling where geometry is the shared
variable) and DAE algebraic-constraint coupling were not
obviously in any of the four classes.

**v4 resolution — decision tree over information-flow modality:**

Given two equations eq_a and eq_b that share information,
the flow between them is classified by a decision tree on
**how the shared quantity enters each equation**:

```
Q1: Do eq_a and eq_b share a conserved quantity Q such that
    d(Q_total)/dt = 0 is imposed across the composition?
    YES → CONSERVATION_BALANCE
    NO  → Q2

Q2: Does eq_b supply the algebraic closure of a free variable
    in eq_a (the variable is undetermined in eq_a alone and
    eq_b provides it as an algebraic function of other state)?
    YES → CONSTITUTIVE_CLOSURE  [may be DAE; index recorded]
    NO  → Q3

Q3: Are eq_a and eq_b in different physical domains connected
    through a power-conserving port structure (effort-flow
    duality with skew-symmetric interconnection, possibly
    modulated)?
    YES → INTER_DOMAIN_TRANSDUCTION
    NO  → Q4

Q4: Does eq_a's time derivative depend on a rate expression
    whose arguments include state variables of eq_b (or
    vice versa) WITHOUT a conserved quantity, algebraic
    closure, or power-conserving port?
    YES → RATE_COUPLING
    NO  → REJECTED as ill-defined
```

**FSI handled by composite classification:**
Fluid-structure interaction is **a pair** — (1) the wetted
geometry is the algebraic closure variable
(CONSTITUTIVE_CLOSURE), AND (2) the stress/velocity
exchange at the interface is a power-conserving port
(INTER_DOMAIN_TRANSDUCTION). The v4 schema allows a
**composite classification** on a single ECP entry when
different pieces of shared information fall under different
classes:

```yaml
composition_class:
  - CONSTITUTIVE_CLOSURE   # geometry closure
  - INTER_DOMAIN_TRANSDUCTION  # interface power port
composite_classification: true
per_piece:
  - piece: "wetted_geometry"
    class: CONSTITUTIVE_CLOSURE
  - piece: "interface_stress_velocity"
    class: INTER_DOMAIN_TRANSDUCTION
```

The validator enforces that the union of `per_piece` classes
covers every piece of shared state. An entry that has
`composite_classification: false` (the common case) must
have exactly one class.

**DAE algebraic-constraint coupling:**
Algebraic constraints on a system of ODEs (incompressible
Navier-Stokes's ∇·u = 0) are CONSTITUTIVE_CLOSURE with
`structural_index > 0`. The Pantelides/Pryce scheme (v3
requirement) handles these; the validator records the
index and requires the index-reduction method to be cited
when index ≥ 2.

**Constructive proof sketch of exhaustiveness:**
Given any two equations that admit a joint solution, the
information flowing between them is one of exactly four
kinds: (1) a conserved quantity invariant across the
composition, (2) an algebraic relationship closing a free
variable, (3) a pair of conjugate variables in duality with
skew-symmetric interconnection, (4) a rate term whose
argument comes from the other equation. These are mutually
exclusive **per piece of shared information** — a single
piece cannot simultaneously be conserved quantity AND
algebraic closure AND power-conserving port AND rate
argument, because each is a distinct mathematical property
of that piece. Compositions sharing multiple pieces may
declare multiple classes via `per_piece`, one per piece.

The 16-example table is retained as **validation** of the
partition, not as the argument for exhaustiveness.

---

## C5 — Gate 2 calibration: 10-decile ECE

**Replacement for v3's single Brier threshold.** v4 Gate 2
uses Expected Calibration Error with 10 equal-mass buckets:

```
ECE_10 := (1/N) · Σ_{b=1..10} n_b · |accuracy(b) − confidence(b)|
```

**Gate 2 pass condition (v4):**
1. `ECE_10(A) ≤ min(0.05, ECE_10(B))`
2. `|accuracy(b) − confidence(b)| ≤ 0.15` for every decile b
3. Reliability diagram published in the benchmark report.

Gates 1 (retrieval quality) and 3 (refusal precision ≥ 0.95
on honest-unknown decoys) are unchanged.

---

## Questions for the board (v4)

1. Does the four-class **constructive partition** with the
   decision-tree ordering and composite-classification
   mechanism close the exhaustiveness gap? Specifically:
   does stochastic coupling (Itô/Stratonovich noise shared
   across two SDEs) fit RATE_COUPLING or need a branch?
2. Is the two-mode Dirac-structure verification (explicit
   matrix J(x) with symbolic-first + mandatory numerical
   fallback, OR implicit junction form with inner-product
   preservation) the right pair, or is a third mode needed?
3. Is DOV-DSL pointwise-only + pint dimensional check
   sufficient, or does the dimensional machinery need to
   handle anisotropic tensors and rank-valued quantities
   (stress/metric tensors) that pint alone cannot?
4. Is the QROM `quantum_query_parameters` block the right
   shape, or should it also carry `adversary_time_complexity`
   and `classical_memory_bound` fields for completeness?
5. Is the ECE_10 calibration gate the right replacement for
   Brier, or should it be ECE_10 hard-gate AND Brier as
   secondary? Does the 0.05 absolute threshold need
   justification from safety-critical ML literature?
6. Fatal flaws remaining: what should the board flag that
   v4 still misses?

Verdict requested: APPROVE / MODIFY / REJECT. v4's goal is
APPROVE so Phase 14 MVP build can begin — AAO publication,
JSON Schema lockdown, and one-at-a-time EWE seeding under
board review per EWE_DEVELOPMENT_PROCESS.md.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of EWE concept v4 "
                  "(Grok included, ~12 model calls, ~6-10 minutes)...")
            result = board.four_phase_query(
                query_id="ewe_concept_review_v4",
                review_subject=(
                    "v4 of the EWE/ECP/EOE/EMP structured knowledge "
                    "framework, addressing the 4 required "
                    "modifications from v3: RATE_COUPLING "
                    "user-declared fixed points + finite-dim ODE "
                    "scope, modulated Dirac structures J(x) with "
                    "two-mode verification, DOV-DSL pointwise scope "
                    "+ pint dimensional check + QROM quantum query "
                    "parameters, and ECP exhaustiveness via "
                    "constructive partition with composite "
                    "classification for FSI and DAE coupling"
                ),
                user_payload=_CONCEPT_V4,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# EWE Concept Review v4 — 4-Phase Academic Protocol\n")
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
