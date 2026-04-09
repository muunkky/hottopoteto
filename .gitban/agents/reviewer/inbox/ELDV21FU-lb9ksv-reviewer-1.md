---
verdict: APPROVAL
card_id: lb9ksv
review_number: 1
commit: 20937cb
date: 2026-04-09
has_backlog_items: true
---

# Review: lb9ksv — Dead Code Removal and Jinja2 Design Documentation

## Summary

This card removes two unreachable `isinstance(rendered, dict)` guards from `core/domains/llm/links.py`, adds inline comments to both the `ast.literal_eval` fallback paths and `StorageSaveLink._extract_data`, and adds a set of pinning tests for all three design contracts. All three acceptance criteria are met. The implementation is approved with one follow-up item.

---

## BLOCKERS

None.

---

## FOLLOW-UP

### L1 — Full test suite coverage gate is failing (26.92% < 50%)

ADR-0005 established a 50% coverage floor enforced by `--cov-fail-under=50`. Running the full test suite against the current sprint branch yields 26.92%, which fails the gate. The executor correctly noted this and correctly stated it is pre-existing — the failures in `test_llm_enrich_schema_path.py` and `test_eldorian_word_v2_output_schema.py` (20 tests) predate this card and are visible in the commit immediately before `57e4375`.

This card does not cause the coverage regression and is not responsible for fixing it. However, the coverage gate failure should be tracked. If it is not already on a card, it should be. The executor's test plan ran the targeted suite only (36 tests), which is appropriate for a scoped cleanup card — the full suite failure does not block approval here.

**Action**: Verify a follow-up card exists for the failing `test_llm_enrich_schema_path.py` and `test_eldorian_word_v2_output_schema.py` tests and the coverage gate regression. If none exists, create one.

---

## Approval Notes

### Dead code removal — AC1

Both `isinstance(rendered, dict)` guards are removed from `_resolve_schema` (line 197) and `_resolve_document` (line 522). The comment placed in their stead accurately describes why they were unreachable and why the `ast.literal_eval` path remains. The removal is clean and correct.

### ast.literal_eval coupling comment — AC3

Both `_resolve_schema` and `_resolve_document` now carry identical, accurate comments explaining the Jinja2 Python-repr rendering behaviour and the architectural coupling to the `ast.literal_eval` fallback. The comment explicitly flags the removal condition (JSON-serialised context values). This is well-executed.

### StorageSaveLink design comment — AC2

The "Design note — bare Environment() is intentional (swallow-and-warn)" section added to `_extract_data`'s docstring is thorough and accurate. It names the divergence from sibling classes explicitly and explains the consequence of changing to `StrictUndefined`. The existing test comment in `test_storage_save_handles_undefined_variables` is appropriately upgraded from behaviour description to design intent.

### TDD compliance

The three new test classes (`TestRenderTemplateAlwaysReturnsStr`, `TestAstLiteralEvalFallback`, `TestStorageSaveLinkSwallowAndWarnBehavior`) pin design contracts, not implementation details. They are proportionate to the scope: a cleanup card removing dead code and adding documentation. The executor trace shows multiple explicit pytest invocations with output verification, including debugging a mid-session test failure and fixing it before the final commit. Test-first framing is credible for a cleanup card — the contracts being tested were already implicit in the dead guards that were removed.

### No regressions

The 36 tests in the targeted suite all pass. The 20 pre-existing failures in the broader suite are unrelated to the files touched by this card and are confirmed present in the commit immediately preceding the work.

### No lazy solves

No dependencies were downgraded, no type checks loosened, no linters disabled.

### ADR compliance

No architectural decisions were introduced. The inline documentation explicitly flags a potential future architectural change (JSON-serialisation of context values) as a trigger for removing the `ast.literal_eval` fallbacks — this is ADR-aware thinking that does not require a new ADR.
