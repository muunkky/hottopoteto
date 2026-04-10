---
verdict: APPROVAL
card_id: i4natl
review_number: 1
commit: d89d1e8
date: 2026-04-08
has_backlog_items: false
---

## Summary

Commit `d89d1e8` reworks all 14 previously-failing integration tests to match the actual executor dispatch behaviour. All 16 tests in `tests/integration/test_executor_integration.py` pass against HEAD. Both blockers from the prior rejection are resolved.

---

## Blocker Resolution

### B1 resolved: All 16 integration tests pass

The root cause was that `_execute_link()` dispatches `llm`, `user_input`, and `function` link types to internal methods before checking the registered handler registry. The rework patches at the correct intercept points:

- `patch.object(RecipeExecutor, "_execute_user_input_link", ...)` replaces the defunct `register_link_type("user_input", ...)` pattern that was bypassed by the built-in dispatch order.
- `patch.object(RecipeExecutor, "_execute_llm_link", ...)` replaces `patch.object(LLMHandler, "execute", ...)` which was equally bypassed.
- `FunctionLinkWrapper` registration is removed; the built-in `random_number` function works natively through `_execute_function_link()` with no mocking needed.
- All memory key assertions are corrected from raw link names (`"User Inputs"`) to sanitized keys (`"User_Inputs"`), matching the executor's `link_name.replace(" ", "_")` normalisation at line 442.
- `LLMOutput` and `UserInputOutput` are imported from `core.executor` where they are defined, fixing the `ImportError` from the incorrect `core.domains.llm.models` import path.

### B2 resolved: `test_llm_prompt_contains_user_input_value` now tests its stated intent

The test now captures `link_config` passed to `_execute_llm_link` and asserts:
1. `_execute_llm_link` is called exactly once.
2. `executor.memory["User_Inputs"].data["test_word"] == "dragon"` — confirming the user input value was present in memory before the LLM link ran, making it available for Jinja template rendering.
3. `"LLM_Step" in executor.memory` — confirming the LLM link executed.

The prior two identical assertions (`"User Inputs" in executor.memory` and `"LLM Step" in executor.memory`) are replaced by substantive checks that distinguish this test from `test_memory_contains_both_link_outputs`.

---

## Non-blocking observations

- `test_llm_handler_error_stored_gracefully` is renamed `test_llm_handler_error_propagates_from_execute`. The rename and updated docstring accurately distinguish between: (a) `_execute_llm_link` swallowing internal `ChatOpenAI` errors as `LLMOutput(data={"error": ...})`, and (b) exceptions raised at the method boundary propagating through `execute()`. Both behaviours are now correctly documented.
- The `MockUserInputHandler` class and the registry-based mocking scaffolding are removed entirely. The file is significantly shorter and the mock boundaries are unambiguous.
- The 20 pre-existing failures in `test_eldorian_word_v2_output_schema.py` and `test_llm_enrich_schema_path.py` are unrelated to this card and were failing before these changes.

---

## Test run

`tests/integration/test_executor_integration.py` — 16 passed
