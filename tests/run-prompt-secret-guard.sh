#!/usr/bin/env bash
# Behavior test for prompt-secret detection across the shared scanner, the
# Claude Code wrapper, and the Codex UserPromptSubmit adapter (spec 014 R4).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO_ROOT/scripts/guardrails/prompt-secret-scan.sh"
CLAUDE_HOOK="$REPO_ROOT/.claude/hooks/user-prompt-submit.sh"
CODEX_ADAPTER="$REPO_ROOT/.codex/hooks/prompt-secret-adapter.sh"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: 'jq' is required for this test." >&2
  exit 1
fi

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

shared_result() {
  local prompt="$1"
  [ -x "$SHARED" ] || {
    echo '{"decision":"MISSING","reason":""}'
    return
  }
  jq -n --arg prompt "$prompt" '{prompt:$prompt}' | bash "$SHARED" 2>/dev/null
}

assert_shared() {
  local name="$1" prompt="$2" want="$3"
  local result got
  result=$(shared_result "$prompt")
  got=$(printf '%s' "$result" | jq -r '.decision // "PARSE_ERROR"')
  check "shared: $name" "$([ "$got" = "$want" ] && echo 1 || echo 0)"
}

AWS_KEY='AKIA1234567890ABCDEF'
GITHUB_TOKEN='ghp_123456789012345678901234567890'
GITHUB_PAT='github_pat_1234567890123456789012'
SLACK_TOKEN='xoxb-1234567890-abcdefghij'
PRIVATE_KEY='-----BEGIN PRIVATE KEY-----'
GOOGLE_KEY='AIza12345678901234567890123456789012345'

assert_shared "benign prompt allowed" "Explain how to rotate a credential safely." "allow"
assert_shared "empty prompt allowed" "" "allow"
assert_shared "AWS key denied" "credential $AWS_KEY" "deny"
assert_shared "GitHub token denied" "credential $GITHUB_TOKEN" "deny"
assert_shared "GitHub fine-grained PAT denied" "credential $GITHUB_PAT" "deny"
assert_shared "Slack token denied" "credential $SLACK_TOKEN" "deny"
assert_shared "private-key header denied" "$PRIVATE_KEY" "deny"
assert_shared "Google API key denied" "credential $GOOGLE_KEY" "deny"

shared_secret_result=$(shared_result "credential $GITHUB_TOKEN")
check "shared: reason does not echo secret value" "$(! printf '%s' "$shared_secret_result" | grep -Fq "$GITHUB_TOKEN" && echo 1 || echo 0)"

claude_hook_exit() {
  local prompt="$1"
  jq -n --arg prompt "$prompt" '{prompt:$prompt}' | bash "$CLAUDE_HOOK" >/dev/null 2>&1
  echo $?
}

check "claude hook: secret exits 2 (block)" "$([ "$(claude_hook_exit "credential $GITHUB_TOKEN")" = "2" ] && echo 1 || echo 0)"
check "claude hook: benign prompt exits 0 (allow)" "$([ "$(claude_hook_exit 'safe prompt')" = "0" ] && echo 1 || echo 0)"
check "claude hook: delegates to shared scanner" "$(rg -q 'prompt-secret-scan\.sh' "$CLAUDE_HOOK" && echo 1 || echo 0)"

codex_result() {
  local prompt="$1"
  [ -x "$CODEX_ADAPTER" ] || {
    echo '{}'
    return
  }
  jq -n --arg prompt "$prompt" '{hook_event_name:"UserPromptSubmit", prompt:$prompt}' \
    | bash "$CODEX_ADAPTER" 2>/dev/null
}

codex_deny=$(codex_result "credential $GITHUB_TOKEN")
codex_allow=$(codex_result "safe prompt")
check "codex adapter: secret stops prompt" "$(printf '%s' "$codex_deny" | jq -e '.continue == false and (.stopReason | length > 0)' >/dev/null 2>&1 && echo 1 || echo 0)"
check "codex adapter: benign prompt continues" "$(printf '%s' "$codex_allow" | jq -e '.continue == true' >/dev/null 2>&1 && echo 1 || echo 0)"
check "codex adapter: stop reason does not echo secret value" "$(! printf '%s' "$codex_deny" | grep -Fq "$GITHUB_TOKEN" && echo 1 || echo 0)"

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
