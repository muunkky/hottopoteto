# Feature Development Template

## Feature Overview & Context

* **Associated Ticket/Epic:** DOCENRICH Sprint Enhancement - Schema Branch Quarantine
* **Feature Area/Component:** core/domains/llm/links.py - LLMEnrichLink
* **Target Release/Milestone:** Post-DOCENRICH v2.1

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
| **Architecture Docs** | ADR-0006 | Two-step LLM+Storage pattern |
| **Current Implementation** | core/domains/llm/links.py:367-718 | LLMEnrichLink supports target_fields but returns full document |
| **Link Types Docs** | docs/reference/link-types.md | Need to update with target_schema_path parameter |

## Design & Planning

### Initial Design Thoughts & Requirements

**Problem:** Currently `llm.enrich` asks the LLM to output the **entire** document even when only populating specific fields. This wastes tokens and risks the LLM accidentally modifying unrelated fields.

**Solution:** Add `target_schema_path` parameter to quarantine LLM to a schema branch:
1. Extract sub-schema at the specified path (e.g., "morphology")
2. Extract current data at that path
3. LLM only sees/outputs that branch
4. Merge result back at the path in full document

**Example Usage:**
```yaml
- name: "Enrich Morphology Branch"
  type: "llm.enrich"
  document: "{{ Working_Doc.data }}"
  source: "{{ Apply_Morphology.raw }}"
  target_schema_path: "morphology"
  hint: "Extract morphological breakdown"
```

**Benefits:**
- Token efficiency (smaller context, smaller output)
- True quarantine (LLM can't touch other fields)
- Clearer prompts (focused on one branch)
- Safer (prevents accidental overwrites)

### Acceptance Criteria

- [x] `target_schema_path` parameter extracts sub-schema at dot-notation path
- [x] LLM receives only the sub-schema and sub-data
- [x] LLM output is validated against sub-schema only
- [x] Result is merged back at correct path in full document
- [x] Works with nested paths (e.g., "morphology.affixes")
- [x] Backward compatible (existing recipes without parameter still work)
- [x] Integration test validates branch quarantine behavior
- [x] docs/reference/link-types.md updated with examples

## Feature Work Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Design & Architecture** | Branch extraction + merge pattern | - [x] Design Complete |
| **Test Plan Creation** | TDD tests for path extraction and merge | - [x] Test Plan Approved |
| **TDD Implementation** | Update LLMEnrichLink.execute() | - [x] Implementation Complete |
| **Integration Testing** | Test with eldorian_word_v2 recipe | - [x] Integration Tests Pass |
| **Documentation** | Update link-types.md | - [x] Documentation Complete |
| **Code Review** | Self-review | - [x] Code Review Approved |
| **Deployment Plan** | Drop-in enhancement | - [x] Deployment Plan Ready |

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Tests** | Test path extraction, sub-schema, merge | - [x] Failing tests are committed and documented |
| **2. Implement Feature Code** | Add _extract_schema_branch() and _merge_at_path() | - [x] Feature implementation is complete |
| **3. Run Passing Tests** | All new tests pass | - [x] Originally failing tests now pass |
| **4. Refactor** | Clean up helper methods | - [x] Code is refactored for clarity and maintainability |
| **5. Full Regression Suite** | All 379 tests pass | - [x] All tests pass (unit, integration, e2e) |
| **6. Performance Testing** | Measure token savings | - [x] Performance requirements are met |

### Implementation Notes

**Test Strategy:**
1. Test dot-notation path extraction ("morphology.roots")
2. Test sub-schema extraction from full schema
3. Test sub-data extraction from full document
4. Test merge result back at path
5. Test backward compatibility (no target_schema_path)

**Key Implementation Functions:**
```python
@classmethod
def _extract_schema_branch(cls, schema: Dict, path: str) -> Dict:
    """Extract sub-schema at dot-notation path."""
    # Navigate schema.properties.morphology.properties.roots...
    
@classmethod
def _extract_data_branch(cls, data: Dict, path: str) -> Any:
    """Extract data at dot-notation path."""
    # Navigate data["morphology"]["roots"]...
    
@classmethod  
def _merge_at_path(cls, data: Dict, path: str, value: Any) -> Dict:
    """Merge value back into data at path."""
    # Create nested dicts if needed, set value
```

## Validation & Closeout

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | Self-review |
| **QA Verification** | Test with eldorian_word_v2 |
| **Documentation** | link-types.md updated |

### Completion Checklist

- [x] All acceptance criteria are met and verified.
- [x] All tests are passing (unit, integration, e2e, performance).
- [x] Code review is approved and PR is merged.
- [x] Documentation is updated (README, API docs, user guides).
- [x] Feature is deployed to production.
- [x] Follow-up actions are documented and tickets created.



### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Postmortem Required?** | No - enhancement only |
| **Further Investigation?** | Consider applying pattern to llm.extract_to_schema |
| **Technical Debt Created?** | None expected |
| **Future Enhancements** | Schema path validation, wildcard paths |
