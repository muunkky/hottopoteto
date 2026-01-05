# Feature Development Template

**When to use this template:** Use this for any new feature work that requires planning, design, implementation, testing, and documentation.

---

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint - Schema-Driven Document Enrichment
* **Feature Area/Component:** Storage Domain - storage.init link type
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
| **README.md** | core/domains/storage/README.md | Storage domain structure documented |
| **Architecture Docs** | docs/concepts/architecture.md | Links execute and return output to memory context |
| **Similar Features** | core/domains/storage/links.py | StorageSaveLink pattern to follow |
| **Storage Functions** | core/domains/storage/functions.py | save_entity function available |

## Design & Planning

### Initial Design Thoughts & Requirements

* `storage.init` creates a "working document" that persists across recipe execution
* Returns document ID, schema, current data state in output
* Schema travels with document so LLM links can reference portions
* Document stored in storage with unique ID for future updates
* Supports initial_data for pre-populating known fields

### Acceptance Criteria

- [x] storage.init link type is registered and executable
- [x] Creates document with unique ID in specified collection
- [x] Loads schema from file reference or inline definition
- [x] Returns schema in output for downstream links to reference
- [x] Returns document ID for storage.update references
- [x] Supports initial_data parameter for pre-population
- [x] Empty fields initialized as null per schema

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | StorageInitLink class design | - [x] Design Complete |
| **Test Plan Creation** | test_storage_init_link.py | - [x] Test Plan Approved |
| **TDD Implementation** | Failing tests first | - [x] Implementation Complete |
| **Integration Testing** | Test in recipe context | - [x] Integration Tests Pass |
| **Documentation** | Update storage README and recipe-format.md | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Merge to main | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Test init creates document with ID, schema, data | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | StorageInitLink in links.py | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All storage.init tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up implementation | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | Run all storage tests | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | N/A | - [x] Performance requirements are met |

### Implementation Notes

**Link Configuration:**
```yaml
- name: "Working_Doc"
  type: "storage.init"
  collection: "eldorian_words"
  schema:
    file: "schemas/eldorian_word.yaml"
  initial_data:
    english_word: "{{ user_input }}"
    connotation: "{{ user_connotation }}"
```

**Output Structure:**
```python
{
  "id": "doc-abc123",          # Unique document ID
  "collection": "eldorian_words",
  "schema": { ... },           # Full schema for downstream reference
  "data": {                    # Current document state
    "english_word": "woman",
    "connotation": "of marriageable age",
    "origin_words": null,      # Empty fields per schema
    "eldorian_word": null
  }
}
```

**Key Implementation:**
```python
class StorageInitLink(LinkHandler):
    @classmethod
    def execute(cls, link_config, context):
        collection = link_config.get("collection")
        schema = cls._resolve_schema(link_config.get("schema"), context)
        initial_data = cls._extract_data(link_config.get("initial_data", {}), context)
        
        # Initialize document with nulls for all schema properties
        data = cls._initialize_from_schema(schema, initial_data)
        
        # Generate unique ID and save
        doc_id = generate_id("doc")
        save_entity(collection, data, metadata={"doc_id": doc_id, "schema": schema})
        
        return {
            "raw": f"Initialized document {doc_id}",
            "data": {
                "id": doc_id,
                "collection": collection,
                "schema": schema,
                "data": data
            }
        }
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review |
| **QA Verification** | Test with recipe |
| **Production Deployment** | Merge to main |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No |
| **Further Investigation?** | Document versioning for future |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Document locking, concurrent access |

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
- `core/domains/storage/links.py` - Existing `StorageSaveLink` pattern to follow
- `core/domains/storage/functions.py` - `save_entity` function implementation
- `core/domains/storage/__init__.py` - Domain registration pattern

**Grep Terms:**
- `StorageSaveLink|storage\.save` - Current storage link implementation
- `save_entity` - Entity persistence function
- `LinkHandler` - Base class for link handlers
- `_extract_data` - Data extraction helper method
- `generate.*id|uuid` - ID generation patterns
- `collection` - Storage collection usage
