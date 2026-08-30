# Feature Specification: Independent Configuration Pyramid

**Feature Branch**: `036-rule-layer-independence`

**Created**: 2026-08-30

**Revised**: 2026-08-30

**Status**: Draft

**Input**: Build a logical pyramid with `CLAUDE.md` as its apex, apply improvements from the apex downward, validate every lower document against its parent and siblings, remove references to lower configuration documents, and make each configuration file independently usable.

## Scope and Definitions

This feature governs the authored Claude Code configuration in three mechanisms:

1. the always-loaded apex instruction;
2. the always-loaded rule files;
3. the on-demand operational and domain skills maintained by this repository.

The hierarchy is semantic, not a chain of file citations. The apex states the complete governing proposition. Rules independently express universal quality conditions supporting that proposition. Skills independently describe conditional procedures and domain overlays. A compound request may select more than one skill; this intentional intersection is not a failure of MECE because operation and domain are separate classification axes.

A **configuration reference** is a name or path that delegates meaning or routing to another configuration node, including an apex-to-rule, rule-to-skill, skill-to-rule, or sibling-skill reference. Such references are prohibited in the scoped authored content. The prohibition does not include:

- a skill's own `references/`, scripts, templates, or other package-owned resources;
- external primary-source citations;
- links in shipped artifacts to the public contract or decision record they explain;
- Spec Kit process-artifact links within the same feature directory.

Bundled third-party archives are not rewritten. Utility and Spec Kit skills remain out of the editorial taxonomy, but all `SKILL.md` files are scanned for upward configuration-path dependencies so the independence claim is not based on a hand-picked sample.

The editorial skill scope is `clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, and `digital-agency-frontend`, plus the Git-workflow and cloud-platform-research skills created when conditional content leaves the rule layer. Document work is partitioned by source maturity and requested outcome: collaborative construction from incomplete material, structural diagnosis of existing material, and final transformation of an existing substantive draft.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The apex governs without delegating (Priority: P1)

As a maintainer, I want `CLAUDE.md` to state one governing proposition and a complete set of first-level conditions without naming lower files, skills, commands, or servers, so its meaning survives any lower-level reorganization.

**Why this priority**: Every other classification must be derived from the apex. Editing children before fixing the apex would optimize against an unstable parent.

**Independent Test**: Read `CLAUDE.md` alone and identify the governing proposition plus the three lifecycle branches—define the right work, execute under control, and hand off a verifiable result—then run the structural scan and obtain zero lower-configuration references.

**Acceptance Scenarios**:

1. **Given** the current file delegates clarification, reasoning, output structure, Spec Kit, documentation, skills, and MCP behavior by name, **When** the apex is rewritten, **Then** no lower configuration path, skill name, slash command, or server registry is required to understand or apply it.
2. **Given** a compound request matches multiple conditional capabilities, **When** the apex is applied, **Then** every independently matching capability is selected and ordered by dependency without a central named routing table.
3. **Given** the apex's first-level branches, **When** they are reviewed horizontally, **Then** they use one lifecycle classification—definition, execution, handoff—without overlap or an uncovered lifecycle phase.

---

### User Story 2 - Universal rules are independent and MECE (Priority: P1)

As a maintainer, I want each always-loaded rule to own one universal quality concern, support exactly one apex branch, and neither cite nor duplicate another rule or skill, so any rule can be revised or removed without creating a dangling dependency.

**Why this priority**: Rules consume context every session. Mixing universal constraints with conditional workflows and live registries creates both logical inconsistency and avoidable context cost.

**Independent Test**: Review each surviving rule alone, map it to exactly one apex branch, and confirm that the set comprises requirements certainty, reasoning completeness, authorization and safety, external expression, and documentation integrity. Run pairwise reference and semantic-ownership checks with zero violations.

**Acceptance Scenarios**:

1. **Given** the existing rules mix quality constraints, Git workflow, skill routing, and an MCP registry, **When** the rule layer is normalized, **Then** only universal quality constraints remain always loaded.
2. **Given** clarification and permission both mention risk, **When** their boundaries are revised, **Then** clarification owns uncertainty that changes the outcome or blast radius, while permission owns authorization and safe execution.
3. **Given** reasoning, output structure, and documentation currently share MECE/pyramid concepts, **When** their boundaries are revised, **Then** internal inference, external presentation, and documentation truth/synchronization are separate concerns.
4. **Given** conditional Git and cloud-tool guidance remains useful, **When** it leaves the rule layer, **Then** its behavior is preserved in independently discoverable on-demand skills rather than silently discarded.

---

### User Story 3 - Skills self-identify and compose without lateral routing (Priority: P2)

As a maintainer, I want each authored skill description and body to state its own triggers, exclusions, procedure, and compound applicability without referring to rules or sibling skills, so selection follows metadata and each package remains portable.

**Why this priority**: Skills are the concrete procedures below the universal constraints. Their independence is only meaningful after the parent rule boundaries are stable.

**Independent Test**: Scan all skill entry points for rule/config paths and pairwise scan the scoped authored skill packages for sibling names. Confirm zero prohibited references, every skill description exposes its selection boundary, and every package-owned link resolves.

**Acceptance Scenarios**:

1. **Given** requirements, implementation, decision recording, and document work are lifecycle operations, **When** skills are classified, **Then** siblings within each operation group use one selection principle and their exclusions are explicit.
2. **Given** Scrum and Digital Agency frontend guidance are domain overlays, **When** a request also needs an operation skill, **Then** both match independently and neither package names the other.
3. **Given** a skill owns references or scripts, **When** configuration references are removed, **Then** downward links to those owned resources remain valid and portable.
4. **Given** task-specific Git and cloud-platform research guidance was formerly always loaded, **When** it becomes on-demand, **Then** each new skill is self-contained and discoverable from its own description.

---

### User Story 4 - The design stays verifiable and durable (Priority: P1)

As a future maintainer, I want executable structural contracts, a clear design guide, and a decision record that distinguish logical hierarchy from file references, so later additions cannot silently recreate central routing tables or cross-layer dependencies.

**Why this priority**: A prose-only convention had already drifted into a contradictory three-level model. Durable checks and rationale are required to prevent recurrence.

**Independent Test**: Run the dedicated configuration-pyramid suite and all existing repository suites; inspect the design guide and ADR independently; verify no shipped documentation claims that deleted rule files are runtime sources.

**Acceptance Scenarios**:

1. **Given** a future apex, rule, or authored skill introduces a prohibited configuration reference, **When** the structural suite runs, **Then** it fails with the offending file and reference.
2. **Given** a rule or skill is added, **When** maintainers consult the design guide, **Then** they can determine whether it is a universal constraint, lifecycle operation, domain overlay, or package-owned resource without reading another configuration file.
3. **Given** old documentation and tests require the central routing file, **When** implementation is complete, **Then** those claims are replaced with metadata-driven multi-match behavior and the full suite passes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `CLAUDE.md` MUST state one governing proposition whose direct support is partitioned into definition, execution, and handoff conditions.
- **FR-002**: `CLAUDE.md` MUST NOT name or path-reference a rule, skill, settings file, MCP registry, server, or slash command.
- **FR-003**: `CLAUDE.md` MUST state a generic compound-capability algorithm: evaluate every available description, apply every independent match, order prerequisites before execution and verification/recording after it, and prefer a specific operation or domain match over generic ambiguity handling.
- **FR-004**: The rule layer MUST contain only universal quality constraints; task-specific workflows and environment-dependent capability registries MUST NOT remain unconditional rules.
- **FR-005**: Each surviving rule MUST own one concern and support exactly one apex branch: requirements certainty, internal reasoning, authorization and safety, external expression, or documentation integrity.
- **FR-006**: No rule MUST name or path-reference another rule, a skill, a settings file, an MCP registry, or a slash command.
- **FR-007**: The Git workflow and cloud-platform documentation behavior removed from unconditional rules MUST be preserved as self-contained on-demand skills.
- **FR-008**: The central named skill-routing rule MUST be removed; capability selection MUST derive from each skill's metadata plus the generic apex algorithm.
- **FR-009**: Each scoped authored skill MUST state its positive trigger, exclusion boundary, primary operation or domain, and behavior when another capability independently matches in its standard `description` metadata; unsupported duplicate trigger metadata MUST NOT be the only source of selection behavior.
- **FR-010**: A scoped authored skill package MUST NOT name a sibling authored skill or depend on an apex/rule/config path. It MAY reference only its own package resources and external evidence.
- **FR-011**: All owned resource links in edited skill packages MUST resolve without assuming a hard-coded repository installation path.
- **FR-012**: Existing behavioral obligations MUST be preserved at the proper abstraction level, including material-gap clarification, safe authorization boundaries, test-first implementation where automatable, factual contract documentation, architecture-decision recording, document operations, Scrum grounding, DADS sourcing/accessibility, Git hygiene, and provider documentation lookup.
- **FR-013**: `docs/claude-config-design.md`, root README files, affected skill documentation, and relevant tests MUST describe the final independent architecture and MUST NOT identify a deleted rule as a runtime source.
- **FR-014**: Proposed ADR-0015 MUST record the selected semantic hierarchy, the separation of universal rules from conditional skills, the internal-reference boundary, the rejected central-router and named-parent alternatives, and consequences without changing its status to Accepted.
- **FR-015**: A dedicated offline structural test MUST enforce prohibited reference patterns, expected rule topology, skill package boundaries, portable owned-resource links, and representative compound-routing metadata contracts.
- **FR-016**: Implementation MUST proceed top-down. Before editing each level, its tests MUST fail against the current state and its nodes MUST be checked against the finalized parent and same-level siblings.
- **FR-017**: The total bytes of always-loaded `CLAUDE.md` and rules after implementation MUST be lower than the pre-implementation baseline.
- **FR-018**: Bundled third-party archives MUST remain byte-for-byte untouched, and utility/Spec Kit skills MUST retain their workflow behavior.

### Key Entities

- **Apex**: The single always-loaded governing proposition and its first-level lifecycle partition. It has semantic children but contains no named link to them.
- **Apex branch**: One of definition, execution, or handoff. Siblings are exhaustive lifecycle stages and use the same ordering principle.
- **Universal rule**: An always-applicable quality constraint that supports exactly one apex branch and is independently interpretable.
- **Lifecycle-operation skill**: An on-demand procedure selected by the requested action or artifact state, such as requirements, implementation, decision recording, or document work.
- **Domain-overlay skill**: On-demand constraints selected by the subject domain; it composes with any independently matching lifecycle operation.
- **Owned resource**: A file below a skill package that its entry point may load progressively. It is encapsulated implementation detail, not a sibling configuration node.
- **Configuration reference**: A named or path-based dependency between independent configuration nodes. It is prohibited regardless of direction.
- **Semantic support edge**: A parent-child relationship established by consistent meaning and abstraction, not by a file citation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Structural scans report zero lower-node, settings, server-registry, or slash-command references in `CLAUDE.md`.
- **SC-002**: Structural scans report zero rule/config/skill-routing references in every surviving rule and zero sibling-rule filename references pairwise.
- **SC-003**: A relation table maps every surviving rule to exactly one of the three apex branches and records no horizontal overlap or uncovered universal concern.
- **SC-004**: Structural scans report zero rule/config paths in all skill entry points and zero sibling authored-skill references in the scoped packages, excluding verbatim third-party archives.
- **SC-005**: Every relative link in each edited authored skill resolves inside that skill package, and no edited package hard-codes `.claude/skills/<name>` as its own location.
- **SC-006**: Offline routing fixtures verify at least these cases: code-only; bare document creation; code plus substantive document update; diagnosis plus rewrite; DADS implementation; ambiguous DADS requirements; Scrum artifact; generic project-management status/Gantt work.
- **SC-007**: The final byte count of `CLAUDE.md` plus `.claude/rules/*.md` is lower than the pre-implementation count captured by the structural test.
- **SC-008**: The dedicated structural suite, every existing `tests/run-*.sh` suite, relevant syntax/frontmatter checks, and `git diff --check` pass.
- **SC-009**: `docs/claude-config-design.md` and ADR-0015 independently explain the architecture, allowed owned-resource boundary, two skill-selection axes, rejected alternatives, and migration consequences.
- **SC-010**: No file in the changed set introduces a new reference to a deleted routing, MCP, or Git rule, and bundled third-party archives have no diff.

## Assumptions

- “下位文書への参照排除” means removing named dependencies among independent configuration nodes, not banning encapsulated resources or evidence links; banning those would make large skills non-self-contained by forcing all content into one file.
- The lifecycle stages define the apex's horizontal MECE partition. Lifecycle-operation skills and domain overlays form two independent selection axes, so an operation and an overlay may intentionally intersect.
- ADR-0015 is still Proposed and may be revised in place before acceptance.
- No commit, push, pull request, or ADR acceptance is authorized by this feature request.

## Out of Scope

- Rewriting verbatim third-party archives or changing their source material.
- Altering the public behavior of Apple application utility skills or Spec Kit workflows beyond independence-compatible metadata/path verification.
- Proving semantic MECE solely by grep; automated checks are supplemented by a documented relation table and manual review.
- Accepting ADR-0015 or publishing changes remotely.
