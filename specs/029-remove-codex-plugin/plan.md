# Implementation Plan: Remove the codex-plugin-cc Claude Code Plugin

**Branch**: `029-remove-codex-plugin` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/029-remove-codex-plugin/spec.md`

## Summary

Delete `install.sh`'s section 4 (`openai/codex-plugin-cc` marketplace registration and `codex@openai-codex` plugin install/update), renumber and tighten the file's step comments so the remaining sequence (0-3) reads cleanly with no gap or stale reference, and remove the two dead `claude` stub branches from `tests/run-install.sh` that existed solely to satisfy the deleted step. No ADR, README, or README.ja.md change is required — none currently documents this plugin.

## Technical Context

**Language/Version**: Bash only (`install.sh`, `tests/run-install.sh`).

**Primary Dependencies**: `claude` CLI (stubbed in tests), `uvx` (unaffected by this change).

**Storage**: N/A.

**Testing**: `tests/run-install.sh` (isolated-home installer contract); full `tests/run-*.sh` suite as a regression check.

**Target Platform**: Local developer machines running `install.sh` (macOS/Linux, bash).

**Project Type**: Single-repo tooling script (installer) with its own deterministic test harness.

**Performance Goals**: N/A (one-time install script, not latency-sensitive).

**Constraints**: Must remain idempotent (repeated runs converge to the same state); must not remove any other managed-path or MCP-registration behavior.

**Scale/Scope**: One installer section (~9 lines) plus its two associated test stub branches (~5 lines). No new files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution ratified (`.specify/memory/constitution.md` is the unfilled template). Applicable governance comes from `.claude/CLAUDE.md` and its rules, already satisfied:

- `rules/clarifier.md`: no ambiguity gap remains — scope, acceptance criteria, and the no-ADR rationale are all resolved in `spec.md`'s Assumptions section.
- `coder` skill (TDD): the isolated-home installer test (`tests/run-install.sh`) already exercises `install.sh`'s full command log; the task sequence below updates that test's stub *first* per red-green discipline — the stub removal itself has no independent "failing test," so the check is the negative assertion described in FR-004/SC-001 (a `grep` for the retired plugin strings), run before and after the edit.
- `rules/live-documentation.md`: no public contract changes outside `install.sh`'s own behavior, which is self-documenting via its step comments (being tightened in this feature); no README/ADR drift is introduced.
- Close-out ADR check (`.claude/CLAUDE.md` § Close-out): explicitly declined as unwarranted — see spec.md Assumptions.

Gate: **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/029-remove-codex-plugin/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output (N/A — no data entities; states so explicitly)
├── quickstart.md         # Phase 1 output
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by /speckit-plan)
```

### Source Code (repository root)

```text
my-claude-code/
├── install.sh                # edit: delete section 4; renumber/tighten step comments 0-3
└── tests/
    └── run-install.sh        # edit: delete the two dead `plugin marketplace list` / `plugin list` stub branches
```

**Structure Decision**: Single-project tooling change confined to the two files above. No new directories, no contracts (installer has no external interface beyond the CLI commands it issues, already covered by the existing test harness), no data model (no persistent entities — only script logic and comments).

## Complexity Tracking

Not applicable — no constitution violations, no new complexity introduced (net deletion).
