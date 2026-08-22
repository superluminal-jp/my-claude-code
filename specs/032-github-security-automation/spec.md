# Feature Specification: GitHub Security Alert Auto-Response

**Feature Branch**: `032-github-security-automation`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "GitHubが検知するセキュリティ脆弱性への自動対応を設定する。対象: Dependabotアラート、Code scanningアラート(CodeQL)、Secret scanningアラート。自動化レベル: Dependabotのパッチ/マイナー更新PRはCI通過後に自動マージ、それ以外(メジャー更新、CodeQL、secret scanning)は人間のレビューに残す。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dependency vulnerability is patched without waiting on a human (Priority: P1)

A maintainer wants low-risk dependency vulnerabilities (patch/minor version bumps) to be fixed automatically, so the repository is never left exposed to a known CVE for longer than it takes CI to run.

**Why this priority**: This is the core "automatic response" the request is about, and it is the only response type where full automation (PR creation *and* merge) is both safe (patch/minor updates are expected to be backward compatible) and high value (closes the exposure window fastest).

**Independent Test**: Introduce a dependency with a known low-severity vulnerability fixable by a patch/minor bump. Confirm a fix pull request is opened automatically, all required checks run, and — once green — the pull request merges into the default branch without a human clicking "merge."

**Acceptance Scenarios**:

1. **Given** a dependency in the repository has a known vulnerability with a patch or minor fix available, **When** GitHub's dependency scanner detects it, **Then** a pull request that upgrades the dependency to the fixed version is opened automatically within GitHub's normal alert-to-PR latency.
2. **Given** an automatically-opened patch/minor fix pull request, **When** all required status checks pass, **Then** the pull request is merged into the default branch without manual approval.
3. **Given** an automatically-opened patch/minor fix pull request, **When** any required status check fails, **Then** the pull request is left open, unmerged, and visible for a human to investigate.

---

### User Story 2 - Major or otherwise risky dependency fixes wait for a human (Priority: P2)

A maintainer wants dependency fixes that could plausibly break the build (major version bumps, or any Dependabot pull request that is not itself a security fix) to stop at human review rather than merge unattended.

**Why this priority**: Auto-merging a breaking change is the main risk this feature introduces; scoping automation away from major bumps is what keeps the P1 automation safe to turn on.

**Independent Test**: Introduce a dependency with a known vulnerability whose only fix is a major version bump. Confirm a fix pull request is opened, but that it is never merged automatically regardless of CI status, and remains queued for manual review.

**Acceptance Scenarios**:

1. **Given** a dependency vulnerability is only fixable by a major version upgrade, **When** GitHub opens the corresponding fix pull request, **Then** the pull request is never merged automatically, even after all checks pass.
2. **Given** a routine (non-security) dependency version-update pull request, **When** it is opened, **Then** it is also excluded from auto-merge and requires manual review, since it was not raised in response to a detected vulnerability.

---

### User Story 3 - Code-level and secret-exposure alerts are surfaced, not silently merged (Priority: P3)

A maintainer wants vulnerabilities that cannot be safely auto-fixed — insecure code patterns found by static analysis, and secrets accidentally committed or pushed — to be actively surfaced (and, for secrets, blocked pre-emptively) rather than requiring someone to remember to go check.

**Why this priority**: These alert types have no reliable automatic *fix*; the achievable "automatic response" is detection, prevention, and visibility rather than merge automation, so they are valuable but not the primary automation win.

**Independent Test**: Push a commit containing a known insecure code pattern and confirm it is flagged in the repository's security alerts. Separately, attempt to push a commit containing a recognizable secret/token pattern and confirm the push itself is rejected before it reaches the default branch.

**Acceptance Scenarios**:

1. **Given** a commit introduces a static-analysis-detectable vulnerable code pattern, **When** the commit is pushed, **Then** an alert appears in the repository's security alert list identifying the file, location, and vulnerability type.
2. **Given** a commit contains content matching a known secret/credential pattern, **When** a contributor attempts to push it, **Then** the push is blocked before the secret reaches any branch, and the contributor is shown the reason.
3. **Given** a secret was already merged into history before this feature existed, **When** the scanner runs against existing history, **Then** an alert is raised for the maintainer to rotate/revoke the credential (no automatic fix is expected for already-exposed secrets).

---

### Edge Cases

- What happens when a patch/minor fix pull request's required checks are still pending (not yet failed or passed) when a second, unrelated vulnerability PR opens? Each pull request's merge decision MUST depend only on that pull request's own check results, not on other open pull requests.
- What happens when a dependency fix pull request modifies more than just the version (e.g., Dependabot cannot cleanly bump and instead proposes a broader change)? Treat anything outside a straightforward patch/minor version bump as ineligible for auto-merge.
- What happens if branch protection / required status checks are not configured on the default branch? Auto-merge MUST NOT be able to bypass an unconfigured or partially configured check gate — absence of a required check must not be treated as "passed."
- How does the system handle a repository administrator merging a flagged pull request manually before automation acts? The manual merge stands; automation must not re-open, revert, or duplicate a pull request that reviewed the same vulnerability once it is resolved.
- What happens when secret scanning push protection produces a false positive (e.g., a test fixture that looks like a credential)? A contributor MUST have a documented way to acknowledge/bypass a specific detected pattern without disabling protection repository-wide.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST have dependency vulnerability detection active so that known CVEs affecting its dependencies are surfaced as alerts.
- **FR-002**: When a dependency vulnerability with an available patch or minor fix is detected, the system MUST automatically open a pull request that upgrades the affected dependency to a fixed version.
- **FR-003**: An automatically-opened dependency fix pull request that only changes a dependency by a patch or minor version, and for which all required status checks have passed, MUST be merged into the default branch without requiring a manual approval action.
- **FR-004**: A dependency-related pull request MUST NOT be auto-merged if it is a major version upgrade, if it was not opened in response to a detected vulnerability, or if any required status check has failed or has not yet reported success.
- **FR-005**: The repository MUST have static code-analysis scanning active on changes to the default branch, and detected findings MUST be recorded as reviewable alerts rather than silently ignored.
- **FR-006**: Code-analysis findings MUST NOT trigger any automatic merge or automatic code change; they require human triage.
- **FR-007**: The repository MUST have secret-detection scanning active, covering both historical content and new pushes.
- **FR-008**: A push containing content recognized as a credential/secret pattern MUST be rejected before the content becomes part of any branch, with the contributor informed of the reason and given a documented path to resolve a false positive.
- **FR-009**: All three alert categories (dependency, code-analysis, secret) MUST remain visible in a single place a maintainer can review, regardless of whether a given alert was auto-resolved or is awaiting a human.
- **FR-010**: The auto-merge behavior in FR-003 MUST be scoped to this repository only; it MUST NOT be applied as an organization-wide default that would silently affect other repositories.

### Key Entities

- **Dependency vulnerability alert**: A detected known vulnerability (CVE) in a project dependency; carries a severity, an affected dependency + version range, and — when available — a fixed version.
- **Dependency fix pull request**: A pull request, generated in response to a dependency vulnerability alert, that changes one dependency's declared version; classified by whether the version change is patch/minor or major.
- **Code-analysis alert**: A detected insecure code pattern in the repository's own source, tied to a file/location and a vulnerability category; has no automated fix path in this feature.
- **Secret alert**: A detected credential-like pattern, either blocked at push time (not yet in history) or found already present in history (requires rotation, not a code fix).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A dependency vulnerability with a patch/minor fix available goes from "detected" to "fixed on the default branch" with zero manual pull-request actions, as long as checks pass.
- **SC-002**: 100% of dependency pull requests that are major-version upgrades, or that were not raised for a security reason, require a manual merge action — none merge unattended.
- **SC-003**: 100% of pushes containing a recognizable secret pattern are rejected before landing on any branch.
- **SC-004**: Every open vulnerability across all three alert categories (dependency, code-analysis, secret) is visible from a single review location, with zero alerts that exist only in an external or undiscoverable channel.
- **SC-005**: No pull request merges automatically while any of its required checks is failing or unreported.

## Assumptions

- The repository already has (or will have, as part of adjacent work) an automated test/lint check that runs on pull requests; "required status checks passing" in FR-003/FR-004 refers to that existing check, not a new one this feature must build.
- "Patch/minor" vs. "major" classification follows Semantic Versioning as interpreted by the platform's own dependency-update tooling; this feature does not need to invent its own version-classification logic.
- The repository is public, so the underlying vulnerability-scanning capabilities used for FR-001, FR-005, and FR-007 are available at no additional cost; a private repository would need the equivalent capability enabled/licensed separately (out of scope here).
- Rotating an already-exposed secret found by FR-007's historical scan is a manual, human, out-of-band action (e.g., revoking the credential at its issuer) — this feature covers detection and prevention, not credential rotation itself.
- Auto-merge (FR-003) is scoped to this one repository; no organization-wide policy change is in scope.
