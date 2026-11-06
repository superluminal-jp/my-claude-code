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
  clarifier
  aws-research
  verified-delivery
  coder
  digital-agency-frontend
  git-workflow
  requirements-decomposition
  problem-definition
  product-strategy
  pyramid-structure
  scrum-master
  secure-logging
)

# A parent skill declares the skills it applies in a "## Child skills"
# section of its SKILL.md, one "- `name`" line per child. Prints the
# declared names, one per line; lines inside code blocks do not count.
# Code blocks follow CommonMark's fence rules, as the bundled checker of
# requirements-decomposition reads them: up to three spaces, then three or
# more backticks or tildes; only the same character, at least as many, with
# nothing but spaces or tabs after it, closes the block. Written without
# interval expressions, which some awk implementations lack.
declared_children() {
  [ -f "$1" ] || return 0
  awk '
    {
      sub(/\r$/, "")
      indent = 0
      while (indent < 3 && substr($0, indent + 1, 1) == " ") indent++
      rest = substr($0, indent + 1)
      mark = substr(rest, 1, 1)
      run = 0
      if (mark == "`" || mark == "~") { while (substr(rest, run + 1, 1) == mark) run++ }
      after = substr(rest, run + 1)
    }
    fence != "" {
      if (mark == fence && run >= fence_run && after ~ /^[ \t]*$/) fence = ""
      next
    }
    run >= 3 && !(mark == "`" && index(after, "`") > 0) { fence = mark; fence_run = run; next }
    /^## / { section = ($0 ~ /^## Child skills[[:space:]]*$/); next }
    section && /^- `[[:alnum:]_-]+`/ {
      name = $0
      sub(/^- `/, "", name)
      sub(/`.*/, "", name)
      print name
    }
  ' "$1"
}

is_listed() {
  local needle="$1" item
  shift
  for item in "$@"; do
    [ "$item" = "$needle" ] && return 0
  done
  return 1
}

# Prints one line per skill-to-skill reference that breaks the contract for
# the skills named after <dir>; prints nothing when the contract holds. A
# package may name another of these skills only when its SKILL.md declares
# that skill as a child, and then only by name, never by path. A declared
# child must be one of these skills and may not declare children itself.
reference_violations() {
  local dir="$1" source target file children child
  shift
  for source in "$@"; do
    [ -d "$dir/$source" ] || continue
    children="$(declared_children "$dir/$source/SKILL.md")"
    while IFS= read -r child; do
      [ -z "$child" ] && continue
      if [ "$child" = "$source" ]; then
        printf '%s declares itself as a child\n' "$source"
      elif ! is_listed "$child" "$@" || [ ! -f "$dir/$child/SKILL.md" ]; then
        printf '%s declares %s, which is not an authored skill\n' "$source" "$child"
      elif [ -n "$(declared_children "$dir/$child/SKILL.md")" ]; then
        printf '%s declares %s, which declares children of its own\n' "$source" "$child"
      fi
    done <<<"$children"
    for target in "$@"; do
      [ "$source" = "$target" ] && continue
      while IFS= read -r file; do
        if printf '%s\n' "$children" | grep -Fxq -- "$target"; then
          if grep -Eiq -- '(^|[^[:alnum:]_-])'"${target}"'/' "$file"; then
            printf '%s names its child %s by path\n' "$file" "$target"
          fi
        elif grep -Eiq -- '(`|/|skills/)'"${target}"'(`|/|[^[:alnum:]_-])' "$file"; then
          printf '%s names sibling package %s\n' "$file" "$target"
        fi
      done < <(find "$dir/$source" -type f -name '*.md' ! -path '*/references/dads-docs/*')
    done
  done
}

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
permissions.md
pyramid-principle.md
thinking-lenses.md"
  actual="$(find "$RULE_DIR" -maxdepth 1 -type f -name '*.md' -exec basename {} \; | sort)"
  check "RULE-01: exactly four universal rule files" "$([ "$actual" = "$expected" ] && echo 1 || echo 0)"

  check_absent_pattern "RULE-02: no config path or slash-command dependency" \
    '(\.claude/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' "$RULE_DIR"
  check_absent_pattern "RULE-03: no named authored-skill routing" \
    '(`|/)(clarifier|aws-research|verified-delivery|coder|digital-agency-frontend|git-workflow|requirements-decomposition|problem-definition|product-strategy|scrum-master)(`|[^[:alnum:]_-])' "$RULE_DIR"

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

  # The vendored upstream plugin (maintaining-living-documentation, vendored
  # with its hooks/hooks.json removed) references its own packaged paths, so
  # only authored skills are checked.
  local authored_entry_points=() entry_skill
  for entry_skill in "${authored_skills[@]}"; do
    authored_entry_points+=("$SKILL_DIR/$entry_skill/SKILL.md")
  done
  check_absent_pattern "SKILL-04: no entry point depends on config paths" \
    '(\.claude/(CLAUDE\.md|rules|skills)|\.agents/skills|rules/[[:alnum:]_-]+\.md)' "${authored_entry_points[@]}"

  local violations
  violations="$(reference_violations "$SKILL_DIR" "${authored_skills[@]}")"
  [ -n "$violations" ] && printf '%s\n' "$violations" | sed 's/^/    /' >&2
  check "SKILL-05: authored packages do not name siblings" "$([ -z "$violations" ] && echo 1 || echo 0)"

  check_contains "SKILL-07: deliverables are read by a subagent that has not seen the conversation" \
    "$SKILL_DIR/pyramid-structure/SKILL.md" 'subagent.*(not|never|none).*(conversation)'

  check_absent_pattern "SKILL-06: packages do not hard-code their install root" \
    '\.claude/skills/(clarifier|aws-research|verified-delivery|coder|digital-agency-frontend|git-workflow|requirements-decomposition|problem-definition|product-strategy|pyramid-structure|scrum-master|secure-logging)' \
    "$SKILL_DIR/clarifier" "$SKILL_DIR/aws-research" "$SKILL_DIR/verified-delivery" "$SKILL_DIR/coder" \
    "$SKILL_DIR/digital-agency-frontend" "$SKILL_DIR/git-workflow" \
    "$SKILL_DIR/requirements-decomposition" "$SKILL_DIR/problem-definition" \
    "$SKILL_DIR/product-strategy" "$SKILL_DIR/pyramid-structure" "$SKILL_DIR/scrum-master" \
    "$SKILL_DIR/secure-logging"

  check "SKILL-08: the decomposition skill is retired to archive/" \
    "$([ ! -e "$SKILL_DIR/meta-spec" ] && [ -f "$REPO_ROOT/archive/meta-spec/SKILL.md" ] && [ -f "$REPO_ROOT/archive/meta-spec/README.md" ] && echo 1 || echo 0)"
}

# Writes one fixture skill: write_fixture_skill <dir> <name> <body>.
write_fixture_skill() {
  mkdir -p "$1/$2"
  printf -- '---\nname: %s\ndescription: Fixture only. Do not use.\n---\n\n%s\n' "$2" "$3" >"$1/$2/SKILL.md"
}

# check_fixture <name> <dir> <regex>: with an empty regex the fixture must
# have no violation; otherwise it must have at least one, and every one must
# match the regex.
check_fixture() {
  local name="$1" dir="$2" expected="$3" out ok=0
  out="$(reference_violations "$dir" parent child-a child-b outsider)"
  if [ -z "$expected" ]; then
    [ -z "$out" ] && ok=1
  elif [ -n "$out" ] && ! printf '%s\n' "$out" | grep -Evq -- "$expected"; then
    ok=1
  fi
  [ "$ok" -eq 0 ] && [ -n "$out" ] && printf '%s\n' "$out" | sed 's/^/    /' >&2
  check "$name" "$ok"
}

# The acceptance scenarios of User Story 1 in specs/058-parent-skill-references:
# parent declares child-a and child-b; outsider is declared by no one.
run_parent_child_fixtures() {
  local root children
  root="$(mktemp -d)"
  children='## Child skills

- `child-a`
- `child-b`'

  write_fixture_skill "$root/f1" parent "Apply \`child-a\` first.

$children"
  write_fixture_skill "$root/f1" child-a "Standalone."
  write_fixture_skill "$root/f1" child-b "Standalone."
  write_fixture_skill "$root/f1" outsider "Standalone."
  check_fixture "PARENT-01: a parent may name a child it declares" "$root/f1" ''

  cp -R "$root/f1" "$root/f2"
  write_fixture_skill "$root/f2" parent "Apply \`outsider\` first.

$children"
  check_fixture "PARENT-02: a parent may not name a skill it does not declare" \
    "$root/f2" 'parent/SKILL\.md names sibling package outsider$'

  cp -R "$root/f1" "$root/f3"
  write_fixture_skill "$root/f3" child-a "Return to \`parent\`."
  check_fixture "PARENT-03: a child may not name its parent" \
    "$root/f3" 'child-a/SKILL\.md names sibling package parent$'

  cp -R "$root/f1" "$root/f4"
  write_fixture_skill "$root/f4" child-a "Then apply \`child-b\`."
  check_fixture "PARENT-04: a child may not name a sibling child" \
    "$root/f4" 'child-a/SKILL\.md names sibling package child-b$'

  cp -R "$root/f1" "$root/f5"
  write_fixture_skill "$root/f5" parent "Apply \`child-a\` first.

$children
- \`ghost\`"
  check_fixture "PARENT-05: a declared child must be an authored skill" \
    "$root/f5" '^parent declares ghost, which is not an authored skill$'

  cp -R "$root/f1" "$root/f6"
  write_fixture_skill "$root/f6" child-a "## Child skills

- \`child-b\`"
  check_fixture "PARENT-06: a declared child may not declare children of its own" \
    "$root/f6" '^parent declares child-a, which declares children of its own$'

  cp -R "$root/f1" "$root/f7"
  write_fixture_skill "$root/f7" parent "Read ../child-a/SKILL.md first.

$children"
  check_fixture "PARENT-07: a parent names its children by name, not by path" \
    "$root/f7" 'parent/SKILL\.md names its child child-a by path$'

  cp -R "$root/f1" "$root/f8"
  write_fixture_skill "$root/f8" parent "Apply \`child-a\` first.

$children
- \`parent\`"
  check_fixture "PARENT-08: a parent may not declare itself as a child" \
    "$root/f8" '^parent declares itself as a child$'

  # Code blocks follow CommonMark's fence rules: ~~~ fences, up to three
  # spaces of indentation, and a closing fence at least as long as the
  # opening one, so an example section inside a fence is not a declaration.
  cp -R "$root/f1" "$root/f9"
  write_fixture_skill "$root/f9" parent "Apply \`child-a\` first.

$children

~~~markdown
## Child skills

- \`ghost\`
~~~

   \`\`\`
## Child skills

- \`ghost\`
   \`\`\`"
  check_fixture "PARENT-09: an example section inside a tilde or indented fence is not a declaration" "$root/f9" ''

  cp -R "$root/f1" "$root/f10"
  write_fixture_skill "$root/f10" parent "\`\`\`\`markdown
\`\`\`
still code
\`\`\`\`

$children
- \`ghost\`"
  check_fixture "PARENT-10: a shorter fence inside a longer one does not close it" \
    "$root/f10" '^parent declares ghost, which is not an authored skill$'

  rm -rf "$root"
}

run_routing_fixtures() {
  check_contains "ROUTE-01: code-only selects implementation" "$SKILL_DIR/coder/SKILL.md" '^description:.*(code|configuration|observable behavior)'
  check_contains "ROUTE-05: DADS remains an independently matching domain overlay" "$SKILL_DIR/digital-agency-frontend/SKILL.md" '^description:.*(overlay|independent|alongside|also applies)'
  check_contains "ROUTE-06: formal requirements can precede DADS implementation" "$SKILL_DIR/clarifier/SKILL.md" '^description:.*(before|prerequisite|independent|compound)'
  check_contains "ROUTE-07: Scrum artifacts retain domain judgement" "$SKILL_DIR/scrum-master/SKILL.md" '^description:.*(artifact|成果物|資料).*(independent|別|併用|適用)'
  check_contains "ROUTE-08: generic PM status and Gantt work is not Scrum" "$SKILL_DIR/scrum-master/SKILL.md" '^description:.*(Gantt|status|project management).*(not|対象外|使わない)'
  check_contains "ROUTE-09: product strategy precedes development, distinct from scope/facilitation/generic docs" "$SKILL_DIR/product-strategy/SKILL.md" '^description:.*(戦略|strategy).*(対象外|使わない|out of scope|not for)'
  check_contains "ROUTE-10: problem definition stays gap-framing, distinct from cause analysis/solutions/scope clarification" "$SKILL_DIR/problem-definition/SKILL.md" '^description:.*(problem|問題).*(out of scope|not for|対象外|使わない)'
  check_contains "ROUTE-12: secure logging stays a domain overlay, distinct from log infrastructure operations" "$SKILL_DIR/secure-logging/SKILL.md" '^description:.*overlay.*alongside.*supplements'
  check_contains "ROUTE-13: secure logging excludes log infrastructure operations" "$SKILL_DIR/secure-logging/SKILL.md" '^description:.*(Do not use|not for).*(SIEM|infrastructure)'
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
run_parent_child_fixtures
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
