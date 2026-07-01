#!/usr/bin/env bash
# Behavior test for .claude/hooks/speckit-expand-update.sh user-scope sync.
# Verifies that after a successful project `specify init`, freshly regenerated
# speckit-* skills are propagated to the user-scope install (~/.claude/skills),
# so skills imported into user settings stay in lockstep with the update.
#
# Deterministic: specify/uv/gh/curl are stubbed on PATH; no network is used.
# Usage: bash tests/run-speckit-update.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO_ROOT/.claude/hooks/speckit-expand-update.sh"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

# Stub `curl`: answers the releases/latest lookup with a fixed tag and fails
# any download (`-o`), so the tarball path is never taken and no real network
# request occurs. The hook falls back to its git+https branch, which the `uv`
# stub below ignores.
CURL_STUB='#!/usr/bin/env bash
for a in "$@"; do
  [ "$a" = "-o" ] && exit 1
done
case "$*" in
  *releases/latest*) echo "{\"tag_name\":\"v0.0.0-stub\"}" ;;
  *) exit 1 ;;
esac'

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

# Build an isolated HOME + project + stubbed toolchain, then run the hook.
# Echoes nothing; sets up state under $1 (work dir). Returns via globals.
run_hook() {
  local work="$1" sync_flag="$2"
  local home="$work/home" proj="$work/proj" bin="$work/bin"

  mkdir -p "$home/.claude/skills/speckit-foo"
  printf 'STALE\n' >"$home/.claude/skills/speckit-foo/SKILL.md"

  mkdir -p "$proj/.specify" "$proj/.claude/skills/speckit-foo" "$proj/.claude/skills/speckit-bar"
  printf 'FRESH-foo\n' >"$proj/.claude/skills/speckit-foo/SKILL.md"
  printf 'FRESH-bar\n' >"$proj/.claude/skills/speckit-bar/SKILL.md"

  # Stub specify/uv/gh/curl so init "succeeds" with no network.
  mkdir -p "$bin"
  printf '#!/usr/bin/env bash\nexit 0\n' >"$bin/specify"
  printf '#!/usr/bin/env bash\nexit 0\n' >"$bin/uv"
  printf '#!/usr/bin/env bash\nexit 1\n' >"$bin/gh"
  printf '%s\n' "$CURL_STUB" >"$bin/curl"
  chmod +x "$bin/specify" "$bin/uv" "$bin/gh" "$bin/curl"

  local input
  input=$(jq -n --arg cwd "$proj" '{cwd:$cwd, command_name:"speckit.plan"}')

  HOME="$home" PATH="$bin:$PATH" SPECIFY_FORCE_AUTO_UPDATE=1 \
    SPECIFY_SYNC_USER_SKILLS="$sync_flag" \
    bash "$HOOK" <<<"$input" >/dev/null 2>&1
}

# --- Test 1: user-scope skills are refreshed from the project after update ---
WORK1=$(mktemp -d)
run_hook "$WORK1" "1"
got1=$(cat "$WORK1/home/.claude/skills/speckit-foo/SKILL.md" 2>/dev/null || echo MISSING)
[ "$got1" = "FRESH-foo" ] && c=1 || c=0
check "stale user-scope skill updated to fresh project version" "$c"
[ -f "$WORK1/home/.claude/skills/speckit-bar/SKILL.md" ] && c=1 || c=0
check "newly added speckit skill propagated to user scope" "$c"
rm -rf "$WORK1"

# --- Test 2: opt-out via SPECIFY_SYNC_USER_SKILLS=0 leaves user scope alone ---
WORK2=$(mktemp -d)
run_hook "$WORK2" "0"
got2=$(cat "$WORK2/home/.claude/skills/speckit-foo/SKILL.md" 2>/dev/null || echo MISSING)
[ "$got2" = "STALE" ] && c=1 || c=0
check "opt-out flag leaves user-scope skills untouched" "$c"
rm -rf "$WORK2"

# --- Test 3: no ~/.claude/skills present -> no crash, nothing created ---
WORK3=$(mktemp -d)
mkdir -p "$WORK3/home" "$WORK3/proj/.specify" "$WORK3/proj/.claude/skills/speckit-foo" "$WORK3/bin"
printf 'FRESH\n' >"$WORK3/proj/.claude/skills/speckit-foo/SKILL.md"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK3/bin/specify"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK3/bin/uv"
printf '#!/usr/bin/env bash\nexit 1\n' >"$WORK3/bin/gh"
printf '%s\n' "$CURL_STUB" >"$WORK3/bin/curl"
chmod +x "$WORK3/bin/specify" "$WORK3/bin/uv" "$WORK3/bin/gh" "$WORK3/bin/curl"
input3=$(jq -n --arg cwd "$WORK3/proj" '{cwd:$cwd, command_name:"speckit.plan"}')
HOME="$WORK3/home" PATH="$WORK3/bin:$PATH" SPECIFY_FORCE_AUTO_UPDATE=1 \
  bash "$HOOK" <<<"$input3" >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && [ ! -d "$WORK3/home/.claude/skills" ] && c=1 || c=0
check "absent user-scope install: hook exits cleanly, creates nothing" "$c"
rm -rf "$WORK3"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
