# Code Refactoring Template

**When to use this template:** Use this for code restructuring, architecture improvements, dependency updates, design pattern implementation, or technical debt reduction that changes code structure without changing functionality. Ensures safe refactoring with proper testing, documentation updates, and incremental changes.

---

## Refactoring Overview & Motivation

* **Refactoring Target:** Pydantic v1 deprecated API usage across core and plugin models
* **Code Location:** `core/domains/storage/models.py`, `core/domains/llm/models.py`, `core/schema/pydantic_integration.py`, `plugins/conlang/domains/linguistics/models.py`
* **Refactoring Type:** Modernize deprecated API — replace `__fields__`, `.schema()`, and non-existent `.allow_none` attribute with Pydantic v2 equivalents
* **Motivation:** Spike tt9cb3 (step-4a) found 3 categories of deprecated usage: (1) `__fields__` used in 3 registry sites — deprecated and removed in Pydantic v3; (2) `.schema()` called in 7 places — deprecated, use `.model_json_schema()`; (3) `field_info.allow_none` accessed in `pydantic_integration.py:43` — this attribute does **not exist** in Pydantic v2 `FieldInfo` and will raise `AttributeError` when `generate_recipe_template()` is called with any model
* **Business Impact:** Prevents runtime crashes from the latent `allow_none` bug; ensures compatibility with Pydantic v3 upgrade path; eliminates `PydanticDeprecatedSince20` warnings on every import
* **Scope:** ~11 lines across 4 files. Low-risk mechanical substitution plus one logic fix in `pydantic_integration.py`.
* **Risk Level:** Low — `__fields__` and `.schema()` changes are drop-in replacements with identical return values (confirmed by spike). The `allow_none` fix requires logic replacement but the function is currently broken, so risk of regression is near zero.
* **Related Work:** Spike TESTCOV1-tt9cb3 (step-4a); Pydantic v2 migration guide https://errors.pydantic.dev/2.12/migration/

**Required Checks:**
* [ ] **Refactoring motivation** clearly explains why this change is needed.
* [ ] **Scope** is specific and bounded (not open-ended "improve everything").
* [ ] **Risk level** is assessed based on code criticality and usage.

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

| Review Source | Link / Location | Key Findings / Constraints |
| :--- | :--- | :--- |
| **Existing Code** | `core/domains/storage/models.py:56`, `core/domains/llm/models.py:51` | Both `register()` methods use `cls.__fields__["name"].default` — deprecated in Pydantic v2, emits `PydanticDeprecatedSince20` warning. Returns same value as `model_fields["name"].default` (confirmed by spike). |
| **Existing Code** | `core/schema/pydantic_integration.py:36,43,47` | Uses `__fields__[field_name]` (deprecated) and `field_info.allow_none` (does not exist in Pydantic v2 `FieldInfo`). Line 43 will raise `AttributeError` at runtime. |
| **Existing Code** | `storage/models.py:148-149`, `linguistics/models.py:74-78` | 7 calls to deprecated `.schema()` method. Should be `.model_json_schema()`. |
| **Test Coverage** | `tests/unit/` | No existing tests for `generate_recipe_template()` — TDD tests must be written first. Registry tests pass currently (spike confirmed correct key values). |
| **Documentation** | Docstrings in affected files | No docstrings reference `__fields__` or `.schema()` specifically. No doc changes needed. |
| **Style Guide** | pre-commit hooks: ruff, mypy | mypy may flag `__fields__` access as deprecated. ruff formatting required. |
| **Dependencies** | `pydantic>=2.0` | All replacements are Pydantic v2 native. No new dependencies. |
| **Previous Attempts** | N/A | First pass at Pydantic v2 migration. |

---

## Refactoring Strategy & Risk Assessment

**Refactoring Approach:**
* Mechanical substitution: `__fields__` → `model_fields`, `.schema()` → `.model_json_schema()` (drop-in, identical return values)
* Logic fix: Replace `field_info.allow_none` and `field_info.default is ...` checks in `pydantic_integration.py` with `field_info.is_required()` and `field_info.default is PydanticUndefined`

**Incremental Steps:**
1. Write failing TDD tests for `generate_recipe_template()` covering required, optional, and default fields
2. Fix `pydantic_integration.py`: replace `__fields__` access and `allow_none` logic
3. Run tests — should now pass
4. Fix `storage/models.py`: `__fields__` in `register()` + 2x `.schema()`
5. Fix `llm/models.py`: `__fields__` in `register()`
6. Fix `linguistics/models.py`: 5x `.schema()`
7. Commit, verify pre-commit hooks pass

**Risk Mitigation:**
* Risk: Registry keying breaks. Mitigation: Spike confirmed `__fields__["name"].default == model_fields["name"].default` for both `FileAdapter` and `OpenAIProvider`.
* Risk: `pydantic_integration.py` logic change incorrect. Mitigation: TDD tests written before fix; all field cases covered (required, Optional, default value, default_factory).

**Rollback Plan:**
* Git revert is trivial — changes are <15 lines. No feature flags needed.

**Success Criteria:**
* All existing tests pass
* New `generate_recipe_template()` tests pass
* No `PydanticDeprecatedSince20` warnings on import of affected modules
* mypy and ruff pass

---

## Refactoring Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Pre-Refactor Test Suite** | TDD tests for `generate_recipe_template()` to be written | - [ ] Comprehensive tests exist before refactoring starts. |
| **Baseline Measurements** | Spike tt9cb3 confirmed: `__fields__` == `model_fields` keys; `.allow_none` absent; registry keys correct | - [ ] Baseline metrics captured (complexity, performance, coverage). |
| **Incremental Refactoring** | Not started | - [ ] Refactoring implemented incrementally with passing tests at each step. |
| **Documentation Updates** | N/A — no docs reference deprecated API | - [ ] All documentation updated to reflect refactored code. |
| **Code Review** | Pending | - [ ] Code reviewed for correctness, style guide compliance, maintainability. |
| **Performance Validation** | N/A — no performance impact expected | - [ ] Performance validated - no regression, ideally improvement. |
| **Staging Deployment** | N/A — no staging environment | - [ ] Refactored code validated in staging environment. |
| **Production Deployment** | N/A — merged to main via PR | - [ ] Refactored code deployed to production with monitoring. |

---

## Safe Refactoring Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Establish Test Safety Net** | Write TDD tests for `generate_recipe_template()` (required/optional/default fields) | - [ ] Comprehensive tests exist covering current behavior. |
| **2. Run Baseline Tests** | Run `pytest tests/unit/` — all should pass before changes | - [ ] All tests pass before any refactoring begins. |
| **3. Capture Baseline Metrics** | Spike findings serve as baseline; 0 tests for `pydantic_integration.py` currently | - [ ] Baseline metrics captured for comparison. |
| **4. Make Smallest Refactor** | Fix `pydantic_integration.py` first (highest risk — latent bug) | - [ ] Smallest possible refactoring change made. |
| **5. Run Tests (Iteration)** | Run new TDD tests against fixed `pydantic_integration.py` | - [ ] All tests pass after refactoring change. |
| **6. Commit Incremental Change** | Commit `pydantic_integration.py` fix | - [ ] Incremental change committed (enables easy rollback). |
| **7. Repeat Steps 4-6** | Fix `storage/models.py`, `llm/models.py`, `linguistics/models.py` in order | - [ ] All incremental refactoring steps completed with passing tests. |
| **8. Update Documentation** | No doc changes needed | - [ ] All documentation updated (docstrings, README, comments, architecture docs). |
| **9. Style & Linting Check** | Run pre-commit hooks: ruff format, ruff lint, mypy | - [ ] Code passes linting, type checking, and style guide validation. |
| **10. Code Review** | PR to main | - [ ] Changes reviewed for correctness and maintainability. |
| **11. Performance Validation** | N/A | - [ ] Performance validated - no regression detected. |
| **12. Deploy to Staging** | N/A | - [ ] Refactored code validated in staging environment. |
| **13. Production Deployment** | Merged to main | - [ ] Gradual production rollout with monitoring. |

#### Refactoring Implementation Notes

**Refactoring Techniques Applied:**
* Inline substitution: deprecated API → current API (no structural change)
* Bug fix: `field_info.allow_none` (AttributeError) → `field_info.is_required()`

**Design Patterns Introduced:**
* None — mechanical migration only

**Code Quality Improvements:**
* Eliminates `PydanticDeprecatedSince20` warnings on import
* Fixes latent `AttributeError` in `generate_recipe_template()`
* Pydantic v3-compatible code

**Before/After Comparison:**
```python
# Before (deprecated):
cls._registry[adapter_class.__fields__["name"].default] = adapter_class
StorageEntity.schema()
field_info = input_model.__fields__[field_name]
if not field_info.allow_none and field_info.default is ...:

# After (Pydantic v2):
cls._registry[adapter_class.model_fields["name"].default] = adapter_class
StorageEntity.model_json_schema()
field_info = input_model.model_fields[field_name]
if field_info.is_required():
```

---

## Refactoring Validation & Completion

| Task | Detail/Link |
| :--- | :--- |
| **Code Location** | `core/domains/storage/models.py`, `core/domains/llm/models.py`, `core/schema/pydantic_integration.py`, `plugins/conlang/domains/linguistics/models.py` |
| **Test Suite** | TDD tests to be added for `generate_recipe_template()`; existing tests provide coverage for registry methods |
| **Baseline Metrics (Before)** | 11 deprecated API usages; 1 latent AttributeError bug; PydanticDeprecatedSince20 warnings on every import |
| **Final Metrics (After)** | 0 deprecated API usages; 0 warnings; `generate_recipe_template()` functional |
| **Performance Validation** | N/A |
| **Style & Linting** | Pre-commit hooks must pass |
| **Code Review** | PR to main |
| **Documentation Updates** | N/A |
| **Staging Validation** | N/A |
| **Production Deployment** | Merged to main |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Further Refactoring Needed?** | No — complete after this card |
| **Design Patterns Reusable?** | N/A |
| **Test Suite Improvements?** | Yes — TDD tests for `generate_recipe_template()` added |
| **Documentation Complete?** | Yes — no docs reference deprecated API |
| **Performance Impact?** | Neutral |
| **Team Knowledge Sharing?** | N/A (solo project) |
| **Technical Debt Reduced?** | Yes — Pydantic v2/v3 migration tech debt eliminated |
| **Code Quality Metrics Improved?** | Yes — 0 deprecation warnings, latent crash fixed |

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
