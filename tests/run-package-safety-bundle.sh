#!/usr/bin/env bash
# Contract test for the team package-install safety bundle
# (team/package-safety/, ADR-0017). Static checks only: no network, no
# package manager runs. The bundle's behaviour inside Claude Code and each
# package manager is verified by hand with the procedure in the bundle's
# README; this suite guards the invariants that keep the files consistent
# with each other and safe to commit into another repository.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE="$REPO_ROOT/team/package-safety"
SETTINGS="$BUNDLE/claude-settings.json"
PROJECT="$BUNDLE/project"

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required but not found on PATH" >&2
  exit 1
fi

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

jqok() { jq -e "$1" "$SETTINGS" >/dev/null 2>&1 && echo 1 || echo 0; }
has_line() { [ -f "$1" ] && grep -qxF "$2" "$1" && echo 1 || echo 0; }

check "settings file is a JSON object" "$(jqok 'type == "object"')"

# The same file must work as a project .claude/settings.json, so it may not
# carry keys that only user or managed settings honour, nor anything that
# widens what a session can do.
check "no allow tier, defaultMode, or autoMode" \
  "$(jqok '(.permissions // {} | has("allow") or has("defaultMode")) or has("autoMode") | not')"
check "no sandbox loosening keys" \
  "$(jqok '(.sandbox.filesystem.disabled // false | not)
           and (.sandbox.allowUnsandboxedCommands // false | not)
           and (.sandbox.enableWeakerNetworkIsolation // false | not)
           and (.sandbox.network.allowAllUnixSockets // false | not)')"
# gh and terraform fail TLS verification under macOS Seatbelt, and git over
# SSH cannot tunnel through the macOS proxy, so exactly these run outside the
# sandbox with their usual credentials. No package manager may be listed:
# install scripts must stay sandboxed (ADR-0017).
check "excluded commands are exactly gh, terraform, and git's network commands" \
  "$(jqok '.sandbox.excludedCommands | sort == [
             "gh *", "git clone *", "git fetch *", "git ls-remote *",
             "git pull *", "git push *", "terraform *"]')"

check "sandbox is on and refuses to run unsandboxed" \
  "$(jqok '.sandbox.enabled == true and .sandbox.failIfUnavailable == true')"
# npm and uv fail inside the sandbox unless they can write their cache, so the
# only extra writable paths are those two caches - nothing on PATH, no rc
# file, and not ~/.npm/_npx, whose contents npx later executes. pip runs with
# its cache disabled and pnpm falls back to a store in the project (ADR-0017).
check "extra writable paths are exactly the npm and uv caches" \
  "$(jqok '.sandbox.filesystem.allowWrite | sort == ["~/.cache/uv", "~/.npm/_cacache"]')"
# pip's default macOS trust-store lookup fails under the sandbox
# (SSLCertVerificationError OSStatus -26276); certifi works.
check "env: pip uses its bundled CA certificates" \
  "$(jqok '.env.PIP_USE_DEPRECATED == "legacy-certs"')"
# pip that other tools still call internally must refuse to install outside a
# virtual environment, so nothing lands in a global interpreter (ADR-0017).
check "env: pip requires a virtual environment" \
  "$(jqok '.env.PIP_REQUIRE_VIRTUALENV == "true"')"
check "network allowlist is exactly the public npm and PyPI hosts" \
  "$(jqok '.sandbox.network.allowedDomains | sort
           == ["files.pythonhosted.org", "pypi.org", "registry.npmjs.org"]')"
# mask entries are dropped from project settings, so every entry must deny.
check "credential env vars are all deny entries" \
  "$(jqok '(.sandbox.credentials.envVars | length > 0)
           and all(.sandbox.credentials.envVars[]; .mode == "deny")')"

# One seven-day rule, expressed in each tool's own unit.
check "env: npm resolves only versions >= 7 days old" \
  "$(jqok '.env.npm_config_min_release_age == "7"')"
check "env: pnpm resolves only versions >= 10080 minutes old" \
  "$(jqok '.env.pnpm_config_minimum_release_age == "10080"')"
# UV_EXCLUDE_NEWER would invalidate every uv.lock that lacks the same cutoff,
# so uv's rule lives only in the project template. pip installs are denied in
# favour of uv, and PIP_UPLOADED_PRIOR_TO=P7D would break the pip that other
# tools still call internally on pip < 26.1 (ADR-0017).
check "env: no UV_EXCLUDE_NEWER or PIP_UPLOADED_PRIOR_TO" \
  "$(jqok '.env | (has("UV_EXCLUDE_NEWER") or has("PIP_UPLOADED_PRIOR_TO")) | not')"
check "template: .npmrc min-release-age=7" "$(has_line "$PROJECT/.npmrc" 'min-release-age=7')"
check "template: pnpm minimumReleaseAge 10080" \
  "$(has_line "$PROJECT/pnpm-workspace.yaml" 'minimumReleaseAge: 10080')"
check "template: uv exclude-newer P7D" "$(has_line "$PROJECT/uv.toml" 'exclude-newer = "P7D"')"

check "npm dependency scripts off in env and template" \
  "$(jqok '.env.npm_config_ignore_scripts == "true"' | grep -q 1 \
     && has_line "$PROJECT/.npmrc" 'ignore-scripts=true')"

# Every command that picks a new package, runs one ad hoc, or changes the
# machine must prompt, as must leaving the sandbox and the excluded commands'
# operations that change something outside this machine.
required_ask='[
  "Bash(npm install *)", "Bash(npm i *)", "Bash(npm add *)", "Bash(npm update *)",
  "Bash(npm exec *)", "Bash(npx *)",
  "Bash(pnpm add *)", "Bash(pnpm update *)", "Bash(pnpm up *)", "Bash(pnpm dlx *)",
  "Bash(yarn add *)", "Bash(yarn dlx *)", "Bash(bun add *)", "Bash(bunx *)",
  "Bash(uv add *)", "Bash(uv pip install *)", "Bash(uv tool install *)",
  "Bash(uv tool run *)", "Bash(uvx *)", "Bash(pipx install *)", "Bash(pipx run *)",
  "Bash(brew install *)", "Bash(brew reinstall *)", "Bash(brew upgrade *)",
  "Bash(brew tap *)", "Bash(brew bundle *)",
  "Bash(git push *)", "Bash(terraform apply *)", "Bash(terraform destroy *)",
  "Bash(terraform import *)", "Bash(gh pr merge *)", "Bash(gh repo delete *)",
  "Bash(gh release create *)", "Bash(gh api *)",
  "Bash(dangerouslyDisableSandbox:true)"
]'
missing="$(jq -r --argjson req "$required_ask" \
  '($req - (.permissions.ask // [])) | join(", ")' "$SETTINGS" 2>/dev/null || echo unreadable)"
[ -z "$missing" ] && c=1 || c=0
check "ask covers every install-class command${missing:+ (missing: $missing)}" "$c"

# Python installs go through uv, so pip's install forms are denied outright,
# and so are installs into a global location; a deny also outranks the
# matching ask above and any allow a teammate adds locally.
bash_deny='["Bash(pip install *)", "Bash(pip3 install *)",
            "Bash(python -m pip install *)", "Bash(python3 -m pip install *)",
            "Bash(npm install -g *)", "Bash(npm i -g *)", "Bash(npm install --global *)",
            "Bash(pnpm add -g *)", "Bash(uv pip install --system *)"]'
missing="$(jq -r --argjson req "$bash_deny" \
  '($req - (.permissions.deny // [])) | join(", ")' "$SETTINGS" 2>/dev/null || echo unreadable)"
[ -z "$missing" ] && c=1 || c=0
check "deny covers pip and global installs${missing:+ (missing: $missing)}" "$c"
# Tool installers stay ask: a CLI tool sometimes belongs in a global location.
check "uv tool install and pipx are asked, not denied" \
  "$(jqok '(.permissions.deny | any(test("^Bash\\((uv tool|pipx) ")) | not)')"

# Remaining deny entries: Read rules anchored with ~/ or **/ so they mean the
# same path in every repository. No ! carve-outs: the sandbox lists them
# verbatim as deny paths, and no exemption could be shown (ADR-0017).
check "other deny entries are portable Read rules without carve-outs" \
  "$(jq -e --argjson bash "$bash_deny" '(.permissions.deny - $bash) as $rest
           | ($rest | length > 0) and all($rest[]; test("^Read\\((~/|\\*\\*/)"))' \
     "$SETTINGS" >/dev/null 2>&1 && echo 1 || echo 0)"

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
