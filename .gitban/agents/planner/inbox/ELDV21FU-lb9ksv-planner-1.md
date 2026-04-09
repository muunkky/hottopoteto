The reviewer flagged 1 non-blocking item, grouped into 1 card below.
Create ONE card per group. Do not split groups into multiple cards.
The planner is responsible for deduplication against existing cards.
All cards go into the current sprint unless marked BLOCKED with a reason.

### Card 1: Fix pre-existing test failures and coverage gate regression (test_llm_enrich_schema_path + test_eldorian_word_v2_output_schema)
Sprint: ELDV21FU
Files touched: tests/unit/test_llm_enrich_schema_path.py, tests/unit/test_eldorian_word_v2_output_schema.py (and whatever source files they cover)
Items:
- L1: 20 pre-existing test failures in test_llm_enrich_schema_path.py and test_eldorian_word_v2_output_schema.py cause the full test suite coverage to sit at 26.92%, below the 50% gate enforced by ADR-0005 (--cov-fail-under=50). These failures predate card lb9ksv and were confirmed present in the commit immediately before 57e4375. Investigate and fix the failing tests and restore coverage to >= 50%.
