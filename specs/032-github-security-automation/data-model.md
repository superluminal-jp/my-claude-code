# Phase 1 Data Model: GitHub Security Alert Auto-Response

This feature has no application data store. "Entities" here are GitHub platform resources this feature reads or acts on, mapped from the spec's Key Entities to their concrete API/webhook representation.

## Dependency vulnerability alert

- **Source**: GitHub Dependency graph + Dependabot, `GET /repos/{owner}/{repo}/dependabot/alerts`.
- **Relevant attributes**: `security_advisory.severity`, `dependency.package.name`, `security_vulnerability.vulnerable_version_range`, `security_vulnerability.first_patched_version`.
- **Relationship**: zero-or-one Dependency fix pull request per open alert (Dependabot opens at most one PR per alert by default).

## Dependency fix pull request

- **Source**: a PR opened by `dependabot[bot]`, `github.event.pull_request` in the workflow context.
- **Relevant attributes** (from `dependabot/fetch-metadata@v2` action outputs):
  - `steps.metadata.outputs.update-type` — one of `version-update:semver-patch`, `version-update:semver-minor`, `version-update:semver-major` (or unset). **This is the sole field the merge decision is keyed on.**
  - `steps.metadata.outputs.dependency-type` — `direct:production`, `direct:development`, `indirect`.
  - `github.actor` — must equal `dependabot[bot]`; the workflow refuses to act on any PR not authored by Dependabot.
- **State transitions** (this feature's workflow):
  1. `opened` (by Dependabot) → workflow runs `dependabot-automerge.yml`.
  2. If `update-type` is patch or minor → `gh pr merge --auto --squash` is requested (does not merge yet).
  3. GitHub holds the PR in "merge requested, waiting on required checks" until `ci.yml`'s job reports success.
  4. On green → GitHub completes the merge automatically. On failure → the auto-merge request is dropped by GitHub and the PR stays open for manual triage.
  5. If `update-type` is major, or the field is absent/unrecognized → workflow takes no merge action; PR stays open for manual review (FR-004).

## Code-analysis alert

- **Source**: CodeQL default setup, `GET /repos/{owner}/{repo}/code-scanning/alerts`.
- **Relevant attributes**: `rule.security_severity_level`, `most_recent_instance.location` (file/line), `state` (`open`/`dismissed`/`fixed`).
- **Relationship**: none to a pull request in this feature's scope — no auto-fix or auto-merge path exists for these (FR-006); they are surfaced, not acted on.

## Secret alert

- **Source**: Secret scanning, `GET /repos/{owner}/{repo}/secret-scanning/alerts` (post-hoc, for anything already in history) and push-protection's synchronous rejection response (for new pushes, before history is affected).
- **Relevant attributes**: `secret_type`, `state` (`open`/`resolved`), `push_protection_bypassed` (whether a contributor used the documented bypass path for a false positive).
- **Relationship**: none to a pull request — resolution is a human rotating/revoking the credential out of band (Assumptions in spec.md); this feature's scope ends at detection/blocking + visibility.
