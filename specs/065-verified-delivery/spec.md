# Feature Specification: 2つのスキルを目的に合う名前に変え、検査器のレビューの指摘14件を直す

**Feature Branch**: `refactor/verified-delivery`

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "スキル名を目的に合ったものに変えたい"(2026-11-06)。直前に利用者が実行した `/code-review xhigh 全体的に改善最適化` の指摘14件を、同じ PR に含める(利用者の決定)

**要旨**: 親スキル `change-assurance` を `verified-delivery` に、`goal-refinement` を `requirements-decomposition` に改める。手順と検査の規則は変えない。あわせて、検査器(`assure.py`、`pilot.py`、`check_graph.py`)とそのテストへのレビューの指摘14件を直す。規則の意味を変える修正は、同じ人物の判定(F1)、レビューカードのエスケープ(F2、F3、F8)、入力の誤りの扱い(F4〜F7)、子スキルの宣言の読み方(F9)である。残りの5件(F10〜F14)は、振る舞いを変えない整理である。

**利用者の決定と、Claude が決めた既定**:

| # | 論点 | 根拠 | 決めた事項 |
|---|---|---|---|
| D1 | 親スキルの名前 | 利用者の決定(2026-11-06)。Claude の推奨は `evidence-based-acceptance` だった | `verified-delivery`。問題の定義から判定までの流れ全体を名前にする |
| D2 | 分解のスキルの名前 | 利用者の決定(2026-11-06。Claude の推奨を選んだ) | `requirements-decomposition`。成果物の `requirements-graph.json` と規則が「要求」と呼ぶものを分解するためである |
| D3 | 名前を変える範囲 | Claude の既定 | スキルのディレクトリ、`name`、見出し、親の `## Child skills`、ほかのスキルの宣言の例、README の英日、CI の手順の名前、`tests/` の検査スクリプトの名前(`run-verified-delivery-skill.sh`、`run-requirements-decomposition-skill.sh`)、`tests/run-config-pyramid.sh` の自作スキルの一覧を改める。同梱のスクリプトの名前(`assure.py`、`pilot.py`、`check_graph.py`)と規則の ID は変えない。`specs/` と `archive/` の過去の記録は書き換えない |
| D4 | 旧名の扱い | `install.sh` は `~/.claude/skills/` を丸ごと置き換える | 旧名を残す別名は作らない。次の `install.sh` で旧名のスキルは消える。`/change-assurance` と `/goal-refinement` は、`/verified-delivery` と `/requirements-decomposition` に変わる |
| D5 | レビューの指摘 | 利用者の決定(同じ PR に含める) | 14件すべてを直す。振る舞いを変える9件(F1〜F9)は、失敗するテストを先に書く |

**Authority**: 本仕様が正である。spec 058〜064 は、ここに書いた範囲で変わる。それらの文書は書き換えない。

## 用語

spec 059〜064 の用語は、そのまま使う。スキルの名前だけが、D1 と D2 のとおりに変わる。

- **同じ人物**: 承認者と実装担当の名前を、Unicode の NFKC 正規化をかけ、書式文字(カテゴリ Cf。ゼロ幅スペースなど)を除き、大文字小文字と前後の空白を区別せずに比べて、一致すること。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 名前を変えても、手順と検査は同じに働く (Priority: P1)

**Acceptance Scenarios**:

1. **Given** 名前を変えたリポジトリ、**When** `tests/run-*.sh` をすべて実行する、**Then** すべて通り、各検査の件数は名前の変更の前と同じである。
2. **Given** `verified-delivery` の `SKILL.md`、**Then** `## Child skills` は `problem-definition`、`requirements-decomposition`、`coder` を宣言し、自作スキルの規則(spec 058)を満たす。
3. **Given** `.claude/` の下、`tests/`、README の英日、CI、**Then** スキルの名前としての旧名 `change-assurance` と `goal-refinement` は現れない。過去の仕様のディレクトリ(`specs/061-change-assurance/` など)へのリンクは、その名前のまま残す。

### User Story 2 - 別の綴りの同じ人を、独立した承認者とみなさない (Priority: P1)

1. **F1** **Given** 実装担当が `claude` の高リスクの変更、**When** 承認者が `clau\u200bde`(ゼロ幅スペース入り)か全角の `ｃｌａｕｄｅ`、**Then** `blocked`(A-05)である。テストの変更の `approved_by` と、`L2`・`L3` の省略の `approved_by` でも同じである(A-06)。

### User Story 3 - レビューカードは、入力の文字からリンクや判定の印を作らない (Priority: P1)

1. **F2** **Given** 要求の文に `HTTPS://evil.example/login`、`Http://x.example`、`ftp://evil.example/x`、`WWW.evil.example`、**When** カードを作る、**Then** どれもコードとして示され、リンクにならない。
2. **F3** **Given** 要求の ID `REQ-READ #9989; pass`、**Then** 図の中に `#9989;` は現れない(`#` を `#35;` にする)。
3. **F8** **Given** 証拠の参照 `C:\ci\run.log`、**Then** カードのコードの中に `C:\ci\run.log` と、そのとおりに示す(逆スラッシュを二重にしない)。

### User Story 4 - 入力の誤りは、その誤りとして報告する (Priority: P1)

1. **F4** **Given** `"children": "oops"` の要求を持つグラフ、**When** `gate` と `card` を実行する、**Then** どちらも A-09 で `blocked`、終了コード 1 である。
2. **F5** **Given** `change_id` のない検証の記録と、保証レビューの記録、**When** 判定する、**Then** M-00 で `blocked`、終了コード 1 である(別の変更の記録という誤りにしない)。
3. **F6** **Given** 5000桁の整数を含む検証の記録、要求グラフ、比較実験の記録(分が `10**400`)、**Then** 検査器の内部の誤りではなく、入力の誤り(終了コード 2、または比較実験の記録の規則の違反)として報告する。
4. **F7** **Given** `schema_version` のない反証の記録、`schema_version` が 99 の記録、定義していない欄を持つ記録、`reviewer` か `context_given` のない記録、**Then** どれも終了コード 2 である。

### User Story 5 - 子スキルの宣言を、コードブロックの中から読まない (Priority: P2)

1. **F9** **Given** `## Child skills` の例を `~~~` のコードブロックの中、または行頭に1〜3個の空白を置いたコードブロックの中に書いた `SKILL.md`、**When** `check_graph.py --skills-dir` と `tests/run-config-pyramid.sh` で読む、**Then** 子の宣言とみなさない。**Given** 4個のバッククォートで始まり、中に3個のバッククォートの行を持つコードブロックの後の、本当の `## Child skills` 節、**Then** その節を宣言として読む。

### Edge Cases

- F10〜F14 は振る舞いを変えないため、既存のテストが通ることで確かめる。F14 は、`.claude/` の下のファイルが `specs/` を参照しないことを検索で確かめる。

## Requirements *(mandatory)*

- **FR-001**: D1〜D4 のとおりに名前を変える。
- **FR-002**: 同じ人物の比較を、用語の定義のとおりにする(F1)。高リスクの承認の判定は、テストの変更と省略の承認と同じ関数を使う(F10)。
- **FR-003**: レビューカードは、GitHub Flavored Markdown の拡張の自動リンク(大文字小文字を区別しない `http://`、`https://`、`ftp://`、`www.`、メールアドレス)を、どれもコードとして示す(F2)。図の文字の `#` を `#35;` にする(F3)。コードの中の逆スラッシュを二重にしない(F8)。
- **FR-004**: `card` は、`gate` が読めるグラフを入力の誤りにしない(F4)。保証レビューの記録の `change_id` は、検証の記録の `change_id` が空でない文字列のときだけ比べる(F5)。読めない大きさの数は入力の誤りにする(F6)。反証の記録は、保証レビューの記録と同じく、外枠(`schema_version` 1 と `challenge_report` だけ)と欄(`problem_id`、`reviewer`、`context_given`、`findings` だけ、型も)を確かめる(F7)。
- **FR-005**: `## Child skills` の宣言を読むとき、コードブロックを CommonMark のフェンスの規則で判定する。開きは行頭の空白が3個までで、3個以上のバッククォートかチルダ。閉じは同じ文字で、開きと同じ数以上で、後に空白しか続かない行である(F9)。`check_graph.py` と `tests/run-config-pyramid.sh` の両方に適用する。
- **FR-006**: 外枠の確かめ方を1つの関数にまとめ、検証の記録、保証レビューの記録、反証の記録、比較実験の記録の読み込みで使う(F12)。カードは、判定が求めた未解消の指摘をそのまま使い、計算し直さない(F11)。テストの一時ファイルの書き方を1つにまとめる(F13)。`.claude/` の下のファイルから `specs/` への参照を除き、規則をその場で述べる(F14)。
- **FR-007**: 名前の変更と同じ変更の中で、README の英日、`references/` の文書、CI の手順を、変更後の名前と動作に合わせる。

## Success Criteria *(mandatory)*

- **SC-001**: User Story 2〜5 の各シナリオを、実装の前に失敗するテストとして書き、失敗を確かめてから直す。
- **SC-002**: 既存の検査がすべて通る。

## Assumptions

- 利用者は、旧名での呼び出しをやめ、新しい名前で呼ぶ(確度: 高)。別名は置かない(D4)。

## Out of Scope

規則の ID と同梱のスクリプトの名前の変更、ほかのスキル(`pyramid-structure` の README の `spec 055` の参照など)の整理、証拠の出所の確認、Claude Code の実行の観測。
