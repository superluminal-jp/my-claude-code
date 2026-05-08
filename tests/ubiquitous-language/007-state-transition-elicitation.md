# Test Scenario: State-Transition Elicitation

**Feature**: 003-ubiquitous-language
**Covers**: FR-009
**User Story**: US1

---

## Setup

- `.specify/ubiquitous-language/` exists with at least one BC file
- A stateful term has been identified in the conversation

---

## Scenario: State-Transition Prompt and Arrow Notation Recording

**Input to Claude**:

```
UL に「注文」を追加したい。注文は受け付けられた後、支払いが承認されると確定され、
その後倉庫で在庫が引き当てられ、出荷指示が出される。支払いが拒否されるとキャンセルされる。
```

**Expected behavior**:
1. Skill identifies "注文" as a stateful term
2. Prompts the user to confirm normal-flow and exception-flow state transitions
3. Records in 状態/ルール using arrow notation

**Expected state/rules field content**:

```
受付済み → 確定済み → 在庫引当済み → 出荷指示済み (例外: 支払い拒否 → キャンセル済み)
```

**Pass criteria**:
- Skill explicitly asks about state transitions for "注文"
- Response uses arrow notation (→) for normal flow
- Exception flows are on the same line, clearly labeled
- No multi-line prose in the 状態/ルール field

---

## Invariant Checks

- [ ] Skill prompts for both normal flow and exception flow
- [ ] Arrow notation is used (not prose)
- [ ] 状態/ルール fits a single line in the table
- [ ] Diff is shown before writing; confirmation required
