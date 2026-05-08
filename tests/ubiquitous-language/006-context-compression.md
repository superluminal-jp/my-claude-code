# Test Scenario: Context Compression — Ontology Header and Delta Notation

**Feature**: 003-ubiquitous-language
**Covers**: FR-022, FR-023, FR-024
**User Story**: US4

---

## Setup

- `.specify/ubiquitous-language/sales.md` contains ≥ 20 confirmed entries
- A new speckit command is being started (session or lifecycle event start)

---

## Scenario 1: Ontology Header at Session Start

**Input to Claude**:

```
/speckit-specify 新しい返品機能の仕様を作成してください。
```

**Expected behavior**:
1. Skill detects ≥ 5 confirmed UL terms in the store
2. Injects Ontology Header at the start of the response (before generating the spec)

**Expected Ontology Header format**:

```
## Ubiquitous Language Reference (BC: 販売)

| 用語 | 1行定義 |
|------|---------|
| 確定済み注文 | 支払い承認済みで在庫引当対象の注文 |
| キャンセル可能注文 | 出荷指示前かつキャンセル期限内の注文 |
| 在庫引当 | 確定済み注文に対して在庫を予約・確保する処理 |
...（最大 30 エントリ / BC）
```

**Pass criteria**:
- Ontology Header appears before the generated artifact
- Maximum 30 entries per BC
- Each row has 用語 + 1-line definition (not full 7-field entry)
- Stateful terms use arrow notation: `状態A → 状態B → 状態C`

---

## Scenario 2: Paraphrase Detection and Substitution Proposal

**Input to Claude** (user submits a spec draft containing paraphrases):

```
## 機能仕様

支払いが承認されて在庫を確保できる状態になった注文は、
出荷指示前かつキャンセル期限内であれば返品リクエストを受け付けられる。
```

**Expected behavior**:
1. Skill detects paraphrase of registered UL term:
   - 「支払いが承認されて在庫を確保できる状態になった注文」 → UL: 「確定済み注文」
   - 「出荷指示前かつキャンセル期限内」 → UL: 「キャンセル可能注文」
2. Presents substitution proposal with diff

**Expected output**:

```
## 言い換え検知

「支払いが承認されて在庫を確保できる状態になった注文」
→ UL 登録済み：「確定済み注文」に置き換えますか？

Before: ...支払いが承認されて在庫を確保できる状態になった注文は...
After:  ...確定済み注文は...

承認しますか？ (yes/no)
```

**Pass criteria**:
- Both paraphrases are detected
- Diff is shown for each substitution proposal
- No substitution is made without explicit user confirmation (FR-023)
- Meaning equivalence must be confirmed by user

---

## Scenario 3: Linkability — Ambiguous BC Term Qualification (FR-024)

**Setup**: context-map.md records 「顧客」 in both 販売 BC and 請求 BC

**Input**: Generated spec uses 「顧客」 without BC qualifier

**Expected behavior**:
1. Skill detects ambiguous UL term usage
2. Adds BC qualifier to each occurrence:
   - 「顧客（販売BC）」 or 「顧客（請求BC）」

**Pass criteria**:
- Ambiguous term is qualified with BC name
- Diff is shown before modification; confirmation required

---

## Scenario 4: Delta Notation for UL Updates

**Input** (user approves adding a new term and updating an existing one):

**Expected output format**:

```
[+] 返品リクエスト: 確定済み注文に対して顧客が申請する返品依頼 (BC: 販売)
[~] キャンセル可能注文: 定義に「返品申請受付可能」条件を追加 (BC: 販売)
```

**Pass criteria**:
- New additions use `[+]` prefix
- Updates use `[~]` prefix
- Deletions use `[-]` prefix
- No full UL table re-display; only changed rows shown

---

## Invariant Checks

- [ ] Ontology Header appears at session/lifecycle event start when ≥ 5 UL terms exist
- [ ] Paraphrase substitution requires explicit confirmation
- [ ] Ambiguous cross-BC terms are qualified with BC name
- [ ] UL updates use Delta Notation (not full re-display)
