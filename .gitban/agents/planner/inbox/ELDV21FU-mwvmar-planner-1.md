The reviewer flagged 2 non-blocking items, grouped into 1 card below.
Create ONE card per group. Do not split groups into multiple cards.
The planner is responsible for deduplication against existing cards.
All cards go into the current sprint unless marked BLOCKED with a reason.

### Card 1: Add warning/error handling for silent target_schema_path fallback in LLMEnrichLink
Sprint: ELDV21FU
Files touched: core/domains/llm/links.py
Items:
- L2: In `execute()` (line 460), when `target_schema_path` resolves to `None`, `_extract_schema_branch` returns `None` and execution silently falls back to the full schema via `or schema`. The quarantine is entirely bypassed without any warning. Add a `logger.warning` (or `ValueError` if contract violation is fatal) so the failure surfaces rather than hides. Similarly on line 461, `_extract_data_branch` falls back to `{}` silently — align the handling with the schema fallback policy (both warn, or both raise) so the contract is consistent and easier to reason about.
