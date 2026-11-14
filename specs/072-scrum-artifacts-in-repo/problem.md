# Problem Statement: プロダクトごとの Scrum の作成物を、リポジトリの中のファイルとして置き、保つ手順が harness にない

**Status**: Complete
**Generated**: 2026-11-14

この問題文の対象は、このリポジトリの `harness/skills/` である。2026-11-14 の利用者とのやりとりから始まった。利用者は Notion のテンプレート「Team Scrum Workspace — Portable Template」（Products、Product Backlog、Sprints、Increments、Definition of Done などを Notion のデータベースで持つ）を示し、「プロダクトごとにこのようなスクラムの成果物をレポジトリ内に構成するようなハーネスを追加するのはどうか」と尋ねた。

用語:
- **Scrum の作成物**: Scrum Guide（2020年版）が定める3つの作成物（Product Backlog、Sprint Backlog、Increment）と、それぞれのコミットメント（Product Goal、Sprint Goal、Definition of Done）。
- **プロダクトのフォルダ**: 1つのリポジトリの中で、別々に作られ別々に届けられる単位のフォルダ。1リポジトリに1プロダクトのときは、リポジトリのルートがそれにあたる。

## 理想の状態

- どのリポジトリでも、プロダクトごとに、Scrum Guide が定める作成物とコミットメントがファイルとしてあり、コードや Pull Request と同じ場所で版管理される。
- 人も AI も、Product Goal、順序付きの Product Backlog、Definition of Done、各 Sprint の Sprint Goal と Sprint Backlog と Increment を、決まった場所から読める。
- Product Backlog と Definition of Done はプロダクトに1つずつで、Sprint ごとに複製されない。Sprint ごとの記録は Sprint の順に並ぶ。
- この形が崩れたこと（必要なファイルが無い、単一であるべき作成物が複数ある、Sprint のフォルダの名前や番号が決まりに合わない）は、機械的な検査がエラーとして報告する。
- 順序、Product Goal、Sprint Goal、Definition of Done、Sprint に選ぶ項目は Scrum Team が決める。AI はそれらを埋めず、決まっていないものは「未設定」と分かる形で残る。

## 現在の状態（このセッションで確認、2026-11-14）

- **雛形はあるが、置く手順がない。** `harness/skills/apply-scrum-guide/references/templates/` に、Product Backlog、Definition of Done、Sprint ごとの6種（Sprint Backlog、Increment、Sprint Planning、Daily Scrum、Sprint Review、Sprint Retrospective）の Markdown の雛形がある。同じフォルダの `README.md` は置き場所として `scrum/projects/<project_name>/sprints/<sprint_num>-<date>/` を勧め、「使用時は本ディレクトリのテンプレートを目的の場所へコピーし」と書くだけである。
- **雛形を持つスキルは書き込めない。** `apply-scrum-guide` の前付けは `kind: overlay`、`permission: read_only` で、手順は診断と提案だけである（`SKILL.md` の「手順」1〜6）。
- **形を検査するものがない。** `harness/skills/` のどのスクリプトも、Scrum の作成物のファイルがあるか、単一か、Sprint のフォルダが決まりに合うかを見ない（`grep -rl "product-backlog" harness/skills --include=*.py` は何も出さない）。
- **置き場所が、プロダクトのフォルダの決まりと合っていない。** `sync-docs` は `.living-documentation.json` の `tree.products` でプロダクトのフォルダを宣言する（`references/practices.md` の「Documentation tree」）。雛形の `README.md` が勧める `scrum/projects/<project_name>/` は、それとは別の、リポジトリのルート直下の木である。
- **未設定のコミットメントを知らせるものがない。** 雛形の `- **Product Goal**：` などの欄が空のままでも、何も報告されない。
- 利用者のリポジトリで、Scrum の作成物がどこにどれだけあるかのデータはない。

## ギャップ

理想では、どのリポジトリでもプロダクトごとに Scrum Guide の作成物とコミットメントが決まった場所のファイルとしてあり、その形が崩れれば検査がエラーにし、Scrum Team が決めるべきものは未設定と分かる形で残る。実際には、雛形は診断用の読み取り専用のスキルの中にあるだけで、リポジトリに置く手順も、置いたものの形を見る検査も、未設定を知らせる仕組みもなく、勧められている置き場所はプロダクトのフォルダの決まりと別になっている。

## 重要性

- `harness/skills/` は `install.sh` で `~/.claude/` に入り、利用者のすべてのプロジェクトで使われる。
- 作成物がリポジトリにあると、AI がコードと同じ場所で Product Goal や Definition of Done を読める。これが Sprint の準備やレビューの質を上げる、というのは検証していない仮説である。
- 機械的に見つけられるようになるのは、ファイルの有無、単一性、Sprint のフォルダの名前と番号、欄が空かどうかという形だけである。Product Backlog の順序が価値に合っているか、Increment が Definition of Done を満たすかは見つけられない（含めないもの）。

## Identified solution (not part of the problem statement)

会話の中で提案し、利用者が採用したもの（2026-11-14）。

- 既存の雛形を各リポジトリに置き、保つ、書き込み型のスキルを1つ加える。
- Notion のデータベース（Delivery Tasks、Increments）や Relation とビューは写さない。Issue・Pull Request・リリースへのリンクと、単一の順序付きの `product-backlog.md` で代える。

## 合意済みの決定（利用者の回答、2026-11-14）

利用者は、提案した4点の推奨について「推奨を採用。標準的なフレームワークを踏襲すること。既存のハーネスを有効に活用して。」と答えた。

- **利用者の範囲**: 自分自身、または Git を使う開発者だけを対象にする。Notion を正とするチームとの同期は含めない。
- **置き場所**: 各プロダクトのフォルダ直下の `scrum/`。1リポジトリに1プロダクトのときはリポジトリのルート直下の `scrum/`。`sync-docs` の `tree.products` のプロダクトのフォルダと揃える。
- **スキルの分け方**: 新しい書き込み型のスキルを加える。`apply-scrum-guide` は読み取り専用の診断のまま残す。
- **範囲**: Scrum Guide の作成物とイベントの記録だけ。Team Charter や AI 運用の文書は含めない。
- **標準的なフレームワークを踏襲する**: 作成物、コミットメント、イベント、誰が決めるかは Scrum Guide（2020年版）に従う。Scrum Guide が定めないこと（フォルダの構造、ファイルの名前）は、このスキルの運用上の決まりであると明記する。（「標準的なフレームワーク」を Scrum Guide と読んだのは実装者の解釈で、確度は中。スキルの形式は、既存のスキルの契約（Agent Skills の仕様に基づく）に従う。）
- **既存のハーネスを有効に活用する**: 既存の雛形を使い、既存のスキルの契約と検査に通し、この変更そのものを既存の納品の流れ（問題、要件、実装、検証）で進める。

## 実装者が決めたこと（利用者の決定から導いたもの。異論があれば変えられる）

- **雛形は新しいスキルへ移す。** スキルは互いのファイルを参照できない（契約 C-08、C-09）。雛形を両方に置くと2つの写しが食い違う。置く手順を持つスキルが雛形を持つ。`apply-scrum-guide` は読み取り専用のまま残り、雛形の同梱だけをやめる。
- **アカウンタビリティの記入欄を `scrum/README.md` に置く。** Scrum Guide は Scrum Team の3つのアカウンタビリティを定める。誰が担うかはチームが決めるので、欄は空で作る。

## 別の問題の候補（この問題に含めない）

- Notion や Issue トラッカーとの同期。
- Sprint の長さ（1か月以内、固定）の検査。
- Product Backlog の項目を1項目1ファイルに分けること。
