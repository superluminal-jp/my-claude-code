#!/usr/bin/env bash
# Offline structural contracts for the independent Claude configuration pyramid.
# Literal backticks are intentional regular-expression delimiters.
# shellcheck disable=SC2016

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APEX="$REPO_ROOT/.claude/CLAUDE.md"
RULE_DIR="$REPO_ROOT/.claude/rules"
SKILL_DIR="$REPO_ROOT/.claude/skills"
BASELINE_BYTES=20126

PASS=0
FAIL=0
FAIL_NAMES=""

check() {
  local name="$1" condition="$2"
  if [ "$condition" = "1" ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf 'FAIL %s\n' "$name" >&2
  fi
}

contains() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && grep -Eiq -- "$pattern" "$file"
}

check_contains() {
  local name="$1" file="$2" pattern="$3"
  check "$name" "$(contains "$file" "$pattern" && echo 1 || echo 0)"
}

check_absent_pattern() {
  local name="$1" pattern="$2"
  shift 2
  check "$name" "$(! grep -Eirq --exclude-dir=dads-docs -- "$pattern" "$@" && echo 1 || echo 0)"
}

authored_skills=(
  adr
  clarifier
  cloud-platform-research
  coder
  digital-agency-frontend
  git-workflow
  minto-builder
  minto-reviewer
  minto-rewriter
  problem-definition
  product-strategy
  scrum-master
)

run_apex_contract() {
  check_contains "APEX-01: one governing outcome" "$APEX" 'trusted|trustworthy|信頼'
  check_contains "APEX-02: definition branch" "$APEX" '^## .*Define|^## .*定義'
  check_contains "APEX-03: execution branch" "$APEX" '^## .*Execute|^## .*実行'
  check_contains "APEX-04: handoff branch" "$APEX" '^## .*Hand off|^## .*引き渡'
  check_contains "APEX-05: evaluates every capability description" "$APEX" '(every|all).*(capabilit|description|適合)'
  check_contains "APEX-06: orders compound matches by dependency" "$APEX" '(dependency|prerequisite|依存).*(order|before|順)'
  check_absent_pattern "APEX-07: no lower configuration or command reference" \
    '(\.claude/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' "$APEX"
  check_absent_pattern "APEX-08: no environment-specific server registry" \
    '(aws-documentation|aws-knowledge|bedrock-agentcore|strands-agents|google-developer-knowledge|microsoft-learn)' "$APEX"
}

run_rule_contract() {
  local actual expected
  expected="clarifier.md
live-documentation.md
permissions.md
pyramid-principle.md
thinking-lenses.md"
  actual="$(find "$RULE_DIR" -maxdepth 1 -type f -name '*.md' -exec basename {} \; | sort)"
  check "RULE-01: exactly five universal rule files" "$([ "$actual" = "$expected" ] && echo 1 || echo 0)"

  check_absent_pattern "RULE-02: no config path or slash-command dependency" \
    '(\.claude/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' "$RULE_DIR"
  check_absent_pattern "RULE-03: no named authored-skill routing" \
    '(`|/)(adr|clarifier|cloud-platform-research|coder|digital-agency-frontend|git-workflow|minto-builder|minto-reviewer|minto-rewriter|problem-definition|product-strategy|scrum-master)(`|[^[:alnum:]_-])' "$RULE_DIR"

  local source target target_name failed=0
  for source in "$RULE_DIR"/*.md; do
    for target in "$RULE_DIR"/*.md; do
      [ "$source" = "$target" ] && continue
      target_name="$(basename "$target")"
      if grep -Fq -- "$target_name" "$source"; then
        printf '    %s names sibling %s\n' "$source" "$target_name" >&2
        failed=1
      fi
    done
  done
  check "RULE-04: no pairwise sibling filename reference" "$([ "$failed" -eq 0 ] && echo 1 || echo 0)"

  check_contains "RULE-05: clarification owns material outcome gaps" "$RULE_DIR/clarifier.md" 'material|outcome|result|結果'
  check_contains "RULE-06: reasoning owns inference" "$RULE_DIR/thinking-lenses.md" 'deduct|induct|演繹|帰納'
  check_contains "RULE-07: permission owns external effects" "$RULE_DIR/permissions.md" 'external|remote|外部'
  check_contains "RULE-08: presentation owns sibling grouping" "$RULE_DIR/pyramid-principle.md" 'siblings|group|MECE|同列'
  check_contains "RULE-09: documentation owns canonical contracts" "$RULE_DIR/live-documentation.md" 'canonical|source of truth|正本'

  check "RULE-10: legacy conditional and routing rules are absent" \
    "$([ ! -e "$RULE_DIR/git-workflow.md" ] && [ ! -e "$RULE_DIR/mcp.md" ] && [ ! -e "$RULE_DIR/skill-routing.md" ] && echo 1 || echo 0)"
}

run_skill_contract() {
  local skill skill_file description
  local missing=0 bad_metadata=0 bad_description=0
  for skill in "${authored_skills[@]}"; do
    skill_file="$SKILL_DIR/$skill/SKILL.md"
    if [ ! -f "$skill_file" ]; then
      printf '    missing %s\n' "$skill_file" >&2
      missing=1
      continue
    fi
    grep -q '^when_to_use:' "$skill_file" && bad_metadata=1
    description="$(grep -m1 '^description:' "$skill_file")"
    if [ -z "$description" ] || ! printf '%s\n' "$description" | grep -Eiq '(Do not use|does not apply|exclude|not for|out of scope|対象外|使わない)'; then
      printf '    description lacks an exclusion boundary: %s\n' "$skill" >&2
      bad_description=1
    fi
  done
  check "SKILL-01: all authored skill entry points exist" "$([ "$missing" -eq 0 ] && echo 1 || echo 0)"
  check "SKILL-02: standard description is the only trigger metadata" "$([ "$bad_metadata" -eq 0 ] && echo 1 || echo 0)"
  check "SKILL-03: every authored description states an exclusion boundary" "$([ "$bad_description" -eq 0 ] && echo 1 || echo 0)"

  check_absent_pattern "SKILL-04: no entry point depends on config paths" \
    '(\.claude/(CLAUDE\.md|rules|skills)|\.agents/skills|rules/[[:alnum:]_-]+\.md)' "$SKILL_DIR"/*/SKILL.md

  local source target file failed=0
  for source in "${authored_skills[@]}"; do
    [ -d "$SKILL_DIR/$source" ] || continue
    for target in "${authored_skills[@]}"; do
      [ "$source" = "$target" ] && continue
      while IFS= read -r file; do
        pattern='(`|/|skills/)'"${target}"'(`|/|[^[:alnum:]_-])'
        if grep -Eiq -- "$pattern" "$file"; then
          printf '    %s names sibling package %s\n' "$file" "$target" >&2
          failed=1
        fi
      done < <(find "$SKILL_DIR/$source" -type f -name '*.md' ! -path '*/references/dads-docs/*')
    done
  done
  check "SKILL-05: authored packages do not name siblings" "$([ "$failed" -eq 0 ] && echo 1 || echo 0)"

  check_absent_pattern "SKILL-06: packages do not hard-code their install root" \
    '\.claude/skills/(adr|clarifier|cloud-platform-research|coder|digital-agency-frontend|git-workflow|minto-builder|minto-reviewer|minto-rewriter|problem-definition|product-strategy|scrum-master)' \
    "$SKILL_DIR/adr" "$SKILL_DIR/clarifier" "$SKILL_DIR/cloud-platform-research" "$SKILL_DIR/coder" \
    "$SKILL_DIR/digital-agency-frontend" "$SKILL_DIR/git-workflow" "$SKILL_DIR/minto-builder" \
    "$SKILL_DIR/minto-reviewer" "$SKILL_DIR/minto-rewriter" "$SKILL_DIR/problem-definition" \
    "$SKILL_DIR/product-strategy" "$SKILL_DIR/scrum-master"
}

run_routing_fixtures() {
  check_contains "ROUTE-01: code-only selects implementation" "$SKILL_DIR/coder/SKILL.md" '^description:.*(code|configuration|observable behavior)'
  check_contains "ROUTE-02: bare document creation selects incomplete-material operation" "$SKILL_DIR/minto-builder/SKILL.md" '^description:.*(document|artifact).*(incomplete|from scratch)'
  check_contains "ROUTE-03: substantive docs can compose with implementation" "$SKILL_DIR/minto-rewriter/SKILL.md" '^description:.*(alongside|compound|independent|implementation)'
  check_contains "ROUTE-04: diagnosis plus rewrite preserves a diagnosis phase" "$SKILL_DIR/minto-reviewer/SKILL.md" '^description:.*(phase|deliverable|rewrite|transform)'
  check_contains "ROUTE-05: DADS remains an independently matching domain overlay" "$SKILL_DIR/digital-agency-frontend/SKILL.md" '^description:.*(overlay|independent|alongside|also applies)'
  check_contains "ROUTE-06: formal requirements can precede DADS implementation" "$SKILL_DIR/clarifier/SKILL.md" '^description:.*(before|prerequisite|independent|compound)'
  check_contains "ROUTE-07: Scrum artifacts retain domain judgement" "$SKILL_DIR/scrum-master/SKILL.md" '^description:.*(artifact|成果物|資料).*(independent|別|併用|適用)'
  check_contains "ROUTE-08: generic PM status and Gantt work is not Scrum" "$SKILL_DIR/scrum-master/SKILL.md" '^description:.*(Gantt|status|project management).*(not|対象外|使わない)'
  check_contains "ROUTE-09: product strategy precedes development, distinct from scope/facilitation/generic docs" "$SKILL_DIR/product-strategy/SKILL.md" '^description:.*(戦略|strategy).*(対象外|使わない|out of scope|not for)'
  check_contains "ROUTE-10: problem definition stays gap-framing, distinct from cause analysis/solutions/scope clarification" "$SKILL_DIR/problem-definition/SKILL.md" '^description:.*(problem|問題).*(out of scope|not for|対象外|使わない)'
}

run_owned_link_contract() {
  local skill file link resolved failed=0
  for skill in "${authored_skills[@]}"; do
    [ -d "$SKILL_DIR/$skill" ] || continue
    while IFS= read -r file; do
      while IFS= read -r link; do
        link="${link%%#*}"
        [ -z "$link" ] && continue
        case "$link" in
          http://* | https://* | mailto:* | \$*) continue ;;
        esac
        resolved="$(dirname "$file")/$link"
        if [ ! -e "$resolved" ]; then
          printf '    unresolved link %s in %s\n' "$link" "$file" >&2
          failed=1
        fi
      done < <(
        awk '/^```/{code = !code; next} !code{print}' "$file" |
          grep -oE '\]\([^)]+' |
          sed 's/^](//' || true
      )
    done < <(find "$SKILL_DIR/$skill" -type f -name '*.md' ! -path '*/references/dads-docs/*')
  done
  check "LINK-01: authored package-relative Markdown links resolve" "$([ "$failed" -eq 0 ] && echo 1 || echo 0)"
}

run_budget_contract() {
  local bytes
  bytes="$(wc -c "$APEX" "$RULE_DIR"/*.md | tail -n 1 | awk '{print $1}')"
  check "BUDGET-01: unconditional corpus is smaller than legacy baseline" "$([ "$bytes" -lt "$BASELINE_BYTES" ] && echo 1 || echo 0)"
}

run_apex_contract
run_rule_contract
run_skill_contract
run_routing_fixtures
run_owned_link_contract
run_budget_contract

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  printf 'Failed:%b\n' "$FAIL_NAMES" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
