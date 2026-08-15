# Research: Remove .claude/hooks/ Entirely

## R1 — Exact edit locations (verified by direct reads, not the impact-survey subagent's summary alone)

A subagent survey (see conversation) produced an initial impact list; the locations below were confirmed by directly reading each file before writing this plan, since several require substantive rewrites (not mechanical deletion) and rewrite quality depends on exact context.

### `.claude/settings.json`
- Remove the entire `hooks` key (currently `PreToolUse` ×2 matchers, `PostToolUse` ×1, `UserPromptSubmit` ×1, `UserPromptExpansion` ×1 — all four event types).
- Remove the top-level `statusLine` key (`{"type": "command", "command": "\"$HOME\"/.claude/hooks/statusline.sh"}`).

### `install.sh`
- Line 3 (top comment): "Idempotent: re-running refreshes hooks/rules/skills/settings..." — drop "hooks/" from the list.
- Line 55 (section comment): "1. Sync managed .claude paths (prevents stale skills/rules/hooks)" — drop "hooks".
- Line 58: `sync_path "hooks"` — **keep this call** (not delete). Precedent from spec-024: a `sync_path` call for a now-empty source is the mechanism that removes the stale directory from `~/.claude/` on next install (mirrors why `sync_path "commands"` was kept after spec-019 emptied `.claude/commands/`). Removing the call would leave `~/.claude/hooks/` stranded on every machine that doesn't get a fresh sync pass.
- Lines 80-83 (guardrails section comment): references "`.claude/hooks/*.sh` resolve this installed copy once deployed" and "Hooks imported into Codex resolve the same scripts" — needs rewording since `.claude/hooks/*.sh` no longer exists; the guardrail scripts themselves are unaffected (still synced at this step) but the sentence describing *why* needs updating to note the caller is gone, only direct/manual/test invocation remains.
- Line 95: `chmod +x "$TARGET_DIR"/hooks/*.sh` — **must be removed or guarded**. Unlike `sync_path "hooks"` (which handles an absent source gracefully via its own `[ -d "$src" ]` check), a bare `chmod +x` on a glob that matches nothing (because the source `.claude/hooks/` is empty/gone, so `sync_path` never repopulated `$TARGET_DIR/hooks/`) will error in most shells when nullglob is off. Remove this line entirely — there is nothing left to chmod.
- Line 167: `echo "Codex hook trust: start Codex and use /hooks to review and trust new or changed user hooks before relying on guardrails."` — this is about **Codex's own** hooks (via its independent `/import`), not `.claude/hooks/`. Per the maintainer's explicit "Codex is not a design constraint" direction, left unmodified — it doesn't reference `.claude/hooks/` and stays accurate regardless of this change.

### `README.md` (English)
- Line 44 area ("What this provides" bullets) and lines 62-63 (scripts/guardrails bullet: "`.claude/hooks/pre-bash.sh`, `pre-edit.sh`, `post-edit-format.sh`, and `user-prompt-submit.sh` are thin wrappers around these") — remove the wrapper-file references; the `scripts/guardrails/` bullet itself stays (those files aren't deleted) but its description of being "wrapped" by now-nonexistent files must be rewritten to describe their current (caller-less) state.
- Lines 128-148: `### What Codex enforces, and what it does not` — **substantive rewrite** (see R2 below for the exact replacement content).
- Lines 150-165 (the "Two more things worth knowing" + "The Claude side is unaffected by all of this" paragraph) — the "unaffected" claim is now false; rewrite to state Claude Code's side is *equally* affected (it has no hooks left) rather than exempt.
- File-structure tree (~283-288): remove the `hooks/` subtree listing.
- Line ~383-384 (Spec Kit git extension section): "A hook supports this per-project workflow (see [`.claude/hooks/README.md`]...): `speckit-expand-update.sh` keeps..." — this entire paragraph describes a deleted feature (Spec Kit auto-update hook) with no replacement; remove it, and note (per FR-006's spirit) that keeping Spec Kit current is now a manual `specify init`/`specify self upgrade` step, matching what `AGENTS.md`'s "Requests" section already tells Codex to do ("Keep Spec Kit current by running `specify init`... periodically").

### `README.ja.md` (Japanese mirror)
- Line 6 (intro): "`.claude/` ディレクトリ全体を `~/.claude/` に同期することで、settings/rules/skills/hooks/memory を..." — drop "hooks" from the enumerated list (settings/rules/skills/memory remain accurate; hooks no longer does).
- Lines 29-30 (skill/hooks bullets): `.claude/hooks/pre-bash.sh` and `.claude/hooks/user-prompt-submit.sh` bullets — remove both.
- Line 45 area (scripts/guardrails description, mirrors README.md 62-63) — same rewrite.
- Lines ~107-109 (mirrors README.md's "Claude側はこの変更の影響を受けません" paragraph) — same rewrite as R2/English equivalent, translated.
- The Claude/Codex comparison table (mirrors README.md 135-142) — same substantive rewrite, translated.
- Line 160 area (file-structure tree) — remove `hooks/` line.
- Lines ~236-237 (Spec Kit git extension section, mirrors README.md ~383-384) — same removal.

### `AGENTS.md`
- Line 61: "Editing Claude Code settings (`.claude/settings.json`, `.claude/settings.local.json`): verify hook paths and permission rules still resolve." — "verify hook paths" no longer applies (no hooks exist to have paths); reword to "verify permission rules still resolve" only.
- Line 66: "Don't paste secrets ... — see 'Enforced via hook or rule' below for the automated backstop." — the backstop being pointed to (Claude Code's own former secret-scanning hook) no longer exists; the section below (line 72) is titled "(Codex CLI only)" and already scopes itself to Codex. Reword this cross-reference so it doesn't imply Claude Code still has an automated backstop.
- Line 90: "Claude Code's equivalents are unaffected and still enforced there — `.claude/hooks/pre-edit.sh` and `.claude/settings.json`'s `permissions` block, both sharing decision logic with Codex's working guards via `scripts/guardrails/*.sh`." — **false after this change**. Rewrite: `.claude/hooks/pre-edit.sh` is gone (Claude Code no longer enforces edit protection either); only `settings.json`'s `permissions` block remains as a Claude Code guardrail, and it doesn't share logic with `scripts/guardrails/*.sh` (that sharing was specifically the now-deleted hook wrappers' job).
- Section title/framing "## Enforced via hook or rule (Codex CLI only)" and its intro ("it is **less** than what Claude Code enforces") — the *comparison direction* is now backwards for the three previously-"yes" Claude Code rows referenced by this section's framing. This section describes what *Codex* enforces, which itself is factually unaffected (Codex's own hooks are independent) — but the framing sentence "it is less than what Claude Code enforces" becomes false and must be corrected (Codex now enforces destructive-command blocking and prompt-secret scanning; Claude Code enforces neither).

## R2 — Replacement content for the Claude/Codex comparison table

Old table (README.md 135-142), all rows currently "yes" for Claude Code:

| Guardrail | Claude Code | Codex |
|---|---|---|
| Destructive command blocking | yes | yes, once trusted |
| Prompt secret scanning | yes | yes, once trusted |
| Edit protection (`.git/`, `main`/`master`) | yes | no |
| Post-edit formatting / linting | yes | no |
| Allow/prompt command policy | yes | no |
| Spec Kit prompt expansion | yes | no |

New reality after this feature:

| Guardrail | Claude Code | Codex |
|---|---|---|
| Destructive command blocking | **no** (removed) | yes, once trusted — Codex's own import, unaffected by this change |
| Prompt secret scanning | **no** (removed) | yes, once trusted |
| Edit protection (`.git/`, `main`/`master`) | **no** (removed) | no |
| Post-edit formatting / linting | **no** (removed) | no |
| Allow/prompt command policy | yes — `.claude/settings.json`'s `permissions` block, independent of hooks, not removed | no |
| Spec Kit prompt expansion | **no** (removed) | no |

The explanatory paragraph below the table (README.md 144-148, about Codex's structural `PreToolUse`/`PostToolUse` shell-only limitation) stays accurate for Codex's rows and needs no change; only the "unaffected"/comparison framing sentences around it need correction (R1).

## R3 — No `contracts/` artifact needed

Same rationale as spec-024 R3: purely internal repository-maintenance change, no external interface.

## R4 — Subagent delegation plan for implementation

Per the maintainer's explicit "use subagents" instruction (process, not architecture — confirmed in spec.md Assumptions), the implementation phase will delegate the high-volume, mechanical portions to subagents and keep the judgment-heavy rewrites (comparison table content, AGENTS.md framing sentence, install.sh comment wording) in the main conversation, since "never delegate understanding" (subagent-delegation.md) means a subagent should execute predetermined text, not decide how to reword a security-comparison table. Concretely: the file deletions (7 hook files, 1 test file) and the mechanical settings.json/install.sh edits are small enough to do directly; the bulk multi-location README.md/README.ja.md edits (~12 and ~8 locations, mostly mechanical removal of dead references, with the two substantive rewrites already fully drafted in R1/R2 above so a subagent only needs to apply them) are good candidates for delegation since they're self-contained, verifiable by grep, and the exact replacement text is already decided here — nothing is left to the subagent's judgment.
