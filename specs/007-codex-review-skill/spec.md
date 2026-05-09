# Feature Specification: OpenAI Codex Review Skill

**Feature Branch**: `007-codex-review-skill`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "openai codex に claude code で作成した成果物をレビューさせるスキルを追加する。openaiのAPIが設定されcodexがインストールされている場合のみ起動する。どのような成果物をどのような観点でレビューさせるのかは要議論"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prerequisite Guard (Priority: P1)

A developer invokes the Codex review skill. If the OpenAI API key is not set or the `codex` CLI is not installed, the skill immediately halts with a clear, actionable message explaining which prerequisite is missing and how to fix it.

**Why this priority**: All other functionality depends on this guard. Without it, later stories produce cryptic errors.

**Independent Test**: Can be tested by invoking the skill with each prerequisite missing in turn; delivers value as a standalone safety net.

**Acceptance Scenarios**:

1. **Given** the OpenAI API key is not configured, **When** the user invokes the review skill, **Then** the skill outputs a message identifying the missing API key and does not call Codex.
2. **Given** the `codex` CLI is not installed, **When** the user invokes the review skill, **Then** the skill outputs a message identifying the missing CLI tool and does not attempt a review.
3. **Given** both prerequisites are satisfied, **When** the user invokes the review skill, **Then** the skill proceeds to artifact collection without error.

---

### User Story 2 - On-Demand Artifact Review (Priority: P2)

A developer has used Claude Code to implement a feature. They invoke the review skill manually and receive a structured Codex review of all artifact types (git-changed files, user-specified paths, and speckit documents) — configurable per invocation — evaluated against code quality and security perspectives.

**Why this priority**: Core value delivery. The review result is the primary output of the feature.

**Independent Test**: Can be tested end-to-end by invoking the skill after a sample implementation and verifying that a non-empty review is returned.

**Acceptance Scenarios**:

1. **Given** prerequisites are met and there are reviewable artifacts, **When** the user invokes the review skill, **Then** a structured review is returned within a reasonable time and displayed in the conversation.
2. **Given** prerequisites are met but no reviewable artifacts exist, **When** the user invokes the review skill, **Then** the skill outputs an informative message rather than an empty or error response.

---

### User Story 3 - Workflow Integration (Priority: P3)

A developer completes an implementation phase. The review skill is on-demand by default (invoked via `/review`), but can be registered as an opt-in `after_implement` hook so the review runs automatically for teams that prefer it.

**Why this priority**: Convenience; reduces friction for teams adopting the skill regularly.

**Independent Test**: Can be tested by confirming the trigger fires (or does not fire) under the defined conditions independent of the review content.

**Acceptance Scenarios**:

1. **Given** the trigger condition is met, **When** the implementation phase completes, **Then** the review skill is invoked according to the configured trigger mode.

---

### Edge Cases

- What happens when Codex returns an empty or malformed response?
- What happens when the artifact set is very large (e.g., hundreds of files)?
- What happens when the OpenAI API key is set but invalid (authentication failure at call time)?
- What happens when the user interrupts the skill mid-execution?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Skill MUST verify that an OpenAI API key is configured before proceeding; if absent, it MUST output a clear error message naming the missing prerequisite.
- **FR-002**: Skill MUST verify that the `codex` CLI is installed before proceeding; if absent, it MUST output a clear error message naming the missing prerequisite.
- **FR-003**: Skill MUST support all of the following artifact modes, selectable per invocation: (a) git-changed files since last commit, (b) user-specified files or glob patterns, (c) speckit documents (spec.md, plan.md, tasks.md). When no mode is specified, git-changed files is the default.
- **FR-004**: Skill MUST apply two review perspectives when constructing the Codex prompt: (a) code quality (correctness, readability, maintainability) and (b) security (vulnerabilities, OWASP top 10). Both perspectives are applied by default; the user may select a subset per invocation.
- **FR-005**: Skill MUST present the Codex review result in the Claude Code conversation in a structured, readable format.
- **FR-006**: Skill MUST handle Codex API errors gracefully and surface actionable messages rather than raw error output.
- **FR-007**: Skill MUST be invocable on-demand via a named slash command. It MUST additionally support registration as an opt-in `after_implement` hook in `.specify/extensions.yml` for automatic post-implementation triggering.

### Key Entities

- **Artifact**: A file or document produced or modified by Claude Code that is subject to review. Supported types: git-changed files, user-specified files/globs, and speckit documents (spec.md, plan.md, tasks.md).
- **Review Result**: Structured feedback from Codex, including findings per artifact or per perspective, presented to the user.
- **Prerequisite Check**: The guard step that validates OpenAI API key presence and Codex CLI availability before any artifact collection or API calls occur.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When prerequisites are missing, the skill surfaces an actionable error message in under 1 second without making any external calls.
- **SC-002**: When prerequisites are met, the skill delivers a non-empty structured review for a standard implementation output in under 60 seconds.
- **SC-003**: 100% of invocations with missing prerequisites produce a user-actionable message (no silent failures or cryptic errors).
- **SC-004**: Review results are presented in a format that allows a developer to act on at least one finding without consulting external documentation.

## Assumptions

- The skill is implemented as a Claude Code skill file (`.claude/skills/`) consistent with existing skills in this project.
- "Codex" refers to the OpenAI `codex` CLI tool (`openai/codex` on npm/GitHub); the skill invokes it via the shell.
- The skill does not modify or auto-apply Codex suggestions; it is read-only and advisory.
- A single invocation defaults to reviewing git-changed files; other artifact modes (user-specified paths, speckit documents) are opt-in per invocation.
- The skill is English-language by default; locale handling is out of scope for v1.
