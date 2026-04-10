---
name: router
description: Parses code review reports and routes instructions to the executor and planner. Use after a reviewer completes a code review to decide next steps.
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/validate-no-direct-card-edit.sh"
---

Read and follow the instructions at `.claude/skills/router/SKILL.md`.
