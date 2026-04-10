---
description: Migrate emergency _coerce_types implementation from storage.update to centralized coerce_to_schema utility in core.validation module, ensuring consistent type handling across all validation points
use_case: Refactor emergency fix into architectural standard, prevent code duplication, enable consistent type coercion for recipe templates and schema validation
---

# Centralize Type Coercion to core.validation Module

**When this refactoring was needed:** After ADR-017 Type Handling Architecture approved, need to migrate emergency fix (_coerce_types in storage/links.py:718-780) to centralized utility following fail-fast architecture (ADR-016).

**Scope:** Extract _coerce_types from storage.update, generalize as coerce_to_schema(), add comprehensive error handling with field paths, update 4 call sites (storage.update, storage.save, llm.extract_to_schema, llm.enrich).

---

## Refactoring Overview & Motivation

* **Refactoring Target:** Type coercion logic for Jinja2 template rendering → schema validation
* **Code Location:** 
  - Source: `core/domains/storage/links.py:718-780` (_coerce_types method)
  - Destination: `core/validation.py` (new coerce_to_schema function)
* **Refactoring Type:** Extract Method + Centralize Utility
* **Motivation:** Emergency fix implemented in storage.update works but is duplicated, undocumented, and not available to other validation points (LLM extraction, enrichment). ADR-017 recommends centralized utility for consistent type handling.
* **Business Impact:** 
  - Prevents silent failures when recipe templates render strings that schemas expect as integers/floats/booleans
  - Enables consistent behavior across storage, LLM, and future validation points
  - Reduces maintenance burden - single implementation vs duplicated logic
  - Aligns with fail-fast architecture (ADR-016) - clear errors on coercion failures
* **Scope:** 
  - Extract 63 lines from storage/links.py:718-780
  - Add comprehensive error handling with field path context
  - Update 4 call sites across 2 domains (storage, LLM)
  - Add tests targeting 95% coverage
* **Risk Level:** Medium - storage.update is critical path for recipe execution, LLM extraction is core functionality
* **Related Work:** 
  - ADR-017 Type Handling Architecture for Recipe Templates (card hgw39p)
  - ADR-016 Schema Validation Error Handling (fail-fast architecture)
  - Emergency fix: storage/links.py:718-780

**Required Checks:**
* [x] **Refactoring motivation** clearly explains why this change is needed.
* [x] **Scope** is specific and bounded (not open-ended "improve everything").
* [x] **Risk level** is assessed based on code criticality and usage.

---

## Pre-Refactoring Context Review

Before refactoring, review existing code, tests, documentation, and dependencies to understand current implementation and prevent breaking changes.

* [ ] Existing code reviewed and behavior fully understood.
* [ ] Test coverage reviewed - current test suite provides safety net.
* [ ] Documentation reviewed (README, docstrings, inline comments).
* [ ] Style guide and coding standards reviewed for compliance.
* [ ] Dependencies reviewed (internal modules, external libraries).
* [ ] Usage patterns reviewed (who calls this code, how it's used).
* [ ] Previous refactoring attempts reviewed (if any - learn from history).

Use the table below to document findings from pre-refactoring review. Add rows as needed.

| Review Source | Link / Location | Key Findings / Constraints |
| :--- | :--- | :--- |
| **Existing Code** | core/domains/storage/links.py:718-780 | Emergency fix: _coerce_types recursively coerces strings to int/float/bool based on schema types. Handles nested objects and arrays. Raises ValidationError on coercion failure. |
| **Test Coverage** | tests/core/domains/storage/ | Need to check existing storage.update tests - likely minimal coverage of _coerce_types since emergency fix |
| **Documentation** | ADR-017 (card hgw39p), ADR-016 (fail-fast architecture) | ADR-017 recommends centralized coerce_to_schema in core.validation. Must align with fail-fast pattern (raise exceptions, never return error dicts). |
| **Style Guide** | docs/guides/plugin-error-handling.md | Must follow fail-fast pattern: raise ValidationError on coercion failure with clear field path context |
| **Dependencies** | jsonschema, core.validation module | Uses jsonschema for schema structure. Will use ValidationError from core.validation. No external library dependencies. |
| **Usage Patterns** | Called by storage.update before validate_schema (line 662) | Critical path: recipe execution calls storage.update hundreds of times. Coercion must be fast (<1ms overhead). |
| **Previous Attempts** | None - emergency fix was first implementation | No prior attempts. Emergency fix proven to work in production recipe execution. |

---

## Refactoring Strategy & Risk Assessment

> Use this space for refactoring approach, incremental steps, risk mitigation, and rollback plan.

**Refactoring Approach:**
* Extract Method: Copy _coerce_types from storage/links.py:718-780 to core/validation.py
* Generalize: Rename to coerce_to_schema, improve error messages with field path context
* Update Call Sites: Replace _coerce_types calls with coerce_to_schema in storage.update, storage.save, llm.extract_to_schema, llm.enrich
* Add Tests: Comprehensive test coverage (95% target) before migration

**Incremental Steps:**
1. **Step 1**: Review emergency fix implementation, understand all edge cases (nested objects, arrays, null handling, coercion failures)
2. **Step 2**: Add comprehensive tests for existing _coerce_types behavior in storage.update (lock in current behavior)
3. **Step 3**: Create coerce_to_schema in core.validation.py (copy + generalize + improve error handling)
4. **Step 4**: Update storage.update to use coerce_to_schema (replace _coerce_types call at line 662)
5. **Step 5**: Run storage tests to verify no regression
6. **Step 6**: Add coerce_to_schema to storage.save (before schema validation)
7. **Step 7**: Add coerce_to_schema to llm.extract_to_schema (before schema validation)
8. **Step 8**: Add coerce_to_schema to llm.enrich (before schema validation)
9. **Step 9**: Run full test suite to verify all call sites working
10. **Step 10**: Remove _coerce_types method from storage/links.py (cleanup)
11. **Step 11**: Update documentation (inline comments, plugin guide, architecture docs)

**Risk Mitigation:**
* **Risk**: Breaking storage.update in production recipes. **Mitigation**: Add comprehensive tests BEFORE refactoring to lock in current behavior. Use feature flag if needed.
* **Risk**: Performance regression (coercion overhead). **Mitigation**: Benchmark before/after, target <1ms overhead for typical recipe data.
* **Risk**: Coercion logic incomplete (missing edge cases). **Mitigation**: Emergency fix already proven in production. Add tests for all edge cases.
* **Risk**: Breaking LLM extraction/enrichment. **Mitigation**: Add coercion incrementally, test each call site independently.

**Rollback Plan:**
* **Rollback**: Git revert to restore _coerce_types in storage.update
* **Emergency**: Keep _coerce_types as fallback for 1 release cycle before removal
* **Testing**: Full regression test suite must pass before removing emergency fix code

**Success Criteria:**
* All existing tests pass without modification
* New tests for coerce_to_schema achieve 95% coverage
* All 4 call sites use centralized coerce_to_schema
* No performance regression (<1ms overhead)
* Documentation updated (inline comments, plugin guide)
* Emergency fix code removed (cleanup)

---

## Refactoring Phases

Track the major phases of refactoring from test establishment through deployment.

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Pre-Refactor Test Suite** | Status: Not Started | - [ ] Comprehensive tests exist before refactoring starts. |
| **Baseline Measurements** | Status: Not Started | - [ ] Baseline metrics captured (complexity, performance, coverage). |
| **Incremental Refactoring** | Status: Not Started | - [ ] Refactoring implemented incrementally with passing tests at each step. |
| **Documentation Updates** | Status: Not Started | - [ ] All documentation updated to reflect refactored code. |
| **Code Review** | Status: Not Started | - [ ] Code reviewed for correctness, style guide compliance, maintainability. |
| **Performance Validation** | Status: Not Started | - [ ] Performance validated - no regression, ideally improvement. |
| **Staging Deployment** | Status: Not Started | - [ ] Refactored code validated in staging environment. |
| **Production Deployment** | Status: Not Started | - [ ] Refactored code deployed to production with monitoring. |

---

## Safe Refactoring Workflow

Follow this workflow to ensure safe refactoring with no functionality broken. Each step must pass before proceeding.

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Establish Test Safety Net** | Status: Not Started | - [ ] Comprehensive tests exist covering current behavior. |
| **2. Run Baseline Tests** | Status: Not Started | - [ ] All tests pass before any refactoring begins. |
| **3. Capture Baseline Metrics** | Status: Not Started | - [ ] Baseline metrics captured for comparison. |
| **4. Make Smallest Refactor** | Status: Not Started | - [ ] Smallest possible refactoring change made. |
| **5. Run Tests (Iteration)** | Status: Not Started | - [ ] All tests pass after refactoring change. |
| **6. Commit Incremental Change** | Status: Not Started | - [ ] Incremental change committed (enables easy rollback). |
| **7. Repeat Steps 4-6** | Status: Not Started | - [ ] All incremental refactoring steps completed with passing tests. |
| **8. Update Documentation** | Status: Not Started | - [ ] All documentation updated (docstrings, README, comments, architecture docs). |
| **9. Style & Linting Check** | Status: Not Started | - [ ] Code passes linting, type checking, and style guide validation. |
| **10. Code Review** | Status: Not Started | - [ ] Changes reviewed for correctness and maintainability. |
| **11. Performance Validation** | Status: Not Started | - [ ] Performance validated - no regression detected. |
| **12. Deploy to Staging** | Status: Not Started | - [ ] Refactored code validated in staging environment. |
| **13. Production Deployment** | Status: Not Started | - [ ] Gradual production rollout with monitoring. |

#### Refactoring Implementation Notes

> Document refactoring techniques used, design patterns introduced, and complexity improvements.

**Refactoring Techniques Applied:**
* Extract Method: Move _coerce_types logic to standalone function
* Centralize Utility: Create reusable coerce_to_schema in core.validation
* Improve Error Handling: Add field path context to ValidationError messages

**Design Patterns Introduced:**
* Utility Pattern: Centralized coercion function used by multiple domains
* Fail-Fast Pattern: Raise exceptions immediately on coercion failure

**Code Quality Improvements:**
* DRY Principle: Single implementation replaces potential duplication across 4 call sites
* Testability: Isolated function easier to test comprehensively
* Maintainability: Single location for type coercion logic
* Error Messages: Field path context helps debug recipe authoring issues

**Before/After Comparison:**
```python
# Before: Emergency fix in storage.update (storage/links.py:718-780)
def _coerce_types(self, data: Any, schema: Dict[str, Any]) -> Any:
    """Coerce string values to schema-expected types (int, float, bool)."""
    # 63 lines of coercion logic...
    pass

# Usage in storage.update (line 662):
data = self._coerce_types(data, schema)

# After: Centralized utility in core.validation
from core.validation import coerce_to_schema

# Usage across multiple domains:
data = coerce_to_schema(data, schema, context="storage.update")
data = coerce_to_schema(data, schema, context="llm.extract_to_schema")
data = coerce_to_schema(data, schema, context="llm.enrich")
```

**Implementation Details:**
```python
# core/validation.py (new function)
def coerce_to_schema(data: Any, schema: Dict[str, Any], context: str = "validation") -> Any:
    """
    Coerce data values to match JSON schema type expectations.
    
    Handles Jinja2 template rendering producing strings when schemas expect
    typed values (integer, number, boolean). Recursively processes nested
    objects and arrays.
    
    Args:
        data: Data to coerce (typically from template rendering)
        schema: JSON schema defining expected types
        context: Context for error messages (e.g., "storage.update")
    
    Returns:
        Coerced data matching schema types
    
    Raises:
        ValidationError: If coercion fails (e.g., "abc" cannot be coerced to integer)
    
    Example:
        >>> schema = {"type": "object", "properties": {"age": {"type": "integer"}}}
        >>> data = {"age": "25"}  # From Jinja2 template
        >>> coerce_to_schema(data, schema)
        {"age": 25}  # Coerced to integer
    """
    # Implementation from storage/links.py:718-780 with improvements:
    # - Add field path tracking for error messages
    # - Add context parameter for clear error messages
    # - Improve handling of edge cases (null, whitespace, overflow)
    pass
```

---

## Refactoring Validation & Completion

| Task | Detail/Link |
| :--- | :--- |
| **Code Location** | Source: core/domains/storage/links.py:718-780. Destination: core/validation.py |
| **Test Suite** | Status: Not Started. Target: 95% coverage for coerce_to_schema |
| **Baseline Metrics (Before)** | Duplication: 1 implementation (will be 4 when other call sites add it). Testability: Mixed with storage.update logic |
| **Final Metrics (After)** | Duplication: 1 centralized implementation. Testability: Isolated function. Call sites: 4 (storage.update, storage.save, llm.extract, llm.enrich) |
| **Performance Validation** | Target: <1ms overhead for typical recipe data (10-20 fields) |
| **Style & Linting** | Must pass: pylint, mypy, type hints on all parameters |
| **Code Review** | Required: Architecture team approval (ADR-017 compliance) |
| **Documentation Updates** | Required: inline docstrings, plugin-error-handling.md, architecture/error-handling.md |
| **Staging Validation** | Required: Run full recipe test suite in staging environment |
| **Production Deployment** | Strategy: Gradual rollout with monitoring (canary → full deployment) |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Further Refactoring Needed?** | Maybe - consider adding custom coercion rules (e.g., date strings → datetime objects) in future |
| **Design Patterns Reusable?** | Yes - coerce_to_schema pattern can be applied to other template → schema workflows |
| **Test Suite Improvements?** | Yes - add comprehensive edge case tests (null, whitespace, overflow, nested structures) |
| **Documentation Complete?** | Required: Update plugin guide, architecture docs, inline comments |
| **Performance Impact?** | Target: Neutral to slight improvement (<1ms overhead) |
| **Team Knowledge Sharing?** | Required: Present refactoring at team meeting, update ADR-017 with implementation notes |
| **Technical Debt Reduced?** | Yes - removes emergency fix, prevents future duplication across 4 call sites |
| **Code Quality Metrics Improved?** | Yes - DRY principle applied, testability improved, maintainability improved |

### Completion Checklist

* [ ] Comprehensive tests exist before refactoring (95%+ coverage target).
* [ ] All tests pass before refactoring begins (baseline established).
* [ ] Baseline metrics captured (complexity, coverage, performance).
* [ ] Refactoring implemented incrementally (small, safe steps).
* [ ] All tests pass after each refactoring step (continuous validation).
* [ ] Documentation updated (docstrings, README, inline comments, architecture docs).
* [ ] Code passes style guide validation (linting, type checking).
* [ ] Code reviewed by at least 2 team members.
* [ ] No performance regression (ideally improvement).
* [ ] Refactored code validated in staging environment.
* [ ] Production deployment successful with monitoring.
* [ ] Code quality metrics improved (complexity, coverage, maintainability).
* [ ] Rollback plan documented and tested (if high-risk refactor).

---

### Implementation Reference

**Emergency Fix Location (to be migrated):**
File: core/domains/storage/links.py
Lines: 718-780
Method: _coerce_types(data, schema)

**Key Logic to Preserve:**
1. Recursive processing of nested objects and arrays
2. String → integer coercion (try int(), raise ValidationError on failure)
3. String → float coercion (try float(), raise ValidationError on failure)
4. String → boolean coercion ("true"/"false" → True/False, case-insensitive)
5. Null handling (preserve None values)
6. Array element coercion (process each element recursively)

**Improvements to Add:**
1. Field path tracking (e.g., "data.generation_summary.target_syllables")
2. Context parameter for error messages (e.g., "storage.update")
3. Comprehensive error messages (e.g., "Cannot coerce 'abc' to integer at field 'age'")
4. Edge case handling (whitespace, overflow, empty strings)
5. Type hints on all parameters and return values

**Call Sites to Update (in order):**
1. core/domains/storage/links.py:662 (storage.update) - replace _coerce_types
2. core/domains/storage/links.py:XXX (storage.save) - add coerce_to_schema before validation
3. core/domains/llm/links.py:146 (llm.extract_to_schema) - add coerce_to_schema before validation
4. core/domains/llm/links.py:493 (llm.enrich) - add coerce_to_schema before validation

**Related Documentation:**
- ADR-017 Type Handling Architecture (card hgw39p)
- ADR-016 Schema Validation Error Handling (fail-fast architecture)
- docs/guides/plugin-error-handling.md
- docs/architecture/error-handling.md
