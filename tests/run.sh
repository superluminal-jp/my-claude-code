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
printf -- 'See `${CLAUDE_SKILL_DIR}/assets/missing.css`.\n' >>"$broken/skills/broken-skill/SKILL.md"
printf -- '---\nname: other\n---\n' >"$broken/agents/nameless.md"
printf -- '---\nglobs: "*.py"\n---\nbody\n' >"$broken/rules/bad.md"
printf -- '---\npaths: "*.py"\n---\n' >"$broken/rules/empty.md"
if out="$(python3 "$REPO_DIR/tests/check_harness.py" "$broken")"; then
  fail "the checker passed a broken skill, agent, and rule"
fi
for expected in "skills/broken-skill/SKILL.md: name 'wrong-name' differs from directory" \
  "skills/broken-skill/SKILL.md: front matter fields Claude Code ignores" \
  "skills/broken-skill/SKILL.md: description does not say when" \
  "skills/broken-skill/SKILL.md: points to assets/missing.css, which does not exist" \
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

echo "== an answer names the practices that decided its reasoning, and only those"
comm="$REPO_DIR/harness/rules/communication.md"
for phrase in "name the method and list its steps before starting" "which step it is on" \
  "end the answer with one line labelled Method" "never one matched to the reasoning afterwards" \
  "a standard that only set a format" "skipped, reordered, or replaced" "An answer that applied none has no Method line"; do
  grep -qF "$phrase" "$comm" || fail "rules/communication.md does not say: $phrase"
done
for removed in "**Premises**" "**Assumptions**" "three labelled lines" "three closing lines"; do
  if grep -qF "$removed" "$comm"; then
    fail "rules/communication.md still has: $removed"
  fi
done
reminder="$REPO_DIR/harness/plugins/writing-check/reminder.md"
grep -qF "a Method line" "$reminder" || fail "reminder.md does not mention the Method line"
if grep -qF "three labelled closing lines" "$reminder"; then
  fail "reminder.md still lists the three closing lines"
fi
if grep -qF "without comment" "$REPO_DIR/harness/rules/standards.md"; then
  fail "rules/standards.md still says to use a standard without comment"
fi

echo "== the writing-check plugin"
python3 "$REPO_DIR/tests/test_writing_check.py" 2>&1 | grep -v "^$"

echo "== the create-presentation skill"
skill="$REPO_DIR/harness/skills/create-presentation"
dads="$skill/assets/dads"
# The DADS files in the skill are a copy of one tagged release, as
# scripts/vendor-dads.sh writes them; SHA256SUMS catches a hand edit.
[ -f "$dads/LICENSE" ] || fail "the skill does not carry the DADS license"
[ -f "$dads/global.css" ] || fail "the skill does not carry DADS global.css"
python3 - "$dads" <<'PY' || fail "assets/dads differs from its SHA256SUMS; run scripts/vendor-dads.sh"
import hashlib, sys
from pathlib import Path

root = Path(sys.argv[1])
listed = {}
for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
    digest, name = line.split("  ", 1)
    listed[name] = digest
present = {
    p.relative_to(root).as_posix()
    for p in root.rglob("*")
    if p.is_file() and p.name not in ("SHA256SUMS", "SOURCE")
}
bad = [n for n in sorted(present | set(listed))
       if n not in listed or n not in present
       or hashlib.sha256((root / n).read_bytes()).hexdigest() != listed[n]]
for name in bad:
    print(f"  {name}", file=sys.stderr)
sys.exit(1 if bad else 0)
PY
bash -n "$skill/scripts/copy-dads.sh" || fail "scripts/copy-dads.sh has a syntax error"
# presentation/ is this repository's own use of the skill, so its base is the
# copy the skill makes; the skill's assets are the source.
for rel in deck.css slide.css slide.js page.css; do
  cmp -s "$skill/assets/base/$rel" "$REPO_DIR/presentation/base/$rel" \
    || fail "presentation/base/$rel differs from the skill's assets/base/$rel"
done
# Copy the templates into a project the way the skill does, and see that every
# file they link resolves, that the license comes along, and that a component
# no template uses is not copied.
project="$WORK_DIR/project/presentation"
mkdir -p "$project"
cp -R "$skill/assets/base" "$project/base"
cp "$skill/assets/templates/slides.html" "$skill/assets/templates/page.html" "$project/"
bash "$skill/scripts/copy-dads.sh" "$project" >/dev/null || fail "copy-dads.sh failed on the templates"
[ -f "$project/dads/LICENSE" ] || fail "copy-dads.sh did not copy the DADS license"
[ ! -e "$project/dads/components/tab" ] || fail "copy-dads.sh copied a component no file uses"
for html in "$project"/*.html "$REPO_DIR"/presentation/*.html; do
  dir="$(dirname "$html")"
  for ref in $(grep -oE '(dads|base)/[A-Za-z0-9/_.-]+\.(css|js)' "$html" | sort -u); do
    [ -f "$dir/$ref" ] || fail "$(basename "$html") links $ref, which is not there"
  done
done
grep -q 'design-system-example-components-html' "$project"/*.html "$REPO_DIR"/presentation/*.html \
  && fail "an HTML file still links the DADS clone"

echo "== install.sh"
target="$WORK_DIR/claude"
mkdir -p "$target/skills/stale-skill" "$target/commands" "$target/rules" "$target/agents"
echo stale >"$target/skills/stale-skill/SKILL.md"
echo keep >"$target/commands/own-command.md"
echo keep >"$target/settings.json"
echo stale >"$target/rules/stale.md"
echo stale >"$target/agents/stale.md"
# Install from a copy of the source that carries files which are not
# configuration, to see that they are left out.
mkdir "$WORK_DIR/repo"
# The path as install.sh will name it: on macOS $TMPDIR ends in a slash, and
# install.sh prints its own directory as `pwd` gives it, with single slashes.
source_repo="$(cd "$WORK_DIR/repo" && pwd)"
cp "$REPO_DIR/install.sh" "$source_repo/install.sh"
cp -R "$REPO_DIR/harness" "$source_repo/harness"
touch "$source_repo/harness/rules/.DS_Store"
mkdir -p "$source_repo/harness/agents/.claude/.cc-writes"
install_out="$(CLAUDE_CONFIG_DIR="$target" bash "$source_repo/install.sh")"
# The plugin is not copied, so the install says how to enable it, with the
# path of the checkout it was run from.
for expected in "claude plugin marketplace add \"$source_repo\"" \
  "claude plugin install writing-check@local-harness --scope user"; do
  grep -qF "$expected" <<<"$install_out" || fail "install.sh did not print: $expected"
done
[ -z "$(find "$target/rules" "$target/agents" "$target/skills" -name .DS_Store -o -name .claude)" ] \
  || fail "Finder metadata or a .claude marker directory was installed"
[ -z "$(find "$target" -maxdepth 1 -name '.install-new.*')" ] || fail "a staging directory was left behind"

for rel in CLAUDE.md rules agents skills; do
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
[ ! -e "$target/skills/stale-skill" ] || fail "a skill removed from harness/ survived the install"
# The check script of the skill is run by path, so it has to stay readable.
[ -r "$target/skills/create-presentation/scripts/check.cjs" ] || fail "the skill's script was not installed"
[ "$(cat "$target/commands/own-command.md")" = keep ] || fail "commands/ was touched"
[ "$(cat "$target/settings.json")" = keep ] || fail "settings.json was touched"
# ~/.claude/plugins/ is where Claude Code keeps its own record of installed
# plugins, so the plugin under harness/plugins/ is not copied there.
[ ! -e "$target/plugins" ] || fail "plugins/ was created in the target"

CLAUDE_CONFIG_DIR="$target" bash "$REPO_DIR/install.sh" >/dev/null \
  || fail "a second install run failed"

echo "== a failed install leaves the installed files as they were"
failing="$WORK_DIR/failing-repo"
mkdir -p "$failing/harness/rules" "$failing/harness/agents" "$failing/harness/skills"
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
