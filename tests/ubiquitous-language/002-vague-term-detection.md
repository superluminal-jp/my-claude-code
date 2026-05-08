# Test Scenario: Vague-Term Detection

**Feature**: 003-ubiquitous-language
**Covers**: FR-010, FR-011, FR-012
**User Story**: US2

---

## Setup

- `.specify/ubiquitous-language/sales.md` exists with registered terms including `契約管理者`, `利用者`, `請求担当者`
- No `watchlist.md` exists (default watchlist is in effect)

---

## Scenario 1: Default Watchlist Detection in Artifact

**Input to Claude** (user submits a spec draft):

```
## 要件定義書

3.1 ユーザーが処理を完了すると、システムはステータスを更新し、管理画面に反映する。
3.2 データが有効な場合、フラグをオンにする。
```

**Expected behavior**:
1. Skill scans the artifact for default watchlist terms
2. Detects: ユーザー (line 3.1), 処理 (3.1), ステータス (3.1), 管理 (3.1), データ (3.2), 有効 (3.2), フラグ (3.2)
3. Presents detection table with quoted locations and UL-grounded replacement candidates

**Expected output**:

```
## 曖昧語検知

| 語 | 検出箇所 | UL 登録済み代替候補 |
|----|---------|------------------|
| ユーザー | 要件定義書 §3.1 | 契約管理者 / 利用者 / 請求担当者 |
| 処理 | 要件定義書 §3.1 | — (UL 未登録 — 業務動詞で定義を追加することを推奨) |
| ステータス | 要件定義書 §3.1 | — (UL 未登録) |
...
```

**Pass criteria**:
- All 7 detected watchlist terms appear in the table
- "ユーザー" shows 3 UL-grounded alternatives
- Each entry quotes the exact section reference

---

## Scenario 2: Block Finalization Until Resolution

**Input** (user tries to finalize the spec):

```
この要件定義書をファイルに保存してください。
```

**Expected behavior**:
1. Skill detects unresolved watchlist terms in the artifact
2. Blocks save with warning:

```
「ユーザー」が未解決のまま残っています。置換語を選ぶか、このまま進めることを明示的に承認してください。
```

**Pass criteria**:
- File is NOT written until user selects replacement or explicitly overrides
- Override requires typing explicit acknowledgement (not just "yes")

---

## Scenario 3: Project-Specific Watchlist Extension

**Setup**: `.specify/ubiquitous-language/watchlist.md` exists with:

```markdown
## Project-specific additions
取引, 顧客
```

**Input**:

```
取引が完了したら顧客に通知する。
```

**Expected behavior**:
1. Both `取引` and `顧客` are flagged (project-specific additions)
2. Default watchlist terms continue to be detected as before

**Pass criteria**:
- `取引` and `顧客` are detected even though they are not in the default list
- Default terms remain active

---

## Invariant Checks

- [ ] All 10 default watchlist terms trigger detection when present in an artifact
- [ ] Detection includes quoted source location
- [ ] UL-registered alternatives are shown when available
- [ ] Finalization is blocked until resolution or explicit override
