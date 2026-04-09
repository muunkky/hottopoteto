===BEGIN REFACTORING INSTRUCTIONS===

Use `.venv/Scripts/python.exe` to run Python commands.

The code review for card tt9cb3 (review #2, commit 8616000dbb398aa712e182b4afa52668f6ad17d4) has returned a REJECTION with the following mandatory blockers. You must fix all of them and run the full test suite before committing.

---

## B1 — Fix the `LLMRequest.messages` contract break

Commit `8616000` changed `LLMRequest.messages` from `Optional[List[LLMMessage]] = Field(default=None)` to `List[LLMMessage] = Field(default_factory=list)`. This breaks the existing contract test:

```
tests/unit/test_llm_models.py::TestLLMRequestAddMessage::test_add_message_initialises_list_when_messages_is_none
```

That test asserts `req.messages is None` before `add_message` is called. After your change it fails because `messages` is now `[]`.

Choose ONE of the following options:

**Option A** — Revert the `LLMRequest.messages` type change back to `Optional[List[LLMMessage]] = Field(default=None)` and keep the None-guarded `add_message` logic from commit `ee1b16e`. The schema registration already handles nullability separately via `"anyOf": [array, null]`, so this is safe. The 2 schema nullability tests pass regardless.

**Option B** — Update `test_llm_models.py::test_add_message_initialises_list_when_messages_is_none` to reflect the new contract (`req.messages == []`, not `req.messages is None`), and delete the now-dead `if self.messages is None` guard in `add_message`. This is only acceptable if you can confirm:
- The 2 schema nullability tests still pass.
- No downstream code depends on `messages` starting as `None`.

Document which option you chose and why in your executor log.

---

## B2 — Run the full test suite

After applying the fix for B1, run:

```
pytest tests/unit/
```

Log the full output. In your executor summary, explicitly list all pre-existing failures by test name so reviewers can confirm nothing regressed. The known pre-existing failures are:

- 13 tests in `test_llm_enrich_schema_path.py` (`AttributeError` on `LLMEnrichLink._extract_schema_branch`) — these predate this sprint card and must be acknowledged but not fixed here.
- 1 test for plugin directory structure — also pre-existing.

`failed_total` in your summary must reflect the true count, and `pre_existing_failures` must name each test file/class.

---

## Non-blocking close-out note (handle during close-out, no new tests required)

The `get_domain_schema` docstring in `domains.py` was trimmed in this commit and lost the prose explanation of what the function does. Restore the sentence:

> "Looks up the schema stored via register_domain_schema and returns the raw schema dict, or None if the domain or schema is not found."

This is a one-line docstring restoration — no test suite re-run required.

===END REFACTORING INSTRUCTIONS===
