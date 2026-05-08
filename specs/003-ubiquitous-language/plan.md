# Implementation Plan: Ubiquitous Language Skill Simplification

**Branch**: `feature/003-ubiquitous-language` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-ubiquitous-language/spec.md`

## Summary

Simplify the `ubiquitous-language` Claude Code skill by: (1) reducing the interface to a single `/ubiquitous-language` slash command with no subcommands, (2) moving UL storage from `.specify/ubiquitous-language/` to `docs/ubiquitous-language.md` and `docs/context-map.md`, (3) rewriting SKILL.md as a concise linear playbook, and (4) updating the CLAUDE.md routing rule to use content-based trigger detection instead of file-presence detection. All speckit references are removed from the skill.

## Technical Context

**Language/Version**: Markdown (Claude Code skill playbook)
**Primary Dependencies**: Claude Code skill system (`SKILL.md` loaded by Claude Code harness)
**Storage**: `docs/ubiquitous-language.md`, `docs/context-map.md` (markdown files at project root)
**Testing**: Manual session-based validation per `quickstart.md` test cases
**Target Platform**: Claude Code (CLI, VS Code extension, web — all clients)
**Project Type**: Claude Code skill (prompt instruction file)
**Performance Goals**: Zero perceptible AI response delay from passive collection (SC-004)
**Constraints**: Single slash command; no speckit references in skill files (SC-003)
**Scale/Scope**: Per-project UL; ≤ 30 entries per Bounded Context section (v1)

## Constitution Check

Constitution file contains unfilled template only — no ratified principles to check against. No gates apply.

## Project Structure

### Documentation (this feature)

```text
specs/003-ubiquitous-language/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   ├── skill-interface.md          ← Phase 1 output
│   └── extensions-yml-additions.md ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — not created here)
```

### Source Files (modified by this feature)

```text
.claude/
├── CLAUDE.md                                    ← update routing rule (1 line)
└── skills/ubiquitous-language/
    ├── SKILL.md                                 ← complete rewrite
    ├── ubiquitous-language-template.md          ← update paths + heading format
    └── context-map-template.md                  ← update paths

docs/                                            ← created by skill at runtime (not by implementation)
├── ubiquitous-language.md
└── context-map.md
```

**Structure Decision**: Skill-only feature — no `src/`, no `tests/` directories. All changes are to Markdown instruction files under `.claude/`. Runtime output files (`docs/`) are created by the skill during user interaction, not during implementation.

## Complexity Tracking

No Constitution violations.
