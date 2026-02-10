# Project Guidelines

**Purpose**: Core principles and references for AI coding assistants. **Scope**: This CLAUDE.md lives in user scope (`~/.claude/`) and is loaded for every session.

**Philosophy**: Keep this file concise (<5KB). Details live in `.claude/rules/`, `.claude/skills/`, `docs/`.

---

## Core Principles

1. **Spec first** - Define what to build before deciding how (spec-driven development via GitHub spec-kit)
2. **Code is source of truth** - Documentation reflects implementation, not aspirations
3. **Quality first** - Professional standards, international best practices
4. **Efficiency** - Targeted edits for large files, minimal changes, clear diffs
5. **Maintainability** - Consistent patterns, clear structure, automated quality checks

---

## Quick Reference

### Key Commands

```bash
# Development
npm run dev       # Start development server
npm test          # Run all tests
npm run lint      # Check code quality

# Documentation  
/update-readme    # Sync README
/update-changelog # Add CHANGELOG entry
/validate-docs   # Check documentation accuracy
/quality-check   # Run quality validations (quality-checker subagent)
```

### Project Structure

`project/`: `src/`, `tests/`, `docs/` (architecture, api, guides). `.claude/`: rules, skills, agents, commands, hooks, settings.json. Root: README.md, CHANGELOG.md, CLAUDE.md.

---

## Where to Find Information

### Memory (Global Preferences)

Located in `.claude/memory-entries.md` - Draft entries for Claude Code memory; also applied as reference. Covers global coding governance, Python/TS/React/Next.js standards, AWS & IaC, and authoritative use of `.claude/` and `.cursor/` rules. Add these to product memory for persistence across sessions; assistants should follow them when this scope is loaded.

### Rules (Always Applied)

Rules are the always-applied convention files CLAUDE.md references; they load every session. See `.claude/rules/memory-vs-repo-rules.md` for the Rules vs. Skills vs. Agents table. Located in `.claude/rules/` - these standards apply to all work:

- `spec-driven-development.md` - Spec-first workflow using GitHub spec-kit
- `output-standards.md` - McKinsey-style writing standards (Pyramid Principle, MECE, SCQA, Tufte, 34 named frameworks)
- `file-editing.md` - File modification strategy (targeted edits vs full rewrites)
- `model-selection.md` - When to use Opus/Sonnet/Haiku
- `context-management.md` - Memory, caching, token optimization
- `memory-vs-repo-rules.md` - What lives in Claude Code memory vs. repo rules and skills
- `documentation.md` - Keep docs synchronized with code

### Skills (Auto-Invoked)

Located in `.claude/skills/` - Activate automatically based on task:

- **document-assistant** - McKinsey-style structured business documents (Pyramid Principle, MECE, SCQA)
- **presentation-assistant** - McKinsey-style slide design (Action Titles, Zelazny chart selection)
- **speckit-workflow** - Spec-driven development for code modifications
- **file-editing-strategy** - Efficient editing for large files
- **documentation-management** - Update README, CHANGELOG, API docs

Quality checks and architecture review: use **Subagents** (quality-checker, architecture-reviewer) or `/quality-check`, `/validate-docs`.

### Subagents (Specialized Tasks)

Located in `.claude/agents/` - Delegate specific work. Each agent explicitly applies its corresponding rule.

| Agent | Applied Rule | Purpose |
|-------|-------------|---------|
| `doc-updater.md` | `documentation.md` | Update all documentation atomically |
| `quality-checker.md` | `output-standards.md` | Validate outputs against standards |
| `architecture-reviewer.md` | — | Review system design changes |
| `spec-compliance-reviewer.md` | `spec-driven-development.md` | Verify spec-first workflow compliance |
| `file-edit-reviewer.md` | `file-editing.md` | Review edit efficiency and strategy |
| `context-optimizer.md` | `context-management.md` | Optimize session context usage |
| `model-selector.md` | `model-selection.md` | Recommend model assignments for tasks |
| `rules-organizer.md` | `memory-vs-repo-rules.md` | Organize content across memory/rules/skills |

### Commands (User-Initiated)

Located in `.claude/commands/` - Explicit shortcuts:

- `/speckit` - Run spec-driven development workflow (GitHub spec-kit)
- `/update-readme` - Regenerate README sections
- `/update-changelog` - Add CHANGELOG entry
- `/validate-docs` - Check documentation accuracy
- `/quality-check` - Run all quality validations

### Hooks (Automated)

Configured in `.claude/settings.json` - Automatic actions:

- **PreToolUse** - Block edits on main branch, check spec-kit artifacts
- **PostToolUse** - Format code after Edit/Write
- **SubagentStop** - Suggest next steps (doc-updater, quality-checker, speckit, etc.)
- **Stop** - Final validation and pre-commit checklist

Hooks align with skills and subagents: PreToolUse encourages spec-first (speckit-workflow); PostToolUse keeps formatting consistent; SubagentStop and Stop point to doc-updater, quality-checker, and /speckit commands. User-level hooks live in `$HOME/.claude/hooks/`; per-project hooks use `$CLAUDE_PROJECT_DIR/.claude/hooks/`.

---

## Standards Applied

McKinsey (Pyramid, MECE, SCQA), spec-kit, plain language, Tufte/Zelazny visualization, Keep a Changelog. Full list: `.claude/rules/output-standards.md`.

---

## Workflow

Spec-driven: Specify → Plan → Tasks → Execute. Update docs atomically. Quality-checker subagent for three-stage review (revision, editing, proofreading). Pre-commit validates docs.

---

## Getting Help

Documents → document-assistant; slides → presentation-assistant; code changes → speckit-workflow; docs sync → `/update-readme`, `/update-changelog`; quality → `/quality-check` or quality-checker subagent. See `.claude/rules/`, `.claude/skills/`, `docs/`.

---

## Contributing

Before commit: tests pass, docs updated, CHANGELOG entry, quality checks, pre-commit hook. Hook enforces.

---

## Notes

- Keep this file under 5KB; move details to rules/skills/docs.
- **Context compaction**: When compacting, always preserve the list of modified files and any test/lint commands run.
- Update quarterly; constitution, not manual.

---

**For detailed guidance**, explore `.claude/` directory and `docs/`.

**Last Updated**: 2026-02-07
