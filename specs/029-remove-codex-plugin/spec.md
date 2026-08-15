# Feature Specification: Remove the codex-plugin-cc Claude Code Plugin

**Feature Branch**: `029-remove-codex-plugin`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Remove the codex-plugin-cc / codex@openai-codex Claude Code plugin installation from install.sh entirely (section 4: `claude plugin marketplace add openai/codex-plugin-cc` + `claude plugin install codex@openai-codex`, and their idempotent update/list-check logic). This plugin (Codex review/rescue invoked from Claude Code) is being deprecated by the maintainer. No ADR documents its original adoption, so none needs superseding. Also, as part of the same change, reorganize install.sh's section comments/structure for clarity — the numbered-step comments (0-4) should read cleanly once section 4 is gone, and stale or confusing comments elsewhere in the file should be tightened. Cascading update: tests/run-install.sh currently stubs `claude plugin marketplace list` and `claude plugin list` (lines 45-49) solely to satisfy this install.sh section; these stub branches become dead code once the section is removed and must be cleaned up. No README/README.ja.md changes needed (they never documented this plugin). Follows the specs/025-028 remove-X pattern for structure, but does NOT require a new ADR (two-way-door, trivially reversible plugin registration, not an architecturally significant decision) — confirm this reasoning explicitly in the spec's Assumptions section."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Running the installer no longer installs codex-plugin-cc (Priority: P1)

As the maintainer, after running `install.sh` I want the `codex-plugin-cc` marketplace and `codex@openai-codex` plugin to no longer be registered or installed by this repository, so a fresh or repeated install matches the deprecation decision instead of silently re-adding a retired integration.

**Why this priority**: The installer is the single mechanism that reproduces this repository's managed state on any machine; leaving deprecated install logic in place means every future run keeps re-introducing what the maintainer decided to drop.

**Independent Test**: Run `install.sh` against an isolated home with stubbed `claude`/`uvx`; the stub's command log contains no `plugin marketplace add`, `plugin marketplace update`, or `plugin install` invocation for `codex-plugin-cc` / `codex@openai-codex`.

**Acceptance Scenarios**:

1. **Given** `install.sh` currently registers the `openai/codex-plugin-cc` marketplace and installs `codex@openai-codex` (section 4), **When** the removal is complete, **Then** `install.sh` contains no marketplace-add, marketplace-update, or plugin-install call naming `codex-plugin-cc`, `openai-codex`, or `codex@openai-codex`.
2. **Given** a machine with a prior install that already registered the marketplace and installed the plugin, **When** `install.sh` is re-run, **Then** the script does not attempt to re-add, update, or reinstall it (the step is deleted, not merely skipped by a new conditional).

---

### User Story 2 - The installer's section comments read cleanly (Priority: P2)

As the maintainer, I want `install.sh`'s numbered step comments and other section commentary to accurately describe what remains after section 4 is deleted, so the file continues to read as a clear, self-documenting sequence rather than leaving a numbering gap or orphaned prose.

**Why this priority**: A close second to the removal itself — stale or gapped comments actively mislead the next reader about what the script does, which is worse than sparse comments.

**Independent Test**: Read `install.sh` top to bottom; every remaining numbered step comment describes an action that immediately follows it, the numbering has no gap or skipped index, and no comment references the deleted plugin step.

**Acceptance Scenarios**:

1. **Given** `install.sh` currently has steps numbered `0` through `4`, **When** step 4 (codex plugin install) is removed, **Then** the remaining steps are renumbered contiguously with no gap and no comment refers to a step that no longer exists.
2. **Given** existing comments elsewhere in the file (e.g., the `sync_path` docstring-style comment, the step-1a cleanup comment), **When** the reorganization is complete, **Then** each remaining comment still accurately describes the code immediately below it.

---

### User Story 3 - The installer test suite has no dead stubs (Priority: P1)

As the maintainer, I want `tests/run-install.sh` to stop stubbing `claude plugin marketplace list` / `claude plugin list` once nothing in `install.sh` calls them, so the test fixture doesn't carry fake responses for a code path that no longer exists.

**Why this priority**: Equal weight to User Story 1 — an installer test that stubs behavior for deleted code silently misrepresents what's under test and would mask a future accidental reintroduction.

**Independent Test**: Run `tests/run-install.sh`; it passes, and a text search of the file finds no stub branch keyed on `plugin marketplace list` or `plugin list`, and no assertion referencing `codex-plugin-cc` / `codex@openai-codex`.

**Acceptance Scenarios**:

1. **Given** the `claude` stub in `tests/run-install.sh` currently special-cases `plugin marketplace list` and `plugin list` arguments (lines 45-49) solely to satisfy the deleted section 4, **When** the removal is complete, **Then** those branches are deleted from the stub.
2. **Given** the full remaining test suite (`tests/run-*.sh`), **When** the change is complete, **Then** every suite still exits successfully.

### Edge Cases

- Does any other file in the repository (README.md, README.ja.md, other `.claude/rules/*.md`) describe or recommend the `codex-plugin-cc` plugin? Confirmed by search: no — it was never documented outside `install.sh` and `tests/run-install.sh`.
- Does an ADR document the original adoption of this plugin, requiring a formal supersession? Confirmed by search: no ADR in `docs/adr/` covers it (ADR-0004 "adopt official codex import" is an unrelated decision about the Codex CLI `/import` migration path, not this Claude Code plugin).
- What happens to `specs/` directories that predate this feature and may reference installing this plugin as it existed then? Left untouched, per the convention already established in specs/024-028.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `install.sh` MUST NOT contain any command that adds, updates, or checks for the `openai-codex` plugin marketplace.
- **FR-002**: `install.sh` MUST NOT contain any command that installs, updates, or checks for the `codex@openai-codex` plugin.
- **FR-003**: `install.sh`'s remaining numbered step comments MUST be contiguous (no gap left by the deleted step) and MUST each accurately describe the code immediately following it.
- **FR-004**: `tests/run-install.sh` MUST NOT stub or assert against `claude plugin marketplace list`, `claude plugin marketplace add`, `claude plugin list`, or `claude plugin install` argument patterns.
- **FR-005**: The full remaining behavior-suite set (every `tests/run-*.sh`) MUST pass after the change.
- **FR-006**: No ADR MUST be created or superseded by this change (see Assumptions).
- **FR-007**: README.md and README.ja.md require no change, since neither currently documents the `codex-plugin-cc` plugin.

### Key Entities

- **`install.sh` section 4**: The `codex-plugin-cc` marketplace registration and `codex@openai-codex` plugin install/update logic (currently lines ~123-131). Deleted entirely.
- **`install.sh`'s numbered step comments (`# 0.` … `# 4.`)**: Sequential documentation of each installer phase. Renumbered/tightened so the sequence stays gap-free and accurate after section 4's removal.
- **`tests/run-install.sh`'s `claude` stub**: A fake `claude` CLI used for deterministic, network-free installer testing. Its `plugin marketplace list` / `plugin list` branches (added solely to satisfy section 4) are deleted along with the code they served.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repository-wide search for `codex-plugin-cc`, `openai-codex`, and `codex@openai-codex` outside `specs/` and `docs/adr/` finds no live reference.
- **SC-002**: Running `install.sh` against an isolated home with a stubbed `claude` CLI produces a command log with zero `plugin marketplace add`, `plugin marketplace update`, or `plugin install` entries.
- **SC-003**: Every remaining `tests/run-*.sh` suite exits successfully, including `tests/run-install.sh`.
- **SC-004**: `install.sh`'s step comments, read in order, contain no numbering gap and no reference to a deleted step.
- **SC-005**: `docs/adr/` contains the same set of files, byte-for-byte unchanged, before and after this feature.

## Assumptions

- **No ADR is required for this change.** Unlike specs/025-027 (which retired repository-wide security/config subsystems — hooks, the permissions block, and the guardrail scripts — each a one-way architectural commitment worth recording), this change deletes a single, trivially-reversible plugin registration in `install.sh`. Re-adding it later is a two-line diff with no migration cost, no rejected alternative was weighed, and no other component depends on its presence. It therefore does not meet this repository's own bar for "architecturally significant, hard to reverse" (`.claude/rules/live-documentation.md` § 0, ADR row). This assumption was confirmed by searching `docs/adr/` for any record of this plugin's original adoption — none exists, so there is also nothing to supersede.
- Following the precedent set by specs/024-028, historical `specs/` directories referencing this plugin as it existed then are not retroactively edited.
- The plugin's removal is a maintainer decision already made (stated directly in the input); this spec does not evaluate whether to deprecate it, only how the removal is scoped and verified.
