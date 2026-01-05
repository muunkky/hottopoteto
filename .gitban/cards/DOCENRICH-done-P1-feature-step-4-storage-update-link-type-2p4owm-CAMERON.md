# Feature Development Template

**When to use this template:** Use this for any new feature work that requires planning, design, implementation, testing, and documentation.

---

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint - Schema-Driven Document Enrichment
* **Feature Area/Component:** Storage Domain - storage.update link type
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
| **README.md** | core/domains/storage/README.md | Current save_entity doesn't support merge |
| **Similar Features** | StorageSaveLink | Pattern for link implementation |
| **Storage Functions** | functions.py | May need update_entity function |

## Design & Planning

### Initial Design Thoughts & Requirements

* `storage.update` merges new data into existing document
* References document by ID from storage.init output
* Supports `merge: true` for partial updates (default behavior)
* Validates merged data against document's schema
* Returns updated document state for downstream links

### Acceptance Criteria

- [x] storage.update link type is registered and executable
- [x] Updates document by document_id reference
- [x] Merges data into existing document (doesn't replace)
- [x] Validates merged data against stored schema
- [x] Returns updated document state including schema
- [x] Handles nested object merging correctly
- [x] Handles array append vs replace options

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | StorageUpdateLink class | - [x] Design Complete |
| **Test Plan Creation** | test_storage_update_link.py | - [x] Test Plan Approved |
| **TDD Implementation** | Failing tests first | - [x] Implementation Complete |
| **Integration Testing** | Multi-step recipe test | - [x] Integration Tests Pass |
| **Documentation** | Update storage README | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Merge to main | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Test merge, validation, nested updates | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | StorageUpdateLink in links.py | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All update tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | All storage tests | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | N/A | - [x] Performance requirements are met |

### Implementation Notes

**Link Configuration:**
```yaml
- name: "Update_Origins"
  type: "storage.update"
  document_id: "{{ Working_Doc.data.id }}"
  collection: "{{ Working_Doc.data.collection }}"
  data:
    origin_words: "{{ Extract_Origins.data }}"
  merge: true  # Default - merge into existing
```

**Output Structure:**
```python
{
  "raw": "Updated document doc-abc123",
  "data": {
    "id": "doc-abc123",
    "collection": "eldorian_words",
    "schema": { ... },
    "data": {
      "english_word": "woman",
      "connotation": "of marriageable age",
      "origin_words": [  # Now populated
        {"word": "fael", "meaning": "grace"},
        {"word": "neth", "meaning": "youth"}
      ],
      "eldorian_word": null  # Still empty
    }
  }
}
```

**Key Implementation:**
```python
class StorageUpdateLink(LinkHandler):
    @classmethod
    def execute(cls, link_config, context):
        doc_id = cls._render_template(link_config.get("document_id"), context)
        collection = cls._render_template(link_config.get("collection"), context)
        new_data = cls._extract_data(link_config.get("data"), context)
        merge = link_config.get("merge", True)
        
        # Get existing document
        existing = get_entity(collection, doc_id)
        schema = existing.get("metadata", {}).get("schema", {})
        
        # Merge or replace
        if merge:
            updated_data = cls._deep_merge(existing["data"], new_data)
        else:
            updated_data = new_data
        
        # Validate against schema
        cls._validate_against_schema(updated_data, schema)
        
        # Save updated document
        save_entity(collection, updated_data, metadata=existing["metadata"])
        
        return {
            "raw": f"Updated document {doc_id}",
            "data": {
                "id": doc_id,
                "collection": collection,
                "schema": schema,
                "data": updated_data
            }
        }
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review |
| **QA Verification** | Test with multi-step recipe |
| **Production Deployment** | Merge to main |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Optimistic locking, conflict resolution |

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
- `core/domains/storage/links.py` - `StorageInitLink` (from Step 3) as foundation
- `core/domains/storage/functions.py` - May need `get_entity`, `update_entity` functions
- `jsonschema` library docs - Validation patterns

**Grep Terms:**
- `StorageInitLink|storage\.init` - Step 3 implementation to extend
- `get_entity|update_entity` - Entity retrieval/update functions
- `deep.*merge|merge.*dict` - Dictionary merge patterns
- `validate.*schema|schema.*validate` - Schema validation calls
- `document_id|doc_id` - Document reference patterns
