---
status: Accepted
date: 2026-08-22
deciders: Taiki Ogihara, Claude
---

# 0012. Scope Dependabot auto-merge to patch/minor security PRs, gated by a required CI check

## Context and problem statement

GitHub already detects vulnerabilities in this repository (Dependabot alerts,
CodeQL, secret scanning), but nothing acted on that detection automatically —
every fix required a human to notice the alert, open the fix PR (or wait for
one), and merge it by hand. We want low-risk dependency fixes to close their
exposure window without waiting on a human, while not letting anything
higher-risk merge unattended. This requires two coupled decisions: (1) which
Dependabot pull requests are safe to auto-merge, and (2) what mechanism
enforces that nothing merges — auto or manual — before CI passes.

## Decision drivers

- Auto-merge must never be able to bypass an unconfigured or partially
  configured check gate (a missing required check must not be treated as
  "passed").
- Distinguishing "this PR exists because of a detected vulnerability" from
  "this is a routine, non-security update" must rely on a signal GitHub
  itself guarantees, not on a pattern we infer.
- The branch-protection mechanism should match GitHub's actively maintained
  direction, since it will keep this repository's `main` protected for the
  life of the project.

## Considered options

- **Auto-merge scope**: (a) auto-merge all Dependabot PRs, (b) auto-merge
  patch/minor Dependabot PRs regardless of why they were opened, filtered by
  label or title pattern to exclude routine updates, (c) auto-merge
  patch/minor Dependabot PRs only, with no `.github/dependabot.yml`
  `updates:` entries at all so every Dependabot PR is by construction a
  security-update PR.
- **Required-check gate mechanism**: (a) classic branch protection
  (`branches/{branch}/protection`), (b) a repository ruleset, (c) a custom
  GitHub Actions workflow that polls the Checks API and merges once green.

## Decision outcome

We will auto-merge only Dependabot-authored pull requests whose
`dependabot/fetch-metadata` `update-type` is `version-update:semver-patch` or
`version-update:semver-minor`, with **no `.github/dependabot.yml`** in the
repository at all — because GitHub's Dependabot security updates already work
directly off the dependency graph without one, and any `updates:` entry
requires a `schedule`, which would necessarily introduce a routine,
non-security update stream (verified against GitHub's own docs: security
updates are exempt from `open-pull-requests-limit`, and `schedule.interval`
is a required key for every `updates:` entry — there is no schema-valid way
to register an ecosystem without also scheduling routine updates for it).
With no `updates:` entries, every Dependabot PR on this repo is, by
construction, a response to a detected vulnerability, so the `update-type`
guard alone is sufficient to satisfy "only merge security fixes automatically."

For the required-check gate, we will use a **repository ruleset** targeting
`main` (`.github/rulesets/main-required-checks.json`, requiring the `ci.yml`
workflow's `test` job), created before `allow_auto_merge` is enabled — because
Rulesets is where GitHub adds new protection capability going forward (not
classic branch protection), it supports per-actor bypass lists instead of an
all-or-nothing admin bypass, and — unlike classic branch protection — it can
be exported and re-imported as JSON, which keeps this decision closer to
config-as-code even though GitHub does not auto-apply that JSON on push.

Merge completion itself is left to GitHub's native `gh pr merge --auto`
(triggered by the `dependabot-automerge.yml` workflow), not a custom
polling workflow: native auto-merge re-evaluates on every check-status event
and refuses to complete while any required check is failing or unreported,
which is exactly the invariant we need and is safer than reimplementing that
logic ourselves.

### Consequences

- Positive: a patch/minor Dependabot security fix goes from "detected" to
  "merged" with zero manual pull-request actions, as long as CI passes.
- Positive: the "security vs. routine" distinction needs no fragile
  label/title inference — it falls out of simply not configuring scheduled
  version updates.
- Positive: the ruleset JSON in `.github/rulesets/` documents the intended
  branch-protection state even though GitHub won't auto-sync it from a push.
- Negative: if this repository later gains a real package manifest (npm,
  pip, etc.) and someone adds a `dependabot.yml` `updates:` entry with a
  `schedule` for routine version updates, the "every Dependabot PR is a
  security PR" assumption silently breaks unless `open-pull-requests-limit`
  or an equivalent exclusion is added at the same time — reviewers should
  treat any future `dependabot.yml` addition as touching this decision.
- Negative: `.github/rulesets/main-required-checks.json` is a manually
  re-applied artifact, not a live sync target — GitHub's Rulesets UI/API
  offers no import path we could find in this session's testing (the "Add
  branch ruleset" flow had no corresponding import option), so the JSON can
  drift from the live ruleset if either is edited without the other.
- Negative: major-version Dependabot PRs and all non-Dependabot PRs still
  require a human to notice and merge them — this decision only removes
  toil for the lowest-risk case.

## Confirmation

- `.github/workflows/dependabot-automerge.yml`'s merge step is gated by an
  explicit `if:` on `update-type`; a change that broadens this condition
  should be caught in code review, not by an automated check.
- `test -f .github/dependabot.yml` failing (i.e., the file staying absent)
  is the structural guarantee behind "every Dependabot PR is a security PR";
  `specs/032-github-security-automation/tasks.md` T009 records this check.
- `gh api repos/superluminal-jp/my-claude-code/rulesets` should always list
  an active ruleset targeting `main` with `test` as a required status check
  (`specs/032-github-security-automation/quickstart.md` §2).

## Pros and cons of the options

### Auto-merge scope: label/title filtering (rejected)

- Good: would work even if `dependabot.yml` `updates:` entries existed later.
- Bad: Dependabot does not reliably attach a distinguishing label to
  security-triggered PRs by default; title/branch-name patterns are not a
  documented, stable GitHub contract and could silently break.

### Required-check gate: classic branch protection (rejected)

- Good: simpler, single-page UI; well understood.
- Bad: GitHub is not adding new capability there; no export/import story,
  unlike Rulesets.

### Required-check gate: custom polling workflow (rejected)

- Good: full control over merge timing/logic.
- Bad: reinvents what `gh pr merge --auto` plus a required-status-check rule
  already does correctly — native auto-merge reacts to check events directly
  rather than on a fixed poll interval, and is less code to maintain and
  audit.

## More information

- `specs/032-github-security-automation/spec.md`, `plan.md`, `research.md`
  (§§1-5), `contracts/dependabot-automerge-workflow.md`.
- Live verification performed in the deciding session: `gh api` audit of
  `superluminal-jp/my-claude-code`'s existing `security_and_analysis`
  settings, GitHub docs lookups confirming `schedule` is a required
  `dependabot.yml` key and that security updates are exempt from
  `open-pull-requests-limit`, and a real PR (#58) exercising `ci.yml` and
  the ruleset end-to-end before merge.
