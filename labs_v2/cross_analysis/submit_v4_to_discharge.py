"""Submit DESIGN-PHASE-12-19.md (now v4) to Round 2 scope-frozen
discharge review.

The FCS from v3's Round 1 editor synthesis:
  C1 — Multiplicative confidence is brittle (high)
  C2 — SymPy+mpmath is not true cross-CAS (high)
  C3 — sp.simplify==0 is incomplete on branch cuts (medium)
  C4 — L0 typed canonical form under-specified (medium)
  C5 — Property-based testing N=50 hand-wavy (medium)
  C6 — Transducer formalism lacks port-H contracts (medium)

Reviewers in Round 2 can only score each FCS item as addressed
/ partially_addressed / not_addressed. They cannot raise new
concerns. Any attempt to do so is logged as a process violation
and escalated to the user.
"""

from __future__ import annotations

import sys
from pathlib import Path

_LABS_V2 = Path(__file__).resolve().parent.parent
if str(_LABS_V2) not in sys.path:
    sys.path.insert(0, str(_LABS_V2))

from framework.ai_consensus import (
    AIConsensusBoard,
    FrozenConcern,
    DESIGN_REVIEW_PERSONAS,
)
from framework.ai_review_board import AIBoardKeysMissing

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "DESIGN_DISCHARGE_ROUND2.md"


# --- Frozen Concern Set from v3 Round 1 editor synthesis ---

FCS = [
    FrozenConcern(
        concern_id="C1",
        headline="Multiplicative composite confidence C = c1·c2·c3·c4 is brittle, "
                 "assumes unvalidated independence, thresholds uncalibrated",
        raised_by=["claude-opus-4-6", "openai-gpt-5", "grok-4"],
        severity="high",
        detail=(
            "v3 used a raw multiplicative confidence rule where a single "
            "zero-level factor collapses the entire score. Reviewers noted "
            "the independence assumption between levels was never specified "
            "or validated, and the promotion thresholds (0.30/0.50/0.80) "
            "had no empirical calibration. Multiple reviewers proposed "
            "log-evidence accumulation or Bayes factors with floors as "
            "the correct remedy."
        ),
    ),
    FrozenConcern(
        concern_id="C2",
        headline="SymPy+mpmath claimed as 'cross-CAS' but mpmath IS sympy's own "
                 "numerical backend — independence claim is factually wrong",
        raised_by=["claude-opus-4-6", "openai-gpt-5", "grok-4"],
        severity="high",
        detail=(
            "v3 §5.2/§11c labeled the verification pipeline as 'cross-CAS "
            "orthogonal verification' including both sympy.evalf and mpmath "
            "high-precision evaluation. Three reviewers independently "
            "pointed out that mpmath IS sympy's numerical backend; calling "
            "these two engines independent is factually wrong. Required "
            "remedy: add at least one genuinely independent numeric engine "
            "such as python-flint (Arb-based), gmpy2/MPFR, or Mathematica "
            "via wolframclient, and relabel the claim honestly."
        ),
    ),
    FrozenConcern(
        concern_id="C3",
        headline="sp.simplify(expr) == 0 is known-incomplete on piecewise, "
                 "abs, branch cuts, multivalued inverses — false positives "
                 "and false negatives possible",
        raised_by=["claude-opus-4-6", "openai-gpt-5"],
        severity="medium",
        detail=(
            "v3's symbolic equivalence check was `sp.simplify(expr) == 0`. "
            "sympy's own documentation acknowledges simplify is a heuristic "
            "and can produce both false positives (different expressions "
            "normalized to identical forms under ambiguity) and false "
            "negatives (expressions that ARE equal but simplify doesn't "
            "recognize). Required remedy: a canonicalization pipeline "
            "with rational function normalization, polynomial remainder "
            "checks, trig/power simplification, and discriminating random "
            "evaluation near branch cuts as the fallback check."
        ),
    ),
    FrozenConcern(
        concern_id="C4",
        headline="L0 typed canonical form and unit system under-specified — "
                 "no UCUM/QUDT adoption with formal dimensional type "
                 "inference and unification",
        raised_by=["openai-gpt-5"],
        severity="medium",
        detail=(
            "v3 declared QUDT URIs on each variable but did not enforce "
            "dimensional consistency during transducer composition, "
            "property-based sampling, or symbolic operations. Required "
            "remedy: a formal dimensional type system with inference "
            "(when operators are applied, the result type is computed "
            "automatically) and unification (when two sub-expressions "
            "must have matching types, the check runs at load time, not "
            "runtime). Enforcement must be load-time, not silent."
        ),
    ),
    FrozenConcern(
        concern_id="C5",
        headline="Property-based testing at N=50 lacks stratification, "
                 "boundary strategy, power analysis, dimensional sampling",
        raised_by=["claude-opus-4-6", "openai-gpt-5"],
        severity="medium",
        detail=(
            "v3 specified 'N=50 random parameter vectors' with no further "
            "structure. Reviewers flagged: no stratification across orders "
            "of magnitude, no deliberate inclusion of boundary cases, no "
            "power analysis justifying N, no singularity guards, no "
            "dimensional consistency enforcement during sampling. Required "
            "remedy: adopt the Hypothesis library (or equivalent) with "
            "stratified, boundary-aware, dimension-consistent sampling, "
            "seeded reproducibility, and a justified N per problem."
        ),
    ),
    FrozenConcern(
        concern_id="C6",
        headline="Transducer formalism lacks explicit energy-flow / "
                 "port-Hamiltonian contracts — composition preserves "
                 "conservation by post-hoc numeric check, not construction",
        raised_by=["openai-gpt-5"],
        severity="medium",
        detail=(
            "v3 treated transducers as named constitutive relations with a "
            "single coefficient. The physical-constraint filter checked "
            "Tellegen pairing and Onsager reciprocity after-the-fact, but "
            "composition itself did not enforce passivity or conservation "
            "by construction. Required remedy: formalize transducers as "
            "port-Hamiltonian subsystems with explicit ports (effort/flow), "
            "energy state vars, Dirac structure constraints, and a "
            "power-conservation equation that must be symbolically "
            "verified at composition time, not at runtime."
        ),
    ),
]


_REVISION_SUMMARY = """\
# v4 discharge summary (what changed from v3)

v4 addresses each FCS item in-place in DESIGN-PHASE-12-19.md:

**C1 (high, §8a)** — Multiplicative rule replaced with
**log-evidence accumulator with per-level floors**. Each
level contributes ℓ_i bounded in [−4.6, +3.0]; absent levels
contribute 0 (neutral, not penalising). Composite is
log_C = ℓ1+ℓ2+ℓ3+ℓ4. Non-brittleness: a coupling with strong
L1+L2+L3 but no sensor data reaches log_C=9.0 without any L4
contribution, enabling PROVED promotion. Promotion thresholds
recalibrated to the log scale with a v4 commitment to
empirical re-calibration against the adversarial pre-reg set
in Phase 12. Independence is NOT claimed; a dependency-audit
protocol catches load-bearing single-level dependencies
during adversarial testing. Full Bayes-factor framework
deferred to Phase 14+ and logged as technical debt.

**C2 (high, §5.2.1–5.2.4)** — The false "cross-CAS" label is
dropped. v4 specifies a four-check pipeline with explicit
honesty about independence:
- Check A: symbolic equivalence via canonicalization
  (§5.2.1)
- Check B: Hypothesis-based property testing (§5.2.2, also
  addresses C5)
- Check C: high-precision mpmath at 50 decimal places,
  labeled as "within-sympy fragility check," NOT cross-CAS
- Check D: **python-flint (Arb-based) interval arithmetic**
  as the GENUINELY independent numeric backend. Phase 12:
  best-effort with graceful skip. Phase 13: hard requirement.
  Mathematica/Maple via wolframclient tracked as Phase 15+
  technical debt.

**C3 (medium, §5.2.1)** — `sp.simplify == 0` replaced with an
explicit canonicalization pipeline: rational function
normalization (cancel + together + expand), trig/power
simplification, polynomial remainder check, then
discriminating random evaluation at N=20 samples drawn to
AVOID declared singularities and branch cuts. Known failure
modes (piecewise, abs, multi-valued inverses) are documented
and trigger `SYMBOLIC_EQUIVALENCE_UNDECIDABLE` rather than
silent mis-classification.

**C4 (medium, §11f)** — L0 gains a formal dimensional type
system on top of QUDT QuantityKind URIs: base dimensions as
rational-exponent 7-tuples, unit prefix tracking, provenance
tags (declared/inferred/asserted), dimensional inference on
composition (add/sub requires unification, mul/div adds
exponents, transcendentals require dimensionless arguments),
and load-time rejection of dimensionally-inconsistent
composites as `DIMENSIONALLY_INCONSISTENT_COMPOSITE`. Every
canonical problem's `problems.yaml` declares its variables'
dimensional signatures explicitly, and reference-value
verification in §5.2 includes a dimensional check as the
first gate.

**C5 (medium, §5.2.2)** — Hypothesis library adopted (the only
new pip dependency in v4). Sampling strategy is
`sample_strategy_for(equation)` which:
- Stratifies unit-consistent parameter draws across orders
  of magnitude
- Includes boundary cases explicitly (min, max, zero,
  unity, near-singularity)
- Avoids declared branch cuts and singularities of every
  function in the canonical form
- Seeds reproducibly with ledger-logged seed for audit replay
- Computes N via power analysis:
  N ≥ 1/(α · δ²) for declared false-discovery rate α and
  minimum detectable effect size δ. Typical N ≈ 10000;
  per-problem declared in `problems.yaml`.

**C6 (medium, §11g)** — Transducers formalized as
port-Hamiltonian subsystems with:
- Explicit ports (effort/flow pairs per domain)
- Energy state vars
- Dirac structure equations as the core algebraic
  constraint
- `power_conservation` equation verified symbolically at
  composition time via sympy (NOT post-hoc numeric)
- Sign convention and constitutive type
- Multi-model-cited provenance

Composition of two equations via a transducer now fails at
load time as `NON_PASSIVE_COMPOSITE` if the Dirac structure
+ power-conservation don't symbolically close. The prior
post-hoc Tellegen/Onsager checks in Phase 6 are retained as
belt-and-braces runtime verification but are no longer the
primary gate.

---

**Plus three new protocol sections (also v4, user-directed,
not FCS-driven but binding):**

**§11a.5 Cost-neutrality disclaimer** — prepended to every
board prompt in framework/ai_consensus.py. Reviewers are
explicitly forbidden from using effort/schedule/preparatory-
work as reasons for any decision. Technical merit only.

**§11e Formal scope-frozen discharge protocol** — built as
AIConsensusBoard.discharge_round() in ai_consensus.py.
Rounds 2+ cannot raise new concerns; they can only
discharge items in the FCS. Process violations are
recorded and escalate to the user Decision Matrix. This
IS the protocol you're running right now.

**§11h Failure Investigation Protocol** — binding for all
Phase 12+ test failures. On ANY test failure: state audit →
assumption audit → literature RAG → board failure-review →
ledger record. Equation modifications and tolerance
adjustments require an `equation_inadequate` verdict with
explicit user approval. Corner-cuts rejected at CI time.

**§11i Academic rigor standard (Nobel-prize bar)** — every
PROVED or GROUNDED coupling must pass a readiness checklist:
quantitative prediction with uncertainty, systematic error
analysis, independent replication pathway, priority search
≥10 citations, honest limitations, multiple-testing
correction, prior-work engagement with adversarial
citations, hall-of-mirrors check (claim re-state-able
outside our framework). The rubric gains an
`academic_defensibility` dimension weighted 2×. Reviewer
prompts carry the external-standard instruction ("would
this survive peer review at Nature? a hostile competing
lab? Nobel-committee methodology scrutiny decades from
now?").
"""


def _load_design_doc() -> str:
    return (_LABS_V2 / "DESIGN-PHASE-12-19.md").read_text()


def main() -> int:
    v4_text = _load_design_doc()
    original_v3 = (
        "Design v3 (previous round) is in the same file's git "
        "history. The FCS below was produced by v3's Round 1 "
        "editor synthesis. This Round 2 evaluates whether the "
        "v4 revision (shown below) addresses each FCS item."
    )

    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running Round 2 discharge review (scope-frozen, "
                  "4 reviewers + editor)...")
            result = board.discharge_round(
                query_id="design_phase_12_20_discharge_round2",
                round_number=2,
                review_subject=(
                    "design v4 of the realization-grounded coupling "
                    "engine, addressing the Frozen Concern Set from "
                    "the v3 Round 1 editor synthesis"
                ),
                fcs=FCS,
                original_submission=original_v3,
                submitter_revision=v4_text,
                submitter_revision_summary=_REVISION_SUMMARY,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# Round 2 Discharge Review — Design v4\n")
    lines.append(f"**Query:** `{result.query_id}`  ")
    lines.append(f"**Round:** {result.round_number}  ")
    lines.append(f"**FCS size:** {len(result.fcs)}  ")
    lines.append(f"**Editor verdict:** `{result.editor_verdict}`\n")

    lines.append("## Editor synthesis (binding)\n")
    lines.append(f"**Verdict:** `{result.editor_verdict}`\n")
    lines.append(f"**Rationale:**\n\n{result.editor_rationale}\n")
    lines.append(f"**Unresolved concerns:** {result.unresolved_concerns}\n")
    if result.process_violations:
        lines.append(f"**⚠ Process violations:**")
        for v in result.process_violations:
            lines.append(f"- {v}")
        lines.append("")
    if result.decision_matrix_needed:
        lines.append("## ⚠ ESCALATION: Decision Matrix required\n")
        if result.decision_matrix_options:
            for opt in result.decision_matrix_options:
                lines.append(
                    f"### Option {opt.get('option', '?')} — "
                    f"{opt.get('name', 'unnamed')}\n"
                )
                lines.append(f"- **Effect:** {opt.get('effect', '')}")
                lines.append(f"- **Residual risk:** {opt.get('residual_risk', '')}")
                lines.append("")

    lines.append("## Per-reviewer discharge reports\n")
    for r in result.replies:
        lines.append(f"### {r.reviewer}\n")
        if r.error:
            lines.append(f"**Status:** discharge failed ({r.error})\n")
            continue
        lines.append(f"**Overall verdict:** `{r.overall_verdict}`  ")
        lines.append(f"**Headline:** {r.headline}\n")
        if r.new_concerns_attempted > 0:
            lines.append(
                f"**⚠ PROCESS VIOLATION:** attempted to raise "
                f"{r.new_concerns_attempted} new concern(s)\n"
            )
        for s in r.scores:
            status_emoji = {
                "addressed": "✅",
                "partially_addressed": "🟡",
                "not_addressed": "❌",
            }.get(s.status, "❓")
            lines.append(f"- {status_emoji} **{s.concern_id}** — `{s.status}`  ")
            lines.append(f"  {s.justification}")
        lines.append("")

    REVIEW_PATH.write_text("\n".join(lines) + "\n")
    print(f"Wrote {REVIEW_PATH}")
    print(f"Editor verdict: {result.editor_verdict}")
    print(f"Unresolved: {result.unresolved_concerns}")
    print(f"Process violations: {len(result.process_violations)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
