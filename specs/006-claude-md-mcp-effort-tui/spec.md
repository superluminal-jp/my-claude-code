# Feature Specification: CLAUDE.md Configuration Improvements

**Feature Branch**: `006-claude-md-mcp-effort-tui`  
**Created**: 2026-05-09  
**Status**: Draft  
**Input**: User description: "AWSやGCPに関するやりとりについては必ずMCPを使用するように改善。デフォルトのeffortをhighに変更。デフォルトのtuiをfullscreenに変更"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - MCP Enforcement for AWS/GCP (Priority: P1)

When a user asks about AWS or GCP topics, Claude must always route through the designated MCP servers rather than falling back to general web search or cached knowledge.

**Why this priority**: Without this enforcement, Claude may answer AWS/GCP questions from stale training data instead of authoritative, up-to-date first-party documentation. This is the highest-impact correctness guarantee among the three changes.

**Independent Test**: Start a new conversation, ask an AWS-specific question (e.g., "What is the latest Lambda runtime support?"), and confirm Claude invokes an MCP tool call rather than answering directly from training knowledge.

**Acceptance Scenarios**:

1. **Given** a user asks a question directly about AWS services, features, or documentation, **When** Claude responds, **Then** Claude invokes one of the AWS MCP servers (`aws-knowledge` or `aws-documentation`) before answering.
2. **Given** a user asks a question directly about GCP services, features, or documentation, **When** Claude responds, **Then** Claude invokes the `google-developer-knowledge` MCP server before answering.
3. **Given** a question that mentions AWS/GCP incidentally but is not about AWS/GCP (e.g., "I'm deployed on AWS but my question is about Python loops"), **When** Claude responds, **Then** Claude is not required to call an MCP server and may answer from training knowledge.

---

### User Story 2 - Default Effort Set to High (Priority: P2)

Claude Code's effort level defaults to `high` so that every session starts with maximum reasoning depth without requiring the user to set it manually.

**Why this priority**: The current default (assumed `normal`) may produce shallower analysis on complex tasks. Setting `high` as default ensures users always get the most thorough responses, with the option to lower it when speed matters.

**Independent Test**: Open a new Claude Code session without any explicit effort flag and confirm that the effective effort level is `high`.

**Acceptance Scenarios**:

1. **Given** no explicit effort flag is passed at session start, **When** Claude Code initialises, **Then** the effort level is `high`.
2. **Given** a user explicitly passes `--effort medium`, **When** Claude Code initialises, **Then** the effort level is `medium` (explicit flag overrides the default).

---

### User Story 3 - Default TUI Set to Fullscreen (Priority: P3)

Claude Code's terminal UI defaults to `fullscreen` mode so the interface expands to the full terminal window on every launch.

**Why this priority**: Fullscreen mode improves readability and context visibility. Defaulting to it benefits the majority of interactive use cases; users who prefer a compact view can still override it.

**Independent Test**: Launch Claude Code interactively without any TUI flag and confirm the terminal UI renders in fullscreen mode.

**Acceptance Scenarios**:

1. **Given** no explicit TUI flag is passed at launch, **When** Claude Code starts an interactive session, **Then** the TUI renders in fullscreen mode.
2. **Given** a user explicitly passes a non-fullscreen TUI option, **When** Claude Code starts, **Then** the specified mode is used (explicit flag overrides the default).

---

### Edge Cases

- What happens when all MCP servers are unavailable (network outage)? Claude MUST warn the user that MCP is unavailable, then proceed to answer from training knowledge. Silent fallback without warning is not permitted.
- What if a question spans both AWS and non-AWS topics? The MCP call should still be made for the AWS portion.
- What if `effort` or `tui` are already explicitly set in a project-level `settings.json`? Project-level settings override user-level defaults; the new defaults apply only where no override exists.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The configuration MUST instruct Claude to invoke an AWS MCP server (`aws-knowledge` or `aws-documentation`) when the question directly concerns AWS services, features, or documentation (incidental AWS mentions in otherwise generic questions do not trigger this rule).
- **FR-002**: The configuration MUST instruct Claude to invoke the `google-developer-knowledge` MCP server when the question directly concerns GCP services, features, or documentation (incidental GCP mentions in otherwise generic questions do not trigger this rule).
- **FR-003**: The MCP-enforcement rule MUST be expressed in a way that applies at the session level (not per-turn), so Claude does not need to re-evaluate it each time.
- **FR-004**: The default `effort` setting MUST be `high` in the project-scope `.claude/settings.json`, applied via `install.sh`.
- **FR-005**: The default `tui` setting MUST be `fullscreen` in the project-scope `.claude/settings.json`, applied via `install.sh`.
- **FR-006**: Existing explicit overrides (project `settings.json`, CLI flags) MUST continue to take precedence over the new defaults.
- **FR-007**: The MCP rule MUST reference the server names already defined in `rules/mcp.md` to stay consistent with the existing catalog.
- **FR-008**: When a required MCP server is unreachable, Claude MUST notify the user before answering from training knowledge; silent fallback is not permitted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of AWS/GCP questions in a new session result in at least one MCP tool call before the answer is delivered.
- **SC-002**: A Claude Code session in this project, started without explicit flags, reports effective effort level `high`.
- **SC-003**: An interactive Claude Code session in this project, started without explicit flags, renders in fullscreen TUI mode.
- **SC-004**: No regression: non-AWS/GCP questions, project-level overrides, and explicit CLI flags behave identically to before the change.

## Clarifications

### Session 2026-05-09

- Q: What constitutes an "AWS/GCP-related exchange" for MCP enforcement? → A: Only when the question directly concerns AWS/GCP services, features, or documentation (not incidental mentions in otherwise generic questions).
- Q: When an AWS/GCP MCP server is unreachable, what should Claude do? → A: Warn the user that MCP is unavailable, then answer from training knowledge.
- Q: Where should the effort=high and tui=fullscreen defaults be set? → A: Project-scope `.claude/settings.json`, applied via `install.sh`.

## Assumptions

- The `effort` and `tui` defaults are set in the project-scope `.claude/settings.json` and distributed via `install.sh`; the exact JSON key names will be confirmed during implementation via Claude Code documentation.
- The `rules/mcp.md` catalog already lists the correct server names; no new MCP server registration is needed for this feature.
- The enforcement rule for MCP is expressed as a text instruction in CLAUDE.md (and/or `rules/mcp.md`), not as a code-level hook, since Claude reads and follows CLAUDE.md directives at session load time.
- Azure-related questions are already covered by the existing MCP rule in `rules/mcp.md`; this feature adds explicit AWS and GCP enforcement at the same level.
