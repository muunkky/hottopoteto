# Feature Development Template

**When to use this template:** Use this for any new feature work that requires planning, design, implementation, testing, and documentation.

---

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint - Schema-Driven Document Enrichment
* **Feature Area/Component:** LLM Domain - llm.enrich link type
* **Target Release/Milestone:** v1.0 - Foundation & Quality

**Required Checks:**
* [x] **Associated Ticket/Epic** link is included above.
* [x] **Feature Area/Component** is identified.
* [x] **Target Release/Milestone** is confirmed.

## Documentation & Prior Art Review

* [x] `README.md` or project documentation reviewed.
* [x] Existing architecture documentation or ADRs reviewed.
* [x] Related feature implementations or similar code reviewed.
* [x] API documentation or interface specs reviewed (if applicable).

| Document Type | Link / Location | Key Findings / Action Required |
| :--- | :--- | :--- |
| **LLM Domain** | core/domains/llm/ | Existing patterns |
| **llm.extract_to_schema** | This sprint | Build on extraction foundation |
| **Document Context** | ADR discussion | Key differentiator - sees existing fields |

## Design & Planning

### Initial Design Thoughts & Requirements

* `llm.enrich` is document-aware extraction that sees the full document context
* LLM sees: current document state + new source text + target fields
* Can make smarter inferences because it knows what's already populated
* Returns the enriched document (preserving existing fields)
* Builds on llm.extract_to_schema patterns

### Acceptance Criteria

- [x] llm.enrich link type is registered and executable
- [x] Receives full document context (not just schema)
- [x] Extracts and populates specified target_fields
- [x] Preserves all existing document fields
- [x] LLM sees existing values for context-aware inference
- [x] Returns complete enriched document
- [x] Supports multiple target_fields in one call
- [x] Supports `target_fields: "auto"` for intelligent detection

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | LLMEnrichLink class | - [x] Design Complete |
| **Test Plan Creation** | test_llm_enrich.py | - [x] Test Plan Approved |
| **TDD Implementation** | Failing tests first | - [x] Implementation Complete |
| **Integration Testing** | Full document workflow | - [x] Integration Tests Pass |
| **Documentation** | Update llm domain docs | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Merge to main | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Test enrichment, context awareness, field preservation | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | LLMEnrichLink | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All enrich tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | All LLM tests | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | N/A | - [x] Performance requirements are met |

### Implementation Notes

**Link Configuration:**
```yaml
- name: "Enrich_With_Origins"
  type: "llm.enrich"
  document: "{{ Working_Doc.data }}"
  source: "{{ Generate_Origins.data.raw }}"
  target_fields:
    - "origin_words"
    - "revised_connotation"
  hint: "Extract the fictional etymologies"
```

**What the LLM Sees:**
```
You are enriching a document with new information.

CURRENT DOCUMENT STATE:
{
  "english_word": "woman",
  "connotation": "of marriageable age",
  "origin_words": null,           // ← needs filling
  "revised_connotation": null,    // ← needs filling  
  "eldorian_word": null,
  "morphology": null
}

TARGET FIELDS TO POPULATE: origin_words, revised_connotation

NEW INFORMATION TO INCORPORATE:
---
The word derives from three Sylvan roots: "fael" meaning grace or beauty, 
"neth" referring to youth or newness, and "wen" a feminine suffix...
---

GUIDANCE: Extract the fictional etymologies

Return the complete document with target fields populated.
Preserve all existing values. Only update the specified target fields.
Return valid JSON matching the document structure.
```

**Key Implementation:**
```python
class LLMEnrichLink(LinkHandler):
    @classmethod
    def execute(cls, link_config, context):
        document = cls._resolve_document(link_config.get("document"), context)
        source = cls._render_template(link_config.get("source"), context)
        target_fields = link_config.get("target_fields", "auto")
        hint = link_config.get("hint", "")
        
        # Get schema from document
        schema = document.get("schema", {})
        current_data = document.get("data", {})
        
        # Determine target fields
        if target_fields == "auto":
            target_fields = cls._find_empty_fields(current_data, schema)
        
        # Build enrichment prompt with full context
        prompt = cls._build_enrichment_prompt(
            current_data=current_data,
            source=source,
            target_fields=target_fields,
            schema=schema,
            hint=hint
        )
        
        # Call LLM with JSON mode
        enriched_data = cls._call_llm_json_mode(
            prompt=prompt,
            schema=schema,
            model=link_config.get("model", "gpt-4o"),
            temperature=link_config.get("temperature", 0.3)
        )
        
        # Validate enriched document
        validate(instance=enriched_data, schema=schema)
        
        return {
            "raw": prompt,
            "data": enriched_data
        }
```

**Output:**
```python
{
  "raw": "...",  # The enrichment prompt
  "data": {      # Complete enriched document
    "english_word": "woman",
    "connotation": "of marriageable age",
    "origin_words": [
      {"word": "fael", "meaning": "grace or beauty", "origin": "Sylvan"},
      {"word": "neth", "meaning": "youth or newness", "origin": "Sylvan"},
      {"word": "wen", "meaning": "feminine suffix", "origin": "Sylvan"}
    ],
    "revised_connotation": "graceful young womanhood with connotations of eligibility",
    "eldorian_word": null,
    "morphology": null
  }
}
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review |
| **QA Verification** | Test with eldorian_word recipe |
| **Production Deployment** | Merge to main |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Multi-source enrichment, partial document updates |

### Completion Checklist

- [x] All acceptance criteria are met and verified.
- [x] All tests are passing (unit, integration, e2e, performance).
- [x] Code review is approved and PR is merged.
- [x] Documentation is updated (README, API docs, user guides).
- [x] Feature is deployed to production.
- [x] Monitoring and alerting are configured.
- [x] Stakeholders are notified of completion.
- [x] Follow-up actions are documented and tickets created.
- [x] Associated ticket/epic is closed.

---

## Required Reading and Grep Terms

**Required Reading:**
- `LLMExtractToSchemaLink` (from Step 5) - Foundation to build on
- `StorageInitLink` (from Step 3) - Document structure format
- `StorageUpdateLink` (from Step 4) - How enriched data gets persisted

**Grep Terms:**
- `LLMExtractToSchemaLink|extract_to_schema` - Step 5 implementation to extend
- `document.*schema|schema.*document` - Document/schema relationships
- `target_fields|target.*field` - Field selection patterns
- `empty.*field|null.*field|field.*null` - Empty field detection
- `enrich|enrichment` - Any existing enrichment patterns
