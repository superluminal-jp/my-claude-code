---

description: "Task list for refreshing the portable system prompts"
---

# Tasks: Refresh Portable System Prompts

**Input**: Design documents from `specs/041-refresh-portable-prompts/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/portable-prompt-contract.md

**Tests**: The spec does not request test code. Verification is the scripted check in quickstart.md (steps 1–2) plus a manual read-through (steps 3–4); T002 establishes the pre-change observation.

**Organization**: One phase per user story; US1 and US2 touch different files and are independent.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Re-read `.claude/CLAUDE.md` and the five files in `.claude/rules/`; confirm the R6 mapping table in `specs/041-refresh-portable-prompts/research.md` still matches (no rule changed since 2026-10-05)
- [x] T002 Record the pre-change observation: run quickstart.md step 1–2 against the current `chatgpt-system-prompt.md` and `claude-ai-system-prompt.md`; save the output as a "Pre-change observation" section in `specs/041-refresh-portable-prompts/research.md` (expect failures: PP-03, PP-04/07, PP-06)

**Checkpoint**: baseline recorded.

## Phase 2: Foundational

- [x] T003 Draft the shared behavior text (accuracy and uncertainty, authorization boundary, clarification with a default, answer-first structure, reasoning completeness, brevity) once, in positive phrasing with one-clause rationales and no all-caps emphasis, in `/private/tmp/claude-501/-Users-taikiogihara-work-my-claude-code/e2fa4b89-5c2b-46aa-a127-ab8d9008adb1/scratchpad/shared-core.md`; both prompts derive from it so they cannot drift apart

**Checkpoint**: shared core exists; US1 and US2 can proceed in parallel.

## Phase 3: User Story 1 — ChatGPT prompt (Priority: P1) 🎯 MVP

**Goal**: ChatGPT file is a faithful, size-valid, fact-verified projection.

**Independent Test**: quickstart.md steps 1–4 on `chatgpt-system-prompt.md` only.

- [x] T004 [P] [US1] Rewrite the header of `chatgpt-system-prompt.md`: placement (Settings → Personalization → Enable customization → Custom Instructions; mobile: Customize ChatGPT), plan limits (1,500 Free/Go; 5,000 paid), "More about you" flagged as UI-observed and officially undocumented, recommended Base style "Efficient"
- [x] T005 [US1] Rewrite the **Custom instructions** block in `chatgpt-system-prompt.md` (operating rules from T003, ≤1,500 chars, no model names, no thinking-level instructions); state its measured length beside the label
- [x] T006 [US1] Rewrite the **More about you** block in `chatgpt-system-prompt.md` (profile, deliverable preferences, language; ≤1,500 chars; remove "Memory off—this thread only"); state its measured length
- [x] T007 [US1] Add "Verified facts" (official URLs and 2026-10-05 date per research.md R1, R2) and "Not ported" (model-routing, skills, hooks, repo paths — with reasons) sections to `chatgpt-system-prompt.md`
- [x] T008 [US1] Run quickstart.md steps 1–2 on `chatgpt-system-prompt.md`; fix until PP-01, PP-04, PP-07 pass

**Checkpoint**: ChatGPT file complete and independently verified.

## Phase 4: User Story 2 — Claude.ai prompt (Priority: P1)

**Goal**: Claude.ai file is a faithful, fact-verified projection with no agent-tooling assumptions.

**Independent Test**: quickstart.md steps 1–4 on `claude-ai-system-prompt.md` only.

- [x] T009 [P] [US2] Rewrite the header of `claude-ai-system-prompt.md`: placement (initials menu → Settings → "Instructions for Claude"), "no character limit documented; self-budget ≈4,000", relation to Project instructions and Memory
- [x] T010 [US2] Rewrite the paste block in `claude-ai-system-prompt.md` from T003: remove "Execution Efficiency" and "Memory (use actively)"; add memory-handling guidance (context, lower priority than explicit instructions, no duplicate facts), authorization boundary for connector/Cowork actions, reasoning completeness; drop FURPS+/INVEST/MoSCoW/5W2H toolkit; state measured length
- [x] T011 [US2] Add "Verified facts" (R3, R4, R5 URLs, 2026-10-05) and "Not ported" sections to `claude-ai-system-prompt.md`
- [x] T012 [US2] Run quickstart.md steps 1–2 on `claude-ai-system-prompt.md`; fix until PP-01, PP-04, PP-07 pass

**Checkpoint**: Claude.ai file complete and independently verified.

## Phase 5: User Story 3 — Maintainer audit trail (Priority: P2)

**Goal**: A reviewer can audit facts and omissions from repository files alone.

**Independent Test**: reviewer lists every service fact with source/date and every omission with reason from the two files plus research.md, in <30 minutes.

- [x] T013 [US3] Cross-check PP-03 and PP-06 for both files: every service claim has a URL and date; every R6 omission appears under "Not ported"; fix gaps in `chatgpt-system-prompt.md` / `claude-ai-system-prompt.md`
- [x] T014 [P] [US3] Append a "Post-change observation" section (script output, checklist ticks) to `specs/041-refresh-portable-prompts/research.md`

## Phase 6: Polish & Cross-Cutting

- [x] T015 Confirm `README.md` and `README.ja.md` do not describe the two files (`grep -n -i "system-prompt\|chatgpt" README.md README.ja.md`); sync only if they do (FR-009)
- [x] T016 Run `.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed`; fix and re-run
- [x] T017 Run `git diff --stat`; confirm only the two root files and `specs/041-refresh-portable-prompts/` (plus `.specify/feature.json`) changed (FR-010)
- [x] T018 Walk quickstart.md steps 3–4 (open each URL, tick coverage) and report completed / skipped / unverified items

## Dependencies & Order

- T001 → T002 → T003 → (US1 ∥ US2) → US3 → Polish
- Within US1: T004 ∥ (T005 → T006) → T007 → T008. Within US2: T009 ∥ T010 → T011 → T012.
- T005, T006, T010 are sequential only because each consumes the T003 core; T004 and T009 touch headers only.

## Parallel Example

After T003: run T004 and T009 together (different files); then T005 and T010 together.

## Implementation Strategy

MVP = US1 (ChatGPT, the higher drift risk). Ship US1, then US2, then audit (US3). Each story is verifiable alone.
