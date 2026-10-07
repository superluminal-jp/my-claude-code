# Feature Specification: Remove the Minto Pyramid Stop Hook

**Feature Branch**: `042-remove-minto-stop-hook`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "minto pyramid の stop hook を廃止 Cite authoritative sources for every non-obvious claim or decision: international standards, industry best practices, scientifically and academically accepted findings, and official documentation, each with its URL. For AWS use the AWS Knowledge and AWS Documentation MCP servers. Never state an unsourced claim as fact; mark unverified points as unverified."

## Scope and Definitions

The feature retires the automatic end-of-turn compliance check that the vendored `minto-pyramid` package adds to every Claude Code session. Minto structure stays available as guidance; it stops being enforced by an extra model call each time a turn ends.

- **Minto Stop hook**: the single `Stop`-event handler of type `prompt` that the `minto-pyramid` package declares in its hook configuration. When a turn ends, it sends the assistant's result to a model, which either allows the stop or returns a correction request. A correction keeps the turn going [S1][S2].
- **Minto package**: the vendored `minto-pyramid` package under `.claude/skills/minto-pyramid/`, which `install.sh` copies to `~/.claude/skills/minto-pyramid/`. It contains the skill entry point, its rules (`core.md`, `completion-check.md`), templates, references, evals, package tests, a README, and the hook configuration.
- **Advisory guidance**: instructions Claude reads as context, without the harness enforcing them: the skill, its completion-check rule, and `.claude/rules/pyramid-principle.md`. Claude Code treats `CLAUDE.md` and rules content as context rather than enforced configuration [S3] (sourced; this repository records the same view in `docs/claude-config-design.md` §1).

In scope:

- Removing the Minto Stop hook.
- Updating the package's own tests and README so they stop describing or asserting the hook.
- Updating the one package reference sentence that states the hook as current behavior: `references/anthropic-guidance.md` line 24, "This plugin uses a `Stop` hook only for observable-output compliance." (observed). The general Claude Code facts on lines 9 and 21–23 of that file stay, because they describe Claude Code, not this package, and remain accurate [S2] (analysis A1).
- Updating the repository documents that describe the package as having a `Stop`-hook check (`README.md`, `README.ja.md`) or as copied verbatim from upstream (`README.md`, `README.ja.md`, `docs/claude-config-design.md` line 87, and the comment in `tests/run-config-pyramid.sh` lines 132–134; observed), since removing the hook makes the copy a local modification (analysis A3).

Out of scope:

- The `maintaining-living-documentation` package and its `SessionStart` and `Stop` hooks.
- The repository-level `PreToolUse` hook in `.claude/settings.json` (ADR-0008).
- The Minto skill's content, rules, templates, and evals, and `.claude/rules/pyramid-principle.md`.
- The archived Minto suite under `archive/`.
- Changes to `install.sh`. Its existing exact-replacement sync of `skills/` already deletes files that were removed from the source (observed in `install.sh`, `sync_path`: `rm -rf "$dst"` followed by `cp -R`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Turns end without a Minto compliance round-trip (Priority: P1)

As the repository owner, after I re-run the installer, my Claude Code turns end without the Minto check running. That removes the extra model call at every turn's end and the correction rounds that made Claude repeat or restate earlier output.

**Why this priority**: This is the change the user asked for. The rest only keeps the repository consistent with it.

**Independent Test**: Install from the changed repository, start a new session, and finish a substantive turn. Confirm that the installed Minto package declares no hooks, and that the turn ends without any Minto correction request.

**Acceptance Scenarios**:

1. **Given** the changed repository, **When** the Minto package's files are listed, **Then** it contains no hook configuration and declares no hooks in its manifest.
2. **Given** a user-level install made before this change, **When** the installer is re-run from the changed repository, **Then** the installed Minto package contains no hook configuration either.
3. **Given** a session started after that re-install, **When** a substantive turn ends, **Then** no Minto correction request appears and the turn ends on the first attempt (unless another, out-of-scope hook blocks it).
4. **Given** the same session, **When** the user asks for a substantive answer, **Then** the Minto skill and the pyramid-principle rule are still available as advisory guidance.

---

### User Story 2 - Package tests and docs match the package (Priority: P2)

As the maintainer, I can run the Minto package's own checks and read its README, and both describe the package as it now is: a skill with a self-applied completion check and no Stop hook.

**Why this priority**: As long as the package test asserts that a Stop hook exists, it fails after the hook is removed. A README that still describes an enforcement model the package no longer has misleads whoever reads it next.

**Independent Test**: Run the package's unit tests and the plugin validator, then search the package README for any description of a `Stop` hook as current behavior.

**Acceptance Scenarios**:

1. **Given** the changed package, **When** its unit tests run, **Then** they all pass, and no test requires a Stop hook to exist.
2. **Given** the changed package, **When** the plugin validator runs in strict mode, **Then** it reports no errors or warnings that this change introduced.
3. **Given** the package README, **When** a reader looks for its enforcement model, **Then** it says that compliance relies on the skill's own completion check and that the package declares no hooks.

---

### User Story 3 - Repository docs record the local divergence (Priority: P3)

As someone who later re-vendors or audits the package, I can see from the repository documentation that this copy of `minto-pyramid` no longer matches upstream, what was removed, and why.

**Why this priority**: Both READMEs currently say both vendored packages are copied verbatim from upstream. After this change, that claim is false for `minto-pyramid`. A later verbatim re-copy would bring the hook back without anyone noticing.

**Independent Test**: Read the vendored-plugin descriptions in `README.md` and `README.ja.md`, plus any design document that calls the package an unmodified upstream copy.

**Acceptance Scenarios**:

1. **Given** `README.md` and `README.ja.md`, **When** the description of `minto-pyramid` is read, **Then** neither mentions a `Stop`-hook check, and both note that the local copy has had its Stop hook removed.
2. **Given** the two READMEs, **When** compared, **Then** they state the same facts about this change (the repository's README-sync rule).
3. **Given** the documentation, **When** a reader asks why the hook was removed, **Then** the documented rationale cites its evidence and marks inferred reasons as inferred.

---

### Edge Cases

- **Stale installed copy**: if the owner does not re-run the installer, the hook in `~/.claude/skills/minto-pyramid/hooks/` keeps running (observed: that file exists in the current install). The documentation must say that re-running `install.sh` is required.
- **Manifest-declared hooks**: a plugin can declare hooks in its manifest, in addition to the default hook file [S2]. The removal covers both places, so no hook stays declared through the manifest.
- **Other Stop hooks**: the `maintaining-living-documentation` Stop hook is unaffected. A turn can still be blocked by that hook, and that is not a regression of this feature.
- **Future re-vendoring**: re-copying the upstream package verbatim would restore the hook. The local-divergence note (User Story 3) is the safeguard against that.
- **Package reference text**: `references/anthropic-guidance.md` line 24 describes the hook as this plugin's current behavior (observed). Leaving it would contradict the package after the change, and user information must match the system it describes [S7] (the standard's wording was not fetched: **unverified**). Only that sentence changes; the rest of `references/` stays byte-identical (FR-003, analysis A1).
- **Eval cases**: the package's eval cases grade output structure and do not depend on the hook (observed: no eval case references a hook). They stay unchanged. Whether their pass rates change without the hook is **unverified**: this specification measures nothing about it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Minto package MUST NOT declare any hook for any event, either in its default hook-configuration location or in its manifest.
- **FR-002**: After the installer is re-run, the user-level copy of the Minto package MUST likewise declare no hooks.
- **FR-003**: The Minto skill entry point, its rules (including `completion-check.md`), templates, references, and eval cases MUST remain present and unchanged, with one exception: line 24 of `references/anthropic-guidance.md` MUST be rewritten so it no longer states that the plugin uses a `Stop` hook (analysis A1). No other line of `references/` changes.
- **FR-004**: The package's unit tests MUST pass, and MUST NOT require a Stop hook. Every other existing assertion (manifest, skill text, resources, eval cases) MUST remain.
- **FR-005**: The package README MUST NOT describe a Stop hook as current behavior. It MUST state that compliance relies on the skill's self-applied completion check.
- **FR-006**: `README.md` and `README.ja.md` MUST stop describing `minto-pyramid` as having a `Stop`-hook check, MUST record that the local copy diverges from upstream by having the hook removed, and MUST stay consistent with each other. Every other repository document that calls `minto-pyramid` an unmodified (verbatim) upstream copy — `docs/claude-config-design.md` and the comment in `tests/run-config-pyramid.sh` (observed) — MUST likewise stop doing so; the test-script edit changes no command or assertion (analysis A3).
- **FR-007**: The `maintaining-living-documentation` package, `.claude/settings.json`, `.claude/rules/`, and `install.sh` MUST NOT change.
- **FR-008**: The documented rationale for the removal MUST separate sourced or observed facts from inferences, and MUST cite each non-obvious claim.
- **FR-009**: The repository's own test suites under `tests/` that pass before the change MUST still pass after it.

### Key Entities

- **Minto package**: the vendored skill package. Its relevant attributes are its hook declarations (none, after this change), its version identifier, and its divergence from upstream.
- **Installed copy**: the user-level mirror of the package. It is derived only by re-running the installer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The Minto package, both in the repository and in a fresh user-level install, declares 0 hooks.
- **SC-002**: In a session started after re-install, 0 of 5 consecutive substantive turns receive a Minto correction request.
- **SC-003**: 100% of the Minto package's unit tests and all previously passing repository test suites pass.
- **SC-004**: 0 current-behavior mentions of a Minto `Stop` hook remain in `README.md`, `README.ja.md`, the package README, and the package's `references/anthropic-guidance.md`; and 0 descriptions of `minto-pyramid` as an unmodified upstream copy remain in those files, `docs/claude-config-design.md`, or `tests/run-config-pyramid.sh` (the archive and historical spec records excluded; analysis A1, A3).
- **SC-005**: Every rationale statement in the changed documentation either cites a source or observation, or is labelled as inference.

## Assumptions

- **Scope (high confidence, inferred from the request's wording)**: "Retire the Minto Stop hook" means removing only the hook. The skill and its advisory guidance stay. The user did not ask to remove the skill.
- **Rationale (inferred, not stated by the user)**: The likely reasons are:
  - each turn's end incurs an extra model call (sourced: the package README says the hook "adds a small model-call cost at turn completion", and prompt hooks send the input to a model [S1]);
  - correction rounds caused repeated output (observed: commit `753eb52` exists to stop a "re-output loop").

  Neither reason is confirmed by the user.
- **Self-check is retained (high confidence)**: The skill's step 10 already tells Claude to apply `rules/completion-check.md` before completion, so self-applied structural checking continues without the hook (observed in `SKILL.md`).
- **Version identifier (medium confidence)**: Changing the package's version identifier to mark the local modification is recommended but not required. The plan decides it.
- **No ADR by default**: This change removes an external package's component rather than changing this repository's architecture. ADR-0005 covers the analogous removal of `.claude/hooks/`. Per the repository's documentation rules, a new ADR is proposed rather than created unless the user asks for one.
- **No AWS dependency**: The feature involves no AWS service, so the request's AWS-research instruction has no applicable target.

## Sources

- [S1] Anthropic, *Claude Code — Hooks reference* (Stop event, `stop_hook_active`, prompt-based hooks returning `ok`/`reason`, plugin hooks merging with user and project hooks): <https://code.claude.com/docs/en/hooks>
- [S2] Anthropic, *Claude Code — Plugin manifest reference* (standard layout: hooks default to `hooks/hooks.json`; the manifest `hooks` key merges with that file): <https://code.claude.com/docs/en/plugins-reference>
- [S3] Anthropic, *Claude Code — How Claude remembers your project*: "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead." <https://code.claude.com/docs/en/memory>
- [S7] ISO/IEC/IEEE 26514:2022, *Design and development of information for users* (same ID as research.md): <https://www.iso.org/standard/77451.html>
- ISO/IEC/IEEE 29148:2018, *Requirements engineering* — basis for the testable, unambiguous requirement form used above: <https://www.iso.org/standard/72089.html>

## Analysis Remediation Log

The `/speckit-analyze` report of 2026-10-07 was not persisted, so its findings were re-derived on 2026-10-07 by re-running the analysis against the repository; IDs A1–A7 below are those re-derived findings. Changes made in this file:

| ID | Severity | Finding | Change here |
|----|----------|---------|-------------|
| A1 | HIGH | `references/anthropic-guidance.md` line 24 states the hook as current behavior, while FR-003 froze all of `references/` | Scope bullet, Edge Case, FR-003 exception, SC-004 |
| A3 | MEDIUM | `docs/claude-config-design.md` and the `tests/run-config-pyramid.sh` comment were edited by the plan without a requirement | Scope bullet, FR-006, SC-004 |

A2 and A4–A7 are owned by plan.md or tasks.md and are logged there.
