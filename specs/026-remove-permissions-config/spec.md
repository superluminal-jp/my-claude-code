# Feature Specification: Remove the permissions Block Entirely

**Feature Branch**: `026-remove-permissions-config`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Delete the `permissions` block entirely (allow/ask/deny in .claude/settings.json; allow in .claude/settings.local.json), with no replacement. Removes the last automated protection Claude Code has for this repository, following directly on from specs/025-remove-claude-hooks/ (ADR-0005). Cascading corrections needed in permissions.md, README.md/README.ja.md, AGENTS.md, git-workflow.md, and tests/run-codex-references.sh RULE-09. ADR-0005 is Accepted and immutable — this needs its own new ADR."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The permissions block is gone with no dangling references (Priority: P1)

As the maintainer, after deleting the `permissions` block from both settings files I want every document that described it as an active guardrail to reflect the new reality — Claude Code now has zero automated enforcement of any kind for this repository — so nothing misleads a future session (or a future me) into believing a protection still runs when it does not.

**Why this priority**: Same principle as spec-024 and spec-025: a stale "this is still enforced" claim is worse than an honest "nothing is enforced," because it creates false confidence exactly where a security-relevant decision would be made.

**Independent Test**: `.claude/settings.json` and `.claude/settings.local.json` have no `permissions` key. A repository-wide search for "permissions.deny", "allow/ask/deny", and prose claiming the permissions block "remains"/"is unaffected"/"is the one guardrail" returns no live hits outside historical `specs/` directories.

**Acceptance Scenarios**:

1. **Given** `.claude/settings.json` currently has a `permissions` key with `allow`/`ask`/`deny` arrays, **When** the removal is complete, **Then** the key does not exist.
2. **Given** `.claude/settings.local.json` currently has a `permissions.allow` array, **When** the removal is complete, **Then** the key does not exist (the file retains its other keys: `prefersReducedMotion`, `spinnerTipsEnabled`).
3. **Given** `.claude/rules/permissions.md` currently states "`Read` denies in `.claude/settings.json` cover the paths above and remain enforced" and has a "## `.claude/settings.json` permissions" section describing specific entries, **When** the removal is complete, **Then** neither claim survives — the document states that no automated enforcement of any policy in it exists anymore.
4. **Given** README.md's and README.ja.md's Codex-comparison table currently shows "Allow/prompt command policy: yes" for Claude Code (the sole remaining "yes" row after spec-025), **When** the removal is complete, **Then** that row also reads "no" for Claude Code, and the surrounding prose no longer claims any Claude Code guardrail survives.
5. **Given** AGENTS.md currently states "The one guardrail Claude Code still enforces is `.claude/settings.json`'s `permissions` block", **When** the removal is complete, **Then** AGENTS.md no longer makes that claim.
6. **Given** `.claude/rules/git-workflow.md` currently states "Composes with `permissions.md` (git writes stay on `ask`)", **When** the removal is complete, **Then** this claim is corrected (no `ask` tier exists in settings.json anymore).

### User Story 2 - The decision is recorded as its own ADR (Priority: P2)

As the maintainer, I want this decision recorded in a new, separate ADR rather than folded into the now-Accepted ADR-0005, so the decision history stays accurate to what was actually decided when.

**Why this priority**: ADR policy (`adr` skill) is explicit: an Accepted record's substance is never edited, only superseded. ADR-0005 asserted a fact (the permissions block is the last remaining guardrail) that this feature invalidates — that requires a new record, not a silent edit of the old one.

**Independent Test**: A new ADR file exists at the next available number, status `Proposed` pending acceptance, referencing ADR-0005 and explaining it further reduces what that record left standing. ADR-0005 itself is byte-for-byte unchanged.

**Acceptance Scenarios**:

1. **Given** ADR-0005 currently exists with `status: Accepted`, **When** this feature is complete, **Then** `docs/adr/0005-remove-claude-hooks.md` is unmodified.
2. **Given** no ADR currently documents removing the permissions block, **When** this feature is complete, **Then** a new ADR exists at `docs/adr/0006-*.md` (or the next free number) documenting it.

### Edge Cases

- What happens to `tests/run-codex-references.sh` RULE-09, which currently asserts `.permissions.deny | length >= 5`? It must stop asserting anything about `.permissions`, since the key no longer exists (`jq '.permissions.deny'` on a key-absent document returns `null`, and `null | length` is `0`, which the current `>= 5` check would then correctly fail — but the check's *purpose*, guarding NFR-002 from spec-021, no longer has anything to guard, since spec-025 already removed the hook half and this feature removes the other half). The rule should be removed entirely rather than kept in a permanently-failing or trivially-adjusted state.
- What happens to `specs/013-cross-agent-guardrail-implementation/`, `specs/021-codex-official-import/`, and other historical specs that describe the permissions block as it existed then? Left untouched — historical record, per the convention already established in spec-024 and spec-025.
- What happens to `.claude/settings.local.json`'s other keys (`prefersReducedMotion`, `spinnerTipsEnabled`)? Untouched — only the `permissions` key is removed from this file.
- Does `install.sh` need changes? No — it syncs `settings.json` wholesale via `sync_path "settings.json"` regardless of its contents; an empty-of-`permissions` file syncs the same way a full one did. No install.sh edit is needed (unlike spec-025, which had to remove a now-erroring `chmod` step — there is no analogous mechanical step here).
- Does `.mcp.json` or any MCP-related doc need changes? No — the `permissions.allow` entries for `mcp__*__*` wildcards were a convenience allowlist, not what makes those servers available (`.mcp.json` and `enableAllProjectMcpServers: true`, which is untouched, control that). Removing the allowlist means the user will be prompted per-tool instead of auto-allowed; it does not remove MCP server availability. This is a usability consequence (more prompts), not a functional one, and is already implied by "zero automated enforcement... of any kind" — no separate requirement needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `.claude/settings.json` MUST NOT contain a `permissions` key after the change.
- **FR-002**: `.claude/settings.local.json` MUST NOT contain a `permissions` key after the change; its other keys MUST remain unchanged.
- **FR-003**: `.claude/rules/permissions.md` MUST NOT claim that any Read-deny, allow, or ask enforcement is currently active in `.claude/settings.json`. Its "## `.claude/settings.json` permissions" section (describing specific entries) MUST be removed or rewritten to state that no such entries exist anymore.
- **FR-004**: README.md and README.ja.md's Codex-comparison table MUST show "no" for Claude Code on every row, including "Allow/prompt command policy," and the surrounding prose MUST NOT claim any Claude Code guardrail (via hooks or via the permissions block) still runs.
- **FR-005**: AGENTS.md MUST NOT claim that `.claude/settings.json`'s `permissions` block is "the one guardrail Claude Code still enforces" or any equivalent claim.
- **FR-006**: `.claude/rules/git-workflow.md` MUST NOT claim that git writes "stay on `ask`" as a `.claude/settings.json`-enforced fact.
- **FR-007**: `tests/run-codex-references.sh` MUST NOT contain RULE-09 (or any check asserting `.claude/settings.json`'s `permissions.deny` has a minimum length) after the change.
- **FR-008**: `docs/adr/0005-remove-claude-hooks.md` MUST remain byte-for-byte unchanged (Accepted ADRs are immutable in substance).
- **FR-009**: A new ADR MUST exist, at the next available number after the highest currently in `docs/adr/`, documenting this decision and referencing ADR-0005.
- **FR-010**: `specs/013-cross-agent-guardrail-implementation/`, `specs/021-codex-official-import/`, and every other `specs/NNN-*/` directory numbered below this feature MUST be left unmodified.
- **FR-011**: The full remaining behavior-suite set (every `tests/run-*.sh` after FR-007's edit) MUST pass after the change.

### Key Entities

- **`.claude/settings.json` `permissions` key**: The allow/ask/deny lists. Deleted in its entirety.
- **`.claude/settings.local.json` `permissions` key**: The local-only allow list. Deleted; sibling keys untouched.
- **`.claude/rules/permissions.md`**: Policy document whose "still enforced" claims (already partially corrected by spec-025) require a further correction — now nothing in it is automatically enforced.
- **Codex-comparison table (README.md / README.ja.md)**: Its last remaining "yes" row for Claude Code flips to "no" — the table now shows Claude Code enforcing nothing at all.
- **AGENTS.md's "one guardrail" claim**: Becomes false; requires rewrite.
- **`git-workflow.md`'s "ask tier" claim**: Becomes false; requires rewrite.
- **`tests/run-codex-references.sh` RULE-09**: Its guarded invariant (NFR-002, spec-021) is fully retired by this feature (spec-025 already retired half of it); the rule itself is removed.
- **New ADR**: Records this decision; references and further reduces what ADR-0005 described as remaining.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `jq 'has("permissions")' .claude/settings.json .claude/settings.local.json` returns `false` for both files.
- **SC-002**: A repository-wide search for "permissions.deny", "allow/ask/deny", and phrases asserting the permissions block "remains"/"is unaffected"/"is the one guardrail"/"stay on ask" returns zero live hits outside historical `specs/` directories and this feature's own directory.
- **SC-003**: Every remaining `tests/run-*.sh` suite exits successfully.
- **SC-004**: A reader of README.md's or README.ja.md's Codex-comparison table after the change comes away understanding that Claude Code enforces nothing automatically at all for this repository, while Codex (once imported and trusted) still blocks destructive commands and prompt secrets.
- **SC-005**: A new, `Accepted`-or-`Proposed` ADR exists documenting this decision; `docs/adr/0005-remove-claude-hooks.md` is unchanged from before this feature started.

## Assumptions

- The maintainer's decision to delete the entire `permissions` block from both files, understanding this leaves Claude Code with zero automated enforcement of any kind for this repository, was confirmed via `AskUserQuestion` before this spec was written.
- MCP server *availability* is unaffected (governed by `.mcp.json` and `enableAllProjectMcpServers`, not by the `permissions.allow` wildcard entries being removed) — only the auto-allow convenience for those tool calls is lost, meaning more interactive prompts, not fewer capabilities.
- `install.sh` needs no changes — `sync_path "settings.json"` copies the file regardless of its contents.
- Following the precedent set by spec-024 and spec-025, historical `specs/` directories are not retroactively edited; this feature's own directory is the record of this decision at the spec-kit level, and the new ADR is the record at the architecture-decision level.
