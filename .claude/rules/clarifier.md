# Clarification Rules

When a request is ambiguous, incomplete, or cannot be completed by reasonable inference, **stop and ask** — do not fabricate intent.

## When to clarify (triggers)

Ask before acting if any of the following hold:

- **Intent gap**: the goal ("why") is unstated or has multiple plausible readings.
- **Scope gap**: inputs, outputs, affected files/systems, or boundaries are undefined.
- **Acceptance gap**: no verifiable success criterion exists (cannot write a test).
- **Constraint gap**: non-functional limits (performance, security, compatibility, deadline) are missing where they matter.
- **Conflict**: new request contradicts an existing spec, `CLAUDE.md` rule, or prior decision in the session.
- **Risk**: action is irreversible, destructive, or has blast radius beyond the local workspace (see `permissions.md`).

If the gap is trivial and the default is obvious (two-way door, local, reversible), proceed and state the assumption explicitly. Otherwise, ask.

## Minimal quality checks

- Outcome is testable.
- Scope is bounded.
- Constraints are explicit when they matter.
- Request does not conflict with existing instructions.
- Assumptions are stated if proceeding without asking.

## Ambiguity patterns to flag

- **Vague quantifiers**: "fast", "a lot", "many", "soon", "robust", "scalable", "user-friendly" -> demand a number + unit.
- **Undefined pronouns / scope**: "it", "the system", "everything" -> name the target.
- **Hidden compound**: statements with "and/or" that bundle multiple requirements -> split.
- **Implicit actor / trigger**: "when needed", "automatically" -> specify actor, event, precondition.
- **Implementation leakage in a requirement**: solution dictated before problem agreed -> separate *what* from *how*.
- **Negation without positive**: "should not be slow" -> restate as measurable positive ("p95 < 200ms").

## How to ask

- **Batch questions, don't drip** — surface blocking gaps in one turn.
- **Offer a default** — "Default: X. Confirm or choose Y/Z."
- **State assumption cost** — reversibility, effort, blast radius.
- **One decision per question** — no compound asks.
- **Confidence tagging** — mark inferred answers with `high / medium / low`.

### Template

```
Blocking gaps:
1. <dimension>: <question> — Default: <X>. Alt: <Y>. Impact: <reversible/irreversible, scope>.
2. …

Assumed (proceed unless corrected):
- <assumption> — confidence: <H/M/L>
```

## Anti-patterns

- Silently picking one interpretation when multiple are plausible.
- Asking after the work is done ("I built X, is that what you wanted?").
- Stacking clarifications turn-by-turn instead of batching.
- Treating "make it better" as actionable — always require a fit criterion.
- Inventing acceptance criteria the user never agreed to.

## Interaction with other rules and skills

- **`permissions.md`** — destructive actions always require confirmation, independent of clarification state.
- **`coder` skill** — a clarified requirement must be testable (TDD) and match its spec (SDD); if you cannot write a failing test from the request, it is still ambiguous.
- **spec-kit projects** — if a `spec.md` exists, clarify against it; run `/speckit.clarify` for spec-level gaps rather than inline Q&A.
- **`clarifier` skill** — use for formal elicitation frameworks (ISO/IEEE/BABOK/INVEST/Gherkin/MoSCoW) and detailed requirement quality checks.
