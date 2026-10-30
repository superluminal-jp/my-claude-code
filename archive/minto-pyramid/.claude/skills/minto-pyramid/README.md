# minto-pyramid

Portable Claude Code plugin that applies the Minto Pyramid Principle to problem framing, reasoning structure, user communication, decisions, plans, and deliverables.

## Purpose

Use this plugin when you want Claude Code to structure substantive work around one controlling question, one governing answer, and a recursively supported hierarchy of claims and evidence.

The plugin **does not request or expose private chain-of-thought**. It constrains internal problem structure and requires only the conclusions, material reasoning, evidence, assumptions, uncertainty, and trade-offs needed by the user.

## Install / run locally

During development or for portable use from a folder:

```bash
claude --plugin-dir /path/to/minto-pyramid
```

Claude Code loads plugin components from the plugin root. The manifest is `.claude-plugin/plugin.json`; the skill is the root `SKILL.md`. The plugin declares no hooks.

## Layout

- `SKILL.md` — operational entry point.
- `.claude-plugin/plugin.json` — plugin manifest. Replace the placeholder `author` before publishing.
- `rules/` — normative logic rules (`core.md`, `completion-check.md`).
- `templates/` — optional structural templates (`answer.md`, `decision.md`, `document.md`).
- `references/` — provenance and source material summaries, and the bibliography.
- `evals/` — behavior cases for `claude plugin eval`, one directory per case (`case.yaml`, `prompt.md`, `graders/`).
- `tests/` — package-level unit tests.

## Design

- `rules/` and `templates/` are **skill resources**, not special Claude Code plugin directories.
- Eval graders are `type: llm` rubrics, one per expectation.

## Enforcement model

The skill description states that the skill applies to every substantive task. Before completion, the skill's step 10 applies `rules/completion-check.md` to the observable result. The package declares no hooks, so this check is advisory self-checking: Claude Code treats instructions as context, not as enforced configuration ([Claude Code memory docs](https://code.claude.com/docs/en/memory)).

The user’s explicit requested format or ordering takes precedence when it conflicts with the default Minto presentation order. The underlying argument structure should still remain pyramidal where possible.

## Notes on portability

The plugin uses no hooks and no executable scripts, so it has no shell/OS dependencies and adds no model call at turn completion.

## Local modification

This copy removes the upstream `Stop` prompt hook (`hooks/hooks.json`); the manifest version `0.3.0+local.no-stop-hook` marks the local build ([SemVer 2.0.0 §10](https://semver.org/spec/v2.0.0.html)). A verbatim re-copy from upstream would restore the hook.

Activation: an existing user-level install keeps running the removed hook from `~/.claude/skills/minto-pyramid/hooks/` until `install.sh` is re-run. The removal then takes effect in a new session, because hooks are captured at session start ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)); run `/hooks` to confirm that no `minto-pyramid` `Stop` hook is listed.

Rationale, with evidence labels:

- A prompt hook sends the hook input to a model for evaluation, so the hook added a model call at the end of every turn ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)).
- A blocking `Stop` hook prevents the stop and keeps the turn running ([Claude Code hooks reference](https://code.claude.com/docs/en/hooks)). *Observed:* commit `753eb52` in the containing repository changed this hook (together with another package's `Stop` gate) to stop a re-output loop during correction rounds.
- *Inferred:* these are the reasons for the removal; the request stated only that the hook be retired.
- *Unverified:* whether output quality or eval pass rates change without the hook. No eval was run.

## Evals

```bash
claude plugin eval . --no-publish
```

Each case runs with and without the plugin; the difference is what the plugin contributes. Runs call the model with your credentials.

## Tests

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate --strict .
```
