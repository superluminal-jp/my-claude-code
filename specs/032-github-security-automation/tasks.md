---

description: "Task list for GitHub Security Alert Auto-Response"
---

# Tasks: GitHub Security Alert Auto-Response

**Input**: Design documents from `/specs/032-github-security-automation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/dependabot-automerge-workflow.md, quickstart.md

**Tests**: No dedicated test framework exists for GitHub Actions/repo-setting behavior; verification is done via the `quickstart.md` scenarios (referenced directly from tasks below) rather than a separate test suite.

**Organization**: Tasks are grouped by user story (spec.md) so each can be validated independently. Any task that mutates a live GitHub repository setting (branch protection, `allow_auto_merge`, CodeQL default setup) is explicitly marked **[CONFIRM]** — per `.claude/rules/permissions.md`, these require pausing for explicit user confirmation before execution; they are not silently auto-applied even under an otherwise autonomous run.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)
- **[CONFIRM]**: Mutates a live repository setting — requires explicit user confirmation first (permissions.md)

## Path Conventions

This repository has no `src/`/application layer. All new files live under `.github/`; documentation updates touch `README.md`/`README.ja.md`; the ADR lives under `docs/adr/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the platform-level baseline research.md documented hasn't drifted since it was captured, and create the `.github/workflows/` directory the rest of the feature writes into.

- [X] T001 Create the `.github/workflows/` directory. **No `.github/dependabot.yml` is created** — verified against GitHub's own docs (research.md §2, corrected 2026-08-22) that Dependabot security updates fire off the dependency graph without one, and any `updates:` entry would force a required `schedule` field, which would reintroduce the routine version-update PRs this feature deliberately avoids.
- [X] T002 [P] Re-run `gh api repos/superluminal-jp/my-claude-code --jq '.security_and_analysis'` and `gh api repos/superluminal-jp/my-claude-code/vulnerability-alerts -i` and confirm they still match research.md §1 (`dependabot_security_updates`, `secret_scanning`, `secret_scanning_push_protection` all `enabled`; alerts endpoint `204`) before proceeding — flag and stop on any drift

**Checkpoint**: Baseline confirmed current; workflow directory ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The CI check and the branch-protection gate that reads it. US1's auto-merge decision has nothing safe to key off until this exists.

**⚠️ CRITICAL**: T005/T006 are **[CONFIRM]** — do not execute until the user has explicitly approved mutating live repo settings.

- [X] T003 Create `.github/workflows/ci.yml` running `tests/run-mcp-startup.sh`, `tests/run-install.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-removed-guardrails.sh` on `push` and `pull_request` targeting `main`, with a stable, named job (this job name is what branch protection will require)
- [ ] T004 Open a throwaway PR (or push to a scratch branch) to confirm `ci.yml` runs and reports its job name as a status context, then delete/close the scratch PR
- [X] T005 **[CONFIRM]** Create a repository ruleset targeting `main` requiring `ci.yml`'s `test` job as a required status check (chosen over classic branch protection — see research.md §3). Source of truth: `.github/rulesets/main-required-checks.json`. Applying it via `gh api POST repos/.../rulesets` from Claude's own Bash tool was blocked by this session's auto-mode classifier (mutating live repo settings), so the user ran the identical `gh api --method POST ... --input .github/rulesets/main-required-checks.json` command themselves — created as ruleset id `21189320`, `enforcement: active`, `required_status_checks: [{"context": "test"}]`, confirmed via `gh api repos/.../rulesets`
- [X] T006 **[CONFIRM]** Enable the `allow_auto_merge` repository setting — run by the user (blocked for Claude's own Bash tool by the same classifier as T005); confirmed `allow_auto_merge: true` in the response

**Checkpoint**: A required, working CI gate exists; auto-merge is possible but nothing yet requests it.

---

## Phase 3: User Story 1 - Dependency vulnerability is patched without waiting on a human (Priority: P1) 🎯 MVP

**Goal**: A patch/minor Dependabot security-fix PR merges itself once CI is green, with zero human clicks.

**Independent Test**: quickstart.md §4 — watch a real (or simulated) patch/minor Dependabot PR go from opened → CI green → merged, with `mergedBy` showing the automation, not a human account.

### Implementation for User Story 1

- [X] T007 [US1] Create `.github/workflows/dependabot-automerge.yml` per `contracts/dependabot-automerge-workflow.md`: `pull_request_target` trigger, `github.actor == 'dependabot[bot]'` guard, `dependabot/fetch-metadata@v2` step, `update-type` guard for `version-update:semver-patch`/`-minor`, least-privilege `permissions:` block, no checkout of PR head content, `gh pr merge --auto --squash` on guard pass
- [ ] T008 [US1] **Partially done**: quickstart.md §2 validated — `gh api repos/.../rulesets/21189320 --jq '...required_status_checks[].context'` returns `test`. quickstart.md §4 (a real patch/minor Dependabot PR auto-merging end-to-end) is **still pending** — `gh api repos/.../dependabot/alerts` is currently `[]`, so there is no live PR to observe yet. Re-run §4 the first time a real Dependabot security PR opens, or note it in this checkbox once observed.

**Checkpoint**: User Story 1 is independently functional — patch/minor security fixes self-merge.

---

## Phase 4: User Story 2 - Major or otherwise risky dependency fixes wait for a human (Priority: P2)

**Goal**: Nothing outside a clean patch/minor security fix ever merges unattended.

**Independent Test**: quickstart.md §5 — a major-version Dependabot PR triggers the workflow but takes no merge action; `autoMergeRequest` stays `null`.

### Implementation for User Story 2

- [X] T009 [US2] Confirm the repository still has no `.github/dependabot.yml` (`test -f .github/dependabot.yml` fails), so there is structurally no routine (non-security) Dependabot PR stream — this is what makes the "routine vs. security" distinction in FR-004 trivially satisfiable by the `update-type` guard alone (research.md §2); document the check in this task
- [ ] T010 [US2] **Pending**: no Dependabot PR (major or otherwise) is currently open (`dependabot/alerts` is `[]`), so quickstart.md §5 cannot be exercised live yet. The negative guard itself is inspectable statically today: `.github/workflows/dependabot-automerge.yml`'s merge step only runs `if: update-type == semver-patch || semver-minor`, so a `semver-major` (or any other) value falls through to no-op by construction — re-run §5 for live confirmation the first time a major-version Dependabot PR appears

**Checkpoint**: User Stories 1 and 2 both hold — safe fixes auto-merge, risky ones don't.

---

## Phase 5: User Story 3 - Code-level and secret-exposure alerts are surfaced, not silently merged (Priority: P3)

**Goal**: CodeQL findings and secret detections are visible and (for secrets) blocked pre-emptively, with no automatic fix/merge path.

**Independent Test**: quickstart.md §6 (secret push blocked) and §7 (CodeQL alert surfaced, nothing auto-merged).

### Implementation for User Story 3

- [X] T011 [US3] **[CONFIRM]** Enable CodeQL default setup for Python — run by the user; confirmed `state: "configured"`, `languages: ["python"]`, `schedule: "weekly"` via `gh api repos/.../code-scanning/default-setup`
- [X] T012 [P] [US3] Ran quickstart.md §7 live on scratch branch `scratch/codeql-alert-test` (PR #59, closed & branch deleted). First two attempts (`shell=True`, hardcoded-credentials) produced **zero** alerts — the run log showed the actually-active query list doesn't include `py/subprocess-popen-with-shell-equals-true` or `py/hardcoded-credentials` (this repo's "default" CodeQL suite is a curated Security query pack, narrower than assumed). Third attempt (`tempfile.mktemp()`) matched `py/insecure-temporary-file`, which *was* in the active list — alert #1 fired (`severity: high`, `state: open`), confirming FR-005/FR-006: alert surfaced, nothing auto-merged (PR was human-authored, so `dependabot-automerge.yml`'s actor guard never even ran). Alert dismissed afterward as `used in tests`.
- [ ] T013 [P] [US3] **Ran (4 attempts total across two sessions), result still contradicts FR-008 for AWS-shaped secrets — investigated, root cause not confirmed, checkbox intentionally left open rather than marked passing.**
  - (1) AWS's canonical placeholder `AKIAIOSFODNN7EXAMPLE` — not blocked, no alert (ever, incl. next-day recheck).
  - (2) Google API Key-shaped value (`AIza...`) — not blocked, but *did* get an async alert within seconds. Expected per GitHub's supported-patterns doc: Google API Key is detection-only, not push-protection-eligible — not a gap.
  - (3) Fresh (non-"EXAMPLE") 20-char AWS Access Key ID + a 38-char secret (wrong length) — not blocked, no alert.
  - (4) Retest with a *correctly-formatted* pair (20-char ID matching `AKIA[A-Z0-9]{16}`, exactly 40-char secret matching the base64-ish charset, per GitHub's docs noting `aws_access_key_id` "requires pairing" with `aws_secret_access_key`) — still not blocked, still no alert, even after ~90s of polling.
  - **Ruled out**: famous-placeholder allowlist (attempt 3 used a fresh non-placeholder key), pairing/length mismatch (attempt 4 used exact documented lengths), org-level policy override (confirmed via `gh api repos/.../` that `superluminal-jp` is a personal `User` account, not an Organization — no org policy layer exists), and async processing delay (checked next-day for attempts 1–3, ~90s polling for attempt 4).
  - **Not ruled out / not testable further from here**: an AWS-specific structural or checksum validation beyond the publicly documented regex (real AWS access key IDs encode structured data via a base32-like scheme; GitHub may validate against that structure, which a naively-random-but-regex-matching string would fail) — this would require either a genuinely-issued-but-revoked AWS key or GitHub Support/docs access neither of which this session has.
  - **Recommendation**: don't treat FR-008 as verified for AWS-shaped secrets specifically. If this matters in practice, either (a) open a GitHub Support inquiry asking why a `AKIA[A-Z0-9]{16}` + 40-char-secret pair isn't detected on this repo, or (b) treat the async-detection path (confirmed working for Google API Key) as the safety net for this repo generally, and don't rely on push protection alone for AWS-shaped credentials until this is explained. All 4 test branches/alerts were cleaned up (branches deleted, the Google-key alert resolved as `used in tests`).

**Checkpoint**: All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Close the documentation and decision-record gates raised in plan.md's Constitution Check.

- [X] T014 [P] Added "Repository security automation" to `README.md` and "リポジトリのセキュリティ自動化" to `README.ja.md`, plus a `.github/` entry in each File structure tree
- [X] T015 Authored `docs/adr/0012-dependabot-automerge-scope.md` via the `adr` skill — covers both the auto-merge-scope decision and the Rulesets-over-classic-branch-protection decision together (they serve the same architectural goal and were decided in the same session), with rejected alternatives from research.md §2–§4
- [X] T016 Re-ran quickstart.md §1–§3 plus `allow_auto_merge` after all settings landed: `security_and_analysis` unchanged from research.md §1, `vulnerability-alerts` still `204`, ruleset `21189320` still requires `test`, CodeQL `state: "configured"`, `allow_auto_merge: true`. §4/§5 remain genuinely pending a real Dependabot PR (see T008/T010); §6/§7 were exercised live under T012/T013, with T013 surfacing a real finding against FR-008 rather than a clean pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001's `.github/workflows/` directory must exist before `ci.yml` can be written there). T005/T006 (**[CONFIRM]**) block all of Phase 3.
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion — cannot validate auto-merge without the CI gate and `allow_auto_merge`.
- **User Story 2 (Phase 4)**: Depends only on Setup (T001) and User Story 1's workflow file (T007) existing, since it validates the *same* workflow's negative case — can start once T007 lands.
- **User Story 3 (Phase 5)**: Independent of Phases 2–4 entirely (CodeQL/secret scanning share no file or setting with the auto-merge path) — can run in parallel with Phase 3/4 once Phase 1 completes.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### Parallel Opportunities

- T002 can run alongside T001.
- Once Phase 1 completes, Phase 5 (US3) can proceed fully in parallel with Phases 2–4, since it touches none of the same files or settings.
- T012 and T013 (both US3, different scratch branches) can run in parallel.
- T014 (README) can start as soon as the behavior it documents (Phases 2–5) is implemented, in parallel with T015 (ADR).

---

## Parallel Example: User Story 3 (fully independent of US1/US2)

```bash
# Once Phase 1 (T001, T002) is done, these can run in parallel with Phase 2-4 work:
Task: "Enable CodeQL default setup for Python [CONFIRM] (T011)"
# ...then, once T011 is confirmed and applied:
Task: "Validate code-scanning alert surfacing via quickstart.md §7 (T012)"
Task: "Validate secret push protection via quickstart.md §6 (T013)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational) — **pause for explicit confirmation at T005/T006**.
3. Complete Phase 3 (User Story 1) — patch/minor auto-merge is now live.
4. **STOP and VALIDATE**: run quickstart.md §4 for real before adding US2/US3 scope.

### Incremental Delivery

1. Setup + Foundational → CI gate exists, auto-merge possible but unused.
2. Add User Story 1 → patch/minor security fixes self-merge (MVP).
3. Add User Story 2 → verify the negative case (major/routine PRs stay manual) — mostly a validation pass over what T007/T001 already built.
4. Add User Story 3 → CodeQL + secret-scanning visibility, independent of the merge path.
5. Polish → README, ADR, final quickstart re-run.

---

## Notes

- Every **[CONFIRM]** task mutates live GitHub repository state and must not be executed without the user's explicit go-ahead in this session, per `.claude/rules/permissions.md` ("modifying CI/CD pipelines" / repo-setting mutation is a self-apply confirmation item).
- Commit after each task or logical group, per `.claude/rules/git-workflow.md` (one logical change per commit; only commit when asked).
- T009 and T012/T013 rely on scratch branches specifically so no vulnerable/secret content is ever proposed against `main`.
