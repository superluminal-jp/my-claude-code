# Test Scenario: Bootstrap — New Project UL Initialization

**Feature**: 003-ubiquitous-language
**Covers**: FR-001, FR-004, FR-005, FR-007, FR-008, FR-009, FR-019, SC-001, SC-007
**User Story**: US1

---

## Setup

- No `.specify/ubiquitous-language/` directory exists
- `.specify/` exists (spec-kit initialized)

---

## Scenario 1: UL-Absence Detection Triggers Elicitation

**Input to Claude**:

```
/ubiquitous-language bootstrap

このシステムは EC サイトの受注管理システムです。
主な業務は、顧客から注文を受け付け、支払い確認後に倉庫へ出荷指示を送ることです。
```

**Expected behavior**:
1. Skill detects `.specify/ubiquitous-language/` is absent
2. Announces bootstrap mode to user
3. Asks the business-event opening question (not role/data first)

**Pass criteria**: Response contains a question asking for 5–10 business events in verb+noun form before any UL file is written.

---

## Scenario 2: 7-Field UL File Generation

**Input to Claude** (continuing from Scenario 1):

```
業務イベントは以下の通りです：
1. 注文が受け付けられる
2. 支払いが承認される
3. 注文が確定される
4. 在庫が引き当てられる
5. 出荷指示が送られる
```

**Expected behavior**:
1. For each event, skill elicits actors, preconditions, result states, exception cases
2. Proposes UL entries with all 7 fields populated
3. Shows diff before writing
4. Waits for explicit confirmation before writing to file

**Pass criteria**:
- Each proposed entry has: 用語, 定義, 文脈（BC）, 状態/ルール, 例, 反例, 実装名
- No entry is written without showing diff and receiving "yes"
- State-transition terms use arrow notation in 状態/ルール (e.g., `受付済み→確定済み→在庫引当済み`)
- At least 80% of terms match actual business vocabulary from the input

---

## Scenario 3: Same-Term Multi-BC Detection During Bootstrap

**Input to Claude**:

```
「顧客」について：
- 営業部門では顧客は商談相手の法人全体を指します
- 請求部門では顧客は請求書の送付先である経理担当者を指します
```

**Expected behavior**:
1. Skill detects conflicting definitions for the same term
2. Presents 3-option conflict resolution:
   - BC ごとに別エントリ化
   - BC を統合する
   - 片方を改名する
3. Does NOT silently unify definitions
4. After user selects option 1, creates separate entries in separate BC files with distinct 実装名

**Pass criteria**:
- Conflict dialog appears before writing
- User selects "BC ごとに別エントリ化"
- Two separate BC files are proposed (e.g., `sales.md`, `billing.md`)
- context-map.md entry is proposed with `same-name-different-meaning` relation type

---

## Scenario 4: Size-Budget Exceeded Proposal

**Input to Claude** (with 31 terms to add):

```
以下の 31 語を UL に追加してください：[31 term definitions]
```

**Expected behavior**:
1. After 30 entries are written, skill detects budget exceeded
2. Presents 3-option proposal: BC 分割 / 用語統合 / バジェット超過承認
3. Does NOT write the 31st entry until user selects an option

**Pass criteria**:
- 31st entry is blocked
- User sees a count display "30 / 30 (budget)"
- After selecting BC 分割, system proposes which terms to move to a new BC

---

## Invariant Checks

- [ ] No UL file was written without showing a diff first
- [ ] No UL file was written without explicit user confirmation
- [ ] All entries have 7 fields (incomplete entries marked `[NEEDS DOMAIN INPUT]`)
- [ ] 更新イベント field is auto-populated (not editable by user)
