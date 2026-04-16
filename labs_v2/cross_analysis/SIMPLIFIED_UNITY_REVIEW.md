# Simplified Unity-of-Equations Review — 4-Phase Academic Protocol

**Query:** `simplified_unity_review_v1`  
**Include Grok:** True  
**Editor verdict:** `modify`

**All responded (Phase A):** True  
**All responded (Phase B):** True

## Phase C — Editor synthesis (binding)

**Verdict:** `modify`

**Rationale:**

All four reviewers converge on the judgment that the proposal is architecturally sound and that the simplification from four parallel catalogs to two embedded artifacts (failure_modes in equation.yaml, unity_map.py) is technically correct. The disagreement is only about whether the remaining gaps are blocking (three MODIFY votes) or non-blocking refinements (one APPROVE). On close reading, the APPROVE reviewer (claude-opus-4-6 Phase B) acknowledges the same three concrete gaps the others raise but argues they are 'refinements to a correct design.' That framing is reasonable in many contexts, but the specific gaps identified are not cosmetic: (1) the validity_envelope claims machine-checkability while specifying no parser, evaluator, or binding semantics — this is a correctness claim that is currently unfalsifiable; (2) the 2-of-2 validation is presented as 'strong evidence' in the body while the hedged discussion concedes it is statistically underpowered — this is an honesty-of-claims issue, not a polish issue; (3) use_instead as a scalar rather than a list is a schema design error that will require a breaking change later. These are the kind of issues that, if shipped, create technical debt in the schema contract itself — the hardest place to fix later. The MODIFY reviewers' reasoning on these points is technically stronger than the APPROVE reviewer's counterargument that they are deferrable. Gemini-2.5-pro's concern about schema corrections (use_instead as list, referential integrity) and grok-4's concern about the falsifiability protocol both identify issues that affect the verifiability of the proposal's core claims. openai-gpt-5's insistence on a minimal formal spec for the validity-envelope DSL is the most consequential requirement: without it, the central value proposition (machine-checkable validity envelopes) is aspirational rather than demonstrated. The editorial decision is MODIFY with four required changes, all of which are well-scoped schema or specification clarifications rather than structural redesigns.

**Required modifications:**
- Publish a minimal formal specification for the validity_envelope DSL: define the grammar of the inequality strings, the binding protocol between symbolic variables and equation.yaml variable names or runtime values, and either commit to a concrete evaluator (e.g., sympy.parse_expr with a documented symbol table) or downgrade the 'machine-checkable' claim to 'machine-readable, human-checked' with a roadmap for the evaluator. Include one fully worked example (e.g., Rossby number check for Newton II) showing the inequality being parsed, bound, and evaluated against sample data.
- Change use_instead from a single object to a list of objects (use_instead: [{target_equation, reason}, ...]) to correctly model the common case where multiple valid remediation paths exist for a single failure mode. Document the intended semantics when multiple alternatives are listed (e.g., are they ranked, contextual, or equivalent?).
- Add a referential integrity check requirement (CI-enforced or documented manual step) that verifies: (a) every variable referenced in failure_mode validity_envelope named_groups or inequalities is present in the equation's variable list or derivable from it, and (b) every target_equation in use_instead references an equation ID that exists in the corpus.
- Resolve the asymmetry between the 'strong evidence' framing of the 2-of-2 unity_map validation and the acknowledged statistical limitations. Either pre-register a falsifiability protocol with defined true-positive/false-positive criteria and a minimum precision threshold at a stated corpus size (e.g., ≥50% precision at n≥30 equations), or restate the 2-of-2 result as a preliminary consistency check rather than evidence of mechanism validity.

## Phase B — Informed votes

### claude-opus-4-6

**Verdict:** `approve`  
**Position change:** strengthened  
**Headline:** A technically sound and architecturally correct simplification; the three concrete gaps identified by peers are real but are refinements to a correct design, not structural defects that block approval.

**Response to peers:**

claude-opus-4-6 raised five concerns. I agree with three on technical merit and disagree that they constitute blocking modifications: (1) The 2-of-2 statistical power concern is valid as a caveat on the strength of the evidence claim, but the submission already asks Question 2 about exactly this and proposes a concrete next step (re-evaluate at 30/50/136 equations). A pre-registered precision threshold is a good practice but is a refinement to an already-correct mechanism, not a precondition for shipping the mechanism. The script is deterministic and reproducible; if it breaks at scale, that will be visible in the diff. (2) The validity-envelope parser concern is the strongest technical point raised by any reviewer. String-encoded inequalities without a specified evaluator do make the 'machine-checkable' claim aspirational. However, the submission already mandates SymPy verification (Rule A9) and the inequalities are simple rational expressions over named dimensionless groups—binding semantics are straightforward given the existing variable list. I would accept this as a post-APPROVE deliverable (deliver the evaluator alongside the first five failure-mode entries) rather than a gate. (3) use_instead as a list rather than scalar is correct and trivial to adopt—this is a schema fix, not an architectural concern. (4) The referential integrity check (variables in named_groups exist in the equation's variable list, target_equation exists in corpus) is good CI hygiene and should be adopted, but again is a refinement, not a structural gap. (5) The severity/coupling-strength field is a reasonable suggestion but is genuinely optional at this stage—the failure investigation protocol can triage by the dimensionless-group magnitude directly from the envelope inequality without a separate severity annotation. openai-gpt-5 raised the most technically substantive concern: exact-match on (property_uri, object_of_interest) will produce false negatives for transform-linked quantities

### openai-gpt-5

**Verdict:** `modify`  
**Position change:** unchanged  
**Headline:** Sound two-artifact simplification; approve once a minimal formal, executable validity-envelope spec is published (grammar, binding, unit checks) and used in one worked example.

**Response to peers:**

claude-opus-4-6: Agree that the 2/2 result is statistically underpowered and should not be framed as strong evidence without a pre-registered evaluation. I also concur on the need for an explicit evaluator for validity_envelope (string DSL is not yet machine-checkable), and on tightening referential integrity. I endorse making use_instead a list and adding a severity/impact field; these are technically correct and improve downstream reasoning. My single gating change for approval is the formal, executable validity-envelope spec; I see the falsifiability protocol for unity_map as the next highest priority but not strictly gating if the claims are toned to 'provisional signal'.

openai-gpt-5: Strong agreement on both fronts: (1) exact (property_uri, object_of_interest) equality will miss transform-linked quantities and can suffer ontology granularity drift; enriching matching with unit/dimension compatibility and optional context/constraint filters is technically appropriate, and emitting an explicit confidence helps auditability; (2) the validity-envelope DSL needs a minimal grammar, variable-binding rules to equation variables, and unit/dimension validation. Also agree that assumption_violated should reference a controlled vocabulary/URIs. I propose adopting these enhancements, with the immediate approval-gating step being the DSL spec + reference evaluator and one Newton II worked example.

gemini-2.5-pro: I share your enthusiasm for the architectural simplification and the compositional-typing intuition. Where I diverge is on the evidentiary weight of 2/2 at small n; it is encouraging but not yet strong. Treating unity_map as a diagnostic to drive better metadata quality is spot on. I would still condition approval on the formalization of the validity-envelope machinery so that 'machine-checkable' is literal rather than aspirational.

grok-4: Agree that the artifacts are verifiable and that embedding failure modes is the right design. I echo your caution on small-

### gemini-2.5-pro

**Verdict:** `modify`  
**Position change:** moderated  
**Headline:** The proposal is fundamentally sound and aligns with first principles of physical modeling, but requires two minor schema corrections to be robust.

**Response to peers:**

My initial 'approve' verdict was based on the proposal's excellent alignment with the core principles of compositional physical modeling: explicit interfaces (ports) and defined validity envelopes. The `unity_map` correctly operationalizes the search for compatible ports, and the `failure_modes` block formalizes the validity envelope. The 2-of-2 validation, while on a small corpus, is a powerful demonstration of the mechanism's correctness, not a statistical anomaly; it confirms that shared `(property, object)` descriptors are indeed the correct places to look for physical coupling.

However, after reviewing my peers' feedback, I am moderating my verdict to 'modify'. Two concerns, raised consistently by reviewers Claude and GPT-5, are valid and must be addressed before approval:

1.  **Validity Envelope Semantics:** The claim that validity envelopes are 'machine-checkable' is not yet substantiated. A string in YAML is only checkable if a parser and evaluation semantics are defined. I now agree this is a required modification. The submission must commit to a concrete evaluation engine (e.g., SymPy with a specified variable binding protocol) for this claim to be honest.

2.  **`use_instead` Cardinality:** Reviewer Claude correctly points out that a physical system boundary can often be addressed by multiple alternative formulations (e.g., Newtonian vs. Lagrangian). The schema must therefore support a list of alternatives, not a single scalar. This is a simple but crucial correction for schema robustness.

I disagree with the concerns about statistical power and the need for a pre-registered falsifiability protocol at this stage. The `unity_map` is a deterministic candidate generator based on a physical principle (connecting like quantities on like objects), not a statistical model. Its utility is not measured by a precision/recall score but by the value of the composites it enables. Demanding a formal protocol now reintroduces the process-heavy mindset this proposal c

### grok-4

**Verdict:** `modify`  
**Position change:** moderated  
**Headline:** The simplified proposal is technically sound and honest in scope, but its claims of strong evidence from a small-sample validation exceed what the data supports without a pre-registered falsifiability protocol.

**Response to peers:**

To claude-opus-4-6: I agree the 2-of-2 validation is statistically underpowered and the falsifiability protocol is essential for rigorous claims—persuading me to moderate from approve to modify; however, I push back on needing a severity field or list for use_instead as these are not load-bearing for core feasibility and can be added iteratively if evidence demands. To openai-gpt-5: Persuaded on formalizing the validity-envelope DSL and strengthening matching criteria to reduce false positives/negatives, which aligns with my falsifiability bias; but free-text assumption_violated is not a blocker if cross-referenced to URIs later, as the proposal's core is buildable without it. To gemini-2.5-pro: Position aligns with mine originally—unchanged approval on strengths like alignment with compositional modeling; your concern on metadata quality is valid but operational, not a design flaw requiring modification. To grok-4 (my prior self): My original approval noted small-corpus limits on falsifiability; peers' deeper critiques on protocols and semantics persuade me to moderate, lowering falsifiability score while keeping other strengths intact.

## Phase A — Independent drafts

### claude-opus-4-6

**COI:** ⚠ I have no specific prior exposure to the hequ.ai project, its repository, or its Phase 13 pipeline. I-ADOPT and QUDT are public standards I have general familiarity with from training data. The MITRE ATT&CK framework is widely known. No conflict of interest.  
**Verdict:** `modify`  
**Headline:** A sound and refreshingly honest simplification that collapses six rounds of over-engineering into two concrete artifacts, but the 2-of-2 validation claim needs a rigorous falsifiability protocol before it can be locked as evidence.

**Strengths:**
- Exceptional intellectual honesty: the submission explicitly identifies its own prior over-engineering, names the cause (projecting MITRE's four-stakeholder structure onto a single-stakeholder system), and proposes a principled correction. This is rare and valuable.
- The failure_modes schema is well-shaped: it carries the genuinely load-bearing content (machine-checkable validity envelopes via dimensionless-group inequalities, detection algorithms, remediation pointers) while dropping ceremony (lifecycle states, inter-annotator agreement, red-team passes) that added no information to a single-author corpus.
- Embedding failure modes directly in equation.yaml rather than a parallel catalog eliminates an entire class of cross-reference consistency bugs and makes the data co-located with the entity it describes — a correct data-modeling decision.
- The unity_map.py generator is the right architectural primitive: a deterministic, reproducible, zero-parameter function from existing metadata to a coupling graph. This is testable, diffable, and composable.
- The decision to let ECP composition classes live on composite.yaml rather than on equations is taxonomically correct — composition is a property of the relationship, not the participants.
- Dropping lifecycle states in favor of git history is sound for a single-author corpus and avoids state-machine maintenance overhead that provides no additional information content in this context.
- The post-APPROVE plan is concrete, scoped, and terminable (stop at five failure_modes entries), which prevents indefinite concept-phase drift.

**Concerns:**
- The 2-of-2 validation is presented as strong evidence but is statistically underpowered: with 16 equations and only 2 descriptor-tuple collisions, the base rate of collisions is ~2/C(16,2)=2/120≈1.7%. At this density, achieving 100% precision and 100% recall on 2 positives is consistent with a wide range of underlying mechanisms including coincidence. The submission acknowledges this (Question 2) but still treats it as 'strong evidence' in the body text. This asymmetry between the hedged question and the confident claim needs resolution.
- The falsifiability protocol for the unity_map is underspecified. What constitutes a false positive? What constitutes a false negative? If the corpus grows to 50 equations and the script emits 40 coupling candidates of which only 3 lead to verified composites, is the mechanism falsified or is 3/40 acceptable? Without a pre-registered precision/recall threshold, the claim is not falsifiable in practice.
- The validity_envelope specification uses string-encoded inequalities ('Ro := U / (f * L) >= 1'). The submission says these are 'machine-checkable' but does not specify the parser, the evaluation semantics, or how symbolic variables bind to runtime values. Without a concrete evaluation engine spec, 'machine-checkable' is aspirational, not actual.
- The failure_modes schema lacks a severity or coupling-strength field. Not all failure modes are equally consequential. A failure mode that produces 0.1% relative error at the boundary is qualitatively different from one that produces divergent solutions. Without severity, downstream consumers (the Failure Investigation Protocol) cannot triage.
- The use_instead field assumes a single alternative equation. In reality, boundary violations often admit multiple remediation paths (e.g., Newton II in a rotating frame can be handled by Lagrangian mechanics, by explicit pseudoforce insertion, or by switching to a GR formulation). The schema should support a list, not a scalar.
- There is no discussion of how the descriptor-matching rule handles partial matches (same property, different object_of_interest) or hierarchical matches (e.g., rigid_body is a subclass of physical_body). As the corpus grows, the ontological granularity of object_of_interest will become a critical design parameter, and the current exact-match rule will either over-split or under-merge.
- The proposal does not address how failure_modes entries will be validated against the equations they annotate. If someone writes a validity_envelope inequality referencing a variable not present in the equation's variable list, or cites a dimensionless group whose definition is inconsistent with the equation's dimensional analysis, nothing in the described system catches this.

**Required modifications:**
- Pre-register a falsifiability protocol for the unity_map: define what counts as a true positive, false positive, true negative, and false negative coupling candidate; specify a minimum precision threshold (e.g., ≥50% of emitted candidates must lead to verified composites at corpus size ≥30); commit to re-evaluating the descriptor-matching mechanism if the threshold is not met. Without this, the 2-of-2 result is an anecdote, not evidence.
- Specify the evaluation semantics for validity_envelope inequalities: either (a) commit to a concrete parser/evaluator (e.g., sympy.parse_expr with a defined symbol table binding protocol) and include it in the schema spec, or (b) downgrade the 'machine-checkable' claim to 'machine-readable, human-checked' and document when the automated evaluator will be delivered. The current string-in-YAML approach is not machine-checkable without an evaluator.
- Change use_instead from a single object to a list of objects (use_instead: [{target_equation, reason}, ...]) to handle the common case of multiple valid remediation paths.
- Add a consistency check requirement: either in CI or as a documented manual step, verify that (a) every variable referenced in a failure_mode's validity_envelope.named_groups is present in the equation's variable list or derivable from it, and (b) every target_equation in use_instead actually exists in the corpus. This closes the referential integrity gap.

### openai-gpt-5

**COI:** no COI  
**Verdict:** `modify`  
**Headline:** Sound simplification with a convincing tangible artifact; strengthen matching criteria and formalize validity-envelope semantics to lock approval.

**Strengths:**
- Clear, minimal schema addition that makes validity and failure envelopes machine-checkable.
- Deterministic unity_map generation that rediscovered 2/2 independently verified composites, demonstrating operational signal in existing descriptors.
- Honest scoping and explicit non-goals; avoids over-architecture while preserving the load-bearing parts (dimensionless groups, envelope checks).
- Buildable with existing repository data and easily verifiable via CI and ledgered composites.
- Falsifiable via precision/recall of predicted couplings and envelope-trigger tests on canonical problems.

**Concerns:**
- Exact match on (property_uri, object_of_interest) alone will likely produce both false negatives (transform-linked quantities, e.g., power–force–velocity, density-mediated couplings) and false positives (ontology granularity/synonym drift) as corpus scales.
- I-ADOPT normalization for object_of_interest and property synonyms/equivalences is underspecified; lack of canonicalization will confound matching across domains.
- Validity-envelope DSL (inequalities over dimensionless groups) lacks a formal grammar, variable binding rules to equation variables, and unit/dimension validation; without this, automated detection is underdetermined.
- Small-n validation (2/2) may reflect curation tautology rather than generalizable coupling recovery; needs a pre-registered evaluation plan as the corpus grows.
- assumption_violated is free text; without a controlled vocabulary/URI linkage, downstream reasoning and cross-equation analytics on failure classes will be brittle.

**Required modifications:**
- Strengthen unity_map matching: in addition to (property_uri, object_of_interest) equality, require dimension/unit compatibility checks and optionally filter or re-rank by context/constraint compatibility; emit these checks and a composite confidence score in unity_map.yaml.
- Formalize the validity-envelope DSL: publish a minimal, machine-validated grammar (with unit/dimension checking and explicit bindings from named_groups to equation variables), and constrain assumption_violated to a controlled vocabulary with URIs; provide one fully worked Newton II example using this formalism.

### gemini-2.5-pro

**COI:** no COI  
**Verdict:** `approve`  
**Headline:** A robust and sound simplification that replaces a complex speculative framework with two concrete, validated, and immediately useful artifacts.

**Strengths:**
- The proposal correctly simplifies a complex, multi-catalog framework into two tangible artifacts that are grounded in existing data and processes.
- The core mechanisms align perfectly with established first principles of compositional physical modeling, treating equations as components with typed interfaces (ports) and explicit validity envelopes.
- The `unity_map.py` generator provides compelling, ground-truth validation by auto-rediscovering 100% (2 of 2) of the existing, independently-verified composite models from metadata alone.
- The embedded `failure_modes` schema is a rigorous and machine-checkable method for capturing the domain of validity for each equation, a fundamental requirement for building reliable composite models.
- The plan to use standard git practices (PR review, diffs of generated artifacts) for workflow and governance is a mature and scalable approach that replaces unnecessary bespoke process machinery.

**Concerns:**
- The compelling validation of the `unity_map` rests on a small corpus (16 equations). While the 100% success rate is a strong positive signal, the true false-positive/negative rates at a larger scale remain the primary unknown. The author correctly identifies this.
- The framework's effectiveness is critically dependent on the long-term quality, consistency, and granularity of the I-ADOPT descriptor annotations. The proposed `unity_map` artifact serves as an excellent diagnostic tool for this, but maintaining metadata quality will be an ongoing operational challenge.

### grok-4

**COI:** no COI  
**Verdict:** `approve`  
**Headline:** This simplified proposal effectively collapses prior complexity into verifiable, data-grounded artifacts without sacrificing core functionality.

**Strengths:**
- The unity_map script provides concrete, reproducible evidence of detecting real couplings, validating the descriptor-matching approach on existing data.
- Embedding failure_modes directly in equation.yaml leverages existing structure, ensuring machine-checkable boundaries that align with first-principles physics.
- Honest reduction of scope eliminates unnecessary machinery while preserving buildable mechanisms for envelope detection and cross-equation connections.

**Concerns:**
- Validation is limited to a small corpus (16 equations, 2 couplings), which may not fully demonstrate robustness against false positives as the corpus scales.
- Prior art engagement is implicit (e.g., MITRE, I-ADOPT) but could benefit from explicit citations to falsifiable benchmarks in physics literature.

