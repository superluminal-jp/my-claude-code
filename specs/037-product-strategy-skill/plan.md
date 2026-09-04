# 実装計画: 開発着手前の戦略整理を支援する `product-strategy` スキルの追加

**ブランチ**: `037-product-strategy-skill` | **日付**: 2026-09-04 | **仕様**: [spec.md](./spec.md)

**入力**: `specs/037-product-strategy-skill/spec.md` の機能仕様

## サマリ

`.claude/skills/product-strategy/SKILL.md` として新しいスキルを1件追加する。ビジョン・ターゲットユーザー・提供価値・成功指標・スコープ優先順位・制約を、10件の引用可能な一次資料（Business Model Canvas、Lean Canvas、Cagan *INSPIRED*、JTBD、ISO 9241-210、Torres のオポチュニティ・ソリューション・ツリー、Value Proposition Design、OKR、Balanced Scorecard、North Star Metric の出典、MoSCoW、Porter、狩野モデル）に基づいて構造化して引き出し、新規/既存プロジェクトを自動判別しながら単体の戦略ブリーフドキュメントを生成する。他のツール（Speckit を含む）のファイルには一切依存・介入しない。

技術的な作業はほぼ全て追加的である。リサーチにより、当初 spec.md が前提としていた「ルーティング回帰スイート」（プロンプト→期待スキルのライブ実行方式）は spec 036 により既に撤去され、`tests/run-config-pyramid.sh` によるオフラインの静的構造契約に置き換わっていることが判明した（research.md D2）。実装は、この現行の契約テストへ `product-strategy` を対象スキルとして追加する形をとる。`install.sh` はディレクトリ一括同期のため変更不要（D5）。

## 技術コンテキスト

**言語/バージョン**: Markdown（スキル本文・フロントマター）、Bash（構造契約テスト）。実行時に評価されるコードは持たない。

**主要依存**: Claude Code CLI のスキル発見・自動ルーティング機構（`description` フロントマターの自動評価のみ。`when_to_use` 等の独自トリガーフィールドは使わない——SKILL-02 相当）

**保存**: ファイルのみ。Git 管理下。`install.sh` により `~/.claude/skills/` へ一括複製同期される。本スキルが対象プロジェクトに生成する戦略ブリーフ自体は、本リポジトリではなく利用先プロジェクトに保存される（FR-011）。

**テスト**: `tests/run-config-pyramid.sh`——`.claude/CLAUDE.md`・`.claude/rules/*.md`・`.claude/skills/*/SKILL.md` に対するオフラインの静的構造契約（正規表現による grep ベースのアサーション、ライブの `claude` CLI 実行は行わない）。`product-strategy` を対象に含めるには、同スクリプト内の `authored_skills` 配列・関連する正規表現リスト・`run_routing_fixtures()` への追加が必要（research.md D2）。加えて SC-001 の検証（表現の異なる4プロンプトでの実ルーティング確認）は、この静的契約では測れないため実装後の手動セッション確認とする。

**対象プラットフォーム**: Claude Code（macOS/Linux/Windows）。`install.sh` は POSIX シェル前提。

**プロジェクト種別**: エージェント設定リポジトリ。成果物はコードではなく、スキル定義（Markdown + フロントマター）とその配布・検証・文書化の仕組みである。

**性能目標**: 該当なし。`run_budget_contract()` は `.claude/CLAUDE.md` + `.claude/rules/*.md` の合計バイト数を `BASELINE_BYTES=20126` 未満に保つことを要求するが、本機能はルールファイルを一切変更しないため、この予算には抵触しない。

**制約**:
- FR-011: 本スキルは自らが作成したファイル以外に一切書き込んではならない（他ツールへの統合・依存を持たない）。
- SKILL-01〜SKILL-06（`run-config-pyramid.sh`）: `authored_skills` 配列に加える以上、これらの構造契約（フロントマターの形、`when_to_use` 不在、description の非対象境界の明記、サイバーリング参照の禁止、インストールルートのハードコード禁止）を満たさなければならない。
- FR-003（spec.md）: 本文が使うフレームワークは必ず出典を明記する。

**規模**: 新規スキルディレクトリ1件（`SKILL.md` 1ファイル。参考文献は本文内引用のみとし、独立した `references/` サブディレクトリは持たない——スキル本文自体が10件の引用を持つ`clarifier`と同等の密度であり、`scrum-master`のような複数ファイルへの分割を要する規模ではないため）。既存ファイルへの編集: `README.md`、`README.ja.md`、`tests/run-config-pyramid.sh`。`install.sh` は無編集（D5）。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入の Spec Kit テンプレートのままであり（全項目が `[PRINCIPLE_N_NAME]` 等のプレースホルダ）、批准済みのプロジェクト原則が存在しないため、このゲート自体は形式的に通過する（research.md D4）。

代わりに、本リポジトリの実質的な統治制約である5つの常時ロードルールに照らして本計画を検証する:

| ルール | ゲート | 状態 |
|---|---|---|
| `clarifier.md` — 重要な結果ギャップの所有 | 未解決の重要な論点はブロッキング質問として解消済みか、前提として明示されているか | **PASS** — 2ラウンドのユーザー往復＋ /speckit-clarify での2論点で解消済み（spec.md 明確化決定・明確化セクション） |
| `live-documentation.md` — 正本の同期 | 変更された公開契約（README のスキル一覧）は同じ変更の中で更新されるか | **PASS** — FR-013 が README.md/README.ja.md の更新を要求し、tasks.md（Phase 2）で同一機能内のタスクとして扱う |
| `permissions.md` — 最小権限・破壊的操作の回避 | 新しい権限・機密ファイルへのアクセスを追加しないか | **PASS** — 本スキルはツール権限を要求しない（`allowed-tools` 不要、ファイル書き込み先は利用先プロジェクトの一般ファイルのみ） |
| `pyramid-principle.md` — 同列の整合 | 要求事項・成功基準が比較可能な粒度で構造化されているか | **PASS** — spec.md の FR/SC は既存スキル仕様（016、035）と同じ粒度・様式 |
| `thinking-lenses.md` — 推論の完全性 | 依存関係・分岐が明示されているか | **PASS** — spec.md の新規/既存プロジェクト分岐（FR-008〜FR-010）と、本計画の Phase 0→1→2 の依存順序が明示されている |

**Phase 1 設計後の再確認**: PASS のまま。Phase 1 で追加した data-model.md・contracts/skill-interface.md・quickstart.md は、いずれも新しい権限やルールファイル変更を導入しない。唯一の設計上の重みを持つ決定——`tests/run-config-pyramid.sh` への追加（新規テストファイルではなく既存ファイルの編集）——は、`live-documentation.md` の「正本を分散させない」という原則にむしろ整合する（新しい並行のテスト機構を作らず、現行の唯一の構造契約に合流させるため）。

**Complexity Tracking**: 不要——正当化を要するゲート違反なし。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/037-product-strategy-skill/
├── spec.md               # 機能仕様（/speckit-specify 相当、手動 + /speckit-clarify で作成）
├── plan.md                # 本ファイル
├── research.md             # Phase 0 出力 — D1〜D5
├── data-model.md           # Phase 1 出力 — エンティティと不変条件
├── quickstart.md           # Phase 1 出力 — 検証ガイド
├── contracts/
│   └── skill-interface.md  # Phase 1 出力 — SKILL.md と戦略ブリーフの契約
└── tasks.md                # Phase 2 出力（/speckit-tasks — 本コマンドでは作成しない）
```

### 変更対象（リポジトリルート）

```text
my-claude-code/
├── .claude/
│   └── skills/
│       └── product-strategy/         # 新規 — スキル本体 (FR-001〜FR-011a)
│           └── SKILL.md              #   frontmatter (name/description) + 本文
├── README.md                          # 編集 — スキル一覧への追加 (FR-013)
├── README.ja.md                       # 編集 — 同上、日本語版 (FR-013)
└── tests/
    └── run-config-pyramid.sh          # 編集 — authored_skills 配列・RULE-03/SKILL-06 正規表現・
                                        #        run_routing_fixtures() への ROUTE-09 追加 (FR-015/016, research.md D2)
```

**構造の決定**: 本リポジトリに `src/` は存在しない——その「ソースコード」は `.claude/` 配下の設定ツリーとインストーラであり、`tests/` はそのツリーに対する構造契約を保持する。上記のレイアウトは、新スキルを既存の10件（authored_skills）が既に占めている位置に slot-in させるだけであり、新しい種類のディレクトリ概念は導入しない。`.claude/skills/scrum-master/` のような `references/`・`scripts/` サブディレクトリは、本スキールが本文内引用のみで完結する規模（FR-003 の10文献はいずれも脚注的な一文で足りる）であるため不要と判断した（規模の項を参照）。

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

該当なし——ゲート違反なし。
