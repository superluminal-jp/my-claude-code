# Phase 0 Research: GitHub Security Alert Auto-Response

All items below were resolved by inspecting the live repository (`gh api`) rather than assumed, per the repo's Accuracy principle.

## 1. What is already enabled on this repository?

**Finding** (via `gh api repos/superluminal-jp/my-claude-code`):

| Setting | Current state |
|---|---|
| `dependabot_security_updates` | `enabled` |
| `secret_scanning` | `enabled` |
| `secret_scanning_push_protection` | `enabled` |
| `secret_scanning_non_provider_patterns` | `disabled` |
| `secret_scanning_validity_checks` | `disabled` |
| `vulnerability-alerts` endpoint | `204` (enabled) |
| `code-scanning/default-setup` | `state: "not-configured"`, but `languages: ["python"]` — GitHub has already identified Python as a scannable language via `gh api .../languages` (`Python: 35447` bytes, from `.specify/extensions/git/scripts/python/*.py`) |
| `allow_auto_merge` | `false` |
| `branches/main/protection` (classic) | `404` — no classic branch protection configured |
| `rulesets` (branch target) | `[]` — no repository ruleset configured either |
| `dependabot/alerts` | `[]` — none open currently |

**Decision**: Do not re-enable what is already on (FR-001, FR-007, FR-008 are satisfied today). Scope the implementation to the four real gaps: CI required check, a `main`-protecting ruleset, `allow_auto_merge`, CodeQL default setup, and the auto-merge workflow itself.

**Alternatives considered**: Re-declaring all settings idempotently via a single setup script regardless of current state — rejected as unnecessary churn; a plan step that checks-then-sets is preferable and matches the "no redundant action" principle, and avoids accidentally toggling `secret_scanning_non_provider_patterns` / `validity_checks` (which were deliberately left off and are out of this feature's requested scope).

## 2. How should "patch/minor auto-merge only" be implemented without a routine-vs-security PR ambiguity?

**Problem**: FR-004 requires that Dependabot pull requests be excluded from auto-merge unless they were raised for a detected vulnerability. Dependabot's PR payload does not carry a clean, stable "this PR exists because of alert #N" boolean that `dependabot/fetch-metadata` exposes as a first-class output.

**Decision (corrected 2026-08-22, verified against GitHub's own docs before implementation)**: Do not create `.github/dependabot.yml` at all. GitHub's official docs confirm two facts that supersede the original plan for this file:

1. Dependabot security updates fire automatically off the dependency graph once enabled in repo settings — they require **no** `dependabot.yml`. This repo already has `dependabot_security_updates: enabled` (research.md §1), so FR-002/FR-003 need no config file to work.
2. Every entry in `dependabot.yml`'s `updates:` array has a **required** `schedule.interval` field — there is no schema-valid way to "register an ecosystem" without also configuring a scheduled cadence. Adding a `github-actions` entry to get on the dependency graph, as originally planned, would therefore *necessarily* turn on routine version-update PRs — the opposite of what this decision is trying to achieve. (`open-pull-requests-limit: 0` can suppress those routine PRs while keeping the entry, but security-update PRs are documented as exempt from that limit and unaffected by it either way — so the limit buys nothing here.)

Net effect: with no `dependabot.yml` in the repo, there is no `updates:` entry for any ecosystem, so there is structurally no routine version-update PR stream — every Dependabot-authored PR is, by construction, a security-update PR. This achieves the exact same outcome as the original plan (FR-004's "routine vs. security" distinction collapses into "is the PR author `dependabot[bot]`") with one fewer file and no schema contradiction.

**Alternatives considered**:
- *Original plan: create `dependabot.yml` with a schedule-less `github-actions` entry*: rejected on verification — not expressible in the schema (`schedule` is required); would have silently introduced routine PRs instead of preventing them.
- *`dependabot.yml` with `open-pull-requests-limit: 0`*: rejected as unnecessary — adds a file and a schedule for a suppression effect that only applies to version updates, which are already absent by simply not creating the file. Revisit only if the repo later gains a real package manifest and needs *scheduled* routine updates for it (at which point `open-pull-requests-limit: 0` remains available for ecosystems that should stay security-only).
- *Label-based filtering* (only auto-merge PRs with a `security` label): rejected — Dependabot does not reliably attach a distinguishing label to security-triggered PRs by default; would require an extra classification step with no authoritative source.
- *Title/branch-name pattern matching*: rejected — brittle, not a documented/stable contract from GitHub, would silently break on a Dependabot format change.

## 3. How is "all required checks pass" enforced so auto-merge can't bypass an unconfigured gate?

**Decision**: Sequence matters. A **repository ruleset** targeting `main`, with a `required_status_checks` rule listing `ci.yml`'s `test` job, must be created *before* the auto-merge workflow is allowed to act, and native GitHub PR auto-merge (`gh pr merge --auto`, gated by the `allow_auto_merge` repo setting) is used instead of a workflow that polls check status itself. GitHub's own merge-queue logic — not custom workflow code — refuses to complete the merge until every required check reports success; this directly satisfies the Edge Case ("absence of a required check must not be treated as passed") because `--auto` merge with no required checks configured merges immediately, which is exactly why the ruleset must be in place first.

**Ruleset vs. classic branch protection**: GitHub now offers two mechanisms for this — the classic `branches/{branch}/protection` API/UI, and the newer repository **Rulesets** (`repos/{owner}/{repo}/rulesets`). Both were evaluated; Rulesets was chosen: it is GitHub's actively-developed direction (new protection capabilities land there, not in classic), it supports per-rule bypass lists scoped to specific actors/apps/teams rather than an all-or-nothing admin bypass, and — relevant to this repo's general preference for config-as-code (see prior discussion in this feature's conversation history) — a ruleset can be exported as JSON and re-imported, which classic branch protection cannot. This repo has neither configured yet (confirmed `rulesets` returns `[]`, in addition to the classic endpoint's `404`), so there is no migration cost either way.

**Alternatives considered**:
- *Classic branch protection*: rejected — no longer where GitHub adds capability, and has no export/import story, unlike Rulesets.
- *A custom workflow step that queries the Checks API in a loop and merges once green*: rejected as reinventing what `gh pr merge --auto` + a required-status-check rule already does correctly and more safely (native auto-merge re-evaluates on every check update via GitHub's own event system, not a fixed poll/timeout).

## 4. How is the `pull_request_target` supply-chain risk mitigated?

**Problem**: Reacting to a Dependabot PR from a forked-PR-style trigger context requires `pull_request_target` (to get a token with write access, since Dependabot PRs are treated similarly to external contributions for permission purposes on some repo configurations). `pull_request_target` workflows that `actions/checkout` the PR's head ref and then run its code are a known GitHub Actions supply-chain vulnerability class (the checked-out code can exfiltrate the workflow's write-scoped token).

**Decision**: The auto-merge workflow triggered on `pull_request_target` MUST NOT check out the PR's head content and MUST NOT execute anything from the PR diff. It only calls `dependabot/fetch-metadata@v2` (which reads PR metadata via the API, not by checking out code) to get `update-type` and `dependency-type`, then conditionally runs `gh pr review --approve` / `gh pr merge --auto` against the PR number — both operate purely through the GitHub API using the workflow's own token, never executing PR-supplied code.

**Alternatives considered**: Using plain `pull_request` trigger — rejected because `GITHUB_TOKEN` in a `pull_request`-triggered workflow run by `dependabot[bot]` is read-only by default on this repo (no evidence of an org-level override), which would prevent the approve/merge calls from succeeding.

## 5. Is there a required-check workflow to gate on at all?

**Finding**: No `.github/workflows/` exists yet (confirmed via `find`). `tests/run-*.sh` exist and run locally but are not wired into CI.

**Decision**: Add `ci.yml` running the four existing `tests/run-*.sh` scripts on `push`/`pull_request` to `main`. This is a prerequisite for the whole feature (nothing to require-status-check on otherwise) and is in scope here rather than deferred, per the spec's Assumptions section.

**Alternatives considered**: Skipping CI and gating auto-merge only on Dependabot's own PR checks (if any) — rejected; Dependabot PRs carry no repo-specific test signal on their own, so skipping this would make FR-003's "all required checks pass" vacuously true and defeat SC-005.
