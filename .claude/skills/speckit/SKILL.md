---
name: speckit
description: Spec-Driven Development (SDD) workflow using github/spec-kit. Use when the repository has a `.specify/` directory, when editing files under `specs/{N}-{name}/`, or when the user invokes any `/speckit.*` command (constitution, specify, clarify, plan, tasks, implement, analyze).
when_to_use: Activate for any work touching `.specify/` or `specs/**/*.md`. Do not activate for general coding in repos without spec-kit.
paths:
  - ".specify/**"
  - "specs/**"
---

# Spec-Driven Development (SDD) with spec-kit

Specs are the single source of truth for behavior. Tool: [github/spec-kit](https://github.com/github/spec-kit).

## Setup

```bash
# Install CLI (requires uv, Python 3.11+)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
specify init <PROJECT_NAME>
```

Creates `.specify/` with templates and slash commands wired into `.claude/CLAUDE.md`.

## Layout

```
.specify/
├── memory/constitution.md              # Governance principles
├── templates/                          # Do not edit manually
└── specs/{NUMBER}-{FEATURE-NAME}/      # e.g., 001-user-authentication
    ├── spec.md       # Feature spec (source of truth)
    ├── plan.md       # Technical plan
    ├── tasks.md      # Actionable checklist
    └── checklist.md  # Quality gates
```

## Workflow (in order; validate each phase before the next)

| # | Command | Output |
|---|---|---|
| 1 | `/speckit.constitution` | `.specify/memory/constitution.md` |
| 2 | `/speckit.specify <desc>` | `specs/{N}-{name}/spec.md` |
| 3 | `/speckit.clarify` | Updated `spec.md` |
| 4 | `/speckit.plan` | `plan.md` |
| 5 | `/speckit.tasks` | `tasks.md` |
| 6 | `/speckit.implement` | Working code |
| 7 | `/speckit.analyze` (read-only) | Consistency report |

## `spec.md`

- User scenarios: plain language + Given/When/Then.
- Functional reqs: `FR-001…` with MUST/SHOULD.
- Success criteria: `SC-001…` measurable.
- Edge cases: boundary and exception paths.
- **What and why** only — no technology/framework decisions.

## `tasks.md`

```
- [ ] T001 [P] [US1] Description with exact file path
```

- `[P]` = parallel-safe (no shared files). `[US1]` = links to a user story.
- Phase order: Setup → Foundational → User stories → Polish.
- Models before services; services before endpoints.

## Rules

- No implementation code without a spec in place.
- Implementation satisfies spec; on divergence fix the implementation (unless spec is wrong).
- Spec changes need explicit user approval — never silently edit a spec to match broken code.
- Ambiguous spec → `/speckit.clarify` before coding.
- Implementation reveals a gap → document it and ask before filling.
- `/speckit.analyze` suggestions are review-only; never auto-apply.
