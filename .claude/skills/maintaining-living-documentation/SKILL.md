---
name: maintaining-living-documentation
description: Keeps documentation consistent with code, specifications, decisions, and research artifacts as they change, following ISO/IEC/IEEE 12207, 15289, 42010, and 26514, Docs-as-Code, arc42, C4, ADRs, and FAIR/W3C PROV/RO-Crate for research. Use when implementing or reviewing changes that affect behavior, interfaces or API schemas, configuration, deployment, architecture or ADRs, README/user or operational guides, CHANGELOG or release notes, or research provenance, and for documentation drift audits. Not needed for changes with no observable or documented effect.
compatibility: Claude Code with Python 3.9+. Git is optional and enables change audits and .gitignore-aware scanning. Project-root substitution needs Claude Code v2.1.196+. Loads as a plugin with an enforcing Stop hook when placed in a skills directory. The scripts are plain CLIs usable by other agents and CI.
---

# Living Documentation

Maintain documentation as part of every relevant change. MUST, SHOULD, and MAY follow RFC 2119. Documentation updates required here are part of the requested work, not an unrequested addition. These instructions apply for the rest of the task, not only to the next step.

## Normative basis

Precedence: law, contracts, organizational policy, and explicit project requirements; then the project's established conventions; then the standards below; then this Skill's defaults. When requirements conflict, keep the higher-precedence one and report the conflict.

1. **Docs-as-Code.** MUST version, review, validate, and update documentation together with the implementation it describes.
2. **Lifecycle information — ISO/IEC/IEEE 15289.** When creating or revising a lifecycle information item (plan, specification, description, procedure, record, report), MUST give it the purpose and content that 15289 assigns to that item type, in the project's existing format.
3. **Lifecycle processes — ISO/IEC/IEEE 12207.** Where the project or organization has adopted 12207, MUST carry out documentation work within its information-management, configuration-management, and maintenance processes. Otherwise use it as a checklist of lifecycle concerns.
4. **Architecture — ISO/IEC/IEEE 42010.** When creating or revising an architecture description, MUST identify its stakeholders and concerns and express it through viewpoints and views that address them. SHOULD structure it with arc42 and visualize it with C4, unless the project uses other conventions.
5. **Decision records — ADR, MADR 4.0.0.** A decision qualifies for a record only when it is architecturally significant (structure, cross-cutting concerns, or external contracts), hard to reverse, and a reasonable alternative was rejected; explain other choices next to what they affect.
   - MUST NOT create or supersede a decision record unless the user explicitly asks for that record. A request to implement the decision is not such a request. Otherwise propose the record in the report, before the decision becomes costly to reverse.
   - When asked, MUST follow the project's existing location, numbering, language, and format (otherwise `${CLAUDE_SKILL_DIR}/templates/adr.md`, with the location agreed with the user), record one decision per record, keep the status `proposed` until the user accepts it, and state how compliance will be confirmed.
   - MUST NOT reuse a number, change the substance of an accepted record, or delete a superseded or deprecated one; record a new decision that supersedes it.
   - If a dedicated decision-record skill is available, follow its procedure.
6. **User information — ISO/IEC/IEEE 26514.** When creating or revising information for users, MUST design it for its audience and their tasks according to 26514 and keep it consistent with the delivered behavior.
7. **Research artifacts.** For data, software, and workflows the project publishes, MUST pursue the FAIR principles. SHOULD record provenance with W3C PROV and package with RO-Crate when structured provenance or packaging adds value.
8. **Conformance claims.** MUST NOT state that the project or a document conforms to a standard unless the project has declared that conformance and the evidence can be checked. This Skill does not contain the standards' texts; when exact clause requirements matter, ask for the project's licensed copy or tailoring decisions instead of reconstructing clauses from memory.

Applicability, interpretation, and sources for each standard: [references/standards.md](references/standards.md).

## For every change

- Determine the documentation impact before declaring the change done.
- Update affected documentation in the same change.
- Prefer generation, extraction, and validation from authoritative sources over duplicated prose.
- Never invent missing facts. Mark unknown, assumed, inferred, proposed, historical, and verified information distinctly when it matters.
- Do not declare completion while implementation, specifications, evidence, and documentation disagree. Report what remains unresolved.
- Discover and respect the project's existing structure. Keep project artifacts in the project, never inside this Skill directory.

If the change alters no observable behavior, interface, configuration, operation, decision, or documented claim (formatting, comments, a refactor that keeps every documented contract), write `Documentation impact: none — <reason>` and stop. Do not add documentation the change does not need.

## Workflow

Track these steps in a task list or a copied checklist:

```
Documentation progress:
- [ ] 1. Inspect project conventions
- [ ] 2. Locate authoritative sources
- [ ] 3. Assess impact
- [ ] 4. Update implementation and documentation together
- [ ] 5. Run checks, fix, and re-run until they pass
- [ ] 6. Report with evidence
```

1. **Inspect.** Find the project's documentation, specifications, tests, decision records, change history, generated artifacts, and conventions (also CONTRIBUTING, documentation build configuration, and CI).
   `python3 "${CLAUDE_SKILL_DIR}/scripts/inspect_project.py" --root "${CLAUDE_PROJECT_DIR}"`
2. **Locate authority.** Identify the authoritative source for each affected fact or contract ([references/practices.md](references/practices.md#source-of-truth)).
3. **Assess impact.** In a Git worktree, list changed artifact classes and impact hints; add `--base <target branch>` to cover the whole branch. Treat each hint as a question to answer, not a verdict.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/audit.py" --root "${CLAUDE_PROJECT_DIR}"`
4. **Update together.** Change the implementation and the affected knowledge in one change, reusing the project's conventions. Use `${CLAUDE_SKILL_DIR}/templates/` only when the project has no applicable convention and a new artifact is needed. When the project keeps change history and the change is user-visible, breaking, or a deprecation, add an entry in the project's format, with migration notes for breaking changes.
5. **Check.** Run the link checker and the project's own tests, documentation builds, schema checks, linters, and generators. Fix failures and re-run.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/check_links.py" --root "${CLAUDE_PROJECT_DIR}" --changed`
   `check_links.py` checks only local links and anchors in Markdown. Without Git, omit `--changed`; for root-relative links (`/path`), pass `--site-root`. If a check cannot run, say which one and why instead of reporting it as passed. For changes to architecture descriptions, specifications, or user documentation, MAY have a subagent compare the documentation with the diff in a fresh context and report only gaps that affect correctness.
6. **Report** in the format below. Report pre-existing drift found along the way; fix it only when it is in scope or the user asks.

Run the commands as written; a project can pre-approve them with permission rules (README.md). If a command still contains a literal `${...}` placeholder (older Claude Code or another agent runtime), use the directory containing this SKILL.md and the repository root (`git rev-parse --show-toplevel`, otherwise the working directory).

## Completion report

```
Documentation impact
- Updated: <file> — <what changed and why>
- No change needed: <area> — <reason>
- Unresolved: <inconsistency or uncertainty> — <what would resolve it>
- Proposed decision record: <title> — <why it qualifies; the user decides whether to record it>
- Checks: <command> — <its result, or why it could not run>
```

Keep the heading `Documentation impact` in English in every language; the Stop-hook gate looks for it. Omit empty lines.

## References

- [references/standards.md](references/standards.md): applicability map, precedence, interpretation, and official links for each standard and practice.
- [references/practices.md](references/practices.md): source of truth, change coupling, change history, minimality, decision records, evidence and uncertainty, research provenance.
- [references/bibliography.bib](references/bibliography.bib): bibliographic metadata.

## Enforcement

When this folder is in `~/.claude/skills/` or a project's `.claude/skills/`, Claude Code loads it as a plugin: `hooks/hooks.json` adds the mandatory rule at session start and runs the Stop-hook gate (`scripts/stop_gate.py`). A project can set `"enforcement": "warn"` or `"off"` in `.living-documentation.json`. README.md describes the enforcement levels, CI, and evals.

## Bundled tooling

The scripts use only the Python standard library, never access the network, never write project files, and run only read-only Git commands. Results are advisory; the project's CI and conventions remain authoritative. `.living-documentation.json` at the project root corrects classification and sets enforcement (see `schemas/config.schema.json`).
