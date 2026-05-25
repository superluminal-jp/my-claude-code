# Feature Specification: Live Documentation Enforcement

**Feature Branch**: `009-live-doc-enforcement`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Live Documentation を強制するスキルもしくはルールを作成。Live Documentation のベストプラクティスに従う。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch Documentation Drift at Review Time (Priority: P1)

A developer makes code changes and asks Claude to review the diff or commit. Claude checks whether documentation has been updated in the same change. If code changed but docs did not, Claude flags the drift and explains which documentation is now stale, before the change is committed or merged.

**Why this priority**: Documentation drift is hardest to fix after the fact. Catching it at the earliest possible point (review/commit time) is the highest-value enforcement moment.

**Independent Test**: Can be fully tested by modifying a function while leaving its accompanying documentation unchanged, then asking Claude to review the diff — Claude MUST flag the undocumented change.

**Acceptance Scenarios**:

1. **Given** a code change that modifies a public API, **When** the accompanying doc comment or spec is not updated in the same change, **Then** Claude flags the drift and refuses to mark the review complete until docs are addressed.
2. **Given** a code change that is purely internal (private helpers, no public contract change), **When** no documentation update is needed, **Then** Claude does not flag a false positive.
3. **Given** a diff where both code and its nearby documentation are updated together, **When** Claude reviews, **Then** Claude confirms synchronization and proceeds without warnings.

---

### User Story 2 - Block Separate Documentation PRs (Priority: P2)

A developer opens a standalone documentation-only PR that describes a feature already shipped in a prior commit. Claude identifies that the documentation is being added separately from the code it describes, flags this as a Live Documentation violation, and instructs the developer to amend the original code commit instead (or accept the separation explicitly with a stated reason).

**Why this priority**: Separate documentation PRs are the primary cause of documentation drift. Preventing them structurally eliminates a major source of "docs lie."

**Independent Test**: Can be tested independently by presenting Claude with a PR that only modifies Markdown files describing existing code — Claude MUST flag it as a Live Doc violation.

**Acceptance Scenarios**:

1. **Given** a PR that contains only documentation changes (no code changes), **When** Claude reviews it, **Then** Claude asks whether the described code was shipped in a prior commit and, if so, flags the separation as a violation.
2. **Given** a developer explicitly states the separation is intentional (e.g., retroactive documentation sprint), **When** Claude is informed, **Then** Claude records the exception and proceeds without blocking.

---

### User Story 3 - Identify Auto-Generatable Documentation (Priority: P3)

A developer asks Claude to write or update a documentation artifact (e.g., API reference, parameter list, schema description). Claude inspects the source and determines whether the artifact can be produced automatically from the code (doctest, OpenAPI annotations, type signatures). If auto-generation is possible, Claude recommends the automated approach rather than hand-writing the content.

**Why this priority**: Hand-written documentation that duplicates code-derivable information is the root cause of Curated Redundancy. Eliminating it structurally is more sustainable than enforcing update discipline.

**Independent Test**: Can be tested independently by asking Claude to "write the API docs for this function" when the function already has type annotations — Claude MUST recommend using the auto-generation tool rather than writing the docs manually.

**Acceptance Scenarios**:

1. **Given** a request to document a function that has complete type signatures and docstrings, **When** an auto-generation tool exists in the project toolchain, **Then** Claude recommends using the tool and declines to hand-write the content.
2. **Given** a request to document a concept that cannot be derived from code (architecture rationale, design decisions), **When** no auto-generation path exists, **Then** Claude writes the documentation and places it proximate to the relevant code.

---

### User Story 4 - Enforce Proximity of Documentation (Priority: P3)

A developer asks Claude to add or update documentation. Claude ensures the documentation is placed in the closest possible location to the code it describes (inline docstring, adjacent README, co-located spec file), rather than in a remote wiki page or central document store that can drift independently.

**Why this priority**: Proximity is the structural guarantee that docs and code stay in sync. Remote docs drift by default.

**Independent Test**: Can be tested independently by asking Claude to "document the authentication module" — Claude MUST create the doc file adjacent to the module, not in a top-level docs/ folder.

**Acceptance Scenarios**:

1. **Given** a request to add documentation for a module, **When** Claude responds, **Then** the documentation is placed in the same directory as the module or inline within the source file.
2. **Given** an existing remote documentation location (e.g., `docs/` root), **When** Claude is asked to add content, **Then** Claude warns that proximity is preferred and proposes the nearest co-located location.

---

### Edge Cases

- What happens when a code change is an automated refactor (rename, formatting) where documentation wording change would be cosmetic only?
- How does the enforcement handle generated files (e.g., migration files, build artifacts) that are not human-documented?
- What happens when the user explicitly overrides the enforcement for a specific change?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Claude MUST check that documentation is updated in the same change (commit/PR) as the code it describes.
- **FR-002**: Claude MUST flag any standalone documentation change that covers already-shipped code as a Live Documentation violation.
- **FR-003**: Claude MUST identify when a requested documentation artifact can be produced automatically from the code and recommend the automated path instead of hand-writing.
- **FR-004**: Claude MUST place documentation in the physically closest location to the code it describes; any placement in a remote or centralized location requires explicit justification.
- **FR-005**: Claude MUST refuse to write duplicate documentation when the information already exists in another location derivable from the same source.
- **FR-006**: Claude MUST allow developers to explicitly override enforcement for a given change, provided the override reason is stated and recorded.
- **FR-007**: Claude MUST apply enforcement passively as an always-on rule — integrated into code review, commit feedback, and documentation-writing flows — without requiring an explicit invocation. The enforcement is delivered as a rule file (`.claude/rules/live-documentation.md`) that applies in every relevant context automatically.

### Key Entities

- **Documentation Artifact**: Any file, comment, or annotation whose primary purpose is to describe code behavior (docstring, README, spec, OpenAPI annotation, changelog entry).
- **Code Change**: A modification to source code, configuration, or schema that alters observable behavior or public contract.
- **Drift**: A state where a Documentation Artifact no longer accurately describes the corresponding Code Change.
- **Override**: An explicit developer decision to accept a Live Documentation violation for a stated reason, recorded in the change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Documentation drift is caught at commit or PR review time in 100% of cases where Claude reviews the change.
- **SC-002**: Separate documentation PRs are flagged within one turn — no drift escapes to the main branch undetected when Claude is in the review loop.
- **SC-003**: Developers receive a specific, actionable correction (not a generic warning) within one response turn, so they can fix the issue without follow-up prompting.
- **SC-004**: False-positive rate for pure-refactor changes (no contract change) is zero — Claude correctly identifies when no documentation update is required.
- **SC-005**: When auto-generation is available, Claude recommends it in 100% of cases rather than hand-writing equivalent content.

## Assumptions

- Claude Code is used for code review, commit feedback, and documentation-writing within this project.
- The project has at least one code change workflow where Claude participates (review, commit, or pair-programming session).
- Auto-generation tooling is identified per-project and specified in the rule/skill context; the enforcement does not assume a universal toolchain.
- The enforcement applies to this project (`my-claude-code`) initially; portability to other projects is out of scope for v1.
- Inline docstrings and co-located spec files are the preferred proximity targets; wiki pages and remote documentation hosts are out of scope.
