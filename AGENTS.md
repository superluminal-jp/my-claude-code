# AGENTS.md

Shared guidance for Codex CLI. Codex reads this file natively — it composes instructions by walking from the git root down to the working directory and concatenating what it finds, so no installer and no import step is needed to make this content apply.

**Keep this file flat.** Codex does **not** expand `@path` imports (`openai/codex` issue #17401 is open), so it cannot delegate to `.claude/rules/*.md` the way `CLAUDE.md` does. Every rule that should reach Codex has to be written here.

Codex-side configuration that *is* generated — skills, MCP servers, hooks, subagents — comes from OpenAI's official import flow, not from this repository. See `README.md` § "Codex CLI support" for the procedure and for what it does and does not give you.

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
  - Scrum events, facilitation, impediment removal, team retrospectives → `scrum-master` (`@.agents/skills/scrum-master/SKILL.md`). Not for general project management — schedules, status reports, Gantt charts.
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

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, call the matching server before answering: AWS → `aws-knowledge` or `aws-documentation`; GCP → `google-developer-knowledge`; Azure → `microsoft-learn`. If the server is unreachable, say live documentation is unavailable, then answer from training knowledge. Incidental mentions of AWS/GCP/Azure in an otherwise generic question don't require a call. These servers reach Codex through the official import flow, which converts this repository's `.mcp.json` into a `[mcp_servers.*]` block in `.codex/config.toml` (measured on Codex 0.147.0, 2026-08-10). When `GOOGLE_DEV_KNOWLEDGE_API_KEY` is absent, the Google entry is present but unusable until the variable is set.

## Editing conventions

- Editing CI/CD configuration (`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`): test in a feature branch first.
- Editing Claude Code settings (`.claude/settings.json`, `.claude/settings.local.json`): verify permission rules still resolve.
- Editing production-looking configuration (`*.prod.*`, `*production*`, `*.env.production`): make sure changes are tested before they land.

## Requests

- Don't paste secrets (API keys, tokens, passwords, private key material) into a prompt. Claude Code has no automated backstop for this anymore (its prompt-secret-scanning hook was removed); see "Enforced via hook or rule" below for what Codex CLI still catches, once imported and trusted.
- If a task looks like non-trivial implementation work and this project has no `.specify/` directory yet, suggest running `specify init` once — don't insist if declined.
- Keep Spec Kit current by running `specify init` (or this project's Spec Kit update flow) periodically, if this project uses Spec Kit.
- `shfmt`, `shellcheck`, `yamllint`, and `jq` are expected to be available in the environment for formatting and lint checks to work.
- Persist decisions, conventions, and durable facts learned while working so they can be reused later, rather than re-deriving them every session.

## Enforced via hook or rule (Codex CLI only)

This repository no longer ships Codex enforcement of its own. What you get depends entirely on whether you ran the official import. Claude Code's own `.claude/hooks/` was removed in its entirety (see [ADR-0005](docs/adr/0005-remove-claude-hooks.md)), so Claude Code now enforces **less** automatically than an imported-and-trusted Codex session does for the two rows below — the comparison used to run the other way. All rows below were measured on Codex 0.147.0, 2026-08-10.

**Two guards work, once armed.** After importing, run `/hooks` in the Codex TUI and trust the imported entries — Codex skips non-managed command hooks until their definition hashes are trusted, and re-review is required whenever a hook changes. There is no feature flag to set: `hooks` is stable and enabled by default (`codex_hooks` does not exist; ignore any guide that says otherwise).

- **Destructive commands are blocked** before they run — force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, `mkfs`/`dd`/fork-bomb patterns, piping remote scripts to a shell, non-HTTPS requests, credential-path reads/writes, global package installs, `sudo`. Verified end to end: the block reaches Codex's tool router and surfaces the reason verbatim.
- **Prompts containing obvious secrets are blocked** — AWS access key IDs, GitHub tokens, Slack tokens, Google API keys, private key headers. The turn stops with no model response.

**Four things are NOT enforced in Codex. Treat them as your own responsibility.**

- **Editing `.git/` directly is _not_ blocked.**
- **Editing files on `main`/`master` is _not_ blocked** — branch first anyway; the discipline still applies, only the enforcement is missing.
- **Files are _not_ auto-formatted after edits** — run `shfmt -w -i 2` + `shellcheck` on `.sh`, `yamllint` on `.yaml`/`.yml`, and a syntax check on `.json` yourself.
- **There is no allow/prompt command policy** — Codex falls back to its own approval defaults, which ask rather than allow. That fails safe, at the cost of more prompts.

The first three are absent for one structural reason: **Codex fires `PreToolUse`/`PostToolUse` for shell commands only.** Edits go through `apply_patch`, which those events never see, so a hook matching `Edit|Write|Delete` is imported and then never runs. This is not something a different configuration can fix.

Claude Code no longer has an equivalent for these three either — `.claude/hooks/pre-edit.sh` was removed along with the rest of `.claude/hooks/`. `.claude/settings.json`'s `permissions` block, which used to be Claude Code's one remaining automatic guardrail, was also removed (see [ADR-0006](docs/adr/0006-remove-permissions-config.md)). Claude Code now enforces nothing automatically for this repository.
