# Research: Remove the codex-plugin-cc Claude Code Plugin

## R1 — Exact edit location in `install.sh` (verified by direct read)

Current (lines 119-133):
```bash
upsert_user_mcp microsoft-learn \
  --transport http \
  https://learn.microsoft.com/api/mcp

# 4. Install codex-plugin-cc (Codex review/rescue from Claude Code)
if ! claude plugin marketplace list 2>/dev/null | grep -q "openai-codex"; then
  claude plugin marketplace add openai/codex-plugin-cc
else
  claude plugin marketplace update openai-codex >/dev/null 2>&1 || true
fi
if ! claude plugin list 2>/dev/null | grep -q "codex@openai-codex"; then
  claude plugin install codex@openai-codex
fi

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
```

New:
```bash
upsert_user_mcp microsoft-learn \
  --transport http \
  https://learn.microsoft.com/api/mcp

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
```

**Decision**: Delete lines 123-132 (the `# 4.` comment, both `if` blocks, and the
blank line that separated them from the closing `echo`) outright — no
conditional cleanup path is needed, unlike the `scripts/guardrails/` precedent
(R1 in specs/027), because a Claude Code plugin install is not a file the
installer copies into `~/.claude`; it is a `claude plugin` CLI registration
that the `claude` tool itself owns and can be removed independently
(`claude plugin uninstall codex@openai-codex`) if desired. There is nothing
under `$TARGET_DIR` for this installer to clean up on re-run.

## R2 — Step-numbering impact

**Finding**: Steps in `install.sh` are `0` (preflight), `1` (sync managed
paths), `1a` (scripts/guardrails cleanup), `2` (chmod), `3` (MCP upsert), `4`
(codex plugin — deleted by this feature). Step `4` is the **last** step, so
deleting it leaves `0, 1, 1a, 2, 3` — already contiguous with no gap. No
renumbering is required elsewhere in the file.

**Decision**: No comment renumbering needed. FR-003 ("no numbering gap") is
satisfied by the deletion itself, not by an additional edit.

## R3 — Comment clarity pass (user request: "わかりやすいように整理してコメントを改善")

Reviewed every comment in `install.sh` for accuracy against the code it sits
above, per the coder skill's "comments describe why, stay accurate" rule.
Findings:

- Lines 1-14 (file header): accurate and current — describes sync + MCP
  upsert scope, explicitly disclaims Codex CLI config. No change needed; it
  already doesn't mention the plugin being removed (that section had its own
  inline `# 4.` comment instead).
- Step `0` (line 47) through step `3` (line 91): each comment accurately
  describes the code immediately following it. No drift found.
- Step `1a` (lines 81-85): still accurate post-specs/027 — describes an
  uninstall-path cleanup, unaffected by this feature.

**Decision**: Scope the "improve comments" request to the one comment that is
actually going away (`# 4. Install codex-plugin-cc ...`) rather than rewriting
unrelated, already-accurate comments — consistent with the coder skill's "no
drive-by refactors outside the agreed task" rule. The single clarity
improvement this feature makes is structural: removing the deleted step's
comment eliminates the one comment in the file that described a
now-nonexistent action, so the remaining sequence (`0` → `1` → `1a` → `2` →
`3`) reads as a complete, gap-free, accurate story on its own.

**Alternatives considered**: Rewriting all step comments file-wide for style
consistency — rejected as unrequested scope creep on an already-accurate file;
the user's clarity request is satisfied by removing the one comment that would
otherwise dangle.

## R4 — `tests/run-install.sh` stub cleanup

Current (lines 40-50):
```bash
cat >"$STUB_BIN/claude" <<'STUB'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$CLAUDE_LOG"

if [ "${1:-}" = "plugin" ] && [ "${2:-}" = "marketplace" ] && [ "${3:-}" = "list" ]; then
  printf '%s\n' 'openai-codex'
elif [ "${1:-}" = "plugin" ] && [ "${2:-}" = "list" ]; then
  printf '%s\n' 'codex@openai-codex'
fi
STUB
```

**Finding**: These two `if`/`elif` branches exist solely to make
`install.sh`'s (now-deleted) plugin marketplace/list checks return
deterministic output. Nothing else in the test file or in `install.sh`
depends on the `claude` stub returning plugin data. No assertion in
`tests/run-install.sh` currently checks plugin-related output either
(confirmed by reading the full file — no `plugin` string appears outside
this stub definition).

**Decision**: Delete both branches, collapsing the stub body to just the
`CLAUDE_LOG` append line:
```bash
cat >"$STUB_BIN/claude" <<'STUB'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$CLAUDE_LOG"
STUB
```

## R5 — No ADR, README, or MCP-catalog change needed

**Finding** (confirmed by repository-wide search, see spec.md Edge Cases):
`codex-plugin-cc` / `openai-codex` / `codex@openai-codex` appear nowhere in
`README.md`, `README.ja.md`, `.claude/rules/*.md`, or `docs/adr/*.md` — only
in `install.sh` and `tests/run-install.sh`. No ADR documents this plugin's
original adoption (ADR-0004 "adopt official codex import" covers the
unrelated Codex CLI `/import` migration, not this Claude Code marketplace
plugin).

**Decision**: This feature touches exactly two files. No documentation sync
obligation exists beyond those two files (Live Documentation Rules § "Out of
Scope": pure internal changes with no public contract shift — the installer's
only public contract is "what state does `install.sh` produce," which is
verified by `tests/run-install.sh`, not prose documentation).

## R6 — No `data-model.md` entities

**Decision**: This feature has no persistent data entities — it deletes shell
logic and a test stub. `data-model.md` states this explicitly rather than
being fabricated, consistent with specs/024-027 precedent for infrastructure-
only features.

## R7 — No `contracts/` artifact

**Decision**: `install.sh` has no external interface beyond the CLI commands
it issues to `claude`/`uvx`, already exercised end-to-end by
`tests/run-install.sh`'s command-log assertions. Same rationale as
specs/024-027.
