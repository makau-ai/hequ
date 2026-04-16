# Round 2 Discharge Review — Design v4

**Query:** `design_phase_12_20_discharge_round2`  
**Round:** 2  
**FCS size:** 6  
**Editor verdict:** `approve`

## Editor synthesis (binding)

**Verdict:** `approve`

**Rationale:**

All four reviewers unanimously report all six FCS concerns (C1–C6) as fully addressed. The two high-severity items are resolved: C1's brittle multiplicative confidence is replaced by a sound log-evidence accumulator with bounded per-level contributions, neutral handling of missing levels, honest independence-assumption disclosure, and an empirical recalibration commitment; C2's factually incorrect cross-CAS claim is retracted, mpmath is honestly relabeled, and a genuinely independent backend (python-flint/Arb) is introduced with correct technical justification. The four medium-severity items are likewise resolved: C3 replaces the incomplete sp.simplify==0 with a multi-stage canonicalization pipeline and an honest UNDECIDABLE fallback; C4 introduces a formal dimensional type system with load-time enforcement; C5 upgrades to Hypothesis-based property testing with stratification, boundary injection, power analysis, and reproducible seeding; C6 formalizes transducers as port-Hamiltonian subsystems with symbolic conservation-by-construction at composition time. One process violation occurred (claude-opus-4-6 attempted to raise 2 new concerns), but this is correctly blocked by the scope-frozen discharge protocol and does not affect the disposition of the six frozen concerns. No regressions were introduced. The submission is approved for Phase 12 execution.

**Unresolved concerns:** []

**⚠ Process violations:**
- claude-opus-4-6 attempted to raise 2 new concern(s) — out-of-scope in discharge mode

## Per-reviewer discharge reports

### claude-opus-4-6

**Overall verdict:** `approve`  
**Headline:** All six frozen concerns are substantively addressed with technically sound, honestly-scoped mechanisms; the design is approved for Phase 12 execution.

**⚠ PROCESS VIOLATION:** attempted to raise 2 new concern(s)

- ✅ **C1** — `addressed`  
  The multiplicative composite C = c1·c2·c3·c4 is fully replaced by a log-evidence accumulator (§8a.1–8a.4). Each level contributes a bounded log-evidence value ℓ_i ∈ [−4.6, +3.0] with absent levels contributing 0 (neutral), eliminating the single-zero-collapse brittleness. The independence assumption is honestly declared as an assumption rather than a claim, with a concrete dependency-audit protocol (remove-one-level test) specified for Phase 12 adversarial testing. Promotion thresholds are recalibrated to the log scale with an explicit empirical recalibration commitment against the adversarial pre-reg set. The full Bayes-factor framework is honestly deferred as technical debt rather than silently omitted. The non-brittleness guarantee is demonstrated concretely: strong L1+L2+L3 with no L4 yields log_C=9.0, sufficient for PROVED. This is a sound and honest remedy.
- ✅ **C2** — `addressed`  
  The false 'cross-CAS' claim is explicitly dropped. §5.2.3 now honestly labels mpmath as 'within-sympy fragility check, NOT cross-CAS.' §5.2.4 specifies python-flint (Arb-based interval arithmetic) as the genuinely independent numeric backend, with correct technical justification: Arb shares no code paths with sympy/mpmath. The dependency is soft in Phase 12 (graceful skip with warning) but hard in Phase 13+, which is a reasonable rollout. Mathematica/Maple integration is tracked as Phase 15+ technical debt. The four-check pipeline (A: symbolic canonicalization, B: property-based sampling, C: mpmath high-precision, D: python-flint interval) is well-structured with honest independence labeling throughout. The factual error from v3 is corrected and the replacement is technically sound.
- ✅ **C3** — `addressed`  
  §5.2.1 replaces sp.simplify(expr)==0 with a multi-stage canonicalization pipeline: (1) dimensional compatibility gate, (2) rational function normalization via cancel+together+expand, (3) trig/power simplification cascade, (4) polynomial remainder check, (5) branch-cut-aware discriminating random evaluation at N=20 samples avoiding declared singularities. Known failure modes (piecewise, abs, multi-valued inverses, complex branch cuts) are explicitly documented and produce SYMBOLIC_EQUIVALENCE_UNDECIDABLE rather than silent misclassification, which escalates to the user Decision Matrix. This is the correct engineering response: a cascading pipeline of increasingly powerful checks with honest failure-mode documentation and a safe fallback for undecidable cases. The discriminating random evaluation as a final catch-all is sound practice for symbolic equivalence checking.
- ✅ **C4** — `addressed`  
  §11f specifies a formal dimensional type system: base dimensions as rational-exponent 7-tuples (L,M,T,I,Θ,N,J) derived from UCUM/QUDT, with explicit inference rules (add/sub requires unification, mul/div adds exponents, transcendentals require dimensionless arguments). Enforcement is at load time, not runtime — inference failure is a hard stop that rejects the composite as DIMENSIONALLY_INCONSISTENT_COMPOSITE before execution. The transducer composition example (F = K_t · I) demonstrates the inference chain concretely. Every canonical problem's problems.yaml declares dimensional signatures explicitly, and §5.2 reference verification includes a dimensional check as the first gate. Provenance tags (declared/inferred/asserted) provide auditability. This is a well-specified dimensional type system with load-time enforcement, directly addressing the concern.
- ✅ **C5** — `addressed`  
  §5.2.2 adopts the Hypothesis library with a concrete sample_strategy_for(equation) generator that: (1) stratifies draws across orders of magnitude with equal probability per band, (2) includes explicit boundary cases (min, max, zero, unity, near-singularity), (3) avoids declared singularities and branch cuts, (4) seeds reproducibly with ledger-logged seeds for audit replay, (5) computes N via power analysis (N ≥ 1/(α·δ²) for declared α=1e-4, δ=1%), yielding typical N≈10000 declared per-problem in problems.yaml rather than a magic constant. The dimensional consistency enforcement during sampling is handled by the §11f type system. This is a thorough replacement of the ad-hoc N=50 approach with justified, structured, reproducible sampling.
- ✅ **C6** — `addressed`  
  §11g formalizes transducers as port-Hamiltonian subsystems with explicit ports (effort/flow pairs per domain), energy state variables, Dirac structure equations as the core algebraic constraint, a power_conservation equation verified symbolically at composition time via sympy, constitutive type classification, and sign convention. The TRANSDUCER-MOTOR example demonstrates the full schema concretely. Composition now fails at load time as NON_PASSIVE_COMPOSITE if the Dirac structure + power conservation don't close symbolically — this is conservation-by-construction, not post-hoc numeric checking. The prior Tellegen/Onsager checks are retained as belt-and-braces runtime verification but are no longer the primary gate. Conjectural transducers must also specify these fields. This directly addresses the concern: composition now preserves conservation by construction via symbolic verification of the port-Hamiltonian structure.

### openai-gpt-5

**Overall verdict:** `approve`  
**Headline:** All six frozen concerns are substantively remedied with sound, verifiable mechanisms aligned with the requested fixes.

- ✅ **C1** — `addressed`  
  Multiplicative confidence was replaced by bounded per‑level log‑evidence with explicit floors and neutral handling of missing levels; independence is no longer assumed (a dependency‑audit is specified), and thresholds are recalibrated on the log scale with an empirical validation plan. This matches the requested move to log/Bayes‑style accumulation with floors.
- ✅ **C2** — `addressed`  
  The false cross‑CAS claim was removed; mpmath is correctly labeled non‑independent, and a genuinely independent backend (python‑flint/Arb interval arithmetic) is added as Check D, with clear integration details and a commitment to make it mandatory next phase. This satisfies the requirement to add an independent engine and relabel claims honestly.
- ✅ **C3** — `addressed`  
  The symbolic check now uses an explicit canonicalization pipeline (rational normalization, trig/power simplification, polynomial remainder when applicable) plus discriminating random evaluation avoiding singularities/branch cuts; known hard cases (piecewise, abs, multivalued inverses, branch cuts) yield an undecidable flag. This directly remedies simplify==0 incompleteness.
- ✅ **C4** — `addressed`  
  An L0 dimensional type system over QUDT/UCUM is defined with 7‑tuple base dimensions, inference and unification rules, and load‑time enforcement; compositions/transducers are checked dimensionally and inconsistencies are rejected before execution. Canonical problems and reference checks include dimensional validation.
- ✅ **C5** — `addressed`  
  Property‑based testing is upgraded to Hypothesis with a strategy that enforces dimensional consistency, stratifies across orders of magnitude, injects boundary cases, avoids branch cuts/singularities, seeds reproducibly, and sets N via stated power analysis. This resolves the prior unstructured N=50 sampling.
- ✅ **C6** — `addressed`  
  Transducers are formalized as port‑Hamiltonian subsystems with explicit ports, Dirac structure, and a power‑conservation equation symbolically verified at composition time; non‑passive composites fail at load time. Post‑hoc numeric checks are retained as secondary safeguards. This meets the by‑construction conservation requirement.

### gemini-2.5-pro

**Overall verdict:** `approve`  
**Headline:** The v4 revision systematically and robustly addresses all frozen concerns, replacing prior weaknesses with state-of-the-art, physically-grounded methodologies.

- ✅ **C1** — `addressed`  
  The brittle multiplicative confidence rule has been replaced with a robust log-evidence accumulator. This standard methodology correctly handles missing evidence as neutral and prevents a single poor score from collapsing the entire assessment, directly resolving the brittleness concern.
- ✅ **C2** — `addressed`  
  The revision corrects the factually inaccurate 'cross-CAS' claim by honestly relabeling the mpmath check and, crucially, adding a genuinely independent numeric backend using python-flint (Arb). This provides the requested orthogonal verification path.
- ✅ **C3** — `addressed`  
  The known-incomplete `sp.simplify == 0` check has been replaced by a rigorous, multi-stage canonicalization pipeline. This new process correctly handles a wider class of expressions and, importantly, explicitly identifies and flags undecidable cases rather than failing silently.
- ✅ **C4** — `addressed`  
  The under-specified unit system has been replaced with a formal dimensional type system. The addition of load-time inference and unification enforces dimensional consistency by construction, preventing inconsistent models from being composed, which fully addresses the concern.
- ✅ **C5** — `addressed`  
  The naive 'N=50 random vectors' approach has been replaced with a state-of-the-art property-based testing strategy using the Hypothesis library. The new methodology includes stratification, boundary testing, power analysis, and dimensional awareness, fully addressing all points of the original concern.
- ✅ **C6** — `addressed`  
  The transducer formalism has been correctly upgraded to a port-Hamiltonian framework. This is a profound architectural improvement that enforces conservation laws symbolically at composition time, by construction, rather than relying on post-hoc numeric checks. The revision is a textbook-correct implementation of the requested formalism.

### grok-4

**Overall verdict:** `approve`  
**Headline:** The v4 revision comprehensively addresses all concerns in the Frozen Concern Set through targeted technical upgrades that enhance soundness, rigor, and verifiability without introducing brittleness or unsubstantiated claims.

- ✅ **C1** — `addressed`  
  The revision replaces the multiplicative rule with a log-evidence accumulator incorporating per-level floors and bounds, recalibrates thresholds with a commitment to empirical validation against pre-registered sets, and introduces a dependency-audit protocol instead of assuming independence, directly implementing the recommended log-based approach for non-brittleness.
- ✅ **C2** — `addressed`  
  The false 'cross-CAS' claim is dropped, and the pipeline now includes python-flint as a genuinely independent numeric backend alongside honest labeling of mpmath as non-independent, with phased implementation matching the remedy of adding an orthogonal engine like Arb-based tools.
- ✅ **C3** — `addressed`  
  The simplistic sp.simplify check is replaced by a comprehensive canonicalization pipeline including rational normalization, trig/power simplification, polynomial remainder checks, and discriminating random evaluation avoiding branch cuts, with documented failure modes triggering UNDECIDABLE, aligning with the required heuristic improvements.
- ✅ **C4** — `addressed`  
  A formal dimensional type system is added with rational-exponent tuples, unit tracking, inference on operations, unification checks, and load-time enforcement of consistency in compositions and problems.yaml, fully specifying and enforcing the under-specified aspects via QUDT integration.
- ✅ **C5** — `addressed`  
  Hypothesis library is adopted with stratified sampling across magnitudes, explicit boundary cases, singularity avoidance, reproducible seeding, and N determined by power analysis (typically ~10000), directly remedying the lack of structure in the original N=50 random vectors.
- ✅ **C6** — `addressed`  
  Transducers are formalized as port-Hamiltonian subsystems with explicit ports, energy variables, Dirac structure, and symbolic power-conservation verification at composition time, shifting from post-hoc checks to by-construction enforcement as required.

