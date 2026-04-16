"""Typed symbolic expressions — the canonical representation layer.

A `TypedExpression` pairs a sympy expression with a dimensional
registry (via pint) that records the physical meaning and SI unit of
every free symbol. This is the Leibnizian "canonical representation"
the design doctrine demands: before any cross-domain comparison, two
equations must be expressible in this common form.

Why not just sympy
------------------
Sympy alone gives us syntactic equality (`a*b == b*a`) but no guard
against lexical collisions: Newton's `r` (a length) and the logistic
equation's `r` (an inverse time) are the same sympy symbol. The
subsumption false positives that broke v1 came from exactly this.
pint adds a dimensional type, so the engine sees `Q_(r, 'meter')` vs
`Q_(r, '1/second')` as incomparable.

Why not just pint
-----------------
pint handles unit arithmetic but does not preserve symbolic
structure. We want to compare `F/m` to `a` symbolically, not
numerically. Sympy gives us that.

The composition: every `TypedExpression` carries a sympy expression
plus a dict {symbol_name → (dimension_string, description)}.
Operations (substitution, normalisation, comparison) check dimensions
before proceeding and reject operations that would mix incompatible
quantities.

YAML on-disk format
-------------------
Each equation's `equation.yaml` looks like::

    id: EQ-NEWTON-II
    name: Newton's Second Law
    domain: classical_mechanics
    canonical_form: F - m*a
    variables:
      F:
        dimension: "[force]"
        unit: "newton"
        meaning: "net force on the body"
      m:
        dimension: "[mass]"
        unit: "kilogram"
        meaning: "inertial mass"
      a:
        dimension: "[acceleration]"
        unit: "meter/second**2"
        meaning: "acceleration of the centre of mass"
    assumptions:
      - "m is strictly positive and constant (not variable-mass)"
      - "frame is inertial"
      - "v << c (classical, non-relativistic)"
    derivation_from:
      - "Newton's three laws (Principia, 1687)"
      - "Equivalent to the Euler-Lagrange equation for L = (1/2)mv^2 - V(x)"
    references:
      - "Goldstein, Classical Mechanics, 3rd ed., Eq. 1-3"

The canonical_form is a **single sympy expression** that equals zero
on the equation's solution manifold. For Newton II, `F - m*a = 0`;
for Fourier's law in 1D, `q + k*diff(T, x) = 0`. This is the
*implicit* form that all four unification sieves operate on.
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sympy as sp


# Lazily-loaded pint registry — importing pint is ~300ms, so we defer
# until the first TypedExpression is constructed.
_PINT_REGISTRY = None


class DimensionalError(TypeError):
    """Raised by `evaluate_with_units` when an input's dimensionality
    is incompatible with the variable's declared dimension, or when a
    raw float is passed in strict mode (the default for user code).
    """
    def __init__(self, eq_id: str, var_name: str, expected, received):
        self.eq_id = eq_id
        self.var_name = var_name
        self.expected = expected
        self.received = received
        super().__init__(
            f"{eq_id}.{var_name}: expected dimensionality {expected}, "
            f"got {received}"
        )


def _pint():
    """Return the shared pint registry built by `framework.dimensions`.

    The registry is built once per process. All custom dimensional
    extensions (currency, information aliases) are documented in
    `dimensions.build_registry` — NOT here. This keeps the policy
    decisions (e.g., information as dimensionless by design) in a
    single auditable location.
    """
    global _PINT_REGISTRY
    if _PINT_REGISTRY is None:
        from .dimensions import build_registry
        _PINT_REGISTRY = build_registry()
    return _PINT_REGISTRY


@dataclass
class Variable:
    """A single typed symbol appearing in a TypedExpression.

    The `dimension` string is a pint dimensionality expression like
    `"[length] ** 2 / [time] ** 3"`. The `unit` string is the SI unit
    used in all worked examples for this equation, like `"newton"` or
    `"mole/liter"`. Both must be consistent; inconsistency is an
    authoring error that fails loading.
    """
    name: str
    dimension: str
    unit: str
    meaning: str
    descriptor: Optional[Descriptor] = None

    def pint_quantity(self, magnitude: float):
        """Return a pint Quantity with the variable's declared unit."""
        return _pint().Quantity(magnitude, self.unit)

    def dimensionality(self):
        """Return the pint dimensionality object for this variable."""
        # pint handles `[force]`, `[length]/[time]**2`, etc.
        return _pint().parse_expression(self.unit).dimensionality


from typing import Set as _SetType

from .descriptor import Descriptor


@dataclass
class TypedExpression:
    """A sympy expression with dimensioned typing on every free symbol.

    The canonical form is an expression that equals zero on the
    solution manifold. Use `lhs_minus_rhs()` for the implicit form or
    `as_equation()` for the familiar `lhs = rhs` presentation.

    PDEs and operator equations
    ---------------------------
    For equations with explicit derivatives, the YAML may declare an
    optional **second representation** `canonical_form_derivatives`
    that uses sympy `Function` and `Derivative` objects rather than
    atomic symbols like `V_t`. The algebraic `canonical_form` stays
    as the workhorse for the Layer 2 structural sieve; the derivative
    form is consumed by the (future) change-of-variables sieve which
    needs the real derivative structure to apply the chain rule.

    Example (Fourier's 1D heat law)::

        canonical_form: "q + k * dT_dx"             # algebraic form
        canonical_form_derivatives:                  # derivative form
            functions:
                T: ["x"]
            expression: "q + k * Derivative(T(x), x)"

    Equations without derivatives leave `canonical_form_derivatives`
    as None and the framework treats the two representations as
    identical.
    """
    id: str
    name: str
    domain: str
    canonical_form: sp.Expr
    variables: Dict[str, Variable]
    assumptions: List[str] = field(default_factory=list)
    derivation_from: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    canonical_form_derivatives: Optional[sp.Expr] = None
    declared_functions: Dict[str, List[str]] = field(default_factory=dict)
    axioms: _SetType[str] = field(default_factory=set)

    # ------------------------------------------------------------
    # Sympy bridge
    # ------------------------------------------------------------

    def free_symbols(self) -> List[str]:
        return sorted(str(s) for s in self.canonical_form.free_symbols)

    def symbol_map(self) -> Dict[str, sp.Symbol]:
        """Return {name: sympy.Symbol} for every declared variable."""
        return {v.name: sp.Symbol(v.name) for v in self.variables.values()}

    def substitute(self, mapping: Dict[str, Any]) -> sp.Expr:
        """Substitute symbol names → values (sympy or numeric).

        Caller is responsible for dimensional consistency. For a
        dimensionally-checked substitution see `evaluate_with_units`.
        """
        subs = {sp.Symbol(k): v for k, v in mapping.items()}
        return self.canonical_form.subs(subs)

    def evaluate_with_units(
        self,
        mapping: Dict[str, Any],
        *,
        strict: bool = True,
    ):
        """Substitute pint Quantities (or raw magnitudes) and evaluate.

        Dimensional contract
        --------------------
        With `strict=True` (the default, and the only mode a lab
        notebook should use): **every input must be a pint Quantity
        with the correct dimensionality**. Raw floats are rejected
        with a `DimensionalError`. This closes the escape hatch the
        architecture auditor flagged: v1's `evaluate_with_units`
        silently accepted `F=5.0` and had no way to distinguish
        "5 newtons" from "5 elephants".

        To pass a raw magnitude, wrap it yourself:
            `eq.evaluate_with_units({"F": 5.0 * ureg.newton, ...})`
        where `ureg = framework.typed_expression._pint()`.

        With `strict=False` (provided for pipeline internals like the
        structural sieve's numerical trials — NOT for user-facing
        notebooks), raw floats are accepted as magnitudes in the
        variable's declared unit.

        Returns the numeric value of the canonical form evaluated at
        the substituted inputs, in the canonical form's natural units
        (dimensionless for implicit-form residuals, or whatever unit
        the expression reduces to).
        """
        pq = _pint()
        unit_map: Dict[str, float] = {}
        for name, val in mapping.items():
            if name not in self.variables:
                raise KeyError(f"{name!r} is not a declared variable of {self.id}")
            var = self.variables[name]
            if hasattr(val, "dimensionality"):
                # pint Quantity → check compatibility strictly.
                if val.dimensionality != var.dimensionality():
                    raise DimensionalError(
                        self.id, name,
                        expected=var.dimensionality(),
                        received=val.dimensionality,
                    )
                unit_map[name] = val.to(var.unit).magnitude
            else:
                if strict:
                    raise DimensionalError(
                        self.id, name,
                        expected=var.dimensionality(),
                        received="<raw float — pass a pint Quantity>",
                    )
                unit_map[name] = float(val)
        result = self.canonical_form.subs(
            {sp.Symbol(k): v for k, v in unit_map.items()}
        )
        return float(result)

    # ------------------------------------------------------------
    # Dimensional signature
    # ------------------------------------------------------------

    def dimensional_signature(self) -> Tuple[Tuple[str, str], ...]:
        """Return a canonical, hashable signature of the variable dimensions.

        Used by the Layer 2 dimensional sieve to bucket equations that
        are dimensionally comparable. Two equations with the same
        signature have the same *set* of dimensioned quantities (up to
        relabeling), which is a necessary condition for dimensional
        analogy.
        """
        return tuple(sorted(
            (v.name, str(v.dimensionality()))
            for v in self.variables.values()
        ))

    def dimension_multiset(self) -> Tuple[str, ...]:
        """A weaker signature: just the multiset of dimensions.

        Stronger than "same dimensions" but ignores variable names. A
        match here with no match on `dimensional_signature` means
        "same dimensioned quantities in different roles" — a classic
        analogy signal (e.g., Fourier vs. Fick: temperature/gradient
        vs. concentration/gradient).
        """
        return tuple(sorted(
            str(v.dimensionality()) for v in self.variables.values()
        ))

    # ------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------

    def lhs_minus_rhs(self) -> sp.Expr:
        return self.canonical_form

    def as_equation(self) -> str:
        """Return a human-readable 'lhs = 0' presentation."""
        return f"{sp.pretty(self.canonical_form)} = 0"


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_equation(yaml_path: Path) -> TypedExpression:
    """Load a TypedExpression from a YAML file."""
    with open(yaml_path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    from .descriptor import parse_descriptor, default_registry

    eq_id = raw.get("id", "<unknown>")
    variables: Dict[str, Variable] = {}
    descriptor_block_present = False
    parsed_descriptors: Dict[str, Descriptor] = {}
    for vname, vdef in raw.get("variables", {}).items():
        descriptor_obj: Optional[Descriptor] = None
        if "descriptor" in vdef:
            descriptor_block_present = True
            descriptor_obj = parse_descriptor(eq_id, vname, vdef["descriptor"])
            parsed_descriptors[vname] = descriptor_obj
        variables[vname] = Variable(
            name=vname,
            dimension=vdef["dimension"],
            unit=vdef["unit"],
            meaning=vdef.get("meaning", ""),
            descriptor=descriptor_obj,
        )

    # If any variable declared a descriptor block, require all
    # variables to declare one — partial descriptors are an
    # authoring error (the coupling sieve would silently skip
    # undeclared variables, and the readiness auditor would call
    # that a regression to v1's "silent fallback" failure mode).
    if descriptor_block_present:
        missing = [
            vname for vname in variables
            if variables[vname].descriptor is None
        ]
        if missing:
            raise ValueError(
                f"{eq_id}: descriptor block declared for some variables "
                f"but not all. Missing: {missing}. Either declare a "
                f"descriptor on every variable or none."
            )
        default_registry().validate_many(eq_id, parsed_descriptors)

    # Parse the canonical form with sympy, providing the declared
    # variables as local symbols so names override sympy's built-ins
    # (I, E, N, S, etc.).
    locals_map = {vname: sp.Symbol(vname) for vname in variables}
    canonical = sp.sympify(raw["canonical_form"], locals=locals_map)

    # Optional derivative-form representation for PDEs. The YAML
    # block is:
    #   canonical_form_derivatives:
    #     functions:
    #       T: ["x"]
    #     expression: "q + k * Derivative(T(x), x)"
    # All declared variables are available as locals; the caller also
    # gets sp.Function and sp.Derivative into the locals namespace.
    canonical_derivs = None
    declared_functions: Dict[str, List[str]] = {}
    if "canonical_form_derivatives" in raw:
        deriv_block = raw["canonical_form_derivatives"]
        declared_functions = dict(deriv_block.get("functions", {}))
        deriv_locals = dict(locals_map)
        # Inject sympy Function objects for each declared function.
        for fname, fargs in declared_functions.items():
            deriv_locals[fname] = sp.Function(fname)
            for arg in fargs:
                deriv_locals.setdefault(arg, sp.Symbol(arg))
        deriv_locals["Derivative"] = sp.Derivative
        deriv_locals["Function"] = sp.Function
        canonical_derivs = sp.sympify(
            deriv_block["expression"], locals=deriv_locals
        )

    # Machine-checkable axioms: validated against the controlled
    # vocabulary and rejected if internally contradictory. The
    # methodology auditor's Principle-3 blocker: these axioms must
    # be consumed by Layer 2/3, not just documented.
    from .axioms import validate_axioms
    axioms_raw = raw.get("axioms", [])
    if not isinstance(axioms_raw, list):
        raise ValueError(
            f"{raw.get('id', 'unknown')}: `axioms` must be a list"
        )
    axiom_set = set(axioms_raw)
    validate_axioms(axiom_set)

    return TypedExpression(
        id=raw["id"],
        name=raw["name"],
        domain=raw["domain"],
        canonical_form=canonical,
        variables=variables,
        assumptions=raw.get("assumptions", []),
        derivation_from=raw.get("derivation_from", []),
        references=raw.get("references", []),
        canonical_form_derivatives=canonical_derivs,
        declared_functions=declared_functions,
        axioms=axiom_set,
    )


def load_all_equations(root: Path) -> Dict[str, TypedExpression]:
    """Walk `root` looking for `equation.yaml` files and load them.

    The root is typically `labs_v2/equations/`. Each equation lives in
    its own subdirectory whose name matches the equation id.
    """
    equations: Dict[str, TypedExpression] = {}
    for yaml_file in sorted(root.rglob("equation.yaml")):
        eq = load_equation(yaml_file)
        equations[eq.id] = eq
    return equations
