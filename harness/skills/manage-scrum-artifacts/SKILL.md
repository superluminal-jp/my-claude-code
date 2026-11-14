---
name: manage-scrum-artifacts
description: Keep a product's Scrum artifacts as files inside its repository - the Product Backlog with its Product Goal, the Definition of Done, and for each Sprint the Sprint Backlog with its Sprint Goal, the Increment, and the event records - placed from bundled Scrum Guide (2020) templates under the product folder's scrum/ directory, extended one Sprint at a time, and checked by bundled scripts. Use when asked to set up, add a Sprint to, check, or draft from Scrum artifacts kept in a repository. Do not use to diagnose or improve how a team practices Scrum, to facilitate an event, for Scrum artifacts kept in an external tool such as an issue tracker or a wiki, or for general project management.
compatibility: Python 3.9 or later.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a product's scrum/ directory placed from templates, a new Sprint folder, or a shape report with its errors and unset commitments
---

# Manage Scrum artifacts in a repository

The Scrum Guide (2020) defines three artifacts, each with a commitment: the Product Backlog with the Product Goal, the Sprint Backlog with the Sprint Goal, and the Increment with the Definition of Done. This skill keeps them as Markdown files next to the code, one set per product, so that people and agents read them from one known place and their history is versioned with the product. The Guide prescribes no folder, file name, or tool, so the layout is this skill's convention and is labeled as such wherever it appears.

## What the Scrum Team decides, never you

- Never decide or write these on your own: the order of the Product Backlog, the Product Goal, the Sprint Goal, the Definition of Done, which items a Sprint selects, an estimate, or who holds an accountability. Write one only when the person gives it to you as the team's decision, in their words.
- Leave what is not decided empty. The check reports an empty commitment as a warning; that warning is correct until the team decides, and filling the field to silence it is forbidden.
- A draft you are asked for (candidate items, questions, options) goes in the conversation or under a heading that says it is a draft for the team to decide. It never goes into a commitment field or reorders the backlog.
- Do not present the layout, the file names, or any practice the Guide does not state as a rule of Scrum.

## Steps

1. **Find the product folder.** A product is a unit built or delivered separately. Ask the person which folder when it is ambiguous; never guess from a folder name.
   - A repository with one product uses the repository root.
   - A repository that declares product folders, under `tree.products` in `.living-documentation.json` or as workspace members in `package.json` or `pyproject.toml`, uses those folders. List them and ask which products to set up.
2. **Place the product's artifacts**, once per product. Files that already exist are kept as they are.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" init --root "${CLAUDE_PROJECT_DIR}" --product <product folder>`
   Omit `--product` for the repository root. If the product folder has a `README.md`, add a link from it to `scrum/README.md`.
3. **Add a Sprint** when the person asks, with the start date they give. Never invent the date.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" sprint --root "${CLAUDE_PROJECT_DIR}" --product <product folder> --start <YYYY-MM-DD>`
   Add `--daily` only when the person wants Daily Scrum records kept.
4. **Write what the team decided.** Put each decision the person gives you into its file: read `references/conventions.md` for which file holds what. In `increment.md`, link to the pull requests, releases, or commits that are the Increment; do not copy issues or tasks into this folder.
5. **Check the shape** after every change to the folder, and fix every error. Report the warnings as they are.
   `python3 "${CLAUDE_SKILL_DIR}/scripts/check_artifacts.py" --root "${CLAUDE_PROJECT_DIR}" --product <product folder>`
   Exit 0 means no error, 1 lists errors, 2 means the product cannot be checked. The check reads shape only: it cannot tell whether the order serves the Product Goal or whether an Increment meets the Definition of Done.
6. **Report** the files created and kept, the check's result, each commitment still unset with who writes it, and anything you drafted that awaits the team's decision.

When asked to prepare for an event from these files (refinement, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective), read `references/event-preparation.md` first.

If a command still shows a literal `${...}` placeholder, use the directory that contains this file and the repository root.

Stop and ask the person when the product folder is unclear, when an existing layout differs from this one (move nothing on your own), or when a request would have you choose a value from the first list above.

## Done when

- Every product worked on has `scrum/product-backlog.md` and `scrum/definition-of-done.md`, and the check reports no error for it.
- No existing file was overwritten, moved, or deleted without the person asking for it.
- No commitment, order, selection, estimate, or accountability was written that the person did not give as the team's decision.
- The report names every unset commitment and every draft that awaits a decision.

## Bundled files

| File | Read or run when |
|---|---|
| `references/conventions.md` | Writing into the files, or explaining the layout: what the Guide states, what is this skill's convention, and every rule of the check |
| `references/event-preparation.md` | Asked to prepare for a Scrum event or for refinement from the files |
| `scripts/scaffold.py` | Steps 2 and 3. Writes only new files under the product's `scrum/` |
| `scripts/check_artifacts.py` | Step 5. Reads only; writes no file |
| `scripts/scrum_layout.py` | Never run directly: the layout shared by the two scripts |
| `templates/` | Never edited in place: the files the scaffold copies. `scrum-readme.md` becomes `scrum/README.md` |
