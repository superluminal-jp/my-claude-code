# Feature Specification: Clarify Skill Pre-Trigger on Speckit Specify

**Feature Branch**: `008-clarify-pretrigger-specify`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "clarify skill を speckit specify 実行時に pre-trigger"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clarify Skill Runs Before Spec Generation (Priority: P1)

`/speckit-specify` を実行すると、仕様を書き始める前に clarify skill が自動的に起動し、ユーザーの意図・スコープ・受け入れ基準を引き出す質問を行う。

**Why this priority**: spec の品質は最初の要件収集フェーズに依存する。曖昧なまま仕様を生成すると後工程で手戻りが発生するため、specify の冒頭で clarify を走らせることが最も価値が高い。

**Independent Test**: `/speckit-specify` を任意の機能説明で実行したとき、spec.md が生成される前に clarify の質問ターンが挟まれることを確認する。clarify の回答を経て生成された spec.md が、回答内容を反映していることを確認する。

**Acceptance Scenarios**:

1. **Given** ユーザーが `/speckit-specify <feature description>` を実行する, **When** pre-trigger が発火する, **Then** clarify skill が起動し、intent / scope / acceptance criteria / constraints に関する質問を最大5問提示する
2. **Given** clarify の質問に対してユーザーが回答を入力した, **When** すべての質問への回答が揃う, **Then** clarify の出力（明確化済み要件）を入力として spec.md が生成される
3. **Given** clarify の質問に対してユーザーがスキップ（空回答 or キャンセル）を選択した, **When** スキップが検出される, **Then** clarify をスキップして元の機能説明のまま spec.md を生成する

---

### User Story 2 - Clarify Hook の有効・無効切り替え (Priority: P2)

プロジェクトの `.specify/extensions.yml` に `before_specify` フックとして clarify を登録・解除することで、プロジェクトごとにこの動作を制御できる。

**Why this priority**: 全プロジェクトで強制するのではなく、既存の specify ワークフローを壊さずにオプトインできる設計が重要。

**Independent Test**: `extensions.yml` の `before_specify` に clarify フックを追加した状態と削除した状態で `/speckit-specify` を実行し、フックの有無で挙動が変わることを確認する。

**Acceptance Scenarios**:

1. **Given** `extensions.yml` の `before_specify` に clarify フックが `enabled: true` で登録されている, **When** `/speckit-specify` が実行される, **Then** clarify skill が pre-trigger として起動する
2. **Given** `extensions.yml` の `before_specify` に clarify フックが `enabled: false` で登録されている, **When** `/speckit-specify` が実行される, **Then** clarify skill はスキップされ、通常の specify フローが走る
3. **Given** `extensions.yml` の `before_specify` に clarify フックが存在しない, **When** `/speckit-specify` が実行される, **Then** 既存のフック（ubiquitous-language, speckit.git.feature）だけが実行される

---

### Edge Cases

- clarify skill の質問に対して途中でユーザーがセッションを終了した場合、仕様は生成されない（中途半端な spec.md を残さない）
- clarify が返す質問数が0のとき（曖昧点なし）は質問ターンをスキップして即座に specify へ進む
- 既存の `before_specify` フック（ubiquitous-language, speckit.git.feature）との実行順序は extensions.yml のリスト順に従う

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/speckit-specify` の `before_specify` フックとして clarify skill を呼び出せること
- **FR-002**: clarify skill の実行後、その出力（明確化済み要件テキスト）が specify の入力として渡されること
- **FR-003**: clarify がゼロ質問を返したとき（要件が十分明確）は質問ターンを挿入せず specify を続行すること
- **FR-004**: ユーザーがスキップを選択したとき、元の機能説明をそのまま specify に渡すこと
- **FR-005**: フックの有効・無効は `extensions.yml` の `enabled` フラグで制御できること
- **FR-006**: clarify フックは `optional: true` / `optional: false` どちらでも設定可能であること

### Key Entities

- **before_specify hook entry**: `extensions.yml` 内のフック定義。`command: clarifier`、`enabled`、`optional`、`condition` を持つ
- **Clarified Input**: clarify skill が生成する明確化済み要件テキスト。specify の feature description として使われる

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `/speckit-specify` 実行時に clarify フックが登録されていれば、spec.md 生成前に必ず質問ターンが挿入される（100% のケースで発火）
- **SC-002**: clarify の回答内容が spec.md の対応セクションに反映されている（生成後に手動で [NEEDS CLARIFICATION] マーカーが残らない割合が向上）
- **SC-003**: clarify のスキップ操作で仕様生成が中断されない（ユーザーがスキップしても specify は完了する）
- **SC-004**: 既存の `before_specify` フック（ubiquitous-language, speckit.git.feature）の動作が変わらない

## Assumptions

- clarify skill はすでに `.claude/skills/clarifier` として実装・動作しており、本機能はそれを呼び出す統合作業である
- `extensions.yml` の `before_specify` リストへエントリを追加するだけで統合できる（speckit-specify の playbook は既にフック処理を実装済み）
- clarify skill の「スキップ」はユーザーが空回答またはキャンセルに相当する操作を行うことで表現される
- 本機能の初期スコープは optional フックとしての登録であり、全プロジェクト強制（mandatory）にするかどうかは別途判断する
