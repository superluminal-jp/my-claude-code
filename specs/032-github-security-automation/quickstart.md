# Quickstart: Validating GitHub Security Alert Auto-Response

Prerequisites: `gh` CLI authenticated against `superluminal-jp/my-claude-code` with admin rights on the repo (needed to read/set the branch ruleset and repo settings).

## 1. Confirm baseline settings (should already be true — see research.md § 1)

```bash
gh api repos/superluminal-jp/my-claude-code --jq '.security_and_analysis'
gh api repos/superluminal-jp/my-claude-code/vulnerability-alerts -i   # expect HTTP 204
```

## 2. Confirm the new CI check exists and is required

```bash
gh api repos/superluminal-jp/my-claude-code/rulesets --jq '.[] | select(.target=="branch")'
# note the id of the ruleset targeting main, then:
gh api repos/superluminal-jp/my-claude-code/rulesets/<id> \
  --jq '.rules[] | select(.type=="required_status_checks") | .parameters.required_status_checks[].context'
# expect "test" (the ci.yml job name) to be listed
```

## 3. Confirm CodeQL default setup is active

```bash
gh api repos/superluminal-jp/my-claude-code/code-scanning/default-setup --jq '.state'
# expect "configured"
```

## 4. End-to-end: patch/minor Dependabot PR auto-merges

1. Open (or wait for) a Dependabot security-fix PR against a `github-actions` dependency with a patch/minor fix available (e.g., bump a pinned `actions/checkout@vX` to a patched patch release).
2. Watch the PR: `gh pr checks <PR#>` until `ci.yml`'s check reports success.
3. Confirm no human clicked merge: `gh pr view <PR#> --json mergedBy,autoMergeRequest`.
4. Expected: `autoMergeRequest` was set by the `dependabot-automerge.yml` run, and the PR shows merged with `mergedBy` reflecting the automation's identity (`github-actions[bot]` or the PAT/App used), not a human account.

## 5. End-to-end: major-version Dependabot PR is left alone

1. Open (or simulate via a draft PR authored as `dependabot[bot]`) a major-version bump PR.
2. Confirm `dependabot-automerge.yml` ran (workflow run visible) but took no merge action: `gh run view <run-id> --log | grep -i "update-type"` shows `version-update:semver-major`, and `gh pr view <PR#> --json autoMergeRequest` is `null`.

## 6. End-to-end: secret push is blocked

1. Attempt to push a commit containing a recognizable test credential pattern (e.g., a GitHub-recognized dummy token format) on a scratch branch.
2. Expected: the push is rejected client-side by push protection before it reaches any remote branch; `git push` output names the detected secret type and a bypass URL.

## 7. End-to-end: code-scanning alert is surfaced, not auto-fixed

1. Introduce a known-insecure pattern in one of the `.specify/extensions/git/scripts/python/*.py` files on a scratch branch (e.g., `subprocess.run(cmd, shell=True)` with untrusted input) and push it.
2. After the CodeQL workflow run completes: `gh api repos/superluminal-jp/my-claude-code/code-scanning/alerts --jq '.[].rule.id'` includes the corresponding CodeQL rule.
3. Confirm no pull request or commit was auto-generated in response — the alert exists, nothing merged (FR-006).

## Rollback

- Disable the auto-merge workflow's effect immediately by setting `allow_auto_merge` back to `false` (`gh api -X PATCH repos/superluminal-jp/my-claude-code -f allow_auto_merge=false`) — existing auto-merge requests on open PRs are cancelled, no history is rewritten.
- Branch protection and CodeQL default setup can each be reverted independently without affecting the other.
