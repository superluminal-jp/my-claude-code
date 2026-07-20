---
status: Proposed
date: 2026-07-20
deciders: repository maintainer
---

# 0002. Deploy Codex configuration at user scope

## Context and problem statement

This repository distributes reusable Claude Code configuration from tracked
sources under `.claude/` to `~/.claude/`. The Codex port needs the same
"author once, apply across projects" property while respecting Codex's native
discovery locations for global guidance, skills, hooks, Rules, prompts, and
MCP servers. Repository-local `.codex/` files alone would apply only in this
checkout, may require project trust, and would not provide a baseline in other
projects.

## Decision drivers

- Apply the shared configuration consistently across projects.
- Use Codex's documented user-scope discovery paths.
- Keep version-controlled sources reviewable without overwriting unrelated
  user-owned Codex configuration.
- Preserve project-specific guidance in the project root rather than leaking
  it into the global baseline.

## Considered options

- Treat repository `.codex/` and `.agents/` as sources and deploy their
  managed artifacts to user scope.
- Use only project-local Codex configuration.
- Maintain independent project-local and user-scope copies manually.

## Decision outcome

We will treat repository `.codex/` and `.agents/` as version-controlled source
material and have `install.sh` deploy managed artifacts to `~/.codex/` and
`~/.agents/`. Shared prose comes from `.codex/AGENTS.md`; the root `AGENTS.md`
contains only guidance specific to this repository. Marker-delimited sections
are used where managed hooks and MCP servers must coexist with user-owned
`config.toml` content, and `default.rules` remains untouched.

### Consequences

- Positive: Codex sessions receive the same baseline in every project after a
  single installation, using native discovery paths.
- Positive: tracked sources, deployed files, and cross-tool catalogs can be
  checked for drift by `tests/run-codex-sync.sh`.
- Negative: changes are not effective globally until `install.sh` is rerun and
  non-managed hooks are reviewed/trusted in Codex.
- Negative: the installer becomes responsible for preserving user-owned
  sections and for converting the MCP catalog from JSON to TOML safely.
- Negative: symlink-based skill discovery targets macOS/Linux environments;
  unsupported Windows symlink setups require a different deployment strategy.

## Confirmation

`tests/run-codex-sync.sh` verifies source/deployment equality, link health,
Rules parity, hook registration, MCP catalog coverage, and absence of plaintext
secret patterns. `tests/run-codex-sync-drift.sh` proves those checks fail for
isolated one-sided changes. Installer tests use a temporary HOME so user-owned
configuration remains untouched.

## More information

- [`specs/014-codex-config-port/spec.md`](../../specs/014-codex-config-port/spec.md)
- [`specs/014-codex-config-port/plan.md`](../../specs/014-codex-config-port/plan.md)
- [`.codex/README.md`](../../.codex/README.md)
