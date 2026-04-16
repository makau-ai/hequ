# labs_v2 — hequ Small-scope reference and discovery engine

Small scope is **complete**. This document is the single entry point
for running, extending, and migrating the v2 artefact.

## What v2 is

A domain-by-domain reference of 10 canonical equations drawn from
physics, electrical engineering, thermal transport, chemistry,
biochemistry, information theory, probability, spectroscopy,
chemical kinetics, and quantitative finance. Each equation is:

1. **Typed** — every variable carries a pint SI dimension and an
   explicit meaning. Lexical collisions between disciplines (e.g.,
   Newton's `r` vs. a growth-rate `r`) are impossible at the type
   level.
2. **Canonicalised** — represented as an implicit `lhs = 0` sympy
   expression so the Layer 2 sieves can compare apples to apples
   across domains.
3. **Executed in a notebook** — real lab data (where available) or
   plausible reference measurements (with citations) drive a
   **correct worked example** that produces a zero residual.
4. **Broken in a notebook** — an **incorrect worked example** pushes
   at least one of the declared assumptions and produces a
   non-zero residual, proving the canonical form discriminates.
5. **Drafted in Lean 4** — a `lean/stub.lean` file carries the
   theorem statement in mathlib-compatible syntax as a migration
   target for future formal certification.
6. **Consumed by a discovery pipeline** — Layers 2 and 3 sieve for
   cross-domain structural identities and log every hypothesis in
   an append-only JSONL ledger.

## The ten equations

| Domain | EQ-id | Canonical form |
|---|---|---|
| classical_mechanics | EQ-NEWTON-II | `F - m·a = 0` |
| classical_mechanics | EQ-WORK-ENERGY | `W - ½m(v_f² - v_i²) = 0` |
| electrical_circuits | EQ-OHM | `V - I·R = 0` |
| thermal_transport | EQ-FOURIER-HEAT | `q + k·dT_dx = 0` |
| mass_transport | EQ-FICK-DIFFUSION | `J + D·dC_dx = 0` |
| information_theory | EQ-SHANNON-ENTROPY | `H + p·log p + (1-p)·log(1-p) = 0` |
| probability | EQ-BAYES | `P(A\|B)·P(B) - P(B\|A)·P(A) = 0` |
| spectroscopy | EQ-BEER-LAMBERT | `A - ε·ℓ·c = 0` |
| chemical_kinetics | EQ-ARRHENIUS | `k_rate - A·exp(-Ea/(RT)) = 0` |
| quantitative_finance | EQ-BLACK-SCHOLES | `V_t + ½σ²S²V_SS + rSV_S - rV = 0` |

## Pipeline status (latest run)

- **Lab build:** 10 / 10 notebooks execute cleanly in the v2
  container.
- **Layer 2 dimensional sieve:** 0 candidate pairs (the 10 equations
  live in 10 different dimensional regimes — correct).
- **Layer 2 structural sieve (dimension-blind):** 2 candidate pairs.
- **Layer 3 verification:** both candidates pass symbolic and
  numerical checks, recorded as `PROVED` in the ledger.

### Pre-registered expectations

| Expectation | Result |
|---|---|
| Fourier's heat law ≡ Fick's first law under σ = {q↔J, k↔D, dT/dx↔dC/dx} | **✅ FOUND** |
| Newton II ≡ Ohm's law under σ = {F↔V, m↔R, a↔I} | **✅ FOUND** |
| Black–Scholes ≡ heat equation under change of variables | ❌ not found (expected; requires Medium-scope substitution sieve) |

2 / 3 pre-registered expectations found; the third is a documented
limitation of the dimension-blind rename sieve, not a bug.

## Running the pipeline

### Build the container

```bash
cd /Users/matthewluallen/hequ
docker build -t hequ-labs:v2 .
```

The v2 image layers on `quay.io/jupyter/scipy-notebook` plus
`icontract`, `hypothesis`, `jupytext`, `networkx`, **`pint==0.24.4`**,
**`pyyaml==6.0.2`**.

### Execute every notebook

```bash
docker run --rm -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:v2 bash -lc \
    "cd /home/jovyan/work && PYTHONPATH=labs_v2 python labs_v2/framework/build_notebooks.py"
```

Writes executed `.ipynb` files to `labs_v2/notebooks_out/` and exits
non-zero if any lab failed.

### Run the discovery pipeline

```bash
docker run --rm -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:v2 bash -lc \
    "cd /home/jovyan/work && PYTHONPATH=labs_v2 python labs_v2/framework/run_discovery.py"
```

Writes `cross_analysis/DISCOVERY.md` (human report) and appends to
`cross_analysis/discovery_ledger.jsonl`.

## Extending

Adding an 11th equation is a five-file task:

1. `labs_v2/equations/<domain>/<EQ-id>/equation.yaml` — canonical
   form, variables with pint units, assumptions, derivation notes.
2. `labs_v2/equations/<domain>/<EQ-id>/notebook.py` — jupytext
   percent-format with correct-example and incorrect-example cells.
3. `labs_v2/equations/<domain>/<EQ-id>/lean/stub.lean` — theorem
   statement as a migration artefact (not compiled).
4. Re-run `build_notebooks.py` to verify the lab executes.
5. Re-run `run_discovery.py` to see if the new equation participates
   in any candidate pairs.

No Python code needs to change.

## Layer 4 status

Lean 4 certification is **drafted but not compiled**. Each
`stub.lean` file contains a theorem statement in mathlib-compatible
syntax with imports of the relevant mathlib modules. A future
Medium scope would install the Lean toolchain in the container and
verify each stub against mathlib.

## Known limitations (honest list)

1. **No change-of-variables substitution sieve.** Black–Scholes ↔
   heat equation requires `x = log S`, which is a substitution, not
   a rename. The structural sieve only does variable permutations.
2. **No compiled Lean proofs.** The stubs are drafts. Compilation
   needs a Lean 4 toolchain installed in the container.
3. **Synthetic lab data for some equations.** Newton II and Ohm use
   genuinely published data; Beer-Lambert uses a real reference ε;
   some of the others (Fourier copper bar, Fick sucrose membrane)
   use textbook values. Black-Scholes uses an analytical
   closed-form solution rather than market data.
4. **Corpus size.** Only 10 equations. This is intentional (Small
   scope) — Medium would scale to ~30.
