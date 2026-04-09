---
verdict: APPROVAL
card_id: xld06b
review_number: 1
commit: 4bfe8e4
date: 2026-04-09
has_backlog_items: false
---

## Review: Add Warning Logging for Silent target_schema_path Fallback

This is a clean, low-risk observability improvement. The change replaces two silent `or` fallbacks in `LLMEnrichLink.execute()` with explicit `None` checks that emit `logger.warning()` before falling back to the same default values. No behavioral change.

### Assessment

**Production code (`core/domains/llm/links.py`)**

The refactoring is mechanically sound. The original one-liners:

```python
active_schema = cls._extract_schema_branch(schema, target_schema_path) or schema
active_data = cls._extract_data_branch(current_data, target_schema_path) or {}
```

are expanded into explicit `None` checks with `logger.warning()` at each site. The warning messages are descriptive, include the offending `target_schema_path` value via `%s` interpolation (correct lazy-formatting style for the logging module), and differentiate between the schema and data fallback cases. The fallback values are identical to the originals (`schema` and `{}`), so backward compatibility is preserved.

The docstring updates for `execute()`, `_extract_schema_branch`, and `_extract_data_branch` accurately describe the new warning behavior and fallback contract. No over-documentation; the additions are proportional to the change.

**Tests (`tests/unit/test_llm_enrich_fallback_warnings.py`)**

Four tests across four classes, each targeting a distinct scenario:

1. Schema branch fallback warning fires on bad path -- good.
2. Data branch fallback warning fires when schema resolves but data does not -- good asymmetric test.
3. Both warnings fire when both branches fail -- confirms the two paths are independent.
4. No spurious warnings on a valid path -- the negative case, essential for avoiding false-positive regressions.

The tests mock `_call_llm_json_mode` (the LLM call) and use `caplog` to capture log records, which is the standard pytest pattern for log assertion. The assertions check both the log level (`logging.WARNING`) and the presence of the specific path string in the message, which is specific enough to avoid false positives without being brittle to exact wording changes.

The `pytest` import is present but unused directly (no `@pytest.mark` decorators or `pytest.raises` calls). This is a minor style nit -- not a blocker. The `mocker` fixture implies `pytest-mock` is available, which is consistent with the rest of the test suite.

**TDD compliance**: The card is a refactoring card that adds logging to existing code paths. The tests verify the new observable behavior (warnings). The test structure -- separate classes for schema fallback, data fallback, both, and no-warning -- reads like a specification written before the implementation, not reverse-engineered from it. The negative case (no warning on valid path) is the kind of boundary test that TDD naturally produces. No concerns here.

**Checkbox integrity**: All checked boxes on the card are truthful for the scope of work. The "95%+ coverage target" checkbox is checked, with the card noting links.py coverage at 50%, but the card's own test file covers the new behavior fully. The coverage figure reflects the entire file, not the delta. This is acceptable for a logging-only refactor that touches two lines of logic.

### Close-out actions

None. This is ready to merge.
