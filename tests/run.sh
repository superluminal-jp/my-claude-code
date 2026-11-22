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
mkdir -p "$broken/skills/broken-skill"
printf -- '---\nname: wrong-name\ndescription: Does a thing.\nmetadata:\n  x: y\n---\nbody\n' \
  >"$broken/skills/broken-skill/SKILL.md"
printf -- '---\nname: other\n---\n' >"$broken/agents/nameless.md"
printf -- '---\nglobs: "*.py"\n---\nbody\n' >"$broken/rules/bad.md"
printf -- '---\npaths: "*.py"\n---\n' >"$broken/rules/empty.md"
if out="$(python3 "$REPO_DIR/tests/check_harness.py" "$broken")"; then
  fail "the checker passed a broken skill, agent, and rule"
fi
for expected in "skills/broken-skill/SKILL.md: name 'wrong-name' differs from directory" \
  "skills/broken-skill/SKILL.md: front matter fields Claude Code ignores" \
  "skills/broken-skill/SKILL.md: description does not say when" \
  "agents/nameless.md: name 'other' differs from file name" \
  "agents/nameless.md: no description" \
  "rules/bad.md: front matter fields Claude Code ignores" \
  "rules/empty.md: empty body"; do
  grep -qF "$expected" <<<"$out" || fail "the checker did not report: $expected"
done

echo "== the checker enforces the always-loaded budget"
big="$WORK_DIR/big"
cp -R "$REPO_DIR/harness" "$big"
python3 -c 'print("x" * 20000)' >>"$big/rules/safety.md"
if out="$(python3 "$REPO_DIR/tests/check_harness.py" "$big")"; then
  fail "the checker passed an oversized always-loaded rule"
fi
grep -q "always-loaded text is" <<<"$out" || fail "the checker did not report the byte budget"

echo "== every answer states its premises, assumptions, and method"
for label in "Premises" "Assumptions" "Method"; do
  grep -qF "**$label**" "$REPO_DIR/harness/rules/communication.md" \
    || fail "rules/communication.md does not require a $label line"
done
for framework in "Toulmin model" "Key Assumptions Check" "IMRaD" "ICD 203"; do
  grep -qF "$framework" "$REPO_DIR/harness/rules/communication.md" \
    || fail "rules/communication.md does not name $framework"
done
if grep -qF "without comment" "$REPO_DIR/harness/rules/standards.md"; then
  fail "rules/standards.md still says to use a standard without comment"
fi

echo "== install.sh"
target="$WORK_DIR/claude"
mkdir -p "$target/skills/own-skill" "$target/rules" "$target/agents"
echo keep >"$target/skills/own-skill/SKILL.md"
echo keep >"$target/settings.json"
echo stale >"$target/rules/stale.md"
echo stale >"$target/agents/stale.md"
# Install from a copy of the source that carries files which are not
# configuration, to see that they are left out.
source_repo="$WORK_DIR/repo"
mkdir "$source_repo"
cp "$REPO_DIR/install.sh" "$source_repo/install.sh"
cp -R "$REPO_DIR/harness" "$source_repo/harness"
touch "$source_repo/harness/rules/.DS_Store"
mkdir -p "$source_repo/harness/agents/.claude/.cc-writes"
CLAUDE_CONFIG_DIR="$target" bash "$source_repo/install.sh" >/dev/null
[ -z "$(find "$target/rules" "$target/agents" -name .DS_Store -o -name .claude)" ] \
  || fail "Finder metadata or a .claude marker directory was installed"
[ -z "$(find "$target" -maxdepth 1 -name '.install-new.*')" ] || fail "a staging directory was left behind"

for rel in CLAUDE.md rules agents; do
  src="$REPO_DIR/harness/$rel"
  if [ -d "$src" ]; then
    diff -r -x .DS_Store -x .claude "$src" "$target/$rel" >/dev/null \
      || fail "$rel in the target differs from harness/$rel"
  else
    cmp -s "$src" "$target/$rel" || fail "$rel in the target differs from harness/$rel"
  fi
done
[ ! -e "$target/rules/stale.md" ] || fail "a rule removed from harness/ survived the install"
[ ! -e "$target/agents/stale.md" ] || fail "an agent removed from harness/ survived the install"
[ "$(cat "$target/skills/own-skill/SKILL.md")" = keep ] || fail "skills/ was touched"
[ "$(cat "$target/settings.json")" = keep ] || fail "settings.json was touched"

CLAUDE_CONFIG_DIR="$target" bash "$REPO_DIR/install.sh" >/dev/null \
  || fail "a second install run failed"

echo "== a failed install leaves the installed files as they were"
failing="$WORK_DIR/failing-repo"
mkdir -p "$failing/harness/rules" "$failing/harness/agents"
cp "$REPO_DIR/install.sh" "$failing/install.sh"
echo new >"$failing/harness/CLAUDE.md"
echo new >"$failing/harness/rules/unreadable.md"
chmod 000 "$failing/harness/rules/unreadable.md"
if CLAUDE_CONFIG_DIR="$target" bash "$failing/install.sh" >/dev/null 2>&1; then
  chmod 644 "$failing/harness/rules/unreadable.md"
  fail "install.sh succeeded although a source file could not be copied"
fi
chmod 644 "$failing/harness/rules/unreadable.md"
cmp -s "$REPO_DIR/harness/CLAUDE.md" "$target/CLAUDE.md" || fail "a failed install changed CLAUDE.md"
[ -f "$target/rules/standards.md" ] || fail "a failed install removed the installed rules"
[ -z "$(find "$target" -maxdepth 1 -name '.install-new.*')" ] || fail "a failed install left its staging directory"

echo "All checks passed."
