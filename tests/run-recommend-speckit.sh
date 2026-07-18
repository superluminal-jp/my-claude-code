#!/usr/bin/env bash
# Behavior test for .claude/hooks/recommend-speckit.sh.
# Verifies the UserPromptSubmit nudge: recommend `specify init` for
# non-trivial implementation prompts in a project without .specify/,
# staying silent for trivial prompts, already-adopted projects, on-topic
# prompts, and within the per-project throttle window.
#
# Deterministic: no network, no external tools beyond jq.
# Usage: bash tests/run-recommend-speckit.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO_ROOT/.claude/hooks/recommend-speckit.sh"

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

IMPL_PROMPT="Please implement a new checkout feature that lets users apply a discount code before payment."
SHORT_PROMPT="fix typo in readme"
ONTOPIC_PROMPT="Please run specify init and set up spec-kit for this new implementation project we are starting."

run_hook() {
  local tmp="$1" proj="$2" prompt="$3"
  shift 3
  local input
  input=$(jq -n --arg cwd "$proj" --arg prompt "$prompt" '{cwd:$cwd, prompt:$prompt}')
  TMPDIR="$tmp" "$@" bash "$HOOK" <<<"$input"
}

# --- Test 1: non-trivial prompt, no .specify/ -> recommends spec-kit ---
WORK1=$(mktemp -d)
mkdir -p "$WORK1/proj" "$WORK1/cache"
out1=$(run_hook "$WORK1/cache" "$WORK1/proj" "$IMPL_PROMPT")
echo "$out1" | jq -e '.hookSpecificOutput.additionalContext | test("specify init")' >/dev/null 2>&1 && c=1 || c=0
check "non-trivial prompt without .specify/ recommends specify init" "$c"
rm -rf "$WORK1"

# --- Test 2: project already has .specify/ -> silent ---
WORK2=$(mktemp -d)
mkdir -p "$WORK2/proj/.specify" "$WORK2/cache"
out2=$(run_hook "$WORK2/cache" "$WORK2/proj" "$IMPL_PROMPT")
[ -z "$out2" ] && c=1 || c=0
check "project with existing .specify/ stays silent" "$c"
rm -rf "$WORK2"

# --- Test 3: short/trivial prompt -> silent ---
WORK3=$(mktemp -d)
mkdir -p "$WORK3/proj" "$WORK3/cache"
out3=$(run_hook "$WORK3/cache" "$WORK3/proj" "$SHORT_PROMPT")
[ -z "$out3" ] && c=1 || c=0
check "short/trivial prompt stays silent" "$c"
rm -rf "$WORK3"

# --- Test 4: prompt already on-topic about spec-kit -> silent ---
WORK4=$(mktemp -d)
mkdir -p "$WORK4/proj" "$WORK4/cache"
out4=$(run_hook "$WORK4/cache" "$WORK4/proj" "$ONTOPIC_PROMPT")
[ -z "$out4" ] && c=1 || c=0
check "prompt already mentioning specify init stays silent" "$c"
rm -rf "$WORK4"

# --- Test 5: throttle — second recommendation within the window is silent ---
WORK5=$(mktemp -d)
mkdir -p "$WORK5/proj" "$WORK5/cache"
first=$(run_hook "$WORK5/cache" "$WORK5/proj" "$IMPL_PROMPT")
second=$(run_hook "$WORK5/cache" "$WORK5/proj" "$IMPL_PROMPT")
[ -n "$first" ] && [ -z "$second" ] && c=1 || c=0
check "second recommendation within the throttle window is silent" "$c"
rm -rf "$WORK5"

# --- Test 6: throttle bypass via SPECKIT_RECOMMEND_INTERVAL_SECONDS=0 ---
WORK6=$(mktemp -d)
mkdir -p "$WORK6/proj" "$WORK6/cache"
run_hook "$WORK6/cache" "$WORK6/proj" "$IMPL_PROMPT" >/dev/null
third=$(run_hook "$WORK6/cache" "$WORK6/proj" "$IMPL_PROMPT" env SPECKIT_RECOMMEND_INTERVAL_SECONDS=0)
echo "$third" | jq -e '.hookSpecificOutput.additionalContext | test("specify init")' >/dev/null 2>&1 && c=1 || c=0
check "SPECKIT_RECOMMEND_INTERVAL_SECONDS=0 bypasses the throttle" "$c"
rm -rf "$WORK6"

# --- Test 7: distinct projects are throttled independently ---
WORK7=$(mktemp -d)
mkdir -p "$WORK7/proj-a" "$WORK7/proj-b" "$WORK7/cache"
run_hook "$WORK7/cache" "$WORK7/proj-a" "$IMPL_PROMPT" >/dev/null
out_b=$(run_hook "$WORK7/cache" "$WORK7/proj-b" "$IMPL_PROMPT")
echo "$out_b" | jq -e '.hookSpecificOutput.additionalContext | test("specify init")' >/dev/null 2>&1 && c=1 || c=0
check "a different project is not affected by another project's throttle" "$c"
rm -rf "$WORK7"

# --- Test 8: missing prompt/cwd -> exits cleanly, no crash ---
WORK8=$(mktemp -d)
TMPDIR="$WORK8/cache" bash "$HOOK" <<<'{}' >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && c=1 || c=0
check "missing prompt/cwd: hook exits cleanly" "$c"
rm -rf "$WORK8"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
