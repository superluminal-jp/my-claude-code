# Feature Specification: Remove scripts/ Entirely

**Feature Branch**: `027-remove-scripts`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Delete scripts/ entirely: the 4 scripts/guardrails/*.sh files, their 4 corresponding dedicated test suites, and the unrelated scripts/check-mcp-consistency.sh (confirmed via AskUserQuestion as a separate, deliberate decision). Third step in a decision arc after specs/025 (ADR-0005) and specs/026 (ADR-0006). Cascading changes to install.sh, README.md/README.ja.md, permissions.md, mcp.md. New ADR (0007) referencing 0005/0006, which stay unmodified."

## Clarifications

### Session 2026-08-16

- Q: What outcome should `install.sh` optimization preserve? → A: After running
  `install.sh`, the configuration managed by this repository is reflected
  completely, with no missing current settings and no stale settings that the
  repository managed previously.
- Q: Should `install.sh` preserve existing files under `~/.claude` that this
  repository does not manage? → A: Yes. Replace only explicitly managed paths,
  preserve all unrelated user files, and add `agents/` to the managed path set.
- Q: How should the three test suites that require an authenticated Claude CLI
  behave when the CLI is unavailable or logged out? → A: Remove those suites
  and their fixtures entirely.
- Q: How should the installer handle the draw.io MCP configuration that its
  stale comment says is installed by a nonexistent later section? → A: Remove
  the draw.io MCP configuration and do not use draw.io MCP.
- Q: Should the draw.io skill and routing rules remain after removing its MCP
  configuration? → A: No. Remove the draw.io capability entirely, including
  its skill, routing, and MCP catalog documentation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - scripts/ is gone with no dangling references (Priority: P1)

As the maintainer, after deleting `scripts/` in its entirety I want every document that described its contents as active tooling to reflect the new reality, so nothing misleads a future session into running or relying on a script that no longer exists.

**Why this priority**: Same principle as specs/024–026: a stale "run this script" instruction is worse than no instruction, because it fails at the worst time — when someone actually tries to follow it.

**Independent Test**: `scripts/` does not exist. A repository-wide search for
`scripts/guardrails` and `scripts/check-mcp-consistency` finds no instruction
to run them and no claim that they contain current logic; negative removal
explanations and the installer's upgrade-cleanup path remain valid.

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

### User Story 3 - Installer reflects the managed repository state (Priority: P1)

As the maintainer, I want `install.sh` to project the repository-managed Claude
Code configuration into user scope exactly, so a new installation is complete
and a repeated installation removes stale artifacts from earlier repository
versions.

**Independent Test**: Run `install.sh` against an isolated home directory with
stubbed external commands and seeded stale managed paths; every current managed
artifact is installed and every retired managed artifact is absent afterward.

**Acceptance Scenarios**:

1. **Given** an empty isolated home directory, **When** `install.sh` runs, **Then** every current repository-managed user-scope setting is present.
2. **Given** an isolated home directory containing paths managed by an earlier repository version, **When** `install.sh` runs, **Then** retired managed paths are removed and current managed paths match the repository.
3. **Given** an isolated home directory containing unrelated user files, **When** `install.sh` runs, **Then** those files remain unchanged while the explicitly managed paths are synchronized.
4. **Given** `agents/` is an explicitly managed path, **When** it exists in the repository, **Then** it is installed recursively, and when it is absent, any stale previously managed user-scope copy is removed.

### User Story 4 - Remaining tests are locally runnable and current (Priority: P1)

As the maintainer, I want the test tree to contain only suites that validate
the current repository and can run without an authenticated Claude CLI, so the
remaining test entry points are actionable in the normal development
environment.

**Independent Test**: No remaining test runner invokes `claude -p`, and no
fixture directory remains without a runner or an active implementation subject.

**Acceptance Scenarios**:

1. **Given** the live-documentation, skill-routing, and type-safety-coder suites require an authenticated Claude CLI, **When** the test tree is optimized, **Then** those three runners and their fixture directories are absent.
2. **Given** `tests/ubiquitous-language/` has no runner and its subject is no longer present, **When** the test tree is optimized, **Then** that orphan fixture directory is absent.
3. **Given** the remaining test runners validate current repository artifacts, **When** they run in their documented environments, **Then** they complete without requiring Claude CLI authentication.

### User Story 5 - draw.io MCP is not configured (Priority: P1)

As the maintainer, I do not want this repository to configure or install the
draw.io MCP server, so neither project-scope nor installer-managed settings
offer it for use.

**Independent Test**: The MCP catalog and installer contain no draw.io MCP
definition, registration, package reference, or plugin-install path.

**Acceptance Scenarios**:

1. **Given** `.mcp.json` currently declares `drawio`, **When** the cleanup is complete, **Then** that server entry is absent.
2. **Given** `install.sh` contains a stale comment claiming a later section installs the draw.io plugin, **When** the cleanup is complete, **Then** that comment and every draw.io install or registration path are absent.
3. **Given** the `drawio` skill and routing rules direct agents to the removed MCP capability, **When** the cleanup is complete, **Then** the skill directory and every live routing or MCP-catalog instruction for draw.io are absent.

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
- **FR-012**: `install.sh` MUST install every current repository-managed user-scope Claude Code artifact and MUST remove stale artifacts that were managed by earlier repository versions, leaving neither missing current configuration nor surplus retired managed configuration.
- **FR-013**: `install.sh` MUST replace only explicitly managed paths, MUST preserve unrelated existing files under `~/.claude`, and MUST include `agents/` in the managed path set.
- **FR-014**: The repository MUST NOT contain `tests/run-live-documentation.sh`, `tests/run-skill-routing.sh`, `tests/run-type-safety-coder.sh`, or their fixture directories.
- **FR-015**: The repository MUST NOT contain the orphaned `tests/ubiquitous-language/` fixture directory.
- **FR-016**: No remaining `tests/run-*.sh` suite MAY require Claude CLI authentication.
- **FR-017**: The repository MUST NOT define, register, install, route to, or recommend the draw.io capability; its MCP entry, skill directory, routing instructions, and MCP-catalog documentation MUST be removed.

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
- **SC-002**: A repository-wide search for `scripts/guardrails` and `scripts/check-mcp-consistency` finds no instruction to run them and no claim that they contain current logic outside historical `specs/` and ADRs; any live matches are limited to negative removal explanations or the installer's upgrade-cleanup path.
- **SC-003**: Every remaining `tests/run-*.sh` suite exits successfully.
- **SC-004**: Running `install.sh` on a machine with a prior install removes any stale `~/.claude/scripts/guardrails/` directory.
- **SC-005**: A new ADR exists; `docs/adr/0005-remove-claude-hooks.md` and `docs/adr/0006-remove-permissions-config.md` are unchanged from before this feature started.
- **SC-006**: An isolated-home installer test demonstrates that a clean install contains every current managed artifact and that reinstallation removes seeded retired managed artifacts.
- **SC-007**: The isolated-home installer test demonstrates that `agents/` follows the same exact-sync behavior as other managed paths and that unrelated user files remain byte-for-byte unchanged.
- **SC-008**: A repository search finds no remaining test runner that invokes `claude -p` and no fixture directory without a corresponding runner and active implementation subject.
- **SC-009**: A live-repository search outside historical specs and ADRs finds no draw.io server name, package reference, plugin installation, skill, routing instruction, or registration command.

## Assumptions

- The maintainer's decision to delete both `scripts/guardrails/` (extending specs/025–026's arc) and the thematically-unrelated `scripts/check-mcp-consistency.sh` was confirmed via two separate `AskUserQuestion` rounds before this spec was written — the second specifically because the two scripts have no relationship to each other beyond both living under `scripts/`.
- Following the precedent set by specs/024–026, historical `specs/` directories are not retroactively edited.
- No CI configuration exists in this repository to update (confirmed: no `.github/` directory).
