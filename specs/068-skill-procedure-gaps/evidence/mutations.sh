#!/usr/bin/env bash
# Two observations for the tests spec 068 added, made on copies in a temporary
# directory (the repository is only read):
# 1. red: the new tests at HEAD fail on their assertions (FAIL), with no
#    error (ERROR, such as a usage error) — against the checkers of main
#    (9cd7932) where main has the command, and otherwise against HEAD with
#    the feature replaced by a stub of its final signature that gives a wrong
#    result (the red coder's TDD section asks for);
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

run_tests() {  # run_tests SKILL_DIR TEST...: prints "failed F, errors E" or "passed"
  local dir="$1"; shift
  local out
  out="$(cd "$dir/tests" && python3 -B -m unittest "$@" 2>&1)"
  if printf '%s' "$out" | grep -q '^OK'; then echo passed; else
    echo "failed $(printf '%s' "$out" | grep -c '^FAIL:'), errors $(printf '%s' "$out" | grep -c '^ERROR:')"; fi
}

replace_once() {  # replace_once FILE OLD NEW
  python3 -I - "$1" "$2" "$3" <<'EOF'
import sys
path, old, new = sys.argv[1:]
text = open(path, encoding="utf-8").read()
if text.count(old) != 1:
    sys.exit(f"the replacement point occurs {text.count(old)} times")
open(path, "w", encoding="utf-8").write(text.replace(old, new))
EOF
}

expect_red() {  # expect_red LABEL DIR TEST: a red is assertion failures and no error
  local got
  got="$(run_tests "$2" "$3")"
  printf 'red      %-45s %s: %s\n' "$3" "$1" "$got"
  case "$got" in "failed 0,"*|passed) bad=1 ;; *", errors 0") ;; *) bad=1 ;; esac
}

# 1. red
copy_skills "$WORK/main"
git -C "$REPO" show 9cd7932:.claude/skills/requirements-decomposition/scripts/check_graph.py > "$WORK/main/requirements-decomposition/scripts/check_graph.py"
git -C "$REPO" show 9cd7932:.claude/skills/verified-delivery/scripts/assure.py > "$WORK/main/verified-delivery/scripts/assure.py"
expect_red "against main" "$WORK/main/requirements-decomposition" test_check_graph.StageAndOriginTests
expect_red "against main" "$WORK/main/verified-delivery" test_card.StageCardTests
expect_red "against main" "$WORK/main/verified-delivery" test_card.OriginCardTests
copy_skills "$WORK/stub"
replace_once "$WORK/stub/verified-delivery/scripts/assure.py" \
  'deferrable = post_deploy_criteria(document) if stage == "pre_deploy" else set()' 'deferrable = set()  # stub' || bad=1
replace_once "$WORK/stub/verified-delivery/scripts/assure.py" \
  'report = load_json(report_path, "the Jest report")' \
  'return [{"check_id": c, "status": "not_run", "reason": "stub"} for c, _, _ in criteria]' || bad=1
expect_red "against a stub of --stage" "$WORK/stub/verified-delivery" test_assure.StageTests
expect_red "against a stub of collect-jest" "$WORK/stub/verified-delivery" test_assure.JestTests

# 2. mutations: FILE, the text to replace (once), its replacement, the test
mutate() {
  local name="$1" skill="$2" file="$3" old="$4" new="$5" test="$6"
  rm -rf "$WORK/m"; copy_skills "$WORK/m"
  replace_once "$WORK/m/$skill/scripts/$file" "$old" "$new" || { bad=1; return; }
  got="$(run_tests "$WORK/m/$skill" "$test")"
  printf 'mutation %-45s %s\n' "$name" "$got"
  case "$got" in "failed 0,"*|passed) bad=1 ;; *", errors 0") ;; *) bad=1 ;; esac
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
mutate "nothing verified before deploy passes" verified-delivery assure.py \
  'deferred = set(left_out)' 'deferred = set()' \
  test_assure.StageTests.test_before_deploy_a_parent_whose_own_checks_are_all_post_deploy_is_blocked
mutate "a Jest file that failed to run is ignored" verified-delivery assure.py \
  'all(outcome == "passed" for outcome in outcomes) and not incomplete:' 'all(outcome == "passed" for outcome in outcomes):' \
  test_assure.JestTests.test_a_file_that_failed_outside_its_tests_lets_nothing_pass

echo "result: $([ "$bad" -eq 0 ] && echo 'every observation as expected' || echo 'some observation NOT as expected')"
exit "$bad"
