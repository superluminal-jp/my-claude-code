# AGENTS.md

Shared guidance for Codex CLI, deployed globally to `~/.codex/AGENTS.md` by `install.sh` (mirroring `.claude/` → `~/.claude/`). This file lives at the repo root — where Codex CLI actually reads a project-scope `AGENTS.md` from — with a `.codex/AGENTS.md` symlink back to this file for anyone browsing `.codex/` alongside `.codex/hooks/`. This file carries the items from this repository's cross-agent guardrail decision record (`specs/012-cross-agent-guardrail-migration/decision-record.md`) that are prose-appropriate for Codex CLI. Real enforcement (destructive-command blocking, pre-edit blocking, post-edit formatting) is implemented as actual Codex CLI hooks, not prose — see the "Enforced via hook" section below for what that covers.

## Tool use

- Prefer your editor/agent's dedicated file-read, search, and edit capabilities over shelling out to `cat`/`grep`/`sed` for the same job — dedicated tools give more reliable, structured results.
- Batch independent read-only operations (multiple file reads, disjoint searches, independent checks) in one turn instead of running them one at a time.

## MCP servers for AWS / GCP / Azure questions

| Server | Transport | Endpoint / package | Key use cases |
|---|---|---|---|
| `aws-knowledge` | HTTP | `https://knowledge-mcp.global.api.aws` | AWS knowledge base |
| `aws-documentation` | stdio | `awslabs.aws-documentation-mcp-server` | AWS official documentation search/fetch |
| `bedrock-agentcore` | stdio | `awslabs.amazon-bedrock-agentcore-mcp-server` | Amazon Bedrock AgentCore docs |
| `strands-agents` | stdio | `strands-agents-mcp-server` | Strands Agents framework docs |
| `google-developer-knowledge` | HTTP | `https://developerknowledge.googleapis.com/mcp` | Google developer knowledge base |
| `microsoft-learn` | HTTP | `https://learn.microsoft.com/api/mcp` | Microsoft Learn / Azure docs |

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, call the matching server before answering: AWS → `aws-knowledge` or `aws-documentation`; GCP → `google-developer-knowledge`; Azure → `microsoft-learn`. If the server is unreachable, say live documentation is unavailable, then answer from training knowledge. Incidental mentions of AWS/GCP/Azure in an otherwise generic question don't require a call.

## Editing conventions

- Editing CI/CD configuration (`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`): test in a feature branch first.
- Editing Claude Code settings (`.claude/settings.json`, `.claude/settings.local.json`): verify hook paths and permission rules still resolve.
- Editing production-looking configuration (`*.prod.*`, `*production*`, `*.env.production`): make sure changes are tested before they land.

## Requests

- Don't paste secrets (API keys, tokens, passwords, private key material) into a prompt.
- If a task looks like non-trivial implementation work and this project has no `.specify/` directory yet, suggest running `specify init` once — don't insist if declined.
- Keep Spec Kit current by running `specify init` (or this project's Spec Kit update flow) periodically, if this project uses Spec Kit.
- `shfmt`, `shellcheck`, `yamllint`, and `jq` are expected to be available in the environment for formatting and lint checks to work.
- Persist decisions, conventions, and durable facts learned while working so they can be reused later, rather than re-deriving them every session.
- For broad, open-ended exploration or research that would consume a lot of context, delegate it to an isolated worker and use only its summarized conclusion, rather than loading all the raw results into the main working context.

## Enforced via hook (Codex CLI only)

The following are not just requests — Codex CLI blocks or auto-formats these via actual hooks in this environment:

- **Destructive commands** are blocked or routed to confirmation before they run (force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb patterns, `curl\|bash`, non-HTTPS requests, credential-path reads/writes, global package installs, `sudo`).
- **Editing `.git/` directly is blocked.**
- **Editing any file while on the `main`/`master` branch is blocked** — create a feature branch first.
- **Files are auto-formatted/linted after every edit**: `.sh` → `shfmt -w -i 2` + `shellcheck`; `.yaml`/`.yml` → `yamllint`; `.json` → syntax check.

These four behaviors are Codex CLI-specific enforcement, not general advice — they don't apply to other tools that might also read this file.
