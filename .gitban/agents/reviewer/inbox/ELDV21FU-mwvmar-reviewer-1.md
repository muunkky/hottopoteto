---
verdict: APPROVAL
card_id: mwvmar
review_number: 1
commit: 9f22e82
date: 2026-04-09
has_backlog_items: true
---

## Summary

The diff introduces three classmethods on `LLMEnrichLink` — `_extract_schema_branch`, `_extract_data_branch`, and `_merge_at_path` — and wires the `target_schema_path` config key into `execute()` to quarantine LLM calls to a sub-tree of the document schema. Four plugin manifests and two `__init__.py` files are also added.

The implementation is clean, behaviour-correct, and the test file pre-existed as a failing specification that the code was written to satisfy (TDD contract fulfilled). No blockers found.

---

## BLOCKERS

None.

---

## FOLLOW-UP

**L1 — `import copy` is a function-body import of a stdlib module.**

`_merge_at_path` does `import copy` inside the method body (line 678 of `links.py`). `copy` is part of the standard library with no risk of circular imports or slow load time in this module. Function-level imports of stdlib modules are an anti-pattern: they hide dependencies, make the module harder to read at a glance, and add a tiny per-call overhead (dict lookup in `sys.modules`, negligible but non-zero). Move it to the top-level imports alongside the existing `from typing import Dict, Any`.

**L2 — Silent fallback in `execute()` when `target_schema_path` resolves to `None`.**

On line 460:
```python
active_schema = cls._extract_schema_branch(schema, target_schema_path) or schema
```
If the caller supplies a `target_schema_path` that does not exist in the schema, `_extract_schema_branch` returns `None` and execution silently falls back to the full schema. The quarantine is then entirely bypassed — the LLM sees the whole document — without any warning to the caller. Depending on how this feature is used in production, silent degradation here could produce subtly wrong enrichments (token-efficiency guarantee violated, wrong fields targeted) without any observable error. A `logger.warning` at minimum, or a raised `ValueError` if contract violation is considered fatal, would make the failure surface rather than hide.

Similarly on line 461:
```python
active_data = cls._extract_data_branch(current_data, target_schema_path) or {}
```
An empty dict fallback when the path resolves to `None` is reasonable, but it is inconsistent with the schema fallback policy directly above it — one silently degrades, the other silently falls back to full scope. Aligning the handling (both degrade with a warning, or both raise) would make the contract easier to reason about.

Neither of these warrants blocking the card. The feature works as designed for the tested cases, and the test coverage is solid. These are quality improvements for a follow-up.

---

## Close-out Actions

- Mark card complete via MCP once this review is delivered.
- Note: the commit message states "396 passed, 4 skipped, 0 failed" while the executor log (ELDV21FU-mwvmar-executor-1.jsonl) reports "tests_passed: 476, tests_skipped: 4". The card work summary also states 476. The discrepancy is likely because the commit message was written mid-session before all integration tests were fixed. The executor trace confirms the full final run at 476 passed (78.82% coverage). No action required, but the commit message is misleading for future archaeology.
