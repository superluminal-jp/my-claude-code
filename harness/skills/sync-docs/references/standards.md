# Standards applicability map

Use these references according to the artifact and lifecycle scope. They are not a mandate to create one document per standard clause.

| Scope | Reference | Apply for |
|---|---|---|
| Software lifecycle | ISO/IEC/IEEE 12207:2026 | Lifecycle processes, activities, tasks, maintenance, operation, evolution, disposal |
| Lifecycle information | ISO/IEC/IEEE 15289:2019 | Purpose and content of systems/software lifecycle information items |
| Architecture description | ISO/IEC/IEEE 42010:2022 | Architecture descriptions, stakeholder concerns, viewpoints, views, model kinds, conformance |
| User information | ISO/IEC/IEEE 26514:2022 | Design, development, structure, content, and maintenance of information for software users |
| Architecture documentation practice | arc42 | Practical architecture documentation structure; docs-as-code usage |
| Architecture visualization | C4 model | System context, container, component, deployment/dynamic views as useful; avoid unnecessary low-level diagrams |
| Decision rationale | ADR practice (Nygard); MADR 4.0.0 | Significant, hard-to-reverse decisions: context, considered options, outcome, consequences, confirmation, supersession |
| Change history | Keep a Changelog 1.1.0 | Human-readable, versioned record of notable changes, deprecations, and removals |
| Version semantics | Semantic Versioning 2.0.0 | Meaning of version increments; signalling breaking changes |
| Research artifact stewardship | FAIR Guiding Principles | Findability, accessibility, interoperability, reusability of research digital objects |
| Provenance | W3C PROV-DM | Explicit provenance where derivation, responsibility, inputs, outputs, and process matter |
| Research-object packaging | RO-Crate Metadata Specification 1.3 | Structured packaging/metadata for research data, software, workflows, and related artifacts |

Editions listed are those current when this Skill was last revised. Before citing an edition, check the ISO page for a newer one (for example, a revision of 15289 was at committee-draft stage at that time).

## Precedence

1. Applicable law, contractual obligations, organizational policy, and explicit project requirements.
2. The target project's established authoritative specifications and conventions.
3. Applicable normative standards above.
4. Non-normative frameworks and practices above.
5. This Skill's fallback guidance.

When requirements conflict, do not silently choose. Preserve the higher-precedence requirement and report the conflict.

## Interpretation

- **ISO/IEC/IEEE 12207** defines lifecycle processes; it explicitly defers detailed lifecycle information-item content to ISO/IEC/IEEE 15289.
- **ISO/IEC/IEEE 15289** defines purposes/content of lifecycle information items, not a required repository layout or documentation technology.
- **ISO/IEC/IEEE 42010** constrains architecture-description structure/expression; it does not prescribe the architecture method, notation, tool, format, or recording medium.
- **ISO/IEC/IEEE 26514** applies specifically to information for users and treats its development/maintenance as lifecycle work.
- **FAIR** is a set of guiding principles, not itself a technical implementation standard.
- **arc42, C4, ADR/MADR, Keep a Changelog, and Semantic Versioning** are community practices and conventions, not ISO standards. Use them when they add stakeholder value and fit project conventions; do not introduce one into a project that follows a different convention.

## Official/current source links

- ISO/IEC/IEEE 12207:2026 — https://www.iso.org/standard/90219.html
- ISO/IEC/IEEE 15289:2019 — https://www.iso.org/standard/74909.html
- ISO/IEC/IEEE 42010:2022 — https://www.iso.org/standard/74393.html
- ISO/IEC/IEEE 26514:2022 — https://www.iso.org/standard/77451.html
- arc42 documentation — https://arc42.org/documentation/
- C4 model — https://c4model.com/
- ADR practice — https://adr.github.io/
- Nygard, "Documenting Architecture Decisions" (2011) — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- MADR 4.0.0 — https://adr.github.io/madr/
- Keep a Changelog 1.1.0 — https://keepachangelog.com/en/1.1.0/
- Semantic Versioning 2.0.0 — https://semver.org/spec/v2.0.0.html
- FAIR — https://doi.org/10.1038/sdata.2016.18
- W3C PROV-DM — https://www.w3.org/TR/prov-dm/
- RO-Crate 1.3 — https://w3id.org/ro/crate/1.3

Do not redistribute copyrighted ISO standard texts unless licensing permits it. Store bibliographic metadata, applicability guidance, and lawful excerpts instead.
