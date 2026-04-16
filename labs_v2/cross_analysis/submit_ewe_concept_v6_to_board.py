"""Submit EWE concept v6 to the 4-phase review board.

v6 addresses the 5 required modifications from v5:
  C1 — Itô-isometry-as-theorem vs verifiable postconditions:
       replace isometry with (a) F_t-adaptedness of each
       diffusion-term integrand, (b) square-integrability
       of those integrands. Cite the isometry as a consequence.
  C2 — Corrected Lotka-Volterra Lyapunov function with distinct
       per-species coefficients, verified symbolically:
       V = c·N_prey − d·log(N_prey) + b·N_pred − a·log(N_pred)
       satisfies dV/dt = 0 exactly (sympy-verified before
       submission; see proof block).
  C3 — STOCHASTIC_COUPLING scope predicate explicitly routing
       McKean-Vlasov, Dean-Kawasaki / SPDE, and rough-path SDEs
       to UNCLASSIFIED.
  C4 — Automated singularity sanity check in C5: mandatory
       `sp.solve(det(J) == 0)` pre-screen that flags undeclared
       singular surfaces.
  C5 — Tensor index controlled vocabulary: ordered
       `[upper, lower, ...]` list per tensor slot so the
       tensor_rank_consistency block is machine-comparable.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "EWE_CONCEPT_REVIEW_V6.md"


_CONCEPT_V6 = """\
# EWE Concept v6 — Board Review

## Context
v5 was reviewed by the 4-phase board. Editor verdict: MODIFY.
All four reviewers responded, rubric means 4.20–4.40, with
five surgical concerns converging independently across
reviewers. Two of the five were factual errors in v5's worked
content (Itô isometry stated as postcondition instead of
theorem; Lotka-Volterra Lyapunov function with wrong
coefficients). v6 corrects each below, with sympy verification
performed before submission to prevent a repeat. Everything
from v5 not listed here is unchanged.

---

## C1 — Itô isometry is a theorem, not a postcondition

**Problem (v5):** I listed the Itô isometry as the flagship
postcondition for STOCHASTIC_COUPLING. But the isometry

    E[(∫₀ᵀ H_s dW_s)²] = E[∫₀ᵀ H_s² ds]

holds for *every* F_t-adapted, square-integrable integrand H —
it is a theorem of the Itô integral (Øksendal §3.2 Theorem
3.1.1), not a property that can discriminate good models from
bad ones. My postcondition could not reject any well-formed
input. This is exactly the vacuous-check failure mode the
framework is supposed to avoid.

**v6 resolution — replace with the actual verifiable conditions:**

```yaml
composition_class: STOCHASTIC_COUPLING
verifiable_postconditions:
  diffusion_integrand_adapted:
    statement: |
      Every integrand H appearing in an Itô integral
      ∫ H dW must be F_t-adapted (measurable with respect
      to the filtration at each time t).
    verification: symbolic_dependency_check
    algorithm: |
      For each H in diffusion_terms:
        if H.free_symbols contains any W(s) for s > t:
          REJECT as non-adapted
        else:
          VERIFY adaptedness
    result: VERIFIED

  diffusion_integrand_square_integrable:
    statement: "E[∫₀ᵀ H² ds] < ∞"
    verification: symbolic_for_bounded_or_polynomial
    algorithm: |
      Case (a) H is a polynomial in x, y with bounded state
        domain D: square-integrability is automatic.
      Case (b) H is globally Lipschitz with linear growth:
        combined with Lipschitz drift, strong solutions
        exist and integrability follows (Øksendal §5.2).
      Case (c) neither: the architect must cite a
        square-integrability theorem specific to the
        coefficient family (e.g., Bessel processes,
        geometric Brownian motion).
    result: VERIFIED

consequence:
  ito_isometry:
    statement: |
      Given adaptedness + square-integrability,
      E[(∫₀ᵀ H_s dW_s)²] = E[∫₀ᵀ H_s² ds] holds as a
      consequence of the Itô isometry theorem.
    citation: "Øksendal, Stochastic Differential Equations
               6th ed., §3.2 Theorem 3.1.1"
    derived_not_verified: true
```

The two *conditions* (adaptedness, square-integrability) are
checkable from the symbolic expression of each integrand. The
isometry is cited as the theorem that follows. The framework
no longer claims to "verify" an identity that is true by
construction.

---

## C2 — Corrected Lotka-Volterra Lyapunov function

**Problem (v5):** I wrote
`V = N_prey + N_pred − K·log(N_prey) − K·log(N_pred)`
with a single parameter K. This is wrong — the standard
conserved quantity has distinct per-species coefficients
matched to the ODE parameters. Three of four reviewers caught
it.

**v6 resolution — corrected form, symbolically verified:**

Consider the Lotka-Volterra system:
```
Ṅ_prey = a·N_prey − b·N_prey·N_pred
Ṅ_pred = c·N_prey·N_pred − d·N_pred
```

The correct conserved quantity is:
```
V(N_prey, N_pred) = c·N_prey − d·log(N_prey)
                  + b·N_pred − a·log(N_pred)
```

**Sympy verification (run locally before submission):**
```python
import sympy as sp
x, y, a, b, c, d = sp.symbols('x y a b c d', positive=True)
x_dot = a*x - b*x*y        # prey ODE
y_dot = c*x*y - d*y        # predator ODE
V = c*x - d*sp.log(x) + b*y - a*sp.log(y)
dV_dt = sp.diff(V, x)*x_dot + sp.diff(V, y)*y_dot
print(sp.simplify(dV_dt))  # prints: 0
```

Result: `dV/dt = 0` exactly. The conserved quantity is
verified symbolically, not by hand-waving.

**Fixed point and Jacobian spectrum (also verified):**
- Unique interior fixed point at `(d/c, a/b)`.
- Jacobian at the fixed point:
  `J = [[0, −b·d/c], [a·c/b, 0]]`
- Eigenvalues: `±i·√(a·d)` — purely imaginary, non-hyperbolic.
- `hyperbolicity.is_hyperbolic: false`, triggering the
  NONHYPERBOLIC_INCONCLUSIVE status.
- The Lyapunov function `V` above provides the required
  certificate: its level sets are closed orbits around the
  fixed point, which upgrades the status to VERIFIED (center,
  neutrally stable).

**v6 RATE_COUPLING worked-example block for Lotka-Volterra:**
```yaml
stability_protocol:
  declared_fixed_points:
    - label: "coexistence"
      state_values: {N_prey: "d/c", N_pred: "a/b"}
      jacobian:
        matrix: "[[0, -b*d/c], [a*c/b, 0]]"
        eigenvalues: ["+I*sqrt(a*d)", "-I*sqrt(a*d)"]
        any_zero_real_part: true
      hyperbolicity:
        is_hyperbolic: false
        reason: "pure imaginary eigenvalues"
      stability_status: NONHYPERBOLIC_INCONCLUSIVE
      required_certificate:
        type: lyapunov_function
        V: "c*N_prey - d*log(N_prey) + b*N_pred - a*log(N_pred)"
        V_dot_symbolic: "sp.simplify(dV/dt) == 0"
        V_dot_value: 0
        interpretation: |
          dV/dt = 0 along trajectories, so level sets of V
          are closed orbits. The fixed point is a center
          (neutrally stable, not asymptotically stable).
        citation: "Murray, Mathematical Biology I, 3rd ed., §3.1"
        upgraded_status: VERIFIED
```

The v6 spec explicitly notes: **every worked example in the
EWE spec must be sympy-verified before the entry is
submitted.** This is added as an anti-drift rule to the
EWE_DEVELOPMENT_PROCESS.md, matching the board's "board is
not a CAS — run the real math locally first" principle.

---

## C3 — STOCHASTIC_COUPLING scope predicate

**Problem (v5):** The decision-tree Q5 accepted any
composition with "shared stochastic driving noise." But
measure-dependent drifts (McKean-Vlasov), distribution-valued
noise (Dean-Kawasaki / SPDE), and rough-path SDEs all fall
outside the standard Itô framework and would be silently
misclassified as STOCHASTIC_COUPLING.

**v6 resolution — explicit scope predicate on Q5:**

```
Q5: Shared stochastic driving noise (SDE diffusion terms)?
  Yes →
    Q5a: Is the noise finite-dimensional standard Brownian
         motion with adapted, square-integrable integrands?
      Yes → Q5b
      No  → UNCLASSIFIED with note "non-standard stochastic
             framework — routes below do not apply"
    Q5b: Is the drift a function of state alone, NOT of the
         distribution of the state (measure-dependent)?
      Yes → Q5c
      No  → UNCLASSIFIED with note "McKean-Vlasov type"
    Q5c: Is the noise process distribution-valued or
         spatially extended (SPDE / Dean-Kawasaki)?
      Yes → UNCLASSIFIED with note "SPDE / distribution-
             valued noise — requires infinite-dim framework"
      No  → Q5d
    Q5d: Is the driving process a standard semimartingale
         (not fractional Brownian motion, not rough path)?
      Yes → STOCHASTIC_COUPLING
      No  → UNCLASSIFIED with note "non-semimartingale
             driver — requires rough-path framework"
  No  → RATE_COUPLING? (see Q4)
```

Each UNCLASSIFIED branch records the specific reason and
routes to the escape-hatch schema from v5's C4 resolution.
The spec explicitly lists the four exclusion categories so
authors know before ingest that their composition is out of
scope.

**Citations for the excluded cases:**
- McKean-Vlasov: Carmona & Delarue, *Probabilistic Theory of
  Mean Field Games*, Vol I, Ch 1.
- Dean-Kawasaki / SPDE: Dean (1996) J. Phys. A 29 L613;
  Kawasaki (1998) Physica A 254 243.
- Rough paths / fBm: Lyons (1998) Rev. Mat. Iberoamericana
  14 215; Friz & Hairer, *A Course on Rough Paths* (2014).

---

## C4 — Automated singularity sanity check

**Problem (v5):** The C5 protocol required architect-declared
singularity sets but had no independent check. An architect
could declare "no singularities" on a J(x) that secretly has
`det(J) = 0` on a surface; the numerical fallback sampler
would almost certainly miss that surface; silent failure.

**v6 resolution — mandatory symbolic pre-screen:**

```yaml
dirac_structure:
  form: explicit_matrix
  J_sympy: "..."
  state_symbols: [...]
  modulated: true
  singularities:
    declared: true | false
    declared_set: "..."  # or null when declared: false

    automated_sanity_check:
      method: "sp.solve(sp.det(J).subs({...}), state_symbols)"
      symbolic_timeout_seconds: 10
      detected_singular_set: "..."   # sp.solve result
      agrees_with_declaration: true  # or false → flag
      on_disagreement: "ingest fails; architect must
                        reconcile or explain"
      on_timeout: "flag as UNDETERMINED; defer to architect
                   declaration with mandatory note"
```

**Rules:**
- The sanity check runs on every ingest of an explicit_matrix
  Dirac entry.
- The sanity check does NOT replace the architect declaration
  — the architect remains responsible for the mathematical
  claim. The sanity check is a second opinion.
- If the automated check finds singularities the architect
  did not declare, ingest fails and the architect must either
  update the declaration or explain why the automated result
  is a false positive (e.g., the extra singularities are
  outside the declared domain of validity).
- On symbolic timeout, the check emits `UNDETERMINED` and
  defers to the architect with a visible note in the entry's
  provenance record. The entry can proceed but carries the
  timeout as a known limitation.

This matches the "board is not a CAS" principle inverted:
here the CAS is not a board, but a safety net that catches
declaration errors before they reach ingest.

---

## C5 — Tensor index controlled vocabulary

**Problem (v5):** The tensor_rank_consistency block was
machine-parseable only for rank but not for index placement.
Different authors could use "sigma_ij" vs "sigma^ij" vs
"σᵢⱼ" inconsistently, making cross-entry comparison fragile.

**v6 resolution — controlled vocabulary for index positions:**

```yaml
tensor_rank_consistency:
  quantities:
    - name: sigma
      rank: 2
      index_positions: [lower, lower]     # controlled enum
      symmetry: symmetric
      index_symmetry_check: "sigma[i,j] == sigma[j,i]"
      physical_interpretation: "Cauchy stress tensor"
      citation: "Landau-Lifshitz Theory of Elasticity §1"
    - name: g
      rank: 2
      index_positions: [lower, lower]
      symmetry: symmetric
      physical_interpretation: "metric tensor"
    - name: R
      rank: 4
      index_positions: [lower, lower, lower, lower]
      symmetry: "R_abcd = -R_bacd = -R_abdc = R_cdab"
      physical_interpretation: "Riemann curvature tensor"
      citation: "Wald, General Relativity §3.2"
  exchange_relations:
    - name: "traction_continuity"
      statement: "t_i = sigma_ij n^j"
      index_positions:
        t: [lower]
        sigma: [lower, lower]
        n: [upper]
      contraction:
        pairs: [[("sigma", 1), ("n", 0)]]
        free_indices: [("sigma", 0) -> ("t", 0)]
```

**Controlled vocabulary:**
- `index_positions` is an ordered list of length equal to
  the tensor's rank.
- Each element is one of the enum values:
  `upper | lower | mixed_upper | mixed_lower`.
- `mixed_upper`/`mixed_lower` are reserved for rare cases
  where a single slot carries both placements under
  index-raising/lowering symmetries.
- Contractions specify `(tensor_name, slot_index)` pairs,
  which the validator can check for rank balance even though
  it does not verify the mathematical content of the
  contraction (that remains human-verified).

This makes the block machine-comparable across authors
without claiming to provide full tensor-aware typing — the
honest-automation-boundary principle is preserved.

---

## Anti-drift rule added to EWE_DEVELOPMENT_PROCESS.md

The two v5 factual errors (Itô isometry, wrong Lyapunov
function) both passed my own review before board submission.
Both would have been caught by running sympy locally first.
v6 adds the following anti-drift rule to the process doc:

> **Rule A9 — sympy-verified worked examples.** Every worked
> example in a spec submission, a board review payload, or an
> EWE entry must be verified symbolically in sympy before the
> document is submitted. The verification script is recorded
> in the entry's provenance as a sibling to the entry itself
> (path: `<entry_id>_verification.py`), runnable with
> `python <script>` from the project root, producing a
> deterministic pass/fail output. "I believe this is the
> standard form" is not sufficient. When the architect cannot
> get the example to verify, the example is WRONG and must
> be corrected before submission — not the framework.

---

## Questions for the board (v6)

1. Does the replacement of the Itô isometry postcondition
   with (a) adaptedness and (b) square-integrability as the
   actual verifiable conditions close the vacuous-check gap?
   Is there a third condition (e.g., progressive
   measurability for non-continuous integrands) that the
   v6 spec should also require?
2. The Lotka-Volterra worked example has been symbolically
   verified to give `dV/dt = 0` exactly. Is the textbook
   citation (Murray, *Mathematical Biology I*, §3.1) the
   right one, or should v6 also cite Lotka (1925) and
   Volterra (1926) as primary sources alongside the modern
   textbook?
3. Does the Q5 scope predicate with four explicit exclusion
   categories (non-standard framework, measure-dependent,
   distribution-valued, non-semimartingale) cover the
   out-of-scope cases cleanly, or is there a fifth (e.g.,
   Lévy processes with jumps, Poisson random measures) that
   should be explicitly listed?
4. Is the automated singularity sanity check (sp.solve on
   det(J)) a sufficient pre-screen, or should it be
   supplemented with a numerical sampler that looks for
   points where the smallest singular value of J drops
   below a threshold (catches approximate degeneracies
   that symbolic det doesn't find)?
5. Is the four-value index_positions vocabulary
   (upper / lower / mixed_upper / mixed_lower) adequate, or
   should v6 adopt a more formal system (e.g., Penrose
   abstract index notation, or the Carroll *Spacetime and
   Geometry* convention) for rigor?
6. Fatal flaws remaining: what should the board flag that
   v6 still misses before Phase 14 build begins?

Verdict requested: APPROVE / MODIFY / REJECT. v6's goal is
APPROVE so the MVP build can start.

**Iteration trajectory:**
  v1 → MODIFY (5 concerns — decomposition, prior art,
               RAG evaluation)
  v2 → MODIFY (5 concerns — ECP exhaustiveness, DSL grammar,
               Dirac correctness)
  v3 → MODIFY (4 concerns — RATE_COUPLING semantics,
               modulated Dirac, QROM queries,
               exhaustiveness)
  v4 → MODIFY (5 concerns — stochastic gap,
               non-hyperbolic fp, tensor rank,
               proof-downgrade, singularities)
  v5 → MODIFY (5 concerns — Itô vacuous,
               LV Lyapunov error, scope predicate,
               det(J) sanity check, index vocab)
  v6 → ?       (addresses v5's exact 5 mods, with sympy
               verification of the LV example performed
               before submission to prevent the C2 error
               class from recurring)
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of EWE concept v6 "
                  "(Grok included, ~12 model calls, ~6-10 minutes)...")
            result = board.four_phase_query(
                query_id="ewe_concept_review_v6",
                review_subject=(
                    "v6 of the EWE/ECP/EOE/EMP structured knowledge "
                    "framework, addressing the 5 required "
                    "modifications from v5: Itô isometry replaced "
                    "with adaptedness + square-integrability as "
                    "actual verifiable postconditions, corrected "
                    "Lotka-Volterra Lyapunov function "
                    "(sympy-verified dV/dt == 0), STOCHASTIC_COUPLING "
                    "scope predicate routing McKean-Vlasov / "
                    "Dean-Kawasaki / rough-path to UNCLASSIFIED, "
                    "automated sp.solve(det(J)) singularity "
                    "pre-screen, and controlled vocabulary for "
                    "tensor index placement"
                ),
                user_payload=_CONCEPT_V6,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# EWE Concept Review v6 — 4-Phase Academic Protocol\n")
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
