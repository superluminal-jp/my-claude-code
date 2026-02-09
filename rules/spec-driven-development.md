# Spec-Driven Development with spec-kit

**Purpose**: Enforce specification-first workflow for code modifications using GitHub spec-kit.

**When Applied**: All code modification tasks — new features, refactoring, bug fixes, and enhancements.

**Reference**: https://github.com/github/spec-kit

---

## Core Principle

**Define what to build before deciding how to build it.**

Every code modification begins with a specification. Implementation follows the spec, not the reverse. This eliminates ambiguity, reduces rework, and produces traceable changes.

---

## Workflow Phases

### Phase 0: Constitution (Project Governance)

Before any development, ensure `.speckit/constitution.md` defines project principles. This file governs all subsequent work — coding standards, architectural constraints, quality expectations.

Run `/speckit.constitution` if the file does not exist.

### Phase 1: Specify (Requirements)

Describe **what** the change accomplishes from the user's perspective. Focus on observable behavior, acceptance criteria, and constraints. Avoid prescribing technical implementation.

Run `/speckit.specify` to create or update `.speckit/spec.md`.

**Good specification**: "Users can reset their password via email. The reset link expires after 15 minutes. Failed attempts are rate-limited to 3 per hour."

**Bad specification**: "Add a POST endpoint at /api/reset-password that sends an email using SendGrid."

### Phase 2: Plan (Architecture)

Define the technical approach — tech stack, dependencies, patterns, constraints. The plan maps spec requirements to implementation decisions.

Run `/speckit.plan` to create `.speckit/plan.md`.

### Phase 3: Tasks (Decomposition)

Break the plan into atomic, implementable tasks. Each task produces a testable increment.

Run `/speckit.tasks` to create `.speckit/tasks.md`.

### Phase 4: Implement (Execution)

Build features according to established tasks. Each implementation step references its originating task.

Run `/speckit.implement` to execute tasks.

---

## When to Apply

### Greenfield (0-to-1)

Full workflow: Constitution → Specify → Plan → Tasks → Implement. No shortcuts. The spec defines the entire system boundary.

### Brownfield (Iterative Enhancement)

Abbreviated workflow for existing codebases:

1. **Check existing spec artifacts** in `.speckit/` directory
2. **Update or create spec** for the specific change
3. **Plan** within existing architectural constraints
4. **Task decomposition** scoped to the change
5. **Implement** with traceability to spec

### Bug Fixes

Minimal workflow:

1. **Specify** the expected vs actual behavior
2. **Plan** the fix approach
3. **Implement** with reference to the spec

### Refactoring

1. **Specify** the quality improvement goal (performance, readability, maintainability)
2. **Analyze** existing code against spec
3. **Plan** the refactoring strategy
4. **Implement** incrementally

---

## Quality Gates

### Before Implementation

- [ ] Spec exists and covers all acceptance criteria
- [ ] Plan references specific spec requirements
- [ ] Tasks are atomic and testable
- [ ] Ambiguities resolved via `/speckit.clarify`

### During Implementation

- [ ] Each change traces to a spec requirement
- [ ] No unspecified behavior introduced
- [ ] Tests validate spec acceptance criteria

### After Implementation

- [ ] `/speckit.analyze` confirms spec-plan-task consistency
- [ ] `/speckit.checklist` validates completeness
- [ ] Documentation reflects implemented spec

---

## Directory Structure

```
.speckit/
├── constitution.md    # Project governance and principles
├── spec.md            # Requirements and acceptance criteria
├── plan.md            # Technical architecture decisions
├── tasks.md           # Decomposed implementation tasks
└── features/          # Feature-specific specs (optional)
    ├── auth/
    │   ├── spec.md
    │   ├── plan.md
    │   └── tasks.md
    └── billing/
        ├── spec.md
        ├── plan.md
        └── tasks.md
```

---

## spec-kit Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/speckit.constitution` | Define project governance | Project setup, principle changes |
| `/speckit.specify` | Create requirements spec | Before any code change |
| `/speckit.plan` | Define technical approach | After spec is finalized |
| `/speckit.tasks` | Decompose into tasks | After plan is approved |
| `/speckit.implement` | Execute implementation | After tasks are defined |
| `/speckit.clarify` | Resolve ambiguities | When spec is underspecified |
| `/speckit.analyze` | Check consistency | Before and after implementation |
| `/speckit.checklist` | Validate completeness | Final quality check |

---

## Anti-Patterns

### Skipping the Spec

Starting implementation without a specification leads to scope creep, missed requirements, and rework. Even a two-line spec ("Expected: X. Actual: Y.") is better than none.

### Over-Specifying Implementation

The spec defines **what**, not **how**. Technical decisions belong in the plan phase. Mixing the two creates brittle specs that break on implementation changes.

### Ignoring Existing Artifacts

When `.speckit/` artifacts exist, read them first. They contain architectural decisions and constraints that must be respected.

---

## Integration with Existing Workflow

spec-kit complements the existing file-editing and documentation rules:

1. **spec-kit spec** → defines what to change
2. **file-editing strategy** → defines how to edit efficiently
3. **documentation rule** → ensures docs reflect the implemented spec
4. **quality gates** → validate spec compliance

---

**Last Updated**: 2026-02-07
