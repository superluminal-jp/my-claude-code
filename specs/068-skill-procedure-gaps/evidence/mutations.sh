#!/usr/bin/env bash
# Shows, test by test, that every test spec 068 added can fail on its
# assertion (coder's red), on copies in a temporary directory (the repository
# is only read). Each new test is run alone:
# 1. red: against the checkers of main (9cd7932) where main has the command,
#    and otherwise against HEAD with the feature replaced by a stub of its
#    final signature that gives a wrong result;
# 2. mutation: against HEAD with the implementation broken on purpose, for
#    the tests the red cannot fail (they pin behavior the change must keep,
#    or the stub passes them for another reason).
# A test is covered when it FAILs (an assertion) in at least one of these; an
# ERROR (such as a usage error or a missing key) never counts and is reported.
# Usage: mutations.sh. Exit 0 when every new test is covered and nothing ERRORs.

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
WORK="$(mktemp -d "${TMPDIR:-/tmp}/spec068-mut.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
bad=0
COVERED="$WORK/covered"
: > "$COVERED"

copy_skills() {  # copy_skills DEST: the two skills of the working tree
  mkdir -p "$1"
  cp -R "$REPO/.claude/skills/requirements-decomposition" "$REPO/.claude/skills/verified-delivery" "$1/"
}

replace_once() {  # replace_once FILE OLD NEW
  python3 -I - "$1" "$2" "$3" <<'EOF'
import sys
path, old, new = sys.argv[1:]
text = open(path, encoding="utf-8").read()
if text.count(old) != 1:
    sys.exit(f"the replacement point occurs {text.count(old)} times: {old!r}")
open(path, "w", encoding="utf-8").write(text.replace(old, new))
EOF
}

outcome() {  # outcome SKILL_DIR TEST_ID: PASS, FAIL (assertions only), or ERROR
  local out
  out="$(cd "$1/tests" && python3 -B -m unittest "$2" 2>&1)"
  if printf '%s' "$out" | grep -q '^OK'; then echo PASS
  elif printf '%s' "$out" | grep -qE '^FAILED \(.*errors='; then echo ERROR
  else echo FAIL; fi
}

new_tests() {  # new_tests SKILL_DIR MODULE.CLASS...: the test ids of these classes
  local dir="$1"; shift
  (cd "$dir/tests" && python3 -B -c '
import sys, unittest
for name in sys.argv[1:]:
    module, cls = name.split(".")
    case = getattr(__import__(module), cls)
    for method in unittest.defaultTestLoader.getTestCaseNames(case):
        print(f"{name}.{method}")' "$@")
}

observe() {  # observe KIND LABEL SKILL_DIR TEST_ID
  local got
  got="$(outcome "$3" "$4")"
  printf '%-8s %-38s %-5s %s\n' "$1" "$2" "$got" "$4"
  [ "$got" = FAIL ] && echo "$4" >> "$COVERED"
  [ "$got" = ERROR ] && bad=1
}

RD_CLASSES="test_check_graph.StageAndOriginTests"
VD_MAIN_CLASSES="test_card.StageCardTests test_card.OriginCardTests"
VD_STUB_CLASSES="test_assure.StageTests test_assure.JestTests"

# 1. red
copy_skills "$WORK/main"
git -C "$REPO" show 9cd7932:.claude/skills/requirements-decomposition/scripts/check_graph.py > "$WORK/main/requirements-decomposition/scripts/check_graph.py"
git -C "$REPO" show 9cd7932:.claude/skills/verified-delivery/scripts/assure.py > "$WORK/main/verified-delivery/scripts/assure.py"
for t in $(new_tests "$WORK/main/requirements-decomposition" $RD_CLASSES); do observe red "against main" "$WORK/main/requirements-decomposition" "$t"; done
for t in $(new_tests "$WORK/main/verified-delivery" $VD_MAIN_CLASSES); do observe red "against main" "$WORK/main/verified-delivery" "$t"; done
# The flow check (tests/assert_delivery_flow.py) with main's checkers: FAIL when it
# exits 1 with a FAIL line for each of its checks and no Python traceback.
mkdir -p "$WORK/main-root/.claude/skills" "$WORK/main-root/tests/fixtures"
cp -R "$WORK/main/requirements-decomposition" "$WORK/main/verified-delivery" "$WORK/main-root/.claude/skills/"
cp -R "$REPO/tests/fixtures/delivery-flow" "$WORK/main-root/tests/fixtures/"
flow_out="$(python3 -B "$REPO/tests/assert_delivery_flow.py" "$WORK/main-root" 2>&1)"; flow_code=$?
flow_checks="$(printf '%s\n' "$flow_out" | grep -cE '^(ok  |FAIL) ')"; flow_fails="$(printf '%s\n' "$flow_out" | grep -c '^FAIL ')"
if [ "$flow_code" -eq 1 ] && [ "$flow_fails" -eq "$flow_checks" ] && ! printf '%s' "$flow_out" | grep -q Traceback; then flow=FAIL; else flow=ERROR; bad=1; fi
printf '%-8s %-38s %-5s %s (%s of %s checks fail)\n' red "against main" "$flow" tests/assert_delivery_flow.py "$flow_fails" "$flow_checks"
[ "$flow" = FAIL ] && echo tests/assert_delivery_flow.py >> "$COVERED"
copy_skills "$WORK/stub"
S="$WORK/stub/verified-delivery/scripts/assure.py"
replace_once "$S" 'deferrable = post_deploy_criteria(document) if stage == "pre_deploy" else set()' 'deferrable = set()  # stub' || bad=1
replace_once "$S" 'report = load_json(report_path, "the Jest report")' \
  'return [{"check_id": c, "status": "not_run", "reason": "stub"} for c, _, _ in criteria]' || bad=1
for t in $(new_tests "$WORK/stub/verified-delivery" $VD_STUB_CLASSES); do observe red "against a stub of the feature" "$WORK/stub/verified-delivery" "$t"; done

# 2. mutations: NAME SKILL FILE OLD NEW TEST...
mutate() {
  local name="$1" skill="$2" file="$3" old="$4" new="$5"; shift 5
  rm -rf "$WORK/m"; copy_skills "$WORK/m"
  replace_once "$WORK/m/$skill/scripts/$file" "$old" "$new" || { bad=1; return; }
  for t in "$@"; do observe mutation "$name" "$WORK/m/$skill" "$t"; done
}
ST=test_assure.StageTests
mutate "origin shape is not checked" requirements-decomposition check_graph.py \
  '        if (not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS' \
  '        if False and (not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS' \
  test_check_graph.StageAndOriginTests.test_a_malformed_origin_is_rejected_under_s_00
mutate "the gate refuses an origin" verified-delivery assure.py \
  '        entries = node.get("acceptance") if isinstance(node, dict) else None' \
  '        if isinstance(node, dict) and "origin" in node: raise InputError("origin")
        entries = node.get("acceptance") if isinstance(node, dict) else None' \
  $ST.test_a_requirement_with_an_instruction_origin_is_decided_as_without_one
mutate "the card always shows before deploy" verified-delivery assure.py \
  'if post_deploy_criteria(document) else None' 'if True else None' \
  test_card.StageCardTests.test_a_graph_without_post_deploy_criteria_has_no_line_before_deploy
mutate "a failed post-deploy check left out" verified-delivery assure.py \
  'elif status == "not_run" and criterion in deferrable:' 'elif criterion in deferrable:' \
  $ST.test_before_deploy_a_failed_blocked_or_missing_post_deploy_check_is_not_left_out
mutate "nothing verified before deploy passes" verified-delivery assure.py \
  'deferred = set(left_out)' 'deferred = set()' \
  $ST.test_before_deploy_a_parent_whose_own_checks_are_all_post_deploy_is_blocked \
  $ST.test_before_deploy_a_requirement_whose_checks_are_all_post_deploy_is_blocked
mutate "passed post-deploy checks unverified" verified-delivery assure.py \
  'deferred = set(left_out)' 'deferred = post_deploy_criteria(document)' \
  $ST.test_after_deploy_such_requirements_pass_once_their_checks_pass
mutate "acceptance leaves checks out too" verified-delivery assure.py \
  'deferrable = post_deploy_criteria(document) if stage == "pre_deploy" else set()' 'deferrable = post_deploy_criteria(document)' \
  $ST.test_acceptance_still_counts_the_post_deploy_check
mutate "every criterion is post-deploy" verified-delivery assure.py \
  'if entry.get("stage") == "post_deploy"}' '}' \
  $ST.test_before_deploy_a_criterion_without_a_stage_is_not_left_out
mutate "the post_deploy stage is refused" verified-delivery assure.py \
  'CRITERION_STAGES = ("pre_deploy", "post_deploy")' 'CRITERION_STAGES = ("pre_deploy",)' \
  $ST.test_a_passed_post_deploy_check_passes_at_both_stages
mutate "an undefined stage is accepted" verified-delivery assure.py \
  'if "stage" in entry and entry["stage"] not in CRITERION_STAGES:' 'if False:' \
  $ST.test_an_undefined_stage_in_the_graph_or_the_option_is_an_input_error
mutate "a Jest file that failed is ignored" verified-delivery assure.py \
  'all(outcome == "passed" for outcome in outcomes) and not incomplete:' 'all(outcome == "passed" for outcome in outcomes):' \
  test_assure.JestTests.test_a_file_that_failed_outside_its_tests_lets_nothing_pass
mutate "an id inside a dotted id counts" verified-delivery assure.py \
  '(?![A-Za-z0-9_.-])' '(?![A-Za-z0-9_-])' \
  test_assure.JestTests.test_an_id_inside_a_dotted_longer_id_does_not_count
mutate "an OR parent is not a parent" verified-delivery assure.py \
  'if kind in ("AND", "OR") and not any(level in PARENT_LEVELS for level in verified):' \
  'if kind in ("AND",) and not any(level in PARENT_LEVELS for level in verified):' \
  $ST.test_before_deploy_an_or_parent_whose_own_checks_are_all_post_deploy_is_blocked

# Every new test must be covered.
all="$( { new_tests "$REPO/.claude/skills/requirements-decomposition" $RD_CLASSES; \
          new_tests "$REPO/.claude/skills/verified-delivery" $VD_MAIN_CLASSES $VD_STUB_CLASSES; \
          echo tests/assert_delivery_flow.py; } | sort -u)"
uncovered="$(printf '%s\n' "$all" | grep -vxF -f "$COVERED")"
total="$(printf '%s\n' "$all" | grep -c .)"
echo "coverage: $((total - $(printf '%s' "$uncovered" | grep -c .))) of $total new tests fail on an assertion in a red or a mutation"
[ -n "$uncovered" ] && { printf 'not covered: %s\n' $uncovered; bad=1; }
echo "result: $([ "$bad" -eq 0 ] && echo 'every observation as expected' || echo 'some observation NOT as expected')"
exit "$bad"
