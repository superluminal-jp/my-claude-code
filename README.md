# my-claude-code

Reusable Claude Code **user-level** configuration that enforces the latest
official specifications and best practices from https://code.claude.com/docs/.

The entire `.claude/` directory is designed to be copied wholesale to
`~/.claude/`, making these settings, rules, hooks, and memory apply across
every project on the machine.

## What this provides

- **`.claude/CLAUDE.md`** — Persistent user memory loaded every session: code
  quality rules, security constraints, response style, MCP server usage
- **`.claude/settings.json`** — User-level settings with safe defaults,
  permission allowlist/denylist, and hook wiring
- **`.claude/rules/`** — Focused rule files referenced from `CLAUDE.md`
- **`.claude/hooks/pre-bash.sh`** — PreToolUse: blocks destructive git/`rm`,
  `curl | bash`, non-localhost `http://` for `curl`/`wget`, and reading
  `.ssh`/`.aws` or `*.pem`/`*.p12`/`*.pfx` via common read commands (see
  [`.claude/rules/permissions.md`](.claude/rules/permissions.md))
- **`scripts/check-mcp-consistency.sh`** — Verifies MCP names, URLs, and pinned
  versions across `.mcp.json`, `install-mcp.sh`, `settings.json`, and
  [`mcp.md`](.claude/rules/mcp.md) (requires `jq` on `PATH`)

## Install as user configuration

Copy the `.claude/` directory into your home directory, then register MCP
servers at user scope:

```sh
cp -r path/to/my-claude-code/.claude/. ~/.claude/
chmod +x ~/.claude/hooks/*.sh ~/.claude/install-mcp.sh
~/.claude/install-mcp.sh
```

The copy installs the user `CLAUDE.md`, `settings.json`, rules, and hooks in
one go. The `pre-bash.sh` hook path in `settings.json` resolves via
`$HOME/.claude/hooks/pre-bash.sh`, so it works immediately after the copy.
`install-mcp.sh` registers all six MCP servers at user scope via the
`claude mcp add -s user` CLI.

### Alternative: import via your own `CLAUDE.md`

If you prefer not to copy, import from any `CLAUDE.md`:

```markdown
@/absolute/path/to/my-claude-code/.claude/CLAUDE.md
```

## File structure

```
my-claude-code/
├── CLAUDE.md                       # Thin re-export: @.claude/CLAUDE.md (for in-repo development)
├── README.md
├── scripts/
│   └── check-mcp-consistency.sh    # MCP catalog drift check (jq required)
├── .mcp.json                       # Project-scope MCP server definitions (reference)
└── .claude/                        # <-- copy this directory's contents to ~/.claude/
    ├── CLAUDE.md                   # Main user memory (imports rules/)
    ├── settings.json               # Permissions, hooks, MCP approval, model defaults
    ├── rules/
    │   ├── permissions.md          # Credential safety, destructive ops
    │   ├── hooks.md                # Hook conventions and exit codes (reference only)
    │   ├── tools.md                # Tool selection, parallel calls
    │   ├── advisor.md              # Advisor role: analysis, decisions, consulting
    │   ├── development.md          # TDD, documentation sync
    │   ├── harness.md              # Patterns from "Harnessing Claude's Intelligence"
    │   ├── mcp.md                  # MCP server catalog (single source of truth for docs)
    │   └── speckit.md              # Spec-driven development with spec-kit (opt-in)
    ├── hooks/
    │   └── pre-bash.sh             # PreToolUse: block dangerous commands
    └── install-mcp.sh              # Register all MCP servers at user scope
```

## Verification

After changing `.mcp.json`, `.claude/install-mcp.sh`, `.claude/settings.json`
(MCP allowlist), or [`.claude/rules/mcp.md`](.claude/rules/mcp.md):

```sh
./scripts/check-mcp-consistency.sh
```

## MCP Servers

MCP servers are defined in `.mcp.json` for project-scope use. Full catalog
(transport, package versions, prerequisites): [`.claude/rules/mcp.md`](.claude/rules/mcp.md).

User-scope MCP servers are registered via the CLI (stored separately; not
installed by copying `.claude/` alone). Equivalent commands:

```sh
claude mcp add -s user aws-knowledge --transport http https://knowledge-mcp.global.api.aws
claude mcp add -s user aws-documentation -- uvx awslabs.aws-documentation-mcp-server@1.1.20
claude mcp add -s user bedrock-agentcore -- uvx awslabs.amazon-bedrock-agentcore-mcp-server@0.0.16
claude mcp add -s user strands-agents -- uvx strands-agents-mcp-server@0.2.7
claude mcp add -s user \
  --transport http \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp \
  --header "X-Goog-Api-Key: ${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}"
claude mcp add -s user microsoft-learn --transport http https://learn.microsoft.com/api/mcp
```

Or run `~/.claude/install-mcp.sh` after copying `.claude/` (see [Install](#install-as-user-configuration)).

## Overriding per project

User-level settings act as the baseline. Any project can extend or override in
its own `.claude/settings.json`:

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

Add to a project's `CLAUDE.md` when that project uses spec-kit:

```markdown
@~/.claude/rules/speckit.md
```
