# Skill Interface Contract: ubiquitous-language

**Skill**: `.claude/skills/ubiquitous-language/SKILL.md`
**Version**: v1 (simplified)
**Date**: 2026-05-09

## Invocation

Single slash command: `/ubiquitous-language`

No subcommands. Behavior auto-routes based on `docs/ubiquitous-language.md` presence.

---

## Bootstrap Flow (file absent)

**Trigger**: `/ubiquitous-language` executed AND `docs/ubiquitous-language.md` does not exist.

Also triggered passively when business event expressions are detected in conversation and no UL file exists (FR-015).

**Steps**:
1. Announce file absence
2. Ask: 「業務で実際に起きる出来事を 5〜10 個挙げてください」
3. For each event: elicit roles, pre/post states, exception paths
4. Draft 7-field UL entries (mark missing fields `[NEEDS DOMAIN INPUT]`)
5. Show diff of proposed `docs/ubiquitous-language.md` and `docs/context-map.md`
6. On user confirmation: create `docs/` if absent, write both files

**Output**: `docs/ubiquitous-language.md` + `docs/context-map.md` (empty table)

---

## Maintenance Flow (file present)

**Trigger**: `/ubiquitous-language` executed AND `docs/ubiquitous-language.md` exists.

**Steps**:
1. Display queued candidates from current session (if any)
2. For each candidate: propose add / skip / custom definition
3. Check for vague-term watchlist hits in recent conversation; show replacements
4. Check for incomplete entries (`[NEEDS DOMAIN INPUT]`); re-surface them
5. If Bounded Context conflict detected: present split-or-rename choice; update `docs/context-map.md`
6. Optionally: offer to add/remove watchlist terms (persisted to `## Watchlist` section)
7. Show diff of all proposed changes; write on confirmation

**Output**: Updated `docs/ubiquitous-language.md` and/or `docs/context-map.md`

---

## Passive Collection (always-on during conversation)

**Trigger**: CLAUDE.md routing rule detects business event expressions or domain vocabulary in user messages.

**Behavior**:
- Queue candidates without interrupting the current response
- Surface batch proposal when: queue ≥ 1 AND preceding turn had zero new candidates (FR-014)
- If file absent and vocabulary detected: propose bootstrap (FR-015)

---

## Batch Proposal Format

```
## Ubiquitous Language — 更新候補

以下の用語を UL に追加/更新しますか？

| 操作 | 用語 | 検出元 | 提案定義 | Bounded Context |
|------|------|--------|---------|-----------------|
| [+] 新規 | 確定済み注文 | 会話ターン 3 | 支払い承認済みで在庫引当対象の注文 | 販売 |
| [!] 曖昧語 | ユーザー | spec.md line 12 | → 契約管理者 / 利用者 / 請求担当者 | — |

回答例: "全て追加" / "1のみ" / "スキップ" / "1は [カスタム定義]"
```

---

## Invariants (all flows)

1. **Diff before write**: Every file write is preceded by showing the diff.
2. **Explicit confirmation**: No file is written without user confirmation.
3. **No silent Bounded Context unification**: Conflicts always present split-or-rename choice.
4. **No speckit references**: SKILL.md contains no mention of speckit, spec-kit, or speckit commands.

---

## Out of Scope (v1)

- Source code file scanning
- Database schema introspection
- Machine translation of domain terms
- Per-Bounded-Context file splitting (deferred to v2)
