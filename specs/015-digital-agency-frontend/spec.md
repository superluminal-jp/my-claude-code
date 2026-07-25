# Feature Specification: Digital Agency Frontend Skill

**Feature Branch**: `015-digital-agency-frontend`

**Created**: 2026-07-20

**Status**: Draft

**Input**: User description: "Add a reusable skill for web frontend development that applies the Digital Agency Design System and the Digital Agency dashboard guidebook. Use the default shared-skill approach, target web frontends only, specialize in the selected component-based frontend and utility-CSS stack, cover requirements through verification, and use live official sources plus bundled supporting resources."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build an accessible public-service frontend (Priority: P1)

A developer asks the assistant to create or modify a public-service web frontend. The assistant follows a repeatable workflow grounded in the Digital Agency Design System, from understanding users and tasks through implementation and verification, while preserving the existing project's architecture.

**Why this priority**: This is the core value of the skill: consistently turning the design system into usable, accessible frontend work rather than producing generic styling.

**Independent Test**: Invoke the skill for a representative public-service page and verify that the response identifies the user task, selects applicable design-system foundations and components, implements within the existing project, and reports accessibility and quality checks.

**Acceptance Scenarios**:

1. **Given** an existing supported web frontend, **When** a developer requests a new public-service page, **Then** the assistant inspects the project and the user task before selecting design-system patterns and implementing the change.
2. **Given** a design-system component or official code example applies, **When** the assistant implements the interface, **Then** it uses or adapts that official pattern and records any material deviation.
3. **Given** the requested interface lacks enough information to choose an accessible interaction, **When** the assistant reaches that decision, **Then** it obtains the missing requirement before implementation rather than inventing user intent.

---

### User Story 2 - Build a decision-oriented web dashboard (Priority: P2)

A developer asks the assistant to create a web dashboard. The assistant uses the dashboard guidebook to define the audience, intended decision or action, dashboard type, information hierarchy, chart selection, layout, color, and accessible alternatives before and during implementation.

**Why this priority**: Dashboard-specific information design is distinct from general component styling and is the reason the second Digital Agency source is included.

**Independent Test**: Invoke the skill for a representative dashboard request and verify that it distinguishes presentation from exploration, connects every prominent visualization to a user question, and supplies text or tabular alternatives for essential information.

**Acceptance Scenarios**:

1. **Given** a dashboard request, **When** the intended audience, decision, or action is not yet explicit, **Then** the assistant resolves those requirements before selecting charts or layout.
2. **Given** a presentation-oriented dashboard, **When** the assistant designs the view, **Then** it prioritizes rapid understanding of status, comparison, and required action over exploratory controls.
3. **Given** a chart communicates essential information, **When** the dashboard is implemented, **Then** the same essential meaning is available without relying only on color or visual chart inspection.
4. **Given** a request for a Power BI artifact, **When** this skill is active, **Then** it states that artifact generation is outside the skill's web-frontend scope and limits its help to transferable design guidance unless another capability is explicitly selected.

---

### User Story 3 - Use the same skill across supported coding agents (Priority: P3)

A maintainer installs this repository's user-level configuration and can discover the same authored skill from both supported coding-agent environments without duplicated skill content or broken links.

**Why this priority**: Cross-agent reuse is an existing repository contract and prevents the new frontend guidance from drifting between tools.

**Independent Test**: Run the repository's installation and sync validations in an isolated fixture and verify that both environments resolve the new skill to the same installed source and that user documentation lists it.

**Acceptance Scenarios**:

1. **Given** the repository checkout before user-level installation, **When** skill discovery is inspected, **Then** the Claude-side skill is present and the Codex-side entry resolves to the same authored directory.
2. **Given** a completed user-level installation, **When** each supported agent scans its global skill location, **Then** it can discover the new skill with the same instructions and bundled resources.
3. **Given** the installer is run repeatedly, **When** synchronization completes, **Then** no duplicate or broken skill entry is created.

### Edge Cases

- The official sources are temporarily unavailable; the skill uses its concise bundled references, identifies their recorded source version or retrieval date, and clearly marks live verification as incomplete.
- The official sources change after the bundled references were written; the live official source wins, and the assistant reports the mismatch rather than silently following stale local guidance.
- The existing frontend does not use the supported stack; the assistant states the scope mismatch and does not introduce a new framework solely to use the skill.
- The project already has a component library or brand system that conflicts with the Digital Agency Design System; the assistant surfaces the conflict and seeks a project-level decision before replacing public interfaces.
- A copied official example is not accessible in the product's full page context; the assistant treats examples as starting points and verifies the integrated result rather than assuming compliance.
- A dashboard uses color, hover, or pointer interaction as the only carrier of meaning; the assistant adds persistent labels, keyboard access, and non-visual alternatives.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The configuration MUST provide one reusable `digital-agency-frontend` skill as the authored source for both supported coding-agent environments.
- **FR-002**: The skill metadata MUST identify concrete triggering requests, including Digital Agency Design System work, Japanese public-service frontend work, accessible component implementation, and web dashboard design or development.
- **FR-003**: The skill MUST cover the complete workflow from intent and constraint discovery through information design, implementation, testing, accessibility verification, and close-out documentation.
- **FR-004**: The skill MUST compose with the repository's existing clarification and coding workflows rather than duplicate their generic requirements, test-driven development, security, or documentation rules.
- **FR-005**: Before implementation, the skill MUST identify the intended users, primary task, use context, content or data, constraints, and verifiable success condition; material gaps MUST be resolved through the existing clarification workflow.
- **FR-006**: The skill MUST treat current official Digital Agency sources as authoritative and MUST provide concise bundled references that record source URLs, source version or retrieval date, scope, and fallback guidance.
- **FR-007**: When live official sources and bundled references disagree, the skill MUST prefer the live official source and disclose the detected drift.
- **FR-008**: For general frontends, the skill MUST guide selection and adaptation of applicable foundations, design tokens, components, content patterns, and official code examples, and MUST require a reason for material deviations.
- **FR-009**: For dashboards, the skill MUST distinguish presentation-oriented and exploration-oriented use, define the intended decision or action, and guide information hierarchy, layout, chart selection, color, labeling, and interaction accordingly.
- **FR-010**: The skill MUST limit artifact creation to web frontends and MUST explicitly exclude generation or editing of Power BI template files.
- **FR-011**: The skill MUST require semantic structure, keyboard operability, visible focus, reflow, sufficient contrast, non-color cues, meaningful text alternatives, and accessible representations of essential chart data.
- **FR-012**: The skill MUST use JIS X 8341-3:2016 level AA and WCAG 2.2 level AA as verification baselines, while recognizing that use of a component or example alone does not prove page-level conformance.
- **FR-013**: The skill MUST preserve the active project's established routing, state management, data access, component, testing, linting, formatting, and build conventions unless the user approves a scoped change.
- **FR-014**: The bundled resources MUST contain only reusable workflow support needed by the skill; they MUST NOT wholesale-vendor the official documentation, PDF guidebook, or Power BI templates.
- **FR-015**: The skill MUST include the source and modification attribution guidance needed when official Digital Agency content is reused or adapted, while distinguishing the licensing treatment of documentation, design data, and code examples.
- **FR-016**: Repository-level discovery, installer, drift validation, routing documentation, and English and Japanese user documentation MUST include the new skill in the same change.
- **FR-017**: Automated contract tests MUST fail when the skill, required bundled references, cross-agent entry, installer registration, routing metadata, or user documentation is missing or inconsistent.
- **FR-018**: The skill package MUST pass the standard structural validation for skill name, required metadata, folder shape, and interface metadata.

### Key Entities

- **Frontend Skill**: The reusable procedure that routes applicable requests, coordinates existing workflows, and defines the design-system and dashboard-specific quality gates.
- **Bundled Reference**: A concise, source-attributed local resource loaded only when its topic is relevant, with an official URL and freshness metadata.
- **Source Record**: The identity, version or retrieval date, usage scope, and licensing or attribution note for an official Digital Agency source.
- **Cross-Agent Entry**: A discovery link or installer registration that exposes the single authored skill to another supported coding agent without copying its content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five representative request classes—public-service page creation, component implementation, accessibility remediation, presentation dashboard creation, and dashboard review—are routed to the skill and produce the corresponding workflow without unrelated guidance.
- **SC-002**: Every completed dashboard workflow records an audience, intended decision or action, dashboard type, and accessible alternative for each essential visualization before the work is reported complete.
- **SC-003**: Every completed frontend workflow reports results for all applicable accessibility checks in the skill, with zero known level-A or level-AA failures left undisclosed.
- **SC-004**: One authored skill directory is discoverable in both supported agent environments, with zero copied skill bodies and zero broken discovery links before and after repeated installation.
- **SC-005**: All official-source records include an official URL plus a version or retrieval date, and 100% of reused or adapted content has the required attribution guidance available to the implementing agent.
- **SC-006**: The complete repository validation suite and the skill structural validator pass with zero failures after implementation.

## Assumptions

- This repository remains a user-level configuration distributed to all projects by `install.sh`.
- The new skill is authored under `.claude/skills/` and exposed to Codex through the repository's existing single-source symlink model.
- The supported implementation stack is recorded in the implementation plan rather than repeated as a business requirement in this specification.
- Live official sources remain the source of truth; bundled references are concise operational aids and offline fallbacks, not mirrors.
- The existing `clarifier` and `coder` skills remain responsible for generic requirements elicitation, test-driven implementation, security, and documentation synchronization.
- Creating a dedicated Claude Code or Codex subagent is outside this feature; a shared skill is sufficient for the confirmed workflow.
- No architecturally significant one-way-door decision is introduced; the feature extends the repository's existing skill and synchronization patterns.
