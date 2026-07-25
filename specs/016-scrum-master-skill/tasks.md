---

description: "Task list for feature 016 — integrate the scrum-master skill"
---

# Tasks: Integrate the `scrum-master` skill into the shared skill set

**Input**: Design documents from `/specs/016-scrum-master-skill/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/skill-integration.md](./contracts/skill-integration.md), [quickstart.md](./quickstart.md)

**Tests**: Test tasks ARE included — the specification explicitly requires them (FR-019 routing regression coverage, FR-020 no regressions, FR-009 enforced by SYNC-03). They are not speculative additions.

**Organization**: Tasks are grouped by user story so each can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3, mapping to the user stories in spec.md
- Every task names its exact file path

## Path Conventions

This repository has no `src/`. Its source is the configuration tree — `.claude/`, `.codex/`, `.agents/` — plus `install.sh` and the `tests/run-*.sh` behaviour suites. All paths below are relative to the repository root `/Users/taikiogihara/work/my-claude-code/`.

**Source of the vendored payload**: `/Users/taikiogihara/work/scrum-master-skill/scrum-master/` (read-only import source; not an upstream — FR-021/FR-022).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the import source is intact and nothing in the repo will silently reject the new skill.

- [X] T001 Record the source inventory as a baseline: run `find /Users/taikiogihara/work/scrum-master-skill/scrum-master -type f | sort` and confirm exactly 11 files (1 `SKILL.md`, 9 `references/*.md`, 1 `scripts/flow_metrics.py`); note the executable bit on the script via `ls -l`
- [X] T002 [P] Confirm no ignore rule will swallow the skill: `git check-ignore -v .claude/skills/scrum-master/SKILL.md` must report nothing (research R7, FR-004)
- [X] T003 [P] Capture the pre-change skill count for later count updates: `ls .claude/skills | grep -vc '^speckit-'` (expect `6`; becomes `7` after this feature)

**Checkpoint**: Import source verified, no blockers.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Get the skill payload into the repository, correct. Every user story depends on this.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Copy the payload preserving mode: `cp -R /Users/taikiogihara/work/scrum-master-skill/scrum-master .claude/skills/scrum-master`, producing `.claude/skills/scrum-master/{SKILL.md,references/,scripts/}` (FR-001)
- [X] T005 Remove the `allowed-tools:` line from the frontmatter of `.claude/skills/scrum-master/SKILL.md` — it names no tool that exists and would restrict the skill's tool set rather than grant a permission (research R0, contract C7). Leave `name`, `description`, and `when_to_use` byte-identical (FR-002, contract C4)
- [X] T006 Fix the unresolvable invocation in the body of `.claude/skills/scrum-master/SKILL.md` (source line 133, the fenced block in the "スクリプト：フロー指標の計算" section). Replace `python3 ${CLAUDE_SKILL_DIR}/scripts/flow_metrics.py tickets.csv` with the **repo-root-relative** form `python3 .claude/skills/scrum-master/scripts/flow_metrics.py tickets.csv`, and add one sentence noting that from a user-scope install the same command is `python3 ~/.claude/skills/scrum-master/scripts/flow_metrics.py tickets.csv`. **These two strings MUST match T013's two permission patterns character-for-character up to the argument** — a skill-directory-relative form such as `python3 scripts/flow_metrics.py` would not match either pattern and would make T016 fail. Leave the prose reference to `scripts/flow_metrics.py` on source line 130 unchanged; it is a correct relative reference, not a command (research R1, FR-014, FR-016)
- [X] T007 Verify the payload against contract C1–C3: 11 files present, `test -x .claude/skills/scrum-master/scripts/flow_metrics.py`, shebang is `#!/usr/bin/env python3`, and every relative Markdown link in `SKILL.md` and `references/*.md` resolves (quickstart step 1; FR-003, SC-005)
- [X] T008 Confirm the frontmatter diff against the source contains **only** the removed `allowed-tools` line: `diff <(sed -n '/^---$/,/^---$/p' /Users/taikiogihara/work/scrum-master-skill/scrum-master/SKILL.md) <(sed -n '/^---$/,/^---$/p' .claude/skills/scrum-master/SKILL.md)` (quickstart step 3; FR-002)

**Checkpoint**: The skill exists in the repository, is internally coherent, and its identity is preserved. User story work can begin.

---

## Phase 3: User Story 1 - A Scrum request loads the skill automatically (Priority: P1) 🎯 MVP

**Goal**: A Scrum, facilitation, or solo-practice request routes to `scrum-master` without the user naming it, and the flow-metrics helper runs without an ad-hoc permission prompt.

**Independent Test**: Open an agent session in this repository, issue a Scrum-flavoured prompt that never says "skill", and observe `scrum-master` load. Then run the helper on a sample CSV and confirm no prompt appears.

### Implementation for User Story 1

- [X] T009 [P] [US1] Add `scrum-master` to the "Skills (mandatory routing)" bullet list in `.claude/CLAUDE.md`, with a one-line trigger description matching the register of the existing entries (FR-007)
- [X] T010 [P] [US1] Add the Scrum/agile-facilitation category to `.claude/rules/skill-routing.md`, routing it to `scrum-master`; state how a compound request spanning Scrum and document work is resolved, consistent with the existing compound-work rule (FR-006)
- [X] T011 [US1] In the same `.claude/rules/skill-routing.md` edit, add the explicit negative boundary required by FR-007a: non-Scrum project management (schedules, Gantt charts, status reports, PMBOK deliverables) does NOT route to `scrum-master`. This is the counterweight to the wider always-loaded trigger surface (depends on T010, same file)
- [X] T012 [P] [US1] Add the routing bullet to the "Skill routing" list in `.codex/AGENTS.md`, ending in the literal string `@.agents/skills/scrum-master/SKILL.md` — `tests/run-codex-sync.sh` SYNC-03 matches this exactly (FR-009, contract C5/V10)
- [X] T013 [US1] Add two anchored entries to `permissions.allow` in `.claude/settings.json`: `Bash(python3 .claude/skills/scrum-master/scripts/flow_metrics.py *)` and `Bash(python3 ~/.claude/skills/scrum-master/scripts/flow_metrics.py *)`. Both MUST match the two commands T006 writes into the playbook character-for-character up to the argument. Do NOT add a bare `Bash(python3 *)` — it violates FR-015 and `permissions.md` least privilege (research R1, contract C7)
- [X] T014 [US1] Confirm `.codex/AGENTS.md` still fits its size budget after T012: `wc -c .codex/AGENTS.md` must be ≤ 32768, and note if it exceeds the 28672 warning threshold (SYNC-03)

### Verification for User Story 1

- [X] T015 [US1] **Observe, do not assume** — in a live Claude Code session in this repository, run the six routing probes from quickstart step 4 (4a 「チームのレトロがマンネリ化している」, 4b 「sprint planning のアジェンダを作って」, 4c 「自分ひとりの作業を週次で振り返りたい」, **4d "our stand-ups keep running long" (English — the case most likely to fail, since the body is Japanese)** → all `scrum-master`; 4e 「プロジェクトのガントチャートを引き直したい」 → NOT `scrum-master`; 4f a code request → `coder` unchanged). Records SC-001 (both languages required), SC-009, FR-005, FR-008
- [X] T016 [US1] Run the helper on a throwaway CSV per quickstart step 4 and confirm it returns cycle-time, throughput, and WIP **with no permission prompt** (SC-007, FR-014). Also re-check the guardrail against the *final* command form T006 settled on — `echo '{"command":"<the exact command>"}' | bash scripts/guardrails/destructive-command.sh` must return `allow` — since research R2 verified only a hypothetical path (FR-014 guardrail clause). If a prompt appears, capture the exact command Claude Code reports and correct the T013 patterns; a persisting prompt degrades FR-014 only and does not block the feature, but record it either way
- [X] T017 [US1] Confirm the helper's failure path is legible: invoke it with a nonexistent file and with a malformed CSV; expect a readable error and non-zero exit, never fabricated numbers (FR-016)

**Checkpoint**: User Story 1 complete — the skill is reachable and usable from this repository. This is the MVP; the feature delivers value here even if Phases 4–6 are deferred.

---

## Phase 4: User Story 2 - The skill reaches every agent the repo supports (Priority: P2)

**Goal**: After one installer run, `scrum-master` is available to Claude Code and Codex CLI from any working directory.

**Independent Test**: Run `install.sh`, then confirm the skill directory and both symlinks exist and resolve to the installed copy.

### Implementation for User Story 2

- [X] T018 [P] [US2] Add `scrum-master` to the `CUSTOM_SKILLS` list at `install.sh:117` (currently `"adr clarifier coder minto-builder minto-reviewer minto-rewriter"`). No other installer change is needed — `sync_path "skills"` is already a recursive `cp -R` that carries `references/` and `scripts/` (research R4, FR-010/FR-011)
- [X] T019 [P] [US2] Create the repo-local Codex mirror link: `ln -s ../../.claude/skills/scrum-master .agents/skills/scrum-master`, relative like its six siblings so it never dangles (contract C6, SYNC-01)

### Verification for User Story 2

- [X] T020 [US2] Run `bash install.sh`, then confirm `~/.claude/skills/scrum-master/references` holds 9 files and `readlink ~/.agents/skills/scrum-master` resolves to `~/.claude/skills/scrum-master` — **not** to a path under `work/my-claude-code` (FR-011, SC-003, contract C6/V15). Then re-run T007's link check against the installed copy, not just the repo copy — US2's fourth acceptance scenario is specifically about links resolving *from the user-scope install*
- [X] T021 [US2] Prove idempotence per quickstart step 5: snapshot `find` output, run the installer a second time, snapshot again, `diff` clean (FR-012, SC-004)
- [X] T022 [US2] Confirm the Spec Kit exclusion still holds and did not catch the new skill: `ls ~/.claude/skills | grep -c '^speckit-'` returns 0 while `scrum-master` is present (FR-013, V18)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - The skill is documented and its routing is guarded by a test (Priority: P3)

**Goal**: The skill appears in every human inventory, and a regression case fails if routing to it ever breaks.

**Independent Test**: Read the inventories and find `scrum-master`; run the routing suite and see a `scrum-master` case pass.

### Tests for User Story 3

> The runner change (T023) must land **before** the case file can pass — see research R3.

- [X] T023 [US3] Extend the inline routing prompt in `tests/run-skill-routing.sh` — locate it by the literal anchors `Rules:` and `Output exactly one of:` inside the `query=` heredoc rather than by line number. Add a `scrum-master` rule to the rules list AND add `scrum-master` to the closing `Output exactly one of:` enum. Both are required — the runner builds a self-contained prompt and never reads `.claude/rules/skill-routing.md`, so a case expecting `scrum-master` can otherwise never pass (research R3, contract C9). Leave the existing `advisor` entry untouched — it is pre-existing drift and FR-020 requires existing cases to keep passing
- [X] T024 [US3] Create `tests/skill-routing/007-scrum-facilitation.md` following the exact format of `tests/skill-routing/001-code-implement.md`: `# Test:` title, `**Category**`, `**ID**: 007`, `## Input Prompt` fenced block containing a Scrum prompt that never names a skill, `## Expected Skill` = `scrum-master`, `## Expected Behavior`, `## Pass Criteria`, and a `## Baseline` block using `___` placeholders so the runner can fill them (FR-019, V24)
- [X] T025 [P] [US3] Add `scrum-master` to the hardcoded skill list in the SYNC-03 loop at `tests/run-codex-sync.sh:96` (`for skill_name in adr clarifier coder minto-builder minto-reviewer minto-rewriter`), turning FR-009 into an enforced invariant (research R5)

### Documentation for User Story 3

- [X] T026 [P] [US3] Update `README.md` in all three shapes: the prose skill inventory (~lines 33-35), the deployment table row listing the skill set (~line 85), and the directory tree (~lines 188-190). The tree entry must show `references/` and `scripts/`, since this is the first skill in the set that is not a bare `SKILL.md` (FR-017, FR-018, contract C8/V13)
- [X] T027 [P] [US3] Update `README.ja.md` in the same three shapes (~lines 18-23, 47, 79-85) **and** correct the count at line 9 from「6 個のスキルリンク」to 7 (FR-017, FR-018, V12)
- [X] T028 [P] [US3] Update the two deployment-map rows in `.codex/README.md` (lines 25-26), changing both「手書き 6 件」to 7 and confirming the `.claude/skills/*` wildcard row still covers the new files without further edit (research R5, V12)

### Verification for User Story 3

- [X] T029 [US3] Verify US3's own artifacts, independently of whether US1 and US2 have landed: `scrum-master` appears by name in `README.md`, `README.ja.md`, `tests/run-codex-sync.sh`, and `tests/run-skill-routing.sh`. **`.codex/README.md` is excluded from the by-name check**: it is a deployment map keyed by path pattern (`.claude/skills/*`) and names no individual skill — not `adr`, not `coder`, none of them — so the correct change there is the hand-written count, verified separately below. Then: `ls .claude/skills | grep -vc '^speckit-'` returns `7`; and every count stated in prose agrees with it. Also read each inventory entry once and confirm a reader can tell what the skill is for from that line alone, without opening `SKILL.md` (SC-006). The full nine-file cross-story sweep belongs to T035, not here

**Checkpoint**: All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T030 Run the full regression gate: `for s in tests/run-*.sh; do echo "=== $s ==="; bash "$s" || echo "FAILED: $s"; done`. Every suite must pass. `run-codex-sync.sh` SKIPs its post-install checks when `~/.codex` is absent — SKIP is not failure (FR-020, SC-008)
- [X] T031 Confirm the six pre-existing routing cases (`tests/skill-routing/001`–`006`) still resolve to their recorded skills — adding the seventh must not perturb them (SC-002, FR-008, contract C10)
- [X] T032 [P] Walk [quickstart.md](./quickstart.md) end to end and tick its "Done when" boxes, recording any step that could not be run and why
- [X] T033 [P] Confirm no synchronisation machinery back to `/Users/taikiogihara/work/scrum-master-skill/` was introduced anywhere in the change — no sync script, no drift test, no scheduled reconciliation (FR-022, contract non-goals)
- [X] T034 Re-read the final diff against `live-documentation.md` § 1 Drift: the skill inventory is the changed public contract, so confirm all three inventories moved in this same change rather than being deferred
- [X] T035 Run the full catalog-agreement sweep from quickstart step 6 across the eight files that name skills individually (`.claude/CLAUDE.md`, `.claude/rules/skill-routing.md`, `.codex/AGENTS.md`, `README.md`, `README.ja.md`, `install.sh`, `tests/run-codex-sync.sh`, `tests/run-skill-routing.sh`); every one must report a non-zero `scrum-master` match count. `.codex/README.md` is verified by its hand-written count instead, since it names no skill individually. This spans all three user stories, which is why it sits here rather than inside any one of them (invariant I1)
- [X] T036 Propose an ADR at `docs/adr/0003-vendor-scrum-master-skill.md` recording the two decisions this feature settled: that the skill is vendored into this repository and that this repository becomes its **sole source of truth**, with the external `/Users/taikiogihara/work/scrum-master-skill/` directory retired as an upstream. Follow the MADR shape of the existing `docs/adr/0001-remove-vendored-speckit-skills.md` — Context, Decision, Consequences, and the rejected alternative (keep the external directory upstream and build drift-detection tooling). This is the durable provenance record FR-021 requires, and discharges the one-way-door ADR obligation in `.claude/CLAUDE.md`'s close-out rules (FR-021, finding C2)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies — start immediately
- **Foundational (Phase 2)**: depends on Phase 1 — **BLOCKS all user stories**
- **User Story 1 (Phase 3)**: depends on Phase 2. Delivers the MVP
- **User Story 2 (Phase 4)**: depends on Phase 2 only — independent of US1
- **User Story 3 (Phase 5)**: depends on Phase 2 only — fully independent of US1 and US2 since the cross-story sweep moved to T035
- **Polish (Phase 6)**: depends on all desired stories being complete. T035 in particular spans all three and cannot run earlier

### User Story Dependencies

- **US1 (P1)**: needs only the Phase 2 payload. Fully independent
- **US2 (P2)**: needs only the Phase 2 payload. Fully independent of US1 — the installer does not care whether routing is wired
- **US3 (P3)**: fully independent. Its verification (T029) checks only US3's own five files; the sweep that needs all three stories present is T035 in Polish

### Within Each User Story

- T011 follows T010 — same file, and the boundary rule is written into the section T010 creates
- T013 must agree with T006 character-for-character; whichever lands second is checked against the first (finding I1)
- T014 follows T012 — measures the file T012 edits
- T015–T017 follow all of T009–T013 — verification of what those tasks wired
- T020–T022 follow T018 and T019 — nothing to install until both land
- T024 follows T023 — the case cannot pass until the runner's enum admits the name

### Parallel Opportunities

- T002, T003 in parallel (Phase 1)
- T009, T010, T012 in parallel — three different files
- T018, T019 in parallel — `install.sh` and a new symlink
- T025, T026, T027, T028 in parallel — four different files
- US1, US2, and US3's authoring tasks can proceed in parallel once Phase 2 completes

---

## Parallel Example: User Story 1

```bash
# Three routing surfaces, three different files — safe to edit together:
Task: "Add scrum-master to the mandatory-routing list in .claude/CLAUDE.md"
Task: "Add the Scrum category to .claude/rules/skill-routing.md"
Task: "Add the routing bullet to .codex/AGENTS.md"
```

## Parallel Example: User Story 3

```bash
# Four inventory/test files, no overlap:
Task: "Add scrum-master to the SYNC-03 list in tests/run-codex-sync.sh"
Task: "Update the three inventory shapes in README.md"
Task: "Update the three inventory shapes and the count in README.ja.md"
Task: "Update the two deployment-map rows in .codex/README.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 Setup → 2. Phase 2 Foundational (blocks everything) → 3. Phase 3 User Story 1
4. **STOP and VALIDATE**: T015–T017 — the skill loads on its own and the helper runs
5. At this point the skill is fully usable inside this repository

### Incremental Delivery

1. Setup + Foundational → payload correct and coherent
2. + US1 → skill reachable in-repo — **MVP**
3. + US2 → skill reachable machine-wide from both agents
4. + US3 → inventories agree and a regression case guards the routing
5. + Polish → full suite green, quickstart walked

---

## Notes

- **The two `SKILL.md` corrections (T005, T006) are the only content edits to the vendored skill.** Everything else is copied verbatim. Do not translate, restructure, or "improve" the playbook — that is out of scope by an explicit spec assumption.
- **T015 and T016 cannot be discharged by reasoning.** They require a live session and an actual observation; research R1 flags the permission pattern as inferred from existing entries, not from a specification.
- The pre-existing `advisor` drift in the routing harness is deliberately left alone (research R3). If it should be fixed, that is a separate change.
- Commit after each phase or logical group; the branch is `016-scrum-master-skill` and commits follow Conventional Commits per `git-workflow.md`.
