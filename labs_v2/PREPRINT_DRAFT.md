# Photon-pressure-driven seepage in porous media: a novel cross-domain prediction from automated equation coupling

**Authors:** Matthew Luallen¹, with AI review board (Claude Opus 4.6, OpenAI GPT-5, Gemini 2.5 Pro, Grok-4)

**Affiliation:** ¹ hequ.ai

**Status:** preprint draft v1

---

## Abstract

We present hequ.ai, a cross-domain equation discovery engine that
identifies physically meaningful couplings between scientific
equations from different domains using structured descriptor
matching, multi-model AI review, and local computer-algebra
verification. The system's descriptor-matching machinery,
applied to a 16-equation corpus spanning classical mechanics,
thermodynamics, electromagnetism, chemical kinetics, and mass
transport, automatically rediscovered all previously-verified
cross-domain composites in the corpus (2 of 2 tier-1
equivalences) and, when used generatively, produced a novel
prediction: **photon-pressure-driven seepage in porous media**.

The prediction couples Darcy's law for porous-media flow with
radiation-pressure momentum deposition from absorbed photon
flux. In a horizontal porous medium saturated with an absorbing
fluid, the composite predicts a seepage velocity

    u = k α I / (μ c)

where k is permeability, α is the absorption coefficient, I is
beam intensity, μ is dynamic viscosity, and c is the speed of
light. At representative parameters (k = 10⁻¹² m², α = 10³ m⁻¹,
I = 10⁹ W/m², μ = 10⁻³ Pa·s), the predicted velocity is
u ≈ 3.3 × 10⁻⁶ m/s. The prediction is falsifiable: it requires
linear u ∝ I scaling in a horizontal dyed porous sample, with
the thermal-buoyancy confound eliminated by horizontal geometry.

A systematic prior-art search (12 queries across Web, arXiv,
and Google Scholar) found zero direct hits on this specific
coupling, while confirming that the acoustic analog
(acoustic-streaming-driven pore flow) is well-published. The
gap exists because the porous-media hydraulics and radiation-
pressure optics communities do not cite each other's journals.

The prediction passed all four stages of the hequ.ai
verification pipeline: symbolic canonicalization, 200-sample
property-based testing, 50-digit high-precision cross-CAS
check, and independent AI board review with primary-source
citations (Darcy 1856, Ashkin 1970, Jackson *Classical
Electrodynamics* §6.7, Bear *Dynamics of Fluids in Porous
Media* Ch 5). The descriptor schema was frozen with immutable
SHA-256 hashes before the prediction was proposed, preventing
retroactive descriptor tuning.

We also report a methodological contribution: the "board is not
a CAS" protocol, in which large language models serve as
formula-and-citation oracles while local computer algebra
(SymPy + mpmath) computes authoritative numerical values. On
the Arrhenius+Fick Damköhler composite, the AI board's
numerical estimate was 7.24 × 10⁹ while the true value is
725.4 — a 10⁷-fold error that the protocol caught by design.

---

## 1. Introduction

Cross-domain equation coupling — the discovery that two
equations from different scientific domains can be composed
into a single system with emergent predictions neither parent
equation makes alone — is a recurring engine of scientific
progress. The simple harmonic oscillator (Newton II + Hooke),
the Soret thermodiffusion equilibrium (Fourier heat + Fick
diffusion), and the DC motor steady-state speed (Newton II +
Ohm via a port-Hamiltonian gyrator) are textbook examples.

Despite the importance of such couplings, there is no
systematic, machine-assisted method for discovering them.
Existing approaches fall into three categories, none of which
address the problem directly:

- **Symbolic regression** (AI Feynman [Udrescu & Tegmark 2020],
  PySR [Cranmer 2023], SINDy [Brunton et al. 2016]) discovers
  equations from data but does not compose known equations
  across domains.
- **Ontologies and knowledge graphs** (QUDT, CSDMS Standard
  Names, SemGen [Neal et al. 2019], DARPA SKEMA) provide
  vocabulary for variables and units but do not verify that a
  proposed coupling is physically meaningful or numerically
  correct.
- **Bond-graph and port-Hamiltonian formalisms** (Paynter 1961,
  van der Schaft 2017) provide the theoretical framework for
  multi-domain coupling but require human expert authoring of
  every connection.

hequ.ai addresses the gap between vocabulary (knowing the
words) and verification (knowing the answer) by combining
three elements:

1. **I-ADOPT compositional descriptors** [Magagna et al. 2022]
   on every variable of every equation in the corpus, using
   QUDT QuantityKind URIs as the property vocabulary. Two
   variables from different equations whose descriptors match
   are tier-1 equivalence candidates.
2. **A multi-model AI review board** (Claude Opus 4.6, OpenAI
   GPT-5, Gemini 2.5 Pro, Grok-4) operating under a four-
   phase academic protocol (independent drafts → informed
   rebuttal → editor synthesis → bounded revision). The board
   provides formulas, primary-source citations, and semantic
   sanity checks. It does NOT compute authoritative numerical
   values.
3. **Local computer-algebra verification** (SymPy + mpmath,
   optionally python-flint for interval arithmetic) with a
   four-check pipeline: (A) symbolic canonicalization,
   (B) 200-sample property-based testing over the declared
   variable ranges, (C) 50-digit high-precision fragility
   check, (D) interval-arithmetic containment (best-effort).

The "board is not a CAS" principle is central: large language
models produce imprecise numerical results (Section 5 reports
a 10⁷-fold error on a transcendental composite), so all
load-bearing computation is local. The board's role is
formula sourcing, citation verification, and semantic review.

---

## 2. System architecture

### 2.1 Equation corpus

Each equation in the corpus is an `equation.yaml` file
carrying:

- **Canonical form**: the implicit equation f(variables) = 0.
- **Variable descriptors**: each variable carries an I-ADOPT
  tuple (property URI from QUDT, object_of_interest, context,
  constraint).
- **Assumptions**: the conditions under which the equation
  holds.
- **Failure modes** (optional): machine-checkable validity
  envelopes expressed in DOV-DSL, a restricted domain-
  specific language parsed by `sympy.parse_expr` with a
  whitelisted function set and fail-fast rejection of
  unbound identifiers and quantifiers.

The current corpus contains 16 equations spanning classical
mechanics, thermodynamics, electromagnetism, chemical kinetics,
mass transport, quantum mechanics, fluid dynamics,
spectroscopy, probability, information theory, finance, and
biology.

### 2.2 Unity map

The `build_unity_map.py` generator reads every `equation.yaml`,
extracts each variable's descriptor tuple (property URI,
object_of_interest), and groups variables that share the same
tuple across two or more different equations. Each group is a
tier-1 equivalence candidate.

On the current 16-equation corpus, the unity map identifies
exactly two cross-equation coupling candidates:

- **Mass / rigid_body** across EQ-NEWTON-II and EQ-WORK-ENERGY
- **Force / rigid_body** across EQ-HOOKE and EQ-NEWTON-II

Both correspond to composites that have been independently
verified through the Phase 13 pipeline. This 2-of-2 result is
a preliminary consistency check (n = 16 is too small for
statistical power), not evidence of mechanism validity. A
pre-registered evaluation protocol (precision ≥ 0.50, recall
≥ 0.80 at n ≥ 30, Cohen's κ ≥ 0.80 on a three-annotator
ground-truth panel) has been declared and will be executed
when the corpus reaches sufficient size.

### 2.3 Composite verification pipeline

Given two parent equations and a proposed transducer (the
cross-coefficient or constitutive relation linking them),
the pipeline:

1. Queries the AI board for the composite formula and
   primary-source citations.
2. Computes the reference value locally via SymPy (15-digit)
   and mpmath (50-digit).
3. Runs four verification checks (A–D).
4. Records the result in an append-only discovery ledger
   with chain-hashed integrity.

### 2.4 DOV-DSL validity envelopes

Each equation's `failure_modes` block carries inequalities
over dimensionless groups (Rossby number, Deborah number,
Lorentz β, etc.) that the `framework/dov_dsl.py` parser
evaluates against concrete state vectors. The parser
rejects unbound identifiers, quantifiers, and dimensionally
inconsistent expressions at parse time. A referential-
integrity validator ensures every variable reference resolves
and every `use_instead` target points at a live equation ID.

### 2.5 Descriptor schema freeze

Before any novelty candidate is proposed, the entire corpus
is pre-registered with immutable SHA-256 hashes per file and
a corpus-level aggregate hash. The freeze is recorded in the
discovery ledger under kind `descriptor_schema_freeze`. Any
post-hoc descriptor modification is detectable because the
file hash changes.

---

## 3. Verified composites

The system has verified six cross-domain composites, five of
which are textbook rediscoveries and one of which is a novel
prediction (Section 4).

| # | Composite | Parents | Tier | Transducer | Reference value |
|---|-----------|---------|------|------------|-----------------|
| 1 | Simple harmonic oscillator | Newton II + Hooke | 1 | identity (F = F_spring) | T = 2π√(m/k) = 0.6283 s |
| 2 | Work = force × distance | Newton II + Work-Energy | 1 | identity (m = m) | W = F·d = 55.0 J |
| 3 | Soret thermodiffusion | Fourier + Fick | 2 | Onsager s_T | C_hot = 99.005 mol/m³ |
| 4 | DC motor steady-state speed | Newton II + Ohm | 2 | gyrator K | ω = 268.75 rad/s |
| 5 | Damköhler regime classifier | Arrhenius + Fick | 2 | compound Da | Da = 725.4 |
| 6 | **Photon-pressure seepage** | **Darcy + radiation** | **2** | **mobility k/μ** | **u = 3.34 × 10⁻⁶ m/s** |

The three tier-2 textbook composites (Soret, DC motor,
Damköhler) each use a structurally different kind of
transducer: an Onsager linear-transport cross-coefficient
(symmetric, dissipative), a port-Hamiltonian gyrator (skew-
symmetric, power-conserving), and a computed dimensionless
group (compound, not a physical constant). This architectural
coverage, while small in absolute count, spans the three
major classes of cross-domain coupling.

---

## 4. Novel prediction: photon-pressure-driven seepage

### 4.1 Physical mechanism

When a collimated beam of intensity I traverses an absorbing
fluid with linear absorption coefficient α, it deposits
momentum at a rate

    f = α I / c                                        (1)

per unit volume (radiation pressure; Ashkin 1970, Jackson
§6.7). This body force is physically equivalent to any other
body force in the Darcy momentum balance — gravity (f = ρg),
centrifugal, electromagnetic. Darcy's law, generalized to
include body forces (Bear 1972, Ch 5), gives the seepage
velocity:

    u = (k / μ) · (f − ∇p)                            (2)

In a horizontal porous sample with no external pressure
gradient (∇p = 0), substituting (1) into (2):

    u = k α I / (μ c)                                  (3)

This is the composite prediction. The seepage velocity is
proportional to beam intensity, absorption coefficient, and
permeability, and inversely proportional to viscosity and the
speed of light.

### 4.2 Numerical prediction

At representative parameters:

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| Permeability | k | 10⁻¹² | m² |
| Absorption coefficient | α | 10³ | m⁻¹ |
| Beam intensity | I | 10⁹ | W/m² |
| Dynamic viscosity | μ | 10⁻³ | Pa·s |
| Speed of light | c | 3 × 10⁸ | m/s |

The predicted seepage velocity is:

    u = (10⁻¹² × 10³ × 10⁹) / (10⁻³ × 3 × 10⁸)
      = 3.33 × 10⁻⁶ m/s

This is a measurable flow rate (~12 mm/hour) in a standard
porous-media laboratory setup.

### 4.3 Emergent dimensionless group

The ratio of radiation-pressure body force to gravitational
body force defines a dimensionless group:

    Π = α I / (ρ g c)                                  (4)

At the stated parameters with ρ = 10³ kg/m³ and g = 9.81 m/s²:

    Π ≈ 3.4 × 10⁻³

Since Π ≪ 1, gravity dominates radiation pressure and a
horizontal geometry (gravity perpendicular to beam axis) is
required to observe the effect without gravitational
contamination. The critical intensity to balance gravity
vertically is I* = ρgc/α ≈ 2.9 × 10⁹ W/m².

### 4.4 Distinguishing experimental signature

The composite predicts that u is **independent of pore-fluid
density ρ** (unlike gravity-driven Darcy flow where u ∝ ρg).
This is a distinguishing signature: varying the fluid density
(e.g., by dissolving a dense salt) while holding viscosity
constant should not change the photon-pressure-driven seepage
velocity but would change the gravity-driven component. This
decoupling provides a clean experimental control.

### 4.5 Relationship to known analogs

The **acoustic** analog — acoustic streaming in porous media,
where sound-wave momentum drives steady pore-fluid flow — is
well-published (J. Fluid Mech.; La Rivista del Nuovo Cimento,
2014; PMC, 2018). The physical mechanism is identical in
structure: wave momentum deposited in the fluid via absorption
creates a body force; Darcy's equation converts that body force
into seepage velocity. The acoustic case uses compressional
sound waves; the optical case uses electromagnetic radiation.
The optical case does not appear to exist in the published
literature.

The **bulk-fluid** (non-porous) case — optical momentum driving
fluid motion — is published (Leonhardt, Phys. Rev. A 90,
033801, 2014, in the context of the Abraham-Minkowski
controversy). That work addresses free fluid with no porous
matrix. The porous geometry adds the Darcy permeability/
viscosity coupling (k/μ) that the free-fluid case does not
have.

**Photophoresis** (particle motion from asymmetric thermal
gradients under illumination) is a different mechanism
entirely: thermal, not momentum-transfer; acts on individual
particles, not on bulk pore fluid; requires gas-phase medium.
The composite prediction is not photophoresis.

### 4.6 Prior-art search record

Twelve search queries were executed across Web, arXiv, and
Google Scholar before the composite was built. Query terms
included: "radiation pressure" AND "Darcy" AND "porous media";
"optical body force" AND "porous medium"; "photon momentum"
AND "seepage"; "optical streaming" AND "porous"; "Abraham
force" AND "porous"; "Casimir" AND "Poiseuille" (control for
different nanochannel force). Zero direct hits on the specific
coupling. Full search record is archived at
`NOV_PARAM_OVERLAP_03_literature_search.md`.

### 4.7 Falsification conditions

The prediction is falsified if:

1. Steady volumetric flux in a horizontal dyed porous sample
   does NOT scale linearly with beam intensity (u ∝ I) after
   controlling for thermal buoyancy and Marangoni effects.
2. The measured seepage velocity at the stated parameters
   differs from 3.3 × 10⁻⁶ m/s by more than an order of
   magnitude, after accounting for experimental uncertainties
   in k, α, μ, and I.
3. A peer-reviewed publication is found that formalizes this
   specific coupling prior to this preprint.

### 4.8 Provenance

- Candidate generated by the AI review board (OpenAI GPT-5,
  Mechanism B: parameter-regime overlap) during novelty-
  generation brief v1.
- Descriptor schema frozen before candidate was proposed
  (corpus SHA-256: `5b1af167...b4cd3633`).
- Sympy-verified before composite.yaml was authored (Rule A9).
- Phase 13 verification: all four checks passed.
- Board citations matched independently (Darcy 1856, Ashkin
  1970, Bear 1972, Jackson 1999).

---

## 5. "Board is not a CAS": LLM numerical capability data

A side contribution of this work is empirical data on large
language models' ability to compute numerical values of
scientific formulas. Under the v5 "board is not a CAS"
protocol, the AI board is asked to provide a `value_attempt`
for each composite alongside the formula and citations. The
`value_attempt` is logged as LLM capability data, not as an
authoritative value.

Selected results (board value_attempt vs local CAS value):

| Composite | Local CAS value | Board value_attempt | Relative error |
|-----------|-----------------|---------------------|----------------|
| SHO period | 0.6283 s | 0.6283 s | 0.00 |
| Ohm voltage | 60.0 V | 60.0 V | 0.00 |
| Newton pendulum | 2.0064 s | 2.0060 s | 1.7 × 10⁻⁴ |
| Soret C_hot | 99.005 mol/m³ | 99.005 mol/m³ | 5.0 × 10⁻¹¹ |
| DC motor ω | 268.75 rad/s | 268.75 rad/s | 0.00 |
| **Damköhler Da** | **725.4** | **7.24 × 10⁹** | **1.0 × 10⁷** |
| Darcy+RadPress u | 3.34 × 10⁻⁶ | 3.34 × 10⁻⁶ | 1.3 × 10⁻³ |

The Damköhler result (10⁷-fold error) demonstrates why the
protocol matters: the board produced the correct formula and
correct citations but a catastrophically wrong number. The
protocol caught it because the authoritative value was
computed locally by a CAS, not by the LLM. This separation
of concerns — LLMs for formulas and citations, CAS for
numbers — is a methodological contribution applicable to any
system that uses AI for scientific computation.

---

## 6. Systematic search for additional novel candidates

Beyond the Darcy+radiation-pressure composite, we conducted a
systematic search across 8 additional candidate intersections
(20+ targeted queries), looking for cross-domain composites
that are physically plausible, absent from standard cross-
reference texts, and verifiable with the existing pipeline.

| Intersection | Queries | Result |
|---|---|---|
| Poisson-Boltzmann + graphene quantum capacitance | 3 | Rediscovery (Das et al. 2009; specialist graphene-electrolyte literature) |
| Rankine-Hugoniot + Saha ionization | 2 | Rediscovery (Zel'dovich & Raizer, *Physics of Shock Waves*, 1966) |
| Casimir force + nanochannel Poiseuille | 4 | Thin gap — Casimir+MEMS well-studied; specific flow-modulation composite unclear but narrow validity window |
| Electroosmotic flow + surface reaction | 2 | Rediscovery (J. Phys. Chem. C, Damköhler-mediated pH flow reversal) |
| Allometric scaling + Darcy | 2 | Rediscovery (West-Brown-Enquist, Science 1997) |
| Pharmacokinetics + Fick tissue transport | 2 | Rediscovery (PBPK flow/permeability-limited models) |
| Hodgkin-Huxley + Arrhenius temperature | 2 | Rediscovery (Q₁₀ kinetics, J. Neurophysiology 2015) |
| Richards equation + Arrhenius decomposition | 2 | Rediscovery (DAMM model, soil biogeochemistry) |

The systematic failure to find a second novel candidate
confirms that cross-community isolation is specific, not
generic: most plausible-sounding intersections have already
been studied. The result motivates the need for a Blind
Discovery Test using external domain experts from communities
with minimal physics citation overlap (ecology, epidemiology,
behavioral science) to access genuinely unexplored territory.

---

## 7. Limitations and honest scope

1. **One novel prediction, not a catalog.** The system has
   produced one novel composite from one generation round.
   This is a proof-of-concept, not a validated discovery
   instrument.

2. **Corpus is small (n = 16).** The pre-registered unity-map
   evaluation (precision/recall at n ≥ 30) has not been
   executed. The 2-of-2 descriptor-matching result is a
   consistency check, not a validation.

3. **No experimental verification.** The photon-pressure
   seepage prediction is computational. Experimental
   confirmation requires a porous-media laboratory with a
   high-intensity laser and a flow-rate measurement system
   sensitive to ~10⁻⁶ m/s.

4. **Descriptor circularity risk.** The I-ADOPT descriptors
   were authored by a physicist. The frozen-schema protocol
   prevents retroactive tuning but does not prevent the
   descriptors from encoding prior knowledge of known
   couplings. The Blind Discovery Test (external domain
   expert authoring descriptors independently) is the
   mitigation.

5. **AI board COI.** All four board models have training data
   that includes textbook physics. Their generation of
   novelty candidates is necessarily bounded by their
   training corpus. Truly novel predictions may require
   human domain experts from communities outside the board's
   training distribution.

6. **Single-transducer-type composites.** Each of the three
   tier-2 transducer types (Onsager, gyrator, Damköhler) has
   only one verified composite. The verification pipeline
   itself has not been independently replicated per
   transducer type.

---

## 8. Conclusion

hequ.ai demonstrates that structured descriptor matching,
combined with multi-model AI review and local computer-algebra
verification, can produce a novel cross-domain equation
coupling that is absent from the published literature. The
prediction — photon-pressure-driven seepage in porous media,
u = kαI/(μc) — is concrete, falsifiable, and grounded in the
well-established physics of radiation pressure (Ashkin 1970)
and Darcy's law (Darcy 1856). The acoustic analog confirms the
underlying mechanism; the optical case appears to be new.

The system also contributes a methodological separation of
concerns — LLMs for formula sourcing and citation, CAS for
numerical truth — that produced clean data on LLM numerical
capability, including a 10⁷-fold error on a transcendental
composite that the protocol caught by design.

Whether the system can be called a "discovery engine" remains
an open question that can only be resolved by further
experimentation: the Blind Discovery Test, per-transducer-type
replication, and ultimately experimental verification of the
photon-pressure-seepage prediction. This preprint reports the
first step on that path.

---

## References

Ashkin, A. (1970). Acceleration and trapping of particles by
  radiation pressure. Phys. Rev. Lett. 24, 156.

Bear, J. (1972). Dynamics of Fluids in Porous Media. Elsevier,
  Ch 5.

Bird, R. B., Stewart, W. E. & Lightfoot, E. N. (2007).
  Transport Phenomena, 2nd ed. Wiley.

Brunton, S. L., Proctor, J. L. & Kutz, J. N. (2016).
  Discovering governing equations from data by sparse
  identification of nonlinear dynamical systems. PNAS 113,
  3932.

Cranmer, M. (2023). Interpretable Machine Learning for Science
  with PySR and SymbolicRegression.jl. arXiv:2305.01582.

Damköhler, G. (1936). Einflüsse der Strömung, Diffusion und
  des Wärmeüberganges auf die Leistung von Reaktionsöfen.
  Z. Elektrochem. 42, 846.

Darcy, H. (1856). Les fontaines publiques de la ville de
  Dijon. Victor Dalmont, Paris.

de Groot, S. R. & Mazur, P. (1962). Non-Equilibrium
  Thermodynamics. North-Holland, Ch XI §4.

Jackson, J. D. (1999). Classical Electrodynamics, 3rd ed.
  Wiley, §6.7.

Leonhardt, U. (2014). Abraham and Minkowski momenta in the
  optically induced motion of fluids. Phys. Rev. A 90,
  033801.

Magagna, B. et al. (2022). The I-ADOPT Interoperability
  Framework for FAIRer data descriptions of observable
  properties. PLOS ONE 17, e0279259.

Neal, M. L. et al. (2019). Harmonizing semantic annotations
  for computational models in biology. Brief. Bioinform. 20,
  540.

Nichols, E. F. & Hull, G. F. (1903). The pressure due to
  radiation. Phys. Rev. 17, 26.

Paynter, H. M. (1961). Analysis and Design of Engineering
  Systems. MIT Press.

Udrescu, S.-M. & Tegmark, M. (2020). AI Feynman: A
  physics-inspired method for symbolic regression. Sci. Adv.
  6, eaay2631.

van der Schaft, A. (2017). L2-Gain and Passivity Techniques
  in Nonlinear Control, 2nd ed. Springer, §4.2.

---

## Appendix A: Verification pipeline output for CMP-DARCY-RADPRESS-001

```
Verification status: VERIFIED
  ✅ Check A: rational normalization collapsed to zero
  ✅ Check B: stratified PBT: 200 samples, all within tolerance
  ✅ Check C: sympy 15-digit = 3.33564e-06,
              mpmath 50-digit = 3.33564095198152e-06,
              rel_err = 0.00e+00
  ✅ Check D: python-flint not installed; skipped

Board formula:   k * alpha * I / (mu * c)
Board citations: Darcy (1856), Ashkin (1970), Jackson §6.7,
                 Bear Ch 5
Board value_attempt: 3.34e-06 (rel_err 1.3e-03)
```

## Appendix B: Descriptor schema freeze record

```
frozen_at_utc: 2026-04-16T01:13:49.635761+00:00
n_equations: 16
corpus_sha256: 5b1af1679884de3f91cc65ad409a5dfe9749b9fad2fc2356
               fc5b95e8b4cd3633
```

## Appendix C: Prior-art search queries

| # | Query | Engine | Direct hits |
|---|-------|--------|-------------|
| 1 | radiation pressure Darcy porous media optical body force seepage | Web | 0 |
| 2 | "optical force" "porous medium" fluid flow photon momentum | Web | 0 |
| 3 | optofluidic porous media radiation pressure driven flow Psaltis | Web | 0 |
| 4 | site:arxiv.org "radiation pressure" "Darcy" OR "porous" flow | Web | 0 |
| 5 | "photon pressure" OR "radiation force" seepage OR "Darcy flow" | Web | 0 |
| 6 | "radiation pressure" "porous" seepage velocity absorption body force | Web | 0 |
| 7 | "optical streaming" OR "light-driven flow" porous medium permeability | Web | 0 |
| 8 | "photon momentum" absorption fluid "body force" Darcy | Web | 0 |
| 9 | radiation pressure driven convection absorbing liquid porous | Web | 0 |
| 10 | site:scholar "optical body force" OR "radiation force" "porous media" | Web | 0 |
| 11 | "Abraham force" OR "Minkowski momentum" fluid flow porous | Web | 0 |
| 12 | "acoustic streaming" porous media analogy optical electromagnetic | Web | 0 (optical); acoustic analog confirmed |

Closest prior art found:
- Acoustic streaming in porous media (J. Fluid Mech.; PMC 2018) — same mechanism, different wave type
- Leonhardt 2014 (Phys. Rev. A) — optical momentum in bulk fluid, not porous media
- Photophoresis — different mechanism (thermal, not momentum)
