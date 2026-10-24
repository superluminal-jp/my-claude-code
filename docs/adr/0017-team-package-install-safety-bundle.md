---
status: Accepted
date: 2026-10-24
deciders: Taiki Ogihara
---

# 0017. Distribute a team package-install safety bundle

## Context and problem statement

Projects that use Claude Code also run npm, pnpm, pip, uv, and Homebrew.
Each install runs third-party code with the developer's privileges: lifecycle
scripts, build backends, and the packages themselves. The August 2025 Nx
"s1ngularity" compromise showed what that code can do on a developer machine:
the malicious versions, live on npm for about five hours, ran locally
installed AI CLIs, Claude Code among them, with permission-skipping flags to
search for secrets.

This repository holds the maintainer's own user-level configuration, and
ADR-0014 deliberately left the OS sandbox out of it. What was missing is a
configuration the maintainer can hand to *other* developers, with one
requirement fixed by the maintainer: **normally, use the newest version that
has been public for at least 7 days.**

## Decision drivers

- One file usable both as a repository's `.claude/settings.json` and as a
  managed-settings drop-in, so moving from "default" to "enforced" needs no
  rewrite.
- The 7-day rule must hold for people and CI, not only for Claude, because a
  lockfile a person updates is what Claude later installs from.
- A failure must be visible. A rule the installed tool silently ignores is
  worse than a loud error.
- The sandbox must stay usable for installs. If it is not, every install
  retries outside it, people approve by reflex, and the sandbox protects
  nothing.

## Considered options

Distribution:

- A Claude Code plugin — rejected: a plugin's `settings` take effect only for
  `agent` and `subagentStatusLine`, so it cannot set `sandbox`, `permissions`,
  or `env`.
- Repository settings only; managed settings only.
- **One file that works as either.** (chosen)

Scope of the 7-day rule: Claude's `env` only, or **`env` plus per-repository
package-manager templates.** (chosen)

Install scripts: stop none, stop all (including pip wheels-only and uv
`no-build`), or **stop npm's dependency scripts only** (chosen; pnpm 10 already
skips them by default, and sdist-only Python packages are common).

Python: allow pip under `ask`, or **standardize on uv and deny `pip install`.**
(chosen)

Global installs: rely on the sandbox's write limit alone, or **also deny the
global forms (`npm install -g`, `npm i -g`, `npm install --global`,
`pnpm add -g`, `uv pip install --system`) and make pip require a virtual
environment, keeping `uv tool install` and `pipx` under `ask`** for CLI tools
that belong on the machine. (chosen)

`gh`, Terraform, and git over SSH, which the sandbox breaks on macOS: run them
inside the sandbox — `enableWeakerNetworkIsolation` for TLS, GitHub and
HashiCorp hosts allowed, and the GitHub token readable by every sandboxed
command, with git switched to HTTPS because the macOS proxy cannot carry SSH
— or **take exactly those commands out with `excludedCommands` and make their
remote-changing operations ask.** (chosen)

Location: elsewhere, or **this repository, under `team/package-safety/`,
outside the paths `install.sh` syncs.** (chosen)

## Decision outcome

We will ship `team/package-safety/` with `claude-settings.json` and three
repository templates (`.npmrc`, `pnpm-workspace.yaml`, `uv.toml`). The
maintainer chose each option above explicitly. The settings file contains:

- **`sandbox`** enabled with `failIfUnavailable`, network limited to
  `registry.npmjs.org`, `pypi.org`, and `files.pythonhosted.org`, and the
  common token variables removed from sandboxed commands (`deny` entries
  only, because `mask` is ignored from repository settings).
- **`sandbox.excludedCommands`** for `gh`, `terraform`, and git's network
  commands (`fetch`, `pull`, `push`, `clone`, `ls-remote`), which then run
  with the developer's normal credentials. No package manager is excluded.
- **`permissions.ask`** for every command that picks a new package, runs one
  ad hoc, or changes the machine (`npm install`, `npx`, `pnpm add`, `uv add`,
  `uvx`, `brew install`, …), for the excluded commands' remote-changing
  operations (`git push`, `terraform apply`/`destroy`/`import`,
  `gh pr merge`, `gh repo delete`, `gh release create`, `gh api`), and for
  `dangerouslyDisableSandbox` retries.
- **`permissions.deny`** for pip's install forms and the global install forms
  above, and `Read` rules for home credential files and `.env` files, which
  the sandbox also applies to every sandboxed command.
- **`env`** with the 7-day rule for npm and pnpm 11, npm's `ignore-scripts`,
  pip's certifi fallback, and `PIP_REQUIRE_VIRTUALENV=true`.

Several choices rest on behaviour observed while building the bundle (macOS,
Claude Code 2.1.289, npm 11.6.2, pnpm 10.28.0, uv 0.7.5, pip 26.0.1), and
are recorded here because none is obvious from the file:

- **uv's rule is only in the template, not in `env`.** With
  `UV_EXCLUDE_NEWER` set, `uv lock --check` failed on a lock created without
  it, so the variable would break `uv sync --locked` in every repository that
  lacks the same cutoff.
- **No `npm_config_minimum_release_age` for pnpm 10.** pnpm 10 reads that
  variable (a probe resolved `@aws-sdk/types` to 3.974.6, the newest version
  at least 7 days old, instead of 3.975.0), but npm then prints an
  `Unknown env config` warning on every command. The `pnpm_config_` form
  covers pnpm 11, and the template covers pnpm 10.16 and later.
- **No `PIP_UPLOADED_PRIOR_TO`.** pip 26.0.1 rejects `P7D` with
  `Invalid isoformat` (relative durations arrived in pip 26.1). With pip
  denied to Claude, the variable would only break the pip that other tools
  call internally.
- **Two cache paths are writable: `~/.npm/_cacache` and `~/.cache/uv`.**
  Without them `npm ci` exited with EPERM (and a misleading `sudo chown`
  suggestion) and `uv lock` failed. pip disabled its cache and carried on, so
  its cache stays read-only. pnpm ignored a writable home store (its store
  detection writes directly under `$HOME`) and created `.pnpm-store/` at the
  project root, so the README tells teams to gitignore it rather than widening
  the sandbox further. `~/.npm/_npx` stays read-only because npx executes what
  it caches there.
- **`PIP_USE_DEPRECATED=legacy-certs`.** pip's default macOS trust-store
  lookup failed inside the sandbox (`SSLCertVerificationError`,
  `OSStatus -26276`); with certifi it downloaded normally.
- **No `!` carve-outs in `deny`.** The sandbox configuration listed
  `Read(!.env.example)` verbatim among its deny paths, and `.env.example` stayed
  unreadable. The test could not separate that from the maintainer's own
  user-level `Read(**/.env.*)`, so an exemption could not be shown and the
  carve-outs were dropped; `.env.example` is unreadable by design.
- **Exclusion, not weaker isolation, for `gh` and git over SSH.** With the
  file applied, `git ls-remote origin` and `git fetch --dry-run origin`
  reached the SSH remote and `gh repo view` succeeded, while the same calls in
  forms that stay sandboxed failed: `git -C . ls-remote origin` could not
  reach the remote, and `env gh repo view` could not read
  `~/.config/gh/config.yml`. The second pair is the property the bundle
  exists for — a sandboxed process cannot use those credentials — and running
  the tools inside the sandbox would have given it up for every sandboxed
  command.
- **Global installs are stopped three ways.** With the file applied,
  `npm install -g --dry-run`, `npm i -g`, `npm install --global`,
  `pnpm add -g`, and `uv pip install --system` were all refused by `deny`
  ahead of the broader `ask` rules they also match; outside a virtual
  environment, pip with `PIP_REQUIRE_VIRTUALENV=true` exited with
  `Could not find an activated virtualenv (required).`; and sandboxed writes
  to the npm global prefix, `~/.local`, pyenv's `site-packages`, and
  `/opt/homebrew` were refused. The interpreter alone is not enough: pyenv's
  Python carries no PEP 668 `EXTERNALLY-MANAGED` marker, while Homebrew's
  does.

### Consequences

- Positive: within one repository, people, CI, and Claude resolve the same
  versions, because the cutoff is committed with the code and, for uv,
  recorded in `uv.lock`.
- Positive: Claude cannot add a dependency, run a downloaded package, or make a
  machine-wide install without a person seeing the exact command first.
- Positive: a malicious install script that runs inside the sandbox cannot read
  `~/.ssh`, `~/.aws`, `~/.npmrc`, or `.env` files, and cannot reach hosts
  beyond the registries without approval.
- Positive: Claude can still use `gh`, Terraform, and SSH remotes, and pushes,
  applies, destroys, and GitHub writes always reach a person first.
- Positive: packages Claude installs stay in the project's `node_modules/` or
  `.venv/`, so they cannot change another project or a shared interpreter.
- Negative: a CLI tool that belongs on the machine needs `uv tool install`,
  `pipx`, or `brew` with a person's approval, and a global flag placed after
  the package name is caught only by the sandbox, not by `deny`. People's own
  terminals are unaffected unless each developer sets pip's
  `require-virtualenv`.
- Negative: an excluded command runs with full access and can reach any host;
  only the permission check stands between it and the developer's
  credentials. Terraform providers downloaded by `terraform init` run that
  way too, outside the 7-day rule.
- Negative: exclusion matches command text, so `git -C …`, `cd … &&`, `env`,
  or a trailing pipe keeps the command sandboxed, where it fails.
- Negative: in repository mode a member can switch the sandbox off for
  themselves; only managed settings make it binding.
- Negative: older tools behave differently and must be upgraded: npm before
  11.10 ignores the rule with a warning, and uv before 0.9.17 refuses to parse
  the template.
- Negative: rules match command text, so `/usr/bin/pip` or `sh -c` forms are
  not covered, and code the sandbox lets write into the project can run
  unsandboxed later.
- Negative: Homebrew has no equivalent setting; its 7-day check is the
  approver's judgement.
- Negative: native Windows cannot start Claude Code with this file, because
  `failIfUnavailable` meets a platform with no sandbox.

## Confirmation

`tests/run-package-safety-bundle.sh` (run in CI) checks the invariants
statically: the same 7-day rule in every tool's unit, no `UV_EXCLUDE_NEWER`
or `PIP_UPLOADED_PRIOR_TO`, `PIP_REQUIRE_VIRTUALENV`, the `ask` and `deny`
coverage with tool installers kept under `ask`, portable `Read`
anchors without carve-outs, exactly the two cache paths writable, exactly the
seven excluded commands, and no key that loosens the sandbox further or only
applies from user or managed settings.

The behaviour above was checked in a live session with the file applied, as
listed. Not yet observed, and to be checked by the README procedure on a
machine with current tools: the 7-day rule under npm 11.10+, pnpm 11, and
uv 0.9.17+; removal of token variables (none were set during the check); a
live `ask` prompt; `terraform` (not installed on the test machine); and Linux
or WSL2.

## More information

- `team/package-safety/README.md` — how to apply, versions, exceptions, limits.
- `docs/adr/0014-restore-credential-deny-rules.md` — the user-level decision
  that left the sandbox out of this repository's own settings; unchanged.
- Claude Code docs: [Sandboxing](https://code.claude.com/docs/en/sandboxing),
  [Configure permissions](https://code.claude.com/docs/en/permissions),
  [Settings files and precedence](https://code.claude.com/docs/en/settings),
  [Deploy managed settings](https://code.claude.com/docs/en/managed-settings),
  [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference).
- Package managers: [npm config](https://docs.npmjs.com/cli/v11/using-npm/config),
  [pnpm settings](https://pnpm.io/settings),
  [uv settings](https://docs.astral.sh/uv/reference/settings/),
  [pip install](https://pip.pypa.io/en/stable/cli/pip_install/),
  [pip changelog](https://pip.pypa.io/en/stable/news/) (26.1: relative
  `--uploaded-prior-to`), uv changelog 0.9.17 (relative `exclude-newer`).
- npm 11.10 as the release that added `min-release-age` is from third-party
  write-ups, e.g. [Classmethod](https://dev.classmethod.jp/articles/npm-v11-min-release-age/);
  the official changelog was not checked.
- Nx s1ngularity: [Snyk](https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/),
  [Wiz](https://www.wiz.io/blog/s1ngularity-supply-chain-attack).
