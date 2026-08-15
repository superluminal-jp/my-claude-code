# Implementation Plan: Minimize scrum-master Skill to Official Scrum Guide Content

**Branch**: `022-minimize-scrum-master-skill` | **Date**: 2026-08-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/022-minimize-scrum-master-skill/spec.md`

## Summary

Strip `.claude/skills/scrum-master/` down to content traceable solely to the official Scrum Guide (2020). Delete the four reference files and the one script whose content is sourced entirely from supplementary frameworks/research (Nexus, LeSS, SAFe, Scrum@Scale, EBM, Kanban Guide, DORA, psychological-safety research, Agile Retrospectives, Coaching Agile Teams, Scrum.org/Agile Alliance anti-pattern material); trim `sources.md` to a single `[SG20]` entry and `scrum-master-role.md` to drop its non-Guide coaching-stance taxonomy; rewrite `SKILL.md` so its routing table, principles, and workflow instructions only ever point at what still exists, and so out-of-scope questions get an explicit decline rather than an answer drawn from deleted material (research.md Decision 1–2). Because `scripts/flow_metrics.py` is one of the deletions, this also requires updating three files `spec.md` doesn't name individually — `README.md` (drops the "flow metrics" capability line and the now-inaccurate file-tree/reference-count description), `.claude/settings.json` (drops the two now-dead permission entries scoped to that script), and the test suite that exercises it (`tests/run-flow-metrics.sh`, `tests/test_flow_metrics.py`) — captured as Decision 3 in `research.md` and required by this repository's Live Documentation rule, not by new scope.

## Technical Context

**Language/Version**: N/A — no new source code is authored. `scripts/flow_metrics.py`, the only code file in scope, is deleted rather than modified.

**Primary Dependencies**: N/A.

**Storage**: N/A — flat Markdown/Python/JSON files only.

**Testing**: `tests/skill-routing/007-scrum-facilitation.md` (run via `tests/run-skill-routing.sh`) must keep passing unchanged. `tests/run-flow-metrics.sh` and `tests/test_flow_metrics.py` are deleted (research.md Decision 3). `.claude/settings.json` must remain valid JSON after edits. `spec.md`'s SC-001–SC-005 are verified via the grep/find commands in `quickstart.md`, not a new automated test.

**Target Platform**: Claude Code (and Codex CLI via the existing mirror described in ADR 0003) skill file system, within this repository only — ADR 0003 already established this repo as the sole source of truth with no external sync surface.

**Project Type**: Single — documentation/skill-content package edited in place; no src/tests application split applies.

**Performance Goals**: N/A.

**Constraints**: Must not alter `when_to_use` / skill-routing triggers (spec.md Assumptions). Must leave zero dead relative links inside the skill (FR-009) and zero dead references in `README.md`/`.claude/settings.json`/`tests/` (research.md Decision 3). Must not edit `docs/adr/0003-vendor-scrum-master-skill.md` (research.md Decision 4 — Accepted ADRs are never rewritten).

**Scale/Scope**: ~10 files deleted, 4 files trimmed/rewritten in the skill directory, 2 files trimmed outside it. Full inventory: `data-model.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template — every field is still a `[PLACEHOLDER]` and it has never been ratified (no version, no ratification date). There are no project-specific gates to evaluate against. This feature instead observes the repository's globally-applicable rules directly (not gated through the constitution file): `.claude/rules/live-documentation.md` (Drift Detection — motivates the `README.md` update in Decision 3) and `.claude/rules/permissions.md` (least privilege — motivates removing the dead `flow_metrics.py` permission entries). No violations identified; no entries needed in Complexity Tracking.

**Post-Phase-1 re-check**: Unchanged. Phase 1 design (data-model.md, quickstart.md) introduced no new dependency, service, or architectural layer that a constitution gate would apply to — it only enumerated the same file-level deletions/edits already scoped in Phase 0. Gate still passes vacuously.

## Project Structure

### Documentation (this feature)

```text
specs/022-minimize-scrum-master-skill/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── checklists/
│   └── requirements.md  # Spec quality checklist (/speckit-specify command)
└── tasks.md              # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` directory is generated: this feature has no external API, CLI schema, or service endpoint. The skill's only "interface" toward the rest of the repository — its `SKILL.md` frontmatter (`name`, `description`, `when_to_use`) that `.claude/rules/skill-routing.md` and the routing regression suite depend on — is explicitly unchanged by this feature (spec.md Assumptions), so there is no contract surface to document. The file-level inventory that would otherwise live in `contracts/` is instead captured in `data-model.md`, which is the more accurate shape for a content-deletion feature.

### Source Code (repository root)

```text
.claude/skills/scrum-master/
├── SKILL.md                              # rewrite — routing table, principles, workflow rescoped
├── references/
│   ├── 2020-Scrum-Guide-US.pdf           # unchanged — sole normative source
│   ├── 2020-Scrum-Guide-Japanese.pdf     # unchanged — sole normative source
│   ├── sources.md                        # trim — single [SG20] entry only
│   ├── scrum-framework.md                # trim — gains 3 quotes folded in from event-playbooks.md
│   ├── scrum-master-role.md              # trim — コーチングスタンス section removed
│   ├── event-playbooks.md                # DELETE
│   ├── measurement-and-diagnostics.md    # DELETE
│   ├── anti-patterns-and-coaching.md     # DELETE
│   └── scaling-frameworks.md             # DELETE
└── scripts/
    ├── flow_metrics.py                   # DELETE
    └── __pycache__/                      # DELETE

README.md                                 # trim — flow-metrics capability line, file-tree row,
                                           #   reference-doc count, post-change test instruction
.claude/settings.json                     # trim — remove 2 dead flow_metrics.py permission entries
tests/run-flow-metrics.sh                 # DELETE
tests/test_flow_metrics.py                # DELETE
tests/__pycache__/test_flow_metrics.cpython-314.pyc  # DELETE
```

**Structure Decision**: This is an in-place content edit to an existing skill package plus three small, necessary edits to repository-root files that describe or depend on what's being deleted (research.md Decision 3). No new directories are created; no build/src/tests scaffolding applies, since the "source" being changed is the skill's own Markdown/PDF/Python content rather than an application.

## Complexity Tracking

*No entries — Constitution Check identified no violations to justify.*
