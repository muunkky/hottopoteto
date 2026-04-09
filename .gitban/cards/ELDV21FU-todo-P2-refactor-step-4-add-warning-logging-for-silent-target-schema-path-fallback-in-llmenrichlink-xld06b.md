# Add Warning Logging for Silent target_schema_path Fallback in LLMEnrichLink

## Refactoring Overview & Motivation

* **Refactoring Target:** `LLMEnrichLink.execute()` silent fallback paths when `target_schema_path` resolves to `None`
* **Code Location:** `core/domains/llm/links.py` — `execute()` method, approximately lines 460-461
* **Refactoring Type:** Add observability — warning/error logging for silent fallback code paths
* **Motivation:** When `target_schema_path` resolves to `None`, `_extract_schema_branch` returns `None` and execution silently falls back to the full schema via `or schema`. The quarantine is entirely bypassed without any warning. Similarly, `_extract_data_branch` falls back to `{}` silently. Both fallbacks hide contract violations that should surface during development and debugging.
* **Business Impact:** Silent fallbacks mask bugs in recipe configuration — a misconfigured `target_schema_path` appears to work but skips quarantine entirely, leading to subtle data quality issues that are hard to diagnose.
* **Scope:** ~10-15 lines changed in 1 file (`core/domains/llm/links.py`)
* **Risk Level:** Low — adding logging to existing code paths, no behavioral change
* **Related Work:** Card mwvmar (fix pre-existing test failures), card eqo5ie (add target-schema-path feature). Reviewer finding L2 from mwvmar review cycle 1.

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

| Review Source | Link / Location | Key Findings / Constraints |
| :--- | :--- | :--- |
| **Existing Code** | `core/domains/llm/links.py` lines ~460-461 | `_extract_schema_branch` returns `None` on failure, `_extract_data_branch` returns `{}` — both trigger silent `or` fallbacks |
| **Test Coverage** | `tests/unit/test_llm_enrich_schema_path.py` | Tests exist for the quarantine feature from card mwvmar |
| **Documentation** | Docstrings in `LLMEnrichLink` | Should document the warning behavior after this change |
| **Style Guide** | Project conventions | Use `logger.warning()` consistent with existing logging patterns in the codebase |
| **Dependencies** | `LLMEnrichLink` used by recipe execution pipeline | Adding warnings is additive — no consumer impact |
| **Usage Patterns** | Called during LLM enrichment with `target_schema_path` config | Fallback path only triggered on misconfiguration or `None` resolution |
| **Previous Attempts** | Card mwvmar — reviewer flagged this as L2 finding | First attempt to address this gap |

---

## Refactoring Strategy & Risk Assessment

**Refactoring Approach:**
* Add `logger.warning()` calls in `execute()` when `_extract_schema_branch` returns `None` and when `_extract_data_branch` returns `{}` (or equivalent empty fallback).
* Ensure both fallback paths use consistent handling — either both warn or both raise, so the contract is uniform and easy to reason about.
* Prefer `logger.warning` over `ValueError` since the current behavior (fallback to full schema) is intentional and non-destructive, but should be visible.

**Incremental Steps:**
1. Review `execute()` to identify both fallback sites precisely.
2. Add `logger.warning(...)` at the schema branch fallback with a message including the `target_schema_path` value that failed to resolve.
3. Add `logger.warning(...)` at the data branch fallback with a matching message.
4. Ensure the `logger` is already imported/configured in the module (add if missing).
5. Add or update tests to verify warnings are emitted on fallback.
6. Update docstrings to document the warning behavior.

**Risk Mitigation:**
* Risk: None significant — adding logging only, no behavioral change.
* Mitigation: Run full test suite to confirm no regressions.

**Rollback Plan:**
* Git revert the warning additions. Existing behavior is preserved either way.

**Success Criteria:**
* Both fallback paths in `execute()` emit `logger.warning()` when quarantine is bypassed.
* Warning messages include the `target_schema_path` value for debuggability.
* Both fallback paths use consistent handling (both warn, not one warns and one silently passes).
* All existing tests pass without modification.
* New test(s) verify the warnings are emitted.

---

## Refactoring Phases

| Phase / Task | Status / Link to Artifact or Card | Universal Check |
| :--- | :--- | :---: |
| **Pre-Refactor Test Suite** | Tests exist from card mwvmar | - [ ] Comprehensive tests exist before refactoring starts. |
| **Baseline Measurements** | Coverage at 78.82% from mwvmar | - [ ] Baseline metrics captured (complexity, performance, coverage). |
| **Incremental Refactoring** | Add warning logging to 2 fallback sites | - [ ] Refactoring implemented incrementally with passing tests at each step. |
| **Documentation Updates** | Update docstrings for `execute()` and helpers | - [ ] All documentation updated to reflect refactored code. |
| **Code Review** | Standard review | - [ ] Code reviewed for correctness, style guide compliance, maintainability. |
| **Performance Validation** | N/A — logging only | - [ ] Performance validated - no regression, ideally improvement. |
| **Staging Deployment** | N/A | - [ ] Refactored code validated in staging environment. |
| **Production Deployment** | N/A | - [ ] Refactored code deployed to production with monitoring. |

---

## Safe Refactoring Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Establish Test Safety Net** | Existing tests from mwvmar sprint | - [ ] Comprehensive tests exist covering current behavior. |
| **2. Run Baseline Tests** | Run `pytest --cov --cov-fail-under=50` | - [ ] All tests pass before any refactoring begins. |
| **3. Capture Baseline Metrics** | Coverage: 78.82%, 476 passed, 0 failed | - [ ] Baseline metrics captured for comparison. |
| **4. Make Smallest Refactor** | Add `logger.warning()` to schema fallback path | - [ ] Smallest possible refactoring change made. |
| **5. Run Tests (Iteration)** | Verify all tests still pass | - [ ] All tests pass after refactoring change. |
| **6. Commit Incremental Change** | Commit warning additions | - [ ] Incremental change committed (enables easy rollback). |
| **7. Repeat Steps 4-6** | Add `logger.warning()` to data fallback path, add tests | - [ ] All incremental refactoring steps completed with passing tests. |
| **8. Update Documentation** | Update docstrings | - [ ] All documentation updated (docstrings, README, comments, architecture docs). |
| **9. Style & Linting Check** | Run linting | - [ ] Code passes linting, type checking, and style guide validation. |
| **10. Code Review** | Standard review | - [ ] Changes reviewed for correctness and maintainability. |
| **11. Performance Validation** | N/A — logging only | - [ ] Performance validated - no regression detected. |
| **12. Deploy to Staging** | N/A | - [ ] Refactored code validated in staging environment. |
| **13. Production Deployment** | N/A | - [ ] Gradual production rollout with monitoring. |

#### Refactoring Implementation Notes

> Document refactoring techniques used, design patterns introduced, and complexity improvements.

**Refactoring Techniques Applied:**
* Add observability (warning logging) to silent fallback paths

**Design Patterns Introduced:**
* None — straightforward logging addition

**Code Quality Improvements:**
* Silent failures become observable failures
* Consistent fallback handling across schema and data branch extraction

**Grep terms to locate relevant code:**
* `_extract_schema_branch`
* `_extract_data_branch`
* `target_schema_path`
* `or schema`

---

## Refactoring Validation & Completion

| Task | Detail/Link |
| :--- | :--- |
| **Code Location** | `core/domains/llm/links.py` — `execute()` method |
| **Test Suite** | Existing + new warning-verification tests |
| **Baseline Metrics (Before)** | Coverage: 78.82%, 476 passed |
| **Final Metrics (After)** | TBD |
| **Performance Validation** | N/A — logging only |
| **Style & Linting** | TBD |
| **Code Review** | TBD |
| **Documentation Updates** | Docstrings for `execute()`, `_extract_schema_branch`, `_extract_data_branch` |
| **Staging Validation** | N/A |
| **Production Deployment** | N/A |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Further Refactoring Needed?** | Evaluate whether `_extract_schema_branch` and `_extract_data_branch` should raise instead of return None/{} |
| **Design Patterns Reusable?** | No — specific to this code path |
| **Test Suite Improvements?** | Add tests verifying warnings are emitted |
| **Documentation Complete?** | TBD |
| **Performance Impact?** | None — logging only |
| **Team Knowledge Sharing?** | N/A |
| **Technical Debt Reduced?** | Yes — silent fallback is a known observability gap |
| **Code Quality Metrics Improved?** | Yes — observable failures improve debuggability |

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
