#!/usr/bin/env bash
# R0-A4: prints what the two checkers under SKILLS_DIR decide on every record
# that main (9cd7932) tracked, so the output for main and for the change can be
# compared with diff. Usage: compat.sh SKILLS_DIR (a directory holding
# requirements-decomposition/ and verified-delivery/). Reads only.

set -uo pipefail
SKILLS="$1"
BASE=9cd7932
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CG="$SKILLS/requirements-decomposition/scripts/check_graph.py"
AS="$SKILLS/verified-delivery/scripts/assure.py"
export PYTHONDONTWRITEBYTECODE=1
cd "$REPO" || exit 2

summary() {
  python3 -I -c '
import json, sys
try:
    d = json.load(sys.stdin)
except ValueError:
    print("unparsable output"); sys.exit()
keep = {k: d.get(k) for k in ("status", "decision", "challenge", "error")}
keep["violations"] = [(v.get("rule_id"), v.get("node_id"), v.get("message")) for v in d.get("violations", [])]
keep["reasons"] = [(r.get("rule_id"), r.get("effect"), r.get("message")) for r in d.get("reasons", [])]
print(json.dumps(keep, ensure_ascii=False, sort_keys=True))'
}

# Every graph, card, and report main tracked, outside the gate fixtures (which
# hold a card, a graph, and a report each and are read together below).
inputs="$(git ls-tree -r --name-only "$BASE" -- specs .claude/skills/requirements-decomposition/tests/fixtures \
  .claude/skills/requirements-decomposition/examples | grep -E '\.json$' | grep -v '/fixtures/gate/' | grep -E 'graph|requirements/|skills/|card|report')"
for f in $inputs; do
  out="$(python3 -B "$CG" --format json "$f")"; code=$?
  printf '%s exit=%s %s\n' "$f" "$code" "$(printf '%s' "$out" | summary)"
done

S=specs/066-harness-behavior-baseline
out="$(python3 -B "$AS" --format json gate "$S/requirements-graph.json" "$S/verification-manifest.json" --report "$S/challenge-report.json" --review "$S/assurance-review-10.f9dbf00.json")"; code=$?
printf 'gate %s exit=%s %s\n' "$S" "$code" "$(printf '%s' "$out" | summary)"
E=.claude/skills/verified-delivery/examples
out="$(python3 -B "$AS" --format json gate "$E/requirements-graph.example.json" "$E/verification-manifest.example.json")"; code=$?
printf 'gate %s exit=%s %s\n' "$E" "$code" "$(printf '%s' "$out" | summary)"

# R4c: a card for a graph without post-deploy criteria is the same text.
for lang in en ja; do
  printf '== card %s %s\n' "$S" "$lang"
  python3 -B "$AS" card --problem "$S/problem-card.json" --graph "$S/requirements-graph.json" --manifest "$S/verification-manifest.json" \
    --report "$S/challenge-report.json" --review "$S/assurance-review-10.f9dbf00.json" --lang "$lang"
  printf '== exit=%s\n' "$?"
  printf '== card %s %s\n' "$E" "$lang"
  python3 -B "$AS" card --problem "$E/problem-card.example.json" --graph "$E/requirements-graph.example.json" \
    --manifest "$E/verification-manifest.example.json" --lang "$lang"
  printf '== exit=%s\n' "$?"
done
