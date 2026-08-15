# Data Model: Remove scripts/ Entirely

No runtime data entities — file deletions/edits and one new ADR.

## Entities

### `scripts/guardrails/` (4 files) + 4 dedicated test suites
- **Relationship**: Tests depend on the scripts existing; both deleted together, no ordering constraint (single atomic change).

### `scripts/check-mcp-consistency.sh`
- **Relationship**: Independent of the guardrails entity — no shared dependents. Referenced by README.md/README.ja.md and `.claude/rules/mcp.md` only.

### `install.sh`'s guardrails sync block
- **Relationship**: Depends on `scripts/guardrails/`'s removal to know what to clean up; becomes an unconditional cleanup step rather than a conditional sync.

### README.md / README.ja.md (bullets, tree, Verification list, Codex-comparison prose)
- **Relationship**: Describes both deleted entities across multiple independent locations.

### `.claude/rules/permissions.md`, `.claude/rules/mcp.md`
- **Relationship**: Each references one of the two deleted scripts as a policy-enforcement mechanism; both need their enforcement claim downgraded to policy-only.

### New ADR (`docs/adr/0007-*.md`)
- **Relationship**: References ADR-0005 and ADR-0006 (both unchanged) as the two prior steps in the same decision arc.

## Removal ordering

Single atomic change — no cross-file ordering constraint at commit time.
