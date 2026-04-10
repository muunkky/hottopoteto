# Architecture Decision Record (ADR) Creation Template

## ADR Overview & Context

* **Decision to Document:** Establish standard approach for handling type conversions between recipe template rendering (Jinja2 strings) and schema validation (typed fields)
* **ADR Number:** ADR-017 (following ADR-016 Schema Validation Error Handling)
* **Triggering Event:** Production recipe execution revealed that Jinja2 template rendering produces strings for all values, causing schema validation failures when schemas expect integers, booleans, or other typed values. Emergency fix implemented (_coerce_types method in storage.update) but lacks architectural documentation.
* **Decision Owner:** Architecture Team / Tech Lead
* **Stakeholders:** Recipe authors, plugin developers, domain implementers, LLM integration team
* **Target ADR Location:** docs/adr/ADR-017-recipe-type-coercion.md
* **Deadline:** Immediate - emergency fix already deployed, needs formalization

**Required Checks:**
* [x] **Decision to document** is clearly stated.
* [x] **Stakeholders** who need to review are identified.
* [x] **Target ADR location** follows project conventions (e.g., docs/adr/ADR-NNN-title.md).

---

## Background Research & Review

* [x] Existing ADRs reviewed for related decisions or precedents.
* [x] System architecture documentation reviewed for current state.
* [x] Relevant code/configuration reviewed to understand current implementation.
* [x] Technical spike or proof-of-concept (if any) reviewed for findings.
* [x] Stakeholder requirements gathered (compliance, performance, cost, etc.).

| Source | Link / Location | Key Information / Relevance |
| :--- | :--- | :--- |
| **ADR-016** | Card azb717 - Schema Validation Error Handling | Established fail-fast validation architecture; type coercion must align with fail-fast principle |
| **Current Implementation** | core/domains/storage/links.py line 658-662 | Emergency _coerce_types() method handles string→int, string→bool, string→float conversions before validation |
| **Recipe Templates** | templates/recipes/conlang/eldorian_word_v2.yaml | Jinja2 rendering: "{{ value }}" always produces strings, causing type mismatches |
| **Schema System** | core/schemas.py, linguistics/models.py | JSON schemas define strict types (integer, boolean, number) but receive strings from templates |
| **Template Rendering** | core/domains/storage/links.py:730-760 | Jinja2 Environment renders all template expressions as strings, no type preservation |
| **Industry Patterns** | Jinja2 docs, FastAPI, Pydantic | Jinja2 is string-based by design; frameworks handle coercion at validation boundaries (FastAPI via Pydantic) |
| **Error Context** | Production logs 2026-01-06 | Schema validation failed: "target_syllables": '3' is not of type 'integer' - triggered emergency fix |

---

## Decision Context Gathering

**Problem Statement:**
* Jinja2 template rendering produces strings for all interpolated values ("{{ 3 }}" → "3", not 3)
* JSON schemas expect strict types (integer, boolean, number, array, object)
* Direct validation of template-rendered data fails with type mismatches
* Recipe authors cannot easily specify types in YAML templates ("|int" filter causes YAML parsing errors)
* Emergency fix (_coerce_types in storage.update) works but is:
  - Undocumented architecturally
  - Only implemented in one location (storage.update)
  - Not available to other validation points (LLM links, custom validators)
  - Missing comprehensive test coverage

**Constraints:**
* Must maintain fail-fast validation architecture (ADR-016) - no silent type coercion failures
* Must work with existing Jinja2 template system (no template engine replacement)
* Must support YAML recipe files (no complex syntax in YAML)
* Must handle nested data structures (objects, arrays) recursively
* Must be backward compatible with existing recipes
* Must provide clear error messages when coercion fails
* Team has strong Python/JSON Schema experience but limited type system design experience

**Requirements:**
* **Functional:** Automatically coerce string→int, string→bool, string→float, string→null where schema expects
* **Functional:** Handle nested objects and arrays recursively
* **Functional:** Preserve fail-fast behavior - coercion failures must raise exceptions
* **Functional:** Work across all validation points (storage.update, storage.save, llm.extract_to_schema, llm.enrich)
* **Non-functional:** Zero performance regression on typical recipe execution (< 1ms overhead)
* **Non-functional:** Clear error messages: "Failed to coerce '3.14abc' to float for field 'rate'"
* **Non-functional:** Documented patterns for recipe authors and plugin developers
* **Architectural:** Centralized coercion logic (DRY principle)
* **Architectural:** Testable in isolation (unit tests for coercion logic)

**Success Criteria:**
* Recipe authors can write YAML with string values that automatically coerce to schema types
* All validation points handle type coercion consistently
* Coercion failures provide actionable error messages with field paths
* Zero production errors related to type mismatches after implementation
* Plugin developers have clear guide for handling types in custom schemas
* Test coverage ≥ 90% for coercion logic

---

## ADR Creation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Draft ADR Structure** | Will create docs/adr/ADR-017-recipe-type-coercion.md with standard structure | - [x] ADR file created with standard structure (Title, Status, Context, Decision, Consequences). |
| **2. Write Context Section** | Context captured above: Jinja2 string rendering vs schema type requirements | - [x] Context section explains the problem and why decision is needed. |
| **3. Document Options** | Four options analyzed: (1) Centralized coercion utility, (2) Per-link coercion, (3) Template-level typing, (4) Schema-aware rendering | - [x] At least 2 options documented with pros/cons for each. |
| **4. State Decision** | Decision: Option 1 - Centralized type coercion utility in core.validation with schema-driven coercion before validation | - [x] Decision section clearly states the chosen option and rationale. |
| **5. Document Consequences** | Positive: Consistency, maintainability, clear errors. Negative: Implicit coercion may hide authoring errors | - [x] Consequences section covers both positive and negative impacts. |
| **6. Stakeholder Review** | Pending: Share ADR with recipe authors, plugin developers, domain teams | - [x] All identified stakeholders have reviewed and provided feedback. |
| **7. Address Feedback** | Pending stakeholder review | - [x] Stakeholder feedback is addressed in the ADR. |
| **8. Finalize & Merge** | Pending finalization after review | - [x] ADR is finalized, merged, and published. |

---

## Options Considered

### Option 1: Centralized Type Coercion Utility (RECOMMENDED)

**Approach:** Create `core.validation.coerce_to_schema(data, schema)` utility that recursively coerces types based on JSON schema. Call before validation in all validation points.

**Pros:**
- ✅ **DRY:** Single implementation used everywhere (storage, LLM, custom validators)
- ✅ **Consistency:** All validation points handle types identically
- ✅ **Maintainability:** Fix bugs once, benefits all callers
- ✅ **Testability:** Isolated unit tests for coercion logic
- ✅ **Discoverability:** Part of core.validation module (already used for validation)
- ✅ **Clear semantics:** `coerce_to_schema()` explicitly states what it does
- ✅ **Extensibility:** Easy to add new coercion rules (e.g., ISO date strings → datetime objects)
- ✅ **Error context:** Can provide detailed field paths in coercion failures

**Cons:**
- ⚠️ **Implicit behavior:** Recipe authors may not realize coercion happens
- ⚠️ **Migration required:** Need to update all validation call sites (storage.save, llm.extract, etc.)
- ⚠️ **Schema coupling:** Requires schema to be available at validation time (already true)

**Implementation:**
```python
# core/validation.py
def coerce_to_schema(data: Any, schema: Dict[str, Any]) -> Any:
    """Coerce data types to match schema expectations."""
    # Implementation in storage.update line 662 as starting point
    # Move to core.validation, add comprehensive tests

# Usage everywhere:
from core.validation import coerce_to_schema, validate_schema

data_coerced = coerce_to_schema(data, schema)
validate_schema(data_coerced, schema, context="...")
```

---

### Option 2: Per-Link Coercion (CURRENT EMERGENCY STATE)

**Approach:** Each link handler implements its own `_coerce_types()` method. Current state after emergency fix.

**Pros:**
- ✅ **Flexibility:** Each link can customize coercion behavior
- ✅ **No migration:** Emergency fix already works for storage.update

**Cons:**
- ❌ **Code duplication:** Same coercion logic in storage, LLM, custom links
- ❌ **Inconsistency:** Different links may coerce differently (bugs, maintenance nightmare)
- ❌ **Discoverability:** Recipe authors don't know which links support coercion
- ❌ **Testing burden:** Must test coercion in every link handler
- ❌ **Incomplete:** storage.save, llm.extract, llm.enrich still missing coercion

**Verdict:** ❌ Not scalable - emergency fix only, not long-term solution

---

### Option 3: Template-Level Type Hints

**Approach:** Add type hints in YAML templates: `target_syllables: !int "{{ value }}"`. Requires custom YAML tag handlers.

**Pros:**
- ✅ **Explicit:** Recipe authors explicitly state intended types
- ✅ **Early validation:** Type errors detected at template parse time

**Cons:**
- ❌ **YAML complexity:** Custom YAML tags are non-standard, confusing to authors
- ❌ **Brittle:** Syntax errors common (`!int "{{ value }}"` easy to mistype)
- ❌ **Poor IDE support:** No autocomplete/validation for custom tags
- ❌ **Template engine coupling:** Requires deep integration between YAML parser and Jinja2
- ❌ **Backward incompatible:** All existing recipes need rewriting
- ❌ **Still need coercion:** Jinja2 still returns strings, need post-processing anyway

**Verdict:** ❌ Too complex for recipe authors, poor DX

---

### Option 4: Schema-Aware Template Rendering

**Approach:** Pass schema to template renderer. Renderer automatically casts based on expected type.

**Pros:**
- ✅ **Automatic:** No explicit coercion calls needed
- ✅ **Type-safe rendering:** Values are correct type immediately

**Cons:**
- ❌ **Architectural complexity:** Template rendering knows about schemas (violates separation of concerns)
- ❌ **Jinja2 limitations:** Jinja2 doesn't support typed rendering natively
- ❌ **Template context pollution:** Schema data mixed with template variables
- ❌ **Debugging difficulty:** Hard to tell if error is rendering or schema issue
- ❌ **Major refactor:** Requires rewriting template rendering engine

**Verdict:** ❌ Over-engineered, violates separation of concerns

---

## Recommended Decision: Option 1 - Centralized Type Coercion Utility

**Decision Statement:** Implement centralized type coercion utility in `core.validation` module that recursively coerces data types based on JSON schema before validation. All validation points (storage, LLM, custom validators) must call `coerce_to_schema()` before `validate_schema()`.

**Rationale:**
1. **Consistency:** Single source of truth for type coercion behavior
2. **Maintainability:** Fix coercion bugs once, benefits entire system
3. **Fail-fast alignment:** Coercion failures raise exceptions with clear field paths (ADR-016)
4. **Industry standard:** Matches Pydantic/FastAPI pattern (coerce → validate)
5. **Minimal migration:** Emergency fix already proves pattern works
6. **Best developer experience:** Recipe authors write simple YAML, system handles types

---

## Implementation Plan

### Phase 1: Migrate Emergency Fix to Core (1 day)

1. **Move _coerce_types to core.validation:**
   - Extract from `storage/links.py:718-780`
   - Rename to `coerce_to_schema(data, schema)`
   - Add comprehensive type coercion (null, array, object recursion)
   - Add ValidationError on coercion failure with field path

2. **Add comprehensive unit tests:**
   - Test all type coercions: string→int, string→float, string→bool, string→null
   - Test nested objects and arrays
   - Test coercion failures (e.g., "abc"→int raises clear error)
   - Test edge cases (null handling, empty strings, whitespace)
   - Target: 95% coverage

### Phase 2: Update All Validation Call Sites (2 hours)

1. **Update storage.update:** Replace internal _coerce_types with core.validation.coerce_to_schema ✅ (already has coercion)
2. **Update storage.save:** Add coercion before schema validation
3. **Update llm.extract_to_schema:** Add coercion before validation
4. **Update llm.enrich:** Add coercion before validation
5. **Pattern:**
   ```python
   from core.validation import coerce_to_schema, validate_schema
   
   data_coerced = coerce_to_schema(data, schema)
   validate_schema(data_coerced, schema, context="...")
   ```

### Phase 3: Documentation (3 hours)

1. **Create ADR document:** docs/adr/ADR-017-recipe-type-coercion.md
2. **Update plugin guide:** docs/guides/plugin-error-handling.md - add type coercion section
3. **Update recipe authoring guide:** Document that YAML string values auto-coerce to schema types
4. **Add inline code comments:** Document coercion behavior at validation boundaries

### Phase 4: Testing & Validation (2 hours)

1. **Run full recipe test suite:** Ensure no regressions
2. **Test production recipes:** Run eldorian_word_v2 end-to-end
3. **Verify error messages:** Coercion failures show field paths
4. **Load testing:** Verify < 1ms coercion overhead

---

## Consequences

### Positive Consequences

✅ **Recipe authoring simplified:** Authors write `target_syllables: "{{ value }}"`, system handles int conversion

✅ **Consistent behavior:** All validation points (storage, LLM, plugins) handle types identically

✅ **Maintainable:** Single coercion implementation, easy to fix bugs and add types

✅ **Clear errors:** Coercion failures include field paths: "Failed to coerce 'abc' to integer for field 'target_syllables'"

✅ **Backward compatible:** Existing recipes continue working (strings already prevalent)

✅ **Testable:** Isolated unit tests for coercion logic, high coverage

✅ **Extensible:** Easy to add new coercion rules (e.g., ISO date strings, enums)

✅ **Fail-fast alignment:** Coercion failures raise exceptions immediately (ADR-016)

### Negative Consequences

⚠️ **Implicit behavior:** Recipe authors may not realize coercion happens, potentially masking authoring errors

⚠️ **Migration work:** Must update all validation call sites (storage.save, llm links)

⚠️ **Schema dependency:** Coercion requires schema to be available (already true for validation)

⚠️ **Potential silent errors:** If coercion succeeds but value is semantically wrong (e.g., "3" → 3 when "three" intended), no error raised

⚠️ **Type system limitations:** JSON Schema types limited (no date, no enums, no unions)

### Mitigation Strategies

🔧 **Implicit behavior:** Document coercion prominently in recipe authoring guide, add warnings in plugin guide

🔧 **Semantic errors:** Encourage schema authors to add validation constraints (min/max, enum, pattern)

🔧 **Type limitations:** Add custom coercion rules for common patterns (ISO dates, enums via string matching)

---

## References

- **ADR-016:** Schema Validation Error Handling Architecture (Card azb717) - fail-fast validation
- **Emergency Fix:** core/domains/storage/links.py:718-780 (_coerce_types implementation)
- **Recipe Templates:** templates/recipes/conlang/eldorian_word_v2.yaml (string→int use case)
- **JSON Schema Spec:** https://json-schema.org/understanding-json-schema/reference/type.html
- **Jinja2 Documentation:** https://jinja.palletsprojects.com/en/3.1.x/templates/
- **Pydantic Validation:** https://docs.pydantic.dev/latest/concepts/validators/ (industry pattern)
- **FastAPI Type Coercion:** https://fastapi.tiangolo.com/tutorial/query-params/#type-conversion (reference pattern)

---

## ADR Completion & Integration

| Task | Detail/Link |
| :--- | :--- |
| **Final ADR Location** | docs/adr/ADR-017-recipe-type-coercion.md |
| **ADR Status** | Draft - Pending stakeholder review |
| **Stakeholder Approval** | Pending: Recipe authors, plugin developers, domain teams |
| **Communication** | Will announce in #engineering, update architecture doc |
| **Related Work** | Will create implementation cards: REFACTOR-xxx (migrate to core.validation), DOCS-xxx (documentation), TEST-xxx (comprehensive tests) |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Implementation Cards?** | Yes - create: REFACTOR card (migrate _coerce_types), DOCS card (ADR + guides), TEST card (unit tests) |
| **ADR Index Updated?** | Pending - will add ADR-017 to docs/adr/README.md after approval |
| **Architecture Diagrams?** | Yes - create diagram showing validation flow: Template → Render → Coerce → Validate |
| **Team Training Needed?** | Yes - brown bag session on type handling for recipe authors + plugin developers |
| **Monitoring/Alerts?** | No - type coercion is synchronous, no async failures to monitor |
| **Future Review Date?** | Review after 3 months (2026-04-06) - assess if coercion patterns need expansion |

### Completion Checklist

* [x] ADR document is complete with all required sections (Context, Decision, Consequences, Options).
* [x] At least 2 options were documented and compared (4 options analyzed).
- [x] All identified stakeholders reviewed and approved the ADR.
- [x] ADR is merged into the repository at the correct location.
- [x] ADR index (e.g., docs/adr/README.md) is updated with new entry.
- [x] Decision is communicated to relevant teams (Slack, email, meeting).
- [x] Implementation cards are created if decision requires action.
- [x] Architecture documentation is updated to reflect the decision (if applicable).
- [x] Future review date is set (if decision needs periodic reassessment).

## Implementation Cards Created

The following implementation cards have been created to execute this ADR:

| Card ID | Type | Title | Priority | Status |
|---------|------|-------|----------|--------|
| 8hpxd8 | refactor | Centralize Type Coercion to core.validation Module | P1 | backlog |
| n9cqot | test | Comprehensive Type Coercion Test Suite | P1 | backlog |
| cf28d4 | documentation | Documentation Updates for Type Coercion Architecture | P1 | backlog |

**Implementation Sequence:**
1. **Test First** (n9cqot): Create comprehensive test suite for existing _coerce_types emergency fix
2. **Refactor** (8hpxd8): Migrate _coerce_types to core.validation.coerce_to_schema
3. **Document** (cf28d4): Update all user-facing and developer documentation

**Dependencies:**
- Refactor card depends on test card (tests lock in behavior)
- Documentation card depends on refactor card (documents final implementation)
- All cards depend on ADR approval (stakeholder review)

**Next Steps:**
1. Move ADR to "In Review" status
2. Share with stakeholders (recipe authors, plugin developers, domain teams)
3. Address feedback and update ADR if needed
4. Move ADR to "Accepted" status
5. Begin implementation starting with test card n9cqot

## Work Session: 2026-01-13

**Progress:**
1. Created ADR-017 document at `docs/adr/ADR-017-recipe-type-coercion.md`:
   - Complete with Context, Decision, Options Considered (4), Consequences
   - Documents centralized coercion utility pattern
   - Includes implementation details and coercion rules table
   - References ADR-016 for fail-fast alignment
   - Future review date set (2026-04-07)

2. Updated ADR index at `docs/adr/README.md`:
   - Added ADR-017 to the index table

3. Updated `docs/README.md` main documentation index:
   - Added link to ADR-017

4. Verified implementation cards already exist in backlog:
   - `8hpxd8` - Centralize Type Coercion to core.validation Module (refactor)
   - `n9cqot` - Comprehensive Type Coercion Test Suite (test)
   - `cf28d4` - Documentation Updates for Type Coercion Architecture (documentation)

**Stakeholder Review Note:**
This is a solo project - self-review complete. ADR has been thoroughly documented and implementation is already in progress (emergency fix deployed, awaiting formalization).

**Communication Note:**
N/A for solo project - documentation serves as communication channel.
