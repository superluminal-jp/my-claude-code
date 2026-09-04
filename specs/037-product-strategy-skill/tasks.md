# Tasks: 開発着手前の戦略整理を支援する `product-strategy` スキルの追加

**入力**: `specs/037-product-strategy-skill/` の設計文書
**前提**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**構成**: タスクはユーザーストーリー単位でグループ化され、各ストーリーは独立して検証できる。

**テストタスクの位置づけ**: spec.md は TDD を明示的に要求していないが、FR-015/FR-016 が `tests/run-config-pyramid.sh`（現行の構造契約テスト、research.md D2）への追加そのものを機能要件として定めている。そのためテスト関連タスク（T018〜T021）は独立した「テストフェーズ」としてではなく、FR を満たす通常の実装タスクとして Phase 5 に含める。検証は主に [quickstart.md](./quickstart.md) の手動手順による。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（別ファイル・未完了タスクへの依存なし）
- **[Story]**: US1 / US2（Setup / Foundational / Phase 5 / Polish には付かない）

## Path Conventions

リポジトリルートは `/Users/taikiogihara/work/my-claude-code`。以下のパスはすべてルート相対。

---

## Phase 1: Setup

- [X] T001 `.claude/skills/product-strategy/SKILL.md` を作成する — フロントマター（`name: product-strategy`）のプレースホルダのみ、本文は空

---

## Phase 2: Foundational (Blocking Prerequisites)

**目的**: 両ユーザーストーリーが依存する、スキルの骨格——トリガー境界、引用基盤、出力契約、共通の安全策——を先に固める。ここが終わるまで US1/US2 の引き出しフローは書けない。

- [X] T002 フロントマター（`description`）を確定する — トリガー語句（戦略/strategy、開発着手前）と、`clarifier`/`scrum-master`/`minto-builder` との除外境界を1文に含める（[contracts/skill-interface.md](./contracts/skill-interface.md) 契約A、FR-002、FR-005、SKILL-02/03） — `.claude/skills/product-strategy/SKILL.md`
- [X] T003 参考文献セクション（10件の一次資料、[spec.md](./spec.md#参考文献) を要約引用）を本文に書く（FR-003、FR-003a〜FR-003g、data-model.md V4） — `.claude/skills/product-strategy/SKILL.md`
- [X] T004 完成ブリーフの出力書式（ステータスマーカー、6セクション見出し）を本文の「出力の型」節として定義し、あわせて「自らが作成したファイル以外には一切書き込まない」という制約を明文で本文に記載する（[contracts/skill-interface.md](./contracts/skill-interface.md) 契約B、data-model.md 戦略ブリーフエンティティ、FR-006、**FR-011**） — `.claude/skills/product-strategy/SKILL.md`
- [X] T005 引き出し中断時のドラフト保存手順（未回答セクション一覧の書式を含む）を本文に定義する（FR-007a、契約B、data-model.md V8） — `.claude/skills/product-strategy/SKILL.md`
- [X] T006 既存ブリーフ検出時の上書き/新バージョン確認ダイアログの手順を本文に定義する（FR-011a、契約B、data-model.md 版数の状態遷移） — `.claude/skills/product-strategy/SKILL.md`
- [X] T007 未解決の重要な論点を「デフォルト/代替案/影響」の3項目で記録する手順（`clarifier` テンプレート流用）と、事実捏造の禁止（FR-007）を本文に定義する — `.claude/skills/product-strategy/SKILL.md`

**チェックポイント**: T002〜T007 が揃った時点で、フレームワークに基づく引き出し・安全な出力という共通基盤が完成している。Phase 3/4 はこの上に各ストーリー固有の分岐を積む。

---

## Phase 3: User Story 1 - 新規プロダクトにおける戦略整理 (Priority: P1) 🎯 MVP

**目的**: グリーンフィールドのプロジェクトで、インタビューのみによる引き出しから完成した戦略ブリーフを生成できるようにする。

**独立した検証**: [quickstart.md](./quickstart.md) シナリオ2。Phase 4 を実装しなくても、この Phase だけで新規プロジェクト向けの価値が完結する。

### Implementation for User Story 1

- [X] T008 [US1] 既存文脈が存在しない場合の判定条件（README/CLAUDE.md/過去の specs/過去のブリーフのいずれも無い）と、インタビューのみの引き出しへのフォールバック手順を本文に定義する（FR-010 新規側、data-model.md V11） — `.claude/skills/product-strategy/SKILL.md`
- [X] T009 [US1] 6セクション（ビジョン/課題、ターゲットユーザー、提供価値、成功指標、スコープと優先順位、制約）それぞれの引き出し質問を、対応するフレームワーク（FR-003a〜FR-003g）に基づいて本文に記述する — `.claude/skills/product-strategy/SKILL.md`
- [X] T010 [US1] スコープ境界（アーキテクチャ/技術スタック/内製購入の決定をしない、FR-004）を本文の非対象事項として明記する — `.claude/skills/product-strategy/SKILL.md`

**チェックポイント**: quickstart.md シナリオ2が、中断時のドラフト保存確認（T005 依存）も含めて通ること。

---

## Phase 4: User Story 2 - 既存プロダクトにおける戦略整理 (Priority: P1)

**目的**: 既存のプロダクト文脈を尊重し、聞き直しと矛盾のサイレントな統合を避けながら戦略を整理できるようにする。

**独立した検証**: [quickstart.md](./quickstart.md) シナリオ3。Phase 3 と論理的に独立（同じ FR-006 の6セクション基盤の上に、既存文脈の発見という別の分岐を積むだけ）だが、同一ファイルを編集するため実行順序としては直列に扱う。

### Implementation for User Story 2

- [X] T011 [US2] 既存文脈の発見手順（README → CLAUDE.md → 過去の戦略ブリーフ → 過去の `specs/` の順に読み込む）を本文に定義する（FR-008） — `.claude/skills/product-strategy/SKILL.md`
- [X] T012 [US2] 発見済みの事実を再度尋ねないための差分質問ロジック（読み込んだ内容と6セクションの対応づけ）を本文に定義する（FR-008、data-model.md 既存プロダクトの文脈エンティティ） — `.claude/skills/product-strategy/SKILL.md`
- [X] T013 [US2] 新しい戦略が既存文脈と矛盾/縮小する場合の明示手順（契約Bの「既存の戦略との関係」セクションの生成）を本文に定義する（FR-009） — `.claude/skills/product-strategy/SKILL.md`
- [X] T014 [US2] 未文書化の既存プロジェクト（文脈ソースは物理的に存在するが記載なし）へのフォールバック手順を本文に定義する（FR-010 既存側、data-model.md V11） — `.claude/skills/product-strategy/SKILL.md`
- [X] T015 [US2] 複数の矛盾する過去の戦略成果物が見つかった場合、最新のものを提示し優先順位をユーザーに確認する手順を本文に定義する（FR-009a、data-model.md V12） — `.claude/skills/product-strategy/SKILL.md`

**チェックポイント**: quickstart.md シナリオ3が通ること。既存文脈の聞き直しがゼロであることを SC-003 のサンプルプロジェクトで確認する。

---

## Phase 5: 配布・ドキュメント・回帰契約（横断的関心事）

**目的**: 新スキルを、既存のガバナンス機構（README 一覧・`run-config-pyramid.sh` 構造契約）へ実際に接続する。US1/US2 のどちらの利用体験にも影響しないが、FR-012〜FR-018 を満たすために必須であり、T002 で確定した `description` の最終文言に依存する。

- [X] T016 [P] `README.md` のスキル一覧散文とスキルツリーに `product-strategy` を1行サマリ付きで追加する（FR-013） — `README.md`
- [X] T017 [P] `README.ja.md` の対応箇所に日本語で同内容を追加する（FR-013） — `README.ja.md`
- [X] T018 `tests/run-config-pyramid.sh` の `authored_skills` 配列に `product-strategy` を追加する（FR-015、research.md D2） — `tests/run-config-pyramid.sh`
- [X] T019 同ファイルの `run_rule_contract()` RULE-03 正規表現リストと `run_skill_contract()` SKILL-06 正規表現リストに `product-strategy` を追加する（FR-017、FR-018、data-model.md V3/V6、契約A） — `tests/run-config-pyramid.sh`
- [X] T020 同ファイルの `run_routing_fixtures()` に、`product-strategy` の `description` がトリガー語と除外境界語を含むことを検証する `ROUTE-09` アサーションを追加する（FR-005、契約A） — `tests/run-config-pyramid.sh`
- [X] T021 `bash tests/run-config-pyramid.sh` を実行し、既存アサーションを含む全件が PASS することを確認する（FR-016、SC-002、quickstart.md シナリオ1） — 検証のみ、ファイル変更なし

**チェックポイント**: quickstart.md シナリオ1（`bash tests/run-config-pyramid.sh`）が0件の失敗で終わること。

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T022 `install.sh` を実行し、`~/.claude/skills/product-strategy/SKILL.md` が配置されること、再実行しても重複・リンク切れが無いことを確認する（SC-005、research.md D5）——**実装中に判明・ユーザー判断で保留**: `install.sh` の `sync_path()` は `~/.claude/settings.json` を `rm -rf` してから本リポジトリの追跡版で上書きする。現在のセッションが使っている live な `~/.claude/settings.json`（`defaultMode`/`effortLevel`/`tui`/`autoApproveEdits` 等の個人設定を含む）を無警告で消しうるため、実行はユーザー自身のタイミングに委ねることとした。settings.json を除外して同期する、またはバックアップを取ってから実行する、という代替手段も提示済み
- [ ] T023 quickstart.md シナリオ2〜4を新規セッションで手動実行し、SC-001（表現の異なる日英計4プロンプト）・SC-003（既存文脈の聞き直しゼロ）・SC-006（1分以内の発見しやすさ）を確認する——T022 未実施のためユーザースコープでの検証は未実施。本リポジトリ内での発見可能性（`.claude/skills/product-strategy/SKILL.md` の存在と自動列挙）は確認済み
- [ ] T024 生成された完成ブリーフのサンプルが、data-model.md の V7〜V10・契約Bの書式をすべて満たすことを目視確認する（SC-004）。あわせて、実行前後で対象プロジェクト内の他のファイル（`README.md` 等）が一切変更されていないことを確認する（FR-011）——実際のブリーフ生成はユーザーによるスキル利用が必要なため未実施

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational — 骨格) ← ブロッキング。ここを飛ばすと US1/US2 が積む土台がない
   ↓
Phase 3 (US1 — 新規プロジェクト) 🎯 MVP
   ↓ （同一ファイルのため直列だが、論理的には US1 に依存しない）
Phase 4 (US2 — 既存プロジェクト)
   ↓
Phase 5 (配布・ドキュメント・回帰契約) ← T002 の description 最終文言に依存
   ↓
Phase 6 (Polish)
```

### User Story Dependencies

- **US1** は Foundational にのみ依存。単独で価値を出す（MVP）。
- **US2** は Foundational にのみ論理的に依存する（US1 と機能的に独立）が、同一ファイル（`SKILL.md`）を編集するため実装順序としては US1 の後に置く。

### Parallel Opportunities

- **Phase 5**: T016（`README.md`）と T017（`README.ja.md`）は別ファイル → 並列可。
- **Phase 5**: T018〜T020 は同一ファイル（`tests/run-config-pyramid.sh`）の異なる関数を編集するが、同一ファイルであるため直列に扱う。

## Parallel Example: Phase 5

```text
# 2 つの README を同時に更新する（互いに依存なし）:
T016 README.md
T017 README.ja.md
```

## Implementation Strategy

### MVP (Phase 1 → 3)

Phase 3（US1）まで完了すれば、**新規プロジェクトにおける戦略整理という中核価値**が成立する。既存プロジェクト対応（US2）や配布・ドキュメント整備（Phase 5）が無くても、このスキルを手元の `.claude/skills/` に置くだけで単独で使える。

### Incremental Delivery

1. Phase 1–3 → 新規プロジェクトの戦略整理が動く（spec.md ユーザーストーリー1）
2. + Phase 4 → 既存プロジェクトの戦略整理が動く（ユーザーストーリー2）
3. + Phase 5 → README・構造契約テストに正式に組み込まれ、リポジトリ全体のガバナンスと整合する（FR-012〜FR-016）
4. + Phase 6 → 配布・実ルーティング・出力書式の最終確認（SC-001/003/004/005/006）

## Notes

- **Phase 2 を飛ばして Phase 3/4 に進むと、出力書式（契約B）や安全策（FR-007/007a/011a）が場当たり的になり、後から作り直すことになる**。Phase 2 は短いが、全ストーリーの土台であることに変わりはない。
- **T002 の `description` 文言が確定するまで Phase 5 の T020（ROUTE-09）は書けない** — 静的契約テストは実際の文言に対する正規表現マッチだからである（research.md D2）。
- **コミットは明示依頼時のみ**（このリポジトリの通常運用）。本タスク群にコミット操作は含まれない。
