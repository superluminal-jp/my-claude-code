---

description: "Task list for removing solo-practice capability from scrum-master and syncing routing docs"
---

# Tasks: Remove solo-practice individual-use capability from `scrum-master`

**Input**: Design documents from `/specs/018-remove-solo-practice/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [quickstart.md](quickstart.md)

**Tests**: Not requested — no existing test exercises solo-specific routing (research.md R1), so no test task is needed; the existing suites are re-run in Polish as a non-regression check.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Confirm the six-file inventory from research.md R1 is still accurate by re-running the same greps (`ソロ|solo|個人` across `.claude/`, `.codex/`, `README.md`; `solo-practice` across `.claude/skills/scrum-master/`) — catches any drift between spec-writing time and implementation time.

---

## Phase 2: User Story 2 - The skill's declared capability matches its actual content (Priority: P1)

**Goal**: Delete the solo-practice file and remove every solo/individual-use mention from `SKILL.md` and the four routing-declaration documents.

**Independent Test**: Grep for solo/individual language across the five documents; confirm zero matches (quickstart.md step 2).

### Implementation for User Story 2

- [X] T002 [US2] Delete `.claude/skills/scrum-master/references/solo-practice.md`.
- [X] T003 [US2] In `.claude/skills/scrum-master/SKILL.md`, remove the solo/individual-use clause from the frontmatter `description` (the sentence "チームがなくても、個人の作業に対して自分専用のScrum Masterとして自己ファシリテーション（週次計画・日次チェックイン・個人レトロ）を行うソロプラクティスにも対応する。"), keeping the rest of the description intact.
- [X] T004 [US2] In the same file, remove the solo/individual-use clause from the frontmatter `when_to_use` (the sentence starting "Also use for a personal/solo Scrum Master request…"), keeping the rest of `when_to_use` intact.
- [X] T005 [US2] In the same file's body, remove the "## 個人利用（ソロプラクティス）" section in full.
- [X] T006 [US2] In the same file's reference-file routing table, remove the row pointing to `solo-practice.md`.
- [X] T007 [P] [US2] In `.claude/rules/skill-routing.md`, remove the sentence "Applies with or without a team: self-facilitation for one person's own work — personal weekly planning, daily check-ins, a solo retrospective — routes here too." from the `scrum-master` bullet, keeping the rest of the bullet intact.
- [X] T008 [P] [US2] In `.claude/CLAUDE.md`, change "`scrum-master` — Scrum events, facilitation, impediments, team or solo retrospectives" to "`scrum-master` — Scrum events, facilitation, impediments, team retrospectives".
- [X] T009 [P] [US2] In `.codex/AGENTS.md`, change "Scrum events, facilitation, impediment removal, team or solo retrospectives → `scrum-master`" to "Scrum events, facilitation, impediment removal, team retrospectives → `scrum-master`".
- [X] T010 [P] [US2] In `README.md`, change "`scrum-master` (Scrum events, facilitation, impediments, flow metrics; team or solo)." to "`scrum-master` (Scrum events, facilitation, impediments, flow metrics; team)." — adjust line-wrap as needed to keep the surrounding list formatting intact.

**Checkpoint**: Re-run quickstart.md steps 1–2; zero solo/individual mentions remain, file is deleted, nothing links to it.

---

## Phase 3: User Story 1 - A solo/individual-use request no longer routes to `scrum-master` (Priority: P1)

**Goal**: Confirm the Phase 2 edits actually change routing behavior, not just documentation wording.

**Independent Test**: quickstart.md step 3 — sample solo and team prompts, confirm the former no longer routes to `scrum-master` and the latter still does.

### Verification for User Story 1

- [X] T011 [US1] Issue at least 3 previously-solo-routed prompts (per quickstart.md step 3) in an agent session; confirm none routes to `scrum-master` (depends on T002–T010 being complete, since routing is driven by the frontmatter/routing-doc text those tasks change).
- [X] T012 [US1] Issue at least 3 team-facing prompts (per quickstart.md step 3) in the same session; confirm all still route to `scrum-master` exactly as before (depends on T002–T010).

**Checkpoint**: Routing behavior confirmed changed for solo prompts and unchanged for team prompts.

---

## Phase 4: User Story 3 - Team-facing content and citation work survive untouched (Priority: P2)

**Goal**: Confirm nothing outside the six files in scope was touched, and the `017-scrum-master-rewrite` citation work is fully intact.

**Independent Test**: quickstart.md steps 4–6.

### Verification for User Story 3

- [X] T013 [US3] Confirm every reference file other than `solo-practice.md` (`scrum-framework.md`, `scrum-master-role.md`, `event-playbooks.md`, `facilitation-and-coaching.md`, `measurement-and-diagnostics.md`, `scaling-frameworks.md`, `anti-patterns-and-coaching.md`, `sources.md`) is byte-identical to its state before this feature's tasks started (`git diff` shows no unintended changes).
- [X] T014 [US3] Confirm the `[SG20` citation count in `scrum-framework.md` (and spot-check 2–3 other files) matches `017-scrum-master-rewrite`'s verified end-state — no citation lost (quickstart.md step 4).
- [X] T015 [US3] Re-run the link-integrity check (quickstart.md step 5) across the surviving files; confirm zero broken links and confirm no remaining link targets `solo-practice.md`.

**Checkpoint**: All three user stories verified; feature complete pending Polish.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T016 Run `bash tests/run-skill-routing.sh` and `bash tests/run-codex-sync.sh`; confirm the same pass/fail profile as at the end of `017-scrum-master-rewrite` (quickstart.md step 6) — no new failures introduced by this feature.

---

## Dependencies & Execution Order

- **Setup (T001)**: No dependencies.
- **User Story 2 (T002–T010)**: Depends on T001. T002–T006 (same file/skill directory) are sequential; T007–T010 (four independent documents) can run in parallel with each other and with T002–T006.
- **User Story 1 (T011–T012)**: Depends on all of T002–T010 (routing behavior depends on every doc being updated, not just some).
- **User Story 3 (T013–T015)**: Can run in parallel with User Story 1's verification, since both depend only on T002–T010 being complete, not on each other.
- **Polish (T016)**: Depends on Phases 2–4 all complete.

## Implementation Strategy

Since User Story 2's edits are the only actual changes (User Stories 1 and 3 are verification of those same edits from different angles), there is no meaningful "MVP-first" staging — complete Phase 2 in full, then verify via Phases 3–4 in parallel, then Polish.
