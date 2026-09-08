# 契約: `clarifier` スキルの公開インターフェース

**ブランチ**: `039-clarifier-shared-understanding` | **日付**: 2026-09-08

本リポジトリが外部に公開する契約は、スキルの**エントリポイント（フロントマター）**、**生成する成果物の形**、**テストハーネスが強制する構造規約**の3つである。

---

## C1. エントリポイント契約（`SKILL.md` フロントマター）

```yaml
---
name: clarifier
description: <拡張後の記述>
---
```

### 強制される条件

| ID | 条件 | 検証 |
|---|---|---|
| C1-1 | `name` は `clarifier` のまま | FR-022。手動確認 |
| C1-2 | `when_to_use:` フィールドを持たない | SKILL-02（自動） |
| C1-3 | `description` が除外境界の語を含む — `Do not use` / `does not apply` / `exclude` / `not for` / `out of scope` / `対象外` / `使わない` のいずれか | SKILL-03（自動） |
| C1-4 | `description` が `before` / `prerequisite` / `independent` / `compound` のいずれかにマッチ | ROUTE-06（自動） |
| C1-5 | `description` が意図の共通認識形成と形式的要件化の双方を反映する | FR-023。手動確認 |
| C1-6 | `description` が兄弟スキル名を含まない | SKILL-05（自動）。境界は**能力の記述**で指す |

### C1-6 の実装指針

FR-023 は「境界を明示」を求めるが、名指しは求めていない。SKILL-05 は兄弟パッケージ名の出現を失敗として扱う。既存スキルに倣い、能力の記述で指すこと。

| 指したい対象 | 書いてよい | 書いてはいけない |
|---|---|---|
| 問題定義スキル | 「現状とあるべき姿のギャップを特定する別の能力」 | `problem-definition` |
| 製品戦略スキル | 「開発着手前の製品方向づけを担う別の能力」 | `product-strategy` |
| 文書構築スキル | 「不完全な素材から対話で文書を作る別の能力」 | `minto-builder` |

---

## C2. パッケージ構造契約

```text
.claude/skills/clarifier/
├── SKILL.md              # 二段構成の手順 ＋ 群レベルの索引
└── references/
    ├── <適用在庫>.md      # 群A〜D（ユーザーに名指しする）
    └── <設計根拠層>.md    # 群E〜G（名指ししない）
```

| ID | 条件 | 検証 |
|---|---|---|
| C2-1 | `SKILL.md` が設定パス（`.claude/rules` / `.claude/skills` / `rules/*.md`）を参照しない | SKILL-04（自動） |
| C2-2 | パッケージが自身の配置パス `.claude/skills/clarifier` をハードコードしない | SKILL-06（自動） |
| C2-3 | 配下 `*.md` の相対リンクがすべて解決する | OWNED-LINK（自動） |
| C2-4 | `references/` 配下の `*.md` も兄弟スキル名を含まない | SKILL-05（自動。走査対象は配下全 `*.md`） |

### C2-1 の注意点（R3）

常時ルールとの責務の乖離（R3）を `SKILL.md` 内で `rules/clarifier.md` と書いて説明すると SKILL-04 が失敗する。この記述は `docs/claude-config-design.md` 側に置くこと。

---

## C3. 成果物契約（スキルが利用先プロジェクトに書き出すもの）

### C3-1. 共通認識メモ

| 項目 | 契約 |
|---|---|
| 個数 | 1合意あたり単一ファイル（FR-008） |
| パス | `specs/<N>-*/shared-understanding.md`、無ければ `docs/shared-understanding/<slug>.md`（FR-009） |
| 構造 | 6セクション、規定順（FR-008 / data-model.md E1） |
| 言語 | 対話言語。枠組み名と出典は原語（FR-042） |
| 既存時 | 上書きか新バージョンかをユーザーに確認（FR-011） |
| 中断時 | 未完成マーカー付きドラフトとして保存（FR-012） |

### C3-2. 恒久的ユーザーモデル

| 項目 | 契約 |
|---|---|
| パス | `docs/shared-understanding/user-profile.md`、プロジェクトごとに1つ（FR-020） |
| 記録対象 | 作業の進め方に関する事実のみ（FR-043） |
| 禁止 | 能力評価・業務上の機微・第三者に関する記述（FR-043） |
| 書き込み | ユーザーの明示的承認後のみ（FR-019） |

### C3-3. 共通の禁止事項

自身が作成していないファイルへ書き込んではならない（FR-010）。

---

## C4. 振る舞い契約（自動検証不能・人手レビュー対象）

D8 のとおり、以下はオフライン静的検査で判定できない。quickstart.md のシナリオで人手検証する。

| ID | 契約 | 対応 SC |
|---|---|---|
| C4-1 | 提示するのは判断基準（内包）であり、ケース一覧（外延）ではない | SC-007 |
| C4-2 | 質問は AIが原理的にアクセスできない事項に限る。解釈・境界・既定値は候補提示 | SC-007 |
| C4-3 | 枠組みの名前は判断に添えてのみ示し、単独で解説しない | SC-008 |
| C4-4 | 対応する枠組みが無い場合、名前を借りずにその旨を明示する | SC-009 |
| C4-5 | 群E・群G を名指ししない。群F は AI自身の振る舞いの理由としてのみ | SC-010 |
| C4-6 | 一回の提示での名指しは2つ以下 | SC-011 |
| C4-7 | 起動は明示要求時と齟齬の兆候成立時のみ | FR-006 / FR-007 |

---

## C5. 変更してはならないもの

| 対象 | 根拠 |
|---|---|
| `.claude/rules/clarifier.md` | FR-025 |
| `specs/001` 〜 `specs/038` | FR-028 |
| `tests/run-config-pyramid.sh` の `authored_skills` | D2（`clarifier` は登録済み） |
| `install.sh` | D2 |
| `.specify/extensions.yml` の `command: clarifier` / `optional: true` | FR-026 |
