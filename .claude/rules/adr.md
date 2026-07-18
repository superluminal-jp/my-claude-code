# Architecture Decision Record (ADR) Rules

Purpose: capture the *why* behind significant, hard-to-reverse decisions so rationale survives the people who made it. Applies when a choice has lasting architectural impact and is costly to reverse. Grounded in Michael Nygard's original ADR essay (2011), the MADR 4.0.0 template, and the architecture-rationale requirements of ISO/IEC/IEEE 42010:2022 (see [References](#references)). Complements `coder` (SDD captures *what/why* of a feature) and `domain-model` (captures structure) by recording the *decision* itself.

## When an ADR is warranted

Record a decision when **all** hold: it is architecturally significant (affects structure, cross-cutting concerns, or external contracts), it is hard to reverse (a one-way door), and a reasonable alternative was rejected. Skip ADRs for reversible, local, or obvious choices — prefer a code comment there.

## Trigger to propose one

When a session settles such a decision (framework/datastore choice, bounded-context boundary, API/protocol, auth model, build/deploy topology), Claude SHOULD propose recording an ADR before moving on. Do not author it silently unless asked; surface the proposal.

## Format and placement (MADR)

- File: `docs/adr/NNNN-<kebab-title>.md`, zero-padded sequential `NNNN`. Numbers are assigned **monotonically and never reused** — even for rejected, deprecated, or superseded records (Nygard).
- **Required sections**: **Title**, **Status**, **Date**, **Context and problem statement**, **Decision** (active voice — "We will …"), **Consequences** (positive *and* negative). Record the **deciders**.
- **Recommended for non-trivial decisions** (MADR 4.0.0): **Decision drivers**, **Considered options** with **pros and cons of each**, **Confirmation** (how compliance will be verified), and **More information** (links/evidence). See the `adr` skill for the template.
- **Rationale content** (ISO/IEC/IEEE 42010:2022): the record should capture the basis for the decision, its impact on quality attributes, the alternatives and trade-offs considered, the consequences, and citations to supporting sources — tying the decision to the stakeholder concerns it serves.
- **Status values**: `Proposed` (under discussion) → `Accepted` (agreed); `Deprecated` (no longer relevant, with no replacement); `Superseded by NNNN` (replaced by a later ADR).
- ADRs are **immutable once Accepted** — never rewrite an accepted record's substance. To reverse a decision, write a **new** ADR and mark the old one `Superseded by NNNN`; **keep the old record** so the history of *why* survives (Nygard).
- Placement follows `live-documentation.md` Proximity: `docs/adr/` is the conventional home and is explicitly out of scope for drift checks (it is a standalone decision record, not code-derivative).

## Use the `adr` skill

For authoring or updating records, load the `adr` skill for the full playbook and template.

## References

- Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011-11-15 — <https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
- MADR — Markdown Any Decision Records, v4.0.0 (2024-09-17) — <https://adr.github.io/madr/>
- Joel Parker Henderson, "Architecture decision record (ADR)" template collection — <https://github.com/joelparkerhenderson/architecture-decision-record>
- ISO/IEC/IEEE 42010:2022, *Software, systems and enterprise — Architecture description* — <https://www.iso.org/standard/74393.html>
