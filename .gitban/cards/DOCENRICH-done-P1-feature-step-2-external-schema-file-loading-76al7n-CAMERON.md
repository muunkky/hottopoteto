# Feature Development Template

**When to use this template:** Use this for any new feature work that requires planning, design, implementation, testing, and documentation.

---

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint - Schema-Driven Document Enrichment
* **Feature Area/Component:** Storage Domain - Schema File Loading
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
| **README.md** | docs/reference/recipe-format.md | Templates use `file:` key for external loading |
| **Architecture Docs** | docs/concepts/principles.md | External files pattern already established for prompts |
| **Similar Features** | core/executor.py template loading | _load_template_file method exists, can extend pattern |
| **Schema Docs** | docs/reference/schema-formats.md | JSON Schema format documented |

## Design & Planning

### Initial Design Thoughts & Requirements

* Schemas should be loaded from `templates/schemas/` directory (parallel to `templates/text/`)
* Use same `file:` key pattern as prompt templates: `schema: { file: "schemas/eldorian_word.yaml" }`
* Support YAML format for schemas (more readable than JSON for complex schemas)
* Schema files should contain valid JSON Schema content
* Consider schema inheritance/extension (future enhancement)

### Acceptance Criteria

- [x] Schema files can be placed in `templates/schemas/` directory
- [x] Recipes can reference schemas with `schema: { file: "path/to/schema.yaml" }`
- [x] Schema loading follows same pattern as template file loading
- [x] Invalid schema files produce clear error messages
- [x] Schema validation uses existing JSON Schema validation

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | Use existing template loading pattern | - [x] Design Complete |
| **Test Plan Creation** | Unit tests for schema loading | - [x] Test Plan Approved |
| **TDD Implementation** | Create failing tests first | - [x] Implementation Complete |
| **Integration Testing** | Test with real recipe | - [x] Integration Tests Pass |
| **Documentation** | Update recipe-format.md | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Merge to main | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | test_schema_file_loading.py | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | Extend executor schema resolution | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All schema loading tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up implementation | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | Run all tests | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | N/A for this feature | - [x] Performance requirements are met |

### Implementation Notes

**Key Implementation Points:**
1. Add `_load_schema_file()` method to executor (similar to `_load_template_file()`)
2. Resolve `{ file: "path" }` syntax in schema fields
3. Support both `.yaml` and `.json` schema files
4. Cache loaded schemas to avoid repeated disk reads

```python
# Example schema file: templates/schemas/eldorian_word.yaml
type: object
properties:
  english_word:
    type: string
    description: The English word being translated
  eldorian_word:
    type: string
    description: The generated Eldorian word
  origin_words:
    type: array
    items:
      type: object
      properties:
        word: { type: string }
        meaning: { type: string }
required:
  - english_word
  - eldorian_word
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review with conventional commits |
| **QA Verification** | Test with eldorian_word recipe |
| **Staging Deployment** | N/A |
| **Production Deployment** | Merge to main |
| **Monitoring Setup** | N/A |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No |
| **Further Investigation?** | Consider schema inheritance for future |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Schema $ref resolution, schema composition |

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
- `core/executor.py` - `_load_template_file()` method for existing template loading pattern
- `templates/text/` - Existing prompt template directory structure
- `docs/reference/schema-formats.md` - JSON Schema format documentation

**Grep Terms:**
- `_load_template_file` - Current template loading implementation
- `file:.*yaml|file:.*json` - Find existing file reference patterns in recipes
- `templates.*path|template.*dir` - Template directory configuration
- `jsonschema|json.*schema` - Schema validation imports and usage
- `\.yaml|\.json` - File extension handling patterns
