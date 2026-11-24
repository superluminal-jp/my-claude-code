# my-claude-code

Claude Code user-level configuration, kept under Git: one `CLAUDE.md`, four rules, and one subagent that apply in every project. `bash install.sh` copies them into `~/.claude/`. A plugin, `writing-check`, is kept with them in `harness/plugins/` and installed at user scope with Claude Code's plugin commands.

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

Everything else under `~/.claude/` is left untouched, including `settings.json` and `skills/`: permissions, sandbox, hooks, plugins, MCP servers, and skills are not managed by `install.sh`. The one plugin of this repository is installed with Claude Code's own plugin commands, as described under [The `writing-check` plugin](#the-writing-check-plugin). Set `CLAUDE_CONFIG_DIR` to install to another directory.

If you already have your own files in those three paths, back them up first; the install overwrites them. Earlier versions of this repository also installed skills into `~/.claude/skills/` and commands into `~/.claude/commands/`, merged keys into `~/.claude/settings.json` (model, permissions, sandbox, hooks, MCP server lists), and installed plugins. This version removes none of that. Delete what you no longer want yourself; in particular, a hook in `settings.json` that calls a script under a deleted skill does nothing.

## What is in `harness/`

| Kind | Loaded | Used here for |
|---|---|---|
| `CLAUDE.md` | Every session | The working agreement: what to settle before starting, how to work, what to verify before reporting |
| Rules | Every session | Standing habits for communication, safety, and delegation, and which standards to follow |
| Subagents | In their own context, on delegation | Work whose long output or independence should stay out of the main conversation |
| Plugin | In every session once installed with `claude plugin install`; not copied by `install.sh` | The hooks that review writing when a turn ends |

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

## The `writing-check` plugin

`harness/plugins/writing-check/` is a Claude Code plugin that reminds Claude of the writing rules when a prompt is submitted, and reviews writing once before a turn ends. The review checks the answer and the documents written during the turn against the installed rules, for what can be judged from the text alone:

| Checked against | What is checked |
|---|---|
| `rules/communication.md` | Every requirement: answer first, structure, the method and steps of multi-step work, the closing premises, assumptions, and method, terms, references, no metaphor, length |
| `rules/standards.md` | The standard for the text's language and kind (for example JTF日本語標準スタイルガイド for Japanese prose, Standard Readme, EARS, Keep a Changelog, ISO 8601 dates); a standard given as a reason is named with its section or criterion number |
| `rules/safety.md` | No secret value or personal data in the text; a request for approval names the target, the effect, and how to undo it |
| The hook's prompt | Language that no listed standard covers; for Japanese, translated-sounding phrasing, particles, and overlong sentences; wording that fits the field of the work (the terms and register its practitioners use) |

What the rules say about how Claude works (approval before an action, delegation, verification) cannot be judged from the text and is not checked. When a reader would be misled, it sends the defects back to Claude, which corrects them in the same turn.

### Install the plugin

```sh
claude plugin marketplace add /path/to/my-claude-code
claude plugin install writing-check@local-harness --scope user
```

`bash install.sh` prints these two commands with the path of the checkout filled in. User scope makes the plugin part of the user-level configuration: it is enabled in every project, like the files `install.sh` copies.

The plugin needs Python 3. Claude Code reads it in place from this checkout: an edit takes effect at the next session or after `/reload-plugins`, without reinstalling. `install.sh` does not copy it, because `~/.claude/plugins/` holds Claude Code's own record of installed plugins. To remove it, run `claude plugin uninstall writing-check@local-harness`.

### How it works

| Hook | Type | What it does |
|---|---|---|
| `UserPromptSubmit` | command | Empties the session's list of written documents, so that the list covers one turn |
| `UserPromptSubmit` | command | Adds `reminder.md` to the context of the turn, so that Claude checks its draft against the rules before the answer is shown; no model is called |
| `PostToolUse` on `Write\|Edit` | command | Adds the file to the list when it is a document (`.md`, `.mdx`, `.markdown`, `.txt`, `.rst`, `.adoc`), marked as written whole or as edited in place; no model is called |
| `Stop` | agent | A reviewer reads the answer, the listed documents (at most five), and the installed rules, and returns a pass or the defects to correct |

- **The reminder comes before the answer, the review after it.** Claude Code shows an answer as it is written, and no hook can hold it back, so a defect the reviewer finds is corrected in a second answer that the person also sees. The reminder lowers how often that happens by putting the points the reviewer judges next to the prompt. It is guidance, not a guarantee, and the review stays as the check.
- **The reminder is short and states no criteria of its own.** `reminder.md` is read with every prompt, so a test holds it to 1,200 characters. It names the rule files and the requirements the reviewer judges, and asks Claude to judge the field of the work from the conversation, which the reviewer does not read and so judges from the text alone; change a criterion in the rule, and change `reminder.md` only when the list of what is judged changes.
- **One correction per turn.** When Claude is already continuing after a correction (`stop_hook_active` in the hook input), the reviewer passes without reading anything. An earlier hook of this repository was removed because repeated corrections made Claude restate its output.
- **Documents are reviewed when the turn ends, not after each edit.** Claude Code documents no way to stop a `PostToolUse` hook from firing again on the edit that answers it, so a review after each edit could not be held to one correction.
- **Cost.** Every turn that ends runs one reviewer, with a limit of 120 seconds. The hook sets no model; the Claude Code documentation says an agent hook then uses the model Claude Code uses for background work. For a short direct reply with no documents, the reviewer reads only `rules/communication.md` and checks what that rule requires of every answer.
- **Edited documents.** In a file that was edited in place, most of the text may be older than the turn. The reviewer reports only what would mislead a reader there, and Claude is told to correct only text it wrote in the turn.
- **The list** is `writing-check/<session_id>.txt` in the Claude configuration directory (`~/.claude/` by default), in a directory only the user can read. The script and the reviewer both derive that directory from the transcript path in the hook input.
- **Criteria.** The criteria are the installed rules; change them there. The hook's prompt says which requirements can be judged from the text, and adds only the criteria for language that no rule or listed standard states. A test fails when the prompt names a rule file that `harness/rules/` does not have.
- **Limits.** Agent hooks are marked experimental in the Claude Code documentation and may change. The review is a model's judgment, not a guarantee.

## What is deliberately not here

- **`settings.json`.** Manage it yourself with `/config` or by editing `~/.claude/settings.json`.
- **Skills.** Every procedure this repository once carried as a skill turned out to be a named standard or framework, and is now one row in `rules/standards.md`.
- **Specification and delivery workflows.** Spec Kit and AI-DLC are set up in each project that uses them. The harness defers to a project's own workflow and does not duplicate it.
- **Enforcement.** Instructions in `CLAUDE.md` and rules are guidance that Claude reads, not guarantees. Anything that must hold without exception belongs in permission settings or hooks. The `writing-check` plugin is the one hook kept here, and it asks for a correction rather than guaranteeing one.

## Develop

```sh
bash tests/run.sh
```

This checks every file in `harness/` against the format Claude Code reads (front matter fields, required fields, the size of what loads in every session), runs the tests of the `writing-check` plugin, and runs `install.sh` against a temporary directory. CI runs the same command on Ubuntu and on macOS.

`claude plugin validate . --strict` and `claude plugin validate harness/plugins/writing-check --strict` check the plugin's manifests. They need Claude Code and are not part of `tests/run.sh` or CI.

Edit `harness/`, run the checks, run `bash install.sh`, and start a new session to use the change. See [CLAUDE.md](CLAUDE.md) for the conventions of this repository.

## Design basis

The layout follows the Claude Code documentation as read on 2026-11-21:

- [Memory: CLAUDE.md and rules](https://code.claude.com/docs/en/memory) - keep `CLAUDE.md` under 200 lines; rules without `paths` load in every session.
- [Subagents](https://code.claude.com/docs/en/sub-agents) - a custom subagent for context isolation or a restricted, specialized role.
- [Best practices](https://code.claude.com/docs/en/best-practices) and [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - which mechanism to use for what; guardrails belong in hooks.
- [Hooks](https://code.claude.com/docs/en/hooks) and [Plugins](https://code.claude.com/docs/en/plugins), read on 2026-11-24 - agent hooks on `Stop`, the `stop_hook_active` input, and a plugin read in place from a local marketplace.
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - add only what Claude does not already know.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - say what to do, explain why, and avoid emphatic wording.
