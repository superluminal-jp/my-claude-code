# Decision Record: Cross-Agent Guardrail & Rule Migration (Codex CLI / Cursor)

**Source**: [spec.md](./spec.md)'s `## Clarifications` (2026-07-19 session, 14/14 items resolved)

**Scope**: For each of the 14 Claude Code-specific hooks/rules in this repository's `.claude/`, this record states whether it was unified into a shared `AGENTS.md` (and at what strength), reimplemented natively per tool, migrated to a non-agent-level control, or kept Claude Code-only — for compatibility with OpenAI Codex CLI and Cursor. **No `AGENTS.md` content, hook scripts, or other implementation artifacts are produced here** — this document is the decision only (per `spec.md` FR-008 / SC-004). Each item below is self-contained and can be read independently of the others (per SC-002).

## How to read each entry

- **Current behavior**: what the Claude Code hook/rule does today, and whether it's a hard block, soft warning, or automation.
- **Options considered**: the choices presented to the maintainer, drawn from this session's prior guardrail-mechanism research.
- **Recorded verdict**: the chosen option. Labeled per tool (Codex CLI / Cursor) wherever the underlying research showed the two tools support this differently (per FR-007 / SC-003); otherwise one verdict applies to both.
- **Rationale**: why, including which recommended option (if any) the maintainer overrode.
- **Unconfirmed dependency**: flagged when the verdict relies on a research finding (`research.md` R1–R5) with only Medium confidence — i.e., not verified against the tool vendor's primary documentation in this session (per FR-009).

---

## P1 — Low-Cost Unification (zero enforcement loss)

These four items were already plain prose in Claude Code (no blocking exit code), so unifying them into `AGENTS.md` loses nothing.

### Q1 — `pre-edit.sh`: CI/settings/production-file edit warnings

- **Current behavior**: Soft warning (not a block) written to stderr when editing `.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`, `.claude/settings.json` / `.claude/settings.local.json`, or `*.prod.*` / `*production*` / `*.env.production` files.
- **Options considered**: (A) Unify into `AGENTS.md`; (B) Keep Claude Code-only.
- **Recorded verdict**: **Unify (both tools)** — transcribe the warning text verbatim into `AGENTS.md`.
- **Rationale**: The source was already non-blocking, so moving it to prose costs nothing in effectiveness.
- **Unconfirmed dependency**: None (R5 — `AGENTS.md` is read natively by both tools — is High confidence).

### Q2 — `tools.md`: "prefer dedicated tools" / "parallelize independent calls" principles

- **Current behavior**: Prose guidance naming Claude Code tools by name (`Read`/`Edit`/`Grep` over Bash; batch independent tool calls in one turn).
- **Options considered**: (A) Unify with tool names genericized to each tool's own vocabulary; (B) Unify verbatim with Claude Code tool names as-is; (C) Keep Claude Code-only.
- **Recorded verdict**: **Unify, Option A (both tools)** — genericize the tool names before transcribing into `AGENTS.md`.
- **Rationale**: The underlying principle (structured tools over shell greps; batch independent work) is tool-agnostic; only the specific tool names needed rewording.
- **Unconfirmed dependency**: None — this is a prose principle, not dependent on any tool-capability claim.

### Q3 — `skill-routing.md`: Skill routing table

- **Current behavior**: Prose table mapping request types to which Claude Code Skill to load (`coder`, `advisor`, `clarifier`, etc.).
- **Options considered**: (A) Unify, with the precondition that SKILL.md files must be discoverable by each tool stated explicitly; (B) Defer unification until SKILL.md cross-tool support is primary-source-verified; (C) Keep Claude Code-only.
- **Recorded verdict**: **Unify, Option A (both tools)** — transcribe the routing table into `AGENTS.md`, with the discoverability precondition stated as an open dependency.
- **Rationale**: The table itself is plain prose; its practical usefulness depends on where the actual `SKILL.md` files live for each tool, which is called out rather than silently assumed.
- **Unconfirmed dependency**: **Yes** — SKILL.md cross-tool discoverability (part of `research.md` R2/R5's Cursor-side claims) is Medium confidence; re-verify against primary docs before relying on this for Codex CLI or Cursor specifically.

### Q4 — `mcp.md`: MCP server catalog and usage rule

- **Current behavior**: Prose catalog table plus a "you MUST call the matching MCP server for AWS/GCP/Azure questions" instruction. No code-level enforcement — always was just an instruction.
- **Options considered**: (A) Unify near-verbatim; (B) Keep Claude Code-only.
- **Recorded verdict**: **Unify, Option A (both tools)** — transcribe near-verbatim into `AGENTS.md`.
- **Rationale**: Lowest migration cost of all 14 items — prose to prose, contingent only on each tool having the same MCP servers connected under its own config format.
- **Unconfirmed dependency**: None.

---

## P2 — Per-Tool Tradeoff Items (Cursor has more native hook coverage than Codex CLI today)

### Q5 — `user-prompt-submit.sh`: secret detection in submitted prompts

- **Current behavior**: Hard block (`exit 2`) before the prompt reaches the model, when it matches AWS/GitHub/Slack/Google key patterns or a private-key header.
- **Options considered**: (A) Cursor: reimplement via `beforeSubmitPrompt`; Codex: no confirmed equivalent, documented as a gap; (B) Neither tool gets anything; (C) Both tools get a prose-only "don't paste secrets" note, no hook.
- **Recorded verdict — Cursor**: **Weak unify** — prose-only note in `AGENTS.md`, no `beforeSubmitPrompt` hook implementation.
- **Recorded verdict — Codex CLI**: **Weak unify** — same prose-only note, no hook (no viable hook confirmed regardless).
- **Rationale**: The maintainer declined the recommended option (A: implement the real Cursor hook) in favor of the simpler, weaker prose-only treatment for both tools. **The Claude Code hard block is unaffected and remains in place** — it is materially stronger than what either other tool gets.
- **Unconfirmed dependency**: **Yes** — Cursor's `beforeSubmitPrompt` hook (R2) is Medium confidence and was never implemented here regardless, so this is a moot dependency for the chosen verdict but would matter if this decision is revisited.

### Q6 — `pre-bash.sh`: destructive-command blocking

- **Current behavior**: Hard block (`exit 2`, or routes to user confirmation) before Bash execution — covers force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, `mkfs`/`dd`/fork-bombs, `curl|bash`, non-HTTPS requests, credential-path reads/writes, and global package installs; routes `sudo` to confirmation.
- **Options considered**: (A) Extract the matching logic into one shared script, with thin adapters for Claude Code's hook, Codex's `PreToolUse` (Bash), and Cursor's `beforeShellExecution` (`failClosed: true`); (B) Cursor only; (C) Keep Claude Code-only.
- **Recorded verdict**: **Unify, Option A (both tools)** — shared script + three thin adapters.
- **Rationale**: This is the **only item, of all 14, where real enforcement can be reproduced across all three tools** — all three support a "receive the command via stdin JSON, return allow/deny/ask via stdout" hook shape. Flagged as the highest-priority follow-up implementation item.
- **Unconfirmed dependency**: **Yes** — depends on `research.md` R1 (Codex `PreToolUse` is Bash-scoped, Medium confidence), R2 (Cursor's `beforeShellExecution` shape, Medium confidence), and R3 (Cursor's `permissions.json` is explicitly not a security guarantee, so the adapter must use the hook, not the allowlist — Medium-high confidence). All three should be re-verified against primary vendor docs before the shared script is built.

### Q7 — `post-edit-format.sh`: auto-formatting after edits

- **Current behavior**: Automation (not a block) — runs `shfmt`/`shellcheck`/`yamllint`/`jq` on edited files by extension; checks CLAUDE.md `@import` paths resolve.
- **Options considered**: (A) Cursor: reimplement via `afterFileEdit`; Codex: prose-only instruction (edit-time hook coverage unconfirmed); (B) Both tools get a prose-only instruction, no hook for either; (C) Neither tool gets anything.
- **Recorded verdict**: **Weak unify, Option B (both tools)** — prose-only "run shfmt/shellcheck after editing .sh files" instruction in `AGENTS.md`, no `afterFileEdit` hook implementation for Cursor despite it being viable.
- **Rationale**: The maintainer declined the recommended per-tool split (implementing Cursor's working hook) in favor of the simpler uniform prose-only treatment. Execution is not guaranteed for either tool.
- **Unconfirmed dependency**: **Yes** — Codex's edit-time hook coverage (R1, Medium confidence) remains unverified; moot for the chosen verdict but relevant if this is revisited to add the Cursor hook later.

### Q8 — `recommend-speckit.sh`: Spec Kit adoption nudge

- **Current behavior**: Soft nudge (not a block) — suggests running `specify init` when a prompt looks like non-trivial implementation work and `.specify/` doesn't exist yet, throttled to once per 7 days via a cache file.
- **Options considered**: (A) Unify, accepting the loss of the throttle (repeated nudging risk); (B) Unify without any throttle-related caveat; (C) Keep Claude Code-only.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — add a "suggest Spec Kit once, don't insist" instruction to `AGENTS.md`, with no throttle mechanism.
- **Rationale**: The maintainer declined the recommended "keep Claude-only" option, accepting the repetition risk since the throttle cache file has no prose equivalent — the resulting `AGENTS.md` guidance is weaker than the original (a real, working de-duplication guarantee becomes an unenforced "don't insist" request).
- **Unconfirmed dependency**: None — this doesn't depend on any tool-hook capability, only on `AGENTS.md` being read (R5, High confidence).

---

## P3 — No Cross-Agent Hook Equivalent (neither tool has a pre-edit block hook today)

### Q9 — `pre-edit.sh`: main/master-branch direct-edit block

- **Current behavior**: Hard block (`exit 2`) before any Edit/Write/Delete tool call when the current git branch is `main` or `master`.
- **Options considered**: (A) Prose-only "don't edit main directly" note in `AGENTS.md`, no enforcement; (B) Migrate to GitHub Branch Protection (a non-agent-level control) as the actual replacement guardrail; (C) Do nothing for Codex/Cursor.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — prose-only note, no enforcement.
- **Rationale**: **The recommended option (B: GitHub Branch Protection) was explicitly considered and declined.** Neither Codex CLI nor Cursor has a hook that fires *before* a file edit completes (Codex's file-edit tools aren't covered by `PreToolUse`; Cursor's `afterFileEdit` fires only after the edit), so no tool-level hook can reproduce this block. Branch Protection remains available as a future option if the prose-only note proves insufficient.
- **Unconfirmed dependency**: **Yes** — depends on `research.md` R1/R4 (neither tool has a pre-edit block hook), Medium confidence.

### Q10 — `pre-edit.sh`: `.git/`-direct-edit block

- **Current behavior**: Hard block (`exit 2`) before any Edit/Write/Delete tool call targeting a path under `.git/`.
- **Options considered**: (A) Prose-only note in `AGENTS.md`; (B) Do nothing; (C) Keep Claude Code-only.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — prose-only "don't edit `.git/` directly" note, no enforcement.
- **Rationale**: Same underlying constraint as Q9 (no pre-edit hook exists in either tool), but lower frequency/impact, so the maintainer chose the same weak-unify treatment rather than "keep Claude-only."
- **Unconfirmed dependency**: **Yes** — same as Q9 (R1/R4, Medium confidence).

### Q11 — `session-start.sh`: lint toolchain bootstrap

- **Current behavior**: Automation, Claude Code on the web-specific — installs `jq`/`shellcheck`/`yamllint`/`shfmt` at session start if missing, only when `CLAUDE_CODE_REMOTE=true`.
- **Options considered**: (A) Prose note in `AGENTS.md` documenting the toolchain expectation (no execution trigger); (B) Do nothing; (C) Keep Claude Code-only, treat as out of scope.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — prose note stating `shfmt`/`shellcheck`/`yamllint`/`jq` are expected to be present.
- **Rationale**: The maintainer declined "keep Claude-only." Note that this verdict produces **documentation of an assumption, not an actionable instruction** — there is no hook or trigger in either tool that would cause the toolchain to actually be installed as a result of this note.
- **Unconfirmed dependency**: None beyond R5 (`AGENTS.md` is read) — the gap here isn't a hook-capability question, it's that no equivalent "session start" lifecycle event was found for either tool at all.

### Q12 — `speckit-expand-update.sh`: Spec Kit CLI auto-update

- **Current behavior**: Automation — checks/upgrades `specify-cli` and re-runs `specify init --here --force` before `/speckit-*` commands and at session start, with `constitution.md` backup/restore protection.
- **Options considered**: (A) Prose note in `AGENTS.md` pointing to `specify init` as the update mechanism; (B) Do nothing; (C) Keep Claude Code-only.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — prose pointer to `specify init`.
- **Rationale**: The maintainer declined "keep Claude-only." The automatic version-check/reinstall/constitution-protection procedure itself is not reproduced — only a pointer to the manual command.
- **Unconfirmed dependency**: None — this is procedural automation, not dependent on a tool-hook capability; Spec Kit's own per-tool integration support (separate from this feature's guardrail research) would be the relevant thing to check if this is revisited.

### Q13 — `tools.md`: Memory section

- **Current behavior**: Prose policy for reading/writing Claude Code's built-in long-term Memory tool (`autoMemoryEnabled`).
- **Options considered**: (A) Mechanism-agnostic prose note in `AGENTS.md` ("persist decisions/conventions for reuse"), no reference to the Claude Memory tool; (B) Do nothing; (C) Keep Claude Code-only.
- **Recorded verdict**: **Weak unify, Option A (both tools)** — mechanism-agnostic note, no tool reference.
- **Rationale**: The maintainer declined "keep Claude-only." Since neither tool is confirmed to have an equivalent persistent-memory mechanism, the note deliberately avoids naming Claude Memory so it doesn't read as an instruction to call a tool that doesn't exist.
- **Unconfirmed dependency**: None named — this verdict is intentionally mechanism-agnostic specifically because no equivalent mechanism was confirmed for either tool.

### Q14 — `tools.md`: Subagents section

- **Current behavior**: Prose policy naming Claude Code's `Agent` tool and `subagent_type` values (e.g. `Explore`) for delegating broad exploration.
- **Options considered**: (A) Unify a mechanism-agnostic principle ("delegate broad exploration to protect context"), stripped of Claude Code-specific names; (B) Do nothing; (C) Keep Claude Code-only.
- **Recorded verdict**: **Unify, Option A (both tools)** — mechanism-agnostic principle only.
- **Rationale**: Unlike Q13, this item needed no hook to begin with — it's a principle, not an enforcement mechanism — so once the Claude Code-specific tool names are stripped, there's no loss in unifying it. Full (not weak) unification.
- **Unconfirmed dependency**: None — this is a prose principle, not dependent on either tool's specific parallel/background-execution feature set.

---

## Verdict summary

| # | Item | Verdict class | Codex CLI | Cursor |
|---|---|---|---|---|
| Q1 | `pre-edit.sh` CI/settings/production warnings | Unify (full) | Same | Same |
| Q2 | `tools.md` dedicated-tools/parallel principles | Unify (full) | Same | Same |
| Q3 | `skill-routing.md` routing table | Unify (full) | Same | Same |
| Q4 | `mcp.md` catalog + usage rule | Unify (full) | Same | Same |
| Q5 | `user-prompt-submit.sh` secret detection | Unify (weak) | Prose only | Prose only (hook declined) |
| Q6 | `pre-bash.sh` destructive-command blocking | Unify (full, real hook) | `PreToolUse` (Bash) adapter | `beforeShellExecution` adapter |
| Q7 | `post-edit-format.sh` auto-formatting | Unify (weak) | Prose only | Prose only (hook declined) |
| Q8 | `recommend-speckit.sh` nudge | Unify (weak — loses throttle) | Same | Same |
| Q9 | `pre-edit.sh` main/master block | Unify (weak) | Prose only (Branch Protection declined) | Prose only |
| Q10 | `pre-edit.sh` `.git/` block | Unify (weak) | Prose only | Prose only |
| Q11 | `session-start.sh` lint bootstrap | Unify (weak, non-actionable) | Prose only | Prose only |
| Q12 | `speckit-expand-update.sh` auto-update | Unify (weak) | Prose only | Prose only |
| Q13 | `tools.md` Memory section | Unify (weak, mechanism-agnostic) | Prose only | Prose only |
| Q14 | `tools.md` Subagents section | Unify (full, mechanism-agnostic) | Same | Same |

**Totals**: 14/14 items decided. 6 full unifications, 8 weak (prose-only) unifications, 0 kept Claude Code-only, 0 dropped. One item (Q6) is flagged as the highest-priority real-enforcement follow-up implementation.

## Items depending on unconfirmed (Medium-confidence) research

Per FR-009, these verdicts should be re-verified against each tool's primary documentation before further action is taken on them: **Q3** (SKILL.md discoverability), **Q5** (Cursor `beforeSubmitPrompt`, moot for the chosen verdict), **Q6** (Codex `PreToolUse` scope, Cursor `beforeShellExecution` shape, Cursor `permissions.json` non-guarantee), **Q7** (Codex edit-time hook coverage, moot for the chosen verdict), **Q9** and **Q10** (absence of a pre-edit block hook in either tool). See `research.md` R1–R4 for the underlying claims and why primary-source access was unavailable in the session that produced this record.
