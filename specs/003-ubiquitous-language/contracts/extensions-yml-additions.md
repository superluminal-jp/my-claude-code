# Contract: extensions.yml Additions

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-08

## Changes to `.specify/extensions.yml`

Add `ubiquitous-language.collect` as an **optional** hook to each relevant `before_*` key. The hook is optional so projects without a bootstrapped UL can proceed without interruption.

### YAML additions (per `before_*` key)

```yaml
- extension: ubiquitous-language
  command: ubiquitous-language.collect
  enabled: true
  optional: true
  prompt: Run ubiquitous language collection/validation before this phase?
  description: Validate UL coverage and surface new candidates before generating artifacts
  condition: null
```

### Keys receiving the new hook entry

- `before_specify`
- `before_clarify`
- `before_plan`
- `before_tasks`
- `before_analyze`

### Keys intentionally excluded

- `before_implement`: Implementation phase reads UL but does not collect; drift detection happens post-implementation via `/ubiquitous-language check`
- `before_checklist`: Lightweight phase; UL validated in prior steps
- `before_taskstoissues`: Downstream conversion; UL state unchanged

### Ordering within existing hook arrays

Insert **after** any existing hooks in the array, so existing mandatory hooks (e.g., `speckit.git.feature`) run first. This is ordering-safe because the UL hook is optional and idempotent.

---

## CLAUDE.md Addition

In `.claude/CLAUDE.md` under the `## Skills (mandatory routing)` section, add one routing rule:

```markdown
- `ubiquitous-language` — active in any project conversation where `.specify/ubiquitous-language/` exists; passively collects domain vocabulary candidates and surfaces them at natural conversation pauses without interrupting ongoing tasks
```

This enables conversational-mode collection (FR-030–FR-032) without requiring a speckit command.
