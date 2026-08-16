# Feature Specification: Remove subagent-delegation Rule

**Feature Branch**: `030-remove-subagent-delegation-rule`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Remove the subagent-delegation Claude rule. Delete .claude/rules/subagent-delegation.md entirely and remove its reference from .claude/CLAUDE.md (the \"Execution: parallelize whenever valid\" section's line pointing to it) and from README.md's file-tree listing at line 247. Rationale: the file's decision guidance (when to delegate vs. stay in-conversation) is judgment the Claude model already makes correctly without an explicit rule; keeping it adds always-loaded context for no behavioral gain. Priority: reduce always-loaded context length. This follows the repo's existing removal-spec pattern (018-remove-solo-practice, 024-remove-verify-config, 025-remove-claude-hooks, 026-remove-permissions-config, 027-remove-scripts, 029-remove-codex-plugin). No replacement content is added elsewhere — this is a straight removal, not a rewrite."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Always-loaded context shrinks with no dangling references (Priority: P1)

As the maintainer, I want `.claude/rules/subagent-delegation.md` deleted and every live pointer to it removed, so every `/speckit`-driven or ordinary session loads less always-on instruction text while still finding no broken reference to a file that no longer exists.

**Why this priority**: The rule's own content states its judgment ("delegate when output is large, self-contained, or independent") is exactly the kind of default reasoning the Claude model performs without being told — keeping it costs context on every turn for no behavioral gain. Reducing that always-loaded footprint is the explicit purpose of this change.

**Independent Test**: `.claude/rules/subagent-delegation.md` does not exist. A repository-wide search for `subagent-delegation` outside `specs/` and `docs/adr/` finds no `@`-include, no prose reference, and no file-tree listing.

**Acceptance Scenarios**:

1. **Given** `.claude/rules/subagent-delegation.md` currently exists, **When** the removal is complete, **Then** the file does not exist at that path.
2. **Given** `.claude/CLAUDE.md`'s "Execution: parallelize whenever valid" section currently contains an `@.claude/rules/subagent-delegation.md` include line and a sentence saying "Whether work belongs in a subagent at all is `rules/subagent-delegation.md`'s decision — check it before planning non-trivial work, not after", **When** the removal is complete, **Then** neither the include line nor any sentence pointing to that file remains, and the surrounding section still reads coherently on its own (governs *how* to issue parallel calls, without depending on the deleted file for *whether* to delegate).
3. **Given** `README.md` line 247 currently lists `subagent-delegation.md  # Whether work runs here or in a subagent` in the repository file-tree, **When** the removal is complete, **Then** that line is absent from the tree.
4. **Given** other project instruction files (e.g. `.claude/rules/live-documentation.md`, other rule files) do not reference `subagent-delegation.md`, **When** the removal is complete, **Then** no other live (non-historical) file has been left with a broken reference.

### Edge Cases

- What happens to `specs/020-subagent-delegation-rule/` (the spec that originally created the file) and other historical specs (`specs/021-codex-official-import/`, `specs/024-remove-verify-config/`) that mention it? Left untouched, per the convention already established in specs/018, 024–027, 029 — historical specs are not retroactively edited.
- Does this removal add replacement guidance anywhere else in `.claude/`? No — confirmed with the user this is a straight removal, not a rewrite; no content is relocated into `CLAUDE.md` or another rule file.
- Was a lighter alternative (trimming the file to keep only harness-specific facts such as the `AskUserQuestion`-unavailable-in-subagents note and the fork/`skills:`/direct-delegation mechanism table) considered? Yes — discussed and drafted with the user first; the user explicitly chose full deletion over the trim once the priority was stated as reducing always-loaded context length, since a trim still carries a non-zero always-loaded cost.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST NOT contain `.claude/rules/subagent-delegation.md` after the change.
- **FR-002**: `.claude/CLAUDE.md` MUST NOT contain the `@.claude/rules/subagent-delegation.md` include line.
- **FR-003**: `.claude/CLAUDE.md`'s "Execution: parallelize whenever valid" section MUST NOT reference `subagent-delegation.md` or claim it governs whether to delegate; the section MUST remain self-contained, covering only *how* to issue parallel calls.
- **FR-004**: `README.md` MUST NOT list `subagent-delegation.md` in its repository file-tree or describe it as an active rule.
- **FR-005**: No other live (non-`specs/`, non-`docs/adr/`) file in the repository MUST reference `subagent-delegation.md` after the change.
- **FR-006**: `specs/020-subagent-delegation-rule/`, `specs/021-codex-official-import/`, `specs/024-remove-verify-config/`, and every other historical `specs/NNN-*/` directory MUST be left unmodified.
- **FR-007**: No replacement content describing subagent-delegation judgment MUST be added to `.claude/CLAUDE.md` or any other rule file as part of this change.

### Key Entities

- **`.claude/rules/subagent-delegation.md`**: The rule file being deleted in full — both its generic "when to delegate" judgment heuristics and its harness-specific facts (no `AskUserQuestion` in subagents, fork vs. `skills:` vs. direct-delegation mechanism table).
- **`.claude/CLAUDE.md` § "Execution: parallelize whenever valid"**: Retains its own content about issuing independent calls in parallel; loses its `@`-include and its cross-reference sentence to the deleted file.
- **`README.md` file-tree listing**: Loses the one line describing `subagent-delegation.md`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `.claude/rules/subagent-delegation.md` does not exist as a file in the repository.
- **SC-002**: A repository-wide search for `subagent-delegation` outside `specs/` and `docs/adr/` returns zero matches.
- **SC-003**: The set of files `@`-included from `.claude/CLAUDE.md` (its always-loaded context) is smaller by exactly the removed file's line count, with no offsetting addition elsewhere in the always-loaded set.
- **SC-004**: `.claude/CLAUDE.md` and `README.md` each still read as internally consistent documents when reviewed on their own, with no leftover sentence that presupposes the deleted file's existence.

## Assumptions

- The rule's generic delegation-judgment guidance ("delegate when output is large, self-contained, or independent; stay in-conversation when back-and-forth or shared context is needed") is judgment the Claude model already applies correctly by default; no evidence of misbehavior was cited as a reason to keep it — the stated priority for removal is reducing always-loaded context length, not a correctness gap.
- No Architecture Decision Record is proposed for this change. Removing a rules file is a two-way-door, git-reversible edit to instruction text, not an architecturally significant decision with a rejected implementation alternative — consistent with specs/018-remove-solo-practice and specs/029-remove-codex-plugin, neither of which received an ADR, unlike specs/025–027 which changed enforcement mechanisms.
- Following the precedent set by specs/018, 024–027, and 029, historical `specs/` directories referencing the deleted file are not retroactively edited.
