---
description: Verify the shared Claude Code and Codex configuration
---

Read `.claude/skills/verify-config/SKILL.md` from the current repository and
follow its verification procedure exactly. Do not modify any files. Also run
`tests/run-codex-sync.sh` and `tests/run-prompt-secret-guard.sh` when present,
and include their outcomes in the same concise pass/fail checklist.

Ignore the skill's `context: fork` / `agent:` frontmatter — those select Claude
Code's forked-subagent execution, which Codex has no equivalent for. The numbered
checks and the report format are what this prompt reuses; run them inline.
