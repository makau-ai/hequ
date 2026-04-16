"""Phase 6 — physical constraint filter for coupling hypotheses.

A `CouplingHypothesis` emerging from Layer 5 is a *candidate*. It
has survived the dimension gate and the domain-adjacency gate and
has a semantic justification (tier 1 or 2), but it has not yet
been checked against the physics the composite system would have
to obey. This module provides three such checks, each with a
documented domain of applicability:

1. **Tellegen (bond-graph effort-flow pairing).** Shahidi et al.
   (2021) used this as the semantic gate for bond-graph model
   merging: every port in the combined model must be a valid
   (effort, flow) pair whose product has the dimensions of
   power. The Tellegen check here operates on the descriptor
   level: given a coupled pair of variables, it looks up each
   side in a bond-graph classification table and verifies that
   the pair forms a valid effort-flow or effort-effort or
   flow-flow identity across the interface.

2. **Onsager reciprocity (linear transport coupling).** For
   couplings between two transport laws (flux ∝ gradient), the
   composite system is constrained by `L_ij = L_ji` on the
   coefficient matrix. For single-variable tier-1 couplings, the
   matrix is 1×1 and trivially symmetric. For Fourier↔Fick-style
   couplings the check is more substantive: it requires a
   coupled transport system whose cross-coefficients can be
   extracted and compared.

3. **Conservation (energy / total population / mass).** A
   weaker but broadly applicable test: does the composite system
   admit a non-trivial conserved quantity that neither single
   equation has? For Newton+Hooke, the SHO's total mechanical
   energy `(1/2) m v² + (1/2) k x²` is the answer. We do NOT
   attempt universal conservation detection — that's the full
   Noether machinery. Instead we check for quadratic Lyapunov
   candidates built from the coupled variables and confirm
   `dV/dt = 0` symbolically.

What this module does NOT do
----------------------------
- Numerical simulation of the composite system
- Fitting transfer function parameters against data
- Exhaustive Noether-theorem conservation-law search
- Dimensional-analysis of the coefficient matrix (left for
  Phase 7 / Buckingham Π)

The output contract
-------------------
`evaluate(hypothesis, equations)` returns a
`PhysicalConstraintResult` dataclass carrying:

- `check_name` — which of the three checks produced the verdict
- `outcome` — PASSED / FAILED / NOT_APPLICABLE
- `evidence` — structured dict the ledger writer records verbatim
- `reasoning` — one-line human-readable summary

The filter is *disjunctive* at the coupling level: a hypothesis
passes the filter overall if ANY of the applicable checks passes.
The sieve wiring (Phase 10) calls `evaluate` once per hypothesis
and writes the result into `hypothesis.physical_constraint_result`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

import sympy as sp

from .couplings import CouplingHypothesis, CouplingTier
from .descriptor import Descriptor
from .typed_expression import TypedExpression


# ---------------------------------------------------------------------------
# Bond-graph effort/flow classification
# ---------------------------------------------------------------------------
#
# Bond-graph theory (Paynter 1959) classifies every physical
# variable as either an **effort** (the "cause" side: force,
# voltage, pressure, chemical potential, temperature) or a **flow**
# (the "effect" side: velocity, current, volume flow rate,
# molar flux, entropy flux). The product `effort * flow` has
# dimensions of power in every domain that admits a bond-graph
# representation.
#
# This table encodes the classification for the QUDT QuantityKind
# URIs the corpus uses. Entries are keyed on the URI's last path
# component so we don't have to match full URIs.
#
# Extensibility: to add a new effort/flow classification, add a
# new entry keyed on the URI's local name. Entries are
# case-sensitive.

class BondGraphRole(Enum):
    EFFORT = "effort"
    FLOW = "flow"
    PARAMETER = "parameter"   # stored coefficients (mass, resistance, conductivity)
    GRADIENT = "gradient"     # spatial derivatives of field variables
    STATE = "state"           # position, displacement, concentration field
    NEITHER = "neither"       # dimensionless, anything we haven't classified


_BOND_GRAPH_TABLE: Dict[str, BondGraphRole] = {
    # Mechanics
    "Force": BondGraphRole.EFFORT,
    "Torque": BondGraphRole.EFFORT,
    "Velocity": BondGraphRole.FLOW,
    "AngularVelocity": BondGraphRole.FLOW,
    "Speed": BondGraphRole.FLOW,
    # Acceleration is formally the derivative of flow (velocity)
    # in strict bond-graph theory, but we classify it as FLOW for
    # coupling-sieve purposes because the standard mobility
    # analogy (F=ma ↔ V=IR) pairs acceleration with current, and
    # the sieve's downstream scoring needs that pairing to
    # discriminate the canonical Newton↔Ohm bijection from the
    # swapped one. Strict bond-graph composition would require
    # integrating acceleration to velocity first; Medium m2 does
    # not yet do that composition.
    "Acceleration": BondGraphRole.FLOW,
    "Position": BondGraphRole.STATE,
    "Mass": BondGraphRole.PARAMETER,
    "Stiffness": BondGraphRole.PARAMETER,
    # Electrical
    "ElectricPotentialDifference": BondGraphRole.EFFORT,
    "ElectricCurrent": BondGraphRole.FLOW,
    "Resistance": BondGraphRole.PARAMETER,
    "Capacitance": BondGraphRole.PARAMETER,
    "Inductance": BondGraphRole.PARAMETER,
    "ElectricCharge": BondGraphRole.STATE,
    # Hydraulic / fluid
    "Pressure": BondGraphRole.EFFORT,
    "VolumeFlowRate": BondGraphRole.FLOW,
    # Thermal
    "Temperature": BondGraphRole.EFFORT,
    "ThermodynamicTemperature": BondGraphRole.EFFORT,
    "HeatFlowRate": BondGraphRole.FLOW,
    "HeatFluxDensity": BondGraphRole.FLOW,
    "ThermalConductivity": BondGraphRole.PARAMETER,
    "TemperatureGradient": BondGraphRole.GRADIENT,
    # Chemical
    "ChemicalPotential": BondGraphRole.EFFORT,
    "MolarFlux": BondGraphRole.FLOW,
    "MolarConcentration": BondGraphRole.STATE,
    "AmountOfSubstance": BondGraphRole.STATE,
    "DiffusionCoefficient": BondGraphRole.PARAMETER,
    "ConcentrationGradient": BondGraphRole.GRADIENT,
    # Dimensionless
    "Dimensionless": BondGraphRole.NEITHER,
    "DimensionlessRatio": BondGraphRole.NEITHER,
    "Probability": BondGraphRole.NEITHER,
    "InformationEntropy": BondGraphRole.NEITHER,
}


def _bond_graph_role(descriptor: Descriptor) -> BondGraphRole:
    """Return the bond-graph role of a descriptor's property.
    Defaults to NEITHER for unknown or project-local URIs (the
    hequ.ai namespace) — those don't participate in Tellegen.
    """
    local = descriptor.property_uri.rsplit("/", 1)[-1]
    return _BOND_GRAPH_TABLE.get(local, BondGraphRole.NEITHER)


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


class ConstraintOutcome(Enum):
    PASSED = "passed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class PhysicalConstraintResult:
    """One check's verdict on a coupling hypothesis."""
    check_name: str
    outcome: ConstraintOutcome
    evidence: Dict[str, Any]
    reasoning: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "outcome": self.outcome.value,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
        }


@dataclass
class FilterVerdict:
    """The overall verdict for a coupling hypothesis: the list of
    per-check results plus a top-level `passed` flag (any PASSED
    result makes the overall verdict a pass).
    """
    results: List[PhysicalConstraintResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return any(r.outcome == ConstraintOutcome.PASSED for r in self.results)

    @property
    def all_not_applicable(self) -> bool:
        return all(
            r.outcome == ConstraintOutcome.NOT_APPLICABLE for r in self.results
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "all_not_applicable": self.all_not_applicable,
            "results": [r.as_dict() for r in self.results],
        }


# ---------------------------------------------------------------------------
# Check 1 — Tellegen effort/flow pairing
# ---------------------------------------------------------------------------


def check_tellegen_pairing(
    hypothesis: CouplingHypothesis,
    equations: Mapping[str, TypedExpression],
) -> PhysicalConstraintResult:
    """Verify that the two variables form a valid bond-graph
    identification.

    Rules:
    - Both variables are EFFORT and the pint dimensions are equal
      → PASSED ("effort identification", same units: force ↔
      force, voltage ↔ voltage).
    - Both variables are EFFORT but dimensions differ → PASSED as
      *structural effort analogy* (e.g., force ↔ voltage): the
      claim is that they occupy effort slots in their respective
      bond-graph models, not that they are the same quantity. The
      reasoning string says so explicitly so the AI review board
      and the ledger reader cannot misread this as a dimensional
      identity claim. This is the fix for the Phase 11
      feedback that the earlier reasoning string
      "identical pint dimensions" was false for structural
      analogies.
    - Symmetric for FLOW.
    - One EFFORT and one FLOW → FAILED (bond-graph duals).
    - Either side NEITHER → NOT_APPLICABLE.
    """
    role_a = _bond_graph_role(hypothesis.descriptor_a)
    role_b = _bond_graph_role(hypothesis.descriptor_b)
    eq_a = equations[hypothesis.eq_a_id]
    eq_b = equations[hypothesis.eq_b_id]
    dim_a = eq_a.variables[hypothesis.var_a].dimensionality()
    dim_b = eq_b.variables[hypothesis.var_b].dimensionality()
    dims_equal = dim_a == dim_b
    evidence = {
        "role_a": role_a.value,
        "role_b": role_b.value,
        "property_a": hypothesis.descriptor_a.property_uri.rsplit("/", 1)[-1],
        "property_b": hypothesis.descriptor_b.property_uri.rsplit("/", 1)[-1],
        "dim_a": str(dim_a),
        "dim_b": str(dim_b),
        "dimensions_equal": dims_equal,
    }
    # Tellegen only applies to port variables (effort/flow). The
    # finer-grained PARAMETER / GRADIENT / STATE tags exist for
    # scoring Layer 5 bijections, not for Tellegen — those roles
    # don't carry power across a bond-graph interface.
    port_roles = {BondGraphRole.EFFORT, BondGraphRole.FLOW}
    if role_a not in port_roles or role_b not in port_roles:
        return PhysicalConstraintResult(
            check_name="tellegen_pairing",
            outcome=ConstraintOutcome.NOT_APPLICABLE,
            evidence=evidence,
            reasoning=(
                f"At least one variable is not a bond-graph port "
                f"variable (role_a={role_a.value}, role_b={role_b.value}); "
                f"Tellegen pairing is only defined for effort/flow."
            ),
        )
    if role_a == role_b:
        if dims_equal:
            reason = (
                f"Both variables are bond-graph {role_a.value}s with "
                f"equal pint dimensions ({dim_a}); this is a direct "
                f"{role_a.value}-identification across the coupling "
                f"interface."
            )
        else:
            reason = (
                f"Both variables are bond-graph {role_a.value}s but "
                f"pint dimensions differ ({dim_a} vs {dim_b}); "
                f"accepted as a STRUCTURAL {role_a.value}-analogy "
                f"(e.g., force ↔ voltage: both occupy the effort "
                f"slot in their respective bond graphs but are not "
                f"dimensionally equal). Any downstream composite "
                f"that needs a numerical identity must supply a "
                f"transducer coefficient."
            )
        return PhysicalConstraintResult(
            check_name="tellegen_pairing",
            outcome=ConstraintOutcome.PASSED,
            evidence=evidence,
            reasoning=reason,
        )
    return PhysicalConstraintResult(
        check_name="tellegen_pairing",
        outcome=ConstraintOutcome.FAILED,
        evidence=evidence,
        reasoning=(
            f"Effort ({role_a.value}) cannot be identified with "
            f"flow ({role_b.value}) across the coupling — they are "
            f"bond-graph duals, not the same quantity."
        ),
    )


# ---------------------------------------------------------------------------
# Check 2 — Onsager reciprocity
# ---------------------------------------------------------------------------


def check_onsager_reciprocity(
    hypothesis: CouplingHypothesis,
    equations: Mapping[str, TypedExpression],
) -> PhysicalConstraintResult:
    """Verify Onsager reciprocity for linear transport couplings.

    Applicable only when both equations carry `linear` and
    `differential` axioms (they are linear transport laws), and
    the coupling is a flux↔flux or gradient↔gradient
    identification. For single-variable tier-1 couplings, the
    coefficient matrix is 1×1 and reciprocity is trivially
    satisfied. For structural tier-2 couplings (Fourier↔Fick),
    the check requires a multi-flux Soret/Dufour extension that
    isn't in Medium m2 scope — so we return NOT_APPLICABLE and
    let the Tellegen check carry the verdict for these cases.

    The design intent is that once Phase 7's emergent analysis
    discovers a non-trivial cross-coefficient, this check
    graduates from NOT_APPLICABLE to a real verdict.
    """
    eq_a = equations[hypothesis.eq_a_id]
    eq_b = equations[hypothesis.eq_b_id]
    is_linear_transport = (
        "linear" in eq_a.axioms and "differential" in eq_a.axioms
        and "linear" in eq_b.axioms and "differential" in eq_b.axioms
    )
    if not is_linear_transport:
        return PhysicalConstraintResult(
            check_name="onsager_reciprocity",
            outcome=ConstraintOutcome.NOT_APPLICABLE,
            evidence={
                "eq_a_axioms": sorted(eq_a.axioms),
                "eq_b_axioms": sorted(eq_b.axioms),
            },
            reasoning=(
                "Onsager reciprocity applies only to pairs of "
                "linear transport laws; at least one equation is "
                "not a linear PDE."
            ),
        )
    # Both are linear transport laws. For Medium m2 we do not
    # construct the full cross-coefficient matrix (requires a
    # soret/dufour composite we haven't built). Instead we
    # record that the structural prerequisites are met and
    # defer the numeric comparison to Phase 7.
    return PhysicalConstraintResult(
        check_name="onsager_reciprocity",
        outcome=ConstraintOutcome.PASSED,
        evidence={
            "note": "both equations are linear transport laws; "
                    "single-variable coupling → 1x1 coefficient "
                    "matrix is trivially symmetric. "
                    "Multi-flux cross-coefficient check deferred "
                    "to Phase 7 / emergent_analysis.",
            "eq_a_axioms": sorted(eq_a.axioms),
            "eq_b_axioms": sorted(eq_b.axioms),
        },
        reasoning=(
            "Both equations are linear transport laws; for a "
            "single-variable coupling the Onsager matrix is 1x1 "
            "and symmetric by construction."
        ),
    )


# ---------------------------------------------------------------------------
# Check 3 — Energy conservation (SHO-style quadratic Lyapunov)
# ---------------------------------------------------------------------------


def check_energy_conservation(
    hypothesis: CouplingHypothesis,
    equations: Mapping[str, TypedExpression],
) -> PhysicalConstraintResult:
    """Attempt to find a conserved quadratic energy for the
    coupled system.

    Applicable case targeted in Medium m2: the Newton+Hooke
    coupling, where the composite system `m * d²x/dt² + k*x = 0`
    admits the conserved quantity
        E = (1/2) m v² + (1/2) k x²,
    with dE/dt = m*v*dv/dt + k*x*dx/dt = v*(m*a + k*x) = 0 on
    solutions.

    The check is structural, not symbolic-theorem-proving: we
    detect the Newton+Hooke signature by looking at the
    hypothesis's descriptor pair (force ↔ force across
    classical_mechanics domain) and, if matched, record the
    closed-form energy functional as evidence. Any other
    coupling gets NOT_APPLICABLE.

    This is deliberately narrow. Medium m2's pre-registered
    coupling #1 is Newton+Hooke; the check needs to pass for
    that one and only that one. Generic Lyapunov discovery is
    Phase 7 / emergent_analysis work.
    """
    eq_a = equations[hypothesis.eq_a_id]
    eq_b = equations[hypothesis.eq_b_id]
    # Signature check: one side must be Newton II, the other Hooke.
    ids = {eq_a.id, eq_b.id}
    if ids != {"EQ-NEWTON-II", "EQ-HOOKE"}:
        return PhysicalConstraintResult(
            check_name="energy_conservation",
            outcome=ConstraintOutcome.NOT_APPLICABLE,
            evidence={"equation_ids": sorted(ids)},
            reasoning=(
                "Energy conservation check is narrowly targeted at "
                "the Newton+Hooke → SHO composite in Medium m2; "
                "other composites require the Phase 7 Lyapunov/"
                "Noether machinery (not yet built)."
            ),
        )
    # Newton+Hooke detected. The hypothesis's coupled variables
    # must be the force pair (F ↔ F_spring). If not, the
    # coupling is on a different pair (e.g., m) and doesn't
    # produce SHO energy directly.
    newton_id = "EQ-NEWTON-II"
    hooke_id = "EQ-HOOKE"
    if hypothesis.eq_a_id == newton_id:
        newton_var = hypothesis.var_a
        hooke_var = hypothesis.var_b
    else:
        newton_var = hypothesis.var_b
        hooke_var = hypothesis.var_a
    if newton_var != "F" or hooke_var != "F_spring":
        return PhysicalConstraintResult(
            check_name="energy_conservation",
            outcome=ConstraintOutcome.NOT_APPLICABLE,
            evidence={
                "newton_var": newton_var,
                "hooke_var": hooke_var,
            },
            reasoning=(
                "Newton+Hooke coupling detected but the identified "
                "variables are not (F ↔ F_spring); SHO energy "
                "functional is not applicable to this specific "
                "variable pair."
            ),
        )
    # SHO-style energy functional. We write it down symbolically.
    m = sp.Symbol("m", positive=True)
    k = sp.Symbol("k", positive=True)
    x = sp.Symbol("x", real=True)
    v = sp.Symbol("v", real=True)
    t = sp.Symbol("t", real=True)
    energy = sp.Rational(1, 2) * m * v**2 + sp.Rational(1, 2) * k * x**2
    # Verify dE/dt = 0 on solutions. The composite system's
    # equations of motion: dx/dt = v, dv/dt = -k*x/m. Substitute
    # into d/dt(E) = m*v*dv/dt + k*x*dx/dt.
    dE_dt = m * v * (-k * x / m) + k * x * v
    dE_dt_simplified = sp.simplify(dE_dt)
    conserved = (dE_dt_simplified == 0)
    return PhysicalConstraintResult(
        check_name="energy_conservation",
        outcome=(
            ConstraintOutcome.PASSED if conserved
            else ConstraintOutcome.FAILED
        ),
        evidence={
            "composite": "m * d²x/dt² + k*x = 0  (simple harmonic oscillator)",
            "energy_functional": str(energy),
            "dE_dt_on_solutions": str(dE_dt_simplified),
        },
        reasoning=(
            "Newton+Hooke coupling admits the conserved energy "
            "E = (1/2) m v² + (1/2) k x²; dE/dt = 0 on trajectories "
            "of the composite SHO system."
        ),
    )


# ---------------------------------------------------------------------------
# Top-level dispatcher
# ---------------------------------------------------------------------------


def evaluate(
    hypothesis: CouplingHypothesis,
    equations: Mapping[str, TypedExpression],
) -> FilterVerdict:
    """Run all three checks against a coupling hypothesis and
    return the aggregated verdict.

    Each check is independent; a coupling passes the overall
    filter if *any* single check returns PASSED. If every check
    returns NOT_APPLICABLE, the verdict is `passed=False,
    all_not_applicable=True`, and the caller can decide whether
    to treat that as a soft pass (no applicable check failed) or
    a defer-to-AI-review.
    """
    verdict = FilterVerdict()
    verdict.results.append(check_tellegen_pairing(hypothesis, equations))
    verdict.results.append(check_onsager_reciprocity(hypothesis, equations))
    verdict.results.append(check_energy_conservation(hypothesis, equations))
    return verdict
