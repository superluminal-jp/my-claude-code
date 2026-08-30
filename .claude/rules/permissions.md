# Permission Rules

Purpose: decide whether an action runs, prompts, or is blocked. Least privilege, fail-safe defaults. Two tiers, and the difference matters: **configuration is enforced by the client; everything else here depends on judgement.**

## Enforced by configuration

`.claude/settings.json` → `permissions.deny` blocks reads of credential paths (`.env`, `.env.*`, `secrets/`, `credentials/`, `.ssh/`, `.aws/`, `*.pem`, `*.p12`, `*.pfx`). That file is the canonical list — not restated here. Rationale, pattern constraints, accepted side effects: `docs/adr/0014-restore-credential-deny-rules.md`.

Boundary — never imply more than this:

- **Covered**: built-in file tools, and the file commands Claude Code recognises in Bash (`cat`, `head`, `tail`, `sed`). A `Read` deny also blocks Edit and Write on that path, including file creation.
- **Not covered**: subprocesses that open files themselves (a Python or Node script), and anything OS-level. That needs the sandbox, which this repository does not enable.

## Self-applied — nothing enforces these

Hooks and guardrail scripts were removed with no replacement (ADR-0005, ADR-0007). Apply these yourself.

- **Confirm first**: recursive deletion; `git reset --hard`, `push --force`, `clean -f`; dropping a database table or collection; overwriting files with uncommitted changes.
- **AWS resource mutation** — creating, modifying, or deleting live AWS resources (`deploy-on-aws`'s `deploy` skill, IaC apply, mutating `aws` CLI calls) requires explicit confirmation **every time**, regardless of prior approval this session (ADR-0009). Default use of that plugin is diagram generation.
- **Installs are project-scoped only**, never global: no `pip install --user` or under `sudo`, no `uv pip install --system`, no `npm`/`pnpm`/`yarn` global install, no `gem install` without `--user-install`, no `cargo install` without `--path`. Governs Claude's own calls only.
- **Credential filenames matched by substring** (`secret`, `credential`, `token`, `key`) — never read, display, log, or commit. Prose deliberately: `**/*key*` would match `.claude/keybindings.json`, and a deny rule admits no allowlist exception, so over-blocking could not be relaxed (ADR-0014).
- **Network defaults to deny**: no `curl | bash` or `wget | sh`, no executing scripts fetched from external URLs, no non-HTTPS endpoints except `localhost` / `127.0.0.1`.
