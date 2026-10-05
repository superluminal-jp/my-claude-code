# Living documentation practices

## Purpose

Living documentation preserves the current, authoritative, and verifiable knowledge needed to understand, develop, operate, evaluate, reproduce, and evolve a project.

The success criterion is not document volume. A competent stakeholder or agent should be able to determine the project's current state, intent, significant rationale, contracts, operational implications, and supporting evidence without relying on undocumented tribal knowledge.

## Source of truth

Identify the authoritative source for each material fact. Typical examples:

- executable behavior → implementation plus tests/observations;
- API/data contract → machine-readable schema/specification where available;
- configuration → configuration schema/defaults;
- infrastructure → infrastructure-as-code or authoritative deployment configuration;
- architecture rationale → accepted decision records;
- research result → analysis/workflow, input data, environment/version, output, and provenance;
- policy/intent → approved requirement, policy, or stakeholder decision.

If a fact exists in multiple places, prefer one of:

1. derive secondary representations from the authoritative source;
2. verify consistency automatically; or
3. explicitly identify which representation is authoritative.

Do not create unexplained competing sources of truth.

## Change coupling

A change has documentation impact when it materially changes any of:

- externally observable behavior;
- requirements or acceptance criteria;
- architecture or dependencies;
- interfaces, schemas, protocols, configuration, or infrastructure;
- user workflows or operational procedures;
- assumptions, constraints, quality attributes, or limitations;
- significant design decisions or rationale;
- experiments, datasets, analytical methods, provenance, or reproducibility.

Update affected knowledge in the same logical change. Do not knowingly leave authoritative documentation describing the previous state.

Deleting or renaming a file, heading, endpoint, option, or command is also a change: update every reference to the old name.

## Change history

Living documentation describes the current state; change history explains how users get there from an earlier state. When the project keeps change history (CHANGELOG, HISTORY, NEWS, release notes, changelog fragment directories such as `changelog.d/` or `.changeset/`):

- add an entry for user-visible changes, in the project's existing format and section names;
- mark breaking changes and deprecations explicitly, with migration steps or a link to a migration guide;
- keep the entry consistent with the project's versioning policy (for example Semantic Versioning, if the project uses it);
- do not create a changelog in a project that has none unless asked; mention the gap in the report instead.

## Pre-existing drift

Inconsistencies that existed before the current change are reported, not silently fixed. Fix them only when they are in the scope of the change or the user asks, so that unrelated edits do not hide inside the change.

## Minimality

Document knowledge when it answers a real stakeholder question, preserves difficult-to-recover rationale, defines a contract, supports verification/reproduction, or reduces engineering/operational risk.

Avoid prose copies of source code, manually duplicated schemas, decorative diagrams, obsolete alternatives presented as current, and details cheaply regenerated on demand.

## Architecture

For architecture-changing work:

- identify affected stakeholder concerns;
- update relevant views/models;
- update interfaces/dependencies;
- capture consequential decisions and supersession (see Decision records);
- prefer versionable/regenerable diagram sources;
- keep only diagram levels that add durable value.

## Decision records

A decision record preserves rationale that is hard to recover from the code: the context, the options considered, the choice, and its consequences [Nygard2011; MADR4].

- **Threshold.** Record a decision only when it is architecturally significant (structure, cross-cutting concerns, external contracts), hard to reverse, and a reasonable alternative was rejected. Typical examples: a framework, datastore, bounded-context boundary, API or protocol, authorization model, or build and deploy topology. Explain reversible, local, or obvious choices next to the code or document they affect.
- **Authority.** A record states what people decided. Create or supersede one only when the user asks for that record; otherwise propose it, and do so while the decision is still cheap to change.
- **Content.** One decision per record, short (Nygard: one or two pages). Name the negative consequences, not only the benefits, and the quality attributes affected. State how compliance will be confirmed: a test, review gate, fitness function, or lint rule.
- **Lifecycle.** `proposed` until the deciders accept it; `accepted`, `rejected`, `deprecated` (no replacement), or `superseded by <record>`. Accepted records are immutable apart from status and links: a change of mind is a new record that supersedes the old one. Numbers are never reused, and superseded or deprecated records are kept.
- **Placement.** Follow the project's existing location, numbering, file naming, and language. MADR's default location is `docs/decisions/`.
- **Local convention (my-claude-code).** Records live in `docs/adr/` as `NNNN-<kebab-title>.md` with four-digit numbers. Front matter is `status` (`Proposed`, `Accepted`, `Deprecated`, or `Superseded by NNNN`, capitalized), `date` (`YYYY-MM-DD`), and `deciders`; the heading is `# NNNN. <title>`, and the body is written in Japanese. This overrides the lower-case MADR status values and the English template headings above; it was carried over from the retired `adr` skill (see `archive/adr/`).
- **Numbering.** When the project has no convention, scan the decision directory for the highest `NNNN`, use the next number zero-padded to four digits, and create the directory if it is absent. Never reuse a number, even for a rejected or superseded record.
- **Language.** Write the record in the language of the current conversation unless the project's existing records use another; the template's headings are English and are translated to match.

## Evidence and uncertainty

Never fill gaps with invented facts. Distinguish when material:

- verified vs inferred;
- current vs historical;
- requirement vs implementation;
- observed behavior vs intended behavior;
- accepted decision vs proposal;
- known vs assumed vs unknown.

## Research projects

Where applicable, preserve enough metadata/provenance to answer:

- what produced the artifact;
- from which inputs;
- using which process/software/environment/version;
- when;
- by which person or agent where relevant;
- which artifact supersedes it.

Use FAIR as the stewardship goal, W3C PROV for formal provenance when useful, and RO-Crate when structured research-object packaging adds value.

## Background

These practices follow the living-documentation approach of keeping knowledge close to, and verified against, the artifacts it describes [Martraire2019], including executable specifications [Adzic2011] and documentation managed as code [Cadavid2023]. Engineers consult documentation selectively and often find it out of date yet still use it [Lethbridge2003]; [Theunissen2022] maps how documentation is practised in continuous software development, where documents must keep pace with frequent change. The emphasis here on accurate, well-located, verifiable knowledge over exhaustive volume is an inference from these sources, not a finding of any one of them. Keys refer to [bibliography.bib](bibliography.bib).
