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

Enforcement: `Read` denies in `.claude/settings.json` + Bash policy in `.claude/hooks/pre-bash.sh` (destructive cmds, `curl | bash`, non-localhost `http://`, credential reads via `cat`/`less`/`more`/`head`/`tail`/`od`/`hexdump`).

## Network — default deny

- `curl | bash` / `wget | sh`
- Execute scripts downloaded from external URLs
- Non-HTTPS endpoints (except `localhost` / `127.0.0.1`)
