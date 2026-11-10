#!/usr/bin/env bash
# Contract for what harness/settings.json installs at user scope about the
# OS sandbox, the SessionStart hooks, and the MCP servers it stops
# (spec 067, ADR-0020, ADR-0021).
#
# Offline and side-effect free: it reads the settings file, and runs each
# SessionStart hook command with a scratch HOME, a scratch CLAUDE_ENV_FILE,
# and stub commands under sh, bash, and (when installed) zsh, because the
# hook may run under any of them.
#
# What it cannot show: that Claude Code honours these keys. That is checked
# in a new session after install.sh (spec 067, T011).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS="$REPO_ROOT/harness/settings.json"

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

# q FILTER — 1 when the jq filter is true for the settings file, else 0.
q() {
  jq -e "$1" "$SETTINGS" >/dev/null 2>&1 && printf 1 || printf 0
}

command -v jq >/dev/null 2>&1 || {
  echo "run-sandbox-settings: jq is required" >&2
  exit 1
}
jq -e . "$SETTINGS" >/dev/null || {
  echo "run-sandbox-settings: $SETTINGS is not valid JSON" >&2
  exit 1
}

# --- The boundary --------------------------------------------------------

check "SBX-01 the sandbox is on by default" \
  "$(q '.sandbox.enabled == true')"

check "SBX-02 strictness is standard: retry outside stays possible, unlisted hosts are not refused outright" \
  "$(q '(.sandbox.allowUnsandboxedCommands // true) == true and (.sandbox.network.strictAllowlist // false) == false')"

check "SBX-03 nothing under ~/.aws, nor the home directory, is re-opened or made writable" \
  "$(q '[(.sandbox.filesystem // {} | .allowRead, .allowWrite | .[]?)
         | select(. == "~" or . == "~/" or . == "/" or startswith("~/.aws"))] | length == 0')"

check "SBX-04 GPG secrets, revocation certificates, and other credential stores stay unreadable" \
  "$(q '["~/.gnupg/private-keys-v1.d", "~/.gnupg/secring.gpg", "~/.gnupg/openpgp-revocs.d",
         "~/.git-credentials", "~/.netrc", "~/.config/gh/hosts.yml", "~/.docker/config.json",
         "~/.kube/config"]
        - (.sandbox.filesystem.denyRead // []) | length == 0')"

# Configuration and scd-event can make a GnuPG process outside the sandbox
# run a program, so they stay unwritable along with the secrets.
check "SBX-05 GPG secrets, keyrings, trust database, configuration, and scd-event stay unwritable" \
  "$(q '["~/.gnupg/private-keys-v1.d", "~/.gnupg/secring.gpg", "~/.gnupg/openpgp-revocs.d",
         "~/.gnupg/pubring.kbx", "~/.gnupg/pubring.gpg", "~/.gnupg/public-keys.d",
         "~/.gnupg/trustdb.gpg", "~/.gnupg/gpg.conf", "~/.gnupg/gpg-agent.conf",
         "~/.gnupg/gpgsm.conf", "~/.gnupg/common.conf", "~/.gnupg/dirmngr.conf",
         "~/.gnupg/scdaemon.conf", "~/.gnupg/keyboxd.conf", "~/.gnupg/sshcontrol",
         "~/.gnupg/trustlist.txt", "~/.gnupg/scd-event"]
        - (.sandbox.filesystem.denyWrite // []) | length == 0')"

check "SBX-06 only the gpg-agent and keyboxd sockets are reachable" \
  "$(q '((.sandbox.network.allowUnixSockets // []) | sort) == ["~/.gnupg/S.gpg-agent", "~/.gnupg/S.keyboxd"]
        and (.sandbox.network.allowAllUnixSockets // false) == false')"

check "SBX-07 hosts allowed without asking are exactly the two Google Fonts hosts" \
  "$(q '((.sandbox.network.allowedDomains // []) | sort) == ["fonts.googleapis.com", "fonts.gstatic.com"]')"

# The same file is read as project settings here and as user settings once
# installed; only ~/ resolves to the same place in both (ADR-0014).
check "SBX-08 every sandbox path is anchored at ~/" \
  "$(q '[(.sandbox.filesystem // {} | .allowWrite, .denyWrite, .denyRead, .allowRead | .[]?),
         (.sandbox.network.allowUnixSockets // [])[]] | all(startswith("~/"))')"

# --- The daily work it opens ---------------------------------------------

check "SBX-09 writes are opened for ~/.gnupg and ~/Library/Fonts only" \
  "$(q '((.sandbox.filesystem.allowWrite // []) | sort) == ["~/.gnupg", "~/Library/Fonts"]')"

check "SBX-10 only aws commands are taken out of the sandbox" \
  "$(q '(.sandbox.excludedCommands // []) == ["aws *"]')"

# --- MCP servers it stops ------------------------------------------------

check "MCP-01 the hosted GitHub MCP server is denied wherever it is defined" \
  "$(q '[.deniedMcpServers[]? | select(.serverUrl == "https://api.githubcopilot.com/*")] | length == 1')"

check "MCP-02 the github plugin is disabled" \
  "$(q '.enabledPlugins["github@claude-plugins-official"] == false')"

check "MCP-03 bedrock-agentcore is denied by name" \
  "$(q '[.deniedMcpServers[]? | select(.serverName == "bedrock-agentcore")] | length == 1')"

check "MCP-04 bedrock-agentcore is denied by command" \
  "$(q '[.deniedMcpServers[]? | select(.serverCommand == ["uvx", "awslabs.amazon-bedrock-agentcore-mcp-server@latest"])] | length == 1')"

check "MCP-05 claude.ai connectors are off" \
  "$(q '.disableClaudeAiConnectors == true')"

check "MCP-06 plugins are not synced from claude.ai" \
  "$(q '.syncClaudeAiPlugins == false')"

# --- SessionStart hooks --------------------------------------------------

ENV_HOOK="Removing Bedrock AWS variables from Bash commands..."
GPG_HOOK="Starting gpg-agent outside the sandbox..."
NOTE_HOOK="Adding shell and sandbox notes..."

hook_command() {
  jq -r --arg m "$1" \
    '[.hooks.SessionStart[]?.hooks[]? | select(.statusMessage == $m) | .command] | if length == 1 then .[0] else empty end' \
    "$SETTINGS"
}

for name in "$ENV_HOOK" "$GPG_HOOK" "$NOTE_HOOK"; do
  [ -n "$(hook_command "$name")" ] && c=1 || c=0
  check "HOOK-00 exactly one SessionStart hook says \"$name\"" "$c"
done

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/sandbox-settings.XXXXXX")"
trap 'rm -rf "$SCRATCH"' EXIT
STUBS="$SCRATCH/bin"
mkdir -p "$STUBS"

SHELLS="sh bash"
command -v zsh >/dev/null 2>&1 && SHELLS="$SHELLS zsh"

# run_hook SHELL COMMAND [VAR=VALUE ...] — run a hook command the way Claude
# Code does, with SessionStart input on stdin and only the given variables.
run_hook() {
  local shell="$1" cmd="$2"
  shift 2
  printf '%s' '{"hook_event_name":"SessionStart","source":"startup"}' |
    env -i PATH="$STUBS:/usr/bin:/bin" HOME="$SCRATCH/home" "$@" "$shell" -c "$cmd"
}

AWS_VARS="AWS_PROFILE AWS_DEFAULT_PROFILE AWS_REGION AWS_DEFAULT_REGION AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_BEARER_TOKEN_BEDROCK"

# after_env_file FILE SHELL — how many of the AWS variables a settings.json
# env block could pass are still set after a Bash command sources FILE.
after_env_file() {
  env -i PATH=/usr/bin:/bin \
    AWS_PROFILE=bedrock AWS_DEFAULT_PROFILE=bedrock AWS_REGION=us-east-1 AWS_DEFAULT_REGION=us-east-1 \
    AWS_ACCESS_KEY_ID=id AWS_SECRET_ACCESS_KEY=secret AWS_SESSION_TOKEN=session AWS_BEARER_TOKEN_BEDROCK=tok \
    "$2" -c '. "$1"; n=0; for v in '"$AWS_VARS"'; do eval "[ -n \"\${$v+set}\" ]" && n=$((n + 1)); done; printf %s "$n"' _ "$1"
}

env_cmd="$(hook_command "$ENV_HOOK")"
gpg_cmd="$(hook_command "$GPG_HOOK")"
note_cmd="$(hook_command "$NOTE_HOOK")"

for sh_name in $SHELLS; do
  mkdir -p "$SCRATCH/home"

  # AWS-01..04: Bash keeps no Bedrock AWS variable in Bedrock mode, and is
  # left alone otherwise.
  envf="$SCRATCH/env.$sh_name"
  for on in 1 true; do
    : >"$envf"
    run_hook "$sh_name" "$env_cmd" CLAUDE_ENV_FILE="$envf" CLAUDE_CODE_USE_BEDROCK="$on"
    [ "$(after_env_file "$envf" "$sh_name")" = "0" ] && c=1 || c=0
    check "AWS-01 [$sh_name] CLAUDE_CODE_USE_BEDROCK=$on leaves Bash none of the eight AWS variables" "$c"
  done

  for off in 0 ""; do
    : >"$envf"
    run_hook "$sh_name" "$env_cmd" CLAUDE_ENV_FILE="$envf" CLAUDE_CODE_USE_BEDROCK="$off"
    [ "$(after_env_file "$envf" "$sh_name")" = "8" ] && c=1 || c=0
    check "AWS-02 [$sh_name] CLAUDE_CODE_USE_BEDROCK='$off' changes no AWS variable" "$c"
  done

  run_hook "$sh_name" "$env_cmd" CLAUDE_CODE_USE_BEDROCK=1
  check "AWS-03 [$sh_name] without CLAUDE_ENV_FILE the hook does nothing and succeeds" "$([ $? -eq 0 ] && echo 1 || echo 0)"

  # GPG-01..03: gpg-agent is launched outside the sandbox only when GnuPG is set up.
  printf '#!/bin/sh\nprintf "%%s\\n" "$*" >>"%s/gpgconf.log"\n' "$SCRATCH" >"$STUBS/gpgconf"
  chmod +x "$STUBS/gpgconf"
  rm -f "$SCRATCH/gpgconf.log"
  mkdir -p "$SCRATCH/home/.gnupg"
  run_hook "$sh_name" "$gpg_cmd"
  rc=$?
  { [ "$rc" -eq 0 ] && [ "$(cat "$SCRATCH/gpgconf.log" 2>/dev/null)" = "--launch gpg-agent" ]; } && c=1 || c=0
  check "GPG-01 [$sh_name] with gpgconf and ~/.gnupg the hook launches gpg-agent" "$c"

  rm -f "$SCRATCH/gpgconf.log"
  rmdir "$SCRATCH/home/.gnupg"
  run_hook "$sh_name" "$gpg_cmd"
  rc=$?
  { [ "$rc" -eq 0 ] && [ ! -e "$SCRATCH/gpgconf.log" ]; } && c=1 || c=0
  check "GPG-02 [$sh_name] without ~/.gnupg the hook launches nothing" "$c"

  rm -f "$STUBS/gpgconf"
  mkdir -p "$SCRATCH/home/.gnupg"
  run_hook "$sh_name" "$gpg_cmd"
  check "GPG-03 [$sh_name] without gpgconf the hook succeeds quietly" "$([ $? -eq 0 ] && echo 1 || echo 0)"
  rmdir "$SCRATCH/home/.gnupg"

  # NOTE-01..07: the context it adds depends on the Bash tool's shell, the
  # OS, and whether the aws CLI is installed.
  printf '#!/bin/sh\necho Darwin\n' >"$STUBS/uname"
  chmod +x "$STUBS/uname"
  out="$(run_hook "$sh_name" "$note_cmd" SHELL=/bin/zsh)"
  case "$out" in
    *"runs commands in zsh"*"no matches found"*"=word"*'"${cmd[@]}"'*) c=1 ;;
    *) c=0 ;;
  esac
  check "NOTE-01 [$sh_name] when the Bash tool runs zsh the note names the three zsh pitfalls" "$c"

  case "$out" in *"--single-process"*) c=1 ;; *) c=0 ;; esac
  check "NOTE-02 [$sh_name] on macOS the note says Chromium needs --single-process in the sandbox" "$c"

  out="$(run_hook "$sh_name" "$note_cmd" SHELL=/bin/zsh CLAUDE_CODE_SHELL=/bin/bash)"
  case "$out" in *zsh*) c=0 ;; *) c=1 ;; esac
  check "NOTE-03 [$sh_name] CLAUDE_CODE_SHELL=bash wins over SHELL=zsh" "$c"

  out="$(run_hook "$sh_name" "$note_cmd" SHELL=/bin/bash CLAUDE_CODE_SHELL=/opt/homebrew/bin/zsh)"
  case "$out" in *"runs commands in zsh"*) c=1 ;; *) c=0 ;; esac
  check "NOTE-04 [$sh_name] CLAUDE_CODE_SHELL=zsh wins over SHELL=bash" "$c"

  printf '#!/bin/sh\necho Linux\n' >"$STUBS/uname"
  out="$(run_hook "$sh_name" "$note_cmd" SHELL=/bin/bash)"
  [ -z "$out" ] && c=1 || c=0
  check "NOTE-05 [$sh_name] with bash on Linux and no aws CLI the hook adds nothing" "$c"

  printf '#!/bin/sh\nexit 0\n' >"$STUBS/aws"
  chmod +x "$STUBS/aws"
  out="$(run_hook "$sh_name" "$note_cmd" SHELL=/bin/bash)"
  case "$out" in *"one aws command"*"--profile"*) c=1 ;; *) c=0 ;; esac
  check "NOTE-06 [$sh_name] with the aws CLI installed the note says how aws leaves the sandbox and to name --profile" "$c"
  rm -f "$STUBS/aws" "$STUBS/uname"
done

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
