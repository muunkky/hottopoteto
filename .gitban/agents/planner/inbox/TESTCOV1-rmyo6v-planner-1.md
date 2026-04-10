The reviewer flagged 1 non-blocking item, grouped into 1 card below.
Create ONE card per group. Do not split groups into multiple cards.
The planner is responsible for deduplication against existing cards.
All cards go into the current sprint unless marked BLOCKED with a reason.

### Card 1: Install mypy in venv and add type checking to quality gate
Sprint: TESTCOV1
Files touched: project venv / dev dependencies (requirements-dev.txt or pyproject.toml)
Items:
- L3: mypy is not installed in the project venv. Type checking is listed as a quality gate in project conventions but is not enforced. Install mypy as a dev dependency and confirm it runs against the codebase without errors. Update any quality gate documentation or CI config to include the mypy check.
