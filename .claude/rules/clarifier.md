# Clarification Rules

When a request is ambiguous, incomplete, or beyond reasonable inference, **stop and ask** — do not fabricate intent.

## When to ask

Any of these, where the answer would change what you build:

- **Intent** — the goal is unstated or has several plausible readings.
- **Scope** — inputs, outputs, affected files or systems, or boundaries are undefined.
- **Acceptance** — no verifiable success criterion; you could not write a test.
- **Constraints** — performance, security, compatibility, or deadline limits are missing where they matter.
- **Conflict** — contradicts an existing spec, a rule here, or a prior decision this session.
- **Risk** — irreversible or destructive, or blast radius beyond the local workspace (`permissions.md`).

Otherwise proceed. Where the gap is trivial and the default obvious — two-way door, local, reversible — **proceed and state the assumption explicitly** instead of asking.

## How to ask

Batch every blocking gap into one turn; never drip questions turn by turn. Per gap: a default, the cost of assuming it (reversibility, effort, blast radius), one decision per question. Tag inferred answers `high`/`medium`/`low` confidence. Never ask after the work is done, and never invent acceptance criteria the user did not agree to.

## Related

The `clarifier` skill supplies the _how_: elicitation toolbox, ambiguity-pattern catalogue, quality gate. If you cannot write a failing test from a requirement, it is still ambiguous (`coder`). Where a `spec.md` exists, clarify against it with `/speckit-clarify` rather than inline Q&A. Destructive actions need confirmation regardless of clarification state (`permissions.md`).
