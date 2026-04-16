# Pre-registered couplings — Medium milestone 2

**Status:** binding. The Layer 5 coupling sieve is considered
broken until every item in this file either matches or is
rejected as listed. Shipping m2 means "this file's pass rate is
100%"; any regression here is a hard stop.

**Authored:** Phase 10, after the design doc and the sieve
implementation. The list was fixed BEFORE running the sieve over
the full corpus so the registration is not retrofitted to the
sieve's actual output.

## Format

Each entry has:

- **ID** — short tag (`PRE-C01`, `PRE-R01` for couplings and
  rejections respectively)
- **Composite** — what physical system the coupling represents
- **Eq pair** — the two equation IDs
- **Variable pair** — the specific variable identification the
  sieve is expected to surface (when the coupling is at tier 1
  or tier 2-variable)
- **Expected tier** — Tier 1, Tier 2 (structural or variable),
  or Reject
- **Physical check** — which Phase 6 filter should fire

The harness (`cross_analysis/run_pre_registered.py`) walks this
file, runs the sieve against the corpus, and asserts that each
expected hypothesis is in the emitted set.

## Positive couplings (MUST surface)

| ID | Composite | Eq A | Eq B | Variable pair | Expected tier | Physical check |
|----|-----------|------|------|---------------|---------------|----------------|
| PRE-C01 | Simple harmonic oscillator `m·ẍ = −k·x` | EQ-NEWTON-II | EQ-HOOKE | F ↔ F_spring | Tier 1 (equivalence) | Energy conservation (SHO total energy) |
| PRE-C02 | Coupled heat-mass transport (Soret/Dufour) | EQ-FOURIER-HEAT | EQ-FICK-DIFFUSION | q ↔ J | Tier 2 (structural) | Tellegen flow-flow pairing + Onsager |
| PRE-C03 | Classical electromechanical analogy | EQ-NEWTON-II | EQ-OHM | F ↔ V | Tier 2 (structural) | Tellegen effort-effort pairing |
| PRE-C04 | Work-Energy shares inertial mass with Newton II | EQ-NEWTON-II | EQ-WORK-ENERGY | m ↔ m | Tier 1 (equivalence) | Soft (no applicable check; parameter identity) |

**Not in Medium m2 scope, deferred to m3:**

| ID | Composite | Why deferred |
|----|-----------|--------------|
| PRE-C05 | Schrödinger + Fourier via Wick rotation | Different variable counts + CoV-level substitution. Belongs to Layer 2 CoV sieve, not Layer 5. |
| PRE-C06 | Reaction-diffusion (Arrhenius + Fick) | Requires composition (adds reaction term to diffusion PDE), not variable identification. Needs a future Layer 6 composition sieve. |
| PRE-C07 | Spatial Lotka-Volterra (LV + Fick) | Same composition problem as PRE-C06. |

## Pre-registered rejections (MUST NOT surface)

| ID | Eq A | Eq B | Reason |
|----|------|------|--------|
| PRE-R01 | EQ-NEWTON-II | EQ-SHANNON-ENTROPY | No physical coupling path. Force and entropy have no shared conservation law; any "match" would be algebraic coincidence. Killed at Gate 2 (domain adjacency: classical_mechanics ↔ information_theory is explicit False). |
| PRE-R02 | EQ-BLACK-SCHOLES | EQ-LOTKA-VOLTERRA | No shared semantic descriptors. Killed at Gate 2 (quantitative_finance ↔ population_dynamics is explicit False). |
| PRE-R03 | EQ-LORENTZ-FACTOR | EQ-BAYES | Incompatible domains, no transform exists between a kinematic invariant and a probability measure. Killed at Gate 2 (special_relativity ↔ probability is explicit False). |

## Done criterion

The sieve passes Phase 10 if:

1. Every PRE-C0N in the Medium m2 scope produces a
   `CouplingHypothesis` with the expected tier and variable
   pair.
2. Every PRE-RNN produces zero hypotheses across any of its
   variable combinations.
3. The ledger-write path emits the correct outcome (PROVED,
   EMPIRICAL, REJECTED, CONJECTURAL) for each.

The harness returns a non-zero exit code on any failure and
writes the failure reason to stdout in a stable format.
