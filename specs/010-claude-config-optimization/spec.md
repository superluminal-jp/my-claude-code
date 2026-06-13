# Feature Specification: Claude Code Personal Configuration Optimization

**Feature Branch**: `claude/speckit-claude-code-settings-lrldfc`

**Created**: 2026-06-13

**Status**: Draft

**Input**: User description: "Claude Codeの個人設定をアップデートしたい。Memory, Subagentsを効率的に使用するように指示を更新／ルール・スキルの内容の見直し、コンテキスト長を最新のモデルが理解できる最低限の長さにする／ルール・スキルでやりたいことの意図の明確化／フック設定の最適化／ドキュメントのベストプラクティスに基づいた再設計／Speckit不使用時にも必要に応じて実行前に同様の設計・プラン・タスク化のフェーズを内部的にでも自動的に挟むように"

## Overview

The owner of this repository operates Claude Code through a personal configuration set (`.claude/CLAUDE.md`, `.claude/rules/*`, `.claude/skills/*`, `.claude/hooks/*`, `.claude/settings.json`). Over several feature iterations the configuration has accumulated overlapping guidance, verbose phrasing, and unstated intent. The owner wants the configuration refreshed so that it (a) steers Claude to use Memory and Subagents deliberately, (b) is **comprehensible and executable** by a modern model — every directive understood and actionable, with the minimum context budget needed to achieve that (redundancy and verbosity removed, but not content the model needs), (c) states the intent behind each rule and skill, (d) keeps hook automation lean and purposeful, (e) follows documentation best practices, (f) applies a lightweight design→plan→task discipline even on tasks that do not invoke the Spec Kit slash commands, and (g) is **grounded in recognized authority** — where a directive asserts a norm, it is anchored to an established best practice, international/industry standard, or academic principle so the model's understanding is accurate rather than vague.

**Comprehension outranks compression.** Length reduction is a means (remove duplication and noise), not the goal. Where a directive is ambiguous or the model could misexecute it, the configuration is *enriched* with a clarifying supplement or an authoritative anchor, even if that adds words. The configuration may therefore grow in places; what must shrink is redundancy, not understanding.

This specification defines **what** the optimized configuration must achieve and **why**, so the actual edits can be planned and validated. It does not prescribe the specific wording of each file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deliberate Memory and Subagent usage (Priority: P1)

The owner wants Claude to treat Memory (persistent project memory) and Subagents (delegated agent runs) as first-class tools used on purpose — not ignored, and not over-used — so that long or multi-part tasks stay efficient in tokens, latency, and cost.

**Why this priority**: This is the first improvement the owner named and has the broadest effect on every future session; misuse of Subagents or Memory directly wastes context budget and money.

**Independent Test**: Give Claude a multi-step, cross-file task and a fact worth remembering. Confirm the configuration causes Claude to (a) consider delegating broad exploration to a Subagent and (b) record/recall the durable fact via Memory, while not spawning Subagents for trivial single-file lookups.

**Acceptance Scenarios**:

1. **Given** the refreshed configuration, **When** the owner reviews the guidance on Memory, **Then** it states a clear, testable trigger for when to write to and read from Memory and when not to.
2. **Given** the refreshed configuration, **When** the owner reviews the guidance on Subagents, **Then** it states when delegation is warranted (broad fan-out search, context protection, explicit request) and when direct tools are preferred.
3. **Given** a trivial single-file lookup, **When** Claude follows the guidance, **Then** it does not spawn a Subagent.

---

### User Story 2 - Comprehensible, intent-explicit rules and skills (Priority: P2)

The owner wants every rule and skill reviewed so each one (a) opens with an explicit statement of what it is for, (b) is written so a current-generation model can understand and correctly execute every directive — ambiguous or under-specified guidance is supplemented rather than merely shortened, and (c) carries the minimum context budget consistent with (a) and (b): redundancy and verbosity removed, overlap consolidated, but no content the model needs to act correctly.

**Why this priority**: Rules and the routing portions of skills are loaded frequently; making them both lean and unambiguous improves every session — fewer tokens spent on duplication, and fewer misexecutions from vague wording. It depends on nothing else and delivers value alone.

**Independent Test**: Compare each rule/skill before and after. Confirm every file has a one-line intent statement, every directive is actionable (you can name the observable behavior it produces), no enforced behavior was dropped, and duplicated guidance was consolidated.

**Acceptance Scenarios**:

1. **Given** any file under `.claude/rules/` or any skill, **When** the owner reads its top, **Then** the intent ("what this is for / when it applies") is stated explicitly and unambiguously.
2. **Given** any directive in a refreshed rule/skill, **When** the owner asks "what observable behavior does this produce?", **Then** the answer is unambiguous; where it was not, a clarifying supplement was added.
3. **Given** two files that previously stated the same rule, **When** the owner reviews the result, **Then** the duplicated guidance exists in one canonical place and is cross-referenced rather than repeated.
4. **Given** the before and after configuration, **When** standing-context redundancy is measured, **Then** duplication is eliminated and any net length increase is attributable only to comprehension supplements (each recorded), not to verbosity.

---

### User Story 3 - Internal design→plan→task discipline without Spec Kit (Priority: P3)

The owner wants non-trivial tasks that do **not** use the `/speckit-*` commands to still pass through a lightweight, internal design → plan → task-breakdown phase before execution, automatically and proportionate to task size, so quality and predictability match Spec Kit flows without the ceremony.

**Why this priority**: It raises output quality on everyday tasks, but is less foundational than getting Memory/Subagent efficiency and lean rules right, and it builds naturally on the existing clarifier/advisor scaffolding.

**Independent Test**: Give Claude a non-trivial request without any slash command. Confirm the configuration causes Claude to internally frame the approach, outline a plan, and break the work into steps before editing — and that a trivial one-line request is allowed to skip the ceremony.

**Acceptance Scenarios**:

1. **Given** a non-trivial request with no `/speckit-*` command, **When** Claude responds, **Then** it first establishes scope/approach, a short plan, and a task breakdown before making changes.
2. **Given** a trivial, reversible one-step request, **When** Claude responds, **Then** the internal planning phase is proportionately minimized and does not add friction.
3. **Given** the new guidance, **When** the owner reviews it, **Then** the threshold that distinguishes "non-trivial" from "trivial" is stated in testable terms.

---

### User Story 4 - Optimized, purposeful hook configuration (Priority: P4)

The owner wants the hook setup (`settings.json` hook wiring plus the scripts in `.claude/hooks/`) reviewed so each hook has a clear purpose, no hook duplicates work better done elsewhere, timeouts and matchers are appropriate, and the safety hooks (credential/destructive-command guards) remain intact.

**Why this priority**: Hooks affect every tool call and session start; tightening them improves responsiveness and clarity, but the current hooks already function, so this is optimization rather than repair.

**Independent Test**: Review each configured hook against its script. Confirm each hook's purpose is documented, no redundant hooks remain, and the credential/destructive-operation protections still fire.

**Acceptance Scenarios**:

1. **Given** the refreshed configuration, **When** the owner lists configured hooks, **Then** each has a stated purpose and an appropriate matcher and timeout.
2. **Given** a destructive command or a credential-path read, **When** it is attempted, **Then** the protective hooks still block or gate it exactly as before.
3. **Given** any hook found to be redundant or obsolete, **When** the review completes, **Then** it is removed or consolidated with its rationale recorded.

---

### User Story 5 - Documentation redesigned to best practice (Priority: P5)

The owner wants the configuration's own documentation (CLAUDE.md and the prose inside rules/skills) redesigned to follow documentation best practices already endorsed in this repo — proximity (docs next to what they govern), no redundancy, explicit intent, and minimal length — so the configuration is self-explanatory and consistent.

**Why this priority**: It improves long-term maintainability and consistency, and naturally consolidates the outputs of the earlier stories, so it sits last as the finishing pass.

**Independent Test**: Audit the documentation against the repo's own Live Documentation principles (proximity, no redundancy, intent, auto-generation preference). Confirm no principle is violated by the refreshed docs.

**Acceptance Scenarios**:

1. **Given** the refreshed documentation, **When** audited against the repo's Live Documentation rules, **Then** it satisfies proximity, no-redundancy, and explicit-intent principles.
2. **Given** any guidance that can be derived or referenced rather than restated, **When** the owner reviews it, **Then** it is referenced, not duplicated.
3. **Given** the import structure of CLAUDE.md, **When** reviewed, **Then** each imported file stays focused and within the repo's stated size guidance.

---

### User Story 6 - Authoritative grounding for accurate model understanding (Priority: P2)

The owner wants the configuration's normative claims anchored to recognized authority — established best practices, international/industry standards, or academic principles — so the model interprets each directive precisely instead of guessing at a vague instruction. Where the existing config already names frameworks (MECE, SCQA, FURPS+, INVEST, OWASP, Tufte, Cleveland–McGill), those anchors are verified and kept; where a directive asserts a norm without grounding, an appropriate, correctly-attributed anchor is added concisely.

**Why this priority**: A directive grounded in a named standard ("validate at boundaries per OWASP ASVS") gives the model a precise, shared referent; an ungrounded one ("validate properly") invites inconsistent behavior. This directly raises execution fidelity and ties with US2 as the comprehension backbone.

**Independent Test**: Sample normative directives across rules/skills. Confirm each either carries a correctly-attributed authoritative anchor or is self-evidently operational, and that no anchor is fabricated, misattributed, or stale.

**Acceptance Scenarios**:

1. **Given** a normative directive (a "should/must" about how work is done), **When** the owner reviews it, **Then** it is either grounded in a correctly-named standard/principle or is concrete enough to execute without one.
2. **Given** any authority the config cites, **When** the owner checks it, **Then** the name and attribution are accurate and current (no invented or misremembered standards).
3. **Given** a directive enriched with an anchor, **When** the model reads it, **Then** the anchor narrows interpretation rather than adding decorative jargon — anchors are functional, not ornamental.

---

### Edge Cases

- **Behavior loss during trimming**: How does the owner confirm that shortening a rule did not silently drop an enforced behavior (e.g., a permission deny, a routing trigger)? A before/after behavior inventory is required.
- **Comprehension vs. compression**: What happens when two goals pull opposite directions — "minimum length" vs. "model must understand and execute"? Comprehension wins: intent statement and actionability are mandatory; length is minimized only by removing redundancy/verbosity, never by dropping content the model needs. Net growth is acceptable when it buys correct execution.
- **Over-grounding / decorative jargon**: How is it ensured that adding standards/principles does not bloat the config with ornamental references? Anchors must be functional (they narrow interpretation); a name with no behavioral effect is removed.
- **Fabricated or stale authority**: What prevents an added "standard" from being invented or misattributed? Every anchor must be a real, correctly-named, current authority; uncertain ones are omitted rather than guessed (Accuracy principle).
- **Over-delegation regression**: How is it ensured the new Subagent guidance does not cause Claude to spawn agents for trivial tasks (the opposite failure)?
- **Planning overhead on trivial tasks**: How is it ensured the internal design→plan→task phase does not slow down genuinely trivial requests?
- **Safety hooks**: What prevents hook "optimization" from weakening the credential or destructive-command guards?
- **User-scope vs project-scope**: How are changes that belong in user scope (`~/.claude/`) versus the checked-in project `.claude/` kept consistent (see `install.sh` sync path)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The configuration MUST provide explicit, testable guidance for when Claude writes to and reads from Memory, and when it does not.
- **FR-002**: The configuration MUST provide explicit, testable guidance for when Claude delegates to a Subagent versus using direct tools, including an explicit anti-pattern against delegating trivial single-file work.
- **FR-003**: Every file under `.claude/rules/` and every skill MUST begin with an explicit statement of its intent (what it is for and when it applies).
- **FR-004**: Redundancy and verbosity in the standing (always-loaded) context — `CLAUDE.md` plus its imported rules — MUST be removed while preserving every currently enforced behavior. Length reduction is subordinate to comprehension: the standing context MUST NOT grow from verbosity, but MAY grow where a comprehension supplement (FR-014) or authoritative anchor (FR-015) is required for correct execution, with each such addition recorded.
- **FR-005**: Redundant guidance duplicated across rules/skills MUST be consolidated to a single canonical location and cross-referenced from any other location that needs it.
- **FR-014**: Every directive in the refreshed configuration MUST be understandable and executable by a current-generation model — i.e., it MUST map to an observable behavior. Where a directive is ambiguous or under-specified, it MUST be enriched with a clarifying supplement rather than merely shortened.
- **FR-015**: Normative directives (statements of how work should be done) MUST be grounded in a correctly-attributed, current authority (established best practice, international/industry standard, or academic principle) where one applies and improves interpretive precision. Anchors MUST be functional (they narrow interpretation), not decorative, and MUST NOT be fabricated, misattributed, or stale; uncertain anchors are omitted, not guessed.
- **FR-006**: The configuration MUST instruct Claude to apply an internal design → plan → task-breakdown phase before executing non-trivial tasks that do not use `/speckit-*` commands, and MUST define the trivial/non-trivial threshold in testable terms.
- **FR-007**: The internal planning phase MUST scale down proportionately for trivial, reversible, single-step requests so it does not add friction.
- **FR-008**: Each configured hook MUST have a documented purpose, an appropriate matcher, and an appropriate timeout; redundant or obsolete hooks MUST be removed or consolidated with rationale recorded.
- **FR-009**: The existing safety protections (credential-path read denials, destructive-command and network guards, prompt secret-scanning) MUST remain functionally intact after hook optimization.
- **FR-010**: The configuration's documentation MUST conform to the repo's own Live Documentation principles (proximity, no redundancy, explicit intent, auto-generation preference).
- **FR-011**: Each file imported by `CLAUDE.md` MUST stay focused and within the repo's stated size guidance (~200 lines).
- **FR-012**: A before/after behavior inventory MUST be produced to verify that no enforced behavior (permission, routing trigger, hook guard, skill obligation) was lost during the optimization.
- **FR-013**: The change MUST keep project-scope (`.claude/`) and any user-scope sync path (`~/.claude/install.sh`) mutually consistent, or explicitly state that user-scope is out of scope.

### Key Entities *(include if feature involves data)*

- **Standing context**: The set of instructions loaded into every session — `CLAUDE.md` and the rule files it imports. Measured by length; the target of reduction.
- **Rule file**: A focused guidance document under `.claude/rules/` governing one concern (permissions, tools, MCP, clarifier, advisor, skill-routing, live-documentation). Each needs an intent line.
- **Skill**: A loadable playbook under `.claude/skills/` activated by routing triggers. Each needs an intent line and minimal routing footprint.
- **Hook**: A configured automation in `settings.json` bound to a script in `.claude/hooks/`, firing on session/tool/prompt events. Each needs a documented purpose.
- **Behavior inventory**: The enumerated list of enforced behaviors (permissions, routing triggers, hook guards, skill obligations) used to verify nothing is lost during trimming.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of files under `.claude/rules/` and 100% of skills begin with an explicit one-line intent statement.
- **SC-002**: Duplicated guidance in the standing context is eliminated (every rule stated once, cross-referenced elsewhere), with zero enforced behaviors lost (verified against the behavior inventory). Any net increase in standing-context length is attributable solely to recorded comprehension supplements or authoritative anchors — never to verbosity; verbosity-driven length is strictly reduced.
- **SC-009**: 100% of directives in the refreshed rules/skills are actionable — each maps to a nameable observable behavior; a reviewer can point to zero directives the model cannot execute as written.
- **SC-010**: Every normative directive that asserts a norm either carries a correctly-attributed authority or is self-evidently operational; an audit finds zero fabricated, misattributed, or decorative-only anchors.
- **SC-003**: The configuration contains explicit, testable triggers for Memory usage and for Subagent delegation, including at least one stated anti-pattern for each (when NOT to use them).
- **SC-004**: 100% of currently enforced safety protections (credential denials, destructive-command guards, prompt secret-scanning) still fire after the change, demonstrated by the behavior inventory.
- **SC-005**: Every configured hook maps to a stated purpose, and the number of redundant/obsolete hooks is zero after the review.
- **SC-006**: For a representative non-trivial task issued without a slash command, Claude produces an approach, a plan, and a task breakdown before editing; for a representative trivial task, it does not add planning overhead.
- **SC-007**: An audit of the refreshed documentation against the repo's Live Documentation principles finds zero unresolved violations.
- **SC-008**: No file imported by `CLAUDE.md` exceeds the repo's ~200-line size guidance.

## Assumptions

- **Scope is the checked-in project configuration** under `.claude/` (CLAUDE.md, rules, skills, hooks, settings.json). User-scope `~/.claude/` is touched only where the existing `install.sh` sync path requires consistency; otherwise it is out of scope (confidence: medium).
- **"Latest model" means a current-generation Claude model** (e.g., the Opus 4.x / Sonnet 4.x family configured in `settings.json`); "minimum length the model can understand" is interpreted as removing redundancy and verbosity while keeping — and where needed adding — the detail and grounding the model needs to execute correctly (confidence: high).
- **Comprehension and correct execution outrank length reduction**: where trimming would drop an enforced behavior or make a directive ambiguous, the content is kept (or supplemented) and only redundant/verbose wording is removed; net length may rise where a supplement or authoritative anchor buys fidelity (confidence: high).
- **Authoritative anchors are added only when functional and certain**: a standard/principle is cited only if it is real, correctly attributed, current, and it narrows the model's interpretation; otherwise the directive is made concrete in plain terms instead (confidence: high).
- **The internal design→plan→task phase reuses the existing clarifier/advisor scaffolding** rather than introducing a new framework, and is internal (does not require verbose user-facing ceremony) unless the task warrants it (confidence: medium).
- **Spec Kit skill files** under `.claude/skills/speckit-*` are largely vendored/generated and are out of scope for length trimming except where the owner's own routing/intent guidance touches them (confidence: medium).
- **This specification produces the spec only**; the actual edits are carried out in the planning/implementation phases (confidence: high).
- **Output language**: deliverables and spec follow the repository's existing English-documentation convention even though the request was written in Japanese (confidence: medium).
