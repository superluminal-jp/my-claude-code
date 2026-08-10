---
name: verify-config
description: Verify the .claude/ configuration — JSON, hooks, MCP catalog, and behavior suites
allowed-tools: Bash(jq *), Bash(shellcheck *), Bash(shfmt *), Bash(yamllint *), Bash(scripts/check-mcp-consistency.sh), Bash(bash scripts/check-mcp-consistency.sh), Bash(tests/run-*.sh), Bash(bash tests/run-*.sh)
disable-model-invocation: true
context: fork
agent: verification-runner
background: false
---

Run the local configuration checks and report a concise pass/fail checklist. Do
not modify any files. Surface the first hard failure with its output.

1. JSON validity: `jq empty .claude/settings.json` and `jq empty .mcp.json`.
2. Import integrity: every `@`-import in `CLAUDE.md` and `.claude/CLAUDE.md`
   resolves to an existing file (paths are relative to the repo root).
3. Hooks: `shellcheck .claude/hooks/*.sh`, then `shfmt -d -i 2 .claude/hooks/*.sh`
   (report diffs only — never write).
4. MCP catalog consistency and stdio startup: run
   `bash scripts/check-mcp-consistency.sh`, then `bash tests/run-mcp-startup.sh`.
   The startup smoke test requires the network and a writable `uv` cache.
5. Behavior suites (require the `claude` CLI and the network; if `claude` is
   absent, skip with a note rather than failing): `bash tests/run-skill-routing.sh`
   and `bash tests/run-live-documentation.sh`.
6. Hook unit tests (deterministic, no `claude` CLI needed):
   `bash tests/run-speckit-update.sh`.

Report each step as `✓`/`✗` with a one-line reason. End with the overall verdict.

<!--
This procedure runs in a forked context (`context: fork`) on the read-only
`verification-runner` subagent, so the raw lint and suite output never reaches
the calling conversation — only the checklist does. `background: false` keeps
the full tool set and returns the verdict in the invoking turn. The fork sees
none of the caller's conversation, so every path and command above is stated
inline rather than assumed. Rationale: specs/019-verify-fork-test-runner/research.md
-->
