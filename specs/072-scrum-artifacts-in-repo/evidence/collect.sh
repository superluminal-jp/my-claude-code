#!/usr/bin/env bash
# Collect the evidence of specs/072 for the commit that is checked out.
# Usage: bash specs/072-scrum-artifacts-in-repo/evidence/collect.sh <reviewed commit, full SHA>
# Writes text files to specs/072-scrum-artifacts-in-repo/evidence/<short SHA>/.
# The working tree must be that commit plus, at most, files of the record directory.
set -uo pipefail
C="${1:?reviewed commit}"
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
: "${TMPDIR:?TMPDIR must be set}"
BASE=2fab98d
S=harness/skills/manage-scrum-artifacts
OLD=harness/skills/apply-scrum-guide/references/templates
E="specs/072-scrum-artifacts-in-repo/evidence/${C:0:7}"
mkdir -p "$E"
if ! git diff --quiet "$C" -- . ':!specs/072-scrum-artifacts-in-repo'; then
  echo "collect: the working tree differs from $C outside the record directory" >&2; exit 2
fi
hdr() { echo "commit: $C"; echo "date: $(date -u +%Y-%m-%dT%H:%MZ)"; echo; }
show() { echo "\$ $*"; "$@" 2>&1; echo "exit: $?"; echo; }

{ hdr; show bash tests/run-harness-skills.sh; } > "$E/harness-skills.txt"
{ hdr; show python3 -B -m unittest discover -s "$S/tests" -t "$S/tests" -v; } > "$E/acceptance-tests.txt"
{ hdr; show bash specs/072-scrum-artifacts-in-repo/evidence/dryrun.sh; } > "$E/dryrun-transcript.txt"
{ hdr
  for t in run-readme-skill-index run-config-pyramid run-harness-eval run-install; do
    echo "\$ bash tests/$t.sh   (lines that name the two Scrum skills, ROUTE-07/08, results, and any FAIL)"
    bash "tests/$t.sh" > "$TMPDIR/collect-out.txt" 2>&1; rc=$?
    grep -E "manage-scrum-artifacts|apply-scrum-guide|ROUTE-0[78]|Results|Result:|harness-eval:|^Ran |^OK|FAIL" "$TMPDIR/collect-out.txt"
    echo "exit: $rc"; echo
  done
  show python3 tests/harness-eval/harness_eval.py check
  show grep -n "manage-scrum-artifacts" tests/harness-eval/scenarios.json docs/harness/capability-map.json
} > "$E/suites.txt"
{ hdr
  show find harness -name product-backlog.md
  show test -e "$OLD"
  show git -c core.quotepath=false diff -M --summary "$BASE" "$C" -- "$OLD" "$S/templates"
  echo "\$ for each of the 8 templates: git show $BASE:$OLD/<name> | cmp -s - $S/templates/<name>"
  for f in product-backlog.md definition-of-done.md sprint/daily-scrum.md sprint/increment.md sprint/sprint-backlog.md \
           sprint/sprint-planning.md sprint/sprint-retrospective.md sprint/sprint-review.md; do
    git show "$BASE:$OLD/$f" | cmp -s - "$S/templates/$f"; echo "$f cmp exit: $?"
  done
} > "$E/templates.txt"
{ hdr
  show grep -n "17 in all\|17 skills\|PDFs bundled\|rebuilt as" README.md
  show grep -n "全部で17件\|。17件\|PDF を同梱する\|件に作り直した" README.ja.md
  echo "# the old counts and the old claim that templates are bundled with the diagnosis skill must be gone (exit 1 = no match)"
  show grep -n "16 in all\|16 skills\|全部で16件\|。16件\|these\$\|この16件\|eight\|8つの Markdown\|テンプレート8件" README.md README.ja.md
  show grep -c 'SKILL.md`（17件）' docs/claude-config-design.md
  show head -7 docs/adr/0023-keep-scrum-artifacts-in-the-product-repository.md
} > "$E/docs.txt"
{ hdr
  show git diff "$BASE" "$C" -- harness/skills/apply-scrum-guide/SKILL.md
  show sed -n 1,9p harness/skills/apply-scrum-guide/SKILL.md
  show sed -n 1,10p "$S/SKILL.md"
} > "$E/compat.txt"
sed -i "s#$TMPDIR#\$TMPDIR#g" "$E"/*.txt
grep -H "^exit: " "$E"/*.txt
