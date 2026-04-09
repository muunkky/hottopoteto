The reviewer flagged 4 non-blocking items, grouped into 2 cards below.
Create ONE card per group. Do not split groups into multiple cards.
The planner is responsible for deduplication against existing cards.
All cards go into the current sprint unless marked BLOCKED with a reason.

### Card 1: Clean up dead code and document Jinja2 environment design choices in link files
Sprint: ELDV21FU
Files touched: core/domains/llm/links.py, core/domains/storage/links.py
Items:
- L1: Remove permanently dead `isinstance(rendered, dict)` guards on lines 197 and 513 of `core/domains/llm/links.py` — `_render_template` always returns a string, so these branches can never be reached and confuse readers about the method contract.
- L3: In `core/domains/storage/links.py`, `StorageSaveLink._extract_data` uses bare `Environment()` intentionally (swallow-and-warn behavior, documented by a pre-existing test). Now that sibling classes use `StrictUndefined`, add an inline comment explicitly documenting the design choice and why this class diverges. The existing test comment ("with default Jinja2, undefined variables render as empty string") should be upgraded to state the design intent.
- L4: The `ast.literal_eval` fallback paths in `_resolve_schema` and `_resolve_document` (`core/domains/llm/links.py`) exist because Jinja2's `render()` produces Python repr for dict objects. Add a comment noting that if the architecture ever moves to JSON-serializing context values before rendering, these fallback paths should be removed. This is a documentation-only change to track the technical debt inline.

### Card 2: Strengthen weak test assertions in TestGenerateRecipeTemplate
Sprint: ELDV21FU
Files touched: tests/unit/test_pydantic_integration.py (or wherever TestGenerateRecipeTemplate lives)
Items:
- L2: `test_generate_recipe_template_default_factory_field_omitted_or_empty` uses an identity check `is not PydanticUndefinedSentinel()` which is weaker than the intended assertion. The real guard should assert that the `default` key is absent from the field definition when a `default_factory` is present. Fix: change the assertion to check key absence.
- L2: `test_generate_recipe_template_none_default_still_omitted` contains `or True` at the end of its assertion, making the test a no-op. Remove the `or True` to restore the regression guard.
