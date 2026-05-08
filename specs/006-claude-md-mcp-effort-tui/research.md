# Research: CLAUDE.md Configuration Improvements

## Settings key names

- **Decision**: Use `"effortLevel": "high"` and `"tui": "fullscreen"` in `.claude/settings.json`
- **Rationale**: Both keys are confirmed in the Claude Code settings schema. `effortLevel` is already present in the file (currently `"medium"`). `tui` is a new key; valid values are `"fullscreen"` (alt-screen renderer) and `"default"` (main-screen renderer).
- **Alternatives considered**: No alternatives — these are the canonical key names.

## Settings distribution mechanism

- **Decision**: Change `.claude/settings.json` only; no changes to `install.sh` needed.
- **Rationale**: `install.sh` already runs `sync_path "settings.json"`, which copies `.claude/settings.json` to `~/.claude/settings.json`. The changes are automatically distributed on the next `install.sh` run.
- **Alternatives considered**: Patching `~/.claude/settings.json` directly — rejected because it would bypass the install workflow and be lost on the next sync.

## MCP enforcement wording

- **Decision**: Update `.claude/rules/mcp.md` — replace the single "Prefer" sentence with a two-tier rule: MUST for direct AWS/GCP/Azure questions; MAY use WebSearch/WebFetch for incidental mentions.
- **Rationale**: The existing rule uses "Prefer", which leaves room for skipping MCP. The spec requires "MUST" for direct questions while allowing flexibility for incidental mentions to avoid unnecessary MCP calls.
- **Alternatives considered**: Adding a new rule section to `CLAUDE.md` — rejected because `mcp.md` is the canonical location for MCP usage rules and is already `@`-imported into `CLAUDE.md`.
