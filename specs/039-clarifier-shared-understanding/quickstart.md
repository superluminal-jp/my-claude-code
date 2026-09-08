# クイックスタート: `clarifier` 拡張の検証

**ブランチ**: `039-clarifier-shared-understanding` | **日付**: 2026-09-08

実装完了後、本機能が動作していることを確認する手順。自動検証（S1）と人手検証（S2）に分かれる。詳細な契約は [contracts/skill-interface.md](./contracts/skill-interface.md)、成果物の形は [data-model.md](./data-model.md) を参照。

---

## 前提

- リポジトリルートで実行する
- ブランチ `039-clarifier-shared-understanding`
- 実装（`.claude/skills/clarifier/` の書き換えと `references/` の作成）が完了していること

---

## S1. 自動検証 — 静的構造契約

```bash
bash tests/run-config-pyramid.sh
```

**期待結果**: `Results: N passed, 0 failed`

失敗した場合に確認する契約（[contracts/skill-interface.md](./contracts/skill-interface.md) C1・C2 参照）:

| 失敗した契約 | 原因の典型 |
|---|---|
| SKILL-03 | 書き換えた `description` から除外境界の語が消えた |
| SKILL-04 | `SKILL.md` に `rules/clarifier.md` 等の設定パスを書いた（R3 の説明は `docs/` 側へ） |
| SKILL-05 | `SKILL.md` または `references/*.md` に兄弟スキル名を書いた |
| SKILL-06 | 自身の配置パスをハードコードした |
| ROUTE-06 | `description` から `before`/`prerequisite`/`independent`/`compound` が消えた |
| OWNED-LINK | `references/` へのリンクが解決しない |
| BUDGET-01 | ルールファイルを変更した（本機能では変更しないはず。FR-025） |

### 不変であることの確認

```bash
git diff --name-only main...HEAD | grep -E '^(\.claude/rules/|specs/0(0|1|2|3[0-8]))' && echo "NG: 変更してはならないものが変更されている" || echo "OK: 不変対象に変更なし"
git diff --stat main...HEAD -- install.sh tests/run-config-pyramid.sh
```

**期待結果**: 前者が `OK`、後者が空（両ファイル無変更）。

---

## S2. 人手検証 — 振る舞い契約

D8 のとおり自動化しない。各シナリオはスキル名を出さずに依頼し、期待される振る舞いを確認する。

### S2-1. 内包で提示するか（C4-1 / C4-2 / SC-007）

**入力例**: 実質的に異なる2つ以上の解釈が成立する依頼を、スキル名を出さずに持ち込む。

**期待**:
- AIの理解・前提（確信度付き）・スコープ外・未解決点が**分離して**提示される
- 提示されるのは判断基準であって、ケースの一つずつの確認ではない
- 解釈・境界・既定値が**質問として**出てこない（候補提示になっている）

**失敗の兆候**: 「Aは含みますか」「Bの場合はどうしますか」と個別ケースを列挙して尋ねてくる。

### S2-2. 枠組みの名指し方（C4-3 / C4-6 / SC-008 / SC-011）

**入力例**: 完了条件が測定不能な依頼（「もっと速くしたい」等）。

**期待**:
- SMART が適用され、測定可能な形が提示される
- SMART の**名前がその判断に添えて**示される
- SMART の**解説そのものは提示されない**
- 一回の提示で名指しされる枠組みが2つ以下

### S2-3. 枠組みが無い場合（C4-4 / SC-009）

**入力例**: 在庫の群A〜Dのいずれにも対応しないギャップを含む依頼。

**期待**: 手近な枠組みに押し込まず、確立した枠組みが無いこととAIの推論に基づく基準であることが明示される。

### S2-4. バイアスの名指し方向（C4-5 / SC-010）

**期待**:
- 「私の理解が伝わっている前提を置かないために復唱します（透明性の錯覚）」のような**AI自身の振る舞いの理由**としてのみ現れる
- 「あなたは知識の呪いにかかっている」のような**ユーザーの認知状態への断定**が現れない
- 群E（学習の設計）と群G（協調の理論）の理論名が一度も現れない

### S2-5. 起動条件（C4-7 / FR-006 / FR-007）

| 入力 | 期待 |
|---|---|
| 単一解釈しか許さない明確な依頼 | **起動しない**。確認を挟まず作業へ進む |
| 直前の成果物を否定してやり直しを求める | **起動する**。同じ理解のまま作り直さず、分岐点を特定する |
| 同一論点を2回言い直す | **起動する** |

### S2-6. 成果物（C3-1 / C3-2 / SC-013〜SC-016）

**期待**:
- 合意成立時に単一ファイルが `specs/<N>-*/shared-understanding.md` または `docs/shared-understanding/<slug>.md` に生成される
- 6セクションが規定順で揃っている
- 記述言語が対話言語と一致し、枠組み名と出典が原語のまま
- 同一パスで2回目を実行すると上書き／新バージョンの確認が出る
- 恒久的ユーザーモデルに能力評価・業務上の機微・第三者への言及が含まれない

---

## S3. ドキュメント同期の確認（FR-027）

```bash
grep -n "clarifier" README.md README.ja.md docs/claude-config-design.md
grep -n -A3 "before_specify" .specify/extensions.yml
```

**期待結果**:
- README 2件と `docs/claude-config-design.md` の `clarifier` 説明が拡張後の内容になっている（拡張前の「requirement elicitation, INVEST/Gherkin」等が残っていない）
- `docs/claude-config-design.md` に R3（常時ルールとの責務の乖離）の記述がある
- `.specify/extensions.yml` の `prompt` / `description` が拡張後の目的を反映し、`command: clarifier` と `optional: true` は不変

---

## S4. 日本語ミラー（FR-024 / D7）

```bash
diff <(grep -c '^#' .claude/skills/clarifier/SKILL.md) <(grep -c '^#' .claude-ja/skills/clarifier/SKILL.md)
```

**期待結果**: 見出し数が一致（同構成）。`references/` の日本語版は**作成しない**（D7）。
