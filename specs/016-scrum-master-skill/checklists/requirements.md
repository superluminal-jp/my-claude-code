# Specification Quality Checklist: Integrate the `scrum-master` skill into the shared skill set

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-25
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- **Iteration 1 (2026-07-25)**: All items pass except the [NEEDS CLARIFICATION] check. Two markers remain, both genuine scope forks with no safe default:
  - **FR-007** — routing tier: always-loaded mandatory routing list vs. routing-rules file only. Changes which files are touched and how aggressively the skill triggers.
  - **FR-021** — provenance: this repo as sole source of truth vs. the external directory staying upstream. The second reading adds drift-detection tooling to scope; the first adds nothing.
- Both are surfaced to the user as Q1/Q2 rather than guessed, per the max-3-marker rule and the scope-first prioritisation.
- Two revisions applied during iteration 1 before recording results:
  - Fixed "Requirements are testable and unambiguous": FR-014/FR-015 originally said the helper "should be runnable"; restated as observable conditions (no ad-hoc prompt, no guardrail block, permission scoped to the single script).
  - Fixed "Success criteria are measurable": SC-001 originally read "routes correctly"; restated with a verification count and the three prompt categories it must cover.
- **Iteration 2 (2026-07-25)**: Both questions answered by the user; all items now pass.
  - **FR-007** → mandatory routing list. Resolved into FR-007 plus a new **FR-007a**: because the trigger surface is now wider, the routing rules must draw an explicit boundary against adjacent non-Scrum project-management work. **SC-009** was added to make that boundary verifiable.
  - **FR-021** → this repository is the sole source of truth. Resolved into FR-021 plus a new **FR-022** stating the negative scope: no sync mechanism, no drift-detection test. An assumption was added noting that deleting the external directory is the user's call, outside this repo.
- Final counts: 23 functional requirements, 9 success criteria, 3 prioritised user stories, 6 edge cases.
- **Status: PASS** — ready for `/speckit-plan`. `/speckit-clarify` is not required; both open questions were resolved in this command.
- **Iteration 3 (2026-07-25, post-`/speckit-analyze`)**: cross-artifact analysis found 11 issues, 0 critical. All actionable ones applied:
  - **I1 (HIGH)** — `tasks.md` T006 told the implementer to write a skill-directory-relative command while T013 granted a repo-root-relative permission. The two would never have matched, surfacing as a confusing prompt at T016. Both tasks now pin the same two literal strings, and contract C7 gained the general rule.
  - **I2** — spec, plan, and tasks disagreed on language coverage. **SC-001 changed from "either" to both languages** and now requires four probes; an English probe was added as quickstart 4d and T015 4d, and plan.md's risk row was aligned.
  - **C1** — SC-003's "clean profile" was unverifiable without wiping the user's `~/.claude`. Restated as "after one installer run", with the `rm -rf`-then-`cp -R` equivalence noted.
  - **C2** — **FR-021 gained a durability clause**, discharged by new task T036 proposing `docs/adr/0003-vendor-scrum-master-skill.md`. This also satisfies the one-way-door ADR obligation in `.claude/CLAUDE.md`'s close-out rules, which was otherwise unmet.
  - **I3** — US3 was not independently testable as spec claimed. The nine-file cross-story sweep moved out of T029 into new Polish task T035; T029 now checks only US3's own five files.
  - **C3** — SC-006 had no verification; folded into T029.
  - **C4** — US2's fourth acceptance scenario is about the *installed* copy; T020 and quickstart step 5 now re-run the link check there.
  - **C5** — the guardrail was verified against a hypothetical path only; T016 and quickstart step 4 now re-check the final command form.
  - **U1** — T023's approximate line numbers replaced with literal string anchors.
  - **D1** (FR-021/FR-022 mild redundancy) and **N1** (constitution is an unfilled template) accepted as-is; N1 is out of this feature's scope.
- Task count: 34 → 36 (T035, T036 added). Success criteria unchanged at 9; FR count unchanged at 23.
