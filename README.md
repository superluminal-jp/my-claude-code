# my-claude-code

Claude Code user-level configuration, kept under Git: one `CLAUDE.md`, four rules, and one subagent that apply in every project. `bash install.sh` copies them into `~/.claude/`.

日本語: [README.ja.md](README.ja.md)

## Install

```sh
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
bash install.sh
```

Installing requires Bash; running the checks also requires Python 3. Start a new Claude Code session afterwards; run `/context` or `/memory` to confirm the files loaded.

`install.sh` replaces three paths under `~/.claude/` so that they match `harness/` exactly:

| Path | Effect |
|---|---|
| `CLAUDE.md` | Replaced |
| `rules/` | Replaced; a rule removed here is removed there |
| `agents/` | Replaced; an agent removed here is removed there |

Everything else under `~/.claude/` is left untouched, including `settings.json` and `skills/`: permissions, sandbox, hooks, plugins, MCP servers, and skills are not managed by this repository. Set `CLAUDE_CONFIG_DIR` to install to another directory.

If you already have your own files in those three paths, back them up first; the install overwrites them. Earlier versions of this repository also installed skills into `~/.claude/skills/` and commands into `~/.claude/commands/`, merged keys into `~/.claude/settings.json` (model, permissions, sandbox, hooks, MCP server lists), and installed plugins. This version removes none of that. Delete what you no longer want yourself; in particular, a hook in `settings.json` that calls a script under a deleted skill does nothing.

## What is in `harness/`

| Kind | Loaded | Used here for |
|---|---|---|
| `CLAUDE.md` | Every session | The working agreement: what to settle before starting, how to work, what to verify before reporting |
| Rules | Every session | Standing habits for communication, safety, and delegation, and which standards to follow |
| Subagents | In their own context, on delegation | Work whose long output or independence should stay out of the main conversation |

### The principle: name the standard

The harness names established standards instead of restating them. Claude already knows PEP 8, Conventional Commits, or the C4 model, so a rule says which standard applies and adds only what no standard covers. A more specific instruction is added when the same mistake is seen twice. Everything that loads in every session is held under a budget of 16,000 bytes, which the checks enforce.

### Rules

| Rule | Content |
|---|---|
| `communication.md` | Answer first, support under it, terms defined for a newcomer; multi-step work names its method and steps first and says which step each answer is on; every answer ends with its premises, assumptions, and method |
| `delegation.md` | When to hand work to a subagent, how to brief it, and how far to trust its report |
| `safety.md` | What needs approval first; handling secrets, personal data, and untrusted content |
| `standards.md` | The established standard to follow, where the project is silent, for code, APIs, cloud and AI workloads, security, documents, problem definition, and Git and GitHub; the few facts no standard covers |

### Subagents

| Subagent | Tools | Use |
|---|---|---|
| `independent-reviewer` | Read, Grep, Glob | Reviews work from the files alone, without the author's reasoning |

Searching, running checks, and general delegated work use Claude Code's built-in `Explore` and `general-purpose` agents, briefed as `rules/delegation.md` describes. A custom subagent is kept only where a tool restriction does the work: the reviewer cannot edit or run anything.

## What is deliberately not here

- **`settings.json`.** Manage it yourself with `/config` or by editing `~/.claude/settings.json`.
- **Skills.** Every procedure this repository once carried as a skill turned out to be a named standard or framework, and is now one row in `rules/standards.md`.
- **Specification and delivery workflows.** Spec Kit and AI-DLC are set up in each project that uses them. The harness defers to a project's own workflow and does not duplicate it.
- **Enforcement.** Instructions in `CLAUDE.md` and rules are guidance that Claude reads, not guarantees. Anything that must hold without exception belongs in permission settings or hooks.

## Develop

```sh
bash tests/run.sh
```

This checks every file in `harness/` against the format Claude Code reads (front matter fields, required fields, the size of what loads in every session) and runs `install.sh` against a temporary directory. CI runs the same command on Ubuntu and on macOS.

Edit `harness/`, run the checks, run `bash install.sh`, and start a new session to use the change. See [CLAUDE.md](CLAUDE.md) for the conventions of this repository.

## Design basis

The layout follows the Claude Code documentation as read on 2026-11-21:

- [Memory: CLAUDE.md and rules](https://code.claude.com/docs/en/memory) - keep `CLAUDE.md` under 200 lines; rules without `paths` load in every session.
- [Subagents](https://code.claude.com/docs/en/sub-agents) - a custom subagent for context isolation or a restricted, specialized role.
- [Best practices](https://code.claude.com/docs/en/best-practices) and [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - which mechanism to use for what; guardrails belong in hooks.
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - add only what Claude does not already know.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - say what to do, explain why, and avoid emphatic wording.
