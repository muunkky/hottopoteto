---
verdict: APPROVAL
card_id: tt9cb3
review_number: 3
commit: c4a9385
date: 2026-04-08
has_backlog_items: false
---

## Summary

Cycle 3 rework addresses both blockers from Cycle 2 cleanly. B1 (LLMRequest.messages type contract) is correctly resolved via Option A (revert to Optional + None guard). B2 (full suite not run) is resolved with a complete `pytest tests/unit/` run, acknowledged failures listed by name, and genuine counts confirmed by independent verification.

## Verification

Tests were independently re-run against this commit:

- `tests/unit/test_llm_models.py` — **3/3 pass.** The contract test `test_add_message_initialises_list_when_messages_is_none` passes. Both sibling tests also pass.
- `tests/unit/test_pydantic_v2_model_fields_inheritance.py` — **17/17 pass.**
- `tests/unit/test_schema_nullability.py` — **2/2 pass.**
- Full `tests/unit/` suite — **347 passed, 13 failed, 4 skipped.** The 13 failures are all in `test_llm_enrich_schema_path.py` and pre-date this card. The executor reported 346 passed / 12 failed — the 1-count discrepancy is a classification artefact: `TestBranchQuarantineIntegration::test_enrich_with_schema_path` was counted as an "error" (missing mocker fixture) in the executor's environment but materialises as a "failure" here because `pytest-mock` is installed in the main venv. The failure is pre-existing and unrelated to this card's scope.

## Changes Assessed

**`core/domains/llm/models.py`**

- `LLMRequest.messages` reverted from `List[LLMMessage] = Field(default_factory=list)` back to `Optional[List[LLMMessage]] = Field(default=None)`. This restores the contract the test suite asserts.
- `add_message` gains a `if self.messages is None: self.messages = []` guard before `.append()`. The guard is correct: it is only entered on first call when `messages` is `None`, subsequent calls skip the branch and append directly.
- Domain schema for `llm.request`: `messages` removed from `required`; field schema changed to `anyOf: [array, null]` with `default: None`. This keeps the JSON Schema in sync with the Python type annotation. Formatting expanded to multi-line for readability.

**`core/domains/storage/models.py`**

- Diff shows only whitespace normalisation (trailing blank line and extra blank line between `StorageEntity` and `StorageQuery` removed). No semantic change. The `tags` fix from Cycle 2 (`StorageEntity.tags` override removed, `model_json_schema()` + null-patch used for schema registration) is correctly present and passes the inheritance and nullability test suites.

## ADR Compliance

No ADRs exist in `docs/adr/` for this project at this time. The changes touch model definitions and schema registration patterns established by existing codebase conventions. The revert restores the prior established contract; no new architectural decision is being introduced.

## TDD Assessment

This is a rework commit, not a new-feature commit. The test contract (`test_add_message_initialises_list_when_messages_is_none`) predates this cycle and defined the accepted behaviour. The executor correctly treated it as the specification and reverted production code to satisfy it rather than changing the test. That is textbook TDD discipline on a rework cycle.

The spike's test suite (`test_pydantic_v2_model_fields_inheritance.py`) was authored in earlier cycles and continues to pass. No new behaviour was introduced in this commit that lacks test coverage.

## BLOCKERS

None.

## FOLLOW-UP

None introduced by this commit. The pre-existing follow-up work (step-4b Pydantic v2 deprecated API migration — card `7l3637`) is correctly tracked on its own card and is unaffected by this approval.

## Close-out Actions

None required. Card may be moved to done.
