# Implementation Plan: Remove /verify-config Verification Feature

**Branch**: `024-remove-verify-config` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/024-remove-verify-config/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Delete the `/verify-config` verification feature in its entirety — the skill
(`.claude/skills/verify-config/SKILL.md`), the project-scoped subagent it
forks into (`.claude/agents/verification-runner.md`), and its dedicated test
suite (`tests/run-verification-agent.sh`) — and remove every reference to it
from README.md and README.ja.md, leaving no dangling instruction, command, or
test. Research (R1) found the original request's Codex-sync footprint
(`tests/run-codex-sync.sh` SYNC-08/09, `.codex/README.md`) no longer exists —
already retired by `specs/021-codex-official-import` — so the actual edit
surface is smaller than originally assumed: three file deletions plus edits to
two README files.

## Technical Context

**Language/Version**: N/A — this feature edits Markdown (skill/agent
frontmatter + prose, README) and deletes one Bash test script; no new code is
written.

**Primary Dependencies**: None introduced or removed at the dependency level.

**Storage**: N/A

**Testing**: Existing `tests/run-*.sh` Bash behavior suites (deterministic,
repository-file inspection only, per this repo's existing convention). No new
test suite is added; `tests/run-verification-agent.sh` is deleted along with
its subject.

**Target Platform**: This repository itself (a Claude Code / Codex CLI
configuration source repo), run locally via `bash`/`zsh` on macOS/Linux.

**Project Type**: Single project — configuration repository, not a
library/service/app.

**Performance Goals**: N/A (no runtime component)

**Constraints**: Leave zero dangling references (FR-007); leave the
"earlier version" cleanup lists in both READMEs untouched (FR-010); leave
historical `specs/` directories untouched (FR-008).

**Scale/Scope**: 3 file deletions, 2 file edits (README.md, README.ja.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled template — this project has
not ratified a project-specific constitution. No gates to evaluate beyond the
repository's own `.claude/rules/` (already applied: `live-documentation.md`
for keeping README accurate, `git-workflow.md` for one-logical-change-per-commit,
`clarifier.md` for the scope-confirmation already completed in conversation
before this spec was written). No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/024-remove-verify-config/
├── plan.md              # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by /speckit-plan)
```

No `contracts/` directory — see research.md R3 (no external interface exposed
by this internal maintenance feature).

### Source Code (repository root)

Existing single-project layout; no new directories. Files touched:

```text
my-claude-code/
├── README.md                              # edit: remove verify-config/verification-runner description
├── README.ja.md                           # edit: Japanese mirror of the same
├── .claude/
│   ├── skills/
│   │   └── verify-config/SKILL.md         # delete
│   └── agents/
│       └── verification-runner.md         # delete
└── tests/
    └── run-verification-agent.sh          # delete
```

**Structure Decision**: No structural change to the repository — this is a
pure removal within the existing `.claude/skills/`, `.claude/agents/`, and
`tests/` directories, plus documentation edits in the two existing READMEs.

## Complexity Tracking

*No constitution violations — this section is not applicable.*
