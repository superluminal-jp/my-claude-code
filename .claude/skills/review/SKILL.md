---
name: review
description: Route Codex review and delegation requests to the codex-plugin-cc Claude Code plugin. Activates when the plugin is installed.
argument-hint: "[review|adversarial|rescue|status|result|cancel|setup] [--base <ref>] [--perspectives quality,security] [<rest>...]"
user-invocable: true
disable-model-invocation: false
---

# Review: Codex Plugin Router

Forward review and Codex delegation requests to the `codex-plugin-cc` plugin's slash commands. This skill is a thin router — it does NOT invoke the `codex` CLI directly. All Codex execution, authentication, prompt construction, and result formatting are delegated to the plugin.

## Prerequisite Check

Run this in shell:
```bash
claude plugin list 2>/dev/null | grep -q "codex@openai-codex"
```

If the grep returns non-zero (plugin not installed), output exactly:

```
codex-plugin-cc is not installed. Run install.sh, or manually:
  claude plugin marketplace add openai/codex-plugin-cc
  claude plugin install codex@openai-codex
After install, restart Claude Code and run /codex:setup once to verify auth.
```

Then halt. Do not attempt routing.

If the plugin is installed, proceed to Routing.

## Routing

Choose the plugin slash command that matches the user's intent, then invoke it via the SlashCommand tool. When uncertain, default to `/codex:review`.

### Intent → command mapping

| User input pattern | Slash command |
|---|---|
| no args / "review" / `after_tasks` or `after_implement` hook context | `/codex:review [--base <ref>]` |
| "adversarial", "challenge design", deep security scrutiny, hard-to-reverse changes | `/codex:adversarial-review` |
| "rescue", "delegate", "investigate", "fix in background" | `/codex:rescue` |
| "status", "what's running" | `/codex:status` |
| "result", "show output", a session id | `/codex:result` |
| "cancel", "stop" | `/codex:cancel` |
| "setup", "verify auth", first-time configuration | `/codex:setup` |

### `--perspectives` (hint only)

Treat `--perspectives` as a soft hint. Use judgement from the full context:

- `quality` (alone or with `security`) on routine work → `/codex:review`
- `security` plus a high-risk change (auth, crypto, parsers, IPC, external input handling) → prefer `/codex:adversarial-review`
- Otherwise default to `/codex:review`

Do not enforce a strict mapping. The plugin's review prompts already cover quality and security broadly.

### `--base <ref>`

Forward verbatim to `/codex:review` or `/codex:adversarial-review`.

### Free-form arguments

Anything else the user typed should be passed to the chosen slash command as its natural-language context, so the plugin can incorporate intent.

## Hook Context (`after_tasks`, `after_implement`)

When invoked by an `extensions.yml` hook with no user arguments, invoke `/codex:review` with no extra arguments. The plugin auto-detects the current work.

## Output

Display the plugin's output verbatim. Do not reformat, summarise, or truncate — the plugin manages its own structured output and session state.

## Why this routing exists

- `extensions.yml` hooks reference `command: review`; keeping the skill preserves that contract.
- The skill consolidates intent → plugin command dispatch in one place so callers (hooks, `/review`, agents) share one entry point.
- All Codex CLI specifics (auth, sandbox, prompt construction) live in the plugin; this skill stays a thin façade.
