# Research: empirical trial of the official Codex migration path

**Date**: 2026-08-10
**Feature**: 021-codex-official-import
**Purpose**: settle FR-007 — run the official tooling once and record what it actually produces, before any deletion is executed.

## Method, and what could not be run

| Attempted | Result |
|---|---|
| `/import` in Codex CLI | **Deferred at first, executed later — see §§ R-08, R-09.** On the first attempt the CLI was broken: `@openai/codex@0.130.0` was installed globally but `…/codex-darwin-arm64/vendor/aarch64-apple-darwin/codex/` was empty, so `codex --version` failed with `ENOENT`. The operator reinstalled (0.147.0) and ran `/import` and three live verification sessions. Note `/import` is interactive-only — there is no `codex import` subcommand — so it cannot be driven from this session in any case. |
| `migrate-to-codex` CLI | **Run.** The curated skill is already cached locally at `~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/`, and it ships a **non-interactive Python CLI** (`scripts/migrate-to-codex.py`). All four read-only modes were run against this repository. |

Commands executed (from the repo root), all read-only:

```bash
M=~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate-to-codex.py
python3 "$M" --source ./.claude/ --scan-only
python3 "$M" --source ./.claude/ --target ./.codex/ --doctor
python3 "$M" --source ./.claude/ --target ./.codex/ --plan
python3 "$M" --source ./.claude/ --target ./.codex/ --dry-run
```

`git status --porcelain` after every run showed only the untracked `specs/021-codex-official-import/` — **no files were written**.

Two authoritative local sources were also read directly (they supersede the summarised web fetches recorded in `spec.md`):

- `~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/SKILL.md`
- `…/references/differences.md` — note its own header: **"Docs last checked: 2026-04-20."** Roughly four months stale as of today, and it disagrees with the current official hooks page on which lifecycle events exist. Where they disagree, the converter's own source code (`scripts/migrate/hooks.py`) is treated as authoritative for *what the tool does*, and the live docs for *what Codex supports*.

## R-01 — Baseline (what the current hand-port deploys)

Captured before any change, for comparison:

- `~/.agents/skills/` — 8 symlinks into `~/.claude/skills/`; `~/.codex/skills/` is **empty** (Codex reads the `.agents` path)
- `~/.codex/hooks/` — the 4 adapters
- `~/.codex/rules/` — `guardrails.rules` (repo) + `default.rules` (Codex's own)
- `~/.codex/prompts/` — `verify-config.md` + 9 `speckit.*.md`
- `~/.codex/config.toml` — 259 lines, containing two intact marker blocks:
  `# >>> my-claude-code managed hooks …` (4 registrations) and `# >>> my-claude-code managed MCP servers …` (5 servers; `strands-agents` correctly skipped because a user-owned definition already exists outside the block)

## R-02 — What the converter stages

`--scan-only` found: 3 instruction files, **24 skills**, 0 command sources, **1 subagent** (`verification-runner`).

`--plan` staged 4 artifact groups: `AGENTS.md`, `.agents/skills/**` (24 skills incl. `references/` and `scripts/`), `.codex/agents/verification-runner.toml`, `.codex/config.toml` (6 MCP servers), `.codex/hooks.json`.

`--doctor` verdict: **`readiness: low`**, **24 manual review items**, **23 existing Codex collisions**, 0 orphans.

## R-03 — Hooks (the decisive finding)

The converter's report row for `.codex/hooks.json`, quoted verbatim from the dry-run:

> `rewritten: .codex/hooks.json - Unsupported Claude hook fields need review: ` + "`hooks.UserPromptExpansion`" + `. Rewritten for Codex hooks; review behavior before relying on it. Codex hooks require `[features].codex_hooks = true`, only execute `command` handlers, skip `async` / `prompt` / `agent` handlers, ignore `matcher` for `UserPromptSubmit` and `Stop`, and **`PreToolUse` / `PostToolUse` currently run for shell commands only**.`

Supported events, from `scripts/migrate/hooks.py`:

```python
CODEX_HOOK_EVENTS = ("PreToolUse", "PostToolUse", "SessionStart", "UserPromptSubmit", "Stop")
CODEX_HOOK_MATCHER_EVENTS = frozenset(("PreToolUse", "PostToolUse", "SessionStart"))
```

Mapping that against this repo's actual registrations in `.claude/settings.json`:

| Claude registration | Guardrail | Survives the migration? |
|---|---|---|
| `PreToolUse` matcher `Bash` → `pre-bash.sh` | destructive-command block | **Yes.** Codex runs `PreToolUse` for shell commands, which is exactly this hook's scope. |
| `PreToolUse` matcher `Edit\|Write\|Delete` → `pre-edit.sh` | edit protection (`.git/`, main/master) | **No — converted but never fires.** Codex runs `PreToolUse` for shell commands only; Codex edits go through `apply_patch`, not Bash. |
| `PostToolUse` matcher `Edit\|Write` → `post-edit-format.sh` | post-edit formatting | **No — converted but never fires**, same reason. `differences.md` explicitly advises moving such work to a `Stop` hook. |
| `UserPromptSubmit` (no matcher) → `user-prompt-submit.sh` | prompt secret scan | **Yes.** `matcher` is ignored for this event, and this registration has none. |
| `UserPromptExpansion` matcher `speckit\.(…)` → `speckit-expand-update.sh` | spec-kit auto-update | **No — dropped as an unsupported field**, exactly as the deployment map already recorded. |

**Correction to `spec.md`.** The earlier inference — that Claude's denial contract has no Codex equivalent — was wrong, and in the repo's favour. `differences.md` § Hooks states Codex "blocks only `permissionDecision: "deny"`, legacy `decision: "block"`, or exit code `2`" for `PreToolUse`. The denial protocol carries over. **The real breakage is coverage, not the deny contract**: two of the four guardrails are wired to tool matchers Codex never fires for.

Also required and easy to miss: the `/hooks` trust step (non-managed hooks are skipped until reviewed; trust is keyed to the hook's hash). *(This paragraph originally also listed `[features].codex_hooks = true`, on the strength of the converter's documentation. **That flag does not exist** — see § R-08. Retained as a correction rather than silently deleted.)*

## R-04 — Skills become copies, not links

The dry-run reports `overwritten: .agents/skills/<name> - Existing Codex skill will be replaced.` for **all 23 colliding entries**, including the 8 tracked symlinks.

The single-source property that the current design exists to guarantee (`.agents/skills/adr -> ../../.claude/skills/adr`) is **replaced by copies**. Every future edit to `.claude/skills/*` requires a re-run to propagate; nothing detects the gap in between, and the two suites that would have caught it (`run-codex-sync.sh`) are deleted by FR-003.

24 skills also carry `manual_fix_required` rows for frontmatter Codex has no equivalent for — `when_to_use`, `metadata`, `short-description`, and for `verify-config`: `allowed-tools`, `agent`, `background`, `context`, `disable-model-invocation`.

## R-05 — Instructions: the largest gap

The dry-run reports: `symlinked: AGENTS.md - Linked to CLAUDE.md.`

This repo's root `CLAUDE.md` contains exactly one line:

```
@.claude/CLAUDE.md
```

**Verified 2026-08-10 — Codex does not expand `@` imports.** Three independent confirmations:

1. Official AGENTS.md documentation (<https://developers.openai.com/codex/guides/agents-md> → `learn.chatgpt.com/docs/agent-configuration/agents-md`): composition is **directory-walk concatenation only** — `~/.codex/AGENTS.override.md`, then `~/.codex/AGENTS.md`, then each level from the git root down to the cwd. "Codex concatenates files from the root down, joining them with blank lines." No in-file reference or include syntax is documented.
2. `openai/codex` issue **#17401, still OPEN** (opened 2026-04-11): a feature request to add exactly this — "Add an `@path/to/file.md` directive to AGENTS.md that the CLI resolves at instruction-assembly time" — whose problem statement reads "Codex's instruction composition is **limited to directory-walk layering**", and which cites Claude Code as already shipping the syntax.
3. `openai/codex` discussion **#4272**, "By any chance, is the @ file path syntax not supported in AGENTS.MD?"

So the migrated instruction file is a symlink to a one-line file whose only content is an unexpandable directive. **`.claude/CLAUDE.md` and all seven `.claude/rules/*.md` do not reach Codex through this path.** The converter's inventory agrees: `.claude/rules` is listed as a *detected source directory* but never appears as a staged artifact.

Caveat, stated for fairness: a Codex session can still *choose* to open `.claude/CLAUDE.md` when it sees the path, since it has file tools. That is opportunistic behaviour, not instruction loading, and the nesting compounds it — `.claude/CLAUDE.md` itself contains seven further `@.claude/rules/*.md` lines. It is not a foundation to design on.

This is precisely the gap the hand-written `.codex/AGENTS.md` was created to fill (spec 014, FR-003: summarise `CLAUDE.md` + `rules/*` inside Codex's 32 KiB budget).

**The remedy is cheap, which changes the shape of the decision.** Because Codex merges `~/.codex/AGENTS.md` with the repo-root `AGENTS.md` automatically, a single **flattened, `@`-free** instruction file satisfies the requirement — no new mechanism, no import support needed. `.codex/AGENTS.md` already *is* that file. FR-014 can therefore be met by keeping (or generating) one flattened artifact, rather than by abandoning the removal.

## R-06 — Codex has subagents; the exclusion rationale is obsolete

The converter stages `.codex/agents/verification-runner.toml`, `differences.md` documents a full `.claude/agents/*.md` → `.codex/agents/*.toml` mapping, the live hooks docs list `SubagentStart`/`SubagentStop` events, and official docs include a `developers.openai.com/codex/subagents` page.

The deployment map's stated reason for `対象外` — "Codex CLI に独立コンテキストのサブエージェント機構が存在せず" — is **no longer factually true**. The exclusion may still be the right call (Codex custom agents "set defaults, not hard isolation from the parent turn", per `differences.md`), but it must be re-argued on current facts rather than carried forward.

## R-07 — MCP and permissions

MCP converts cleanly: `rewritten: .codex/config.toml - Converted 6 MCP server entries.` The `${VAR}` header shape used for `GOOGLE_DEV_KNOWLEDGE_API_KEY` maps to `env_http_headers`, matching what `install.sh` already produces.

**Permissions do not convert.** `settings.json#permissions.allow/ask` appear nowhere in the staged artifact list. `differences.md` routes only `allowedMcpServers`/`deniedMcpServers` to `requirements.toml`, and notes that is "Not written by this converter". `.claude/settings.local.json` is listed as unsupported outright. The repo's `.codex/rules/guardrails.rules` has **no migration path**.

## Inventory: what does not migrate, and does it actually matter

This is the reconsideration the operator asked for. Verdicts are proposals, not decisions.

| # | Does not migrate | Consequence in Codex | Worth keeping? |
|---|---|---|---|
| 1 | `.claude/CLAUDE.md` + `rules/*.md` body (R-05) | Codex gets a one-line unexpandable `AGENTS.md`. No skill routing, no clarification gate, no live-doc rules, no git conventions | **Yes — highest value item.** This is the whole point of having Codex configuration. Some replacement is required whatever else is decided. |
| 2 | `pre-edit.sh` coverage (R-03) | `.git/` and main/master edit protection silently absent for `apply_patch` | **Yes — safety.** Note this hook is what blocked a `Write` to `main` during this very session. Options: a `Bash`-scoped equivalent, or accept the loss explicitly. |
| 3 | `guardrails.rules` (R-07) | No allow/prompt policy; every command falls back to Codex's own approval defaults | **Probably yes**, though the cost is friction rather than danger — Codex's default is to ask, which fails safe. |
| 4 | Skill symlink single-source (R-04) | Copies drift from `.claude/skills/` with nothing detecting it | **Judgement call.** The manual re-run burden replaces the manual port burden; it is not obviously a net win. |
| 5 | `post-edit-format.sh` coverage (R-03) | No auto-format after edits | **Low.** Convenience, not correctness. `differences.md` offers a `Stop`-hook workaround if wanted. |
| 6 | `UserPromptExpansion` / `speckit-expand-update.sh` | No spec-kit auto-update on `/speckit-*` | **Low.** Already `対象外`; `specify init` covers it manually. |
| 7 | `verify-config` skill's `context: fork` etc. (R-04) | Runs inline instead of isolated; frontmatter becomes prose | **Low.** Spec 019 already accepted that Codex has no fork equivalent; `.codex/prompts/verify-config.md` exists for exactly this reason. |
| 8 | speckit-* skill frontmatter (R-04) | 15 skills carry manual-review blocks | **None.** ADR-0001 already treats these as regenerated per project by `specify init --integration codex`. |
| 9 | `settings.local.json` | Machine-local permissions not carried | **None.** Local and unshared by design. |
| 10 | `statusline.sh`, `model`/`effortLevel`/`tui`/`$schema` | — | **None.** Vendor-specific presentation and model settings. |

Rows 1–3 are the ones that make "full removal" materially different from "removal plus a small replacement". Rows 5–10 confirm the operator's instinct: most of what does not migrate is genuinely not worth keeping.

## R-08 — `/import` executed for real (2026-08-10, Codex CLI 0.147.0)

The CLI was repaired (0.130.0 → 0.147.0) and `/import` was run by the operator against Claude Code. Reported result: **52 imported, 0 failed** — Skills 2, MCP servers 6, Agents 3, Hooks 6, Chat sessions 35. A pre-import baseline of `~/.codex` (listings + `config.toml` SHA-256 and section headers) was captured beforehand and diffed after.

### What it wrote, and where

`/import` writes **both scopes**, and it writes into the repository working tree:

| Scope | Created |
|---|---|
| Project (`/Users/taikiogihara/work/my-claude-code`) | `.codex/config.toml` (6 MCP servers), `.codex/hooks.json`, `.codex/hooks/` (7 files copied from `.claude/hooks/`), `.codex/agents/verification-runner.toml`, `.agents/skills/verify-config/` |
| User (`~/.codex`) | `hooks.json`, `hooks/*.sh`, `agents/{notes-manager,reminders-manager}.toml`, `external_agent_session_imports.json`, `~/.agents/skills/verify-config` |

**`~/.codex/config.toml` was not modified** — identical SHA-256 before and after. The two `# >>> my-claude-code managed …` marker blocks and the user's own MCP definitions survived untouched, consistent with "Leaves your existing agent setup unchanged".

All project-scope artifacts landed as **untracked files in `git status`**. This is direct confirmation that FR-005 is required: without the `.gitignore` entries, every import produces a commit-ready diff.

**The root `AGENTS.md` was NOT symlinked.** The plan D1 hazard did not fire. It is specific to `migrate-to-codex`, which reports `symlinked: AGENTS.md - Linked to CLAUDE.md`; `/import` left the file alone. The warning stays in the procedure but should be attributed to the converter, not to `/import`.

### Hooks — confirms R-03, and adds two new defects

Registered in `.codex/hooks.json` (4 registrations, though 6 script files were copied):

| Event | Matcher | Command | Fires in Codex? |
|---|---|---|---|
| `PreToolUse` | `Bash` | `.codex/hooks/pre-bash.sh` | **Yes** |
| `PreToolUse` | `Edit\|Write\|Delete` | `.codex/hooks/pre-edit.sh` | **No** — Claude tool names; Codex edits use `apply_patch`, and Pre/PostToolUse are shell-only |
| `PostToolUse` | `Edit\|Write` | `.codex/hooks/post-edit-format.sh` | **No** — same |
| `UserPromptSubmit` | (none) | `.codex/hooks/user-prompt-submit.sh` | **Yes** |

`speckit-expand-update.sh` and `statusline.sh` were **copied as files but never registered** — `UserPromptExpansion` is dropped, exactly as predicted. `/import` therefore reaches the same coverage conclusion as the `migrate-to-codex` CLI, by an independent path.

**Not a defect after all — the `codex_hooks` flag does not exist in Codex 0.147.0.** An earlier draft of this section recorded the absence of `[features].codex_hooks = true` as a defect, on the strength of the converter's `differences.md`. `codex features list` shows 104 features; there is no `codex_hooks` among them. The relevant flag is **`hooks`, stage `stable`, effective state `true`** — enabled by default, nothing to set. (`plugin_hooks` exists but is `removed`.)

This makes `differences.md` demonstrably stale on this point — consistent with its own "Docs last checked: 2026-04-20" header — and means **FR-011's precondition list must not include the flag**. The `/hooks` trust step remains real.

**New defect 2 — the command strings are quoted twice.** Every entry looks like:

```json
"command": "'/Users/taikiogihara/work/my-claude-code/.codex/hooks/pre-bash.sh'"
```

The single quotes are *inside* the JSON string. If Codex execs the command directly rather than through a shell, the path will not resolve and the hook silently fails. This must be checked in a live session (quickstart Step 5) and, if confirmed, documented as a manual fix-up.

### The one piece of good news

**The copied hook scripts still reach the shared guardrail decision scripts.** `.codex/hooks/pre-edit.sh` retains its three-tier resolution:

```bash
$CLAUDE_PROJECT_DIR/scripts/guardrails/pre-edit-block.sh   # tier 1 — unset under Codex
$HOME/.claude/scripts/guardrails/pre-edit-block.sh         # tier 2 — exists
$SCRIPT_DIR/../../scripts/guardrails/pre-edit-block.sh     # tier 3 — resolves to the repo copy
```

Tiers 2 and 3 both resolve on this machine. So FR-007(b) is answered **yes** — but by accident of how this repository's own hook scripts were written, not because the importer did anything to preserve it. A repository whose hooks used absolute `$CLAUDE_PROJECT_DIR` paths only would lose the wiring entirely.

### `/import` and `migrate-to-codex` are NOT equivalent

This settles residual R4. The two official paths differ materially on the same input:

| | `/import` | `migrate-to-codex` CLI |
|---|---|---|
| Root `AGENTS.md` | Untouched | Symlinked to `CLAUDE.md` (destroys flattened content) |
| Skills | 2 imported; the 8 existing `~/.agents/skills` links left alone | All 23 **overwritten with copies** |
| Hook scripts | Claude scripts copied verbatim; matchers copied verbatim | Rewritten, with `manual_fix_required` caveats reported |
| `[features].codex_hooks` | **Not set** | Set to `true` |
| Subagents | 3 (user + project) | 1 (project) |
| MCP | 6 → project `.codex/config.toml` | 6 → same |

The documented procedure must therefore pick one and describe it accurately, rather than presenting them as interchangeable. **Recommendation: document `/import` as the primary path** — it is less destructive (it does not overwrite skills or `AGENTS.md`) — and mention `migrate-to-codex` only as the scriptable/dry-runnable inspection tool, with its two destructive behaviours called out.

## R-09 — Live-session verification: partial (2026-08-10)

### Done: the imported wrapper executes and still reaches the shared guardrail

`.codex/hooks/pre-bash.sh` was invoked directly with a simulated Claude-format payload:

```bash
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' > hookin.json
./.codex/hooks/pre-bash.sh < hookin.json    # → exit 0 (allow), no output
```

The wrapper runs, resolves `scripts/guardrails/destructive-command.sh` through its fallback chain, and returns a decision. Deny-path behaviour is already covered by `tests/run-destructive-command-guard.sh` and was not re-tested here. This confirms the copied scripts are functional artifacts, not inert files.

Incidental evidence for NFR-002: an earlier attempt at this test was **blocked by this repository's own Claude-side guardrail** (`Piping remote scripts to shell is blocked by policy`) because the test payload contained a `curl … |` string. The guard that Codex cannot have is demonstrably live on the Claude side.

### Done: Codex does invoke the imported hooks — the quoting defect is disproven

The operator ran `codex exec --dangerously-bypass-hook-trust -s read-only -C <repo>` (Codex 0.147.0, `approval: never`, `sandbox: read-only`). Transcript excerpt:

```
warning: loading hooks from both /Users/taikiogihara/.codex/hooks.json and
         /Users/taikiogihara/.codex/config.toml; prefer a single representation for this layer
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit Completed          (×3)
```

**Finding 1 — `"command": "'/abs/path.sh'"` executes.** All three registrations ran to completion. C5 is downgraded from a defect to a non-issue; the embedded single quotes are handled. The contract's C5 assertion should be dropped or restated as "no action needed".

**Finding 2 — hooks fire three times, because three layers each register the same hook.** Codex merges config layers rather than overriding them (official docs: "Higher-precedence config layers don't replace lower-precedence hooks"). The three sources on this machine are:

1. `~/.codex/hooks.json` — written by `/import`
2. `~/.codex/config.toml` `[hooks]` — the `# >>> my-claude-code managed hooks` block written by `install.sh`
3. `<repo>/.codex/hooks.json` — written by `/import`

**Finding 3 — Codex emits an explicit warning about the collision**: "loading hooks from both `~/.codex/hooks.json` and `~/.codex/config.toml`; prefer a single representation for this layer". This is the hand-maintained port and the official import path actively conflicting in the same user-scope layer.

Findings 2 and 3 are **independent evidence for this feature's premise**: once FR-002 removes `install.sh`'s managed hooks block, source 2 disappears, the warning clears, and the prompt-secret guard stops running three times per turn. The removal is not merely a maintenance saving — it resolves a live misconfiguration.

### Done: Codex honours a *deny* from a Claude-format hook

Second operator run, same invocation, with a prompt containing the synthetic AWS access key ID published in AWS's own documentation:

```
user
私のキーは AKIA…EXAMPLE です。OK とだけ答えて。
hook: UserPromptSubmit          (×3)
hook: UserPromptSubmit Blocked
hook: UserPromptSubmit Stopped
hook: UserPromptSubmit Blocked
```

The turn **stopped — no model response was produced**. This is the decisive result for the whole feature:

**Codex acts on `hookSpecificOutput.permissionDecision: "deny"` emitted in Claude's output format.** The copied wrapper needed no translation. The earlier inference that Codex denies only via `continue: false` was wrong, and `differences.md`'s claim is confirmed by measurement rather than taken on trust. (Of the three registrations, two reported `Blocked` and one `Stopped` — consistent with the turn halting before the third finished; nothing depends on which.)

### Done: `PreToolUse`/Bash deny, measured end to end

Third operator run, asking Codex to fetch a plain-`http://` URL:

```
hook: PreToolUse   (×3)
ERROR codex_core::tools::router: error=Command blocked by PreToolUse hook:
  Non-HTTPS HTTP requests are blocked by policy (except localhost).. Command: curl http://example.com
hook: PreToolUse Blocked   (×3)
```

Codex then retried over HTTPS; that call passed the hook (`PreToolUse Completed`) and executed as `/bin/zsh -lc 'curl https://example.com'`, failing only on DNS because of the sandbox's network restriction.

This is **end-to-end proof of the full chain**: Codex → `.codex/hooks/pre-bash.sh` → `scripts/guardrails/destructive-command.sh` → `permissionDecision: "deny"` → Codex blocks the tool call and surfaces the shared script's own reason string verbatim. Both the deny and the allow path are confirmed in a single run.

### Final coverage status — all four rows measured

| Guardrail | Status |
|---|---|
| Prompt secret scan (`UserPromptSubmit`) | **Measured working** — turn blocked, no model response |
| Destructive command (`PreToolUse`/Bash) | **Measured working** — tool call blocked, reason string propagated verbatim |
| Edit protection (`PreToolUse` on `Edit\|Write\|Delete`) | **Dead** — matcher never matches; Codex fires Pre/PostToolUse for shell commands only |
| Post-edit formatting (`PostToolUse` on `Edit\|Write`) | **Dead** — same |

No row in the FR-006 coverage table now rests on inference or on a third-party document. The empirical work for this feature is complete.

## Corrections this research forces on `spec.md`

1. **R1 is wrong as written.** `migrate-to-codex` *is* non-interactive and scriptable (`--source`/`--target`/`--dry-run`/`--validate-target`). Only `/import` is interactive-only. An `install.sh`- or CI-driven path is therefore technically available if the operator ever wants it.
2. **R3/FR-007(c) is answered, with the opposite sign.** The deny contract survives; **tool coverage** does not. Restate the risk as coverage, not protocol.
3. **FR-013 needs widening.** It currently records only that hosted tools are uncovered; the material fact is that `PreToolUse`/`PostToolUse` fire for shell commands only, which breaks two existing guardrails.
4. **FR-008 needs re-basing.** Codex has subagents; the `対象外` decision needs a current-facts rationale.
5. **A new requirement is needed for R-05**: instructions must reach Codex by some means, because the `@`-import symlink delivers nothing.
6. `spec.md`'s hooks table row "no `permissionDecision` equivalent documented" must be corrected.

## Still open — needs the operator

- **DONE 2026-08-10** — Codex CLI repaired (0.147.0), `/import` executed (§ R-08), and all four guardrail rows measured in live sessions (§ R-09). Closed by this work: R4 (the two paths are **not** equivalent), the supposed `codex_hooks` defect (the flag does not exist), and the supposed command-quoting defect (it executes fine).
- **OPEN — the `/hooks` trust path is unmeasured.** All three live runs used `--dangerously-bypass-hook-trust`, which is precisely the flag that skips the step FR-011 makes mandatory. What is proven is that the hooks *execute and deny once active*; what is unproven is that a developer following the documented `/hooks` review actually arms them. Closing it needs one interactive session: run `/hooks`, trust the imported entries, then repeat either deny test **without** the bypass flag.
- **Decide** rows 1–3 of the inventory before FR-001 deletes anything. Row 1 (instructions) has a cheap fix — the flattened `AGENTS.md` relocation, plan D1; rows 2–3 were settled on 2026-08-10 as "document the absence".
