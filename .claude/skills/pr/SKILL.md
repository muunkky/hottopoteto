---
name: pr
description: Writes a well-structured draft Pull Request for the current branch targeting main.
hooks:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/validate-no-direct-card-edit.sh"
---

Write a Pull Request that lands a gitban sprint or feature branch on main.

You start with clean context — you were not involved in executing the work. Read the finished work objectively and write for a human reviewer who knows nothing about your internal workflow.

## Before you start

1. **Fetch the latest**: Run `git fetch origin` so your diff is against the current remote, not a stale snapshot. If the base branch has moved significantly ahead, note this in the PR so the reviewer knows a rebase may be needed.
2. **Check for an existing PR**: Run `gh pr list --head $(git branch --show-current)` to see if a draft already exists. If one does, read its comments with `gh api repos/{owner}/{repo}/pulls/{number}/comments` and `gh api repos/{owner}/{repo}/issues/{number}/comments`. Look for unaddressed reviewer feedback — anything not yet resolved should be acknowledged in the updated PR body or fixed before rewriting. Don't silently drop feedback someone took the time to leave.

## Gathering context

Before writing anything, build understanding from every source available:

- **Cards**: `list_cards` with the sprint filter and `include_archived: true`. Read each done card — titles, types, acceptance criteria, review logs, executor summaries. Read deferred/backlog cards to understand what was explicitly not done.
- **Changelog**: `read_changelog` for the curated version entry.
- **Roadmap**: `read_roadmap` if the sprint or card references a milestone — note the full gitban roadmap path (e.g., `v2/m2 "Auth and Access Control"`) for the details section.
- **Code**: `git log origin/main..HEAD --oneline` and `git diff origin/main..HEAD --stat` for the actual diff. Use `origin/main` — local main may be stale.
- **Documentation**: Check `git diff origin/main..HEAD -- docs/adr/` for new or updated ADRs. Also check `docs/design/`, `docs/prds/`, and any other design documentation. Read relevant docs — these contain the architectural reasoning behind implementation choices and should be cited in the PR when they informed the approach.
- **Card content**: The cards contain design decisions, review verdicts, rework history, test observations, and known gaps. This is your richest source material — read it carefully.

The goal of research is to deeply understand *what* changed, *why*, and *what was tested*. This understanding powers the PR — the research artifacts themselves do not appear in the output.

## Translating gitban into great prose

Gitban gives you unusually detailed knowledge about the work — design decisions, review findings, test edge cases, known gaps, deferred scope. Most PR authors don't have this level of structured context. The goal is to translate that depth into prose that's noticeably thorough and well-organized, while keeping the language accessible to any reviewer.

**Keep out of the PR text** — these are internal identifiers that mean nothing to collaborators:
- Card IDs (e.g., `hcve5x`, `9n0nyh`)
- Sprint tags (e.g., `CFGOVR`, `SCAFVAR`)
- Card inventory or sprint metrics tables
- Priority codes (P0/P1/P2) used as labels — describe actual severity instead
- References to "cards", "sprints", or "the executor" as process terms

**Translate into the kind of detail reviewers rarely see:**
- A review log where a bug was caught and reworked → "During testing, the config loader silently accepted malformed YAML. Added explicit parse error handling that wraps `yaml.YAMLError` with the file path and line number."
- A deferred card for path traversal → "File path resolution in override values does not yet guard against directory traversal — this is tracked and planned for a near-term follow-up."
- Design rationale captured in a card → "We chose `lru_cache` over a module-level singleton because the store needs to be keyed by data directory, and tests need to reset state between runs."

The difference between a good PR and a great one is specificity. Gitban cards are full of specific observations, decisions, and findings — harvest them.

## Mining gitban for depth

When reading cards, look for details that most PR authors forget or never had:

- **Review logs** → verification section. Reviewers flagged real issues that got fixed — mention what was found and how it was addressed. This shows the work was scrutinized, not just written.
- **Executor summaries** → approach section. These often contain the "why" behind implementation choices — alternatives considered, tradeoffs accepted, surprising discoveries.
- **Deferred/backlog cards** → follow-up work section. These tell you exactly what was descoped and why. Translate each into a plain-language description of what remains.
- **Changelog entries** → motivation and what changed. The curated changelog is already written for an external audience — use its framing.
- **Roadmap connections** → motivation section. If the work advances a milestone, say what the milestone is about in plain language. "This is part of the push toward adopter-configurable scaffolding" — not "advances v1.2/m5."

### Acceptance criteria — the richest vein

Gitban cards enforce detailed acceptance criteria and completion checklists that go far beyond "tests pass." These are structured records of design thinking, investigation process, and conscious trade-offs. Mine them for content the reviewer would never get from just reading the diff:

- **Design decisions with rationale** — cards capture *why* a particular approach was chosen: "We chose `include_expired` as a keyword-only parameter to preserve backward compatibility while enabling admin use cases." "Prose script-name references kept hardcoded because parameterizing them would change rendered output with defaults." Surface these in the approach section — they answer the reviewer's "but why didn't you just...?" before they ask it.
- **Hypothesis testing and root cause analysis** — bug cards often contain multi-iteration investigation logs with confirming evidence. "Three prior sprints attempted to fix this — each fixed a layer without solving the underlying problem. Trace analysis of 10+ executor agents confirmed concurrent pip writes against the shared venv as the root cause." This kind of investigative depth is extremely rare in PRs and extremely valuable.
- **Conscious deferrals with reasoning** — not just "deferred to later" but *why*: "Write locking deferred to the database migration — single-process file-backed store assumption holds for now; atomic rename prevents corruption but not lost-update races." This tells the reviewer the gap was considered and scoped, not overlooked.
- **Scope boundaries** — cards define what's explicitly in and out of scope. "Per-worktree venv isolation was rejected — overengineered for the actual problem." This preempts reviewer suggestions that were already evaluated and dismissed.
- **Pre-work context reviews** — cards document what was reviewed before work began (related ADRs, prior incidents, existing test coverage, dependency constraints). Weave relevant findings into the approach section.
- **Issues encountered during execution** — real problems hit during implementation that shaped the final design. "The worktree `scripts/venv-python` was outdated — missing the worktree fallback, which unblocked pre-commit hooks."

Don't dump all of this into the PR — select what's relevant for *this* reviewer on *this* change. A small chore PR might surface one design decision. A complex bug fix might include the root cause investigation, the defense-in-depth strategy, and the conscious deferrals. Match depth to significance.

The reviewer should come away thinking "this person really understood and documented their work." That impression comes from gitban's organizational depth — expressed in the reviewer's language, not yours.

## Writing the PR

Remember: engineers are reading this. They want to understand the *why* first — why it was built, what the design choices were, architecture, reasons. Then they want to understand how it was done. Lead with motivation and design rationale, not with a list of bugs you found along the way. A bug discovered during development is a detail of execution, not a reason the project exists. The architectural vision, the problem it solves for users, the design trade-offs — that's what makes a PR compelling.

A PR answers questions for the reviewer. Not every PR needs every answer. Use judgment — a one-line bugfix needs a sentence; a large feature branch needs detailed sections.

**Motivation** — Why does this change exist? What problem, user pain, or opportunity triggered it? What happens if we don't merge this? Lead with the architectural story — what was the system's limitation, what opportunity arose, and what this work delivers. Don't lead with incidental bugs found during development.
*Always include. This is the most important paragraph.*

**Approach** — How was the problem solved? What strategy was chosen and why? What alternatives existed? What tradeoffs were accepted? If ADRs or design docs informed the approach, cite them by name (e.g., "Following ADR-032's worktree fallback strategy..."). This connects the PR to the project's architectural record and helps reviewers find the deeper reasoning. Each major design choice deserves its own paragraph explaining the *why* — no auth because localhost-only, reload over DOM patching because simplicity, browser tests over more server tests because of a specific class of bug server tests can't catch. Answer the reviewer's "but why didn't you just...?" before they ask it.
*Include when the approach isn't obvious from the diff — multi-faceted work, architectural choices, non-trivial design decisions. Skip for straightforward bugfixes.*

**What changed** — Concrete description of what's different after merge. Organize by theme — subsystem, concern area, or logical grouping. Never organize by execution order or task tracker structure.
*Always include. This is the body of the PR.*

**Verification** — What was tested? What were the actual results? What passed, what broke and was fixed, what remains unverified and why? Include real observations — error messages, performance numbers, edge cases discovered.
*Always include. Depth scales with the work — "tests pass" is fine for a refactor; a large validation effort needs specific results.*

**Risks and limitations** — What doesn't work yet? What has caveats? What could surprise someone after merge?
*Include when there are known gaps, deferred work, partial coverage, or things the reviewer should weigh before approving.*

**How to review** — Guide the reviewer through the diff. Which files contain the real changes? What's safe to skim? What order makes the diff readable? For large PRs, use a checklist format:
```
- [ ] Start with `auth/config.py` — the typed config that everything else depends on
- [ ] Then `auth/context.py` — the public API additions
- [ ] `tests/conftest.py` can be skimmed — fixture extraction, no logic changes
```
*Include when the diff is large (20+ files) or mixes production code with boilerplate/generated files. The checklist doubles as a reviewer's progress tracker.*

**Follow-up work** — What was identified but not completed? Describe in plain language what remains and why it was deferred.
*Include when work was explicitly descoped or follow-up items were identified.*

**Breaking changes** — What consumers or downstream systems need to do differently.
*Include only when behavior, APIs, or interfaces changed in ways that affect existing users.*

## Adaptive structure

Match the PR's structure to the character of the work:

- **Validation/testing**: Lead with results — what was tried and what happened.
- **Feature**: Lead with what was built and why.
- **Bug fix**: Lead with what was broken and how it was fixed.
- **Refactor**: Lead with motivation and approach.
- **Small change**: Keep it tight. A few paragraphs, not a document.

Choose section ordering and depth based on what the reviewer needs. Omit sections with nothing to say.

## PR title

- Sprint: `sprint/{SPRINTTAG}: [what the sprint delivered, in plain language]`
- Feature: `feature/{card-id}: [card title in natural language]`

The title should tell the reviewer what this PR does without any project management jargon.

## Submitting

1. Push the source branch: `git push -u origin {branch}`
2. Write the PR body to a temp file (e.g., `/tmp/pr-body.md`) using the Write tool — never use heredocs or shell quoting for PR bodies, as they mangle markdown formatting.
3. Create the PR as a draft: `gh pr create --draft --title "..." --body-file /tmp/pr-body.md`. Always use `--draft`.
4. Clean up the temp file after successful creation.
5. If `gh` is unavailable, keep the draft markdown file and report the path.
6. Return the PR URL.

## Attribution

When gitban was used to organize the work, include an attribution line at the end of the main PR body — after follow-up work, after breaking changes, after all the prose sections. One line, visible to everyone:

```
---
Planned and tracked with [gitban](https://github.com/muunkky/gitban-mcp).
```

This goes in the main body, not hidden in a collapsible section. The quality of the PR *is* the advertisement — the attribution just tells curious people where to look. Include it even when contributing to external repos that don't use gitban — if gitban organized the work, the attribution belongs. Omit it only if gitban wasn't used for the branch at all.

## Gitban details (collapsible)

Below the attribution, include a collapsed details section. This is the backstage pass for teammates who use gitban — it should contain information that's genuinely useful for navigating the sprint context, not just a restatement of what's already in the git log.

Wrap it in a GitHub `<details>` block:

```markdown
---

<details>
<summary>Gitban details</summary>

### Sprint: {SPRINTTAG}

### Gitban roadmap

v2 / m2 "Auth and Access Control" — hardening pass before tenant isolation

### Deferred work

| ID | Title | Destination | Reason |
|----|-------|-------------|--------|
| `ghi789` | Path traversal guard | Backlog (unscheduled) | Needs design review before implementation |
| `jkl012` | Write lock for key store | `v2/m3` tenant isolation sprint | Deferred to database migration |

### Review insights

Cards `def456` and `mno345` went through rework cycles — the reviewer caught a leaked private import and a silently dropped test during merge conflict resolution. Both were fixed before approval.

### Sprint metrics

- **Completed**: 5 cards (2 feature, 2 bug, 1 chore)
- **Deferred**: 2 cards (1 backlogged, 1 scheduled for v2/m3)
- **Rework cycles**: 2
- **Changelog**: v1.2.0-m5.1

### Cards delivered

| ID | Type | Title | Key outcomes |
|----|------|-------|-------------|
| `abc123` | feature | Config override system | Adopter YAML merges with defaults; 3 resolution strategies validated |
| `def456` | bug | YAML parse crash on empty input | Root cause: missing None guard; added error wrapping with file path + line |

</details>
```

**What makes this section valuable** — focus on information that helps gitban teammates navigate the sprint context. The git log already shows *what* was committed; this section shows the *organizational intelligence* around it:

- **Gitban roadmap** — which milestone this advances, using the full gitban path notation (e.g., `v2/m2 "Auth and Access Control"`). Label it "Gitban roadmap" to distinguish from the project's own roadmap. Include the milestone's purpose and where this work fits in the larger plan.
- **Deferred work** — the most actionable part. For each deferred card, include its **destination**: which sprint or backlog it moved to, or whether it's unscheduled. "Deferred" alone is nearly useless — "deferred to v2/m3 tenant isolation sprint" tells the team exactly where to find it and when it'll be addressed. If a card was deferred and you can't find where it went, flag that explicitly ("destination unclear — may need triage").
- **Review insights** — a brief narrative of significant review findings and rework cycles. What did reviewers catch? What got fixed? This tells the team about the quality assurance process, not just the output.
- **Sprint metrics** — completion counts by type, rework cycles, deferred counts with disposition (backlogged vs. scheduled).
- **Cards delivered** — the full inventory with IDs, types, titles, and a **"Key outcomes"** column. This is the unique value of the gitban details section — each card's acceptance criteria contain rich completion summaries that no one else can see from the git log. Summarize the most important outcome or finding from each card's exit criteria in 1-2 phrases. For bug cards, this might be the root cause confirmed. For feature cards, the key design decision validated. For chores, the measurable improvement achieved. Keep this at the bottom — it's reference material, not the lead.

**What does NOT belong here** — ADRs, design docs, runbooks, and other project documentation are *not* gitban artifacts. They belong in the main PR body (approach, what-changed sections) where every reviewer can see them. The gitban details section is exclusively for gitban-specific organizational data: sprint tags, card IDs, roadmap paths, deferred destinations, review cycle narratives.

**What to leave out:**
- Handle assignments (visible in the cards themselves)
- Timestamps or dates (the git log has these)
- Raw card content or acceptance criteria (that's what `read_card` is for)
- The attribution line (it's in the main body above)

For single-card PRs or small changes, this section can be minimal — just the card ID, roadmap context if relevant, and any documentation references. Don't pad it out.

Omit the entire section if gitban wasn't used for the branch.

## .gitban content in PRs

The `.gitban/` directory is a local/fork workflow artifact. **Do not include `.gitban/` content in PRs targeting repositories that don't use gitban.** A pre-push hook enforces this automatically when isolation is configured. If the push is blocked, the hook will tell you why and how to fix it. If isolation is not yet configured for the target remote, run the MCP `isolate_remote_tool` to enable it.

## Anti-patterns

- Never conclude something is "missing" without reading it first. Metadata listings show structure, not content. Read the actual card/roadmap content before claiming absence.
- When summarizing completed work, inspect done/archived cards too — not just active ones. The PR covers all work on the branch, including finished items.
- Don't write the PR as a transcript of your research. The reader doesn't need to know you read 18 cards — they need to know what changed and why.
- Don't include tables of internal tracking artifacts. If a table appears in the PR, it should contain information the reviewer needs (file paths, test results, API changes) — not process metadata.

## Constraints

- Use gitban MCP tools for all card interactions. Do not read or edit files in `.gitban/cards/` directly.
- No co-authored-by lines in commits.
- Never use `--no-verify` to bypass pre-commit hooks.
- Use `origin/main` for diffs, not local `main`.
