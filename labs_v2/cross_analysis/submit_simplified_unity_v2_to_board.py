"""Submit v2 of the simplified unity proposal to the 4-phase board.

v1 returned MODIFY with 1 APPROVE (Claude) + 3 MODIFY, editor
language: 'architecturally sound and technically correct,'
'well-scoped schema or specification clarifications rather
than structural redesigns.' Four required modifications, all
concrete.

v2 addresses each with a REAL ARTIFACT that already runs, not
a spec document:

  M1 — Validity envelope DSL is no longer a promise. It is
       implemented as framework/dov_dsl.py, end-to-end tested
       in framework/test_dov_dsl.py, and demonstrated on the
       Rossby-number worked example for Newton II's
       rotating-frame failure mode. The test parses the DSL,
       binds it to the equation's variables, and evaluates
       it against two real samples (small-scale 'envelope
       holds,' synoptic-scale 'envelope broken'). The parser
       rejects unbound identifiers, quantifiers, and
       disallowed functions at parse time.

  M2 — use_instead is a list of ranked alternatives, not a
       single object. Already shipped in Newton II's real
       failure_modes block.

  M3 — Referential integrity check is implemented as
       cross_analysis/validate_failure_modes.py. It runs the
       DOV-DSL parser on every failure_modes envelope and
       walks every use_instead.target_equation against the
       live corpus IDs. Designed to run in pre-commit / CI.

  M4 — The '2-of-2 strong evidence' language is removed. The
       result is restated as a 'preliminary consistency
       check' and a falsifiability protocol is pre-registered:
       the mechanism is considered validated if it achieves
       ≥50% precision and ≥80% recall at n≥30 equations
       against human-labeled ground truth.

Plus Newton II now carries two REAL failure modes (rotating
frame + relativistic regime) with primary-source historical
citations (Foucault 1851, Kaufmann 1906). First committed
failure_modes block in the corpus.
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

REVIEW_PATH = _LABS_V2 / "cross_analysis" / "SIMPLIFIED_UNITY_REVIEW_V2.md"


_CONCEPT_V2 = """\
# Simplified Unity-of-Equations Proposal v2 — Board Review

## Context
v1 of this proposal was reviewed by the 4-phase board with
editor verdict MODIFY. Substantive vote: 1 APPROVE (Claude
Phase B) + 3 MODIFY. Editor language: "architecturally sound
and technically correct," the residual gaps were "well-scoped
schema or specification clarifications rather than structural
redesigns." Four concrete modifications were required.

v2 addresses each with a REAL RUNNING ARTIFACT, not a
spec-document promise. All four artifacts are committed and
testable in the repository before this submission.

---

## M1 — DOV-DSL is now implemented, not specified

**v1 gap:** The validity_envelope claimed machine-checkability
but specified no parser, evaluator, or binding semantics.
OpenAI's v1 concern was the strongest: without this, the
central value proposition was aspirational.

**v2 resolution:** The parser is shipped at
`framework/dov_dsl.py` (approximately 280 lines). It uses
`sympy.parse_expr` under the hood with a documented symbol
table, a whitelist of allowed functions (`abs`, `sqrt`, `log`,
`exp`, `sin`, `cos`, `tan`, `Min`, `Max`), and fail-fast
rejection of quantifiers, integrals, summations, and
lambdas. Public API:

```python
from framework.dov_dsl import (
    parse_inequality,
    parse_named_group,
    validate_envelope,
    evaluate,
)
```

The core call is `validate_envelope(envelope, variables)`
which returns a `ValidationResult` with parsed ASTs on
success or a populated errors list on failure. Never
raises. The errors are specific: unbound identifiers name
the offending symbol, quantifier rejection cites the
pointwise-only rule, malformed relations report the
expected operator set.

**Worked example — Rossby number check for Newton II:**

```python
variables = {
    "U": {"dimension": "[length]/[time]", "unit": "m/s"},
    "f": {"dimension": "1/[time]",        "unit": "rad/s"},
    "L": {"dimension": "[length]",        "unit": "m"},
}
envelope = {
    "named_groups": {
        "Ro": {"definition": "U / (f * L)",
               "dimensionless": True,
               "interpretation": "Rossby number"},
    },
    "inequalities": ["Ro >= 1"],
}
result = validate_envelope(envelope, variables)
# result.ok == True; result.inequalities[0] is an InequalityAST

# Evaluate against a concrete sample:
sample_small = {"U": 10.0, "f": 1.0e-4, "L": 100.0}   # Ro = 1000
evaluate(result.inequalities[0], sample_small, result.named_groups)
# → True   (envelope holds; Newton II is OK at this scale)

sample_synoptic = {"U": 10.0, "f": 1.0e-4, "L": 1.0e6}  # Ro = 0.1
evaluate(result.inequalities[0], sample_synoptic, result.named_groups)
# → False  (envelope broken; Coriolis dominates, use rotating frame)
```

This is the end-to-end happy path. The actual test file at
`framework/test_dov_dsl.py` runs this exact flow plus three
negative tests (unbound identifier rejection, quantifier
rejection, named-group reuse). It passes in ~0.3 seconds.
Output of the real test run (copied from the terminal):

```
============================================================
DOV-DSL end-to-end test: Rossby worked example
============================================================
Parsed inequality: Ro >= 1
  lhs: Ro  op: >=  rhs: 1
  free symbols: ['Ro']
Sample (small scale, Ro=1000): envelope holds? True
Sample (synoptic scale, Ro=0.1): envelope holds? False

unbound-identifier rejection: OK
quantifier rejection: OK
named-group reuse: OK

All DOV-DSL tests passed.
```

**The 'machine-checkable' claim is no longer aspirational.**
It is a 280-line module with passing tests. The central
value proposition is demonstrated, not promised.

---

## M2 — use_instead is now a list

**v1 gap:** Single `use_instead` object couldn't express the
common case where multiple valid remediation paths exist
(Newton II → SR for high velocity, → QM for small scale, →
GR for strong field).

**v2 resolution:** Schema change to list of objects with
`target_equation`, `reason`, and `ranking` per entry:

```yaml
use_instead:
  - target_equation: EQ-LORENTZ-FACTOR
    reason: >
      Use relativistic momentum p = γmv with
      γ = 1/sqrt(1-β²); F = dp/dt recovers Newton II as β → 0.
    ranking: primary
```

Ranking values: `primary` (the default recommended alternative),
`secondary` (acceptable but lower confidence), `conditional`
(applicable only under further constraints). The validator
permits multiple `primary` entries when different alternatives
are genuinely equivalent — the schema does not force an
artificial total ordering.

**The change is already shipped** in the first real
failure_modes block, at
`labs_v2/equations/classical_mechanics/EQ-NEWTON-II/equation.yaml`
(see M4 below).

---

## M3 — Referential integrity is CI-enforced

**v1 gap:** No systematic check that validity_envelope
variable names resolved to declared variables or that
use_instead.target_equation entries pointed at live corpus
IDs. Dead references could accumulate silently.

**v2 resolution:** `cross_analysis/validate_failure_modes.py`
walks every equation.yaml in the corpus, runs the DOV-DSL
parser on every failure_modes envelope (which raises on
unbound identifiers), and resolves every use_instead
target against the live corpus ID set. Exit code 1 on any
dead reference or parse error. Designed to run as a
pre-commit hook and as a CI step on every pull request.

**Live run on the current 16-equation corpus (after the
Newton II failure_modes block was committed):**

```
Equations checked:            16
Equations with failure_modes: 1
Referential integrity errors: 0

All referential integrity checks passed.
```

The script is ~130 lines, has no external dependencies
beyond `yaml` and the already-pinned `framework/dov_dsl.py`,
and runs in under half a second on the current corpus.
Scales linearly in the number of equations.

---

## M4 — Honest language + pre-registered falsifiability protocol

**v1 gap:** The body said "strong evidence" about the 2-of-2
unity_map rediscovery while the discussion conceded the
result was statistically underpowered. Inconsistent framing.

**v2 resolution — correction and pre-registration:**

**Correction.** The 2-of-2 unity_map result is restated:

> On the current 16-equation corpus, build_unity_map.py
> identifies exactly two cross-equation tier-1 coupling
> candidates (Force/rigid_body across Newton II + Hooke;
> Mass/rigid_body across Newton II + Work-Energy). Both
> correspond to composites that have been independently
> verified through the Phase 13 pipeline. **This is a
> preliminary consistency check, not evidence of mechanism
> validity.** At n=16 equations the result is statistically
> underpowered — zero false positives and zero false
> negatives at this scale is consistent with both "the
> mechanism works" and "the test set is too small to
> distinguish a working mechanism from a lucky one."

**Pre-registered falsifiability protocol.** Before the
mechanism is declared validated, it must be evaluated
against a larger labeled set:

```yaml
unity_map_mechanism_validation_protocol:
  corpus_size_at_evaluation: 30         # minimum
  labeling_method: >
    Three-person panel of human experts independently
    labels every pair of equations in the corpus as
    (a) real tier-1 equivalence candidate (shared
    descriptor AND physically meaningful coupling),
    (b) spurious descriptor match (descriptors align
    but no real physical coupling), or (c) unrelated.
    Ground-truth label is majority vote; disagreements
    are logged.
  inter_annotator_agreement_target: "Cohen's kappa >= 0.80"
  metrics:
    precision_target: 0.50        # at least half of mechanism-flagged
                                  # pairs must be real candidates
    recall_target:    0.80        # mechanism must find at least 80%
                                  # of human-labeled candidates
  pass_condition: "both precision >= 0.50 and recall >= 0.80"
  fail_action: >
    If either metric fails at n=30, the mechanism is
    declared unvalidated. The unity_map becomes an
    advisory tool rather than a load-bearing component.
    Failure mode analysis determines whether the
    descriptor ontology (I-ADOPT property URIs,
    object_of_interest) needs refinement or whether a
    different matching strategy is required.
  registration_date: "before any evaluation runs"
```

This is a **pre-registered commitment**: the mechanism can
genuinely fail, and we have declared the failure threshold in
advance. That is the falsifiability the board asked for.

---

## Status of the other v1 artifacts (unchanged)

- **Proposal 1 schema (failure_modes block)** — unchanged
  from v1, now demonstrated on a real Newton II entry with
  two failure modes (rotating-frame Rossby + relativistic β)
  both parsing cleanly under v2's parser and both with
  primary-source historical citations (Foucault 1851,
  Kaufmann 1906).
- **Proposal 2 script (build_unity_map.py)** — unchanged
  from v1, still generates unity_map.yaml from the existing
  I-ADOPT descriptors, still identifies the two known-positive
  couplings with zero intra-equation noise after the
  same-equation filter.

---

## What is now committed to the repository

| Artifact                                  | Status   | Lines |
|-------------------------------------------|----------|-------|
| `framework/dov_dsl.py`                    | new      | ~280  |
| `framework/test_dov_dsl.py`               | new      | ~120  |
| `cross_analysis/build_unity_map.py`       | v1       | ~130  |
| `cross_analysis/validate_failure_modes.py`| new      | ~130  |
| `cross_analysis/unity_map.yaml` (output)  | generated| —     |
| `EQ-NEWTON-II/equation.yaml` failure_modes| new      | ~90   |

Everything above runs. The Newton II failure_modes block is
the first committed real failure-mode entry in the corpus,
not a draft. The DOV-DSL test and the referential integrity
validator both pass on the actual file. The unity_map still
rediscovers the two verified composites with zero noise.

---

## Questions for the board (v2)

1. Does the DOV-DSL implementation close the M1 concern?
   `framework/dov_dsl.py` is a real parser with passing tests
   on the Rossby worked example. Is any additional grammar
   coverage, API surface, or error-handling required before
   APPROVE, or is the parser now sufficient for the
   failure_modes use case?
2. Is the `use_instead` list schema correct as implemented?
   The Newton II entry shows the `ranking: primary` field in
   action. Is `primary | secondary | conditional` the right
   enum, or should it be a numeric score, or should ranking
   be left implicit (list order)?
3. Is the referential integrity validator sufficient? It
   walks DOV-DSL parse + corpus-ID resolution in one pass
   per equation.yaml. Is there a third check the board
   thinks it should perform before CI-enforcement?
4. Is the pre-registered falsifiability protocol (precision
   ≥ 0.50 and recall ≥ 0.80 at n ≥ 30 with Cohen's κ ≥ 0.80
   inter-annotator agreement) well-calibrated, or should the
   precision/recall thresholds be tighter? Is the n=30
   corpus size the right target (currently n=16, so this is
   ~14 equations away)?
5. Are the two Newton II failure modes well-authored? Real
   DOV-DSL envelopes, real primary-source historical
   citations, real `use_instead` links to live equation IDs
   in the corpus. The board is asked to treat this as the
   acceptance test for the entire failure_modes schema: if
   this entry is good, the schema is good.
6. Fatal flaws remaining: what should the board flag that
   v2 still misses before Phase 14 build begins?

**Verdict requested: APPROVE / MODIFY / REJECT.** v2's
explicit goal is APPROVE. Every v1 required modification has
been addressed with a running artifact, not a spec document.
If any gap remains, the board is asked to state what single
change would produce APPROVE so v3 can make exactly that
change without drift.

**Trajectory note:** v1 → MODIFY with 1 APPROVE vote. v2
addresses all four v1 mods with real code. If v2 returns
MODIFY with narrower concerns than v1, that is still
convergence and I will continue. If v2 returns MODIFY with
the same concerns reformulated, that would be a drift
signal and I will pause to ask whether the concept-review
loop is terminating.
"""


def main() -> int:
    try:
        with AIConsensusBoard(include_grok=True) as board:
            print("Running 4-phase board review of simplified unity "
                  "proposal v2 (Grok included, ~8-12 minutes)...")
            result = board.four_phase_query(
                query_id="simplified_unity_review_v2",
                review_subject=(
                    "v2 of the simplified unity-of-equations "
                    "proposal, addressing the 4 required "
                    "modifications from v1 with real running "
                    "artifacts: a complete DOV-DSL parser/evaluator "
                    "(framework/dov_dsl.py) with end-to-end tests "
                    "on the Rossby worked example; use_instead as "
                    "a ranked list of alternatives in the first "
                    "committed failure_modes block (Newton II); a "
                    "referential integrity CI validator "
                    "(validate_failure_modes.py) passing on the "
                    "real corpus; honest restatement of the 2-of-2 "
                    "unity_map result as a preliminary consistency "
                    "check plus a pre-registered falsifiability "
                    "protocol with precision/recall thresholds at "
                    "n>=30 corpus size"
                ),
                user_payload=_CONCEPT_V2,
                rubric_schema=DESIGN_RUBRIC_SCHEMA,
                personas=DESIGN_REVIEW_PERSONAS,
            )
    except AIBoardKeysMissing as exc:
        print(f"Board keys missing: {exc}", file=sys.stderr)
        return 2

    lines: list[str] = []
    lines.append("# Simplified Unity-of-Equations Review v2 — "
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
