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
- **`.claude/hooks/pre-bash.sh`** — PreToolUse/Bash: blocks destructive
  git/`rm`, `curl | bash`, non-localhost `http://` for `curl`/`wget`, reading
  and writing `.ssh`/`.aws` or `*.pem`/`*.p12`/`*.pfx` via common shell
  commands, and routes `sudo` to user confirmation (see
  [`.claude/rules/permissions.md`](.claude/rules/permissions.md))
- **`.claude/hooks/user-prompt-submit.sh`** — UserPromptSubmit: blocks
  prompts containing AWS/GitHub/Slack/Google API keys or private key blocks
- **`scripts/check-mcp-consistency.sh`** — Verifies MCP names, URLs, and pinned
  versions across `.mcp.json`, `install.sh`, `settings.json`, and
  [`mcp.md`](.claude/rules/mcp.md) (requires `jq` on `PATH`)

## Install as user configuration

Run the bundled installer from the cloned repo. It copies `.claude/` to
`~/.claude/`, makes hooks executable, and registers all MCP servers at user
scope:

```sh
bash path/to/my-claude-code/.claude/install.sh
```

Re-running is safe: it refreshes the copy and re-registers the MCP servers.
Hook paths in `settings.json` resolve via `$HOME/.claude/hooks/*.sh`, so they
fire for every project on the machine after install.

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
    ├── rules/                      # Always-on: loaded every session
    │   ├── permissions.md          # Credential safety, destructive ops
    │   ├── tools.md                # Tool selection, parallel calls
    │   ├── advisor.md              # Advisor role: analysis, decisions, consulting
    │   ├── clarify.md              # When and how to ask before acting
    │   ├── harness.md              # Patterns from "Harnessing Claude's Intelligence"
    │   └── mcp.md                  # MCP server catalog + usage rule
    ├── skills/                     # On-demand: loaded when relevant or /-invoked
    │   └── development/SKILL.md    # TDD + SDD + documentation sync (auto-activates on code changes)
    ├── hooks/
    │   ├── pre-bash.sh             # PreToolUse/Bash: block dangerous commands
    │   └── user-prompt-submit.sh   # UserPromptSubmit: block secret leaks
    └── install.sh                  # Copy to ~/.claude/ + register MCP servers
```

## Verification

After changing `.mcp.json`, `.claude/install.sh`, `.claude/settings.json`
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

Or run `~/.claude/install.sh` (see [Install](#install-as-user-configuration)) — the installer performs these registrations.

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

Run `specify init` in the project to install spec-kit. It registers the
`/speckit.*` slash commands, each of which carries its own playbook. The
`development` skill's SDD section applies regardless of whether spec-kit is
installed.
