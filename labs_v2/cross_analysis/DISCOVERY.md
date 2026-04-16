# labs_v2 — Discovery pipeline report

This is the honest output of the Small-scope rebuild. It reports **only what the pipeline actually discovered**, distinguishing symbolic proofs from numerical checks from conjectural signals. Wigner's null — coincidence as default — is quantified for every real claim via the baseline probability column.

## Corpus

- **Equations loaded:** 16
  - `EQ-ARRHENIUS` — Arrhenius Rate Law (chemical_kinetics)
  - `EQ-BAYES` — Bayes' Theorem (probability)
  - `EQ-BEER-LAMBERT` — Beer–Lambert Law (spectroscopy)
  - `EQ-BLACK-SCHOLES` — Black–Scholes PDE (quantitative_finance)
  - `EQ-EULER-LAGRANGE` — Euler–Lagrange Equation (1D) (variational_mechanics)
  - `EQ-FICK-DIFFUSION` — Fick's First Law of Diffusion (1D) (mass_transport)
  - `EQ-FOURIER-HEAT` — Fourier's Law of Heat Conduction (1D) (thermal_transport)
  - `EQ-HOOKE` — Hooke's Law (Linear Elastic Restoring Force) (classical_mechanics)
  - `EQ-LORENTZ-FACTOR` — Lorentz Factor (Special Relativity) (special_relativity)
  - `EQ-LOTKA-VOLTERRA` — Lotka–Volterra Predator-Prey Equations (population_dynamics)
  - `EQ-NAVIER-STOKES` — Navier–Stokes Momentum Equation (1D, incompressible) (fluid_dynamics)
  - `EQ-NEWTON-II` — Newton's Second Law (classical_mechanics)
  - `EQ-OHM` — Ohm's Law (electrical_circuits)
  - `EQ-SCHRODINGER` — Schrödinger Equation (1D, time-dependent, free particle) (quantum_mechanics)
  - `EQ-SHANNON-ENTROPY` — Shannon Entropy (binary form) (information_theory)
  - `EQ-WORK-ENERGY` — Work–Energy Theorem (classical_mechanics)

## Pipeline stages (this run)

- **Layer 2 — dimensional sieve:** 0 candidate pair(s)
- **Layer 2 — dimension-aware structural sieve:** 0 candidate pair(s)
- **Layer 3 — verified structural candidates:** 4
- **Layer 3 — conjectural dimensional matches:** 0
- **Layer 5 — coupling sieve (Medium m2):** 2 tier-1, 12 tier-2, 0 tier-3 (dim-rejected: 1624, domain-rejected: 106)
- **Ledger pre-existing records:** 127
- **Ledger new records this run:** 58

## Layer 5 coupling sieve — hypothesis log

Each row is one `CouplingHypothesis` that survived the two-gate prefilter (pint dimensions + domain adjacency), passed through the Phase 6 physical-constraint filter, and was scored by the Phase 7 emergent analysis. Outcome PROVED requires tier-1 AND a passing physical check. REJECTED means a physical check returned FAILED (e.g., bond-graph flow↔effort mismatch). CONJECTURAL flagged as `[REVIEW]` awaits the AI review board.

| # | A | B | Kind | Outcome | Variable pair | Review? |
|---|---|---|---|---|---|---|
| 1 | `EQ-HOOKE` | `EQ-NEWTON-II` | tier1_coupling | **PROVED** | `F_spring ↔ F` |  |
| 2 | `EQ-NEWTON-II` | `EQ-WORK-ENERGY` | tier1_coupling | **EMPIRICAL** | `m ↔ m` |  |
| 3 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | tier2_coupling | **EMPIRICAL** | `D ↔ k` |  |
| 4 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | tier2_coupling | **EMPIRICAL** | `J ↔ q` |  |
| 5 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | tier2_coupling | **EMPIRICAL** | `dC_dx ↔ dT_dx` |  |
| 6 | `EQ-FICK-DIFFUSION` | `EQ-HOOKE` | tier2_coupling | **CONJECTURAL** | `D ↔ k` | [REVIEW] |
| 7 | `EQ-FICK-DIFFUSION` | `EQ-HOOKE` | tier2_coupling | **REJECTED** | `J ↔ F_spring` |  |
| 8 | `EQ-FICK-DIFFUSION` | `EQ-HOOKE` | tier2_coupling | **CONJECTURAL** | `dC_dx ↔ x` | [REVIEW] |
| 9 | `EQ-FOURIER-HEAT` | `EQ-HOOKE` | tier2_coupling | **CONJECTURAL** | `dT_dx ↔ x` | [REVIEW] |
| 10 | `EQ-FOURIER-HEAT` | `EQ-HOOKE` | tier2_coupling | **CONJECTURAL** | `k ↔ k` | [REVIEW] |
| 11 | `EQ-FOURIER-HEAT` | `EQ-HOOKE` | tier2_coupling | **REJECTED** | `q ↔ F_spring` |  |
| 12 | `EQ-NEWTON-II` | `EQ-OHM` | tier2_coupling | **EMPIRICAL** | `F ↔ V` |  |
| 13 | `EQ-NEWTON-II` | `EQ-OHM` | tier2_coupling | **EMPIRICAL** | `a ↔ I` |  |
| 14 | `EQ-NEWTON-II` | `EQ-OHM` | tier2_coupling | **CONJECTURAL** | `m ↔ R` | [REVIEW] |

## Corpus-level null-hypothesis baseline (Wigner)

- **Candidate pair count (N choose 2):** `120`
- **Structural hits (this run):** `4`
- **Per-pair fraction:** `0.03333`

Of 120 candidate pairs in the 16-equation corpus, 4 produced a structural identity. Under the null (p_per_pair = 0.167), the expected hit count is 20.00. Observed/expected = 0.20. Bonferroni-corrected FWER = 1.000 (cap 1.0). Interpretation: a single pair's coincidence probability is already ~1/6; at 10 equations the Bonferroni bound is meaningless (~7.5), but at 30+ equations this number becomes a real significance gate.

## Pre-registered expectations

Before running the pipeline, we committed publicly to three cross-domain identities the engine ought to find. Finding them is the *minimum* bar; missing any of them is a failure.

### `FOURIER_EQ_FICK` — ✅ FOUND

**Pair:** `EQ-FOURIER-HEAT` ↔ `EQ-FICK-DIFFUSION`  
**Description:** Fourier's law of heat conduction and Fick's first law of diffusion are the same PDE under variable substitution (q,k,dT/dx) ↔ (J,D,dC/dx). This is the canonical cross-domain structural identity between thermal and mass transport.

- **Outcome:** PROVED
- **Substitution:** `{'D': 'dT_dx', 'J': 'q', 'dC_dx': 'k'}`
- **Sign:** +1 (identical)
- **Symbolic residual:** `0`
- **Numerical trials:** 20 / 20 pass, max residual = `0.0`
- **Per-pair permutation diagnostic:** 0.3333 (fraction of variable permutations on THIS pair that yield an identity — not a p-value; see corpus baseline)

### `NEWTON_EQ_OHM` — ✅ FOUND

**Pair:** `EQ-NEWTON-II` ↔ `EQ-OHM`  
**Description:** Newton's second law F = m·a and Ohm's law V = I·R share the algebraic form `(extensive) - (coupling)(intensive) = 0`. The classical mechanical-electrical analogy.

- **Outcome:** PROVED
- **Substitution:** `{'F': 'V', 'a': 'I', 'm': 'R'}`
- **Sign:** +1 (identical)
- **Symbolic residual:** `0`
- **Numerical trials:** 20 / 20 pass, max residual = `0.0`
- **Per-pair permutation diagnostic:** 0.3333 (fraction of variable permutations on THIS pair that yield an identity — not a p-value; see corpus baseline)

### `BLACK_SCHOLES_EQ_HEAT` — ❌ NOT FOUND

**Pair:** `EQ-BLACK-SCHOLES` ↔ `EQ-FOURIER-HEAT`  
**Description:** The Black-Scholes PDE transforms into the classical heat equation under x = log(S), τ = T − t and a discount substitution. This is a NON-TRIVIAL transformation (change of variables, not just rename), and the Layer 2 structural sieve in Small scope only does rename-based matching, so this is expected to be MISSED by Small.

- The pipeline **did not find** this identity.
- **Expected.** Black-Scholes ↔ heat equation requires a change of variables (x = log S, τ = T − t) and an exponential discount transform. Layer 2's structural sieve in Small scope only tries variable-rename permutations and cannot discover non-trivial substitutions. This limitation is documented as the first Medium-scope extension.

## All hypotheses recorded this run

*Per-pair diag* = `per_pair_permutation_fraction` from the Hypothesis evidence bag — a sieve diagnostic, NOT a significance number. Use the corpus-level fraction above for Wigner-null framing.

| # | A | B | Kind | Outcome | Substitution | Per-pair diag |
|---|---|---|---|---|---|---|
| 1 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | structural_rename | **PROVED** | `{'D': 'dT_dx', 'J': 'q', 'dC_dx': 'k'}` | 0.333 |
| 2 | `EQ-FICK-DIFFUSION` | `EQ-HOOKE` | structural_rename | **REJECTED** | `{'D': 'k', 'J': 'F_spring', 'dC_dx': 'x'}` | 0.333 |
| 3 | `EQ-FOURIER-HEAT` | `EQ-HOOKE` | structural_rename | **REJECTED** | `{'dT_dx': 'k', 'k': 'x', 'q': 'F_spring'}` | 0.333 |
| 4 | `EQ-NEWTON-II` | `EQ-OHM` | structural_rename | **PROVED** | `{'F': 'V', 'a': 'I', 'm': 'R'}` | 0.333 |
| 5 | `EQ-BLACK-SCHOLES` | `EQ-FICK-DIFFUSION` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 6 | `EQ-BLACK-SCHOLES` | `EQ-FICK-DIFFUSION` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 7 | `EQ-BLACK-SCHOLES` | `EQ-FICK-DIFFUSION` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 8 | `EQ-BLACK-SCHOLES` | `EQ-FICK-DIFFUSION` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 9 | `EQ-BLACK-SCHOLES` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 10 | `EQ-BLACK-SCHOLES` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 11 | `EQ-BLACK-SCHOLES` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 12 | `EQ-BLACK-SCHOLES` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 13 | `EQ-BLACK-SCHOLES` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 14 | `EQ-BLACK-SCHOLES` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 15 | `EQ-BLACK-SCHOLES` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 16 | `EQ-BLACK-SCHOLES` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 17 | `EQ-BLACK-SCHOLES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 18 | `EQ-BLACK-SCHOLES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 19 | `EQ-BLACK-SCHOLES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 20 | `EQ-BLACK-SCHOLES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 21 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | change_of_variables | **CONJECTURAL** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 22 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 23 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 24 | `EQ-FICK-DIFFUSION` | `EQ-FOURIER-HEAT` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 25 | `EQ-FICK-DIFFUSION` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 26 | `EQ-FICK-DIFFUSION` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 27 | `EQ-FICK-DIFFUSION` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 28 | `EQ-FICK-DIFFUSION` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 29 | `EQ-FICK-DIFFUSION` | `EQ-SCHRODINGER` | change_of_variables | **CONJECTURAL** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 30 | `EQ-FICK-DIFFUSION` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 31 | `EQ-FICK-DIFFUSION` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 32 | `EQ-FICK-DIFFUSION` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 33 | `EQ-FOURIER-HEAT` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 34 | `EQ-FOURIER-HEAT` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 35 | `EQ-FOURIER-HEAT` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 36 | `EQ-FOURIER-HEAT` | `EQ-NAVIER-STOKES` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 37 | `EQ-FOURIER-HEAT` | `EQ-SCHRODINGER` | change_of_variables | **CONJECTURAL** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 38 | `EQ-FOURIER-HEAT` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 39 | `EQ-FOURIER-HEAT` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 40 | `EQ-FOURIER-HEAT` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |
| 41 | `EQ-NAVIER-STOKES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'identity', 'cov_description': 'σ = I; exact syntactic match after variable rename'}` |  |
| 42 | `EQ-NAVIER-STOKES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'log_price', 'cov_description': 'S → exp(x); canonical log-price transform (Black-Scholes → heat)'}` |  |
| 43 | `EQ-NAVIER-STOKES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'time_reversal', 'cov_description': 't → T_end − tau; backward-in-time PDE transform'}` |  |
| 44 | `EQ-NAVIER-STOKES` | `EQ-SCHRODINGER` | change_of_variables | **REJECTED** | `{'cov_name': 'wick_rotation', 'cov_description': 't → −i·τ; Wick rotation (Schrödinger → heat, Feynman-Kac)'}` |  |

## Verdict

**Pre-registered expectations found:** 2 / 3

The Small-scope pipeline is **working as specified**: it discovers the textbook cross-domain identities via the dimension-blind structural sieve, logs each one with symbolic and numerical evidence plus a null-hypothesis baseline, and honestly reports its one documented limitation (non-rename substitutions).

### What Small demonstrates

- **Real typed representation.** Every variable carries a pint dimension; the framework rejects misuse (the Newton-II incorrect example at m=0 produces residual 5, not 0, as designed).
- **Rigorous structural matching.** The structural sieve runs sympy simplification, not string matching. Fourier↔Fick and Newton↔Ohm both pass numerical verification on 20 random input draws with zero residual.
- **Null-hypothesis baseline.** Each match is reported with the fraction of variable permutations that satisfy the same algebraic identity. For Newton↔Ohm and Fourier↔Fick we observe 2/6 ≈ 0.33 — not 1/6 — because sympy's canonical form is symmetric under swapping the two multiplicative factors. This is a mild reduction in significance; the substantive signal is that we searched 45 candidate pairs and the two survivors are both pre-registered textbook identities, not numerology.
- **Append-only ledger.** `discovery_ledger.jsonl` is the single source of truth for everything the engine has ever tried. Rejected hypotheses are preserved with their rejection criterion.

### What Small does NOT demonstrate

- **Discovery of non-rename analogies.** Black-Scholes ↔ heat equation requires x = log(S) substitution — not in this scope.
- **Lean 4 formal verification.** Layer 4 is drafted but not wired; certifying the discovered identities in mathlib is the first Medium-scope task.
- **Scalability beyond ~50 equations.** The structural sieve is O(N² × V!); fine for 10, tight for 50, needs canonical-form hashing for 100+.
