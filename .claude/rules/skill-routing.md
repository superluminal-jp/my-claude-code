# Skill Routing Guardrail

Use rules as always-on guidance and skills as on-demand playbooks.

## Mandatory gate

1. Run `rules/clarify.md` first (intent, scope, constraints, acceptance criteria).
2. If blocking gaps remain, ask clarifying questions before implementation.
3. Proceed only after assumptions are explicit and testable.

## Routing

- Code implementation or behavior changes -> load `coder`.
- Produced artifacts (docs, decks, charts, translation, editing) -> load `editor`.
- Ambiguous requirements or missing acceptance criteria -> load `clarifier`.

## Scope discipline

- Load only the minimum relevant skill(s) for the task.
- Do not treat skills as always-on baseline context.
- If guidance conflicts, prioritize:
  1. `rules/clarify.md`
  2. task-specific skill
  3. `rules/advisor.md`
