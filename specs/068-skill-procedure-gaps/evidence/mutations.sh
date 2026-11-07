#!/usr/bin/env bash
# Two observations for the tests spec 068 added, made on copies in a temporary
# directory (the repository is only read):
# 1. red: the new tests at HEAD, run against the checkers of main (9cd7932),
#    fail on their assertions;
# 2. mutation: the tests that could not fail before the change (they pin
#    behavior the change must keep, or the change's absence passed them for
#    another reason) fail when the implementation is broken on purpose.
# Usage: mutations.sh. Prints one line per observation; exit 0 when every
# observation is as expected.

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
WORK="$(mktemp -d "${TMPDIR:-/tmp}/spec068-mut.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
bad=0

copy_skills() {  # copy_skills DEST: the two skills at the working tree of HEAD
  mkdir -p "$1"
  cp -R "$REPO/.claude/skills/requirements-decomposition" "$REPO/.claude/skills/verified-delivery" "$1/"
}

run_tests() {  # run_tests SKILL_DIR TEST...: prints "failed N" or "passed"
  local dir="$1"; shift
  local out
  out="$(cd "$dir/tests" && python3 -B -m unittest "$@" 2>&1)"
  if printf '%s' "$out" | grep -q '^OK'; then echo passed; else
    echo "failed $(printf '%s' "$out" | grep -cE '^(FAIL|ERROR):')"; fi
}

# 1. red against main's checkers
copy_skills "$WORK/red"
git -C "$REPO" show 9cd7932:.claude/skills/requirements-decomposition/scripts/check_graph.py > "$WORK/red/requirements-decomposition/scripts/check_graph.py"
git -C "$REPO" show 9cd7932:.claude/skills/verified-delivery/scripts/assure.py > "$WORK/red/verified-delivery/scripts/assure.py"
for spec in "requirements-decomposition test_check_graph.StageAndOriginTests" \
            "verified-delivery test_assure.StageTests" "verified-delivery test_assure.JestTests" \
            "verified-delivery test_card.StageCardTests" "verified-delivery test_card.OriginCardTests"; do
  set -- $spec
  got="$(run_tests "$WORK/red/$1" "$2")"
  printf 'red      %-45s against main: %s\n' "$2" "$got"
  case "$got" in failed*) ;; *) bad=1 ;; esac
done

# 2. mutations: FILE, the text to replace (once), its replacement, the test
mutate() {
  local name="$1" skill="$2" file="$3" old="$4" new="$5" test="$6"
  rm -rf "$WORK/m"; copy_skills "$WORK/m"
  if ! python3 -I - "$WORK/m/$skill/scripts/$file" "$old" "$new" <<'EOF'
import sys
path, old, new = sys.argv[1:]
text = open(path, encoding="utf-8").read()
if text.count(old) != 1:
    sys.exit(f"the mutation point occurs {text.count(old)} times")
open(path, "w", encoding="utf-8").write(text.replace(old, new))
EOF
  then bad=1; return; fi
  got="$(run_tests "$WORK/m/$skill" "$test")"
  printf 'mutation %-45s %s\n' "$name" "$got"
  case "$got" in failed*) ;; *) bad=1 ;; esac
}

mutate "origin shape is not checked" requirements-decomposition check_graph.py \
  '        if (not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS' \
  '        if False and (not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS' \
  test_check_graph.StageAndOriginTests.test_a_malformed_origin_is_rejected_under_s_00
mutate "the gate refuses a graph with an origin" verified-delivery assure.py \
  '        entries = node.get("acceptance") if isinstance(node, dict) else None' \
  '        if isinstance(node, dict) and "origin" in node: raise InputError("origin")
        entries = node.get("acceptance") if isinstance(node, dict) else None' \
  test_assure.StageTests.test_a_requirement_with_an_instruction_origin_is_decided_as_without_one
mutate "the card always shows a decision before deploy" verified-delivery assure.py \
  'if post_deploy_criteria(document) else None' 'if True else None' \
  test_card.StageCardTests.test_a_graph_without_post_deploy_criteria_has_no_line_before_deploy
mutate "a failed post-deploy check is left out" verified-delivery assure.py \
  'elif status == "not_run" and criterion in deferrable:' 'elif criterion in deferrable:' \
  test_assure.StageTests.test_before_deploy_a_failed_blocked_or_missing_post_deploy_check_is_not_left_out
mutate "a Jest file that failed to run is ignored" verified-delivery assure.py \
  'all(outcome == "passed" for outcome in outcomes) and not incomplete:' 'all(outcome == "passed" for outcome in outcomes):' \
  test_assure.JestTests.test_a_file_that_failed_outside_its_tests_lets_nothing_pass

echo "result: $([ "$bad" -eq 0 ] && echo 'every observation as expected' || echo 'some observation NOT as expected')"
exit "$bad"
