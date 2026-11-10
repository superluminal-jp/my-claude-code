# Normative basis by document type

Read when creating or revising one of the document types below. Each standard applies to its own type of document; use the project's existing format in every case. Applicability, interpretation, and official sources for each standard are in [standards.md](standards.md).

| Document type | Basis | What to do |
|---|---|---|
| Lifecycle information item (a plan, specification, description, procedure, record, or report) | ISO/IEC/IEEE 15289 | Give the item the purpose and content that 15289 assigns to its type |
| Any documentation work in a project that has adopted it | ISO/IEC/IEEE 12207 | Carry the work out within the project's information-management, configuration-management, and maintenance processes. Where 12207 is not adopted, use it as a checklist of lifecycle concerns |
| Architecture description | ISO/IEC/IEEE 42010 | Identify the stakeholders and their concerns, and express the description through viewpoints and views that address them. Structure it with arc42 and draw it with C4 unless the project uses other conventions |
| Decision record | ADR practice, MADR 4.0.0 | See the rules below |
| Information for users | ISO/IEC/IEEE 26514 | Design it for its audience and their tasks, and keep it consistent with the delivered behavior |
| Published data, software, or workflows of a research project | FAIR principles; W3C PROV; RO-Crate | Pursue the FAIR principles. Record provenance with W3C PROV and package with RO-Crate when structured provenance or packaging adds value |

## Decision records

A decision qualifies for a record only when it is architecturally significant (structure, a cross-cutting concern, or an external contract), hard to reverse, and a reasonable alternative was rejected. Explain other choices next to what they affect.

- Do not create or supersede a decision record unless the person explicitly asks for that record. Otherwise propose it in the report, before the decision becomes costly to reverse.
- When asked, follow the project's existing location, numbering, language, and format; otherwise use `templates/adr.md` from this skill, with the location agreed with the person. Record one decision per record, keep the status `proposed` until the person accepts it, and state how compliance will be confirmed.
- Never reuse a number, change the substance of an accepted record, or delete a superseded or deprecated one. Record a new decision that supersedes it.

## Conformance claims

Do not state that the project or a document conforms to a standard unless the project has declared that conformance and the evidence can be checked. This skill does not contain the standards' texts. When exact clause requirements matter, ask for the project's licensed copy or its tailoring decisions instead of reconstructing clauses from memory.
