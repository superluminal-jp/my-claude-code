#!/usr/bin/env bash
# UserPromptSubmit: nudge toward adopting Spec Kit per-project.
#
# Non-blocking (always exit 0). When the submitted prompt reads like
# non-trivial feature/implementation work AND the current project has not
# opted into Spec Kit (no .specify/ under $CWD), emits additionalContext
# suggesting Claude recommend `specify init` to the user (see README.md
# "Opt-in to spec-kit"). Silent otherwise — this never blocks or rewrites
# the prompt, only adds context for Claude to act on.
#
# Heuristic (deliberately simple and testable, mirrors the character-count
# style threshold already used for the clarifier trigger in skill-routing.md):
#   - trimmed prompt length > 40 chars (skip one-liners / trivial asks)
#   - prompt does not already mention Spec Kit / specify (avoid nagging when
#     the user is already on-topic)
#   - prompt matches an implementation-intent keyword (English or Japanese)
# Throttled to once per SPECKIT_RECOMMEND_INTERVAL_SECONDS (default 7 days)
# per project directory, tracked in a temp cache file — never written inside
# the project itself.

set -uo pipefail

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty' 2>/dev/null || echo "")
CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")

[ -z "$PROMPT" ] && exit 0
[ -z "$CWD" ] && exit 0

# Already opted in — nothing to recommend.
[ -d "$CWD/.specify" ] && exit 0

TRIMMED=$(echo "$PROMPT" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
[ "${#TRIMMED}" -le 40 ] && exit 0

# Already on-topic about Spec Kit — don't nag.
if echo "$PROMPT" | grep -qiE 'speckit|spec-kit|spec kit|specify init|specify\.io'; then
  exit 0
fi

IMPL_INTENT_RE='implement|implementation|add (a |the )?feature|new feature|build (a|the|an)|create (a|an) (api|endpoint|service|feature|app|application)|refactor|redesign|migrate|migration|architecture|design (a|the|and build)|develop|feature request|実装|新機能|機能追加|機能を追加|設計して|開発して|作って|リファクタ|移行|構築'
if ! echo "$PROMPT" | grep -qiE "$IMPL_INTENT_RE"; then
  exit 0
fi

INTERVAL_SECONDS="${SPECKIT_RECOMMEND_INTERVAL_SECONDS:-604800}"
CACHE_DIR="${TMPDIR:-/tmp}/claude-speckit-recommend"
mkdir -p "$CACHE_DIR" 2>/dev/null || exit 0
STATE_FILE="$CACHE_DIR/${CWD//\//_}"

now_epoch=$(date +%s)
last_shown=0
if [ -f "$STATE_FILE" ]; then
  last_shown=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
fi
elapsed=$((now_epoch - last_shown))
if [ "$elapsed" -lt "$INTERVAL_SECONDS" ]; then
  exit 0
fi

printf '%s\n' "$now_epoch" >"$STATE_FILE"

MSG='This request looks like non-trivial feature/implementation work in a project that has not adopted Spec Kit (no .specify/ here). Consider suggesting the user run `specify init` to get spec-driven development (constitution, spec, plan, tasks) for this project — see README.md "Opt-in to spec-kit". Mention it once; do not insist if they decline or ignore it.'

jq -n --arg msg "$MSG" \
  '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $msg}}'
exit 0
