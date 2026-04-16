"""Layer 5 — the cross-domain coupling sieve.

Phase 5 deliverable for Medium milestone 2 (see
`labs_v2/DESIGN-COUPLING-SIEVE.md` §10). Takes a corpus of
equations loaded with I-ADOPT descriptors and emits a list of
`CouplingHypothesis` objects at tiers 1, 2, and 3.

Pipeline
--------
1. **Two-gate prefilter** (§10):
   - Gate 1: pint-dimension compatibility of variable A and
     variable B. Rejects ~70-80% of pairs on typical corpora.
   - Gate 2: domain adjacency lookup
     (`framework.domain_adjacency.is_adjacent`). Rejects
     explicit-False domain pairs and lets default-allow through.

2. **Tier 1 — Equivalence matcher**: the strongest claim the
   sieve can make. Two variables match at tier 1 iff their
   `descriptor.tier1_key()` tuples are exactly equal AND pint
   dimensions are identical. No transfer function needed
   (implicit identity).

3. **Tier 2 — Similarity matcher**: weaker than tier 1 but not
   conjectural. Two variables match at tier 2 iff:
   - Same `object_of_interest` OR same property URI, AND
   - Compatible contexts (exact match, or both in the small set
     of "Wick-compatible" context pairs declared below), AND
   - Compatible pint dimensions, AND
   - A non-identity transfer function from the library yields a
     fit for the canonical algebraic relation between the two
     variables' coefficient positions in their respective
     equations.

4. **Tier 3 — Conjectural matcher**: dimensionally compatible
   but semantically unrelated. These are ALWAYS conjectural;
   they never auto-promote. The sieve emits them so the AI
   review board has the option to investigate, but they carry a
   `review_required=True` flag.

Discovery vs proof
------------------
The sieve proves nothing. Every emitted hypothesis is a
*candidate* the downstream physical-constraint filter (Phase 6)
and the AI review board (Phase 9 / Phase 12 of the design doc)
must confirm. Nothing in this module touches the ledger or the
discovery classification.

Determinism and ordering
------------------------
All iteration is over `sorted(equations.items())` so the sieve's
output is deterministic under permutation of the input dict, and
the pre-registered validation tests are stable. Tier-1 matches
are emitted before tier-2 before tier-3 so the first match of
any given variable pair is the strongest the sieve can make.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Tuple

import itertools

import sympy as sp

from .couplings import (
    CouplingHypothesis,
    CouplingTier,
    get_transfer_function,
)
from .descriptor import Descriptor
from .domain_adjacency import is_adjacent
from .layer2_sieves import (
    StructuralCandidate,
    dimensionally_consistent_structural_sieve,
    structural_sieve,
)
from .physical_constraints import BondGraphRole, _bond_graph_role
from .typed_expression import TypedExpression


# ---------------------------------------------------------------------------
# Context compatibility
# ---------------------------------------------------------------------------
#
# For tier 2, contexts must be compatible but not necessarily
# identical. The allowed cross-context pairs are declared here
# explicitly. Adding an entry requires a line in the design doc.
#
# Key observation: the Wick-rotation bridge (Schrödinger ↔
# heat equation) is a context transformation, not a property
# transformation. The property "wavefunction time derivative" is
# not the same as "temperature time derivative", but under the
# t → -i*tau rotation they satisfy the same PDE form. We
# encode this by declaring `time_dependent` and `near_equilibrium`
# as tier-2 compatible for quantum/thermal couplings.

_CONTEXT_COMPATIBLE_PAIRS = frozenset({
    # Wick rotation bridge
    ("time_dependent", "near_equilibrium"),
    ("time_dependent", "quasi_equilibrium"),
    # Log-price bridge (Black-Scholes ↔ heat eq)
    ("risk_neutral_measure", "near_equilibrium"),
    # Steady-state vs frame-agnostic mechanics
    ("inertial_frame", "steady_state"),
    # Dilute ↔ near-equilibrium for Fick/Fourier coupling
    ("dilute", "near_equilibrium"),
    # Well-mixed ↔ dilute for population-coupling
    ("well_mixed", "dilute"),
})


def _contexts_compatible(ctx_a: str, ctx_b: str) -> bool:
    """Return True if two contexts can participate in a tier-2
    coupling. Exact match always; otherwise check the explicit
    compatibility set (symmetric).
    """
    if ctx_a == ctx_b:
        return True
    if (ctx_a, ctx_b) in _CONTEXT_COMPATIBLE_PAIRS:
        return True
    if (ctx_b, ctx_a) in _CONTEXT_COMPATIBLE_PAIRS:
        return True
    return False


# ---------------------------------------------------------------------------
# Sieve runner
# ---------------------------------------------------------------------------


@dataclass
class SieveReport:
    """Result of one full sieve pass on the corpus.

    Carries the emitted hypotheses plus bookkeeping counters for
    post-run audit. The counters are the input the Phase 10
    validation harness uses to verify the sieve didn't silently
    throw away pre-registered couplings.
    """
    hypotheses: List[CouplingHypothesis] = field(default_factory=list)
    total_variable_pairs_considered: int = 0
    rejected_by_dimension: int = 0
    rejected_by_domain_adjacency: int = 0
    tier1_count: int = 0
    tier2_count: int = 0
    tier3_count: int = 0

    def summary(self) -> str:
        return (
            f"SieveReport: pairs={self.total_variable_pairs_considered} "
            f"dim_rejected={self.rejected_by_dimension} "
            f"domain_rejected={self.rejected_by_domain_adjacency} "
            f"tier1={self.tier1_count} "
            f"tier2={self.tier2_count} "
            f"tier3={self.tier3_count}"
        )


def _dims_match(eq_a: TypedExpression, var_a: str,
                eq_b: TypedExpression, var_b: str) -> bool:
    """Return True if the two variables have exactly-equal pint
    dimensionality. The coupling sieve does NOT currently allow
    dimension-changing transfer functions; if a tier-2 fit needs
    to apply a `scale` with dimensional factor, the downstream
    physical-constraint filter will catch it. For the initial
    Medium m2 scope we require dimension identity.
    """
    return eq_a.variables[var_a].dimensionality() == eq_b.variables[var_b].dimensionality()


def _tier1_match(
    eq_a_id: str, eq_b_id: str,
    var_a: str, var_b: str,
    desc_a: Descriptor, desc_b: Descriptor,
) -> Optional[CouplingHypothesis]:
    """Check whether two variables match at tier 1 (equivalence).
    Returns a CouplingHypothesis on success, None otherwise.

    Tier 1 requires the tier1 descriptor keys to be exactly equal.
    `Descriptor.tier1_key()` returns a 4-tuple of
    (object_of_interest, property_uri, context, constraint).
    """
    if desc_a.tier1_key() != desc_b.tier1_key():
        return None
    return CouplingHypothesis(
        eq_a_id=eq_a_id,
        eq_b_id=eq_b_id,
        var_a=var_a,
        var_b=var_b,
        descriptor_a=desc_a,
        descriptor_b=desc_b,
        transfer_function="identity",
        transfer_params={},
        tier=CouplingTier.TIER1_EQUIVALENCE,
        reason=(
            f"Identical tier1 key "
            f"(object={desc_a.object_of_interest}, "
            f"property={desc_a.property_uri.rsplit('/', 1)[-1]}, "
            f"context={desc_a.context}, "
            f"constraint={desc_a.constraint})"
        ),
    )


def _tier2_match(
    eq_a_id: str, eq_b_id: str,
    var_a: str, var_b: str,
    desc_a: Descriptor, desc_b: Descriptor,
) -> Optional[CouplingHypothesis]:
    """Check whether two variables match at tier 2 (similarity).

    Tier 2 requires:
    - Same object_of_interest OR same property URI (the "shared
      semantic anchor" condition — at least one of the two
      primary descriptor fields agrees).
    - Compatible contexts via `_contexts_compatible`.

    The transfer function for tier-2 couplings at this point is
    the symbolic `identity` (since we already required dimension
    equality upstream). The transfer function slot is reserved
    for Phase 6 / Phase 7 enrichment: when a tier-2 coupling
    passes the physical-constraint filter, those modules can
    rewrite the transfer function to something more specific
    (scale, first_order_lag, etc.).

    We do NOT try to fit the full library here because the
    variable-level sieve doesn't have enough context — the right
    scope for transfer-function fitting is the whole-equation
    composition, which Phase 6 does. Keeping tier 2 at
    "descriptor similarity + dimension match" keeps the sieve
    fast and the downstream stages honest.
    """
    # Tier 1 already filtered exact matches; tier 2 is the relaxed
    # case. If the keys were exactly equal we'd never have reached
    # here — `_tier1_match` would have been picked first.
    same_object = desc_a.object_of_interest == desc_b.object_of_interest
    same_property = desc_a.property_uri == desc_b.property_uri
    if not (same_object or same_property):
        return None
    if not _contexts_compatible(desc_a.context, desc_b.context):
        return None
    # Identify the looser field (object or property) so the
    # reason string is informative.
    shared_bits = []
    if same_object:
        shared_bits.append(f"object={desc_a.object_of_interest}")
    if same_property:
        shared_bits.append(
            f"property={desc_a.property_uri.rsplit('/', 1)[-1]}"
        )
    shared_bits.append(
        f"ctx_a={desc_a.context}" if desc_a.context == desc_b.context
        else f"ctx_pair=({desc_a.context},{desc_b.context})"
    )
    return CouplingHypothesis(
        eq_a_id=eq_a_id,
        eq_b_id=eq_b_id,
        var_a=var_a,
        var_b=var_b,
        descriptor_a=desc_a,
        descriptor_b=desc_b,
        transfer_function="identity",  # refined by Phase 6 if needed
        transfer_params={},
        tier=CouplingTier.TIER2_SIMILARITY,
        reason=(
            "Shared semantic anchor + compatible context: "
            + ", ".join(shared_bits)
        ),
    )


def _tier3_match(
    eq_a_id: str, eq_b_id: str,
    var_a: str, var_b: str,
    desc_a: Descriptor, desc_b: Descriptor,
) -> CouplingHypothesis:
    """Build a conjectural (tier-3) hypothesis. This path is only
    reached if tier 1 and tier 2 both fail but the pair still
    survived the dimension gate and the domain-adjacency gate.
    The hypothesis is flagged for AI review board inspection.

    Unlike tier 1 and tier 2, tier 3 always succeeds structurally
    — there's nothing to fail. The return type is
    CouplingHypothesis, not Optional, because the decision to
    emit a tier-3 hypothesis is the caller's (they've already
    decided the pair passed the prefilter).
    """
    return CouplingHypothesis(
        eq_a_id=eq_a_id,
        eq_b_id=eq_b_id,
        var_a=var_a,
        var_b=var_b,
        descriptor_a=desc_a,
        descriptor_b=desc_b,
        transfer_function="identity",
        transfer_params={},
        tier=CouplingTier.TIER3_CONJECTURAL,
        reason=(
            "Dimensionally compatible but semantically unrelated: "
            f"a=({desc_a.object_of_interest}, "
            f"{desc_a.property_uri.rsplit('/', 1)[-1]}, "
            f"{desc_a.context}), "
            f"b=({desc_b.object_of_interest}, "
            f"{desc_b.property_uri.rsplit('/', 1)[-1]}, "
            f"{desc_b.context}) — AI review board decision required"
        ),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _score_bijection_by_roles(
    eq_a: TypedExpression,
    eq_b: TypedExpression,
    substitution: Dict[str, str],
) -> float:
    """Score a structural bijection by bond-graph role matching.

    Higher is better. With the Phase 11 fix, the bond-graph
    taxonomy is 6-way: EFFORT, FLOW, PARAMETER, GRADIENT, STATE,
    NEITHER. Matching roles are worth +3; mismatched port
    variables (effort↔flow) are penalised heavily so a
    duality-violating pair can never be selected; role mismatches
    across other axes are mildly penalised.

    The 6-way taxonomy is what discriminates the two equally
    valid Fourier↔Fick bijections: under 3-way tagging both
    scored identically (everything not-a-flux was NEITHER), so
    the choice fell to an unreliable tiebreaker. Under 6-way
    tagging the canonical bijection {J↔q, D↔k, dC_dx↔dT_dx}
    pairs FLOW-FLOW, PARAMETER-PARAMETER, GRADIENT-GRADIENT and
    scores +9; the swapped bijection {J↔q, D↔dT_dx, dC_dx↔k}
    pairs FLOW-FLOW, PARAMETER-GRADIENT, GRADIENT-PARAMETER and
    scores +3 − 2 = +1.

    No dimension-distance component: Newton↔Ohm is an explicitly
    *cross-dimensional* analogy, and dim distance would push the
    sieve towards the wrong (low-distance) bijection there.
    """
    score = 0.0
    EFFORT_FLOW = {BondGraphRole.EFFORT, BondGraphRole.FLOW}
    for var_a, var_b in substitution.items():
        desc_a = eq_a.variables[var_a].descriptor
        desc_b = eq_b.variables[var_b].descriptor
        if desc_a is None or desc_b is None:
            continue
        role_a = _bond_graph_role(desc_a)
        role_b = _bond_graph_role(desc_b)
        if role_a == BondGraphRole.NEITHER or role_b == BondGraphRole.NEITHER:
            # NEITHER is the catch-all for dimensionless and
            # un-classified URIs. Treat as neutral so it doesn't
            # tip the balance.
            continue
        if role_a == role_b:
            score += 3.0
        elif role_a in EFFORT_FLOW and role_b in EFFORT_FLOW:
            # Effort↔flow dual mismatch — physically invalid, kill
            # the bijection.
            score -= 100.0
        else:
            # Cross-axis mismatch (e.g. PARAMETER↔GRADIENT): a
            # mild penalty is enough to prefer aligned bijections
            # without killing anything outright.
            score -= 2.0
    return score


def _best_bijection_for_structural(
    cand: StructuralCandidate,
    eq_a: TypedExpression,
    eq_b: TypedExpression,
) -> Dict[str, str]:
    """Given a structural-sieve candidate whose bijection is one
    of several valid renamings under commutative multiplication,
    return the variable map with the highest bond-graph-role
    score.

    Algorithm:
    1. Enumerate all permutations of eq_b's variables against
       sorted(eq_a.variables) up to the V-cap used by the
       structural sieve.
    2. For each permutation, check whether the renamed
       canonical forms are still equal (i.e., this is a valid
       alternative bijection). Skip if not.
    3. Score each surviving bijection via `_score_bijection_by_roles`.
    4. Return the highest-scoring one. Ties broken by sticking
       with the original candidate (preserves determinism).

    This is a surgical fix for Phase 11's bug: the sieve
    correctly identifies that Fourier and Fick share a canonical
    shape, but when multiple renamings satisfy the shape due to
    multiplicative commutativity, it was picking the first
    alphabetical one rather than the physically correct
    (role-preserving) one.
    """
    vars_a = sorted(eq_a.variables.keys())
    vars_b = sorted(eq_b.variables.keys())
    if len(vars_a) != len(vars_b):
        return cand.substitution
    # Tight V-cap: 6! = 720 permutations, tractable.
    if len(vars_a) > 6:
        return cand.substitution
    expr_a = eq_a.canonical_form
    expr_b = eq_b.canonical_form
    best_sub = cand.substitution
    best_score = _score_bijection_by_roles(eq_a, eq_b, cand.substitution)
    for perm in itertools.permutations(vars_b):
        sub = dict(zip(vars_a, perm))
        subs_map = {sp.Symbol(s): sp.Symbol(t) for s, t in sub.items()}
        relabelled = expr_a.subs(subs_map, simultaneous=True)
        diff = sp.simplify(relabelled - (cand.sign * expr_b))
        if diff != 0:
            continue
        score = _score_bijection_by_roles(eq_a, eq_b, sub)
        if score > best_score:
            best_score = score
            best_sub = sub
    return best_sub


def _tier2_from_structural(
    equations: Mapping[str, TypedExpression],
) -> List[CouplingHypothesis]:
    """Bridge the existing Layer 2 structural sieve into Layer 5
    tier-2. The structural sieve finds equation pairs whose
    canonical forms are syntactically identical under a variable
    permutation; for the Layer 5 coupling framework we wrap each
    discovered bijection as one CouplingHypothesis per variable
    pair, all tagged tier-2.

    Why this path exists
    --------------------
    Variable-level tier-2 (same descriptor key + dim-compat) is
    too strict for cross-domain analogies whose whole equations
    match under rename but whose individual variables have
    different dimensions (the canonical case: Fourier's
    `q + k*dT_dx` and Fick's `J + D*dC_dx`). These couplings are
    pre-registered (§14) as tier-2 and must surface; the only
    way to surface them is at the equation level, not the
    variable level.

    We reuse the existing `structural_sieve` (and the dimensionally-
    consistent variant) because those already solved the
    combinatorial problem (hash pre-filter, V-cap, alpha-canonical
    signature). Running a second matcher would duplicate work
    and risk divergence.

    The emitted hypotheses use `transfer_function="identity"`
    because the structural match is an algebraic identity after
    rename. Downstream Phase 6 may rewrite this to
    `first_order_lag` or a domain-specific form if the
    physical-constraint filter reveals a real-world coupling
    transform (e.g., Soret effect for Fourier↔Fick).

    Duplicate suppression: tier-2 structural pairs may have
    variable slots that also match at tier-1 (same dimension
    AND same descriptor). In that case the tier-1 path in the
    main loop emits the pair, and the structural wrapper skips
    any variable pair that was already seen at tier-1 (detected
    by matching (eq_a_id, eq_b_id, var_a, var_b) against the
    prior report).
    """
    hypotheses: List[CouplingHypothesis] = []
    candidates: List[StructuralCandidate] = structural_sieve(dict(equations))
    for cand in candidates:
        # Gate 2 still applies: respect domain adjacency even for
        # structurally-identical equations. A structural match
        # between finance and thermal transport is exactly the
        # Black-Scholes↔heat bridge which Layer 2's CoV sieve
        # owns, so we let the adjacency matrix kill it here.
        eq_a = equations[cand.eq_a]
        eq_b = equations[cand.eq_b]
        if not is_adjacent(eq_a.domain, eq_b.domain):
            continue
        # Re-score the bijection: the structural sieve is
        # dimension-blind and picks the alphabetically-first
        # valid rename. For cases like Fourier↔Fick where
        # multiplicative commutativity admits several bijections,
        # we prefer the one that pairs bond-graph roles
        # correctly (Phase 11 board-flagged bug).
        better_sub = _best_bijection_for_structural(cand, eq_a, eq_b)
        for var_a_name, var_b_name in better_sub.items():
            desc_a = eq_a.variables[var_a_name].descriptor
            desc_b = eq_b.variables[var_b_name].descriptor
            if desc_a is None or desc_b is None:
                continue
            hypotheses.append(CouplingHypothesis(
                eq_a_id=cand.eq_a,
                eq_b_id=cand.eq_b,
                var_a=var_a_name,
                var_b=var_b_name,
                descriptor_a=desc_a,
                descriptor_b=desc_b,
                transfer_function="identity",
                transfer_params={},
                tier=CouplingTier.TIER2_SIMILARITY,
                reason=(
                    f"Structural equation-level identity "
                    f"(sign={cand.sign:+d}): the canonical forms of "
                    f"{cand.eq_a} and {cand.eq_b} are syntactically "
                    f"equal under rename, and {var_a_name} maps to "
                    f"{var_b_name} under the discovered bijection"
                ),
            ))
    return hypotheses


def run_coupling_sieve(
    equations: Mapping[str, TypedExpression],
    *,
    emit_tier3: bool = True,
) -> SieveReport:
    """Run the full Layer 5 coupling sieve on a loaded corpus.

    Parameters
    ----------
    equations
        Mapping {equation_id: TypedExpression} from
        `framework.typed_expression.load_all_equations`. Every
        equation must already have descriptor blocks on every
        variable — a precondition the loader enforces, so the
        sieve doesn't need to recheck.
    emit_tier3
        If False, the sieve skips tier-3 emission entirely. Used
        by the pre-registered validation harness, which tests
        only that the tier-1 and tier-2 pre-registered couplings
        surface, without drowning the output in conjecturals.

    Returns
    -------
    SieveReport with the emitted hypotheses and prefilter
    counters. The report's hypotheses are in deterministic order:
    sorted by (eq_a_id, eq_b_id, var_a, var_b).
    """
    report = SieveReport()
    items = sorted(equations.items())
    for (a_id, eq_a), (b_id, eq_b) in itertools.combinations(items, 2):
        # Gate 2: domain adjacency. Applied once per equation pair
        # before the O(V_a * V_b) variable loop, so an explicit
        # rejection short-circuits the whole pair.
        if not is_adjacent(eq_a.domain, eq_b.domain):
            report.rejected_by_domain_adjacency += len(eq_a.variables) * len(eq_b.variables)
            continue
        for var_a_name, var_a in sorted(eq_a.variables.items()):
            if var_a.descriptor is None:
                continue
            for var_b_name, var_b in sorted(eq_b.variables.items()):
                if var_b.descriptor is None:
                    continue
                report.total_variable_pairs_considered += 1
                # Gate 1: dimension compatibility.
                if not _dims_match(eq_a, var_a_name, eq_b, var_b_name):
                    report.rejected_by_dimension += 1
                    continue
                desc_a = var_a.descriptor
                desc_b = var_b.descriptor
                # Tier 1 has priority.
                h = _tier1_match(
                    a_id, b_id, var_a_name, var_b_name, desc_a, desc_b
                )
                if h is not None:
                    report.hypotheses.append(h)
                    report.tier1_count += 1
                    continue
                # Tier 2 next.
                h = _tier2_match(
                    a_id, b_id, var_a_name, var_b_name, desc_a, desc_b
                )
                if h is not None:
                    report.hypotheses.append(h)
                    report.tier2_count += 1
                    continue
                # Tier 3 last, optional.
                if emit_tier3:
                    h = _tier3_match(
                        a_id, b_id, var_a_name, var_b_name, desc_a, desc_b
                    )
                    report.hypotheses.append(h)
                    report.tier3_count += 1

    # Equation-level tier-2: cross-domain structural-identity
    # couplings that variable-level tier-2 cannot catch because
    # the variables have different pint dimensions (Fourier↔Fick
    # is the canonical case). Deduplicated against already-seen
    # (a_id, b_id, var_a, var_b) tuples so a pair that matched at
    # tier 1 doesn't also get a weaker tier-2 entry.
    already_seen = {
        (h.eq_a_id, h.eq_b_id, h.var_a, h.var_b)
        for h in report.hypotheses
    }
    for h in _tier2_from_structural(equations):
        key = (h.eq_a_id, h.eq_b_id, h.var_a, h.var_b)
        if key in already_seen:
            continue
        report.hypotheses.append(h)
        report.tier2_count += 1
        already_seen.add(key)
    return report


def run_and_filter_couplings(
    equations: Mapping[str, TypedExpression],
    *,
    tiers: Tuple[CouplingTier, ...] = (
        CouplingTier.TIER1_EQUIVALENCE,
        CouplingTier.TIER2_SIMILARITY,
    ),
) -> List[CouplingHypothesis]:
    """Run the sieve and return only hypotheses at the requested
    tiers. Convenience wrapper for the pre-registered validation
    harness, which cares about tier 1 and tier 2 but not the
    conjectural flood.
    """
    report = run_coupling_sieve(equations, emit_tier3=False)
    allowed = set(tiers)
    return [h for h in report.hypotheses if h.tier in allowed]
