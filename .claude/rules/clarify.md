# Clarification Rules

When a request is ambiguous, incomplete, or cannot be completed by reasonable inference, **stop and ask** — do not fabricate intent. Ground every clarification in requirements-engineering standards, not ad-hoc guesses.

## When to clarify (triggers)

Ask before acting if any of the following hold:

- **Intent gap**: the goal ("why") is unstated or has multiple plausible readings.
- **Scope gap**: inputs, outputs, affected files/systems, or boundaries are undefined.
- **Acceptance gap**: no verifiable success criterion exists (cannot write a test).
- **Constraint gap**: non-functional limits (performance, security, compatibility, deadline) are missing where they matter.
- **Conflict**: new request contradicts an existing spec, CLAUDE.md rule, or prior decision in the session.
- **Risk**: action is irreversible, destructive, or has blast radius beyond the local workspace (see `permissions.md`).

If the gap is trivial and the default is obvious (two-way door, local, reversible), proceed and state the assumption explicitly. Otherwise, ask.

## Quality checks (per requirement)

Based on **ISO/IEC/IEEE 29148:2018 §5.2.4** and **IEEE 830-1998 §4.3**. A request is complete only if each item is:

| Attribute | Check |
|---|---|
| Necessary | Removing it changes the outcome. |
| Unambiguous | Exactly one interpretation. |
| Complete | No "TBD", no missing actor / action / object / condition. |
| Singular | One requirement per statement (no "and" hiding two). |
| Feasible | Achievable within known constraints. |
| Verifiable | A concrete test, inspection, or metric can confirm it. |
| Correct | Matches stakeholder need (validate via restatement). |
| Consistent | No contradiction with other requirements. |

Set-level checks: **Complete, Consistent, Bounded, Affordable** (29148 §5.2.5).

## Ambiguity patterns to flag

- **Vague quantifiers**: "fast", "a lot", "many", "soon", "robust", "scalable", "user-friendly" → demand a number + unit.
- **Undefined pronouns / scope**: "it", "the system", "everything" → name the target.
- **Hidden compound**: statements with "and/or" that bundle multiple reqs → split.
- **Implicit actor / trigger**: "when needed", "automatically" → specify actor, event, precondition.
- **Implementation leakage in a requirement**: solution dictated before problem agreed → separate *what* from *how*.
- **Negation without positive**: "should not be slow" → restate as measurable positive ("p95 < 200ms").

## Elicitation toolkit

Pick the lightest tool that closes the gap. Reference **BABOK v3** elicitation techniques.

- **5W2H** — What / Why / Who / When / Where / How / How much. Use to spot missing dimensions.
- **SMART** _(goals)_ — Specific, Measurable, Achievable, Relevant, Time-bound.
- **INVEST** _(user stories)_ — Independent, Negotiable, Valuable, Estimable, Small, Testable.
- **User story shell** — `As a <role>, I want <capability>, so that <benefit>.` Forces role + value.
- **Gherkin / Given-When-Then** — testable acceptance criteria; one scenario per logical outcome.
- **MoSCoW** _(priority)_ — Must / Should / Could / Won't. Use when scope exceeds budget.
- **Volere fit criterion** — every requirement paired with a measurable pass/fail rule.
- **Kano** _(features)_ — Must-be / Performance / Delighter. Use when trade-offs are unclear.
- **FURPS+** _(non-functional)_ — Functionality, Usability, Reliability, Performance, Supportability, + constraints.

## How to ask

- **Batch questions, don't drip** — surface all blocking gaps in one turn; group by decision.
- **Offer a default** — "Default: X. Confirm, or choose Y/Z." Reduces user load (cf. BABOK "option analysis").
- **State assumption cost** — make the risk of each choice explicit (reversibility, effort, blast radius).
- **One decision per question** — no compound asks.
- **Confidence tagging** — mark inferred answers with `high / medium / low` confidence (see `advisor.md`).

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

## Interaction with other rules

- **`permissions.md`** — destructive actions always require confirmation, independent of clarification state.
- **`speckit.md`** — if a spec exists, clarify against `spec.md`; run `/speckit.clarify` for spec-level gaps rather than inline Q&A.
- **`development.md`** — a clarified requirement must be testable; if you cannot write a failing test for it, the requirement is still ambiguous.
- **`advisor.md`** — after clarification, deliver analysis conclusion-first; do not re-ask once the decision is made.
