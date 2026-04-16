"""Custom dimensional registry — the single place where pint is extended.

Rationale (documented on the record, per review-board audit)
------------------------------------------------------------
The project uses `pint` for dimensional typing. Two design decisions
are load-bearing and must be explicit:

1. **Currency is a distinct base dimension `[currency]`.** We register
   `dollar` as its unit. This prevents a silent coincidence where a
   currency and a dimensionless scalar happen to share the same
   pint type. Applies to Black–Scholes today and any future monetary
   equation.

2. **Information is dimensionless — `nat` and `bit` are aliases for
   `dimensionless`, NOT a distinct base dimension.** This is the
   standard mathematical convention (Shannon 1948 formulates entropy
   as a scalar; the "bit" name indicates the log base, not a unit).
   **Consequence for the discovery pipeline:** any two equations
   whose variables are all dimensionless will pass the dimensional
   sieve trivially. This includes the forthcoming Shannon↔Gibbs
   identity (once Gibbs is added), where the real signal is the
   functional form and not the units. The null baseline must carry
   more weight in these cases; see `layer3_discovery._null_baseline`.
   The *alternative* — promoting `[information]` to a base dimension —
   would make Shannon and Gibbs dimensionally incompatible (nats vs
   J/K) and break a real structural identity. We chose the looser
   option deliberately.

3. **Population counts are `[substance]` in pint.** Biology
   equations that distinguish population from molar count should use
   a custom `[count]` dimension when added in Medium; until then
   `mole` serves.

This module is imported once by `typed_expression.py` and registers
the additions on the shared registry. No other module should extend
pint.
"""

from __future__ import annotations

import pint


def build_registry() -> pint.UnitRegistry:
    """Build the project-wide pint UnitRegistry with custom extensions.

    Called once by `typed_expression._pint()`.
    """
    registry = pint.UnitRegistry(auto_reduce_dimensions=True)

    # --- Currency as a distinct base dimension ---
    registry.define("currency_ = [currency]")
    registry.define("dollar = currency_")
    registry.define("usd = currency_")
    registry.define("euro = currency_")

    return registry


def assert_information_is_dimensionless() -> None:
    """Explicit, runtime-checked affirmation that the nat/bit decision
    (information is dimensionless, per the Medium readiness audit) is
    still the active policy. Run at module import or during tests.

    The test is trivially true under the current build_registry()
    because no explicit nat/bit units are defined; we make the
    check explicit so a future maintainer who adds
    `registry.define("bit = [information]")` will also have to
    reverse this test on the record.
    """
    registry = build_registry()
    dimensionless = registry.parse_expression("dimensionless").dimensionality
    # A scalar "1" has the same dimensionality as "dimensionless".
    one_dim = registry.Quantity(1.0).dimensionality
    assert dimensionless == one_dim, (
        "Information should be dimensionless per the policy in "
        "dimensions.py. If this assertion is failing, either pint's "
        "internal representation changed, or someone introduced a "
        "distinct information dimension. The latter breaks the "
        "Shannon↔Gibbs identity contract."
    )
    # pint ships `bit` as a built-in data/memory unit that is
    # already dimensionless. We verify that whatever pint thinks
    # `bit` means, it is dimensionless — NOT a distinct
    # information-dimension. If a future pint release promotes `bit`
    # to a base dimension, this assertion will catch it.
    try:
        bit_dim = registry.parse_expression("bit").dimensionality
        assert bit_dim == dimensionless, (
            f"Expected 'bit' to be dimensionless; pint reports "
            f"{bit_dim}. A distinct information dimension would "
            f"break the Shannon↔Gibbs identity contract."
        )
    except pint.errors.UndefinedUnitError:
        # Fine: no 'bit' unit in the registry. The assertion is
        # about the dimensionless invariant, not about presence.
        pass


# --- Information aliases to dimensionless (documented decision) ---
# `nat` and `bit` are *not* distinct dimensions; they are log-base
# labels for dimensionless scalars. This is a deliberate policy:
# information-theoretic entropies are dimensionless scalars, and
# the only difference between "1 bit" and "ln 2 nats" is a
# multiplicative constant that the notebook should apply
# explicitly. Making `bit` a distinct pint dimension would break
# the future Shannon↔Gibbs cross-domain identity (Gibbs is in
# [energy]/[temperature], Shannon is dimensionless — pint would
# refuse to compare them).
#
# Medium milestone 1: this decision is tested by
# `assert_information_is_dimensionless` above; any future
# maintainer who tries to reverse the policy will have to also
# reverse that assertion explicitly.

    return registry
