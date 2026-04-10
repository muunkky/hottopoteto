Use `.venv/Scripts/python.exe` to run Python commands.

The code review for gitban card **n0mtjg** was REJECTED. The review identified one hard blocker that must be resolved before the card can be approved.

===BEGIN REFACTORING INSTRUCTIONS===

### B1 — requirements.txt strips out critical working dependencies and massively downgrades every pinned version

The diff replaces the prior `requirements.txt` wholesale. Two categories of damage must be corrected:

**1a. Dependencies removed entirely with no justification:**

| Package | Prior version | Evidence it is still needed |
|---|---|---|
| `PyExecJS` | 1.5.1 | `core/executor.py` imports it |
| `click` | 8.3.1 | `core/cli/commands/packages.py`, `plugins/conlang/domains/linguistics/cli.py` |
| `MarkupSafe` | 3.0.3 | Jinja2 transitive hard dependency |
| `langchain-core` | 0.3.28 | Should be re-evaluated explicitly, not silently dropped |
| `langsmith` | 0.2.11 | Same |
| `setuptools` | >=75.0.0 | Build-time dependency |
| `pytest-cov` | 7.0.0 | ADR-0005 and DEVELOPMENT.md both reference `pytest --cov`; coverage gate enforced via pytest.ini depends on this |
| `pytest-mock` | 3.15.1 | The test suite uses `mocker` fixtures; removing this silently breaks test isolation |
| `pytest-asyncio` | 1.3.0 | Present in the venv; may be relied on by future tests per ADR-0005 |

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

**Refactor plan:**

1. Revert `requirements.txt` to the state it was in at `HEAD~1` (the working version).
2. Add only the intended change: insert `mypy>=1.10` in alphabetical order between `lexicon` and `protobuf`.
3. Leave all other packages, their versions, and their presence exactly as before.
4. If some of the removed packages (langchain-core, langsmith, etc.) are genuinely unused, that is a separate card with its own analysis — do not remove them here.

The `mypy.ini` addition and the `DEVELOPMENT.md` update are correct and complete — those changes must be kept.

===END REFACTORING INSTRUCTIONS===

After implementing the fix, submit the updated card for re-review.
