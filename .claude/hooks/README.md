# Claude Code Hooks

Purpose: document what each hook script actually does and when it fires, so this stays the single source of truth for hook *mechanics*. Policy rationale (why these rules exist) lives in `../rules/permissions.md`; this file documents the *implementation*.

Wiring is declared in `../settings.json` under `hooks` (and `statusLine` for the status line). All scripts are read-only with respect to their trigger unless noted, fail open on missing dependencies (`jq`, `shellcheck`, etc.), and never abort the session on their own errors except where a hook explicitly blocks (`exit 2`).

## Hook index

| Script | Event | Matcher | Effect |
|---|---|---|---|
| `pre-bash.sh` | `PreToolUse` | `Bash` | Blocks or gates dangerous shell commands before they run |
| `pre-edit.sh` | `PreToolUse` | `Edit\|Write\|Delete` | Blocks edits to `.git/` internals and to the `main`/`master` branch; warns on sensitive paths |
| `post-edit-format.sh` | `PostToolUse` | `Edit\|Write` | Formats/lints the file just written (shfmt, shellcheck, yamllint, jq, `@import` check) |
| `user-prompt-submit.sh` | `UserPromptSubmit` | — | Blocks prompts that contain obvious credential material |
| `speckit-expand-update.sh` | `UserPromptExpansion` | `speckit\.(specify\|clarify\|plan\|tasks\|implement\|checklist\|analyze\|taskstoissues\|constitution\|converge)` | Upgrades `specify-cli` and refreshes Spec Kit project files before a `/speckit-*` command expands |
| `session-start.sh` | `SessionStart` | — | Installs the lint toolchain (jq/shellcheck/yamllint/shfmt) on Claude Code Web containers only |
| `statusline.sh` | `statusLine` (not a hook event) | — | Renders `<model> \| <dir> \| <branch>` for the TUI status line |

Exit-code convention for `PreToolUse` / `UserPromptSubmit`: `exit 2` blocks the action and shows stderr to Claude; `exit 0` allows it. A hook can also allow-with-confirmation by emitting a JSON body with `permissionDecision: "ask"` (see `pre-bash.sh`).

## `pre-bash.sh` — PreToolUse, matcher `Bash`

Reads `.tool_input.command` from stdin and blocks or gates it before execution:

- **Always blocked** (`exit 2`): `git push --force`/`-f`, `git reset --hard`, `git clean -f`, `rm -rf` targeting `/`, `~`, `.`, or `$HOME`, device-overwrite/`mkfs`/fork-bomb patterns, `curl|wget \| bash/sh/zsh`, non-HTTPS `http://` (except `localhost`/`127.0.0.1`), reads of credential paths (`.ssh/`, `.aws/`, `.env*`, `secrets/`, `credentials/`, `*.pem/.p12/.pfx`) via `cat`/`less`/`more`/`head`/`tail`/`od`/`hexdump`, writes to those same credential paths via redirection or `tee`, and global package installs (`pip`/`pip3 install --user` or under `sudo`, `uv pip install --system`, `npm`/`pnpm install|add -g|--global`, `yarn global add`, `gem install` without `--user-install`, `cargo install` without `--path`) — this only restricts Claude's own Bash calls, not what the user runs interactively.
- **Routed to user confirmation** (`permissionDecision: "ask"`): `rm -rf` on any other target, and `sudo`.
- Everything else falls through to `exit 0` (allowed).

Grounded in `../rules/permissions.md` "Destructive Operations" / "Credential Safety" / "Network".

## `pre-edit.sh` — PreToolUse, matcher `Edit|Write|Delete`

Reads `.tool_input.path` / `.tool_input.file_path` and:

- Blocks (`exit 2`) any path under `.git/`.
- Blocks (`exit 2`) edits when the current branch (resolved from `CLAUDE_PROJECT_DIR`) is `main` or `master` — this is what forces a feature branch before editing.
- Warns (stderr only, does not block) on CI config (`.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`), `.claude/settings*.json`, and production-looking paths (`*.prod.*`, `*production*`, `*.env.production`).

## `post-edit-format.sh` — PostToolUse, matcher `Edit|Write`

Reads the written file's path and, based on extension, silently reformats/lints it:

- `*.json` → `jq empty` syntax check (warns on stderr if invalid).
- `*.sh` → `shfmt -w -i 2` (2-space indent, matching repo convention) then `shellcheck`.
- `*.yaml`/`*.yml` → `yamllint`.
- `*/CLAUDE.md` → verifies every `@import` line resolves to an existing file relative to the repo root; warns on stderr if broken.

Never blocks (`exit 0` always); missing tools are silently skipped.

## `user-prompt-submit.sh` — UserPromptSubmit

Scans the raw prompt text for secret-shaped substrings and blocks (`exit 2`) if found: AWS access key IDs (`AKIA…`/`ASIA…`), GitHub tokens (`ghp_/gho_/ghu_/ghs_/ghr_…`, `github_pat_…`), Slack tokens (`xox[abpors]-…`), `-----BEGIN … PRIVATE KEY-----` blocks, and Google API keys (`AIza…`). Empty prompts pass through.

## `speckit-expand-update.sh` — UserPromptExpansion, matcher on `speckit.*` commands

Runs before any `/speckit-specify|clarify|plan|tasks|implement|checklist|analyze|taskstoissues|constitution|converge` command expands, scoped to workspaces that already have a `.specify/` directory (no-op otherwise):

1. **Upgrade specify-cli**: if `specify` is on `PATH`, runs `specify self upgrade` (its own updater, resolves latest stable via GitHub Releases). Otherwise bootstraps a first install by resolving the latest non-prerelease tag (GitHub `releases/latest` API, falling back to `gh release list`) and installing from an HTTPS tarball via `uv tool install` or `pipx`, falling back to `git+https://...` if the tarball fetch fails.
2. **Refresh project files**: runs `specify init --here --force --integration "$INTEGRATION"` (`INTEGRATION` defaults to `claude`, override via `SPECIFY_INTEGRATION`). `speckit.specify` always runs this step; every other command throttles it to once per `SPECIFY_AUTO_UPDATE_INTERVAL_SECONDS` (default 86400s), tracked in `.specify/.last-auto-update`. Set `SPECIFY_FORCE_AUTO_UPDATE=1` to bypass the throttle.
3. **Protect the constitution**: if `.specify/memory/constitution.md` differs from its template, it's backed up before `specify init` and restored immediately after, so customizations survive the refresh.

Spec Kit is opt-in per project: the regenerated `.claude/skills/speckit-*` skills stay local to the workspace that ran `specify init` — this hook never copies them to `~/.claude` or any other project (see `docs/adr/0001-remove-vendored-speckit-skills.md`).

Output is captured to a temp log and returned as `additionalContext` so Claude sees what happened; the hook itself never fails the turn (`|| true` around the body).

## `session-start.sh` — SessionStart

No-ops immediately unless `CLAUDE_CODE_REMOTE=true` (i.e., Claude Code Web). On web containers, best-effort installs `jq`, `shellcheck`, `yamllint`, and `shfmt` (apt, then pip/go fallbacks as applicable) so `post-edit-format.sh` and `scripts/check-mcp-consistency.sh` have their toolchain available. Never blocks session startup; reports what's still missing to stderr.

## `statusline.sh` — statusLine

Not a lifecycle hook — wired via the top-level `statusLine` key in `settings.json`, invoked whenever the TUI redraws the status line. Reads the status JSON payload from stdin and prints `<model> | <basename of cwd> | <git branch>`, degrading gracefully (falls back to `claude` / `$PWD` / omitting the branch) if any field is missing.
