# Permission Rules

Purpose: decide whether an action runs, prompts, or is blocked. Applies to every Bash command, file read/write, and network call. Grounded in the security design principles of **least privilege** and **fail-safe defaults** (default-deny for destructive and network actions) — Saltzer & Schroeder, 1975 (see [References](#references)). This file states policy only. Automatic enforcement of the destructive-operation and credential-safety rules below — via `.claude/hooks/` and the pattern-matching logic that used to live in `scripts/guardrails/*.sh` — was removed entirely with no replacement (see `docs/adr/0005-remove-claude-hooks.md` and `docs/adr/0007-remove-scripts.md`).

Evaluation order: **deny → ask → allow** (first match wins; deny always overrides).

## Destructive Operations — confirm before executing

- `rm -rf` or equivalent recursive deletion (always blocked when targeting `/`, `~`, `.`, or `$HOME`; otherwise routes to user confirmation)
- `git reset --hard` (discards uncommitted work)
- `git push --force` / `-f` (rewrites remote history)
- `git clean -f` (deletes untracked files)
- Drop database table / collection — no hook can detect this; self-apply
- Overwrite files with uncommitted changes — no hook can detect this; self-apply
- AWS resource operations via the `deploy-on-aws` plugin's `deploy` skill, or any other action that creates, modifies, or deletes live AWS resources (IaC apply/deploy, `aws` CLI mutating commands) — no hook can detect this; self-apply. Default use of this plugin is diagram generation (`aws-architecture-diagram`); any deploy/resource-mutating action requires explicit confirmation every time, regardless of prior approvals in the same session (see `docs/adr/0009-adopt-deploy-on-aws-plugin.md`).

## Package Installs — Claude installs project-scoped only

Claude may install dependencies only within the scope of the current project (virtual env, `package.json` local deps, etc.), never globally. This governs Claude's own Bash calls; the user remains free to install tools globally themselves.

- Blocked for Claude: `pip`/`pip3 install --user` or under `sudo`, `uv pip install --system`, `npm`/`pnpm install|add -g`/`--global`, `yarn global add`, `gem install` without `--user-install`, `cargo install` without `--path`.

## Credential Safety — never read, display, log, or commit

- `.env`, `.env.*`
- `secrets/`, `credentials/`, `.aws/`, `.ssh/` directories
- Filenames containing `secret`, `credential`, `token`, `key`
- Private keys: `.pem`, `.p12`, `.pfx`

`Read` denies for these paths, prompt-level scanning, and shell-level blocking were all removed with no automated replacement — see `docs/adr/0005-remove-claude-hooks.md` and `docs/adr/0006-remove-permissions-config.md`. This section is policy only now; nothing in Claude Code enforces it automatically.

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs — no hook can detect this two-step pattern; self-apply
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)

## `.claude/settings.json` permissions

None anymore. The `permissions` block (allow/ask/deny) was removed entirely
from both `.claude/settings.json` and `.claude/settings.local.json` — see
`docs/adr/0006-remove-permissions-config.md`. Every action, including commits and
git writes, now goes through Claude Code's default interactive prompting
with no automated allow/ask shortcuts or deny blocks.

## References

- Jerome H. Saltzer & Michael D. Schroeder, "The Protection of Information in Computer Systems," *Proceedings of the IEEE* 63(9): 1278–1308, 1975 (least privilege, fail-safe defaults) — <https://www.cs.virginia.edu/~evans/cs551/saltzer/>
