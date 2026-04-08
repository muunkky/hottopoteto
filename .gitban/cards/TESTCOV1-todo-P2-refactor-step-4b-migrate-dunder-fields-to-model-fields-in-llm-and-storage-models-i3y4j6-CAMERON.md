# Code Refactoring Template

**When to use this template:** Use this for code restructuring, architecture improvements, dependency updates, design pattern implementation, or technical debt reduction that changes code structure without changing functionality.

---

## Refactoring Overview & Motivation

* **Refactoring Target:** All uses of `__fields__` (Pydantic v1 API) in LLM domain models (`core/domains/llm/models.py`) and storage domain models (`core/domains/storage/models.py`), plus any callers in `core/` and `plugins/`.
* **Code Location:** `core/domains/llm/models.py`, `core/domains/storage/models.py`, `core/links/`, `plugins/`
* **Refactoring Type:** Modernize dependencies — replace deprecated Pydantic v1 `__fields__` introspection with Pydantic v2 `model_fields` API.
* **Motivation:** Pydantic v2 deprecated `__fields__` (it still works via shim but emits `DeprecationWarning`). Using `model_fields` is the correct v2 API and avoids silent breakage when the shim is eventually removed. Step-4a spike (tt9cb3) should be completed first to identify all affected sites.
* **Business Impact:** Eliminates deprecation warnings, ensures correct field introspection under Pydantic v2 inheritance, and future-proofs the codebase against Pydantic v3.
* **Scope:** Likely 5–15 occurrences across 4–6 files. Low risk — purely mechanical substitution.
* **Risk Level:** Low — `model_fields` is a direct replacement; no behavior change expected. Existing test suite (323+ tests) provides full safety net.
* **Related Work:** Follows step-4a spike (tt9cb3) which identifies exact affected sites. Part of TESTCOV1 sprint technical debt closeout.

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
| **Existing Code** | `core/domains/llm/models.py`, `core/domains/storage/models.py` | Contains Pydantic model definitions; grep for `__fields__` to find all sites |
| **Test Coverage** | `tests/unit/`, `tests/integration/` | 323+ tests passing — strong safety net for mechanical refactor |
| **Documentation** | Pydantic v2 migration guide | `Model.model_fields` returns `dict[str, FieldInfo]`; replaces `Model.__fields__` |
| **Style Guide** | Project conventions | Use `model_fields` consistently; remove any `__fields__` shim workarounds |
| **Dependencies** | `core/links/`, `plugins/conlang/`, `plugins/gemini/` | Check callers that introspect model fields |
| **Usage Patterns** | grep `__fields__` across repo | Identify all call sites before starting |
| **Previous Attempts** | None | First migration attempt |

---

## Refactoring Strategy & Risk Assessment

**Refactoring Approach:**
* Direct substitution: Replace `Model.__fields__` with `Model.model_fields` at each call site. Adjust any downstream code that relied on `__fields__` returning `ModelField` objects (v1) vs `FieldInfo` objects (v2).

**Incremental Steps:**
1. Complete step-4a spike — get exact list of affected sites.
2. Run baseline tests; confirm all 323+ pass and record coverage %.
3. For each affected site: replace `__fields__` with `model_fields`, run tests after each file.
4. Fix any `ModelField` attribute accesses that differ in `FieldInfo` (e.g., `.outer_type_` → `.annotation`).
5. Run full test suite; confirm no regressions.
6. Run with `-W error::DeprecationWarning` to confirm no Pydantic warnings remain.

**Risk Mitigation:**
* Risk: `FieldInfo` attributes differ from `ModelField` attributes. Mitigation: Review each access site against Pydantic v2 docs before substituting.
* Risk: Third-party plugins using `__fields__`. Mitigation: Grep plugins/ directory before starting.

**Rollback Plan:**
* Git revert is trivial — purely mechanical change with no logic modification.

**Success Criteria:**
* All existing tests pass after migration (323+ tests).
* No `DeprecationWarning` from Pydantic when running with `-W error::DeprecationWarning`.
* No use of `__fields__` remains in `core/` or `plugins/`.

---

## Refactoring Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Pre-Refactor Test Suite** | 323+ tests passing (established in TESTCOV1 sprint) | - [ ] Comprehensive tests exist before refactoring starts. |
| **Baseline Measurements** | [Run test suite, record coverage % and warning count] | - [ ] Baseline metrics captured (complexity, performance, coverage). |
| **Incremental Refactoring** | [Replace __fields__ site by site, test after each file] | - [ ] Refactoring implemented incrementally with passing tests at each step. |
| **Documentation Updates** | [Update any docstrings that reference __fields__] | - [ ] All documentation updated to reflect refactored code. |
| **Code Review** | [Self-review; confirm no ModelField attribute regressions] | - [ ] Code reviewed for correctness, style guide compliance, maintainability. |
| **Performance Validation** | N/A — no performance impact expected | - [ ] Performance validated - no regression, ideally improvement. |
| **Staging Deployment** | N/A — local project | - [ ] Refactored code validated in staging environment. |
| **Production Deployment** | Merge to sprint branch | - [ ] Refactored code deployed to production with monitoring. |

---

## Safe Refactoring Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Establish Test Safety Net** | 323+ tests from TESTCOV1 sprint | - [ ] Comprehensive tests exist covering current behavior. |
| **2. Run Baseline Tests** | [Run pytest, confirm all pass] | - [ ] All tests pass before any refactoring begins. |
| **3. Capture Baseline Metrics** | [Record test count, coverage %, DeprecationWarning count] | - [ ] Baseline metrics captured for comparison. |
| **4. Make Smallest Refactor** | [Replace __fields__ in first affected file] | - [ ] Smallest possible refactoring change made. |
| **5. Run Tests (Iteration)** | [pytest after each file change] | - [ ] All tests pass after refactoring change. |
| **6. Commit Incremental Change** | [Commit per file or per logical group] | - [ ] Incremental change committed (enables easy rollback). |
| **7. Repeat Steps 4-6** | [All sites migrated] | - [ ] All incremental refactoring steps completed with passing tests. |
| **8. Update Documentation** | [Update docstrings referencing __fields__] | - [ ] All documentation updated. |
| **9. Style & Linting Check** | [Run linter, confirm no new warnings] | - [ ] Code passes linting and style guide validation. |
| **10. Code Review** | [Self-review complete] | - [ ] Changes reviewed for correctness and maintainability. |
| **11. Performance Validation** | N/A | - [ ] Performance validated. |
| **12. Deploy to Staging** | N/A | - [ ] Refactored code validated in staging environment. |
| **13. Production Deployment** | Merge to sprint branch | - [ ] Gradual production rollout with monitoring. |

#### Refactoring Implementation Notes

**Refactoring Techniques Applied:**
* Direct API substitution: `Model.__fields__` → `Model.model_fields`
* Attribute mapping: `field.outer_type_` → `field.annotation`, `field.required` → `field.is_required()` (where applicable)

**Design Patterns Introduced:**
* None — purely mechanical modernization.

**Code Quality Improvements:**
* Eliminates Pydantic v2 deprecation warnings.
* Consistent use of v2-native introspection API.

**Before/After Comparison:**
```python
# Before (Pydantic v1 shim, deprecated in v2):
for name, field in MyModel.__fields__.items():
    print(name, field.outer_type_)

# After (Pydantic v2 native):
for name, field_info in MyModel.model_fields.items():
    print(name, field_info.annotation)
```

---

## Refactoring Validation & Completion

| Task | Detail/Link |
| :--- | :--- |
| **Code Location** | `core/domains/llm/models.py`, `core/domains/storage/models.py`, callers in `core/links/` and `plugins/` |
| **Test Suite** | [323+ tests, all passing after migration] |
| **Baseline Metrics (Before)** | [Record before starting] |
| **Final Metrics (After)** | [Record after completing] |
| **Performance Validation** | N/A |
| **Style & Linting** | [Linting passes, no DeprecationWarning] |
| **Code Review** | Self-review |
| **Documentation Updates** | Docstrings updated where needed |
| **Staging Validation** | N/A |
| **Production Deployment** | Merged to sprint branch |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Further Refactoring Needed?** | [TBD — check if any other v1 patterns remain after migration] |
| **Design Patterns Reusable?** | N/A |
| **Test Suite Improvements?** | Already comprehensive |
| **Documentation Complete?** | ADR-0005 covers testing strategy; no new ADR needed for this mechanical change |
| **Performance Impact?** | Neutral expected |
| **Team Knowledge Sharing?** | N/A (solo project) |
| **Technical Debt Reduced?** | Yes — removes Pydantic v1 shim dependency |
| **Code Quality Metrics Improved?** | Yes — zero DeprecationWarnings from Pydantic |

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
