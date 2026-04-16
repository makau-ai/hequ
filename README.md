# hequ — Hoare-verified exploratory labs for the critical-equations corpus

## What this is

A reproducible, container-based lab environment for building **hands-
on, applied exploratory Jupyter labs** over the 137 equations in
`critical_equations_inventory.json`. Every lab:

- Formalises the underlying equation as a **Hoare triple**
  $\{P\}\,C\,\{Q\}$ (precondition → command → postcondition),
- Implements the command in Python with **runtime triple enforcement**
  (violations raise structured `PreconditionViolation` /
  `PostconditionViolation` exceptions),
- Runs **numerical experiments** end-to-end inside a headless kernel
  with plots and a worked example,
- Deliberately **triggers the negation / failure case** and asserts
  the precondition fires,
- **Cross-links** to other equations in the corpus (energy drift in
  an Euler integrator → cross-link to conservation of energy, etc.),
- **Registers a solver** with a unified dispatcher that aims to grow
  into the "one algorithm for all situations" described in the
  project goals.

## Repository layout

```
hequ/
├── Dockerfile                         # scipy-notebook + icontract + hypothesis + jupytext
├── requirements.txt                   # Python pins (icontract, hypothesis, jupytext, networkx)
├── README.md                          # this file
├── MIGRATION.md                       # how to move off Docker / Jupyter / Python
│
├── Critical_Equations_Complete_Edition.docx    # source corpus (narrative form)
├── critical_equations_complete.csv             # source corpus (tabular)
├── critical_equations_inventory.json           # source corpus (primary — framework loads this)
├── deep-research-report (2).md                 # source corpus (analytical overview)
│
└── labs/
    ├── framework/                     # Python package — migration boundary
    │   ├── __init__.py                #   public re-exports
    │   ├── hoare.py                   #   HoareTriple, verify, verified, subsumes
    │   ├── taxonomy.py                #   JSON loader, role canonicalisation, audit_roles
    │   ├── registry.py                #   {equation_id -> [triple]} module registry
    │   ├── unified_solver.py          #   role-dispatched meta-solver
    │   └── build_notebooks.py         #   headless .py → executed .ipynb pipeline
    │
    ├── physics/                       # Physics labs (52 equations target; 2 pilot)
    │   ├── EQ_0001_newtons_second_law.py
    │   └── EQ_0005_conservation_of_energy.py
    │
    ├── chemistry/                     # Chemistry labs (9 equations target; 1 pilot)
    │   └── EQ_0056_beer_lambert_law.py
    │
    ├── cross_analysis/
    │   ├── pilot_findings.md          # running ledger of overlaps / omissions / errors
    │   └── audit_findings.json        # output of audit_roles() over the full corpus
    │
    └── notebooks_out/                 # generated — do not edit by hand
        ├── physics/
        │   ├── EQ_0001_newtons_second_law.ipynb
        │   └── EQ_0005_conservation_of_energy.ipynb
        └── chemistry/
            └── EQ_0056_beer_lambert_law.ipynb
```

### Source of truth

Labs are authored as **jupytext percent-format `.py` files**, not as
`.ipynb` directly. Rationale:

- `.py` files are grep-able, diff-able, and reviewable in plain text.
- `.ipynb` files include execution outputs, base64-encoded PNGs, and
  cell IDs — noisy in version control and hostile to migration.
- `jupytext` converts `.py` → `.ipynb` on demand, and the pipeline
  (`labs/framework/build_notebooks.py`) executes them in a clean
  kernel and writes the resulting `.ipynb` to `labs/notebooks_out/`.

Review the `.py` source; read the `.ipynb` for outputs.

## Build and run

### Prerequisites

- Docker (tested with Docker Desktop 29.2 on macOS arm64).
- ~4 GB free disk for the base image + our layer.

### Build the image

```bash
cd /Users/matthewluallen/hequ
docker build -t hequ-labs:latest .
```

Build time: ~20–40 s once the base image is cached, ~3 min on a
cold pull of `quay.io/jupyter/scipy-notebook`.

### Execute every lab headlessly

```bash
docker run --rm \
    -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:latest \
    bash -lc "cd /home/jovyan/work && python labs/framework/build_notebooks.py"
```

Exit code is 0 iff every lab ran cleanly (precondition violations
inside deliberate negation-case `try/except` blocks are expected and
do not fail the build; *un*-caught exceptions do). The summary
table at the end of the output names each lab and its execution
time.

### Interactive Jupyter Lab

```bash
docker run --rm -p 8888:8888 \
    -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:latest
```

Open http://localhost:8888 and navigate to `work/labs/`. Jupytext
pairs the `.py` and `.ipynb` views automatically — edit either,
and jupytext keeps them in sync.

## The framework in one page

### Hoare triples

```python
from framework import verified

@verified(
    precondition=lambda m, F: m > 0 and math.isfinite(m) and math.isfinite(F),
    postcondition=lambda inputs, output: abs(inputs["m"] * output - inputs["F"]) < 1e-12,
    name="EQ-0001/closed-form-acceleration",
    wp_notes="wp(a := F/m, m*a == F) = (F == F ∧ m > 0)",
)
def newton(*, m, F):
    return F / m

newton(m=5.0, F=20.0)    # returns 4.0; triple verified
newton(m=0.0, F=20.0)    # raises PreconditionViolation
```

The decorated object **is** a `HoareTriple`. Labs can also construct
triples manually (`framework.HoareTriple(...)`) when they need loop
invariants or different wiring.

### Registering with the unified solver

```python
from framework import register, solve

register("EQ-0001", newton)               # one triple per call; can register many

result, trace = solve("EQ-0001", m=5.0, F=20.0)
print(trace.as_markdown())                # audit log of which triple fired
```

Multi-triple dispatch: if several triples are registered under one
`equation_id`, the dispatcher picks the **most-specific-matching**
triple (the one whose precondition signature consumes the most of
the caller's inputs), falling back to registration order as the
tiebreaker. A closed-form triple taking `{m, F}` and a trajectory
triple taking `{m, F, x0, v0, T, dt}` coexist cleanly; `solve()`
picks the right one based on which parameters the caller supplies.

### Cross-analysis audit

```python
from framework.taxonomy import audit_roles
findings = audit_roles()  # list of dicts with kind / id / detail
```

The audit runs four heuristic checks:

1. `role_mismatch` — the formula looks like deterministic dynamics
   but the source JSON classifies it as a conservation law.
2. `missing_assumptions` — `key_assumptions` is empty.
3. `placeholder_assumptions` — contains `"See negation section"`.
4. `assumptions_leaked_from_negation` — verbatim fragment of
   `negation_failure_case` text.

Pilot audit surfaced **153 findings across 137 equations** — see
`labs/cross_analysis/pilot_findings.md` for discussion.

## Current status

- **Framework:** complete and verified against the 3 pilot labs.
- **Pilot labs:** 3 / 137 equations (2 Physics, 1 Chemistry). All
  three execute cleanly end-to-end.
- **Cross-analysis:** pilot-scale, with an automated audit pass over
  the full corpus.
- **Unified solver:** single-equation dispatch with most-specific-
  match signature projection. Role-family fallbacks are **not yet
  implemented** — that is Phase 6 of the scale-up plan.

See `labs/cross_analysis/pilot_findings.md` §5 for the phased
scale-up plan to cover the remaining 134 equations.

## Testing

```bash
# Full rebuild + execute. Exit code 0 iff every lab is green.
docker run --rm -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:latest \
    bash -lc "cd /home/jovyan/work && python labs/framework/build_notebooks.py"

# Audit the source corpus without running any labs.
docker run --rm -v /Users/matthewluallen/hequ:/home/jovyan/work \
    hequ-labs:latest \
    bash -lc "cd /home/jovyan/work && PYTHONPATH=labs python -c \
        'from framework.taxonomy import audit_roles; \
         import json; print(json.dumps(audit_roles(), indent=2))'"
```

## See also

- `MIGRATION.md` — how to move this off Docker, off Jupyter, or into
  a different runtime.
- `labs/cross_analysis/pilot_findings.md` — detailed findings from
  the pilot, including the full audit breakdown.
- `deep-research-report (2).md` — the analytical framing that drives
  the role taxonomy.
