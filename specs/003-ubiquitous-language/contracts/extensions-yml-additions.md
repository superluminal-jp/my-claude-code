# Contract: CLAUDE.md Update

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-09

## Change to `.claude/CLAUDE.md`

In the `## Skills (mandatory routing)` section, replace the existing `ubiquitous-language` routing line:

**Remove**:
```markdown
- `ubiquitous-language` — active in any project conversation where `.specify/ubiquitous-language/` exists; passively collects domain vocabulary candidates and surfaces them at natural conversation pauses without interrupting ongoing tasks
```

**Replace with**:
```markdown
- `ubiquitous-language` — activate when conversation contains business event expressions (past/passive verb+noun: e.g., 「注文が確定された」) or domain vocabulary candidates; passively queues candidates without interrupting; surfaces them at natural pauses (no new candidates in preceding turn)
```

**Rationale**: Trigger is now conversation-content based (FR-013/FR-015/FR-017), not file-presence based. This enables bootstrap prompting even before `docs/ubiquitous-language.md` exists.

---

## Changes to `.specify/extensions.yml`

The simplified skill removes all subcommands. The hook command `ubiquitous-language.collect` no longer exists; it should be updated to `ubiquitous-language` (the single command) in all `before_*` hook arrays.

**Find and replace** in every hook entry under `before_specify`, `before_clarify`, `before_plan`, `before_tasks`, `before_analyze`:

```yaml
# Before
  command: ubiquitous-language.collect

# After
  command: ubiquitous-language
```

All other hook fields (`extension`, `enabled`, `optional`, `prompt`, `description`, `condition`) remain unchanged.
