# Living documentation (mandatory)

These rules apply to every change in this repository that affects behavior, interfaces or schemas, configuration, deployment, architecture or decisions, user or operational guidance, or research provenance. Documentation updates they require are part of the requested work, not an unrequested addition.

- Before finishing such a change, use the `maintaining-living-documentation` skill and follow its normative basis and workflow.
- Update affected documentation in the same change. If the project keeps change history (CHANGELOG, release notes, changelog fragments), add an entry for user-visible, breaking, or deprecating changes.
- Run the skill's `check_links.py --changed` and the project's own documentation checks, fix failures, and re-run. If a check cannot run, say which one and why.
- When a turn changed files, end its final message with the skill's completion report under the heading `Documentation impact`. Keep that heading in English even when replying in another language. If nothing needs documenting, write one line: `Documentation impact: none — <reason>`.
- Create or supersede a decision record (ADR) only when the user explicitly asks for it; otherwise propose it in the report.
- Never invent project facts or claim conformance to a standard the project has not declared. Report unresolved inconsistencies under `Unresolved` instead of claiming completion.
