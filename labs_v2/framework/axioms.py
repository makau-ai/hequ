"""Machine-checkable axiomatic characterization of equations.

Motivation (from the methodology re-audit)
------------------------------------------
The headline concern the historical-methodology auditor repeated in
both the Small and Small-plus audits is **Principle 3: axiomatic
characterization consumed by the sieves**. Every equation's YAML
ships an `assumptions` block as free text, but no code reads those
assumptions; the sieves operate on surface sympy trees alone.

At N=10 this is tolerable — the corpus is small enough that pattern
matching finds exactly the pre-registered identities and nothing
else. At N=30 with richer sieves, the false-positive rate of pure
pattern matching outruns the null-baseline's ability to absorb it,
and the engine starts laundering surface matches as "discoveries".

This module is the smallest step that addresses the concern: a
controlled vocabulary of axiom tags that each equation declares in
YAML, plus a compatibility check that the sieves consume during
candidate generation. Incompatible pairs are rejected at Layer 2
before any symbolic search; compatible pairs carry their axiom
Jaccard score through to Layer 3 where it demotes or accepts the
final outcome.

Vocabulary
----------
The axiom tags are deliberately minimal (about a dozen) and fall
into four families:

- **Structural**: algebraic vs differential, linear vs nonlinear,
  constant_coefficients, commutative_factors
- **Regime**: steady_state vs dynamical, dilute_limit,
  thermal_equilibrium, non_relativistic, classical (non-quantum)
- **Symmetry**: isotropic, homogeneous, time_translation_invariant
- **Statistical**: deterministic vs stochastic_derivation,
  dimensionless

Any equation may declare any subset. Contradictory pairs (e.g.
`linear` and `nonlinear`, or `steady_state` and `dynamical`) are
forbidden within a single equation and trigger a loader error.
Cross-equation contradictions reject the pair from consideration.

Compatibility rule
------------------
Two equations are COMPATIBLE iff:
  1. No axiom in A contradicts any axiom in B (see CONTRADICTIONS).
  2. Their Jaccard similarity
     `|A ∩ B| / |A ∪ B|`
     is at least `MIN_JACCARD` (default 0.3).

Jaccard below the threshold but without contradictions means the
equations have too little in common for a confident analogy — such
candidates are recorded as `CONJECTURAL`, not `PROVED`.

Design decisions
----------------
- The vocabulary lives here, not in each equation's YAML. This
  guarantees a single source of truth for axiom names. Adding a new
  axiom requires a change here AND in the equations that declare it
  — both deliberate steps.
- Contradictions are symmetric and transitive through their defining
  pair sets. We do not attempt a full taxonomic lattice because the
  vocabulary is small enough for the explicit pair list.
- The module has no sympy or pint dependency — it's pure set
  algebra on strings — so it is cheap to import and test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Set, Tuple


# Canonical vocabulary. Adding an entry here is the one-and-only
# place to do so — the loader in `typed_expression.py` validates
# every YAML declaration against this set.
#
# Medium milestone 1 extension: added tags for quantum mechanics,
# relativity, fluids, variational principles, and biology so the
# first five new equations can declare their axiomatic stance
# against the same controlled vocabulary the Small-plus-plus
# corpus uses. Additions are grouped by domain family at the end.
AXIOM_VOCABULARY: FrozenSet[str] = frozenset({
    # --- Structural ---
    "algebraic",              # pure algebraic relation, no derivatives
    "differential",           # contains derivatives / is a PDE/ODE
    "linear",                 # linear in state variables
    "nonlinear",              # explicitly nonlinear
    "constant_coefficients",  # no state-dependent parameters
    "commutative_factors",    # multiplication of factors is commutative

    # --- Regime ---
    "steady_state",           # no explicit time dependence
    "dynamical",              # time-evolution law
    "dilute_limit",           # small-parameter expansion regime
    "thermal_equilibrium",    # Boltzmann-distributed state
    "non_relativistic",       # |v| << c
    "classical",              # non-quantum (used for non-QM laws)

    # --- Symmetry ---
    "isotropic",              # rotationally invariant
    "homogeneous",            # translation-invariant
    "time_translation_invariant",
    "galilean_invariant",     # Galilean group (non-relativistic fluids, Newton)
    "lorentz_invariant",      # Lorentz group (special relativity)
    "gauge_invariant",        # gauge symmetry (electromagnetism, Yang-Mills)

    # --- Statistical / Information ---
    "deterministic",          # no randomness in the law itself
    "stochastic_derivation",  # law derived from stochastic process
    "dimensionless",          # all variables dimensionless
    "concave",                # functional is concave (Shannon, utility)

    # --- Quantum mechanics ---
    "quantum",                # explicitly quantum (complementary to 'classical')
    "hermitian",              # observable / Hamiltonian is self-adjoint
    "unitary",                # time evolution is unitary (norm-preserving)
    "linear_superposition",   # state space admits linear combinations
    "probability_conserving", # total probability is a conserved quantity

    # --- Fluids / continuum ---
    "incompressible",         # density is constant
    "compressible",           # density can vary
    "viscous",                # nonzero viscosity
    "inviscid",               # zero viscosity idealisation

    # --- Variational / mechanics ---
    "variational",            # stationary-point condition of a functional
    "stationary_action",      # specifically derived from Hamilton's principle
    "hamiltonian_form",       # expressible as dH/dp, -dH/dq
    "conservative_force",     # force derived from a potential

    # --- Biology / population dynamics ---
    "conservative_count",     # total count (mass, population, probability) conserved
    "logistic",               # quadratic saturation in population term
    "bounded_growth",         # carrying capacity bounded
})


# Pairs that cannot both hold in a single equation and cannot hold
# across a candidate unification pair either. Listed once; the
# compatibility check treats (a, b) and (b, a) symmetrically.
#
# Medium milestone 1: added contradictions for QM/fluids/relativity
# domains. The old cleanup of the `classical`/`non_relativistic`
# non-contradiction is removed — those two are distinct orthogonal
# tags and simply left out of the contradiction set.
CONTRADICTIONS: FrozenSet[Tuple[str, str]] = frozenset({
    # Structural — these are real algebraic contradictions
    ("algebraic", "differential"),
    ("linear", "nonlinear"),
    ("steady_state", "dynamical"),
    # Statistical
    ("deterministic", "stochastic_derivation"),
    # QM vs stochastic (unitary evolution is deterministic in law)
    ("unitary", "stochastic_derivation"),
    # Fluids
    ("incompressible", "compressible"),
    ("inviscid", "viscous"),
    # Relativity
    ("lorentz_invariant", "non_relativistic"),
    ("lorentz_invariant", "galilean_invariant"),
    # NOTE: `classical` vs `quantum` is NOT a structural contradiction.
    # The Schrödinger equation (quantum) and the heat equation
    # (classical) are formally the same PDE under Wick rotation
    # (t → −iτ) — this is the Feynman-Kac bridge and the whole
    # point of the CoV sieve's `wick_rotation` substitution. A
    # contradiction here would block the sieve from finding the
    # exact cross-domain identity it was built to find. The
    # `classical` and `quantum` tags are preserved in the
    # vocabulary as physics-regime descriptors, but they do not
    # contradict each other at the structural/algebraic level.
})


# Minimum Jaccard similarity for two equations to pass the axiom
# filter. Below this, a candidate can still be recorded as
# CONJECTURAL but not PROVED or EMPIRICAL.
MIN_JACCARD: float = 0.3


# Result type for the compatibility check. Kept as a plain dataclass
# so it serialises into the discovery ledger's `evidence` bag.
@dataclass
class AxiomCompatibility:
    """Verdict on whether two equations share enough axiomatic ground
    to support a cross-domain unification claim.

    Fields
    ------
    compatible:
        True iff there are no contradictions AND Jaccard ≥ MIN_JACCARD.
        Incompatible candidates are either REJECTED (contradictions)
        or demoted to CONJECTURAL (too little overlap).
    contradictions:
        List of (axiom_a, axiom_b) pairs that contradict. Empty when
        `compatible` is True.
    jaccard:
        `|A ∩ B| / |A ∪ B|`, the set similarity of the two equations'
        axiom sets. 1.0 means identical; 0.0 means disjoint.
    shared:
        Sorted list of axioms present in both sets — the "load-bearing
        common ground" for the claim.
    only_a / only_b:
        Sorted lists of axioms present in only one set. These are
        where the asymmetry lies — important for human readers
        deciding if the hypothesis is interesting.
    """
    compatible: bool
    contradictions: Tuple[Tuple[str, str], ...]
    jaccard: float
    shared: Tuple[str, ...]
    only_a: Tuple[str, ...]
    only_b: Tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "compatible": self.compatible,
            "contradictions": [list(p) for p in self.contradictions],
            "jaccard": round(self.jaccard, 4),
            "shared": list(self.shared),
            "only_a": list(self.only_a),
            "only_b": list(self.only_b),
        }


def validate_axioms(axioms: Set[str]) -> None:
    """Check that the declared axiom set is in the vocabulary and has
    no internal contradictions. Called by the loader on every
    equation YAML.

    Raises
    ------
    ValueError:
        If any axiom is not in `AXIOM_VOCABULARY`, or if the set
        contains a contradictory pair.
    """
    unknown = axioms - AXIOM_VOCABULARY
    if unknown:
        raise ValueError(
            f"Unknown axioms: {sorted(unknown)}. "
            f"Vocabulary: {sorted(AXIOM_VOCABULARY)}"
        )
    for a, b in CONTRADICTIONS:
        if a in axioms and b in axioms:
            raise ValueError(
                f"Contradictory axioms in the same equation: {a!r} and {b!r}"
            )


def compatibility(a_axioms: Set[str], b_axioms: Set[str]) -> AxiomCompatibility:
    """Compare two equation axiom sets and return the verdict.

    Semantics
    ---------
    - Any contradiction makes `compatible=False` regardless of Jaccard.
    - No contradictions and Jaccard ≥ MIN_JACCARD ⇒ compatible=True.
    - No contradictions and Jaccard < MIN_JACCARD ⇒ compatible=False
      (but the absence of contradictions means the pair can still be
      recorded as CONJECTURAL by the sieve).

    Empty axiom sets on either side return compatibility=False with
    Jaccard 0.0 — the methodology auditor's point: equations without
    declared axioms cannot participate in axiom-filtered discovery.
    """
    contradictions = []
    for ca, cb in CONTRADICTIONS:
        if (ca in a_axioms and cb in b_axioms) or (cb in a_axioms and ca in b_axioms):
            contradictions.append((ca, cb))
    shared = a_axioms & b_axioms
    union = a_axioms | b_axioms
    jaccard = len(shared) / len(union) if union else 0.0
    compatible = (
        len(contradictions) == 0
        and jaccard >= MIN_JACCARD
        and len(union) > 0
    )
    return AxiomCompatibility(
        compatible=compatible,
        contradictions=tuple(sorted(contradictions)),
        jaccard=jaccard,
        shared=tuple(sorted(shared)),
        only_a=tuple(sorted(a_axioms - b_axioms)),
        only_b=tuple(sorted(b_axioms - a_axioms)),
    )
