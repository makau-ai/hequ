# Design: Realization-Grounded Coupling Engine (Phase 12–20)

**Version:** v4 (Round-2 discharge submission)

**Status:** Round 1 (Discovery) is complete. Three board
reviews (v1/v2/v3) produced converging technical concerns that
the editor synthesized into a **Frozen Concern Set (FCS)** of
six items (C1–C6, see §13). v4 addresses each FCS item
in-place and is submitted to Round 2 for **scope-frozen
discharge review** via `AIConsensusBoard.discharge_round()`.
Reviewers in Round 2 can only evaluate whether C1–C6 are
addressed; they cannot raise new concerns.

v4 also formally records three protocol additions that were
architected during Round 1 discussion and are now binding:

- **§11a.5** Cost-neutrality disclaimer (binding on every
  future board prompt)
- **§11e** Formal scope-frozen discharge protocol (built as
  `AIConsensusBoard.discharge_round()` in
  `framework/ai_consensus.py`)
- **§11h** Failure Investigation Protocol (binding: equation
  modifications and tolerance adjustments require state audit
  → assumption audit → literature RAG → board failure review
  → user approval; no corner cuts)
- **§11i** Academic rigor standard (binding: every PROVED or
  GROUNDED coupling must pass a Nobel-prize-caliber readiness
  checklist; internal board consensus is necessary but not
  sufficient)

**Authorship:** Architect synthesis. Built on the surviving work of
Phase 0–11 and the fix-pack, and directly shaped by the Phase 11
board rerun findings (OpenAI's "no named transducer" objection and
the pattern of rejection that revealed how thin our grounding was).

---

## 0. The thesis

**The difference between a coincidence and a genuine cross-domain
coupling is executable realization.**

A real cross-domain coupling admits a physical system in which
both equations hold simultaneously at the same moment in time, on
the same substrate, and produce the same measurable answer.
Newton+Hooke is real because mass-spring oscillators exist.
Fourier+Fick is real because counter-flow heat-and-mass exchangers
exist. Newton+Shannon is not real because no laboratory object
obeys both equations at once.

Every prior attempt at cross-domain equation discovery has failed
by arguing about symbols while ignoring execution. This engine
will run experiments and compare to reality.

## 1. What's different from every prior attempt

We've been reading through SINDy, PySR, AI Feynman, SemGen/SemSim,
DARPA ASKE/ASKEM/SKEMA, CycL, Wolfram Alpha, Catlab, and the entire
bond-graph literature. The failures share a shape:

1. **Single-domain focus.** Equation-discovery-from-data tools
   work inside one domain because state variables are one-domain.
2. **Syntactic sieves without physical grounding.** Structural
   matching finds algebraic twins and cannot distinguish an
   analogy from an accident.
3. **No executable composite.** When a tool "merges" two models,
   it produces a glued-together description, not a running
   simulation. There is nothing to compare against reality.
4. **No real reference values.** Nobody solves a composite and
   asks whether the answer matches a real measurement.
5. **No adversarial pressure.** Systems test themselves with
   their own metric, which is circular.
6. **Human-in-the-loop as the hidden fallback.** DARPA SKEMA
   reports manual correction as standard. SemGen requires domain
   experts. Nobody runs this fully automatically at scale with
   trustworthy output.
7. **One reviewer with one model's blind spots.**

Our current Phase 11 state improves on (6) and (7) with the
three-model board and unanimous voting rule. This design targets
(1), (3), (4), and (5): real executable composites, real
reference values from board-triangulated textbook citations,
adversarial pre-registration at scale, and eventually live
sensor grounding.

## 2. Evidence hierarchy

For every coupling hypothesis, evidence accumulates across four
levels, from weakest to strongest:

| Level | Source | What it proves |
|---|---|---|
| 1 | Unit test on canonical problem (Phase 12) | The equation is correctly implemented |
| 2 | Composite notebook vs textbook reference (Phase 13) | The coupling produces the right answer in theory |
| 3 | Literature citation via board consensus (Phase 14) | The coupling is claimed in primary sources |
| **4** | **Live sensor agreement (Phase 16–17)** | **The coupling predicts real measurements** |

Level 4 is the only one that cannot be gamed by clever prompting.
It is the thing that would make this project genuinely different
from every prior attempt.

A coupling's ledger status is a function of which levels it has
passed:

- **PROVED**: passes L1 + L2 AND the board unanimously approves
  with citations (L3 consensus of ≥2 of 3)
- **EMPIRICAL**: passes L1 + L2 with board majority-approve but
  one dissent
- **GROUNDED**: passes L4 (live sensor agreement) in addition
  to all above — highest-confidence tier, added in Phase 17
- **CONJECTURAL**: passes L1 but no composite exists or all
  composites fail
- **REJECTED**: fails L2 (composite produces wrong answer) OR
  2-of-3 reject OR any constraint filter returns FAILED

Promotion to PROVED requires explicit AI board sign-off with
literature citations. Promotion to GROUNDED requires live sensor
agreement with declared tolerance bounds. Both decisions are
ledger-recorded with full provenance.

## 3. Architecture — nine layers

```
Layer 0 — Typed canonical form           [already built]
Layer 1 — Canonical problems             [Phase 12]
Layer 2 — Composite problem catalog      [Phase 13]
Layer 3 — Literature RAG + transducers   [Phase 14]
Layer 4 — Layer 5 coupling sieve         [already built]
Layer 5 — Physical constraint filter     [already built, refined]
Layer 6 — Realization grounding          [Phase 14]
Layer 7 — AI review board (augmented)    [upgraded in Phase 14]
Layer 8 — Adversarial pre-registration   [Phase 15]
Layer 9 — Live sensor grounding          [Phase 16–17]
Layer 10 — Experiment authority          [Phase 19]
Layer 11 — Quantum specialist (Rigetti)  [Phase 20]
```

### Layer 1 — Canonical problems

For every equation in the corpus, a `problems/` directory:

```
labs_v2/equations/classical_mechanics/EQ-NEWTON-II/
├── equation.yaml
├── problems/
│   ├── 01_projectile.ipynb
│   ├── 02_elastic_collision.ipynb
│   └── 03_variable_mass.ipynb      (deliberate negative case)
├── problems.yaml                    (registry + board-sourced refs)
└── citations.bib
```

Each problem has:
- **Statement** — plain-English description of the physical scenario
- **Setup** — symbolic variables, numeric values, units
- **Expected value** — numerical answer with citation
- **Reference source** — board-sourced via cross-validation (§5)
- **Pytest assertion** — `math.isclose(computed, expected, rel_tol=...)`
- **Notebook** — executable derivation + solve + assert

Reference values are sourced by the AI consensus board (§5), not
hardcoded by the architect. No page citation that hasn't been
produced by ≥2 models independently.

### Layer 2 — Composite problem catalog

For every known cross-domain coupling, a composite notebook:

```
labs_v2/composites/
├── newton_hooke_sho/
│   ├── notebook.ipynb               — solves m·x''+k·x=0
│   ├── expected.yaml                — T=2π√(m/k), board-cited
│   └── composite.yaml               — {eq_a, eq_b, coupling_var, type}
├── newton_ohm_dc_motor/
│   ├── notebook.ipynb               — back-EMF loop
│   ├── expected.yaml                — torque-current curve, board-cited
│   └── composite.yaml
├── fourier_fick_soret/
│   ├── notebook.ipynb               — thermodiffusion in NaCl brine
│   ├── expected.yaml                — Soret coefficient, board-cited
│   └── composite.yaml
...
```

Starter catalog (authored with board consensus):
1. **Newton + Hooke → simple harmonic oscillator**
2. **Newton + gravity → Kepler orbital period**
3. **Newton + Ohm → DC motor torque curve via back-EMF**
4. **Newton + work-energy → elastic collision energy conservation**
5. **Fourier + Fick → Soret thermodiffusion in dilute brine**
6. **Arrhenius + Fick → reaction-diffusion wavefront speed**
7. **Schrödinger + heat → Wick rotation of free propagator**
8. **Black-Scholes + heat → log-price substitution**
9. **Ohm + Joule → resistor dissipation**
10. **Fick + Nernst → electrochemistry transport number**

A coupling hypothesis is **grounded** iff a composite notebook
exists for it AND the notebook's asserted output matches the
board-cited reference within tolerance. A coupling for which no
composite can be authored stays at CONJECTURAL forever — even if
the sieve adores it.

### 2a. Automated composite notebook generation

**Added per board v1 review.** Gemini correctly flagged that v1
said "generated or retrieved" without specifying HOW for the
generated case. The risk was a hidden human-in-the-loop
bottleneck. v2 specifies the full programmatic generation path.

Given a coupling `(eq_a, eq_b, transducer)`, the engine emits a
runnable notebook via the following deterministic pipeline:

1. **System assembly.** The two canonical forms are combined via
   the transducer's constitutive relations. For Newton+Ohm via
   the `motor_constant` transducer: substitute `F = K_t · I` into
   Newton II and `V = K_t · v` into Ohm, producing the coupled
   ODE system `{m·dv/dt = K_t·I − b·v, V = K_t·v + I·R}`.
2. **Problem parameterisation query.** The board is asked: "What
   is the simplest initial-value problem that demonstrates this
   coupled system? Reply as JSON with initial conditions,
   numerical parameter values, and time horizon." Consensus
   required per §5.
3. **Reference value query.** The board is asked for the expected
   value of a declared observable at a declared time (e.g.,
   steady-state angular velocity `ω_ss` when the motor reaches
   terminal torque). Consensus + orthogonal verification per §5.
4. **Notebook assembly via `nbformat`.** The engine programmatically
   builds an `.ipynb` with cells:
   - Imports (sympy, scipy, numpy, matplotlib, pint)
   - Problem statement (from the board's reply, verbatim)
   - Symbolic setup (sympy variables, the coupled ODE system)
   - Numeric parameters (from the board's parameterisation)
   - Solver (scipy.integrate.solve_ivp)
   - Observable extraction (evaluate the named observable at the
     declared time)
   - Assertion (`math.isclose(computed, reference_value,
     rel_tol=0.02)`)
   - Plot (time series for human inspection)
5. **Execution via `nbclient`.** The notebook is executed in a
   subprocess. Any cell error, assertion failure, or
   dimensional-consistency failure marks the composite as
   `EXECUTION_FAILED` and the coupling inherits that failure.
6. **Provenance recording.** The generated notebook path, the
   board replies that shaped it, the pytest output, and the
   final observable value are all written to the ledger as
   `RealizationResult(source="composite", ...)`.

For well-known composites (the starter catalog), the notebook is
hand-authored ONCE by the architect and reused — the auto-
generation pipeline runs only for NOVEL couplings the sieve
surfaces that aren't in the catalog. Hand-authored and auto-
generated composites pass through the same `nbclient` execution
path so the downstream evidence layer can't tell them apart.

This is the full answer to Gemini's v1 missing-piece #2. There
is no human in the loop for novel-composite generation. The
board is queried programmatically, the notebook is assembled by
code, and the execution is automated.

### Layer 3 — Literature + transducer library

- **Per-equation passage index**: each equation has a
  `literature/` directory with board-produced citations to
  primary sources (Feynman Lectures, OpenStax, NIST handbook,
  Landau-Lifshitz, Incropera, Goldstein, etc.). The board
  triangulates: a citation is accepted only if ≥2 models produce
  the same primary source (within author + volume).
- **Transducer catalog**: `labs_v2/transducers.yaml` — a
  ~30-entry table of named bond-graph transducers connecting
  different physical domains:

```yaml
- id: TRANSDUCER-MOTOR
  domains: [classical_mechanics, electrical_circuits]
  effort_a: Force          # N
  flow_a: Velocity         # m/s
  effort_b: ElectricPotentialDifference  # V
  flow_b: ElectricCurrent  # A
  coefficient: motor_constant   # N/A or V·s/m (same)
  formula: "F = K_t · I AND V_back = K_t · v"
  citation: ["Karnopp §5.2", "Paynter 1961", "Breedveld 1984"]
  sourced_by: [claude-opus-4-6, openai-gpt-5]
```

The transducer catalog is authored by querying the board:
"Produce a list of 30 named bond-graph transducers connecting
distinct physical domains. Each entry: name, domains, effort/flow
pairs, coefficient name, formula, primary citation." I take the
intersection of the three replies and require ≥2 models to
produce the same entry for it to enter the catalog.

When the sieve emits a coupling, it attaches a transducer from
the catalog instead of `transfer_function="identity"`. This
directly addresses OpenAI's Phase 11 objection.

### 3a. Conjectural transducer proposal (NEW, per board v1 review)

Gemini v1 flagged: "the system may become over-reliant on the
initial, manually-curated transducer library, potentially
limiting its ability to discover phenomena involving novel or
uncatalogued transducer mechanisms." Fair point — the catalog
would stall on any genuine discovery.

**Fix:** when the sieve finds a high-score coupling for which
no catalogued transducer fits, it produces a
`ConjecturalTransducer` hypothesis with the structure below,
and the AI board reviews it separately:

```python
@dataclass
class ConjecturalTransducer:
    domain_a: str           # e.g. "classical_mechanics"
    domain_b: str           # e.g. "population_dynamics"
    effort_a: str           # QUDT property URI
    flow_a: str
    effort_b: str
    flow_b: str
    implied_coefficient_name: str        # proposed, e.g. "ecological_impedance"
    implied_coefficient_dimensions: str  # pint string, e.g. "[mass]*[time]/[substance]"
    implied_formula: str                 # "F = k_eco · y"
    confidence_from_sieve: float         # 0.0–1.0
    supporting_sieve_evidence: dict      # bond-graph role match, dim distance, etc.
```

The conjectural transducer enters a separate board-review queue:
"Does this bond-graph transducer correspond to a named physical
mechanism in the literature? If so, name the mechanism and cite
it. If not, is it still physically plausible? Reply as JSON
with verdict={known_transducer, plausible_novel, spurious} and
justification."

Outcomes:
- **`known_transducer`**: ≥2 models identify the same real
  mechanism with a citation → the entry is added to the main
  catalog as a fully-credited transducer.
- **`plausible_novel`**: ≥2 models find it plausible but
  uncatalogued → the entry enters a `conjectural_transducers.yaml`
  file (distinct from the main catalog) with the flag
  `REQUIRES_EXPERIMENTAL_VALIDATION`. Any coupling using it is
  ledger-marked CONJECTURAL regardless of other signals.
- **`spurious`**: ≥2 models reject → the coupling it came from
  is demoted to REJECTED.

This is the organic-growth mechanism the catalog needs. It also
creates an honest path from "sieve finds a weird coupling" to
"board proposes a new named physical mechanism the engine
believes exists but isn't in textbooks yet." Those are the
candidates worth live-sensor testing in Phase 17+.

### Layer 6 — Realization grounding

A new step in `run_discovery.py`, after the Phase 6 physical
constraint filter and before the Phase 9 AI review board call:

```python
for hypothesis in coupling_report.hypotheses:
    # ... existing Phase 6 / Phase 7 evaluation ...
    realization = ground_against_composite(hypothesis, composites_catalog)
    hypothesis.realization = realization   # RealizationResult
    if realization.source == 'composite' and realization.passed is False:
        hypothesis.outcome = REJECTED
        hypothesis.rejection_criterion = (
            f"composite execution failed: {realization.notebook_path}"
        )
```

`RealizationResult` is source-agnostic (see §4) — the same
dataclass carries evidence from unit tests, composite notebooks,
literature citations, and live sensor readings. Phase 12 populates
L1. Phase 13 populates L2. Phase 14 populates L3. Phase 16–17
populates L4. The downstream code never special-cases the source.

### Layer 7 — Augmented AI review board

The existing three-model review board gains additional evidence
in every prompt:

- Composite notebook output + reference value + delta
- Transducer attached to the coupling
- Literature citations from the per-equation passage index
- Pytest pass/fail status

OpenAI's Phase 11 rejection pattern ("no transducer named")
should flip to APPROVE once the transducer is explicit in the
prompt. Claude's Phase 11 approval pattern should hold.
Gemini's permissiveness should be tempered by the requirement
that every claim point to a composite result.

### Layer 8 — Adversarial pre-registration

The current pre-reg harness (§10 of the coupling sieve design)
has 4 positives + 3 rejections. Phase 15 grows this to ~30
items:

- **Must surface** (10): Newton+Hooke SHO, Fourier+Fick, Newton+Ohm,
  Newton+Work-Energy, Schrödinger+heat via Wick, Black-Scholes+heat
  via log-price, Arrhenius+Fick reaction-diffusion, Newton+gravity
  Kepler, RLC+mass-spring-damper, Kirchhoff-current vs Newton-force.
- **Must reject** (15): Newton+Shannon, Black-Scholes+Lotka-Volterra,
  Lorentz+Bayes, Maxwell-displacement+Fick (same shape, different
  physics), Poisson+Laplacian-of-velocity, Helmholtz-acoustic+
  Schrödinger (same Laplacian form), Bernoulli+Navier-Stokes (related
  but no variable id), Boltzmann-entropy+Shannon-entropy (related but
  different units), …
- **Honest unknowns** (5): Wick-rotation duality class at large,
  RG-flow similarities, Kolmogorov-Wiener filtering vs Schrödinger
  (a known hard case), …

Every run must produce 100% on the first two categories. Any
failure is a hard stop. Only after passing must-surface and
must-reject does the sieve get to speak on the honest-unknowns.

### Layer 9 — Live sensor grounding

The evidence hierarchy's level 4. Realized via the
`framework/sensors/` subpackage with a capability-gated adapter
interface (§6). Starter sensor targets per equation family (not
all will be implemented; these are the realistic entry points):

- **Newton II, Hooke**: phone IMU via Web Sensor API or a
  Raspberry Pi + MPU-6050. Pendulum, spring-mass rig.
- **Fourier**: ecobee/Nest API + DS18B20 on a heated rod.
- **Ohm, Kirchhoff**: Shelly EM clamp or smart meter.
- **Bernoulli, Navier-Stokes**: NOAA METAR feed + barometer.
- **Arrhenius**: weather × food-spoilage datasets.
- **Lotka-Volterra**: iNaturalist, public fisheries.
- **Black-Scholes**: Polygon.io free tier options + underlying.
- **Shannon**: entropy estimators on any live text stream.
- **Bayes**: A/B test streams from any product telemetry.
- **Relativity**: LIGO open data, JWST astrometry.
- **Fick**: Purple Air PM2.5 network.

### Layer 10 — Experiment authority

The board should eventually be able to **propose and run
experiments** to test hypotheses and create conditions, not
just review static evidence. This is Phase 19 — the largest-
risk / highest-payoff part of the whole architecture. See §6.

### Layer 11 — Quantum specialist (Rigetti via Amazon Braket)

**Project name self-realization.** `hequ` encodes H + EQU + QU +
.AI — Human, Equation, Quantum, AI (and *hequ*, a strong horse —
motion and force, fitting for a mechanics-rooted project). The
`QU` is not decorative. We have access to a **Rigetti 108-qubit
device via Amazon Braket**
(https://aws.amazon.com/braket/quantum-computers/rigetti/). The
project should use it.

Concrete first use: **Level-4 evidence from a real quantum
computer**. Take the Newton+Hooke → simple harmonic oscillator
composite, map it to a small Hamiltonian (2–4 qubits for a
low-energy basis truncation of the quantum harmonic oscillator),
run VQE on Rigetti Aspen / Ankaa, and compare the measured
ground-state energy against the board-sourced classical
reference `E_0 = (1/2) ℏω = (1/2) ℏ √(k/m)`. If the quantum
measurement agrees with the classical reference within the
Rigetti gate-error budget, that's a Level-4 signal obtained from
a real physical experiment on real quantum hardware — exactly
the "executable realization" the thesis demands.

What quantum adds beyond classical grounding:

1. **Authentic cross-domain evidence.** The quantum computer is
   a sensor for quantum predictions. Running the SHO Hamiltonian
   on it and getting `(1/2)ℏω` validates both the Schrödinger
   equation entry in the corpus AND the Newton+Hooke coupling
   simultaneously, on a substrate that cannot be faked.
2. **Wick rotation demonstration.** Schrödinger ↔ heat via
   t → −iτ is one of our pre-registered couplings. We can
   actually execute a short time evolution on the hardware,
   analytically continue, and compare to the heat-equation
   solution. This is the most non-trivial cross-domain coupling
   in the corpus and the only one for which the Wick rotation
   isn't merely symbolic.
3. **QAOA for the sieve's bijection search.** The structural
   sieve currently enumerates O(V!) permutations to find the
   best bond-graph-role-scored bijection. For V ≤ 6 this is
   trivial. For V ≥ 8 (Navier-Stokes scale) we hit the V-cap.
   The bijection problem is a max-weight bipartite matching
   with structural constraints — a natural QAOA target. Deferred
   to Phase 20+, not yet needed.
4. **Demonstration value.** The site can show "here's a
   coupling that has been validated on a 108-qubit Rigetti
   machine, here's the circuit, here's the citation chain."
   That's an honest signal no prior cross-domain discovery
   project has ever produced.

Architecture notes for Phase 20:
- `framework/sensors/rigetti_aspen.py` — `SensorAdapter`
  subclass with `CAPABILITIES = {READ, WRITE}` (write = submit
  a circuit; read = retrieve results).
- All Braket API calls go through the capability system. A
  quantum "experiment" is an `ExperimentEnvelope` with
  magnitude limits on circuit depth, qubit count, and shot
  count (so cost and noise are bounded).
- Results flow back as `RealizationResult(source="sensor_live",
  provenance={device: "rigetti-ankaa-9q", task_arn: ...,
  shots: N, raw_counts: ...})`.
- Cost gate: every quantum experiment's estimated cost is
  computed from Braket's pricing before submission, compared
  against a per-run budget, and blocked if over-budget.

## 4. Core dataclass contracts

### RealizationResult

```python
@dataclass
class RealizationResult:
    source: Literal["unit_test", "composite", "literature",
                    "sensor_historical", "sensor_live"]
    passed: Optional[bool]           # None for literature
    computed_value: Optional[float]
    reference_value: Optional[float]
    rel_tolerance: float = 0.05
    citation: Optional[str] = None
    notebook_path: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    # For sensor sources: {sensor_id, time_range, sample_count,
    #                      calibration_id, adapter_version}
    # For composite: {composite_id, generated_or_authored}
    # For unit test: {problem_id, reference_source}
```

### CouplingHypothesis (extended)

```python
@dataclass
class CouplingHypothesis:
    # ... existing fields ...
    realization: Optional[RealizationResult] = None
    transducer: Optional[TransducerEntry] = None
    live_evidence: List[SensorReading] = field(default_factory=list)
```

### SensorAdapter (abstract, Phase 16)

```python
class SensorCapability(Enum):
    READ = "read"
    WRITE = "write"
    CONTROL = "control"
    ACTUATE = "actuate"

class SensorAdapter(ABC):
    sensor_id: str
    CAPABILITIES: FrozenSet[SensorCapability] = frozenset({SensorCapability.READ})
    @abstractmethod
    def read(self, query: SensorQuery) -> List[SensorReading]: ...
    def write(self, cmd: SensorCommand,
              envelope: ExperimentEnvelope) -> SensorResult:
        raise PermissionError("adapter has no WRITE capability")
    def actuate(self, cmd: SensorCommand,
                envelope: ExperimentEnvelope) -> SensorResult:
        raise PermissionError("adapter has no ACTUATE capability")
```

Defaults force every adapter to start READ-only. Adding WRITE or
ACTUATE capability to a specific adapter is a deliberate per-
adapter decision that shows up in code review. No adapter gains
actuation capability implicitly.

### ExperimentEnvelope (Phase 19)

```python
@dataclass
class ExperimentEnvelope:
    experiment_id: str
    hypothesis: str                  # what the experiment tests
    proposed_by: str                 # model id, e.g. "claude-opus-4-6"
    actuator_ids: List[str]
    sensor_ids: List[str]
    time_limit_seconds: int
    magnitude_limits: Dict[str, tuple[float, float]]
    rollback_plan: str               # human-readable + code reference
    approval_tokens: List[str]       # each is {reviewer, verdict, ts}
    status: Literal["proposed", "approved", "running", "done", "aborted"]
```

## 5. Board-sourced reference values with orthogonal verification

The novel part. For every canonical problem and every composite,
reference values come from the AI consensus board
(`framework/ai_consensus.py`), **and every accepted value passes
an orthogonal verification step** that breaks the circularity
risk Gemini correctly flagged in v1.

### 5.1 Query protocol

1. Architect writes the problem statement (pendulum L=1m, m=1kg
   on Earth, find period T).
2. Architect queries the board, demanding a structured reply:

```json
{
  "formula_symbolic": "2*pi*sqrt(L/g)",
  "formula_latex": "2\\pi\\sqrt{L/g}",
  "substitutions": {"L": 1.0, "g": 9.80665},
  "value": 2.006,
  "unit": "second",
  "citation_primary": "Goldstein, Classical Mechanics §6.1",
  "citation_secondary": "Feynman Lectures Vol I Ch 21",
  "confidence": 0.98
}
```

3. Three models reply independently.
4. Board consensus is accepted IFF:
   - ≥2 models produced `value` numerically and agree within 1%
     relative tolerance (via `numerical_reference_aggregator`)
   - ≥2 models produced the same `formula_symbolic` (symbolic
     equality after sympy normalization — not string equality)

### 5.2 Multi-check local verification (v4 revision, FCS C2+C3)

**v4 revision.** v3 claimed this verification was "orthogonal
cross-CAS." Round 1 reviewers correctly flagged that claim as
**factually wrong**: mpmath is sympy's own numerical backend, so
calling `sp.evalf()` and calling `mpmath` directly are not
independent code paths. v4 drops the false claim and specifies
a **multi-check pipeline** with explicit honesty about what is
and isn't independent, plus a concrete plan for genuine
orthogonal numerics via `python-flint` / `gmpy2`.

**No board-sourced value enters the ledger until the architect's
local multi-check pipeline passes.** The pipeline has four
sub-checks; ALL must pass.

#### 5.2.1 Check A — Symbolic equivalence via canonicalization pipeline (FCS C3)

v3 used `sp.simplify(expr) == 0` as the symbolic check. This
is **known incomplete** in sympy: `simplify` is a heuristic
that can return non-zero for expressions that ARE zero under
a stronger canonicalization, and conversely can normalize
different expressions to superficially-identical forms under
piecewise or branch-cut ambiguity. v4 replaces `sp.simplify`
with an explicit canonicalization pipeline:

```python
def symbolic_equivalence_check(board_formula, local_formula):
    # 1. Substitute QUDT-typed variables into both expressions
    #    so free symbols carry dimensional metadata
    f_b = inject_units(board_formula, descriptor_registry)
    f_l = inject_units(local_formula, descriptor_registry)

    # 2. Dimensional compatibility: refuse to compare expressions
    #    with different base-dimension signatures
    if base_dimensions(f_b) != base_dimensions(f_l):
        return FAIL("dimensional mismatch")

    # 3. Rational function normalization: cancel + together +
    #    expand + factor on the difference
    diff = sp.cancel(sp.together(sp.expand(f_b - f_l)))
    if diff == 0:
        return PASS("rational normalization collapsed to zero")

    # 4. Trigonometric + power simplification (cascaded)
    diff = sp.trigsimp(sp.powsimp(sp.expand_trig(diff)))
    if diff == 0:
        return PASS("trig/power simplification collapsed to zero")

    # 5. Polynomial remainder over a known-good basis (when the
    #    expressions are polynomial in the declared variables)
    if sp.degree(diff) >= 0:
        rem = sp.Poly(diff).as_expr().simplify()
        if rem == 0:
            return PASS("polynomial remainder is zero")

    # 6. Branch-cut-aware discriminating random evaluation:
    #    pick N=20 sample points drawn from a distribution
    #    that AVOIDS declared singularities and branch cuts
    #    of each variable, evaluate both expressions at each,
    #    compare with a declared tolerance. This catches cases
    #    where `simplify` fails but the expressions are
    #    numerically equal on the regular domain.
    for sample in discriminating_samples(f_b, f_l, n=20):
        v_b = safe_evalf(f_b, sample)
        v_l = safe_evalf(f_l, sample)
        if abs(v_b - v_l) / (abs(v_b) + abs(v_l) + 1e-30) > 1e-10:
            return FAIL(f"numerical divergence at sample {sample}")
    return PASS("discriminating random evaluation agrees everywhere")
```

**Known failure modes, documented:** the pipeline does NOT
handle the following correctly and will flag them as
`SYMBOLIC_EQUIVALENCE_UNDECIDABLE` instead of silently
mis-classifying:

- Piecewise functions with boundary conditions
- Multi-valued inverse functions (arcsin, arccos, arctan with
  quadrant ambiguity)
- `abs(x)` outside its principal domain
- Complex-argument branch cuts of `log`, `sqrt`, fractional
  powers

A formula flagged `SYMBOLIC_EQUIVALENCE_UNDECIDABLE` does not
enter the ledger automatically — it escalates to the user
Decision Matrix per §11e, because the failure is a LIMIT of
the verification pipeline, not a board hallucination.

#### 5.2.2 Check B — Property-based randomized sampling (FCS C5)

v3 specified "N=50 random parameter vectors." v4 upgrades this
to Hypothesis-style strategy-driven sampling with stratification,
boundary case coverage, and power analysis.

```python
from hypothesis import given, strategies as st, settings, HealthCheck

@given(sample_strategy_for(equation))
@settings(
    max_examples=N_power_analyzed,     # determined by §5.2.5
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
def test_formula_satisfies_relation(params):
    # Evaluate board_formula at params
    v_b = safe_evalf(board_formula, params)
    # Evaluate the governing equation's canonical form,
    # plugging params + v_b into the variables the board
    # claims are related
    residual = canonical_form.subs({**params, observable: v_b})
    # Dimensional check at the sample point
    assert dimensions_match(residual, expected_dimensionality)
    # Numerical residual must be within declared tolerance
    assert abs(safe_evalf(residual, {})) <= tolerance(params)
```

**`sample_strategy_for(equation)`** is a strategy generator
that, given the equation's declared variable types and their
QUDT QuantityKind URIs:

1. Draws unit-consistent parameter values from the variable's
   declared range (not uniform — stratified)
2. **Stratifies** the draws across orders of magnitude: for a
   variable that spans `[1e-6, 1e6]`, each order-of-magnitude
   band gets equal sample probability
3. Deliberately includes **boundary cases**: minimum, maximum,
   zero (if in domain), unity, and nearest-to-singularity
4. **Avoids declared singularities and branch cuts** of any
   function in the canonical form
5. **Seeds reproducibly**: the sample seed is logged in the
   ledger so any future audit can replay the exact sample set

**`N_power_analyzed`** is computed via a simple power analysis:
for a declared false-discovery rate `α = 1e-4` and a declared
minimum detectable effect size `δ = 1%` relative error, the
minimum number of samples N satisfies roughly
`N ≥ 1/(α · δ²)`. For typical problems, `N ≈ 10000`, but the
exact value is declared per-problem in the
`problems.yaml` entry, not a magic constant. Small problems
(scalar algebraic) may justify `N ≈ 200`; PDE composites may
need `N ≈ 50000`.

The Phase 12 implementation uses the `hypothesis` Python
package. This is the **only** new pip dependency introduced in
v4 (beyond sympy, scipy, numpy, pint, pyyaml already present).

#### 5.2.3 Check C — High-precision numeric evaluation via `mpmath`

`mpmath` (sympy's internal numerical backend) is evaluated at
**50 decimal places** of precision at the canonical sample
point and compared against sympy's default 15-decimal-place
evaluation. Disagreement beyond 10 decimal places flags the
formula as **numerically fragile** and requires investigation
before the value enters the ledger.

**Honesty label:** v4 calls this check "high-precision
evaluation via mpmath," NOT "cross-CAS verification." mpmath
IS sympy's numerical backend; the two are not independent. The
value of this check is catching *numerical fragility* within
sympy itself, not providing orthogonal cross-engine
verification.

#### 5.2.4 Check D — Truly independent numeric backend (python-flint / gmpy2)

The **only** genuinely orthogonal numeric check available
without shelling out to Mathematica/Maple is to use a
different low-level arithmetic library that does not share
code paths with sympy.

**v4 plan:** add `python-flint` (Arb-based interval
arithmetic) as a soft dependency. When available, it provides
rigorous interval bounds on the canonical sample evaluation.
When not available, the check is skipped with a warning
recorded in the verification result; the other three checks
still run.

```python
try:
    from flint import arb, ctx
    ctx.prec = 200           # 200 bits = ~60 decimal places
    a = arb(board_value_exact)
    b = evaluate_formula_via_flint(board_formula, params_as_arb)
    if not (a & b):          # interval intersection empty
        return FAIL("python-flint interval disjoint from board claim")
    return PASS(f"python-flint: board value lies in flint interval {b}")
except ImportError:
    return SKIPPED("python-flint not installed; Check D omitted")
```

`python-flint` is Python bindings for Arb (Fredrik Johansson's
rigorous ball arithmetic library), which shares no code with
sympy. Installing it gives the pipeline a genuinely
orthogonal numeric backend.

**Dependency status:**
- **Phase 12 MVP:** Check D is best-effort. If `python-flint`
  isn't installed, the pipeline runs with A + B + C and logs
  the skip.
- **Phase 13:** Check D is a hard requirement. If
  `python-flint` isn't available, the verification fails and
  the reference value cannot enter the ledger.
- **Tracked technical debt:** integration of Mathematica or
  Maple via `wolframclient` / `sage` as a third truly
  independent path. Deferred to Phase 15+.

#### 5.2.5 Four-check aggregation

For a board-sourced reference value to enter the ledger:

| Check | Must Pass |
|---|---|
| A — symbolic equivalence (canonicalization pipeline) | **Yes** |
| B — property-based randomized sampling | **Yes** |
| C — high-precision mpmath evaluation | **Yes** |
| D — python-flint interval check | **Best-effort in Phase 12, hard requirement in Phase 13+** |

Any single failure → `BOARD_HALLUCINATION_DETECTED`, escalate.
Any `SYMBOLIC_EQUIVALENCE_UNDECIDABLE` on Check A →
`REFERENCE_UNRESOLVED`, user Decision Matrix fires per §11e.

### 5.3 Escalation on disagreement

- **All 3 agree + sympy verifies**: ACCEPTED, confidence=1.0
- **2 of 3 agree + sympy verifies**: ACCEPTED, confidence=0.67
- **≥2 agree + sympy disagrees**: `BOARD_HALLUCINATION_DETECTED`,
  architect manually investigates
- **<2 agree**: `REFERENCE_UNRESOLVED`, architect re-queries or
  falls back to hand-authored reference with an external citation

Every outcome is ledger-recorded with full provenance (all three
model replies, the sympy verification step, the decision).

## 6. Experiment authority — design constraints for Phase 19

The board will eventually be able to propose experiments. Guard
rails, baked in from the start:

1. **Default READ-only.** Every sensor adapter starts with only
   the `READ` capability. Adding WRITE / CONTROL / ACTUATE
   requires a code change in the adapter file itself — not a
   config flag, not an env var.
2. **Envelope-gated actuation.** Any `write()` or `actuate()`
   call requires an `ExperimentEnvelope` that has received
   approval tokens from ≥2 board members AND a human gate for
   first-time actions.
3. **Time + magnitude bounds.** Every envelope declares maximum
   time duration and per-parameter magnitude bounds. The
   framework enforces these at the adapter level — the model
   cannot override.
4. **Rollback plan mandatory.** Every envelope must specify the
   "safe default state" to return to on failure or time-out.
   The engine runs the rollback if any fault is detected.
5. **Provenance.** Every actuation is ledger-recorded with:
   proposer model, envelope text, approval tokens, sensor+
   actuator IDs, timestamps, result, rollback status.
6. **First-time human gate.** The first instance of a given
   envelope shape requires a human approval click in a minimal
   web UI (Phase 19 deliverable). Repeated identical envelopes
   can auto-approve after the first run.
7. **No credentials in prompts.** The model receives descriptive
   metadata about available actuators (units, ranges) but never
   the credentials to call them. The framework is the only
   caller.
8. **Kill switch.** A single ledger entry kind
   (`actuation_halt`) immediately blocks all future envelopes
   until manually cleared.

The board's voting rule for experiment envelopes is stricter
than for couplings: **unanimous approve** required for actuation,
not just majority.

## 7. Phased plan

| Phase | Deliverable | Dependencies |
|---|---|---|
| 12 | Canonical problems + board-sourced reference values for 16 equations | `ai_consensus.py` |
| 13 | Composite problem catalog (starter 10) with board-cited references | Phase 12 |
| 14 | Transducer library + literature index + realization grounding step | Phase 13, `ai_consensus.py` |
| 15 | Adversarial pre-reg expanded to ~30 items + board rerun with full evidence | Phase 14 |
| 16 | `SensorAdapter` interface + fixture implementation + 2 historical adapters (NOAA, Polygon) | Phase 15 |
| 17 | First flagship coupling passing all 4 evidence levels (Newton+Hooke via phone IMU rig) | Phase 16 + physical rig |
| 18 | Continuous ledger update loop (sensor replay + drift detection) | Phase 17 |
| 19 | Experiment authority framework (capability + envelope + approval) | Phase 18 |
| 20 | Quantum specialist: Rigetti VQE on SHO Hamiltonian via Braket | Phase 19 |

## 8. What the board is reviewing right now

Not the detailed code — the **architectural frame**. Specifically:

1. **Is the thesis right?** "Coincidence vs coupling = executable
   realization." Is that a defensible distinction?
2. **Is the evidence hierarchy right?** L1 → L4, with promotion
   gated by citations AND execution AND sensor agreement.
3. **Is board-sourced reference values the right research
   mechanism?** Or is it circular (the board is being asked to
   generate its own source material)?
4. **Is the transducer library the right fix** for OpenAI's
   "no named transducer" objection, or is it a bandage?
5. **Is the experiment authority framework's guard rail system
   sufficient?** Specifically the default-READ invariant and the
   envelope-gated actuation.
6. **What are we missing?** Every prior attempt had a fatal flaw
   that its authors didn't see. What might ours be?

The board's verdict should be: APPROVE, MODIFY (with specific
concerns), or REJECT (with a better path). If unanimous APPROVE,
architect proceeds to Phase 12. If MODIFY, architect revises
and resubmits. If REJECT, architect escalates to the user for
a strategic reset.

## 8a. Confidence aggregation across L1–L4 — v3 revised labels

**v3 change (per board v2 review — OpenAI monotonicity concern):**
the label ordering in v2 was non-monotonic (PROVED at 0.50
threshold but GROUNDED at 0.80 caused confusion). v3 fixes this
with strictly-increasing rigor:

| Label | Threshold | Minimum levels | Extra gate |
|---|---|---|---|
| `CONJECTURAL` | C < 0.30 | L1 optional | — |
| `EMPIRICAL` | C ≥ 0.30 | L1 + L2 | ≥2 board APPROVE |
| `PROVED` | C ≥ 0.60 | L1 + L2 + L3 | unanimous board APPROVE |
| `GROUNDED` | C ≥ 0.85 | L1 + L2 + L3 + L4 | live-sensor c4 > 0.5 |
| `DUALITY` | n/a | L1 + L2 + L3 | sidebar status (§8a.1) |

Rigor is now strictly monotonic in both the confidence
threshold and the required evidence levels. A `PROVED` coupling
has passed more evidence levels and a stricter consensus gate
than `EMPIRICAL`, which has both stricter than `CONJECTURAL`,
and `GROUNDED` is above all three.

### 8a.1 The `DUALITY` sidebar status (v3, per board v2 review)

OpenAI v2: *"mathematical isomorphisms (e.g., Wick rotation)
risk being misclassified as physical couplings without an
explicit analytic-continuation policy."*

Mathematical dualities — Wick rotation (t → −iτ), log-price
substitution (S → exp(x)), certain RG flows, Kolmogorov filter
↔ Schrödinger — produce structurally-identical equations under
analytic continuation but do NOT describe the same physical
substrate. Schrödinger ↔ heat via Wick is algebraically
equivalent but you can't put a real-time-domain thermometer in
a Schrödinger experiment.

**Policy:** A coupling whose only L3 evidence is "these two
equations become identical under analytic continuation" is
marked as `DUALITY`, not `PROVED`. It can accumulate L1 + L2
+ L3 confidence but cannot be promoted past `EMPIRICAL` unless
it ALSO has L4 evidence from both domains independently —
i.e., a real-time-domain experiment agrees with the heat-
equation solution AND a real quantum experiment agrees with
the Schrödinger prediction. Only then does the duality rise to
`GROUNDED`.

The `DUALITY` label is recorded in the ledger as a separate
kind (`mathematical_duality`) distinct from
`tier1_equivalence`, `tier2_similarity`, `tier3_conjectural`.
The sieve's structural matcher automatically flags any
substitution involving `i*t`, `−i*t`, `log(x)`, or
`exp(-r*t)` as a duality candidate for this path.



Gemini v1 flagged as a missing piece: "A formal strategy for
managing uncertainty and error propagation. How do tolerances
from L1 (implementation), L2 (reference value), and L4 (sensor
noise) combine to determine the final confidence in a coupling?"

**v4 revision (FCS C1).** v3 used a raw multiplicative rule
`C = c1·c2·c3·c4`. Three Round-1 reviewers independently flagged
this as brittle: a single zero-level collapses the whole score,
the independence assumption between levels was never validated,
and promotion thresholds were not calibrated on any benchmark.
v4 replaces it with a **calibrated log-evidence accumulator with
per-level floors**, and rewrites each per-level score as an
explicit likelihood-ratio-style contribution rather than an
ad-hoc scalar.

### 8a.1 Per-level log-evidence contributions

Each level contributes a log-evidence value `ℓ_i` whose sign
indicates support-for vs evidence-against, whose magnitude is
bounded, and which never collapses a composite to zero on a
missing level. The per-level floor is `log(0.01) = −4.6`; the
ceiling is `log(100) = +4.6`. Both are symmetric around zero
so an absent level contributes `ℓ = 0` (neutral) and a
strongly-contradicted level contributes up to `ℓ = −4.6`.

- **L1 — unit test pass.** The equation's canonical problem
  either passes pytest (`ℓ1 = +3.0`) or fails (`ℓ1 = −4.6`).
  If no unit test has been authored for the equation yet,
  `ℓ1 = 0` (neutral). Binary in practice, with a defined
  "unknown" state.

- **L2 — composite execution vs reference.** Let the relative
  deviation be `δ = |computed − reference| / |reference|` and
  the declared tolerance be `τ` (default 0.02). Then:
  - `δ ≤ τ/4`: strong agreement → `ℓ2 = +3.0`
  - `τ/4 < δ ≤ τ`: within tolerance → `ℓ2 = +3.0 · (1 − δ/τ)`
  - `τ < δ ≤ 5τ`: outside tolerance, contradicts → `ℓ2 = −2.0 · log10(δ/τ + 1)`
  - `δ > 5τ`: severe disagreement → `ℓ2 = −4.6`
  - no composite available: `ℓ2 = 0` (neutral)

- **L3 — independent primary citations.** Let `n` = number of
  DOI-level-independent primary citations produced by the
  review board for this coupling. "DOI-level independent"
  means citations that cannot be traced to the same source
  document, the same review article, or the same textbook
  chapter; §11c specifies the independence test. Then
  `ℓ3 = min(3.0, 1.5 · log2(1 + n))`, with a hard floor of `0`
  (citations never count against a coupling). Zero citations
  contribute `0`; 2 independent citations contribute `~2.4`;
  5 contribute `~3.8` capped at `3.0`.

- **L4 — live sensor agreement.** Bayesian posterior update
  from rolling-window sensor readings against the composite's
  predicted observable. Using Gaussian likelihoods with
  declared sensor noise `σ_s` and model uncertainty `σ_m`, and
  N readings `y_i`:
  ```
  ℓ4 = (1/N) · Σ_i [ −(y_i − μ_model)² / (2·(σ_m² + σ_s²))
                     − (1/2) · log(2π · (σ_m² + σ_s²)) ]
       + N-dependent normalization constant
  ```
  The normalization is chosen so that perfect agreement over
  ≥10 readings contributes `ℓ4 = +3.0` and systematic
  disagreement contributes `ℓ4 = −4.6`. If no sensor data
  exists, `ℓ4 = 0` (neutral — NOT a penalty).

### 8a.2 Log-evidence accumulator

Composite log-evidence is the **sum** of the level contributions:

```
log_C = ℓ1 + ℓ2 + ℓ3 + ℓ4
```

Equivalently, `C_geom = exp(log_C / 4)` if we want a geometric-
mean-in-confidence-space view, but the protocol operates on
`log_C` directly because it is the natural scale for
likelihood-ratio accumulation.

**Non-brittleness guarantee.** Because each level has a floor of
`−4.6` and the "unknown" state is 0 (neutral, not penalising),
a coupling with strong L1 + L2 + L3 evidence but no L4 sensor
data yet will have `log_C = 9.0 + 0 = 9.0` — enough for
`PROVED` promotion without any sensor data. This is the
direct non-brittleness fix the Round-1 FCS required.

### 8a.3 Promotion thresholds (calibrated to the log-scale)

| Label | `log_C` | Required levels | Board gate |
|---|---|---|---|
| `CONJECTURAL` | `log_C < 2.0` | any | — |
| `EMPIRICAL` | `log_C ≥ 2.0` | L1 + L2 | ≥2 of 3 board approve |
| `PROVED` | `log_C ≥ 6.0` | L1 + L2 + L3 | unanimous board approve |
| `GROUNDED` | `log_C ≥ 9.0` | L1 + L2 + L3 + L4 | unanimous + `ℓ4 ≥ 1.5` |
| `DUALITY` | n/a | L1 + L2 + L3 | sidebar status, cannot pass GROUNDED without independent L4 from both domains |

These thresholds are **v4 initial calibration**. They will be
validated empirically in Phase 12 against the must-surface and
must-reject items in the adversarial pre-registration set
(§14). If the current thresholds surface fewer than 10 must-
surface couplings or admit any must-reject, the thresholds are
considered miscalibrated and must be re-tuned via a board
consensus query on the held-out adversarial set. Calibration
provenance is ledger-recorded.

### 8a.4 Independence assumptions, honestly declared

The log-evidence accumulator assumes the four levels are
approximately independent. This is NOT true in general: a
sensing gap at L1 can cause an L2 composite failure, an L3
citation can be downstream of the same experimental paper an
L4 sensor is indirectly validating, etc. v4 does not claim
full independence. Instead:

1. Every evidence level is logged with its **provenance chain**
   so a later audit can detect dependency (e.g., "L2 reference
   value came from the same paper L3 citation #1 cited").
2. The Phase 12 pre-registered adversarial test includes a
   **dependency-audit check**: for each known-good coupling,
   we re-run the confidence accumulator after REMOVING one
   level's evidence; the remaining `log_C` should still cross
   the correct threshold. If it doesn't, the removed level
   was load-bearing in a way that reveals dependency.
3. Known dependency cases are documented in
   `TECHNICAL_DEBT.md` as "dependency audit: L2 and L3 share
   source X for coupling Y" and the board is warned in the
   prompt for any future review involving that coupling.

This is not a proof of independence — it is an honest
acknowledgment that independence is an assumption and an
empirical protocol for detecting when it is violated. A
formal Bayes-factor framework with declared joint likelihoods
is noted in `TECHNICAL_DEBT.md` as a Phase 14+ refinement.

## 8b. Domain taxonomy (NEW, per board v1 review)

Gemini v1 flagged as a missing piece: "A formal definition of
what constitutes a 'domain.'"

**Definition.** A *domain* is an equivalence class of equations
under the relation: two equations share a domain iff the
majority of their variables' QUDT QuantityKind URIs fall in the
same top-level QUDT `SystemOfQuantities` subtree. This is
bootstrap-able from the existing per-variable property URIs
without additional authoring.

Top-level QUDT SystemOfQuantities subtrees (simplified):
- `SOQ_ISO-80000-3-Space-And-Time`
- `SOQ_ISO-80000-4-Mechanics`
- `SOQ_ISO-80000-5-Thermodynamics`
- `SOQ_ISO-80000-6-Electromagnetism`
- `SOQ_ISO-80000-7-LightAndRadiation`
- `SOQ_ISO-80000-8-Acoustics`
- `SOQ_ISO-80000-9-PhysicalChemistryAndMolecularPhysics`
- `SOQ_ISO-80000-10-AtomicAndNuclearPhysics`
- `SOQ_ISO-80000-11-CharacteristicNumbers` (dimensionless)
- plus project-local extensions for biology, finance, information

The domain-adjacency matrix (`framework/domain_adjacency.py`) is
re-keyed by SOQ id. This removes the ad-hoc string matching on
`"classical_mechanics"` etc. and lets the sieve's Gate 2 operate
against an externally-maintainable ontology.

## 8c. Experiment authority governance (NEW, per board v1 review)

Gemini v1 flagged as a missing piece: "A governance model for
the Experiment Authority beyond the technical guards. Who is
accountable for the 'human gate' and under what protocol? How
are budgets allocated?"

**Governance rules** (binding for Phase 19):

1. **Project owner = sole human gate.** For the project's
   current scope, the user (project owner) is the only human
   authorized to approve first-time experiment envelopes. Future
   team expansion requires an explicit code-level change to
   add additional approver identities.
2. **Budget per-experiment envelope.** Every envelope declares
   a numerical budget in USD (for cloud experiments) or a
   physical-cost budget (for sensor/actuator experiments). The
   envelope cannot run until budget is attached and the owner
   has signed off on spend.
3. **Accumulated-spend kill switch.** A project-level spend
   ceiling is declared in `labs_v2/EXPERIMENT_BUDGET.yaml` with
   a daily and monthly cap. The ledger tracks accumulated spend.
   When accumulated spend exceeds the cap, all subsequent
   envelopes are blocked until the owner manually resets.
4. **Rollback audit.** Every completed envelope writes a
   "rollback verified" ledger entry within 60 seconds of
   experiment end. If the rollback entry is missing, the next
   envelope attempt is blocked until a human certifies the
   system is in a safe state.
5. **Postmortem on failure.** Any envelope whose rollback fails
   or whose observables exceed the declared magnitude limits
   triggers an automatic postmortem ledger entry. The next
   envelope of the same shape is blocked until the postmortem
   is manually reviewed and cleared.

## 8d. Model-drift and canonical maintenance (NEW, per board v1 review)

Gemini v1 flagged as a missing piece: "How will the canonical
problems, composite catalog, and transducer library be kept
up-to-date and re-validated as the underlying foundation models
of the review board are updated or replaced?"

**Rule.** Every 90 days (or on explicit user invocation), the
engine re-runs:
1. All canonical problem unit tests (L1 — these are code, not
   model output; these should never drift)
2. All composite notebook executions (L2 — these are also code,
   should not drift)
3. All board-sourced reference value queries (L3 — THIS is the
   drift-risk surface)

For (3), the engine re-queries the board for each reference
value and compares against the ledger's recorded consensus. If
a new query disagrees with the stored value:
- Within orthogonal-verification tolerance → silent update (the
  new value replaces the old, with audit trail)
- Outside tolerance → `CANONICAL_DRIFT_DETECTED` flag, architect
  investigates. Possible causes: model update changed textbook
  recall, the original was a consensus hallucination that
  escaped sympy verification, or the underlying physics
  understanding evolved.

The `CANONICAL_DRIFT_DETECTED` status blocks any new coupling
promotions until the drift is resolved — we don't want the
engine accepting new discoveries while its own foundations are
in flux.

## 9. Open questions for the board

- Is "board-sourced reference values" honest given that the
  board is both the source and the reviewer of the same evidence?
  How do we break the circularity? One option: for every
  board-sourced reference, require a local sympy sanity check
  that the value satisfies the governing equation symbolically.
  Another: the board sources the formula, the architect computes
  the value, and the board cross-validates against its own reply.
- The sieve is currently finding ~14 coupling candidates across
  16 equations. At N=100 equations (Phase 20+), the candidate
  count grows quadratically. Do we need a sampling strategy
  before the corpus expands, or will the two-gate prefilter
  continue to scale?
- Should the adversarial pre-reg list itself be board-sourced?
  If the board writes the traps, can the board also write the
  correct rejections? How do we avoid self-dealing?
- For the transducer library: what happens when a coupling
  requires a transducer that isn't yet catalogued? Do we stall,
  or do we emit a conjecture ("there should be a transducer
  here named X with dimensions Y")?
- For live sensors: what's the tolerance threshold? At 1%
  agreement, the board may still accept a coupling that's
  physically wrong (noise masking error). At 0.1%, we may never
  accept anything.

---

## 11a.5 Cost-neutrality disclaimer (v4, user-directed, binding)

**v4 change.** Every Phase A, Phase B, editor, and discharge
prompt in `framework/ai_consensus.py` now prepends a
cost-neutrality disclaimer. Reviewers are explicitly forbidden
from using effort, schedule, preparatory work, paradigm shift,
engineering capacity, or "this would delay shipping" as
reasons to prefer one option over another.

The full text of the disclaimer is in
`ai_consensus.COST_NEUTRALITY_DISCLAIMER`. Key excerpt:

> IMPORTANT — COST NEUTRALITY. Before you evaluate the
> submission below, note that the project owner has explicitly
> declared that **time, effort, implementation cost, and
> engineering capacity are NOT constraints** on this
> architecture. You are forbidden from using any of the
> following as reasons to prefer one option over another:
> "this would require significant preparatory work," "this is
> a paradigm shift that would take effort to implement," "this
> would delay shipping," "a simpler approach would be faster
> to build," "the scope is ambitious," "this is a lot of
> engineering work."
>
> Evaluate the submission on technical merit alone. If a
> design is ambitious but sound, that is APPROVE-worthy. If a
> design is cheap but wrong, that is REJECT-worthy. Cheap-and-
> wrong is never better than ambitious-and-correct.

**Why.** During Round 1 review, the board repeatedly drifted
toward "prefer the less-ambitious option because it ships
faster" framing. The project owner identified this as
systemic bias inherited from the reviewers' training data
(which models real-world developer time as a binding
constraint). For this project, it is not. The disclaimer
eliminates the drift at the prompt level.

**Architectural rule.** Any future prompt builder added to
`ai_consensus.py` MUST prepend `COST_NEUTRALITY_DISCLAIMER`.
CI (when it exists) will grep for this.

## 11e. Scope-frozen discharge protocol (v4, user-directed, binding)

**v4 change.** The user directed a formal-verification-style
protocol for handling multi-round reviews. After Round 1
produces a Frozen Concern Set (FCS), all subsequent rounds
operate in **discharge-only mode**: reviewers may only
evaluate whether each FCS item has been addressed. They cannot
raise new concerns. If they try, the editor records a process
violation and escalates to the user.

### 11e.1 Round definitions

| Round | Mode | What happens |
|---|---|---|
| 1 | **Discovery** (unrestricted) | Four-phase protocol: Phase A independent → Phase B informed → Phase C editor synthesis. Editor's Phase C output includes the FCS = numbered list of required modifications. FCS becomes immutable at the end of Round 1. |
| 2+ | **Discharge** (scope-frozen) | `AIConsensusBoard.discharge_round()`. Each reviewer scores each FCS item as `addressed` / `partially_addressed` / `not_addressed` with justification. Editor synthesizes a binding verdict: APPROVE (all high-severity addressed), MODIFY (some partially addressed, convergence plausible), REJECT (regression), or ESCALATE (irresolvable disagreement → Decision Matrix to user). |

### 11e.2 Process violation handling

If a reviewer in a discharge round tries to raise a new
concern (indicated by `new_concerns_attempted > 0` in their
JSON reply), the editor immediately flags a process violation
and the decision matrix includes an "escalate to user — new
concerns arose, should FCS be reopened?" option. The user is
the only authority that can reopen an FCS — reviewers cannot
do it unilaterally.

### 11e.3 Convergence guarantee

The discharge protocol has a finite termination: each round
either approves (done), modifies (next round, max 2 rebuttal
cycles), or escalates (user decides). There is no case where
the board iterates indefinitely — if Round 2 produces
unresolved concerns AND the editor's Round 3 produces the
same unresolved set, the Decision Matrix fires and the user
picks an option from an explicit labeled list.

### 11e.4 Implementation

Built in `framework/ai_consensus.py`:
- `FrozenConcern` dataclass with `concern_id`, `headline`,
  `raised_by`, `severity`, `detail`
- `DischargeScore` dataclass per reviewer per concern
- `DischargeReply` dataclass per reviewer per round
- `DischargeResult` dataclass per round
- `AIConsensusBoard.discharge_round()` method with scope-
  frozen prompt construction and editor synthesis
- `_build_discharge_prompt()` — explicitly forbids new
  concerns in the prompt text
- `_build_discharge_editor_prompt()` — editor is told to
  output a Decision Matrix on escalation

The FCS from Round 1 is passed in as a list of
`FrozenConcern` objects. The submitter passes its revision
text as `submitter_revision`. The protocol is deterministic
under the same inputs.

## 11f. L0 dimensional type system (v4, addresses FCS C4)

**v4 change.** Addresses FCS C4 (OpenAI Round 1: "Typed
canonical form (L0) and unit system are under-specified").

v3 relied on pint + QUDT URIs attached to each variable, but
did not enforce dimensional consistency during transducer
composition or randomized parameter sampling. v4 adds a
formal **dimensional type system** on top of the existing
QUDT annotations:

### 11f.1 Type layer over QUDT

Each variable in `equation.yaml` already carries a QUDT
QuantityKind URI via the I-ADOPT descriptor. v4 adds a
runtime type with:

- Base dimensions as a 7-tuple `(L, M, T, I, Θ, N, J)` of
  rational exponents, derived from UCUM/QUDT
- Unit prefix and magnitude scale
- Optional "provenance" tag: `declared` (from YAML),
  `inferred` (computed from composition), `asserted` (user-
  added without justification — triggers warning)

### 11f.2 Dimensional inference and unification

When two variables are composed via a transducer or a
canonical form's operation, the resulting type is inferred
by unifying the operand types under standard dimensional
algebra:
- Add / subtract: both operands must unify to the same type
  (no implicit coercion)
- Multiply / divide: exponents add / subtract element-wise
- Power: exponents scale; fractional powers are allowed but
  flagged for review
- Transcendental functions (`exp`, `log`, `sin`, etc.): the
  argument must be dimensionless; the result is dimensionless

Inference failure is a hard stop — the equation is rejected
at load time, not at runtime, not silently.

### 11f.3 Enforcement in composition

When the Phase 13 composite generator assembles an ODE
system from two equations plus a transducer, every
substitution step runs through the type checker. A transducer
that claims `F = K_t · I` (force = motor constant · current)
must declare the dimensions of `K_t` (force / current =
N/A = V·s/m), and the inference runs:

```
type(F) = type(K_t) · type(I)
[M L T⁻²] ?= [M L T⁻³ I⁻¹] · [I]
[M L T⁻²]  = [M L T⁻²]   ✓
```

If any step fails, the composite is rejected as
`DIMENSIONALLY_INCONSISTENT_COMPOSITE` before execution.

### 11f.4 What this changes for Phase 12

Every canonical problem's `problems.yaml` now declares the
dimensional signature of each variable explicitly. Reference
values from the board must be verified dimensionally as part
of the three-way check in §5.2 — not just numerically.

## 11g. Port-Hamiltonian transducer contracts (v4, addresses FCS C6)

**v4 change.** Addresses FCS C6 (OpenAI Round 1: "Transducer
formalism lacks explicit energy-flow or port-Hamiltonian
contracts; composition preserves conservation by construction,
not by post-hoc numeric check").

v3 treated transducers as named constitutive relations
between (effort_a, flow_a) and (effort_b, flow_b) with a
single coefficient. v4 formalizes them as **port-Hamiltonian
subsystems** with explicit energy-storage, dissipation, and
power-conservation contracts.

### 11g.1 Port-Hamiltonian form

Every transducer in `labs_v2/transducers.yaml` is now
represented as a tuple:

```yaml
- id: TRANSDUCER-MOTOR
  ports:
    - {name: mechanical, effort: Force, flow: Velocity}
    - {name: electrical, effort: Voltage, flow: Current}
  energy_state_vars: []     # an ideal transducer stores no energy
  dirac_structure:           # the core algebraic constraint
    - "F_mech = K_t · I_elec"
    - "V_elec = K_t · v_mech"
  power_conservation: "F_mech · v_mech − V_elec · I_elec = 0"
  constitutive_type: "ideal_gyrator"
  sign_convention: "passive_into_ports"
  citation: ["Paynter 1961 §5.2", "Karnopp 2012 Ch 9"]
  sourced_by: [claude-opus-4-6, openai-gpt-5, gemini-2.5-pro]
```

### 11g.2 Composition checks the Dirac structure, not the numbers

When two equations are composed via a transducer, the
framework verifies at load time that:

1. Every port's effort and flow have dimensions consistent
   with their declared QUDT property
2. The Dirac structure equations are satisfied symbolically
   by the claimed transfer functions (sympy verifies)
3. `power_conservation == 0` symbolically on the
   constitutive relations — NOT as a post-hoc numeric check
4. The sign convention is consistent across the composite

A transducer whose composition breaks power conservation is
rejected as `NON_PASSIVE_COMPOSITE` at load time. The
previous v3 approach (post-hoc numeric Tellegen check in
Phase 6) is retained as a belt-and-braces runtime
verification, but the type-level check fires first.

### 11g.3 What this changes for conjectural transducers

A `ConjecturalTransducer` proposed by the sieve must now
specify the Dirac structure and power-conservation relation
as part of the proposal. The AI review board cannot approve
a conjectural transducer that lacks these fields — the
prompt template requires them.

## 11h. Failure Investigation Protocol (v4, user-directed, binding)

**v4 change.** The user directed an explicit protocol for
handling evidence-level failures: when a unit test, composite
execution, or sensor disagreement fails, the engine MUST NOT
loosen tolerances, swap to a simpler formula, or "refine"
the equation to make it pass. That is corner-cutting and
produces false confidence.

### 11h.1 The protocol — binding sequence

On any L1/L2/L3/L4 failure, the engine enters
`INVESTIGATION_PENDING` state and runs the following fixed
sequence, no shortcuts:

**Step 1 — State audit.** Enumerate every variable the
equation depends on. Is the engine observing each one? A
failure where a relevant variable is unobserved is a
**sensing gap**, not an equation error. Fix the observation,
not the equation.

**Step 2 — Assumption audit.** Re-read the equation's
declared assumptions in `equation.yaml`. Is any assumption
violated by the failing test's conditions? A failure under a
violated assumption is an **assumption violation**. Either
reformulate the test or move it to a different equation that
fits the regime.

**Step 3 — Literature RAG for known failure modes.** For the
specific equation under investigation, query the per-equation
`failure_modes/` index for known failure modes, edge cases,
and corrections documented in primary sources. Every equation
gets a `failure_modes.md` file populated by board-driven
literature search. Before any modification is proposed, this
file must contain at least 3 citations from peer-reviewed
primary sources discussing the specific observed failure.

**Step 4 — Board failure investigation.** The state audit,
assumption audit, and literature findings are compiled into a
**failure report**. The AI review board runs a specialized
`investigate_failure()` query on it (specialist personas +
cost-neutrality + academic rigor standard) and produces one
of three verdicts:

- `sensing_gap` — no equation change; add the missing
  observable to the test
- `assumption_violated` — no equation change; reformulate or
  move the test
- `equation_inadequate` — the gigantic-deal path; escalates
  to the user with a full Decision Matrix showing evidence,
  literature chain, proposed alternative formulation with its
  own citations, and the risks of each option. User is the
  only authority that can promote this to an equation change.

**Step 5 — Ledger entry.** The investigation record is
written to the ledger as `kind="failure_investigation"`,
append-only, with full provenance.

### 11h.2 Binding rule

An equation's `canonical_form` in `equation.yaml` may not be
edited except by a resolved `failure_investigation` with an
`equation_inadequate` verdict that has explicit user
approval. Tolerance loosening on a reference value requires
the same procedure. Anything else is a corner cut and the
framework rejects the change at CI time.

## 11i. Academic rigor standard — Nobel-prize bar (v4, user-directed, binding)

**v4 change.** The user directed that the engine's bar is not
internal board consensus but **external academic peer review**
— anything the engine finds must in principle survive peer
review at a top journal and decades of replication attempts.
Internal board agreement is necessary but not sufficient.

### 11i.1 Academic readiness checklist

Every PROVED or GROUNDED coupling must pass this checklist
before promotion:

- [ ] **Quantitative prediction with declared uncertainty.**
  Not "these couple" but "under conditions X, observable Y =
  Z ± ε at declared confidence level."
- [ ] **Systematic error analysis.** What systematic effects
  could produce the observed agreement without the claim being
  true? Enumerate and address each.
- [ ] **Independent replication pathway.** A specific
  experiment that a third party could run, with listed
  equipment, parameter ranges, and expected results. If no
  such pathway exists, the coupling cannot reach GROUNDED.
- [ ] **Priority / novelty search ≥10 citations.** Not the 3
  RAG citations used for L3 evidence — a full literature
  review. Engages with claims that contradict or complicate
  this one.
- [ ] **Honest limitations section.** What the claim does NOT
  say. Edge cases where it would fail. The specific
  assumptions on which it rests. Regimes outside which it is
  invalid. Default: the limitations section is LONGER than the
  strengths section.
- [ ] **Multiple-testing correction.** Bonferroni or FDR
  applied across the full adversarial pre-reg corpus.
- [ ] **Prior-work engagement with adversarial citations.**
  Cite work that contradicts the claim, not just work that
  supports it.
- [ ] **Hall-of-mirrors check.** The claim must be re-
  state-able in a form that doesn't depend on our specific
  framework — portable to Mathematica, SymPy-only, or a
  Modelica co-simulation.

A coupling missing ANY checklist item stays at EMPIRICAL
regardless of internal board consensus.

### 11i.2 Rubric extension

Every coupling-review rubric (Phase 12+) gains a new
dimension:

- `academic_defensibility` — 1 (board agreed but a real
  peer reviewer would reject) to 5 (claim is bulletproof
  against hostile external review)

This dimension is weighted **2× in the editor's synthesis**
because it is the hardest to satisfy and the most
consequential.

### 11i.3 External-standard instruction in reviewer prompts

Every coupling-review Phase A and Phase B prompt now carries
this standing instruction:

> Evaluate this submission as if you were a reviewer at
> Nature / Science / PRL. Would it survive peer review by
> human domain experts? Would it survive replication by a
> hostile competing lab? If submitted to a Nobel committee
> decades from now, would the methodology withstand
> historical scrutiny? Your role is not to be lenient; it is
> to anticipate the hardest external review this finding
> would face.

### 11i.4 Hall-of-mirrors check implementation

Every PROVED coupling must include a `portability_proof`
file in its ledger entry:

- The coupling's composite equation in pure LaTeX (no
  framework-specific notation)
- A SymPy-only script that reproduces the numerical result
  without importing `framework.*`
- A description of how to port the coupling to a FMI-
  compatible Modelica block, without our code

If any of these three cannot be produced, the coupling is
self-referential and stays at EMPIRICAL.

## 11a. Four-phase AI review board protocol (v3, academic mirror)

**v3 change.** The AI review board's voting protocol is
upgraded from a single-pass query to a **four-phase protocol**
modelled directly on real academic peer review. Each phase
mirrors a standard peer-review mechanism that is near-
universal across Nature, Science, NeurIPS, ICML, PRL, and
major medical journals.

**Phase A — Independent draft + COI declaration.** Each of the
three reviewer models receives the query in isolation. No
cross-contamination. Each is given a **specialist persona**
matched to the submission's topic (e.g., for a thermal
coupling: "senior thermodynamicist"; for this design review:
"senior scientific-software architect"). Each model begins its
reply with a **Conflict-of-Interest self-declaration** — did
it encounter this specific formulation during training? If yes,
declare it. The COI declaration is logged alongside the
review; it does not disqualify the reviewer but makes
potential training-data leakage auditable. Each reviewer then
produces a draft rubric-scored verdict.

**Phase B — Informed rebuttal-aware vote.** The three Phase-A
drafts are consolidated into a **board briefing document** that
shows each model what the other two said, attributed. Each
model is asked to produce its FINAL rubric-scored verdict,
explicitly addressing the other reviewers' concerns: do you
agree, disagree, or update your position? This second pass is
what the voting rule evaluates; Phase A is archived as audit
provenance. Phase B enforces engagement — a concern only one
model raised either persuades the other two (then it's real)
or is pushed back against (then it's contested).

**Phase C — Editor synthesis.** A **fourth, distinct model call**
(Claude Opus in the "editor" persona, distinct from the Phase
A/B reviewer personas) reads all three Phase-B verdicts and
produces an **editorial decision**:
- Binding verdict (approve / modify / reject)
- Rationale that weights reviewer reasoning quality, not vote count
- Consolidated list of required modifications
- Flag for fundamental reviewer disagreement, if any

The editor is empowered to override a naive vote count when
one reviewer's reasoning is visibly stronger. This is
standard editorial practice at every legitimate venue. In our
current automated setup, a deterministic fallback rule
(2-of-3 APPROVE → approve) still applies if the editor call
fails.

**Phase D — Bounded rebuttal (optional, max 2 cycles).** If
the editor's decision is MODIFY with specific required
changes, the submitter is allowed one **rebuttal cycle**:
produce a revision that addresses the required changes, and
resubmit for a second Phase B + C. A maximum of 2 rebuttal
cycles are allowed before the submission is treated as
permanently in its current state. This mirrors the
author-response phase standard at CS conferences (NeurIPS,
ICML, ICLR) and bounds the iteration budget.

### 11a.1 Rubric-scored verdicts (five dimensions, 1–5 each)

Every reviewer in Phase A and Phase B produces a scored rubric.
For **architecture / design-doc reviews** the rubric is:

| Dimension | 1 (reject) | 5 (excellent) |
|---|---|---|
| `thesis_soundness` | Core argument is wrong | Core argument is provably correct and novel |
| `technical_feasibility` | Proposed mechanism can't work | Mechanism is clearly buildable and sound |
| `falsifiability` | Cannot be proven wrong | Explicitly falsifiable, with tests |
| `prior_art_awareness` | Ignorant of existing work | Fully engaged with state of the art |
| `honest_scope` | Overpromises | Honest about what it can and cannot do |

For **coupling hypothesis reviews** the rubric is:

| Dimension | 1 (reject) | 5 (excellent) |
|---|---|---|
| `physical_plausibility` | Nonsense coupling | Canonical textbook coupling |
| `dimensional_consistency` | Units mismatch ignored | Transducer dimensions verified |
| `literature_grounding` | No citation found | Multiple independent primary sources |
| `falsifiability` | No composite test possible | Composite executes with reference value |
| `novelty_or_emergent_insight` | Restates each equation | Produces new dimensionless group |

The editor (Phase C) computes a weighted total per reviewer
(equal weights by default; unequal weights are configurable
per submission class in `framework/ai_consensus_rubrics.py`)
and ranks verdicts by total score alongside the text verdict.

### 11a.2 Specialist persona selection

Each reviewer is assigned a persona that matches the
submission's topic. For **design-doc reviews**:
- Claude Opus: *"senior scientific-software architect with
  20 years building research infrastructure; you have shipped
  systems at scale and you have seen every kind of failure"*
- OpenAI GPT-5: *"senior researcher in symbolic AI, formal
  methods, and equation discovery; you have published on
  SINDy, PySR, and their limitations"*
- Gemini 2.5 Pro: *"senior physicist with cross-domain
  modelling expertise; you have implemented bond-graph and
  port-Hamiltonian systems"*

For **coupling-hypothesis reviews**, personas are selected
from a catalog keyed on the coupling's domains. A thermal-
mass coupling gets thermodynamicist personas; an electromech-
anical coupling gets mechatronics personas; etc. The catalog
lives in `framework/ai_consensus_personas.py`. Unknown
domains fall back to the generic "senior scientific reviewer"
persona with a logged warning.

### 11a.3 COI self-declaration protocol

Each reviewer's Phase A reply MUST begin with a `coi` field:

```json
{
  "coi": {
    "encountered_during_training": true|false,
    "specific_note": "<free-text, empty if no>"
  },
  "rubric": {...},
  "verdict": "approve|modify|reject",
  ...
}
```

A declared COI does not disqualify the reviewer (all three
models share some training on foundational physics
literature; full exclusion would leave no reviewers). But the
declaration is logged, and if 3/3 reviewers all declare
training exposure to the exact formulation under review, the
coupling is flagged `HIGH_COI_CORRELATION_RISK` and cannot be
promoted past EMPIRICAL without independent experimental
evidence.

### 11a.4 Implementation

`framework/ai_consensus.AIConsensusBoard` gains a
`four_phase_query()` method. All phases are recorded in the
ledger with full provenance: Phase A drafts with COI, the
consolidation briefing document, Phase B informed verdicts,
Phase C editor synthesis, and any Phase D rebuttal cycles.
The gate (2-of-3 APPROVE or editor-APPROVE) is evaluated on
Phase C only.

All subsequent board queries in Phase 12+ use the four-phase
protocol. Single-pass `.query()` is kept for low-stakes
lookups (reference-value sourcing that's cheap to sanity-check
via sympy) but is deprecated for coupling verdicts and
architectural decisions.

## 11b. Container-sandboxed notebook execution (v3, user-directed)

**v3 change.** OpenAI v2 correctly flagged: *"executable
notebooks can be a supply-chain and sandboxing risk (code
injection via board inputs)."* v3 addresses this with
container-sandboxed execution.

Every auto-generated composite notebook runs inside a Docker
container with:

- **Pinned base image by SHA** — `python:3.12-slim@sha256:<SHA>`
  fixed for the project's lifetime; upgrades require explicit
  design-doc update
- **Frozen requirements.txt with hashes** — `pip install
  --require-hashes` so an attacker publishing a compromised
  version of a dependency cannot substitute it mid-run
- **`--network=none`** — notebook cells cannot reach the
  internet; no board-sourced input can exfiltrate data
- **`--read-only` root filesystem** — no persistent
  modification
- **`--tmpfs /workspace:rw,size=64m`** — ephemeral writable
  scratch; gone on container exit
- **Non-root UID 1000:1000** — no root escape path
- **Per-cell execution timeout** — nbclient `--timeout=60`
  kills runaway sympy calls
- **Memory + CPU cgroup limits** — `--memory=512m --cpus=1.0`
- **No host volume mounts** except the bind-mounted input
  notebook (read-only) — eliminates the host filesystem
  attack surface

Each generated notebook and its SHA-256 content hash is
logged in the ledger as part of the `RealizationResult`:

```python
@dataclass
class RealizationResult:
    # ...existing fields...
    exec_provenance: Dict[str, Any] = field(default_factory=dict)
    # e.g. {
    #   "image_sha256": "sha256:<pinned>",
    #   "notebook_sha256": "sha256:<generated-notebook-hash>",
    #   "container_runtime": "docker@24.0.7",
    #   "exit_code": 0,
    #   "wall_time_seconds": 12.3,
    #   "memory_peak_mb": 142,
    # }
```

**Infrastructure:** `labs_v2/exec/Dockerfile` with pinned SHAs
and a `labs_v2/exec/requirements.txt` generated via
`pip-compile` with `--generate-hashes`. `framework/exec_sandbox.py`
provides a Python wrapper that invokes the sandbox and returns
a `RealizationResult`. Cost: zero — runs on the local host's
Docker Desktop / OrbStack / Podman / Colima. Optional Cloud
Run path documented for Phase 16+ when continuous sensor
polling needs a 24/7 substrate.

## 11c. Property-based + cross-CAS verification (v3, per v2 board)

**v3 change.** OpenAI v2: *"single-point numeric SymPy checks
can pass spurious or mis-typed formulas; no property-based,
multi-point, or dimensional equivalence verification is
specified."*

v2's orthogonal verification (§5.2) evaluated the board-sourced
formula at the board-sourced parameter values. v3 upgrades
this to three orthogonal checks:

1. **Symbolic equivalence check.** Parse the board-sourced
   formula symbolically and compare against the expected form
   derived locally. `sp.simplify(board_formula - local_formula)
   == 0` is a stronger guarantee than any single-point numeric
   evaluation.

2. **Property-based randomized sampling.** Using a
   Hypothesis-style strategy, draw N=50 random parameter
   vectors from unit-consistent ranges, evaluate the formula
   at each, and check that the computed value matches the
   board's claimed relationship (or formula) at every sample.
   Pure Python stdlib `random` + sympy — no new pip
   dependency.

3. **Cross-CAS verification with mpmath.** Evaluate the
   formula at the canonical sample point with `mpmath` at
   50-decimal precision and compare against sympy's
   single-precision result. Disagreement at >10 decimal
   places flags the formula as numerically fragile. No new
   dependency — mpmath ships with sympy.

All three checks must pass for the reference value to enter
the ledger. A single-point agreement is no longer sufficient.
This directly breaks the "single-point sympy can pass a
subtly wrong formula" failure mode.

## 11d. Transducer catalog versioning (v3, per v2 board)

**v3 change.** OpenAI v2: *"version and freeze the transducer
catalog per run; log semantic version in the ledger to prevent
moving-target regressions during pre-registered evaluations."*

`labs_v2/transducers.yaml` gains a top-level `version` field
using semantic versioning (e.g., `"0.1.0"`). Every Phase 12+
run reads the catalog ONCE at startup and stamps the version
into every `CouplingHypothesis.transducer` record it emits.
The ledger v5 schema records the catalog version alongside
each coupling. When the catalog changes, the version is
bumped and old ledger entries remain interpretable against
their original catalog version.

Pre-registered adversarial tests pin to a specific catalog
version. A catalog bump that causes a must-surface coupling
to vanish triggers `CATALOG_REGRESSION_DETECTED` and blocks
the merge. This prevents a catalog update from silently
breaking a known-good coupling.

## 12. v1 → v2 change log (from board review)

**v1 board review received:** Claude Opus 4.6 APPROVE (minimal
reply), OpenAI GPT-5 TIMEOUT (read timeout on 90s), Gemini 2.5
Pro MODIFY with 3 required modifications and 4 missing pieces.

Claude's approval confirmed the thesis and evidence hierarchy
are defensible. Gemini's modifications were substantive and all
fixable. OpenAI's timeout is a vendor-reliability issue, not a
design issue — the retry in v2 is expected to produce a real
verdict.

**Changes in v2:**

1. **§5.2 Orthogonal verification of board-sourced references**
   (addresses Gemini required-mod #1). Every board-sourced
   value is locally re-computed in sympy from the board's own
   claimed formula before acceptance. Disagreement triggers
   `BOARD_HALLUCINATION_DETECTED`.
2. **§2a Automated composite notebook generation** (addresses
   Gemini required-mod #2). The "generated" path for composite
   notebooks is now fully specified: system assembly via
   transducer substitution → board-queried parameterisation →
   board-queried reference value → `nbformat` programmatic
   assembly → `nbclient` execution → ledger provenance. No
   hidden human-in-the-loop.
3. **§3a Conjectural transducer proposals** (addresses Gemini
   required-mod #3). The catalog grows organically: the sieve
   proposes `ConjecturalTransducer` hypotheses when no
   catalogued entry fits, the board classifies them as
   `known_transducer`, `plausible_novel`, or `spurious`, and
   new entries flow into the catalog with full provenance.
4. **§8a Confidence aggregation across L1–L4** (addresses
   Gemini missing-piece #1). Multiplicative composite
   confidence rule with explicit per-level formulas and
   promotion thresholds (PROVED ≥ 0.50, GROUNDED ≥ 0.80 with
   c4 > 0.5).
5. **§8b Domain taxonomy** (addresses Gemini missing-piece #3).
   Domains are now QUDT SystemOfQuantities-rooted equivalence
   classes, not ad-hoc string matching.
6. **§8c Experiment authority governance** (addresses Gemini
   missing-piece #2). Project owner is the sole human gate,
   per-envelope and accumulated-spend budget caps, rollback
   audit, postmortem on failure.
7. **§8d Model-drift and canonical maintenance** (addresses
   Gemini missing-piece #4). 90-day re-run of all canonical
   problems, composite notebooks, and reference value queries.
   `CANONICAL_DRIFT_DETECTED` blocks new promotions until
   resolved.

Gemini's citations from v1 are recorded as the initial set of
validated prior-work references for the project:
- Todorov et al. (2012), MuJoCo — simulators as reasoning basis
- Schmidt & Lipson (2009), Science — symbolic regression single-domain
- Valverde-Albacete & Peláez-Moreno (2014) — bond graph survey
- Karnopp, Margolis & Rosenberg (2012) — canonical transducers
- Langley (2022), Cambridge University Press — state of the art

---

**This design v2 is submitted to the AI review board for
approval.** Phase 12 starts immediately on 2-of-3 APPROVE. On
further MODIFY, I revise and resubmit. On REJECT, I escalate
to the user for a strategic reset.
