# my-claude-code

Claude Code user-level configuration, kept under Git: one `CLAUDE.md`, rules, skills, and subagents that apply in every project. `bash install.sh` copies them into `~/.claude/`.

日本語: [README.ja.md](README.ja.md)

## Install

```sh
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
bash install.sh
```

Requires Bash. Start a new Claude Code session afterwards; run `/context` or `/memory` to confirm the files loaded.

`install.sh` replaces four paths under `~/.claude/` so that they match `harness/` exactly:

| Path | Effect |
|---|---|
| `CLAUDE.md` | Replaced |
| `rules/` | Replaced; a rule removed here is removed there |
| `skills/` | Replaced, except `skills/synced/`, which the Claude app owns and is preserved |
| `agents/` | Replaced |

Everything else under `~/.claude/` is left untouched, including `settings.json`: permissions, sandbox, hooks, plugins, and MCP servers are not managed by this repository. Set `CLAUDE_CONFIG_DIR` to install to another directory.

If you already have your own files in those four paths, back them up first; the install overwrites them.

## What is in `harness/`

Each kind of file is used for what Claude Code loads it for, so that only what every session needs is paid for in every session.

| Kind | Loaded | Used here for |
|---|---|---|
| `CLAUDE.md` | Every session | The working agreement: what to settle before starting, how to work, what to verify before reporting |
| Rules without `paths` | Every session | Standing habits for communication and safety |
| Rules with `paths` | When a matching file is read or edited | Conventions for one language or file type |
| Skills | Description every session; body when used | Procedures for a kind of task |
| Subagents | In their own context, on delegation | Work whose long output or independence should stay out of the main conversation |

### Rules

| Rule | Loads | Content |
|---|---|---|
| `communication.md` | Always | Answer first, support under it, terms defined for a newcomer |
| `safety.md` | Always | What needs approval first; handling secrets and untrusted content |
| `python.md` | `*.py`, `pyproject.toml` | Typing, boundaries, errors, paths, logging |
| `typescript.md` | `*.ts`, `*.tsx`, `*.mts`, `*.cts`, `tsconfig*.json` | Strictness, narrowing, boundaries, promises, React |
| `shell.md` | `*.sh`, `*.bash`, `*.zsh` | Strict mode, quoting, temporary files, portability |
| `tests.md` | Test files and test directories | Behavior-named, deterministic tests; failing tests are evidence |
| `github-actions.md` | Workflow and action files | Least-privilege tokens, injection, pinning, OIDC |

### Skills

| Skill | Use it to |
|---|---|
| `clarify-intent` | Get one reading of a request agreed before working on it |
| `define-problem` | State a problem as a checkable gap, apart from causes and fixes |
| `implement-change` | Change behavior test-first and verify it |
| `debug-failure` | Find and confirm the cause of a failure before fixing it |
| `manage-git` | Branch, commit, push, and open pull requests without overstepping |
| `structure-document` | Structure a document as one claim tree (Minto pyramid) |
| `sync-docs` | Keep documentation in step with a change, or audit it for drift |
| `record-decision` | Write an architecture decision record |
| `draw-system-diagrams` | Draw architecture views (C4 levels) in Mermaid |
| `research-aws` | Answer AWS questions from current official documentation |
| `apply-secure-logging` | Check or change logging against an OWASP-based checklist |
| `apply-dads-frontend` | Apply the Digital Agency Design System to React and Tailwind CSS work |

Each skill is invoked automatically when a request matches its description, or directly as `/<skill-name>`.

### Subagents

| Subagent | Tools | Use |
|---|---|---|
| `check-runner` | Bash, Read, Grep, Glob | Runs tests, builds, and linters and reports exit codes and verbatim failures |
| `independent-reviewer` | Read, Grep, Glob | Reviews work from the files alone, without the author's reasoning |

Searching and general delegated work use Claude Code's built-in `Explore` and `general-purpose` agents.

## What is deliberately not here

- **`settings.json`.** Manage it yourself with `/config` or by editing `~/.claude/settings.json`.
- **Specification and delivery workflows.** Spec Kit and AI-DLC are set up in each project that uses them. The harness defers to a project's own workflow and does not duplicate it.
- **Enforcement.** Instructions in `CLAUDE.md` and rules are guidance that Claude reads, not guarantees. Anything that must hold without exception belongs in permission settings or hooks.

## Develop

```sh
bash tests/run.sh
```

This checks every file in `harness/` against the format Claude Code reads (front matter fields, name and description limits, body length, references that exist) and runs `install.sh` against a temporary directory. CI runs the same command.

Edit `harness/`, run the checks, run `bash install.sh`, and start a new session to use the change. See [CLAUDE.md](CLAUDE.md) for the conventions of this repository.

## Design basis

The layout follows the Claude Code documentation as read on 2026-11-21:

- [Memory: CLAUDE.md and rules](https://code.claude.com/docs/en/memory) - keep `CLAUDE.md` under 200 lines; `paths` is the only rule front matter field; path-scoped rules load when a matching file is touched.
- [Skills](https://code.claude.com/docs/en/skills) and [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - descriptions in the third person stating what and when; bodies under 500 lines; reference files one level deep.
- [Subagents](https://code.claude.com/docs/en/sub-agents) - a custom subagent for context isolation or a restricted, specialized role.
- [Best practices](https://code.claude.com/docs/en/best-practices) and [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - which mechanism to use for what; guardrails belong in hooks.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - say what to do, explain why, and avoid emphatic wording.

## Bundled third-party material

- `harness/skills/apply-dads-frontend/references/dads-docs/` is an unmodified copy of the Digital Agency of Japan's official Markdown export of the [Digital Agency Design System](https://design.digital.go.jp/dads/) site. Its terms and attribution rules are described in `harness/skills/apply-dads-frontend/references/sourcing-and-licensing.md`.
