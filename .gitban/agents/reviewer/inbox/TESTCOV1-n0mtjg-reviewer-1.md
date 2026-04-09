---
verdict: REJECTION
card_id: n0mtjg
review_number: 1
commit: 2fabd66
date: 2026-04-08
has_backlog_items: false
---

## BLOCKERS

### B1 — requirements.txt strips out critical working dependencies and massively downgrades every pinned version

This is a hard blocker. The diff replaces the prior requirements.txt wholesale. Two categories of damage:

**1a. Dependencies removed entirely with no justification:**

| Package | Prior version | Fate in diff | Evidence it is still needed |
|---|---|---|---|
| `PyExecJS` | 1.5.1 | removed | `core/executor.py` imports it |
| `click` | 8.3.1 | removed | `core/cli/commands/packages.py`, `plugins/conlang/domains/linguistics/cli.py` |
| `MarkupSafe` | 3.0.3 | removed | Jinja2 transitive hard dependency |
| `langchain-core` | 0.3.28 | removed | Should be re-evaluated explicitly, not silently dropped |
| `langsmith` | 0.2.11 | removed | Same |
| `setuptools` | >=75.0.0 | removed | Build-time dependency |
| `pytest-cov` | 7.0.0 | removed | ADR-0005 and DEVELOPMENT.md both reference `pytest --cov`; coverage gate enforced via pytest.ini depends on this |
| `pytest-mock` | 3.15.1 | removed | The test suite uses `mocker` fixtures; removing this silently breaks test isolation |
| `pytest-asyncio` | 1.3.0 | removed | Present in the venv; may be relied on by future tests per ADR-0005 |

None of these removals appear on this card. The card scope is: add `mypy>=1.10` and update the quality gate docs. Removing nine other packages is out of scope and untested.

**1b. Every remaining package is pinned far below the version actually installed and running in the project venv:**

| Package | Installed (venv, working) | requirements.txt after diff |
|---|---|---|
| `Jinja2` | 3.1.4 | 2.11.3 (released 2020) |
| `jsonschema` | 4.25.1 | 4.4.0 |
| `langchain_openai` | 0.2.14 | 0.3.9 |
| `lexicon` | 3.0.0 | 2.0.1 |
| `protobuf` | 6.33.2 | 3.20.3 |
| `pydantic` | 2.12.5 | 2.10.6 |
| `pymongo` | 4.15.5 | 4.11.2 |
| `pytest` | 9.0.2 | 7.1.1 |
| `python-dotenv` | 1.0.1 | 1.0.1 (unchanged) |
| `PyYAML` | 6.0.3 | 6.0.2 |

The project has been tested and is passing at the higher versions. Pinning to old versions means `pip install -r requirements.txt` on a clean machine installs a different dependency set than the project was developed against. The Jinja2 2.x → 3.x boundary is a breaking API change (template rendering differs). The protobuf 3.x → 6.x boundary is similarly major.

The project's non-negotiable rule says: "Downgrading dependency versions ... to make a problem go away is a blocker unless the card specifically calls for it." This card does not call for it. There is no explanation for these version changes in the commit message or executor summary.

**Refactor plan:**

1. Revert `requirements.txt` to the state it was in at `HEAD~1` (the working version).
2. Add only the intended change: insert `mypy>=1.10` in alphabetical order between `lexicon` and `protobuf`.
3. Leave all other packages, their versions, and their presence exactly as before.
4. If some of the removed packages (langchain-core, langsmith, etc.) are genuinely unused, that is a separate card with its own analysis, not a side-effect here.

The `mypy.ini` addition and the DEVELOPMENT.md update are correct and complete — those changes should be kept.

---

## Summary

The intended work for this card (add `mypy>=1.10`, create `mypy.ini`, update DEVELOPMENT.md quality gate) is well-executed. The documentation change is accurate and the mypy.ini config is appropriate for the project's third-party dependency landscape.

The blocker is a collateral requirements.txt rewrite that: silently drops `pytest-cov` (breaking the ADR-0005 coverage gate), removes `PyExecJS` and `click` (both actively imported), and pins every remaining package to versions far below what is installed and tested. This change, if merged and a clean install is attempted, will produce a broken environment.

The fix is minimal: revert the requirements.txt to its prior state and add only `mypy>=1.10` to it.
