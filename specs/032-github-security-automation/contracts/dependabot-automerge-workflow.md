# Contract: `dependabot-automerge.yml` workflow

This is the one externally-observable interface this feature adds (a GitHub Actions workflow other automation/contributors can trigger and observe). Documented as a contract because getting its permission scope wrong is a supply-chain risk, not just a style choice (see research.md § 4).

## Trigger

- Event: `pull_request_target`
- Types: `opened`, `synchronize`, `reopened`
- Branches: PRs targeting `main` only

## Guard conditions (all must hold, evaluated in order — short-circuits otherwise)

1. `github.actor == 'dependabot[bot]'` — refuses to run its merge logic for any human- or other-bot-authored PR.
2. `dependabot/fetch-metadata@v2` output `update-type` is exactly `version-update:semver-patch` or `version-update:semver-minor`.

If either guard fails, the workflow exits without approving or merging — the PR is left exactly as GitHub created it (FR-004).

## Permissions (least privilege)

```yaml
permissions:
  contents: write        # required to trigger a merge
  pull-requests: write    # required to approve/enable auto-merge
```

No `checkout` step runs against the PR's head ref anywhere in this workflow — it must only call the GitHub API (via `dependabot/fetch-metadata`, `gh pr review`, `gh pr merge`), never execute code from the PR diff. This is the mitigation for the `pull_request_target` risk in research.md § 4; a future edit to this workflow that adds a checkout of `github.event.pull_request.head.sha` followed by running any script from that checkout would reintroduce the vulnerability class and must be rejected in review.

## Effect

- On guard pass: `gh pr review --approve` (if the repo's branch protection requires an approving review) followed by `gh pr merge --auto --squash`.
- Actual merge completion is deferred to GitHub's native auto-merge mechanism, which waits for `ci.yml`'s required status check to report success (see data-model.md, "State transitions").
- On guard fail: no-op; workflow run shows as skipped/passed with no side effect.

## Non-goals

- Does not merge major-version Dependabot PRs (left for manual review — FR-004).
- Does not act on non-Dependabot PRs under any condition.
- Does not modify, dismiss, or otherwise touch code-scanning or secret-scanning alerts.
