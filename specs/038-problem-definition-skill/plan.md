# 実装計画: 「理想と現実のギャップ」として問題を定義する `problem-definition` スキルの追加

**ブランチ**: `038-problem-definition-skill` | **日付**: 2026-09-05 | **仕様**: [spec.md](./spec.md)

**入力**: `specs/038-problem-definition-skill/spec.md` の機能仕様

## サマリ

`.claude/skills/problem-definition/SKILL.md` として新しいスキルを1件追加する。曖昧な「問題がある」という訴えを、Ishikawa/Kepner-Tregoe/BABOK/A3の4つの独立した伝統に基づき、現状・あるべき姿・ギャップ・重要性の4要素からなる単一の問題文へ構造化して引き出す。解決策や未検証の原因が問題として持ち込まれた場合はそれを識別して切り分け、`product-strategy` を含む他のいかなるスキルの内容にも依存しない、完全に独立したスキルとする。

技術的な作業のほぼ全ては、`037-product-strategy-skill` の実装で確立済みの現行メカニズムへ、`problem-definition` を追加する形をとる——`tests/run-config-pyramid.sh` の `authored_skills` 群への追加、README 2件への一行追加、`install.sh` は無編集（research.md でこれらを`037`の research.md D2/D3/D5から再確認・再利用する）。`037`との違いは中身（4要素の問題文 vs 6セクションの戦略ブリーフ）と、意図的な相互非依存の徹底のみである。

## 技術コンテキスト

**言語/バージョン**: Markdown（スキル本文・フロントマター）、Bash（構造契約テスト）。実行時に評価されるコードは持たない。

**主要依存**: Claude Code CLI のスキル発見・自動ルーティング機構（`description` フロントマターの自動評価のみ）。

**保存**: ファイルのみ。Git 管理下。`install.sh` により `~/.claude/skills/` へ一括複製同期される。本スキルが対象の文脈に生成する問題文自体は、本リポジトリではなく利用先プロジェクトに保存される（FR-015）。

**テスト**: `tests/run-config-pyramid.sh`——`037-product-strategy-skill` の実装により確立済みのオフライン静的構造契約（research.md D1、`037`の research.md D2 を参照）。`problem-definition` を対象に含めるには、同スクリプト内の `authored_skills` 配列・関連する正規表現リスト・`run_routing_fixtures()` への追加が必要。

**対象プラットフォーム**: Claude Code（macOS/Linux/Windows）。`install.sh` は POSIX シェル前提。

**プロジェクト種別**: エージェント設定リポジトリ。成果物はスキル定義（Markdown + フロントマター）とその配布・検証・文書化の仕組みである。

**性能目標**: 該当なし。`run_budget_contract()` の予算（`.claude/CLAUDE.md` + `.claude/rules/*.md` 合計 `BASELINE_BYTES=20126` 未満）には抵触しない——本機能はルールファイルを一切変更しない。

**制約**:
- FR-015: 本スキルは自らが作成したファイル以外に一切書き込んではならない。
- FR-016/FR-017: 兄弟スキル名を埋め込まない、自分自身の配置パスをハードコードしない——`037`で `run-config-pyramid.sh` の SKILL-05/SKILL-06 として学習済みの制約を、spec.md 自体に最初から明記した（`037`は `/speckit-analyze` で事後追加したが、本機能では最初から反映済み）。
- FR-006: `product-strategy` を含む他スキルへの参照・依存を持たない。

**規模**: 新規スキルディレクトリ1件（`SKILL.md` 1ファイル）。既存ファイルへの編集: `README.md`、`README.ja.md`、`tests/run-config-pyramid.sh`。`install.sh` は無編集。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入の Spec Kit テンプレートのままであり、批准済みのプロジェクト原則が存在しないため、このゲート自体は形式的に通過する（`037`の research.md D4 と同じ状況を再確認済み）。

代わりに、本リポジトリの実質的な統治制約である5つの常時ロードルールに照らして本計画を検証する:

| ルール | ゲート | 状態 |
|---|---|---|
| `clarifier.md` — 重要な結果ギャップの所有 | 未解決の重要な論点はブロッキング質問として解消済みか | **PASS** — /speckit-clarify で2論点を解消済み（再実行・中断時の扱い） |
| `live-documentation.md` — 正本の同期 | 変更された公開契約（README のスキル一覧）は同じ変更の中で更新されるか | **PASS** — FR-019 が README.md/README.ja.md の更新を要求し、tasks.md（Phase 2）で同一機能内のタスクとして扱う |
| `permissions.md` — 最小権限・破壊的操作の回避 | 新しい権限・機密ファイルへのアクセスを追加しないか | **PASS** — 本スキルはツール権限を要求しない |
| `pyramid-principle.md` — 同列の整合 | 要求事項・成功基準が比較可能な粒度で構造化されているか | **PASS** — spec.md の FR/SC は `037` と同じ粒度・様式 |
| `thinking-lenses.md` — 推論の完全性 | 依存関係・分岐が明示されているか | **PASS** — 解決策/原因混入の識別分岐（FR-010/FR-011）、対立するあるべき姿の分岐（FR-012）が明示されている |

**Phase 1 設計後の再確認**: PASS のまま。Phase 1 で追加する data-model.md・contracts/problem-interface.md・quickstart.md は、いずれも新しい権限やルールファイル変更を導入しない。

**Complexity Tracking**: 不要——正当化を要するゲート違反なし。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/038-problem-definition-skill/
├── spec.md                    # 機能仕様（手動 + /speckit-clarify で作成）
├── plan.md                    # 本ファイル
├── research.md                 # Phase 0 出力
├── data-model.md               # Phase 1 出力 — エンティティと不変条件
├── quickstart.md               # Phase 1 出力 — 検証ガイド
├── contracts/
│   └── problem-interface.md    # Phase 1 出力 — SKILL.md と問題文の契約
└── tasks.md                    # Phase 2 出力（/speckit-tasks — 本コマンドでは作成しない）
```

### 変更対象（リポジトリルート）

```text
my-claude-code/
├── .claude/
│   └── skills/
│       └── problem-definition/       # 新規 — スキル本体 (FR-001〜FR-014)
│           └── SKILL.md              #   frontmatter (name/description) + 本文
├── README.md                          # 編集 — スキル一覧への追加 (FR-019)
├── README.ja.md                       # 編集 — 同上、日本語版 (FR-019)
└── tests/
    └── run-config-pyramid.sh          # 編集 — authored_skills 配列・RULE-03/SKILL-06 正規表現・
                                        #        run_routing_fixtures() への新規アサーション追加 (FR-020/021)
```

**構造の決定**: `037-product-strategy-skill` が確立したレイアウトへ、新スキルを同じ位置に slot-in させるだけであり、新しい種類のディレクトリ概念は導入しない。`references/`・`scripts/` サブディレクトリは、本スキルが本文内引用のみで完結する規模（4件の一次資料）であるため不要と判断した。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

該当なし——ゲート違反なし。
