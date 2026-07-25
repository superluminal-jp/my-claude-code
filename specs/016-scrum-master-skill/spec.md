# Feature Specification: Integrate the `scrum-master` skill into the shared skill set

**Feature Branch**: `016-scrum-master-skill`

**Created**: 2026-07-25

**Status**: Draft

**Input**: User description: "scrum-master スキル（/Users/taikiogihara/work/scrum-master-skill/scrum-master/）を my-claude-code リポジトリの共有スキルセットの一つとして取り込む。既存の adr/clarifier/coder/minto-* と同じ扱いにし、Claude Code・Codex CLI 双方から発見・ルーティングされ、install.sh でユーザースコープに配布され、README とスキルルーティング規則に記載され、ルーティング回帰テストで検証される状態にする。既存スキルと違い references/ と scripts/flow_metrics.py（allowed-tools 付き）を持つ点を扱うこと。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Scrum request loads the skill automatically (Priority: P1)

Someone working in a repository that uses this configuration asks an agent for help with a Scrum concern — "our stand-ups are dragging", "write me a sprint planning agenda", "run a retro for my own week" — without naming a skill. The agent loads the `scrum-master` playbook and answers from it, the same way a coding request loads `coder` today.

**Why this priority**: This is the entire point of "taking the skill in". Without automatic discovery and routing, the files are inert; every other item on the list (distribution, docs, tests) only has value once this works.

**Independent Test**: Start an agent session in this repository, issue a Scrum-flavoured prompt that never says "skill" or "scrum-master", and observe which skill loads. Delivers value on its own: the skill is usable from this repo even if nothing is installed to user scope yet.

**Acceptance Scenarios**:

1. **Given** an agent session opened in this repository, **When** the user asks a facilitation question such as "チームのレトロがマンネリ化している", **Then** the `scrum-master` skill is loaded and the response follows its playbook.
2. **Given** an agent session opened in this repository, **When** the user asks a solo-practice question such as "自分ひとりの作業を週次で振り返りたい", **Then** the `scrum-master` skill is loaded rather than a document or clarification skill.
3. **Given** a coding request unrelated to Scrum, **When** the user submits it, **Then** `coder` still loads and `scrum-master` does not — adding the new skill causes no misrouting of existing categories.
4. **Given** the skill is loaded and the user supplies a CSV of completed tickets, **When** the skill's flow-metrics helper is invoked, **Then** it runs and returns cycle-time, throughput, and WIP figures without the run being blocked by a safety guardrail.

---

### User Story 2 - The skill reaches every agent the repo supports (Priority: P2)

A user runs this repository's installer to refresh their machine-wide agent configuration. Afterwards the `scrum-master` skill is available to Claude Code and to Codex CLI from any working directory, not just from inside this repository.

**Why this priority**: The repository's stated value is a single configuration that serves multiple agents at user scope. A skill that only works inside one checkout is a second-class member of the set. It ranks below P1 because the skill is already useful in-repo without it.

**Independent Test**: Run the installer, then list the installed skill directories and links for both agents and confirm `scrum-master` is present and resolves to a readable playbook. Testable without touching routing or docs.

**Acceptance Scenarios**:

1. **Given** a clean machine profile, **When** the installer runs, **Then** the `scrum-master` skill — including its reference files and helper script — is present in the user-scope Claude Code skill location.
2. **Given** the installer has run, **When** Codex CLI's skill discovery path is inspected, **Then** `scrum-master` appears there alongside the other custom skills and resolves to the installed copy, not to this repository's working tree.
3. **Given** the installer is run a second time, **When** it completes, **Then** the result is identical to the first run — no duplicated entries and no broken links.
4. **Given** the skill's reference files and helper script exist, **When** the skill is loaded from the user-scope install, **Then** every reference link in the playbook resolves to a file that exists.

---

### User Story 3 - The skill is documented and its routing is guarded by a test (Priority: P3)

A contributor reading this repository's documentation sees `scrum-master` listed among the skills, understands what it is for, and finds a routing regression test that fails if the skill stops being reached.

**Why this priority**: Documentation and a regression test protect the first two stories from silently rotting, but neither is required for the skill to work today.

**Independent Test**: Read the repository's skill inventory and routing rules and confirm `scrum-master` is described; run the routing test suite and confirm it exercises a Scrum prompt.

**Acceptance Scenarios**:

1. **Given** the repository documentation, **When** a reader looks for the list of available skills, **Then** `scrum-master` is listed with a one-line purpose in the same places the existing skills are listed, in both the English and Japanese documentation.
2. **Given** the routing rules document, **When** a reader looks for how a Scrum or facilitation request is dispatched, **Then** a rule names `scrum-master` and distinguishes it from the code and document categories.
3. **Given** the routing regression suite, **When** it is run, **Then** it includes at least one case whose expected skill is `scrum-master` and that case passes.
4. **Given** the Codex CLI guidance document, **When** a reader looks at its routing list, **Then** `scrum-master` appears there with a path to its playbook, consistent with the other custom skills.

---

### Edge Cases

- **A Scrum request that is also a document request** — "レトロの結果をレポートにまとめて". Routing must resolve compound work rather than silently picking one skill, the same way code-plus-document requests are resolved today.
- **A project-management-flavoured request that is not Scrum** — a Gantt chart, a PMBOK deliverable, a status report. These must not be swept into `scrum-master`, whose remit is Scrum and empiricism.
- **The helper script is invoked without input, or with a malformed CSV** — the failure must be legible to the user rather than silently producing fabricated metrics, since the skill's own rule is never to invent numbers.
- **A machine without the language runtime the helper script needs** — the rest of the skill must remain fully usable; only the metrics helper degrades.
- **Spec Kit's generated skills are excluded from distribution** — the new skill must be picked up by the same mechanism without accidentally re-including the excluded generated ones.
- **The skill's playbook is written in Japanese while existing skill playbooks are in English** — mixed-language skill bodies must not break discovery, listing, or routing.

## Requirements *(mandatory)*

### Functional Requirements

**Skill presence and shape**

- **FR-001**: The `scrum-master` skill MUST live in this repository alongside the existing custom skills, and MUST include its playbook, all of its reference documents, and its flow-metrics helper script.
- **FR-002**: The skill's declared identity — name, description, and trigger phrases — MUST be preserved from the source so that the behaviour the source repository specified is the behaviour delivered here.
- **FR-003**: Every internal link in the skill's playbook MUST resolve to a file present in this repository.
- **FR-004**: The skill MUST NOT be excluded by the repository's rules for ignoring generated, per-project artifacts.

**Discovery and routing**

- **FR-005**: A Scrum, agile-facilitation, or solo-practice request MUST route to `scrum-master` without the user naming the skill.
- **FR-006**: The repository's routing rules MUST state when `scrum-master` applies and how it is distinguished from the code and document categories, including how a compound request that spans categories is resolved.
- **FR-007**: `scrum-master` MUST appear in the always-loaded mandatory-routing list the agent instructions carry on every turn, alongside `coder`, `clarifier`, and the Minto suite — not only in the separate routing-rules file the way `adr` is listed.
- **FR-007a**: Because the skill is always in the routing list, the routing rules MUST draw an explicit boundary against adjacent-but-out-of-remit requests — general project management, status reporting, scheduling — so that the wider trigger surface does not pull in work the skill is not for.
- **FR-008**: Adding the skill MUST NOT change which skill is selected for the request categories that already have routing coverage.
- **FR-009**: The Codex CLI guidance document MUST list `scrum-master` in its routing section with a path to the playbook, in the same form as the other custom skills.

**Distribution**

- **FR-010**: The installer MUST place the skill, with its references and helper script intact, into the user-scope location Claude Code reads.
- **FR-011**: The installer MUST make the skill discoverable to Codex CLI by the same mechanism used for the other custom skills, resolving to the installed copy rather than to this repository's working tree.
- **FR-012**: Re-running the installer MUST leave the same end state as the first run, with no duplicates and no broken links.
- **FR-013**: The installer MUST continue to exclude Spec Kit's generated per-project skills while including `scrum-master`.

**Helper script**

- **FR-014**: The flow-metrics helper MUST be executable from within a skill session without the user having to grant an ad-hoc permission for each run, and without a safety guardrail blocking it.
- **FR-015**: The permission the skill requests for its helper MUST be scoped to that one script — it MUST NOT widen the agent's general ability to run arbitrary commands.
- **FR-016**: If the helper cannot run — missing runtime, missing or malformed input — the user MUST get a legible failure, and the rest of the skill MUST remain usable.

**Documentation**

- **FR-017**: The repository's skill inventory MUST list `scrum-master` with a one-line purpose everywhere the existing skills are enumerated, in both the English and Japanese documentation.
- **FR-018**: Documentation describing the repository's directory layout MUST reflect that this skill carries reference files and a script, not a playbook alone.

**Regression coverage**

- **FR-019**: The routing regression suite MUST include at least one case whose expected skill is `scrum-master`, following the existing case format.
- **FR-020**: The existing regression suites MUST continue to pass unchanged.

**Provenance**

- **FR-021**: This repository MUST become the single source of truth for the skill once it is integrated. The external `scrum-master-skill` working directory is a one-time import source, not an upstream. The change MUST record that provenance somewhere durable, so a later reader can tell where the vendored files came from and that no upstream is being tracked.
- **FR-022**: Because there is no upstream, the feature MUST NOT add any synchronisation mechanism, drift-detection test, or scheduled reconciliation between this repository and the external directory.

### Key Entities

- **Skill**: A named, on-demand playbook an agent loads when a request matches its triggers. Carries an identity (name, description, trigger phrases), a body, and optionally supporting reference documents, helper scripts, and a declared tool permission.
- **Routing rule**: The statement that maps a category of request to exactly one skill, and that says how compound requests spanning categories are resolved.
- **Skill inventory**: The enumerations of available skills that appear in the repository's documentation and in each agent's guidance document; these must agree with what is actually present.
- **Distribution target**: A per-agent, user-scope location from which a skill is discoverable outside this repository; each supported agent has one.
- **Routing regression case**: A recorded prompt plus its expected skill, used to detect routing regressions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user who asks a Scrum or facilitation question without naming a skill gets an answer grounded in the `scrum-master` playbook — verified across at least four differently-phrased prompts covering team facilitation, a specific Scrum event, and solo practice, **of which at least one is in English and at least one in Japanese**. Both languages are required, not either: the playbook body is Japanese while its trigger phrases are English, so an English prompt exercises the case most likely to fail.
- **SC-002**: Every routing regression case that existed before this change still resolves to the same skill it did before — zero regressions.
- **SC-003**: After one installer run, `scrum-master` is discoverable from both supported agents from any working directory, with all of its reference documents present and its links still resolving from the installed copy. (Verification does not require wiping an existing profile — the installer replaces each managed path outright, so a single run on an existing profile is equivalent to a clean one for the paths in scope.)
- **SC-004**: Running the installer twice produces an identical end state — no duplicated entries, no broken links, no leftover files.
- **SC-005**: Every link inside the skill's playbook resolves to an existing file — zero broken references.
- **SC-006**: A reader can find `scrum-master` and understand its purpose from the repository's documentation in under one minute, in both the English and Japanese versions, without opening the skill itself.
- **SC-007**: The flow-metrics helper produces cycle-time, throughput, and WIP figures from a sample input on the first attempt, with no ad-hoc permission prompt and no guardrail block.
- **SC-008**: All existing behaviour suites in the repository pass after the change.
- **SC-009**: A project-management request that is not Scrum — a schedule, a status report, a generic planning document — does not load `scrum-master`, confirming the always-loaded routing entry widened the trigger surface without blurring the boundary.

## Assumptions

- **Integration means a copy, not a reference.** "取り込み" is read as vendoring the skill's files into this repository so it is self-contained, matching how the existing custom skills live here. A submodule, symlink, or package dependency on the external directory is out of scope.
- **The skill's content is taken as-is.** Its playbook, references, and script are integrated without editorial rewriting. Improving, translating, or restructuring the skill's content is a separate concern from integrating it.
- **The Japanese-language body is acceptable.** Existing skill playbooks are written in English; this one is in Japanese. Translation is explicitly not part of this feature, and mixed-language bodies are assumed not to affect discovery or routing.
- **The declared tool permission is the right mechanism** for the helper script — a narrowly scoped, script-specific declaration rather than a broad permission entry — unless verification shows a guardrail blocks it anyway.
- **The external source directory is not deleted by this feature.** FR-021 settles which copy is authoritative; retiring or archiving the external directory is the user's call and happens outside this repository.
- **Cursor is not a distribution target for custom skills.** Its skill directory currently holds only Spec Kit's generated skills, so this feature does not add one there.
- **The routing regression suite requires a live agent CLI to run**, so its cases are authored to the existing format and executed where that CLI is available; authoring the case is in scope, provisioning the CLI is not.
- **The source directory remains readable during implementation**, so the files can be copied from it.
