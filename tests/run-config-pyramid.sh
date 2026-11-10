#!/usr/bin/env bash
# Offline structural contracts for the always-loaded layers of the harness:
# the apex (harness/CLAUDE.md), the four rules (harness/rules/), the routing
# boundaries the skill descriptions state, and the size of what loads in
# every session. The skills' own contract (names, metadata, sandbox rules,
# sibling references, links, parent and child declarations) is checked by
# tests/assert_skill_contract.py, which tests/run-harness-skills.sh runs.
# Literal backticks are intentional regular-expression delimiters.
# shellcheck disable=SC2016

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APEX="$REPO_ROOT/harness/CLAUDE.md"
RULE_DIR="$REPO_ROOT/harness/rules"
SKILL_DIR="$REPO_ROOT/harness/skills"
# The size, in bytes, that the apex and the rules together must stay under.
# 16,000 is the target set when the always-loaded text was last minimized;
# the earlier limit of 20,126 was the size before that work and could not
# detect regrowth.
BUDGET_BYTES=16000

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
  check "$name" "$(! grep -Eirq -- "$pattern" "$@" && echo 1 || echo 0)"
}

# The skill names, joined for a regular expression. Read from the directory,
# so a skill added or renamed needs no edit here.
skill_names="$(find "$SKILL_DIR" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort | paste -sd '|' -)"

run_apex_contract() {
  check_contains "APEX-01: one governing outcome" "$APEX" 'trusted|trustworthy|信頼'
  check_contains "APEX-02: definition branch" "$APEX" '^## .*Define|^## .*定義'
  check_contains "APEX-03: execution branch" "$APEX" '^## .*Execute|^## .*実行'
  check_contains "APEX-04: handoff branch" "$APEX" '^## .*Hand off|^## .*引き渡'
  check_contains "APEX-05: evaluates every capability description" "$APEX" '(every|all).*(capabilit|description|適合)'
  check_contains "APEX-06: orders compound matches by dependency" "$APEX" '(dependency|prerequisite|依存).*(order|before|順)'
  check_absent_pattern "APEX-07: no lower configuration or command reference" \
    '(\.claude/|harness/|rules/|skills/|agents/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' "$APEX"
  check_absent_pattern "APEX-08: no environment-specific server registry" \
    '(aws-documentation|aws-knowledge|bedrock-agentcore|strands-agents|google-developer-knowledge|microsoft-learn)' "$APEX"
  check_contains "APEX-09: delegates under three conditions, without waiting for the user" "$APEX" \
    'without waiting for the user to ask.*subagent.*one of three conditions'
  check_contains "APEX-10: keeps the judgment that the work is complete on the main conversation's model" "$APEX" \
    "judgment that the work is complete on the main conversation's model"
  check_contains "APEX-11: leaves model, effort, and tools to the subagent type defined for the work" "$APEX" \
    'subagent type defined for that kind of work.*model, effort, and tools'
  check_absent_pattern "APEX-12: names no model and no subagent or skill" \
    '(`haiku`|`sonnet`|`opus`|`fable`|read-only-reviewer|check-runner|file-searcher|task-worker|(^|[^[:alnum:]_-])('"$skill_names"')([^[:alnum:]_-]|$))' "$APEX"
  check_contains "APEX-13: states what each level of risk needs" "$APEX" \
    "failing check and a passing run.*evidence for each acceptance criterion.*independent review.*person's approval"
}

run_rule_contract() {
  local actual expected
  expected="clarifier.md
permissions.md
pyramid-principle.md
thinking-lenses.md"
  actual="$(find "$RULE_DIR" -maxdepth 1 -type f -name '*.md' -exec basename {} \; | sort)"
  check "RULE-01: exactly four universal rule files" "$([ "$actual" = "$expected" ] && echo 1 || echo 0)"

  check_absent_pattern "RULE-02: no config path or slash-command dependency" \
    '(\.claude/|harness/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' "$RULE_DIR"
  check_absent_pattern "RULE-03: no named skill routing" \
    '(`|/)('"$skill_names"')(`|[^[:alnum:]_-])' "$RULE_DIR"

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

  check "RULE-10: legacy conditional and routing rules are absent" \
    "$([ ! -e "$RULE_DIR/git-workflow.md" ] && [ ! -e "$RULE_DIR/mcp.md" ] && [ ! -e "$RULE_DIR/skill-routing.md" ] && echo 1 || echo 0)"

  check_contains "RULE-12: presentation defines terms for a newcomer" "$RULE_DIR/pyramid-principle.md" 'newcomer.*(term|defin)|(term|defin).*newcomer'
  check_contains "RULE-13: presentation forbids explaining by metaphor or analogy" "$RULE_DIR/pyramid-principle.md" '[Nn]ever explain by (metaphor|analogy)'
  check_contains "RULE-14: presentation orders the parts of a research paper, answer first" "$RULE_DIR/pyramid-principle.md" 'summary.*premises.*method.*results.*discussion.*conclusion'
  check_contains "RULE-15: presentation opens each paragraph with its claim" "$RULE_DIR/pyramid-principle.md" 'paragraph.*first sentence|first sentence.*paragraph'
  check_contains "RULE-16: presentation makes each supporting claim visible" "$RULE_DIR/pyramid-principle.md" 'claim.*bold|bold.*claim'
  check_contains "RULE-17: presentation matches the visual form to the relation" "$RULE_DIR/pyramid-principle.md" 'numbered list.*table|table.*numbered list'
  check_contains "RULE-18: presentation takes each term's form from its field" "$RULE_DIR/pyramid-principle.md" 'term.*form.*field'
  check_contains "RULE-19: presentation never coins a translation" "$RULE_DIR/pyramid-principle.md" 'never coin a translation'
  check_contains "RULE-20: presentation assumes a reader without the conversation, code, or documents" "$RULE_DIR/pyramid-principle.md" 'seen none of the conversation, code, or documents'
  check_contains "RULE-21: presentation names the referent of a word with several referents" "$RULE_DIR/pyramid-principle.md" 'several referents.*(environment|account)'
  check_contains "RULE-22: presentation resolves pointers into unseen context" "$RULE_DIR/pyramid-principle.md" 'pointer.*option B'
  check_absent_pattern "RULE-23: presentation defines a term even when the user has used it" \
    'skip the definition only for a term the user' "$RULE_DIR/pyramid-principle.md"
  check "RULE-24: the model routing rule is retired" "$([ ! -e "$RULE_DIR/model-routing.md" ] && echo 1 || echo 0)"
  # Reference lists back a rule up; they do not change a judgment, so they
  # live in docs/claude-config-design.md, outside what loads in every session.
  check_absent_pattern "RULE-25: no reference list in an always-loaded rule" '^## References?[[:space:]]*$' "$RULE_DIR"
  check_contains "RULE-26: the design record holds the rules' reference lists" \
    "$REPO_ROOT/docs/claude-config-design.md" 'The Minto Pyramid Principle'
}

# What each description must keep saying for requests to be routed the same
# way. These are phrase checks; whether a model follows them is measured by
# tests/harness-eval.
run_routing_contract() {
  check_contains "ROUTE-01: code-only work selects implementation" "$SKILL_DIR/implement-change/SKILL.md" '^description:.*(code|configuration|observable behavior)'
  check_contains "ROUTE-02: clarification leaves requirements, problems, and product direction to others" "$SKILL_DIR/clarify-intent/SKILL.md" '^description:.*Do not use.*(problem|product direction|formal requirements)'
  check_contains "ROUTE-03: requirements exclude defining the problem and judging evidence" "$SKILL_DIR/specify-requirements/SKILL.md" '^description:.*Do not use.*define a vague problem.*test evidence'
  check_contains "ROUTE-04: the parent skill is not for a single step" "$SKILL_DIR/deliver-change/SKILL.md" '^description:.*Do not use.*only one of the four steps'
  check_contains "ROUTE-07: Scrum applies to named Scrum events, artifacts, and accountabilities" "$SKILL_DIR/apply-scrum-guide/SKILL.md" '^description:.*(イベント|作成物).*(使う)'
  check_contains "ROUTE-08: generic project management and Gantt work is not Scrum" "$SKILL_DIR/apply-scrum-guide/SKILL.md" '^description:.*(ガントチャート|プロジェクト管理).*(使わない)'
  check_contains "ROUTE-09: product strategy excludes feature scope, facilitation, and architecture" "$SKILL_DIR/define-product-strategy/SKILL.md" '^description:.*strategy.*Do not use.*(scope|Scrum|architecture)'
  check_contains "ROUTE-10: problem definition excludes cause analysis and solutions" "$SKILL_DIR/define-problem/SKILL.md" '^description:.*problem.*Do not use.*(root-cause|solutions)'
  check_contains "ROUTE-11: document structuring is not for a conversational answer" "$SKILL_DIR/structure-document/SKILL.md" '^description:.*Do not use.*conversational answer'
  check_contains "ROUTE-13: secure logging excludes log infrastructure operations" "$SKILL_DIR/apply-secure-logging/SKILL.md" '^description:.*(Do not use|not for).*(SIEM|infrastructure)'
  check_contains "ROUTE-14: system diagrams exclude diagrams built from a cloud vendor's official icon set" "$SKILL_DIR/draw-system-diagrams/SKILL.md" "^description:.*Do not use for.*official icon set"
  check_contains "ROUTE-15: DADS frontend excludes slide decks, and DADS slides exclude web pages" "$SKILL_DIR/apply-dads-frontend/SKILL.md" '^description:.*Do not use.*slide decks'
  check_contains "ROUTE-16: a document read outside the conversation is read by a subagent that has not seen it" \
    "$SKILL_DIR/structure-document/references/context-free-read.md" 'new subagent, not a fork.*seen none of the conversation'
  check "ROUTE-17: the retired decomposition skill stays in archive/" \
    "$([ ! -e "$SKILL_DIR/meta-spec" ] && [ -f "$REPO_ROOT/archive/meta-spec/SKILL.md" ] && echo 1 || echo 0)"
}

run_budget_contract() {
  local bytes
  bytes="$(cat "$APEX" "$RULE_DIR"/*.md | wc -c | tr -d ' ')"
  check "BUDGET-01: the apex and the rules together stay under $BUDGET_BYTES bytes (now $bytes)" \
    "$([ "$bytes" -lt "$BUDGET_BYTES" ] && echo 1 || echo 0)"
}

run_apex_contract
run_rule_contract
run_routing_contract
run_budget_contract

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  printf 'Failed:%b\n' "$FAIL_NAMES" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
