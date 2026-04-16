# Design: Coupling Sieve (Medium milestone 2)

**Status:** Phase 0 — locked in after three-model AI review board
(Claude Opus, Gemini, OpenAI). Binding on subsequent phases until
superseded by an explicit design update.

**Authorship:** Synthesis of three independent AI reports plus
project-team decisions. Key precedents cited inline.

---

## 1. Goal

Build an **AI-assisted cross-domain coupling discovery pipeline**
that proposes ranked candidate couplings between equations in the
corpus, validates them against semantic, dimensional, and physical
constraints, and records every attempt in an append-only ledger for
AI-board review.

A **coupling** is a variable identification of the form

    v_A = T(v_B)

between a variable `v_A` in equation A and a variable `v_B` in
equation B, where:

- `v_A` and `v_B` share a **compositional semantic descriptor**
  (not just a pint dimension, not just a flat tag);
- `T` is a transfer function drawn from a small explicit library;
- The composition `A ∪ B ∪ (v_A = T(v_B))` satisfies dimensional
  consistency AND at least one physical-constraint sanity check
  (conservation / Tellegen / Onsager) before being elevated to
  `PROVED`.

The sieve's output is a **review queue of candidate couplings** with
full provenance. Nothing is labeled "discovered" without AI review
board sign-off (at minimum: a Claude-Gemini-OpenAI trio vote).

## 2. Non-goals for Medium m2

Explicitly **out of scope** and deferred:

- Human-UI review interface (review happens via AI board)
- Automatic fitting of transfer function parameters from real
  observational data (we use symbolic transfer functions with
  closed-form parameters)
- Neural / learning-based coupling proposers
- Full Catlab / decorated-cospan categorical implementation
  (we adopt the mental model, not the machinery)
- Real-time numerical simulation of composite systems
- Couplings involving more than 3 equations simultaneously
- Claims of "novel scientific discovery" — all outputs are
  review candidates

## 3. Lessons from prior art (the three AI reports)

Three directly relevant prior-art clusters the board identified:

**Semantics-based model merging (physiology / systems biology).** The
SemSim / SemGen / OPB ecosystem (Gennari, Neal, Cook at U. Washington)
is the tightest prior overlap. Their documented limitation —
"recognizes semantic equivalency, not similarity" — becomes our
explicit tier-1 vs tier-2 distinction. Shahidi et al.
(PLOS Comp Bio 2021, PLOS ONE 2022) demonstrated semantics-based
bond-graph composition that enforces energy conservation during
merge; our physical-constraint filter (§8) follows their pattern.

**Compositional variable descriptors (Earth system + environmental
modeling).** CSDMS Standard Names encodes variables as
`object + quantity (+ operation)` with assumptions held in metadata
rather than in the name. The I-ADOPT framework formalizes
`{object_of_interest, property, context, constraint}` as the
interoperability primitive. Our descriptor schema (§5) is a direct
adaptation.

**Categorical composition.** Decorated cospans (Fong; Baez–Courser–
Vasilakopoulou) and operads of wiring diagrams (Vagner–Spivak–Lerman)
provide the formal "compose by variable-sharing" algebra. We adopt
it as the mental model and defer the full Catlab implementation.

**DARPA ASKE / ASKEM / SKEMA.** Demonstrated practical automation of
variable extraction from code and text (F1 ≈ 0.49-0.92 depending
on task). Relevant to Phase 2+ when we'd extract variables from
unstructured sources; not part of Medium m2 scope.

**AI Feynman / SINDy / PySR.** Equation-discovery-from-data tools
that work within a single domain. Tangentially related; not a
competitor because they don't attempt cross-domain coupling.

## 4. Architectural framing

**The sieve is an AI-assisted coupling assistant, not a coupling
oracle.** Every historical attempt at fully automated discovery of
cross-domain scientific relationships has failed or scoped down.
The sieve generates ranked candidates with explanations; an AI
review board (Claude Opus + Gemini + OpenAI o1/GPT-5) accepts or
rejects each candidate before it enters the ledger as
`REVIEW_APPROVED`. This design decision is binding.

This framing is explicitly motivated by:

- Opus's structural-impossibility warning ("every precedent
  requires a human in the loop");
- SemGen's equivalence-vs-similarity limitation pattern;
- Falkenhainer & Forbus's "assumption management becomes the
  connective tissue" historical lesson;
- The reality that even DARPA's SKEMA effort reports manual
  correction as part of the standard workflow.

## 5. Semantic descriptor schema

**Every variable in every equation carries a compositional
descriptor**, not a flat type tag. The descriptor is a structured
record with four fields; three are required, one is optional.

```yaml
variables:
  F:
    dimension: "[force]"
    unit: "newton"
    descriptor:
      object_of_interest: "rigid_body"        # REQUIRED
      property: "http://qudt.org/vocab/quantitykind/Force"  # REQUIRED, QUDT URI
      context: "inertial_frame"               # REQUIRED
      constraint: "net_external"              # OPTIONAL
    meaning: "net external force on the body's centre of mass"
```

### 5.1 Field semantics

**`object_of_interest`** — what thing has this property. Drawn from a
small controlled vocabulary of object kinds: `rigid_body`,
`point_particle`, `fluid_parcel`, `resistor`, `capacitor`,
`conductor`, `chemical_species`, `population`, `photon`,
`wavefunction`, `portfolio`, `market`, `information_channel`,
`thermodynamic_system`, `control_volume`, etc. Extensible with
explicit maintainer approval.

**`property`** — what physical/mathematical property it is. Namespace:
QUDT `QuantityKind` URIs
(`http://qudt.org/vocab/quantitykind/Force`, etc.) augmented with
project-local extensions for quantities QUDT doesn't cover
(`AxiomOfCountability`, `ProbabilityMass`, etc.). Stored as a full
URI so we inherit QUDT's `skos:broader` / `skos:narrower` hierarchy
for free — that gives us lattice subsumption for similarity
matching (§6).

**`context`** — the regime, reference frame, or model context. Drawn
from a controlled vocabulary: `inertial_frame`, `rotating_frame`,
`galilean`, `lorentz`, `non_relativistic`, `classical_limit`,
`steady_state`, `quasi_equilibrium`, `dilute`, `low_reynolds`,
`optically_thin`, `risk_neutral_measure`, etc. Context is what the
equation assumes about the world, not what type the variable is.

**`constraint`** — optional narrowing of the variable's role. Examples:
`net_external` (force), `partial_pressure`, `dimensionless_group`,
`ratio_of_extensives`, `component_flux`. When absent, no constraint.

### 5.2 Why this specific structure

- **CSDMS precedent:** object + quantity disambiguates temperature-
  of-air vs temperature-of-soil at the type level.
- **I-ADOPT precedent:** four-field compositional descriptor is the
  minimum expressive schema.
- **Assumptions out of the name:** assumptions go into `context`, not
  into longer property names. Keeps the property namespace compact
  and reuses QUDT.
- **Lattice-ready:** QUDT's `skos:broader` gives us subsumption for
  free. `InternalEnergy` is `skos:broader` `Energy`, `KineticEnergy`
  is also `skos:broader` `Energy`, so similarity matching can
  ascend the lattice.

### 5.3 Loader + validator

- `framework/descriptor.py`: `Descriptor` dataclass + `load_qudt_uris()`
  + `DescriptorRegistry` that validates every YAML's descriptor
  block against the vocabularies (object, context) and the QUDT
  ontology (property URI resolvability).
- Validation is load-time. A descriptor with an unknown
  `object_of_interest` or an unresolvable `property` URI fails the
  equation's load. **No silent fallback to "generic".**
- QUDT ingestion: bootstrap from `https://qudt.org/2.1/vocab/quantitykind`
  as a one-time download into `labs_v2/framework/vendor/qudt_quantitykinds.ttl`.
  Parse with `rdflib`. Cache in-process.

## 6. Coupling tiers

Couplings enter the ledger under one of three tiers:

### Tier 1 — Equivalence (strong)

- Same `property` URI (exact match, not subsumption)
- Same `object_of_interest` category
- Compatible `context` (either identical or one is
  `skos:broader` the other in the context lattice)
- Identical pint dimension
- Transfer function = `identity`

A tier-1 match means "these two variables are the same thing in
both equations". Feed them together, the composite is
dimensionally and semantically sound by construction. **All
pre-registered couplings should land here or fail the sieve.**

### Tier 2 — Similarity (with transfer function)

- Properties are siblings or lattice-neighbors under `skos:broader`
  (same parent in the QUDT lattice, distance ≤ 2)
- Compatible dimensions (possibly after applying T)
- Transfer function T from the library (§7) is non-trivial
- Physical-constraint filter (§8) passes

A tier-2 match is "these are related but not identical and require
a transform". E.g., `KineticEnergy` ↔ `ThermalEnergy` under the
equipartition transform for an ideal gas.

### Tier 3 — Conjectural (AI review board required)

- Dimensions compatible, but semantic descriptors are unrelated or
  weakly related (lattice distance > 2)
- No transfer function in the library applies cleanly
- Physical-constraint filter does not apply (no energy interpretation)

Tier-3 matches are conjectural by default and **never promoted
past `CONJECTURAL` without explicit AI review board approval**.
Review outcome is recorded in the ledger.

## 7. Transfer function library

Six functions in the v1 library. Each is a sympy expression
template with a small number of parameters:

| Name | Template | When to try | Parameters |
|---|---|---|---|
| `identity` | `y = x` | Always (tier 1) | — |
| `scale` | `y = k·x` | Dimension match, magnitude offset | `k` |
| `first_order_lag` | `y = x / (1 + τs)` in Laplace, or `τ·dy/dt + y = x` in time | Flow-from-effort couplings (RC, heat, viscous) | `τ` |
| `exponential_decay` | `y(t) = x·exp(−λt)` | Dynamic coupling, decay | `λ` |
| `power_law` | `y = k·xⁿ` | Allometric / scaling couplings | `k, n` |
| `logistic` | `y = K / (1 + exp(−r(x−x₀)))` | Saturation couplings (bio, utility) | `K, r, x₀` |

Library is extensible. Each entry is a `TransferFunction` dataclass
in `framework/couplings.py` with a sympy template, a parameter
schema, and a `try_fit(v_a_expr, v_b_expr)` method that attempts to
solve for the parameters given the two symbolic expressions.

## 8. Physical-constraint filter (post-filter)

Before any tier-1 or tier-2 coupling can be promoted past
`EMPIRICAL`, the candidate composite system must pass at least one
of three physical-plausibility checks:

### 8.1 Conservation check

For each coupled system, attempt to find a conserved quantity
`Q(state, params)` such that `dQ/dt = 0` under the coupled ODE.
Mechanism: linearize the coupled system around its fixed point,
compute the Jacobian, check for zero-eigenvalue directions that
correspond to conservation laws. Sympy-powered.

### 8.2 Tellegen-style effort-flow invariant

If both coupled variables can be classified as `effort` or `flow`
in the bond-graph sense, verify that
`Σ (effort × flow) = 0` across the coupling interface. Effort/flow
tags are derived from the descriptor's `property` field via a
lookup table. This is the Shahidi et al. (2021) pattern for
semantics-based bond-graph composition.

### 8.3 Onsager reciprocal check

For transport couplings (fluxes linear in gradients), verify that
the cross-coupling coefficient matrix is symmetric:
`L_ij = L_ji`. This is the classical test for thermodynamic
plausibility of a linear transport coupling.

A candidate passing at least one of these three checks is
**physically consistent**. A candidate passing none stays at
`EMPIRICAL` pending AI review board vote.

## 9. Emergent properties analysis

For every tier-1 or tier-2 coupling that passes the physical filter,
the sieve computes four emergent properties and records them in the
ledger:

### 9.1 Symbolic steady state

Solve `d/dt(state) = 0` for fixed points of the coupled ODE.
Sympy `solve()` with fallback to numerical `scipy.optimize.fsolve`.
Fixed points are recorded as ledger evidence.

### 9.2 Linear stability at each fixed point

Compute the Jacobian of the coupled ODE at the fixed point, extract
eigenvalues, classify (stable / unstable / saddle / center /
Hopf-like). Sympy for the Jacobian; numpy for eigenvalues.

### 9.3 Buckingham Π on the coupled parameter list

Collect the union of all parameters from the two coupled equations,
compute pint dimensions, find the dimension matrix nullspace, and
emit the resulting dimensionless groups. **New groups** — groups
that don't appear in either single equation's Π-signature — are
flagged as `emergent_dimensionless_group` in the ledger. This is
the "genuine new insight" path: if a coupled system has a Π group
no single equation produces, that's a substantive discovery
candidate (pending review).

### 9.4 Conserved quantities

Attempt to find all Q(state, params) with dQ/dt = 0, beyond the
one required by the physical filter. Record all.

The sieve never claims "new insight" unless at least one of §9.3
or §9.4 produces a non-trivial output the single equations don't.

## 10. Two-gate prefilter (combinatorial explosion mitigation)

Before any variable-pair enumeration or tier analysis:

### Gate 1 — Dimensional compatibility

For every pair (v_A, v_B), check pint dimension equality (or
equivalence under the transfer function's expected dimension
change). Rejects ~70-80% of pairs.

### Gate 2 — Domain adjacency

An explicit `framework/domain_adjacency.py` matrix declares which
domain pairs can interact:

```python
ADJACENCY = {
    ("classical_mechanics", "electrical_circuits"): True,   # Newton ↔ Ohm
    ("thermal_transport", "mass_transport"):         True,   # Fourier ↔ Fick
    ("quantum_mechanics", "thermal_transport"):      True,   # Wick rotation
    ("population_dynamics", "classical_mechanics"):  False,  # no coupling path
    ("quantitative_finance", "soil_mechanics"):      False,  # implausible
    ...
}
```

When in doubt, default is `True` (allow) — we prefer false positives
that get filtered by later stages over false negatives that
silently kill a real coupling. The matrix is explicit so the
absence of a pair is reviewable.

The two gates together typically reduce the candidate space by
80-90% before semantic matching runs. Pigeonhole calculation: at
N=50 equations with ~10 variables each and 6 transfer functions,
raw candidate count is ~750k; two-gate prefilter brings it to
~75-150k, which is tractable.

## 11. Ledger schema v4

Schema version bumps to 4. New `Hypothesis.kind` values:

- `tier1_coupling` — equivalence-level coupling
- `tier2_coupling` — similarity-level coupling with transform
- `tier3_conjectural` — dimensionally-compatible but semantically
  weak

New `Hypothesis.substitution` field type for couplings:

```python
{
    "v_a": {"equation": "EQ-NEWTON-II", "variable": "F"},
    "v_b": {"equation": "EQ-HOOKE",     "variable": "F_spring"},
    "transfer_function": "identity",   # or "scale", "first_order_lag", etc.
    "transfer_params": {},             # or {"k": ...}
    "lattice_distance": 0,             # 0 for exact equivalence
}
```

New `Hypothesis.evidence` fields for couplings:

- `descriptor_match`: the shared descriptor fields
- `physical_constraint_check`: which filter (conservation / Tellegen /
  Onsager) passed, and the evidence
- `emergent_properties`: {steady_states, stability, pi_groups,
  conserved_quantities}
- `ai_review`: {reviewer_model, vote, reasoning, timestamp} per
  review board member

Schema migration from v3: old v3 records stay loadable, old
`structural_rename` and `change_of_variables` kinds continue to work.

## 12. AI review board

Every coupling promoted past `CONJECTURAL` requires a vote from
the AI review board. The review board is a multi-model protocol
implemented as a single module
`framework/ai_review_board.py`.

### 12.1 Board members

- Claude Opus (primary — most structurally critical reviewer based on
  Phase 0 report behavior)
- OpenAI GPT-5 / o3 (strongest on prior-art recall)
- Gemini 2.5 Pro (strongest on combinatorial-failure prediction)

Each gets the same prompt template for every candidate:

> "You are reviewing a proposed cross-domain coupling between
> equation A and equation B. The coupling is [tier], via transfer
> function [T]. The compositional descriptors are [...]. The
> physical-constraint filter [passed/failed] with evidence [...].
> Emergent properties found: [...]. Do you approve this coupling
> for the project ledger? Reply with a structured verdict: APPROVE /
> REJECT / NEEDS_MORE_INFO, a one-paragraph reason, and any
> specific concerns."

### 12.2 Voting rules

- **Unanimous APPROVE** → promote to `PROVED`
- **2 APPROVE + 1 NEEDS_MORE_INFO** → promote to `EMPIRICAL`,
  flag for follow-up
- **Any REJECT** → demote to `CONJECTURAL` and log the rejector's
  reasoning as the rejection criterion
- **Any 2-of-3 REJECT** → full rejection, coupling does not enter
  further analysis

### 12.3 API key handling

Keys provided by the user at board-invocation time via a shell
command the user runs. The module never persists keys to disk.
If keys are not provided, the board operation raises a structured
`AIBoardKeysMissing` error and the candidate stays at
`CONJECTURAL`.

### 12.4 Logging

Every vote is recorded in the ledger as part of the Hypothesis's
`ai_review` evidence field. Rejected votes include the rejecting
model's reasoning verbatim. Append-only.

## 13. Module layout

```
labs_v2/framework/
├── descriptor.py            (NEW)   I-ADOPT compositional descriptors
├── qudt_loader.py           (NEW)   QUDT vocabulary ingestion
├── couplings.py             (NEW)   CouplingHypothesis type,
│                                    TransferFunction library
├── domain_adjacency.py      (NEW)   explicit domain pair matrix
├── physical_constraints.py  (NEW)   Tellegen / Onsager / conservation
├── emergent_analysis.py     (NEW)   steady state, stability, Π groups,
│                                    conserved quantities
├── layer5_coupling_sieve.py (NEW)   the sieve itself
├── ai_review_board.py       (NEW)   multi-model voting protocol
├── vendor/
│   └── qudt_quantitykinds.ttl  (NEW)  cached QUDT ontology
└── run_discovery.py         (UPDATE) add Layer 5 invocation
```

## 14. Pre-registered test couplings

Before the sieve is trusted on any novel coupling, it must
rediscover this set. Pre-registration is binding and recorded
in `labs_v2/cross_analysis/PRE_REGISTERED_COUPLINGS.md`.

| # | Coupling | Composite system | Expected tier | Physical check |
|---|---|---|---|---|
| 1 | EQ-NEWTON-II + EQ-HOOKE | Simple harmonic oscillator `m·ẍ = −k·x` | Tier 1 | Conservation: total energy |
| 2 | EQ-FOURIER-HEAT + EQ-FICK-DIFFUSION | Coupled heat-mass transport (Soret/Dufour regime) | Tier 2 | Onsager reciprocity |
| 3 | EQ-ARRHENIUS + EQ-FICK-DIFFUSION | Reaction-diffusion (pattern formation precursor) | Tier 2 | Conservation: species |
| 4 | EQ-LOTKA-VOLTERRA + EQ-FICK-DIFFUSION | Spatial predator-prey | Tier 2 | Conservation: total population |
| 5 | EQ-SCHRODINGER + EQ-FOURIER-HEAT (via Wick) | Imaginary-time QM ≡ heat diffusion | Tier 2 | Wick rotation as transfer |

Failure of any pre-registered test means the sieve is broken and
Medium m2 does not ship until it passes. The sieve is never
trusted on a novel coupling before all five pass.

Additional known failure cases (must reject, not accept):

| # | Rejection target | Reason |
|---|---|---|
| A | EQ-NEWTON-II + EQ-SHANNON-ENTROPY | No physical coupling path exists |
| B | EQ-BLACK-SCHOLES + EQ-LOTKA-VOLTERRA | No shared semantic descriptors |
| C | EQ-LORENTZ-FACTOR + EQ-BAYES | Incompatible domains / no transform |

## 15. Failure modes → mitigations

| Risk | AI board consensus | Mitigation |
|---|---|---|
| Flat semantic types → polysemy/synonymy/context-blindness | All 3 | Compositional descriptor §5 |
| Combinatorial explosion at N≥50 | Gemini | Two-gate prefilter §10 |
| False-positive couplings | All 3 | Physical constraint filter §8 + AI review board §12 |
| Semantic drift across corpus versions | OpenAI | QUDT as anchor + version-pinned `DescriptorRegistry` |
| Structural impossibility of full automation | Opus | Assistant framing §4 + AI review board §12 |
| Transfer function library bit-rot | All 3 | Each entry has a parameter schema + unit test |
| Equivalence-vs-similarity confusion (SemGen lesson) | OpenAI | Explicit tier-1 vs tier-2 distinction §6 |
| Assumption/context mismatch (Falkenhainer-Forbus) | OpenAI | `context` field in descriptor §5 |

## 16. Execution phases (binding order)

Phase 1 — Descriptor schema + QUDT loader + validator. **Start point.**
Phase 2 — Migrate all 15 existing equation YAMLs to the new schema.
Phase 3 — Add EQ-HOOKE (16th equation) authored in the new schema.
Phase 4 — `framework/couplings.py`: types + transfer function library.
Phase 5 — `framework/layer5_coupling_sieve.py`: two-gate prefilter +
           tier-1 matcher + tier-2 matcher.
Phase 6 — `framework/physical_constraints.py`: conservation +
           Tellegen + Onsager.
Phase 7 — `framework/emergent_analysis.py`: steady state + stability
           + Buckingham Π + conserved quantities.
Phase 8 — Ledger schema v4 + migration from v3.
Phase 9 — `framework/ai_review_board.py`: multi-model voting stub.
Phase 10 — Wire into `run_discovery.py` + run pre-registered
           validation tests (§14).
Phase 11 — AI review board pass on the whole Medium m2 state.

Each phase has a git tag for rollback. Each phase's deliverable
must execute cleanly before the next phase starts.

## 17. Rollback strategy

If any phase fails:

1. Revert to the previous phase's git tag
2. Document the failure in `cross_analysis/MEDIUM_M2_FAILURES.md`
3. Revise this design doc with the lesson
4. Restart the phase with the revised design

The existing Medium m1 state (15 equations, Layer 2-3 sieves, CoV
sieve) is **not touched** by Medium m2 — the coupling sieve is
Layer 5, parallel to the existing sieves. Rollback to M1 is always
available.

## 18. Definition of "done" for Medium m2

1. All 16 equations load with compositional descriptors validated
   against QUDT
2. All 16 notebooks execute cleanly (16/16)
3. All 5 pre-registered couplings found at their expected tier
4. All 3 pre-registered rejections correctly rejected
5. Zero false positives in the ledger after the AI review board
   pass
6. Emergent Buckingham Π analysis produces at least one
   non-trivial new dimensionless group on the pre-registered
   coupling set
7. AI review board votes recorded for every `PROVED` and
   `EMPIRICAL` coupling

## 19. Open questions (re-raise during execution if they bite)

- **Context lattice** — do we need a formal `skos:broader` hierarchy
  for `context` values, or is exact-match enough? Start with
  exact-match, upgrade if tier-1 fails on obvious matches.
- **Transfer function composition** — can T₁ ∘ T₂ be tried
  automatically? Not in Medium m2; defer to m3.
- **N-ary couplings (N > 2)** — Medium m3 or later; not in m2 scope.
- **Emergent-properties false positives** — if Buckingham Π
  produces 5+ new dimensionless groups per coupling, most will be
  trivial reorderings. Need a canonicalization step.

---

**This design is locked.** Phase 1 starts immediately after user
approval of the doc. No further scope questions until Phase 1
deliverable is ready for review.
