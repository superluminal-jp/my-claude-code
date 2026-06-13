---
description: "Task list for Claude Code Personal Configuration Optimization"
---

# Tasks: Claude Code Personal Configuration Optimization

**Input**: Design documents from `specs/010-claude-config-optimization/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/behavior-inventory.md, quickstart.md (all present)

**Tests**: No automated test suite — this is a configuration/documentation feature. "Verification" means running the `contracts/behavior-inventory.md` gate and the `quickstart.md` checks. No TDD test tasks are generated (none requested).

**Organization**: Tasks are grouped by user story. US2 (comprehension) and US6 (grounding) are both P2 and execute as one per-file pass (a file is edited once, satisfying both), so their phase tasks carry the combined label `[US2][US6]`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: User story served (US1…US6); none for Setup/Foundational/Polish

## Path note

All edits are config files under `.claude/` at repo root. No `src/`. The "behavior inventory" at `specs/010-claude-config-optimization/contracts/behavior-inventory.md` is the loss-prevention gate for every edit.

---

## Phase 1: Setup (Baseline capture)

**Purpose**: Record the before-state so "no loss + no verbosity bloat" is provable afterward.

- [x] T001 [P] Record baseline metrics in a scratch note (commit message or `quickstart.md` run): `wc -l` of the standing-context import set (`CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/skill-routing.md`, `.claude/rules/live-documentation.md`, `.claude/rules/mcp.md` = 146 lines), current intent-line coverage, and the list of authority anchors already named across `.claude/`.
- [x] T002 [P] Establish the green baseline: run the `quickstart.md` §4 spot-checks against the **unmodified** config (`echo '{"tool_input":{"command":"git push -f"}}' | .claude/hooks/pre-bash.sh` → exit 2; `echo '{"prompt":"AKIAIOSFODNN7EXAMPLE"}' | .claude/hooks/user-prompt-submit.sh` → exit 2; `jq empty .claude/settings.json`) and confirm all pass before any edit.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the gate and the de-duplication decision before touching content.

**⚠️ CRITICAL**: No user-story edits begin until T003–T004 are complete.

- [x] T003 Designate `.claude/rules/clarifier.md` as the single canonical clarification source; enumerate every location that currently restates it (`.claude/CLAUDE.md` "Response Preflight", `.claude/skills/clarifier/SKILL.md`) to be converted to cross-references. Records the dedup plan that US2 tasks consume.
- [x] T004 Verify `specs/010-claude-config-optimization/contracts/behavior-inventory.md` is complete against the current `.claude/settings.json` + 6 hook scripts + routing triggers + skill obligations; add any missing enforced item. This frozen list is the post-edit gate.

**Checkpoint**: Gate defined, dedup target chosen — edits may begin.

---

## Phase 3: User Story 1 - Deliberate Memory & Subagent usage (Priority: P1) 🎯 MVP

**Goal**: `.claude/rules/tools.md` gives testable Memory and Subagent guidance, each with an explicit anti-pattern.

**Independent Test**: `quickstart.md` §3 — `tools.md` has a Memory trigger + anti-pattern and a Subagent trigger + anti-pattern.

- [x] T005 [US1] Add an intent line ("Purpose / Applies when") to the top of `.claude/rules/tools.md`.
- [x] T006 [US1] Add a Memory policy to `.claude/rules/tools.md`: write/read only durable cross-session facts (conventions, decisions, key file locations, user preferences); explicit anti-pattern (no transient state, secrets, or trivially re-derivable facts); grounded in the harness's Memory guidance, paired with the existing `autoMemoryEnabled: true` setting (FR-001, SC-003).
- [x] T007 [US1] Sharpen the Subagents section in `.claude/rules/tools.md`: delegation triggers (broad fan-out search, main-context protection, explicit user request) + explicit anti-pattern (never delegate single-file or known-scope work) (FR-002, SC-003).

**Checkpoint**: MVP — Memory/Subagent guidance complete and independently verifiable.

---

## Phase 4: User Story 2 + User Story 6 - Comprehension & Authoritative grounding (Priority: P2)

**Goal**: Every rule and owner skill opens with explicit intent, has only actionable directives (ambiguous ones supplemented), states each shared rule once (cross-referenced), and grounds normative directives in correctly-attributed authority. Per-file pass applies R9 (actionability + grounding) from `research.md`.

**Independent Test**: `quickstart.md` §1 (zero duplication), §2 (intent lines), §8 (actionability, SC-009), §9 (grounding accuracy, SC-010).

> Each task: add intent line, make directives actionable (supplement ambiguous ones, FR-014), remove verbosity, verify/add correctly-attributed anchors (FR-015). `[P]` tasks touch different files.

### Standing context

- [x] T008 [P] [US2][US6] Refresh `.claude/CLAUDE.md`: per-section intent; actionable directives; remove verbosity; convert the "Response Preflight" clarification detail to a cross-reference to `.claude/rules/clarifier.md` (per T003); verify MECE/SCQA/FURPS+/INVEST references are correct and functional. (Note: T020 also edits this file — must run before T020.)
- [x] T009 [P] [US2][US6] Refresh `.claude/rules/skill-routing.md`: add intent line; keep routing triggers verbatim (enforced); confirm each trigger is actionable.
- [x] T010 [P] [US2][US6] Refresh `.claude/rules/live-documentation.md`: add intent line; tighten prose; preserve all five principles + override handling verbatim in effect.
- [x] T011 [P] [US2][US6] Refresh `.claude/rules/mcp.md`: add intent line; keep catalog table + usage rule; ensure the AWS/GCP/Azure routing directive is actionable.

### On-demand rules

- [x] T012 [P] [US2][US6] Refresh `.claude/rules/permissions.md`: add intent line; keep every deny/ask/allow rule; ground the evaluation order in least-privilege (deny → ask → allow).
- [x] T013 [US2][US6] Make `.claude/rules/clarifier.md` the canonical clarification source: add intent line; ensure directives actionable; ground in ISO/IEC/IEEE 29148 (requirement quality), INVEST, Gherkin, MoSCoW, FURPS+, SMART with correct attribution; absorb any unique content from `.claude/CLAUDE.md` preflight (depends on T003, T008).
- [x] T014 [P] [US2][US6] Refresh `.claude/rules/advisor.md`: add intent line; trim; verify anchors (one-way/two-way door, pre-mortem, Fermi, MECE, SCQA) are real and functional.

### Owner skills

- [x] T015 [P] [US2][US6] Refresh `.claude/skills/coder/SKILL.md`: body intent line; actionable directives; verify OWASP Top 10 / OWASP ASVS / CWE anchors; preserve TDD/SDD/docs-sync/no-drive-by obligations.
- [x] T016 [P] [US2][US6] Refresh `.claude/skills/editor/SKILL.md`: body intent line; verify Pyramid (Minto)/MECE/SCQA/BLUF/Tufte/Cleveland–McGill/Strunk & White anchors; trim.
- [x] T017 [US2][US6] Refresh `.claude/skills/clarifier/SKILL.md`: body intent line; cross-reference `.claude/rules/clarifier.md` and remove duplicated trigger prose (per T003); keep the formal elicitation toolbox; verify anchors (depends on T013).
- [x] T018 [P] [US2][US6] Refresh `.claude/skills/domain-model/SKILL.md`: body intent line; make directives actionable; trim toward ≤200 lines where loss-free; verify DDD anchors (Evans/Fowler patterns) are correctly attributed.
- [x] T019 [P] [US2][US6] Refresh `.claude/skills/ubiquitous-language/SKILL.md`: body intent line; actionability; trim; verify the DDD ubiquitous-language anchor.

**Checkpoint**: All rules/skills are intent-explicit, actionable, de-duplicated, and grounded.

---

## Phase 5: User Story 3 - Internal design→plan→task discipline without Spec Kit (Priority: P3)

**Goal**: Non-trivial non-Spec-Kit tasks pass through an internal approach→plan→task-breakdown phase, scaled down for trivial tasks.

**Independent Test**: `quickstart.md` §6 — non-trivial request gets the phase; trivial request does not.

- [x] T020 [US3] Add a "Pre-execution discipline" subsection to `.claude/CLAUDE.md` Response Preflight: for non-trivial tasks (multi-file, new/changed behavior, or irreversible) internally state approach → short plan → task breakdown before editing, reusing the clarifier (scope) and advisor (options/recommendation) scaffolding; trivial tasks (single-file, reversible, ≤1 logical step) skip the ceremony; state the threshold in testable terms (FR-006, FR-007, SC-006). Depends on T008 (same file).

**Checkpoint**: Internal planning discipline encoded without adding a new import or framework.

---

## Phase 6: User Story 4 - Optimized hook configuration (Priority: P4)

**Goal**: Each hook has a stated purpose and correct wiring; safety-guard logic is frozen; scripts are consistent and lint-clean.

**Independent Test**: `quickstart.md` §4 — all hooks executable & lint-clean, `settings.json` valid, guard spot-checks still exit 2.

- [x] T021 [P] [US4] Set executable bit `0755` on `.claude/hooks/pre-edit.sh` and `.claude/hooks/post-edit-format.sh` (currently `0644`).
- [x] T022 [P] [US4] Verify/append a one-line purpose header comment on each of the six hook scripts in `.claude/hooks/`; do not alter any guard logic.
- [x] T023 [US4] Review `.claude/settings.json` hook wiring (matchers, timeouts) and permission lists for correctness; make no semantic change; validate with `jq empty .claude/settings.json`.
- [x] T024 [US4] Run `shfmt -i 2 -w` and `shellcheck` on all `.claude/hooks/*.sh`; confirm clean; confirm `pre-bash.sh` and `user-prompt-submit.sh` guard behavior is unchanged vs the T002 baseline (SC-004).

**Checkpoint**: Hooks lean, documented, executable, and safety guards provably intact.

---

## Phase 7: User Story 5 - Documentation redesigned to best practice (Priority: P5)

**Goal**: The refreshed config docs satisfy the repo's own Live Documentation principles.

**Independent Test**: `quickstart.md` §7 — audit finds zero unresolved violations.

- [x] T025 [US5] Audit refreshed `.claude/CLAUDE.md`, `.claude/rules/*`, and owner skills against `.claude/rules/live-documentation.md` (proximity, no redundancy, explicit intent, auto-generation preference); fix any violation found.
- [x] T026 [US5] Verify the `CLAUDE.md` import chain: each imported file is focused and ≤200 lines (SC-008); confirm every cross-reference added in Phase 4 resolves to an existing heading/path.

**Checkpoint**: Documentation consistent and principle-compliant.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Prove the success criteria end-to-end and ship.

- [x] T027 Re-run the full behavior inventory (`quickstart.md` §4 and §5) against the edited config; confirm zero enforced-behavior loss across permissions, hook guards, and routing triggers (SC-002, SC-004).
- [x] T028 [P] Run the actionability review (`quickstart.md` §8, SC-009) and grounding-accuracy audit (`quickstart.md` §9, SC-010); remove or fix any vacuous directive, fabricated, misattributed, or decorative-only anchor.
- [x] T029 [P] Compute the net standing-context delta vs the T001 baseline; record a one-line reason for each net addition; confirm verbosity-driven length fell and no duplication remains (SC-002).
- [x] T030 Update `specs/010-claude-config-optimization/checklists/requirements.md` status and run `quickstart.md` §1–§9 end-to-end as the final acceptance pass.
- [x] T031 Commit and push all `.claude/` config changes to `claude/speckit-claude-code-settings-lrldfc`.

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (P1)** → no deps.
- **Foundational (P2: T003–T004)** → after Setup; **blocks all edits**.
- **US1 (P3 phase)** → after Foundational. MVP.
- **US2+US6 (P4 phase)** → after Foundational; independent of US1 (different files; US1 owns `tools.md`).
- **US3 (P5 phase)** → T020 depends on T008 (same file `.claude/CLAUDE.md`).
- **US4 (P6 phase)** → after Foundational; independent of content phases (hooks/settings).
- **US5 (P7 phase)** → after US2+US6 and US3 (audits their output).
- **Polish (P8)** → after all desired stories.

### Key intra-phase dependencies

- T013 depends on T003 (dedup target) and T008 (absorb preflight content).
- T017 depends on T013 (cross-reference target finalized).
- T020 depends on T008 (edits same file after the comprehension pass).

### Parallel opportunities

- T001, T002 together.
- Phase 4: T008, T009, T010, T011, T012, T014, T015, T016, T018, T019 are all `[P]` (distinct files). T013 and T017 are sequential within the clarification chain.
- Phase 6: T021, T022 together (then T023, T024).
- Phase 8: T028, T029 together.

---

## Parallel Example: Phase 4 (Comprehension & grounding)

```bash
# Distinct files — safe to run together:
Task: "Refresh .claude/rules/skill-routing.md (T009)"
Task: "Refresh .claude/rules/live-documentation.md (T010)"
Task: "Refresh .claude/rules/mcp.md (T011)"
Task: "Refresh .claude/rules/permissions.md (T012)"
Task: "Refresh .claude/rules/advisor.md (T014)"
Task: "Refresh .claude/skills/coder/SKILL.md (T015)"
Task: "Refresh .claude/skills/editor/SKILL.md (T016)"
Task: "Refresh .claude/skills/domain-model/SKILL.md (T018)"
Task: "Refresh .claude/skills/ubiquitous-language/SKILL.md (T019)"
# Then sequentially: T013 (clarifier.md canonical) → T017 (clarifier skill cross-ref)
```

---

## Implementation Strategy

### MVP first

1. Setup (T001–T002) → 2. Foundational (T003–T004) → 3. US1 (T005–T007) → **STOP & validate** `quickstart.md` §3. Memory/Subagent guidance is a shippable increment.

### Incremental delivery

US1 (MVP) → US2+US6 (the comprehension/grounding backbone, largest value) → US3 (internal planning) → US4 (hooks) → US5 (doc audit) → Polish. Each phase is independently verifiable via its `quickstart.md` section; commit after each phase.

### Notes

- `[P]` = different files, no incomplete dependency.
- Comprehension outranks compression: never drop content the model needs; record any net-length increase with a reason (T029).
- Re-run the behavior-inventory gate (T027) before claiming done — zero enforced-behavior loss is mandatory.
- Commit after each phase or logical group; final push in T031.
