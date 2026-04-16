# EWE Concept Review — 4-Phase Academic Protocol

**Query:** `ewe_concept_review_v1`  
**Include Grok:** True  
**Editor verdict:** `escalate`

**All responded (Phase A):** False  
**All responded (Phase B):** True

## Phase C — Editor synthesis (binding)

**Verdict:** `escalate`

**Rationale:**

Non-response from 1 reviewer(s): claude-opus-4-6. Per v4 'all must respond' rule, non-response counts as dissent. The gate is NOT met. Escalating to user.

---

Original editor synthesis (still recorded):

All four reviewers agree that the core intellectual contribution—applying MITRE-style structured decomposition to equation failure modes—is novel, well-motivated, and architecturally sound. The EWE/ECP/EOE/EMP four-layer analogy is coherent, the worked example (EWE-001) demonstrates real explanatory value, and the proposal is in principle buildable and verifiable. There is no fundamental technical flaw. However, three of four reviewers (openai-gpt-5, gemini-2.5-pro, grok-4) independently converge on two substantive technical gaps that are not merely about effort but about whether the proposed system can deliver on its central claim—that structured relationships reduce hallucination risk and outperform free-text RAG. First, the schema remains largely prose-level; without machine-checkable fields (canonical equation ASTs, typed variable/unit bindings, domain-of-validity expressed as inequalities over dimensionless groups, and formalized assumption types), the structured corpus cannot be distinguished from well-organized free text by a retrieval system, undermining the entire value proposition. Second, the claim of RAG superiority over unstructured baselines is currently unfalsifiable: no evaluation protocol, benchmark, or success metric is specified. Claude-opus-4-6's argument that these gaps are addressable within a later phase (Phase 14) is reasonable in a project-management sense, but the editor's concern is architectural soundness of the *design document itself*: a concept review that asserts superiority over free-text RAG must at minimum specify what would constitute evidence for or against that claim, and must define the formal semantics that make the structure computationally meaningful rather than decorative. These are not scope-reduction requests; they are requests for the design to be complete on its own terms. The modifications below are technically necessary for the framework to be internally consistent and its claims to be testable.

**Required modifications:**
- Add machine-checkable fields to every EWE entry: (a) canonical equation representation (OpenMath, Content MathML, or SymPy AST) with a variable dictionary and QUDT/ISO 80000 unit bindings; (b) domain-of-validity expressed as explicit inequalities over dimensionless groups and state variables; (c) identification of small parameters with error-scaling order; (d) boundary/initial-condition constraints; (e) frame/symmetry invariance declarations.
- Define and adopt a standardized Assumption/Approximation Ontology. Each EWE entry must link to one or more named assumption types (e.g., linearization, dilute limit, local thermodynamic equilibrium, scale separation, Markovianity, continuum limit, weak coupling, equilibrium). This ontology must be enumerated with clear definitions, not left as free text.
- Formalize ECP semantics beyond narrative descriptions: classify composition patterns into at minimum (i) conservation/balance coupling, (ii) constitutive closure, (iii) inter-domain transduction/port connection. Each ECP entry must specify pre/post-conditions (compatibility of conserved quantities, continuity constraints, causality direction) and should reference established formalisms (bond-graph, port-Hamiltonian, or Modelica connector semantics) where applicable. Sharpen the ontological boundary between a single-equation EWE failure and a composition-induced ECP failure with explicit classification criteria.
- Strengthen EOE and EMP provenance: add evidence-level grading (primary experiment, replication, meta-analysis, textbook consensus) and mapping confidence for each EOE→EWE link. EMP entries must include algorithmic specifications for detection tests (not just prose descriptions), preconditions for applicability, and effectiveness estimates with stated uncertainty.
- Pre-register a falsifiable evaluation protocol for the RAG superiority claim: construct a benchmark of diagnostic queries (observed anomalies, regime descriptors, composition failures) with gold-standard EWE/EMP answers; compare structured-graph RAG against a strong free-text embedding baseline on Top-k accuracy, MRR, and calibration; include inter-annotator agreement metrics for EOE↔EWE mappings; report ablations showing the marginal contribution of machine-checkable fields versus prose-only structure.

## Phase B — Informed votes

### claude-opus-4-6

**Verdict:** `approve`  
**Position change:** strengthened  
**Headline:** A genuinely novel and architecturally sound knowledge framework whose core thesis is correct; the falsifiability gap is real but addressable within the proposed Phase 14 scope rather than as a gate to approval.

**Response to peers:**

openai-gpt-5 raises the strongest technical concern: that without machine-checkable fields (ASTs, regime inequalities, nondimensional groups), the structured graph may not meaningfully outperform well-embedded free text. I agree this is the right question, but I disagree that it should block approval. The proposal already includes detection_methods and regime-bound prose; promoting those to typed fields is a schema refinement, not a redesign. The submission explicitly asks whether 'dimensional signature, regime bounds, order-of-magnitude of the small parameter' belong in the schema (Question 3), demonstrating awareness. I would include this as a strong recommendation rather than a required modification gating approval. The call for a pre-registered evaluation protocol (A/B on structured vs. free-text RAG) is valuable and I echo it — but the framework's value extends beyond RAG retrieval: it is an authoring discipline and a knowledge-engineering artifact that forces completeness. Even if the RAG delta turns out to be modest, the structured catalog itself is a contribution. gemini-2.5-pro's full-5 approval aligns with my assessment of the core thesis soundness and novelty. The concern about the EWE/ECP boundary is well-taken but tractable: composition failures are failures of the joint assumption set, and the schema can enforce that every ECP-level failure decomposes into constituent EWE triggers plus a coupling-specific residual. This is a schema design task, not a conceptual flaw. grok-4's suggestion to merge ECP into EWE misreads the decomposition. ECP captures a fundamentally different object: the coupling template itself, not the weakness of an individual equation. Newton II is not wrong; Hooke's law is not wrong; the SHO composition has its own joint assumption envelope (small displacement AND inertial frame AND linear restoring force) that is not the union of the individual EWE entries but a new entity with emergent failure modes. Collapsing this distinction wo

### openai-gpt-5

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** Sound, novel framework; add formal semantics (AST, units, validity) and a falsifiable benchmark to substantiate the RAG advantage.

**Response to peers:**

To claude-opus-4-6: No substantive technical feedback was available due to a JSON parsing failure; nothing to address.

To openai-gpt-5: I agree across the board. The current schemas are too prose-heavy to guarantee the claimed retrieval and diagnostic gains. I would require: (1) Canonical equation representation and typing: include a machine-parseable AST (SymPy/OpenMath/Content MathML), a variable dictionary with QUDT unit bindings, and explicit symbol scopes; enable automated dimensional checks and invariant tests. (2) Validity as constraints: encode domains of validity as inequalities over nondimensional groups (via Buckingham–Pi) and state variables; name small parameters and add error scaling laws (e.g., O(ε^2)) plus boundary/initial-condition constraints and symmetry/frame invariances. (3) Assumption/Approximation Ontology: standardize tags such as linearization, dilute limit, LTE, continuum limit, Markovianity, weak coupling, quasistatic, ergodicity; link each EWE to these. (4) ECP formal semantics: classify at least into conservation/balance, constitutive closure, and inter-domain transduction; add pre/post-conditions (compatibility of conserved quantities, continuity constraints, causality/passivity) and, where applicable, bond-graph/port-Hamiltonian style connectors (effort/flow, transformers, gyrators) with explicit port/variable mappings. (5) Provenance and uncertainty: for EOE→EWE links, add evidence level and mapping confidence/weights; for EMP, specify preconditions, explicit detection algorithms/specs, effectiveness estimates with uncertainty and dataset sizes. (6) Falsifiable evaluation plan: build a benchmark of anomaly-style and regime-descriptor queries with gold EWE/EMP answers; compare structured-graph RAG versus a strong free-text baseline on Top-1/Top-k, MRR, calibration/Brier, and ablations (with/without machine-checkable fields); include inter-annotator agreement for EOE↔EWE.

To gemini-2.5-pro: I concur on the novelty and on the need to s

### gemini-2.5-pro

**Verdict:** `modify`  
**Position change:** moderated  
**Headline:** The framework's core analogy is powerful, but its schemas require machine-checkable semantics and its performance claims must be made falsifiable through a formal evaluation plan.

**Response to peers:**

My initial 'approve' verdict was based on the conceptual strength of the proposal, which remains high. However, I am persuaded by the consensus from my peers (openai-gpt-5, grok-4) that the proposal as-written lacks critical components for rigor and validation. My position is therefore moderated to 'modify' to incorporate their excellent suggestions, with one specific point of disagreement.

I strongly agree with the critique, particularly from reviewer `openai-gpt-5`, that the schemas must be augmented with machine-checkable fields. Adding canonical equation representations (e.g., SymPy/MathML ASTs), domain-of-validity constraints expressed via dimensionless numbers, and links to a formal assumption ontology will elevate this from a well-structured text database to a true computational knowledge graph. This is essential for realizing the claimed RAG benefits.

Furthermore, I fully endorse the consensus that the claim of outperforming free-text RAG is currently an unfalsifiable assertion. A required modification must be the definition of a clear, pre-registered evaluation protocol with benchmarks, as both peers rightly demand.

Where I must push back is on reviewer `grok-4`'s suggestion to consider merging ECP (Composition Patterns) into EWE (Weaknesses). From a multi-physics modeling perspective, this would be a profound error. The distinction between a failure *within* a constitutive law (an EWE, like a non-linear material response) and a failure at the *interface* between two valid laws (an ECP failure, like an energy-inconsistent coupling) is fundamental. Bond-graph and port-Hamiltonian formalisms are built entirely around this distinction, separating component properties from their power-conserving interconnection structure (the 'junction structure'). ECP is the correct layer to formalize these interconnections, their associated assumptions (e.g., perfect transduction, no storage at the port), and their failure modes. Merging ECP into EWE would conflate compone

### grok-4

**Verdict:** `modify`  
**Position change:** strengthened  
**Headline:** Strong conceptual foundation for equation failure modes, but RAG superiority claims remain unfalsifiable without benchmarks and deeper prior art analysis.

**Response to peers:**

openai-gpt-5's concerns on schema formalization, machine-checkable fields, and a pre-registered evaluation protocol align closely with my emphasis on falsifiability and evidence for RAG claims, strengthening my call for benchmarks and provenance; I agree with requiring assumption ontology and ECP semantics but push back on mandating bond-graph links as overkill unless evidence shows necessity for the MVP. gemini-2.5-pro's approval overlooks the lack of empirical tests for the RAG substrate claim, which exceeds evidence—I disagree that falsifiability is already at 5 without specified metrics or benchmarks, though I concur on needing clearer EWE/ECP boundaries; their high prior_art_awareness score is fair but doesn't address my concern for explicit overlap rulings with PDE benchmarks or V&V ontologies.

## Phase A — Independent drafts

### claude-opus-4-6

**Status:** Phase A failed (Failed to parse JSON)

### openai-gpt-5

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** Promising, technically sound MITRE-style ontology for equation failure modes; require schema formalization and a falsifiable evaluation plan.

**Strengths:**
- Accurately identifies the core gap: failure/assumption semantics of equations are trapped in prose and not computable.
- Clear, coherent decomposition (EWE/ECP/EOE/EMP) mapping to CWE/CAPEC/ATT&CK/D3FEND with a concrete, instructive worked example (EWE-001).
- Emphasis on relationships and evidence (EOE↔EWE) and actionable countermeasures (EMP) is appropriate for a RAG substrate aimed at diagnosis and mitigation.
- Good initial engagement with relevant standards/ontologies (QUDT, ISO 80000) and V&V literature; avoids re-inventing units/definitions.
- Concept is in-principle buildable: schemas, graph index, and cross-referencing are straightforward; lends itself to machine reasoning.

**Concerns:**
- Schema is still largely prose; without machine-checkable fields (dimensionless groups, regime bounds, error scaling), the RAG advantage over strong free-text embeddings may be marginal.
- No canonical equation representation (AST/OpenMath/SymPy) or typed variable/units bindings; this impedes consistent linking, dimensional checks, and automated detection methods.
- ECP categories need more formal semantics (e.g., conservation-balance vs constitutive closure vs transduction) to prevent overlap and ensure compositional correctness.
- Evidence and mitigation claims lack grading and uncertainty (EOE→EWE mapping strength; EMP effectiveness with confidence); provenance needs to be explicit.
- Evaluation/falsifiability plan is not specified: no retrieval benchmarks, inter-annotator agreement, or prospective tests demonstrating superiority over unstructured RAG.

**Required modifications:**
- Augment all artifacts with machine-checkable fields: for EWE add (a) canonical equation AST (e.g., OpenMath/Content MathML or SymPy) with variable dictionary and QUDT unit bindings; (b) domain-of-validity expressed as inequalities over nondimensional groups and state variables; (c) small-parameter name(s) with error scaling law/order; (d) boundary/initial-condition constraints; (e) frame/symmetry invariances.
- Introduce an Assumption/Approximation Ontology and link each EWE to one or more standardized assumption types (e.g., linearization, dilute limit, LTE, scale separation, Markovianity, continuum limit, weak coupling, equilibrium).
- Formalize ECP semantics: classify patterns at least into (i) conservation/balance coupling, (ii) constitutive closure, (iii) inter-domain transduction/port connection; require pre/post-conditions (compatibility of conserved quantities, continuity constraints, causality) and optionally link to bond-graph or port-Hamiltonian formalisms/Modelica connectors.
- Strengthen EOE and EMP provenance: add fields for evidence level (e.g., primary experiment, replication, meta-analysis), mapping confidence/weight for each EOE→EWE link, and for EMP include preconditions, explicit algorithm/specification of detection tests, and effectiveness estimates with uncertainty and dataset size.
- Define and pre-register an evaluation protocol to test the RAG substrate claim: construct a benchmark of queries (observed anomalies, regime descriptors) with gold EWE/EMP answers; compare structured-graph RAG vs a strong free-text baseline on Top-1/Top-k accuracy, MRR, calibration, and ablations (with/without machine-checkable fields); include inter-annotator agreement for EOE↔EWE labels.
- Ensure separation of concerns: distinguish physical-law misapplication (EWE) from numerical/discretization failures and from measurement-model/observability issues; add optional links to companion entries for numerical and measurement-model failure modes.
- Integration guidance: make EWE/ECP/EOE/EMP first-class ledger artifacts with stable IDs; embed lightweight cross-references in equation.yaml (e.g., links to relevant EWE IDs and assumption ontology IDs) to enable many-to-many relationships.
- Add minimal computational test assets: for each seeded EWE, include at least one reproducible demonstrator (simulation script or dataset) that exhibits the failure and validates at least one EMP detection/mitigation.
- Extend taxonomy mappings: include PDE/ODE classification, stochastic vs deterministic, linearity, operator type, and known symmetries/conservation laws to support automated compatibility and regime checks.
- Encode dimensional consistency and variable role metadata: explicitly tag state, parameter, control, and observable variables; include measurement-model mappings when relevant (sensor proxies, transfer functions, resolution limits).

### gemini-2.5-pro

**COI:** no COI  
**Verdict:** `approve`  
**Headline:** A robust and novel proposal to structure the 'failure modes' of physical laws, creating a powerful new substrate for AI-driven scientific discovery.

**Strengths:**
- The core analogy to cybersecurity frameworks (CWE/ATT&CK) provides a proven, scalable, and powerful structure for a domain where such formalism is lacking.
- The focus on weaknesses, misapplications, and mitigations is a fundamental shift from existing equation catalogs, capturing the tacit knowledge essential for expert-level modeling.
- The proposal is exceptionally well-researched, showing deep awareness of a wide range of prior art and articulating its unique value proposition with clarity.

**Concerns:**
- The ontological boundary between a fundamental weakness in a single equation (EWE) and a failure arising from incorrect composition of multiple valid equations (ECP) is not yet sharply defined. A failure in coupling could be ambiguously classified.
- The Equation Composition Patterns (ECP) layer, while conceptually sound, requires a more rigorous formalism to capture multi-physics interactions beyond simple substitution. Its power will depend on how well it represents concepts like energy-conserving transformations and signal-flow coupling, akin to the role of transformers/gyrators in bond graphs.

**Required modifications:**
- The next phase must produce a formal specification document defining the precise scope of, and relationships between, the EWE, ECP, EOE, and EMP entities. This document must include clear criteria for classifying a failure as an EWE vs. an ECP-related issue, with illustrative examples.
- The ECP schema definition in the next phase should be elaborated to include more formal semantics for equation coupling, such as explicit port/variable mapping and specification of the physical domain (e.g., thermal, mechanical, electrical) of the coupling variables, to ensure it can capture the subtleties of multi-physics models.

### grok-4

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** Ambitious and novel framework for structuring equation failure modes, but claims of RAG superiority lack empirical support and falsifiable tests.

**Strengths:**
- Core analogy to MITRE frameworks is sound and creatively applied to scientific equations, addressing a real gap in structured knowledge of failure modes.
- Proposed schemas and decompositions are technically buildable, with clear examples demonstrating principled design from first-principles physics.
- Honest about scope, including MVP focus on high-leverage equations and explicit questions for the board on prior art and alternatives.

**Concerns:**
- Claims that the structured graph 'meaningfully outperforms' free-text RAG are asserted without evidence, exceeding what can be supported absent comparative benchmarks.
- Falsifiability is weak: no specific tests or metrics proposed to verify if the framework improves retrieval accuracy, anomaly detection, or discovery outcomes.
- Prior art awareness lists candidates but does not deeply analyze overlaps (e.g., how PDE benchmarks or V&V standards might subsume parts of EWE), leaving potential redundancies unaddressed.

**Required modifications:**
- Incorporate falsifiable tests, such as A/B benchmarks comparing RAG precision/recall on structured vs. free-text corpora for failure-mode queries.
- Conduct and include a deeper prior art review, explicitly ruling in/out overlaps with physics-informed ML benchmarks and model validation ontologies.
- Refine decomposition by evaluating if ECP (composition patterns) is necessary or could be merged into EWE for simplicity, based on equation-specific needs rather than strict MITRE analogy.

