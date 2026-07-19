# Implementation Plan: Codex CLI Guardrail Implementation (AGENTS.md + Native Hooks)

**Branch**: `013-cross-agent-guardrail-implementation` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-cross-agent-guardrail-implementation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Turn spec 012's Codex CLI-relevant decisions into real, globally-installed artifacts. Author a root-level `AGENTS.md` carrying the 12 prose-appropriate items; extract three shared guardrail scripts (destructive-command blocking, pre-edit blocking, post-edit formatting) out of the existing `.claude/hooks/pre-bash.sh` / `pre-edit.sh` / `post-edit-format.sh`, add a Codex CLI adapter for each; make the 9 custom skills discoverable to Codex CLI's native `.agents/skills` scan via symlinks; and extend this repository's existing `install.sh` — which already copies `.claude/` to `~/.claude/` for every project on the machine — to deploy all of the above globally (`~/.codex/AGENTS.md`, `~/.agents/skills/`, Codex CLI hook registration). Separately, restructure `.claude/rules/mcp.md` to `@path`-import `AGENTS.md`'s MCP catalog entry instead of duplicating it — the one item in this feature where a Claude Code-side file, not just a new Codex CLI-side artifact, gets rewritten.

## Technical Context

**Language/Version**: Bash (POSIX-leaning, matching `.claude/hooks/*.sh`'s existing `#!/usr/bin/env bash` + `set -euo pipefail` convention); Markdown for `AGENTS.md`; TOML for Codex CLI's hook/skill configuration surface (`~/.codex/config.toml`)

**Primary Dependencies**: `jq` (JSON stdin parsing — already required by every existing hook in this repo), `shfmt`/`shellcheck` (already required by `post-edit-format.sh` and this repo's own `post-edit-format.sh` lint gate, which will lint every new `.sh` file this feature adds), Codex CLI itself (required to complete FR-010/FR-022/FR-024/FR-028's live-session re-verification steps)

**Storage**: Plain files only, no database. New or changed: `AGENTS.md` (root), `scripts/guardrails/*.sh` (3 new shared scripts), `.codex/hooks/*.sh` (3 new Codex CLI adapter scripts), `install.sh` (extended), `.claude/hooks/pre-bash.sh` / `pre-edit.sh` / `post-edit-format.sh` (refactored to thin wrappers), `.claude/rules/mcp.md` (restructured to a `@path` import), `tests/run-*.sh` + fixtures (3 new suites)

**Testing**: Bash-based behavior test suites, following this repository's existing `tests/run-<feature>.sh` + `tests/<feature>/` fixture-directory convention (precedent: `tests/run-live-documentation.sh`, `tests/run-skill-routing.sh`). One suite per shared script (FR-012), each run against the shared script directly and against both integration points that call it (the existing Claude Code hook, the new Codex CLI adapter) to prove FR-009/018/021's zero-regression requirement and SC-002's cross-tool parity requirement in one pass.

**Target Platform**: Developer machines running Claude Code and Codex CLI locally (macOS/Linux — matches `install.sh`'s existing `command -v` preflight checks and lack of Windows-specific paths; this feature does not add Windows support beyond what already exists)

**Project Type**: Single project. This repository *is* the deliverable — a distributable global configuration installed via `install.sh` — not an application with separate frontend/backend tiers.

**Performance Goals**: No explicit target beyond "stays fast enough not to be noticeable." Existing hooks run under a 10–15s `timeout` in `.claude/settings.json`; new Codex CLI adapters should target the same order of magnitude, since they wrap the same shared-script logic.

**Constraints**:
- `AGENTS.md` MUST fit Codex CLI's 32 KiB default `project_doc_max_bytes` budget (FR-011a).
- Every shared script MUST produce byte-identical allow/deny/ask decisions to today's `.claude/hooks/*.sh` for every existing behavior — zero regression (FR-009, FR-018, FR-021).
- `install.sh`'s extension MUST follow its existing idempotent, blunt-overwrite `sync_path()` pattern (`rm -rf "$dst"; cp -R "$src" "$dst"`), not introduce a different install style (see Research R6).
- Cursor is out of scope entirely (spec FR-015) — no Cursor-facing code, config, or claim is introduced anywhere in this plan.

**Scale/Scope**: 3 shared scripts extracted from 3 existing hooks; 3 new Codex CLI adapter scripts; 1 new `AGENTS.md` (~12 entries, budget-constrained); 9 skill symlinks (repo-local) + their global counterparts via `install.sh`; 1 `install.sh` extension (4 new deployment steps); 1 restructured rules file (`mcp.md`); 3 new test suites.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template (placeholder principles only — `[PRINCIPLE_1_NAME]` etc. were never replaced). No project-specific gates are defined. **Gate: PASS (vacuously — no constitution to violate).**

In the absence of a formal constitution, this repository's own `.claude/hooks/README.md` and `.claude/rules/*.md` are its de facto engineering conventions. The closest thing to a "gate" here is: match `.claude/hooks/*.sh`'s existing bash/`shellcheck`/`shfmt` style, and match `install.sh`'s existing idempotent sync pattern. Neither is a blocking constitutional gate; both are captured as Constraints above, and the second is enforced mechanically — `.claude/hooks/post-edit-format.sh` (soon to be one of this feature's own subjects) lints every `.sh` file this feature adds or edits as it's written.

**Post-Phase-1 re-check**: No new violations introduced by the Phase 1 design (data model, contracts, quickstart) — see [research.md](./research.md) R1–R7 for the specific technical decisions that keep this feature within the existing repo's conventions rather than introducing new ones.

## Project Structure

### Documentation (this feature)

```text
specs/013-cross-agent-guardrail-implementation/
├── spec.md                        # Feature spec + Clarifications (this feature's WHAT/WHY)
├── plan.md                        # This file (/speckit-plan command output)
├── research.md                    # Phase 0 output — R1-R7 technical decisions
├── data-model.md                  # Phase 1 output — entities from spec's Key Entities section
├── contracts/
│   └── guardrail-script-io.md     # Phase 1 output — shared script stdin/stdout contract
├── quickstart.md                  # Phase 1 output — how to validate this feature end-to-end
├── checklists/
│   └── requirements.md            # Spec quality checklist (16/16 passing)
└── tasks.md                       # Phase 2 output (/speckit-tasks command — NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
AGENTS.md                              # NEW — root-level source; deployed to ~/.codex/AGENTS.md by install.sh (FR-025)

scripts/
├── check-mcp-consistency.sh           # existing, unchanged
└── guardrails/                        # NEW
    ├── destructive-command.sh         # shared logic for Q6 — extracted from .claude/hooks/pre-bash.sh
    ├── pre-edit-block.sh              # shared logic for Q9/Q10 — extracted from .claude/hooks/pre-edit.sh
    └── post-edit-format.sh            # shared logic for Q7 — extracted from .claude/hooks/post-edit-format.sh
    # I/O contract for all three: contracts/guardrail-script-io.md

.claude/
├── hooks/
│   ├── pre-bash.sh                    # MODIFIED — thin wrapper calling scripts/guardrails/destructive-command.sh
│   ├── pre-edit.sh                    # MODIFIED — thin wrapper calling scripts/guardrails/pre-edit-block.sh
│   └── post-edit-format.sh            # MODIFIED — thin wrapper calling scripts/guardrails/post-edit-format.sh
├── rules/
│   └── mcp.md                         # MODIFIED — @path import instead of standalone MCP catalog content (FR-023)
└── skills/
    └── {adr,advisor,...}/SKILL.md     # unchanged — remains the single source; .agents/skills/ symlinks to these

.agents/
└── skills/
    └── {adr,advisor,...}              # NEW — symlinks to ../../.claude/skills/{name} (FR-014); speckit-* entries here are
                                        # pre-existing, gitignored, untouched by this feature

.codex/
└── hooks/                             # NEW — adapter scripts, deployed to ~/.codex/hooks/ by install.sh (FR-027)
    ├── destructive-command-adapter.sh
    ├── pre-edit-adapter.sh
    └── post-edit-adapter.sh

install.sh                              # MODIFIED — 4 new deployment steps (AGENTS.md, .agents/skills symlinks,
                                         # Codex CLI hook registration in ~/.codex/config.toml); existing steps unchanged

tests/
├── run-destructive-command-guard.sh    # NEW — covers FR-006/007/008/009 (Q6)
├── run-pre-edit-guard.sh               # NEW — covers FR-016/017/018 (Q9/Q10)
├── run-post-edit-format-guard.sh       # NEW — covers FR-019/020/021 (Q7)
└── <fixtures under tests/<name>/, matching the existing tests/live-documentation/, tests/skill-routing/ pattern>
```

**Structure Decision**: Single project. Shared guardrail logic lives in a new `scripts/guardrails/` directory at the repository root — following the existing `scripts/check-mcp-consistency.sh` precedent — rather than under `.claude/`, since each script is consumed by both a Claude Code hook and a Codex CLI adapter; nesting it inside `.claude/` would misrepresent it as Claude Code-specific. `.claude/hooks/*.sh` become thin wrappers around the shared scripts rather than being deleted, preserving today's exact `settings.json` hook wiring and behavior. Codex CLI adapter scripts live under a new `.codex/hooks/` (mirroring `.claude/hooks/`'s naming), deployed globally by `install.sh` exactly as `.claude/hooks/` already is.

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
