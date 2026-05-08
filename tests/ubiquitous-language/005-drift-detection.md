# Test Scenario: Implementation-Name Drift Detection

**Feature**: 003-ubiquitous-language
**Covers**: FR-016, FR-017, FR-018
**User Story**: US2

---

## Setup

- `.specify/ubiquitous-language/sales.md` contains:
  ```
  | 確定済み注文 | ... | 販売 | ... | ... | ... | `ConfirmedOrder`, `Order.confirm()`, `OrderConfirmed` (event) | ... | ... |
  ```

---

## Scenario 1: Drift Detection — Semantic Divergence

**Input to Claude** (user submits plan.md for review):

```
## 3. 実装方針

受注サービス（OrderService）は `Order.process()` メソッドで注文処理を行い、
完了後に `OrderProcessed` イベントを発行する。
```

**Expected behavior**:
1. Skill scans plan.md identifiers
2. Normalizes: `Order.process()` → `orderprocess`; UL `Order.confirm()` → `orderconfirm`
3. Detects semantic divergence (different verbs: process vs. confirm)
4. Generates Drift Report

**Expected Drift Report**:

```
## UL ドリフト検知

| 場所 | 記述 | UL の期待値 | 推奨アクション |
|------|------|-----------|--------------|
| plan.md §3 | Order.process() | Order.confirm() | A) artifact 修正 / B) UL 更新 / C) 新語として分離 |
| plan.md §3 | OrderProcessed | OrderConfirmed (event) | A) artifact 修正 / B) UL 更新 / C) 新語として分離 |
```

**Pass criteria**:
- Both drifted identifiers are detected
- Report shows exact artifact location
- All 3 resolution options are presented for each item

---

## Scenario 2: No False Positive on Casing

**Input to Claude** (plan.md with casing difference only):

```
`order.confirm()` を呼び出す
```

**Expected behavior**:
1. Normalizes: `order.confirm()` → `orderconfirm`; UL `Order.confirm()` → `orderconfirm`
2. Normalized forms match — **no drift detected**

**Pass criteria**:
- No drift warning for casing-only difference
- Response proceeds normally

---

## Scenario 3: Resolution — Artifact Modification (Option A)

**Input** (user selects option A for Order.process()):

```
A を選択します。plan.md を修正してください。
```

**Expected behavior**:
1. Skill shows diff: `Order.process()` → `Order.confirm()`
2. Waits for explicit confirmation before modifying plan.md
3. After confirmation, updates plan.md

**Pass criteria**:
- Diff is shown (no silent rewrite — FR-018)
- plan.md is NOT modified until user confirms
- After modification, drift report for this item is resolved

---

## Invariant Checks

- [ ] Case/separator differences do NOT trigger drift warnings
- [ ] Semantic differences DO trigger drift warnings
- [ ] All 3 resolution options are presented
- [ ] No artifact or UL file is modified without showing diff and receiving confirmation
