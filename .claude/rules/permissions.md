# Permission Rules

Evaluation order: **deny → ask → allow** (first match wins; deny always overrides).

## Destructive Operations — confirm before executing

- `rm -rf` or equivalent recursive deletion
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
- `.claude/hooks/pre-bash.sh` (PreToolUse/Bash) blocks destructive commands, `curl | bash`, non-localhost `http://`, credential reads (`cat`/`less`/`more`/`head`/`tail`/`od`/`hexdump`), and credential-path writes (redirection or `tee`). `sudo` is routed to user confirmation via `permissionDecision: "ask"`.
- `.claude/hooks/user-prompt-submit.sh` (UserPromptSubmit) blocks prompts containing AWS access keys (`AKIA…`/`ASIA…`), GitHub tokens (`ghp_…`, `github_pat_…`), Slack tokens (`xox[abpors]-…`), Google API keys (`AIza…`), and `-----BEGIN … PRIVATE KEY-----` blocks.
- `.claude/hooks/post-write.sh` (PostToolUse/Write|Edit|MultiEdit) emits non-blocking doc-sync reminders per `.claude/rules/development.md` triggers when the repo has targetable docs.

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)
