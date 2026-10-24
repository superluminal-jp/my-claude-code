#!/usr/bin/env bash
# Every skill directory under .claude/skills/ must be named in both READMEs.
# The READMEs list skills by hand, so a skill added without a README entry
# used to go unnoticed (apple-notes and apple-reminders were missing from
# both). speckit-* directories are excluded: `specify init` generates them
# per project and they are gitignored.
#
# A skill counts as named when it appears as `<name>` or as a <name>/ path
# segment. A bare substring is not enough: the clarifier skill shares its
# name with the rule file clarifier.md.
#
# Usage: bash tests/run-readme-skill-index.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills"

PASS=0
FAIL=0

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL %s\n' "$name" >&2
  fi
}

skills=()
while IFS= read -r skill; do
  skills+=("$skill")
done < <(find "$SKILL_DIR" -mindepth 1 -maxdepth 1 -type d ! -name 'speckit-*' -exec basename {} \; | sort)

[ "${#skills[@]}" -gt 0 ] && c=1 || c=0
check "IDX-00: .claude/skills/ has at least one skill directory" "$c"

for skill in "${skills[@]}"; do
  pattern="(\`${skill}\`|(^|[^[:alnum:]_-])${skill}/)"
  for readme in README.md README.ja.md; do
    grep -Eq -- "$pattern" "$REPO_ROOT/$readme" && c=1 || c=0
    check "IDX: $readme names skill $skill" "$c"
  done
done

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
