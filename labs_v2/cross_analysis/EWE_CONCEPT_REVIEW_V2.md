# EWE Concept Review v2 — 4-Phase Academic Protocol

**Query:** `ewe_concept_review_v2`  
**Include Grok:** True  
**Editor verdict:** `modify`

**All responded (Phase A):** True  
**All responded (Phase B):** True

## Phase C — Editor synthesis (binding)

**Verdict:** `modify`

**Rationale:**

All four reviewers independently converge on MODIFY with rubric means between 4.20 and 4.60, and their reasoning is uniformly strong and mutually reinforcing. The framework is technically sound, genuinely falsifiable (the pre-registered three-arm evaluation with retraction clause is exemplary), and addresses a real gap: scientific-equation assumption failures are currently buried in prose, and a structured, machine-checkable knowledge graph is a legitimate and buildable contribution. The MITRE analogy is apt and well-executed. However, every reviewer identifies the same critical structural gap — the three-way ECP classification (CONSERVATION_BALANCE, CONSTITUTIVE_CLOSURE, INTER_DOMAIN_TRANSDUCTION) is not exhaustive. Non-power-conserving couplings (rate-coupling in Lotka-Volterra, signal-flow in control theory, stoichiometric coupling in systems biology) demonstrably fall outside all three classes, and at least 3 of the 16 seed equations require this fourth category. This is not a cosmetic omission; it is a soundness defect in the composition formalism's claim of disjoint exhaustiveness. Additionally, all reviewers flag that the domain-of-validity inequality strings lack a formal grammar or parsing specification, which undermines the central 'machine-checkable' claim of M1 — without at minimum a restricted DSL or BNF grammar, the inequalities are structured prose, not executable assertions. The port-Hamiltonian power-conservation postcondition needs corrected semantics (Dirac structures conserve power, not create it; the postcondition should assert that the skew-symmetric interconnection matrix J satisfies x^T J x = 0, not merely 'power balance to machine precision'). The crypto sub-appendix's CRYPTO_REDUCTION pattern requires formal fields for tightness (advantage-loss factor, polynomial vs. exact reduction) to match the rigor of the physics ECP postconditions. Finally, calibration (Brier score) in HEQU-BENCH-001 should be a hard gate rather than one of four fungible metrics, given that a miscalibrated system feeding a scientific discovery engine is actively dangerous. These are all well-reasoned, technically grounded modifications that strengthen a fundamentally sound and ambitious framework.

**Required modifications:**
- Add a fourth ECP class (e.g., RATE_COUPLING or SIGNAL_FLOW_COUPLING) for non-power-conserving compositions where equations share state variables through rate terms, signal paths, or stoichiometric matrices. Define disjoint pre/post-conditions with rigor comparable to the existing three classes. Demonstrate coverage by classifying all 16 seed equations' composition patterns under the four-class scheme and proving mutual exclusivity.
- Provide a formal grammar (BNF or restricted SymPy inequality DSL) for domain-of-validity expressions in M1. Each inequality string must be parseable and evaluable against the SymPy AST of the canonical equation. Specify the parser, the variable-binding mechanism linking inequality symbols to the canonical_equation's variable declarations, and the evaluation semantics (including handling of undefined/unobservable quantities).
- Correct the port-Hamiltonian power-conservation postcondition for INTER_DOMAIN_TRANSDUCTION: the Dirac-structure interconnection matrix J is skew-symmetric (x^T J x = 0), meaning power is conserved (net zero), not generated. State the postcondition as a machine-verifiable assertion on the skew-symmetry of J, not as a vague 'power balance to machine precision' check.
- Formalize the CRYPTO_REDUCTION ECP pattern's pre/post-conditions to match the rigor of the physics ECP patterns. Add explicit fields for: reduction type (polynomial/exact), tightness (advantage-loss factor as a symbolic expression), the security model in which the reduction holds, and a machine-checkable postcondition (e.g., advantage bound as a verifiable inequality over security parameters), replacing the current prose-level 'advantage bound proven in a specified model.'
- Make calibration (Brier score) a hard-gate requirement in HEQU-BENCH-001, not one of four fungible metrics. A system that passes on precision, recall, and latency but fails on calibration should not pass the benchmark, because miscalibrated confidence in scientific-equation validity assessments is a safety-critical failure mode for a discovery engine.

## Phase B — Informed votes

### claude-opus-4-6

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** A rigorously falsifiable and technically grounded framework that needs three targeted corrections before approval: a fourth ECP class for non-power-conserving coupling, corrected port-Hamiltonian power semantics, and a formal grammar for domain-of-validity expressions.

**Response to peers:**

All four reviewers converged on the ECP exhaustiveness gap (signal-flow / informational / rate coupling), and I agree this is the single most important required modification — three of the sixteen seed equations (Lotka-Volterra, Boltzmann transport, Black-Scholes) demonstrably fail to fit the three proposed classes, which is not an edge case but a structural deficiency in the typology. Grok-4's APPROVE verdict acknowledged the gap but deemed it non-fatal given the board-review process for additions; I disagree — this is not a future-proofing concern but a day-one correctness issue affecting the MVP seed set itself, so it must be resolved before build. OpenAI-GPT-5 raised the critical point that the ECP power-conservation postcondition 'e·f = ė·ḟ' is dimensionally incorrect; the standard Dirac-structure constraint is Σ_i e_i f_i = 0 at junctions with transformer/gyrator constitutive maps preserving power. This is a genuine technical error in the submission, not a stylistic quibble, and I am surprised only one reviewer flagged it with full specificity — I strongly endorse this as a required fix. OpenAI-GPT-5 also raised the DAE index analysis point for CONSTITUTIVE_CLOSURE: the simple rank-equals-states postcondition is indeed insufficient for differential-algebraic systems (e.g., incompressible Navier-Stokes, constrained mechanical systems), and the Pantelides/Pryce structural index check is the right tool. I endorse adding this as a required field. Gemini-2.5-pro's perfect 5.0 mean score is generous but defensible on technical merit given the pre-registered evaluation protocol and the crypto sub-appendix's honesty; I hold at 4.4 mean because the power-semantics error and missing DSL grammar for domain_of_validity strings are substantive enough to prevent a 5 on thesis_soundness and technical_feasibility respectively. Claude-opus-4-6's point about mapping_confidence lacking an operationalized definition is correct and I adopt it. The concern about calibration being a

### openai-gpt-5

**Verdict:** `modify`  
**Position change:** strengthened  
**Headline:** Approve after adding a fourth ECP class for signal/information coupling, correcting Dirac power semantics, formalizing domain-of-validity/DAE/error bounds, and tightening crypto-reduction fields and calibration gating.

**Response to peers:**

Claude — Agreed on all substantive points. 1) Add a fourth ECP class (SIGNAL_FLOW_COUPLING or RATE_COUPLING) for non-power-conserving compositions. Pre: typed signal ports with declared causality; shared state appears in rate/parameter terms with unit consistency; optional noise model. Post: well-defined Jacobian/transfer map; no algebraic loop unless explicitly modeled as a DAE constraint; stability/causality checks where declared. Validate that Lotka–Volterra, Boltzmann-transport couplings, and Black–Scholes delta-hedging land here. 2) Specify a strict, validator-enforced DSL for domain_of_validity and error_scaling: restricted SymPy expressions bound to QUDT-typed symbols; require inequalities over dimensionless Pi-groups or quantities annotated dimensionless_by_definition; parser failure is a schema failure. 3) Strengthen CRYPTO_REDUCTION: add tightness_loss {type: exact|polynomial|concrete, factor: <expr>}, model {random_oracle|quantum_random_oracle|standard|algebraic_group|generic_group}, advantage_bound: <expr in q,t,queries>, with theorem_ref {paper, section, theorem_id}. Post: advantage_bound is unit-consistent (probabilities unitless; time in stated units) and traceable to the cited theorem. 4) Extend AAO with stationarity, separability, memoryless (distributional, distinct from Markovianity), Born–Oppenheimer_separation; for crypto add honest_verifier and algebraic_group_model. 5) Define mapping_confidence: use a Dawid–Skene-style annotator model with Beta–Binomial posterior; field includes method: dawid_skene, priors, and posterior mean p(correct). 6) Make calibration a hard gate: A must not underperform B on Brier; additionally require reliability slope near 1 within CI or apply post-hoc calibration and report both pre/post. OpenAI — Fully concur and extend. 1) Correct ECP power semantics: replace e·f = ė·ḟ with Dirac-structure constraints: (i) for junctions Σ_i e_i f_i ≈ 0 (within tolerance); (ii) for transformers/gyrators, enforce constitutive effort/

### gemini-2.5-pro

**Verdict:** `modify`  
**Position change:** strengthened  
**Headline:** Framework remains exceptionally promising but requires foundational semantic corrections and extension of its composition typology, as identified by a strong peer consensus.

**Response to peers:**

My initial 'modify' verdict from Phase A is strongly reinforced by the detailed and largely convergent critiques from my peers. 

1. **ECP Typology Exhaustiveness:** The consensus between myself, Claude, and OpenAI is clear and correct: the three proposed ECP classes are insufficient. They brilliantly capture energy-conserving physical interactions but entirely miss the critical category of non-power-conserving signal/information flow, which is fundamental to control theory, systems biology, and econometrics. The proposed fourth class (`SIGNAL_FLOW_COUPLING` or `INFORMATIONAL_COUPLING`) is a non-negotiable addition. Grok's position that this can be handled by future governance is, in my view, too permissive; this is a foundational semantic gap in the proposed formalism that must be closed now.

2. **Critical Flaw in Power Conservation:** I was persuaded by OpenAI's sharp observation of the error in the `INTER_DOMAIN_TRANSDUCTION` post-condition. The statement `e·f = ė·ḟ` is dimensionally inconsistent and physically incorrect. The correct condition for a power-conserving Dirac structure is `Σ eᵢ·fᵢ = 0`. This is not a minor detail; it is a fatal flaw in the current specification that undermines the framework's claim to physical rigor. This correction is mandatory.

3. **Formalizing 'Machine-Checkable' Claims:** The points raised by both Claude and OpenAI regarding the string-based `domain_of_validity` inequalities are valid. Without a specified grammar or a restricted DSL (e.g., a SymPy subset) that a validator can parse, the 'machine-checkable' claim is aspirational. This must be formalized.

4. **Strengthening Formalism:** I endorse several other proposed enhancements that significantly increase the framework's rigor. Specifically: OpenAI's call to replace the simple rank check in `CONSTITUTIVE_CLOSURE` with a more sophisticated DAE index analysis is an expert-level correction that I fully support. Similarly, Claude's proposal to add machine-checkable fields for ti

### grok-4

**Verdict:** `modify`  
**Position change:** moderated  
**Headline:** The framework is sound and falsifiable but requires a fourth ECP category for non-power-conserving couplings to ensure exhaustiveness, as unanimously raised by peers.

**Response to peers:**

Claude's concerns on ECP exhaustiveness (missing signal-flow) persuade me to support adding a fourth category, as it addresses a verifiable gap in covering equations like Lotka-Volterra; I agree on needing a grammar for domain_of_validity inequalities for true machine-checkability, but push back on mandatory calibration as a hard gate since the pre-registered metrics already enforce falsifiability without overconstraining; for AAO additions, evidence supports including stationarity and separability but not honest_verifier or algebraic_group_model yet, as the crypto tags are sufficient for the proposed scope. OpenAI's point on correcting ECP power semantics (e·f = ė·ḟ is indeed inconsistent) is valid and evidence-based, warranting a fix for soundness; I concur on formalizing domain_of_validity with dimensionless enforcement and strengthening small-parameter semantics, but the DAE refinements for CONSTITUTIVE_CLOSURE exceed evidence of need in the current corpus without prior failures. Gemini's focus on adding an INFORMATIONAL_COUPLING ECP category aligns with my updated view, strengthening the case for modification; their AAO governance concern is noted but not actioned, as the board-review process is already specified. Overall, peers' evidence on ECP gaps moderated my approve to modify, but I push back on over-expanding AAO or crypto without falsifiable justification.

## Phase A — Independent drafts

### claude-opus-4-6

**COI:** ⚠ Familiar with MITRE CWE/CAPEC/ATT&CK frameworks, port-Hamiltonian modeling, QUDT ontology, OpenMath, and standard cryptographic hardness assumptions from training data. No relationship with hequ.ai or its contributors. The v1 review context references a prior Claude Phase A truncation — I have no memory of that session and am evaluating v2 de novo.  
**Verdict:** `modify`  
**Headline:** A technically sound and unusually honest framework with a rigorous pre-registered evaluation commitment; requires modifications to close gaps in ECP exhaustiveness, AAO completeness, and the crypto sub-appendix's reduction formalism.

**Strengths:**
- M5 is exemplary: a pre-registered three-arm evaluation with a pre-committed retraction clause is rare in infrastructure proposals and makes the entire framework genuinely falsifiable — this alone elevates the submission above most comparable ontology proposals.
- M1's machine-checkable fields are well-designed: the combination of SymPy AST, QUDT-typed variables, explicit domain-of-validity inequalities with named small parameters and error-scaling orders, and enumerated detection methods creates a record that is actually parseable and testable, not just 'structured prose in YAML clothing.'
- M3's disjoint ECP classification with port-Hamiltonian semantics is a real formalism, not a taxonomy by vibes. Effort/flow typing, Dirac-structure power conservation as a unit-testable postcondition, and the coupling_residual_class enum give ECP failures sharp semantics that are distinct from EWE-level failures.
- The crypto sub-appendix is honest about the fundamental mismatch between the verification pipeline's assumptions (CAS in <1s) and cryptographic equations, and the three-regime classification (TRACTABLE/HEAVY/INFEASIBLE) is the correct decomposition. The explicit sandbox routing guard is a sign of operational maturity.
- The AAO is enumerated with board-review governance for additions, which prevents tag sprawl — the failure mode that kills most scientific ontologies. The 24-tag seed covers the most common assumption classes in mathematical physics and is neither over- nor under-specified for the 136-equation corpus.
- M4's provenance grading with inter-annotator agreement metrics (Cohen's κ) and evidence-level enums brings the EOE layer to a standard comparable to evidence-based medicine's GRADE system, which is appropriate rigor for a knowledge graph that will inform downstream retrieval.

**Concerns:**
- ECP exhaustiveness (Q3): The three-way classification misses signal-flow / block-diagram coupling, which is non-power-conserving and pervasive in control theory, systems biology (stoichiometric matrices), and econometric structural equation models. A Lotka-Volterra predator-prey coupling is neither a conservation balance, nor a constitutive closure, nor a port-Hamiltonian transduction — it is a rate-coupling through shared state variables. The submission itself flags this gap but does not resolve it. This is not a minor edge case: at least 3 of the 16 prioritized seed equations (Lotka-Volterra, Boltzmann transport, Black-Scholes) have compositions that fall outside the three classes.
- AAO seed gap: The 24 tags omit 'stationarity' (distinct from quasistatic — critical for time-series equations like Black-Scholes and any spectral method), 'Born-Oppenheimer_separation' (needed if any quantum-chemistry equations enter the corpus), 'no_memory / memoryless' (distinct from Markovianity — Markovianity is a process property, memorylessness is a distributional one), and 'separability' (quantum and classical). For the crypto regime, 'honest_verifier' and 'algebraic_group_model' are standard assumptions that the 7 proposed crypto tags miss.
- The CRYPTO_REDUCTION ECP pattern's pre/post conditions are underspecified relative to the rigor of the physics ECP patterns. 'Reduction is tight or concrete' needs a formal field: is tightness expressed as an advantage-loss factor? Is the reduction polynomial or exact? The physics ECPs have unit-testable postconditions (dimensional consistency, rank check, power balance to machine precision); the crypto ECP's postcondition ('advantage bound proven in a specified model') is a prose statement about a proof, not a machine-checkable assertion. This asymmetry weakens the framework's uniformity.
- The domain_of_validity inequalities in M1 use string representations ('Ro := U / (f * L) >= 1'). There is no specification of how these strings are parsed, evaluated, or connected to the SymPy AST. If these are meant to be machine-checkable (the whole point of M1), they need a grammar — even a simple one like a restricted SymPy inequality DSL. Without this, the 'machine-checkable' claim is aspirational rather than actual.
- The 300-query benchmark (HEQU-BENCH-001) includes decoy queries where the system must refuse, which is excellent. However, the pass condition requires A to beat B on 'at least 3 of 4' metrics — this allows A to fail on calibration (Brier score) while still passing. For a system that will feed a scientific discovery engine, calibration failure is arguably a veto-level defect. Consider making calibration a hard gate rather than one of four fungible metrics.
- The mapping_confidence field in EOE entries is described as 'independent board evaluation' but no protocol is given for how this number is produced. Is it the mean of annotator ratings? A Bayesian posterior? An ordinal scale mapped to [0,1]? Without this, the 0.98 in the example is an ungrounded number.
- Small but sharp: the error_scaling field uses big-O notation as a string ('O(beta**2)'). This is fine for human reading but is not machine-checkable without a parser that understands asymptotic notation. If you are going to commit to machine-checkability, either provide a parser spec or reduce these to a structured form like {leading_order: 2, variable: 'beta'}.

**Required modifications:**
- Add a fourth ECP class — provisionally SIGNAL_FLOW_COUPLING or RATE_COUPLING — for non-power-conserving compositions where equations share state variables through rate terms or signal paths. Define pre/post conditions with comparable rigor to the existing three classes: Pre: shared state variable appears in rate expressions of both equations with compatible units. Post: Jacobian of the coupled system is well-defined and the coupling does not introduce algebraic loops (or, if it does, the algebraic constraint is explicitly identified). Verify that Lotka-Volterra, Boltzmann transport equation coupling, and Black-Scholes delta-hedging composition all fit cleanly into either this new class or one of the existing three.
- Specify a grammar or DSL for domain_of_validity inequalities and error_scaling expressions. At minimum, define these as restricted SymPy expressions that the validator can parse and evaluate given a state dict. If the inequality string cannot be parsed by the validator, the EWE entry must fail validation — otherwise M1's machine-checkability claim is hollow.
- Strengthen the CRYPTO_REDUCTION ECP with machine-checkable fields: add 'tightness_loss: {type: exact | polynomial | concrete, factor: <expr>}', 'model: {type: random_oracle | standard | algebraic_group | generic_group}', and 'advantage_bound: <expr in terms of adversary resources>'. The postcondition should be: advantage_bound expression is dimensionally consistent (probabilities are unitless, time is in stated units) and the reduction statement is traceable to a cited theorem number in the primary source.
- Add 'stationarity', 'separability', 'honest_verifier', and 'algebraic_group_model' to the AAO seed set (bringing it to 28+). Provide the same formal-definition-plus-canonical-reference treatment as the existing 24 tags. If the board disagrees on any of these four, provide explicit rationale for exclusion.
- Define the protocol for producing mapping_confidence values in EOE entries: specify whether it is mean annotator rating on a Likert scale mapped to [0,1], a Bayesian posterior, or another method. Without this, the field is uninterpretable and cannot be used in downstream calibration analysis.
- Make calibration (Brier score) a hard independent gate in the HEQU-BENCH-001 pass condition, rather than one of four fungible metrics. A system that retrieves accurately but is miscalibrated will generate false confidence in a discovery engine context, which is worse than a system that retrieves less accurately but knows when it is uncertain. Proposed revision: A must beat B on at least 2 of {Top-1, Top-5, MRR} AND must beat B on calibration, AND A−C must be positive-significant.

### openai-gpt-5

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** Principled, testable framework with strong semantics; needs targeted formal fixes (ECP power condition, crypto parameterization, signal-flow class, invariance/DAE checks) before approval.

**Strengths:**
- Clear, machine-checkable schema (M1) grounded in SymPy/OpenMath/QUDT with enforced required fields.
- Enumerated Assumption/Approximation Ontology (M2) with hierarchical relations, preventing free-text drift.
- Well-typed ECP semantics with explicit pre/post conditions and failure classes, separating coupling errors from equation misuse.
- EOE/EMP provenance and effectiveness grading with datasets and CIs, discouraging unverifiable claims (M4).
- Pre-registered, falsifiable RAG evaluation with ablation and calibration requirements (M5).
- Crypto sub-appendix correctly separates compute regimes and avoids unsafe/meaningless sandbox execution for intractable instances.

**Concerns:**
- ECP post-condition appears incorrect: e·f = ė·ḟ is dimensionally inconsistent; power-conserving Dirac structures require Σ_i e_i f_i = 0 (and transformer/gyrator relations), not equality of time-derivative products.
- Three ECP classes are not exhaustive: non-power-conserving signal/information coupling (measurement, feedback, controllers, observers) is missing and cannot be shoehorned into INTER_DOMAIN_TRANSDUCTION.
- Domain-of-validity inequalities mix dimensioned quantities without an explicit guarantee of dimensionlessness or reference scaling; semantics for computing, checking, and binding U, f, L, etc., to units and frames need to be formalized.
- Small-parameter error_scaling uses informal big-O without a certificate or bound; no mechanism to attach validated asymptotic error bounds or regimes of uniform validity.
- CONSTITUTIVE_CLOSURE post-condition uses a simple rank=states criterion, which is insufficient for DAEs; well-posedness should reference DAE index analysis (e.g., mass-matrix invertibility, Pantelides/Pryce structural methods).
- Frame and symmetry fields (e.g., galilean_invariant, rotation_invariant) are underspecified; invariance should be tied to named Lie groups with explicit transformation laws and automated tests.
- Crypto sub-appendix lacks security-parameterized semantics: no explicit (λ, instance distribution, adversary class, time/query resources, reduction tightness/advantage bound) fields; ROM vs standard-model distinctions are not instantiated with concrete advantage bounds.
- AAO seed set misses several ubiquitous physical approximations (e.g., low_Mach, Boussinesq, hydrostatic, thin_film/lubrication, quasi_neutral_plasma, WKB/Born–Oppenheimer, LTE vs non-LTE) that frequently gate validity.
- RAG benchmark size (n=300) may be underpowered across multiple strata and metrics without a pre-registered power analysis; calibration/refusal metrics need a clear selective-prediction protocol.
- Detection_methods in EWE entries report point FPRs without required datasets/uncertainty links (EMP enforces this; EWE should reference EMP or EOE for empirical support).

**Required modifications:**
- Correct ECP power semantics: replace the post-condition "e·f = ė·ḟ" with standard port-Hamiltonian/Dirac constraints. Required: (i) for junctions, Σ_i e_i f_i = 0 to numerical tolerance; (ii) for transformers/gyrators, enforce constitutive effort/flow mappings that imply power conservation; (iii) include unit tests that compute total power residuals and stored-energy balance over transients.
- Add a fourth, disjoint ECP category for non-energy coupling: SIGNAL_FLOW_COUPLING (or INFORMATION_COUPLING). Pre: typed signal ports with causality (input/output), optional stochastic/noise model; Post: well-defined functional/transfer relationship, no net power flow, and stability/causality constraints where applicable. Include failure classes (e.g., causality_violation, algebraic_loop_without_delay, estimator_mismatch).
- Formalize domain_of_validity semantics: (i) enforce that inequalities are expressed over dimensionless groups (automatic unit-normalization or explicit Pi-groups); (ii) bind symbols to QUDT units and frames; (iii) specify how derived quantities (e.g., Rossby number) are computed and validated; (iv) add static checks that reject dimensioned inequalities and missing unit bindings.
- Strengthen small-parameter error semantics: add fields for asymptotic certificate type (e.g., rigorous bound, matched asymptotics heuristic), bound function B(ε) or citation to a validated remainder estimate, and the domain over which the bound holds (uniform vs pointwise).
- Refine CONSTITUTIVE_CLOSURE well-posedness: replace the plain rank check with DAE-oriented analysis. Add fields for mass matrix, structural index (Pantelides/Pryce/Sigma-method outcome), and a post-condition that index ≤ 1 (or explicitly recorded if higher) with justification and numerical test cases that verify solvability.
- Upgrade symmetry/frames: encode invariances against named groups (Galilean, Lorentz, SO(3), SE(3), parity, time-reversal) with transformation rules for variables and an automated invariance test (symbolic or numeric). Deprecate bare booleans in favor of typed group-annotations and tests.
- Crypto parameterization: extend CRYPTO_REDUCTION and crypto AAO entries with mandatory fields: security_parameter λ; instance_distribution; adversary_class (classical/quantum) with resource bounds (time, queries, memory); reduction_type (tight/concrete) with explicit advantage/time bound function Adv_A(λ, t, q, …); proof_citation (DOI/arXiv) and, where possible, mechanized proof artifact references (EasyCrypt/CryptoVerif/FCF/Tamarin).
- Augment crypto regime verification: for REGIME-HEAVY/INFEASIBLE, require multi-source cross-checks anchored to standard test vectors (e.g., NIST KATs) with artifact hashes/DOIs, and encode parameterized security levels (e.g., NIST categories) as machine-checkable fields.
- Expand AAO with high-frequency tags: low_Mach (ChildOf non_relativistic), Boussinesq (ChildOf incompressible), hydrostatic (ChildOf quasistatic), thin_film_lubrication (ChildOf scale_separation), quasi_neutral_plasma (ChildOf continuum_limit), WKB and Born_Oppenheimer (ChildOf scale_separation/weak_coupling), LTE_vs_nonLTE disambiguation. Provide formal definitions and references for each.
- Benchmark rigor: add a pre-registered power analysis justifying n=300 for the targeted effect sizes across strata; specify the selective-prediction protocol for refusals (thresholding/calibration method), report AUROC/AUPRC for refusal in addition to precision, and pre-register the statistical tests and multiple-comparison corrections.

### gemini-2.5-pro

**COI:** ⚠ The core concepts (bond graphs, port-Hamiltonian systems, dimensional analysis with QUDT, SymPy, MITRE ATT&CK analogies, pre-registered experiments) are all well-represented in the training corpus. The specific synthesis into the EWE/ECP/EOE/EMP framework as presented is novel.  
**Verdict:** `modify`  
**Headline:** The proposed framework is exceptionally rigorous, technically sound, and well-grounded in established physical modeling principles, with a gold-standard evaluation protocol, but its equation composition typology needs to be extended to cover non-power-conserving informational coupling.

**Strengths:**
- The EWE schema provides a powerful, machine-checkable representation of an equation's validity domain, grounded in established standards like SymPy, OpenMath, and QUDT.
- The ECP classification correctly leverages the powerful formalisms of port-Hamiltonian systems and bond graphs to categorize energy-conserving physical system compositions, which is a significant leap beyond simple graph linking.
- The pre-registered RAG evaluation protocol is a model of scientific integrity, providing a sharp, falsifiable test of the core hypothesis that the structured fields provide value over prose-only methods.
- The cryptographic sub-appendix demonstrates foresight and technical depth, correctly identifying the unique failure modes and composition semantics of a domain not governed by physical conservation laws.
- The grounding of the knowledge base in empirical evidence via the EOE and EMP schemas, with requirements for provenance and quantitative effectiveness, provides a robust defense against unsubstantiated claims.

**Concerns:**
- The three proposed ECP categories (Conservation, Constitutive, Transduction), while correctly capturing energy-based physical modeling, do not explicitly account for non-power-conserving, signal-flow coupling common in control systems and cyber-physical systems. This represents a potential gap in the typology's exhaustiveness.
- The success of the AAO will depend critically on the long-term rigor of the governance process for adding new tags; a low bar for entry could dilute the ontology's value.

**Required modifications:**
- Add a fourth, disjoint ECP category, such as `INFORMATIONAL_COUPLING` or `CONTROL_MODULATION`, to formally model non-power-conserving signal flows. This category must have its own pre- and post-conditions to distinguish it from power-conserving transduction, addressing cases where a variable in one equation modulates a parameter in another without an associated back-action or energy exchange (e.g., a sensor reading controlling a valve).

### grok-4

**COI:** no COI  
**Verdict:** `approve`  
**Headline:** v2 effectively addresses all v1 modifications with rigorous, falsifiable structures and a sound crypto extension.

**Strengths:**
- Pre-registered benchmark provides strong falsifiability, with clear pass/fail criteria and ablation tests to verify structured value.
- Machine-checkable fields and AAO ontology enforce rigor and prevent free-text drift, aligning well with first-principles verifiability.
- Crypto sub-appendix thoughtfully handles infeasible computations via regimes and proof-theoretic checks, maintaining soundness without overclaiming computability.

**Concerns:**
- ECP classification into three disjoint categories is exhaustive for the specified domains but may not fully capture emergent quantum or statistical couplings without evidence of overlooked classes.
- AAO seed set of 24 tags is a solid foundation but lacks explicit tags for quantum-specific assumptions like decoherence-free subspaces, though this is not fatal given the board-review process for additions.

