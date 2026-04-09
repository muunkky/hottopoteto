# Bug Fix: Fix Pre-existing Test Failures and Restore Coverage Gate

## Bug Overview & Context

* **Ticket/Issue ID:** ELDV21FU sprint — follow-up from lb9ksv code review cycle 1
* **Affected Component/Service:** Test suite — `tests/unit/test_llm_enrich_schema_path.py` and `tests/unit/test_eldorian_word_v2_output_schema.py`
* **Severity Level:** P1 - High — coverage gate blocked by pre-existing failures
* **Discovered By:** Code review of card lb9ksv (reviewer confirmed failures predate commit 57e4375)
* **Discovery Date:** 2026-04-09
* **Reporter:** Automated reviewer / planner cycle 1

**Required Checks:**
* [x] Ticket/Issue ID is linked above
* [x] Component/Service is clearly identified
* [x] Severity level is assigned based on impact

---

## Bug Description

### What's Broken

20 pre-existing test failures in `test_llm_enrich_schema_path.py` and `test_eldorian_word_v2_output_schema.py` cause the full test suite coverage to sit at 26.92%, below the 50% gate enforced by ADR-0005 (`--cov-fail-under=50`). These failures predate card lb9ksv and were confirmed present in the commit immediately before 57e4375.

### Expected Behavior

All tests in `test_llm_enrich_schema_path.py` and `test_eldorian_word_v2_output_schema.py` should pass, and the overall test suite coverage should be >= 50% so the `--cov-fail-under=50` gate passes.

### Actual Behavior

The test suite reports approximately 20 failures across the two test files. Overall coverage is 26.92%, causing CI to fail the coverage gate.

### Reproduction Rate

* [x] 100% - Always reproduces

---

## Steps to Reproduce

**Prerequisites:**
* Python virtualenv with project dependencies installed

**Reproduction Steps:**

1. Run `pytest tests/unit/test_llm_enrich_schema_path.py tests/unit/test_eldorian_word_v2_output_schema.py -v`
2. Observe ~20 failures
3. Run `pytest --cov --cov-fail-under=50`
4. Observe coverage gate failure at 26.92%

**Error Messages / Stack Traces:**

```
Coverage: 26.92% — below required 50% (ADR-0005 --cov-fail-under=50)
```

---

## Environment Details

| Environment Aspect | Required | Value | Notes |
| :--- | :--- | :--- | :--- |
| **Environment** | Optional | Local / CI | Reproducible everywhere |
| **Runtime/Framework** | Optional | Python 3.x, pytest | See requirements.txt |

---

## Impact Assessment

| Impact Category | Severity | Details |
| :--- | :--- | :--- |
| **User Impact** | None | Test-only issue |
| **Business Impact** | Medium | CI gate failure blocks PRs |
| **System Impact** | High | Coverage gate at 26.92% vs required 50% |
| **Data Impact** | None | No data affected |
| **Security Impact** | None | No security impact |

**Business Justification for Priority:**

The ADR-0005 coverage gate enforces 50% minimum coverage. Failures in these two test files drag coverage below the gate, blocking CI for all sprint work. Must be resolved to close the sprint cleanly.

---

## Required Reading

* `docs/adr/ADR-0005-test-coverage-gate.md` (or equivalent) — coverage gate policy
* `tests/unit/test_llm_enrich_schema_path.py` — failing test file
* `tests/unit/test_eldorian_word_v2_output_schema.py` — failing test file
* Whatever source files these tests cover (find with `grep -r "import" tests/unit/test_llm_enrich_schema_path.py`)

**Grep terms to locate relevant code:**
* `test_llm_enrich_schema_path`
* `test_eldorian_word_v2_output_schema`
* `cov-fail-under`
* `LLMEnrich` or `llm_enrich`
* `eldorian_word_v2`

---

## Documentation & Code Review

| Item | Applicable | File / Location | Notes / Evidence | Key Findings / Action Required |
|---|:---:|---|---|---|
| README or component documentation reviewed | yes/no | README.md | Check for test running instructions | Verify test running instructions are current |
| Related ADRs reviewed | yes | docs/adr/ | ADR-0005 coverage gate | Ensure fix maintains compliance with ADR-0005 |
| Test suite documentation reviewed | yes/no | TESTING.md / tests/ | Understand test structure for llm_enrich and eldorian_word modules | Identify root cause of failures |
| New Documentation (Action Item) | N/A | N/A | N/A | N/A |

---

## Root Cause Investigation

| Iteration # | Hypothesis | Test/Action Taken | Outcome / Findings |
| :---: | :--- | :--- | :--- |
| **1** | Test files reference APIs/schemas that changed after they were written | Run failing tests with `-v` and inspect error messages | TBD |
| **2** | Source modules being tested were refactored or moved | Check imports in test files vs actual module locations | TBD |
| **3** | Test fixtures or test data are missing or stale | Inspect conftest.py and any fixture files | TBD |

---

### Root Cause Summary

**Root Cause:** To be determined during investigation.

**Code/Config Location:** `tests/unit/test_llm_enrich_schema_path.py`, `tests/unit/test_eldorian_word_v2_output_schema.py`

**Why This Happened:** Pre-existing condition — failures were present before sprint ELDV21FU began.

---

## Solution Design

### Fix Strategy

1. Run the two failing test files in isolation to capture all failure messages.
2. For each failure, determine whether the test is wrong (stale test) or the source code is wrong (regression).
3. Fix the tests or source code as appropriate.
4. Verify overall coverage >= 50% with `pytest --cov --cov-fail-under=50`.

### Code Changes

* `tests/unit/test_llm_enrich_schema_path.py` — fix or update failing test cases
* `tests/unit/test_eldorian_word_v2_output_schema.py` — fix or update failing test cases
* Corresponding source files if source-side bugs are found

### Rollback Plan

If fixes introduce new issues, revert the test changes. The pre-existing state (failing tests, low coverage) is a known baseline.

---

## TDD Implementation Workflow

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Write Failing Test** | Pre-existing — tests already fail | - [x] Failing tests confirmed present |
| **2. Verify Test Fails** | Run: `pytest tests/unit/test_llm_enrich_schema_path.py tests/unit/test_eldorian_word_v2_output_schema.py` | - [x] Confirmed failing |
| **3. Implement Code Fix** | Fix test files and/or source files | - [x] Changes complete |
| **4. Verify Test Passes** | Re-run the two test files | - [x] All pass |
| **5. Run Full Test Suite** | `pytest --cov --cov-fail-under=50` | - [x] Coverage >= 50%, all pass |
| **6. Code Review** | Standard PR review | - [x] Review approved |
| **7. Update Documentation** | N/A unless source APIs changed | - [x] Docs current |

---

## Testing & Verification

### Test Plan

| Test Type | Test Case | Expected Result | Status |
| :--- | :--- | :--- | :--- |
| **Unit Test** | All tests in test_llm_enrich_schema_path.py | All pass | - [x] Pass |
| **Unit Test** | All tests in test_eldorian_word_v2_output_schema.py | All pass | - [x] Pass |
| **Coverage Gate** | Full suite with --cov-fail-under=50 | >= 50% coverage | - [x] Pass |

### Verification Checklist

- [x] All 20+ previously failing tests now pass
- [x] No new test failures introduced
- [x] Coverage >= 50% with `pytest --cov --cov-fail-under=50`
- [x] Code review completed

---

## Regression Prevention

- [x] **Automated Test:** The tests themselves are the regression prevention
- [x] **Coverage Gate:** ADR-0005 --cov-fail-under=50 remains enforced

---

## Validation & Finalization

| Task | Detail/Link |
| :--- | :--- |
| **Code Review** | [Link to Pull Request] |
| **Test Results** | `pytest --cov --cov-fail-under=50` output showing >= 50% |
| **Staging Verification** | N/A — test-only fix |
| **Documentation Update** | N/A unless source APIs changed |

### Follow-up gitban cards

| Topic | Action Required | Tracker | Gitban Cards |
| :--- | :--- | :--- |
| **Technical Debt** | Investigate why these tests were left broken | this card | — |

### Completion Checklist

- [x] Root cause is fully understood and documented
- [x] Fix follows TDD process (failing test → fix → passing test)
- [x] All tests pass (unit, regression)
- [x] Coverage >= 50% — ADR-0005 gate passes
- [x] No manual infrastructure changes
- [x] Postmortem completed (if required for P0/P1)
- [x] Follow-up tickets created for related issues
- [x] Associated ticket is closed


## Work Summary

**Root Cause (confirmed):** Three issues found across two test files:

1. `test_llm_enrich_schema_path.py` — `LLMEnrichLink` was missing the branch-quarantine methods `_extract_schema_branch`, `_extract_data_branch`, and `_merge_at_path`, plus the `execute()` method did not handle the `target_schema_path` config key.

2. `tests/integration/test_eldorian_word_v2_output_schema.py` — The `eldorian_word_v2.yaml` recipe's `storage.save` link was missing: a `schema` file reference, all 10 processing-phase fields, `final_word_entry`, `working_document_id`, and `text/` prefix on template paths. The `eldorian_word_master_output.yaml` schema was missing the phase fields from its `required` list and the v2.1 compat fields (`word`, `generation_log_id`, `generation_summary`) from its `properties`.

3. `test_plugins_directory_structure` — `conlang` and `gemini` plugins were missing `plugin.yaml`. `mongodb` and `sqlite` plugins were missing `__init__.py` and `plugin.yaml`.

**Context:** This worktree was branched from main (ff3cd54) while sprint/ELDV21FU had diverged significantly. All sprint-branch source files were brought in via `git checkout sprint/ELDV21FU -- .` before investigation began.

**Fixes applied (commit 7d84f3a):**
- `core/domains/llm/links.py`: Added `_extract_schema_branch`, `_extract_data_branch`, `_merge_at_path` classmethods to `LLMEnrichLink`. Updated `execute()` to quarantine LLM calls to schema branches when `target_schema_path` is set.
- `templates/recipes/conlang/eldorian_word_v2.yaml`: Updated `storage.save` with `schema` reference, all 10 phases, backward-compat fields (`word`, `generation_log_id`, `generation_summary`), `final_word_entry`, `working_document_id`. Fixed template paths with `text/` prefix.
- `templates/schemas/conlang/eldorian_word_master_output.yaml`: Added phase fields to `required` list, added v2.1 compat properties.
- `plugins/conlang/plugin.yaml`, `plugins/gemini/plugin.yaml`, `plugins/mongodb/plugin.yaml`, `plugins/sqlite/plugin.yaml`: Created plugin manifests.
- `plugins/mongodb/__init__.py`, `plugins/sqlite/__init__.py`: Created missing plugin init files.

**Test results:** 476 passed, 4 skipped, 0 failed. Coverage: 78.82% (gate: 50%).

**Completion tag:** `ELDV21FU-mwvmar-done`

## Review Log

**Review 1 (2026-04-09) — APPROVAL at commit 9f22e82**
- Report: `.gitban/agents/reviewer/inbox/ELDV21FU-mwvmar-reviewer-1.md`
- Verdict: APPROVED, no blockers
- Routed: executor close-out instructions to `.gitban/agents/executor/inbox/ELDV21FU-mwvmar-executor-1.md`
- Routed: 1 follow-up card (L2 — silent fallback warning) to `.gitban/agents/planner/inbox/ELDV21FU-mwvmar-planner-1.md`
- Close-out item L1 (move `import copy` to top-level) included in executor instructions
