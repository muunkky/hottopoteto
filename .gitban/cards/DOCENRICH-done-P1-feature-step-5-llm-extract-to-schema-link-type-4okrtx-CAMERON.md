# Feature Development Template

**When to use this template:** Use this for any new feature work that requires planning, design, implementation, testing, and documentation.

---

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint - Schema-Driven Document Enrichment
* **Feature Area/Component:** LLM Domain - llm.extract_to_schema link type
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
| **LLM Domain** | core/domains/llm/ | Existing LLM link patterns |
| **JSON Mode** | OpenAI/Anthropic docs | response_format for structured output |
| **Schema Validation** | jsonschema library | Already used in executor |

## Design & Planning

### Initial Design Thoughts & Requirements

* `llm.extract_to_schema` extracts structured data from unstructured text
* Takes source text + target schema, returns data matching schema
* Auto-generates extraction prompt from schema structure
* Uses LLM JSON mode for reliable structured output
* Optional `hint` parameter for domain-specific guidance
* Smart defaults - works with minimal config

### Acceptance Criteria

- [x] llm.extract_to_schema link type is registered and executable
- [x] Extracts data from source text to match provided schema
- [x] Auto-generates intelligent extraction prompt from schema
- [x] Uses JSON mode for structured LLM output
- [x] Supports optional `hint` parameter for guidance
- [x] Validates output against schema before returning
- [x] Handles extraction failures gracefully

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | LLMExtractToSchemaLink class | - [x] Design Complete |
| **Test Plan Creation** | test_llm_extract_to_schema.py | - [x] Test Plan Approved |
| **TDD Implementation** | Failing tests first | - [x] Implementation Complete |
| **Integration Testing** | Test with storage workflow | - [x] Integration Tests Pass |
| **Documentation** | Update llm domain docs | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Merge to main | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Test extraction, prompt generation, validation | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | LLMExtractToSchemaLink | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All extraction tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | All LLM tests | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | N/A | - [x] Performance requirements are met |

### Implementation Notes

**Link Configuration:**
```yaml
# Minimal (smart defaults)
- name: "Extract_Origins"
  type: "llm.extract_to_schema"
  source: "{{ Generate_Origins.data.raw }}"
  schema: "{{ Working_Doc.data.schema.properties.origin_words }}"

# With guidance
- name: "Extract_Origins"
  type: "llm.extract_to_schema"
  source: "{{ Generate_Origins.data.raw }}"
  schema: "{{ Working_Doc.data.schema.properties.origin_words }}"
  hint: "Focus on the fictional etymology components"
  model: "gpt-4o"
  temperature: 0.2
```

**Auto-Generated Prompt:**
```
Extract structured data from the following text.

TARGET SCHEMA:
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "word": {"type": "string", "description": "The origin word"},
      "meaning": {"type": "string", "description": "Meaning in English"}
    }
  }
}

EXTRACTION GUIDANCE: Focus on the fictional etymology components

SOURCE TEXT:
---
The word derives from three Sylvan roots: "fael" meaning grace or beauty, 
"neth" referring to youth or newness, and "wen" a feminine suffix...
---

Extract data matching the schema above. Return valid JSON only.
```

**Key Implementation:**
```python
class LLMExtractToSchemaLink(LinkHandler):
    @classmethod
    def execute(cls, link_config, context):
        source = cls._render_template(link_config.get("source"), context)
        schema = cls._resolve_schema(link_config.get("schema"), context)
        hint = link_config.get("hint", "")
        
        # Build extraction prompt from schema
        prompt = cls._build_extraction_prompt(source, schema, hint)
        
        # Call LLM with JSON mode
        result = cls._call_llm_json_mode(
            prompt=prompt,
            schema=schema,
            model=link_config.get("model", "gpt-4o"),
            temperature=link_config.get("temperature", 0.2)
        )
        
        # Validate against schema
        validate(instance=result, schema=schema)
        
        return {
            "raw": prompt,
            "data": result
        }
    
    @classmethod
    def _build_extraction_prompt(cls, source, schema, hint):
        """Build intelligent extraction prompt from schema."""
        field_descriptions = cls._describe_schema_fields(schema)
        
        prompt = f"""Extract structured data from the following text.

TARGET SCHEMA:
{json.dumps(schema, indent=2)}

{f"EXTRACTION GUIDANCE: {hint}" if hint else ""}

SOURCE TEXT:
---
{source}
---

Extract data matching the schema above. Return valid JSON only.
If a field cannot be determined, omit it (optional) or infer (required)."""
        
        return prompt
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review |
| **QA Verification** | Test with real recipe |
| **Production Deployment** | Merge to main |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Multi-model support, extraction confidence scores |

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
- `core/domains/llm/links.py` - Existing LLM link patterns
- `core/domains/llm/functions.py` - LLM calling functions
- OpenAI API docs - `response_format` / JSON mode
- Anthropic API docs - Structured output patterns

**Grep Terms:**
- `LLM.*Link|llm.*link` - Existing LLM link implementations
- `response_format|json.*mode` - Structured output configuration
- `openai.*chat|anthropic.*message` - API call patterns
- `jsonschema.*validate|validate.*instance` - Schema validation
- `temperature|model.*config` - LLM configuration patterns
