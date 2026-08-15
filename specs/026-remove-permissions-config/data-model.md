# Data Model: Remove the permissions Block Entirely

No runtime data entities — file deletions/edits and one new ADR.

## Entities

### `.claude/settings.json` `permissions` key
- **Relationship**: Independent of the `hooks`/`statusLine` keys spec-025 already removed. No ordering constraint with other entities.

### `.claude/settings.local.json` `permissions` key
- **Relationship**: Independent, personal/gitignored file. No ordering constraint.

### `.claude/rules/permissions.md`
- **Relationship**: Describes both files above. Edited in the same change so the policy document doesn't claim enforcement that no longer exists.

### README.md / README.ja.md Codex-comparison table + prose
- **Relationship**: Describes the same two files. The table's last "yes" row (added meaning by spec-025's edit) flips to "no."

### AGENTS.md "one guardrail" claim
- **Relationship**: Directly references the `permissions` block. Becomes false the moment it's deleted.

### `.claude/rules/git-workflow.md` "ask tier" claim
- **Relationship**: References the same `permissions.ask` array. Becomes false.

### `tests/run-codex-references.sh` RULE-09
- **Relationship**: Asserts `.permissions.deny` length. Its guarded invariant is now fully retired (spec-025 retired the hooks half, this feature retires the rest) — removed, not adjusted.

### New ADR (`docs/adr/0006-*.md`)
- **Relationship**: References ADR-0005 (unchanged) and documents this decision as a further reduction of what 0005 left standing.

## Removal ordering

Single atomic change, as with spec-024/spec-025 — no cross-file ordering constraint at commit time.
