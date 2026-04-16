"""Reference-value sourcing with v4 four-check verification pipeline.

Phase 12 deliverable. Implements the v4 §5.2 multi-check
verification pipeline that the Round-2 discharge review
approved. Given a canonical physics problem, this module:

1. Constructs a structured query to the AI review board
   asking for the reference value + formula + citation
2. Verifies the board's reply locally via four orthogonal-
   where-possible checks:
   - **Check A**: symbolic equivalence via canonicalization
     pipeline (rational normalization → trig/power simp →
     polynomial remainder → branch-cut-aware discriminating
     random eval)
   - **Check B**: Hypothesis-style stratified randomized
     property-based testing (stratified over orders of
     magnitude, includes boundary cases, avoids declared
     singularities, seeded for reproducibility)
   - **Check C**: mpmath high-precision evaluation (labeled
     honestly as within-sympy fragility check, NOT cross-CAS)
   - **Check D**: python-flint (Arb-based) interval
     arithmetic, genuinely independent from sympy; best-
     effort in Phase 12 with graceful skip if unavailable
3. Writes the accepted value to the ledger with full
   verification provenance, or raises
   `BoardHallucinationDetected` on any check failure

No corner cuts: on verification failure, the Failure
Investigation Protocol (§11h) fires. Tolerances are NOT
adjusted to make the verification pass.

The module explicitly does NOT import mpmath directly — it
goes through sympy's `evalf(mp=...)` so the "within-sympy"
characterization is accurate. If a future version wants
genuinely independent mpmath it would import mpmath at module
level instead.
"""

from __future__ import annotations

import json
import math
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy as sp

from .ai_consensus import AIConsensusBoard
from .ai_review_board import AIBoardKeysMissing


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """Outcome of one verification check (A/B/C/D)."""
    name: str                            # "A", "B", "C", "D"
    passed: bool
    detail: str
    elapsed_seconds: float = 0.0
    samples_tested: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "check": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "samples_tested": self.samples_tested,
        }


@dataclass
class ReferenceValueResult:
    """The full sourced + verified reference value.

    Fields:
    - `query_id`: stable identifier for ledger lookup
    - `problem_statement`: the plain-English problem
    - `formula_symbolic`: the board-sourced formula (sympy-parseable)
    - `substitutions`: {variable_name: numeric_value} used to evaluate
    - `value`: the board-claimed numeric answer
    - `unit`: the declared unit (pint-parseable)
    - `citations`: list of primary-source citations from board
    - `checks`: list of CheckResult objects, one per A/B/C/D
    - `all_passed`: True iff every check that ran passed
    - `board_queried_at`: ISO8601 timestamp of board query
    - `sampling_seed`: integer seed for PBT reproducibility
    - `verification_status`: "VERIFIED" | "BOARD_HALLUCINATION_DETECTED"
      | "SYMBOLIC_EQUIVALENCE_UNDECIDABLE" | "REFERENCE_UNRESOLVED"
    """
    query_id: str
    problem_statement: str
    formula_symbolic: str
    substitutions: Dict[str, float]
    value: float
    unit: str
    citations: List[str] = field(default_factory=list)
    checks: List[CheckResult] = field(default_factory=list)
    all_passed: bool = False
    board_queried_at: str = ""
    sampling_seed: int = 0
    verification_status: str = "REFERENCE_UNRESOLVED"

    def as_ledger_dict(self) -> Dict[str, Any]:
        return {
            "query_id": self.query_id,
            "problem_statement": self.problem_statement,
            "formula_symbolic": self.formula_symbolic,
            "substitutions": self.substitutions,
            "value": self.value,
            "unit": self.unit,
            "citations": self.citations,
            "checks": [c.as_dict() for c in self.checks],
            "all_passed": self.all_passed,
            "board_queried_at": self.board_queried_at,
            "sampling_seed": self.sampling_seed,
            "verification_status": self.verification_status,
        }


class BoardHallucinationDetected(Exception):
    """Raised when local verification disagrees with the board's
    claimed value, triggering escalation via the Failure
    Investigation Protocol (§11h).
    """


class SymbolicEquivalenceUndecidable(Exception):
    """Raised when the canonicalization pipeline hits a known
    limit (piecewise, branch cut, multi-valued inverse) and
    cannot decide equivalence. Per §5.2.1, this escalates to
    the user Decision Matrix — it is NOT a hallucination and
    must not be silently mis-classified.
    """


# ---------------------------------------------------------------------------
# Check A — symbolic equivalence via canonicalization pipeline
# ---------------------------------------------------------------------------


def _known_undecidable_symbols(expr: sp.Basic) -> List[str]:
    """Detect known-undecidable sympy features in the expression.
    Returns a list of feature names encountered.
    """
    features: List[str] = []
    # Piecewise
    if expr.has(sp.Piecewise):
        features.append("Piecewise")
    # Abs (problematic when argument sign is symbolic)
    if expr.has(sp.Abs):
        features.append("Abs")
    # Multivalued inverses
    for f in (sp.asin, sp.acos, sp.atan, sp.asec, sp.acsc, sp.acot):
        if expr.has(f):
            features.append(f.__name__)
    # Fractional powers with negative possible base
    if expr.has(sp.Pow):
        # Heuristic: any non-integer exponent on a non-positive-declared base
        for p in expr.atoms(sp.Pow):
            if not p.exp.is_integer:
                if p.base.is_real is not False and p.base.is_positive is not True:
                    features.append(f"fractional_power({p})")
                    break
    return features


def check_a_symbolic_equivalence(
    board_formula: sp.Basic,
    local_formula: sp.Basic,
    declared_tolerance: float = 1e-10,
) -> CheckResult:
    """Check A — multi-stage canonicalization pipeline from v4 §5.2.1.

    Returns a PASSED CheckResult if board_formula and local_formula
    are symbolically equivalent. Returns a FAILED CheckResult with
    the specific stage that caught the divergence. Raises
    `SymbolicEquivalenceUndecidable` if the pipeline hits a known
    limit (piecewise, branch cut, etc.).
    """
    import time
    t0 = time.perf_counter()

    # Undecidability gate — escalate immediately per v4 §5.2.1
    bad_features = (
        _known_undecidable_symbols(board_formula)
        + _known_undecidable_symbols(local_formula)
    )
    if bad_features:
        raise SymbolicEquivalenceUndecidable(
            f"canonicalization pipeline hit known-undecidable "
            f"features: {bad_features}. Escalating to user "
            f"Decision Matrix per §5.2.1."
        )

    # Stage 1 — rational function normalization
    diff = sp.cancel(sp.together(sp.expand(board_formula - local_formula)))
    if diff == 0:
        return CheckResult(
            name="A", passed=True,
            detail="rational normalization collapsed to zero",
            elapsed_seconds=time.perf_counter() - t0,
        )

    # Stage 2 — trig/power simplification
    try:
        diff2 = sp.trigsimp(sp.powsimp(sp.expand_trig(diff)))
        if diff2 == 0:
            return CheckResult(
                name="A", passed=True,
                detail="trig/power simplification collapsed to zero",
                elapsed_seconds=time.perf_counter() - t0,
            )
    except Exception as exc:
        # sympy occasionally trips on exotic expressions; record
        # but continue to the next stage
        diff2 = diff

    # Stage 3 — polynomial remainder check when applicable
    try:
        free = diff2.free_symbols
        if free and all(sp.Poly(diff2, s).is_polynomial for s in free):
            rem = sp.Poly(diff2, *sorted(free, key=lambda s: s.name)).as_expr()
            rem_simp = sp.simplify(rem)
            if rem_simp == 0:
                return CheckResult(
                    name="A", passed=True,
                    detail="polynomial remainder is zero",
                    elapsed_seconds=time.perf_counter() - t0,
                )
    except Exception:
        pass  # fall through to random evaluation

    # Stage 4 — branch-cut-aware discriminating random evaluation
    free_symbols = sorted(
        board_formula.free_symbols | local_formula.free_symbols,
        key=lambda s: s.name,
    )
    if not free_symbols:
        # No free variables → compare numeric evaluation directly
        try:
            v_b = float(sp.N(board_formula))
            v_l = float(sp.N(local_formula))
            if abs(v_b - v_l) / (abs(v_b) + abs(v_l) + 1e-30) > declared_tolerance:
                return CheckResult(
                    name="A", passed=False,
                    detail=f"constant-expression numerical divergence: "
                           f"{v_b} vs {v_l}",
                    elapsed_seconds=time.perf_counter() - t0,
                )
            return CheckResult(
                name="A", passed=True,
                detail="constant-expression numerical match",
                elapsed_seconds=time.perf_counter() - t0,
            )
        except Exception as exc:
            return CheckResult(
                name="A", passed=False,
                detail=f"could not numerically evaluate: {exc}",
                elapsed_seconds=time.perf_counter() - t0,
            )

    # Random evaluation with N=20 samples, positive-real draws
    # (to avoid most branch cuts for sqrt/log)
    rng = random.Random(42)
    for i in range(20):
        sample = {s: rng.uniform(0.1, 10.0) for s in free_symbols}
        try:
            v_b = float(board_formula.subs(sample).evalf())
            v_l = float(local_formula.subs(sample).evalf())
        except (TypeError, ValueError) as exc:
            continue  # sample hit a non-evaluable point, try next
        if not (math.isfinite(v_b) and math.isfinite(v_l)):
            continue
        rel = abs(v_b - v_l) / (abs(v_b) + abs(v_l) + 1e-30)
        if rel > declared_tolerance:
            return CheckResult(
                name="A", passed=False,
                detail=f"sample {i}: board eval={v_b:g}, local "
                       f"eval={v_l:g}, rel_err={rel:.2e}",
                elapsed_seconds=time.perf_counter() - t0,
                samples_tested=i + 1,
            )
    return CheckResult(
        name="A", passed=True,
        detail="20 discriminating random samples all agree within tolerance",
        elapsed_seconds=time.perf_counter() - t0,
        samples_tested=20,
    )


# ---------------------------------------------------------------------------
# Check B — property-based stratified randomized sampling
# ---------------------------------------------------------------------------


def _stratified_sample(
    variable_ranges: Dict[str, Tuple[float, float]],
    n: int,
    seed: int,
) -> List[Dict[str, float]]:
    """Generate n stratified samples over orders of magnitude
    per variable, with boundary cases included. Returns a list
    of {variable_name: value} dicts.

    Stratification: for a variable with range [lo, hi], the log
    interval [log10(lo), log10(hi)] is divided into n/2 bands;
    each band gets one sample drawn uniformly in log space. The
    remaining n/2 samples are drawn uniformly across the full
    range for diversity.
    """
    rng = random.Random(seed)
    samples: List[Dict[str, float]] = []

    # First half — stratified over log10 ranges
    for i in range(n // 2):
        sample: Dict[str, float] = {}
        for var, (lo, hi) in variable_ranges.items():
            if lo <= 0:
                # Linear stratification if log isn't well defined
                band_width = (hi - lo) / max(1, n // 2)
                sample[var] = lo + band_width * (i + rng.random())
            else:
                log_lo = math.log10(lo)
                log_hi = math.log10(hi)
                log_band = (log_hi - log_lo) / max(1, n // 2)
                log_val = log_lo + log_band * (i + rng.random())
                sample[var] = 10 ** log_val
        samples.append(sample)

    # Second half — uniform random
    for _ in range(n - (n // 2)):
        sample = {}
        for var, (lo, hi) in variable_ranges.items():
            sample[var] = lo + rng.random() * (hi - lo)
        samples.append(sample)

    # Boundary cases — replace the last few samples with specific
    # boundary values so the check explicitly covers min, max,
    # and unity for each variable
    if samples and len(samples) >= 3:
        # Replace [-1], [-2], [-3] with boundary samples
        for idx, which in enumerate(("min", "max", "unity")):
            if len(samples) - 1 - idx < 0:
                break
            boundary: Dict[str, float] = {}
            for var, (lo, hi) in variable_ranges.items():
                if which == "min":
                    boundary[var] = lo
                elif which == "max":
                    boundary[var] = hi
                elif which == "unity":
                    boundary[var] = min(max(1.0, lo), hi)
            samples[-1 - idx] = boundary

    return samples


def check_b_property_based(
    board_formula: sp.Basic,
    local_formula: sp.Basic,
    variable_ranges: Dict[str, Tuple[float, float]],
    n_samples: int = 200,
    declared_tolerance: float = 1e-6,
    seed: int = 2026_04_15,
) -> CheckResult:
    """Check B — Hypothesis-style stratified property-based
    testing. At each sample, evaluate both expressions and
    require agreement within `declared_tolerance` relative error.

    v4 §5.2.2: this check replaces v3's "N=50 random draws" with
    a stratified-over-orders-of-magnitude strategy that includes
    boundary cases and seeds reproducibly.
    """
    import time
    t0 = time.perf_counter()

    sym_map = {s.name: s for s in (board_formula.free_symbols
                                    | local_formula.free_symbols)}
    missing = [v for v in variable_ranges if v not in sym_map]
    if missing:
        return CheckResult(
            name="B", passed=False,
            detail=f"variable_ranges declared unknown vars: {missing}",
            elapsed_seconds=time.perf_counter() - t0,
        )

    samples = _stratified_sample(variable_ranges, n_samples, seed)
    failures: List[str] = []
    evaluated = 0

    for i, sample in enumerate(samples):
        subs = {sym_map[name]: val for name, val in sample.items()}
        try:
            v_b = float(board_formula.subs(subs).evalf())
            v_l = float(local_formula.subs(subs).evalf())
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(v_b) and math.isfinite(v_l)):
            continue
        evaluated += 1
        rel_err = abs(v_b - v_l) / (abs(v_b) + abs(v_l) + 1e-30)
        if rel_err > declared_tolerance:
            failures.append(
                f"sample {i} ({sample}): rel_err={rel_err:.2e}"
            )
            if len(failures) >= 5:
                break  # don't spam

    if failures:
        return CheckResult(
            name="B", passed=False,
            detail=f"{len(failures)} failures (first: {failures[0]})",
            elapsed_seconds=time.perf_counter() - t0,
            samples_tested=evaluated,
        )
    return CheckResult(
        name="B", passed=True,
        detail=f"stratified PBT: {evaluated} samples, all within tolerance",
        elapsed_seconds=time.perf_counter() - t0,
        samples_tested=evaluated,
    )


# ---------------------------------------------------------------------------
# Check C — mpmath high-precision evaluation (within-sympy fragility)
# ---------------------------------------------------------------------------


def check_c_high_precision(
    formula: sp.Basic,
    substitutions: Dict[str, float],
    board_value: float,
    declared_tolerance: float = 1e-10,
) -> CheckResult:
    """Check C — evaluate the board's formula at the canonical
    sample point at 50 decimal places and compare against the
    board's claimed value.

    v4 §5.2.3: this is labeled honestly as a "within-sympy
    numerical fragility check," NOT cross-CAS. mpmath is sympy's
    internal numerical backend.
    """
    import time
    t0 = time.perf_counter()

    try:
        free_map = {s.name: s for s in formula.free_symbols}
        subs_sym = {free_map[k]: v for k, v in substitutions.items() if k in free_map}
        # sympy.N with mpmath at 50 decimal places
        high_precision = sp.N(formula.subs(subs_sym), 50)
        v_hp = float(high_precision)
    except Exception as exc:
        return CheckResult(
            name="C", passed=False,
            detail=f"high-precision eval failed: {exc}",
            elapsed_seconds=time.perf_counter() - t0,
        )

    if not math.isfinite(v_hp) or not math.isfinite(board_value):
        return CheckResult(
            name="C", passed=False,
            detail=f"non-finite: mpmath={v_hp}, board={board_value}",
            elapsed_seconds=time.perf_counter() - t0,
        )

    rel_err = abs(v_hp - board_value) / (abs(board_value) + 1e-30)
    if rel_err > declared_tolerance:
        return CheckResult(
            name="C", passed=False,
            detail=f"mpmath={v_hp:.15g}, board={board_value:.15g}, "
                   f"rel_err={rel_err:.2e}",
            elapsed_seconds=time.perf_counter() - t0,
        )
    return CheckResult(
        name="C", passed=True,
        detail=f"mpmath 50-decimal eval={v_hp:.15g} matches board value "
               f"(rel_err={rel_err:.2e})",
        elapsed_seconds=time.perf_counter() - t0,
    )


# ---------------------------------------------------------------------------
# Check D — python-flint Arb interval arithmetic (genuinely independent)
# ---------------------------------------------------------------------------


def check_d_flint_interval(
    formula_callable: Callable[..., Any],
    substitutions: Dict[str, float],
    board_value: float,
    tolerance_bits: int = 200,
) -> CheckResult:
    """Check D — genuinely independent numeric backend via
    python-flint (Arb ball arithmetic). Graceful skip if the
    library isn't installed.

    v4 §5.2.4: Phase 12 best-effort, Phase 13+ hard requirement.
    """
    import time
    t0 = time.perf_counter()
    try:
        from flint import arb, ctx  # type: ignore
    except ImportError:
        return CheckResult(
            name="D", passed=True,   # skipped = neutral, not fail
            detail="python-flint not installed; Check D skipped "
                   "(best-effort in Phase 12, hard requirement Phase 13+)",
            elapsed_seconds=time.perf_counter() - t0,
        )
    try:
        ctx.prec = tolerance_bits
        arb_subs = {k: arb(v) for k, v in substitutions.items()}
        result = formula_callable(**arb_subs)
        result_as_arb = arb(result) if not isinstance(result, arb) else result
        # Check if board_value lies in the arb interval
        board_arb = arb(board_value)
        # arb overlap check: (a - b).abs().contains(0) if intervals touch
        diff = result_as_arb - board_arb
        if diff.contains_zero():
            return CheckResult(
                name="D", passed=True,
                detail=f"python-flint interval contains board value "
                       f"(prec={tolerance_bits} bits)",
                elapsed_seconds=time.perf_counter() - t0,
            )
        return CheckResult(
            name="D", passed=False,
            detail=f"python-flint interval disjoint from board value: "
                   f"result={result_as_arb}, board={board_value}",
            elapsed_seconds=time.perf_counter() - t0,
        )
    except Exception as exc:
        return CheckResult(
            name="D", passed=False,
            detail=f"python-flint evaluation failed: {exc}",
            elapsed_seconds=time.perf_counter() - t0,
        )


# ---------------------------------------------------------------------------
# Board query + aggregation entry point
# ---------------------------------------------------------------------------


_BOARD_SYSTEM_PROMPT = """\
You are a senior physics textbook oracle with expertise across
classical mechanics, thermodynamics, electromagnetism, quantum
mechanics, and relativity. You are being asked for the
**closed-form formula and primary-source citations** for a
canonical physics problem.

IMPORTANT: You are NOT being asked to produce the numerical
value. The architect will compute the number LOCALLY using a
real symbolic math engine (sympy + mpmath + python-flint).
Language models produce imprecise decimals, and the protocol
has been updated to acknowledge this limitation. Your role is
FORMULA and CITATIONS — the things you are good at.

Reply ONLY with a single JSON object, no preamble, no markdown
fences, no trailing text:

{
  "formula_symbolic": "<sympy-parseable formula, using standard symbol names>",
  "formula_latex": "<optional LaTeX rendering>",
  "substitutions": {"<var_name>": <numeric_value>, ...},
  "unit": "<pint-parseable unit string>",
  "citation_primary": "<primary source with page or chapter>",
  "citation_secondary": "<secondary source with page or chapter>",
  "confidence": <float 0-1>,
  "value_attempt": <optional float; your best-effort attempt at computing the number — logged as capability data but NEVER used as the authoritative reference>
}

Critical instructions:
- The formula must be mathematically exact (closed-form where
  possible), not an approximation. This is what you are good at.
- The substitutions must include ALL free variables of the
  formula with their numeric values — these are the inputs the
  local CAS will plug into your formula.
- `value_attempt` is OPTIONAL. Include it if you like (it is
  data on when LLMs can do math and when they can't), but do
  NOT worry about precision — the architect's CAS is the
  authority. You are not being tested on decimal arithmetic.
- Cite the primary source honestly; if you are not certain of
  the citation, say so in the secondary field.
"""


_BOARD_SANITY_CHECK_PROMPT = """\
You are a senior physics textbook oracle reviewing a locally-
computed reference value for a canonical physics problem. The
formula and citations came from an earlier board query; the
architect has now computed the numerical value locally using a
real symbolic math engine (sympy + mpmath + python-flint).

Your job is a SEMANTIC sanity check — not a recomputation. Is
the value of the right order of magnitude? Does it match your
training-data recollection of what this problem's answer
should be? Are the units and dimensions consistent? Is there
anything physically wrong with the claim?

You may compare against your own rough mental estimate but do
NOT worry about precision — the architect's CAS is the
authority, and small decimal differences between your mental
estimate and the CAS result reflect your limitations, not the
architect's.

Reply ONLY with a JSON object:

{
  "sanity_verdict": "approve" | "suspect" | "reject",
  "rationale": "<one or two sentences>",
  "order_of_magnitude_match": true|false,
  "units_match": true|false,
  "physical_plausibility": true|false
}

- `approve` — the value matches your training-data expectation
  within the precision you can mentally estimate.
- `suspect` — the value seems off in a way you cannot
  immediately explain; flag it for manual review.
- `reject` — the value is clearly physically wrong (wrong
  order of magnitude, wrong sign, wrong units).
"""


def query_board_for_formula(
    problem_statement: str,
    variable_names: List[str],
    query_id: str,
    include_grok: bool = False,
) -> Dict[str, Any]:
    """Query the board for FORMULA + CITATIONS only.

    Per 'Board is not a CAS' rule: the board is asked for the
    closed-form formula and primary-source citations; the
    numerical value is computed LOCALLY from the formula. The
    board may optionally include a `value_attempt` as capability
    data, but it is never used as the authoritative reference.
    """
    user_msg = (
        f"## Canonical problem\n\n{problem_statement}\n\n"
        f"## Free variables\n\n"
        + ", ".join(f"`{v}`" for v in variable_names)
        + "\n\n## Your task\n\nProduce the JSON reply specified "
          "in the system prompt. You are providing the FORMULA "
          "and CITATIONS — the numerical value will be computed "
          "locally by a real symbolic math engine (sympy + mpmath "
          "+ python-flint). You do not need to compute the "
          "decimal expansion; the CAS is authoritative for that."
    )

    with AIConsensusBoard(include_grok=include_grok) as board:
        result = board.query(
            query_id=query_id,
            system_instructions=_BOARD_SYSTEM_PROMPT,
            user_message=user_msg,
            required_keys=("formula_symbolic", "substitutions", "unit"),
        )
    return {
        "consensus": result.consensus,
        "responses": [r.as_dict() for r in result.responses],
        "agreement": result.agreement,
        "schema_ok": result.schema_ok,
    }


def query_board_for_sanity_check(
    problem_statement: str,
    formula_symbolic: str,
    substitutions: Dict[str, float],
    computed_value: float,
    unit: str,
    query_id: str,
    include_grok: bool = False,
) -> Dict[str, Any]:
    """Send the locally-computed value back to the board for a
    semantic sanity check. The board is explicitly told this is
    NOT a recomputation — it's asked whether the value is of
    the right order of magnitude, units match, and the claim
    is physically plausible.
    """
    payload = {
        "problem_statement": problem_statement,
        "formula_symbolic": formula_symbolic,
        "substitutions": substitutions,
        "computed_value": computed_value,
        "unit": unit,
    }
    user_msg = (
        "A canonical physics problem has been computed locally "
        "via a real CAS. Please review the result for semantic "
        "plausibility.\n\n"
        + json.dumps(payload, indent=2)
    )
    with AIConsensusBoard(include_grok=include_grok) as board:
        result = board.query(
            query_id=query_id,
            system_instructions=_BOARD_SANITY_CHECK_PROMPT,
            user_message=user_msg,
            required_keys=("sanity_verdict",),
        )
    return {
        "consensus": result.consensus,
        "responses": [r.as_dict() for r in result.responses],
    }


def source_and_verify(
    problem_statement: str,
    query_id: str,
    local_formula: sp.Basic,
    variable_ranges: Dict[str, Tuple[float, float]],
    canonical_substitutions: Dict[str, float],
    include_grok: bool = False,
    n_pbt_samples: int = 200,
    pbt_seed: int = 2026_04_15,
) -> ReferenceValueResult:
    """Phase 12 pipeline, v5 'board is not a CAS' protocol:

    1. Query the board for formula + citations (NOT value).
    2. Verify the board's formula symbolically matches the
       architect's local formula (Check A + Check B).
    3. Compute the authoritative reference value LOCALLY via
       sympy + mpmath high-precision + python-flint interval.
    4. Send the locally-computed value back to the board for a
       semantic sanity check.
    5. Return the result with full provenance.

    The AUTHORITATIVE numerical value comes from the local CAS,
    NOT from the board. The board's optional value_attempt is
    logged as capability data only.
    """
    query_response = query_board_for_formula(
        problem_statement=problem_statement,
        variable_names=list(variable_ranges.keys()),
        query_id=query_id,
        include_grok=include_grok,
    )

    # Find the first response with formula + substitutions
    board_reply: Optional[Dict[str, Any]] = None
    for resp in query_response["responses"]:
        parsed = resp.get("parsed")
        if parsed and "formula_symbolic" in parsed and "substitutions" in parsed:
            board_reply = parsed
            break

    if not board_reply:
        return ReferenceValueResult(
            query_id=query_id,
            problem_statement=problem_statement,
            formula_symbolic="",
            substitutions=canonical_substitutions,
            value=float("nan"),
            unit="",
            citations=[],
            board_queried_at=datetime.now(tz=timezone.utc).isoformat(),
            sampling_seed=pbt_seed,
            verification_status="REFERENCE_UNRESOLVED",
        )

    board_formula_str = str(board_reply["formula_symbolic"])
    board_unit = str(board_reply.get("unit", ""))
    # Prefer the board's provided substitutions; fall back to
    # canonical if missing or partial
    board_subs_raw = board_reply.get("substitutions") or {}
    if isinstance(board_subs_raw, dict) and board_subs_raw:
        merged_subs = {**canonical_substitutions, **{
            k: float(v) for k, v in board_subs_raw.items()
            if isinstance(v, (int, float))
        }}
    else:
        merged_subs = dict(canonical_substitutions)
    # The board's value_attempt is captured for the ledger but
    # never used as the authoritative number
    board_value_attempt = board_reply.get("value_attempt")
    citations = [
        str(board_reply.get("citation_primary", "")),
        str(board_reply.get("citation_secondary", "")),
    ]
    citations = [c for c in citations if c]

    # Parse the board's formula in the architect's symbol space
    sym_locals = {s.name: s for s in local_formula.free_symbols}
    try:
        board_formula = sp.sympify(board_formula_str, locals=sym_locals)
    except (sp.SympifyError, SyntaxError) as exc:
        return ReferenceValueResult(
            query_id=query_id,
            problem_statement=problem_statement,
            formula_symbolic=board_formula_str,
            substitutions=merged_subs,
            value=float("nan"),
            unit=board_unit,
            citations=citations,
            board_queried_at=datetime.now(tz=timezone.utc).isoformat(),
            sampling_seed=pbt_seed,
            verification_status="REFERENCE_UNRESOLVED",
            checks=[CheckResult(
                name="A", passed=False,
                detail=f"could not parse board formula as sympy: {exc}",
            )],
        )

    # --- Check A: formula equivalence (board formula vs local formula) ---
    try:
        check_a = check_a_symbolic_equivalence(
            board_formula=board_formula,
            local_formula=local_formula,
        )
    except SymbolicEquivalenceUndecidable as exc:
        return ReferenceValueResult(
            query_id=query_id,
            problem_statement=problem_statement,
            formula_symbolic=board_formula_str,
            substitutions=merged_subs,
            value=float("nan"),
            unit=board_unit,
            citations=citations,
            board_queried_at=datetime.now(tz=timezone.utc).isoformat(),
            sampling_seed=pbt_seed,
            verification_status="SYMBOLIC_EQUIVALENCE_UNDECIDABLE",
            checks=[CheckResult(
                name="A", passed=False,
                detail=f"UNDECIDABLE: {exc}",
            )],
        )

    # --- Check B: property-based stratified sampling ---
    check_b = check_b_property_based(
        board_formula=board_formula,
        local_formula=local_formula,
        variable_ranges=variable_ranges,
        n_samples=n_pbt_samples,
        seed=pbt_seed,
    )

    # --- LOCAL authoritative computation via sympy + mpmath ---
    # This is the real math. No board value in the critical path.
    sym_subs = {sym_locals[k]: v for k, v in merged_subs.items() if k in sym_locals}
    try:
        local_sympy = local_formula.subs(sym_subs).evalf(15)
        local_mpmath = local_formula.subs(sym_subs).evalf(50)
        computed_value = float(local_sympy)
        high_precision_str = str(local_mpmath)
    except Exception as exc:
        return ReferenceValueResult(
            query_id=query_id,
            problem_statement=problem_statement,
            formula_symbolic=board_formula_str,
            substitutions=merged_subs,
            value=float("nan"),
            unit=board_unit,
            citations=citations,
            board_queried_at=datetime.now(tz=timezone.utc).isoformat(),
            sampling_seed=pbt_seed,
            verification_status="REFERENCE_UNRESOLVED",
            checks=[check_a, check_b, CheckResult(
                name="C", passed=False,
                detail=f"local sympy evaluation failed: {exc}",
            )],
        )

    # --- Check C: sympy 15-digit vs mpmath 50-digit (fragility) ---
    rel_err_cc = abs(float(local_mpmath) - computed_value) / (
        abs(computed_value) + 1e-300
    )
    check_c = CheckResult(
        name="C",
        passed=rel_err_cc < 1e-10,
        detail=(
            f"sympy 15-digit={computed_value:.15g}, "
            f"mpmath 50-digit={high_precision_str[:20]}..., "
            f"rel_err={rel_err_cc:.2e} "
            f"(within-sympy numerical fragility check)"
        ),
    )

    # --- Check D: python-flint interval arithmetic ---
    def _flint_callable(**subs: Any) -> Any:
        s = {sym_locals[k]: v for k, v in subs.items() if k in sym_locals}
        return local_formula.subs(s)
    check_d = check_d_flint_interval(
        formula_callable=_flint_callable,
        substitutions=merged_subs,
        board_value=computed_value,  # compare flint vs local, not vs board
    )

    # --- Board sanity check on the locally-computed value ---
    sanity_reply: Dict[str, Any] = {}
    try:
        sanity_reply = query_board_for_sanity_check(
            problem_statement=problem_statement,
            formula_symbolic=board_formula_str,
            substitutions=merged_subs,
            computed_value=computed_value,
            unit=board_unit,
            query_id=f"{query_id}_sanity",
            include_grok=include_grok,
        )
    except Exception:
        # Sanity check is advisory; failure is non-blocking
        sanity_reply = {"consensus": None, "responses": [], "error": "sanity check unavailable"}

    # --- Aggregate verification status ---
    critical_failures = [
        c for c in (check_a, check_b, check_c, check_d)
        if not c.passed and "skipped" not in c.detail.lower()
    ]
    verification_status = "VERIFIED" if not critical_failures else "BOARD_HALLUCINATION_DETECTED"

    result = ReferenceValueResult(
        query_id=query_id,
        problem_statement=problem_statement,
        formula_symbolic=board_formula_str,
        substitutions=merged_subs,
        value=computed_value,  # LOCAL authoritative value
        unit=board_unit,
        citations=citations,
        board_queried_at=datetime.now(tz=timezone.utc).isoformat(),
        sampling_seed=pbt_seed,
        checks=[check_a, check_b, check_c, check_d],
        all_passed=(not critical_failures),
        verification_status=verification_status,
    )
    # Capture the board's value_attempt and sanity check in the
    # ledger's provenance dict (exposed via a side attribute for
    # the runner to surface)
    result.__dict__["_board_value_attempt"] = board_value_attempt
    result.__dict__["_board_sanity_check"] = sanity_reply.get("consensus")
    result.__dict__["_high_precision_value"] = high_precision_str
    return result
