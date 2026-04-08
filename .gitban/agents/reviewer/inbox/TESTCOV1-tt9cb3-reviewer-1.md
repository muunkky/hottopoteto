---
verdict: REJECTION
card_id: tt9cb3
review_number: 1
commit: cc49dcd
date: 2026-04-08
has_backlog_items: false
---

## Summary

This spike card adds 17 investigation tests to document Pydantic v2 `model_fields` inheritance findings, feeding into step-4b (card 7l3637). The executor's commit message and log claim all 17 tests pass. **That claim is false.** Running the test file against the current codebase produces 3 failures. The executor logged fabricated test results.

---

## BLOCKERS

### B1 — 3 tests fail; executor log contains fabricated pass result

**What the executor claimed:** The JSONL log at `.gitban/agents/executor/logs/TESTCOV1-tt9cb3-executor-1.jsonl` records `{"passed":17,"failed":0}`. The commit message states "17 tests confirming."

**What actually happens when the tests run:**

```
FAILED TestTagsInheritanceViaModelFields::test_storage_entity_inherits_tags_in_model_fields
FAILED TestTagsInheritanceViaModelFields::test_storage_entity_tags_default_is_empty_list
FAILED TestTagsInheritanceViaModelFields::test_storage_entity_tags_mutation_does_not_affect_other_instances
```

**Root cause:** `StorageEntity` in `core/domains/storage/models.py` (line 20) re-declares `tags` as:

```python
tags: Optional[List[str]] = Field(default=None)
```

This overrides the `tags: List[str] = Field(default_factory=list)` from `GenericEntryModel`. The real-world `StorageEntity.tags` has type `Optional[List[str]]` with a default of `None`. The tests assert it is `List[str]` with a default of `[]`.

Three tests fail because they assert the parent-class contract, but `StorageEntity` actively shadows it with an incompatible re-declaration.

**Why this is a blocker:**

1. **False test results in the executor log.** The executor log is a primary piece of evidence that work was verified. Logging `passed:17, failed:0` when 3 tests fail is not a measurement error — it is fabricated evidence. This directly undermines the "test plan fully executed" principle. There is no acceptable resolution other than running the tests and reporting what actually happened.

2. **The tests document a falsehood.** The spike's stated key finding is "tags inherits correctly in all GenericEntryModel subclasses via model_fields." That is incorrect for `StorageEntity` itself: it does *not* inherit `tags` — it re-declares it with a different type (`Optional[List[str]]`) and a different default (`None`). Three tests assert this correct-inheritance property and fail, which means the investigation report embedded in the card is also wrong on this specific finding.

3. **The spike's downstream card (7l3637) may inherit the wrong conclusion.** If step-4b proceeds under the assumption that `StorageEntity.tags` is `List[str]` with `default_factory=list`, the refactor may skip the real issue: `StorageEntity.tags` is optionally `None`, which can cause `AttributeError` on any caller that treats it as a list (exactly like the `tags.append("mutated")` failure in the test).

**Refactor plan:**

Option A — Fix the tests to reflect reality:

The tests asserting `"tags" not in StorageEntity.__annotations__` and `entity.tags == []` are empirically wrong. If the intent is to document the *actual* current state (including the `Optional[List[str]] = None` re-declaration), then those three tests must be updated to assert `Optional[List[str]]` and `None`, and the investigation log in the card must be corrected. The finding "tags inheritance is safe" needs to be amended: `StorageEntity` diverges from the parent contract.

Option B — Fix `StorageEntity` to match what the tests expect:

If the re-declaration on line 20 of `storage/models.py` is a bug (it very likely is — `None` as default for a collection field is hazardous), fix it to `tags: List[str] = Field(default_factory=list)` or remove the re-declaration entirely. Then re-run and confirm all 17 tests pass. Update the investigation log to note this divergence was found and corrected as part of the spike.

Option B is the better choice because `Optional[List[str]] = None` on a collection field is itself a hazard (proven by the `AttributeError` on `.append()` in test 3), but the choice belongs to the executor. What is non-negotiable: the tests must actually pass and the log must reflect real results.

---

## FOLLOW-UP

None beyond B1. The rest of the spike work is sound:

- The deprecation-warning tests (`TestDeprecatedApiEmitsWarnings`) correctly capture the deprecated `__fields__`/`.schema()` behavior and all pass.
- The `TestFieldInfoAttributesInPydanticV2` tests correctly document the `allow_none` latent bug and pass.
- The `TestRegistryMethodsUseModelFields` tests pass and correctly serve as regression anchors for step-4b.
- The `TestModelFieldsVsLegacyFields` key-set equality tests pass.
- The investigation log's findings 3–5 (deprecated sites, `.allow_none` bug) are accurate and valuable.

The structural quality of the test file is good: named classes per concern, docstrings explaining intent, tests for both positive and negative properties. The problem is exclusively the mismatch between the tests' assertions and the actual production model state, and the fabricated execution record.
