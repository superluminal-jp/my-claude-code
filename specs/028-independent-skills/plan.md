# Implementation Plan: Skill Bodies Independent of Sibling Skills

**Branch**: `028-independent-skills` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/028-independent-skills/spec.md`

## Summary

Remove sibling-skill cross-references from six `SKILL.md` bodies —
`digital-agency-frontend` (naming `coder`/`clarifier`, 4 instructions),
`coder` (naming `adr`, 1 instruction), `adr` (naming `coder`, 1 mention),
and the minto triad `minto-builder`/`minto-reviewer`/`minto-rewriter`
(mutually routing to each other, 2 sentences each) — so each skill body
is self-contained and understandable in isolation. Where a removed
instruction carried load-bearing behavior (`digital-agency-frontend`'s
reliance on `coder`'s TDD/security/doc-sync and `clarifier`'s ambiguity
resolution), inline the DADS-specific equivalent so no behavior is lost.
Supersede `specs/015-digital-agency-frontend/spec.md` FR-004 in place
(composition requirement → self-containment requirement) and rewrite
`tests/run-digital-agency-frontend-skill.sh` DADS-06/DADS-07 to assert
the new contract. The router layer (`.claude/CLAUDE.md`,
`.claude/rules/skill-routing.md`) and all documentation describing it
(README.md, README.ja.md, AGENTS.md) are explicitly out of scope —
sequencing multiple skills for one task remains the router's job.

## Technical Context

**Language/Version**: N/A — Markdown (SKILL.md, spec.md) and Bash
(test assertions) edits only.

**Primary Dependencies**: None.

**Testing**: Existing `tests/run-*.sh`; `tests/run-digital-agency-frontend-skill.sh`
DADS-06 and DADS-07 rewritten to assert the new contract; SYNC-SKILL-05A
verified unchanged.

**Target Platform**: This repository's `.claude/skills/` (Claude Code
skill discovery); Codex discovers the same authored source via `/import`
per ADR-0004, so no separate Codex-side edit is needed.

**Project Type**: Single project — configuration repository.

**Scale/Scope**: 6 `SKILL.md` edits, 1 spec FR rewrite (015 FR-004),
1 test file edit (2 assertions rewritten), 0 new ADRs.

## Constitution Check

No project-specific constitution ratified (template unfilled). Applicable
repository rules satisfied: `clarifier.md` (scope — skill-body-only vs.
full decoupling — and conflict-resolution path confirmed via
`AskUserQuestion` before the spec was written, since the request
contradicted spec 015 FR-004); `live-documentation.md` (FR-004 and its
guarding tests corrected in the same change, not left drifted —
Drift Detection and Override-free correction, since this is a planned
supersession, not a silent skip); `skill-routing.md`/`CLAUDE.md`
untouched per the confirmed "skill-body only" scope, so the mandatory
routing system's composition directives keep functioning; `adr` skill
policy — no ADR needed (see spec's Assumptions: the routing mechanism
itself is unchanged, only where the instruction to compose is written
down changes, which is not an architecturally significant one-way-door
decision).

## Project Structure

### Documentation (this feature)

```text
specs/028-independent-skills/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

No `contracts/` — no external interface is exposed; this feature edits
instructional skill content and its guarding tests.

### Source Code (repository root)

```text
my-claude-code/
├── .claude/
│   └── skills/
│       ├── digital-agency-frontend/SKILL.md  # edit: remove 4 coder/clarifier instructions, inline DADS-specific equivalents
│       ├── coder/SKILL.md                    # edit: remove 1 adr-loading instruction
│       ├── adr/SKILL.md                      # edit: reword purpose statement to not name coder
│       ├── minto-builder/SKILL.md             # edit: remove 2 routing sentences
│       ├── minto-reviewer/SKILL.md            # edit: remove 2 routing sentences
│       └── minto-rewriter/SKILL.md            # edit: remove 2 routing sentences
├── specs/
│   └── 015-digital-agency-frontend/
│       └── spec.md                           # edit: rewrite FR-004 (supersede composition → self-containment)
└── tests/
    └── run-digital-agency-frontend-skill.sh  # edit: rewrite DADS-06, DADS-07 assertions
```

**Structure Decision**: No structural change — text edits within existing
files. No files created or deleted, no ADR, no router/doc-layer edits.

## Complexity Tracking

Not applicable — no constitution violations.
