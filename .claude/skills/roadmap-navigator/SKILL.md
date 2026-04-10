---
name: roadmap-navigator
description: >
  Navigate, query, and update the gitban roadmap efficiently. Use this skill whenever you need to
  explore the project roadmap, find specific features or projects, check milestone status, update
  roadmap items, or plan work from roadmap content. Trigger for any mention of "roadmap", milestone
  planning, feature tracking, version status, or when the user wants to understand what's planned,
  in progress, or completed at a strategic level. Also use when creating sprint cards from roadmap
  projects, or when updating roadmap status after completing work.
---

# Roadmap Navigator

The roadmap is a hierarchical YAML document that can contain hundreds of items across versions, milestones, features, and projects. Loading it all at once wastes context and makes it hard to find what matters. This skill teaches you to navigate it surgically.

## Hierarchy

```
versions (v1, v2, ...)
  └─ milestones (m1, m2, ...)
      └─ features (kebab-case IDs)
          └─ projects (kebab-case IDs)
```

Each level has a status: `todo`, `in_progress`, or `done`.

## Core Principle: Browse, Read, Take Notes

Navigate the roadmap in three steps:

1. **Browse** with `list_roadmap()` to orient yourself (cheap)
2. **Read** specific items with `read_roadmap(path=...)` to get details (targeted)
3. **Take notes** — write down what's relevant to your current task so you don't have to re-query

### Taking Notes

After you've found the roadmap items relevant to your work, write a scratchpad file summarizing what you learned. This saves you from re-reading the roadmap later in the session when you need to reference feature IDs, project statuses, dependency chains, or TDD specs.

Write your notes to `.gitban/agents/{role}/scratchpad.md` (where `{role}` is your agent role, or `notes` if you're working interactively). Include:

- The roadmap paths you explored and why they're relevant
- Key IDs, statuses, and relationships you'll need to reference
- TDD specs or success criteria that inform your current work
- Dependencies or blockers you discovered

Keep it concise — this is a working document for the current session, not permanent documentation. Future sessions should re-query the roadmap rather than trust stale notes.

**Example:**

```markdown
# Roadmap Notes — INFRACORE sprint

## Relevant path: v1/m1/infra-core
- Status: in_progress (3/6 projects done)
- Projects remaining:
  - service-accounts (sequence: 3, depends_on: [terraform-setup]) — todo
  - monitoring-setup (sequence: 5) — todo
  - ci-cd-pipeline (sequence: 6, depends_on: [service-accounts]) — todo

## TDD specs I need:
- service-accounts: "3 service accounts created with least-privilege IAM bindings"
- ci-cd-pipeline: "GitHub Actions workflow triggers terraform plan on PR, apply on merge"

## Dependencies:
- ci-cd-pipeline blocked by service-accounts
- monitoring-setup is independent, can parallelize
```

This pattern is especially valuable when you're about to create sprint cards, enrich existing cards with roadmap context, or plan work across multiple features — you capture the landscape once and work from your notes.

## Tool Cost Awareness

`list_roadmap()` and `read_roadmap()` have very different token costs. Understanding which to reach for matters.

**`list_roadmap(path=...)`** — safe for browsing. Returns metadata only (IDs, titles, statuses, child counts). No descriptions or specs unless you explicitly request them with `include_fields`. Always use `path` to scope your query.

**`read_roadmap(path=...)`** — returns full YAML content including all nested children. The tool has a built-in safety valve: if the content exceeds ~20k tokens without pagination, it returns a size warning and suggestion instead of dumping the content. When you hit that guard, narrow your `path` or add pagination (`offset`/`limit` or `around_line`/`context_lines`).

**`search_roadmap(query=...)`** — generally safe. Returns breadcrumbs and snippets, not full content.

**`roadmap://current`** (MCP resource) — loads the entire raw YAML. Almost never what you want. Use the tools instead.

## Navigation Patterns

### Drilling Down (most common)

Start broad, narrow progressively. Each step gives you the IDs you need for the next.

```
list_roadmap()                          → see versions
list_roadmap(path="v1")                 → see milestones in v1
list_roadmap(path="v1/m2")             → see features in m2
list_roadmap(path="v1/m2/some-feature") → see projects in feature
read_roadmap(path="v1/m2/some-feature") → full details when needed
```

### Searching (when you know a keyword)

```
search_roadmap(query="terraform")
search_roadmap(query="auth", include_archived_versions=True)
```

Search returns breadcrumbs showing where each match lives in the hierarchy, so you can jump straight to the right path with `read_roadmap(path=...)`.

### Selective Field Loading

When you need a bit more than metadata but not full content:

```
list_roadmap(path="v1/m1", include_fields=["description"])
list_roadmap(path="v1/m1/infra-core", include_fields=["tdd_spec", "owner"])
```

Available extra fields vary by level:
- **versions**: description, start_date, target_completion, docs_ref
- **milestones**: description, success_criteria, depends_on, docs_ref
- **features**: description, depends_on, docs_ref
- **projects**: description, owner, tdd_spec, docs_ref, depends_on

### Paginated Reading

When `read_roadmap` hits the size guard, use pagination:

```
read_roadmap(path="v1", offset=0, limit=100)
read_roadmap(path="v1", offset=100, limit=100)
read_roadmap(path="v1", around_line=150, context_lines=25)
```

The response includes pagination metadata (total_lines, has_more) so you know when to stop.

## Common Tasks

### "What's the current status?"

```
list_roadmap()                    → version statuses + descendant counts
list_roadmap(path="v1")           → milestone statuses
```

Look at `node_counts.total_descendants` to gauge size before drilling deeper.

### "What's in progress right now?"

```
list_roadmap(path="v1")           → find in_progress milestones
list_roadmap(path="v1/m2")        → find in_progress features within
```

Filter results by status yourself — the tools return all items at the requested level.

### "Find everything related to X"

```
search_roadmap(query="X")
```

Then drill into specific matches with `read_roadmap(path=...)`.

### "Update a project status"

```
upsert_roadmap({"status": "done"}, path="v1/m1/infra-core/terraform-setup")
```

Partial updates — only the fields you provide are changed. Everything else is preserved.

### "Add a new feature or project"

Read `roadmap://schema` (MCP resource) if you need to confirm required fields. Then:

```
upsert_roadmap({
  "id": "new-feature",
  "title": "New Feature Title",
  "description": "What it does and why",
  "status": "todo",
  "projects": {}
}, path="v1/m2/new-feature")
```

### "Delete something from the roadmap"

Preview first with dry_run, then confirm:

```
delete_from_roadmap(path="v1/m1/old-feature", dry_run=True)   → see cascade
delete_from_roadmap(path="v1/m1/old-feature", confirm=True)    → execute
```

### "Create sprint cards from roadmap projects"

1. `list_roadmap(path="v1/m2/target-feature")` — get project list
2. `read_roadmap(path="v1/m2/target-feature/specific-project")` — get tdd_spec and details
3. Create gitban cards using the feature ID as the sprint tag
4. The roadmap informs cards but cards never reference back into the roadmap

## Rules

- **Roadmap is strategic, Gitban is tactical.** The roadmap tracks what and when. Gitban tracks who and how. Don't put daily task details in the roadmap.
- **Milestones are objectives, not work lists.** A milestone states what's true when done ("any agent can connect regardless of transport"), not what changes ("add HTTP transport"). Features describe the path to the outcome. Design happens during development, not in the roadmap.
- **Cards reference the roadmap, not the reverse.** The roadmap is the long-lived source of truth. Gitban cards are semi-ephemeral. Never put card IDs or links in roadmap content.
- **Update roadmap status at milestone boundaries**, not after every card. Mark a feature done when all its projects are done. Mark a milestone done when all features are done.
- **Use `node_counts` to gauge depth.** If a version shows `total_descendants: 66`, don't read the whole version — drill into specific milestones or features.
- **Link documents via `docs_ref`.** Every level supports an optional `docs_ref` field pointing to the node's primary reference document. When creating or updating roadmap items that have associated docs, set this field. This is how the roadmap connects to its static documentation — the roadmap stays lean (titles, statuses, sequencing) while `docs_ref` points to the depth.

  **Document hierarchy and where each lives on the roadmap:**

  | Document type | Path | Purpose | Typical roadmap level |
  |--------------|------|---------|----------------------|
  | **PRD** | `docs/prds/` | Product vision, user segments, scope, delivery phases | Milestone or feature |
  | **ADR** | `docs/adr/` | Architectural decision and tradeoffs | Feature or project |
  | **Design doc** | `docs/designs/` | Implementation plan bridging ADR to sprint cards | Project |

  - **PRDs** attach at the **milestone** level (or occasionally a large feature). They define *what* to build and *for whom* — the product strategy that drives everything below. A milestone without a PRD is just a title.
  - **ADRs** attach at the **feature** level (or project, for narrowly-scoped decisions). They resolve *why this architecture* — the durable technical decision. A feature may spawn multiple ADRs for different architectural questions.
  - **Design docs** attach at the **project** level. They translate an ADR into *how to build it* — detailed enough that sprint cards become mechanical to create.

  When a node already has a `docs_ref` and you need to link an additional document at the same level, link the new document one level down. For example, if a feature already has an ADR linked and you write a design doc, link the design doc on the project beneath the feature.

  **The flow**: PRD (vision) informs ADRs (architecture) which inform design docs (implementation). Each references the one above it. The roadmap is the index that connects them all via `docs_ref`.

## MCP Resources (read-only context)

These are available via MCP resource reads if you need reference material:

- `roadmap://schema` — JSON schema with required fields per level
- `roadmap://usage-guide` — comprehensive usage documentation
- `roadmap://current` — raw YAML (caution: can be very large, prefer tools)
