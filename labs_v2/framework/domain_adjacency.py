"""Domain adjacency matrix for the Layer 5 coupling sieve.

Phase 5 Gate 2 (see `labs_v2/DESIGN-COUPLING-SIEVE.md` §10). The
matrix declares explicitly which (domain_A, domain_B) pairs can
physically interact, reducing the candidate space before any
variable-pair enumeration.

Design principles:

1. **Explicit is better than implicit.** An absence in the matrix
   means "never considered", which is reviewable. We prefer false
   positives (allowed pair that ends up rejected downstream) over
   false negatives (silently killed pair).

2. **Default-allow when uncertain.** `is_adjacent` returns True for
   any pair whose status is not explicitly `False`. Adding
   explicit False entries is how we kill known-implausible pairs
   (e.g., relativity ↔ probability, finance ↔ thermal transport).

3. **Symmetric.** (A, B) and (B, A) always have the same status.
   `is_adjacent` normalises the argument order internally.

4. **Additions require design-doc rationale.** Flipping a pair
   from default-allow to explicit False (or vice versa) is a
   binding change that gets a line in the DESIGN-COUPLING-SIEVE.md
   execution log.

The matrix is consulted during Gate 2 of the coupling sieve's
two-gate prefilter. Gate 1 is the pint-dimension check on the
individual variables; Gate 2 is this module. Both must pass
before any tier matching is attempted.
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Tuple


def _ordered(a: str, b: str) -> Tuple[str, str]:
    """Return the pair in alphabetical order, canonicalising
    symmetric lookups. No other logic — just a two-element sort.
    """
    return (a, b) if a <= b else (b, a)


# The explicit adjacency table. True = allowed (default when
# absent); False = explicitly killed. Stored as a symmetric dict
# with the pair written in alphabetical order.
#
# Categories of explicit False:
#   - "no physical coupling path": the two domains share no
#     quantity whose identification would have physical meaning
#     (relativity ↔ probability, Shannon ↔ fluid dynamics)
#   - "scale mismatch": quantum field ↔ population dynamics
#   - "pre-registered rejection": the design doc §14 rejections
_EXPLICIT: Dict[Tuple[str, str], bool] = {}


# Pre-registered POSITIVES: always allowed, documented here so
# a false negative (pair silently killed) is a loud failure.
POSITIVE_PAIRS: FrozenSet[Tuple[str, str]] = frozenset({
    _ordered("classical_mechanics", "classical_mechanics"),   # Newton + Hooke
    _ordered("thermal_transport", "mass_transport"),          # Fourier + Fick
    _ordered("chemical_kinetics", "mass_transport"),          # Arrhenius + Fick
    _ordered("population_dynamics", "mass_transport"),        # LV + Fick spatial
    _ordered("quantum_mechanics", "thermal_transport"),       # Wick rotation
})

# Pre-registered REJECTIONS (§14 table A-C). These MUST NOT
# surface a coupling. They go into _EXPLICIT as False so Gate 2
# rejects them before tier matching even runs.
_REJECTIONS = [
    (_ordered("classical_mechanics", "information_theory"),
     "Newton II + Shannon entropy: no physical coupling path. "
     "Force is an inertial quantity; entropy is a functional of "
     "a probability measure. Any apparent algebraic similarity is "
     "coincidence, not physics."),
    (_ordered("quantitative_finance", "population_dynamics"),
     "Black-Scholes + Lotka-Volterra: geometric Brownian motion "
     "and predator-prey dynamics share only superficial "
     "nonlinearity. No shared conservation law, no shared "
     "physical mechanism."),
    (_ordered("special_relativity", "probability"),
     "Lorentz factor + Bayes theorem: no transform exists that "
     "can map between a kinematic invariant and a coherent "
     "probability measure. Pre-registered as an obvious-false-"
     "positive trap for the sieve."),
]
for pair, _why in _REJECTIONS:
    _EXPLICIT[pair] = False

# Additional default-False rejections beyond the pre-registered
# list. These are domains that are almost certainly unrelated and
# we prefer to save the combinatorics for the useful pairs. Each
# entry carries a one-line rationale; revisit if Medium m3 needs
# a coupling that requires enabling one of these.
_ADDITIONAL_FALSE = [
    (_ordered("spectroscopy", "population_dynamics"),
     "Beer-Lambert is a one-shot optical attenuation law; no "
     "plausible coupling to population ecology."),
    (_ordered("special_relativity", "mass_transport"),
     "Lorentz kinematics does not interact with diffusive "
     "transport at any scope this corpus operates in."),
    (_ordered("quantitative_finance", "thermal_transport"),
     "Black-Scholes and heat conduction are formally related via "
     "log-price + time-reversal, but this bridge is in the CoV "
     "sieve (Layer 2), not the coupling sieve. The coupling "
     "sieve treats them as non-adjacent so we don't double-count."),
]
for pair, _why in _ADDITIONAL_FALSE:
    _EXPLICIT[pair] = False


def is_adjacent(domain_a: str, domain_b: str) -> bool:
    """Return True if the two domains are allowed to produce
    coupling candidates.

    Lookup policy:
    - If the pair is in `_EXPLICIT`, return the stored value.
    - Otherwise return True (default-allow).

    This is Gate 2 of the two-gate prefilter. A False result
    means the sieve will never construct a coupling candidate
    between any variable of domain_a and any variable of
    domain_b, regardless of their individual descriptors.
    """
    pair = _ordered(domain_a, domain_b)
    return _EXPLICIT.get(pair, True)


def explicit_rejections() -> Dict[Tuple[str, str], bool]:
    """Return a shallow copy of the explicit-False entries for
    inspection (used by the sieve's preflight summary and by the
    tests).
    """
    return {k: v for k, v in _EXPLICIT.items() if v is False}
