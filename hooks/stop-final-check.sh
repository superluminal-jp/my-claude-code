#!/bin/bash
# Stop final check hook
# Final validation before task completion
# Per Claude Code docs: when stop_hook_active is true, skip output to avoid infinite loop.

set -e

# Read stdin (hook input JSON); if stop_hook_active is true, exit immediately to avoid infinite loop
if [ ! -t 0 ]; then
    HOOK_INPUT="$(cat 2>/dev/null || true)"
    if [ -n "$HOOK_INPUT" ] && command -v jq >/dev/null 2>&1; then
        STOP_HOOK_ACTIVE="$(echo "$HOOK_INPUT" | jq -r '.stop_hook_active // empty' 2>/dev/null || true)"
        if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
            exit 0
        fi
    fi
fi

echo ""
echo "═══════════════════════════════════════"
echo "✓ Task Complete - Final Check"
echo "═══════════════════════════════════════"
echo ""

# Check for uncommitted changes
if git status --short 2>/dev/null | grep -q '^'; then
    echo "📝 Uncommitted Changes"
    echo ""
    git status --short 2>/dev/null
    echo ""
    
    # Categorize changes
    MODIFIED=$(git status --short 2>/dev/null | grep '^ M' | wc -l)
    ADDED=$(git status --short 2>/dev/null | grep '^A' | wc -l)
    DELETED=$(git status --short 2>/dev/null | grep '^ D' | wc -l)
    UNTRACKED=$(git status --short 2>/dev/null | grep '^??' | wc -l)
    
    echo "Summary:"
    [ $MODIFIED -gt 0 ] && echo "  Modified: $MODIFIED files"
    [ $ADDED -gt 0 ] && echo "  Added: $ADDED files"
    [ $DELETED -gt 0 ] && echo "  Deleted: $DELETED files"
    [ $UNTRACKED -gt 0 ] && echo "  Untracked: $UNTRACKED files"
    echo ""
fi

# Pre-commit checklist
echo "📋 Pre-Commit Checklist"
echo ""
echo "Before committing, verify:"
echo ""
echo "  Code Quality:"
echo "    [ ] Code changes tested and working"
echo "    [ ] No syntax errors or warnings"
echo "    [ ] Follows project coding standards"
echo ""
echo "  Documentation:"
echo "    [ ] README.md updated (if needed)"
echo "    [ ] CHANGELOG.md entry added"
echo "    [ ] API docs synchronized"
echo "    [ ] Code comments added for complex logic"
echo ""
echo "  Testing:"
echo "    [ ] Unit tests pass"
echo "    [ ] Integration tests pass"
echo "    [ ] New tests added for new functionality"
echo ""
echo "  Review:"
echo "    [ ] Changes reviewed (git diff)"
echo "    [ ] No sensitive data committed"
echo "    [ ] No large files (>1MB) without reason"
echo "    [ ] If spec/requirements changed, .speckit/ artifacts updated"
echo ""
echo "  Quality:"
echo "    [ ] Quality check: quality-checker subagent or /quality-check"
echo ""

# Suggest validation commands
echo "🔧 Validation Commands"
echo ""
echo "  Run pre-commit validation:"
echo "    .claude/hooks/pre-commit-validate.sh"
echo ""
echo "  Quality and spec:"
echo "    /quality-check    # or invoke quality-checker subagent"
echo "    /speckit.analyze  # spec–plan–implementation consistency"
echo ""
echo "  Review changes:"
echo "    git diff"
echo "    git diff --cached (for staged changes)"
echo ""
echo "  Test (adjust for your project):"
echo "    npm test        # JavaScript/TypeScript"
echo "    pytest          # Python"
echo "    cargo test      # Rust"
echo "    go test ./...   # Go"
echo ""

# Commit reminder
if git status --short 2>/dev/null | grep -q '^'; then
    echo "✅ Ready to Commit?"
    echo ""
    echo "  git add ."
    echo "  git commit -m 'type: description'"
    echo ""
    echo "  Commit types:"
    echo "    feat:     New feature"
    echo "    fix:      Bug fix"
    echo "    docs:     Documentation only"
    echo "    style:    Formatting, missing semicolons, etc"
    echo "    refactor: Code change that neither fixes nor adds feature"
    echo "    test:     Adding tests"
    echo "    chore:    Updating build tasks, package manager configs, etc"
    echo ""
fi

echo "═══════════════════════════════════════"
echo "✓ All checks complete"
echo "═══════════════════════════════════════"
echo ""

exit 0
