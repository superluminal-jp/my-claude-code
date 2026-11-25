# my-claude-code

Claude Code user-level configuration, kept under Git: one `CLAUDE.md`, four rules, one subagent, and one skill that apply in every project. `bash install.sh` copies them into `~/.claude/`. A plugin, `writing-check`, is kept with them in `harness/plugins/` and installed at user scope with Claude Code's plugin commands.

日本語: [README.ja.md](README.ja.md)

## Install

```sh
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
bash install.sh
```

Installing requires Bash; running the checks also requires Python 3. Start a new Claude Code session afterwards; run `/context` or `/memory` to confirm the files loaded.

`install.sh` replaces four paths under `~/.claude/` so that they match `harness/` exactly:

| Path | Effect |
|---|---|
| `CLAUDE.md` | Replaced |
| `rules/` | Replaced; a rule removed here is removed there |
| `agents/` | Replaced; an agent removed here is removed there |
| `skills/` | Replaced; a skill removed here is removed there, and so is any skill placed there some other way |

Everything else under `~/.claude/` is left untouched, including `settings.json` and `commands/`: permissions, sandbox, hooks, plugins, and MCP servers are not managed by `install.sh`. Every user-level skill lives in `harness/skills/`; one added to `~/.claude/skills/` by hand is removed by the next install. The one plugin of this repository is installed with Claude Code's own plugin commands, as described under [The `writing-check` plugin](#the-writing-check-plugin). Set `CLAUDE_CONFIG_DIR` to install to another directory.

If you already have your own files in those four paths, back them up first; the install overwrites them. Earlier versions of this repository also installed commands into `~/.claude/commands/`, merged keys into `~/.claude/settings.json` (model, permissions, sandbox, hooks, MCP server lists), and installed plugins. This version removes none of that. Delete what you no longer want yourself; in particular, a hook in `settings.json` that calls a script under a deleted skill does nothing.

## What is in `harness/`

| Kind | Loaded | Used here for |
|---|---|---|
| `CLAUDE.md` | Every session | The working agreement: what to settle before starting, how to work, what to verify before reporting |
| Rules | Every session | Standing habits for communication, safety, and delegation, and which standards to follow |
| Subagents | In their own context, on delegation | Work whose long output or independence should stay out of the main conversation |
| Skills | When the task matches the skill's description, or when invoked as `/name` | A procedure, with its files, that no named standard covers |
| Plugin | In every session once installed with `claude plugin install`; not copied by `install.sh` | A hook that reminds Claude of the writing rules with each prompt |

### The principle: name the standard

The harness names established standards instead of restating them. Claude already knows PEP 8, Conventional Commits, or the C4 model, so a rule says which standard applies and adds only what no standard covers. A more specific instruction is added when the same mistake is seen twice. Everything that loads in every session is held under a budget of 16,000 bytes, which the checks enforce.

### Rules

| Rule | Content |
|---|---|
| `communication.md` | Answer first, support under it, terms defined for a newcomer; multi-step work names its method and steps first and says which step each answer is on; an answer whose reasoning a named practice, standard, or framework decided ends with one line naming each and what it decided |
| `delegation.md` | When to hand work to a subagent, how to brief it, and how far to trust its report |
| `safety.md` | What needs approval first; handling secrets, personal data, and untrusted content |
| `standards.md` | The established standard to follow, where the project is silent, for code, APIs, cloud and AI workloads, security, documents, problem definition, and Git and GitHub; the few facts no standard covers |

### Subagents

| Subagent | Tools | Use |
|---|---|---|
| `independent-reviewer` | Read, Grep, Glob | Reviews work from the files alone, without the author's reasoning |

Searching, running checks, and general delegated work use Claude Code's built-in `Explore` and `general-purpose` agents, briefed as `rules/delegation.md` describes. A custom subagent is kept only where a tool restriction does the work: the reviewer cannot edit or run anything.

## The `writing-check` plugin

`harness/plugins/writing-check/` is a Claude Code plugin that reminds Claude of the writing rules when a prompt is submitted. Claude Code adds `reminder.md` to the context of the turn, so that Claude checks its draft against the installed rules before the answer is shown. The reminder lists what can be judged from the text alone:

| Rule or source | What the reminder lists |
|---|---|
| `rules/communication.md` | Answer first, the Method line, terms defined at first use, references that say what they point to, no metaphor, length |
| `rules/standards.md` | The standard for the text's language and kind; a standard given as a reason is named with its section or criterion number |
| `rules/safety.md` | No secret value or personal data in the text; a request for approval names the target, the effect, and how to undo it |
| `reminder.md` itself | Language that reads as written by a careful native writer, with no translated-sounding phrasing; wording that fits the field of the work, judged from the conversation |

What the rules say about how Claude works (approval before an action, delegation, verification) is not in the reminder.

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
| `UserPromptSubmit` | command | `scripts/remind.py` prints `reminder.md` as the `additionalContext` of the hook output, which Claude Code adds to the context of the turn; no model is called |

- **The reminder is short and states no criteria of its own.** `reminder.md` is read with every prompt, so a test holds it to 1,200 characters. It names the rule files and the requirements that show in the text; change a criterion in the rule, and change `reminder.md` only when the list of what it names changes. A test fails when it names a rule file that `harness/rules/` does not have.
- **A failure does not disturb the prompt.** When `reminder.md` cannot be read, the script prints nothing, and it always exits 0.
- **Guidance, not a check.** The reminder is text Claude reads, not a guarantee; nothing checks the answer after it is written.

## What is deliberately not here

- **`settings.json`.** Manage it yourself with `/config` or by editing `~/.claude/settings.json`.
- **Skills for named standards.** Every procedure this repository once carried as a skill turned out to be a named standard or framework, and is now one row in `rules/standards.md`. A skill is kept only for a procedure no standard covers; `create-presentation` is the one such skill.
- **Specification and delivery workflows.** Spec Kit and AI-DLC are set up in each project that uses them. The harness defers to a project's own workflow and does not duplicate it.
- **Enforcement.** Instructions in `CLAUDE.md` and rules are guidance that Claude reads, not guarantees. Anything that must hold without exception belongs in permission settings or hooks. The `writing-check` plugin is the one hook kept here, and it reminds Claude of the rules rather than checking the answer.

## The `create-presentation` skill

`harness/skills/create-presentation/` writes explanatory material as plain HTML built on the HTML components of the Digital Agency Design System (DADS), in two formats: slides (a fixed 16:9 canvas, one slide per screen and per PDF page) and a page that scrolls. Claude reads it when such material is asked for; `/create-presentation` invokes it directly.

| In the skill | Content |
|---|---|
| `SKILL.md` | The steps, the rules that keep the material working, and the slide layouts |
| `references/components.md` | Which DADS components suit slides, a page, or neither |
| `assets/base/` | What DADS does not provide: the slide canvas, columns, panels, a code block, tree diagrams |
| `assets/templates/` | One slide file and one page file that show every pattern |
| `assets/dads/` | A copy of the DADS components that suit either format, from one tagged release: the license, `global.css`, and each component's stylesheet, sample HTML, and script |
| `scripts/copy-dads.sh` | Copies into a project the DADS files its material links |
| `scripts/check.cjs` | Opens the material in a headless browser and reports content that is cut off |

- **What it writes into a project.** `presentation/` only: a copy of the base, the material, and `dads/` with the DADS files the material links (tens of KB) and the DADS license. There is no clone of DADS, and the material opens and can be shared on its own.
- **Network.** None to make the material; the templates load Noto Sans JP from Google Fonts as the DADS samples do. The skill says so before the first run in a project.
- **The check needs Node.js and Playwright with Chromium.** Without them the skill reports that the material was not checked; it installs nothing on its own.
- **Moving to another DADS release.** `bash scripts/vendor-dads.sh <tag>` replaces `assets/dads/` from that tag and writes `SOURCE` (the tag and commit) and `SHA256SUMS`; `tests/run.sh` fails when the files differ from `SHA256SUMS`. Commit the result, run `copy-dads.sh` on `presentation/`, and run the browser check.
- **Limits.** The check finds content that runs past a slide, a tree diagram that scrolls, a page that scrolls sideways, a local file that failed to load, and script errors. It does not judge appearance, and it has been run with Chromium only.

[presentation/](presentation/README.md) is this repository's own use of the skill: a trial deck and page about this repository (Japanese). Its `base/` and `dads/` are the copies the skill makes, and `tests/run.sh` fails when `base/` differs from the skill's assets or when an HTML file links a file that is not there.

## Develop

```sh
bash tests/run.sh
```

This checks every file in `harness/` against the format Claude Code reads (front matter fields, required fields, the size of what loads in every session), runs the tests of the `writing-check` plugin, checks the `create-presentation` skill against `presentation/`, and runs `install.sh` against a temporary directory. CI runs the same command on Ubuntu and on macOS.

`claude plugin validate . --strict` and `claude plugin validate harness/plugins/writing-check --strict` check the plugin's manifests. They need Claude Code and are not part of `tests/run.sh` or CI. Neither is `scripts/check.cjs` of the `create-presentation` skill, which needs a browser.

Edit `harness/`, run the checks, run `bash install.sh`, and start a new session to use the change. See [CLAUDE.md](CLAUDE.md) for the conventions of this repository.

## Design basis

The layout follows the Claude Code documentation as read on 2026-11-21:

- [Memory: CLAUDE.md and rules](https://code.claude.com/docs/en/memory) - keep `CLAUDE.md` under 200 lines; rules without `paths` load in every session.
- [Subagents](https://code.claude.com/docs/en/sub-agents) - a custom subagent for context isolation or a restricted, specialized role.
- [Best practices](https://code.claude.com/docs/en/best-practices) and [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - which mechanism to use for what; guardrails belong in hooks.
- [Hooks](https://code.claude.com/docs/en/hooks) and [Plugins](https://code.claude.com/docs/en/plugins), read on 2026-11-24 - a plugin read in place from a local marketplace.
- [Skills](https://code.claude.com/docs/en/skills), read on 2026-11-25 - `${CLAUDE_SKILL_DIR}` in a skill's text is replaced by the skill's directory. The [Plugins reference](https://code.claude.com/docs/en/plugins/plugins-reference), read the same day, says a plugin cannot carry `CLAUDE.md` or rules, so a plugin is used here only for hooks.
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - add only what Claude does not already know.
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - say what to do, explain why, and avoid emphatic wording.
