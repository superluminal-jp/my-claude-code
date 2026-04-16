# Spec-Driven Development (SDD) with spec-kit

Use [github/spec-kit](https://github.com/github/spec-kit) as the standard tooling for SDD.
Specifications are the single source of truth for behavior.

## Setup

```bash
# Install spec-kit CLI (requires uv and Python 3.11+)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z

# Initialize in project root
specify init <PROJECT_NAME>
```

This creates the `.specify/` directory with templates and slash commands wired into `.claude/CLAUDE.md`.

## Directory Structure

```
.specify/
├── memory/constitution.md          # Project governance principles
├── templates/                      # Spec-kit templates (do not edit manually)
└── specs/
    └── {NUMBER}-{FEATURE-NAME}/    # e.g., 001-user-authentication/
        ├── spec.md                 # Feature specification (source of truth)
        ├── plan.md                 # Technical implementation plan
        ├── tasks.md                # Actionable task checklist
        └── checklist.md           # Quality gates
```

## Workflow (execute in order)

| Step | Command | Output |
|------|---------|--------|
| 1. Governance | `/speckit.constitution` | `.specify/memory/constitution.md` |
| 2. Specify | `/speckit.specify <description>` | `specs/{N}-{name}/spec.md` |
| 3. Clarify | `/speckit.clarify` | Updated `spec.md` |
| 4. Plan | `/speckit.plan` | `plan.md` |
| 5. Tasks | `/speckit.tasks` | `tasks.md` |
| 6. Implement | `/speckit.implement` | Working code |
| 7. Analyze | `/speckit.analyze` | Consistency report |

Validate each phase before proceeding to the next.

## Spec Format (`spec.md`)

- **User scenarios**: Plain language + Given/When/Then acceptance criteria
- **Functional requirements**: `FR-001`, `FR-002`, … with MUST/SHOULD language
- **Success criteria**: `SC-001`, `SC-002`, … with measurable outcomes
- **Edge cases**: Boundary conditions and exception paths
- Focus on **what** and **why** — no technology or framework decisions in the spec

## Task Format (`tasks.md`)

```
- [ ] T001 [P] [US1] Description with exact file path
```

- `[P]` marks tasks that can run in parallel (no shared file dependencies)
- `[US1]` links to a user story
- Phase order: Setup → Foundational infrastructure → User stories → Polish
- Rule: models before services, services before endpoints

## Rules

- Never write implementation code without a spec in place
- Specs describe behavior; implementation satisfies the spec
- When spec and implementation diverge, fix the implementation — not the spec (unless the spec is wrong)
- Spec changes require explicit user approval; never silently update a spec to match a broken implementation
- When a spec is ambiguous, surface the ambiguity via `/speckit.clarify` before coding
- If implementation reveals a spec gap, document the gap and ask before filling it
- `/speckit.analyze` is read-only; never auto-apply its remediation suggestions without review
