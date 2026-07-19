# Implementation Plan: Type Safety Enforcement in Coder Skill

**Branch**: `011-type-safety-coder` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/011-type-safety-coder/spec.md`

## Summary

Add a "Type Safety" instruction block to `~/.claude/skills/coder/SKILL.md` (the always-loaded `coder` playbook) covering: type-annotated public interfaces by default, no unsafe type escapes without a stated justification, running the project's configured type checker before reporting done, and validating/narrowing types at system boundaries — all scoped to follow the existing repo typing convention rather than introducing a new one. Deliver behavioral test scenarios in `tests/type-safety-coder/` with a bash runner, following the established `tests/skill-routing/` / `tests/live-documentation/` pattern.

## Technical Context

**Language/Version**: Markdown (skill file) + Bash (test runner)

**Primary Dependencies**: Claude Code CLI (`claude -p` for headless test evaluation)

**Storage**: File system — `~/.claude/skills/coder/SKILL.md`, `tests/type-safety-coder/`

**Testing**: Bash runner (`tests/run-type-safety-coder.sh`) + `claude -p` headless evaluation, mirroring `tests/run-live-documentation.sh`

**Target Platform**: Claude Code CLI / Desktop (macOS)

**Project Type**: Configuration/skill project — deliverable is a Markdown instruction block, not application code

**Performance Goals**: N/A (static skill file; no runtime performance requirements)

**Constraints**: Addition must fit within the coder skill's existing structure without pushing the file past a reasonable single-skill length; must not weaken or reorder the existing TDD/SDD/Documentation Sync sections; new instructions must reference the skill's existing "Language and stack conventions" principle (match repo conventions) rather than mandate a specific toolchain

**Scale/Scope**: One instruction block in one existing skill file + 1 test runner + behavioral test scenarios covering the four user stories (P1–P3)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution status**: `.specify/memory/constitution.md` contains the unfilled template — no project constitution has been ratified. No constitutional gates apply.

**Re-check post-design**: No new violations introduced. The change is a documentation/instruction artifact (skill file); no architectural constraints were added.

**Result**: PASS (no gates to evaluate)

## Project Structure

### Documentation (this feature)

```text
specs/011-type-safety-coder/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md         ← Phase 1 output
├── quickstart.md         ← Phase 1 output
├── contracts/
│   └── type-safety-behavior.md ← Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md              ← Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
/Users/taikiogihara/.claude/skills/coder/
└── SKILL.md                          ← MODIFY: add "Type Safety" section

tests/
├── run-type-safety-coder.sh          ← NEW: bash test runner
└── type-safety-coder/
    ├── 001-typed-public-interface.md ← NEW: User Story 1 scenario
    ├── 002-no-unsafe-escape.md       ← NEW: User Story 2 scenario
    ├── 003-type-checker-verification.md ← NEW: User Story 3 scenario
    └── 004-boundary-validation.md    ← NEW: User Story 4 scenario
```

**Structure Decision**: Single-project layout, no `src/` tree — this feature edits an existing global skill file (outside the repo, under `~/.claude/skills/`) and adds repo-local tests that mirror the established `tests/skill-routing/` and `tests/live-documentation/` pattern (bash runner + one Markdown scenario file per behavioral contract).

## Complexity Tracking

*(No constitution violations to justify.)*
