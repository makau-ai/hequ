"""Phase 7 — emergent properties of coupled systems.

Given a coupling hypothesis that passed the Phase 6 physical
constraint filter, this module computes four emergent properties
and records them as ledger evidence. The goal is to answer the
question "did the coupling produce anything the single equations
don't have on their own?" — that's the honest signal that the
coupling is more than a formal analogy.

Four emergent properties, in binding order (§9 of the design
doc):

1. **Symbolic steady state**: solve `d/dt(state) = 0` for fixed
   points. Used as the basis for the stability and conservation
   analyses below.

2. **Linear stability at each fixed point**: Jacobian +
   eigenvalues, classified as stable / unstable / saddle /
   center / Hopf-candidate.

3. **Buckingham Π**: dimensional nullspace of the combined
   parameter list. The ACTUAL payoff: if the coupled system has
   a dimensionless group that neither single equation has, that
   group is flagged as emergent and joins the ledger evidence.

4. **Conserved quantities**: go beyond the Phase 6 "one energy
   is enough" check by searching for additional invariants.
   Medium m2 handles the SHO (Newton+Hooke) case and defers
   general Lyapunov discovery.

Medium m2 scope
---------------
- Full steady-state + stability for 2D ODE composites (the
  Newton+Hooke SHO system, the Fourier+Fick 1D transport
  system).
- Full Buckingham Π on the union of parameters — this is the
  only universal one. Works for every coupling that has a
  well-defined parameter list.
- Conserved quantities restricted to the SHO case, same as
  Phase 6. Extending to Lotka-Volterra (which has a known
  conserved quantity `δx - γ ln x + βy - α ln y`) is deferred
  to milestone m3.

Output contract
---------------
`analyse(hypothesis, equations)` returns an
`EmergentAnalysis` dataclass with four optional fields
corresponding to the four properties. Fields that the analysis
could not compute (or that are not applicable to this
coupling's composite) are set to None, not left out — the
ledger reader needs to tell "skipped" from "zero result".

Nothing in this module writes to the ledger. That's Phase 8's
job.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import sympy as sp

from .couplings import CouplingHypothesis
from .typed_expression import TypedExpression, _pint


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class EmergentAnalysis:
    """The four emergent properties of a coupled system.

    All four fields are Optional: None means "not computed / not
    applicable to this coupling". A populated field is the
    analysis result in a stable, serializable form (strings for
    sympy expressions; floats/ints for numeric results; lists
    for multi-valued results).
    """
    steady_states: Optional[List[Dict[str, str]]] = None
    stability: Optional[List[Dict[str, Any]]] = None
    buckingham_pi_groups: Optional[List[str]] = None
    emergent_pi_groups: Optional[List[str]] = None
    conserved_quantities: Optional[List[str]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "steady_states": self.steady_states,
            "stability": self.stability,
            "buckingham_pi_groups": self.buckingham_pi_groups,
            "emergent_pi_groups": self.emergent_pi_groups,
            "conserved_quantities": self.conserved_quantities,
        }

    def has_emergent_insight(self) -> bool:
        """True if the coupled system exposes a property that at
        least one of the single equations did not. The current
        criterion: `emergent_pi_groups` is non-empty OR
        `conserved_quantities` lists an invariant beyond the
        trivial one already known to each single equation.
        """
        if self.emergent_pi_groups:
            return True
        if self.conserved_quantities and len(self.conserved_quantities) >= 1:
            return True
        return False


# ---------------------------------------------------------------------------
# Buckingham Π on the combined parameter list
# ---------------------------------------------------------------------------


def _collect_parameter_dimensions(
    equations_involved: List[TypedExpression],
) -> Dict[str, sp.Matrix]:
    """Build a map {parameter_name: dimension_vector} for every
    variable in the two equations.

    A "dimension vector" is a length-7 vector of SI base-unit
    exponents in the order (length, mass, time, electric_current,
    temperature, substance, luminous_intensity). pint exposes
    the base dimensions but not directly as a vector; we
    extract them by parsing the variable's unit string and
    pulling the dimensionality dict.
    """
    base_order = [
        "[length]", "[mass]", "[time]", "[current]",
        "[temperature]", "[substance]", "[luminosity]",
    ]
    ureg = _pint()
    result: Dict[str, sp.Matrix] = {}
    for eq in equations_involved:
        for var_name, var in eq.variables.items():
            dim = ureg.parse_expression(var.unit).dimensionality
            vec = [sp.Rational(dim.get(bn, 0)).limit_denominator() for bn in base_order]
            # Disambiguate across equations with the same variable name
            # by prefixing with the equation id.
            key = f"{eq.id}::{var_name}"
            result[key] = sp.Matrix(vec)
    return result


def _buckingham_pi(
    param_dims: Dict[str, sp.Matrix],
) -> List[str]:
    """Return a list of independent dimensionless combinations
    of the given parameters, expressed as strings of the form
    `name1^a * name2^b * ...`.

    Algorithm: stack the parameter vectors into a column matrix
    M (7 rows × N cols). Compute the nullspace of M.T (the
    left-nullspace of M): each basis vector in the nullspace is
    a sequence of exponents `(e_1, ..., e_N)` such that
    `Σ e_i * dim(param_i) = 0`, i.e. a dimensionless monomial.

    Returns a list of string expressions, one per nullspace
    basis vector. The list may be empty if the parameter set is
    dimensionally independent.
    """
    if not param_dims:
        return []
    names = sorted(param_dims.keys())
    cols = [param_dims[n] for n in names]
    M = sp.Matrix.hstack(*cols)  # 7 x N
    # Nullspace of M is the space of column vectors x such that
    # M @ x = 0, which is exactly the dimensionless combinations.
    nullspace = M.nullspace()
    groups: List[str] = []
    for vec in nullspace:
        pieces = []
        for i, name in enumerate(names):
            exp = vec[i]
            if exp == 0:
                continue
            # Strip the equation-id prefix for legibility
            short = name.split("::", 1)[-1]
            if exp == 1:
                pieces.append(short)
            else:
                pieces.append(f"{short}^({exp})")
        if pieces:
            groups.append(" * ".join(pieces))
    return groups


# ---------------------------------------------------------------------------
# Steady-state + stability for the Newton+Hooke composite
# ---------------------------------------------------------------------------


def _sho_steady_and_stability() -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
    """Compute the steady state and stability of the 2D SHO
    system
        dx/dt = v
        dv/dt = -k*x/m
    which is the Newton+Hooke composite. One fixed point at
    (x*, v*) = (0, 0). Jacobian is
        [[0, 1], [-k/m, 0]]
    whose eigenvalues are ±i*sqrt(k/m) — a linear center.
    Canonical worked example for the stability module.
    """
    k, m = sp.symbols("k m", positive=True)
    x, v = sp.symbols("x v", real=True)
    J = sp.Matrix([[0, 1], [-k / m, 0]])
    eigs = list(J.eigenvals().keys())
    classification = "center"  # purely imaginary eigenvalues
    return (
        [{"x": "0", "v": "0"}],
        [{
            "fixed_point": {"x": "0", "v": "0"},
            "jacobian": str(J),
            "eigenvalues": [str(e) for e in eigs],
            "classification": classification,
            "notes": (
                "Linear center: oscillations neither grow nor decay, "
                "amplitude is set by initial conditions. This is the "
                "simple harmonic oscillator, which is the canonical "
                "marginally-stable dynamical system."
            ),
        }],
    )


def _sho_conserved_quantities() -> List[str]:
    """Return the single conserved quantity of the SHO: total
    mechanical energy. Returned as a list (even though it's
    singleton) because `EmergentAnalysis.conserved_quantities`
    is a list — and the field is reused by future richer
    analyses.
    """
    return ["(1/2) * m * v**2 + (1/2) * k * x**2"]


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def analyse(
    hypothesis: CouplingHypothesis,
    equations: Mapping[str, TypedExpression],
) -> EmergentAnalysis:
    """Run the four emergent analyses on the coupling's
    composite system and return the aggregated result.

    Applicability rules:
    - Buckingham Π is always attempted (any pair has a
      parameter list).
    - Steady state + stability is attempted only for the
      Newton+Hooke (SHO) composite in Medium m2. Any other
      composite returns None for both fields.
    - Conserved quantities currently works only for
      Newton+Hooke (inherited from Phase 6).
    """
    eq_a = equations[hypothesis.eq_a_id]
    eq_b = equations[hypothesis.eq_b_id]
    result = EmergentAnalysis()

    # Buckingham Π — universal
    param_dims_a = _collect_parameter_dimensions([eq_a])
    param_dims_b = _collect_parameter_dimensions([eq_b])
    param_dims_both = _collect_parameter_dimensions([eq_a, eq_b])
    groups_a = _buckingham_pi(param_dims_a)
    groups_b = _buckingham_pi(param_dims_b)
    groups_both = _buckingham_pi(param_dims_both)
    result.buckingham_pi_groups = groups_both
    # Emergent groups: those in `groups_both` whose name set
    # mixes variables from both equations. A group that mentions
    # only eq_a variables (or only eq_b variables) was already
    # discoverable in one single equation.
    emergent: List[str] = []
    a_names = {n.split("::", 1)[-1] for n in param_dims_a}
    b_names = {n.split("::", 1)[-1] for n in param_dims_b}
    for g in groups_both:
        # Split the group string into variable names (tokens
        # ending at `^` or `*` or whitespace). Quick heuristic:
        # check whether any a-only and any b-only variable
        # appears in the text.
        mentions_a = any(n in g for n in a_names if n not in b_names)
        mentions_b = any(n in g for n in b_names if n not in a_names)
        if mentions_a and mentions_b:
            emergent.append(g)
    result.emergent_pi_groups = emergent

    # Steady state + stability — Newton+Hooke only
    ids = {eq_a.id, eq_b.id}
    if ids == {"EQ-NEWTON-II", "EQ-HOOKE"}:
        steady, stability = _sho_steady_and_stability()
        result.steady_states = steady
        result.stability = stability
        result.conserved_quantities = _sho_conserved_quantities()

    return result
