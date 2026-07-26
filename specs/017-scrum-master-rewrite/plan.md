# Implementation Plan: Restructure `scrum-master` into a citation-grounded pure Scrum Master playbook

**Branch**: `017-scrum-master-rewrite` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/017-scrum-master-rewrite/spec.md`

## Summary

`scrum-master`'s `SKILL.md` and its nine `references/*.md` files already carry a source-tag system (`[SG20, p.X]` etc.) and a four-tier evidence hierarchy in `sources.md`, but many normative sentences cite a source without quoting it, several explanations are restated verbatim across two or three files, and the evidence tier of a claim is only discoverable by cross-checking `sources.md`. The rewrite (a) adds a short, verified direct quotation to every Scrum Guide-defined claim and every complementary-source claim, sourced by directly reading the primary documents the user supplied locally rather than from memory; (b) removes or relabels sentences that assert fact without any citation or stance label; (c) consolidates each duplicated explanation into one canonical file, converting the other occurrences into links; and (d) makes each section's evidence tier legible at the point of the claim. Frontmatter, routing rules, distribution tooling, and `scripts/flow_metrics.py` are untouched.

## Technical Context

**Language/Version**: N/A — Markdown content (skill playbook + reference docs), no source code produced or changed except the existing `scripts/flow_metrics.py`, which this feature does not modify.

**Primary Dependencies**: The skill's existing `references/sources.md` source-tag registry; the locally supplied primary-source corpus at `/Users/taikiogihara/Downloads/scrum_official_docs/` (Scrum Guide 2020, Nexus Guide 2021, Kanban Guide 2021, EBM Guide 2024, Scrum@Scale Guide, Agile Manifesto JA, Scrum Guide Expansion Pack) — read directly via the Read tool (PDF support) to verify every quotation and page number before it is written.

**Storage**: N/A (flat Markdown files under `.claude/skills/scrum-master/`).

**Testing**: Existing routing regression suites (`tests/run-skill-routing.sh`, `tests/skill-routing/007-scrum-facilitation.md`, `tests/run-codex-sync.sh`) must continue to pass unchanged (FR-012). This feature adds no new automated test — verification is manual sampling against the quickstart checklist (SC-001–SC-008), since citation/quotation correctness cannot be asserted by a script without re-deriving the same judgment a human reviewer makes.

**Target Platform**: Claude Code / Codex skill runtime that loads `SKILL.md` and `references/*.md` as Markdown at conversation time; no build step.

**Project Type**: Skill content / documentation rewrite (not a software feature with an API or UI).

**Performance Goals**: N/A.

**Constraints**: Must not alter `SKILL.md` frontmatter (`name`, `description`, `when_to_use`), `.claude/rules/skill-routing.md`, distribution mechanisms (installer), or `scripts/flow_metrics.py` and its declared permission (FR-010, FR-011). Quotations must stay short (a phrase/clause) per `sources.md`'s existing minimal-quotation rule and copyright considerations (FR-003).

**Scale/Scope**: 9 files, ~863 lines / ~9,000 words today (`SKILL.md` + 8 reference files + `sources.md`); target is a net reduction in combined word count (SC-005) with the same routing-table coverage.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled template (`[PROJECT_NAME] Constitution` with bracketed placeholders) — no ratified project principles exist yet in this repository. There is nothing to check against, so this gate passes trivially. No new principle is being proposed as part of this feature.

## Project Structure

### Documentation (this feature)

```text
specs/017-scrum-master-rewrite/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── citation-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/speckit-tasks command — NOT created by /speckit-plan)
```

### Source Code (repository root)

This feature has no `src/`/`backend/`/`frontend/` split — it edits an existing, self-contained skill directory in place:

```text
.claude/skills/scrum-master/
├── SKILL.md                                   # entry point; frontmatter frozen, body restructured
└── references/
    ├── sources.md                             # citation registry; gains per-entry page/quote precision, JA pagination note
    ├── scrum-framework.md                     # canonical home for Scrum Guide definitions/events/artifacts (SG20 quotes)
    ├── scrum-master-role.md                   # canonical home for SM accountability + coaching-stance taxonomy
    ├── event-playbooks.md                     # event facilitation detail; timeboxes link to scrum-framework.md, not restated
    ├── facilitation-and-coaching.md           # facilitation technique + psychological-safety definition (canonical)
    ├── measurement-and-diagnostics.md         # flow/quality/EBM/DORA metrics; links to facilitation-and-coaching.md for psych-safety
    ├── anti-patterns-and-coaching.md          # anti-pattern taxonomy (canonical); SKILL.md summary links here
    ├── scaling-frameworks.md                  # Nexus/LeSS/SAFe (+ optional Scrum@Scale, FR-015)
    └── solo-practice.md                       # solo adaptation; links to event-playbooks.md and measurement-and-diagnostics.md
```

No files are added or removed; `scripts/flow_metrics.py` is untouched.

**Structure Decision**: Edit in place. Each reference file keeps its current responsibility (per `SKILL.md`'s routing table, FR-007), but the plan reassigns which file is *canonical* for each explanation that currently appears in more than one place (see `data-model.md`), so restructuring is about removing restatement and adding citation precision, not moving content to new files.

## Complexity Tracking

*No constitution violations — this section is not applicable.*
