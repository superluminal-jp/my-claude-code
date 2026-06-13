---
name: adr
description: Record architecturally significant, hard-to-reverse decisions as immutable Architecture Decision Records. Use when a session settles a one-way-door choice (datastore, framework, bounded-context boundary, API/protocol, auth model, deploy topology) and a reasonable alternative was rejected — capturing Context, Decision, Consequences, and Alternatives so rationale outlives the decision-makers. Generates docs/adr/NNNN-<title>.md in MADR format, assigns the next sequential number, and supersedes rather than rewrites prior records. Grounded in Nygard ADRs and the MADR template.
when_to_use: record architecture decision, write ADR, document why we chose, capture decision rationale, ADR for datastore/framework/protocol choice, bounded context boundary decision, supersede a previous decision, decision log entry, one-way door decision
---

# Skill: adr

Purpose: author and maintain Architecture Decision Records. Applies when a significant, hard-to-reverse decision is made. Read `rules/adr.md` for the governing policy (when to record, placement, immutability); this skill is the authoring playbook. Grounded in Nygard's ADRs and the MADR template.

## Procedure

1. **Confirm it warrants an ADR** — significant + hard to reverse + a real alternative rejected (per `rules/adr.md`). If not, suggest a code comment instead and stop.
2. **Find the next number** — scan `docs/adr/` for the highest `NNNN`; use `NNNN+1`, zero-padded to 4 digits. Create `docs/adr/` if absent.
3. **Draft** from the template below; fill every section. Be concrete in Consequences — name the negative trade-offs, not just benefits.
4. **Set Status** — `Proposed` until the user accepts, then `Accepted`. To replace a prior decision, write a new ADR and set the old one's status to `Superseded by NNNN`; never edit an Accepted record's substance.
5. **Cross-link** — reference the spec, issue, or related ADRs.

## Template

```markdown
# NNNN. <Decision title in one line>

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD
- Deciders: <who>

## Context

<The forces at play: requirements, constraints, the problem. Why a decision is needed now.>

## Decision

<The choice made, stated in active voice: "We will …">

## Consequences

- Positive: <what becomes easier>
- Negative: <what becomes harder; trade-offs accepted>

## Alternatives considered

- <Option B> — <why rejected>
- <Option C> — <why rejected>
```

## Conventions

- **Language**: respond and write in the language of the current conversation; the template above is English — adapt at runtime.
- **One decision per ADR**; split compound decisions.
- Keep it short — an ADR is a record, not an essay. Link out for detail.
