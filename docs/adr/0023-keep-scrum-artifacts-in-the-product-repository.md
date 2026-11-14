---
status: Accepted
date: 2026-11-14
deciders: 利用者（このリポジトリの保守者）
---

# 0023. Scrum の作成物を、プロダクトのフォルダの `scrum/` に置くスキルを加え、雛形をそこへ移す

## コンテキストと問題

利用者は 2026-11-14 に、Notion のテンプレート「Team Scrum Workspace — Portable Template」（Products、Product Backlog、Sprints、Delivery Tasks、Increments を Notion のデータベースで持ち、Relation とビューでつなぐ）を示し、プロダクトごとにこのような Scrum の成果物をリポジトリの中に構成する harness を加えることを尋ねた。

そのときの harness は次の状態だった（`specs/072-scrum-artifacts-in-repo/problem.md`）。

- Scrum の作成物とイベントの雛形8件は、読み取り専用の診断用スキル `apply-scrum-guide` の `references/templates/` にあった。
- 雛形をリポジトリに置く手順も、置いたものの形を見る検査もなかった。
- 雛形の README が勧める置き場所（`scrum/projects/<project_name>/`）は、`sync-docs` が `.living-documentation.json` の `tree.products` で宣言するプロダクトのフォルダとは別の木だった。

## 決定

利用者は、示した4点の推奨を採用し、「標準的なフレームワークを踏襲すること。既存のハーネスを有効に活用して。」と加えた。

- **書き込み型のスキル `manage-scrum-artifacts` を加える。** `apply-scrum-guide` は読み取り専用の診断のまま残す。
- **置き場所は、各プロダクトのフォルダ直下の `scrum/` とする。** 1つのリポジトリに1つのプロダクトなら、リポジトリのルート直下である。
- **範囲は、Scrum Guide（2020年版）の作成物、コミットメント、イベントの記録だけとする。** フォルダの構造とファイルの名前は Scrum Guide が定めないので、スキルの運用上の決まりであると、スキルの本文、参照文書、置かれる `scrum/README.md` のそれぞれに書く。
- **対象は、Git を使う利用者だけとする。** Notion や Issue トラッカーとの同期は行わない。
- **Notion のデータベースと Relation は写さない。** Delivery Tasks は Issue と Pull Request へのリンクで、Increments は Sprint ごとの `increment.md` に書く Pull Request・リリース・コミットへのリンクで代える。
- **Scrum Team が決める値を AI は書かない。** Product Backlog の順序、Product Goal、Sprint Goal、Definition of Done、Sprint に選ぶ項目、見積もり、アカウンタビリティを担う人である。検査は、空のコミットメントを警告として出し、終了コードを変えない。

次の2点は、利用者の決定から実装者が導いた。

- **雛形を `manage-scrum-artifacts` へ移す。** スキルは互いのファイルを参照できない（スキルの契約 C-08、C-09）。置く手順を持つスキルが雛形を持つ。`apply-scrum-guide` は雛形の同梱をやめる。
- **`scrum/README.md` にアカウンタビリティの記入欄を置く。** 欄は空で作る。

## 検討した選択肢

- **`apply-scrum-guide` を書き込み可能にする**: スキルは増えない。診断だけの依頼でもファイルを書けるようになり、読み取り専用という宣言を失う。利用者は別のスキルを選んだ。
- **雛形を両方のスキルに置く**: `apply-scrum-guide` は変わらない。同じ雛形の2つの写しが食い違う。[ADR-0003](0003-vendor-scrum-master-skill.md) は、写しを2か所に持たないことを選んでいる。
- **既存の `scrum/projects/<project_name>/` を保つ**: 変更は少ない。作成物がプロダクトのコードから離れ、`sync-docs` のプロダクトのフォルダと別の木になる。利用者は、プロダクトのフォルダ直下を選んだ。
- **Notion を正とし、リポジトリには読み取り用の写しを置く**: Git を使わない Product Owner やステークホルダーも扱える。同期の仕組みと、どちらが正かの決まりが要る。対象を Git を使う利用者に絞ったので、採らない。
- **Product Backlog の項目を1項目1ファイルにする**: 項目ごとの履歴と Sprint からのリンクが明確になる。順序を別に持つ必要があり、「単一の順序付きの一覧」がファイルの並びから読めなくなる。今は含めない。

## 結果

- スキルは16件から17件になる。両方の README、`docs/claude-config-design.md` の現在の件数、評価の対応表（`docs/harness/capability-map.json`）とシナリオ集に加えた。
- すでに `scrum/projects/<project_name>/` に作成物を置いたリポジトリは、検査の対象にならない。移すかどうかは、そのリポジトリの利用者が決める。スキルは、既存の配置が違うときは何も動かさず、人に尋ねる。
- 検査が見るのは形だけである。Product Backlog の順序の妥当性、Increment が Definition of Done を満たすか、Sprint の長さは見ない。
- `install.sh` を次に実行するまで、`~/.claude/` にはこのスキルが無く、`apply-scrum-guide` には古い雛形が残る。

## 確認方法

- `bash tests/run-harness-skills.sh` が、17スキルの契約と、`manage-scrum-artifacts` のスクリプトのテストを通す。
- `find harness -name product-backlog.md` が、`harness/skills/manage-scrum-artifacts/templates/product-backlog.md` だけを出す。
- `python3 tests/harness-eval/harness_eval.py check` が通る。モデルを呼ぶ評価（`run`）で、作成物を置く依頼にこのスキルが使われ、イベントの進め方を見直す依頼に使われないことは、まだ測っていない。

## 補足情報

- `specs/072-scrum-artifacts-in-repo/` — 問題文、要件グラフ、検証の記録。
- [ADR-0003](0003-vendor-scrum-master-skill.md) — `apply-scrum-guide` の前身のスキルを、このリポジトリを唯一の出どころとして取り込んだ決定。
- [ADR-0015](0015-rule-layer-independence.md) — 層が互いを名指さない決まり。
