# Research: Remove scripts/ Entirely

## R1 — Exact edit locations (verified by direct reads)

### `install.sh` (lines ~82-96)
Current: a comment block + `if [ -d "$GUARDRAILS_SRC" ]; then ... fi` that syncs `scripts/guardrails/` → `~/.claude/scripts/guardrails/`, silently no-op if the source is absent.
New: unconditional `rm -rf "$TARGET_DIR/scripts/guardrails"` with a comment explaining it's now the uninstall path (mirrors `sync_path "hooks"` from specs/025). No re-copy, since the source no longer exists.

### `README.md`
1. "What this provides" bullet for `scripts/check-mcp-consistency.sh` (lines 46-48) → remove entirely.
2. "What this provides" bullet for `scripts/guardrails/` (lines 52-60) → remove entirely.
3. File-structure tree: remove the `scripts/` subtree (both `check-mcp-consistency.sh` and `guardrails/` lines) and the top comment mentioning "Copy .claude/ to ~/.claude/ + Codex CLI artifacts + register MCP servers" for `install.sh` stays (unrelated to scripts/).
4. Verification section: remove `./scripts/check-mcp-consistency.sh` and `./tests/run-prompt-secret-guard.sh` lines from the command block (the latter is one of the four deleted test suites — confirmed via grep it's the only one of the four still listed there).
5. Codex-comparison section, two sentences (already identified in the driving conversation):
   - "`scripts/guardrails/*.sh` still contains the guardrail matching logic for reference, but nothing calls it and nothing shares logic with it" → rewrite: the scripts no longer exist at all.
   - "`scripts/guardrails/*.sh` remains the shared decision logic that Codex's two working guards call." (a few lines below, in the "Setting up skills, MCP servers and hooks" or nearby section) → rewrite: no longer exists; Codex's own imported copies (if any) are self-contained.

### `README.ja.md`
Mirrored: skill-list bullets (there is no separate check-mcp-consistency bullet in the ja skill list, only in the file-structure tree and Verification section, confirmed by earlier grep — README.ja.md's "What this provides" list doesn't enumerate scripts/ items the way README.md's does), file-structure tree (`scripts/` subtree), Verification section (drop `./scripts/check-mcp-consistency.sh` and `./tests/run-prompt-secret-guard.sh`), and the closing Codex-comparison paragraph already located in the driving conversation.

### `.claude/rules/permissions.md`
Current: "`scripts/guardrails/*.sh` still contains the pattern-matching logic these rules describe, for reference, though nothing invokes it automatically anymore." (opening paragraph) and "This section is policy only now; nothing in Claude Code enforces it automatically." (Credential Safety section, added by specs/026).
New: remove the `scripts/guardrails/*.sh` reference-pointer clause from the opening paragraph (the scripts no longer exist to point to); the Credential Safety section's "policy only" statement already holds without change.

### `.claude/rules/mcp.md`
Line 3: "...since `scripts/check-mcp-consistency.sh` requires every `.mcp.json` entry to appear here..." → rewrite: the completeness expectation is manual policy now, no script enforces it.

## R2 — install.sh exact replacement

Old (lines ~82-96):
```bash
# 1a. Sync the shared guardrail scripts (repo-root scripts/guardrails/, not
# under .claude/ — they're tool-agnostic decision logic, so they're deployed
# here as a sibling of rules/skills rather than nested under one tool's
# directory). Claude Code no longer calls these automatically (the .claude/hooks/
# wrappers that used to invoke them were removed — see
# specs/025-remove-claude-hooks/); they stay available for direct/manual
# invocation and for the tests/run-*-guard.sh suites that exercise them.
GUARDRAILS_SRC="$SCRIPT_DIR/scripts/guardrails"
GUARDRAILS_DST="$TARGET_DIR/scripts/guardrails"
if [ -d "$GUARDRAILS_SRC" ]; then
  rm -rf "$GUARDRAILS_DST"
  mkdir -p "$GUARDRAILS_DST"
  cp -R "$GUARDRAILS_SRC"/. "$GUARDRAILS_DST/"
  chmod +x "$GUARDRAILS_DST"/*.sh
  echo "Synced shared guardrail scripts -> $GUARDRAILS_DST"
fi
```

New:
```bash
# 1a. scripts/guardrails/ no longer exists in this repository (removed
# entirely, along with its dedicated tests and scripts/check-mcp-consistency.sh
# — see specs/027-remove-scripts/). This step stays as the uninstall path: it
# clears any ~/.claude/scripts/guardrails/ left by an install made before
# that removal, the same pattern used for "hooks" in install.sh above.
rm -rf "$TARGET_DIR/scripts/guardrails"
```

## R3 — No `contracts/` artifact needed

Same rationale as specs/024-026.

## R4 — New ADR numbering

`docs/adr/` has 0001-0004 (pre-existing numbering collision, not this feature's concern), 0005 (Accepted), 0006 (Accepted). Next available: **0007**.
