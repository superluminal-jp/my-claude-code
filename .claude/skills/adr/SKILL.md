---
name: adr
description: Record architecturally significant, hard-to-reverse decisions with a rejected reasonable alternative as immutable Architecture Decision Records containing context, decision, consequences, and alternatives. Use to create or supersede a record only when the user explicitly requests that action; when a qualifying decision emerges without that authorization, propose a record and wait. Do not use for reversible, local, obvious, or day-to-day implementation choices. When another capability independently matches, keep it active and place the record or proposal at the point where the consequential decision is settled.
---

# Skill: adr

Purpose: author and maintain Architecture Decision Records. An ADR captures a decision's context, choice, consequences, and rejected alternatives, distinct from a feature's day-to-day *what/why*. The template follows Nygard's original structure extended with MADR 4.0.0 optional sections; rationale content follows ISO/IEC/IEEE 42010:2022 (see [References](#references)).

## When to record

Record when **all** hold: architecturally significant (affects structure, cross-cutting concerns, or external contracts), hard to reverse (a one-way door), and a reasonable alternative was rejected. Skip reversible, local, obvious, and ordinary implementation choices; a nearby explanation is sufficient when one is needed.

Creating or changing a record requires an explicit user request for that action. A general request to implement the underlying decision is not sufficient authorization. If a session settles a qualifying choice such as a framework, datastore, bounded-context boundary, API or protocol, authorization model, or build/deploy topology without an explicit record request, propose the record and wait; never author it silently.

This procedure remains applicable when another capability independently matches. Continue that work and place the proposal before the decision becomes costly to reverse, or create the authorized record once the decision and rejected alternative are stable.

## Procedure

1. **Confirm authority and significance** — verify the user explicitly requested creation or supersession and that the decision meets every criterion above. Without creation authority, make only the proposal. If the decision is not significant enough, recommend a nearby explanation when useful and stop.
2. **Find the next number** — scan `docs/adr/` for the highest `NNNN`; use `NNNN+1`, zero-padded to 4 digits. **Never reuse a number**, even if an earlier ADR was rejected or superseded. Create `docs/adr/` if absent; a standalone rationale record is not generated contract documentation.
3. **Draft** from the template below. Fill the mandatory core; add the optional MADR sections only when the decision's complexity warrants them (a large ADR goes unread — Nygard). Be concrete in Consequences — name the negative trade-offs, not just benefits; where relevant, note the impact on quality attributes (ISO/IEC/IEEE 42010).
4. **State how it will be confirmed** — when applicable, record how compliance with the decision will be verified (a test, review gate, fitness function, or lint rule) in *Confirmation*.
5. **Set Status** — `Proposed` until the user accepts, then `Accepted`. Use `Deprecated` when a decision is no longer relevant with no replacement; `Superseded by NNNN` when a later ADR replaces it. Never edit an Accepted record's substance, and **keep** superseded/deprecated records — do not delete them.
6. **Cross-link** — reference the spec, issue, or related ADRs under *More information*.

## Template

Mandatory core = Title, Status, Date, Context and problem statement, Decision, Consequences. The remaining sections are MADR 4.0.0 options — include them only when the decision is non-trivial.

```markdown
---
status: Proposed | Accepted | Deprecated | Superseded by NNNN
date: YYYY-MM-DD
deciders: <who made the decision>
consulted: <SMEs consulted — optional>
informed: <kept informed — optional>
---

# NNNN. <Decision title: a short noun phrase>

## Context and problem statement

<The forces at play — technical, political, social, project-local — and the
problem that forces a decision now. Tie it to the stakeholder concerns or
quality attributes affected.>

## Decision drivers <!-- optional -->

- <driver / criterion 1>
- <driver / criterion 2>

## Considered options <!-- optional -->

- <Option A>
- <Option B>
- <Option C>

## Decision outcome

We will <Option A>, because <justification tied to the drivers>.

### Consequences

- Positive: <what becomes easier>
- Negative: <what becomes harder; trade-offs accepted>

## Confirmation <!-- optional -->

<How compliance with this decision will be verified: a test, review gate,
fitness function, or lint rule.>

## Pros and cons of the options <!-- optional -->

### <Option A>

- Good: <…>
- Bad: <…>

### <Option B>

- Good: <…>
- Bad: <…>

## More information <!-- optional -->

<Links to the spec, issue, related ADRs, evidence, or the team agreement.>
```

## Conventions

- **Language**: respond and write in the language of the current conversation; the template above is English — adapt at runtime.
- **One decision per ADR**; split compound decisions.
- Keep it short — an ADR is a record, not an essay; large documents go unread and unmaintained (Nygard). Use the mandatory core by default and add optional sections only when they earn their place. Link out for detail.

## References

- Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011-11-15 — <https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
- MADR — Markdown Any Decision Records, v4.0.0 (2024-09-17) — <https://adr.github.io/madr/>
- Joel Parker Henderson, "Architecture decision record (ADR)" template collection — <https://github.com/joelparkerhenderson/architecture-decision-record>
- ISO/IEC/IEEE 42010:2022, *Software, systems and enterprise — Architecture description* — <https://www.iso.org/standard/74393.html>
