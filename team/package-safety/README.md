# Package-install safety bundle

日本語版: [README.ja.md](README.ja.md)

A Claude Code configuration you can hand to a development team. When Claude
works in a project with it applied, a package installer runs third-party code
only under five conditions:

1. **Normally, only versions published at least 7 days ago are resolved** —
   the newest version past that age, not the newest version.
2. **A person approves every new package**, every ad-hoc package run, and
   every machine-wide install.
3. **Python packages go through uv**; Claude may not run `pip install`.
4. **Packages go into the project, not the machine**: global npm and pnpm
   installs and `uv pip install --system` are refused, and pip refuses to
   install outside a virtual environment (see [No global installs](#no-global-installs)).
5. **Installs run in the OS sandbox**, which reaches only the public npm and
   PyPI registries and cannot read the usual credential files or tokens.

`gh`, Terraform, and git over SSH cannot work inside the sandbox, so those
commands alone run outside it with their usual credentials, and their
operations that change something remote need approval each time (see
[Tools that run outside the sandbox](#tools-that-run-outside-the-sandbox)).

The decision record is
[ADR-0017](../../docs/adr/0017-team-package-install-safety-bundle.md).

## Contents

| File | Where it goes | What it does |
|---|---|---|
| [`claude-settings.json`](claude-settings.json) | A repository's `.claude/settings.json`, or a managed-settings drop-in | Claude-side controls: sandbox and its excluded commands, `ask`/`deny` rules, 7-day `env` |
| [`project/.npmrc`](project/.npmrc) | Repository root | npm: 7-day rule, no dependency install scripts |
| [`project/pnpm-workspace.yaml`](project/pnpm-workspace.yaml) | Repository root | pnpm: 7-day rule |
| [`project/uv.toml`](project/uv.toml) | Repository root (or `[tool.uv]` in `pyproject.toml`) | uv: 7-day rule |

The `project/` files apply to everyone who runs the package manager in the
repository — people and CI as well as Claude. `claude-settings.json` applies
only to Claude Code sessions.

## Apply it

The same `claude-settings.json` works in either place. Start with the
repository route; move to managed settings when the rules must not be
switchable off.

### Per repository (no admin rights; each member can override)

Run from the target repository's root, with `BUNDLE` pointing at this
directory:

```bash
BUNDLE=path/to/my-claude-code/team/package-safety
mkdir -p .claude
[ -f .claude/settings.json ] || echo '{}' > .claude/settings.json
jq -s 'def merge($a; $b): reduce ($b | keys_unsorted[]) as $k ($a; .[$k] = (if ($a[$k] | type) == "object" and ($b[$k] | type) == "object" then merge($a[$k]; $b[$k]) elif ($a[$k] | type) == "array" and ($b[$k] | type) == "array" then $a[$k] + ($b[$k] - $a[$k]) else $b[$k] end)); merge(.[0]; .[1])' .claude/settings.json "$BUNDLE/claude-settings.json" > .claude/settings.json.new && mv .claude/settings.json.new .claude/settings.json
cp -n "$BUNDLE/project/.npmrc" "$BUNDLE/project/pnpm-workspace.yaml" "$BUNDLE/project/uv.toml" .
echo '.pnpm-store/' >> .gitignore
```

The merge keeps every key and list entry the repository already has and adds
the bundle's; running it twice changes nothing. `cp -n` leaves an existing
file alone — merge its keys by hand, following the comments in each template.
Use only the templates for the package managers the repository uses, and if
`pyproject.toml` already has a `[tool.uv]` table, put `exclude-newer` there
instead of adding `uv.toml`. Commit the result.

Members get the `ask`/`deny` rules immediately and the `env` values after they
trust the folder. A member can still turn the sandbox off for themselves
(`sandbox.enabled: false` in their user or local settings), so this route
sets a default, not a guarantee.

### Managed settings (admin rights or MDM; cannot be overridden)

Copy the file into the managed drop-in directory on each machine:

```bash
sudo mkdir -p "/Library/Application Support/ClaudeCode/managed-settings.d"
sudo cp claude-settings.json "/Library/Application Support/ClaudeCode/managed-settings.d/package-safety.json"
```

On Linux and WSL the directory is `/etc/claude-code/managed-settings.d/`. An
MDM profile or the claude.ai admin console (server-managed settings) takes the
same keys. In managed settings you can additionally set
`"sandbox": {"allowUnsandboxedCommands": false}` so no command can retry
outside the sandbox, which also makes Claude Code ignore a repository's
sandbox-loosening settings. The bundle's own excluded commands keep working,
because they are then part of the managed file; other commands that cannot
work inside the sandbox, such as `docker` and `brew` (which writes outside
it), cannot run from Claude unless you add them to the managed
`sandbox.excludedCommands`.

## What each tool does

| Tool | 7-day rule | Minimum version | On an older version |
|---|---|---|---|
| npm | `min-release-age=7` (days) in `.npmrc` and `env` | 11.10 | Prints `Unknown … config "min-release-age"` and **ignores it** — check the version |
| pnpm | `minimumReleaseAge: 10080` (minutes) in `pnpm-workspace.yaml` | 10.16 | Not supported (behavior not verified) |
| pnpm (Claude `env`) | `pnpm_config_minimum_release_age` | 11 | pnpm 10 reads only `npm_config_*`; the repository template still covers it |
| uv | `exclude-newer = "P7D"` in `uv.toml` / `[tool.uv]` | 0.9.17 | **Fails** to parse the file, so every uv command stops until you upgrade |
| pip | Not used: Claude's `pip install` is denied; use uv | — | — |
| Homebrew | No equivalent setting | — | Claude must ask before every `brew install`/`upgrade`/`tap`; the person approving checks the release date |

The uv rule is deliberately not in `env`: a `UV_EXCLUDE_NEWER` that differs
from a project's own setting invalidates its `uv.lock`, so `uv sync --locked`
fails and `uv lock` rewrites the file.

## No global installs

Each project keeps its own packages — `node_modules/` for npm and pnpm, a
`.venv/` for Python — so nothing Claude installs changes another project or
the machine. Three layers enforce this:

| Layer | What it stops |
|---|---|
| `deny` rules | `npm install -g`, `npm i -g`, `npm install --global`, `pnpm add -g`, `uv pip install --system`, and every `pip install` form |
| `PIP_REQUIRE_VIRTUALENV=true` | pip that another tool calls internally exits with `Could not find an activated virtualenv (required).` when no virtual environment is active |
| The sandbox | Writes outside the project. On macOS it refused writes to the npm global prefix, `~/.local` (pip `--user`, uv tools), pyenv's `site-packages`, and `/opt/homebrew` |

uv already works this way on its own: `uv add`, `uv sync`, and `uv run` use
the project's `.venv`, and `uv pip install` stops when there is no virtual
environment unless given `--system`. For a one-off run, `uvx <tool>`,
`uv run --with <package>`, and scripts that declare their dependencies inline
(`uv run script.py`) each get a temporary environment that leaves nothing
behind.

A CLI tool sometimes does belong on the machine. `uv tool install`, `pipx`,
and `brew` stay available but ask first, and their writes outside the
project mean they run only once a person approves the retry outside the
sandbox.

The `deny` rules match command text, so a flag in another position
(`npm install some-tool -g`) is not matched; the sandbox still refuses the
write. None of this applies to commands people type in their own terminals.
To keep pip out of global interpreters there too, each developer can run
`pip config set global.require-virtualenv true` (or add
`export PIP_REQUIRE_VIRTUALENV=true` to their shell profile); an interpreter
marked as externally managed under PEP 668, such as Homebrew's Python, already
refuses, while pyenv's interpreters do not.

## Tools that run outside the sandbox

On macOS, `gh` and `terraform` fail TLS verification inside the sandbox, and
git cannot tunnel SSH through the sandbox proxy. Making them work inside it
would mean letting every sandboxed command — install scripts included — read
the GitHub token, SSH keys, and cloud credentials they need. Instead,
`sandbox.excludedCommands` takes exactly these commands out:

| Excluded | Always asks first |
|---|---|
| `gh *` | `gh pr merge`, `gh repo delete`, `gh release create`, `gh api` |
| `terraform *` | `terraform apply`, `terraform destroy`, `terraform import` |
| `git fetch`, `git pull`, `git push`, `git clone`, `git ls-remote` | `git push` |

An excluded command runs with your normal access: your SSH keys and agent,
`gh`'s stored login, your cloud credentials, and any host. It still goes
through the permission check (a prompt in default mode, the classifier in
auto mode), and the operations in the right-hand column always prompt.
Package installers are never excluded, so their scripts stay sandboxed.

Matching is on the command text, and every part of a compound command must
match. `git -C dir fetch`, `cd dir && git pull`, `env gh …`, or a pipe after
the command stays inside the sandbox and fails — for example
`git -C . ls-remote origin` cannot reach the SSH remote, and `env gh repo view`
cannot read `gh`'s configuration — so run these commands on their own.

`terraform init` downloads providers and later runs them outside the
sandbox with your cloud credentials. The 7-day rule does not cover them:
commit `.terraform.lock.hcl` and review provider version changes in PRs.

## Exceptions (an urgent fix released less than 7 days ago)

Exceptions are a person's decision, made visibly:

- **npm**: run `npm install <package>@<version> --min-release-age=0` yourself.
- **pnpm**: add the package to `minimumReleaseAgeExclude` in
  `pnpm-workspace.yaml` and review it in a PR.
- **uv**: add `some-package = false` under `[exclude-newer-package]` and review
  it in a PR.

If Claude proposes any of these, the `ask` rule shows you the exact command
first.

## Moving Python projects to uv

| Before | With uv |
|---|---|
| `python -m venv .venv && pip install -r requirements.txt` | `uv venv && uv pip install -r requirements.txt`, or adopt a lockfile: `uv init --bare && uv add -r requirements.txt` |
| `pip install <package>` | `uv add <package>` (project) or `uv pip install <package>` (environment) |
| `pipx install <tool>` | `uv tool install <tool>` |

`uv sync --locked` installs exactly what `uv.lock` records, including hashes.

## Known limits

- **Rules match command text.** `deny` and `ask` cover the forms Claude
  normally writes, not `/usr/bin/pip`, `sh -c '…'`, or `python3.12 -m pip`.
  The sandbox is the boundary that does not depend on wording.
- **The sandbox is not a complete boundary.** A malicious install script can
  still write into the project (for example `node_modules/`, `.venv/`), which
  later runs outside the sandbox. In auto mode, a command that names a host
  outside the allowlist goes to the auto-mode classifier, which may allow it.
- **Sandbox side effects**, observed on macOS:
  - npm and uv need their caches (`~/.npm/_cacache`, `~/.cache/uv`) writable,
    which the bundle allows. If npm reports root-owned cache files and
    suggests `sudo chown`, that is the sandbox, not ownership — do not run it.
  - pnpm cannot use its home store from the sandbox and creates
    `.pnpm-store/` at the project root instead; keep it in `.gitignore`. It
    also prints `failed to copy trust settings of system certificate`, which
    is harmless.
  - pip's macOS trust-store lookup fails in the sandbox, so `env` sets
    `PIP_USE_DEPRECATED=legacy-certs` for tools that still call pip. Behind a
    TLS-inspecting proxy, also set `PIP_CERT` to your CA bundle.
  - `docker` does not work in the sandbox. If Claude needs it, add a narrow
    pattern such as `docker compose *` to `sandbox.excludedCommands` in the
    repository.
- **`.env.example` is unreadable too**, because `Read(**/.env.*)` covers it.
- **Platforms**: Linux and WSL2 need `bubblewrap` and `socat`. Native Windows
  has no sandbox, and `failIfUnavailable` then stops Claude Code from
  starting — use WSL2.
- **Private registries**: add the host to `sandbox.network.allowedDomains`.
  The bundle removes `NPM_TOKEN` and similar tokens from sandboxed commands;
  to let a tool authenticate without exposing the token, use a `mask` entry,
  which Claude Code honors only from user or managed settings.

## Check that it is in force

Restart Claude Code in the repository, run `/status`, and confirm the
`Setting sources` line lists the project (or managed) settings. Then:

```bash
npm --version
pnpm --version
uv --version
npm config get min-release-age
```

The versions must meet the table above, and the last command must print `7`
with no `Unknown` warning. Asking Claude to run `ls ~/.ssh` should fail with
`Operation not permitted`, asking it to run `pip install requests` or
`npm install -g some-tool` should be refused by the permission rules, and
`git ls-remote origin` and `gh auth status` should still work.
