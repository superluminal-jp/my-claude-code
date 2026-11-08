#!/usr/bin/env bash
# Shows, test by test, that every test spec 069 added can fail on its
# assertion: each new unittest test, and each check of
# tests/assert_review_prep_flow.py, is run alone against a copy of
# scripts/review_prep.py broken on purpose (a mutation), in a temporary
# directory; the repository is only read. A test is covered when it FAILs (an
# assertion) under at least one mutation; an ERROR never counts.
# Usage: mutations.sh. Exit 0 when every new test is covered and nothing ERRORs.

set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILL="$REPO/.claude/skills/verified-delivery"
export PYTHONDONTWRITEBYTECODE=1
WORK="$(mktemp -d "${TMPDIR:-/tmp}/spec069-mut.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
bad=0
COVERED="$WORK/covered"
: > "$COVERED"
T=test_review_prep

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

mutate() {  # mutate NAME OLD NEW TEST... (a TEST of the form flow:<check> runs the flow check)
  local name="$1" old="$2" new="$3" t got out line check; shift 3
  rm -rf "$WORK/m"; mkdir -p "$WORK/m/.claude/skills"
  cp -R "$SKILL" "$WORK/m/.claude/skills/"
  replace_once "$WORK/m/.claude/skills/verified-delivery/scripts/review_prep.py" "$old" "$new" || { bad=1; return; }
  for t in "$@"; do
    if [ "${t#flow:}" != "$t" ]; then
      out="$(python3 -B "$REPO/tests/assert_review_prep_flow.py" "$WORK/m" 2>&1)"
      check="${t#flow:}"
      if printf '%s' "$out" | grep -q Traceback; then got=ERROR
      elif printf '%s\n' "$out" | grep -qF "FAIL $check"; then got=FAIL
      else got=PASS; fi
    else
      got="$(outcome "$WORK/m/.claude/skills/verified-delivery" "$T.$t")"
    fi
    printf '%-8s %-40s %-5s %s\n' mutation "$name" "$got" "$t"
    [ "$got" = FAIL ] && echo "$t" >> "$COVERED"
    [ "$got" = ERROR ] && bad=1
  done
}

mutate "check always finds a violation" 'return violations
' 'return violations + [("P-00", "x", "mutation")]
' CheckTests.test_records_that_follow_the_procedure_have_no_violation \
  "flow:check before the first round finds no record error"
mutate "commits after the review are not checked" 'if not is_record(path, records):' 'if False:' \
  CheckTests.test_a_change_outside_the_record_directory_after_the_reviewed_commit_is_a_violation \
  "flow:check finds a code change committed after the reviewed commit"
mutate "evidence files are not checked" 'for ref in [f"{records}/{MANIFEST}"] + repository_refs(body):' 'for ref in []:' \
  CheckTests.test_missing_untracked_or_ignored_evidence_is_a_violation
mutate "a bad reviewed_commit is not P-01" '("P-01", body["reviewed_commit"]' '("P-09", body["reviewed_commit"]' \
  CheckTests.test_a_reviewed_commit_that_is_no_commit_or_not_behind_head_is_a_violation
mutate "URL evidence is opened" 'and not URL.match(ref) and ref not in refs' 'and ref not in refs' \
  CheckTests.test_url_evidence_is_not_opened
mutate "record data files stay in the diff" 'excluded = [f":(exclude,glob){records}/**/*{suffix}" for suffix in RECORD_SUFFIXES]' 'excluded = []' \
  BundleTests.test_the_first_round_bundle_holds_the_change_and_not_the_records \
  "flow:the first round's bundle holds the code change and no record file"
mutate "scripts of the record directory are left out" 'excluded = [f":(exclude,glob){records}/**/*{suffix}" for suffix in RECORD_SUFFIXES]' 'excluded = [f":(exclude){records}"]' \
  BundleTests.test_the_first_round_bundle_holds_the_change_and_not_the_records
mutate "any record-directory file counts as a record" 'and Path(path).suffix.lower() in RECORD_SUFFIXES' '' \
  CheckTests.test_a_script_in_the_record_directory_changed_after_the_review_is_a_violation
mutate "renames hide a file moved into the records" '"--name-only", "--no-renames", reviewed, "HEAD"' '"--name-only", reviewed, "HEAD"' \
  CheckTests.test_a_file_moved_into_the_record_directory_after_the_review_is_a_violation
mutate "selection conditions count as structure" 'node["selection"] = sorted(node["selection"])' 'node["selection"] = node["selection"]' \
  ScopeTests.test_a_change_to_a_selection_condition_only_is_a_fix_round
mutate "--out inside the repository is accepted" 'if out == repo.root or repo.root in out.parents:' 'if False:' \
  BundleTests.test_an_out_directory_inside_the_repository_or_not_empty_is_refused
mutate "the previous review is not copied" 'shutil.copyfile(previous_review, out / "previous-review.json")' \
  '(out / "previous-review.json").write_text("{}", encoding="utf-8")' \
  BundleTests.test_the_previous_review_is_copied_into_the_bundle
mutate "text fields count as structure" 'TEXT_FIELDS = ("statement", "assumptions", "counterexamples")' 'TEXT_FIELDS = ()' \
  ScopeTests.test_a_change_to_text_fields_only_is_a_fix_round_from_the_previous_commit \
  "flow:a fix that changes only the graph's text is a fix round from the previous reviewed commit"
mutate "structure changes are not seen" '    if a == b:
        return []' '    if True:
        return []' ScopeTests.test_a_structural_change_makes_a_whole_round_from_the_base \
  "flow:a fix that adds an acceptance criterion is a whole round from the base"
mutate "a risk change is not seen" '        if old != new:' '        if False:' \
  ScopeTests.test_a_changed_problem_card_or_risk_class_makes_a_whole_round
mutate "a missing previous manifest is not a reason" \
  'reasons.append("no committed manifest names the previous reviewed commit, so its risk class is unknown")' 'pass' \
  ScopeTests.test_a_previous_round_without_records_makes_a_whole_round

mutate "requirement records may change after the review" '            if path in requirement_records:' '            if False:' \
  CheckTests.test_a_requirement_record_changed_after_the_review_is_a_violation
mutate "only-staged evidence counts as untracked" '            return "is staged but not committed"' '            return "is not tracked"' \
  CheckTests.test_evidence_that_is_only_staged_or_differs_from_its_commit_is_a_violation
mutate "a changed working copy is not seen" 'if not target.is_file() or repo.git("diff", "--quiet", "HEAD", "--", ref, ok=(0, 1)).returncode != 0:' 'if not target.is_file():' \
  CheckTests.test_evidence_that_is_only_staged_or_differs_from_its_commit_is_a_violation
mutate "every reference counts as plain" '    return not ref.startswith("/") and "\\" not in ref' '    return True or not ref.startswith("/") and "\\" not in ref' \
  CheckTests.test_a_reference_that_climbs_out_with_dot_dot_is_a_violation
mutate "the bundle copies the working tree" 'content = repo.show_bytes("HEAD", ref) if is_plain(ref) else None' \
  'content = (repo.root / ref).read_bytes() if (repo.root / ref).is_file() else None' \
  BundleTests.test_the_bundle_copies_the_committed_records_and_writes_only_under_out

all="$( { (cd "$SKILL/tests" && python3 -B -c '
import unittest, test_review_prep as m
for cls in ("CheckTests", "BundleTests", "ScopeTests"):
    for name in unittest.defaultTestLoader.getTestCaseNames(getattr(m, cls)):
        print(f"{cls}.{name}")'); \
        python3 -B "$REPO/tests/assert_review_prep_flow.py" "$REPO" | sed -nE 's/^ok   (.*)$/flow:\1/p'; } | sort -u)"
uncovered="$(printf '%s\n' "$all" | grep -vxF -f "$COVERED")"
total="$(printf '%s\n' "$all" | grep -c .)"
echo "coverage: $((total - $(printf '%s' "$uncovered" | grep -c .))) of $total new tests fail on an assertion under a mutation"
[ -n "$uncovered" ] && { printf 'not covered: %s\n' "$uncovered"; bad=1; }
echo "result: $([ "$bad" -eq 0 ] && echo 'every observation as expected' || echo 'some observation NOT as expected')"
exit "$bad"
