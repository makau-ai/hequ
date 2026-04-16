"""Coupling hypothesis types + transfer function library.

Phase 4 deliverable for Medium milestone 2 (see
`labs_v2/DESIGN-COUPLING-SIEVE.md` §6, §7, §11). A coupling is a
variable identification `v_A = T(v_B)` between a variable `v_A`
in equation A and `v_B` in equation B, under a transfer function
`T` drawn from an explicit, small library. Couplings enter the
ledger under one of three tiers:

- **Tier 1 — Equivalence**: identical tier1 descriptor key,
  transfer function = `identity`. The strongest possible claim:
  "these two variables are the same thing in both equations."

- **Tier 2 — Similarity**: compatible-but-not-identical semantic
  descriptors (sibling QUDT properties, compatible contexts) with
  a non-trivial transfer function from the library below. These
  are the interesting couplings: Soret/Dufour, Wick-rotation
  bridges, power-law allometry.

- **Tier 3 — Conjectural**: dimensionally compatible but
  semantically weak matches. Always requires AI review board
  approval; never auto-promoted.

The transfer function library is deliberately tiny (six entries)
so every function can be unit-tested against a known analytical
fit. Growing the library is a design-doc decision, not an
implementation decision.

Nothing in this module runs the sieve — that's Phase 5
(`layer5_coupling_sieve.py`). This module provides the types and
library the sieve composes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy as sp

from .descriptor import Descriptor


# ---------------------------------------------------------------------------
# Coupling tier enum
# ---------------------------------------------------------------------------


class CouplingTier(Enum):
    """Three tiers of coupling strength.

    The tier is an intrinsic property of the proposed coupling
    (descriptor key + transfer function + physical filter
    outcome), not of downstream ledger status. A tier-3 coupling
    may still end up in the ledger — it will just carry a
    `REVIEW_REQUIRED` flag that the AI review board must clear.
    """
    TIER1_EQUIVALENCE = "tier1_equivalence"
    TIER2_SIMILARITY = "tier2_similarity"
    TIER3_CONJECTURAL = "tier3_conjectural"


# ---------------------------------------------------------------------------
# Transfer function
# ---------------------------------------------------------------------------


@dataclass
class TransferFunction:
    """A named symbolic relation y = f(x; parameters).

    Each library entry owns three things:

    - `template` — a sympy expression in the free symbols `x` and
      the parameter list. This is the canonical form of the
      relation; the sieve's `try_fit` method tries to solve this
      expression against a specific (v_a_expr, v_b_expr) pair.

    - `parameters` — a tuple of sympy symbols that are free in
      the template and must be solved for during fitting. For
      `identity` this is empty; for `power_law` it is (k, n).

    - `dimension_change` — an optional callable that, given the
      pint dimensionality of x, returns the pint dimensionality
      of y. `None` means "y has the same dimensions as x" (this
      is the norm for identity, scale, first_order_lag,
      exponential_decay). Power_law can change dimensions only
      if n is dimensionless and integer — we don't model that
      yet; the current `power_law` assumes dimensionless x and y.

    Each entry also ships with at least one **sanity unit test**
    in the corresponding test module: we construct a known pair
    (v_a, v_b) the template should fit, call `try_fit`, and
    assert the returned parameters match by exact symbolic
    equality. This protects against silent library bit-rot.
    """
    name: str
    template: sp.Expr
    x_symbol: sp.Symbol
    y_symbol: sp.Symbol
    parameters: Tuple[sp.Symbol, ...]
    description: str
    dimension_change: Optional[Callable[[Any], Any]] = None

    def try_fit(
        self,
        v_a_expr: sp.Expr,
        v_b_expr: sp.Expr,
    ) -> Optional[Dict[str, sp.Expr]]:
        """Attempt to fit this transfer function to the relation
        `v_a_expr = T(v_b_expr)`. Returns a dict of
        {parameter_name: sympy_value} on success, or None if the
        template cannot be solved for this pair.

        The sieve calls this during tier-2 matching. The method is
        symbolic, not numeric — no parameter fitting against data.

        Algorithm:
        1. Substitute `y_symbol → v_a_expr`, `x_symbol → v_b_expr`
           with parameters replaced by `sp.Wild` pattern atoms.
        2. Use `expr.match` on `v_a_expr` against the right-hand
           side `T(v_b_expr; wild_params)`. Pattern matching
           (not `solve`) is the right tool here because we are
           closing symbolic parameters against a target
           expression's exact shape, not numerically fitting
           against data. `solve` fails on multi-unknown cases
           like `y = k*x^n` (underdetermined as one equation);
           `match` handles them natively.
        3. Return the matched substitution as a plain dict.
        """
        if not self.parameters:
            # Parameter-free template: v_a_expr must equal the
            # template evaluated at v_b_expr.
            rhs = sp.solve(self.template, self.y_symbol)
            if not rhs:
                return None
            rhs_at_b = rhs[0].subs(self.x_symbol, v_b_expr)
            if sp.simplify(v_a_expr - rhs_at_b) == 0:
                return {}
            return None
        # Build a Wild-parameterised right-hand side. We isolate
        # the template's right-hand side by solving `template = 0`
        # for y_symbol (every library entry is linear in y).
        try:
            rhs_list = sp.solve(self.template, self.y_symbol)
        except (NotImplementedError, TypeError):
            return None
        if not rhs_list:
            return None
        rhs = rhs_list[0]
        wild_map = {p: sp.Wild(f"W_{p.name}") for p in self.parameters}
        rhs_wild = rhs.subs(wild_map).subs(self.x_symbol, v_b_expr)
        match = v_a_expr.match(rhs_wild)
        if match is None:
            return None
        result: Dict[str, sp.Expr] = {}
        for p, w in wild_map.items():
            if w not in match:
                return None
            result[str(p)] = match[w]
        return result


# ---------------------------------------------------------------------------
# Transfer function library (v1 — six entries)
# ---------------------------------------------------------------------------

_X = sp.Symbol("x_tf")
_Y = sp.Symbol("y_tf")
_K = sp.Symbol("k_tf")
_N = sp.Symbol("n_tf")
_TAU = sp.Symbol("tau_tf")
_LAM = sp.Symbol("lambda_tf")
_S_LAP = sp.Symbol("s_tf")  # Laplace frequency
_K_SAT = sp.Symbol("K_sat_tf")
_R_LOG = sp.Symbol("r_log_tf")
_X0 = sp.Symbol("x0_tf")


TRANSFER_FUNCTION_LIBRARY: Dict[str, TransferFunction] = {
    "identity": TransferFunction(
        name="identity",
        template=_Y - _X,
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(),
        description="y = x. The tier-1 transfer function; used whenever "
                    "two variables have identical tier1 descriptor keys.",
    ),
    "scale": TransferFunction(
        name="scale",
        template=_Y - _K * _X,
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(_K,),
        description="y = k*x. A linear rescaling. Used when two "
                    "variables share a dimension and the coupling "
                    "is a unit/magnitude change.",
    ),
    "first_order_lag": TransferFunction(
        name="first_order_lag",
        # y * (1 + tau*s) = x, equivalently x - y - tau*s*y = 0
        template=_X - _Y - _TAU * _S_LAP * _Y,
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(_TAU,),
        description="y = x / (1 + tau*s) in the Laplace domain. "
                    "Flow-from-effort couplings: RC circuit, Newton "
                    "cooling, viscous damping. Captures the linear "
                    "single-pole lag structure shared across domains.",
    ),
    "exponential_decay": TransferFunction(
        name="exponential_decay",
        # y = x * exp(-lambda * t) where we treat the decay profile
        # itself as a symbolic relation between y and x at a given t.
        template=_Y - _X * sp.exp(-_LAM * sp.Symbol("t_tf")),
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(_LAM,),
        description="y = x * exp(-lambda*t). Matches first-order "
                    "decay dynamics across domains: Arrhenius, Beer-"
                    "Lambert attenuation, radioactive decay, RC "
                    "discharge.",
    ),
    "power_law": TransferFunction(
        name="power_law",
        template=_Y - _K * _X**_N,
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(_K, _N),
        description="y = k * x^n. Allometric / scaling couplings: "
                    "Kleiber's law, stress-strain exponential "
                    "hardening, Reynolds-number scaling.",
    ),
    "logistic": TransferFunction(
        name="logistic",
        template=_Y - _K_SAT / (1 + sp.exp(-_R_LOG * (_X - _X0))),
        x_symbol=_X,
        y_symbol=_Y,
        parameters=(_K_SAT, _R_LOG, _X0),
        description="y = K / (1 + exp(-r*(x-x0))). Saturation "
                    "couplings: Michaelis-Menten, sigmoid utility "
                    "functions, Hill kinetics.",
    ),
}


def get_transfer_function(name: str) -> TransferFunction:
    """Look up a transfer function by name. Raises KeyError if
    unknown — we want authoring mistakes to be loud.
    """
    if name not in TRANSFER_FUNCTION_LIBRARY:
        raise KeyError(
            f"unknown transfer function {name!r}. Known: "
            f"{sorted(TRANSFER_FUNCTION_LIBRARY)}"
        )
    return TRANSFER_FUNCTION_LIBRARY[name]


# ---------------------------------------------------------------------------
# Coupling hypothesis
# ---------------------------------------------------------------------------


@dataclass
class CouplingHypothesis:
    """A proposed coupling between two equations, at a specific tier.

    Produced by `layer5_coupling_sieve.py` and consumed by the
    physical constraint filter (Phase 6), the emergent analysis
    (Phase 7), and the ledger writer (Phase 8).

    Fields:
    - `eq_a_id`, `eq_b_id` — the two equation IDs being coupled
    - `var_a`, `var_b` — the specific variables being identified
    - `descriptor_a`, `descriptor_b` — their descriptors (copied
      by value so the ledger entry is self-contained)
    - `transfer_function` — name of the T in the library, e.g.
      "identity", "first_order_lag"
    - `transfer_params` — dict of solved parameter values; empty
      for identity, populated for scale/power_law/etc.
    - `tier` — the CouplingTier the sieve assigns
    - `reason` — a short human-readable explanation of why this
      coupling matched at this tier (for the ledger and for the
      AI review board prompt)
    - `physical_constraint_result` — set by the Phase 6 filter
      AFTER the sieve constructs the hypothesis; None until then
    - `emergent_properties` — set by Phase 7; None until then
    """
    eq_a_id: str
    eq_b_id: str
    var_a: str
    var_b: str
    descriptor_a: Descriptor
    descriptor_b: Descriptor
    transfer_function: str
    transfer_params: Dict[str, Any]
    tier: CouplingTier
    reason: str
    physical_constraint_result: Optional[Dict[str, Any]] = None
    emergent_properties: Optional[Dict[str, Any]] = None

    def as_ledger_substitution(self) -> Dict[str, Any]:
        """Return the substitution dict the ledger v4 schema expects
        for `Hypothesis.substitution` (see DESIGN-COUPLING-SIEVE.md
        §11).
        """
        return {
            "v_a": {"equation": self.eq_a_id, "variable": self.var_a},
            "v_b": {"equation": self.eq_b_id, "variable": self.var_b},
            "transfer_function": self.transfer_function,
            "transfer_params": {
                k: str(v) for k, v in self.transfer_params.items()
            },
            "lattice_distance": 0 if self.tier == CouplingTier.TIER1_EQUIVALENCE else None,
        }

    def as_ledger_evidence(self) -> Dict[str, Any]:
        """Return the evidence dict the ledger v4 schema expects
        for `Hypothesis.evidence`. The physical-constraint and
        emergent-property fields default to explicit `null` when
        not yet computed, so downstream readers can tell the
        difference between "not computed" and "computed but empty".
        """
        return {
            "descriptor_match": {
                "a": self.descriptor_a.as_dict(),
                "b": self.descriptor_b.as_dict(),
                "tier": self.tier.value,
            },
            "reason": self.reason,
            "physical_constraint_check": self.physical_constraint_result,
            "emergent_properties": self.emergent_properties,
        }
