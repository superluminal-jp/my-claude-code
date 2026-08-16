# Feature Specification: Remove Codex CLI Support and All Codex References

**Feature Branch**: `031-remove-codex-support`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Completely remove Codex CLI support and all references to Codex from this repository, and delete AGENTS.md entirely. Removes the root `AGENTS.md`, the README `## Codex CLI support` sections (English and Japanese), the Codex-referencing comment in `install.sh`, the dedicated `tests/run-codex-references.sh` and `tests/run-codex-drift.sh` suites, the Codex-specific checks inside `tests/run-subagent-delegation.sh` and `tests/run-digital-agency-frontend-skill.sh`, and the Codex mention in `tests/run-mcp-startup.sh`'s comment — while leaving `specs/*` history, `docs/adr/0002-*`/`0004-*` bodies, and Spec Kit's own `codex` multi-agent-integration bookkeeping (`.specify/integrations/codex.manifest.json`, the `codex` entry in `.specify/extensions/.registry`) untouched, and adding a superseding ADR."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The repository no longer ships any Codex-facing guidance (Priority: P1)

As the maintainer, I want the root `AGENTS.md` file deleted so the repository stops shipping guidance for Codex CLI to read natively, matching the decision to drop Codex support entirely rather than maintain a parity layer for it.

**Why this priority**: `AGENTS.md` is the single file Codex CLI reads automatically; its presence is itself a declaration that this repository supports Codex. Deleting it is the core, irreducible action this feature exists to perform.

**Independent Test**: After the change, `AGENTS.md` does not exist at the repository root (`test -f AGENTS.md` fails).

**Acceptance Scenarios**:

1. **Given** `AGENTS.md` currently exists at the repository root (90 lines, Codex-specific guidance), **When** the removal is complete, **Then** the file no longer exists anywhere in the repository.
2. **Given** other files reference `AGENTS.md` by path (README.md, README.ja.md, two test suites), **When** `AGENTS.md` is deleted, **Then** none of those references remain dangling — each referencing file is updated or its Codex-specific reference removed in the same change.

---

### User Story 2 - The documentation makes no Codex claims (Priority: P1)

As a reader of `README.md` or `README.ja.md`, I want no mention of Codex CLI, its `/import` flow, or Codex-specific guardrail behavior, so the documentation accurately reflects that this repository no longer supports or documents Codex in any capacity.

**Why this priority**: Equal weight to User Story 1 — leaving Codex documentation in place while deleting the file it describes (`AGENTS.md`) would make the README actively wrong, which is worse than having no Codex section at all.

**Independent Test**: A case-insensitive search for "codex" in `README.md` and `README.ja.md` returns no matches.

**Acceptance Scenarios**:

1. **Given** `README.md` currently has a `## Codex CLI support` section (~line 48–193) plus scattered references (an `AGENTS.md` bullet, a file-structure tree row, two test-suite mentions under Verification, and `--integration codex` example lines), **When** the removal is complete, **Then** none of these remain and the surrounding sections read as a coherent document with no gap.
2. **Given** `README.ja.md` mirrors the same content in Japanese (`## Codex CLI サポート`, ~line 59–146, plus the same scattered references), **When** the removal is complete, **Then** the Japanese document is updated in lockstep and reads coherently.
3. **Given** `install.sh`'s header comment (lines 6–9) currently tells the reader "see README.md § Codex CLI support and docs/adr/0004-...", **When** the referenced section is gone, **Then** the comment no longer points to it and does not otherwise name Codex.

---

### User Story 3 - The test suite has no dead or dangling Codex checks (Priority: P1)

As the maintainer, I want every test file that referenced Codex or `AGENTS.md` updated or removed, so the test suite continues to pass and does not assert against files or sections that no longer exist.

**Why this priority**: Equal weight to the above — a passing test suite is the only mechanical guarantee that this repository-wide removal didn't silently break verification. Un-updated tests would fail immediately or, worse, mask breakage by asserting on the wrong thing.

**Independent Test**: Every `tests/run-*.sh` suite exits successfully, and no test file references `AGENTS.md`, `codex`, or the two deleted suites by name.

**Acceptance Scenarios**:

1. **Given** `tests/run-codex-references.sh` exists solely to verify `AGENTS.md` stays in sync with `.claude/rules/*`, **When** `AGENTS.md` is deleted, **Then** this suite is deleted too (it has nothing left to verify).
2. **Given** `tests/run-codex-drift.sh` exists solely to re-derive the live Codex-version facts backing the README's Codex section, **When** that section is deleted, **Then** this suite is deleted too.
3. **Given** `tests/run-subagent-delegation.sh` has a check asserting `AGENTS.md` addresses delegation for Codex, **When** `AGENTS.md` is deleted, **Then** that check and its supporting comment are removed or rewritten so the suite still passes and still verifies something meaningful about subagent delegation.
4. **Given** `tests/run-digital-agency-frontend-skill.sh` has a check asserting `AGENTS.md` lists Codex routing for the digital-agency-frontend skill, **When** `AGENTS.md` is deleted, **Then** that check and its supporting comment are removed or rewritten so the suite still passes.
5. **Given** `tests/run-mcp-startup.sh` has one comment line naming Codex as an example of what a failed MCP handshake report looks like, **When** the removal is complete, **Then** the comment is reworded to make the same point without naming Codex.
6. **Given** the full remaining `tests/run-*.sh` suite set, **When** all edits above are complete, **Then** no suite that passed before this change starts failing, and the suites this feature edits directly (`tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh`) contain no remaining Codex-specific check or comment. (Two suites — `tests/run-install.sh` and `tests/run-subagent-delegation.sh` — already fail on `main` for reasons unrelated to Codex, per spec 030's incomplete cleanup; fixing those pre-existing failures is out of scope for this feature.)

---

### User Story 4 - The decision is recorded, not silently made (Priority: P2)

As a future reader of `docs/adr/`, I want a new Architecture Decision Record explaining why Codex CLI support was dropped entirely (rather than continuing the "documented, user-driven `/import`" approach from ADR-0004), so the rationale and rejected alternative are on the permanent record the same way every prior Codex-related architectural decision was.

**Why this priority**: Lower priority than the mechanical removal itself (Stories 1–3), but still required before this feature is complete — the removal reverses the operative decision behind this repository's Codex relationship (ADR-0004, currently Status: Proposed — it was acted on by spec 021 but never formally moved to Accepted; ADR-0002 is already marked Superseded by 0004), and this repository's own convention requires that reversal to be recorded, not silently overwritten.

**Independent Test**: `docs/adr/` contains a new numbered ADR whose Status is Accepted and whose body names ADR-0004 as Superseded (and describes ADR-0002's already-Superseded status accurately); ADR-0002's body is byte-for-byte unchanged, and ADR-0004's body is unchanged except for its Status line.

**Acceptance Scenarios**:

1. **Given** ADR-0004 ("adopt official codex import") is currently Status: Proposed — the decision spec 021 actually implemented, even though it was never formally moved to Accepted — **When** this feature is implemented, **Then** a new ADR is added with Status Accepted, and ADR-0004's Status line (only) is changed to "Superseded by [new ADR number]".
2. **Given** ADR-0002 ("deploy codex configuration at user scope") is already marked "Superseded by 0004", **When** the new ADR is written, **Then** ADR-0002 is left untouched (it already points forward through ADR-0004, which now itself points forward to the new ADR) and the new ADR's Context section states this chain accurately.
3. **Given** ADRs are immutable once accepted as the operative decision, **When** ADR-0004 is touched, **Then** only its Status line changes — no other line in its body is edited; ADR-0002 is not edited at all.

### Edge Cases

- **`.gitignore` lines mentioning Codex/`.codex/`/`.agents/`**: these ignore directories a developer's own tooling (OpenAI's `/import`, `migrate-to-codex`) could still create locally, independent of whether this repository documents or supports that workflow. Removing the ignore rule would not stop Codex from writing there — it would just make any such local artifact show up as untracked noise in `git status` for any developer who still runs `/import` on their own initiative. **Resolution**: keep the `.gitignore` entries (`.codex/`, `.agents/`), and reword their explanatory comment to describe the directories generically (external CLI tooling this repository does not generate or manage) without the word "Codex" in prose. The literal path segments `.codex/`/`.agents/` themselves cannot avoid containing the substring "codex" — that is the actual, external tool's own directory-naming convention, not this repository documenting or supporting it, so SC-001's repository-wide "codex" search excludes `.gitignore`'s two directory-ignore lines on that basis while still requiring the prose comment above them to drop the word.
- **`.specify/integrations/codex.manifest.json` and the `codex` entry in `.specify/extensions/.registry`**: these track Spec Kit's own unrelated `specify init --integration codex` multi-agent-integration feature (hashes of gitignored `.agents/skills/speckit-*` files), not this repository's Codex CLI guardrail-parity documentation. Confirmed out of scope — see Assumptions.
- **Historical `specs/NNN-*/` directories** (007, 012, 013, 014, 021, 029, and others) whose own narrative names Codex: left untouched, per the precedent already established by specs 024–029.
- **What if a test file's Codex-specific check is the *only* check in a `describe`-style block?** None of the four affected test files (`run-subagent-delegation.sh`, `run-digital-agency-frontend-skill.sh`, `run-mcp-startup.sh`) have this shape — each Codex-related check is one assertion among several; removing or rewording it leaves the rest of the suite intact.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST NOT contain a file named `AGENTS.md` at its root after this change.
- **FR-002**: `README.md` and `README.ja.md` MUST NOT contain the substring "codex" (case-insensitive) anywhere, including section headings, prose, file-tree diagrams, command examples, and the Verification section's test list.
- **FR-003**: `install.sh` MUST NOT reference `AGENTS.md`, the README's Codex section, or `docs/adr/0004-adopt-official-codex-import.md` by name in its header comment or anywhere else in the file.
- **FR-004**: `tests/run-codex-references.sh` and `tests/run-codex-drift.sh` MUST be deleted from the repository.
- **FR-005**: `tests/run-subagent-delegation.sh` MUST NOT assert against `AGENTS.md` for Codex-specific content; it MUST continue to pass and continue verifying subagent-delegation behavior through some other means (a Claude Code-facing check, or removal of the assertion if no longer meaningful).
- **FR-006**: `tests/run-digital-agency-frontend-skill.sh` MUST NOT assert against `AGENTS.md` for Codex routing content; it MUST continue to pass.
- **FR-007**: `tests/run-mcp-startup.sh` MUST NOT contain the word "Codex" in any comment or string; the check it documents MUST remain functionally unchanged.
- **FR-008**: No `tests/run-*.sh` suite that exits successfully before this change MUST start failing because of this change; the three suites this feature edits directly (`tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh`) MUST contain no remaining Codex-specific check, comment, or string afterward. (`tests/run-install.sh` and `tests/run-subagent-delegation.sh` already fail on `main` before this change for reasons unrelated to Codex — spec 030's incomplete cleanup of `.claude/rules/subagent-delegation.md`; fixing those pre-existing failures is out of scope.)
- **FR-009**: A new ADR MUST be added to `docs/adr/` with Status Accepted, documenting the decision to drop Codex CLI support entirely and naming ADR-0004 as superseded (and describing ADR-0002's already-superseded status accurately).
- **FR-010**: `docs/adr/0002-deploy-codex-configuration-at-user-scope.md` and `docs/adr/0004-adopt-official-codex-import.md` MUST NOT be edited except for their Status line.
- **FR-011**: No file under `specs/` MUST be modified by this change.
- **FR-012**: `.specify/integrations/codex.manifest.json` and the `codex` entry in `.specify/extensions/.registry` MUST NOT be modified by this change.
- **FR-013**: `.gitignore`'s Codex-related entries (`.codex/`, `.agents/`) MUST be retained, with their explanatory comment reworded to drop citations to the now-deleted README section and specs, per the Edge Cases resolution above.

### Key Entities

- **`AGENTS.md`**: The repo-root file Codex CLI reads natively (flattened from `.claude/CLAUDE.md` and `.claude/rules/`). Deleted entirely.
- **README `## Codex CLI support` / `## Codex CLI サポート` sections**: The English and Japanese documentation of how a developer brings their own Codex configuration via `/import`. Deleted entirely, along with every other Codex mention in both files.
- **`tests/run-codex-references.sh`**: Verified `AGENTS.md` stayed in sync with `.claude/rules/*`. Deleted.
- **`tests/run-codex-drift.sh`**: Re-derived live Codex-version facts backing the README section. Deleted.
- **Codex-specific checks inside `tests/run-subagent-delegation.sh` and `tests/run-digital-agency-frontend-skill.sh`**: Individual assertions referencing `AGENTS.md`/Codex within otherwise-surviving suites. Removed or rewritten in place.
- **New ADR**: Records the decision to drop Codex support entirely, superseding ADR-0004 and (per its current status) ADR-0002.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repository-wide case-insensitive search for "codex" — excluding `specs/`, `docs/adr/0002-*`, `docs/adr/0004-*`, the new superseding ADR's required references to those two files, `.specify/integrations/`, `.specify/extensions/.registry`, and `.gitignore`'s two literal `.codex/`/`.agents/` directory-ignore lines (not their comment) — returns zero matches.
- **SC-002**: `AGENTS.md` does not exist at the repository root.
- **SC-003**: `tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, and `tests/run-mcp-startup.sh` — the suites this feature edits — run without a new failure caused by this feature's edits (pre-existing, unrelated failures in `tests/run-subagent-delegation.sh` are unaffected by this feature and remain open per spec 030); every other `tests/run-*.sh` suite continues to pass exactly as it did before this change.
- **SC-004**: `docs/adr/` contains exactly one new file whose Status is Accepted and whose body names the superseded ADR(s); `docs/adr/0002-*.md` is byte-for-byte unchanged and `docs/adr/0004-*.md` differs from its pre-change version only in its Status line.
- **SC-005**: `git status --porcelain specs/` and `git status --porcelain .specify/integrations/ .specify/extensions/.registry` both return no output (neither tree is touched).

## Assumptions

- **`.specify/integrations/codex.manifest.json` and the `codex` entry in `.specify/extensions/.registry` are out of scope.** They track Spec Kit's own machine-generated bookkeeping for its `specify init --integration codex` multi-agent-integration feature (hashes of gitignored `.agents/skills/speckit-*` files) — a different, orthogonal use of "codex" as a Spec Kit integration identifier, not hand-authored documentation of this repository's Codex CLI guardrail-parity effort. Regenerating or removing this bookkeeping is the `specify` CLI's job (via its own integration-management commands), not a hand edit, and doing so is a separate decision from "does this repository describe or support Codex CLI." This mirrors the reasoning already applied in spec 029's Assumptions section for a different Codex-adjacent artifact.
- **Historical `specs/NNN-*/` directories are not retroactively edited**, per the precedent established by specs 024–029 and restated in spec 029's own Assumptions section.
- **`.gitignore`'s Codex-related ignore rules are kept, not deleted**, per the Edge Cases resolution: they guard against local tooling output (`/import`, `migrate-to-codex`) a developer might still run on their own initiative, independent of whether this repository documents that workflow.
- **A new ADR is required**, unlike spec 029's single plugin-registration removal. This change reverses the operative architectural decision governing how this repository relates to Codex (ADR-0004, Status: Proposed but implemented by spec 021; itself superseding ADR-0002) — that is exactly the "architecturally significant, hard to reverse, prior decision superseded" case this repository's own ADR policy requires recording (`.claude/rules/live-documentation.md` § 0, ADR row; `adr` skill).
- **`tests/run-subagent-delegation.sh` and `tests/run-digital-agency-frontend-skill.sh` keep the rest of their assertions.** Only the Codex/`AGENTS.md`-specific check in each is removed or rewritten; no other verification in either suite is affected by this feature.
