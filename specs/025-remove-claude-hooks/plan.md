# Implementation Plan: Remove .claude/hooks/ Entirely

**Branch**: `025-remove-claude-hooks` | **Date**: 2026-08-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/025-remove-claude-hooks/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Delete `.claude/hooks/` (7 files) with no replacement, removing all automatic
Claude Code enforcement this repository provided (destructive-command
blocking, edit protection, post-edit formatting, prompt-secret scanning,
Spec Kit auto-update, status line). Update `.claude/settings.json` (drop
`hooks`/`statusLine` keys), `install.sh` (drop the dangling `chmod`, keep
`sync_path "hooks"` as the uninstall path, per spec-024 precedent), rewrite
the Claude/Codex enforcement comparison table in README.md/README.ja.md and
AGENTS.md's now-false "unaffected" claim, edit 4 guardrail test suites to
drop only their now-dead wrapper assertions, delete `tests/run-speckit-update.sh`
entirely, and propose an ADR recording this as an architecturally significant
decision. `scripts/guardrails/*.sh` and `specs/013-cross-agent-guardrail-implementation/`
are explicitly out of scope and left untouched.

## Technical Context

**Language/Version**: N/A — Markdown/JSON/Bash edits and deletions, no new code.

**Primary Dependencies**: None introduced or removed.

**Storage**: N/A

**Testing**: Existing `tests/run-*.sh` Bash suites; 4 edited (drop dead
assertions), 1 deleted (`run-speckit-update.sh`), rest untouched.

**Target Platform**: This repository itself, run locally via bash/zsh on
macOS/Linux, and every other project on the machine once `install.sh` is
next run (loses this repo's hook-based enforcement at that point).

**Project Type**: Single project — configuration repository.

**Performance Goals**: N/A

**Constraints**: Zero dangling references (FR-005/007/008); `scripts/guardrails/*.sh`,
`.claude/rules/permissions.md`, and historical `specs/` directories
untouched (FR-010/011/012); comparison table rewritten with accurate
inverted content, not merely stripped (FR-006).

**Scale/Scope**: 8 file deletions (7 hooks + 1 test), edits to 7 files
(settings.json, install.sh, README.md, README.ja.md, AGENTS.md, and the
4 guardrail test suites count as 4 more — 6 edited files total), 1 new ADR.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled template — no
project-specific constitution ratified. Applicable repository rules already
satisfied: `clarifier.md` (two rounds of `AskUserQuestion` completed before
this spec was written), `permissions.md` (this is exactly the kind of
destructive, security-relevant action the rule requires confirming before
executing — confirmed), `live-documentation.md` (README/AGENTS.md rewrites
are scoped in the same change, not deferred), `CLAUDE.md` close-out (ADR
proposal included as FR-014/SC-005, not silently skipped). No violations to
justify.

## Project Structure

### Documentation (this feature)

```text
specs/025-remove-claude-hooks/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md              # /speckit-tasks output, not created here
```

No `contracts/` — see research.md R3.

### Source Code (repository root)

```text
my-claude-code/
├── README.md                              # edit: ~12 locations, incl. table rewrite
├── README.ja.md                           # edit: ~8 locations, incl. table rewrite
├── AGENTS.md                              # edit: 3 locations
├── install.sh                             # edit: drop chmod line, reword comments
├── .claude/
│   ├── settings.json                      # edit: drop hooks/statusLine keys
│   └── hooks/                             # delete: entire directory (7 files)
└── tests/
    ├── run-destructive-command-guard.sh   # edit: drop CLAUDE_HOOK assertions
    ├── run-pre-edit-guard.sh              # edit: drop CLAUDE_HOOK assertions
    ├── run-post-edit-format-guard.sh      # edit: drop CLAUDE_HOOK assertions
    ├── run-prompt-secret-guard.sh         # edit: drop CLAUDE_HOOK assertions
    └── run-speckit-update.sh              # delete: entire file
```

Plus a new `docs/adr/NNNN-remove-claude-hooks.md` proposed during close-out
(exact number assigned by the `adr` skill at that time).

**Structure Decision**: No structural change — deletions and edits within
existing directories, plus one new ADR file via the `adr` skill's own
process (not hand-authored here).

## Complexity Tracking

*No constitution violations — not applicable.*
