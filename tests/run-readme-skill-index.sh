#!/usr/bin/env bash
# Every skill directory under harness/skills/ and every subagent definition
# under harness/agents/ must be named in both READMEs. The READMEs list them
# by hand, so one added without a README entry used to go unnoticed.
#
# A name counts as named when it appears as `<name>` or as a <name>/ path
# segment. A bare substring is not enough: a skill can share a word with a
# rule file or with another skill.
#
# Usage: bash tests/run-readme-skill-index.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/harness/skills"
AGENT_DIR="$REPO_ROOT/harness/agents"

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
done < <(find "$SKILL_DIR" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -exec dirname {} \; | xargs -n 1 basename | sort)

agents=()
while IFS= read -r agent; do
  agents+=("$agent")
done < <(find "$AGENT_DIR" -mindepth 1 -maxdepth 1 -type f -name '*.md' -exec basename {} .md \; | sort)

[ "${#skills[@]}" -gt 0 ] && c=1 || c=0
check "IDX-00: harness/skills/ has at least one skill directory" "$c"
[ "${#agents[@]}" -gt 0 ] && c=1 || c=0
check "IDX-01: harness/agents/ has at least one subagent definition" "$c"

for name in "${skills[@]}" "${agents[@]}"; do
  pattern="(\`${name}\`|(^|[^[:alnum:]_-])${name}/)"
  for readme in README.md README.ja.md; do
    grep -Eq -- "$pattern" "$REPO_ROOT/$readme" && c=1 || c=0
    check "IDX: $readme names $name" "$c"
  done
done

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
