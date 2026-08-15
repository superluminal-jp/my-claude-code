# Feature Specification: Remove .claude/hooks/ Entirely

**Feature Branch**: `025-remove-claude-hooks`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "Delete .claude/hooks/ in its entirety (all 7 files), with no replacement mechanism. This removes all structural/automatic enforcement this repository provided via Claude Code hooks: destructive-command blocking, edit protection (.git/ and main/master branch), post-edit auto-formatting, prompt secret-scanning, Spec Kit auto-update before /speckit-* commands, and the TUI status line. The maintainer has explicitly confirmed this is intentional, that the security-blocking hooks specifically are included, and understands subagents cannot replace PreToolUse/UserPromptSubmit blocking. scripts/guardrails/*.sh are NOT being deleted. Cascading changes needed in settings.json, install.sh, README.md, README.ja.md, AGENTS.md, 4 guardrail test suites, and tests/run-speckit-update.sh (deleted). specs/013-cross-agent-guardrail-implementation/ stays untouched. Propose an ADR during close-out."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hooks are gone with no dangling references (Priority: P1)

As the maintainer of this configuration repository, after removing `.claude/hooks/` I want every file, setting, and piece of documentation that referenced it to reflect the new reality — no automatic enforcement exists anymore in Claude Code for this repository — so that nobody (including a future session of Claude Code itself) is misled into believing a guardrail still runs when it does not.

**Why this priority**: A stale claim that a guardrail "still blocks X" is worse than no guardrail at all — it creates false confidence. This is the same principle that drove the prior `verify-config` removal (spec-024): a clean removal is one where documentation matches reality, not one where the files are gone but the prose still describes them.

**Independent Test**: Grep the repository for `.claude/hooks` and each of the seven deleted filenames; the only hits are historical `specs/` directories that predate this removal, and this spec's own directory. Additionally, read the "What Codex enforces, and what it does not" comparison table (README.md / README.ja.md) and confirm it accurately states that Claude Code now enforces nothing automatically except the `settings.json` permissions allow/ask/deny list.

**Acceptance Scenarios**:

1. **Given** `.claude/hooks/` currently contains seven files, **When** the removal is complete, **Then** the directory does not exist.
2. **Given** `.claude/settings.json` currently wires four hook events and a `statusLine` command to files under `.claude/hooks/`, **When** the removal is complete, **Then** neither the `hooks` key nor the `statusLine` key exists in `.claude/settings.json`.
3. **Given** `install.sh` currently syncs `.claude/hooks/` to `~/.claude/hooks/` and `chmod +x`'s files there, **When** the removal is complete, **Then** running `install.sh` again removes `~/.claude/hooks/` (via the now-empty-source sync) without erroring on a missing directory.
4. **Given** README.md and README.ja.md currently claim "Claude Code's equivalents are unaffected" and show a comparison table where Claude Code enforces more than Codex, **When** the removal is complete, **Then** both documents accurately state that Claude Code enforces nothing automatically via hooks anymore, and the comparison table reflects that Codex (once imported and trusted) now enforces destructive-command blocking and prompt-secret scanning while Claude Code does not.
5. **Given** AGENTS.md currently claims Claude Code's `pre-edit.sh` guardrail is "unaffected" by Codex's enforcement gaps, **When** the removal is complete, **Then** AGENTS.md no longer makes that claim (the file no longer exists to be unaffected).

### User Story 2 - Remaining tests still test something real (Priority: P2)

As the maintainer, after the removal I want every test suite that previously tested a now-deleted hook wrapper to either (a) drop only the assertions about the deleted wrapper while keeping assertions about `scripts/guardrails/*.sh` (which are not deleted), or (b) be deleted entirely if its sole subject was a deleted hook, so that the test suite continues to test something that actually exists.

**Why this priority**: A test asserting properties of a file that no longer exists doesn't fail loudly — `[ -x "$MISSING_FILE" ]` guards typically report "SKIP" or silently pass through a conditional, masking the gap. Leaving such assertions in place would create silent, misleading test coverage.

**Independent Test**: Run every remaining `tests/run-*.sh` suite; each passes, and reading each guardrail suite's source shows no reference to `.claude/hooks/`.

**Acceptance Scenarios**:

1. **Given** `tests/run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, `run-post-edit-format-guard.sh`, and `run-prompt-secret-guard.sh` each currently test both a `scripts/guardrails/*.sh` script directly and a `.claude/hooks/*.sh` wrapper, **When** the removal is complete, **Then** each suite still tests its `scripts/guardrails/*.sh` subject and no longer references any `.claude/hooks/` file.
2. **Given** `tests/run-speckit-update.sh` tests only `.claude/hooks/speckit-expand-update.sh`, **When** the removal is complete, **Then** this test file does not exist.

### Edge Cases

- What happens to `specs/013-cross-agent-guardrail-implementation/`, the design record that originally introduced these hooks? It stays untouched — historical Spec Kit directories are an append-only decision log, not live configuration, per this repository's established convention (also followed in spec-024's removal).
- What happens to `scripts/guardrails/*.sh` now that their only automatic caller is gone? They are explicitly **not** deleted by this feature — the request named `.claude/hooks/` only. They remain directly invokable (by hand, by the surviving test assertions, and via `settings.json`'s `permissions.allow` list entries `Bash(scripts/guardrails/*.sh)` and `Bash(bash scripts/guardrails/*.sh)`, which also stay unchanged since they are independent of the `hooks` key). Whether this makes them effectively orphaned is a judgment the maintainer can revisit later; this feature does not decide it.
- What happens to the `.claude/rules/permissions.md` policy document? **Correction found during implementation** (T007 grep validation): contrary to this spec's original assumption, `permissions.md` does literally reference `.claude/hooks/README.md` by path, twice — once in its opening paragraph, once in the Credential Safety section — pointing at the now-deleted mechanics doc as if it still existed. FR-012 (below) is amended accordingly: `permissions.md` IS edited, not left unmodified, to state that automatic enforcement was removed and that `scripts/guardrails/*.sh` remains as reference-only logic. The policy statements themselves remain the intended behavior even though automated enforcement of that policy is gone — that gap is a known, accepted consequence of this decision, not a defect to silently paper over.
- What happens to the Codex CLI side (`.codex/hooks/`, generated by Codex's own `/import`)? Out of scope — the maintainer has explicitly stated Codex's own import mechanism handles that independently and is not a design constraint for this repository's `.claude/hooks/`.
- What happens to the `~/.claude/hooks/` copy on this and other machines once `install.sh` is re-run? It is removed (via `sync_path`'s existing `rm -rf` semantics acting on an empty/absent source) — every project on the machine loses this repository's Claude Code guardrail enforcement once `install.sh` is next run. This is the intended, accepted consequence of this decision, not an incidental side effect to work around.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST NOT contain any file under `.claude/hooks/` after the change (all seven: `pre-bash.sh`, `pre-edit.sh`, `post-edit-format.sh`, `user-prompt-submit.sh`, `speckit-expand-update.sh`, `statusline.sh`, `README.md`).
- **FR-002**: `.claude/settings.json` MUST NOT contain a `hooks` key after the change.
- **FR-003**: `.claude/settings.json` MUST NOT contain a `statusLine` key after the change.
- **FR-004**: `install.sh` MUST NOT contain a `sync_path "hooks"` call or a `chmod +x` step targeting `.claude/hooks/` or its installed copy after the change; any comments explaining hook-related sync behavior MUST be updated to no longer describe a step that no longer exists.
- **FR-005**: README.md and README.ja.md MUST NOT reference any of the seven deleted files or the `.claude/hooks/` path as a currently-existing, currently-functioning part of the repository.
- **FR-006**: README.md's "What Codex enforces, and what it does not" section (and README.ja.md's equivalent) MUST be rewritten, not merely stripped of dead links, to accurately state the post-removal reality: Claude Code enforces nothing automatically via hooks; Codex (once imported and independently trusted, unaffected by this change) still enforces destructive-command blocking and prompt-secret scanning; neither enforces edit protection, post-edit formatting, or Spec Kit prompt expansion; Claude Code still enforces its allow/prompt command policy via `settings.json`'s `permissions` block, which is unrelated to hooks and is not being removed.
- **FR-007**: AGENTS.md MUST NOT claim that "Claude Code's equivalents are unaffected" or otherwise imply `.claude/hooks/pre-edit.sh` (or any other deleted hook) still runs.
- **FR-008**: `tests/run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, `run-post-edit-format-guard.sh`, and `run-prompt-secret-guard.sh` MUST continue to test their respective `scripts/guardrails/*.sh` subject directly, and MUST NOT contain assertions referencing any `.claude/hooks/` file.
- **FR-009**: `tests/run-speckit-update.sh` MUST NOT exist after the change (its sole subject is deleted).
- **FR-010**: `scripts/guardrails/*.sh` (all four files) and their `Bash(scripts/guardrails/*.sh)` / `Bash(bash scripts/guardrails/*.sh)` permission-allowlist entries in `.claude/settings.json` MUST be left unmodified by this feature.
- **FR-011**: `specs/013-cross-agent-guardrail-implementation/` MUST be left unmodified — historical decision record, not live configuration.
- **FR-012**: `.claude/rules/permissions.md` MUST NOT reference `.claude/hooks/README.md` (or any deleted hook file) as if it still exists. *(Amended during implementation — the original draft assumed no such reference existed; T007's grep validation found two. See Edge Cases.)*
- **FR-013**: The full remaining behavior-suite set (every `tests/run-*.sh` left after FR-009's deletion) MUST pass after the change.
- **FR-015**: `tests/run-codex-references.sh`'s RULE-09 (added by `specs/021-codex-official-import` to guard NFR-002 — that the Codex-import migration must not weaken Claude Code) MUST NOT assert that `.claude/settings.json` has four hook events, since this feature intentionally removes them; it MUST continue asserting `permissions.deny` stays non-empty (the part of NFR-002 unrelated to hooks). *(Found during T013 full-suite run — this test suite was not identified by the original impact survey since it doesn't reference `.claude/hooks/` by path, only by asserting `settings.json`'s `hooks` key structure.)*
- **FR-014**: An Architecture Decision Record MUST be proposed during close-out documenting this removal as an architecturally significant, hard-to-reverse-in-practice decision, per this repository's own governance (`.claude/CLAUDE.md` § Close-out) — no existing ADR currently covers hook removal.

### Key Entities

- **`.claude/hooks/` (7 files)**: The hook scripts and their mechanics README. Deleted in their entirety.
- **`scripts/guardrails/` (4 files)**: The shared guardrail decision logic the deleted wrappers called into. Explicitly out of scope for deletion; loses its only automatic runtime caller but remains directly invokable.
- **`.claude/settings.json` `hooks` and `statusLine` keys**: The wiring that made the deleted files run automatically. Removed alongside the files they point to.
- **Comparison table (README.md "What Codex enforces, and what it does not" / README.ja.md equivalent)**: Currently asserts Claude Code enforces more guardrails than Codex. Requires substantive content rewrite (not deletion) to state the inverted post-removal reality.
- **AGENTS.md's "unaffected" claim**: A specific sentence asserting Claude Code's guardrails remain intact regardless of Codex's enforcement gaps. Becomes false; requires rewrite.
- **Four guardrail test suites**: Each tests both a surviving `scripts/guardrails/*.sh` script and a deleted `.claude/hooks/*.sh` wrapper. Requires partial edit (drop wrapper assertions only).
- **`tests/run-speckit-update.sh`**: Tests only a deleted hook. Requires full deletion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repository-wide search for `.claude/hooks` and each of the seven deleted filenames returns zero matches outside of `specs/` directories that predate `025` and `specs/025-remove-claude-hooks/` itself.
- **SC-002**: Every remaining `tests/run-*.sh` suite exits successfully when run after the change.
- **SC-003**: A reader of README.md's or README.ja.md's Codex-comparison section after the change comes away with an accurate understanding that Claude Code enforces nothing automatically via hooks, while Codex (once imported and trusted) still blocks destructive commands and prompt secrets.
- **SC-004**: `install.sh` completes a sync run with no errors and no reference to `.claude/hooks/`.
- **SC-005**: An ADR documenting this decision exists in `docs/adr/` after close-out.

## Assumptions

- The maintainer's decision to delete all seven hook files, including the three that provided structural security blocking (destructive-command, edit-protection, prompt-secret), is final for this spec's scope and was made with explicit awareness of the consequence (confirmed via two rounds of `AskUserQuestion` in the driving conversation, prior to this spec being written).
- "Use subagents" in the original request refers to how the *implementation work* of this spec should be carried out (delegating suitable chunks to subagents), not to a design requirement that subagent-based mechanisms replace the deleted hooks' blocking behavior — subagents cannot intercept or block other tool calls before they execute, so no such replacement is technically possible via subagents regardless of intent.
- `scripts/guardrails/*.sh` being left in place but losing their automatic caller is an accepted, known state (effectively dormant except for manual/test invocation) — this feature does not additionally delete them, rename them, or repurpose them, since the original request scoped deletion to `.claude/hooks/` only.
- The "historical specs stay unmodified" convention (FR-011) follows the precedent already established by `specs/024-remove-verify-config` (which left `specs/019`, `specs/021`, etc. untouched) — this feature applies the same convention rather than establishing a new one.
- Codex CLI's own guardrail behavior (via its independently-generated, gitignored `.codex/hooks/`) is unaffected by this change and is explicitly out of scope for verification or adjustment, per the maintainer's direction that Codex-side concerns are handled by Codex's own `/import` flow.
