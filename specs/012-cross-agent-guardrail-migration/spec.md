# Feature Specification: Cross-Agent Guardrail & Rule Migration Decision Record

**Feature Branch**: `012-cross-agent-guardrail-migration`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "Cross-agent config migration: for each of the 14 Claude Code-specific hooks/rules identified in this session's investigation (pre-bash.sh destructive-command blocking, user-prompt-submit.sh secret detection, pre-edit.sh .git/-edit block, pre-edit.sh main/master-branch block, pre-edit.sh CI/settings/production warnings, post-edit-format.sh auto-formatting, session-start.sh lint toolchain bootstrap, recommend-speckit.sh nudge, speckit-expand-update.sh auto-update, tools.md dedicated-tools/parallel-calls principles, tools.md Memory section, tools.md Subagents section, skill-routing.md routing table, mcp.md catalog+usage rule), decide and record whether to unify it for OpenAI Codex CLI and Cursor compatibility (via AGENTS.md prose, native hook reimplementation using Codex's PreToolUse/approval_policy/sandbox_mode or Cursor's beforeShellExecution/beforeSubmitPrompt/afterFileEdit hooks, or migration to GitHub Branch Protection), or keep it Claude Code-only. The spec should capture this as a decision record: for each item, the current Claude Code behavior, the cross-agent options considered, and the criteria for choosing. No source code implementation is in scope for this feature — the deliverable is a written decision document."

## Clarifications

### Session 2026-07-19

- Q: `pre-edit.sh` — CI/settings/production編集時の警告を共通化するか？ → A: 共通化する（AGENTS.mdに転記。ブロックでなく警告のため実効性の劣化なし）
- Q: `tools.md` — 「構造化ツール優先」「独立作業は並列化」の原則を共通化するか？ → A: 共通化する（ツール名を各ツールの語彙に一般化した文言でAGENTS.mdに転記）
- Q: `skill-routing.md` — Skillルーティング表を共通化するか？ → A: 共通化する（AGENTS.mdへ転記。ただしSKILL.mdが各ツールから見える場所に配置されていることを前提条件として明記する）
- Q: `mcp.md` — MCPサーバ使い分け表・使用ルールを共通化するか？ → A: 共通化する（AGENTS.mdへほぼそのまま転記）
- Q: `user-prompt-submit.sh` — プロンプト内秘密情報検知をCodex/Cursorへどう展開するか？ → A: 弱い形で共通化する（フック実装はせず、AGENTS.mdに「秘密情報を貼らない」という注意書きのみ両ツールに追加。推奨案（CursorはbeforeSubmitPromptへロジック移植、Codexは代替なし明記）は不採用。Claude Code側のuser-prompt-submit.shによるハードブロックは実効性が異なるため引き続き必須のまま残す）
- Q: `pre-bash.sh` — 破壊的コマンド遮断を共通化するか？ → A: 共通化する（判定ロジックを共通スクリプトに抽出し、Claude Code hook・Codex `PreToolUse`(Bash)・Cursor `beforeShellExecution`(`failClosed:true`)それぞれの薄いアダプタから呼ぶ）

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Decide the low-cost, low-risk unification items (Priority: P1)

As the maintainer of this `.claude/` configuration, I want to walk through the items that are plain prose today (no enforcement, no blocking exit code) and confirm whether each should be copied into a shared `AGENTS.md`, so that Codex CLI and Cursor sessions in this repository get the same guidance Claude Code sessions already have, at near-zero implementation cost.

**Why this priority**: These five items require no new engineering (no hook script, no per-tool adapter) — only a decision and a copy/rewrite into `AGENTS.md`. They are the fastest path to visible cross-agent value and should be resolved first so later, harder items can build on a confirmed baseline.

**Independent Test**: Can be fully tested by reviewing the decision record after this story and confirming each of the five items has a recorded verdict (unify / keep Claude-only) with a one-line rationale, independent of whether any other item in this feature has been decided yet.

**Acceptance Scenarios**:

1. **Given** the `mcp.md` catalog-and-usage-rule item, **When** the maintainer is presented with its current behavior and options, **Then** the maintainer records a verdict (unify into `AGENTS.md` / keep Claude-only) with rationale. **Recorded verdict**: 共通化 — transcribe near-verbatim into `AGENTS.md`.
2. **Given** the `skill-routing.md` routing-table item, **When** the maintainer is presented with its current behavior, options, and the precondition that skill files must be discoverable by each tool, **Then** the maintainer records a verdict with rationale. **Recorded verdict**: 共通化 — transcribe into `AGENTS.md`, with the SKILL.md-discoverability precondition stated explicitly as an open dependency.
3. **Given** the `tools.md` "prefer dedicated tools / parallelize independent calls" principles, **When** the maintainer is presented with the tool-name-genericization tradeoff, **Then** the maintainer records a verdict with rationale. **Recorded verdict**: 共通化 — genericize tool names (Read/Edit/Grep → each tool's own vocabulary) and transcribe into `AGENTS.md`.
4. **Given** the `pre-edit.sh` warning-only checks (CI config, `.claude/settings.json`, production config), **When** the maintainer is presented with the warning-vs-block distinction, **Then** the maintainer records a verdict with rationale. **Recorded verdict**: 共通化 — transcribe verbatim into `AGENTS.md`.

---

### User Story 2 - Decide the partial-parity items that need a per-tool tradeoff call (Priority: P2)

As the maintainer, I want to walk through the items where Cursor has a matching native hook but Codex CLI's equivalent is unconfirmed (or absent), so that I can decide, tool by tool, whether to implement the Cursor-side hook, accept a documented gap for Codex, or skip both until Codex's capability is verified.

**Why this priority**: These items carry real implementation cost (a hook script per tool) and asymmetric payoff (Cursor now, Codex maybe later). They depend on the P1 baseline decision (whether `AGENTS.md` exists at all) but not on each other, so they can be decided in any order once P1 is resolved.

**Independent Test**: Can be fully tested by reviewing the decision record and confirming each of the four items has a per-tool verdict (Cursor: implement/skip; Codex: implement/accept gap/defer) with the reason the two tools were treated differently where applicable.

**Acceptance Scenarios**:

1. **Given** `user-prompt-submit.sh` secret detection, **When** the maintainer is presented with Cursor's `beforeSubmitPrompt` match and Codex's unconfirmed equivalent, **Then** the maintainer records a verdict per tool. **Recorded verdict**: 弱い共通化（both tools） — prose-only "don't paste secrets" note in `AGENTS.md`, no hook implementation for either tool. Note: materially weaker than the Claude Code hard block; the Claude Code hook stays in place regardless.
2. **Given** `pre-bash.sh` destructive-command blocking, **When** the maintainer is presented with the shared-script-with-adapters option (Claude Code hook, Codex `PreToolUse`, Cursor `beforeShellExecution`), **Then** the maintainer records a verdict and, if unifying, confirms the shared-logic approach. **Recorded verdict**: 共通化 — extract the command-matching logic into one shared script; Claude Code hook, Codex `PreToolUse` (Bash), and Cursor `beforeShellExecution` (`failClosed: true`) each get a thin adapter calling it. Highest-priority implementation item (only item reproducing real enforcement across all three tools).
3. **Given** `post-edit-format.sh` auto-formatting, **When** the maintainer is presented with Cursor's `afterFileEdit` match and Codex's unconfirmed edit-time hook coverage, **Then** the maintainer records a verdict per tool.
4. **Given** `recommend-speckit.sh`'s Spec Kit adoption nudge, **When** the maintainer is presented with the repetition/de-duplication tradeoff of losing the throttle cache, **Then** the maintainer records a verdict on whether to accept the degraded (un-throttled) behavior in `AGENTS.md`.

---

### User Story 3 - Decide the items with no cross-agent hook equivalent (Priority: P3)

As the maintainer, I want to walk through the items that cannot be reproduced as a pre-action block in either Codex CLI or Cursor today, so that I can decide, for each, whether to keep it Claude Code-only, replace it with a non-agent-level control (e.g. GitHub Branch Protection), or drop it.

**Why this priority**: These items were already established (in prior investigation this session) to have no viable hook-level equivalent; deciding them does not block P1/P2 but closes out the full 14-item inventory so the decision record is complete.

**Independent Test**: Can be fully tested by reviewing the decision record and confirming each of the five items has a recorded verdict (keep Claude-only / migrate to non-agent control / drop) with rationale, and that the main/master-branch item explicitly names its proposed replacement control if not kept as a Claude Code hook.

**Acceptance Scenarios**:

1. **Given** `pre-edit.sh`'s main/master-branch edit block, **When** the maintainer is presented with the finding that no tool has a pre-edit block hook and that GitHub Branch Protection is a non-agent-level alternative, **Then** the maintainer records a verdict naming the chosen control.
2. **Given** `pre-edit.sh`'s `.git/`-direct-edit block, **When** the maintainer is presented with its low-frequency/low-impact profile, **Then** the maintainer records a verdict.
3. **Given** `session-start.sh`'s lint-toolchain bootstrap, **When** the maintainer is presented with its Claude-Code-on-the-web-specific scope, **Then** the maintainer records a verdict.
4. **Given** `speckit-expand-update.sh`'s Spec Kit CLI auto-update, **When** the maintainer is presented with its procedural (non-instructable) nature, **Then** the maintainer records a verdict.
5. **Given** `tools.md`'s Memory and Subagents sections, **When** the maintainer is presented with their dependency on Claude-Code-specific mechanisms, **Then** the maintainer records a verdict.

### Edge Cases

- What happens if the maintainer wants to revisit a verdict already recorded earlier in the same walkthrough? The decision record MUST be treated as editable until the walkthrough is marked complete, not append-only.
- How does the process handle an item where the maintainer's answer doesn't match any of the presented options? The process MUST accept a free-form custom answer and record it verbatim alongside its rationale.
- What happens if a later item's answer invalidates an earlier verdict (e.g. deciding to drop `AGENTS.md` entirely after already recording three "unify into AGENTS.md" verdicts)? The process MUST flag the inconsistency to the maintainer before finalizing the record rather than silently overwriting prior verdicts.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The process MUST present all 14 identified items to the maintainer, one at a time, grouped by the three priorities above.
- **FR-002**: For each item, the process MUST explain the item's current Claude Code behavior (what it does today, and whether it is a hard block, a soft warning, or automation) before asking for a decision.
- **FR-003**: For each item, the process MUST present the maintainer with a bounded set of options (unify via `AGENTS.md` prose / reimplement natively per tool / migrate to a non-agent-level control / keep Claude Code-only / drop) restricted to the options that are actually viable for that item, based on this session's prior guardrail-mechanism research.
- **FR-004**: For each item, the process MUST record the maintainer's chosen verdict and the stated rationale (the "why," not just the "what").
- **FR-005**: The process MUST NOT proceed to a final written decision record until all 14 items have a recorded verdict, unless the maintainer explicitly defers a specific item.
- **FR-006**: The process MUST write the completed decision record to a Markdown file, organized so each of the 14 items is independently readable without needing the rest of the document as context.
- **FR-007**: The written decision record MUST distinguish, per item, between a verdict that applies uniformly to both Codex CLI and Cursor and a verdict that differs per tool (per the User Story 2 pattern).
- **FR-008**: The written decision record MUST NOT include source code changes, hook scripts, or `AGENTS.md` content itself — only the decisions and their rationale (implementation is explicitly out of scope for this feature).
- **FR-009**: Where a verdict depends on an unconfirmed technical claim from prior research (e.g., "Codex CLI's edit-time hook coverage is unconfirmed"), the written record MUST flag that dependency so a future implementation phase knows what to re-verify before acting on it.

### Key Entities

- **Migration Item**: One of the 14 named hooks/rules under review. Attributes: name, source file, current Claude Code behavior (hard block / soft warning / automation / UI-only), priority group (P1/P2/P3).
- **Decision Verdict**: The outcome recorded for a Migration Item. Attributes: chosen option, per-tool split (if applicable: Codex verdict, Cursor verdict), rationale, any flagged unconfirmed dependency.
- **Decision Record**: The final Markdown artifact. Composed of all 14 Migration Items paired with their Decision Verdicts, organized by priority group.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 14 migration items have exactly one recorded verdict each in the final Markdown file.
- **SC-002**: A reader unfamiliar with this session's investigation can, for any single item in the Markdown file, understand the current behavior, the options considered, and the chosen verdict without reading the rest of the document.
- **SC-003**: Every verdict that differs between Codex CLI and Cursor is labeled per-tool in the output, with zero items presenting a single unlabeled verdict where the underlying research showed asymmetric tool support.
- **SC-004**: Zero implementation artifacts (hook scripts, `AGENTS.md` content, config files) are produced by this feature — the sole deliverable is the decision record.

## Assumptions

- The 14 items enumerated in the input are the complete and correct scope; no additional Claude Code hooks/rules are added to the review mid-walkthrough.
- The maintainer is the sole decision-maker for this walkthrough (no multi-stakeholder sign-off process is required).
- The options presented per item reuse the findings already established earlier in this session (guardrail-mechanism research for Codex CLI and Cursor); this feature does not re-research tool capabilities from scratch.
- "One at a time" (per the user's request) means the maintainer reviews and answers each item sequentially rather than receiving all 14 as a single batch; the process may still group related items (e.g. the three `pre-edit.sh` sub-items) for readability as long as each retains its own recorded verdict.
- The output location is a new file under this feature's spec directory (`specs/012-cross-agent-guardrail-migration/`); it does not modify the repository's live `.claude/` configuration.
