# Feature Specification: Replace the hand-maintained Codex port with OpenAI's official import path

**Feature Branch**: `021-codex-official-import`

**Created**: 2026-08-10

**Status**: Draft — requirements only. Do not implement until the operator promotes this draft.

**Input**: User description: "このレポジトリの `.agents/` の設定は `.claude/` を openai codex 用に移植したものだが、使うときに都度 OpenAI が公式で準備している import コマンドや migrate-to-codex スキルを使うように変更したい。"

## Context

### What exists today (verified against the working tree, 2026-08-10)

The Codex port is not confined to `.agents/`. It is a set of coupled artifacts:

| Artifact | Current content | Verified by |
|---|---|---|
| `.agents/skills/` | 8 tracked relative symlinks into `.claude/skills/` (`adr`, `clarifier`, `coder`, `digital-agency-frontend`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`). `speckit-*` entries are untracked and gitignored per ADR-0001 | `git ls-files .agents`, `ls -la .agents/skills` |
| `.codex/AGENTS.md` | Hand-written summary of `.claude/CLAUDE.md` + `.claude/rules/*` inside Codex's 32 KiB budget | `.codex/README.md` deployment map |
| `.codex/hooks/*.sh` | 4 adapters (`destructive-command`, `pre-edit`, `post-edit`, `prompt-secret`) that wrap the shared `scripts/guardrails/*.sh` decision scripts | `ls .codex/hooks`, `.codex/README.md` |
| `.codex/rules/guardrails.rules` | Exact-prefix allow/prompt policy mirroring `settings.json#permissions` | `.codex/README.md` |
| `.codex/prompts/verify-config.md` | Codex counterpart of the `verify-config` skill, invoked as `/prompts:verify-config` | `.codex/README.md` |
| `install.sh` | ~71 lines referencing Codex/agents paths: deploys `.codex/AGENTS.md` → `~/.codex/AGENTS.md`, skills → `~/.agents/skills/`, hooks → `~/.codex/hooks/` registered in a managed block of `~/.codex/config.toml`, rules, prompts, and a managed `[mcp_servers.*]` block converted from `.mcp.json` | `grep -cin "codex\|agents" install.sh` = 71 |
| `tests/run-codex-sync.sh`, `tests/run-codex-sync-drift.sh` | SYNC-01 … SYNC-12 consistency checks over the hand-maintained duplication, plus a destructive acceptance suite for the checker itself | `grep -oE "SYNC-[0-9]+"` |
| `.codex/README.md` | Deployment map recording, per element, classification / sync method / behavioural delta / provenance | file contents |

Provenance: `specs/012-cross-agent-guardrail-migration`, `specs/013-cross-agent-guardrail-implementation`, `specs/014-codex-config-port`, extended by 015/016/019/020; ADR-0002 (`docs/adr/0002-deploy-codex-configuration-at-user-scope.md`).

### The official tools, as documented

Sources read 2026-08-10. The authoritative page is `https://developers.openai.com/codex/import`, which 308-redirects to `https://learn.chatgpt.com/docs/import` (both OpenAI-operated). All statements below come from the official pages. A third-party documentation mirror was checked early on and rejected as non-official; only OpenAI-operated hosts are cited anywhere in this feature.

**`/import` (Codex CLI)** — <https://developers.openai.com/codex/import>

- An **interactive in-session command**: in Codex CLI type `/import`, select Claude Code, then choose what to import. "Use the import flow to bring instructions, settings, skills, plugins, projects, and recent work from another agent."
- Documented conversions: **instruction files → `AGENTS.md`**, **`settings.json` → `config.toml`**; plus skills, plugins, **hooks**, slash commands, MCP server configuration, **subagents**, project memories, and existing project folders.
- Chats: "imports up to 50 chats from the last 30 days."
- "isn't available during a running task, in a remote session, or while connected to a local app-server daemon."
- "Leaves your existing agent setup unchanged."
- **No flags and no idempotency guarantees are documented.**
- The page explicitly instructs: "Review imported setup before you rely on it," naming MCP servers needing custom auth, **hooks with altered behavior**, and prompt templates depending on arguments, shell interpolation, or file-path placeholders.

### Hooks: the same word, and NOT the same contract

`.claude/hooks/` and Codex hooks are the same *category* of mechanism — scripts injected into the agentic loop, receiving JSON on stdin — and the lifecycle event **names are shared**. The blocking contract is not. Compiled from <https://developers.openai.com/codex/hooks> and <https://code.claude.com/docs/en/hooks>, both read 2026-08-10.

| Dimension | Claude Code | Codex |
|---|---|---|
| Lifecycle events | ~30, incl. `UserPromptExpansion`, `PostToolBatch`, `ConfigChange`, `FileChanged`, `WorktreeCreate` | **11 documented**: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop`, `SessionStart`, `SubagentStart`, `SessionEnd` |
| Configuration | `settings.json#hooks` | `~/.codex/hooks.json`, `~/.codex/config.toml` `[hooks]`, `<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml`, plugin bundles. Layers **merge** — "Higher-precedence config layers don't replace lower-precedence hooks." |
| Structure | event → matcher → hooks | event → matcher group (regex) → handlers |
| Common stdin fields | `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `effort` | `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `model`, **`turn_id`**, `permission_mode` |
| How a hook denies | exit 2; top-level `decision: "block"`; `hookSpecificOutput.permissionDecision: "deny"` with `permissionDecisionReason` | **The same contract works**: per the converter's `references/differences.md`, Codex `PreToolUse` "blocks only `permissionDecision: "deny"`, legacy `decision: "block"`, or exit code `2`". The hooks page additionally documents `continue`/`stopReason`/`systemMessage`/`additionalContext`. Verified empirically — see `research.md` § R-03 |
| Which tools trigger Pre/PostToolUse | every tool, per `matcher` | **Shell commands only** (converter report, 2026-08-10). Edits go through `apply_patch` and do **not** trigger them — this is the actual breakage, see `research.md` § R-03 |
| Trust model | none — configured hooks run | **Non-managed command hooks are skipped until reviewed and trusted via `/hooks`**; trust is recorded against the hook's hash, so any edit requires re-review. Managed hooks (`requirements.toml`, MDM, system) bypass review |
| Tool coverage | all tools | `PreToolUse`/`PostToolUse` cover Bash, `apply_patch`, MCP tools, and local function tools — **not hosted tools** such as WebSearch |

Three consequences for this feature:

Three consequences, as revised by the empirical trial in `research.md`:

1. **Two of the four guardrails survive; two do not.** `pre-bash.sh` (`PreToolUse`/Bash) and `user-prompt-submit.sh` (`UserPromptSubmit`) convert and fire. `pre-edit.sh` (`Edit|Write|Delete`) and `post-edit-format.sh` (`Edit|Write`) convert but **never fire**, because Codex runs `PreToolUse`/`PostToolUse` for shell commands only. `speckit-expand-update.sh` (`UserPromptExpansion`) is dropped as unsupported.
2. **The deny contract is not the problem.** Codex honours `permissionDecision: "deny"`, `decision: "block"`, and exit code 2. The earlier inference to the contrary is withdrawn. Tool **coverage** is the breakage.
3. **Import alone does not arm a hook.** Until the developer runs `/hooks` and trusts it, a non-managed imported hook is skipped. A procedure that omits this step silently ships with guardrails disabled. There is **no feature flag to set**: Codex 0.147.0 has no `codex_hooks` feature; the real flag is `hooks`, which is `stable` and enabled by default (measured, `research.md` § R-08).

Note: `.codex/README.md` currently records "matcher は公式仕様上無視される" for `UserPromptSubmit`; the current official hooks documentation describes matcher groups generally. That file is deleted by FR-001, so the discrepancy is recorded here rather than fixed there.

**`migrate-to-codex` skill** — <https://github.com/openai/skills/blob/main/skills/.curated/migrate-to-codex/SKILL.md>

- Description: "Migrate supported instruction files, skills, agents, and MCP config into Codex project and global files."
- Mappings: `CLAUDE.md`/`AGENTS.md` → `AGENTS.md`; slash commands → `.agents/skills/`; subagents → `.codex/agents/`; hooks → `.codex/hooks.json`; model/sandbox settings and MCP servers → `.codex/config.toml`; `.mcp.json` → the `config.toml` MCP section.
- Workflow: scan → review differences → plan → convert in a fixed order → dry-run → execute → validate → self-heal until clean.
- Does not modify source Claude Code files, unrelated project code, secrets, or external repositories.

### Why this is a reversal, not an increment

Three recorded decisions are contradicted by delegating to the official tools:

1. **ADR-0002** deploys Codex configuration at **user scope** (`~/.codex/`, `~/.agents/skills/`) from repo sources. The official mapping writes **project-scope** files (`.codex/hooks.json`, `.codex/config.toml`, `.codex/agents/`).
2. The deployment map deliberately routes hooks through **shared shell decision scripts** (`scripts/guardrails/*.sh`) so Claude and Codex cannot drift. The official mapping produces `.codex/hooks.json` with no stated contract about invoking those scripts.
3. Subagents are recorded as **対象外** ("Codex has no independent-context subagent equivalent" — deployment map, 019 plan D1/D2/D4, 020 research R5). The official skill maps subagents to `.codex/agents/`, and `/import` imports subagents.

## Clarifications

### Session 2026-08-10

- Q: How far does the replacement reach? → A: Remove the entire `.codex/` set, the `.agents/` links, the Codex portion of `install.sh`, and the codex-sync suites; Codex configuration is produced per use by `/import` or `migrate-to-codex`.
- Q: Are the tool-generated Codex files tracked in git? → A: No — gitignored; each developer imports for themselves. The repo ships sources (`.claude/`, `.mcp.json`) and the procedure only.
- Q: Who runs the import, and when? → A: The developer, manually, in a Codex session. `install.sh` and CI do not invoke it.
- Q: What happens to the shared guardrail wiring and the subagent exclusion? → A: (initially "keep existing decisions") superseded by the next answer for guardrails; the subagent exclusion still stands.
- Q: How is the conflict between "remove everything" and "keep the shared guardrail wiring" resolved? → A: **Full removal**, delegating guardrails to the import result — **conditional on an empirical check** that imported Codex hooks actually invoke `scripts/guardrails/*.sh`.
- Q: What replaces SYNC-01…12 as the acceptance bar? → A: All four of: procedure-existence verification, dangling-reference detection, existing suites green, and a real-session Codex verification.

### Session 2026-08-10 (follow-up: source and hook compatibility)

- Operator: the documentation host used initially may not be official; use `developers.openai.com`. → Confirmed. `developers.openai.com/codex/import` is authoritative (redirects to `learn.chatgpt.com/docs/import`). The third-party host was struck from the references entirely.
- Operator: "hooks" may denote different things in Claude and Codex; verify compatibility. → Verified against both official references. Same category and **same event names**, but a different denial contract (`continue: false` vs `permissionDecision: "deny"`), a smaller event set (11 vs ~30), an additional hash-based trust gate, and no coverage of hosted tools. See § "Hooks: the same word, and NOT the same contract". This tightens FR-006/FR-007 and adds FR-011.

### Session 2026-08-10 (post-trial decisions)

- Q: After the empirical trial, what happens to the two guardrails that do not survive (edit protection) and to `guardrails.rules` (allow/prompt policy)? → A: **Dropped on the Codex side, documented explicitly.** Codex provides destructive-command blocking and prompt secret scanning only.
- Q: Should they also be deleted from the Claude Code side, for symmetry? → A: **No — Claude side unchanged.** Recommendation accepted: symmetry would level down to the weaker platform, `pre-edit-block.sh` demonstrably fires (it blocked a `Write` to `main` during this feature's own session), and `settings.json#permissions.deny` is what actually enforces the credential-safety list. NFR-002 stands unmodified.
- Q: Does FR-014 (instructions) block the removal? → A: No. Codex merges `~/.codex/AGENTS.md` with the repo-root `AGENTS.md`, so one flattened `@`-free file satisfies it.
- Q: `/import` or `migrate-to-codex` — which does the repository actually use? → A: **Hybrid, asymmetric.** `/import` performs the setup (it writes); `migrate-to-codex` is documented for its read-only modes only (`--scan-only`, `--plan`, `--doctor`, `--dry-run`, `--validate-target`). Its write modes are excluded because they destroy the flattened `AGENTS.md` and replace skills with copies (plan D5, contract A0).
- Q: How does this survive upstream changes to the command and the skill? → A: Dated observations plus a skip-if-absent drift check plus a stated revalidation trigger — **FR-015**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A developer sets up Codex from this repo without any hand-maintained port (Priority: P1)

A developer clones the repo, runs `install.sh` for the Claude side, then opens Codex CLI and follows a documented procedure to import the Claude configuration. No `.codex/` or `.agents/` artifact in the repo participates.

**Why this priority**: This is the point of the change — the maintenance burden of the hand-written port moves to OpenAI's tooling.

**Independent Test**: On a machine with no prior `~/.codex` managed block, follow the README procedure end to end and confirm Codex sees the repo's skills and instructions.

**Acceptance Scenarios**:

1. **Given** a fresh clone, **When** the developer reads the README's Codex section, **Then** it names `/import` and `migrate-to-codex`, states where each is obtained, and states that Codex artifacts are generated locally and not tracked.
2. **Given** the documented procedure is followed, **When** the developer starts a Codex session, **Then** the repo's skills are discoverable by Codex.
3. **Given** the import has been run, **When** the developer inspects `git status`, **Then** no generated Codex artifact appears as an untracked change to be committed.

---

### User Story 2 — Runtime guardrails survive the removal (Priority: P1)

The four guardrail behaviours (destructive-command block, edit protection, post-edit format, prompt-secret block) currently reach Codex through repo-owned adapters. After removal they must either reach Codex through the import result, or their absence must be explicit and documented — never silently lost.

**Why this priority**: These are safety behaviours. Losing them without noticing is the worst outcome of this change, and full removal was accepted **only** on the condition that this is empirically checked.

**Independent Test**: In a real Codex session after import, attempt a destructive command and a protected-file edit and observe whether the guardrail fires.

**Acceptance Scenarios**:

1. **Given** the import has been run, **When** a destructive command is attempted in Codex, **Then** the guardrail either fires, or the README documents that Codex guardrails are not provided by this repo and what the developer must do instead.
2. **Given** the import result is inspected, **When** its hook configuration is read, **Then** it is recorded whether it invokes `scripts/guardrails/*.sh` or a copy — because a copy reintroduces the drift the shared scripts existed to prevent.

---

### User Story 3 — Nothing in the repo points at the removed files (Priority: P2)

`README.md`, `README.ja.md`, root `AGENTS.md`, `install.sh`, `.gitignore`, and the test suites currently reference `.codex/` and `.agents/` extensively (README.md §"Codex CLI support" and §"File structure"; root `AGENTS.md` is a single sentence pointing at `.codex/AGENTS.md`).

**Independent Test**: Grep the tree for `.codex/` and `.agents/` and confirm every remaining hit is either the new procedure documentation or a historical spec/ADR.

**Acceptance Scenarios**:

1. **Given** the removal is complete, **When** the tree is searched for references to deleted paths, **Then** no live document, script, or test resolves to a non-existent path.
2. **Given** historical records (`specs/012`–`020`, `docs/adr/*`), **When** they mention `.codex/`, **Then** they are left unmodified — they record what was true when written.

## Requirements *(mandatory)*

### Functional

- **FR-001**: The repository MUST NOT ship a hand-maintained Codex port. `.agents/skills/` (8 tracked symlinks), `.codex/AGENTS.md`, `.codex/hooks/`, `.codex/rules/`, `.codex/prompts/`, and `.codex/README.md` are removed.
- **FR-002**: `install.sh` MUST NOT deploy any Codex-side artifact. Its Claude-side behaviour (`~/.claude` sync, Claude MCP registration) is unchanged.
- **FR-003**: `tests/run-codex-sync.sh` and `tests/run-codex-sync-drift.sh` MUST be removed; no remaining suite may reference SYNC-01…12.
- **FR-004**: `README.md` and `README.ja.md` MUST document a Codex procedure stating: the two official entry points (`/import`, `migrate-to-codex`), how each is obtained, that it is run manually by the developer in a Codex session, that `/import` cannot run inside a running task / remote session / app-server-connected session, and that generated artifacts are local and untracked.
- **FR-005**: `.gitignore` MUST exclude the Codex artifacts the official tools generate at project scope (at minimum `.codex/`, `.agents/`), so an import never produces a commit-ready diff.
- **FR-006**: The documentation MUST state the guardrail position explicitly, per the settled decision: **Codex gets destructive-command blocking (`PreToolUse`/Bash) and prompt secret scanning (`UserPromptSubmit`) only. Edit-time protection (`.git/`, main/master) and the allow/prompt policy of `guardrails.rules` are NOT provided for Codex** — Codex fires `PreToolUse`/`PostToolUse` for shell commands only, and the converter has no path for `settings.json#permissions`. This absence MUST be written down, not left implicit. The Claude-side equivalents are unaffected (NFR-002).
- **FR-007** *(SATISFIED 2026-08-10 — discharged in `research.md` §§ R-08/R-09 before implementation; it has no task ID in `tasks.md` by design)*: Planning MUST include an empirical task that runs the import on a real machine and records: (a) which files it wrote and where; (b) whether the imported hook definitions invoke `scripts/guardrails/*.sh` or a copy; (c) **whether the imported hooks actually deny — i.e. whether the Claude denial contract (`permissionDecision: "deny"`, exit 2, `decision: "block"`) was translated to Codex's `continue: false`, or carried over verbatim and therefore silently fails to block**; (d) whether it produced `.codex/agents/` subagent definitions. The recorded result is an input to FR-006, FR-008 and FR-011, not an optional appendix.
- **FR-008**: If the import produces subagent definitions, the documentation MUST state that this repository does not rely on them (the exclusion recorded in 019/020 stands), so a generated `.codex/agents/` is not mistaken for a supported surface.
- **FR-009**: Root `AGENTS.md` MUST be updated; its current single sentence points at `.codex/AGENTS.md`, which FR-001 deletes.
- **FR-010**: The removal MUST be recorded in a new ADR that supersedes ADR-0002, stating the rejected alternative (keep the port) and the accepted cost (Codex configuration is no longer reproducible from this repo alone).
- **FR-011**: The documented procedure MUST include the `/hooks` trust step. Non-managed imported hooks are skipped until reviewed and trusted, and trust is keyed to the hook's hash — a procedure that stops at `/import` ships with guardrails inert.
- **FR-012**: Every Codex documentation URL in this repository MUST be on `developers.openai.com` or its `learn.chatgpt.com/docs/*` redirect target. No third-party documentation mirror may be cited.
- **FR-013**: The documentation MUST record the actual guardrail coverage in Codex, verified in `research.md` § R-03: `PreToolUse`/`PostToolUse` fire for **shell commands only**, so edit-time protection and post-edit formatting do not apply to `apply_patch`; hosted tools (e.g. WebSearch) are not covered either. Claimed coverage must not be overstated relative to Claude's.
- **FR-014**: The change MUST NOT leave Codex without this repository's operating guidance. `research.md` § R-05 shows the official path symlinks `AGENTS.md` to a root `CLAUDE.md` containing only `@.claude/CLAUDE.md`, and verifies that **Codex does not expand `@` imports** (official docs describe directory-walk concatenation only; `openai/codex` issue #17401 requesting `@include` is still open). So `.claude/CLAUDE.md` and all seven `.claude/rules/*.md` reach Codex as nothing. Satisfying this needs no new mechanism: Codex automatically merges `~/.codex/AGENTS.md` with the repo-root `AGENTS.md`, so **one flattened, `@`-free instruction file** suffices — which is what `.codex/AGENTS.md` already is. Either such a file is retained/generated, or the documentation states plainly that Codex operates without these rules.

- **FR-015**: The documentation MUST be resilient to upstream change, because every behavioural claim in it describes a moving target. Concretely:
  - **(a) Dated observations, not assertions.** Every statement about Codex or converter behaviour carries the version and date it was measured (e.g. "measured on Codex 0.147.0, 2026-08-10"), so a reader can tell a stale claim from a current one.
  - **(b) A drift check.** `tests/run-codex-drift.sh` re-derives the small set of upstream facts the documentation depends on, and **SKIPs** (not fails) when `codex` is absent, following the existing convention in `tests/run-*.sh`. Assertions are specified in `contracts/codex-setup-procedure.md` § G.
  - **(c) A revalidation trigger.** The documentation states that when the drift check warns, `quickstart.md` Steps 4–5 are re-run and the dated claims updated.

  *Justification*: within a single session (2026-08-10) the Codex CLI moved 0.130.0 → 0.147.0, the converter's own reference file proved wrong on two points while self-dated 2026-04-20, and Codex refreshed its curated-skill cache. Three claims in this very spec had to be withdrawn. Documentation that states behaviour without a date will mislead.

### Non-functional / constraints

- **NFR-001**: Historical specs and ADRs are immutable; they are not edited to match the new state.
- **NFR-002**: No Claude-side behaviour changes. `.claude/`, `scripts/guardrails/`, and every non-Codex suite are untouched.
- **NFR-003**: `scripts/guardrails/*.sh` remain in the repo regardless of the FR-007 outcome — they are the Claude hooks' decision scripts, independent of Codex.

## Success Criteria *(mandatory)*

- **SC-001** (procedure existence): Every command, skill, and acquisition path named in the new README section has been executed or resolved at least once by a human, and the confirmation is recorded in this feature's `research.md` with the date.
- **SC-002** (no dangling references): A search across `README.md`, `README.ja.md`, `AGENTS.md`, `install.sh`, `.gitignore`, `scripts/`, and `tests/` returns zero references to paths deleted by FR-001/FR-003.
- **SC-003** (suites green): After the removal, every remaining `tests/run-*.sh` passes.
- **SC-004** (real-session verification): In a real Codex CLI session following the documented procedure — including the `/hooks` trust step (FR-011) — the repo's skills are discoverable, and the guardrail behaviour observed (attempt a destructive command; attempt a protected-file edit) matches exactly what FR-006 documents. A mismatch in either direction fails this criterion.

## Risks and open items

- **R1 — REVISED.** `/import` is interactive-only, but `migrate-to-codex` ships a **non-interactive Python CLI** (`--source`/`--target`/`--scan-only`/`--plan`/`--doctor`/`--dry-run`/`--validate-target`). Automation is therefore technically available if the operator ever wants it; the "manual only" decision stands as a choice, not a constraint. See `research.md` § Method.
- **R2 — Reproducibility loss.** After this change, two developers can end up with different Codex configurations from the same commit. This is the accepted cost of the "gitignore / each developer imports" decision and belongs in the ADR's Consequences.
- **R3 — FULLY ANSWERED, and the answer is mixed.** Measured against a live Codex 0.147.0 session (`research.md` § R-09): the deny contract survives — Codex honours `permissionDecision: "deny"` emitted in Claude's format, blocking both a prompt (`UserPromptSubmit`) and a tool call (`PreToolUse`/Bash) with the shared script's reason string surfaced verbatim. But `PreToolUse`/`PostToolUse` fire for shell commands only, so **`pre-edit.sh` and `post-edit-format.sh` convert and then never run**. The operator settled the trade-off on 2026-08-10: document the absence (FR-006). No row of the coverage table rests on inference.
- **R4 — Source fidelity.** The official pages were read via summarising fetches. Planning must re-read <https://developers.openai.com/codex/import> and <https://developers.openai.com/codex/hooks> directly before the README text is finalised.
- **R5 — RESOLVED.** The official source is `developers.openai.com/codex/*` (308 → `learn.chatgpt.com/docs/*`). The non-official mirror consulted early was removed from this feature's documents entirely. Captured as FR-012.
- **R7 — The instruction gap is the largest single loss.** See FR-014 and `research.md` § R-05. Without a replacement, Codex loses skill routing, the clarification gate, the live-documentation rules, and the git conventions — i.e. everything that makes this repository's configuration worth deploying.
- **R8 — The subagent exclusion rests on an obsolete fact.** Codex has subagents (`.codex/agents/*.toml`, `SubagentStart`/`SubagentStop` events, an official subagents page), so the deployment map's stated reason no longer holds. FR-008 must re-argue the exclusion on current facts — `differences.md` offers one ("Codex custom-agent files set defaults, not hard isolation from the parent turn") — or drop it.
- **R6 — Event-set asymmetry.** Codex documents 11 lifecycle events; Claude's `UserPromptExpansion` (used by `.claude/hooks/speckit-expand-update.sh`) has no Codex counterpart. This was already recorded as 対象外 in the deployment map and does not change, but the reason disappears with that file — FR-004's documentation should carry it forward.

## References

- Codex `/import`, official — <https://developers.openai.com/codex/import> (redirects to <https://learn.chatgpt.com/docs/import>), read 2026-08-10
- Codex hooks, official — <https://developers.openai.com/codex/hooks> (redirects to <https://learn.chatgpt.com/docs/hooks>), read 2026-08-10
- Claude Code hooks reference — <https://code.claude.com/docs/en/hooks>, read 2026-08-10
- `migrate-to-codex` skill, openai/skills curated set, read 2026-08-10 — <https://github.com/openai/skills/blob/main/skills/.curated/migrate-to-codex/SKILL.md>
- This repository: `specs/012-cross-agent-guardrail-migration`, `specs/013-cross-agent-guardrail-implementation`, `specs/014-codex-config-port`, `specs/019-verify-fork-test-runner`, `specs/020-subagent-delegation-rule`, `docs/adr/0002-deploy-codex-configuration-at-user-scope.md`, `.codex/README.md`
