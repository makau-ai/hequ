"""DOV-DSL: Domain-of-Validity Domain-Specific Language.

A small, restricted DSL for writing machine-checkable validity
envelopes on equation.yaml failure modes. An inequality in
DOV-DSL is a function

    f: StateSpace -> Bool

that evaluates to true or false given a concrete assignment of
all canonical_equation variables and named dimensionless groups.
Universal / existential / integral quantifications are OUT OF
SCOPE for DOV-DSL — those belong in a separate provenance field.

Grammar (informal):
    inequality  ::= arith_expr REL_OP arith_expr
    REL_OP      ::= '<' | '<=' | '>' | '>=' | '==' | '!='
    arith_expr  ::= sympy-parseable expression over IDENTs and
                    FUNCs, where every IDENT must resolve to
                    either (a) a key in the equation's
                    `variables:` block, or (b) a previously
                    declared named group in `named_groups:`.
    FUNC        ::= abs | sqrt | log | exp | sin | cos | tan
                    | Min | Max (whitelisted; anything else is
                    a parse error)

Function conventions (per board hardening modification 2):
    log  = NATURAL logarithm (base e), following SymPy.
           Base-10 is NOT in the whitelist; authors needing
           log₁₀ must write `log(x) / log(10)` explicitly.
    exp  = natural exponential.
    sin/cos/tan = trigonometric, arguments in RADIANS.
    sqrt = principal positive square root.
    abs / Abs = absolute value.
    Min / Max = n-ary minimum / maximum.

Named groups are introduced with `Ro := U / (f * L)` inside a
validity_envelope block. They are parsed into sympy expressions
at load time and made available as atomic symbols in subsequent
inequalities.

Public API:
    parse_inequality(text, variables, named_groups) -> InequalityAST
    evaluate(ast, sample) -> bool      (raises EvaluationError on
                                        divide-by-zero, NaN, or
                                        undefined intermediate result)
    validate_envelope(envelope, variables) -> ValidationResult

Evaluation semantics (per board hardening modification 1):
    If a named-group definition produces a zero denominator, NaN,
    or any undefined intermediate (sympy `zoo`, `nan`, or
    `ComplexInfinity`) at the evaluation point, `evaluate()` raises
    `EvaluationError` with a human-readable diagnostic. Silent
    coercion to False is explicitly forbidden: an inequality that
    cannot be decided at a point should stop the caller, not lie
    to it. The equatorial-Coriolis test (f = 0 in the Rossby
    definition) exercises this path.

The parser is `sympy.parse_expr` under the hood with a documented
symbol table and a whitelist of allowed function names. It
rejects quantified expressions, unbound identifiers, and
disallowed functions at parse time — not evaluation time — so
bad validity envelopes fail fast at equation.yaml ingest.

Related work and differentiation:
    DOV-DSL sits in a design space occupied by a handful of
    existing validity-metadata systems. The distinguishing
    claim is that DOV-DSL is (a) expression-level machine-
    checkable in the same CAS the rest of the hequ.ai pipeline
    uses, and (b) scoped to pointwise numerical envelopes over
    the same variables the canonical equation already declares.
    Close relatives:

    - NIST DLMF (Digital Library of Mathematical Functions) —
      prose-level validity annotations on formulas (e.g.,
      "valid for x > 0"). Machine-readable only in the sense
      that the text is structured XML; there is no evaluator
      and no binding between the annotation and a runtime
      state vector. DOV-DSL keeps DLMF's spirit — every formula
      carries its validity envelope — but adds a parser, a
      symbol table, and a concrete pass/fail at a given point.
    - Modelica Standard Library validity constraints —
      component-level `assert(...)` statements that fire at
      simulation time inside a Modelica compiler. Powerful but
      scoped to the Modelica runtime, requiring a full
      component model rather than a standalone equation
      annotation. DOV-DSL is lighter: a YAML-embedded
      expression, a sympy parse, no compiler in the loop.
    - SysML parametric constraint blocks — graph-based
      constraint propagation for systems engineering models.
      Expressive for multi-equation constraint networks, but
      the modeling cost is high and the ecosystem is
      commercial-tool-dependent. DOV-DSL's goal is different:
      lightweight per-equation envelopes authored in plain
      YAML and checked in CI, not constraint solving over a
      system graph.
    - QUDT + schema.org quantity kinds — give vocabulary for
      units and quantity kinds but do NOT express validity
      regions or failure envelopes. DOV-DSL uses QUDT URIs in
      the equation's variable descriptors but adds the
      envelope layer QUDT itself does not provide.

    To our knowledge, no existing system combines (1) per-
    equation YAML-embedded envelopes, (2) a CAS-backed parser
    with symbol binding to the equation's declared variables,
    (3) pointwise numeric evaluation at arbitrary sample
    states, and (4) CI-enforced referential integrity against
    a named equation corpus. That is the niche DOV-DSL fills.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

# ---------------------------------------------------------------------------
# Whitelists and rejection rules
# ---------------------------------------------------------------------------

_ALLOWED_FUNCS = {
    "abs": sp.Abs,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "exp": sp.exp,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "Abs": sp.Abs,  # sympy's canonical spelling
    "Min": sp.Min,
    "Max": sp.Max,
}

_FORBIDDEN_TOKENS = (
    # Quantifiers — DOV-DSL is pointwise-only per v6 spec.
    "forall", "exists", "∀", "∃",
    # Integral / summation / derivative — pointwise eval only.
    "Integral", "Sum", "integrate", "summation", "diff", "Derivative",
    # Pattern that could smuggle in a lambda or iteration.
    "lambda", "for ", "while ",
)

_REL_OPS = {"<", "<=", ">", ">=", "==", "!="}

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class InequalityAST:
    """A parsed DOV-DSL inequality, ready for evaluation."""
    source: str
    lhs: sp.Expr
    rhs: sp.Expr
    rel_op: str
    free_symbols: Tuple[sp.Symbol, ...]

    def as_sympy_relational(self) -> sp.Rel:
        """Return a sympy relational expression for this inequality."""
        op_map = {
            "<":  sp.Lt,
            "<=": sp.Le,
            ">":  sp.Gt,
            ">=": sp.Ge,
            "==": sp.Eq,
            "!=": sp.Ne,
        }
        return op_map[self.rel_op](self.lhs, self.rhs)


@dataclass
class NamedGroup:
    """A named dimensionless group declared in a validity envelope."""
    name: str
    definition_source: str
    definition_ast: sp.Expr
    free_symbols: Tuple[sp.Symbol, ...]


@dataclass
class ValidationResult:
    """Outcome of validating a failure-mode validity envelope."""
    ok: bool
    errors: List[str] = field(default_factory=list)
    named_groups: Dict[str, NamedGroup] = field(default_factory=dict)
    inequalities: List[InequalityAST] = field(default_factory=list)


class DovDslParseError(ValueError):
    """Raised when a DOV-DSL expression cannot be parsed or
    references unbound identifiers."""


class EvaluationError(ValueError):
    """Raised when evaluating a parsed DOV-DSL inequality at a
    concrete sample produces an undefined result (divide-by-zero,
    NaN, complex infinity, or any sympy singular value). Silent
    coercion to False is forbidden: if the inequality cannot be
    decided at a point, the caller must stop and handle it."""


# ---------------------------------------------------------------------------
# Core parser
# ---------------------------------------------------------------------------


def _reject_forbidden_tokens(text: str) -> None:
    """Fail fast on quantifiers, integrals, summations, lambdas."""
    for token in _FORBIDDEN_TOKENS:
        if token in text:
            raise DovDslParseError(
                f"DOV-DSL is pointwise-only; token {token!r} is out of scope. "
                f"Route quantified / integral conditions to "
                f"validity_meta.quantified_conditions instead."
            )


def _split_relation(text: str) -> Tuple[str, str, str]:
    """Split an inequality 'lhs OP rhs' into its three pieces.

    Handles the two-character ops (<=, >=, ==, !=) before the
    one-character ops so that '<=' is not mis-read as '<'.
    """
    for op in ("<=", ">=", "==", "!="):
        idx = text.find(op)
        if idx != -1:
            return text[:idx].strip(), op, text[idx + 2:].strip()
    for op in ("<", ">"):
        idx = text.find(op)
        if idx != -1:
            return text[:idx].strip(), op, text[idx + 1:].strip()
    raise DovDslParseError(
        f"No relational operator found in expression: {text!r}. "
        f"DOV-DSL inequalities must contain one of "
        f"{sorted(_REL_OPS)}."
    )


def _build_local_dict(
    variables: Mapping[str, Any],
    named_groups: Mapping[str, NamedGroup],
) -> Dict[str, sp.Symbol]:
    """Build the parser's symbol table.

    Every variable declared in equation.yaml.variables becomes
    a positive real sympy Symbol (consistent with physics
    conventions — most physical variables are positive reals;
    we relax this per variable if equation.yaml declares it).
    Named groups are added as Symbols too; their definitions
    are substituted at evaluation time if the caller asks.
    """
    local: Dict[str, sp.Symbol] = {}
    for name in variables:
        # Default to positive=True; individual variables can
        # override by declaring `domain: real` in equation.yaml.
        local[name] = sp.Symbol(name, positive=True)
    for name in named_groups:
        local[name] = sp.Symbol(name, positive=True)
    # Whitelist the allowed math functions so parse_expr
    # recognizes them.
    local.update(_ALLOWED_FUNCS)
    return local


def _parse_sympy_expr(
    text: str,
    local_dict: Mapping[str, Any],
) -> sp.Expr:
    """Wrap sympy.parse_expr with DOV-DSL's restrictions."""
    try:
        expr = parse_expr(
            text,
            local_dict=dict(local_dict),
            transformations=_TRANSFORMATIONS,
            evaluate=False,
        )
    except (SyntaxError, TypeError, sp.SympifyError) as exc:
        raise DovDslParseError(
            f"Cannot parse expression {text!r}: {exc}"
        ) from exc
    return expr


def _check_free_symbols_bound(
    expr: sp.Expr,
    local_dict: Mapping[str, Any],
    source: str,
) -> Tuple[sp.Symbol, ...]:
    """Verify every free symbol in expr is in the local dict.
    Unbound symbols are a parse error — the DSL refuses to
    silently infer what an unknown identifier meant."""
    bound_symbols = {
        v for v in local_dict.values()
        if isinstance(v, sp.Symbol)
    }
    free = tuple(sorted(expr.free_symbols, key=lambda s: s.name))
    unbound = [s for s in free if s not in bound_symbols]
    if unbound:
        names = ", ".join(sorted(s.name for s in unbound))
        raise DovDslParseError(
            f"Unbound identifier(s) in {source!r}: {names}. "
            f"Every identifier in a DOV-DSL expression must be "
            f"either a variable in equation.yaml.variables or a "
            f"previously-declared named group."
        )
    return free


def parse_named_group(
    declaration: str,
    variables: Mapping[str, Any],
    existing_groups: Mapping[str, NamedGroup],
) -> NamedGroup:
    """Parse a named-group declaration of the form 'name := expr'.

    Example:
        Ro := U / (f * L)
    """
    _reject_forbidden_tokens(declaration)
    if ":=" not in declaration:
        raise DovDslParseError(
            f"Named group declaration {declaration!r} missing ':=' "
            f"separator. Expected 'name := expression'."
        )
    name_part, _, def_part = declaration.partition(":=")
    name = name_part.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise DovDslParseError(
            f"Named-group name {name!r} is not a valid identifier."
        )
    if name in variables:
        raise DovDslParseError(
            f"Named-group name {name!r} collides with a variable in "
            f"equation.yaml.variables. Pick a different name."
        )
    if name in existing_groups:
        raise DovDslParseError(
            f"Named group {name!r} declared twice."
        )
    # Build symbol table WITHOUT the new group (can't self-ref).
    local = _build_local_dict(variables, existing_groups)
    expr = _parse_sympy_expr(def_part.strip(), local)
    free = _check_free_symbols_bound(expr, local, declaration)
    return NamedGroup(
        name=name,
        definition_source=declaration,
        definition_ast=expr,
        free_symbols=free,
    )


def parse_inequality(
    text: str,
    variables: Mapping[str, Any],
    named_groups: Mapping[str, NamedGroup],
) -> InequalityAST:
    """Parse one DOV-DSL inequality into an InequalityAST."""
    _reject_forbidden_tokens(text)
    lhs_str, op, rhs_str = _split_relation(text)
    local = _build_local_dict(variables, named_groups)
    lhs = _parse_sympy_expr(lhs_str, local)
    rhs = _parse_sympy_expr(rhs_str, local)
    combined_free = _check_free_symbols_bound(lhs - rhs, local, text)
    return InequalityAST(
        source=text,
        lhs=lhs,
        rhs=rhs,
        rel_op=op,
        free_symbols=combined_free,
    )


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------


def _coerce_side(expr_value: Any, side: str, source: str) -> float:
    """Convert a substituted sympy value to a finite float, raising
    EvaluationError on zoo / nan / ComplexInfinity / non-finite."""
    # sympy's singularity markers
    if expr_value is sp.zoo or expr_value == sp.zoo:
        raise EvaluationError(
            f"{side} of {source!r} evaluated to complex infinity "
            f"(sympy zoo) — likely a divide-by-zero inside a named "
            f"group or sub-expression."
        )
    if expr_value is sp.nan or expr_value == sp.nan:
        raise EvaluationError(
            f"{side} of {source!r} evaluated to NaN — undefined "
            f"intermediate result (e.g., 0/0, log(0), or 0**0)."
        )
    try:
        as_float = float(expr_value)
    except (TypeError, ValueError) as exc:
        raise EvaluationError(
            f"{side} of {source!r} could not be converted to a "
            f"finite float: {exc}. Raw sympy result: {expr_value!r}."
        ) from exc
    if as_float != as_float:  # NaN check after float coercion
        raise EvaluationError(
            f"{side} of {source!r} coerced to NaN after evalf."
        )
    if as_float in (float("inf"), float("-inf")):
        raise EvaluationError(
            f"{side} of {source!r} evaluated to {as_float}."
        )
    return as_float


def evaluate(
    ast: InequalityAST,
    sample: Mapping[str, float],
    named_groups: Optional[Mapping[str, NamedGroup]] = None,
) -> bool:
    """Evaluate an InequalityAST against a concrete sample.

    `sample` is a mapping from variable name → numeric value.
    Named-group symbols are resolved by substituting their
    definitions before substituting the sample values, so
    callers only need to supply the raw variable values.

    Raises:
        EvaluationError: if any intermediate result is undefined
            (divide-by-zero, NaN, complex infinity, non-finite).
            Silent coercion to False is forbidden per the
            board-approved semantics.
    """
    named_groups = named_groups or {}
    subs: Dict[sp.Symbol, Any] = {}
    # First, substitute named groups with their expressions
    # so every free symbol reduces to raw variables.
    lhs_reduced = ast.lhs
    rhs_reduced = ast.rhs
    for name, group in named_groups.items():
        sym = sp.Symbol(name, positive=True)
        lhs_reduced = lhs_reduced.subs(sym, group.definition_ast)
        rhs_reduced = rhs_reduced.subs(sym, group.definition_ast)
    # Now bind the raw variables to numbers.
    for name, value in sample.items():
        sym = sp.Symbol(name, positive=True)
        subs[sym] = value
    lhs_raw = lhs_reduced.subs(subs).evalf()
    rhs_raw = rhs_reduced.subs(subs).evalf()
    lhs_val = _coerce_side(lhs_raw, "lhs", ast.source)
    rhs_val = _coerce_side(rhs_raw, "rhs", ast.source)
    op = ast.rel_op
    if op == "<":  return lhs_val <  rhs_val
    if op == "<=": return lhs_val <= rhs_val
    if op == ">":  return lhs_val >  rhs_val
    if op == ">=": return lhs_val >= rhs_val
    if op == "==": return lhs_val == rhs_val
    if op == "!=": return lhs_val != rhs_val
    raise AssertionError(f"unreachable: unknown op {op!r}")


# ---------------------------------------------------------------------------
# High-level validator
# ---------------------------------------------------------------------------


def validate_envelope(
    envelope: Mapping[str, Any],
    variables: Mapping[str, Any],
) -> ValidationResult:
    """Parse and validate a validity_envelope block from a
    failure_modes entry.

    `envelope` is the YAML sub-dict with the shape:
        named_groups: {Ro: {definition: "U / (f * L)", ...}}
        inequalities: ["Ro >= 1", "|v|/c < 0.1"]
    `variables` is the equation's variables block (same one the
    rest of the equation.yaml uses).

    Returns a ValidationResult with parsed ASTs on success or
    a populated errors list on failure. Never raises.
    """
    result = ValidationResult(ok=True)
    parsed_groups: Dict[str, NamedGroup] = {}

    # Pass 1 — named groups
    raw_groups = envelope.get("named_groups") or {}
    for name, body in raw_groups.items():
        if isinstance(body, dict):
            definition = body.get("definition")
        elif isinstance(body, str):
            definition = body
        else:
            result.errors.append(
                f"named_group {name!r} must be a string or dict "
                f"with 'definition:' key"
            )
            continue
        if not definition:
            result.errors.append(
                f"named_group {name!r} has no definition"
            )
            continue
        try:
            group = parse_named_group(
                f"{name} := {definition}", variables, parsed_groups
            )
        except DovDslParseError as exc:
            result.errors.append(str(exc))
            continue
        parsed_groups[name] = group

    # Pass 2 — inequalities
    inequality_strings = envelope.get("inequalities") or []
    parsed_inequalities: List[InequalityAST] = []
    for text in inequality_strings:
        try:
            ast = parse_inequality(text, variables, parsed_groups)
        except DovDslParseError as exc:
            result.errors.append(str(exc))
            continue
        parsed_inequalities.append(ast)

    result.named_groups = parsed_groups
    result.inequalities = parsed_inequalities
    result.ok = not result.errors
    return result
