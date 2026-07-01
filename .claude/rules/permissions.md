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
- `.claude/hooks/speckit-expand-update.sh` (UserPromptExpansion, matcher `speckit.(specify|clarify|plan|tasks|implement|checklist|analyze|taskstoissues|constitution|converge)`) runs before `/speckit-*` expands: resolves the latest stable `spec-kit` release from GitHub's `releases/latest` API (excludes drafts/prereleases; falls back to `gh release list --exclude-drafts --exclude-pre-releases`), upgrades `specify-cli` via `uv` or `pipx` from an HTTPS release tarball (falls back to `git+https://...` if the tarball download fails), then `specify init --here --force` when `.specify/` exists (network access; may refresh slash commands and overwrite Spec Kit template files—see Spec Kit upgrade guide). After a successful init it syncs the regenerated `speckit-*` skills into the user-scope install (`~/.claude/skills`); opt out with `SPECIFY_SYNC_USER_SKILLS=0`.
- Git permissions in `.claude/settings.json` default to read-style allow (`status`, `diff`, `log`, `fetch`) and ask for write-style operations (`add`, `commit`, `checkout`, `branch`, `stash`, `pull`).
- The repo's own non-destructive verification commands are allow-listed in `.claude/settings.json` to avoid prompt friction: the behavior suites (`tests/run-*.sh`), `scripts/check-mcp-consistency.sh`, and the lint/format tools (`shellcheck`, `shfmt`, `jq`, `yamllint`). These read or reformat repo files only; git write operations stay on `ask`.

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)
