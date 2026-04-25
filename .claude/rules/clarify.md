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

## How to ask

- **Batch questions, don't drip** — surface all blocking gaps in one turn; group by decision.
- **Offer a default** — "Default: X. Confirm, or choose Y/Z."
- **State assumption cost** — make the risk of each choice explicit (reversibility, effort, blast radius).
- **One decision per question** — no compound asks.
- **Confidence tagging** — mark inferred answers with `high / medium / low` confidence (use the `advisor` skill for analysis norms after context is clear).

For ISO/BABOK elicitation patterns, quality-check tables, and anti-patterns, invoke the **`requirements`** skill.

### Template

```
Blocking gaps:
1. <dimension>: <question> — Default: <X>. Alt: <Y>. Impact: <reversible/irreversible, scope>.
2. …

Assumed (proceed unless corrected):
- <assumption> — confidence: <H/M/L>
```
