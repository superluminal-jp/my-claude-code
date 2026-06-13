# Live Documentation Rules

Purpose: keep documentation truthful and co-located with the code it describes. Applies when reviewing diffs/commits/PRs or creating any Documentation Artifact. Documentation must never lie; these rules enforce the five Live Documentation principles (drift, separate-doc-PR, auto-generation, proximity, no-redundancy) in every session.

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
