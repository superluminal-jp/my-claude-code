# Spec-Driven Development

**Purpose**: Define what to build before deciding how. Every code modification begins with a specification.

**Reference**: [GitHub spec-kit](https://github.com/github/spec-kit)

---

## Core Principle

Specification first, implementation second. Eliminates ambiguity, reduces rework, produces traceable changes.

## Workflow Phases

1. **Constitution** — Project governance (`.speckit/constitution.md`)
2. **Specify** — What the change accomplishes, acceptance criteria, constraints
3. **Plan** — Technical approach, dependencies, architecture
4. **Tasks** — Atomic, testable implementation steps
5. **Implement** — Build according to tasks, traceability to spec

## When to Apply

| Change Type | Workflow |
|-------------|----------|
| Greenfield | Full: Constitution → Specify → Plan → Tasks → Implement |
| Enhancement | Update spec → Plan → Tasks → Implement |
| Bug fix | Minimal: Expected vs actual → Plan → Implement |
| Refactor | Quality goal → Analyze → Plan → Implement |

## Quality Gates

**Before**: Spec covers acceptance criteria, ambiguities resolved, tasks are atomic and testable.
**During**: Each change traces to a spec requirement, no unspecified behavior.
**After**: Tests validate spec criteria, docs reflect implemented spec.

## Anti-Patterns

- **Skipping spec**: Implementation without specification
- **Over-specifying how**: Spec defines "what," plan defines "how"
- **Ignoring artifacts**: Always read `.speckit/` before making changes

---

**For step-by-step workflow**: Use `speckit-workflow` skill or `/speckit` command.

**Last Updated**: 2026-02-10
