# Feature Specification: Spec Kit Skills Sync with Upstream

**Feature Branch**: `002-sync-speckit-skills`
**Created**: 2026-05-08
**Status**: Draft
**Input**: User description: "https://github.com/github/spec-kit 最新の実装を参照してこのプロジェクト内でのスキルを一致させる。speckitについて言及しているドキュメントやrules,skills,hooksも公式の実態に合わせる"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Constitution Governance During Implementation (Priority: P1)

As a developer using `/speckit-implement` to execute a task plan, I want the implementation workflow to automatically load the project constitution so that governance constraints are enforced throughout implementation without manual intervention.

**Why this priority**: Constitution loading is a newly released spec-kit behavior (v0.8.7). Without it, implementations may violate project governance principles silently. This is the highest-value behavioral gap between the upstream and local skills.

**Independent Test**: Run `/speckit-implement` on a project that has `.specify/memory/constitution.md`. Verify the skill reads that file as part of context loading before executing tasks.

**Acceptance Scenarios**:

1. **Given** a spec-kit project with `.specify/memory/constitution.md` present, **When** `/speckit-implement` is invoked, **Then** the skill reads the constitution file as part of the implementation context
2. **Given** a spec-kit project without `.specify/memory/constitution.md`, **When** `/speckit-implement` is invoked, **Then** the skill proceeds normally without error
3. **Given** a constitution with a governance constraint, **When** implementation tasks conflict with that constraint, **Then** the conflict is surfaced to the user before proceeding

---

### User Story 2 - Consistent Speckit Skill Behavior with Upstream (Priority: P2)

As a maintainer of this project, I want all speckit skills to behave identically to the latest upstream spec-kit workflow, so that users following the official spec-kit documentation get the same experience from the Claude Code integration.

**Why this priority**: Behavioral divergence between the Claude Code skills and the upstream grows over time if not actively managed. Each new spec-kit release may introduce workflow changes that must be reflected here.

**Independent Test**: Compare the Outline/Goal/Phases sections of each local SKILL.md against the corresponding upstream `templates/commands/*.md`. All substantive workflow steps must match (modulo Claude Code-specific adaptations).

**Acceptance Scenarios**:

1. **Given** a new spec-kit release with workflow changes, **When** a comparison is performed between local skills and the upstream, **Then** all substantive workflow differences are identified
2. **Given** identified workflow gaps, **When** the local skills are updated, **Then** the updated skills produce the same outcomes as the upstream templates
3. **Given** Claude Code-specific adaptations (slash command format, script path resolution), **When** skills are synced, **Then** those adaptations are preserved and not overwritten

---

### User Story 3 - Correct Path References in Rules and Hooks (Priority: P3)

As a developer using any speckit command, I want all path references in rules, hooks, and skill files to resolve correctly in the Claude Code context, so that commands succeed without manual path correction.

**Why this priority**: Incorrect paths cause silent failures. The Claude Code context uses `.specify/` as a base directory for templates and memory, which differs from how the spec-kit CLI resolves paths via template variables.

**Independent Test**: Invoke each speckit skill and verify no "file not found" errors occur for path references like `.specify/memory/constitution.md` and `.specify/templates/spec-template.md`.

**Acceptance Scenarios**:

1. **Given** a spec-kit project initialized with `specify init`, **When** any speckit skill references a file path, **Then** the path resolves correctly relative to the project root
2. **Given** the upstream uses template variables like `{SCRIPT}` or `__SPECKIT_COMMAND_PLAN__`, **When** local skills are used in Claude Code, **Then** those variables are replaced with the correct Claude Code equivalents

---

### Edge Cases

- What happens when `.specify/` has not been initialized (no `specify init` run yet)?
- How should hooks behave when already on a feature branch when `/speckit-specify` is invoked?
- What if the upstream spec-kit updates a template variable resolution that differs from the Claude Code adaptation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `speckit-implement` skill MUST load `.specify/memory/constitution.md` when it exists, as part of step 3 context loading, before executing any implementation tasks
- **FR-002**: All speckit skills MUST implement the same workflow steps and decision logic as their corresponding upstream `templates/commands/*.md` files
- **FR-003**: Claude Code-specific adaptations MUST be preserved when syncing: slash command format (`/speckit-*` not dot notation), script paths resolved to `.specify/scripts/`, template paths resolved to `.specify/templates/`
- **FR-004**: Path references to the project constitution MUST use `.specify/memory/constitution.md` consistently across all skills (speckit-implement, speckit-plan, speckit-analyze)
- **FR-005**: The hook command conversion instruction MUST remain in skill files to correctly map spec-kit dot-notation commands (`speckit.git.commit`) to Claude Code slash commands (`/speckit-git-commit`)
- **FR-006**: Skill frontmatter MUST remain in Claude Code skill format (with `name`, `argument-hint`, `user-invocable` fields), NOT the spec-kit CLI format (`handoffs`, `scripts` fields), as these are incompatible systems

### Key Entities

- **Speckit Skill**: A SKILL.md file under `.claude/skills/speckit-*/` that implements a spec-kit workflow command for Claude Code
- **Upstream Template**: A markdown file under `templates/commands/` in the spec-kit GitHub repository that defines the canonical workflow
- **Claude Code Adaptation**: A deliberate change from the upstream template required for Claude Code compatibility (e.g., slash command format, path resolution)
- **Spec-kit Version**: The version of the upstream spec-kit CLI whose templates the local skills should match

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of speckit skills reflect the same workflow steps as their corresponding upstream templates for the current spec-kit version
- **SC-002**: `/speckit-implement` successfully loads `.specify/memory/constitution.md` when the file exists, verified by reading the file contents during implementation
- **SC-003**: Zero path-not-found errors occur when running any speckit skill on a correctly initialized spec-kit project
- **SC-004**: All Claude Code-specific adaptations remain intact after any sync operation, verifiable by comparing the adaptation list before and after

## Assumptions

- Spec-kit version being aligned with is 0.8.7 (latest as of 2026-05-08)
- The project uses Claude Code's slash command format (`/speckit-*`) and the hook conversion instruction is required for this to work
- Constitution is stored at `.specify/memory/constitution.md` after `specify init` (not at `/memory/constitution.md` as some upstream templates suggest—this appears to be a CLI template variable)
- Claude Code skill frontmatter format is intentionally different from the spec-kit CLI native format; `handoffs` and `scripts` fields from upstream are not applicable to Claude Code skills
- The speckit-expand-update.sh hook auto-refreshes spec-kit templates on `/speckit-specify` invocation, but skill SKILL.md files must be manually maintained
