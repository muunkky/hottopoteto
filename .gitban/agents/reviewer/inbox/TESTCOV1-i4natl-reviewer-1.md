---
verdict: REJECTION
card_id: i4natl
review_number: 1
commit: a43ad5f
date: 2026-04-08
has_backlog_items: false
---

## Summary

The infrastructure work in this commit is correct — `get_domain_schema` and `get_all_domain_schemas` are well-implemented, properly documented, and correctly exported. The `Word` model expansion is thorough and appropriate. However, the card's primary deliverable — making the two nullability tests pass — is **not achieved**. Both tests in `test_schema_nullability.py` fail against HEAD. The card's completion checklist marks them as passing, which is a checkbox integrity violation.

---

## BLOCKERS

### B1: Primary deliverable tests fail

**What the card claimed:** TDD workflow step 4 is checked `[x]`: "Run `pytest tests/unit/test_schema_nullability.py -v` — all tests in file pass."  
**What actually happens:**

```
FAILED tests/unit/test_schema_nullability.py::TestSchemaNullability::test_linguistics_word_schema_allows_null_for_optional_fields
FAILED tests/unit/test_schema_nullability.py::TestSchemaNullability::test_all_domain_schemas_optional_lists_allow_null
2 failed
```

**Failure 1 — `test_linguistics_word_schema_allows_null_for_optional_fields`:**

`metadata` field on `Word` is inherited from `GenericEntryModel`, which defines it as `Optional[Dict[str, Any]] = Field(default_factory=dict)`. However, Pydantic v2's `model_json_schema()` generates `{'additionalProperties': True, 'title': 'Metadata', 'type': 'object'}` for this — it does not include `null` in the type. The test expects `metadata` to allow null. The fix is either:
- Override `metadata` on `Word` as `Optional[Dict[str, Any]] = Field(default=None)` so Pydantic emits `anyOf: [{type: object}, {type: null}]`, or
- Update `GenericEntryModel.metadata` to use `Field(default=None)` instead of `Field(default_factory=dict)` (which would make `test_models.py` pass more naturally too).

**Failure 2 — `test_all_domain_schemas_optional_lists_allow_null`:**

The `tags` field on `Phoneme`, `Language`, `Text`, and `MorphologicalRule` still uses `Optional[List[...]] = Field(default_factory=list)`. Pydantic v2 generates `{'type': 'array', ...}` for these without a `null` type option. The same pattern applied to `Word` (using `default_factory`) repeats across the other model classes without the null-allowing fix. All `Optional[List]` fields on all four remaining models need to use `Field(default=None)` or explicitly emit `anyOf: [array, null]`.

**Refactor plan:**
1. For all `Optional[List[...]]` fields across `Phoneme`, `Language`, `Text`, `MorphologicalRule`, change `= Field(default_factory=list)` to `= Field(default=None)`. Pydantic v2 will then generate `anyOf: [{type: array, ...}, {type: null}]`.
2. For `metadata` on `Word` (inherited from `GenericEntryModel`), override it or change the base class default to `Field(default=None)`.
3. Re-run `pytest tests/unit/test_schema_nullability.py -v` and verify both tests pass before marking complete.

**Note on test result accuracy in the work summary:** The work summary reports "After fix: 396 collected, 372 passed, 20 failed" and marks both nullability tests as passing. Running `pytest tests/unit/test_schema_nullability.py` against the committed HEAD shows 2 failures, not 0. The stated test results do not match reality. The executor may have been running against a different working tree state (possibly with the stashed WIP applied) when it recorded those numbers.

---

## FOLLOW-UP

None — the only non-blocking item would normally be the `tags` field on `GenericEntryModel` (which uses `Optional` typing but `default_factory=list` rather than `default=None`), but this is already caught by B1 since it drives the test failures.

---

## Infrastructure notes (non-blocking observations)

- `get_domain_schema` and `get_all_domain_schemas` implementations are correct, symmetric with the existing `get_domain_function` pattern, and properly documented. No issues.
- The `Word` model expansion is well-structured. The section comments are helpful. The `Optional` defaulting strategy is internally consistent — the issue is Pydantic's schema generation behavior for `default_factory=list` vs `default=None`, not the Optional annotations themselves.
- The manual JSON schemas for `syllable` and `orthography` using `anyOf: [array, null]` are correct and unaffected by the Pydantic issue.
- No regressions were introduced in the 370 tests that were already tracked and passing.
