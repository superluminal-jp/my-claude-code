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

## Layers, placement, and proximity

Where each kind of knowledge goes, for a project that has no convention of its own (the project's existing structure always wins; see the precedence in [standards.md](standards.md)). Each row of the table says whether it rests on material reviewed for this skill (**Sourced**, with a bibliography key) or is this skill's own **Design decision**. A design decision is a default, not a finding of any source.

| Layer | Reader's question | Placement | Form | Basis |
|---|---|---|---|---|
| Project entry (README) | What is this, and where do I start? | `README.md` at the repository root; localized copies as `README.<lang>.md` | Purpose, prerequisites, shortest path to a result; links onward and holds no detail | Sourced [GoogleSWE2020]: a landing page states its purpose and mainly links. The repository-root placement is a design decision |
| How-to and tutorial | How do I reach goal X? | `docs/`, one document per goal | Numbered steps with stated prerequisites; a tutorial assumes no prior knowledge | Sourced [GoogleSWE2020; Diataxis] |
| Reference | What exactly is the value, signature, or constraint? | Beside the authoritative source (schema, types, code comments); a human-readable copy is generated, not hand-copied | Complete and consistent, so a reader can scan it | Sourced [GoogleSWE2020; Diataxis] |
| Architecture | How do the parts fit together? | `docs/`, one architecture description | Zoom levels that answer a reader's question: system, container, component | Sourced [BrownC4; Arc42] for the levels. Keeping only the levels that add durable value is a design decision (see Minimality) |
| Decision records | Why was this chosen over the alternatives? | The project's existing location (see Decision records) | One decision per record | Sourced [Nygard2011; MADR4]; design documents also keep alternatives and trade-offs [GoogleSWE2020] |
| Change history | What changed between versions? | The project's existing change history (see Change history) | Per release, user-visible changes first | Sourced [KeepAChangelog] |
| Feature specification | What must this feature do, observably? | `specs/<feature>/` or the project's convention | Purpose, observable end state, acceptance scenarios | Design decision: matches the Spec Kit convention used with this skill; no source reviewed covers it |
| Code comments | What does this code do, and why is it like this? | Directly above the code they describe | Two kinds, below | Sourced [GoogleSWE2020; PEP8; LinuxKernelStyle] |
| Research provenance | What produced this artifact, from what inputs? | Next to the artifact, or in a metadata file | Structured provenance | Sourced [W3C_PROV_DM_2013; ROCrate2026] (see Research projects) |

### Code comments: two audiences

- **API comments** serve a user of the API, who cannot be assumed to know it as well as its author. They describe usage and leave out implementation details and design rationale. Keep their form consistent so readers can scan them, and start a function comment with a verb that says what the function does and returns [GoogleSWE2020].
- **Implementation comments** serve maintainers. They may assume more domain knowledge but should still say exactly why the code was written this way, because people leave projects [GoogleSWE2020]. Design rationale belongs in a design document, not in an API comment [GoogleSWE2020].
- **Do not restate the code.** An inline comment that repeats what the code plainly does is noise, while one that explains a non-obvious reason is useful [PEP8]. A comment that contradicts the code is worse than no comment, so update comments in the same change as the code [PEP8].
- **Sources differ in emphasis.** The Linux kernel style asks comments to say what code does rather than how, and to avoid comments inside function bodies in favor of one at the top of the function [LinuxKernelStyle]. Reading these together, this skill's design decision is: say at the top what a unit is for, add "why" comments only where the code cannot say it, and never narrate the code.

### Placement patterns

- **Next to what it documents.** Documents live under source control, are reviewed, and change in the same change as the code; a canonical document placed beside the source is easier to recognize as authoritative [GoogleSWE2020]. A directory of documents beside each API is one observed form of this [GoogleSWE2020].
- **Cross-API guides get their own set.** Documentation that spans several APIs has no natural place inside one of them; keep it in a set organized by topic [GoogleSWE2020].
- **Avoid an unowned shared wiki.** Google observed obsolete pages, duplicates, and no way to report errors in a wiki without owners [GoogleSWE2020].
- **One canonical document per topic.** When documents conflict, name the primary one and consolidate or deprecate the rest. Retire a document that no longer serves a purpose by removing it or marking it obsolete and pointing to the replacement [GoogleSWE2020]. Google also attaches review dates to documents; that is an observed practice, not a requirement of this skill.
- **Landing pages only link.** A landing page states its purpose and links elsewhere; user-facing and team-facing pages are kept apart [GoogleSWE2020].
- **One purpose per document.** Reference, design document, tutorial, conceptual document, and landing page are separate types that should not be mixed [GoogleSWE2020]; Diátaxis likewise separates documentation by the user need it serves [Diataxis].
- **Single-source the reference.** Reference documentation is generated from comments in the codebase so it has one source [GoogleSWE2020]. This supports preferring generation over hand-copied prose (see Source of truth).

### Proximity (design decision)

Proximity measures how close a document is to what it describes. It is this skill's **design decision**, used to rank documents that a change may affect (for example, `find_related.py` reports P1 candidates). It is not a finding of any source.

| Level | Where the document sits | Typical example |
|---|---|---|
| P0 | In the same file as what it describes | Code comments, docstrings, schema descriptions |
| P1 | In the same directory | A per-directory README or neighboring Markdown |
| P2 | In the project's documentation area | `docs/`, `specs/`, the decision-record directory |
| P3 | At the repository root | The root README and change history |
| P4 | Outside the repository | An external wiki or portal; avoid, and when unavoidable record which side is authoritative |

The **per-directory README (P1) is also a design decision**. The nearest sourced practice is a documentation directory beside each API [GoogleSWE2020], which does not mention a README.

No source reviewed presents a single hierarchy from the project README down to code comments. The sources describe different axes: C4 gives four levels of architectural abstraction (software system, container, component, code) [BrownC4]; the arc42 building block view descends through levels 1 to 3 [Arc42]; Diátaxis classifies documentation by four user needs [Diataxis]. The proximity scale combines placement with how often a document changes together with its subject, and should be read as a working default rather than an established model.

## Stack conventions

Reference documentation inside a file (proximity P0) takes the form that each stack's tooling reads. When a change alters a public contract in one of these files, update that in-file documentation in the same change; `find_related.py` lists the changed file's own comments as P0 advice. The project's existing convention still wins (see the precedence in [standards.md](standards.md)), and the documentation is still checked against its source of truth.

| Stack | In-file reference documentation | Mechanical check | Basis |
|---|---|---|---|
| Python | Docstrings on every module, on the functions and classes a module exports, and on public methods including `__init__`; a package is documented in its `__init__.py`. A function's docstring summarizes its behavior on one line, then documents its arguments, return values, side effects, exceptions raised, and restrictions on calling it | The project's docstring linter, if it has one | Sourced [PEP257] |
| TypeScript | `/** ... */` doc comments on exported APIs in TSDoc syntax. TSDoc is a Microsoft proposal to standardize TypeScript doc comments, not part of TypeScript, so the project's existing comment style wins where it differs | `eslint-plugin-tsdoc`, if the project uses it | Sourced [TSDoc] |
| Terraform | A one- or two-sentence `description` on every variable and output; a README in the root module and in each nested module; usage examples under `examples/` | None in the sources reviewed | Sourced [TFModuleStructure] |
| Bicep | `@description()` on each parameter whose purpose its name does not convey; the Azure portal shows the text as a tip during deployment | The linter rule `use-description-params`, which requires a non-empty description on every parameter when it is enabled | Sourced [BicepParameters; BicepLintDescription] |
| GitHub Actions | `description` for the action and for each of its inputs and outputs in `action.yml` or `action.yaml`; the metadata syntax requires all of them | None in the sources reviewed | Sourced [GHActionMetadata] |
| AWS CDK and React | The sources reviewed for this skill give no documentation convention for them. CDK code and its synthesized template are the source of truth for infrastructure facts (see Source of truth), and React components use the doc comments of their language | None | Design decision |

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
