# Sprint Cleanup Template

## Cleanup Scope & Context

* **Sprint/Release:** DOCENRICH - Schema-Driven Document Enrichment Sprint
* **Primary Feature Work:** storage.init, storage.update, llm.extract_to_schema, llm.enrich link types + external schema files
* **Cleanup Category:** Mixed (documentation, testing, integration, example recipe)

**Required Checks:**
* [x] Sprint/Release is identified above.
* [x] Primary feature work that generated this cleanup is documented.

---

## Deferred Work Review

- [x] Reviewed commit messages for "TODO" and "FIXME" comments added during sprint.
- [x] Reviewed PR comments for "out of scope" or "follow-up needed" discussions.
- [x] Reviewed code for new TODO/FIXME markers (grep for them).
- [x] Checked team chat/standup notes for deferred items.

| Cleanup Category | Specific Item / Location | Priority | Justification for Cleanup |
| :--- | :--- | :---: | :--- |
| **Documentation** | docs/reference/recipe-format.md - Document new link types | P0 | Users need to know how to use new features |
| **Documentation** | docs/reference/link-types.md - Add new link types reference | P0 | Complete link type reference |
| **Documentation** | core/domains/llm/README.md - Document extraction/enrich patterns | P1 | Domain documentation consistency |
| **Example Recipe** | templates/recipes/examples/schema_enrichment.yaml | P0 | Demonstrate the new workflow |
| **ADR** | docs/architecture/decisions/adr-0006 final review | P0 | Document architectural decision |
| **Tests** | Integration test for full schema → init → enrich → update → save flow | P1 | End-to-end validation |
| **Changelog** | Update project CHANGELOG.md with new features | P1 | Track version changes |
| **Roadmap** | Update gitban roadmap with completed work | P2 | Track project progress |

---

## Cleanup Checklist

### Documentation Updates

| Task | Status / Details | Done? |
| :--- | :--- | :---: |
| **README.md** | Update main README with new schema workflow | - [x] |
| **API Documentation** | docs/reference/recipe-format.md - Add storage.init, storage.update, llm.extract_to_schema, llm.enrich | - [x] |
| **API Documentation** | docs/reference/link-types.md - Add new link type reference | - [x] |
| **Architecture Docs** | Finalize ADR-0006 | - [x] |
| **CHANGELOG** | Add DOCENRICH sprint features to CHANGELOG.md | - [x] |
| **ADRs** | Final review and commit ADR-0006 | - [x] |
| **Docstrings** | Ensure all new link classes have docstrings | - [x] |

### Testing & Quality

| Task | Status / Details | Done? |
| :--- | :--- | :---: |
| **Missing Integration Tests** | End-to-end schema enrichment workflow test | - [x] |
| **Test Coverage** | Verify coverage for new link types (323 tests passing) | - [x] |
| **Example Recipe** | Create working example recipe demonstrating pattern | - [x] |

### Code Quality & Technical

| Task | Status / Details | Done? |
| :--- | :--- | :---: |
| **TODOs Resolved** | Review any TODOs added during sprint | - [x] |
| **Code Formatting** | Run formatter on all new files | - [x] |
| **Linter Warnings** | Resolve any new warnings | - [x] |

---

## Validation & Closeout

### Pre-Completion Verification

| Verification Task | Status / Evidence |
| :--- | :--- |
| **All P0 Items Complete** | ✅ All P0 items complete |
| **All P1 Items Complete or Ticketed** | ✅ All P1 items complete |
| **Tests Passing** | ✅ 323 tests passing |
| **No New Warnings** | ✅ Linter clean |
| **Documentation Updated** | ✅ All docs updated |
| **Code Review** | ✅ Self-review completed |

### Follow-up & Lessons Learned

| Topic | Status / Action Required |
| :--- | :--- |
| **Remaining P2 Items** | None - all complete |
| **Recurring Issues** | Two-step pattern (LLM+Storage) works well |
| **Process Improvements** | TDD workflow effective for complex links |
| **Technical Debt Tickets** | None identified |

### Completion Checklist

* [x] All P0 items are complete and verified.
* [x] All P1 items are complete or have follow-up tickets created.
* [x] P2 items are complete or explicitly deferred with tickets.
* [x] All tests are passing (unit, integration, and regression).
* [x] No new linter warnings or errors introduced.
* [x] All documentation updates are complete and reviewed.
* [x] Code changes (if any) are reviewed and merged.
* [x] Follow-up tickets are created and prioritized for next sprint.
* [x] Team retrospective includes discussion of cleanup backlog (if significant).

---

## Required Reading and Grep Terms

**Required Reading:**
- All completed cards from Steps 1-6
- `docs/reference/recipe-format.md` - Update with new link types
- `docs/reference/link-types.md` - Add new link type reference
- `CHANGELOG.md` - Version tracking

**Grep Terms:**
- `storage\.init|storage\.update` - New storage links to document
- `llm\.extract|llm\.enrich` - New LLM links to document
- `TODO|FIXME` - Deferred work from sprint
- `@pytest\.mark\.skip` - Skipped tests to review
- `NotImplemented|raise.*Error` - Incomplete implementations
