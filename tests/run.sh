#!/usr/bin/env bash
# Run every check of this repository. Writes only under $TMPDIR.
#
# Usage: bash tests/run.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/harness-test.XXXXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

fail() {
  echo "FAIL $1" >&2
  exit 1
}

echo "== format of harness/"
python3 "$REPO_DIR/tests/check_harness.py"

echo "== the checker rejects a broken harness"
broken="$WORK_DIR/broken"
cp -R "$REPO_DIR/harness" "$broken"
rm -rf "$broken/skills/apply-dads-frontend"
printf -- '---\nname: wrong-name\ndescription: Does a thing.\nmetadata:\n  x: y\n---\nbody\n' \
  >"$broken/skills/manage-git/SKILL.md"
if out="$(python3 "$REPO_DIR/tests/check_harness.py" "$broken")"; then
  fail "the checker passed a skill with a wrong name, an ignored field, and no trigger"
fi
for expected in "differs from directory" "Claude Code ignores" "does not say when"; do
  grep -q "$expected" <<<"$out" || fail "the checker did not report: $expected"
done

echo "== install.sh"
target="$WORK_DIR/claude"
mkdir -p "$target/skills/synced/app-skill" "$target/skills/stale-skill" "$target/rules"
echo keep >"$target/skills/synced/app-skill/SKILL.md"
echo keep >"$target/settings.json"
echo stale >"$target/rules/stale.md"
CLAUDE_CONFIG_DIR="$target" bash "$REPO_DIR/install.sh" >/dev/null

for rel in CLAUDE.md rules skills agents; do
  src="$REPO_DIR/harness/$rel"
  if [ -d "$src" ]; then
    diff -r -x synced -x .DS_Store -x .claude "$src" "$target/$rel" >/dev/null \
      || fail "$rel in the target differs from harness/$rel"
  else
    cmp -s "$src" "$target/$rel" || fail "$rel in the target differs from harness/$rel"
  fi
done
[ ! -e "$target/skills/stale-skill" ] || fail "a skill removed from harness/ survived the install"
[ ! -e "$target/rules/stale.md" ] || fail "a rule removed from harness/ survived the install"
[ "$(cat "$target/skills/synced/app-skill/SKILL.md")" = keep ] || fail "skills/synced/ was not preserved"
[ "$(cat "$target/settings.json")" = keep ] || fail "settings.json was touched"
[ -z "$(find "$target" -maxdepth 1 -name '.install-keep.*')" ] || fail "a temporary directory was left behind"

CLAUDE_CONFIG_DIR="$target" bash "$REPO_DIR/install.sh" >/dev/null \
  || fail "a second install run failed"

echo "== install.sh recovers skills/synced from an interrupted run"
rm -rf "$target/skills/synced"
mkdir -p "$target/.install-keep.old/synced"
echo stranded >"$target/.install-keep.old/synced/marker"
CLAUDE_CONFIG_DIR="$target" bash "$REPO_DIR/install.sh" >/dev/null
[ "$(cat "$target/skills/synced/marker" 2>/dev/null)" = stranded ] || fail "a stranded skills/synced/ was not recovered"
[ -z "$(find "$target" -maxdepth 1 -name '.install-keep.*')" ] || fail "a keep directory was left behind after recovery"

echo "== install.sh puts skills/synced back when a copy fails"
failing="$WORK_DIR/failing-repo"
mkdir -p "$failing/harness/rules" "$failing/harness/agents"
cp "$REPO_DIR/install.sh" "$failing/install.sh"
echo x >"$failing/harness/CLAUDE.md"
mkdir "$failing/harness/skills"
echo x >"$failing/harness/skills/unreadable"
chmod 000 "$failing/harness/skills/unreadable"
if CLAUDE_CONFIG_DIR="$target" bash "$failing/install.sh" >/dev/null 2>&1; then
  chmod 644 "$failing/harness/skills/unreadable"
  fail "install.sh succeeded although a source file could not be copied"
fi
chmod 644 "$failing/harness/skills/unreadable"
[ "$(cat "$target/skills/synced/marker" 2>/dev/null)" = stranded ] || fail "skills/synced/ was lost when the install failed"

echo "All checks passed."
