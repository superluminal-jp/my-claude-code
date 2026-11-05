# refinement-checker

English: [README.md](README.md)

`check_graph.py` は、要求の論理グラフまたはスキル合成グラフの宣言を読み、破っている構造の規則をすべて報告する。何も変更しない。合格は、宣言が結果に挙げた規則に合うことだけを意味し、分解が十分であること、実装が安全であること、テストを実行したことを示さない。契約は [spec 059](../../specs/059-refinement-graph-checker/spec.md) であり、引数、出力、終了コードの詳細は[コマンドの契約](../../specs/059-refinement-graph-checker/contracts/cli.md)にある。

以下で使う語:

- **スキル**: Claude Code のスキル。`SKILL.md` という手順書を持つディレクトリで、作業に関係するときに Claude が読み込む。このリポジトリのスキルは `.claude/skills/` にある。
- **spec 058**: [`specs/058-parent-skill-references/spec.md`](../../specs/058-parent-skill-references/spec.md)。親スキルが `SKILL.md` の「`## Child skills`」節に、順に適用するスキルを1行に1つ「- `名前`」の形で挙げられると定め、一段だけを許す(子スキルは自分の子を挙げられない)。
- **水準 L1、L2、L3**: 受け入れ条件が何を検証するか。L1 は1つの葉の要求、L2 は子を統合した親の要求、L3 はシステム全体を検証する。
- **Phase**: spec 059 は5段階の Phase 1 である。Phase 2 は問題定義と分解のスキル、Phase 3 は各層の独立した検証と証拠の記録(どのテストがどのコミットでどう終わったか)、Phase 4 は人の判断のためのレビューカード、Phase 5 はレビュー時間と品質の比較実験を扱う。

## 用途、実行主体、配布先

- **用途**: AI が作った変更を、すべての差分を読み直すのではなく、要求と証拠でレビューできるようにする計画の Phase 1。後の Phase で親スキル(まだ1つもない)や独立した監査役のエージェントを書く前に、要求の分解とスキルの合成を、機械が検査できる宣言の形にする。
- **実行主体**: GitHub Actions の `.github/workflows/ci.yml` のジョブ `test`(`tests/run-refinement-checker.sh` から)と、手元で実行する保守者または Claude。
- **配布先**: なし。`.claude/` の外にあるため、`install.sh` は `~/.claude/` に写さない。`.claude/skills/` の下のスキルへ移すかは Phase 2 で決める。

## 使い方

Python 3.9 以上。標準ライブラリだけを使い、ネットワークに接続しない。

```sh
python3 tools/refinement-checker/check_graph.py FILE
python3 tools/refinement-checker/check_graph.py --format json FILE
python3 tools/refinement-checker/check_graph.py --skills-dir .claude/skills
```

`FILE` は1つの宣言ファイル(JSON)である。`--skills-dir DIR` は互換モードで、`DIR/*/SKILL.md` の「`## Child skills`」節を spec 058 の定めのとおりに読む。どちらか一方だけを指定する。

## 宣言の形式

宣言ファイルは `"schema_version": 1` と、`requirements` か `skills` のちょうど一方(ノードの配列)を持つ。それぞれの例は [`examples/`](examples/) にある。欄ごとの型と、欄がないときや誤っているときに破る規則は[データモデル](../../specs/059-refinement-graph-checker/data-model.md)にある。

- **要求のノード**: `id`、`statement`、`decomposition`(`AND`、`OR`、`LEAF`)、`acceptance`(1件以上の `{id, description, level}`。水準は `L1`、`L2`、`L3`)。任意で `children`、`assumptions`、`counterexamples`、OR だけの `selection`(すべての子の条件)。
- **スキルのノード**: `id`、`permission`(`read_only`、`workspace_write`、`external_effect`)、`role`(`orchestrator`、`worker`、`auditor`、`checker`)。任意で `children`。

## 規則

「対象」の列で、*宣言ファイル*は2種類の宣言ファイルの両方、*要求*と*スキル*はその種類だけ、*互換モード*は `--skills-dir`、*すべて*はすべての入力を指す。

| 規則 | 対象 | 合格の条件 |
|---|---|---|
| S-00 | 宣言ファイル | 各ノードがオブジェクトで、欄の値の型が正しく、定義していない欄がない |
| S-01 | 宣言ファイル | 各ノードが空でない一意な `id` を持つ |
| S-02 | すべて | 子が定義されており(互換モードでは `SKILL.md` があり)、一度だけ挙げられる |
| S-03 | すべて | 子をたどって元のノードに戻らない。違反は循環を示す |
| S-04 | 要求 | `LEAF` は子を持たず、`AND` と `OR` は2件以上の子を持つ |
| S-05 | 要求 | `OR` がすべての子に空でない条件を与え、子でない ID を挙げない。ほかのノードは `selection` を持たない |
| S-06 | 要求 | すべてのノードが1件以上の受け入れ条件を持つ |
| S-07 | 要求 | 受け入れ条件の ID が空でなくグラフ全体で一意で、水準が `L1`〜`L3` である |
| S-08 | すべて | 複数の親を持つ子は合格する(報告しない) |
| S-09 | スキル | 権限と役割が定めた値である。`auditor` と `checker` は、自分も届くすべてのスキルも `read_only` である |
| S-10 | 互換モード | 宣言された子が自分の子を宣言しない(spec 058 の一段) |
| S-11 | 要求 | 親を持たないノードが2つ以上ない。挙げ忘れた子は2つ目の根として見つかる |

## 終了コード

| コード | 意味 |
|---|---|
| 0 | 違反がない |
| 1 | 規則の違反が1件以上ある |
| 2 | 入力を解釈できない(引数の誤り、読めない・5 MiB を超える・UTF-8 でない入力、JSON の構文の誤り、キーの重複、深すぎる入れ子、誤った最上位)、または検査器自身の異常 |

## 限界

- `permission` と `role` は宣言であり、強制ではない。ファイルを書くスキルが `permission: read_only` と宣言しても、監査役が `role: worker` と宣言しても、S-09 を通る。強制は Claude Code の権限設定と、スキルを動かす実行環境が担う。
- 宣言したスキルの ID を実在の `SKILL.md` と照合しない。実在のスキルを読むのは互換モードだけである。
- 互換モードは spec 058 の構造の規則だけを検査する。宣言された子が配列 `authored_skills`(このリポジトリが書いたスキルの一覧。`tests/run-config-pyramid.sh` の冒頭にある)にあるか、スキルが本文でほかのスキルをどう名指すかは、引き続き `tests/run-config-pyramid.sh` が検査する。
- OR の条件は存在だけを検査し、排他か、すべての場合を覆うかは検査しない。親の受け入れ条件が本当に親を検証しているかは、レビューする人の判断である。

## テスト

```sh
bash tests/run-refinement-checker.sh
```

[`tests/`](tests/) の受け入れテストを実行し、2つの例を検査し、このリポジトリの `.claude/skills/` を互換モードで読む。Phase 3 の証拠の記録を要する4つのテストは `NOT RUN` と表示し、合格の件数に数えない。T-04(親の検証が失敗すれば変更を完了としない)、T-05(証拠のない完了の報告を受け入れない)、T-06(別のコミットの証拠を古い証拠として拒否する)、T-10(不明なリスクの分類を低リスクとみなさず停止する)である。
