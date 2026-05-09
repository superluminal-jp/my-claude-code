# Tasks: OpenAI Codex Review Skill

**Input**: Design documents from `specs/007-codex-review-skill/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: Not requested in spec. No test tasks included.

**Organization**: Tasks map to three user stories (US1: prereq guard, US2: on-demand review, US3: hook integration), delivered as independently testable increments.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1 / US2 / US3)

---

## Phase 1: Setup

**Purpose**: Create the skill directory and file skeleton so all later sections have a target to write into.

- [ ] T001 Create `.claude/skills/review/SKILL.md` with YAML frontmatter: `name: review`, `description` (one-sentence summary of the review skill), `argument-hint: "[--artifacts <mode>] [--perspectives <list>] [<file> ...]"`, `user-invocable: true`, `disable-model-invocation: false`

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Argument parsing must be resolved before any user story section can run Codex or collect artifacts.

**⚠️ CRITICAL**: All user story phases depend on this section being present.

- [ ] T002 Write the **Argument Parsing** section in `.claude/skills/review/SKILL.md` — document how to resolve `--artifacts` (allowed: `git-changed` | `user-specified` | `speckit-docs`; default: `git-changed`), `--perspectives` (allowed: `quality` | `security` | comma-separated list; default: `quality,security`), and positional `<file>` arguments (required when `--artifacts user-specified`, ignored otherwise)

**Checkpoint**: Skeleton + argument contract in place — user story sections can now be written independently.

---

## Phase 3: User Story 1 — Prerequisite Guard (Priority: P1) 🎯 MVP

**Goal**: When the OpenAI API key or `codex` CLI is missing, the skill exits immediately with a clear, named error message and fix instructions — before attempting any artifact collection or Codex call.

**Independent Test**: Unset `OPENAI_API_KEY`, invoke `/review`, verify the skill outputs the expected message and makes no further calls. Repeat with `codex` not on PATH.

- [ ] T003 [US1] Write the **Prerequisite Check** section in `.claude/skills/review/SKILL.md` — two sequential shell checks: (1) `[[ -z "$OPENAI_API_KEY" ]]` → output `"OPENAI_API_KEY is not set. Export it with: export OPENAI_API_KEY=sk-..."` and halt; (2) `command -v codex` → on failure output `` "`codex` is not installed. Install with: npm install -g @openai/codex" `` and halt. Both checks run before any artifact collection.

**Checkpoint**: Invoking `/review` with each prerequisite absent produces an actionable message and exits cleanly. US1 is independently testable and deliverable.

---

## Phase 4: User Story 2 — On-Demand Artifact Review (Priority: P2)

**Goal**: When both prerequisites pass, the skill collects artifacts per the selected mode, invokes Codex with the selected perspectives, and displays the structured review result in the Claude Code conversation.

**Independent Test**: With prerequisites met and at least one changed file in git, invoke `/review`. Verify a non-empty Codex review is returned and displayed. Verify each artifact mode resolves correctly. Verify an empty artifact set produces an informative message rather than an error.

- [ ] T004 [US2] Write the **Artifact Collection** section in `.claude/skills/review/SKILL.md` — implement three `ArtifactMode` branches: (a) `git-changed`: run `git diff --name-only HEAD`; fall back to `git status --short --porcelain | awk '{print $2}'` when HEAD does not exist; (b) `user-specified`: use the positional `<file>` arguments as-is; (c) `speckit-docs`: read `.specify/feature.json`, extract `feature_directory`, enumerate `${feature_directory}/*.md`. After collection, if the resolved list is empty output `"No reviewable artifacts found for mode <mode>."` and halt.

- [ ] T005 [US2] Write the **Codex Invocation** section in `.claude/skills/review/SKILL.md` — construct a review prompt combining the selected perspectives: quality section (correctness, naming, readability, dead code, error handling, maintainability) and/or security section (OWASP Top 10 classes, hardcoded secrets, unsafe deserialization, unsafe patterns); prompt must instruct Codex to report findings only, not modify files; invoke with `codex --quiet --approval-policy suggest "<prompt>" -- <file_list>`; capture stdout as the review result. (Depends on T004.)

- [ ] T006 [US2] Write the **Output & Error Handling** section in `.claude/skills/review/SKILL.md` — display the captured Codex stdout verbatim in the conversation under a `## Codex Review` heading; if Codex exits non-zero, output an actionable message: `"Codex returned an error. Check that OPENAI_API_KEY is valid and that the codex CLI version supports --approval-policy suggest."` — do not surface raw stderr or stack traces.

**Checkpoint**: Invoking `/review` with each artifact mode and both perspectives produces a structured Codex review. US2 independently covers the core value-delivery path.

---

## Phase 5: User Story 3 — Workflow Integration (Priority: P3)

**Goal**: The review skill can be registered as an opt-in `after_implement` hook so teams can trigger it automatically. The default state is disabled (no change to existing workflows).

**Independent Test**: (a) Confirm the new `after_implement` entry exists in `.specify/extensions.yml` with `enabled: false` and `optional: true`. (b) Temporarily set `enabled: true`, invoke `/speckit-implement`, and confirm the hook prompt appears.

- [ ] T007 [P] [US3] Append an `after_implement` hook entry to `.specify/extensions.yml` under the `after_implement` list: `extension: codex-review`, `command: review`, `enabled: false`, `optional: true`, `prompt: "Run Codex review after implementation?"`, `description: "Review implemented artifacts with OpenAI Codex for quality and security"`, `condition: null`

- [ ] T008 [US3] Write the **Hook Context** section in `.claude/skills/review/SKILL.md` — document that when invoked as a hook (no user arguments), the skill defaults to `--artifacts git-changed` and `--perspectives quality,security`; no interactive prompting occurs; the review result is appended to the conversation output of the implementation run.

**Checkpoint**: `extensions.yml` contains the new disabled hook entry. The skill documents its hook-mode behavior. US3 is independently verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T009 [P] Validate the SKILL.md invocation signature against `specs/007-codex-review-skill/contracts/skill-invocation.md` — confirm all parameters (`--artifacts`, `--perspectives`, `<file>`), defaults, and exit condition messages match exactly
- [ ] T010 Walk through all scenarios in `specs/007-codex-review-skill/quickstart.md` to validate golden-path and edge-case behavior (missing prerequisites, empty artifact set, each artifact mode, subset perspective selection)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks all user story phases
- **US1 (Phase 3)**: Depends on Phase 2
- **US2 (Phase 4)**: Depends on Phase 2; T005 depends on T004
- **US3 (Phase 5)**: Depends on Phase 2; T007 is independent of T008 (different files)
- **Polish (Phase 6)**: Depends on all user story phases

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 — independently testable after Phase 2
- **US2 (P2)**: No dependency on US1 at the SKILL.md level; logically US1 must precede US2 at runtime (prereq guard runs first in the skill flow), but the sections can be written in any order
- **US3 (P3)**: T007 (extensions.yml) is fully independent; T008 (SKILL.md section) requires the file to exist from T001

### Within Each User Story

- SKILL.md sections can be appended sequentially; T004 must precede T005 (collection before invocation)
- T007 and all SKILL.md tasks can proceed in parallel once Phase 2 is complete

### Parallel Opportunities

- T007 (extensions.yml) can run in parallel with any SKILL.md task
- T009 and T010 (polish) can run in parallel

---

## Parallel Example: User Story 2

```bash
# Append T004 and T007 simultaneously (different files):
Task: "Write Artifact Collection section in .claude/skills/review/SKILL.md"  → T004
Task: "Add after_implement hook entry to .specify/extensions.yml"             → T007

# Then T005 (depends on T004 being written):
Task: "Write Codex Invocation section in .claude/skills/review/SKILL.md"     → T005
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Create SKILL.md skeleton
2. Phase 2: Write Argument Parsing section
3. Phase 3: Write Prerequisite Check section
4. **STOP and VALIDATE**: Invoke `/review` without API key; confirm named error + clean exit
5. Ship as a usable safety net

### Incremental Delivery

1. Setup + Foundational → Skeleton ready
2. Add US1 (Phase 3) → Prerequisite guard works → Demo/validate
3. Add US2 (Phase 4) → On-demand review works → Demo/validate (core value)
4. Add US3 (Phase 5) → Hook registration available → Demo/validate

### Single-Developer Sequence

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010

---

## Notes

- All tasks write to or validate `.claude/skills/review/SKILL.md`, except T007 (`.specify/extensions.yml`) and T009/T010 (validation only)
- [P] tasks touch different files — they can be issued to parallel agents without conflicts
- Commit after completing each user story phase (use `/speckit-git-commit`)
- Stop at each **Checkpoint** to validate the story independently before continuing
