#!/usr/bin/env bash
# Sync-health suite for the Codex CLI port of .claude/ config (feature 014).
# Detects drift between the repo-tracked Codex sources (.codex/, .agents/)
# and their deployed/expanded counterparts, and between the two tools'
# permission/MCP/skill catalogs. See specs/014-codex-config-port/contracts/
# sync-check.md for the full contract (check IDs, exit codes, skip-warn rules).
#
# Deterministic where possible: no network. Checks that depend on a local
# `~/.codex`/`~/.agents`/`~/.claude` expansion (i.e. install.sh having been
# run) SKIP with a warning instead of failing when that expansion is absent,
# so this suite is meaningful both in CI (repo-only) and on a developer
# machine (post-install).
#
# Usage: bash tests/run-codex-sync.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="${CODEX_SYNC_REPO_ROOT_OVERRIDE:-$REPO_ROOT}"
SYNC_HOME="${CODEX_SYNC_HOME_OVERRIDE:-$HOME}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0
FAIL_NAMES=""

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: 'jq' is required for this test." >&2
  exit 1
fi

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

skip() {
  local name="$1" reason="$2"
  SKIP=$((SKIP + 1))
  printf "${YELLOW}SKIP${NC} %s (%s)\n" "$name" "$reason"
}

# Broken-symlink helper: prints paths under $1 whose symlinks don't resolve.
find_broken_symlinks() {
  local dir="$1"
  [ -d "$dir" ] || return 0
  find "$dir" -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null
}

# ---------------------------------------------------------------------------
# SYNC-01/02: .agents/skills/ (repo + expanded) broken-symlink checks
# ---------------------------------------------------------------------------

REPO_SKILLS="$REPO_ROOT/.agents/skills"
HOME_SKILLS="$SYNC_HOME/.agents/skills"
repo_broken=$(find_broken_symlinks "$REPO_SKILLS")
check "SYNC-01: repository skill links resolve" "$([ -z "$repo_broken" ] && echo 1 || echo 0)"

if [ -d "$HOME_SKILLS" ]; then
  HOME_SKILLS_OK=1
  home_broken=$(find_broken_symlinks "$HOME_SKILLS")
  [ -z "$home_broken" ] || HOME_SKILLS_OK=0
  for skill_name in adr clarifier coder digital-agency-frontend minto-builder minto-reviewer minto-rewriter; do
    deployed_link="$HOME_SKILLS/$skill_name"
    expected_target="$SYNC_HOME/.claude/skills/$skill_name"
    deployed_target=$(readlink "$deployed_link" 2>/dev/null || true)
    [ -L "$deployed_link" ] && [ "$deployed_target" = "$expected_target" ] && [ -f "$deployed_link/SKILL.md" ] || HOME_SKILLS_OK=0
  done
  check "SYNC-02: deployed user skill catalog is complete and resolves" "$HOME_SKILLS_OK"
else
  skip "SYNC-02: deployed user skill catalog is complete and resolves" "~/.agents/skills not deployed — run install.sh"
fi

# ---------------------------------------------------------------------------
# SYNC-03/06: .codex/AGENTS.md size budget + repo/expanded content match
# ---------------------------------------------------------------------------

CODEX_AGENTS_SRC="$REPO_ROOT/.codex/AGENTS.md"
CODEX_AGENTS_DST="$SYNC_HOME/.codex/AGENTS.md"
AGENTS_MAX_BYTES=32768
AGENTS_WARN_BYTES=28672

if [ -f "$CODEX_AGENTS_SRC" ]; then
  size=$(wc -c <"$CODEX_AGENTS_SRC" | tr -d ' ')
  check "SYNC-03: .codex/AGENTS.md <= 32 KiB ($size bytes)" "$([ "$size" -le "$AGENTS_MAX_BYTES" ] && echo 1 || echo 0)"
  GUIDANCE_OK=1
  for required_heading in '## Clarification' '## Skill routing' '## Git workflow' '## Live documentation'; do
    grep -Fq "$required_heading" "$CODEX_AGENTS_SRC" || GUIDANCE_OK=0
  done
  check "SYNC-03: shared guidance covers core Claude prose rules" "$GUIDANCE_OK"
  SKILL_ROUTING_OK=1
  for skill_name in adr clarifier coder digital-agency-frontend minto-builder minto-reviewer minto-rewriter; do
    skill_reference="@.agents/skills/$skill_name/SKILL.md"
    grep -Fq "$skill_reference" "$CODEX_AGENTS_SRC" || SKILL_ROUTING_OK=0
  done
  check "SYNC-03: skill routing references project skill instructions" "$SKILL_ROUTING_OK"
  if [ "$size" -gt "$AGENTS_WARN_BYTES" ] && [ "$size" -le "$AGENTS_MAX_BYTES" ]; then
    printf "${YELLOW}WARN${NC} SYNC-03: .codex/AGENTS.md is %d bytes, approaching the 32 KiB budget\n" "$size"
  fi
else
  check "SYNC-03: .codex/AGENTS.md exists" 0
fi

if [ -f "$CODEX_AGENTS_DST" ]; then
  DEPLOYED_CODEX_OK=1
  cmp -s "$CODEX_AGENTS_SRC" "$CODEX_AGENTS_DST" || DEPLOYED_CODEX_OK=0
  for source_hook in "$REPO_ROOT"/.codex/hooks/*.sh; do
    deployed_hook="$SYNC_HOME/.codex/hooks/$(basename "$source_hook")"
    [ -x "$deployed_hook" ] && cmp -s "$source_hook" "$deployed_hook" || DEPLOYED_CODEX_OK=0
  done
  for managed_pair in \
    '.codex/rules/guardrails.rules|.codex/rules/guardrails.rules' \
    '.codex/prompts/verify-config.md|.codex/prompts/verify-config.md'; do
    source_rel=${managed_pair%%|*}
    deployed_rel=${managed_pair#*|}
    cmp -s "$REPO_ROOT/$source_rel" "$SYNC_HOME/$deployed_rel" || DEPLOYED_CODEX_OK=0
  done
  check "SYNC-06: deployed Codex files match repository sources" "$DEPLOYED_CODEX_OK"
else
  skip "SYNC-06: deployed Codex files match repository sources" "~/.codex/AGENTS.md not deployed — run install.sh"
fi

# ---------------------------------------------------------------------------
# SYNC-04: .mcp.json server set <= ~/.codex/config.toml mcp_servers set
# ---------------------------------------------------------------------------

CODEX_CONFIG="$SYNC_HOME/.codex/config.toml"
MCP_BEGIN='# >>> my-claude-code managed MCP servers (do not edit by hand; see install.sh) >>>'
MCP_END='# <<< my-claude-code managed MCP servers <<<'

if [ -f "$CODEX_CONFIG" ]; then
  MCP_SET_OK=1
  MCP_UNIQUE_OK=1
  while IFS= read -r server; do
    server_header_count=$(grep -Ec "^\\[mcp_servers\\.(\"${server}\"|${server})\\]$" "$CODEX_CONFIG")
    [ "$server_header_count" -ge 1 ] || MCP_SET_OK=0
    [ "$server_header_count" -eq 1 ] || MCP_UNIQUE_OK=0
  done < <(jq -r '.mcpServers | keys[]' "$REPO_ROOT/.mcp.json")
  check "SYNC-04: ~/.codex/config.toml contains every .mcp.json server" "$MCP_SET_OK"
  check "SYNC-04: each catalog MCP server is defined exactly once" "$MCP_UNIQUE_OK"
else
  skip "SYNC-04: Codex MCP catalog matches .mcp.json" "~/.codex/config.toml not deployed — run install.sh"
fi

# ---------------------------------------------------------------------------
# SYNC-05: .codex/hooks/ adapters exist, executable, and match install.sh's
# ADAPTERS list
# ---------------------------------------------------------------------------

HOOKS_OK=1
for adapter_spec in \
  'destructive-command-adapter.sh|PreToolUse|Bash' \
  'pre-edit-adapter.sh|PreToolUse|apply_patch|Edit|Write' \
  'post-edit-adapter.sh|PostToolUse|apply_patch|Edit|Write' \
  'prompt-secret-adapter.sh|UserPromptSubmit|NONE'; do
  filename=${adapter_spec%%|*}
  remainder=${adapter_spec#*|}
  event=${remainder%%|*}
  matcher=${remainder#*|}
  [ -x "$REPO_ROOT/.codex/hooks/$filename" ] || HOOKS_OK=0
  if [ "$matcher" = "NONE" ]; then
    grep -Fq "(\"$filename\", \"$event\", None)" "$REPO_ROOT/install.sh" || HOOKS_OK=0
  else
    grep -Fq "(\"$filename\", \"$event\", \"$matcher\")" "$REPO_ROOT/install.sh" || HOOKS_OK=0
  fi
done
grep -Fq 'if matcher is not None:' "$REPO_ROOT/install.sh" || HOOKS_OK=0
check "SYNC-05: four executable adapters match install.sh ADAPTERS" "$HOOKS_OK"

# ---------------------------------------------------------------------------
# SYNC-07: ~/.claude/scripts/guardrails/ present + executable
# ---------------------------------------------------------------------------

HOME_GUARDRAILS="$SYNC_HOME/.claude/scripts/guardrails"
if [ -d "$HOME_GUARDRAILS" ]; then
  GUARDRAILS_OK=1
  for shared_script in "$REPO_ROOT"/scripts/guardrails/*.sh; do
    [ -x "$HOME_GUARDRAILS/$(basename "$shared_script")" ] || GUARDRAILS_OK=0
  done
  check "SYNC-07: deployed shared guardrails are complete and executable" "$GUARDRAILS_OK"
else
  skip "SYNC-07: deployed shared guardrails are complete and executable" "~/.claude/scripts/guardrails not deployed — run install.sh"
fi

# ---------------------------------------------------------------------------
# SYNC-08: .codex/README.md coverage vs actual .claude/ elements
# ---------------------------------------------------------------------------

DEPLOYMENT_MAP="$REPO_ROOT/.codex/README.md"
COVERAGE_OK=1
[ -f "$DEPLOYMENT_MAP" ] || COVERAGE_OK=0
if [ -f "$DEPLOYMENT_MAP" ]; then
  while IFS= read -r source_file; do
    case "$source_file" in
    .claude/skills/*)
      grep -Fq '.claude/skills/*' "$DEPLOYMENT_MAP" || COVERAGE_OK=0
      ;;
    .claude/settings.json)
      while IFS= read -r settings_key; do
        grep -Fq "#$settings_key" "$DEPLOYMENT_MAP" || COVERAGE_OK=0
      done < <(jq -r 'keys[]' "$REPO_ROOT/.claude/settings.json")
      ;;
    *)
      grep -Fq "$source_file" "$DEPLOYMENT_MAP" || COVERAGE_OK=0
      ;;
    esac
  done < <(cd "$REPO_ROOT" && find .claude -type f -print | sort)
  grep -Fq '.mcp.json' "$DEPLOYMENT_MAP" || COVERAGE_OK=0
  grep -Fq '| TODO' "$DEPLOYMENT_MAP" && COVERAGE_OK=0
fi
check "SYNC-08: deployment map classifies every Claude configuration element" "$COVERAGE_OK"

# ---------------------------------------------------------------------------
# SYNC-09: .codex/prompts/verify-config.md <-> .claude/commands/verify-config.md
# ---------------------------------------------------------------------------

CODEX_VERIFY_PROMPT="$REPO_ROOT/.codex/prompts/verify-config.md"
CLAUDE_VERIFY_COMMAND="$REPO_ROOT/.claude/commands/verify-config.md"
VERIFY_PROMPT_OK=1
[ -f "$CODEX_VERIFY_PROMPT" ] || VERIFY_PROMPT_OK=0
[ -f "$CLAUDE_VERIFY_COMMAND" ] || VERIFY_PROMPT_OK=0
if [ -f "$CODEX_VERIFY_PROMPT" ]; then
  grep -Fq '.claude/commands/verify-config.md' "$CODEX_VERIFY_PROMPT" || VERIFY_PROMPT_OK=0
  grep -Fqi 'do not modify' "$CODEX_VERIFY_PROMPT" || VERIFY_PROMPT_OK=0
fi
check "SYNC-09: Codex prompt delegates to the Claude verification procedure" "$VERIFY_PROMPT_OK"

# ---------------------------------------------------------------------------
# SYNC-10: .codex/rules/guardrails.rules syntax lint
# ---------------------------------------------------------------------------

RULES_FILE="$REPO_ROOT/.codex/rules/guardrails.rules"
RULES_OK=1
if [ ! -f "$RULES_FILE" ]; then
  RULES_OK=0
else
  prefix_count=$(grep -Ec '^[[:space:]]*prefix_rule\(' "$RULES_FILE" || true)
  decision_count=$(grep -Ec 'decision[[:space:]]*=[[:space:]]*"(allow|prompt|forbidden)"' "$RULES_FILE" || true)
  all_decision_count=$(grep -Ec 'decision[[:space:]]*=' "$RULES_FILE" || true)
  closed_count=$(grep -Ec '^[[:space:]]*prefix_rule\(.*\)[[:space:]]*$' "$RULES_FILE" || true)
  [ "$prefix_count" -gt 0 ] || RULES_OK=0
  [ "$prefix_count" -eq "$decision_count" ] || RULES_OK=0
  [ "$decision_count" -eq "$all_decision_count" ] || RULES_OK=0
  [ "$prefix_count" -eq "$closed_count" ] || RULES_OK=0
fi
check "SYNC-10: guardrails.rules uses valid prefix_rule decisions" "$RULES_OK"

# ---------------------------------------------------------------------------
# SYNC-11: representative allow-list categories present in both
# .claude/settings.json permissions.allow and .codex/rules/guardrails.rules
# ---------------------------------------------------------------------------

SETTINGS_FILE="$REPO_ROOT/.claude/settings.json"

settings_allows() {
  local entry="$1"
  jq -e --arg entry "$entry" '.permissions.allow | index($entry) != null' "$SETTINGS_FILE" >/dev/null 2>&1
}

rules_allow() {
  local pattern="$1"
  [ -f "$RULES_FILE" ] && grep -F "$pattern" "$RULES_FILE" | grep -Fq 'decision = "allow"'
}

ALLOW_PARITY_OK=1
settings_allows 'Bash(tests/run-*.sh)' && rules_allow 'pattern = ["tests/run-codex-sync.sh"]' || ALLOW_PARITY_OK=0
settings_allows 'Bash(scripts/check-mcp-consistency.sh)' && rules_allow 'pattern = ["scripts/check-mcp-consistency.sh"]' || ALLOW_PARITY_OK=0
for tool in shellcheck shfmt jq yamllint; do
  settings_allows "Bash($tool *)" && rules_allow "pattern = [\"$tool\"]" || ALLOW_PARITY_OK=0
done
for git_command in status diff log fetch; do
  settings_entry="Bash(git $git_command *)"
  [ "$git_command" = "status" ] && settings_entry='Bash(git status)'
  settings_allows "$settings_entry" && rules_allow "pattern = [\"git\", \"$git_command\"]" || ALLOW_PARITY_OK=0
done
check "SYNC-11: representative allow categories match Claude permissions" "$ALLOW_PARITY_OK"

# ---------------------------------------------------------------------------
# SYNC-12: ~/.codex/config.toml mcp_servers block has no plaintext secrets
# ---------------------------------------------------------------------------

if [ -f "$CODEX_CONFIG" ]; then
  MCP_BLOCK=$(awk -v begin="$MCP_BEGIN" -v end="$MCP_END" '
    $0 == begin { capture = 1; next }
    $0 == end { capture = 0; found = 1 }
    capture { print }
    END { if (!found) exit 2 }
  ' "$CODEX_CONFIG" 2>/dev/null) || MCP_BLOCK=""
  SECRET_PATTERN='(AKIA|ASIA)[0-9A-Z]{16}|(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{22,}|xox[abpors]-[A-Za-z0-9-]{10,}|-----BEGIN ([A-Z]+ )?PRIVATE KEY-----|AIza[0-9A-Za-z_-]{35}'
  MCP_SECRET_OK=1
  [ -n "$MCP_BLOCK" ] || MCP_SECRET_OK=0
  printf '%s' "$MCP_BLOCK" | grep -Eq -- "$SECRET_PATTERN" && MCP_SECRET_OK=0
  check "SYNC-12: managed Codex MCP block contains no plaintext secrets" "$MCP_SECRET_OK"
else
  skip "SYNC-12: managed Codex MCP block contains no plaintext secrets" "~/.codex/config.toml not deployed — run install.sh"
fi

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}, ${YELLOW}%d skipped${NC}\n" "$PASS" "$FAIL" "$SKIP"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
