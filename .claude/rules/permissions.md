# Permission Rules

Two tiers, and the difference binds: **configuration is enforced by the client; everything below it depends on judgement.**

## Enforced by configuration

`.claude/settings.json` → `permissions.deny` blocks reads of credential paths (`.env`, `.env.*`, `secrets/`, `credentials/`, `.ssh/`, `.aws/`, `*.pem`, `*.p12`, `*.pfx`). That file is the canonical list — not restated here.

Boundary — never imply more than this:

- **Covered**: built-in file tools, and the file commands Claude Code recognises in Bash (`cat`, `head`, `tail`, `sed`). A `Read` deny also blocks Edit and Write on that path, including file creation.
- **Not covered**: subprocesses that open files themselves (a Python or Node script), and anything OS-level.

## Self-applied — nothing enforces these

- **Confirm first**: recursive deletion; `git reset --hard`, `push --force`, `clean -f`; dropping a database table or collection; overwriting files with uncommitted changes.
- **AWS resource mutation** — creating, modifying, or deleting live AWS resources (`deploy-on-aws`'s `deploy` skill, IaC apply, mutating `aws` CLI calls) requires explicit confirmation **every time**, regardless of prior approval this session. Default use of that plugin is diagram generation.
- **Installs are project-scoped only**, never global: no `pip install --user` or under `sudo`, no `uv pip install --system`, no `npm`/`pnpm`/`yarn` global install, no `gem install` without `--user-install`, no `cargo install` without `--path`. Governs Claude's own calls only.
- **Credential filenames matched by substring** (`secret`, `credential`, `token`, `key`) — never read, display, log, or commit.
- **Network defaults to deny**: no `curl | bash` or `wget | sh`, no executing scripts fetched from external URLs, no non-HTTPS endpoints except `localhost` / `127.0.0.1`.

## References

- Jerome H. Saltzer & Michael D. Schroeder, "The Protection of Information in Computer Systems," _Proceedings of the IEEE_ 63(9), 1975 — least privilege, fail-safe defaults: <https://www.cs.virginia.edu/~evans/cs551/saltzer/>
