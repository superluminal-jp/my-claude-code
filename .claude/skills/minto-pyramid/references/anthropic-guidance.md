# Anthropic / Claude Code implementation guidance

Checked against the current Claude Code documentation on 2026-10-05.

## Plugin packaging

- A Claude Code plugin is a directory loaded as one unit.
- The manifest, when present, is `.claude-plugin/plugin.json` under the plugin root.
- Standard plugin component locations include `skills/` and `hooks/hooks.json`.
- A root `CLAUDE.md` in a plugin is not loaded as plugin context; instructions belong in a skill.
- A plugin can be loaded directly from a folder with `--plugin-dir` during development/portable use.

## Skill design

- Keep the skill entry point concise and operational.
- Put detailed rules, references, examples, and reusable assets in supporting files so they are read only when needed.
- Describe the skill so Claude can decide when to invoke it automatically.

## Hooks

- Plugin hooks live in `hooks/hooks.json` and merge with user/project hooks when the plugin is enabled.
- Prompt-based hooks avoid shell dependencies but incur a model call.
- `Stop` prompt hooks can return `ok: false` with a reason; Claude Code feeds that reason back so Claude can continue and repair the result.
- This plugin uses a `Stop` hook only for observable-output compliance. It explicitly does not request hidden chain-of-thought.

## Non-standard resource directories

`rules/` and `templates/` are not special top-level Claude Code plugin component directories. In this package they sit beside `SKILL.md` at the package root as progressive-disclosure resources referenced by it.

## Primary documentation

- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/hooks
