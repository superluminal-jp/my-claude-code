#!/usr/bin/env bash
# Shared pre-edit guardrail (Q9/Q10). Tool-agnostic: reads
# {"tool_name": "...", "path": "...", "project_dir": "..."} on stdin, writes
# {"decision": "allow"|"deny", "reason": "..."} on stdout. Exit 0 regardless
# of decision; non-zero only on a real script error (caller must treat that
# as "deny", per contracts/guardrail-script-io.md).
#
# Extracted from .claude/hooks/pre-edit.sh — logic kept verbatim so both the
# refactored Claude Code hook and the Codex CLI adapter produce identical
# outcomes to what pre-edit.sh already produced for these two checks (FR-018).
# The CI/settings/production-path warnings (Q1) are NOT part of this script's
# contract — they're prose-only in AGENTS.md and stay in the Claude Code
# wrapper unchanged.

set -euo pipefail

emit() {
  local decision="$1" reason="$2"
  jq -n --arg decision "$decision" --arg reason "$reason" '{decision:$decision, reason:$reason}'
}

HOOK_INPUT="$(cat 2>/dev/null || true)"
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")
FILE_PATH=$(echo "$HOOK_INPUT" | jq -r '.path // empty' 2>/dev/null || echo "")
PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.project_dir // empty' 2>/dev/null || echo "")

# Block direct edits to .git internals
if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -qE '(^|/)\.git/'; then
  emit "deny" "Direct modification of .git/ is not allowed."
  exit 0
fi

# Block edits on main/master (only when project dir is known to avoid false positives)
if [ -n "$PROJECT_DIR" ] && [ -d "$PROJECT_DIR" ]; then
  if (cd "$PROJECT_DIR" && git rev-parse --git-dir >/dev/null 2>&1); then
    CURRENT_BRANCH=$(cd "$PROJECT_DIR" && git branch --show-current 2>/dev/null || echo "")
    if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
      emit "deny" "Cannot ${TOOL_NAME:-edit} on $CURRENT_BRANCH branch. Create a feature branch first: git checkout -b feature/your-feature"
      exit 0
    fi
  fi
fi

emit "allow" ""
