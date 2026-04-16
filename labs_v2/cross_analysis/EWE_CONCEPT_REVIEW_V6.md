# EWE Concept Review v6 — 4-Phase Academic Protocol

**Query:** `ewe_concept_review_v6`  
**Include Grok:** True  
**Editor verdict:** `modify`

**All responded (Phase A):** True  
**All responded (Phase B):** True

## Phase C — Editor synthesis (binding)

**Verdict:** `modify`

**Rationale:**

All four reviewers independently converge on MODIFY with rubric means of 4.80–5.00, and the quality of their reasoning is uniformly strong. v6 represents a genuine and rigorous correction of the five v5 deficiencies: the Itô isometry reclassification from postcondition to derived consequence is mathematically correct, the Lotka-Volterra Lyapunov function is now symbolically verified with the proper per-species coefficients, and the scope predicates, singularity pre-screen, and index vocabulary are all well-structured. However, all four reviewers independently identify the same three critical technical gaps, and their arguments are sound on the merits: (1) Progressive measurability: The current C1 postconditions (adaptedness + square-integrability) are sufficient only for continuous diffusion coefficients, but the spec does not state this restriction. For non-continuous integrands, progressive measurability is the correct condition (Revuz-Yor §IV.2, Protter §II.4). This is not a pedantic refinement — it is a correctness boundary that must be explicitly drawn. (2) Jump-process scoping: The C3 scope predicate will incorrectly classify Lévy-driven and jump-diffusion SDEs as STOCHASTIC_COUPLING, yet the C1 postconditions cover only the continuous-martingale part and say nothing about compensated Poisson integrals. This creates a silent gap where models pass classification but receive incomplete verification — precisely the failure mode the framework exists to prevent. A Q5e exclusion branch or extended postconditions are required. (3) Numerical singularity fallback: The symbolic det(J)=0 pre-screen will effectively time out for structured matrices of moderate rank, rendering the check vacuous in the regime where it matters most. A numerical SVD sampling fallback with declared budget and threshold is needed not as an alternative but as a complement when symbolic methods are inconclusive. Two additional points raised by individual reviewers also have merit: relabeling the LV certificate as a 'first integral' rather than 'Lyapunov function' (since dV/dt=0 establishes conservation, not asymptotic stability — a meaningful semantic distinction), and extending the square-integrability condition to Hilbert-Schmidt norms for multi-dimensional Wiener processes. These are technically correct observations that strengthen precision. There is no substantive disagreement among reviewers — the convergence is genuine and well-reasoned.

**Required modifications:**
- C1 progressive measurability: Either (a) add an explicit scope restriction stating STOCHASTIC_COUPLING postconditions assume continuous diffusion coefficients, with a note that adaptedness implies progressive measurability in this case, OR (b) add a third postcondition 'diffusion_integrand_progressively_measurable' with verification algorithm (auto-derived for continuous coefficients; requires explicit attestation with citation for discontinuous integrands). Cite Revuz-Yor §IV.2 or Protter §II.4.
- C3 jump-process routing: Add a Q5e branch to the scope predicate: 'Does the SDE include jump terms driven by Poisson random measures, Lévy processes, compound Poisson processes, or other pure-jump semimartingales? If yes → UNCLASSIFIED with note that extended postconditions for compensated Poisson integrals (E[∫₀ᵀ∫ H²(s,z) ν(dz) ds] < ∞) are required.' Cite Applebaum, Lévy Processes and Stochastic Calculus, 2nd ed., §4.3.
- C4 numerical SVD fallback: Specify a numerical singular-value sampling procedure as a mandatory fallback when symbolic det(J)=0 solve times out or returns UNDETERMINED. Declare sampling budget (e.g., N ≥ 10000 points drawn from the declared domain), threshold (e.g., σ_min < 1e-8 flags near-singularity), and reporting semantics (flagged regions trigger architect review, not automatic rejection).
- C2 semantic relabeling: Relabel the LV conserved quantity as a 'first integral' or 'conserved quantity' rather than 'Lyapunov function', since dV/dt = 0 establishes orbit confinement (conservation), not asymptotic stability. The eigenvalue analysis confirming a center (purely imaginary eigenvalues) is consistent with this — note explicitly that this is a stability-neutral certificate, not an asymptotic stability proof.
- C1 multi-dimensional extension: For SDEs driven by d-dimensional Wiener processes, state that the square-integrability postcondition generalizes to the Hilbert-Schmidt norm: E[∫₀ᵀ ‖σ(s)‖²_HS ds] < ∞, where σ is the diffusion matrix. This is required for the multi-dimensional Itô isometry to apply (Øksendal §4.2).

## Phase B — Informed votes

### claude-opus-4-6

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** v6 is technically excellent across all five corrections; unanimous peer convergence on three remaining gaps (progressive measurability, jump-process scoping, numerical singularity fallback) is well-founded and should be addressed before build.

**Response to peers:**

All four Phase A reports converge on the same three issues, which strongly validates each concern independently. (1) Progressive measurability (claude-opus-4-6, openai-gpt-5, grok-4): I agree fully. The submission's adaptedness check via 'future W symbol absence' is a syntactic heuristic that is neither necessary nor sufficient for the measure-theoretic property required. For continuous diffusion coefficients, adapted ⇒ progressively measurable (Revuz-Yor IV.2), so the simplest correct fix is claude-opus-4-6's option (b): add an explicit scope gate restricting STOCHASTIC_COUPLING to continuous diffusion coefficients and note progressive measurability is implied, with a citation to Protter §II.4 for the general case. openai-gpt-5's stronger proposal of typed-construction enforcement is mathematically superior but introduces a type system whose soundness would itself need verification; I'd accept either approach provided the scope restriction is stated. (2) Jump-process / Lévy scoping (all four reviewers): Complete agreement. Lévy-driven SDEs are semimartingales and currently pass Q5d, but the postconditions (adaptedness + L²-integrability of continuous diffusion integrands) say nothing about the compensated Poisson integral. A Q5e branch routing jump semimartingales to UNCLASSIFIED (citing Applebaum §4.3) is the minimal correct fix. gemini-2.5-pro's framing as 'check if the driving noise is continuous' is the cleanest gate. (3) Numerical singularity fallback (claude-opus-4-6, openai-gpt-5): I agree that sp.solve(det(J)) will timeout on systems of realistic size, rendering the check vacuous precisely where it matters most. A Monte Carlo SVD sampler with declared budget, threshold, and reproducible seed is a sound supplementary mechanism. I side with claude-opus-4-6 that this should be specified as a concrete fallback in the schema rather than grok-4's framing as an optional enhancement — the whole point of C4 is catching what architects miss, and a check that is vacuo

### openai-gpt-5

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** Approve after adding progressive measurability (or continuous-coefficient restriction), explicit jump-noise routing, HS-norm integrability for d-Wiener, a numeric SVD singularity audit, and relabeling the LV certificate as a first integral.

**Response to peers:**

claude-opus-4-6: Agree on the progressive measurability gap; adaptedness+L2 is not sufficient in general. I recommend adding a third verifiable postcondition requiring progressive (or predictable) measurability; for continuous diffusion coefficients, document that adaptedness implies progressive measurability and allow auto-discharge in that case (cite Protter/Revuz–Yor). On jumps: while Q5a already confines to standard Brownian motion, I concur that an explicit Q5e branch for Lévy/PRM jump terms is needed to prevent misinterpretation and to record the correct reason for UNCLASSIFIED (cite Applebaum). On singularities: agree that a numeric SVD fallback should supplement the symbolic det(J) screen; specify a reproducible sampler, σ_min threshold, and rectangular-J rank checks, and define reconciliation rules with the symbolic result. openai-gpt-5: Strong agreement that the ‘no future W’ syntactic heuristic is insufficient. Require a typed construction rule guaranteeing predictability/progressive measurability (integrands built from adapted processes via predictable operations), and record the proof obligation. Also agree to generalize the integrability/isometry checks to d-dimensional Brownian drivers via the Hilbert–Schmidt norm (E∫ trace(H H^T) dt < ∞) and to state the isometry accordingly. Explicit jump handling: add a dedicated Q5e UNCLASSIFIED branch (or a separate STOCHASTIC_JUMP_COUPLING class in a later revision); for v6, the UNCLASSIFIED branch with citations is the minimal sound fix. Singularity screening: add numeric SVD audit and rectangular-rank handling as above. Relabel the LV ‘lyapunov_function’ certificate to ‘first_integral’ (constant of motion) to avoid terminological drift while keeping the center-stability interpretation. Typed tensor indices: the current controlled vocabulary is adequate for rank/variance consistency; adding space/metric tags per index would be a valuable follow-on but is not strictly required to keep claims sound in v6. gemini-

### gemini-2.5-pro

**Verdict:** `modify`  
**Position change:** strengthened  
**Headline:** v6 is a major step towards rigor, but peer review correctly identifies critical gaps in stochastic scope and numerical stability that must be closed before build.

**Response to peers:**

My initial assessment in Phase A was positive but identified similar ambiguities in the stochastic and numerical domains. The Phase A reports from my peers have crystallized these concerns with remarkable consensus and technical precision, strengthening my conviction that these final modifications are not optional enhancements but are essential for the framework's claimed rigor. I concur with the required modifications proposed by the board and will elaborate from my perspective.

1.  **On Stochastic Scope (Jump Processes):** All four reviewers correctly identified that the Q5 decision tree fails to handle jump-diffusions (Lévy processes, Poisson random measures). As a physicist who models systems with intermittent interactions or shot noise, this is a critical omission, not a niche case. These processes are semimartingales and would be misclassified by the current v6 logic. The consensus recommendation to add a specific Q5 branch to route jump-driven SDEs to UNCLASSIFIED is the correct and necessary fix to maintain the framework's honesty. I endorse Reviewer `claude-opus-4-6`'s proposed wording for the new Q5e branch and citation of Applebaum.

2.  **On Stochastic Correctness (Progressive Measurability):** I agree strongly with Reviewers `claude-opus-4-6`, `openai-gpt-5`, and `grok-4`. For a framework that prides itself on precision, stating 'adaptedness' when 'progressive measurability' is the formally sufficient condition (especially for non-continuous integrands) is a technical error. The simplest resolution is to add a scope constraint, restricting STOCHASTIC_COUPLING to SDEs with continuous integrands, and noting that progressive measurability is then implied by adaptedness. This is a clean, honest fix that avoids adding complex verification logic for the general case at this stage.

3.  **On Singularity Detection (Numerical Fallback):** I fully support the consensus view of `claude-opus-4-6` and `openai-gpt-5` that the symbolic `sp.solve(det(J))` is a necessa

### grok-4

**Verdict:** `modify`  
**Position change:** strengthened  
**Headline:** v6 delivers rigorous fixes to v5's issues but requires final refinements on measurability, jump processes, and numerical checks to ensure comprehensive scope and verifiability.

**Response to peers:**

To claude-opus-4-6: I agree fully with adding progressive measurability handling and a Q5e branch for Lévy/jump SDEs, as these align with my initial concerns and strengthen the scope; I also concur on the numerical singular-value fallback as a necessary supplement, not just optional as I suggested, since peers emphasize its role in catching practical degeneracies without overclaiming automation. To openai-gpt-5: I support strengthening adaptedness to predictable/progressive measurability via typed construction, as it pushes beyond heuristics for better falsifiability; I agree on generalizing to multidimensional Brownian via Hilbert-Schmidt norms for soundness in vector SDEs; the jump branch extension is spot-on; the numeric audit augmentation is persuasive for handling brittleness; however, I push back on relabeling the Lotka-Volterra certificate from 'lyapunov_function'—while dV/dt=0 indicates a first integral, it functions as a Lyapunov function for proving neutral stability (level sets confine orbits), and the terminology is standard in dynamical systems (e.g., per Murray), so no change is needed unless evidence shows misuse. To gemini-2.5-pro: I agree on augmenting Q5 for jump components to UNCLASSIFIED, reinforcing honest scoping; on numerical ill-conditioning, I now see the need for a required (not optional) sampler to address near-singularities, as this enhances technical feasibility without violating automation boundaries. Overall, peers' convergent concerns on jumps and numerics have strengthened my modify position, while I maintain pushback on non-essential relabeling to avoid overcorrecting sound claims.

## Phase A — Independent drafts

### claude-opus-4-6

**COI:** ⚠ Familiar with Øksendal, Murray, Carmona-Delarue, Friz-Hairer, and the other cited textbooks from training data. No relationship with the submission authors or the EWE project itself.  
**Verdict:** `modify`  
**Headline:** v6 is a rigorous and honest correction of all five v5 concerns, but three identifiable technical gaps remain that should be closed before build begins.

**Strengths:**
- C1 resolution is exactly right: adaptedness and square-integrability are the actual preconditions that an architect can get wrong, and relegating the Itô isometry to a derived consequence with `derived_not_verified: true` is both mathematically correct and epistemologically honest — this is the cleanest fix possible.
- C2 Lotka-Volterra Lyapunov function is now correct (V = c·x − d·ln x + b·y − a·ln y), the sympy verification script is reproducible, and the eigenvalue analysis at the coexistence fixed point (±i√(ad)) is textbook-accurate. The upgrade path from NONHYPERBOLIC_INCONCLUSIVE to VERIFIED via the Lyapunov certificate is well-structured.
- C3 scope predicate is admirably precise: four explicit exclusion branches (non-adapted/non-square-integrable, McKean-Vlasov, SPDE/Dean-Kawasaki, rough-path/fBm) with correct citations and clean routing to UNCLASSIFIED. This is honest scope-bounding done properly.
- C4 automated singularity pre-screen with graceful degradation (symbolic timeout → UNDETERMINED with provenance note, disagreement → ingest failure) correctly treats the CAS as a safety net rather than an oracle, preserving the architect-responsibility model.
- C5 controlled vocabulary for index positions is pragmatic and machine-parseable without overclaiming tensor-algebraic verification. The contraction-pair specification allows rank-balance checking, which catches the most common class of index errors.
- Rule A9 (sympy-verified worked examples) is the correct meta-level response to the v5 error class. Recording the verification script as a sibling artifact in provenance is a strong auditability choice.
- The self-awareness about why v5's errors escaped review, and the structural response (process rule, not just content fix), demonstrates mature engineering epistemology.

**Concerns:**
- C1 gap — progressive measurability: The submission's own Q1 asks about this but does not resolve it. For non-continuous integrands (e.g., piecewise-constant control processes, jump-adapted integrands), adapted + square-integrable is insufficient; progressive measurability (joint measurability in (t,ω) w.r.t. the progressive σ-algebra) is the correct condition for the general Itô integral (see Revuz-Yor, Continuous Martingales and Brownian Motion, §IV.2, or Protter, Stochastic Integration and Differential Equations, §II.4). For continuous integrands, adaptedness implies progressive measurability, so the current spec is correct for continuous diffusion coefficients — but the spec does not state this restriction. Either (a) add progressive measurability as a third postcondition, or (b) add an explicit scope restriction to continuous integrands and note that the progressive measurability condition is auto-satisfied in that case.
- C3 gap — Lévy-driven SDEs / jump processes: The submission's own Q3 identifies this. Lévy processes with jumps (compound Poisson, α-stable, tempered stable) and Poisson random measures are standard semimartingales, so they pass Q5d and would be classified as STOCHASTIC_COUPLING. However, the postconditions in C1 (adaptedness + square-integrability of diffusion integrands) are specific to the continuous-martingale part; they say nothing about the compensated Poisson integral ∫∫ H(s,z) Ñ(ds,dz), which requires its own integrability condition (E[∫₀ᵀ∫ H²(s,z) ν(dz) ds] < ∞ for the compensated measure). Either add a Q5e branch excluding Lévy/jump-driven SDEs to UNCLASSIFIED, or extend the postconditions to cover the jump integral. The former is cleaner for the MVP scope.
- C4 limitation — sp.solve(det(J)) is a necessary but weak pre-screen for structured Dirac matrices. For large symbolic J (say rank ≥ 6), sympy's solve will timeout on most nontrivial entries, making the check effectively vacuous in the regime where it matters most. The submission's own Q4 asks whether a numerical singular-value sampler should supplement this. The answer is yes: a Monte Carlo sampler drawing N points in the declared domain and computing min(svd(J(x))) catches approximate degeneracies and near-singular regions that symbolic methods miss. This should be specified as a fallback when symbolic solve times out, not as a replacement. The sampling budget and threshold should be declared in the schema (e.g., N=10000, threshold=1e-8, flagging regions where σ_min < threshold).

**Required modifications:**
- Add progressive measurability handling to C1: either (a) add `diffusion_integrand_progressively_measurable` as a third postcondition with verification algorithm (for continuous coefficients: auto-derived from adaptedness; for discontinuous: requires explicit attestation with citation), or (b) add an explicit scope gate restricting STOCHASTIC_COUPLING to continuous diffusion coefficients and note that progressive measurability is implied.
- Add a Q5e branch to C3 for Lévy / jump-driven SDEs: 'Q5e: Does the SDE include jump terms driven by Poisson random measures, Lévy processes, or other pure-jump semimartingales? Yes → UNCLASSIFIED with note "jump-diffusion SDE — requires extended postconditions for compensated Poisson integrals". No → STOCHASTIC_COUPLING.' Cite Applebaum, Lévy Processes and Stochastic Calculus, 2nd ed., §4.3 for the integrability conditions on compensated Poisson integrals.
- Add a numerical singular-value fallback to C4's automated_sanity_check: when symbolic solve times out (or always, as a second independent check), sample N points uniformly in the declared domain, compute σ_min(J(x)) at each, and flag any point where σ_min < threshold. Specify N, threshold, and sampling strategy in the schema. This closes the 'timeout makes the check vacuous for large systems' gap.

### openai-gpt-5

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** Solid v6 that closes the Itô vacuity and fixes Lotka–Volterra; require stronger adaptedness formalism, explicit jump-noise handling, a numeric singularity audit, and typed tensor indices.

**Strengths:**
- Replaces Itô isometry as a postcondition with the actually verifiable prerequisites (adaptedness and square-integrability), restoring non-vacuous checking aligned with Øksendal.
- Lotka–Volterra conserved quantity is now correct and CAS-verified; adding Rule A9 (sympy-verified examples) is an excellent rigor upgrade.
- Scope predicate for STOCHASTIC_COUPLING clearly excludes McKean–Vlasov, SPDE/Dean–Kawasaki, and rough-path cases with citations.
- Automated det(J) prescreen introduces a concrete, reproducible safety net before ingest.
- Index-position controlled vocabulary is a pragmatic step toward cross-entry comparability.

**Concerns:**
- The proposed adaptedness check is underspecified and too weak: absence of explicit future W symbols is neither necessary nor sufficient; predictable/progressive measurability (or type-driven construction) should be required.
- Square-integrability/isometry are stated in scalar form; multidimensional Brownian drivers require Hilbert–Schmidt norm (trace(H H^T)) checks.
- Jump-noise (Lévy/Poisson random measures) is not explicitly routed; current Q5 would silently lump all non-Brownian semimartingales into UNCLASSIFIED without a precise note.
- sp.solve(det(J)) is brittle (missed components, transcendental factors); no numerical rank check exists, and rectangular J/rank-deficiency beyond det=0 is unaddressed.
- Labeling a first integral (dV/dt = 0) as a Lyapunov function is terminologically misleading even if the stability conclusion (center) is correct.
- Tensor index schema lacks index-space typing and explicit raising/lowering maps; “mixed_*” is ambiguous and impedes automated compatibility checks.

**Required modifications:**
- Strengthen the adaptedness postcondition: require predictable or progressive measurability w.r.t. the stated filtration, and enforce it via a typed construction rule (integrands built from adapted processes through predictable operations). Replace the ‘future W symbol’ heuristic with a check that H(t, state_t, ...) is constructed within the adapted fragment; record the proof obligation in the entry.
- Generalize the isometry and integrability checks to d-dimensional Brownian motion: verify square-integrability via the Hilbert–Schmidt norm (E∫ trace(H H^T) dt < ∞) and state the isometry consequence accordingly. Update validators to operate on matrix-valued H.
- Extend Q5 with an explicit branch for jump semimartingales (Lévy processes/Poisson random measures): either (a) route to UNCLASSIFIED with the explicit note “jump semimartingale — Lévy/PRM” and citations (Applebaum; Protter), or (b) define a new STOCHASTIC_JUMP_COUPLING class with predictable/integrability postconditions for both Brownian and jump parts.
- Augment the singularity screening with a numeric audit: (i) perform randomized domain-restricted sampling and SVD-based smallest singular value checks (with reproducible seeds) to detect near-rank drops; (ii) support rectangular J by rank/minor criteria; (iii) reconcile symbolic vs numeric findings with explicit escalation rules.
- Relabel the Lotka–Volterra certificate from ‘lyapunov_function’ to ‘first_integral’ (or ‘constant_of_motion’) and keep the stability interpretation (center). Optionally cite classical first-integral treatments alongside Murray.
- Upgrade the tensor index schema with index-space typing and raising/lowering data: for each tensor, declare the index space label(s), dimension(s), and the bilinear form/metric (with signature) used for raising/lowering; prohibit use of ‘mixed_*’ unless accompanied by an explicit raise/lower map, and make the contraction validator check slot-compatibility by space label.
- Provide minimal test fixtures that both accept and reject cases for: (i) adapted vs anticipating integrands; (ii) multidimensional diffusion isometry; (iii) jump-noise routing; (iv) singularity discovery (symbolic hit/miss, numeric catch); and (v) tensor contractions across mismatched index spaces.

### gemini-2.5-pro

**COI:** ⚠ The concepts discussed—port-Hamiltonian systems, bond graphs, stochastic differential equations, Lyapunov stability, tensor formalisms—are foundational to my field of expertise. I have no conflict of interest with respect to the specific EWE/ECP/EOE/EMP project itself.  
**Verdict:** `modify`  
**Headline:** The framework's rigor is substantially improved by replacing vacuous checks with verifiable preconditions and adding automated symbolic sanity checks, but the stochastic scoping needs one final refinement.

**Strengths:**
- Excellent response to previous review feedback, demonstrating deep technical understanding. Each of the five concerns is addressed with a robust and well-reasoned solution.
- The introduction of mandatory symbolic verification for all worked examples (Rule A9) is a superb process improvement that will prevent entire classes of errors and increase the trustworthiness of the framework's content.
- The explicit and well-cited scoping of the STOCHASTIC_COUPLING class is a model of intellectual honesty, clearly delineating the boundary between what the framework can and cannot rigorously handle.

**Concerns:**
- The STOCHASTIC_COUPLING scope predicate (C3), while vastly improved, still omits SDEs driven by processes with jumps (e.g., Lévy processes or Poisson random measures), which represent a significant class of models in fields like mathematical finance and physics.
- The automated singularity check (C4) focuses on exact symbolic degeneracy (`det(J)=0`). It does not address numerical ill-conditioning (near-singularity), which can be equally problematic in practice. While acceptable for an MVP, this limitation should be tracked for future development.

**Required modifications:**
- Augment the STOCHASTIC_COUPLING scope predicate decision tree (Q5). Add a question to explicitly check if the driving noise is a continuous process. If the noise includes jump components (e.g., is a Lévy process or involves a Poisson random measure), the system must be routed to UNCLASSIFIED with an appropriate note, consistent with the handling of other out-of-scope advanced stochastic frameworks.

### grok-4

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** v6 rigorously addresses the five v5 concerns with verifiable fixes, but requires minor enhancements to scope predicates and citations for completeness.

**Strengths:**
- Precise replacement of Itô isometry with checkable adaptedness and square-integrability conditions, correctly framing the theorem as a derived consequence.
- Symbolic verification of Lotka-Volterra Lyapunov function eliminates factual errors and enforces rigor via anti-drift rule.
- Scope predicate for STOCHASTIC_COUPLING honestly excludes out-of-scope cases with clear citations, enhancing framework honesty.
- Automated singularity pre-screen and controlled tensor index vocabulary add buildable, verifiable mechanisms without overclaiming automation.

**Concerns:**
- Itô conditions may need to explicitly include progressive or predictable measurability for non-continuous integrands, as adaptedness alone is insufficient in some rigorous settings.
- Scope predicate covers key exclusions but omits explicit handling of jump processes (e.g., Lévy or Poisson), which are semimartingales but require distinct verification for integrability and stability.
- Citations are solid but should include primary sources for foundational models like Lotka-Volterra to fully demonstrate prior art awareness.

**Required modifications:**
- Add progressive measurability check to STOCHASTIC_COUPLING verifiable postconditions, citing e.g., Protter's Stochastic Integration §II.3 for when it differs from adaptedness.
- Extend Q5 scope predicate to explicitly flag jump-diffusion SDEs (e.g., with Poisson measures) as a separate UNCLASSIFIED branch, requiring specialized postconditions like jump-adaptedness.
- Supplement Lotka-Volterra citation with primaries: Lotka (1925) Elements of Physical Biology and Volterra (1926) Variazioni e fluttuazioni del numero d'individui in specie animali conviventi.
- Consider optional numerical supplement to singularity check (e.g., sampling smallest singular values), but frame it as an enhancement, not a requirement, to avoid over-automation claims.

