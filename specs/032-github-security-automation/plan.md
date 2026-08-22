# Implementation Plan: GitHub Security Alert Auto-Response

**Branch**: `032-github-security-automation` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/032-github-security-automation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Close the gap between "GitHub detects a vulnerability" and "the repository is actually protected," for the three alert categories GitHub raises on this repo (Dependabot dependency alerts, CodeQL code-scanning alerts, secret-scanning alerts). A `gh api` audit of the live repository (`superluminal-jp/my-claude-code`, public) found Dependabot security updates, secret scanning, and secret-scanning push protection **already enabled** at the account/repo-settings level — so FR-001, FR-007, and FR-008 are largely satisfied already. The real gaps are: (1) no required CI check exists yet, so there is nothing for auto-merge to gate on; (2) `allow_auto_merge` is `false` and `main` has no branch protection, so nothing can auto-merge even once a check exists; (3) CodeQL default setup is `not-configured` even though the repo has a real CodeQL-supported language (Python, via `.specify/extensions/git/scripts/python/*.py`); (4) there is no workflow that turns a green, patch/minor Dependabot PR into a merged commit. The plan adds a minimal CI workflow (runs the existing `tests/run-*.sh` scripts), turns on required-status-check branch protection + `allow_auto_merge` + CodeQL default setup, and adds a scoped `pull_request_target` auto-merge workflow restricted to `dependabot[bot]` patch/minor PRs.

## Technical Context

**Language/Version**: N/A — no single application language. Surface area is GitHub Actions workflow YAML plus the repo's existing Python 3.x scripts (`.specify/extensions/git/scripts/python/*.py`), which become CodeQL's scan target.

**Primary Dependencies**: GitHub Dependabot (security updates — already enabled), GitHub CodeQL default setup (language: Python, currently `not-configured`), GitHub Secret Scanning + Push Protection (already enabled), GitHub Actions (`actions/checkout`, `dependabot/fetch-metadata@v2`), GitHub branch protection (required status checks), GitHub native PR auto-merge (`allow_auto_merge` repo setting).

**Storage**: N/A

**Testing**: `tests/run-mcp-startup.sh`, `tests/run-install.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-removed-guardrails.sh` — exist today but do not run in CI. This feature adds the GitHub Actions workflow that executes them on push/PR; that workflow's success is the "required status check" the rest of the feature gates on.

**Target Platform**: GitHub.com, repository `superluminal-jp/my-claude-code` (public — confirmed via `gh repo view`).

**Project Type**: Repository configuration / CI-CD — not an application feature; no `src/`-style code is added.

**Performance Goals**: N/A. The only latency of interest (alert detected → fix merged) is bounded by GitHub's own Dependabot scan cadence, which this feature does not control.

**Constraints**:
- Auto-merge MUST NOT be able to bypass an unconfigured or partially-configured check gate (spec Edge Cases) — enforced by adding branch protection with a required status check *before* enabling auto-merge, not after.
- The auto-merge workflow is triggered by a Dependabot-authored PR, which requires `pull_request_target` (not plain `pull_request`) to obtain write permissions; `pull_request_target` workflows that check out and execute PR head content are a known supply-chain risk (untrusted code running with repo-write token). Mitigation: the workflow only reads PR *metadata* (via `dependabot/fetch-metadata`) and never checks out or executes the PR's changed files.
- Per `.claude/rules/permissions.md`, modifying CI/CD pipelines and mutating live repository settings (branch protection, `allow_auto_merge`, code-scanning default setup) are self-apply confirmation items — this plan's Phase 1 artifacts are files only; applying the repo-setting mutations and merging to `main` happens at `/speckit-implement` time and requires explicit user confirmation first.

**Scale/Scope**: Single repository. Deliverables: 1 Dependabot alert-visibility confirmation (no new file — already enabled), 1 CI workflow file, 1 auto-merge workflow file, repository-setting changes (branch protection ruleset, `allow_auto_merge=true`, CodeQL default setup enable), and README documentation of the new security posture.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template (all `[PRINCIPLE_N_NAME]` placeholders) — no project-specific constitution has been ratified for this repo. Falling back to the global rules that function as this project's governance for this change:

- **`permissions.md`** (Destructive Operations): explicitly lists "modifying CI/CD pipelines" and treats it as a self-apply confirmation item. **Gate**: implementation must pause for explicit user confirmation before (a) mutating live repository settings via `gh api`/`gh` CLI, and (b) merging the feature branch into `main`. Creating the workflow/config files themselves on a feature branch is reversible and does not require a pause.
- **`live-documentation.md`** § Drift Detection: this change creates a new observable repository contract (how security alerts are handled) with no existing docstring/README section describing it. **Gate**: README.md (or a co-located `.github/README.md`) must be updated in the same change to describe the new auto-merge/CodeQL/secret-scanning posture — tracked as a task in Phase 2.
- **ADR guidance** (`.claude/CLAUDE.md` Close-out + `adr` skill): auto-merging pull requests into `main` without human review is a one-way-door process decision (reversing it later means explaining why previously-auto-merged history exists). **Gate**: propose an ADR for "scope and safety conditions of Dependabot auto-merge" — tracked as a task in Phase 2, to be authored alongside implementation rather than silently skipped.

No violations to justify in Complexity Tracking — these are process gates to satisfy during `/speckit-tasks` / `/speckit-implement`, not architectural complexity being added.

## Project Structure

### Documentation (this feature)

```text
specs/032-github-security-automation/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.github/
└── workflows/
    ├── ci.yml                         # runs tests/run-*.sh — the required status check (new)
    └── dependabot-automerge.yml       # pull_request_target: approve+merge patch/minor dependabot PRs (new)

# No .github/dependabot.yml: security-update PRs work off the dependency graph
# without one (research.md §2), and any `updates:` entry would force a required
# `schedule` field that reintroduces routine version-update PRs — the opposite
# of what this feature needs.

README.md / README.ja.md               # security-posture section added (existing files, updated)
docs/adr/NNNN-dependabot-automerge-scope.md  # ADR for the auto-merge policy decision (new)
tests/run-*.sh                         # existing bash test scripts — unchanged, now executed by ci.yml
```

No `src/` tree applies — this repository has no single application to place code in; the feature's entire footprint is `.github/` configuration plus its required documentation and ADR.

**Structure Decision**: Single flat `.github/` addition at the repo root (Option 1 shape, degenerate to config-only — no `src/`/`tests/` split needed since the "tests" this feature exercises already exist under the repo's own `tests/`).

## Complexity Tracking

*No constitution violations to justify — see Constitution Check gates above, which are process/documentation gates rather than architectural complexity.*
