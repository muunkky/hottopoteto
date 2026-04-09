Use `.venv/Scripts/python.exe` to run Python commands.

The code for the gitban card with id i3y4j6 has been approved as of commit 14aee22. Please use the gitban tools to update the gitban card and begin the tasks required to properly complete it.

## Card Close-out tasks:
- Use gitban's checkbox tools to ensure all checkboxes on the card are checked off for completed work if not already.
- Do not mark any work as deferred. This card will be closed and archived and likely never seen again.
- Use gitban's complete card tool to submit and validate if not already completed.
- Close-out items:
  - The card's completion checklist includes boxes for "code reviewed by at least 2 team members", "staging environment validation", and "production deployment with monitoring". These are boilerplate from the template and are inapplicable to a solo project. They do not represent false claims — the card's own text marks staging/production as N/A. No action needed.
  - No `__fields__` usage remains in `core/` or `plugins/` after this commit. The success criterion "No use of `__fields__` remains in `core/` or `plugins/`" is satisfied.
  - The 12 pre-existing failures in `test_llm_enrich_schema_path.py` noted in the execution summary are confirmed pre-existing and unrelated to this commit.
- If this card is not in a sprint, push the feature branch and create a draft PR to main using `gh pr create --draft`. Do not merge it — the user reviews and merges.

Note: You are closing out this card only. The dispatcher owns sprint lifecycle — do not close, archive, or finalize the sprint itself. The exception is a sprint close-out card, which will be obvious from its content.
