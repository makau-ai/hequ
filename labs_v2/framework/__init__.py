"""hequ labs v2 — cross-domain discovery framework.

A fresh start informed by the historical methodology of Maxwell, Noether,
Shannon, and Feynman, and by the 2024-2026 state of the art in symbolic
regression, automated theorem proving, and applied category theory.

Architecture (four layers)
--------------------------

1. **Canonical reference** — `equations/<domain>/<eq_id>/` directories,
   each with: `equation.yaml` (dimensional signature + canonical sympy
   form), `notebook.py` (jupytext, deep derivation + correct and
   incorrect worked examples with real data), `data/` (real lab data
   files), `lean/stub.lean` (theorem statement).

2. **Unification sieves** — `layer2_sieves.py`:
   - Dimensional Π-signature (pint + nullspace over the dimension
     matrix)
   - Symmetry-algebra fingerprint (sympy, for equations with an
     explicit Lagrangian)
   - Structural equality modulo theory (sympy simplify + equals; ATP
     fallback stub)

3. **Discovery loop** — `layer3_discovery.py`:
   - Proposer: generates substitutions between candidate pairs
   - Evaluator: numeric + symbolic equivalence after substitution
   - Ledger: every hypothesis recorded with outcome and evidence

4. **Certification** — `layer4_certification.py`:
   - For top-ranked discoveries, emit a Lean 4 theorem statement using
     the project's typed-expression representation. Compilation is
     optional in v2.

Design non-negotiables (from the research agents' reports)
----------------------------------------------------------
- **Every parameter is dimensioned via pint before it enters any
  cross-domain comparison.** Lexical collisions (Newton's `r` =
  radius vs. logistic's `r` = rate) are eliminated at the type level.
- **Coincidence is the null hypothesis.** Every proposed connection
  carries a baseline probability computed over the search space.
- **Three-tier output** — proved / empirically-supported / conjectural
  — never collapsed (Gödel's warning).
- **Each equation ships with a correct example AND an incorrect
  example** (the out-of-domain failure mode) — the discriminator that
  proves the formal method does real work.
- **The ledger is append-only.** Rejected hypotheses are never
  deleted; their rejection criterion is part of the record.
"""

from .typed_expression import TypedExpression, load_equation, load_all_equations
from .discovery_ledger import DiscoveryLedger, Hypothesis, HypothesisOutcome

__all__ = [
    "TypedExpression",
    "load_equation",
    "load_all_equations",
    "DiscoveryLedger",
    "Hypothesis",
    "HypothesisOutcome",
]
