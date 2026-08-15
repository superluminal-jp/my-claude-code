# Feature Specification: Remove scripts/ Entirely

**Feature Branch**: `027-remove-scripts`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Delete scripts/ entirely: the 4 scripts/guardrails/*.sh files, their 4 corresponding dedicated test suites, and the unrelated scripts/check-mcp-consistency.sh (confirmed via AskUserQuestion as a separate, deliberate decision). Third step in a decision arc after specs/025 (ADR-0005) and specs/026 (ADR-0006). Cascading changes to install.sh, README.md/README.ja.md, permissions.md, mcp.md. New ADR (0007) referencing 0005/0006, which stay unmodified."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - scripts/ is gone with no dangling references (Priority: P1)

As the maintainer, after deleting `scripts/` in its entirety I want every document that described its contents as active tooling to reflect the new reality, so nothing misleads a future session into running or relying on a script that no longer exists.

**Why this priority**: Same principle as specs/024–026: a stale "run this script" instruction is worse than no instruction, because it fails at the worst time — when someone actually tries to follow it.

**Independent Test**: `scripts/` does not exist. A repository-wide search for `scripts/guardrails` and `scripts/check-mcp-consistency` returns no live hits outside historical `specs/` directories.

**Acceptance Scenarios**:

1. **Given** `scripts/guardrails/` currently has 4 files and `scripts/check-mcp-consistency.sh` sits alongside it, **When** the removal is complete, **Then** the `scripts/` directory does not exist.
2. **Given** `tests/run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, `run-post-edit-format-guard.sh`, and `run-prompt-secret-guard.sh` currently test `scripts/guardrails/*.sh` directly, **When** the removal is complete, **Then** none of these four test files exist (their sole subject is gone).
3. **Given** `install.sh` currently has a conditional sync block for `scripts/guardrails/` that only acts `if [ -d "$GUARDRAILS_SRC" ]`, **When** the removal is complete, **Then** running `install.sh` on a machine with a prior install still removes the stale `~/.claude/scripts/guardrails/` copy (the block becomes an unconditional cleanup, mirroring how specs/025 kept `sync_path "hooks"` as an uninstall path rather than deleting it outright).
4. **Given** README.md and README.ja.md currently describe both scripts in their "What this provides" bullets, file-structure tree, Verification section command list, and two separate sentences in the Codex-comparison section claiming `scripts/guardrails/*.sh` "still contains" or "remains" logic, **When** the removal is complete, **Then** none of these describe either script as existing.
5. **Given** `.claude/rules/permissions.md` currently states `scripts/guardrails/*.sh` "still contains the pattern-matching logic these rules describe, for reference," **When** the removal is complete, **Then** this claim is corrected.
6. **Given** `.claude/rules/mcp.md` currently grounds its own doc-completeness rule on `scripts/check-mcp-consistency.sh`'s existence, **When** the removal is complete, **Then** the rule is restated as manual policy, not as something a script enforces.

### User Story 2 - The decision is recorded as its own ADR (Priority: P2)

As the maintainer, I want this decision recorded in a new ADR that references ADR-0005 and ADR-0006 without editing either, consistent with ADR immutability policy.

**Independent Test**: A new ADR exists at the next available number; ADR-0005 and ADR-0006 are byte-for-byte unchanged.

**Acceptance Scenarios**:

1. **Given** ADR-0005 and ADR-0006 currently exist with `status: Accepted`, **When** this feature is complete, **Then** both files are unmodified.
2. **Given** no ADR currently documents removing `scripts/`, **When** this feature is complete, **Then** a new ADR exists documenting it, referencing both prior records.

### Edge Cases

- What happens to `specs/013-cross-agent-guardrail-implementation/` and other historical specs describing these scripts as they existed then? Left untouched, per the convention already established in specs/024–026.
- Does any CI configuration reference either script? Confirmed by search: no `.github/` directory exists in this repository, so no CI config needs updating.
- Does `tests/run-mcp-startup.sh` or any other surviving test depend on `check-mcp-consistency.sh`? Confirmed by search: no — it is a standalone script with no test-suite dependents.
- What happens to the general "MCP definitions must stay consistent across `.mcp.json`, `install.sh`, `settings.json`, and `mcp.md`" expectation once its automated checker is gone? It becomes a manual-review expectation, stated as policy in `.claude/rules/mcp.md` rather than as an automatically-verified fact — the same pattern already applied to the destructive-operation and credential-safety policies in `permissions.md` after specs/025–026.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST NOT contain `scripts/guardrails/` or any of its four files after the change.
- **FR-002**: The repository MUST NOT contain `scripts/check-mcp-consistency.sh` after the change.
- **FR-003**: The repository MUST NOT contain `tests/run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, `run-post-edit-format-guard.sh`, or `run-prompt-secret-guard.sh` after the change.
- **FR-004**: `install.sh` MUST NOT contain a conditional (`if [ -d ... ]`-guarded) sync step for `scripts/guardrails/` that silently no-ops when the source is absent; it MUST unconditionally remove any previously-installed `~/.claude/scripts/guardrails/` copy.
- **FR-005**: README.md and README.ja.md MUST NOT describe `scripts/guardrails/*.sh` or `scripts/check-mcp-consistency.sh` as existing, runnable, or containing current logic, in any section (provided-features list, file-structure tree, Verification command list, Codex-comparison prose).
- **FR-006**: `.claude/rules/permissions.md` MUST NOT claim `scripts/guardrails/*.sh` contains reference logic that still exists.
- **FR-007**: `.claude/rules/mcp.md` MUST NOT ground its `.mcp.json`-entry-completeness rule on `scripts/check-mcp-consistency.sh`'s existence; the completeness expectation itself MUST remain stated as policy.
- **FR-008**: `docs/adr/0005-remove-claude-hooks.md` and `docs/adr/0006-remove-permissions-config.md` MUST remain byte-for-byte unchanged.
- **FR-009**: A new ADR MUST exist, at the next available number, documenting this decision and referencing both ADR-0005 and ADR-0006.
- **FR-010**: `specs/013-cross-agent-guardrail-implementation/` and every other `specs/NNN-*/` directory numbered below this feature MUST be left unmodified.
- **FR-011**: The full remaining behavior-suite set (every `tests/run-*.sh` after FR-003's deletions) MUST pass after the change.

### Key Entities

- **`scripts/guardrails/` (4 files)**: Reference-only guardrail matching logic, left standing by specs/025–026. Deleted entirely.
- **`scripts/check-mcp-consistency.sh`**: Unrelated MCP-catalog drift checker. Deleted entirely as a separately-confirmed decision.
- **Four guardrail test suites**: Their sole subject is deleted; the suites are deleted with them.
- **`install.sh`'s guardrails sync block**: Becomes an unconditional cleanup step (uninstall path), not a deleted block — mirrors the `sync_path "hooks"` precedent.
- **README.md/README.ja.md, permissions.md, mcp.md**: Documentation requiring correction so no live reference claims either script exists.
- **New ADR**: Records this decision; references ADR-0005 and ADR-0006 without editing them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `scripts/` does not exist as a directory in the repository.
- **SC-002**: A repository-wide search for `scripts/guardrails` and `scripts/check-mcp-consistency` returns zero matches outside historical `specs/` directories and this feature's own directory.
- **SC-003**: Every remaining `tests/run-*.sh` suite exits successfully.
- **SC-004**: Running `install.sh` on a machine with a prior install removes any stale `~/.claude/scripts/guardrails/` directory.
- **SC-005**: A new ADR exists; `docs/adr/0005-remove-claude-hooks.md` and `docs/adr/0006-remove-permissions-config.md` are unchanged from before this feature started.

## Assumptions

- The maintainer's decision to delete both `scripts/guardrails/` (extending specs/025–026's arc) and the thematically-unrelated `scripts/check-mcp-consistency.sh` was confirmed via two separate `AskUserQuestion` rounds before this spec was written — the second specifically because the two scripts have no relationship to each other beyond both living under `scripts/`.
- Following the precedent set by specs/024–026, historical `specs/` directories are not retroactively edited.
- No CI configuration exists in this repository to update (confirmed: no `.github/` directory).
