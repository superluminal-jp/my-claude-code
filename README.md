# my-claude-code

Reusable Claude Code configuration that enforces the latest official specifications
and best practices from https://code.claude.com/docs/.

## What this does

- **CLAUDE.md** — Persistent instructions loaded every session: code quality rules,
  security constraints, response style, MCP server usage
- **.claude/settings.json** — Project-level settings with safe defaults, permission
  allowlist/denylist, and hook wiring
- **.claude/rules/** — Focused rule files, auto-loaded by Claude Code
- **.claude/hooks/pre-bash.sh** — Blocks dangerous Bash commands at runtime
  (force push, `rm -rf`, `git clean -f`, `curl | bash`)

## How to use in a project

### Option A: Copy

```sh
cp -r path/to/my-claude-code/.claude your-project/
cp path/to/my-claude-code/CLAUDE.md your-project/
```

### Option B: Import via CLAUDE.md

Add to your project's `CLAUDE.md`:

```markdown
@/absolute/path/to/my-claude-code/CLAUDE.md
```

### Option C: User-level global config

Place `CLAUDE.md` at `~/.claude/CLAUDE.md` to apply across all projects.

## MCP Servers

Configured in `.mcp.json`, auto-approved via `enableAllProjectMcpServers: true`.

| Server                       | Transport | Package / URL                                        | Version |
|------------------------------|-----------|------------------------------------------------------|---------|
| `aws-knowledge`              | HTTP      | `https://knowledge-mcp.global.api.aws`               | —       |
| `aws-documentation`          | stdio     | `awslabs.aws-documentation-mcp-server`               | 1.1.20  |
| `bedrock-agentcore`          | stdio     | `awslabs.amazon-bedrock-agentcore-mcp-server`        | 0.0.16  |
| `strands-agents`             | stdio     | `strands-agents-mcp-server`                          | 0.2.7   |
| `google-developer-knowledge` | HTTP      | `https://developerknowledge.googleapis.com/mcp`      | —       |
| `microsoft-learn`            | HTTP      | `https://learn.microsoft.com/api/mcp`                | —       |

**Prerequisites:**
- `uv` must be installed for the four `uvx`-based servers.
- `GOOGLE_DEV_KNOWLEDGE_API_KEY` env var must be set for `google-developer-knowledge`.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## File structure

```
my-claude-code/
├── CLAUDE.md                        # Main instructions (imports rules/)
├── .mcp.json                        # MCP server definitions (version-pinned)
└── .claude/
    ├── settings.json                # Permissions, hooks, MCP approval, model defaults
    ├── rules/
    │   ├── permissions.md           # Credential safety, destructive ops
    │   ├── hooks.md                 # Hook conventions and exit codes (reference only)
    │   ├── tools.md                 # Tool selection, parallel calls
    │   ├── advisor.md               # Advisor role: analysis, decisions, consulting
    │   ├── development.md           # TDD, documentation sync
    │   └── speckit.md               # Spec-driven development with spec-kit (opt-in)
    └── hooks/
        └── pre-bash.sh              # PreToolUse: block dangerous commands
```

## Customizing for a project

Override or extend in the project's own `.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": []
  }
}
```

Permission precedence (high → low):
managed > local (`.local.json`) > project (`settings.json`) > user (`~/.claude/settings.json`)

### Opt-in to spec-kit

Add to CLAUDE.md in projects that use spec-kit:

```markdown
@.claude/rules/speckit.md
```
