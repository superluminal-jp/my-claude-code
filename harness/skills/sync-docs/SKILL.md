---
name: sync-docs
description: Keeps documentation consistent with the code, configuration, and decisions it describes, and audits existing documentation for drift. Use when asked to update documentation for a change, to find which documents a change left out of date, or to check a README, guide, changelog, or reference against the code. Not for the routine one-document update that is part of implementing a change, nor for structuring the prose of a single document.
---

# Sync documentation

A document that disagrees with the code is worse than none, because readers trust it. Documentation changes in the same change as the thing it describes.

## For a change in progress

1. **List what the change alters that someone outside the code relies on:** commands and flags, configuration keys and defaults, environment variables, API routes and schemas, file formats, install or deploy steps, required versions, user-visible behavior, architecture.

2. **Find where each is documented.** Search for the names involved rather than guessing which file is affected:

   ```sh
   git diff --name-only <base>...HEAD        # what changed
   grep -rn --include='*.md' -e '<flag-or-key-or-command>' .
   ```

   Look in: the root and nested READMEs, `docs/`, the changelog, API descriptions (OpenAPI, JSON Schema), example configuration files, comments on public interfaces, CLI help text, and decision records.

3. **Update each place** so it states what the code now does. Use the document's existing style and language. Run every changed example or command, or mark it as not run.

4. **Follow the project's conventions for records:** add a changelog entry when the project keeps a changelog; write a decision record with the `record-decision` skill when the change makes a decision later readers will need the reason for. A decision record that was accepted is history; supersede it rather than editing it.

5. **Report** each document updated, each one checked and found correct, and - when nothing documented changed - that fact in one line with the reason.

## For an audit

1. Set the scope with the person: which documents, against which code.
2. For each document, extract its checkable claims: commands, paths, option names, defaults, versions, links, described behavior.
3. Check each claim against the source: does the path exist, does the command run, does the option exist with that default, does the link resolve.
4. Report findings as a table - document and line, the claim, what the source shows, and the proposed correction - ordered with claims that would mislead a user first. Fix them only when asked.

## Guidelines

- Write documentation where it will be found: beside the thing it describes, linked from its parent README.
- State a fact in one place and link to it from others; copies drift apart.
- Describe what is, in the present tense. Plans and history belong in issues, changelogs, and decision records.
- Prefer a tested example to a description of one.

## Done when

- Every documented fact the change altered now matches the code, or is reported as an open item.
- Changed examples and commands were run, or are marked as not run.
- The report separates updated, checked-and-correct, and unverified documents.
