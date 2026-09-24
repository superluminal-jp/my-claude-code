# Tasks: Model and Effort Routing Rule

**Input**: Design documents in `specs/040-model-routing-rule/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/rule-file-contract.md](./contracts/rule-file-contract.md), [quickstart.md](./quickstart.md)

**Organization**: Tasks are grouped by user story. Stories US1–US3 are successive sections of one file, so they run in sequence; only the documentation and mirror tasks in US4 run in parallel.

**Test-first**: The structure check is an automated contract, so it changes before the rule exists (Phase 2) and must be seen failing (T003) before the rule file is created. The behavioral criteria (SC-001) are a manual read-through, as the plan states.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1–US4 (none for Setup, Foundational, Polish)

## Path Conventions

Paths are relative to the repository root.

## Constraints for every task

- Do not edit the five existing rule files, `.claude/CLAUDE.md`, any skill, `install.sh`, `docs/adr/`, or `specs/001`–`039` (FR-016).
- The new rule file must contain no `.claude/`, `rules/`, `skills/`, `SKILL.md`, `settings.json`, `.mcp.json`, `/speckit-*`, authored-skill name in backticks, or sibling rule filename (FR-011).
- Do not add a tier, escalation condition, or effort level beyond the draft `/Users/taikiogihara/Downloads/model-routing.md` (SC-005).

---

## Phase 1: Setup

- [X] T001 Record the pre-change baseline: run `bash tests/run-config-pyramid.sh` and `bash tests/run-install.sh` on the unmodified branch and note that both pass with five rules (source: quickstart §1).

---

## Phase 2: Foundational (blocks all user stories)

- [X] T002 In `tests/run-config-pyramid.sh`, change RULE-01 to expect the six sorted names (`clarifier.md`, `live-documentation.md`, `model-routing.md`, `permissions.md`, `pyramid-principle.md`, `thinking-lenses.md`) and rename it "exactly six universal rule files"; add `RULE-11: routing owns capability tiers and effort` using `check_contains` on `$RULE_DIR/model-routing.md` with pattern `tier|capabilit|effort`, placed after RULE-10 (contract §3).
- [X] T003 Run `bash tests/run-config-pyramid.sh` and confirm RULE-01 and RULE-11 fail and nothing else regresses. This is the red step; record the output.
- [X] T004 [P] Check the aliases `fable`, `opus`, `sonnet`, `haiku` against the official Claude Code model configuration documentation. Record the result and source URL in `specs/040-model-routing-rule/research.md` under D9. If any alias differs, stop and report to the user instead of changing the draft's substance.

**Checkpoint**: The check fails for the right reason and the aliases are confirmed or the discrepancy is reported.

---

## Phase 3: User Story 1 — The agent picks the cheapest sufficient model and effort (P1)

**Goal**: A session loads a rule that maps each unit of work to a tier and effort by the stated basis.

**Independent Test**: With only the rule file, the four sample units in the spec's US1 test resolve to `haiku`/low, `sonnet`/medium, `opus`/high, `fable`/high-or-above.

- [X] T005 [US1] Create `.claude/rules/model-routing.md` with the title `# Model and Effort Routing`, the purpose paragraph (lowest capability and effort that reliably completes each independent unit; route by required judgment, ambiguity, dependency breadth, blast radius, not size alone), and a `## Capability tiers` section holding the four-row table (tier · alias · use when) plus the line "decide → higher capability; implement → balanced; execute mechanically → efficient" (FR-001–005; data-model.md tier table).

---

## Phase 4: User Story 2 — Escalation and hand-back are bounded (P1)

**Goal**: The rule closes the set of escalation triggers and returns bounded work to lower tiers.

**Independent Test**: A reviewer answers "do not escalate / escalate / hand back" correctly for the three scenarios in the spec's US2 test.

- [X] T006 [US2] In `.claude/rules/model-routing.md`, add `## Escalation and hand-back`: escalate only when the current tier cannot determine correct behavior, meets semantic ambiguity, needs an architectural trade-off, or fails for reasoning-related reasons; size or repetition alone directs to decomposition or parallelization; after a higher tier resolves the uncertain part, hand bounded implementation, verification, and cleanup back to a lower tier where practical (FR-006–008).

---

## Phase 5: User Story 3 — Delegation sets model and effort deliberately (P2)

**Goal**: The rule treats capability and effort as separate controls and governs subagent use.

**Independent Test**: A reader decides "direct" for a trivial single-file edit and "subagents, `haiku`/low" for three independent parallel searches.

- [X] T007 [US3] In `.claude/rules/model-routing.md`, add `## Effort and delegation`: capability and effort are separate controls; the five levels with `medium` as the ordinary default; `xhigh`/`max` only where the hardest reasoning is materially useful and the model supports them; choose a subagent's model and effort deliberately; prefer direct execution for trivial sequential or single-file work; use subagents for independent, parallelizable, or context-isolated work. End the file with one closing sufficiency sentence. Add a `## References` section only if T004 confirmed the aliases against an official source, citing it (FR-009, FR-010, FR-012; research D2, D4).
- [X] T008 [US3] Run `bash tests/run-config-pyramid.sh` and confirm RULE-01 through RULE-04 and RULE-11 now pass. This is the green step. Also confirm the file is at most 40 lines.

**Checkpoint**: The rule is complete and passes the structure check.

---

## Phase 6: User Story 4 — The new rule fits the rule layer and the docs stay true (P2)

**Goal**: The Japanese mirror and every artifact that counts or lists the rules agree with six rules.

**Independent Test**: The full check and the stale-count search (quickstart §1, §3) both pass.

- [X] T009 [P] [US4] Create `.claude-ja/rules/model-routing.md` with the same six elements in the same order as the English file: English headings each followed by a full-width-parenthesis Japanese gloss, Japanese body, aliases and effort names unchanged (FR-015; contract §2; pattern: `.claude-ja/rules/thinking-lenses.md`).
- [X] T010 [P] [US4] In `README.md`, change the `rules/` tree comment from "5 independent concerns" to 6, add a `model-routing.md` line with a one-line purpose in the tree, and add the routing concern to the `.claude/rules/` paragraph that enumerates the concerns (FR-014).
- [X] T011 [P] [US4] In `README.ja.md`, add the routing concern to the `.claude/rules/` paragraph that enumerates the concerns, in Japanese (FR-014).
- [X] T012 [P] [US4] In `docs/claude-config-design.md`, change §3.1's heading from 5つ to 6つ; add a `model-routing.md` row recording what the rule deliberately leaves out (model IDs, prices, limits, and the syntax for setting model or effort → harness and vendor model documentation); change §5's "5個のユニバーサルルール" and the layer table's `（5件）` to six (FR-014; research D6, D8).

---

## Phase 7: Polish and verification

- [X] T013 Run every offline suite: `bash tests/run-config-pyramid.sh`, `bash tests/run-install.sh`, `bash tests/run-removed-guardrails.sh`, `bash tests/run-digital-agency-frontend-skill.sh`, `bash tests/run-digital-agency-slides-skill.sh`. Report each result; report `tests/run-mcp-startup.sh` as not run (needs network) unless it is run.
- [X] T014 Run the non-regression diff and stale-count search from quickstart §2 and §3; both must produce no output.
- [X] T015 Complete the manual read-through (quickstart §4, 9 of 9) and mirror check (quickstart §6); record results in `specs/040-model-routing-rule/quickstart.md` or the completion report.
- [X] T016 Update `specs/040-model-routing-rule/spec.md` **Status** from Draft to Implemented and confirm every checklist item in `checklists/requirements.md` still passes.

---

## Dependencies and execution order

- Phase 1 → Phase 2 → Phases 3–5 → Phase 6 → Phase 7.
- T003 (red) must complete before T005 (create the rule).
- T004 has no dependency and may run alongside T002–T003, but its result gates T007's References decision.
- T005 → T006 → T007 → T008 (same file, sequential).
- T009–T012 depend on T007 (final English content) and are independent of each other.
- Phase 7 depends on all earlier tasks.

## Parallel opportunities

- T004 alongside T002–T003.
- T009, T010, T011, T012 together once T007 is done (four different files).

## Implementation strategy

**MVP**: Phases 1–5 (T001–T008) deliver the working English rule with a passing structure check. Do not stop there: until Phase 6 the docs still say five and the mirror lacks the file, which violates FR-014 and FR-015.

**Delivery**: Complete in order; commit after Phase 5 and after Phase 6 if incremental commits are wanted (the git commit hooks are optional and need your go-ahead).
