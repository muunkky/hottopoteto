Use `.venv/Scripts/python.exe` to run Python commands.

The code for the gitban card with id rmyo6v has been approved as of commit 0871017. Please use the gitban tools to update the gitban card and begin the tasks required to properly complete it.

## Card Close-out tasks:
- Use gitban's checkbox tools to ensure all checkboxes on the card are checked off for completed work if not already.
- Do not mark any work as deferred. This card will be closed and archived and likely never seen again.
- Use gitban's complete card tool to submit and validate if not already completed.
- If this card is not in a sprint, push the feature branch and create a draft PR to main using `gh pr create --draft`. Do not merge it — the user reviews and merges.

## Close-out items (fix before completing the card):

### L1 — Move inline import to module level
File: `tests/unit/test_pydantic_integration_model_fields.py`
Fix: Move `import yaml` from inside the `test_optional_none_default_field_does_not_emit_default_key` method body to the top of the file alongside the other module-level imports.

### L2 — Remove unused imports
File: `tests/unit/test_pydantic_integration_model_fields.py`
Fix: Remove unused `import pytest` and remove `List` from the `from typing import` line. Neither is referenced in the file.

Note: You are closing out this card only. The dispatcher owns sprint lifecycle — do not close, archive, or finalize the sprint itself.
