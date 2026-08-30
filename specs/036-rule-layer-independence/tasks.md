# Tasks: Independent Configuration Pyramid

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md)

**Tests**: Strict top-down red → green. A lower layer starts only after its parent passes its structural contract and relation review.

## Phase 1: Setup and Requirement Gates

**Purpose**: Preserve the worktree, establish the revised requirements, and capture the legacy baseline.

- [X] T001 Confirm branch, user-owned changes, feature directory, and 20,126-byte unconditional baseline using `specs/036-rule-layer-independence/quickstart.md` §1
- [X] T002 Validate every item in `specs/036-rule-layer-independence/checklists/requirements.md` and `specs/036-rule-layer-independence/checklists/logic-architecture.md`
- [X] T003 Record the final apex/rule/skill ownership relation in `specs/036-rule-layer-independence/data-model.md` and confirm each sibling group uses one classification principle

---

## Phase 2: Foundational Structural Contract

**Purpose**: Make the legacy architecture fail before editing runtime configuration.

**⚠️ CRITICAL**: No runtime configuration edit begins until T005 fails for the expected apex/rule/routing violations.

- [X] T004 Add offline assertions for apex references, exact rule topology, pairwise rule references, skill config paths, authored-package sibling references, portable owned links, legacy-path absence, byte budget, and routing fixtures in `tests/run-config-pyramid.sh`
- [X] T005 Run `tests/run-config-pyramid.sh` and record a RED result caused by the legacy apex, eight-rule topology, central router, and cross-config dependencies

**Checkpoint**: The permanent test detects the architecture the feature is replacing.

---

## Phase 3: Pre-implementation Spec Kit Analysis

**Purpose**: Check cross-artifact consistency after tasks exist and before runtime implementation starts.

- [X] T006 Run the read-only Spec Kit consistency analysis across `spec.md`, `plan.md`, `tasks.md`, and both requirement checklists; classify critical/high/medium findings
- [X] T007 Remediate every critical or high finding in the owning feature artifact and rerun the analysis

**Checkpoint**: Specification, plan, tasks, and checklists agree on scope, ordering, requirements, and authority.

---

## Phase 4: User Story 1 — The apex governs without delegating (Priority: P1) 🎯 MVP

**Goal**: Establish the one governing proposition and three lifecycle branches before changing any child.

**Independent Test**: The apex-only portion of `tests/run-config-pyramid.sh` passes; the rule/skill portions still fail.

- [X] T008 [US1] Review every proposed apex sentence against the definition/execution/handoff sibling partition in `specs/036-rule-layer-independence/data-model.md`
- [X] T009 [US1] Rewrite `.claude/CLAUDE.md` with the single outcome, three lifecycle branches, evidence/control/handoff obligations, and generic multi-match algorithm without lower-node names
- [X] T010 [US1] Run the apex-only structural scans in `specs/036-rule-layer-independence/quickstart.md` §3 and confirm zero prohibited references
- [X] T011 [US1] Manually verify that the three apex branches are deductively necessary, lifecycle-ordered, non-overlapping, and collectively exhaustive

**Checkpoint**: The finalized apex is the stable parent for rule work.

---

## Phase 5: User Story 2 — Universal rules are independent and MECE (Priority: P1)

**Goal**: Retain five self-contained universal concerns and move conditional content out of the always-loaded layer without behavior loss.

**Independent Test**: Rule topology, reference scans, semantic ownership approximations, and apex-to-rule relation review pass; skill migration checks may still fail.

- [X] T012 [US2] Compare all eight current rules to the finalized apex and one another; confirm the five ownership rows and three conditional-file migrations in `specs/036-rule-layer-independence/data-model.md`
- [X] T013 [P] [US2] Rewrite requirements certainty without named routing or permission delegation in `.claude/rules/clarifier.md`
- [X] T014 [P] [US2] Rewrite dependency, branching, iteration, and inference completeness without output-structure ownership in `.claude/rules/thinking-lenses.md`
- [X] T015 [P] [US2] Rewrite authorization and safety around destructive actions, external effects, machine-wide changes, credentials, and remote execution in `.claude/rules/permissions.md`
- [X] T016 [P] [US2] Rewrite reader-facing hierarchy, horizontal grouping, one-logic grouping, and ordering in `.claude/rules/pyramid-principle.md`
- [X] T017 [P] [US2] Rewrite documentation integrity around canonical scope, contract synchronization, generation, non-duplication, process-artifact isolation, and recorded override in `.claude/rules/live-documentation.md`
- [X] T018 [US2] Add self-contained conditional Git behavior to `.claude/skills/git-workflow/SKILL.md` before removing `.claude/rules/git-workflow.md`
- [X] T019 [US2] Add self-contained current provider-documentation and tool-discovery behavior to `.claude/skills/cloud-platform-research/SKILL.md` before removing `.claude/rules/mcp.md`
- [X] T020 [US2] Remove `.claude/rules/git-workflow.md`, `.claude/rules/mcp.md`, and `.claude/rules/skill-routing.md` after T018–T019 preserve their non-duplicated behavior
- [X] T021 [US2] Run rule-layer structural tests and manually verify every surviving rule supports exactly one apex branch with no sibling overlap
- [X] T022 [US2] Confirm the apex-plus-rules byte count is below the corresponding legacy corpus and record the result in `specs/036-rule-layer-independence/quickstart.md`

**Checkpoint**: The always-loaded architecture is complete, independent, and smaller.

---

## Phase 6: User Story 3 — Skills self-identify and compose without routing (Priority: P2)

**Goal**: Make lifecycle-operation and domain-overlay packages independently discoverable, portable, and composable.

**Independent Test**: Skill metadata, upward-path, pairwise-name, owned-link, portable-path, and routing-fixture assertions pass.

- [X] T023 [US3] Compare all scoped authored skill descriptions against the finalized apex/rules and same-axis siblings; record no unowned operation, ambiguous boundary, or false MECE claim in `specs/036-rule-layer-independence/data-model.md`
- [X] T024 [P] [US3] Make formal requirement elicitation and material-ambiguity boundaries self-contained in `.claude/skills/clarifier/SKILL.md`
- [X] T025 [P] [US3] Make implementation, automatable red→green, security, contract-sync, and compound-operation boundaries self-contained in `.claude/skills/coder/SKILL.md`
- [X] T026 [P] [US3] Remove rule dependency and clarify explicit authorization versus proposal behavior in `.claude/skills/adr/SKILL.md`
- [X] T027 [P] [US3] Clarify incomplete-material creation and ordinary context elicitation in `.claude/skills/minto-builder/SKILL.md`
- [X] T028 [P] [US3] Clarify diagnosis-phase ownership in compound deliverable requests in `.claude/skills/minto-reviewer/SKILL.md`
- [X] T029 [P] [US3] Clarify substantive existing-document transformation and compound final-phase ownership in `.claude/skills/minto-rewriter/SKILL.md`
- [X] T030 [P] [US3] Narrow the Scrum trigger, preserve domain-overlay composition, and replace named artifact routing in `.claude/skills/scrum-master/SKILL.md`
- [X] T031 [P] [US3] State DADS domain-overlay composition and use package-portable reference paths in `.claude/skills/digital-agency-frontend/SKILL.md`
- [X] T032 [P] [US3] Replace named sibling routing with self-contained blocking-gap and implementation obligations in `.claude/skills/digital-agency-frontend/references/dashboard-design.md`
- [X] T033 [P] [US3] Make archive paths portable and destructive refresh steps authorization-safe in `.claude/skills/digital-agency-frontend/references/sourcing-and-licensing.md`
- [X] T034 [P] [US3] Harden live-source download examples in `.claude/skills/digital-agency-frontend/references/component-implementation.md`
- [X] T035 [P] [US3] Remove redundant upward/back-links while retaining valid owned-resource navigation in `.claude/skills/scrum-master/references/README.md` and `.claude/skills/scrum-master/references/scrum-master-role.md`
- [X] T036 [US3] Run skill structural tests and all eight positive/compound/negative routing fixtures in `tests/run-config-pyramid.sh`
- [X] T037 [US3] Verify all edited owned links resolve and `.claude/skills/digital-agency-frontend/references/dads-docs/` has no diff

**Checkpoint**: No central routing table or lateral package knowledge is required for skill selection or execution.

---

## Phase 7: User Story 4 — Durable synchronized architecture (Priority: P1)

**Goal**: Align public documentation, decision rationale, and existing contract tests with the stable runtime design.

**Independent Test**: No current documentation/test references a deleted runtime rule; design guide and ADR independently explain the final model; targeted suites pass.

- [ ] T038 [P] [US4] Replace the runtime configuration tree and metadata-driven multi-match explanation in `README.md`
- [ ] T039 [P] [US4] Apply the equivalent user-facing architecture and MCP verification updates in `README.ja.md`
- [ ] T040 [P] [US4] Rewrite the configuration taxonomy, relation table, authoring decisions, and validation procedure in `docs/claude-config-design.md`
- [ ] T041 [P] [US4] Rewrite MCP operational ownership from unconditional rule to conditional skill/tool discovery in `docs/mcp-servers.md`
- [ ] T042 [P] [US4] Synchronize affected Japanese Minto skill documentation in `docs/minto-builder.ja.md`, `docs/minto-reviewer.ja.md`, and `docs/minto-rewriter.ja.md`
- [ ] T043 [US4] Rewrite Proposed ADR-0015 with the finalized semantic hierarchy, mechanism separation, reference boundary, alternatives, and consequences in `docs/adr/0015-rule-layer-independence.md`
- [ ] T044 [US4] Replace central-router assertions with description/package-independence contracts in `tests/run-digital-agency-frontend-skill.sh`
- [ ] T045 [US4] Update any affected installer, routing, or MCP tests without weakening their observable behavior contracts
- [ ] T046 [US4] Run targeted suites from `specs/036-rule-layer-independence/quickstart.md` §6

**Checkpoint**: Runtime, documentation, ADR, and compatibility tests tell one story.

---

## Phase 8: Full Validation

**Purpose**: Detect cross-artifact contradictions, remediate under the user's existing implementation authorization, and prove completion.

- [ ] T047 Run every `tests/run-*.sh` suite and isolate any environment-only failure with exact evidence
- [ ] T048 Run frontmatter, package-link, archive-diff, byte-budget, prohibited-reference, and `git diff --check` validation from `specs/036-rule-layer-independence/quickstart.md`
- [ ] T049 Validate FR-001–FR-018 and SC-001–SC-010 against concrete evidence; mark all completed tasks and leave ADR-0015 Proposed

---

## Dependencies and Execution Order

### Phase dependencies

- Phase 1 establishes requirements and baseline.
- Phase 2 depends on Phase 1 and creates the RED contract.
- Phase 3 depends on Phase 2 and freezes the parent apex.
- Phase 4 depends on Phase 3 and freezes universal rules.
- Phase 5 depends on Phase 4 and then changes conditional skills.
- Phase 6 depends on stable runtime structure from Phases 3–5.
- Phase 7 depends on every user story and may return to the owning artifact when analysis finds a contradiction.

### Parallel opportunities

- T011–T015 are disjoint rule files after T010 establishes shared ownership boundaries.
- T022–T033 are disjoint skill packages/resources after T021 establishes the two-axis classification.
- T036–T040 are disjoint documentation files after runtime structure is stable.

### Story independence

- US1 is independently testable and defines the parent contract.
- US2 can be validated against US1 without any skill edit, although migration skill stubs must exist before rule deletion.
- US3 is independently testable against the stable apex/rules.
- US4 is independently testable as documentation and regression synchronization, but intentionally waits for runtime stability.

## Notes

- `[P]` means parallel only after the phase's relationship-review task completes.
- Use `apply_patch` for edits and preserve unrelated user changes.
- A task becomes `[X]` only after its stated check passes.
- Do not commit, push, accept the ADR, or modify vendored third-party archives.
