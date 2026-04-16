"""I-ADOPT compositional descriptors for typed variables.

Phase 1 deliverable for the Medium milestone 2 coupling sieve
(see `labs_v2/DESIGN-COUPLING-SIEVE.md` §5). Every variable in
every equation carries a four-field descriptor:

    {
        object_of_interest: <controlled vocab term>,
        property: <QUDT QuantityKind URI>,
        context: <controlled vocab term>,
        constraint: <optional free-text narrowing>,
    }

Why four fields and not, say, a single tag like "force":

- **CSDMS precedent** — `object + quantity` disambiguates
  temperature-of-air vs temperature-of-soil at the type level, so
  the sieve never accidentally unifies "the temperature of the
  rod" with "the temperature of a thermal reservoir" via the
  string "temperature".
- **I-ADOPT precedent** — four-field compositional descriptors are
  the minimum expressive schema identified by the European Open
  Science Cloud interoperability working group.
- **Context kept out of the name** — assumptions like "steady
  state", "inertial frame", "risk-neutral measure" live in
  `context`, not embedded in longer property names. This keeps
  QUDT's namespace compact and lets the sieve reason about the
  assumption as a separate dimension.

The compositional descriptor is the replacement for the flat
axiom-tag system used in Medium milestone 1. Axioms still exist,
but now operate on the equation level; descriptors operate on the
variable level. Both participate in coupling acceptance in
different phases (axioms gate CoV substitutions, descriptors drive
semantic tier-1/tier-2 matching).

Validation is LOAD-TIME. An equation whose descriptor block
references an unknown `object_of_interest` value, an unresolved
`context` value, or a QUDT URI that isn't in the vendor cache,
fails to load. No silent fallback to "generic" — that was one of
the v1 failure modes the readiness auditor flagged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, Mapping, Optional, Set


# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------
#
# These are the only valid values for the `object_of_interest` and
# `context` fields. Extensions require an explicit code change here
# (and, implicitly, a design-doc update). That's by design: the cost
# of admitting a new vocabulary term is deliberate friction.
#
# The vocabularies were chosen by taking the union of what the 15
# Medium m1 equations actually need, plus the EQ-HOOKE extension
# for Phase 3. If Phase 2 migration reveals a gap, add the term
# here and document the addition in DESIGN-COUPLING-SIEVE.md.

OBJECT_OF_INTEREST_VOCAB: FrozenSet[str] = frozenset({
    # Mechanics
    "rigid_body",
    "point_particle",
    "spring",
    # Fluids
    "fluid_parcel",
    "control_volume",
    # Electrical
    "conductor",
    "resistor",
    "capacitor",
    "inductor",
    "circuit_element",
    # Thermal / transport
    "thermal_body",
    "thermal_reservoir",
    "heat_conducting_medium",
    "diffusing_medium",
    # Chemical
    "chemical_species",
    "reaction_mixture",
    "solute",
    "solvent",
    # Biology / population
    "population",
    "predator_population",
    "prey_population",
    "organism",
    # Quantum
    "wavefunction",
    "quantum_state",
    "photon",
    # Relativity
    "lorentz_observer",
    "inertial_frame_body",
    # Statistics / information
    "probability_distribution",
    "information_channel",
    "random_variable",
    "bayesian_hypothesis",
    # Finance
    "portfolio",
    "security",
    "market",
    # Generic (last-resort; avoid in new work)
    "abstract_quantity",
})
"""Controlled vocabulary for `object_of_interest`.

Each term names a kind of thing a variable can be "about". The
decision rule when authoring: if two equations have variables with
different `object_of_interest` values, they should NOT be unified
at tier 1 even if they share the same property URI. A temperature
of a rigid body and a temperature of a fluid parcel are different
quantities from a modelling perspective, even if QUDT says both are
`Temperature`.
"""


CONTEXT_VOCAB: FrozenSet[str] = frozenset({
    # Frames
    "inertial_frame",
    "rotating_frame",
    "galilean",
    "lorentz_frame",
    "non_relativistic",
    "classical_limit",
    # Thermodynamic regimes
    "steady_state",
    "quasi_equilibrium",
    "near_equilibrium",
    "isothermal",
    "adiabatic",
    "isobaric",
    # Transport regimes
    "dilute",
    "low_reynolds",
    "high_reynolds",
    "incompressible",
    "laminar",
    "optically_thin",
    # Quantum regimes
    "free_particle",
    "bound_state",
    "time_independent",
    "time_dependent",
    # Probabilistic / measure
    "risk_neutral_measure",
    "physical_measure",
    "frequentist",
    "bayesian",
    # Biological
    "well_mixed",
    "mean_field",
    "spatial",
    # Generic
    "generic",
})
"""Controlled vocabulary for `context`.

`context` captures what the equation assumes about the world —
the regime, reference frame, or model — separately from what the
variable IS. The Wick-rotation bridge from Schrödinger to the heat
equation is exactly a `context` transformation: same variable
role, different context (`time_dependent` quantum →
`time_dependent` diffusive).
"""


# ---------------------------------------------------------------------------
# Descriptor dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Descriptor:
    """A compositional semantic descriptor for a typed variable.

    Frozen so it is hashable — we use descriptors as dictionary
    keys in the coupling sieve's tier-1 equivalence lookup.
    """
    object_of_interest: str
    property_uri: str
    context: str
    constraint: Optional[str] = None

    def as_dict(self) -> Dict[str, Optional[str]]:
        """Return a plain-dict form for ledger serialization."""
        return {
            "object_of_interest": self.object_of_interest,
            "property": self.property_uri,
            "context": self.context,
            "constraint": self.constraint,
        }

    def tier1_key(self) -> tuple:
        """The hashable key used for tier-1 equivalence matching.

        Tier 1 requires exact match on all three required fields
        plus identity on the constraint. Two variables whose
        `tier1_key()` agrees are "the same thing in both equations"
        by the sieve's criterion (see DESIGN-COUPLING-SIEVE.md §6.1).
        """
        return (
            self.object_of_interest,
            self.property_uri,
            self.context,
            self.constraint,
        )


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


class DescriptorValidationError(ValueError):
    """Raised when a descriptor block fails load-time validation.

    The error message always includes the equation id, variable
    name, and the offending field value so an authoring mistake is
    traceable from the stack trace alone.
    """
    def __init__(self, eq_id: str, var_name: str, field_name: str, value, reason: str):
        self.eq_id = eq_id
        self.var_name = var_name
        self.field_name = field_name
        self.value = value
        self.reason = reason
        super().__init__(
            f"{eq_id}.{var_name}.descriptor.{field_name}={value!r}: {reason}"
        )


# ---------------------------------------------------------------------------
# Descriptor registry (validator)
# ---------------------------------------------------------------------------


@dataclass
class DescriptorRegistry:
    """Validates descriptor blocks against the vocabularies + QUDT.

    Construction is cheap: the registry caches the frozensets for
    object/context and the set of QUDT QuantityKind URIs pulled from
    `qudt_loader.load_quantity_kinds()`. `validate()` is the only
    public method; it is called once per variable at load time.

    The registry is built lazily by `default_registry()` so tests
    and short scripts that don't touch the QUDT ontology don't pay
    the rdflib parsing cost.
    """
    object_vocab: FrozenSet[str]
    context_vocab: FrozenSet[str]
    quantity_kind_uris: FrozenSet[str]

    def validate(
        self,
        eq_id: str,
        var_name: str,
        descriptor: Descriptor,
    ) -> None:
        """Validate one descriptor. Raises `DescriptorValidationError`
        on the first failure. Does not accumulate errors — the
        authoring convention is "fix the first complaint, try again".
        """
        if descriptor.object_of_interest not in self.object_vocab:
            raise DescriptorValidationError(
                eq_id, var_name, "object_of_interest",
                descriptor.object_of_interest,
                "not in OBJECT_OF_INTEREST_VOCAB — add it to "
                "framework/descriptor.py with a design-doc update",
            )
        if descriptor.context not in self.context_vocab:
            raise DescriptorValidationError(
                eq_id, var_name, "context",
                descriptor.context,
                "not in CONTEXT_VOCAB — add it to "
                "framework/descriptor.py with a design-doc update",
            )
        if descriptor.property_uri not in self.quantity_kind_uris:
            raise DescriptorValidationError(
                eq_id, var_name, "property",
                descriptor.property_uri,
                "not a known QUDT QuantityKind URI — check vendor "
                "cache (framework/vendor/qudt_quantitykinds.ttl) or "
                "add a project-local extension",
            )

    def validate_many(
        self,
        eq_id: str,
        descriptors: Mapping[str, Descriptor],
    ) -> None:
        for var_name, descriptor in descriptors.items():
            self.validate(eq_id, var_name, descriptor)


# ---------------------------------------------------------------------------
# Lazy default registry
# ---------------------------------------------------------------------------


_DEFAULT_REGISTRY: Optional[DescriptorRegistry] = None


def default_registry() -> DescriptorRegistry:
    """Return the process-wide default registry.

    Built once on first call and reused. Triggers QUDT ingestion
    from the vendor cache, which takes ~200ms cold but is cached
    after that.
    """
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        from .qudt_loader import load_quantity_kind_uris
        _DEFAULT_REGISTRY = DescriptorRegistry(
            object_vocab=OBJECT_OF_INTEREST_VOCAB,
            context_vocab=CONTEXT_VOCAB,
            quantity_kind_uris=load_quantity_kind_uris(),
        )
    return _DEFAULT_REGISTRY


def reset_default_registry() -> None:
    """Test-only hook: clear the cached registry so the next
    `default_registry()` call rebuilds it. Used by tests that need
    to swap vocabularies mid-process.
    """
    global _DEFAULT_REGISTRY
    _DEFAULT_REGISTRY = None


# ---------------------------------------------------------------------------
# Dict → Descriptor parser used by the equation YAML loader
# ---------------------------------------------------------------------------


def parse_descriptor(
    eq_id: str,
    var_name: str,
    raw: Mapping[str, object],
) -> Descriptor:
    """Build a `Descriptor` from the YAML mapping under
    `variables[X].descriptor`. Raises `DescriptorValidationError`
    if required fields are missing.
    """
    required = ("object_of_interest", "property", "context")
    for field_name in required:
        if field_name not in raw:
            raise DescriptorValidationError(
                eq_id, var_name, field_name, None,
                f"missing required field",
            )
    return Descriptor(
        object_of_interest=str(raw["object_of_interest"]),
        property_uri=str(raw["property"]),
        context=str(raw["context"]),
        constraint=(
            str(raw["constraint"]) if raw.get("constraint") is not None else None
        ),
    )
