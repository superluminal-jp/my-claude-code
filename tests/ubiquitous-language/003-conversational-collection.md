# Test Scenario: Conversational-Mode Passive Collection

**Feature**: 003-ubiquitous-language
**Covers**: FR-030, FR-031, FR-032
**User Story**: US2

---

## Setup

- `.specify/ubiquitous-language/sales.md` exists (UL has been bootstrapped)
- No `/speckit-*` command is used in this scenario
- CLAUDE.md routing rule for `ubiquitous-language` is active

---

## Scenario 1: Business Events in Chat Are Queued

**Input to Claude** (plain chat message, no slash command):

```
注文が確定されると在庫引当が走ります。引当に失敗した場合は注文が保留状態になり、
在庫補充後に再引当が試みられます。
```

**Expected behavior**:
1. Skill activates passively (does NOT interrupt the current response)
2. Queues the following candidates:
   - 在庫引当 (new-concept)
   - 保留状態 (new-concept / possible state name)
   - 在庫補充 (new-concept)
   - 再引当 (new-concept)
3. The current response answers the user's question WITHOUT mentioning UL collection mid-response

**Pass criteria**:
- Current response is delivered normally (no mid-response interruption)
- Candidates are NOT surfaced immediately — they go into queue

---

## Scenario 2: Batch Proposal at Natural Pause

**Input to Claude** (next message with no new domain vocabulary):

```
ありがとうございます。よく分かりました。
```

**Expected behavior**:
1. Skill detects no new domain vocabulary in this turn
2. Triggers batch proposal for all queued candidates

**Expected output**:

```
## Ubiquitous Language — 更新候補

以下の用語を UL に追加/更新しますか？

| 操作 | 用語 | 検出元 | 提案定義 | BC |
|------|------|--------|---------|-----|
| [+] 新規 | 在庫引当 | 会話ターン N | 確定済み注文に対して在庫を予約・確保する処理 | 販売 |
| [+] 新規 | 保留状態 | 会話ターン N | 在庫引当に失敗し再試行待ちの注文状態 | 販売 |
| [+] 新規 | 在庫補充 | 会話ターン N | 在庫不足を解消するための補充入荷処理 | 在庫管理 |
| [+] 新規 | 再引当 | 会話ターン N | 在庫補充後に保留注文に対して再度行う引当処理 | 販売 |

回答例: "全て追加" / "1のみ" / "スキップ" / "1は [カスタム定義]"
```

**Pass criteria**:
- Batch proposal appears at the natural pause (not mid-response)
- All 4 terms are proposed
- User can select individually or in bulk

---

## Scenario 3: No-Activation Guard (FR-032)

**Setup**: No `.specify/ubiquitous-language/` directory exists

**Input to Claude** (plain chat):

```
注文が確定されると在庫引当が走ります。
```

**Expected behavior**:
1. Skill checks for UL store
2. Does NOT activate collection (no UL store discoverable)
3. Notes once (not on every message) that UL collection requires a discoverable store

**Pass criteria**:
- No batch proposal appears
- No interruption to normal conversation
- Note appears at most once per session

---

## Invariant Checks

- [ ] Current response is never interrupted by UL collection
- [ ] Batch proposal appears only at natural pauses or lifecycle events
- [ ] Deferred items re-surface at the next trigger
- [ ] No activation when UL store is not discoverable
