# AGENTS.md

Shared guidance for Codex CLI, deployed globally to `~/.codex/AGENTS.md` by `install.sh` (mirroring `.claude/` → `~/.claude/`). This file carries the items from this repository's cross-agent guardrail decision record (`specs/012-cross-agent-guardrail-migration/decision-record.md`) that are prose-appropriate for Codex CLI, plus the items feature 014 (`specs/014-codex-config-port/`) ported with real enforcement. Real enforcement (destructive-command blocking, pre-edit blocking, post-edit formatting, prompt-secret blocking, an allow-list for routine commands) is implemented as actual Codex CLI mechanisms, not prose — see "Enforced via hook or rule" below for what that covers.

## Tool use

- Prefer your editor/agent's dedicated file-read, search, and edit capabilities over shelling out to `cat`/`grep`/`sed` for the same job — dedicated tools give more reliable, structured results.
- Batch independent read-only operations (multiple file reads, disjoint searches, independent checks) in one turn instead of running them one at a time.
- For broad, open-ended exploration or research that would consume a lot of context, delegate it to an isolated worker and use only its summarized conclusion, rather than loading all the raw results into the main working context.

## Clarification

- Ask before acting when intent, scope, acceptance criteria, constraints, or a safety-sensitive choice is materially ambiguous. Proceed with a stated assumption only when the default is obvious, local, reversible, and low risk.
- Keep requirements testable: identify an observable outcome before implementing behavior, and stop if the specification conflicts with the requested change.

## Skill routing

- Before acting, read the matching project's skill instructions completely. In this repository, route work through these sources:
  - Code, behavior, configuration, or synchronized documentation changes → `coder` (`@.agents/skills/coder/SKILL.md`).
  - React/Tailwind public-service frontends or web dashboards using the Digital Agency Design System or dashboard guidebook → `digital-agency-frontend` (`@.agents/skills/digital-agency-frontend/SKILL.md`), after `coder` for implementation work.
  - Materially ambiguous requirements or acceptance criteria → `clarifier` (`@.agents/skills/clarifier/SKILL.md`).
  - Diagnosis of an existing document's argument structure → `minto-reviewer` (`@.agents/skills/minto-reviewer/SKILL.md`).
  - Rewriting an existing substantial draft into its final form → `minto-rewriter` (`@.agents/skills/minto-rewriter/SKILL.md`).
  - Building a document collaboratively from incomplete material → `minto-builder` (`@.agents/skills/minto-builder/SKILL.md`).
  - Architecturally significant, hard-to-reverse decisions → `adr` (`@.agents/skills/adr/SKILL.md`).
- Resolve compound work first: Digital Agency frontend implementation uses `coder` followed by `digital-agency-frontend`; code changes plus an existing-document update use `coder` followed by `minto-rewriter`, never either skill alone.
- Route a recognizable work category before generic ambiguity. A brief request that names a document and asks to create it uses `minto-builder`; brevity alone does not make it a `clarifier` task.
- For Spec Kit projects, invoke the applicable `speckit-*` workflow explicitly and read its `@.agents/skills/<skill-name>/SKILL.md`. Its command-specific playbook replaces the generic routing above.

## Git workflow

- Commit, push, or open a pull request only when requested. Use Conventional Commits (`<type>(<scope>)?: <imperative subject>`) and keep one logical change—including its tests and documentation—in each commit.
- Never use destructive git operations (`reset --hard`, force push, `clean -f`) without explicit approval. Keep feature branches short-lived and do not write directly to `main` or `master`.

## Live documentation

- Update documentation in the same change whenever public behavior, configuration, usage, or interfaces change. Keep documentation close to the artifact it describes and do not duplicate generated reference material by hand.
- Propose an ADR for an architecturally significant, hard-to-reverse decision with a rejected alternative; ADRs are immutable after acceptance and may only be superseded.

## MCP servers for AWS / GCP / Azure questions

| Server | Transport | Endpoint / package | Key use cases |
|---|---|---|---|
| `aws-knowledge` | HTTP | `https://knowledge-mcp.global.api.aws` | AWS knowledge base |
| `aws-documentation` | stdio | `awslabs.aws-documentation-mcp-server` | AWS official documentation search/fetch |
| `bedrock-agentcore` | stdio | `awslabs.amazon-bedrock-agentcore-mcp-server` | Amazon Bedrock AgentCore docs |
| `strands-agents` | stdio | `strands-agents-mcp-server` | Strands Agents framework docs |
| `google-developer-knowledge` | HTTP | `https://developerknowledge.googleapis.com/mcp` | Google developer knowledge base |
| `microsoft-learn` | HTTP | `https://learn.microsoft.com/api/mcp` | Microsoft Learn / Azure docs |

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, call the matching server before answering: AWS → `aws-knowledge` or `aws-documentation`; GCP → `google-developer-knowledge`; Azure → `microsoft-learn`. If the server is unreachable, say live documentation is unavailable, then answer from training knowledge. Incidental mentions of AWS/GCP/Azure in an otherwise generic question don't require a call. These servers are registered in `~/.codex/config.toml`'s `[mcp_servers.*]` block (generated by `install.sh` from this repository's `.mcp.json`). When `GOOGLE_DEV_KNOWLEDGE_API_KEY` is absent, the Google entry remains in the catalog but is deployed disabled.

## Editing conventions

- Editing CI/CD configuration (`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`): test in a feature branch first.
- Editing Claude Code settings (`.claude/settings.json`, `.claude/settings.local.json`): verify hook paths and permission rules still resolve.
- Editing production-looking configuration (`*.prod.*`, `*production*`, `*.env.production`): make sure changes are tested before they land.

## Requests

- Don't paste secrets (API keys, tokens, passwords, private key material) into a prompt — see "Enforced via hook or rule" below for the automated backstop.
- If a task looks like non-trivial implementation work and this project has no `.specify/` directory yet, suggest running `specify init` once — don't insist if declined.
- Keep Spec Kit current by running `specify init` (or this project's Spec Kit update flow) periodically, if this project uses Spec Kit.
- `shfmt`, `shellcheck`, `yamllint`, and `jq` are expected to be available in the environment for formatting and lint checks to work.
- Persist decisions, conventions, and durable facts learned while working so they can be reused later, rather than re-deriving them every session.
- A configuration-verification entry point equivalent to Claude Code's `/verify-config` is available as `/prompts:verify-config` from `~/.codex/prompts/verify-config.md`. Codex custom prompts are deprecated upstream; this compatibility entry remains explicit-only and should migrate to a skill if the Claude-side command is retired.

## Enforced via hook or rule (Codex CLI only)

The following are not just requests — Codex CLI blocks, gates, or auto-formats these via actual mechanisms registered in `~/.codex/config.toml`'s managed section (by `install.sh`, from this repository's `.codex/hooks/` adapters) and `~/.codex/rules/guardrails.rules`:

After installation, review and trust new or changed user hooks with `/hooks` in the Codex TUI. Codex skips non-managed command hooks until their current definition hashes are trusted; rerun this review whenever a hook changes.

- **Destructive commands** are blocked or routed to confirmation before they run (force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb patterns, `curl\|bash`, non-HTTPS requests, credential-path reads/writes, global package installs, `sudo`).
- **Editing `.git/` directly is blocked.**
- **Editing any file while on the `main`/`master` branch is blocked** — create a feature branch first.
- **Files are auto-formatted/linted after every edit**: `.sh` → `shfmt -w -i 2` + `shellcheck`; `.yaml`/`.yml` → `yamllint`; `.json` → syntax check.
- **Prompts containing obvious secrets are blocked** (AWS access key IDs, GitHub tokens, Slack tokens, Google API keys, private key headers).
- **Routine, read-only, or verification commands run without a confirmation prompt** (the repository's currently enumerated `tests/run-*.sh` suites, `scripts/check-mcp-consistency.sh`, `shellcheck`/`shfmt`/`jq`/`yamllint`, git read operations and `commit`); git write operations (`add`/`checkout`/`branch`/`stash`/`pull`) route to confirmation instead. New test runners must be added to `guardrails.rules` because Rules match exact argument prefixes rather than shell globs.

These behaviors are Codex CLI-specific enforcement, not general advice — they don't apply to other tools that might also read this file. Judgments that can't be expressed by Codex's native prefix-based Rules (e.g. detecting `rm -rf` embedded mid-command after `&&`) are covered by the hook adapters instead, which share their decision logic with Claude Code's own hooks via `scripts/guardrails/*.sh`.
