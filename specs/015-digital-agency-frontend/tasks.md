# Tasks: Digital Agency Frontend Skill

**Input**: Design documents from `specs/015-digital-agency-frontend/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/skill-interface.md`, `quickstart.md`

**Tests**: Required by FR-017 and the repository's strict TDD policy. The dedicated suite exposes `dads`, `dashboard`, and `sync` selectors so each user story can be verified independently.

**Organization**: Tasks are grouped by user story and ordered red → green → refactor/documentation.

## Phase 1: Setup

**Purpose**: Establish the deterministic contract before implementation.

- [x] T001 Create selector-based failing contract checks for skill metadata, DADS workflow, dashboard workflow, source records, cross-agent discovery, installer registration, and documentation in `tests/run-digital-agency-frontend-skill.sh`
- [x] T002 Run `bash tests/run-digital-agency-frontend-skill.sh` and record that `dads`, `dashboard`, and `sync` selectors fail because the feature is not implemented

---

## Phase 2: Foundational

**Purpose**: Create the standard skill package shell required by every user story.

- [x] T003 Initialize `.claude/skills/digital-agency-frontend/` with the standard skill-creator script, `references/`, and generated `agents/openai.yaml`
- [x] T004 Replace generated placeholders with concise routing and workflow structure in `.claude/skills/digital-agency-frontend/SKILL.md`

**Checkpoint**: The package is discoverable by path and structurally valid, but story-specific contract selectors remain red.

---

## Phase 3: User Story 1 - Build an accessible public-service frontend (Priority: P1) 🎯 MVP

**Goal**: Provide the DADS-based React/Tailwind workflow, official-source handling, accessibility gates, and implementation composition.

**Independent Test**: `bash tests/run-digital-agency-frontend-skill.sh dads` passes while dashboard and sync work can remain incomplete.

### Implementation

- [x] T005 [US1] Write the dated source inventory, React/Tailwind version adaptation, DADS component selection, accessibility checklist, and attribution guidance in `.claude/skills/digital-agency-frontend/references/dads-react-tailwind.md`
- [x] T006 [US1] Complete the intent-to-close-out workflow, source drift behavior, `coder`/`clarifier` composition, and DADS reference routing in `.claude/skills/digital-agency-frontend/SKILL.md`
- [x] T007 [US1] Run `bash tests/run-digital-agency-frontend-skill.sh dads` and the standard structural validator; fix only US1 contract failures

**Checkpoint**: General DADS React/Tailwind frontend requests are independently supported and validated.

---

## Phase 4: User Story 2 - Build a decision-oriented web dashboard (Priority: P2)

**Goal**: Add web-dashboard requirements, presentation/exploration selection, visual encoding, layout, and accessible alternatives without Power BI artifact generation.

**Independent Test**: `bash tests/run-digital-agency-frontend-skill.sh dashboard` passes after US1 foundation is available.

### Implementation

- [x] T008 [US2] Write the dated guidebook source inventory, dashboard requirements worksheet, presentation/exploration decision, information hierarchy, chart selection, layout, color, interaction, and accessible-alternative gates in `.claude/skills/digital-agency-frontend/references/dashboard-design.md`
- [x] T009 [US2] Add conditional dashboard-reference loading and the explicit web-only/Power-BI boundary to `.claude/skills/digital-agency-frontend/SKILL.md`
- [x] T010 [US2] Run `bash tests/run-digital-agency-frontend-skill.sh dashboard`; fix only US2 contract failures

**Checkpoint**: Dashboard work is independently supported without loading dashboard detail for general frontend work.

---

## Phase 5: User Story 3 - Use the same skill across supported coding agents (Priority: P3)

**Goal**: Expose one authored skill through both discovery mechanisms and document the user-level behavior.

**Independent Test**: `bash tests/run-digital-agency-frontend-skill.sh sync`, `bash tests/run-codex-sync.sh`, and `bash tests/run-codex-sync-drift.sh` pass.

### Implementation

- [x] T011 [US3] Create `.agents/skills/digital-agency-frontend` as a relative symlink to `../../.claude/skills/digital-agency-frontend`
- [x] T012 [US3] Register `digital-agency-frontend` in `CUSTOM_SKILLS` and update nearby installer comments in `install.sh`
- [x] T013 [US3] Add composed `coder` → `digital-agency-frontend` routing to `.claude/CLAUDE.md` and `.codex/AGENTS.md`
- [x] T014 [US3] Add the new skill to the English/Japanese capability lists, installation map, and repository tree in `README.md` and `README.ja.md`
- [x] T015 [US3] Update the element deployment classification in `.codex/README.md` and hard-coded custom-skill expectations in `tests/run-codex-sync.sh`
- [x] T016 [US3] Run the dedicated sync contract and isolated install/drift suites; confirm the repository passes and record that the real user deployment remains stale until `install.sh` is intentionally run

**Checkpoint**: One skill body is available from Claude and Codex before and after isolated repeated installation.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Prove the whole feature, synchronize the record, and remove generated placeholders.

- [x] T017 Mark completed tasks in `specs/015-digital-agency-frontend/tasks.md` and verify the implementation against `spec.md`, `plan.md`, and `contracts/skill-interface.md`
- [x] T018 Run the full dedicated suite, skill structural validator, sync suites, live-documentation suite, post-edit-format suite, shell lint/format checks, and `git diff --check`
- [x] T019 Review `git diff` for accidental scope expansion, copied official content, secrets, stale counts, broken links, or missing attribution and correct any findings in the affected files

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: Starts immediately and establishes red tests.
- **Foundational**: Depends on Setup and initializes the package shape.
- **US1**: Depends on Foundational and delivers the MVP.
- **US2**: Depends on the core workflow from US1 but remains independently selectable and testable.
- **US3**: Depends on the final skill directory existing; it does not depend on dashboard content semantics.
- **Polish**: Depends on all three stories.

### TDD Order

1. T001 writes every selector contract before feature implementation.
2. T002 proves all selectors fail.
3. T005–T007 turn `dads` green.
4. T008–T010 turn `dashboard` green.
5. T011–T016 turn `sync` green and run the integration fixtures.
6. T018 proves the combined suite remains green.

### Parallel Opportunities

- Research already separated DADS and dashboard domains, but implementation remains sequential because both update `SKILL.md`.
- After T011 and T012, T013, T014, and T015 touch disjoint files and could run in parallel; they are executed locally in sequence to avoid hidden documentation dependencies.
- Independent verification commands in T018 can be batched where their test fixtures do not share state.

## Parallel Example: User Story 3

```text
Task: "Update routing in .claude/CLAUDE.md and .codex/AGENTS.md"
Task: "Update bilingual README capability and installation documentation"
Task: "Update .codex/README.md and tests/run-codex-sync.sh expectations"
```

## Implementation Strategy

### MVP First

1. Establish the complete red contract.
2. Initialize the standard package.
3. Deliver US1 and make `dads` green.
4. Stop and validate general DADS frontend behavior independently.

### Incremental Delivery

1. Add US2 dashboard guidance and make `dashboard` green.
2. Add US3 discovery/install/documentation and make `sync` green.
3. Run the full repository validation matrix.

## Notes

- Do not commit, push, or open a pull request unless separately requested.
- Do not vendor the official DADS Markdown archive, dashboard PDF/text, Power BI templates, or third-party assets.
- Use official live sources as authoritative; bundled references must state their retrieval date and fallback status.
