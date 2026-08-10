# Contract: Removal manifest and reference integrity

**Feature**: 021-codex-official-import | **Date**: 2026-08-10

The authoritative list of what is deleted and the mechanical rules that must hold afterwards. `tests/run-codex-references.sh` implements the RULE-* checks; `tasks.md` implements the deletion set.

## Deletion set

Exactly these paths are removed. Anything not listed here stays.

```
.agents/skills/adr
.agents/skills/clarifier
.agents/skills/coder
.agents/skills/digital-agency-frontend
.agents/skills/minto-builder
.agents/skills/minto-reviewer
.agents/skills/minto-rewriter
.agents/skills/scrum-master
.codex/AGENTS.md                        # content relocated to root AGENTS.md first
.codex/README.md
.codex/hooks/destructive-command-adapter.sh
.codex/hooks/pre-edit-adapter.sh
.codex/hooks/post-edit-adapter.sh
.codex/hooks/prompt-secret-adapter.sh
.codex/rules/guardrails.rules
.codex/prompts/verify-config.md
tests/run-codex-sync.sh
tests/run-codex-sync-drift.sh
```

Result: `.agents/` and `.codex/` contain no tracked files.

## Explicitly NOT deleted

| Path | Why it stays |
|---|---|
| `scripts/guardrails/*.sh` | Claude's hooks call them; independent of Codex (NFR-003) |
| `.claude/**` | NFR-002, reaffirmed 2026-08-10 |
| `tests/run-{pre-edit,destructive-command,post-edit-format,prompt-secret}-guard.sh` | Cover the Claude-side guardrails, which are unchanged |
| `specs/012-*`, `specs/013-*`, `specs/014-*`, `docs/adr/000{1,2,3}-*` | Historical records; immutable (NFR-001) |
| `.specify/**` | Unrelated to the Codex port |

## Installer contract

`install.sh` after the change:

- **MUST NOT** reference `.codex/`, `.agents/`, `~/.codex`, or `~/.agents`.
- **MUST NOT** write, or leave behind, the `# >>> my-claude-code managed hooks` and `# >>> my-claude-code managed MCP servers` marker blocks.
- **MUST** preserve its Claude-side behaviour unchanged: `~/.claude` sync and Claude user-scope MCP registration.
- **SHOULD** state in its header comment that Codex configuration is now produced by the developer via the documented procedure.

**Migration note for existing installs**: users who ran the old `install.sh` already have `~/.codex/hooks/`, `~/.codex/rules/guardrails.rules`, `~/.codex/prompts/`, `~/.agents/skills/` and two marker blocks in `~/.codex/config.toml`. The new installer does not remove them — it does not touch user-owned Codex configuration at all. `contracts/codex-setup-procedure.md` § Cleanup tells the developer how to remove them by hand if they want to.

## Reference-integrity rules

Enforced by `tests/run-codex-references.sh`. Each rule is a pass/fail check with a named id.

| Id | Rule | Scope searched |
|---|---|---|
| `RULE-01` | No file references any path in the deletion set, **except `.agents/skills/<name>`** | `README.md`, `README.ja.md`, `AGENTS.md`, `CLAUDE.md`, `install.sh`, `.gitignore`, `scripts/**`, `tests/**`, `.claude/**` |
| `RULE-02` | No `SYNC-\d\d` token survives | `tests/**`, `README*.md`, `AGENTS.md` |
| `RULE-03` | Root `AGENTS.md` is a regular file, not a symlink | `AGENTS.md` |
| `RULE-04` | Root `AGENTS.md` is > 1 KiB and ≤ 32 KiB | `AGENTS.md` |
| `RULE-05` | Root `AGENTS.md` contains no line beginning with `@` (Codex does not expand imports) | `AGENTS.md` |
| `RULE-06` | `.gitignore` ignores both `.codex/` and `.agents/` | `.gitignore` |
| `RULE-07` | Host allowlist: every URL whose host or path contains `codex` resolves to `developers.openai.com`, `learn.chatgpt.com`, or `github.com/openai/` — any other host fails | whole repo except `.git/` |
| `RULE-08` | Every documentation URL in the user-facing docs is `https://` and on an allowlisted host | `README.md`, `README.ja.md`, `AGENTS.md` |
| `RULE-09` | `.claude/settings.json` still registers all five hooks and retains `permissions.deny` | `.claude/settings.json` |
| `RULE-10` | `install.sh` contains no Codex/agents reference **on an executable line** (comment lines are exempt — the header states the installer does *not* touch `~/.codex`, and saying so must not trip the check proving it) | `install.sh` |

**Exclusions**: `specs/**` and `docs/adr/**` are exempt from RULE-01 and RULE-02 — they are historical records and must keep naming what existed. **RULE-07 has no exclusions**: the host allowlist applies to the whole repository, historical documents included.

**RULE-01's `.agents/skills/<name>` carve-out** (added during implementation, 2026-08-10): those paths are deleted *as tracked symlinks* but immediately reappear *as generated skills* once a developer runs `/import`. `AGENTS.md`'s skill-routing section must keep pointing at them, because that is where Codex genuinely finds the skills. Only `.codex/**` paths and the two codex-sync suites are true dangling references.

**Failure output**: each violation prints `FAIL <RULE-id> <path>:<line> <matched text>`; the suite exits non-zero if any rule fails. This matches the existing `tests/run-*.sh` convention (named check ids, green/red output, non-zero exit).

## Acceptance

The manifest is satisfied when:

1. Every path in the deletion set is absent from the working tree and from `git ls-files`.
2. `tests/run-codex-references.sh` exits 0.
3. Every other `tests/run-*.sh` exits 0 (SC-003).
4. `git diff --stat` shows no change under `.claude/` or `scripts/guardrails/`.
