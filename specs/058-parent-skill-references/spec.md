# Feature Specification: 親スキルが宣言した子スキルを名前で参照できるようにし、meta-spec と model-routing を廃止する

**Feature Branch**: `feat/parent-skill-references`

**Created**: 2026-11-05

**Status**: Draft

**Input**: User description: "meta-spec model-routing は廃止してもよい。取りまとめ役などの親スキルは子スキルを参照しても良いようにルールを変更。各スキルをエージェントとして組み直すことも検討" および "新しいブランチとワークツリーを使って作業"

**利用者の指示と、Claude が決めた既定**: 利用者は3点を指示した。Claude は、利用者に確認せずに次の既定を選んだ。いずれも Git の履歴から戻せる。

| # | 論点 | 利用者の指示 | Claude が選んだ既定と理由 |
|---|---|---|---|
| D1 | `meta-spec` スキルと `model-routing.md` ルールを残すか | 廃止してもよい | 両方を廃止する。`meta-spec` は、過去に廃止したスキルと同じく `archive/` へ移す。`model-routing.md` は、過去に廃止したルール `skill-routing.md`(スキルの組み合わせ方を並べた中央の表)と同じく削除する。どちらも Git の履歴から戻せる |
| D2 | 親スキルが参照してよい範囲 | 取りまとめ役などの親スキルは、子スキルを参照してよい | 親スキルは、自分の `SKILL.md` で宣言した子スキルだけを、名前で参照できる。子スキルから親や兄弟への参照、パスでの参照は従来どおり禁止する |
| D3 | 親子の宣言の仕方 | 指定なし | 親スキルの `SKILL.md` に「`## Child skills`」節を置き、子を1行に1つ「- `名前`」の形で書く。スキル自身が自分を記述するというこのリポジトリの方針に合わせ、中央の一覧は作らない |
| D4 | 階層の深さ | 指定なし | 1段に限る。子スキルは自分の子を宣言できない。親→子→親の循環は、子が親を自分の子として宣言して初めて生じる。子は何も宣言できない(FR-004)ので、循環そのものを探す検査がなくても、この循環は起きない。多段が要る親スキルが現れたら緩める |
| D5 | スキルをエージェントとして組み直すか | 検討 | 本仕様の対象外とする。検討の結果は会話で報告する |
| D6 | 意思決定記録(ADR)を作るか | 指定なし | 作らない。`maintaining-living-documentation` スキルは、利用者が求めない限り ADR を作らないと定めている。ADR-0015 との食い違いは Edge Cases に書き、会話で作成の可否を尋ねる |

**Authority**: 本仕様(この `spec.md`)が正である。`docs/adr/0015-rule-layer-independence.md`(状態は Proposed)は、親から子への名前付きの参照を「却下した代替案」に挙げ、設定ノード間の名前参照を禁じている。本仕様は、スキル層に限ってこの禁止を緩める。ADR-0015 の本文は書き換えない(D6)。

## 用語

- **設定の層と設定ノード**: このリポジトリの設定は3つの層から成る。頂点の `.claude/CLAUDE.md`、常時ロードのルール(`.claude/rules/*.md`)、スキル(`.claude/skills/`)である。ADR-0015(`docs/adr/0015-rule-layer-independence.md`、層どうしの参照の向きを決めた意思決定記録)は、これらの各ファイルを「設定ノード」と呼ぶ。「スキル層」はスキルの層を指す。
- **検査の ID**: `tests/run-config-pyramid.sh` の中で各検査に付けた名前(例: SKILL-05)。この仕様に出る ID の意味は次のとおり。APEX-07: 頂点がほかの設定のパスを書かない。RULE-01: ルールのファイルの一覧が決まったとおりである。RULE-02: ルールが設定のパスを書かない。RULE-03: ルールが自作スキルを名指ししない。RULE-11(本仕様で削除): `model-routing.md` が能力層と労力を扱う。RULE-24(本仕様で追加): `model-routing.md` がない。SKILL-04: スキルの入口のファイルが設定のパスを書かない。SKILL-05: 自作スキルがほかの自作スキルを名指ししない。SKILL-06: スキルが自分のインストール先のパスを書かない。SKILL-08(本仕様で追加): `meta-spec` が退避されている。ROUTE-11(本仕様で削除): `meta-spec` の説明文が、分割だけを扱い個々の仕様を扱わないと書いている。BUDGET-01: 常時ロードの合計が基準値未満である。PARENT-01〜08(本仕様で追加): User Story 1 の受け入れシナリオ1〜8。
- **Spec Kit**: 仕様(`spec.md`)、計画、タスクの一覧の順に作って実装する開発手順を支える、GitHub の道具。各プロジェクトで `specify init` を実行すると、`speckit-*` という名前のスキルを生成する。
- **スキル**: `.claude/skills/<名前>/SKILL.md` に置く手順書。Claude は、その説明文(`description`)から作業に関係すると判断したときだけ本文を読み込む。`install.sh` が `~/.claude/skills/` に同期する。
- **自作スキル**: `tests/run-config-pyramid.sh` の配列 `authored_skills` に並ぶスキル。このリポジトリで書いたスキルのうち、構造の検査の対象にするもので、この配列が正本である。上流から取り込んだ `maintaining-living-documentation` と、Spec Kit が生成する `speckit-*` は含まない。
- **親スキルと子スキル**: 親スキルは、「`## Child skills`」節で宣言した複数のスキルを、順序を決めて適用する取りまとめ役のスキルである。子スキルは、その節に名前が書かれた自作スキルである。子スキルは親がなくても、自分の説明文だけで呼ばれる。
- **名前で参照する**: スキルの本文やパッケージ内の Markdown に、ほかのスキルの名前をバッククォートで囲んで書くこと(例: `` `coder` ``)、またはスラッシュの後に書くこと(例: `/coder`)。検査 SKILL-05 は、この形を参照とみなす。
- **パスで参照する**: 名前の直後にスラッシュを続け、ファイルの位置を書くこと(例: `../coder/SKILL.md`、`.claude/skills/coder/`)。検査は、名前の直後にスラッシュが続く形をパスとみなす。スキルが置かれる場所は、利用者の設定・プロジェクト・プラグインで異なるため、パスでの参照は親スキルにも許さない。
- **常時ロード**: Claude Code がすべてのセッションの開始時に読み込む設定ファイル。このリポジトリでは `.claude/CLAUDE.md` と `.claude/rules/*.md` である。合計の大きさを検査 BUDGET-01 が基準値 20,126 バイト未満に制限している。基準値は spec 036(`specs/036-rule-layer-independence/`)で決めた値で、本仕様では変えない。
- **退避**: 廃止したスキルを `archive/<名前>/` へ移すこと。`install.sh` は `archive/` を同期しないため、退避したスキルは次のインストールで `~/.claude/skills/` から消える。

## 背景

変更前(`origin/main` のコミット e5ffcf4)は、どの自作スキルもほかの自作スキルを名前で参照できなかった。根拠は3か所にある。

1. `tests/run-config-pyramid.sh` の検査 SKILL-05(「authored packages do not name siblings」)が、自作スキルのパッケージ内の Markdown に別の自作スキルの名前があれば失敗する。
2. `docs/claude-config-design.md`(設定の設計方針を記録した文書)の §5「変更するとき」の表が、スキルの「禁止する参照」に「他スキルへの名指し・パス参照」を挙げる。
3. ADR-0015 が、親から子への名前付きの参照を却下している。理由は、発見の情報(どのスキルをいつ使うか)を二重に管理することになり、スキルの追加や改名のたびに常時ロードの設定を変える必要が出るためである。

このため、複数のスキルを決まった順序で使う作業手順(例: 問題の定義、要件の合意、実装、PR 本文の点検)を、1つのスキルとして書けなかった。利用者が工程ごとにスキル名を指定するしかなかった。

本仕様の親スキルは、ADR-0015 が却下した理由に当たらない。親スキルは常時ロードではなく、条件付きで読み込まれる。子スキルがいつ呼ばれるかは、引き続き子スキル自身の説明文が決める。親スキルが持つのは、自分の作業手順の中で子を使う順序だけである。子を改名したときに壊れるのは、その子を宣言した親スキルだけで、検査がそれを見つける(FR-003。宣言した子が自作スキルとして存在しなければ違反になる)。

`meta-spec` スキル(1つの大きな取り組みを、独立に仕様化できる単位に分けて記録する手順)と `.claude/rules/model-routing.md`(作業の単位ごとに、モデルの能力層と推論の労力を選ぶ常時ロードのルール)は、利用者が不要と判断した(D1)。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 親スキルは、宣言した子スキルを名前で参照できる (Priority: P1)

保守者(このリポジトリの設定を書く人)が、複数のスキルを順に使う取りまとめ役のスキルを書く。親スキルの `SKILL.md` に「`## Child skills`」節を置いて子を宣言すれば、本文で子を名前で参照しても検査は通る。宣言していないスキルの参照や、子から親への参照は、検査で失敗する。

**Why this priority**: 利用者が直接求めた変更である。これがないと、取りまとめ役のスキルを書けない。

**Independent Test**: 実際の親スキルはまだリポジトリにない。このため実際の自作スキルに対しては、検査 SKILL-05 が、どのスキルもほかのスキルを名指ししないことを確かめる。親子の規則は、`tests/run-config-pyramid.sh` が一時ディレクトリに架空のスキル(親 `parent`、子 `child-a` と `child-b`、どちらでもない `outsider`)を作り、次の受け入れシナリオの結果を検査 PARENT-01〜08 で確かめる。

**Acceptance Scenarios**:

1. **Given** `child-a` を子として宣言した `parent`、**When** `parent` の本文が `` `child-a` `` と書く、**Then** 違反はない。
2. **Given** 同じ `parent`、**When** 宣言していない `` `outsider` `` を書く、**Then** 違反になる。
3. **Given** `parent` が宣言した `child-a`、**When** `child-a` の本文が `` `parent` `` と書く、**Then** 違反になる。
4. **Given** `parent` が宣言した `child-a` と `child-b`、**When** `child-a` の本文が `` `child-b` `` と書く、**Then** 違反になる。
5. **Given** 自作スキルにない `ghost` を子として宣言した `parent`、**When** 検査する、**Then** 違反になる。
6. **Given** `parent` が宣言した `child-a`、**When** `child-a` が自分の「`## Child skills`」節で `child-b` を宣言する、**Then** 違反になる(D4)。
7. **Given** `child-a` を子として宣言した `parent`、**When** `parent` の本文が `../child-a/SKILL.md` と書く、**Then** 違反になる(パスでの参照)。
8. **Given** `parent`、**When** `parent` が自分自身を子として宣言する、**Then** 違反になる。

---

### User Story 2 - `meta-spec` スキルを退避する (Priority: P1)

`meta-spec` スキルは `archive/meta-spec/` に移り、次のインストールで利用者の `~/.claude/skills/` から消える。退避の理由と戻し方は `archive/meta-spec/README.md` に書かれている。

**Why this priority**: 利用者が廃止を許し、Claude が廃止を選んだ(D1)。

**Independent Test**: 検査 SKILL-08 が、`.claude/skills/meta-spec/` がなく、`archive/meta-spec/SKILL.md` と `archive/meta-spec/README.md` があることを確かめる。

**Acceptance Scenarios**:

1. **Given** 変更後のリポジトリ、**When** `.claude/skills/` を見る、**Then** `meta-spec/` がない。
2. **Given** 同じリポジトリ、**When** `archive/meta-spec/` を見る、**Then** スキルの元のファイルと、退避の理由と戻し方を書いた `README.md` がある。
3. **Given** `tests/run-config-pyramid.sh`、**When** 読む、**Then** `authored_skills` と、スキル名を並べた検査のパターンに `meta-spec` がない。

---

### User Story 3 - `model-routing.md` ルールを廃止する (Priority: P1)

`.claude/rules/model-routing.md` を削除し、常時ロードのルールは4ファイルになる。

**Why this priority**: 利用者が廃止を許し、Claude が廃止を選んだ(D1)。常時ロードはすべてのセッションで読み込まれるため、不要な文を除くと全セッションの文脈の消費が減る。

**Independent Test**: `tests/run-config-pyramid.sh` の検査 RULE-01 がルールを4ファイルと確かめ、検査 RULE-24 が `model-routing.md` がないことを確かめる。

**Acceptance Scenarios**:

1. **Given** 変更後の `.claude/rules/`、**When** ファイルを数える、**Then** `clarifier.md`、`permissions.md`、`pyramid-principle.md`、`thinking-lenses.md` の4つだけがある。
2. **Given** 常時ロード、**When** 合計の大きさを測る、**Then** 変更前の 20,099 バイトより小さい。

---

### Edge Cases

- **子スキルは単独でも使われる**: 子スキルの本文は変えない。子スキルは親を名指ししないため、親がなくても読める。
- **常時ロードは引き続きスキルを名指ししない**: `.claude/CLAUDE.md` とルールの検査(APEX-07、RULE-02、RULE-03)は変えない。親スキルを常時ロードから呼ぶ経路は作らない。
- **パッケージ内の参考資料**: 親スキルは、`SKILL.md` だけでなく自分のパッケージ内の Markdown(`references/` など)でも、宣言した子を名前で参照できる。検査 SKILL-05 はパッケージ内のすべての Markdown を見る。
- **ADR-0015 との食い違い**: ADR-0015 の「参照境界」節は「独立した実行時設定ノードは、上位、下位、横の別ノードを名前またはパスで参照しない」と書く。本仕様の後は、スキル層ではこの文が成り立たない。ADR-0015 の本文は変えず(D6)、`docs/claude-config-design.md` の §5「変更するとき」に本仕様の規則を書いて食い違いを明示する。新しい ADR を作るかは利用者に尋ねる。
- **サブエージェントのモデル**: `model-routing.md` の廃止後は、サブエージェントのモデルと労力を選ぶ常時ロードの指示がなくなる。spec 057(`specs/057-context-free-reader/`、成果物を会話を見ていないサブエージェントに読ませる手順を加えた変更)の Assumptions は、そのサブエージェントのモデルと労力を `model-routing.md` に従って選ぶと書いている。仕様は当時の記録なので書き換えない。廃止後は、指定がなければ、サブエージェントは呼び出し元のモデルを使う。
- **過去の仕様**: `specs/` の過去の仕様にある `meta-spec` と `model-routing.md` への言及は、当時の事実の記録として残す。
- **スライドの検査**: `tests/run-digital-agency-slides-skill.sh` は、`digital-agency-slides` スキル(自作スキルだが `authored_skills` に入っていない)がほかのスキルを名指ししないことを、名前の一覧で検査している。一覧には、過去に廃止した `adr` スキル(意思決定記録の手順)の名前も残っている。廃止した名前を残すこの一覧の慣例に合わせ、`meta-spec` も残す。残しておけば、退避したスキルを戻したときにも、スライドのスキルからの名指しを見つけられる。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 親スキルは、`SKILL.md` の「`## Child skills`」節に、子を1行に1つ「- `名前`」の形で宣言する。コードブロックの中の行は宣言とみなさない。
- **FR-002**: 自作スキルのパッケージ内の Markdown は、ほかの自作スキルを名前で参照してはならない。ただし、そのパッケージ自身の `SKILL.md` が子として宣言したスキルは例外とする。「`## Child skills`」節の宣言の行も名前での参照に当たるが、宣言した名前なのでこの例外に含まれる。「`## Child skills`」節を持たないパッケージには例外がない。子スキルが「`## Child skills`」節を持つことは、この要件ではなく FR-004 の違反として判定する。
- **FR-003**: 宣言された子は、自作スキルであり、`SKILL.md` が存在しなければならない。親は自分自身を子として宣言してはならない。
- **FR-004**: 宣言された子は、自分の子を宣言してはならない(D4)。
- **FR-005**: 親スキルも、子をパスで参照してはならない。既存の検査 SKILL-04(スキルの入口のファイルが設定のパスを書かない)と SKILL-06(スキルが自分のインストール先のパスを書かない)は変えない。
- **FR-006**: `tests/run-config-pyramid.sh` は、FR-001〜FR-005 を、実際の自作スキルと、User Story 1 の架空のスキルの両方に対して検査する。実際の自作スキルには親スキルがまだないため、今は FR-002(ほかのスキルを名指ししない)だけが実際に働き、FR-003〜FR-005 は親スキルが加わったときに働く。
- **FR-007**: `meta-spec` を `archive/meta-spec/` へ移し、退避の理由と戻し方を `archive/meta-spec/README.md` に書く。`tests/run-config-pyramid.sh` の `authored_skills` と、検査 RULE-03 と SKILL-06 のパターンから `meta-spec` を除く。`meta-spec` の説明文を確かめる検査 ROUTE-11 を削除し、退避を確かめる検査 SKILL-08 を加える。
- **FR-008**: `.claude/rules/model-routing.md` を削除する。検査 RULE-01 を4ファイルに改め、`model-routing.md` の内容を確かめる検査 RULE-11 を削除し、削除を確かめる検査 RULE-24 を加える。
- **FR-009**: `README.md`、`README.ja.md`、`docs/claude-config-design.md`、持ち運び用プロンプト(`claude-ai-system-prompt.md`、`chatgpt-system-prompt.md`。このリポジトリの原則を Claude.ai と ChatGPT のカスタム指示欄に貼れる形にした2ファイル)の記述を、変更後の内容に合わせる。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `tests/run-config-pyramid.sh` が、新しい検査を含めてすべて通る。新しい検査のうち振る舞いの変更を表すものは、変更前に失敗することを確かめる。
- **SC-002**: ほかの `tests/run-*.sh` と、`pyramid-structure` スキル(結論を先に置く構成で文章を組み、送る前に検査するスキル。`authored_skills` に入っている)の単体テスト(`.claude/skills/pyramid-structure/tests/`)が通る。`tests/run-readme-skill-index.sh` は、`README.md` と `README.ja.md` がすべてのスキルの名前を挙げていることを、スキルとファイルの組ごとに1件として検査する。その件数は、変更前の31件から `meta-spec` の2件(`README.md` と `README.ja.md` の分)が減る。この検査は `.claude/skills/` にあるスキルだけを数えるので、README の退避の一覧に `meta-spec` を載せても数に入らない。
- **SC-003**: 常時ロードの合計が、変更前の 20,099 バイトより小さい。

## Assumptions

各項目の確度は、その仮定が利用者の意図に合っている見込みを高・中・低で示す。

- 「廃止してもよい」は、廃止するかの判断を Claude に委ねたものと読む(確度: 中)。廃止は Git の履歴から戻せる。
- 親子は1段で足りる(確度: 中)。想定している取りまとめ役(例: 問題の定義、要件の合意、実装、PR 本文の点検を順に適用するスキル)は、子を直接並べるだけである。
- 取りまとめ役のスキルそのものは本仕様では作らない(確度: 中)。利用者が求めたのは規則の変更である。子をスキルのまま使うか、エージェント(Claude Code が作業の一部を任せるために起動する別の Claude の定義)にするか(D5)によって、親が子を呼ぶ方法が変わる。スキルなら Claude がスキルとして読み込み、エージェントならサブエージェントとして起動する。
