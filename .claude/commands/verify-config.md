---
description: Verify the .claude/ configuration — JSON, hooks, MCP catalog, and behavior suites
allowed-tools: Bash(jq *), Bash(shellcheck *), Bash(shfmt *), Bash(yamllint *), Bash(scripts/check-mcp-consistency.sh), Bash(bash scripts/check-mcp-consistency.sh), Bash(tests/run-*.sh), Bash(bash tests/run-*.sh)
---

Run the local configuration checks and report a concise pass/fail checklist. Do
not modify any files. Surface the first hard failure with its output.

1. JSON validity: `jq empty .claude/settings.json` and `jq empty .mcp.json`.
2. Import integrity: every `@`-import in `CLAUDE.md` and `.claude/CLAUDE.md`
   resolves to an existing file (paths are relative to the repo root).
3. Hooks: `shellcheck .claude/hooks/*.sh`, then `shfmt -d -i 2 .claude/hooks/*.sh`
   (report diffs only — never write).
4. MCP catalog consistency: `bash scripts/check-mcp-consistency.sh`.
5. Behavior suites (require the `claude` CLI and the network; if `claude` is
   absent, skip with a note rather than failing): `bash tests/run-skill-routing.sh`
   and `bash tests/run-live-documentation.sh`.

Report each step as `✓`/`✗` with a one-line reason. End with the overall verdict.
