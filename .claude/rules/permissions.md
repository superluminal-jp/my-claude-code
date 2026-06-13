# Permission Rules

Purpose: decide whether an action runs, prompts, or is blocked. Applies to every Bash command, file read/write, and network call. Grounded in least-privilege (default-deny for destructive and network actions).

Evaluation order: **deny → ask → allow** (first match wins; deny always overrides).

## Destructive Operations — confirm before executing

- `rm -rf` or equivalent recursive deletion (always blocked when targeting `/`, `~`, `.`, or `$HOME`; otherwise routes to user confirmation)
- `git reset --hard` (discards uncommitted work)
- `git push --force` / `-f` (rewrites remote history)
- `git clean -f` (deletes untracked files)
- Drop database table / collection
- Overwrite files with uncommitted changes

## Credential Safety — never read, display, log, or commit

- `.env`, `.env.*`
- `secrets/`, `credentials/`, `.aws/`, `.ssh/` directories
- Filenames containing `secret`, `credential`, `token`, `key`
- Private keys: `.pem`, `.p12`, `.pfx`

Enforcement:

- `Read` denies in `.claude/settings.json` cover the credential paths above.
- `.claude/hooks/pre-bash.sh` (PreToolUse/Bash) blocks destructive commands, `curl | bash`, non-localhost `http://`, credential reads (`cat`/`less`/`more`/`head`/`tail`/`od`/`hexdump`, including `.env`, `secrets/`, and `credentials/`), and credential-path writes (redirection or `tee`). `sudo` is routed to user confirmation via `permissionDecision: "ask"`.
- `.claude/hooks/user-prompt-submit.sh` (UserPromptSubmit) blocks prompts containing AWS access keys (`AKIA…`/`ASIA…`), GitHub tokens (`ghp_…`, `github_pat_…`), Slack tokens (`xox[abpors]-…`), Google API keys (`AIza…`), and `-----BEGIN … PRIVATE KEY-----` blocks.
- `.claude/hooks/speckit-expand-update.sh` (UserPromptExpansion, matcher `speckit.(specify|clarify|plan|tasks|implement|checklist|analyze|taskstoissues|constitution)`) runs before `/speckit-*` expands: upgrades `specify-cli` via `uv` or `pipx`, then `specify init --here --force` when `.specify/` exists (network access; may refresh slash commands and overwrite Spec Kit template files—see Spec Kit upgrade guide).
- Git permissions in `.claude/settings.json` default to read-style allow (`status`, `diff`, `log`, `fetch`) and ask for write-style operations (`add`, `commit`, `checkout`, `branch`, `stash`, `pull`).

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)
