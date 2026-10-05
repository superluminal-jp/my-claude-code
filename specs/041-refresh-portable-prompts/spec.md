# Feature Specification: Refresh Portable System Prompts

**Feature Branch**: `041-refresh-portable-prompts`

**Created**: 2026-10-05

**Status**: Implemented

**Input**: User description: "Update the two portable system prompts at the repo root, `chatgpt-system-prompt.md` (ChatGPT: \"More about you\" + \"Custom instructions\", 1,500 chars each) and `claude-ai-system-prompt.md` (Claude.ai personal preferences / system instructions), so they (1) reflect the current content of `.claude/` (CLAUDE.md and rules: permissions, clarifier, pyramid-principle, thinking-lenses, model-routing; plus skills where universal) and (2) follow each service's current best practices and the latest model/service specifications (current models, field names/locations, character limits, memory/projects/tools features as of 2026-10). Verify service specs from official sources; do not invent limits or features. Keep each prompt within its service's limits and keep the files self-describing."

## Scope and Definitions

The feature rewrites two existing repository-root files so each is a faithful, service-appropriate projection of the user-level configuration in `.claude/` for a chat service that cannot load that directory.

- **Portable prompt**: one of the two root files, `chatgpt-system-prompt.md` or `claude-ai-system-prompt.md`, whose fenced blocks the owner pastes into a service's settings.
- **Source configuration**: `.claude/CLAUDE.md`, the five files in `.claude/rules/` (permissions, clarifier, pyramid-principle, thinking-lenses, model-routing), and the universal behaviors of the skills under `.claude/skills/`. It is the authority for *what* behavior the prompts convey.
- **Service specification**: the owning vendor's current official statement of where custom instructions are entered, field names, character limits, supported models, and memory, project, and tool features. It is the authority for *how* each prompt is shaped and sized.
- **Paste block**: a fenced block intended to be pasted verbatim into one service field.

Out of scope: changing `.claude/` itself, changing the installer, and adding prompts for other services. Behaviors that exist only inside Claude Code (slash commands, hooks, repository paths, named skills, subagent delegation) are not carried over unless the target service has a verified equivalent.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ChatGPT prompt matches the current configuration and service (Priority: P1)

As the repository owner, I paste the ChatGPT prompt into ChatGPT's personalization settings and get the same working principles as my Claude Code setup, shaped for ChatGPT as it exists now.

**Why this priority**: The ChatGPT file is the one most likely to be stale or wrong, because ChatGPT's personalization fields, limits, and memory behavior change independently of this repository; a paste that exceeds a limit or targets a renamed field fails outright.

**Independent Test**: Open the ChatGPT file next to the official ChatGPT custom-instructions documentation. Confirm each paste block's target field name and character count against the documentation, and confirm each principle in the source configuration is either present or listed as intentionally omitted with a reason.

**Acceptance Scenarios**:

1. **Given** each paste block, **When** its characters are counted, **Then** it is within the limit the official documentation states for its field.
2. **Given** the field names and menu path written in the file, **When** compared with the official documentation as of 2026-10, **Then** they match.
3. **Given** the source configuration's behaviors (authorization boundary, requirement clarification, conclusion-first structure, reasoning completeness), **When** the ChatGPT blocks are read, **Then** each behavior is expressed in language ChatGPT can follow without tools it lacks.
4. **Given** a statement about memory, projects, or models in the file, **When** checked against official sources, **Then** it is accurate for 2026-10 or has been removed.

---

### User Story 2 - Claude.ai prompt matches the current configuration and service (Priority: P1)

As the repository owner, I paste the Claude.ai prompt into Claude.ai's preferences and get my Claude Code working principles in the web and app experience.

**Why this priority**: Equal in value to Story 1; the Claude.ai file currently carries parts that presuppose agent tooling (subagent delegation, preflight habits) and omits rules added since it was last synced (the authorization boundary, reasoning completeness, model routing's applicable parts).

**Independent Test**: Compare the Claude.ai file with the source configuration and with Anthropic's current Claude.ai help documentation for personal preferences, memory, and projects; each divergence must be either resolved or recorded as an intentional omission.

**Acceptance Scenarios**:

1. **Given** the Claude.ai file, **When** compared with the source configuration, **Then** every universal behavior is present and no behavior that no longer exists in the source remains.
2. **Given** the placement instructions and any size guidance in the file, **When** checked against current official Claude.ai documentation, **Then** they are accurate.
3. **Given** statements in the file about memory, tools, or delegation, **When** checked against what Claude.ai supports as of 2026-10, **Then** each is supported by an official source or is removed.
4. **Given** the file's paste content, **When** pasted into the documented field, **Then** it is accepted without truncation.

---

### User Story 3 - A maintainer can see what was verified and what was left out (Priority: P2)

As a future maintainer, I can tell from the repository which service facts were verified, from which sources and on what date, and which source behaviors were deliberately not ported, so the next refresh starts from evidence instead of redoing the research.

**Why this priority**: The prompts are only trustworthy while their service facts are current; recording provenance makes staleness detectable. It adds no behavior for the chat user, so it follows the two prompt stories.

**Independent Test**: A reviewer who has not seen this work can list, from repository files only, each service fact the prompts rely on with its source and verification date, and each omitted source behavior with its reason.

**Acceptance Scenarios**:

1. **Given** the repository after the change, **When** a reviewer looks for the source and date of a character limit or field name, **Then** a durable artifact states them.
2. **Given** a source behavior that was not ported, **When** the reviewer looks for it, **Then** a durable artifact states why it was omitted.

---

### Edge Cases

- A service's official documentation is silent on a limit or feature the current files assume: the assumption is removed or marked unverified; no value is invented.
- Two official sources disagree, or the in-product behavior differs from the documentation: the discrepancy is recorded and the more conservative value is used.
- A source behavior has no equivalent in the service (for example subagent delegation, hooks, filesystem rules): it is omitted, not approximated with a misleading instruction.
- Compressing the source configuration into the ChatGPT limit forces a choice between behaviors: the higher-impact behavior (authorization and accuracy) is kept and the omission is recorded.
- A statement about "latest model" would age quickly: it is phrased so the prompt stays correct when the model changes, or it is dated.
- Repository documentation (`README.md`, `README.ja.md`) describes the two files: it is updated in the same change if the files' purpose or structure changed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each portable prompt MUST express every universal behavior of the source configuration that the target service can act on, and MUST NOT retain behavior that no longer exists in the source configuration.
- **FR-002**: Each paste block MUST fit within the character limit the target service's official documentation states for that field, and the file MUST state the measured length of each block.
- **FR-003**: Each file MUST name the correct settings location and field labels for its service as of 2026-10, per official documentation.
- **FR-004**: Statements about models, memory, projects, tools, or other service features MUST be supported by an official source consulted for this change, or be removed.
- **FR-005**: The ChatGPT file MUST keep its two-field split (profile context versus response behavior) unless the official documentation shows the fields changed, in which case the file MUST follow the documented structure.
- **FR-006**: The Claude.ai file MUST not instruct behavior that depends on agent tooling Claude.ai does not provide.
- **FR-007**: Prompt wording MUST follow each vendor's published guidance for writing instructions (clear, direct, positively phrased, no conflicting directives) and MUST keep framework names out of user-facing output instructions, consistent with the source configuration.
- **FR-008**: The change MUST include a durable record of each verified service fact (source, date) and each source behavior intentionally omitted (reason).
- **FR-009**: Repository documentation that describes the two files MUST be synchronized with their resulting purpose, structure, and limits.
- **FR-011**: Paste blocks MUST embed the working method, named standards, and frameworks (with author/year or standard number) of the `minto-pyramid`, `problem-definition`, `clarifier`, and `coder` skills, in dense notation written for the model rather than for human reading; the framework-naming restriction applies to the model's *output*, with the clarifier's two-name exception.
- **FR-012**: Skill steps that write repository files MUST be recorded under "Not ported" for services without a repository.
- **FR-010**: The change MUST NOT modify `.claude/`, the installer, or files outside the two prompts, their provenance record, and synchronized documentation.

### Key Entities

- **Portable prompt**: a root file with a header explaining placement, one or more paste blocks, and measured lengths.
- **Service fact**: a claim about a vendor service (field name, limit, feature) with its official source and verification date.
- **Omission record**: a source behavior not ported, with the reason it has no faithful equivalent or no room.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of paste blocks are at or under their documented limit, and 0 are truncated when pasted into the target field.
- **SC-002**: 100% of service facts stated in the two files trace to an official source with a verification date on or after 2026-10-01.
- **SC-003**: 100% of the source configuration's rules (five rule files plus the governing proposition) are accounted for in each prompt as either conveyed or recorded as omitted with a reason.
- **SC-004**: A reviewer can complete the audit of SC-001 through SC-003 in under 30 minutes using only repository files.
- **SC-005**: Zero statements remain in either file that an official source contradicts.

## Assumptions

- The owner pastes the files' contents manually; nothing is synchronized automatically.
- "Latest model and service specifications" means what the vendors' official documentation states on or near 2026-10-05; if a fact cannot be verified, it is dropped rather than guessed.
- The two prompts continue to be written primarily in English, with the instruction to mirror the user's language retained, as in the current files.
- The model-routing rule is Claude Code-specific in its mechanics (aliases, subagents); only its transferable principle (match effort and capability to the work's difficulty) is a candidate for porting, and only where the service exposes a corresponding choice.
- Where the ChatGPT limit forces compression, authorization/accuracy and clarification behaviors take priority over formatting preferences.
- Skills under `.claude/skills/` are mostly procedure-specific; only their universal behaviors (for example conclusion-first structure and clarification) are in scope, and these are already carried by the rules.
