# Test Scenario: Size-Budget Enforcement

**Feature**: 003-ubiquitous-language
**Covers**: FR-019
**User Story**: US1

---

## Setup

- `.specify/ubiquitous-language/sales.md` exists with exactly 30 entries
- The file header shows: `**Entry Count**: 30 / 30 (budget)`

---

## Scenario 1: Budget Exceeded — BC Split Proposal

**Input to Claude**:

```
「返品リクエスト」を販売 BC に追加してください。
返品リクエストとは、顧客が購入済み商品の返品を申請する行為です。
実装名は ReturnRequest です。
```

**Expected behavior**:
1. Skill reads `sales.md`, detects entry count = 30
2. Blocks the write
3. Presents 3-option budget proposal:
   - **BC 分割**: suggests terms that could move to a new BC (e.g., アフターセールス BC)
   - **用語統合**: lists similar terms that could be merged
   - **バジェット超過承認**: allows override with explicit acknowledgement

**Pass criteria**:
- Write is blocked (no new row appears until user responds)
- User sees current count: "30 / 30 (budget)"
- After selecting BC 分割, system proposes candidate terms to move (with explanation)
- System proposes new BC name (e.g., `after-sales`)

---

## Scenario 2: Budget Exceeded — Term Consolidation

**Input** (same setup, user selects 用語統合):

**Expected behavior**:
1. System identifies terms with overlapping definitions in `sales.md`
2. Proposes merging candidates with diff showing definition changes
3. After consolidation, count drops below 30 and new term can be added

**Pass criteria**:
- Consolidation proposal shows specific entries with overlapping definitions
- Merged entry preserves all unique information from both entries
- Diff is shown before merge; confirmation required

---

## Invariant Checks

- [ ] Entry is never written when count is at budget
- [ ] All 3 options are presented
- [ ] No option executes without user selection
- [ ] After resolution, entry count is correctly reflected in file header
