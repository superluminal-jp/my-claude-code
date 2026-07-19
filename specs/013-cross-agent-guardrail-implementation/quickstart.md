# Quickstart: Validate the Codex CLI Guardrail Implementation

This walks through validating each user story from `spec.md` end-to-end, after implementation. Each section is independently runnable, matching the spec's own "Independent Test" for that story — you don't need every story implemented to validate the ones that are.

## Prerequisites

- Codex CLI installed and on `PATH`.
- This repository cloned locally, with the feature's changes present (either on this branch, or after `install.sh` has run from it).
- `jq`, `shfmt`, `shellcheck`, `yamllint` on `PATH` (already required by this repo's existing hooks — see `.claude/hooks/README.md`).
- Run `bash install.sh` from the repository root at least once, so `~/.codex/AGENTS.md`, `~/.agents/skills/`, and `~/.codex/config.toml`'s `[hooks]` entries exist (User Stories 1–5 validate the *global* deployment, per the spec's Clarifications — not just this repository's working tree).

## User Story 1 — AGENTS.md baseline guidance

1. `cat ~/.codex/AGENTS.md` (or `AGENTS.md` at this repository's root, before install).
2. Confirm all 12 items are present: Q1, Q2, Q4, Q5, Q7–Q14 (see `data-model.md`'s AGENTS.md Entry entity for the exact list).
3. Confirm Q2's entry names no Claude Code-specific tool (`Read`/`Edit`/`Grep`); confirm Q13's entry names no `Claude Memory`; confirm Q14's entry names no `Agent` tool or `subagent_type`.
4. Confirm Q7, Q9, and Q10's entries each state plainly that Codex CLI enforces the item via hook (not phrased as a mere note).
5. Check file size: `wc -c ~/.codex/AGENTS.md` — MUST be under 32768 bytes (FR-011a).

**Expected outcome**: SC-001 and SC-004 hold — a reader with no prior context can determine, for any of the 12 items, whether it's enforced or advisory.

## User Story 2 — Native skill discovery via .agents/skills

1. `ls -la ~/.agents/skills/` — confirm the 9 custom skills (`adr`, `advisor`, `clarifier`, `coder`, `domain-model`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `ubiquitous-language`) are present as symlinks (`ls -la` shows the `->` target).
2. `diff ~/.agents/skills/advisor/SKILL.md ~/.claude/skills/advisor/SKILL.md` — MUST be empty (they're the same file via symlink, not merely similar).
3. From a Codex CLI session in any project, submit a decision/trade-off request (the kind that should trigger `advisor`) and confirm Codex CLI's response reflects `advisor`'s actual `SKILL.md` content, not a generic answer.

**Expected outcome**: SC-006 holds.

## User Story 3 — Real destructive-command blocking

1. Run this feature's new test suite directly against the shared script: `bash tests/run-destructive-command-guard.sh`.
2. From a Codex CLI session in any project, attempt a hard-blocked command (e.g. `git push --force`) — confirm it is denied before execution, with a message matching `contracts/guardrail-script-io.md`'s `destructive-command.sh` reason text.
3. Attempt an `ask`-tier command (e.g. `sudo ls`) — confirm it is either routed to confirmation or denied (never silently allowed).
4. Attempt a benign command (e.g. `ls`) — confirm it is allowed.
5. Repeat step 1 of `tests/run-destructive-command-guard.sh` against Claude Code's own `.claude/hooks/pre-bash.sh` in the same run, to confirm SC-002/SC-003 (parity + zero regression) in one pass.

**Expected outcome**: SC-002, SC-003, SC-005 hold.

## User Story 4 — Real pre-edit blocking

1. Run `bash tests/run-pre-edit-guard.sh`.
2. From a Codex CLI session, attempt to edit a file under `.git/` — confirm it is denied before the edit completes.
3. On a `main`/`master` branch, attempt any edit — confirm it is denied before the edit completes.
4. On a feature branch, attempt an edit outside `.git/` — confirm it is allowed.

**Expected outcome**: SC-007, SC-009 hold.

## User Story 5 — Real post-edit auto-format

1. Run `bash tests/run-post-edit-format-guard.sh`.
2. From a Codex CLI session, edit a `.sh` file with intentionally inconsistent indentation — confirm it is reformatted to 2-space indent (matching `shfmt -w -i 2`) after the edit completes, and any `shellcheck` warnings appear.
3. Edit a `.yaml` file with a lint issue — confirm a `yamllint` warning appears, matching current Claude Code behavior.

**Expected outcome**: SC-008, SC-009 hold.

## User Story 6 — Deduplicate the MCP catalog via `@path` import

1. `cat .claude/rules/mcp.md` (post-install: `cat ~/.claude/rules/mcp.md`) — confirm it contains a `@path` import line, not a standalone MCP table.
2. Open a Claude Code session in any project and confirm the full MCP catalog and usage rule still appear in context (imported from `AGENTS.md`), matching what a Codex CLI session sees natively.
3. Edit `AGENTS.md`'s Q4 entry (e.g. add a test server to the catalog table), re-run step 2, and confirm the change is visible to Claude Code without any second edit to `mcp.md`.
4. **If step 1 shows `.claude/rules/mcp.md` still has standalone content**: this means FR-024's live-session verification found `@path` cannot target a file outside `.claude/` — confirm the fallback is documented (per FR-024/R7) rather than silently left as an unexplained discrepancy.

**Expected outcome**: SC-010 holds, or its documented fallback does.

## Cross-cutting: `install.sh` idempotency (SC-011)

1. On a machine with neither `~/.codex/` nor `~/.agents/` present, run `bash install.sh` once. Confirm `~/.codex/AGENTS.md`, `~/.agents/skills/<name>` (×9), and `~/.codex/config.toml`'s `[hooks]` entries (×3) all exist and are correct.
2. Run `bash install.sh` a second time immediately. Confirm: no duplicated `[hooks]` entries in `~/.codex/config.toml`, no broken symlinks under `~/.agents/skills/`, and `~/.codex/AGENTS.md` is unchanged (byte-identical) if the source `AGENTS.md` didn't change.

**Expected outcome**: SC-011 holds.

## Regression check (all shared-script refactors)

Run the full existing test suite set plus the three new suites together: `for f in tests/run-*.sh; do bash "$f" || echo "FAILED: $f"; done`. All must pass, with particular attention to `run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, and `run-post-edit-format-guard.sh`'s Claude Code-side assertions (SC-003, SC-009 — zero regression from the shared-script extraction).
