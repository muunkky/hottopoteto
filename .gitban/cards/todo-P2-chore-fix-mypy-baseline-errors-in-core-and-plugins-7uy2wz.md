# fix mypy baseline errors in core and plugins

## Task Overview

* **Task Description:** Fix all 167 mypy type errors found in `core/` and `plugins/` on the first baseline run after mypy was installed (TESTCOV1 card n0mtjg).
* **Motivation:** The mypy quality gate was added in TESTCOV1 but cannot pass (exits non-zero) due to pre-existing type annotation gaps. Until these are fixed, the gate provides no enforcement value.
* **Scope:** `core/executor.py`, `core/registry.py`, `core/domains/storage/`, `core/domains/llm/`, `core/schema/`, `plugins/conlang/`, `plugins/sqlite/`, `plugins/mongodb/`, `plugins/gemini/`, `plugins/__init__.py`
* **Related Work:** Follow-up from TESTCOV1 card n0mtjg (mypy install and quality gate)
* **Estimated Effort:** 1-2 days

**Required Checks:**
* [x] **Task description** clearly states what needs to be done.
* [x] **Motivation** explains why this work is necessary.
* [x] **Scope** defines what will be changed.

---

## Work Log

| Step | Status/Details | Universal Check |
| :---: | :--- | :---: |
| **1. Review Current State** | `python -m mypy core/ plugins/` → 167 errors in 18 files (mypy 1.20.0, `explicit_package_bases=True`, `ignore_missing_imports=True`). Error breakdown documented in Work Notes. | - [x] Current state is understood and documented. |
| **2. Plan Changes** | Fix by file, heaviest-first: executor.py (~94), conlang models (~12), schema/ (~13), storage/ (~12), registry (~4), plugins (~11), other (~21) | - [ ] Change plan is documented. |
| **3. Make Changes** | Not started | - [ ] Changes are implemented. |
| **4. Test/Verify** | Not started | - [ ] Changes are tested/verified. |
| **5. Update Documentation** | N/A — no docs changes expected | - [ ] Documentation is updated (if applicable). |
| **6. Review/Merge** | Not started | - [ ] Changes are reviewed and merged. |

#### Work Notes

**Error distribution by file (from baseline run 2026-04-08):**

| File | ~Count | Dominant Categories |
| :--- | :---: | :--- |
| `core/executor.py` | 94 | `[attr-defined]` (52), `[assignment]` (17), `[arg-type]` (15), `[call-arg]` (7) |
| `plugins/conlang/domains/linguistics/models.py` | 12 | `[assignment]` — Optional field overrides non-Optional base |
| `core/schema/translator.py` | 8 | `[union-attr]`, `[arg-type]` |
| `core/domains/storage/functions.py` | 7 | `[assignment]`, `[no-redef]` |
| `core/schema/pydantic_integration.py` | 5 | `[assignment]`, implicit Optional |
| `core/domains/storage/links.py` | 5 | `[arg-type]` |
| `core/domains/llm/links.py` | 5 | `[return-value]` |
| `core/registry.py` | 4 | `[var-annotated]` |
| `plugins/mongodb/links.py` | 6 | `[dict-item]`, `[index]`, `[var-annotated]` |
| `plugins/sqlite/links.py` | 2 | `[assignment]` |
| Other files | ~13 | Mixed |

Notable: `core/executor.py` has 52 `[attr-defined]` errors — many are `Logger.trace` calls (logger lacks trace level) and `ChatOpenAI` called with deprecated kwargs (`model_name=`, `max_tokens=`).

**Commands:**
```bash
python -m mypy core/ plugins/
```

---

## Completion & Follow-up

| Task | Detail/Link |
| :--- | :--- |
| **Changes Made** | Not yet started |
| **Files Modified** | TBD |
| **Pull Request** | TBD |
| **Testing Performed** | TBD |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Related Chores Identified?** | Consider enabling `--strict` mode once baseline passes (separate follow-up card) |
| **Documentation Updates Needed?** | No |
| **Follow-up Work Required?** | Strict mode follow-up after this card closes |
| **Process Improvements?** | N/A |
| **Automation Opportunities?** | Could wire mypy into pre-commit hook once baseline is clean |

### Completion Checklist

* [ ] All planned changes are implemented.
* [ ] Changes are tested/verified (tests pass, configs work, etc.).
* [ ] Documentation is updated (CHANGELOG, README, etc.) if applicable.
* [ ] Changes are reviewed (self-review or peer review as appropriate).
* [ ] Pull request is merged or changes are committed.
* [ ] Follow-up tickets created for related work identified during execution.
