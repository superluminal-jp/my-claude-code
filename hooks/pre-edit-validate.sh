#!/bin/bash
# Pre-edit validation hook
# Runs before any Edit/Write tool use
# Note: Branch check below is also enforced by advanced-pre-tool-use.sh (same matcher); kept here for redundancy.

set -e

# Get current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")

# Block edits on main/master branches
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
    echo '{
        "block": true,
        "message": "❌ Cannot edit on '"$CURRENT_BRANCH"' branch.\n\nCreate a feature branch first:\n  git checkout -b feature/your-feature-name"
    }' >&2
    exit 2
fi

# Check if file is in critical paths that require extra care
FILE_PATH="${CLAUDE_TOOL_INPUT_PATH:-}"
if [ -n "$FILE_PATH" ]; then
    case "$FILE_PATH" in
        package.json|package-lock.json|Cargo.toml|Cargo.lock|go.mod|go.sum)
            echo "⚠️  Warning: Editing dependency file $FILE_PATH"
            echo "   Consider reviewing changes carefully before committing."
            ;;
        .github/workflows/*|.gitlab-ci.yml|.circleci/*)
            echo "⚠️  Warning: Editing CI/CD configuration"
            echo "   Test changes in a separate branch first."
            ;;
        */migrations/*|*/schema.sql)
            echo "⚠️  Warning: Editing database schema/migration"
            echo "   Ensure backward compatibility and rollback plan."
            ;;
    esac
fi

# Success - allow edit
exit 0
