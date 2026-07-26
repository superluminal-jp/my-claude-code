# Implementation Plan: Remove solo-practice individual-use capability from `scrum-master`

**Branch**: `018-remove-solo-practice` | **Date**: 2026-07-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/018-remove-solo-practice/spec.md`

## Summary

Delete `.claude/skills/scrum-master/references/solo-practice.md` and every reference to solo/individual-use capability across `SKILL.md` (frontmatter + body + routing table) and the four documents that declare the skill's routing scope (`.claude/rules/skill-routing.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, `README.md`), so the skill's declared capability matches its actual content. A prior grep-based inventory (done before writing the spec) confirmed exactly six files need changes and no test file requires modification, since no existing regression case exercises solo-specific routing. The `017-scrum-master-rewrite` citation work, still uncommitted on this branch's parent state, must remain untouched.

## Technical Context

**Language/Version**: N/A — Markdown/YAML frontmatter edits and one file deletion; no code.

**Primary Dependencies**: None beyond the repository's existing skill/routing documentation set.

**Storage**: N/A.

**Testing**: `tests/run-skill-routing.sh`, `tests/skill-routing/007-scrum-facilitation.md`, `tests/run-codex-sync.sh` — must pass unchanged (FR-012). No new test is added (no existing solo-specific case to replace, per the Assumptions in spec.md).

**Target Platform**: Claude Code / Codex skill runtime and this repository's own documentation set.

**Project Type**: Documentation/content removal and cross-document consistency fix.

**Performance Goals**: N/A.

**Constraints**: Must not touch `017-scrum-master-rewrite`'s citation/quotation content in files other than the ones this feature explicitly changes (FR-011). Must not modify installed user-scope copies directly (FR-014).

**Scale/Scope**: 6 files changed (1 deleted, 5 edited): `SKILL.md`, `solo-practice.md` (deleted), `.claude/rules/skill-routing.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, `README.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template — no ratified principles to check against. Gate passes trivially, as it did for `017-scrum-master-rewrite`.

## Project Structure

### Documentation (this feature)

```text
specs/018-remove-solo-practice/
├── plan.md              # This file
├── research.md          # Phase 0 output — inventory of every solo-practice reference
├── quickstart.md         # Phase 1 output — verification steps
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/speckit-tasks)
```

No `data-model.md` or `contracts/` — this feature has no data entities or external interfaces; it is a targeted deletion plus five documentation edits, and `research.md` plus `quickstart.md` fully cover what a plan needs to say.

### Source Code (repository root)

```text
.claude/skills/scrum-master/
├── SKILL.md                                   # frontmatter + body + routing table: remove solo mentions
└── references/
    └── solo-practice.md                       # DELETE

.claude/rules/skill-routing.md                 # remove solo-routing sentence from scrum-master entry
.claude/CLAUDE.md                              # remove "team or solo retrospectives" -> "team retrospectives"
.codex/AGENTS.md                               # remove "team or solo retrospectives" -> "team retrospectives"
README.md                                      # remove "team or solo" -> "team"
```

**Structure Decision**: Edit in place; delete one file. No new files, no restructuring beyond what FR-001–FR-010 specify.

## Complexity Tracking

*No constitution violations — not applicable.*
