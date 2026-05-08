# Implementation Plan: CLAUDE.md Configuration Improvements

**Branch**: `006-claude-md-mcp-effort-tui` | **Date**: 2026-05-09 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/006-claude-md-mcp-effort-tui/spec.md`

## Summary

Three targeted configuration changes: (1) strengthen the MCP usage rule in `rules/mcp.md` from "Prefer" to "MUST" for direct AWS/GCP/Azure questions; (2) raise `effortLevel` from `medium` to `high` in `.claude/settings.json`; (3) add `"tui": "fullscreen"` to `.claude/settings.json`. Settings changes are automatically distributed to user scope via `install.sh`.

## Technical Context

**Language/Version**: JSON (settings), Markdown (rules)  
**Primary Dependencies**: Claude Code CLI settings schema  
**Storage**: N/A  
**Testing**: Manual verification — open a new session, check effective effort/TUI, ask an AWS question and confirm MCP tool call  
**Target Platform**: Claude Code (macOS, cross-platform)  
**Project Type**: Configuration / documentation  
**Performance Goals**: N/A  
**Constraints**: Must not break existing project-level overrides or explicit CLI flags  
**Scale/Scope**: 2 files changed (`.claude/rules/mcp.md`, `.claude/settings.json`)

## Constitution Check

Constitution template is unpopulated — no project-specific gates to evaluate. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-claude-md-mcp-effort-tui/
├── plan.md              # This file
├── research.md          # Phase 0 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Files Changed

```text
.claude/
├── rules/
│   └── mcp.md           # Change 1: strengthen MCP usage rule
└── settings.json        # Changes 2 & 3: effortLevel + tui
```

**Structure Decision**: No new files or directories needed. All changes are in-place edits to existing files.

## Change Details

### Change 1 — `.claude/rules/mcp.md`: Strengthen MCP enforcement rule

**Current** (line 18):
```
Prefer these MCP servers over `WebSearch` / `WebFetch` for AWS, GCP, or Azure questions — they return first-party documentation and avoid drift from cached search results.
```

**New rule** (replace the single Usage rule section):
```markdown
## Usage rule

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, you MUST invoke the matching MCP server before answering:

- AWS question → `aws-knowledge` or `aws-documentation`
- GCP question → `google-developer-knowledge`
- Azure question → `microsoft-learn`

If the MCP server is unreachable, warn the user that live documentation is unavailable, then answer from training knowledge.

Incidental mentions of AWS/GCP/Azure in otherwise generic questions (e.g., "I'm deployed on AWS but my question is about Python loops") do not require an MCP call.
```

### Change 2 — `.claude/settings.json`: Raise effort level

Change `"effortLevel": "medium"` → `"effortLevel": "high"`.

### Change 3 — `.claude/settings.json`: Add TUI fullscreen default

Add `"tui": "fullscreen"` after the `"effortLevel"` line.

## Verification Steps

1. Run `install.sh` and confirm `~/.claude/settings.json` contains `"effortLevel": "high"` and `"tui": "fullscreen"`.
2. Open a new Claude Code session; confirm TUI renders fullscreen.
3. Ask a direct AWS question (e.g., "What Lambda runtimes does AWS support?"); confirm an `mcp__aws-*` tool call appears in the trace before the answer.
4. Ask a generic Python question that mentions AWS incidentally; confirm no MCP call is made.
5. Verify that explicitly passing `--effort medium` at the CLI overrides the default.
