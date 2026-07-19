# Implementation Plan: Cross-Agent Guardrail & Rule Migration Decision Record

**Branch**: `012-cross-agent-guardrail-migration` | **Date**: 2026-07-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-cross-agent-guardrail-migration/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Walk the maintainer through all 14 Claude Code-specific hooks/rules identified in prior investigation, one at a time, and record a migration verdict for each (unify into `AGENTS.md` at full or reduced strength, reimplement natively per tool, migrate to a non-agent-level control, or keep Claude Code-only). All 14 verdicts were already elicited and recorded in `spec.md`'s `## Clarifications` section via `/speckit-clarify`. This plan's remaining work is to consolidate that already-decided content into a single, standalone, reader-friendly decision record — no source code, hook scripts, or `AGENTS.md` content is produced.

## Technical Context

**Language/Version**: N/A — no source code is produced by this feature

**Primary Dependencies**: N/A

**Storage**: A single Markdown file (the decision record); no database or persistent state

**Testing**: N/A — no automated tests; validation is a manual read-through against the spec's Success Criteria (SC-001–SC-004) and the quickstart checklist below

**Target Platform**: N/A — the deliverable is documentation, read by humans (and, secondarily, by a future implementation-phase agent)

**Project Type**: Documentation / decision record (not a software system)

**Performance Goals**: N/A

**Constraints**: The record must not contain implementation artifacts (FR-008); every per-tool-asymmetric verdict must be labeled per tool (FR-007, SC-003)

**Scale/Scope**: 14 migration items, single output file, one authoring pass (no iteration loop expected — content already finalized during clarification)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template (placeholder principles only — `[PRINCIPLE_1_NAME]` etc. have never been replaced with real project principles). No project-specific gates are defined, so there is nothing to check this plan against. **Gate: PASS (vacuously — no constitution to violate).**

## Project Structure

### Documentation (this feature)

```text
specs/012-cross-agent-guardrail-migration/
├── spec.md               # Feature spec + Clarifications (14 Q&A, all verdicts recorded)
├── plan.md               # This file (/speckit-plan command output)
├── research.md           # Phase 0 output — confirms no unresolved unknowns
├── data-model.md          # Phase 1 output — Migration Item / Decision Verdict / Decision Record entities
├── quickstart.md          # Phase 1 output — how to validate the decision record
├── checklists/
│   └── requirements.md    # Spec quality checklist (16/16 passing)
└── decision-record.md     # The feature's actual deliverable (produced in /speckit-implement or a direct authoring pass)
```

No `contracts/` directory: this feature exposes no API, CLI, or schema to other systems or users — the sole interface is the Markdown file itself, read directly by a human. Per the Phase 1 instructions ("skip if project is purely internal"), contract generation is skipped.

### Source Code (repository root)

Not applicable — this feature does not touch `src/`, `tests/`, or any application code. The only repository paths involved are under `specs/012-cross-agent-guardrail-migration/`.

**Structure Decision**: Single documentation artifact (`decision-record.md`) co-located with its spec under `specs/012-cross-agent-guardrail-migration/`, consistent with this feature's own Assumptions ("does not modify the repository's live `.claude/` configuration").

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
