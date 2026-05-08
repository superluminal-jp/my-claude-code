# Skill Interface Contract: ubiquitous-language

**Skill**: `.claude/skills/ubiquitous-language/SKILL.md`
**Version**: v1
**Date**: 2026-05-08

## Invocation Modes

### Mode A: Lifecycle Hook (invoked by external hook system)

**Trigger**: Invoked as `ubiquitous-language.collect` from any lifecycle hook system (e.g., speckit's `extensions.yml` `before_*` entries). The skill does not know or depend on which system issued the call.

**Entry conditions**:
- UL store path is discoverable (default: `.specify/ubiquitous-language/` relative to project root)
- An artifact may be present in the current session context (optional — if absent, runs bootstrap check only)

**Input**: none (skill detects context by reading the UL store and any artifact present in the current session; does not read speckit-specific files directly)

**Output**:
- If no UL exists: bootstrap elicitation flow → produces `.specify/ubiquitous-language/<bc-name>.md`
- If UL exists: validation sweep of the current artifact being processed → produces Drift Report (in-conversation) and/or queued candidate prompts

---

### Mode B: Slash Command (user-invoked)

**Trigger**: User types `/ubiquitous-language [subcommand]`

**Subcommands**:

| Subcommand | Description |
|---|---|
| *(none)* | Run validation sweep on current project; surface all queued candidates |
| `bootstrap` | Force bootstrap elicitation for a new or additional BC |
| `show [bc-name]` | Display current UL table for the named BC |
| `add [term]` | Interactively add a new term to specified BC |
| `check` | Run vague-term watchlist scan on the most recently generated artifact |

---

### Mode C: Conversational (CLAUDE.md persistent rule)

**Trigger**: CLAUDE.md rule activates when `.specify/ubiquitous-language/` exists in the project and domain vocabulary is detected in user messages.

**Entry conditions**:
- `.specify/ubiquitous-language/` directory exists (UL has been bootstrapped)
- User message contains business events (verb-past-form), state names, or role names

**Behavior**:
- Monitor passively: queue candidates, do NOT interrupt current response
- Surface batch proposal at natural conversation pause (FR-031)
- Do NOT activate if UL collection was already triggered in the same session turn (deduplication — avoid double-processing)

---

## Outputs (all modes)

### Batch Proposal (in-conversation text)

```
## Ubiquitous Language — 更新候補

以下の用語を UL に追加/更新しますか？

| 操作 | 用語 | 検出元 | 提案定義 | BC |
|------|------|--------|---------|-----|
| [+] 新規 | 支払い承認済み | スペック §2 | 決済事業者から承認コードを受領した状態 | 販売 |
| [!] 曖昧語 | ユーザー | spec.md line 42 | → 契約管理者 / 利用者 / 請求担当者 のいずれか | — |
| [~] ドリフト | Order.confirm() | plan.md | UL には Order.process() が記録済み | 販売 |

回答例: "全て追加" / "1のみ" / "スキップ" / "1は [カスタム定義]"
```

### UL File Update (after user confirmation)

- Target: `.specify/ubiquitous-language/<bc-name>.md`
- Operation: Append row / Update row / Delete row
- Diff is shown before write; write requires explicit confirmation (FR-018)

### Drift Report (in-conversation, transient)

```
## UL ドリフト検知

| 場所 | 記述 | UL の期待値 | 推奨アクション |
|------|------|-----------|--------------|
| plan.md §3 | Order.process() | Order.confirm() | A) artifact 修正 / B) UL 更新 / C) 新語として分離 |
```

---

## Error / Edge Conditions

| Condition | Behavior |
|---|---|
| UL store path not discoverable | Do nothing; note once that UL collection requires a discoverable UL store path (default: `.specify/ubiquitous-language/`) |
| User defers all candidates | Queue persists; re-surface at next trigger |
| BC budget exceeded (> 30 entries) | Propose split before adding new entry; block write until resolved |
| Conflicting BC definitions detected | Present 3-option conflict resolution (split / merge / rename); block unification |
| Vague term in final artifact with no replacement agreed | Block artifact acceptance with warning; allow override with explicit acknowledgement |

---

## Non-Interface (out of scope for this contract)

- Source code file scanning
- Database schema introspection
- External API contract comparison
- Machine translation of domain terms
