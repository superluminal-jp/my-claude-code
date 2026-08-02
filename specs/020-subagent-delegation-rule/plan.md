# Implementation Plan: A grounded rule for when to delegate work to a subagent

**Branch**: `020-subagent-delegation-rule` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/020-subagent-delegation-rule/spec.md`

## Summary

Add `.claude/rules/subagent-delegation.md` — an always-on rule stating when work is delegated to a subagent and when it stays in the main conversation, derived from and cited to the official Claude Code documentation. Import it from `.claude/CLAUDE.md`, narrow the existing "Execution" section so the two do not overlap, and record the rule as intentionally not ported to Codex.

## Technical Context

**Language/Version**: Markdown. No code.

**Primary Dependencies**: None at runtime. `jq` for the sync suite.

**Storage**: N/A.

**Testing**: `tests/run-subagent-delegation.sh` (new, deterministic) plus the existing suites, chiefly `tests/run-codex-sync.sh` for SYNC-08.

**Target Platform**: Claude Code sessions in this repository and, via `install.sh`, at user scope.

**Project Type**: Agent-configuration repository.

**Performance Goals**: N/A. The relevant budget is always-loaded instruction size — the rule is held to roughly the size of the existing mid-sized rules (`skill-routing.md` is 3.6 KB, `clarifier.md` 4.6 KB), not the largest (`live-documentation.md` at 9.0 KB).

**Constraints**: Always-loaded, so terse. Every behavioural claim must be citable (research R3). SYNC-08 requires a deployment-map row.

**Scale/Scope**: 1 new rule, 1 new test suite, ~5 documents touched.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unmodified Spec Kit template — all principles are `[PRINCIPLE_N_NAME]` placeholders. **No project-specific constitutional gate applies.** Governing rules:

| Gate | Source | Status |
|---|---|---|
| Failing test before implementation | `coder` (TDD) | Planned as T001, before the rule is written |
| Spec is the source of truth | `coder` (SDD) | ✅ spec written first |
| Claims grounded in verifiable sources | `.claude/CLAUDE.md` Core Principle 1 | ✅ research R3 maps every claim to source text |
| Docs updated in the same change | `rules/live-documentation.md` §1 | Planned — inventory updates are in Phase 3 |
| Proximity | `rules/live-documentation.md` §4 | ✅ the rule sits in `.claude/rules/`, alongside the rules it composes with |
| No redundancy | `rules/live-documentation.md` §5 | ✅ research R2 resolves the overlap with `.claude/CLAUDE.md` § Execution |
| Auto-generation preferred | `rules/live-documentation.md` §3 | N/A — prose guidance has no generation path |
| One-way-door decisions recorded | `adr` skill | Assessed in D3 below |

**Post-design re-check**: no new gate triggered; see [§ Constitution re-check](#constitution-re-check).

## Project Structure

### Documentation (this feature)

```text
specs/020-subagent-delegation-rule/
├── spec.md
├── research.md          # R1 placement, R2 overlap, R3 claim-to-source map, R4 citation form, R5 parity
├── plan.md              # This file
└── tasks.md
```

No `contracts/` or `data-model.md` — no data entities, no new inter-component contract.

### Source (repository root)

```text
.claude/
├── rules/subagent-delegation.md   # NEW — the rule
└── CLAUDE.md                      # @-import + narrowed Execution section

.codex/README.md                   # deployment-map row (対象外, SYNC-08)
README.md, README.ja.md            # rules inventory
tests/run-subagent-delegation.sh   # NEW deterministic suite
```

**Structure Decision**: `.claude/rules/` is the documented home for always-applicable, cross-cutting instructions in this repository; research R1 records why `.claude/CLAUDE.md`, a skill, and the `coder` skill were each rejected.

## Key design decisions

### D1. The rule is decision criteria, not documentation of the feature

It answers "should this work run here or elsewhere, and by which mechanism" and stops. It does not explain what a subagent is, enumerate frontmatter fields, or reproduce tool lists. Rationale in research R3: version-gated specifics go stale, and this file pays its cost on every turn.

### D2. `.claude/CLAUDE.md` gains an import and one narrowing edit, not the guidance

The existing § "Execution: parallelize whenever valid" keeps ownership of *how to issue* independent calls; the new rule owns *whether to delegate at all*. Without this edit the two files would both speak to subagent launches, which `rules/live-documentation.md` §5 forbids.

### D3. No ADR

Assessed against the `adr` skill's three-part test: architecturally significant — marginal; hard to reverse — no, deleting one file and one import line restores the prior state; a reasonable alternative rejected — yes (research R1). Two of three fail. The rationale lives in `research.md`.

### D4. Codex parity is a `対象外` row, not a port

Codex CLI has no subagent mechanism to map onto. The deployment map's legend requires a stated reason for `対象外`, which is supplied. This is the honest record; inventing a partial Codex analogue would be worse than declaring the gap.

## Phasing

- **Phase 1 — Test.** Write `tests/run-subagent-delegation.sh`; confirm red.
- **Phase 2 — Rule.** Author `.claude/rules/subagent-delegation.md`; import it; narrow § Execution.
- **Phase 3 — Parity and inventory.** `.codex/README.md` row; README rules inventories.
- **Phase 4 — Verification.** Full suite run; working tree check.

## Constitution re-check

Re-checked after the design. No gate newly triggered. D3 records the ADR assessment; D2 records the redundancy resolution; research R3 satisfies the grounding principle by mapping each claim to its source before the rule is written rather than after.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

No violations.

## Out of scope

- Encoding version-gated behaviour (spawn-limit values beyond their existence, environment-variable names, background tool lists). Named in research R3 as deliberately excluded.
- Revisiting whether any *existing* skill should become a subagent. That analysis was delivered in conversation and acted on for one case in feature 019; this feature records the general rule only.
- The pre-existing drift items flagged in `specs/019-verify-fork-test-runner/plan.md` § Out of scope, which remain open.
