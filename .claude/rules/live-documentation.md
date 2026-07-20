# Live Documentation Rules

Purpose: keep documentation truthful and co-located with the code it describes, across the whole lifecycle — not only as an after-the-fact patch. Applies when reviewing diffs/commits/PRs, when creating any Documentation Artifact, and before/during non-trivial work (see § 0). Documentation must never lie; sections 1–5 operationalize the Living Documentation approach (Martraire, 2019 — see [References](#references)) as five enforcement checks applied in every session: drift, separate-doc-PR, auto-generation, proximity, and no-redundancy. The five checks are this repo's own operationalization, not a canonical list from the source.

## 0. Documentation Across the Lifecycle (named standards)

Apply recognized documentation-process practices at each phase, from both the software-engineering and the project-management discipline — not only at close-out. Deviating from a named practice is fine — state the rationale (Core Principle #2, `.claude/CLAUDE.md`).

| Phase | Discipline | Practice / standard | Governs |
|---|---|---|---|
| Before work | Software eng. | ISO/IEC/IEEE 29148:2018 | requirements are unambiguous, verifiable, feasible before implementation starts (`rules/clarifier.md`) |
| Before work | Software eng. | README-Driven Development (Preston-Werner, 2010) | write the README/interface first — a "perfect implementation of the wrong spec is worthless" |
| Before work | Software eng. | arc42 (Starke & Hruschka, 2005) | template for architecture documentation on non-trivial design work |
| Before / at decision | Software eng. | MADR / Nygard ADRs | one-way-door decisions recorded with rationale before or as they're made (`adr` skill) |
| Before work | Project mgmt. | ISO 21502:2020 | project-management guidance across the life cycle, incl. what a project plan/business case must document |
| Before work | Project mgmt. | PMBOK® Guide, 7th ed. (PMI, 2021) | project charter, project management plan, and project documents (requirements/risk/stakeholder registers) drafted before execution |
| Before work | Project mgmt. | PRINCE2 (originated UK Cabinet Office; PeopleCert since 2021) | Project Initiation Documentation (PID) — business case, plan, quality/risk approach — baselined before a stage starts |
| During work | Software eng. | Docs as Code / *Docs Like Code* (Gentle, 2017) | docs versioned, reviewed, and updated in the same change as code, using the same tooling |
| During work | Software eng. | Living Documentation (Martraire, 2019) | docs stay truthful and co-located — operationalized as §§ 1–5 below |
| During work (structure) | Software eng. | Diátaxis (Procida, 2020) | organizes documentation output into tutorial / how-to guide / reference / explanation |
| During work | Project mgmt. | PRINCE2 management products | Highlight Reports / End Stage Reports track progress against the PID as work proceeds |
| Lifecycle-wide | Software eng. | ISO/IEC/IEEE 15289:2019 | defines required content for life-cycle documentation items across the whole process |
| Lifecycle-wide | Project mgmt. | ISO 10006:2017 | quality-management guidance for project documentation (e.g., the project quality plan) |
| User-facing docs | Software eng. | ISO/IEC/IEEE 26514:2022 | design & development requirements for information aimed at users |

## 1. Drift Detection

When reviewing a code diff or commit:
- Identify every changed source file that has a public contract (exported function, public method, API endpoint, CLI argument, schema field).
- For each such file, check whether a Documentation Artifact (docstring, README, spec, OpenAPI annotation) covering that contract is updated in the **same** diff.
- If a contract changed but its Documentation Artifact did not: Claude MUST flag this as a **Live Documentation violation (Drift)**, name the stale artifact by path, and refuse to pass the review until either:
  - The artifact is updated in the same change, OR
  - The developer provides an Override with a stated reason (see Override Handling below).
- Do NOT flag pure internal changes (private method renames, formatting, implementation-only refactors with no contract change).

## 2. Separate Documentation PR Detection

When reviewing a PR or diff that contains only Documentation Artifact changes (no source code changed):
- Ask: "Does this documentation describe code that was already shipped in a prior commit?"
- If yes: flag as a **Live Documentation violation** and recommend amending the original code commit to include the docs.
- If the developer confirms the separation is intentional (e.g., retroactive documentation sprint, onboarding docs, ADR): accept an Override with a stated reason and proceed.
- Do NOT flag standalone ADRs, onboarding guides, or architectural decision records that are not code-derivative.

## 3. Auto-generation Recommendation

When asked to write or update a Documentation Artifact (API reference, parameter list, schema description, type docs):
- First determine: can this artifact be produced automatically from the code (type signatures, annotations, docstrings, OpenAPI decorators)?
- If yes: identify the auto-generation path ("this can be produced by running `<tool>`") and recommend it. Decline to produce the hand-written version.
- If no auto-generation path exists in this project: proceed with hand-writing, and apply Proximity Enforcement (section 4).

## 4. Proximity Enforcement

When adding or placing any Documentation Artifact:
- Place it at the physically closest location to the code it describes:
  - Inline docstring if the language supports it (preferred)
  - `README.md` in the **same directory** as the source files
  - A co-located spec or contract file adjacent to the source
- If a developer proposes a remote or centralized location (top-level `docs/`, external wiki, separate repo): warn that this violates the Proximity principle and offer the nearest co-located alternative.

## 5. No Redundancy

When asked to create a Documentation Artifact:
- Check whether the same information already exists elsewhere in the repo (another doc, a docstring, a spec file, a contract file).
- If a duplicate exists: point to the existing source and decline to create the duplicate.
- Offer to add a cross-reference link if the developer needs discoverability from the new location.

## Override Handling

A developer may explicitly accept a Live Documentation violation by stating a reason.

- Accept an Override **only if** a reason is stated inline (e.g., "Override: emergency hotfix, docs will follow in #123").
- Record the acknowledgment: respond with "Override accepted: [stated reason]" before proceeding.
- Reject **silent overrides** ("just skip the doc check", "ignore this") — respond with: "Please state a reason for this override so it is on record."

## Out of Scope (do not enforce)

- Pure internal refactors with no public contract change.
- Generated files: migration files, build artifacts, lock files, compiled outputs.
- New standalone ADRs, onboarding docs, or design documents not derived from existing code.
- Test files that describe expected behavior — these are Executable Specifications; drift check applies only when the tested interface changes.

## References

- Cyrille Martraire, *Living Documentation: Continuous Knowledge Sharing by Design*, Addison-Wesley, 2019 — <https://www.oreilly.com/library/view/living-documentation-continuous/9780134689418/>
- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* (2nd ed.) — <https://www.iso.org/standard/72089.html>
- Tom Preston-Werner, "Readme Driven Development," 2010 — <https://tom.preston-werner.com/2010/08/23/readme-driven-development>
- arc42 template (Gernot Starke & Peter Hruschka), since 2005 — <https://arc42.org/>
- Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011; MADR 4.0.0 — see `adr` skill § References
- Anne Gentle, *Docs Like Code*, 2017 (3rd ed. 2022) — <https://www.docslikecode.com/>
- Daniele Procida, Diátaxis framework, 2020 — <https://diataxis.fr/>
- ISO/IEC/IEEE 15289:2019, *Systems and software engineering — Content of life-cycle information items (documentation)* — <https://www.iso.org/standard/74909.html>
- ISO/IEC/IEEE 26514:2022, *Systems and software engineering — Design and development of information for users* — <https://www.iso.org/standard/77451.html>
- ISO 21502:2020, *Project, programme and portfolio management — Guidance on project management* — <https://www.iso.org/standard/74947.html>
- Project Management Institute, *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)*, 7th ed., 2021 — <https://www.pmi.org/standards/pmbok>
- PRINCE2 (PeopleCert / formerly AXELOS), project management method — <https://www.axelos.com/certifications/propath/prince2-project-management>
- ISO 10006:2017, *Quality management — Guidelines for quality management in projects* — <https://www.iso.org/standard/70376.html>
