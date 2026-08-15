# Feature Specification: Remove /verify-config Verification Feature

**Feature Branch**: `024-remove-verify-config`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Remove the /verify-config verification feature entirely: delete .claude/skills/verify-config/SKILL.md, .claude/agents/verification-runner.md, and tests/run-verification-agent.sh. Update README.md and README.ja.md to remove all references to /verify-config, verification-runner, and the Codex-CLI inline-verification fallback procedure that exists solely to parallel this feature (since the feature it parallels is being removed). Check tests/run-codex-sync.sh for SYNC-08/09 checks that reference this feature's deploy-map row in .codex/README.md and update/remove accordingly. Rationale: this was a repository-local (non-synced) verification subagent designed in spec-019 to isolate large verification output from the main conversation; the maintainer has decided the feature is no longer wanted and should be cleanly removed along with all its documentation and tests, leaving no dangling references."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clean removal leaves no dangling references (Priority: P1)

As the maintainer of this configuration repository, after removing the `/verify-config` feature I want every trace of it gone — the skill, the agent, its dedicated test suite, and every mention in both READMEs and in the Codex sync test suite — so that nothing in the repository points at a component that no longer exists.

**Why this priority**: A partial removal (e.g., deleting the agent but leaving the skill referencing it, or leaving stale README prose) is worse than not removing it at all — it reintroduces exactly the "confusing, hard to tell what's real" problem that motivated the removal.

**Independent Test**: Grep the repository for `verify-config` and `verification-runner` (case-insensitive) after the change; the only remaining hits should be this spec's own directory (`specs/019-*`, `specs/024-*`) and historical spec/ADR material that documents past decisions, never live instructions, skill/agent definitions, or README how-to sections.

**Acceptance Scenarios**:

1. **Given** the repository currently has `.claude/skills/verify-config/SKILL.md`, `.claude/agents/verification-runner.md`, and `tests/run-verification-agent.sh`, **When** the removal is complete, **Then** none of these three files exist.
2. **Given** README.md and README.ja.md currently document `/verify-config`, the `verification-runner` agent, and the Codex-CLI inline-verification fallback procedure, **When** the removal is complete, **Then** neither README mentions any of the three.
3. **Given** `tests/run-codex-sync.sh` currently has checks (SYNC-08/09) that assert a deploy-map row for this feature exists in `.codex/README.md`, **When** the removal is complete, **Then** those checks either verify the row's absence or are themselves removed, and the suite passes.

### User Story 2 - Repository stays internally consistent after removal (Priority: P2)

As the maintainer, after the removal I want the remaining test suites and the `install.sh` sync process to still run cleanly, so that removing an unwanted feature doesn't silently break unrelated tooling.

**Why this priority**: This repository is the maintainer's own Claude Code configuration source; a broken test suite or sync script blocks every future change until fixed, not just this one.

**Independent Test**: Run the full behavior-suite set (`tests/run-*.sh`) after the change; every suite that does not reference the removed feature passes exactly as it did before, and no suite fails due to a missing file the removal did not account for.

**Acceptance Scenarios**:

1. **Given** the removal has deleted `tests/run-verification-agent.sh`, **When** the full test suite list is run, **Then** no other script or CI-style entry point still tries to invoke the deleted file.
2. **Given** `install.sh` never synced `.claude/agents/` in the first place, **When** the removal deletes `.claude/agents/verification-runner.md`, **Then** `install.sh` requires no changes and continues to run cleanly.

### Edge Cases

- What happens to the `specs/019-verify-fork-test-runner/` directory that originally designed this feature? It is historical record of a past decision and stays untouched — Spec Kit directories are an append-only decision log, not live configuration; only spec `024` (this one) documents the removal.
- What happens to `specs/021-codex-official-import/`, `specs/014-codex-config-port/`, and other historical spec files that reference `verification-runner` or `verify-config` as prior context? Same as above — historical spec artifacts are not edited retroactively; only currently-live instructions (READMEs, skill/agent files, active test suites) are in scope for this removal.
- The Codex-side counterpart this feature once had (`.codex/prompts/verify-config.md`, a `/prompts:verify-config` command, and a deploy-map row in `.codex/README.md`) was already retired by `specs/021-codex-official-import` (ADR-0004): this repository no longer ships any Codex port, `.codex/` is git-ignored and produced locally by each developer's own `/import`, and `tests/run-codex-sync.sh` no longer exists (replaced by `tests/run-codex-references.sh` and `tests/run-codex-drift.sh`, neither of which references this feature). So there is no live Codex-side artifact or test to remove — only the now-inaccurate claim in README.md/README.ja.md's Verification section (that `/prompts:verify-config` is Codex's counterpart) needs to go, as part of the README text removal.
- README.md's opening section (around "install.sh also deploys a Codex CLI counterpart ... and a verification prompt") already contradicts the repository's current "no longer ships a Codex port" state (per the Codex CLI support section and ADR-0004) — this is pre-existing documentation drift that predates this feature and is not caused by it. It is out of scope for this removal and is called out separately rather than silently fixed here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST NOT contain `.claude/skills/verify-config/SKILL.md` after the change.
- **FR-002**: The repository MUST NOT contain `.claude/agents/verification-runner.md` after the change.
- **FR-003**: The repository MUST NOT contain `tests/run-verification-agent.sh` after the change.
- **FR-004**: README.md MUST NOT reference `/verify-config`, the `verification-runner` agent, or the Codex-CLI inline-verification fallback procedure that existed solely to parallel this feature.
- **FR-005**: README.ja.md MUST NOT reference `/verify-config`, the `verification-runner` agent, or the Codex-CLI inline-verification fallback procedure.
- **FR-006**: README.md and README.ja.md MUST NOT claim that a Codex CLI counterpart (e.g. `/prompts:verify-config`) runs the same checks, since no such Codex-side artifact currently exists in the repository (retired by `specs/021-codex-official-import`).
- **FR-007**: No currently-live file under `.claude/`, `tests/`, `scripts/`, or the repository root MUST reference `verify-config` or `verification-runner` as an instruction, command, or active component after the change. (There is currently no `.codex/README.md` deploy-map row or `tests/run-codex-sync.sh` SYNC-08/09 check to update — both were already removed by `specs/021-codex-official-import`; this requirement covers whatever currently-live references actually exist, confirmed during planning.)
- **FR-008**: Historical Spec Kit artifacts (`specs/019-verify-fork-test-runner/`, and the pre-existing references inside `specs/014-codex-config-port/` and `specs/021-codex-official-import/`) MUST be left unmodified — they are a decision record, not live configuration, and this removal is itself recorded as a new spec (`024`) rather than by editing the old ones.
- **FR-009**: The full behavior-suite set (every `tests/run-*.sh` remaining after removal) MUST pass after the change, with no suite failing due to a reference to a file this removal deleted.
- **FR-010**: The list of files a user should manually clean up after installing an earlier version of this repository (README.md's "If you installed an earlier version" section, and its README.ja.md equivalent) MUST NOT be modified by this removal — it describes historical install artifacts, not this feature's current documentation, and remains accurate regardless of whether the feature exists today.

### Key Entities

- **`/verify-config` skill**: The user-facing command definition (`.claude/skills/verify-config/SKILL.md`) that forked into the verification subagent. Being removed in its entirety.
- **`verification-runner` agent**: The project-scoped (non-synced) subagent definition (`.claude/agents/verification-runner.md`) that ran this repository's configuration checks and behavior suites. Being removed in its entirety.
- **Codex-CLI counterpart claim**: A sentence in README.md/README.ja.md's Verification section stating that `/prompts:verify-config` is Codex CLI's counterpart to `/verify-config`. The Codex-side artifact this once referred to (`.codex/prompts/verify-config.md`) was already deleted by `specs/021-codex-official-import`, so the claim is currently inaccurate independent of this removal; it is deleted alongside the rest of the Verification section's `/verify-config` description.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repository-wide search for `verify-config` and `verification-runner` returns zero matches outside of (a) any `specs/` directory that predates `024` (all are historical decision records, not just the three anticipated during planning — implementation also found matches in `020-subagent-delegation-rule/`), (b) `specs/024-remove-verify-config/` itself, and (c) the two named exceptions in FR-006/FR-010 (README's "earlier version" cleanup list, and install.sh's past-tense explanatory comment for the `commands` sync step).
- **SC-002**: Every remaining behavior-suite script (`tests/run-*.sh`) exits successfully when run after the change.
- **SC-003**: `install.sh` completes a sync run with no errors and no reference to the removed files.
- **SC-004**: A reader of README.md or README.ja.md after the change finds no instruction, command, or agent description for a verification feature that no longer exists in the repository.

## Assumptions

- The maintainer's decision to remove this feature is final for this spec's scope; re-adding equivalent functionality later (if ever) is a separate, future feature and out of scope here.
- "Historical Spec Kit artifacts stay unmodified" (FR-008) reflects this repository's existing convention that spec directories are an append-only record of decisions over time (evidenced by `specs/019` never having been retroactively edited by later specs); this removal follows the same convention rather than rewriting history.
- No other project (outside this repository) depends on `.claude/agents/verification-runner.md`, since `install.sh` never synced `.claude/agents/` to `~/.claude/` — confirmed by inspecting `install.sh`'s `sync_path` calls, which cover only `hooks`, `rules`, `skills`, `commands`, `CLAUDE.md`, and `settings.json`.
- The user's original request assumed `tests/run-codex-sync.sh` (with SYNC-08/09 checks) and a `.codex/README.md` deploy-map row still existed. Confirmed during planning that both were already removed by `specs/021-codex-official-import` when this repository stopped shipping a Codex port (ADR-0004); `.codex/` is now git-ignored and locally generated per developer. FR-006/FR-007 are scoped to what currently exists (the README's counterpart claim) rather than to files that no longer exist.
- README.md's introductory paragraph claiming `install.sh` "also deploys a Codex CLI counterpart ... and a verification prompt" is pre-existing drift (contradicts the repo's current no-Codex-port state) that predates and is unrelated to this feature; left unmodified per FR-007's scope (currently-live references *to this feature*, not unrelated stale claims elsewhere).
