# Maintaining Living Documentation — Claude Code Skill and plugin

A portable Claude Code Skill for keeping implementation, specifications, decisions, evidence, and documentation consistent as a project evolves. The same folder is also a Claude Code plugin, so placing it in a skills directory also enforces the workflow with hooks.

## Install

Personal installation (all your projects):

```bash
cp -R maintaining-living-documentation ~/.claude/skills/
```

Project installation (everyone who clones the repository; also used by the CI template):

```bash
mkdir -p .claude/skills
cp -R maintaining-living-documentation .claude/skills/
```

Because the folder contains `.claude-plugin/plugin.json`, Claude Code loads it from either location as a skills-directory plugin (`maintaining-living-documentation@skills-dir`):

- the Skill (`SKILL.md`) becomes available, and
- `hooks/hooks.json` registers the enforcing hooks (see [Making it mandatory](#making-it-mandatory)).

A project-scope plugin loads only after you accept the workspace trust dialog for the project folder, and only from the `.claude/skills/` of the folder where the session starts. Running with `-p` does not count as accepting trust. To disable the plugin while keeping the files, set `"enabledPlugins": {"maintaining-living-documentation@skills-dir": false}` in a settings file, or set `"enforcement": "off"` in the project's `.living-documentation.json` to keep the Skill but disable the hooks' effect.

Other ways to load it: `claude --plugin-dir ./maintaining-living-documentation` for one session, or publish it through a plugin marketplace. When loaded as a plugin from those sources, the Skill is named `/maintaining-living-documentation:maintaining-living-documentation`.

## Requirements

- Python 3.9 or later, standard library only. The hooks call `python3`; on systems where Python 3 has another name (for example `py` on Windows), edit `hooks/hooks.json`.
- Git is optional. With Git, file listing honors `.gitignore`, and `audit.py`, `check_links.py --changed`, and the Stop-hook gate become available.
- Claude Code v2.1.196 or later fills in the project root in `SKILL.md`. Older versions and other agent runtimes fall back to the repository root, as described in `SKILL.md`.
- `claude plugin eval` requires Claude Code v2.1.269 or later.

## Layout

- `SKILL.md` — normative basis, standing instructions, workflow, and the completion report format.
- `.claude-plugin/plugin.json` — plugin manifest. Replace the placeholder `author` before publishing.
- `hooks/hooks.json` — `SessionStart`, `UserPromptSubmit`, and `Stop` hooks, in exec form (`command` plus `args`) so they need no shell.
- `hooks/rule.md` — the mandatory rule that the `SessionStart` hook adds to Claude's context.
- `references/` — standards applicability, practices, and bibliography.
- `scripts/` — read-only inspection, change-audit, and link-check helpers, and the hook script.
- `schemas/` — JSON Schema for the optional project configuration. The scripts read it at run time, so it is the single definition of accepted keys.
- `templates/` — fallback document templates (used only when the target project has no convention) and a CI workflow template.
- `evals/` — behavior tests for `claude plugin eval`.
- `tests/` — unit tests for the scripts.

The Skill does **not** prescribe `docs/`, `specs/`, ADR paths, programming languages, build systems, or CI providers. It discovers and respects the target project's structure.

## Scripts

| Script | Purpose | Needs Git |
|---|---|---|
| `scripts/inspect_project.py` | Inventory artifact classes (implementation, documentation, specification, decision, evidence, generated, infrastructure, configuration) and change-history files | No |
| `scripts/audit.py` | Classify changed files and list possible documentation impact, including renamed/deleted files, a missing changelog entry, and edits to accepted decision records | Yes |
| `scripts/check_links.py` | Check local Markdown links, images, reference definitions, HTML `href`/`src`, and heading anchors; ignores code blocks and comments | Only for `--changed` |
| `scripts/stop_gate.py` | `SessionStart`/`UserPromptSubmit`/`Stop` hook that injects the rule and enforces the workflow | Yes (inactive without it) |

Run them from anywhere:

```bash
SKILL_DIR=~/.claude/skills/maintaining-living-documentation
python3 "$SKILL_DIR/scripts/inspect_project.py" --root /path/to/repo
python3 "$SKILL_DIR/scripts/audit.py" --root /path/to/repo --base origin/main
python3 "$SKILL_DIR/scripts/check_links.py" --root /path/to/repo --changed --base origin/main
```

All scripts accept `--json`. Exit codes: `0` success, `1` findings (`check_links.py` errors), `2` usage, configuration, or Git errors.

`check_links.py` is a link checker, not a consistency validator: it does not compare documentation with behavior. Root-relative links (`/path`) and anchors are reported as warnings because static site generators resolve them differently; pass `--site-root <dir>` for site-absolute links and `--strict` to make warnings fail.

### Pre-approve the read-only scripts

To let Claude run the three read-only scripts without asking, add these rules to `permissions.allow` in a settings file:

```json
"Bash(python3 *maintaining-living-documentation/scripts/inspect_project.py*)",
"Bash(python3 *maintaining-living-documentation/scripts/audit.py*)",
"Bash(python3 *maintaining-living-documentation/scripts/check_links.py*)"
```

The trailing `*` comes right after `.py` so that it also covers the closing quote of a quoted path. The Skill does not declare `allowed-tools`: on Claude Code 2.1.289, any `allowed-tools` declaration made invoking the Skill itself require approval, and non-interactive runs then failed to load it.

## Optional project configuration

The scripts work without configuration. To adjust classification or enforcement, add `.living-documentation.json` at the target project's root, for example:

```json
{
  "enforcement": "warn",
  "implementation_globs": ["spec/support/**"],
  "exclude_globs": ["fixtures/**"]
}
```

`schemas/config.schema.json` defines every key.

- `enforcement`: `block` (default), `warn`, or `off` for the Stop-hook gate and the session-start rule. The `LIVING_DOCS_GATE` environment variable overrides it.
- `<category>_globs`: if any pattern matches a file, those categories replace the built-in heuristics for that file. Use this to fix false positives, for example `"implementation_globs": ["spec/support/**"]`.
- `exclude_globs`: adds to the built-in exclusions (VCS metadata, `node_modules`, virtual environments, and caches at any depth; `dist`, `build`, `target`, `vendor`, `out`, `site`, `_build` at the top level).
- Patterns match project-relative POSIX paths; `*` also crosses `/`, and a leading `**/` also matches at the top level.
- A `"$schema"` key is allowed for editor validation against `schemas/config.schema.json`.

## Making it mandatory

Claude applies a Skill when it judges the Skill relevant; Claude Code cannot preload or force one. CLAUDE.md and `.claude/rules/` load every session but are guidance ("context, not enforced configuration" in the Claude Code docs). Hooks and CI enforce mechanically. The layers:

| Layer | What it does | Strength |
|---|---|---|
| Skill (`SKILL.md`) | Normative basis, workflow, references, scripts | Applied when Claude judges it relevant |
| Rule (injected by the `SessionStart` hook, or `.claude/rules/living-documentation.md`) | Tells Claude, at every session start and after compaction, to use the Skill and end with the `Documentation impact` report | Strong guidance, not enforced |
| Stop hook (`scripts/stop_gate.py`) | When files changed during the session, blocks Claude from finishing while links in the changed scope are broken, or while code, specification, configuration, infrastructure, or decision files changed without the report | Enforced within Claude Code |
| CI (`templates/ci/github-actions.yml`) | Link check on pull requests | Enforced before merge, for every contributor and tool |

When the folder loads as a plugin, the first three layers need no setup. CLAUDE.md needs no entry: the rule reaches Claude through the hook or a rule file, and a CLAUDE.md copy would duplicate it. If the project also uses other coding agents, put the rule's bullet points in their instruction file (for example `AGENTS.md`).

### Where the folder does not load as a plugin

If plugins are restricted by policy or the folder sits outside a skills directory, copy the `hooks` object from `hooks/hooks.json` into a settings file, replacing `${CLAUDE_PLUGIN_ROOT}` with the folder's path (for a project, `${CLAUDE_PROJECT_DIR}/<path>`). To commit the rule as a visible file instead of relying on the hook, copy `hooks/rule.md` to `.claude/rules/living-documentation.md`; the hook then stops adding it.

### How the gate behaves

- At session start it records the state of uncommitted changes, so changes that existed before the session do not trigger the gate. It also adds `hooks/rule.md` to Claude's context, with the Skill's install path, unless `.claude/rules/living-documentation.md` exists in the project or in `~/.claude/`.
- At the start of each turn (`UserPromptSubmit`) it records the worktree state again. On each stop after an `end_turn`, the gate runs only if the worktree differs from that turn-start state, the session baseline, and the last passing check, so edits made between turns do not trigger it.
- A failing check blocks the stop and tells Claude what is missing. The block asks Claude not to repeat its earlier answer. The same worktree state is blocked at most twice (`LIVING_DOCS_GATE_MAX_BLOCKS`), and never again right after the gate's own block (`stop_hook_active`); then the stop is allowed and you see a warning. Claude Code also caps consecutive Stop blocks.
- The gate checks that the report exists and that links are intact. It cannot judge whether the documentation is correct; review and CI remain necessary.
- Outside Git worktrees, without Git, or on internal errors, the gate does nothing (fails open). State is kept in the system temp directory, never in the project.

## CI integration

`templates/ci/github-actions.yml` runs the impact audit (advisory) and the changed-scope link check on pull requests. It assumes the project installation path; copy it to `.github/workflows/` in the target project and adjust. Other CI systems can run the same commands.

## Evals

`evals/` holds behavior cases for `claude plugin eval`. Each case seeds a small Git project and checks the result with deterministic graders (no judge model). The cases check that a configuration-default change also updates the configuration document, the changelog, and the report; that a behavior-preserving rename leaves documentation untouched and reports `Documentation impact: none`; and that a change reversing an accepted decision proposes a new record instead of creating one or editing the accepted record. From this folder:

```bash
claude plugin eval . --scaffold --allow-tools Edit Write --trust-plugin --no-publish --max-cost-usd 10
```

`--scaffold` runs the cases' `fixture.sh` scripts, which create the test projects. Each case runs with and without the plugin; the difference (`Δ`) is what the plugin contributes. Runs call the model with your credentials. Pin `--model` in CI so model updates are not mistaken for regressions.

## Tests

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate --strict .
```

The unit tests also run `claude plugin validate` when the Claude Code CLI is installed.

## Local modifications

This copy differs from the upstream package in one place: `references/practices.md` (Decision records) adds the *Numbering* and *Language* bullets, which came from the retired `adr` skill (see `archive/adr/`). Re-apply them when updating from upstream.

## Security

The bundled scripts do not access the network, install packages, or execute commands from project configuration. They invoke only read-only Git commands (`rev-parse`, `ls-files`, `diff`, `merge-base`, `status`). None of them writes project files; `stop_gate.py` keeps its state in the system temp directory. The eval fixtures run only when you pass `--scaffold`.

## Local modifications

This copy is vendored in my-claude-code. It differs from upstream only by the `Local convention (my-claude-code)` bullet under *Decision records* in `references/practices.md`. Re-apply it when updating from upstream.
