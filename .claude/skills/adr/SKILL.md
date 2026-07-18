---
name: adr
description: Record architecturally significant, hard-to-reverse decisions as immutable Architecture Decision Records. Use when a session settles a one-way-door choice (datastore, framework, bounded-context boundary, API/protocol, auth model, deploy topology) and a reasonable alternative was rejected — capturing Context, Decision, Consequences, and Alternatives so rationale outlives the decision-makers. Generates docs/adr/NNNN-<title>.md in MADR format, assigns the next sequential number (never reused), and supersedes rather than rewrites prior records. Grounded in Nygard's ADRs, the MADR 4.0.0 template, and ISO/IEC/IEEE 42010:2022 rationale requirements.
when_to_use: record architecture decision, write ADR, document why we chose, capture decision rationale, ADR for datastore/framework/protocol choice, bounded context boundary decision, supersede a previous decision, decision log entry, one-way door decision
---

# Skill: adr

Purpose: author and maintain Architecture Decision Records. Applies when a significant, hard-to-reverse decision is made. Read `rules/adr.md` for the governing policy (when to record, placement, immutability, status values, and full references); this skill is the authoring playbook. The template below follows Nygard's original structure extended with the MADR 4.0.0 optional sections.

## Procedure

1. **Confirm it warrants an ADR** — significant + hard to reverse + a real alternative rejected (per `rules/adr.md`). If not, suggest a code comment instead and stop.
2. **Find the next number** — scan `docs/adr/` for the highest `NNNN`; use `NNNN+1`, zero-padded to 4 digits. **Never reuse a number**, even if an earlier ADR was rejected or superseded. Create `docs/adr/` if absent.
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

Template derived from Nygard (2011) and MADR 4.0.0; rationale content per ISO/IEC/IEEE 42010:2022. Full citations with URLs: `rules/adr.md` § References.
