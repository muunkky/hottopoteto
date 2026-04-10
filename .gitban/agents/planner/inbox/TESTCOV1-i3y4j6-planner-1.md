The reviewer flagged 3 non-blocking items, grouped into 1 card below.
Create ONE card per group. Do not split groups into multiple cards.
The planner is responsible for deduplication against existing cards.
All cards go into the current sprint unless marked BLOCKED with a reason.

### Card 1: cleanup pydantic_integration.py — simplify field iteration, remove dead isinstance guard, and pin None-default test
Sprint: TESTCOV1
Files touched:
- core/schema/pydantic_integration.py
- tests/unit/test_pydantic_integration_model_fields.py

Items:
- L1: `generate_recipe_template` iterates `__annotations__` then filters against `model_fields`. Replace the two-pass approach with a single pass over `model_fields.items()`, using `field_info.annotation` for type resolution via `_get_field_type`.
- L2: The `isinstance(default, PydanticUndefinedType)` guard inside the field loop is dead code — the preceding `is_required()` guard already guarantees the default is not `PydanticUndefined`. Remove the guard. If `PydanticUndefinedType` is retained for any reason, move its import to the module top level (currently deferred into the loop body, re-evaluated on every iteration).
- L3: Add a test asserting that `Optional[str] = None` fields do NOT emit a `default:` key in the generated YAML template. The omission of `None` defaults is intentional design; currently there is no test that pins this behavior, so a future change to the guard would go undetected.
