# Research: Remove the permissions Block Entirely

## R1 — Exact edit locations and replacement content (verified by direct reads)

### `.claude/settings.json`
Remove the `permissions` key (currently the only remaining top-level key besides `$schema`, `defaultMode`, `effortLevel`, `tui`, `alwaysThinkingEnabled`, `autoMemoryEnabled`, `enableAllProjectMcpServers`).

### `.claude/settings.local.json`
Remove the `permissions` key. Keep `prefersReducedMotion` and `spinnerTipsEnabled` unchanged.

### `.claude/rules/permissions.md`
- Opening paragraph: currently states (after spec-025's edit) "Automatic enforcement of the destructive-operation and credential-safety rules below via `.claude/hooks/` was removed with no replacement... `scripts/guardrails/*.sh` still contains the pattern-matching logic these rules describe, for reference, though nothing invokes it automatically anymore." This remains accurate (still about hooks) — no change needed here.
- Credential Safety section's closing line: "`Read` denies in `.claude/settings.json` cover the paths above and remain enforced. Prompt-level and shell-level enforcement (formerly `.claude/hooks/user-prompt-submit.sh` and `pre-bash.sh`) was removed with no automated replacement — see `specs/025-remove-claude-hooks/`." → **must change**: the Read-deny list itself is being removed by this feature. New text: "`Read` denies for these paths, prompt-level scanning, and shell-level blocking were all removed with no automated replacement — see `specs/025-remove-claude-hooks/` and `specs/026-remove-permissions-config/`. This section is policy only now; nothing in Claude Code enforces it automatically."
- "## `.claude/settings.json` permissions" section (describes the git allow/ask split and the allow-listed tools) → **remove entirely**, replace with a short note that no `permissions` configuration exists anymore in either settings file.

### README.md (English)
Three locations in `### What Codex enforces, and what it does not` (see exact old/new text below, R2).

### README.ja.md (Japanese)
Mirrored three locations (R2).

### AGENTS.md
The sentence "Claude Code no longer has an equivalent for these three either — `.claude/hooks/pre-edit.sh` was removed along with the rest of `.claude/hooks/`. The one guardrail Claude Code still enforces is `.claude/settings.json`'s `permissions` block (allow/ask/deny), which is independent of hooks and was not affected by that removal." → rewrite the last sentence: the permissions block is now also gone.

### `.claude/rules/git-workflow.md`
Line 3: "Composes with `permissions.md` (git writes stay on `ask`) and `live-documentation.md` (docs move with code)." → the "(git writes stay on `ask`)" parenthetical is a mechanical claim about settings.json that becomes false. Rewrite to "(destructive git operations require confirmation as a matter of policy, though no automated enforcement of it remains — see `specs/026-remove-permissions-config/`)".

### `tests/run-codex-references.sh`
RULE-09 (already narrowed by spec-025 to check only `permissions.deny | length >= 5`) must be removed entirely — its guarded invariant (NFR-002 from spec-021: "the Codex-import migration must not weaken Claude Code") has nothing left to check once `.permissions` doesn't exist. Remove the `if [ -f .claude/settings.json ]; then ... fi` block for RULE-09 and its check call.

## R2 — Exact README.md / README.ja.md replacement text

### README.md, intro paragraph (currently):
```
Claude Code enforces nothing automatically here anymore: `.claude/hooks/` was
removed in its entirety, with no replacement mechanism. The only guardrail
Claude Code still enforces is `.claude/settings.json`'s `permissions`
allow/ask/deny list, which is independent of hooks and unaffected by the
removal. Codex, once imported and trusted, now enforces **more** than Claude
Code does: ...
```
→ new:
```
Claude Code enforces nothing automatically here anymore, in any form:
`.claude/hooks/` was removed in its entirety, and `.claude/settings.json`'s
`permissions` allow/ask/deny block — briefly the last guardrail standing —
was removed too, with no replacement mechanism for either. Codex, once
imported and trusted, enforces guardrails Claude Code no longer does: ...
```
(rest of the paragraph, about `/hooks` trust, unchanged)

### README.md, table row (currently):
```
| Allow/prompt command policy | **yes** — `.claude/settings.json`'s `permissions` block, independent of hooks and not removed | **no** — Codex falls back to its own defaults, which ask rather than allow |
```
→ new:
```
| Allow/prompt command policy | **no** (removed too — see `specs/026-remove-permissions-config/`) | **no** — Codex falls back to its own defaults, which ask rather than allow |
```

### README.md, closing paragraph (currently):
```
**The Claude side is affected by all of this too.** `.claude/hooks/pre-edit.sh`
no longer exists — Claude Code enforces no edit protection anymore. Only
`.claude/settings.json`'s `permissions` block remains as a Claude Code
guardrail, and it does not share logic with `scripts/guardrails/*.sh`; that
sharing was specifically the now-deleted hook wrappers' job.
```
→ new:
```
**The Claude side is affected by all of this too, now completely.**
`.claude/hooks/pre-edit.sh` no longer exists, and neither does
`.claude/settings.json`'s `permissions` block — Claude Code enforces nothing
automatically here at all anymore. `scripts/guardrails/*.sh` still contains
the guardrail matching logic for reference, but nothing calls it and nothing
shares logic with it; that sharing was specifically the now-deleted hook
wrappers' job.
```

### README.ja.md — same three locations, translated in matching tone:

Intro paragraph → "Claude Code はもうこの領域で、いかなる形でも自動的に何も強制しません。`.claude/hooks/` は全ファイルが削除され、`.claude/settings.json` の `permissions` allow/ask/deny ブロック——一時的に最後の砦だったもの——も削除され、どちらにも代替の仕組みはありません。Codex は import して信頼すれば、Claude Code がもう持たないガードレールを引き続き強制します — ..."（以下 `/hooks` 信頼の記述は変更なし）

Table row → `| コマンドの allow/prompt 方針 | **なし**（こちらも削除済み — `specs/026-remove-permissions-config/` 参照） | **なし** — Codex 既定（確認を求める側）にフォールバック |`

Closing paragraph → "**Claude側もこの変更の影響を、今度は完全に受けます。** `.claude/hooks/pre-edit.sh` はもう存在せず、`.claude/settings.json` の `permissions` ブロックも同様です — Claude Code はこの領域で一切自動的に何も強制しません。`scripts/guardrails/*.sh` は参考用の判定ロジックとして残りますが、これを呼び出すものも、判定ロジックを共有するものも、もうありません（共有していたのは、削除済みのフックラッパーの役目でした）。"

## R3 — No `contracts/` artifact needed

Same rationale as spec-024/spec-025.

## R4 — New ADR numbering

`docs/adr/` currently has 0001-0004 (with a pre-existing 0004 numbering collision between "adopt-deploy-on-aws-plugin" and "adopt-official-codex-import", not this feature's concern) and 0005 (spec-025's ADR, Accepted, immutable). Next available number: **0006**.
