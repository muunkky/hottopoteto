---
name: reviewer
description: Architectural code reviewer for gitban sprint cards. Evaluates for tech debt, coupling, ADR violations, and TDD/IaC/DaC compliance.
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/validate-no-direct-card-edit.sh"
---

Read and follow the instructions at `.claude/skills/reviewer/SKILL.md`.
