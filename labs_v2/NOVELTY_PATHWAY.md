# Novelty Pathway Document

**Status:** draft v1, written in response to the project meta-analysis
board review (Claude priority #5, unanimous across reviewers).
**Bar:** either articulate a concrete mechanism by which hequ.ai could
produce a genuinely novel cross-domain coupling prediction, or honestly
conclude the project is a verification/cataloguing tool rather than a
discovery engine.

---

## What "novel" has to mean here

A genuinely novel coupling is one that:

1. **Cannot be found by reading any textbook in any of the two parent
   domains** as a "see also" link.
2. **Has never been the subject of a published paper** that makes the
   coupling explicit (tested via Google Scholar / OpenAlex search on
   the formal variable names after the coupling is proposed).
3. **Has a falsifiable prediction** — either a numerical value that
   can be checked against a dataset or against a reference
   calculation in a different modeling framework.
4. **Is not merely a Wick-rotation / analytic-continuation / log-
   transform duality.** Heat equation ↔ Black-Scholes is a famous
   mathematical isomorphism but does not couple *physical* degrees of
   freedom between a thermal system and a financial one. Such
   dualities should be catalogued separately (the v3 design doc
   called this the DUALITY sidebar status); they are structurally
   interesting but not discoveries in the physics sense.

By that definition, every one of the five verified composites in the
current corpus is **zero** on condition (1) — they all appear in
textbook indexes. The discovery claim has therefore never been tested
at all.

---

## Three concrete mechanisms by which hequ.ai could produce a novel coupling

### Mechanism A — Cross-community isolation

**Thesis.** Two scientific communities can study structurally similar
equations in parallel for decades without ever citing each other,
because their vocabulary, venues, and training pipelines do not
overlap. The unity map can surface such couplings when its descriptor
vocabulary is *semantic enough* to match across vocabularies that
never aligned historically.

**Worked failure scenario.** The Fisher-KPP equation (1937, population
genetics) and reaction-diffusion propagation fronts in combustion
chemistry (1940s onward) are the same equation, `∂u/∂t = D·∇²u + r·u·(1-u)`,
studied by biologists and chemists in near-total isolation for
~30 years until applied mathematicians noticed. A 1950 hequ.ai with
both domains in the corpus could have flagged the coupling.

**What it takes to actually do this.** The corpus must contain
equations from domains whose communities do not cite each other, and
the I-ADOPT descriptor vocabulary must be expressive enough that the
reaction-diffusion structure of both equations produces matching
descriptor tuples. Concretely: add equations from **quantitative
ecology** (allometric scaling, metabolic theory, Metabolic Ecology by
Brown et al. 2004), **network epidemiology** (SIR/SIS on graphs,
Pastor-Satorras & Vespignani), and **behavioral economics**
(prospect-theory value functions, nonlinear discounting), then see
whether the unity map finds couplings to existing physics entries
that are not already in review articles.

**Falsification.** This mechanism is falsified if the unity map
produces zero cross-community matches after 30 equations from
3 non-physics communities are added, or produces only matches that
are already catalogued in interdisciplinary review papers.

### Mechanism B — Parameter-regime overlap with no published composite

**Thesis.** Two equations can be individually well-known but their
*composite* in a specific parameter regime can be unreported because
the parameter regime is physically unusual. The unity map can propose
such composites by checking where the validity envelopes of two
equations overlap in a state space that has not been experimentally
explored.

**Worked scenario.** Arrhenius rate law (chemical kinetics) and
Lorentz factor (special relativity) overlap in exactly one regime:
reaction dynamics at relativistic temperatures (~10⁹ K, early
universe nucleosynthesis, ultra-high-intensity laser plasmas). The
composite `k(T) = A · exp(−E_a/(R·T·√(1 − v²/c²)))` is not a standard
textbook equation because the regime is exotic. Whether it is
*correct* is a separate question (a professional chemist or nuclear
astrophysicist would be needed), but it is the kind of composite the
machinery could flag.

**What it takes.** Every equation in the corpus must carry a
machine-readable validity envelope (this is what DOV-DSL already
provides). The unity map must be extended to check not just
descriptor matches but **envelope overlap in a shared state space**.
Specifically: "in what parameter region are both equations valid,
and does a cross-product of their variable sets predict an emergent
scalar that neither equation alone predicts?"

**Falsification.** This mechanism is falsified if the union of
failure_modes envelopes across the corpus never produces a non-empty
shared validity region for two equations from different domains that
is not already covered by an existing composite.

### Mechanism C — Structural-type matching beyond semantic descriptors

**Thesis.** The current I-ADOPT descriptors are *semantic*
(`property: Force`, `object_of_interest: rigid_body`). A second
descriptor layer — *structural type* (second-order linear parabolic
PDE, first-order nonlinear ODE, stochastic DE with multiplicative
noise, Fredholm integral equation) — would surface couplings between
equations of different semantics but identical mathematical
structure. Some of those structural matches are the DUALITY sidebar
cases (discarded). Others are real physical couplings through shared
Green's functions or shared asymptotic behavior.

**Worked scenario.** The Smoluchowski coagulation equation and the
Smoluchowski drift-diffusion equation share the name of the same
Polish physicist but are structurally different objects
(integro-differential vs. parabolic PDE). The drift-diffusion form is
widely used in semiconductor physics; the coagulation form is widely
used in aerosol science and astrophysics. A hequ.ai that carried
both structural types could propose a composite when a system
exhibits both phenomena simultaneously (e.g., charged aerosol
dynamics in a gas-discharge plasma). The composite may or may not be
already known — it is the kind of cross-community question hequ.ai
could surface.

**What it takes.** Add a `structural_type` field to each
equation.yaml: `ODE | PDE_parabolic | PDE_hyperbolic | PDE_elliptic |
stochastic_DE | integral_equation | integro_differential | algebraic |
transcendental`. Then run a second pass of the unity_map that groups
equations by structural type *and* cross-community semantic
separation. Report candidates as DUALITY_CANDIDATE (mathematical
isomorphism without physical coupling) or PHYSICAL_COUPLING_CANDIDATE
(same structure, shared parameter regime, no published composite).

**Falsification.** This mechanism is falsified if every
PHYSICAL_COUPLING_CANDIDATE turns out to be either (a) an already-
published composite, or (b) a pure mathematical duality without
physical content.

---

## Known failure modes shared by all three mechanisms

- **Descriptor circularity.** If the descriptors are assigned by a
  physicist who already knows which couplings are interesting, the
  mechanism will produce only the couplings the physicist already
  expected. The **descriptor provenance audit** (board priority #3)
  is a direct test for this. Pre-registration of the descriptor
  schema before any blind-discovery run is the mitigation.
- **Corpus bias toward textbook equations.** The current 16-equation
  corpus was chosen because the equations are canonical and have
  textbook verification targets. This is the opposite of what the
  discovery mechanisms need: unusual, under-studied, or communities-
  in-isolation equations. Scaling to n=30 with equations selected to
  minimize overlap with standard physics textbooks is necessary.
- **No domain-expert adversary.** Any novelty candidate needs to be
  evaluated by a domain expert who is not me and who is not part of
  the hequ.ai review board (no COI). This is the hard dependency
  that makes the Blind Discovery Test expensive.

---

## Honest assessment

Of the three mechanisms, **Mechanism A (cross-community isolation) is
the most credible short-term pathway**. It does not require any new
machinery — only corpus expansion into communities that do not cite
physics and vice-versa. The descriptor provenance audit and
pre-registration of the descriptor schema are feasible within the
current architecture.

Mechanism B (parameter-regime overlap) requires the DOV-DSL
machinery we already have plus a cross-envelope-intersection
extension to the unity map. That extension is bounded in scope (a
few hundred lines of code). It is the second-most-credible pathway.

Mechanism C (structural-type matching) is the most speculative. Its
failure mode (rediscovering known dualities under the guise of novel
couplings) is exactly the kind of result that would fail peer review
from a physicist. It is not the first thing to build.

## The specific experiment that tests all three

**The Blind Discovery Test** (board priority #1). Have an independent
domain expert — one not affiliated with hequ.ai and unfamiliar with
its composite ledger — select 5–10 equations from a domain I am not
expert in (ecology, epidemiology, quantitative finance, or
behavioral economics) and author equation.yaml files with I-ADOPT
descriptors of their own choosing. Freeze the descriptor schema
(immutable hashes) **before** running the unity map. Run the unity
map. Report all candidates, including false positives. Evaluate each
as (a) real and already published, (b) real and not yet published,
or (c) spurious. The Blind Discovery Test simultaneously tests
Mechanisms A and B and measures the descriptor circularity risk
directly.

If (b) produces even one candidate, the discovery claim has survived
its first real test. If every candidate is (a) or (c), the
rediscovery-vs-discovery question resolves as: **hequ.ai is a
verification and cataloguing tool with publishable methodology
contributions but is not, today, a discovery engine.** That finding
would itself be valuable and would sharpen every subsequent priority.

---

## Fallback — what hequ.ai is if all three mechanisms fail

Even if no genuine discovery emerges from the Blind Discovery Test,
hequ.ai has two publishable contributions that do not depend on the
discovery claim:

1. **The "board is not a CAS" verification protocol** — a method for
   using LLMs as formula-and-citation oracles while keeping numeric
   computation authoritative. The 7-order-of-magnitude Arrhenius+Fick
   error (board `value_attempt` 7.24e9 vs true 725.41) is a clean
   data point demonstrating why this separation matters. The
   protocol + the LLM-math-capability dataset would be a credible
   workshop paper on its own.
2. **DOV-DSL + failure_modes schema** — a lightweight, CAS-backed,
   CI-enforced way to attach machine-checkable validity envelopes to
   scientific equations, with referential integrity and a pre-
   registered evaluation protocol. This fills a niche currently
   occupied by prose-level DLMF annotations and heavyweight Modelica
   constraint systems. A methodology paper is defensible independent
   of any discovery claim.

These two artifacts would justify the project even in the failure
case. The discovery engine is the ambitious claim; these are the
load-bearing contributions that already exist. Being honest about the
distinction is the point of this document.

---

## Immediate next action, contingent on the above

Proceed with the Blind Discovery Test setup:

1. Pre-register the descriptor schema — freeze the current I-ADOPT
   convention, commit an immutable SHA256 hash of every current
   equation.yaml, and log it in the discovery_ledger.jsonl as a new
   record kind `descriptor_schema_freeze`.
2. Draft a one-page call to independent domain experts (ecology,
   epidemiology, finance, behavioral economics) describing the
   minimal equation.yaml authoring protocol and the blind-submission
   ground rules.
3. Until the blind test is executed, do not add any more equations
   selected from physics textbooks. Every new entry must come from
   outside my own expertise or from a community with minimal physics
   overlap.
4. In parallel, implement the lightweight physical-admissibility
   check (Gemini's top add) for existing composites: automated
   skew-symmetry verification on explicit gyrator J matrices,
   automated symbolic L_12 = L_21 check on Onsager cross-
   coefficients, automated dimensional consistency of compound
   dimensionless groups. These are small additions that address a
   unanimous board concern without any risk of re-introducing EWE
   complexity.
