# EWE Concept Review v3 — 4-Phase Academic Protocol

**Query:** `ewe_concept_review_v3`  
**Include Grok:** True  
**Editor verdict:** `modify`

**All responded (Phase A):** True  
**All responded (Phase B):** True

## Phase C — Editor synthesis (binding)

**Verdict:** `modify`

**Rationale:**

Three of four reviewers independently converge on MODIFY with highly specific, technically grounded concerns, while the lone APPROVE (grok-4, rubric mean 4.40) characterizes the same gaps as 'minor peer-suggested refinements' without substantively rebutting them. On close examination, the MODIFY arguments are visibly stronger: (1) The modulated Dirac-structure gap (raised by claude-opus-4-6 and gemini-2.5-pro) is not cosmetic — state-dependent J(x) is the norm in nontrivial port-Hamiltonian systems, and the current postcondition's silence on whether skew-symmetry is checked symbolically with x as a free symbol or pointwise is a correctness defect in the verification pipeline. (2) The RATE_COUPLING postcondition's requirement to compute eigenvalue spectra 'at each declared fixed point' is under-specified: fixed-point enumeration is undecidable for general nonlinear systems, so the postcondition is not machine-checkable without an explicit user-declaration protocol and UNDETERMINED fallback — exactly the kind of systems (Lotka-Volterra, Boltzmann transport) that motivated the class. (3) The DOV-DSL quantifier gap (claude-opus-4-6) and QROM quantum-query-complexity omission (claude-opus-4-6, openai-gpt-5) are genuine schema completeness issues that will cause silent misclassification or omission of security-critical parameters. (4) The exhaustiveness argument for four ECP classes resting on 16 examples rather than a constructive partition of coupling modalities is a falsifiability concern — boundary-condition coupling (FSI) and algebraic-constraint coupling are not obviously covered. grok-4's higher rubric score does not outweigh the fact that it does not engage with these specific technical objections. The submission is architecturally sound and the RATE_COUPLING addition is well-motivated, but four precisely-scoped modifications are required before the verification claims are actually machine-checkable and the schema is complete.

**Required modifications:**
- M1 — RATE_COUPLING fixed-point protocol: Specify that fixed points are user-declared (not auto-discovered). Add an explicit UNDETERMINED status when symbolic eigenvalue computation fails or times out. A RATE_COUPLING entry with zero declared fixed points must be valid but tagged stability_status: NOT_ASSESSED. This makes the postcondition machine-checkable for the nonlinear systems that motivated the class.
- M2 — Modulated (state-dependent) Dirac structures: Extend the Dirac-structure postcondition to handle J(x). The skew-symmetry check must be performed symbolically with state variables as free symbols (sp.simplify(J(x) + J(x).T) == 0). If symbolic verification is infeasible, fall back to numerical sampling over the declared domain with explicit coverage criteria and an UNVERIFIED_SYMBOLICALLY flag. Without this, a majority of real INTER_DOMAIN_TRANSDUCTION instances (robot arms, Euler equations on SO(3), configuration-dependent mass matrices) are silently mis-verified.
- M3 — DOV-DSL quantifier scope and QROM query semantics: (a) Either add restricted universal/existential quantifiers to the DOV-DSL grammar or explicitly declare the grammar handles only pointwise-evaluable conditions, routing quantified validity conditions to a separate provenance field. (b) Add explicit quantum_oracle_queries_bounded and q_quantum fields to the CRYPTO_REDUCTION schema to prevent silent omission of quantum query complexity in QROM-model reductions (Kyber, Dilithium).
- M4 — ECP exhaustiveness argument: Replace the 16-example coverage table (necessary but insufficient) with a constructive partition argument over inter-equation coupling modalities. Explicitly address coupling via shared boundary conditions (e.g., fluid-structure interaction where geometry is the shared variable) and algebraic-constraint coupling, showing they reduce to one of the four classes or adding a fifth class if they do not.

## Phase B — Informed votes

### claude-opus-4-6

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** v3 is architecturally sound and addresses all five v2 modifications credibly; four precisely-scoped technical gaps must be closed before APPROVE, all of which are tractable.

**Response to peers:**

Claude-Opus raised five concerns; I agree with all five and consider them the most technically precise of any reviewer. (1) RATE_COUPLING fixed-point undecidability: exactly right — the postcondition as written is not machine-checkable for general nonlinear systems. User-declared fixed points with UNDETERMINED fallback is the correct fix. (2) Modulated Dirac structures: this is the concern I would have led with. Every nontrivial port-Hamiltonian system (robot arms, Euler equations, anything with a configuration-dependent inertia) has state-dependent J(x). The symbolic check must be performed with x as free SymPy symbols, and the entry must declare modulated: true. This is not an edge case; it is the common case. I fully endorse M2. (3) DOV-DSL quantifier scope: agreed. The DSL must explicitly declare itself pointwise-evaluable and route quantified conditions (Lyapunov existence, universal domain statements) to a separate field. Silent misclassification is a real risk otherwise. (4) Quantum query parameters for QROM: all four reviewers converged on this independently, which is strong evidence it is a genuine gap. A single advantage_loss_factor can technically encode both classical and quantum query counts, but requiring explicit q_quantum and superposition_queries_bounded fields prevents silent omission — this is a schema-design correctness issue, not just a convenience. (5) Calibration bucket specification: reasonable but lower priority; I would accept it as a SHOULD rather than MUST. — GPT-5 raised several additional concerns. The PDE/kinetic-equation point (operator-valued Jacobians for Boltzmann transport) is valid: RATE_COUPLING postconditions implicitly assume finite-dimensional ODEs, but the coverage table includes Boltzmann transport which is infinite-dimensional. Either restrict RATE_COUPLING to finite-dimensional systems with a PDE annex, or specify the discretization/truncation obligation. The stochastic coupling proposal (Itô/Stratonovich fields) is techn

### openai-gpt-5

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** v3 is materially stronger and buildable in principle; approve once Dirac generalization, RATE_COUPLING well‑posedness (ODE vs operator), DOV‑DSL scope/units, and QROM query semantics are explicitly codified.

**Response to peers:**

claude-opus-4-6
- Fixed-point semantics in RATE_COUPLING: Agree. The postcondition must be machine-checkable without implicit global root-finding. Require a declared_fixed_points list; verify Jacobian spectra at those points symbolically (free symbols) with numerical fallback and an UNDETERMINED status on timeout. Allow zero declared points with stability_status: NOT_ASSESSED. This directly addresses undecidability in nonlinear PDE/kinetic exemplars.
- Modulated Dirac structures: Agree. Add modulated: true when J = J(x) and require a symbolic check J(x)+J(x)^T = 0 with x free; do not collapse to pointwise numeric checks. I also recommend accepting an equivalent implicit/junction form (isotropy test) alongside explicit J; see below under openai-gpt-5.
- DOV-DSL quantifiers: Agree. Make the scope explicit: DOV-DSL is pointwise-evaluable only. Add validity_meta.quantified_conditions for universal/existential statements (Lyapunov/existence-of-function claims) with provenance grading. This prevents silent misuse.
- QROM quantum queries: Agree. Add quantum_query_parameters: {q_quantum, superposition_queries_bounded} and require reference to q_quantum in advantage_loss_factor/postcondition_advantage_bound when security_model.name == QROM.
- Calibration buckets: Agree. Fix Gate 2 to 10 equal-mass buckets (deciles), compute Brier on the full set, and enforce per-bucket |obs − conf| ≤ 0.15. Keep numerical-fallback guidance explicit.
- Exhaustiveness/boundary couplings: The four-class partition is plausible but the argument should explicitly classify shared-boundary/geometry couplings. Either (i) treat boundary ports as INTER_DOMAIN_TRANSDUCTION (power-preserving boundary flows) or (ii) treat geometry/BC resolution as CONSTITUTIVE_CLOSURE when it algebraically closes unknowns. Spell this out with a fluid–structure interaction normative example and a decision rule.

openai-gpt-5
- RATE_COUPLING scope and well-posedness: Agree. Baseline RATE_COUPLING should be normatively ODE/C1

### gemini-2.5-pro

**Verdict:** `modify`  
**Position change:** moderated  
**Headline:** V3 is a significant improvement, but its handling of power-conserving interconnections is critically incomplete without support for modulated (state-dependent) Dirac structures.

**Response to peers:**

My initial assessment was highly positive, aligning with Gemini-2.5-pro's view. However, after reviewing the Phase A reports, my position has moderated. I now believe several modifications are non-negotiable for approval. Specifically:

1.  **On Modulated Dirac Structures (Claude, OpenAI):** I strongly concur. The current postcondition for INTER_DOMAIN_TRANSDUCTION, limited to constant `J`, is inadequate. The vast majority of non-trivial port-Hamiltonian systems, from robotics to fluid dynamics, rely on modulated, state-dependent Dirac structures `J(x)`. This is not an edge case; it is the standard case. Grok's 'approve' verdict misses the severity of this omission. The framework is not fit for purpose in its current state. I endorse OpenAI's suggestion to allow two verification modes: (1) a symbolic check on `J(x) + J(x).T == 0` for explicit structures, and (2) an implicit junction form for bond-graph style interconnections, checking `⟨e, f⟩ = 0` on the constraint space. This is a mandatory correction.

2.  **On RATE_COUPLING Postcondition (Claude, OpenAI):** I agree that requiring the computation of eigenvalue spectra at *all* fixed points is non-computable in general. The postcondition is therefore not machine-checkable as written. Claude's proposed solution—requiring user-declaration of fixed points for local analysis and providing an explicit 'UNDETERMINED' status on failure—is the correct, pragmatic path to making this feature verifiable.

3.  **On DOV-DSL Scope and Units (Claude, OpenAI):** Both reviewers correctly identify weaknesses. I find two proposed modifications essential. First, Claude's proposal to explicitly scope the DSL to pointwise-evaluable conditions is necessary to prevent silent misuse for quantified statements. Second, OpenAI's call to add machine-checkable dimensional analysis is non-negotiable for a framework intended to model physical reality. Composing equations without verifying dimensional consistency is a source of fundamental errors.

### grok-4

**Verdict:** `approve`  
**Position change:** unchanged  
**Headline:** v3 robustly addresses prior issues with verifiable enhancements, maintaining technical soundness and warranting approval despite minor peer-suggested refinements.

**Response to peers:**

Claude's concerns on RATE_COUPLING fixed points are valid but not fatal—user-declared points suffice for falsifiability without requiring undecidable automation, so I push back as this doesn't undermine buildability; modulated Dirac is a good point from physics, but v3's formulation covers core cases symbolically, and extension can happen post-approval without evidence of overclaim; DOV-DSL quantifiers gap is real but the submission honestly scopes to pointwise conditions, avoiding silent misuse via explicit binding—agree but not a blocker; quantum queries in CRYPTO_REDUCTION should be added for QROM completeness, but current fields handle classical bounds verifiably, so partial agreement without changing verdict; exhaustiveness argument is evidence-based via coverage table, and boundary couplings fit existing classes per examples. OpenAI's PDE/SDE extensions for RATE_COUPLING are ambitious but exceed v3's finite-dimensional scope—push back as the submission doesn't claim PDE coverage, and adding now would be premature without evidence of necessity; block-diagram handling fits RATE_COUPLING as-is, per submission's signal-flow matrix; DOV-DSL hygiene suggestions (separate declarations, operators) improve usability but aren't required for soundness or parsability; Dirac generalization to implicit modes is technically meritorious but v3's matrix mode is falsifiable and prior-art aware, so not essential; stochastic support is a nice-to-have, not a gap in claimed coverage. Gemini's quantum query extension for CRYPTO_REDUCTION aligns with my partial agreement on Claude's point—it's a clarification worth noting but doesn't falsify v3's post-quantum handling, as advantage expressions can implicitly include it; notation and ECE suggestions are minor polish, not soundness issues. Overall, peers raise thoughtful refinements, but none expose unsubstantiated claims or unverifiable mechanisms, preserving my approve stance on technical merit.

## Phase A — Independent drafts

### claude-opus-4-6

**COI:** ⚠ I have likely seen prior versions of this EWE/ECP/EOE/EMP framework in training data, including v1 and v2 review discussions. I have general training-time exposure to all cited references (van der Schaft, Bellare-Rogaway, Katz-Lindell, Duindam et al., Pantelides, Pryce). I have no financial or personal conflict.  
**Verdict:** `modify`  
**Headline:** v3 is a substantial and mostly correct advance; three technical gaps remain that must be closed before APPROVE, none of which threatens the architecture.

**Strengths:**
- RATE_COUPLING is well-motivated and the mutual-exclusivity enforcement via ordered pre-condition testing is a clean design; the 16-equation coverage table is the right kind of evidence and the examples are correctly classified.
- DOV-DSL grammar is appropriately restrictive; the decision to emit SymPy ASTs and reuse the same grammar for CRYPTO_REDUCTION advantage bounds is sound and avoids two parsers for one job.
- Corrected Dirac-structure postcondition is now textbook-correct, the van der Schaft and Duindam citations are the right ones, and the symbolic-first / numerical-fallback verification strategy is the right ordering.
- Promoting calibration to a non-fungible hard gate in HEQU-BENCH-001 is the correct safety-critical decision; the dual condition (relative to baseline AND absolute Brier ≤ 0.10) prevents gaming.
- CRYPTO_REDUCTION formal fields are substantially improved; the verifiable_when guard region that returns ADVANTAGE_BOUND_OUTSIDE_PROVEN_REGION rather than a false positive is exactly the right epistemic move.
- Prior-art engagement is excellent across all five modifications — Pantelides/Pryce for DAE index, Fujisaki-Okamoto for KEM reduction, Bellare-Rogaway for ROM, van der Schaft for port-Hamiltonian structures.
- The explicit questions posed to the board are well-formulated and demonstrate genuine uncertainty about the right boundaries, which is a mark of intellectual honesty.

**Concerns:**
- RATE_COUPLING postcondition requires computing the Jacobian eigenvalue spectrum 'at each declared fixed point,' but the set of fixed points is itself undecidable for general nonlinear systems. The postcondition needs a fallback: either (a) fixed points are user-declared and the system only verifies local Jacobian properties at those points, or (b) a symbolic root-finder is attempted with an explicit timeout and UNDETERMINED status. Without this, the postcondition is not machine-checkable for the very systems (Lotka-Volterra with many equilibria, Boltzmann transport) that motivated the class.
- The Dirac-structure postcondition as stated covers only constant (state-independent) Dirac structures. Modulated Dirac structures — where J = J(x) depends on state — arise in every nontrivial port-Hamiltonian system (e.g., a robot arm, Euler equations on SO(3), any system with configuration-dependent mass matrix). The skew-symmetry check J(x) + J(x)^T = 0 must hold pointwise, and v3 does not clarify whether the symbolic check is performed with x as a free symbol or at evaluated points. This is not a minor edge case; it covers a majority of real INTER_DOMAIN_TRANSDUCTION instances.
- DOV-DSL grammar lacks quantifiers. Validity conditions like 'for all x in domain D, Re(x) > 0' or 'there exists a Lyapunov function' cannot be expressed. The grammar should either (a) explicitly declare it handles only pointwise-evaluable conditions and route quantified conditions to a separate provenance field, or (b) add restricted universal/existential quantifiers. Currently the boundary is implicit, which will cause silent misclassification of validity domains that require universal statements.
- CRYPTO_REDUCTION is missing a dedicated field for quantum query complexity (number of superposition queries to oracles), which is distinct from classical oracle query count. For QROM-model reductions (Kyber, Dilithium), the advantage loss factor depends on both classical and quantum query counts with different exponents. A single advantage_loss_factor expression can encode this, but the schema should require explicit quantum_oracle_queries_bounded: true/false and q_quantum parameter to prevent users from silently omitting the quantum query dimension.
- The 16-equation coverage table is necessary but not sufficient for an exhaustiveness argument. The claim that four classes are exhaustive requires a constructive argument about what forms of inter-equation dependency exist, not just that 16 examples each fit one class. The four classes partition couplings into: shared conserved quantity, closure of algebraic freedom, effort-flow port pairing, and rate-term signal flow. What about coupling via shared boundary conditions (e.g., fluid-structure interaction where geometry is the shared variable, not a rate term and not a conserved quantity)? This may fit CONSTITUTIVE_CLOSURE, but the argument needs to be made explicitly.
- HEQU-BENCH-001 Gate 2 specifies Brier score ≤ 0.10 and per-bucket deviation ≤ 0.15, but does not specify the number or spacing of calibration buckets. With 3 buckets, 0.15 per-bucket tolerance is extremely permissive; with 100 buckets, sampling noise makes it nearly impossible to pass. The bucket count and whether buckets are equal-width or equal-mass must be specified for the gate to be reproducible.

**Required modifications:**
- M1: RATE_COUPLING postcondition must specify that fixed points are user-declared (not automatically discovered) and add explicit UNDETERMINED status when symbolic eigenvalue computation fails. The postcondition should read: 'For each declared_fixed_point, the linearized Jacobian eigenvalues are computed symbolically if possible, numerically otherwise, with UNDETERMINED status if neither succeeds within timeout. A RATE_COUPLING entry with zero declared fixed points is valid but receives stability_status: NOT_ASSESSED.'
- M2: Dirac-structure postcondition must be extended to modulated (state-dependent) Dirac structures. The symbolic skew-symmetry check sp.simplify(J(x) + J(x).T) == 0 must be performed with state variables as free SymPy symbols. If J depends on state, the entry must declare modulated: true, and the verification is symbolic-over-free-variables, not pointwise. Cite van der Schaft & Maschke (2002) 'Hamiltonian formulation of distributed-parameter systems with boundary energy flow' or Duindam Ch 4 for the modulated case.
- M3: DOV-DSL specification must add an explicit scope declaration: 'DOV-DSL expresses pointwise-evaluable conditions only. Conditions requiring universal quantification over continuous domains, existence of auxiliary functions (Lyapunov, entropy), or measure-theoretic statements must be recorded in a separate validity_meta.quantified_conditions free-text field with provenance_grade: TEXTBOOK or DERIVED.' This prevents silent misuse of the DSL for statements it cannot evaluate.
- M4: CRYPTO_REDUCTION schema must add quantum_query_parameters: {q_quantum: <int_or_symbol>, superposition_queries_bounded: true/false} as a required field when security_model.name is QROM. The advantage_loss_factor expression must reference q_quantum explicitly in QROM entries. This is not optional for Kyber/Dilithium correctness.
- M5: HEQU-BENCH-001 Gate 2 must specify calibration bucket parameters: 10 equal-mass buckets (each containing 10% of test predictions), per-bucket |observed_accuracy - stated_confidence| ≤ 0.15, and Brier score computed over the full un-bucketed prediction set. State explicitly that bucket count is fixed at 10 and not a tunable parameter.

### openai-gpt-5

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** v3 materially strengthens the framework (RATE_COUPLING, DOV-DSL, Dirac fix, crypto fields, calibration gate) but needs precise generalizations and semantics for Dirac structures, DSL declarations/units, PDE/SDE handling, and crypto-bound formalization before approval.

**Strengths:**
- RATE_COUPLING is well-motivated with clear pre-/post-conditions, an explicit stoichiometric/signal-flow matrix S, and stability recording at fixed points.
- DOV-DSL introduces a parsable, bind-checked subset with propagation of UNOBSERVABLE states into the existing failure protocol, improving falsifiability and auditability.
- INTER_DOMAIN_TRANSDUCTION correction to skew-symmetric structure is textbook-accurate and backed by strong citations; numerical fallback is reasonable.
- DAE awareness via Pantelides/Pryce structural-index requirement is an appropriate strengthening of CONSTITUTIVE_CLOSURE postconditions.
- CRYPTO_REDUCTION fields capture reduction type, model, and a machine-parsable bound with a verifiable-when guard, aligning with standard proof obligations (ROM/QROM/UC).
- Calibration upgrade to a hard gate with explicit Brier and reliability-diagram criteria directly addresses safety and evaluation leakage risks.

**Concerns:**
- RATE_COUPLING postconditions implicitly assume finite-dimensional, C1 dynamics; coverage examples include PDE/kinetic equations where Jacobians and spectra are operator-valued—discretization/functional-analytic obligations are unspecified.
- Block-diagram control couplings (PID, state feedback) and algebraic loops are not normatively handled; well-posedness (e.g., input-output stability, loop solvability) is not checked beyond Jacobian existence.
- DOV-DSL grammar blends use and declaration (NAMED_GROUP via ':=' inside atom) and lacks a clear declaration phase, unit/dimension typing, and NOT/min/max operators; symbol resolution for constants/parameters is under-specified.
- The Dirac postcondition is restricted to an explicit matrix J; general Dirac structures (implicit/junction forms, modulated J(x), constraint-based interconnections) can be power-preserving without admitting a global constant J matrix.
- CRYPTO_REDUCTION evaluates a relation containing Adv_A with DOV-DSL rules that require bound identifiers; the semantics should express a universally quantified bound (template) and separate the computable RHS from the uninterpreted LHS; also missing separate quantum/classical query counters and precise definitions for 'tight' vs 'exact'.
- Calibration gate lacks details for multi-class Brier normalization, binning policy (min counts, Wilson intervals), and significance control; the 0.10 absolute threshold may interact poorly with very large label spaces.
- Coverage table contains a misleading 'Schrödinger+Maxwell → QED' label; what is implemented is minimal coupling (Pauli/Schrödinger with gauge fields), not QED.
- Stochastic couplings (SDEs; Ito vs Stratonovich; diffusion cross-coupling) are not represented; RATE_COUPLING as stated addresses only deterministic drift terms.

**Required modifications:**
- RATE_COUPLING scope and well-posedness: (a) explicitly restrict to finite-dimensional ODEs or add a PDE/kinetic annex specifying the discretization/operator model used for Jacobians and spectra, including how fixed points are defined and sampled; (b) require a Lipschitz/Carathéodory condition or DOV-DSL-asserted differentiability on the declared domain; (c) add an algebraic-loop solvability check (e.g., implicit function or structural nonsingularity) for signal-flow couplings; (d) include a normative PID/controller example and state that pure block-diagram feedback falls under RATE_COUPLING with S as the signal adjacency.
- Introduce stochastic coupling support: add optional fields {stochastic: true|false, calculus: Ito|Stratonovich, diffusion_matrix: sympy, noise_coupling_S: matrix mapping states to diffusion terms} and require corresponding well-posedness checks (nondegeneracy, linearization via Lyapunov for mean-square stability when declared).
- DOV-DSL hygiene: separate NAMED_GROUP declarations from boolean formulas (two-phase parse with a symbol table); add operators NOT, min, max; allow constants and parameters declared in canonical_equation (with explicit typing).
- Units/dimensional analysis: add an optional but machine-checkable dimension system; require NAMED_GROUPs flagged as dimensionless with automatic rejection when units do not cancel; surface unit-consistency failures as parsing errors.
- Dirac structures generalization: allow two equivalent verification modes: (1) structure-matrix mode with state-dependent J(x) and a symbolic check J(x) + J(x)^T = 0; (2) implicit/junction mode using incidence/constraint matrices (e.g., Af = 0, e = A^Tλ) with machine-check of isotropy ⟨e,f⟩ = 0 for all admissible (f,e); document both and accept either as satisfying INTER_DOMAIN_TRANSDUCTION.
- CONSTITUTIVE_CLOSURE (DAE) additions: require reporting of consistency conditions and stabilization strategy (e.g., Baumgarte parameters or projection), and ensure the structural index computation is reproducible (tool, version, signature matrix).
- CRYPTO_REDUCTION semantics: replace 'postcondition_advantage_bound.sympy_ast' with a pair {bound_rhs: sympy_expr over security params, bound_relation: 'for_all A in adversary_class: Adv_A(params) <= bound_rhs'}; parse only bound_rhs; evaluate numerically under verifiable_when; keep Adv_A symbolic and uninterpreted; document proof citations and loss tightness assumptions.
- Crypto query accounting: add separate fields for classical vs quantum oracle queries (q_classical, q_quantum) and explicitly define 'reduction_type' taxonomy (exact = equality, tight = constant-factor loss, polynomial = poly loss in parameters, loose = known suboptimal).
- Calibration gate formalization: (a) define multi-class Brier as mean squared error over the full label distribution with normalization; (b) fix reliability binning (e.g., 10 equal-width bins) with a minimum per-bin count or Wilson-adjusted tolerance; (c) add ECE(10) as an additional hard check or include a CI-based test (bootstrap) to avoid false rejections on low-count bins; (d) specify how refusals are scored under abstention (proper scoring for selective prediction).
- Coverage and nomenclature cleanup: change 'Schrödinger+Maxwell → QED' to 'Schrödinger with minimal EM coupling (Pauli/Schrödinger + gauge)' and add a note on when quantum field theoretic couplings are out of scope for current ECP classes.

### gemini-2.5-pro

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** A technically superb and rigorous v3 that robustly addresses all prior concerns; approval is contingent on one minor clarification in the quantum security model.

**Strengths:**
- The introduction of the RATE_COUPLING class, supported by a compelling coverage proof, successfully closes the framework's exhaustiveness gap for non-power-conserving systems.
- The formal, machine-checkable nature of the DOV-DSL, crypto reduction fields, and DAE index checks represents an exemplary commitment to rigor and falsifiability.
- The promotion of calibration to a hard, non-fungible gate in HEQU-BENCH-001 is a critical and well-justified design choice for system safety and reliability.
- The corrections to the port-Hamiltonian post-conditions and the introduction of structural index analysis for DAEs demonstrate a deep and accurate engagement with prior art in physical systems theory.

**Concerns:**
- The notation for the Dirac structure interconnection `(f, e) ↦ J · (f, e)` is slightly non-standard, though the resulting machine-verifiable assertion `⟨e, f⟩ = 0` is correct. Aligning with textbook port-Hamiltonian notation (e.g., defining the map on the port variables `[e; f]`) would improve clarity.
- While the proposed calibration metrics (Brier score, reliability diagram) are strong, the addition of Expected Calibration Error (ECE) to HEQU-BENCH-001 could provide a more comprehensive single-statistic summary of calibration performance.
- The answer to Question 1 is that pure signal-flow models like PID controllers fit cleanly into the RATE_COUPLING class via its signal-flow matrix S, without needing a fifth class.

**Required modifications:**
- For CRYPTO_REDUCTION specifications under the QROM security model, the schema must be extended to explicitly accommodate bounds on quantum oracle queries (e.g., a `q_quantum` variable) in addition to classical queries (`q_h`, `q_s`). The `advantage_loss_factor` and `postcondition_advantage_bound` expressions must then be able to reference this variable to be fully expressive for post-quantum analyses.

### grok-4

**COI:** no COI  
**Verdict:** `approve`  
**Headline:** v3 effectively addresses all five required modifications with rigorous, verifiable enhancements, closing key gaps in the framework's soundness and coverage.

**Strengths:**
- RATE_COUPLING class addition provides a clean, exhaustive categorization with machine-enforceable preconditions and postconditions, supported by a comprehensive coverage table.
- DOV-DSL formal grammar introduces precise, parseable validity constraints tied directly to failure protocols, enhancing falsifiability.
- Corrected Dirac-structure postcondition aligns with established bond graph theory, with symbolic verification and DAE index checks adding technical rigor.
- CRYPTO_REDUCTION formal fields enable verifiable security reductions, including post-quantum cases, with symbolic expressions for advantage bounds.
- Elevation of calibration to a hard gate in HEQU-BENCH-001 enforces critical safety without overclaiming capabilities.

**Concerns:**
- RATE_COUPLING's handling of pure signal-flow systems (e.g., PID controllers) fits but could benefit from explicit examples to confirm no fifth class is needed; current evidence supports exhaustiveness but lacks edge-case disproof.
- DOV-DSL is a solid restriction but doesn't reference or align with existing standards like MathML or Lean, potentially missing interoperability opportunities—though not a fatal flaw.
- Structural index check for DAEs is appropriate but could be strengthened by mandating signature matrix methods for higher-index cases, as Pantelides/Pryce has known limitations in complex systems.

