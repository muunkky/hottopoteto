---
verdict: REJECTION
card_id: tt9cb3
review_number: 2
commit: 8616000dbb398aa712e182b4afa52668f6ad17d4
date: 2026-04-08
has_backlog_items: false
---

## BLOCKERS

### B1 — `LLMRequest.messages` type change breaks an existing contract test

**What happened.** Commit `8616000` changed `LLMRequest.messages` from
`Optional[List[LLMMessage]] = Field(default=None)` to
`List[LLMMessage] = Field(default_factory=list)`. This is a behavioural contract
change on a public model. A test that documents and enforces that contract already
exists in the repo:

```
tests/unit/test_llm_models.py::TestLLMRequestAddMessage::test_add_message_initialises_list_when_messages_is_none
```

That test was written at commit `ee1b16e` as a TDD contract for `add_message`
initialising the list when `messages is None`. After this commit it fails:

```
assert req.messages is None   # AssertionError — messages is now []
```

The executor's log records only the two new test files (17+2 = 19 passing) and does
not show a full suite run. Running `pytest tests/unit/` against the committed code
produces 1 additional failure (the test above) plus 13 pre-existing failures in
`test_llm_enrich_schema_path.py` (unrelated sprint, pre-dates this card).

**Standard violated.** A full test-suite run is required before committing. No code
change may leave the suite in a worse state than it entered. Selectively running only
new tests to avoid surfacing breakage is not TDD compliance — it is the opposite.

**Required fix.** Two coherent paths:

Option A — revert the `LLMRequest.messages` type change and keep the None-guarded
`add_message` from `ee1b16e`. The schema registration already uses
`"anyOf": [array, null]` separately, so this is safe. The 2 schema nullability
tests pass regardless of whether the Python field is `Optional` or not.

Option B — update `test_llm_models.py::test_add_message_initialises_list_when_messages_is_none`
to reflect the new contract (`req.messages == []`, not `req.messages is None`), and
delete the now-dead `if self.messages is None` guard. This is only acceptable if the
executor can demonstrate the schema nullability tests still pass and no downstream
code depends on `messages` starting as `None`.

Either path must be verified by running `pytest tests/unit/` in full and showing
the output before committing.

---

### B2 — Executor did not run the full test suite

**What happened.** The executor log (`TESTCOV1-tt9cb3-executor-2.jsonl`) contains
two `test-run` events (the two new files) and a `summary` with `failed_total: 0`.
It does not contain a full-suite run. The broken `test_llm_models.py` test is not
acknowledged in the log. `pre_existing_failures: 1` in the summary refers to the
plugin directory structure test, not `test_llm_models.py`.

**Standard violated.** Every commit must demonstrate a clean full-suite run (or
explicitly acknowledge pre-existing failures by name). Selective test execution
that omits tests covering changed modules is not acceptable.

**Required fix.** Run `pytest tests/unit/` after the fix in B1. Log the output.
Acknowledge any pre-existing failures by name in the executor log so reviewers
can verify nothing regressed.

---

## Notes for executor

The `test_llm_enrich_schema_path.py` failures (13 tests, `AttributeError` on
`LLMEnrichLink._extract_schema_branch`) are confirmed pre-existing — that file was
last modified at `7189ede`, which predates this sprint card. You must acknowledge
them in your summary log but they are not introduced by this card.

The `StorageEntity.tags` fix itself is correct and the 17 inheritance tests + 2
schema nullability tests all pass as claimed. The `_entity_schema` patch approach
(mutating the dict after `model_json_schema()`) is a reasonable workaround given
the constraint that `tags` must accept null in the domain schema while Pydantic
emits a strict array type. The inline comment adequately explains the intent.

The `get_domain_schema` docstring trimming in `domains.py` is cosmetically fine but
loses the prose explanation of what the function does. Consider keeping the sentence
"Looks up the schema stored via register_domain_schema and returns the raw schema
dict, or None if the domain or schema is not found." — it adds value for callers.
This is non-blocking.
