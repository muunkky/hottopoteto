Use `.venv/Scripts/python.exe` to run Python commands.

The code for the gitban card with id mwvmar has been approved as of commit 9f22e82. Please use the gitban tools to update the gitban card and begin the tasks required to properly complete it.

## Card Close-out tasks:
- Use gitban's checkbox tools to ensure all checkboxes on the card are checked off for completed work if not already.
- Do not mark any work as deferred. This card will be closed and archived and likely never seen again.
- Use gitban's complete card tool to submit and validate if not already completed.
- Close-out items:
  - **L1 — Move `import copy` to top-level imports in `core/domains/llm/links.py`.** The `_merge_at_path` method (line 678) does `import copy` inside the method body. `copy` is stdlib with no circular import risk. Move it to the top-level imports alongside the existing `from typing import Dict, Any`. This is a one-line change that does not require rerunning the test suite.
  - Note from reviewer: The commit message states "396 passed, 4 skipped, 0 failed" while the executor trace confirms 476 passed. The commit message is misleading for future archaeology but no action required.
- If this card is not in a sprint, push the feature branch and create a draft PR to main using `gh pr create --draft`. Do not merge it — the user reviews and merges.

Note: You are closing out this card only. The dispatcher owns sprint lifecycle — do not close, archive, or finalize the sprint itself. The exception is a sprint close-out card, which will be obvious from its content.
