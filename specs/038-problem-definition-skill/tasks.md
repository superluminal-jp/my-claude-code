# Tasks: 「理想と現実のギャップ」として問題を定義する `problem-definition` スキルの追加

**入力**: `specs/038-problem-definition-skill/` の設計文書
**前提**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**構成**: タスクはユーザーストーリー単位でグループ化され、各ストーリーは独立して検証できる。

**テストタスクの位置づけ**: spec.md は TDD を明示的に要求していないが、FR-020/FR-021 が `tests/run-config-pyramid.sh`（`037`で確立済みの構造契約テスト）への追加そのものを機能要件として定めている。そのためテスト関連タスク（T021〜T024）は独立した「テストフェーズ」としてではなく、FR を満たす通常の実装タスクとして Phase 5 に含める。検証は主に [quickstart.md](./quickstart.md) の手動手順による。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（別ファイル・未完了タスクへの依存なし）
- **[Story]**: US1 / US2（Setup / Foundational / Phase 5 / Polish には付かない）

## Path Conventions

リポジトリルートは `/Users/taikiogihara/work/my-claude-code`。以下のパスはすべてルート相対。

---

## Phase 1: Setup

- [X] T001 `.claude/skills/problem-definition/SKILL.md` を作成する — フロントマター（`name: problem-definition`）のプレースホルダのみ、本文は空

---

## Phase 2: Foundational (Blocking Prerequisites)

**目的**: 両ユーザーストーリーが依存する、スキルの骨格——トリガー境界、引用基盤、出力契約、共通の安全策——を先に固める。ここが終わるまで US1/US2 の引き出しフローは書けない。

- [X] T002 フロントマター（`description`）を確定する — トリガー語句（問題/problem）と、除外境界を1文に含める。兄弟スキル名は一切埋め込まず、`product-strategy` を含むいかなる他スキルの内容にも触れない（research.md D2の言語設計に従う）。ビジネス/技術/個人/組織のいずれかに限定する語彙を使わず、ドメイン不問であることが伝わる記述にする（[contracts/problem-interface.md](./contracts/problem-interface.md) 契約A、FR-002、FR-004、FR-006、FR-016、SKILL-02/03） — `.claude/skills/problem-definition/SKILL.md`
- [X] T003 参考文献セクション（4件の一次資料: Ishikawa、Kepner-Tregoe、BABOK、Shook/A3、[spec.md](./spec.md#参考文献) を要約引用）を本文に書く（FR-003、data-model.md V4） — `.claude/skills/problem-definition/SKILL.md`
- [X] T004 完成した問題文の出力書式（ステータスマーカー、4要素見出し）を本文の「出力の型」節として定義し、あわせて「自らが作成したファイル以外には一切書き込まない」という制約を明文で本文に記載する（[contracts/problem-interface.md](./contracts/problem-interface.md) 契約B、data-model.md 問題文エンティティ、FR-007、FR-015） — `.claude/skills/problem-definition/SKILL.md`
- [X] T005 引き出し中断時のドラフト保存手順（未回答要素一覧の書式を含む）を本文に定義する（FR-009a、契約B、data-model.md V9） — `.claude/skills/problem-definition/SKILL.md`
- [X] T006 既存問題文検出時の上書き/新バージョン確認ダイアログの手順を本文に定義する（FR-015a、契約B、data-model.md 版数の状態遷移） — `.claude/skills/problem-definition/SKILL.md`
- [X] T007 未解決の論点を「論点/デフォルト/代替案/影響」の3項目で記録する手順と、事実捏造の禁止（FR-009）を本文に定義する。この記録形式は [contracts/problem-interface.md](./contracts/problem-interface.md) の「対立するあるべき姿の記録」（FR-012）が参照する — `.claude/skills/problem-definition/SKILL.md`

**チェックポイント**: T002〜T007 が揃った時点で、共通基盤が完成している。Phase 3/4 はこの上に各ストーリー固有の分岐を積む。

---

## Phase 3: User Story 1 - 曖昧な「問題がある」感覚を検証可能な問題文にする (Priority: P1) 🎯 MVP

**目的**: 現状・あるべき姿・ギャップ・重要性の4要素を、対応するフレームワークに基づいて引き出し、単一の問題文を生成できるようにする。

**独立した検証**: [quickstart.md](./quickstart.md) シナリオ2。Phase 4 を実装しなくても、この Phase だけで核心価値が完結する。

### Implementation for User Story 1

- [X] T008 [US1] 現状の引き出し手順（BABOK/A3に基づき、事実・データに根ざした記述を促す）を本文に定義する。例示や質問文言は特定ドメイン（ビジネス/技術/個人/組織）に偏らせない（research.md D3、FR-004、FR-007、FR-008） — `.claude/skills/problem-definition/SKILL.md`
- [X] T009 [US1] あるべき姿の引き出し手順（Ishikawa/QC・BABOK・A3に基づき、期待値・標準を明確化させる）を本文に定義する（research.md D3、FR-007、FR-008） — `.claude/skills/problem-definition/SKILL.md`
- [X] T010 [US1] ギャップ（問題文の核）の定式化手順（Kepner-Tregoe/A3に基づき、現状とあるべき姿の対比として問題文を組み立てる）を本文に定義する（research.md D3、FR-007） — `.claude/skills/problem-definition/SKILL.md`
- [X] T011 [US1] 重要性の引き出し手順（Kepner-Tregoeの「対応を要するほど重大か」という判定基準に基づく）を本文に定義する（research.md D3、FR-007） — `.claude/skills/problem-definition/SKILL.md`
- [X] T012 [US1] 定量データが利用できない場合に質的な記述へ切り替え、データの欠如を前提として明示する手順（精度を理由に引き出しをブロックしない）を本文に定義する（FR-008） — `.claude/skills/problem-definition/SKILL.md`
- [X] T013 [US1] 現状とあるべき姿の間に実質的なギャップが無いと判明した場合、問題をでっち上げず率直に伝える手順を本文に定義する（FR-014、data-model.md V11） — `.claude/skills/problem-definition/SKILL.md`

**チェックポイント**: quickstart.md シナリオ2が、中断時のドラフト保存確認（T005 依存）も含めて通ること。

---

## Phase 4: User Story 2 - 問題定義に解決策や思い込みの原因が紛れ込むのを防ぐ (Priority: P1)

**目的**: 解決策・未検証の原因・対立するあるべき姿・束ねられた複数のギャップを識別し、問題文の核から切り分ける。

**独立した検証**: [quickstart.md](./quickstart.md) シナリオ3・4。Phase 3 と論理的に独立（同じ4要素の基盤の上に、混入検知という別の分岐を積むだけ）だが、同一ファイルを編集するため実行順序としては直列に扱う。

### Implementation for User Story 2

- [X] T014 [US2] 解決策の混入を検知し、問題文の核から切り分けて別記する手順（その解決策が解消しようとしているギャップを別途引き出す）を本文に定義する（FR-010、契約B「識別された解決策」、data-model.md V13） — `.claude/skills/problem-definition/SKILL.md`
- [X] T015 [US2] 未検証の原因の混入を検知し、原因分析を行うのではなくギャップの記述そのものへ引き出しを戻す手順を本文に定義する（原因分析は本スキルが担わない別の関心事であることを明記する）（FR-011、契約B「識別された未検証の原因」、data-model.md V13） — `.claude/skills/problem-definition/SKILL.md`
- [X] T016 [US2] あるべき姿について関係者間で見解が対立する場合、一方を無断で採用せず両論を併記し、どちらを基準とするかをユーザーに確認する手順（T007の論点記録形式を用いる）を本文に定義する（FR-012、契約B「あるべき姿に関する見解の対立」） — `.claude/skills/problem-definition/SKILL.md`
- [X] T017 [US2] 複数の異なるギャップが1つの訴えに束ねられている場合、単一の問題文に統合せず分解して別々の問題文候補として提示する手順を本文に定義する（FR-013、data-model.md V12） — `.claude/skills/problem-definition/SKILL.md`
- [X] T018 [US2] 原因分析・対応策の検討・実行計画の策定を行わないという非対象事項を本文に明記する（FR-005） — `.claude/skills/problem-definition/SKILL.md`

**チェックポイント**: quickstart.md シナリオ3・4が通ること。

---

## Phase 5: 配布・ドキュメント・回帰契約（横断的関心事）

**目的**: 新スキルを、既存のガバナンス機構（README 一覧・`run-config-pyramid.sh` 構造契約）へ実際に接続する。US1/US2 のどちらの利用体験にも影響しないが、FR-018〜FR-021 を満たすために必須であり、T002 で確定した `description` の最終文言に依存する。

- [X] T019 [P] `README.md` のスキル一覧散文とスキルツリーに `problem-definition` を1行サマリ付きで追加する（FR-019） — `README.md`
- [X] T020 [P] `README.ja.md` の対応箇所に日本語で同内容を追加する（FR-019） — `README.ja.md`
- [X] T021 `tests/run-config-pyramid.sh` の `authored_skills` 配列に `problem-definition` を追加する（FR-020） — `tests/run-config-pyramid.sh`
- [X] T022 同ファイルの `run_rule_contract()` RULE-03 正規表現リストと `run_skill_contract()` SKILL-06 正規表現リストに `problem-definition` を追加する（FR-016、FR-017、FR-020、data-model.md V3/V6） — `tests/run-config-pyramid.sh`
- [X] T023 同ファイルの `run_routing_fixtures()` に、`problem-definition` の `description` がトリガー語と除外境界語を含むことを検証する新規アサーションを追加する（FR-002、FR-020） — `tests/run-config-pyramid.sh`
- [X] T024 `bash tests/run-config-pyramid.sh` を実行し、既存アサーション（`037`の `ROUTE-09` を含む）を含む全件が PASS することを確認する（FR-021、SC-002、quickstart.md シナリオ1） — 検証のみ、ファイル変更なし

**チェックポイント**: quickstart.md シナリオ1（`bash tests/run-config-pyramid.sh`）が0件の失敗で終わること。

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T025 `install.sh` を実行し、`~/.claude/skills/problem-definition/SKILL.md` が配置されること、再実行しても重複・リンク切れが無いことを確認する（SC-005）——**注意**: `037`実装時に判明したとおり、`install.sh` の `sync_path()` は `~/.claude/settings.json` を上書きし、live な個人設定を消しうる。実行前にユーザーへ確認すること（`037`の T022 と同じ判断が必要）
- [ ] T026 quickstart.md シナリオ2〜5を新規セッションで手動実行し、SC-001（表現の異なる日英計4プロンプト）・SC-004（解決策/未検証原因の分離）・SC-006（1分以内の発見しやすさ）を確認する——**部分的に検証済み**: 独立したフレッシュサブエージェント3件（日本語の曖昧な訴え、英語の曖昧な訴え、日本語の解決策混入）で実施し、いずれも `problem-definition` が正しくロードされ、現状/あるべき姿/重要性を事実捏造なく引き出し、混入した解決策を問題文から分離することを確認した。SC-001 が求める「表現の異なる4プロンプト」には1件（日英いずれかの追加プロンプト）不足しており、SC-006（1分以内の発見しやすさ）は未検証のまま
- [ ] T027 生成された完成問題文のサンプルが、data-model.md の V8〜V13・契約Bの書式をすべて満たすことを目視確認する（SC-003）。あわせて、実行前後で対象の文脈内の他のファイルが一切変更されていないことを確認する（FR-015）——**未実施**: T026 の検証はいずれも単発ターンの引き出し段階で終わっており（正しい挙動——4要素が揃う前に完成させていない）、完成ステータスの問題文ファイルはまだ生成されていない。複数ターンの対話が必要なため、フレッシュエージェント1回では検証できなかった

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational — 骨格) ← ブロッキング。ここを飛ばすと US1/US2 が積む土台がない
   ↓
Phase 3 (US1 — 問題文の生成) 🎯 MVP
   ↓ （同一ファイルのため直列だが、論理的には US1 に依存しない）
Phase 4 (US2 — 混入の切り分け)
   ↓
Phase 5 (配布・ドキュメント・回帰契約) ← T002 の description 最終文言に依存
   ↓
Phase 6 (Polish)
```

### User Story Dependencies

- **US1** は Foundational にのみ依存。単独で価値を出す（MVP）。
- **US2** は Foundational にのみ論理的に依存する（US1 と機能的に独立）が、同一ファイル（`SKILL.md`）を編集するため実装順序としては US1 の後に置く。

### Parallel Opportunities

- **Phase 5**: T019（`README.md`）と T020（`README.ja.md`）は別ファイル → 並列可。
- **Phase 5**: T021〜T023 は同一ファイル（`tests/run-config-pyramid.sh`）の異なる関数を編集するが、同一ファイルであるため直列に扱う。

## Parallel Example: Phase 5

```text
# 2 つの README を同時に更新する（互いに依存なし）:
T019 README.md
T020 README.ja.md
```

## Implementation Strategy

### MVP (Phase 1 → 3)

Phase 3（US1）まで完了すれば、**曖昧な訴えを検証可能な問題文に変換するという中核価値**が成立する。混入の切り分け（US2）や配布・ドキュメント整備（Phase 5）が無くても、このスキルを手元の `.claude/skills/` に置くだけで単独で使える。

### Incremental Delivery

1. Phase 1–3 → 問題文の生成が動く（spec.md ユーザーストーリー1）
2. + Phase 4 → 解決策/原因の混入切り分けが動く（ユーザーストーリー2）
3. + Phase 5 → README・構造契約テストに正式に組み込まれ、リポジトリ全体のガバナンスと整合する（FR-018〜FR-021）
4. + Phase 6 → 配布・実ルーティング・出力書式の最終確認（SC-001〜SC-006）

## Notes

- **Phase 2 を飛ばして Phase 3/4 に進むと、出力書式（契約B）や安全策（FR-009a/015a）が場当たり的になり、後から作り直すことになる**。Phase 2 は短いが、全ストーリーの土台であることに変わりはない。
- **T002 の `description` 文言が確定するまで Phase 5 の T023 は書けない** — 静的契約テストは実際の文言に対する正規表現マッチだからである（research.md D1、`037`の research.md D2）。
- **コミットは明示依頼時のみ**（このリポジトリの通常運用）。本タスク群にコミット操作は含まれない。
