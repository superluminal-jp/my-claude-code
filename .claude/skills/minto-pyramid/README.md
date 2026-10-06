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

Claude Code loads plugin components from the plugin root. The manifest is `.claude-plugin/plugin.json`; the skill is the root `SKILL.md`; plugin hooks are under `hooks/hooks.json`.

## Layout

- `SKILL.md` — operational entry point.
- `.claude-plugin/plugin.json` — plugin manifest. Replace the placeholder `author` before publishing.
- `hooks/hooks.json` — `Stop` prompt hook that performs the final semantic compliance check.
- `rules/` — normative logic rules (`core.md`, `completion-check.md`).
- `templates/` — optional structural templates (`answer.md`, `decision.md`, `document.md`).
- `references/` — provenance and source material summaries, and the bibliography.
- `evals/` — behavior cases for `claude plugin eval`, one directory per case (`case.yaml`, `prompt.md`, `graders/`).
- `tests/` — package-level unit tests.

## Design

- `rules/` and `templates/` are **skill resources**, not special Claude Code plugin directories.
- `hooks/hooks.json` is a standard Claude Code plugin hook. It does not ask for hidden reasoning.
- Eval graders are `type: llm` rubrics, one per expectation.

## Enforcement model

The skill description states that the skill applies to every substantive task. The `Stop` hook then checks the observable result against the core Minto constraints. If the result is materially non-compliant, Claude receives a concrete correction request (without repeating its earlier output) and continues rather than ending the turn. The hook allows the stop when `stop_hook_active` is true, so it corrects at most once per turn.

The user’s explicit requested format or ordering takes precedence when it conflicts with the default Minto presentation order. The underlying argument structure should still remain pyramidal where possible.

## Notes on portability

The plugin uses no external executable hook scripts. The compliance hook is a prompt-based Claude Code hook, so it avoids shell/OS dependencies. This adds a small model-call cost at turn completion.

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
