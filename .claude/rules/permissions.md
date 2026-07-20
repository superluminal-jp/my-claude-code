# Permission Rules

Purpose: decide whether an action runs, prompts, or is blocked. Applies to every Bash command, file read/write, and network call. Grounded in the security design principles of **least privilege** and **fail-safe defaults** (default-deny for destructive and network actions) — Saltzer & Schroeder, 1975 (see [References](#references)). This file states policy only; hook mechanics (exact scripts, matchers, regexes) are `.claude/hooks/README.md`'s domain — don't restate them here.

Evaluation order: **deny → ask → allow** (first match wins; deny always overrides).

## Destructive Operations — confirm before executing

- `rm -rf` or equivalent recursive deletion (always blocked when targeting `/`, `~`, `.`, or `$HOME`; otherwise routes to user confirmation)
- `git reset --hard` (discards uncommitted work)
- `git push --force` / `-f` (rewrites remote history)
- `git clean -f` (deletes untracked files)
- Drop database table / collection — no hook can detect this; self-apply
- Overwrite files with uncommitted changes — no hook can detect this; self-apply

## Package Installs — Claude installs project-scoped only

Claude may install dependencies only within the scope of the current project (virtual env, `package.json` local deps, etc.), never globally. This governs Claude's own Bash calls; the user remains free to install tools globally themselves.

- Blocked for Claude: `pip`/`pip3 install --user` or under `sudo`, `uv pip install --system`, `npm`/`pnpm install|add -g`/`--global`, `yarn global add`, `gem install` without `--user-install`, `cargo install` without `--path`.

## Credential Safety — never read, display, log, or commit

- `.env`, `.env.*`
- `secrets/`, `credentials/`, `.aws/`, `.ssh/` directories
- Filenames containing `secret`, `credential`, `token`, `key`
- Private keys: `.pem`, `.p12`, `.pfx`

`Read` denies in `.claude/settings.json` cover the paths above; prompt-level and shell-level enforcement mechanics: `.claude/hooks/README.md`.

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs — no hook can detect this two-step pattern; self-apply
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)

## `.claude/settings.json` permissions

- Git: `status`/`diff`/`log`/`fetch`/`commit` allow (`commit` auto-allowed — `git-workflow.md`'s "commit only when asked" still governs *whether* Claude commits, this only removes the per-call prompt); `add`/`checkout`/`branch`/`stash`/`pull` ask.
- Allow-listed to avoid prompt friction (read or reformat repo files only, no write-style git ops among them): the behavior suites (`tests/run-*.sh`), `scripts/check-mcp-consistency.sh`, `scripts/guardrails/*.sh`, `.codex/hooks/*.sh`, and the lint/format tools (`shellcheck`, `shfmt`, `jq`, `yamllint`).

## References

- Jerome H. Saltzer & Michael D. Schroeder, "The Protection of Information in Computer Systems," *Proceedings of the IEEE* 63(9): 1278–1308, 1975 (least privilege, fail-safe defaults) — <https://www.cs.virginia.edu/~evans/cs551/saltzer/>
