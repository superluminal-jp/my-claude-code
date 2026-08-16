# Implementation Plan: Remove Codex CLI Support and All Codex References

**Branch**: `031-remove-codex-support` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/031-remove-codex-support/spec.md`

## Summary

Delete the root `AGENTS.md`, strip every Codex mention from `README.md`/`README.ja.md` and `install.sh`'s header comment, delete the two dedicated Codex verification suites (`tests/run-codex-references.sh`, `tests/run-codex-drift.sh`), remove the Codex-specific check inside two surviving test suites (`tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`), reword one comment in `tests/run-mcp-startup.sh`, reword `.gitignore`'s Codex-directory comment (keeping the ignore rules themselves), and add a new ADR (`0010`) that supersedes ADR-0004. `specs/`, `docs/adr/0002-*`/`0004-*` bodies, and Spec Kit's own `codex`-integration bookkeeping stay untouched.

## Technical Context

**Language/Version**: Markdown (README, ADR) and Bash (`install.sh`, `tests/run-*.sh`). No application code.

**Primary Dependencies**: None new. Existing test harness uses `grep`/`jq`/`bash` only, per `tests/run-*.sh` conventions already in place.

**Storage**: N/A.

**Testing**: `tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh` (suites edited directly); full `tests/run-*.sh` set as a regression baseline, compared against the pre-change baseline captured in research.md R12 (two suites already fail on `main` for reasons unrelated to this feature).

**Target Platform**: Local developer machines and any CI running this repository's own test suites (macOS/Linux, bash).

**Project Type**: Single-repo documentation + tooling-script change with its own deterministic shell test harness. No frontend/backend split.

**Performance Goals**: N/A — documentation and one-time verification scripts, not latency-sensitive.

**Constraints**: Must not edit any file under `specs/`; must not edit `docs/adr/0002-*.md` at all, nor `docs/adr/0004-*.md` beyond its Status line; must not modify `.specify/integrations/codex.manifest.json` or the `codex` entry in `.specify/extensions/.registry`; must keep `.gitignore`'s `.codex/`/`.agents/` ignore rules.

**Scale/Scope**: One file deleted (`AGENTS.md`, 90 lines), two files deleted (`tests/run-codex-references.sh` 172 lines, `tests/run-codex-drift.sh` 152 lines), five files edited (`README.md`, `README.ja.md`, `install.sh`, `tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh`, `.gitignore` — seven, not five), one file added (`docs/adr/0010-*.md`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution ratified (`.specify/memory/constitution.md` is the unfilled template). Applicable governance comes from `.claude/CLAUDE.md` and its rules:

- `rules/clarifier.md`: no ambiguity gap remains — scope, exclusions, and the ADR-0004-status correction are all resolved in `spec.md` (Edge Cases, Assumptions, and the corrections applied during this planning pass).
- `coder` skill (TDD/red-green): each edited test suite's Codex-specific check is a negative assertion (SC-001's repository-wide grep) run before and after the edit, per the same discipline spec 029 used — no synthetic failing test is fabricated for a pure deletion/removal.
- `rules/live-documentation.md`: this feature *is* the drift/proximity/no-redundancy/intermediate-artifact-isolation cleanup — every doc and test edit lands in the same change as the artifact it describes going away. No new documentation is introduced that would itself need a Documentation Artifact.
- Close-out ADR check (`.claude/CLAUDE.md` § Close-out): required and in scope — FR-009/FR-010, User Story 4. This reverses the operative Codex-relationship decision (ADR-0004), which is exactly the case the ADR policy exists for.

Gate: **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/031-remove-codex-support/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A — no data entities; states so explicitly)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks — not created by /speckit-plan)
```

### Source Code (repository root)

```text
my-claude-code/
├── AGENTS.md                              # delete entirely
├── README.md                              # edit: remove all Codex mentions (§ Codex CLI support, bullets, tree row, verification list, integration example)
├── README.ja.md                           # edit: mirror the above in Japanese
├── install.sh                             # edit: rewrite header comment (lines 6-9), drop Codex/AGENTS.md/ADR-0004 references
├── .gitignore                             # edit: reword the `.codex/`/`.agents/` comment (lines 76-78); keep the two ignore lines
├── docs/adr/
│   └── 0010-remove-codex-cli-support.md   # add: supersedes ADR-0004
└── tests/
    ├── run-codex-references.sh            # delete entirely
    ├── run-codex-drift.sh                 # delete entirely
    ├── run-subagent-delegation.sh         # edit: remove the R5 cross-agent-parity block (lines ~19, 131-141)
    ├── run-digital-agency-frontend-skill.sh  # edit: remove the SYNC-SKILL-06 check (lines ~97-106)
    └── run-mcp-startup.sh                 # edit: reword one comment line (line 6)
```

**Structure Decision**: Single-project documentation/tooling change. No new directories, no contracts (none of the edited files expose an external interface beyond what the existing `tests/run-*.sh` harness already verifies), no data model (no persistent entities — only prose, comments, and shell-script assertions).

## Complexity Tracking

Not applicable — no constitution violations. The one added file (the new ADR) is required by this repository's own governance for reversing a recorded decision, not incidental complexity.
