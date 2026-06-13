# Architecture Decision Record (ADR) Rules

Purpose: capture the *why* behind significant, hard-to-reverse decisions so rationale survives the people who made it. Applies when a choice has lasting architectural impact and is costly to reverse. Grounded in Nygard's Architecture Decision Records and the MADR template. Complements `coder` (SDD captures *what/why* of a feature) and `domain-model` (captures structure) by recording the *decision* itself.

## When an ADR is warranted

Record a decision when **all** hold: it is architecturally significant (affects structure, cross-cutting concerns, or external contracts), it is hard to reverse (a one-way door), and a reasonable alternative was rejected. Skip ADRs for reversible, local, or obvious choices — prefer a code comment there.

## Trigger to propose one

When a session settles such a decision (framework/datastore choice, bounded-context boundary, API/protocol, auth model, build/deploy topology), Claude SHOULD propose recording an ADR before moving on. Do not author it silently unless asked; surface the proposal.

## Format and placement (MADR)

- File: `docs/adr/NNNN-<kebab-title>.md`, zero-padded sequential `NNNN`.
- Sections: **Title**, **Status** (`Proposed` / `Accepted` / `Superseded by NNNN`), **Context**, **Decision**, **Consequences** (positive and negative), **Alternatives considered**.
- ADRs are **immutable once Accepted** — supersede with a new ADR; do not rewrite history.
- Placement follows `live-documentation.md` Proximity: `docs/adr/` is the conventional home and is explicitly out of scope for drift checks (it is a standalone decision record, not code-derivative).

## Use the `adr` skill

For authoring or updating records, load the `adr` skill for the full playbook and template.
