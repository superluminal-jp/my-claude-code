# Feature Specification: Isolate high-volume verification output from the parent context

**Feature Branch**: `019-verify-fork-test-runner`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "推奨した5件のうち #2（`/verify-config` のフォーク化）と #4（テストスイート実行の委譲）を実装する。Spec Kit で進め、サブエージェントを使う。"

## Context

Verification work in this repository is high-volume and low-signal. Running `shellcheck`, `shfmt -d`, `jq`, the MCP consistency script, and the `tests/run-*.sh` behaviour suites produces large raw output, of which only the pass/fail verdict and the first hard failure matter. Today that entire raw output lands in the main conversation, where it is never referenced again.

This feature moves that output out of the main conversation. It changes *where verification runs*, not *what is verified*: the checks, their order, and their verdicts stay as they are today.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Running the configuration check no longer floods the conversation (Priority: P1)

An operator asks for the repository's configuration to be verified. The checks run as they always have — JSON validity, import integrity, hook lint and format, MCP catalog consistency, behaviour suites, hook unit tests — but the raw tool output stays out of the main conversation. What returns is the `✓`/`✗` checklist and the first hard failure with its output.

**Why this priority**: This is the feature. Until the verbose output is actually isolated, nothing has been gained.

**Independent Test**: Invoke the configuration check and confirm that (a) the same steps are reported with the same verdicts as before, and (b) the raw `shellcheck`/`shfmt`/suite output does not appear in the main conversation.

**Acceptance Scenarios**:

1. **Given** a repository whose configuration is valid, **When** the operator runs the configuration check, **Then** every step is reported as `✓` with a one-line reason and an overall verdict, and no raw lint or suite output appears in the main conversation.
2. **Given** a repository with a malformed `.claude/settings.json`, **When** the operator runs the configuration check, **Then** the first hard failure is reported as `✗` together with the output needed to diagnose it.
3. **Given** the check is running, **When** it needs a tool outside the reduced background tool set, **Then** it still completes rather than failing part-way.
4. **Given** the check has completed, **When** the operator inspects the working tree, **Then** no file has been modified by the check.

---

### User Story 2 - Running the behaviour suites returns only what failed (Priority: P1)

An operator asks for the behaviour suites to be run. The suites execute in isolation and the main conversation receives only the per-suite pass/fail result and, for failures, the failing assertion and its error output — not the full transcript of every passing case.

**Why this priority**: Equal to Story 1 and independently valuable. The behaviour suites drive the `claude` CLI, so their raw output is the largest single source of disposable text in this repository. This story delivers value even if Story 1 is not implemented, and vice versa.

**Independent Test**: Ask for the behaviour suites to be run and confirm that passing suites contribute a single result line each while failing suites contribute their diagnostic output.

**Acceptance Scenarios**:

1. **Given** all behaviour suites pass, **When** the operator asks for them to be run, **Then** the main conversation receives one result line per suite and an overall verdict, without per-case transcripts.
2. **Given** one suite fails, **When** the operator asks for the suites to be run, **Then** the failing suite is named together with the failing assertion and enough output to diagnose it, and the other suites are still reported.
3. **Given** the `claude` CLI is unavailable in the environment, **When** the suites that require it are run, **Then** those suites are reported as skipped with a stated reason rather than as failures.
4. **Given** the suites are run, **When** they complete, **Then** no source or configuration file has been modified.

---

### User Story 3 - The repository's own documentation states where verification runs (Priority: P2)

A contributor reading the repository's documentation can see that verification runs in an isolated context, which artifact provides it, and how to invoke it.

**Why this priority**: Lower than P1 because the capability works without it, but this repository treats a capability whose declared surface does not match its actual surface as drift. The inventory documents that list the project's skills and commands are part of the change, not a follow-up.

**Independent Test**: Read the repository's skill/command inventory documents and confirm each names the current artifact and its invocation path, with no reference to a path that no longer exists.

**Acceptance Scenarios**:

1. **Given** the configuration check has moved, **When** a contributor greps the repository for its former location, **Then** no document still points at a path that no longer exists.
2. **Given** the new verification artifacts exist, **When** a contributor reads the skill inventory, **Then** both are listed in the same format as the existing entries.

---

### Edge Cases

- **A required external tool is missing.** When `shellcheck`, `shfmt`, `jq`, or `yamllint` is absent, the affected step is reported as skipped with a stated reason rather than silently passing or hard-failing the run.
- **The isolated run needs approval for a command.** A verification command that is not pre-approved must surface its approval prompt to the operator rather than being silently denied, since a silent denial would be reported as a failed check.
- **The isolated run is asked a question it cannot ask.** Verification must never require an interactive decision; if a step is ambiguous it is reported as `✗` with the ambiguity stated, not resolved by guessing.
- **Verification is requested twice concurrently.** The second request must not interleave its output with the first or report the first run's verdict as its own.
- **A check would modify a file.** Format checks report diffs only; a verification run that would write is a defect, not an accepted outcome.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The configuration check MUST run in a context isolated from the main conversation, so that its raw tool output does not enter the main conversation.
- **FR-002**: The configuration check MUST return the same step-by-step `✓`/`✗` checklist, one-line reasons, and overall verdict that it returns today, and MUST surface the first hard failure with its output.
- **FR-003**: The configuration check MUST NOT modify any file.
- **FR-004**: The configuration check MUST remain invocable by the operator on demand.
- **FR-005**: The behaviour suites MUST be runnable in a context isolated from the main conversation, returning per-suite results and failure diagnostics only.
- **FR-006**: The behaviour-suite runner MUST report a suite whose prerequisites are unavailable as skipped with a stated reason, distinct from a failure.
- **FR-007**: The behaviour-suite runner MUST NOT modify any file, and MUST NOT attempt to fix a failure it discovers.
- **FR-008**: Both artifacts MUST have access to the tools their steps require; a reduced tool set that would break a step is not acceptable.
- **FR-009**: Every document in the repository that enumerates the project's skills or commands MUST list these artifacts and MUST NOT reference a location that no longer exists.
- **FR-010**: The isolated runs MUST NOT depend on the main conversation's history, since that history is not available to them.

### Key Entities

- **Configuration check**: the operator-invoked verification of `.claude/` — JSON validity, import integrity, hook lint/format, MCP catalog consistency, behaviour suites, hook unit tests. Produces a checklist and a verdict.
- **Behaviour-suite run**: an execution of the repository's `tests/run-*.sh` suites. Produces per-suite results and, on failure, diagnostics.
- **Skill/command inventory**: the set of documents that declare which skills and commands this repository provides.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the configuration check adds no raw `shellcheck`, `shfmt`, `jq`, or behaviour-suite output to the main conversation — only the checklist, the first hard failure's output, and the verdict.
- **SC-002**: The configuration check reports the same steps, in the same order, with the same verdicts as it does before this change, for both a passing and a deliberately broken configuration.
- **SC-003**: Running all behaviour suites when they pass contributes at most one result line per suite plus an overall verdict to the main conversation.
- **SC-004**: A grep of the repository for the configuration check's former location returns no hits in any document.
- **SC-005**: Neither artifact leaves the working tree modified after a run (`git status` is unchanged).

## Assumptions

- The set of checks and their order are correct today and are carried over unchanged; this feature relocates where they run, and does not re-scope what is verified.
- Verification is inherently non-interactive: no verification step legitimately requires asking the operator a question mid-run. This is what makes isolation safe here, and it is stated as a constraint (FR-010, Edge Cases) rather than assumed silently.
- The behaviour suites' existing skip-when-unavailable behaviour is the intended contract and is preserved rather than redesigned.
- The repository's project constitution (`.specify/memory/constitution.md`) is an unfilled template, so no project-specific constitutional gate applies to this feature beyond the rules in `.claude/CLAUDE.md` and `.claude/rules/`.
