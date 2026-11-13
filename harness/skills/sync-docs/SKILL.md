---
name: sync-docs
description: Keep documentation consistent with code, specifications, decisions, and research artifacts as they change, and audit existing documentation for drift, using bundled read-only scripts that list the documents a change may leave out of date. Use when implementing or reviewing a change that affects behavior, interfaces or API schemas, configuration, deployment, architecture or decision records, a README or user or operational guide, a change log or release notes, or research provenance; when asked for a documentation drift audit; and when asked to declare, check, or build the documentation tree of a repository, a README for the repository, each product, and each feature folder, linked parent to child. Not for a change with no observable or documented effect, and not for structuring the prose of a single document.
compatibility: Python 3.9 or later. Git is optional and enables change audits and ignore-aware scanning.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: updated documents and a documentation-impact report
---

# Synchronize documentation

Documentation is part of the change it describes: it is versioned, reviewed, checked, and updated together with the implementation. A document update this skill requires is part of the requested work, not an unrequested addition.

## For every change

- Determine the documentation impact before declaring the change done, and update the affected documents in the same change.
- Prefer generating, extracting, and validating from the authoritative source over duplicating prose.
- Never invent a missing fact. Mark unknown, assumed, inferred, proposed, historical, and verified information distinctly when it matters.
- Do not declare completion while implementation, specifications, evidence, and documentation disagree. Report what remains unresolved.
- Respect the project's existing structure and conventions. Keep project artifacts in the project, never in this skill's directory.
- Create a document only when the change adds a new public contract (a command, option, setting, API, or module) and no related document covers it. Create at most three new files per change and propose the rest in the report. A README that the declared documentation tree requires for a new node is part of the change and does not count toward that limit.
- Never create or supersede a decision record unless the person asks for that record; a request to implement the decision is not such a request. Propose it in the report instead. Never start a change history the project does not keep.
- Precedence when requirements conflict: law, contracts, organizational policy, and explicit project requirements; then the project's conventions; then the standards in `references/standards.md`; then this skill's defaults. Keep the higher one and report the conflict.

If the change alters no observable behavior, interface, configuration, operation, decision, or documented claim, write `Documentation impact: none - <reason>` and stop.

## Steps

1. **Inspect.** Find the project's documentation, specifications, tests, decision records, change history, generated artifacts, and conventions.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/inspect_project.py" --root "${CLAUDE_PROJECT_DIR}"`
2. **Locate authority.** Identify the authoritative source for each affected fact or contract (`references/practices.md#source-of-truth`).
3. **Assess impact.** List the changed artifact classes and impact hints; add `--base <target branch>` to cover the whole branch. Treat each hint as a question to answer, not a verdict.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/audit.py" --root "${CLAUDE_PROJECT_DIR}"`
   Then list the documents next to the changed files. Update each one, or name its path in the final message with the reason it needs no change.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/find_related.py" --root "${CLAUDE_PROJECT_DIR}"`
4. **Update together.** Change the implementation and the affected documents in one change, in the project's conventions.
   - When a public contract changes in a file whose stack keeps its reference documentation in the file (docstrings, doc comments, parameter descriptions), update it there in that stack's form (`references/practices.md#stack-conventions`).
   - When creating or revising a lifecycle information item, an architecture description, a decision record, user documentation, or a published research artifact, read `references/normative-basis.md` first.
   - Use `templates/` only when the project has no convention and a new artifact is needed.
   - When the project keeps a change history and the change is user-visible, breaking, or a deprecation, add an entry in the project's format, with migration notes for a breaking change.
5. **Check.** Run the link checker and the project's own tests, documentation builds, schema checks, linters, and generators. Fix failures and run again. Stop when every check passes, or when a failure remains after two fixes or lies outside this change; report it instead of continuing.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/check_links.py" --root "${CLAUDE_PROJECT_DIR}" --changed`
   When the project declares a documentation tree (`tree` in `.living-documentation.json`), also run the tree check and fix every error. A new node needs a README from the template of its kind, linked from its parent's README and back (`references/practices.md#documentation-tree`).
   `python3 "${CLAUDE_SKILL_DIR}/scripts/check_tree.py" --root "${CLAUDE_PROJECT_DIR}"`
   Without Git, omit `--changed`. If a check cannot run, say which and why. These checks confirm links and builds, not that the documentation is correct: for a breaking change or a new or changed public contract, have a subagent with a fresh context compare the documentation with the diff and report only gaps that affect correctness.
6. **Report** in the format below. Report drift that existed before the change; fix it only when it is in scope or the person asks.

For a drift audit with no change in hand, run steps 1, 3 (with `--base`), 5, and 6, and change nothing unless asked.

If a command still shows a literal `${...}` placeholder, use the directory that contains this file and the repository root.

## Build a documentation tree

Use this procedure only when the person explicitly asks to build the documentation tree of a repository: one README for the repository, each product, and each feature folder, linked parent to child and back. Otherwise keep an existing tree with the steps above.

1. **Declare.** Run `check_tree.py` in a project without a declaration to list candidate patterns per kind. Show them to the person, and write `tree` into `.living-documentation.json` only after the person has confirmed or corrected them.
2. **Create.** Give every node that lacks a `README.md` one from the template of its kind: `templates/readme-repository.md`, `templates/readme-product.md`, or `templates/readme-feature.md`. Replace every `{{...}}` text and every `replace:` link target, repeat the child line once per child node, and drop a list of children that would stay empty. In this procedure only, the limit of three new files does not apply.
3. **Fill only what you verified.** Write a fact only when a file of the project, or the output of a command such as `git log`, states it, and keep that source for the report: the path and line, or the command and its output. Never infer a purpose, a boundary, or a rationale from a name or a guess: leave it as `TODO(unfilled): <what is missing and who or what can settle it>`.
4. **Check.** Run `check_tree.py` and `check_links.py`, fix every error they report, and confirm that no `{{` and no `replace:` remains in the new READMEs: neither script reports one left in a list that needs no link.
5. **Report** the README files created, the source of each fact written in them, and every remaining unfilled item, read from the READMEs: `check_tree.py` keeps warning, on every run, how many each README still holds.

## Report format

```text
Documentation impact
- Updated: <file> - <what changed and why>; agrees with <authoritative source>
- Created: <file> - <what it documents and why no existing document fit>; agrees with <authoritative source>
- No change needed: <area> - <reason>
- Unresolved: <document> - <how it disagrees with its authoritative source>; <what would resolve it>
- Unverified: <document or claim> - <the evidence that would settle it>
- Proposed decision record: <title> - <why it qualifies; the person decides whether to record it>
- Checks: <command> - <its result, or why it could not run>
```

Keep the heading `Documentation impact` in English in every language, and omit empty lines. An `Updated` or `Created` line claims that the document now agrees with the authoritative source of step 2. Editing a document is not evidence that it is correct: when that agreement was not checked, list the document under `Unverified`.

## Done when

- Every document that `find_related.py` listed was updated, or is named in the report with the reason it needs no change.
- The link checker and the project's own checks pass, or each failure is reported with why it remains.
- When the project declares a documentation tree, `check_tree.py` reports no error.
- The report is given in the format above, with no `Updated` line for a document whose agreement was not checked.

## Bundled files

| File | Read or run when |
|---|---|
| `references/practices.md` | Deciding the authoritative source, where a document belongs, a stack's own documentation form, or how to mark uncertainty (steps 2 and 4) |
| `references/normative-basis.md` | Creating or revising a lifecycle item, architecture description, decision record, user documentation, or research artifact (step 4) |
| `references/standards.md` | Checking which standard applies, its precedence, or its official source |
| `references/bibliography.bib` | Citing a source in a document |
| `scripts/` | Steps 1, 3, and 5, and building a documentation tree. Standard library only; no network; read-only Git commands; no project file is written |
| `templates/` | The project has no convention for a new artifact; `readme-*.md` when a node of the documentation tree needs its README |
| `schemas/config.schema.json` | Writing `.living-documentation.json`, the project file that corrects the scripts' classification and declares the documentation tree |
