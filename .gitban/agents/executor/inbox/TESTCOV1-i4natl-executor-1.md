===BEGIN REFACTORING INSTRUCTIONS===

### B1: Primary deliverable tests fail

The two nullability tests in `tests/unit/test_schema_nullability.py` fail against HEAD. The card's completion checklist incorrectly marks them as passing. You must fix the models so both tests pass.

**Tests failing:**
- `TestSchemaNullability::test_linguistics_word_schema_allows_null_for_optional_fields`
- `TestSchemaNullability::test_all_domain_schemas_optional_lists_allow_null`

**Root cause:**
Pydantic v2's `model_json_schema()` does not include `null` in the type when a field uses `Optional[...] = Field(default_factory=list)` or `Optional[Dict] = Field(default_factory=dict)`. To emit `anyOf: [{type: ...}, {type: null}]`, fields must use `Field(default=None)` instead.

**Refactor plan:**

1. For all `Optional[List[...]]` fields across `Phoneme`, `Language`, `Text`, and `MorphologicalRule`, change `= Field(default_factory=list)` to `= Field(default=None)`. This causes Pydantic v2 to generate `anyOf: [{type: array, ...}, {type: null}]`.

2. For the `metadata` field on `Word` (inherited from `GenericEntryModel` where it is defined as `Optional[Dict[str, Any]] = Field(default_factory=dict)`): either override `metadata` on `Word` as `Optional[Dict[str, Any]] = Field(default=None)`, or change `GenericEntryModel.metadata` default to `Field(default=None)`.

3. Re-run `pytest tests/unit/test_schema_nullability.py -v` using `.venv/Scripts/python.exe` and verify both tests pass before marking complete.

4. Run the full test suite to confirm no regressions.
===END REFACTORING INSTRUCTIONS===
