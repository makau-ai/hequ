# Migration guide — moving this project off Docker / Jupyter

This document exists because you asked for it up front: *"document in
detail so that we can also migrate this to another platform once we
get this test case done."* The pilot is complete and all 3 labs
execute cleanly. This is the runbook for moving the project out of
its current Docker + Jupyter home.

## Architectural design notes that make migration cheap

Every design decision in the framework was made with migration in
mind. A short inventory:

1. **The `framework/` package has no Jupyter dependency.** Every
   module in `labs/framework/` imports only from the standard
   library, `numpy`, `scipy`, `sympy`, `icontract`, and `hypothesis`.
   `build_notebooks.py` is the single file that imports `jupytext`
   and `nbclient`; drop it and the framework still works.

2. **Labs are jupytext percent-format `.py` files.** These are
   plain Python scripts with `# %%` and `# %% [markdown]` cell
   markers. They run top-to-bottom under any Python 3.10+
   interpreter without jupytext installed (the cell markers are
   just comments). Convert to `.ipynb`, `.qmd`, or `.md` on
   demand; nothing is locked to the notebook format.

3. **No state leaks between cells.** Each lab re-imports its
   dependencies at the top and does not rely on the Jupyter kernel's
   persistent namespace. You can run any lab as `python
   labs/physics/EQ_0001_newtons_second_law.py` directly.

4. **Triples are plain dataclasses.** `HoareTriple` has no
   notebook-specific representation. The `verify` / `verified`
   surface is a pure-Python API and ports unchanged to any runtime.

5. **The equation corpus is a single JSON file.** `taxonomy.py`
   is the only module that touches it, via the `HEQU_INVENTORY`
   environment variable as an override. Moving to a database, a
   REST endpoint, or a different serialisation is a single-file
   change.

6. **The unified solver dispatches by equation id, not by Python
   module path.** The registry is explicit (`register("EQ-0001",
   triple)`) — no import-side-effect magic, no entry-point
   discovery, no plugin system. Any runtime that can execute
   Python and call `register` can populate the registry.

## Migration targets

### A. Bare-metal Python (no container)

The lightest-weight move. Works on macOS, Linux, or Windows with
Python 3.10+.

```bash
cd /Users/matthewluallen/hequ
python3 -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib sympy icontract==2.7.1 \
            hypothesis==6.112.1 jupytext==1.16.4 networkx==3.3 \
            jupyter nbclient nbformat

# Set the inventory path (or leave the default repo-root lookup).
export HEQU_INVENTORY=$PWD/critical_equations_inventory.json

# Execute all labs
PYTHONPATH=labs python labs/framework/build_notebooks.py
```

The only file that references `/home/jovyan/work` is
`build_notebooks.py` — update `REPO_ROOT` near the top to
`Path.cwd()` or `Path(__file__).resolve().parents[2]` for portable
operation.

### B. conda / mamba

```bash
conda create -n hequ python=3.11
conda activate hequ
conda install -c conda-forge numpy scipy matplotlib sympy \
              jupyterlab jupytext networkx nbclient nbformat
pip install icontract==2.7.1 hypothesis==6.112.1
```

Same `build_notebooks.py` adjustment as above. Conda gives you
pre-built wheels for everything including pygraphviz if you later
decide to re-add it (see the commented block in `requirements.txt`).

### C. Podman / Apptainer (rootless container)

`Dockerfile` uses only portable instructions (`FROM`, `RUN`, `COPY`,
`USER`, `WORKDIR`, `CMD`). Build with:

```bash
podman build -t hequ-labs:latest .
podman run --rm -v $PWD:/home/jovyan/work hequ-labs:latest \
    bash -lc "cd /home/jovyan/work && python labs/framework/build_notebooks.py"
```

For Apptainer / Singularity on an HPC cluster:

```bash
apptainer build hequ-labs.sif docker://localhost/hequ-labs:latest
apptainer exec --bind $PWD:/work hequ-labs.sif \
    bash -lc "cd /work && python labs/framework/build_notebooks.py"
```

### D. Managed notebook services

| Service              | What to mount / upload         | Adjustment                                           |
| -------------------- | ------------------------------ | ---------------------------------------------------- |
| **Google Colab**     | Upload `labs/` and the JSON    | `pip install` the framework deps in the first cell |
| **Kaggle Kernels**   | Same                            | Same; use an "Internet on" kernel for pip installs   |
| **Databricks**       | Repos clone                     | Use `%pip install`; paths are `/Workspace/...`       |
| **SageMaker Studio** | Clone into the user directory   | Use the `conda_python3` kernel                       |
| **Hugging Face Spaces (Gradio / Streamlit)** | Repo clone + `requirements.txt` | `build_notebooks.py` can be a Space hook      |

For all of these: (a) upload or clone `labs/` and the inventory
JSON, (b) `pip install -r requirements.txt`, (c) set
`HEQU_INVENTORY` to the JSON path in the hosted filesystem. Nothing
else changes.

### E. Off Python entirely

Two rails to consider:

#### E1. Julia + jupyter

Jupytext's percent format is Python-only, but the *structure* of a
lab (markdown, code, plots, Hoare triples, solver registry) is
language-agnostic. A Julia port:

- Rewrite `framework/` in Julia using `ContractsCore.jl` (runtime
  contracts) + `Test.jl` (property-based).
- Port each lab as a `.jl` file in the same percent layout —
  Jupytext supports `.jl`.
- The equation-corpus JSON loads natively via `JSON.jl`.
- Triples become Julia types with the same three fields; the
  registry is a `Dict{String, Vector{HoareTriple}}`.

Roughly a 1:1 line port. The only non-trivial step is translating
`icontract` decorators to Julia macros.

#### E2. Formal-verification targets (Lean 4 / Dafny / Coq)

The pilot framework uses *runtime* Hoare triples, which is sufficient
for empirical verification but doesn't give mechanised proof. To
escalate:

- **Dafny.** Port the unified solver dispatch logic only (it is the
  most load-bearing piece and fits in ~200 lines of Dafny). Each
  lab's command function becomes a Dafny method with explicit
  `requires` / `ensures` clauses that mirror the Python
  precondition/postcondition. Dafny's `wp` calculator then verifies
  the triple mechanically.
- **Lean 4 / mathlib.** The closed-form equations (Beer–Lambert,
  Newton's Second Law point-form, Hooke, etc.) port cleanly to
  Lean as `theorem` statements; the proofs are one-liners for
  algebraic identities and non-trivial for PDEs. Lean's
  `decide` / `norm_num` / `field_simp` tactics dispatch the
  algebraic cases automatically.
- **Coq.** Similar story to Lean; `Coq.Reals` is usable for the
  analytic parts but the mechanisation overhead is higher. Prefer
  Lean for this corpus.

In all three cases the `framework/` Python code stays as the
executable spec, and the formal-verification artefacts live alongside
in a parallel `formal/` directory. **We do not plan to do this
during the 137-equation scale-up** — the runtime triples are
sufficient to surface overlap/omission/error signals — but the
migration path is intentionally open.

## What changes in each migration target

| Concern                | Docker (current) | Bare-metal Python | conda | Podman | Managed notebook | Julia | Dafny/Lean |
| ---------------------- | :--------------: | :---------------: | :---: | :----: | :--------------: | :---: | :--------: |
| Framework code         |    unchanged     |     unchanged     | unchanged | unchanged | unchanged | rewrite | rewrite |
| Lab `.py` sources      |    unchanged     |     unchanged     | unchanged | unchanged | unchanged | rewrite | rewrite |
| Equation JSON          |    unchanged     |     unchanged     | unchanged | unchanged | unchanged | unchanged | unchanged |
| `Dockerfile`           |    unchanged     |      N/A          |  N/A  | trivial edit | N/A | N/A | N/A |
| `requirements.txt`     |    unchanged     |     unchanged     | split into conda-forge + pip | unchanged | unchanged | `Project.toml` | `lakefile.lean` etc. |
| `build_notebooks.py`   |    unchanged     | adjust `REPO_ROOT` | adjust `REPO_ROOT` | trivial | hosted equivalent | rewrite | drop |
| Execution command      |  docker run …    |  `python …`       | `python …` | `podman run …` | cell-by-cell | `julia …` | `dafny verify` |

**The migration boundary is `build_notebooks.py`.** Everything
upstream of it is portable.

## Pre-migration checklist

Before moving, run these commands in the current Docker environment
and archive the outputs:

1. `python labs/framework/build_notebooks.py` → save the summary
   table and `labs/notebooks_out/` tree as the baseline.
2. `python -c "from framework.taxonomy import audit_roles; import
   json; print(json.dumps(audit_roles(), indent=2))"` → save as
   `labs/cross_analysis/audit_findings.json` (already generated
   as part of the pilot).
3. `pip freeze > labs/framework/requirements-frozen.txt` from
   inside the container — this is the exact set of transitive
   versions, useful if anyone needs to reproduce bit-for-bit later.
4. Commit a git tag `pilot-baseline` pointing at the corresponding
   source tree.

After migration, re-run (1) and (2) on the target and diff against
the baselines. Any new or missing findings indicate environmental
drift — chase them before proceeding.

## Known migration gotchas

1. **macOS vs Linux font rendering.** Matplotlib default fonts
   differ; lab PNG outputs will not be byte-identical across
   platforms. Compare numerical outputs (tables, printed values),
   not image hashes.

2. **Numpy BLAS backend.** Apple Silicon uses Accelerate by default;
   Linux x86_64 typically uses OpenBLAS. Floating-point reductions
   differ in the last 1–2 ULPs. Our tolerances (`1e-12 * max(1,
   |F|)`) are generous enough to absorb this, but any tightening
   must account for it.

3. **`hypothesis` seed stability.** Hypothesis records its seed in
   `.hypothesis/`; that directory is container-local. Delete it
   between runs on a new host to avoid stale shrinking state.

4. **`icontract` version.** We pin 2.7.1 because 2.8+ introduced a
   breaking change in how `**kwargs` propagates through
   `@require`/`@ensure`. When upgrading, rerun the test-pipeline
   and re-verify every lab.

5. **`jupytext` header format.** We use format version `1.3` with
   the `percent` dialect. Jupytext 2.x (not yet released) may
   change the comment marker; pin `jupytext<2` in requirements if
   the upgrade path is not yet clear.

## Questions to answer before the scale-up phase

- Will the target platform be known before we author the remaining
  134 labs, or should we keep Docker as the canonical environment
  and treat migration as a post-scale-up exercise? (The pilot is
  structured so the answer can be "either".)
- Does any lab need GPU-accelerated numerics (e.g. quantum
  mechanics labs with large Hamiltonian diagonalisations)? If yes,
  the migration target grows to include `torch` or `jax`, and the
  container base should switch from `scipy-notebook` to a CUDA-
  enabled image.
- Do we want the cross-analysis artefacts (overlap graphs, audit
  findings) to be first-class exports, or kept inline in
  `cross_analysis/`? For portability to managed notebook services
  the former is slightly cleaner.

Answer these before starting Phase 2 and the scale-up proceeds
cleanly.
