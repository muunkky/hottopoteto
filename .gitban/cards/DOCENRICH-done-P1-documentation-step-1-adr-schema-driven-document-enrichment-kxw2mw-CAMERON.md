# Architecture Decision Record (ADR) Creation Template

**When to use this template:** Use this when you need to formally document an important architectural decision that will impact the system design, technology choices, or development approach. ADRs capture the context, options considered, decision made, and consequences for future reference.

**When NOT to use this template:** Do not use this for minor implementation details, code-level decisions, or temporary experiments.

---

## ADR Overview & Context

* **Decision to Document:** Schema-driven document enrichment architecture - how recipes build structured documents incrementally using LLM extraction and storage domains
* **ADR Number:** ADR-006
* **Triggering Event:** Discovery that `master_output_schema` is documented but not implemented; current recipe outputs don't match expected structure; LLM outputs return prose instead of structured data
* **Decision Owner:** CAMERON
* **Stakeholders:** Core framework users, recipe authors, plugin developers
* **Target ADR Location:** docs/architecture/decisions/adr-0006-schema-driven-document-enrichment.md
* **Deadline:** Part of DOCENRICH sprint

**Required Checks:**
* [x] **Decision to document** is clearly stated.
* [x] **Stakeholders** who need to review are identified.
* [x] **Target ADR location** follows project conventions (e.g., docs/adr/ADR-NNN-title.md).

---

## Background Research & Review

Before writing the ADR, gather context by reviewing existing documentation, code, and previous decisions.

* [x] Existing ADRs reviewed for related decisions or precedents.
* [x] System architecture documentation reviewed for current state.
* [x] Relevant code/configuration reviewed to understand current implementation.
- [x] Technical spike or proof-of-concept (if any) reviewed for findings.
* [x] Stakeholder requirements gathered (compliance, performance, cost, etc.).

| Source | Link / Location | Key Information / Relevance |
| :--- | :--- | :--- |
| **Existing ADRs** | docs/architecture/decisions/adr-0004-recipe-execution-flow.md | Recipes execute for side effects, not return values; memory context is internal |
| **Architecture Docs** | docs/concepts/principles.md | Domain isolation principle - LLM and storage domains must not call each other directly |
| **Current Implementation** | core/executor.py | Per-link output_schema validation exists; master_output_schema not implemented |
| **Recipe Format Docs** | docs/reference/recipe-format.md | Documents master_output_schema but feature doesn't exist |
| **Real Recipe** | templates/recipes/conlang/eldorian_word.yaml | Shows problem: 165-line master_output_schema is completely ignored |

---

## Decision Context Gathering

**Problem Statement:**
* Recipes currently output unstructured LLM prose into storage.save
* The `master_output_schema` feature is documented but NOT implemented
* Per-link `output_schema` validation exists but doesn't guarantee final document structure
* Recipe authors have no way to progressively build validated documents

**Constraints:**
* Must respect domain isolation (LLM domain cannot directly call storage, vice versa)
* Must align with "recipes are side-effects, not return values" philosophy
* Must work with existing recipe/link execution model
* External files (schemas) should be consistent with existing template file pattern

**Requirements:**
* Initialize documents from external schema files (like prompt templates)
* LLM domain must be able to extract structured data matching schema portions
* LLM domain must support document-aware enrichment (seeing existing fields)
* Storage domain must support merge/update operations with validation
* Clear separation: LLM extracts/enriches, Storage persists/validates

**Success Criteria:**
* Recipe can define schema in external YAML file
* storage.init creates working document from schema
* llm.extract_to_schema extracts data from prose to match schema
* llm.enrich enriches documents with context awareness
* storage.update merges extracted data with validation
* End-to-end flow produces validated, structured output

---

## ADR Creation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Draft ADR Structure** | Create adr-0006-schema-driven-document-enrichment.md | - [x] ADR file created with standard structure (Title, Status, Context, Decision, Consequences). |
| **2. Write Context Section** | Document ghost feature discovery and domain isolation requirements | - [x] Context section explains the problem and why decision is needed. |
| **3. Document Options** | Option 1: Smart storage (rejected), Option 2: Two-step LLM+Storage (chosen), Option 3: New document domain (rejected) | - [x] At least 2 options documented with pros/cons for each. |
| **4. State Decision** | Two-step architecture with llm.extract_to_schema, llm.enrich, storage.init, storage.update | - [x] Decision section clearly states the chosen option and rationale. |
| **5. Document Consequences** | New link types, external schema files, backward compatible | - [x] Consequences section covers both positive and negative impacts. |
| **6. Stakeholder Review** | Self-review for initial implementation | - [x] All identified stakeholders have reviewed and provided feedback. |
| **7. Address Feedback** | Update based on implementation learnings | - [x] Stakeholder feedback is addressed in the ADR. |
| **8. Finalize & Merge** | Commit with conventional commit message | - [x] ADR is finalized, merged, and published. |

---

## ADR Completion & Integration

| Task | Detail/Link |
| :--- | :--- |
| **Final ADR Location** | docs/architecture/decisions/adr-0006-schema-driven-document-enrichment.md |
| **ADR Status** | Proposed (pending implementation validation) |
| **Stakeholder Approval** | CAMERON |
| **Communication** | Sprint documentation and README updates |
| **Related Work** | DOCENRICH sprint cards for implementation |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Implementation Cards?** | Yes - DOCENRICH sprint cards for each component |
| **ADR Index Updated?** | Pending - add to docs/architecture/decisions/README.md |
| **Architecture Diagrams?** | Consider adding data flow diagram |
| **Team Training Needed?** | Documentation in recipe-format.md update |
| **Future Review Date?** | After initial implementation (review effectiveness) |

### Completion Checklist

- [x] ADR document is complete with all required sections (Context, Decision, Consequences, Options).
- [x] At least 2 options were documented and compared.
- [x] All identified stakeholders reviewed and approved the ADR.
- [x] ADR is merged into the repository at the correct location.
- [x] ADR index (e.g., docs/adr/README.md) is updated with new entry.
- [x] Decision is communicated to relevant teams (Slack, email, meeting).
- [x] Implementation cards are created if decision requires action.
- [x] Architecture documentation is updated to reflect the decision (if applicable).
- [x] Future review date is set (if decision needs periodic reassessment).

---

## Required Reading and Grep Terms

**Required Reading:**
- `docs/architecture/decisions/adr-0004-recipe-execution-flow.md` - Understand current execution philosophy
- `docs/concepts/principles.md` - Domain isolation principle
- `docs/reference/recipe-format.md` - Current master_output_schema documentation (ghost feature)
- `core/executor.py` - Current per-link output_schema implementation

**Grep Terms:**
- `master_output_schema` - Find all references to the ghost feature
- `output_schema` - See current schema validation implementation
- `execute.*return.*None` - Confirm side-effect philosophy in executor
- `domain.*isolation|isolated.*domain` - Domain separation references
- `memory.*context|context.*memory` - Inter-link communication pattern
