# Test Scenario: BC Split — Same-Term Conflict

**Feature**: 003-ubiquitous-language
**Covers**: FR-013, FR-014, FR-015, FR-028, FR-029
**User Story**: US3

---

## Setup

- `.specify/ubiquitous-language/` exists but no entry for 「顧客」 in any BC yet

---

## Scenario 1: BC-Split Selection — Three BC Definitions

**Input to Claude**:

```
「顧客」について、3 つの部門で異なる定義があります：
- 営業部門：商談中または取引実績のある法人全体
- 請求部門：請求書の送付先となる経理担当者
- サポート部門：製品を利用中のエンドユーザー
```

**Expected behavior**:
1. Skill detects conflicting definitions for the same term across 3 contexts
2. Presents conflict before writing any file
3. Shows 3-option dialog:
   - BC ごとに別エントリ化
   - BC を統合する
   - 片方を改名する

**Pass criteria**:
- Conflict dialog appears before any UL file is modified
- All 3 options are clearly presented
- No silent global unification of definitions

---

## Scenario 2: BC-Split Result — Separate Files with Distinct 実装名

**Input** (user selects option 1: BC ごとに別エントリ化):

**Expected behavior**:
1. Skill proposes 3 separate BC entries with distinct English 実装名:
   - 営業 BC → `SalesAccount`
   - 請求 BC → `BillingParty`
   - サポート BC → `SupportContact`
2. Shows diff for each proposed BC file
3. Waits for confirmation before writing

**Pass criteria**:
- Three separate files are proposed: `sales.md`, `billing.md`, `support.md`
- Each entry has a distinct `実装名` in English (FR-029)
- Each `用語` is written in Japanese (FR-028)
- Diff is shown before any write; confirmation required

---

## Scenario 3: Context-Map Update

**After** user confirms BC-split:

**Expected behavior**:
1. Skill proposes an update to `context-map.md`
2. Shows diff with the new row:

```
| 顧客 | SalesAccount | BillingParty | same-name-different-meaning | 営業は商談中法人、請求は請求先法人 |
| 顧客 | SalesAccount | SupportContact | same-name-different-meaning | 営業は法人全体、サポートはエンドユーザー |
```

3. Confirms context-map.md update with user

**Pass criteria**:
- `context-map.md` rows use `same-name-different-meaning` relation type
- Diff is shown before write; confirmation required
- All 3 BC pairs are recorded (not just 2)

---

## Invariant Checks

- [ ] Conflict dialog always precedes any write
- [ ] No definition is silently unified across BCs
- [ ] 実装名 is in English; 用語 is in domain language (Japanese)
- [ ] context-map.md is updated after BC-split with correct relation type
