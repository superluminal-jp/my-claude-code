# 実装計画: `clarifier` の「意図の共通認識形成 ＋ 形式的要件化」への拡張

**ブランチ**: `039-clarifier-shared-understanding` | **日付**: 2026-09-08 | **仕様**: [spec.md](./spec.md)

**入力**: `specs/039-clarifier-shared-understanding/spec.md` の機能仕様

## サマリ

既存スキル `.claude/skills/clarifier/SKILL.md` を、形式的要件化のみを担う現状から、**第1段: 意図の共通認識形成 → 第2段: 形式的要件化**の二段構成へ書き換える。名前・登録・ルール層は変更しない。

中核の設計判断は3つ。**(1)** AIが判断基準（内包）を提示しユーザーが却下する向きに固定し、ケース一覧（外延）で意図を詰めない。**(2)** その判断基準を名前のある枠組みから引き、生んだ判断に添えて名指しすることで、基準を外部情報源に照らして検証可能にすると同時に、ユーザーが枠組みを暗黙的に習得する経路を作る。**(3)** 34種の在庫（適用在庫24 ＋ 設計根拠層10）を、名指しする層（群A〜D）と名指ししない層（群E〜G）に二層化し、`references/` へ分離する。

Phase 0 リサーチは利用者指示に従い参考文献25件を一次情報に照合し、**1件の帰属誤りを検出・修正**した（推論のはしごの7段形は Argyris ではなく Ross/Senge 版）。これは spec 自身が R4「枠組み劇場」として定義した失敗の実例であり、本機能が導入する規律がその規律自身によって検出された形になる。

## 技術コンテキスト

**言語/バージョン**: Markdown（スキル本文・フロントマター・参照ファイル）、Bash（構造契約テスト）。実行時に評価されるコードを持たない。

**主要依存**: Claude Code CLI のスキル発見・自動ルーティング機構（`description` フロントマターの自動評価のみ）。

**保存**: ファイルのみ。Git 管理下。`install.sh` により `~/.claude/skills/` へ一括複製同期される。本スキルが生成する共通認識メモと恒久的ユーザーモデルは、本リポジトリではなく利用先プロジェクトに保存される（FR-009 / FR-020）。

**テスト**: `tests/run-config-pyramid.sh` のオフライン静的構造契約のみ。`clarifier` は `authored_skills` に登録済みのためハーネス自体の変更は不要（research.md D2）。振る舞い系の成功基準 SC-007〜SC-016 は自動化せず、[quickstart.md](./quickstart.md) S2 の人手検証に委ねる（D8）。

**対象プラットフォーム**: Claude Code（macOS/Linux/Windows）。`install.sh` は POSIX シェル前提。

**プロジェクト種別**: エージェント設定リポジトリ。成果物はスキル定義（Markdown ＋ フロントマター）とその配布・検証・文書化の仕組み。

**性能目標**: 該当なし。

**制約**:
- FR-025: `.claude/rules/clarifier.md` を変更しない。
- FR-028: `specs/001`〜`038` を変更しない。
- SKILL-04: `SKILL.md` が設定パスを参照しない——R3 の説明は `docs/claude-config-design.md` 側に置く。
- SKILL-05: パッケージ配下の全 `*.md` が兄弟スキル名を含まない——FR-023 の境界明示は**能力の記述**で行う（D4）。
- ROUTE-06 / SKILL-03: 書き換え後の `description` が既存の正規表現契約を満たし続ける。

**規模**: 既存スキル1件の本体書き換え ＋ `references/` 配下の新規参照ファイル。既存ファイルへの編集: `.claude-ja/skills/clarifier/SKILL.md`、`.specify/extensions.yml`、`README.md`、`README.ja.md`、`docs/claude-config-design.md`。`install.sh` と `tests/run-config-pyramid.sh` は無編集。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入の Spec Kit テンプレートのままであり、批准済みのプロジェクト原則が存在しないため、このゲート自体は形式的に通過する。

代わりに、本リポジトリの実質的な統治制約である5つの常時ロードルールに照らして検証する。

| ルール | ゲート | 状態 |
|---|---|---|
| `clarifier.md` — 重要な結果ギャップの所有 | 未解決の重要な論点が解消されているか | **PASS** — `/speckit-clarify` で5論点、Phase 0 で A2・A3・R6 を解消。前提 A1〜A5 はすべて解消済み |
| `live-documentation.md` — 正本の同期 | 変更された公開契約の説明が同じ変更内で更新されるか | **PASS** — FR-027 が README 2件と `docs/claude-config-design.md` を、FR-026 が `.specify/extensions.yml` を、FR-024 が日本語ミラーを要求。tasks.md で同一機能内のタスクとして扱う |
| `permissions.md` — 最小権限・破壊的操作の回避 | 新しい権限や機微ファイルへのアクセスを追加しないか | **PASS** — ツール権限を要求しない。FR-043 が恒久的ユーザーモデルの記録対象を制限し、公開コミット履歴への機微情報流入を防ぐ |
| `pyramid-principle.md` — 同列の整合 | 要求事項・成功基準が比較可能な粒度で構造化されているか | **PASS** — FR-001〜044 は関心事ごとに節分けされ、SC-001〜016 が対応する |
| `thinking-lenses.md` — 推論の完全性 | 依存関係・分岐が明示されているか | **PASS** — FR-017（第2段は第1段の後）、FR-040（群を先に選ぶ）、FR-006/007（起動条件の成立・不成立）が分岐を明示 |

**Phase 1 設計後の再確認**: **PASS のまま**。Phase 1 で追加した data-model.md・contracts/skill-interface.md・quickstart.md は、新しい権限もルールファイル変更も導入しない。ただし Phase 0 で検出した以下2点を記録する。

1. **D4（SKILL-05 と FR-023 の緊張）** — 名指しではなく能力の記述で境界を示すことで解消。spec の変更を要さず、ゲート違反ではない。
2. **D1（帰属誤り）** — spec.md を修正済み。`live-documentation.md` の「never invent support」に照らした是正であり、未解決の違反は残らない。

**Complexity Tracking**: 不要——正当化を要するゲート違反なし。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/039-clarifier-shared-understanding/
├── spec.md                        # 機能仕様（FR-001〜044、SC-001〜016）
├── plan.md                        # 本ファイル
├── research.md                    # Phase 0（D1 引用検証を含む）
├── data-model.md                  # Phase 1
├── quickstart.md                  # Phase 1（S1 自動 / S2 人手）
├── contracts/
│   └── skill-interface.md         # Phase 1
└── tasks.md                       # Phase 2（/speckit-tasks が生成。本コマンドでは作らない）
```

### 変更対象（リポジトリルート）

```text
.claude/skills/clarifier/
├── SKILL.md                       # 【書き換え】二段構成 ＋ 群レベルの索引
└── references/                    # 【新規】在庫の分離先
    ├── <適用在庫>.md               #   群A〜D（ユーザーに名指しする）
    └── <設計根拠層>.md             #   群E〜G（名指ししない）

.claude-ja/skills/clarifier/SKILL.md   # 【同期】英語版と同構成。references/ の訳は作らない
.claude/rules/clarifier.md             # 【不変】FR-025
.specify/extensions.yml                # 【編集】L11-13 の prompt / description のみ
README.md                              # 【編集】L39, L139
README.ja.md                           # 【編集】L28
docs/claude-config-design.md           # 【編集】L44 の対応表 ＋ R3 の乖離記述
tests/run-config-pyramid.sh            # 【不変】clarifier は登録済み
install.sh                             # 【不変】skills を一括同期
specs/001〜038                          # 【不変】FR-028
```

**構造判断**: 新規ディレクトリを増やさず、既存の `clarifier` パッケージ内に `references/` を追加する。この構成は `digital-agency-frontend`・`scrum-master`・`apple-notes` で確立済みのパターンであり（research.md D3）、新しい規約を導入しない。

## 実装順序（依存関係）

Phase 2（`/speckit-tasks`）が詳細化する前提の、真の依存関係のみを示す。

```text
1. references/ の作成（在庫34種の記述）
       │  ← SKILL.md の索引がここへリンクするため先行が必要
       ↓
2. SKILL.md の書き換え（二段構成 ＋ 索引 ＋ description）
       │  ← 日本語ミラーは英語版の確定後
       ↓
3. .claude-ja/skills/clarifier/SKILL.md の同期
       │
       ├─→ 4. .specify/extensions.yml（独立して実施可）
       ├─→ 5. README.md / README.ja.md（独立して実施可）
       └─→ 6. docs/claude-config-design.md（R3 記述を含む。独立して実施可）
       ↓
7. bash tests/run-config-pyramid.sh（S1）
       ↓
8. quickstart.md S2 の人手検証
```

4〜6 は相互に独立であり、順序を強制しない。7 は 1〜6 の完了後にのみ意味を持つ。

## 残る限界

- **SC-007〜SC-016 は自動検証できない**（D8）。実行時のモデルの振る舞いに関する基準であり、オフライン静的検査の対象外。人手レビューに依存する。
- **R2・R4・R5 は実行時の自己判定に依存する**。齟齬の検知も、枠組みが判断を実際に支持しているかの判定も、AI自身が行う。FR-036 が「枠組みが無い」と述べる経路を正規の出力として用意することで、失敗が行き止まりにならないようにしている。
- **Robertson & Robertson の版・刊行年が一次情報で未確認**（D1）。実装時に版表記を落とすか、確認する。
- **`.claude-ja` の同期方針そのもの**（新規スキルを追随させるか）は本機能の範囲外（D7）。
