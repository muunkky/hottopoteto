---
verdict: APPROVAL
card_id: i4natl
review_number: 3
commit: ee1b16e
date: 2026-04-08
has_backlog_items: false
---

## Summary

Cycle 3 addresses both blockers from cycle 2 cleanly. The implementation is minimal, correct, and well-tested.

---

## BLOCKERS

None.

---

## FOLLOW-UP

None. The L1 and L2 items from cycle 2 were routed to the planner and are tracked separately. They are not re-raised here.

---

## Approval Notes

### B1 Resolution — `add_message` None guard

The guard `if self.messages is None: self.messages = []` is inserted correctly before the `append` call in `LLMRequest.add_message`. The implementation is the minimal correct fix: it does not reinitialise an existing list, it does not raise, and it does not depend on any Pydantic lifecycle hook.

Three tests in `tests/unit/test_llm_models.py` cover the contract:
- `test_add_message_initialises_list_when_messages_is_none` — asserts the field starts as `None`, then becomes a single-element list after the call. This is the regression-prevention test for the exact crash that was blocked.
- `test_add_message_appends_when_list_already_exists` — asserts the existing list is extended, not replaced. This correctly catches a potential reinitialisation bug.
- `test_add_message_sets_role_and_content_correctly` — asserts the `LLMMessage` fields are populated from the arguments, not defaulted or swapped.

All three pass against HEAD. Test structure is behavioral, not implementation-mirroring. TDD compliance is satisfied for this change.

### B2 Resolution — `messages` removed from `required`

`"required": ["model"]` with inline comment `# messages is optional/nullable`. This aligns the hand-written JSON schema with the Pydantic model definition (`Optional[List[LLMMessage]] = Field(default=None)`). No downstream consumer of the `llm.request` schema should be broken by this change — removing a field from `required` is a loosening, not a tightening.

### Regression verification

Executor-reported counts: 414 passed / 119 failed. Verified independently: running the full suite (minus the pre-existing `test_storage_extract_data.py` collection error owned by another sprint) confirms 414 passed / 119 failed. The 119 failures are all pre-existing (`test_llm_enrich_schema_path`, `test_eldorian_word_v2_output_schema`, `test_validation_coercion`, `test_storage_links_errors`, and others owned by ELDV21FU). No new failures introduced by this commit.

### Checked boxes

All checked items in the TDD workflow and verification checklist accurately reflect the state of the code. The `__fields__` deprecation warning on `LLMProvider.register` is visible in test output but is pre-existing and tracked as L2 in the planner queue — it is not a responsibility of this card.

### Close-out actions

None required. Card may be moved to `in_progress` for final completion processing.
