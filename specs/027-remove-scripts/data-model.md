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

### Installer managed path set
- **Members**: `hooks`, `rules`, `skills`, `agents`, `commands`, `CLAUDE.md`,
  and `settings.json`.
- **State rule**: Source present → destination replaced exactly; source absent →
  stale destination removed.
- **Boundary**: Any path outside the declared set remains user-owned and is
  preserved.

### Retired installer artifacts
- **Members**: `hooks/`, `commands/`, and `scripts/guardrails/` while absent
  from the repository.
- **Relationship**: Cleanup is part of exact synchronization for upgrades, not
  an installed current capability.

### Test suite inventory
- **Retained**: Codex drift/references, Digital Agency skill, MCP startup,
  subagent delegation, and the new isolated-home installer contract.
- **Removed**: Authenticated Claude prompt-evaluation runners and fixtures;
  orphan ubiquitous-language fixtures.

### draw.io capability
- **Prior components**: `.mcp.json` entry, skill, routing, coder pointer,
  installer comment, and MCP catalog documentation.
- **State**: Removed atomically so no live surface routes to an unavailable MCP.

## Removal ordering

Write the installer contract test first and observe failure. Then change the
installer and remove obsolete assets atomically; update live documentation in
the same change.
