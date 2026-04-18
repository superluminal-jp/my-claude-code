#!/usr/bin/env bash
# PostToolUse hook: remind to sync docs when doc-impacting files change
# Exit 0 = silent pass
# Exit 1 = non-blocking warning (logged; action proceeds)
# Grounded in .claude/rules/development.md "Documentation Sync" triggers.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Relativize against project dir for cleaner matching / messages
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
REL="${FILE_PATH#"$PROJECT_DIR"/}"

# Skip doc files themselves (editing docs is what we want to encourage)
case "$REL" in
  README*|*/README*|docs/*|*/docs/*|CHANGELOG*|*.md)
    exit 0
    ;;
esac

# Collect doc-impacting signals based on file identity
TRIGGERS=()

case "$REL" in
  package.json|*/package.json|pyproject.toml|*/pyproject.toml|requirements*.txt|*/requirements*.txt|Cargo.toml|*/Cargo.toml|go.mod|*/go.mod)
    TRIGGERS+=("dependency manifest changed → update install/prerequisites docs")
    ;;
  .mcp.json|*/.mcp.json|.claude/install-mcp.sh|*/.claude/install-mcp.sh)
    TRIGGERS+=("MCP server catalog changed → update .claude/rules/mcp.md")
    ;;
  .claude/settings.json|*/.claude/settings.json)
    TRIGGERS+=("settings changed → verify .claude/rules/permissions.md reflects enforcement")
    ;;
esac

# Content-based signals (CLI flags, env vars, HTTP routes) — only for source files
case "$REL" in
  *.py|*.ts|*.tsx|*.js|*.jsx|*.go|*.rs|*.sh)
    CONTENT=$(printf '%s' "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty' 2>/dev/null || echo "")
    if [ -n "$CONTENT" ]; then
      if echo "$CONTENT" | grep -qE '(add_argument|ArgumentParser|click\.(option|argument)|commander\.|yargs|flag\.(String|Bool|Int))'; then
        TRIGGERS+=("CLI flag added/changed → update README usage")
      fi
      if echo "$CONTENT" | grep -qE '(os\.environ|process\.env|std::env::var|getenv)'; then
        TRIGGERS+=("env var referenced → verify README/docs configuration section")
      fi
      if echo "$CONTENT" | grep -qE '(@app\.(route|get|post|put|delete|patch)|router\.(get|post|put|delete|patch)|app\.(get|post|put|delete|patch))'; then
        TRIGGERS+=("HTTP route added/changed → update docs/api")
      fi
    fi
    ;;
esac

if [ "${#TRIGGERS[@]}" -eq 0 ]; then
  exit 0
fi

# Only warn when targetable docs actually exist — some projects legitimately have none
HAS_DOCS=0
[ -f "$PROJECT_DIR/README.md" ] && HAS_DOCS=1
[ -d "$PROJECT_DIR/docs" ] && HAS_DOCS=1
[ -d "$PROJECT_DIR/.claude/rules" ] && HAS_DOCS=1

if [ "$HAS_DOCS" -eq 0 ]; then
  exit 0
fi

echo "Doc sync reminder for $REL:" >&2
for t in "${TRIGGERS[@]}"; do
  echo "  - $t" >&2
done
exit 1
