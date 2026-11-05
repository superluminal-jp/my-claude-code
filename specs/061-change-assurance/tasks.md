---
description: "Task list for 061: 実行の証拠で、葉・親・システムの検証を別々に判定する"
---

# Tasks: 実行の証拠で、葉・親・システムの検証を別々に判定する

背景、用語、既定 D1〜D6、規則 A は同じディレクトリの `spec.md`、欄の詳細は `contracts/manifest.md` にある。作業は、ブランチ `feat/goal-refinement`(コミット d0736a2)から作ったワークツリー `my-claude-code-worktrees/change-assurance`(ブランチ `feat/change-assurance`)で行う。「スキル」は `.claude/skills/change-assurance/`、「検査器」はその `scripts/assure.py` を指す。

- [X] T001 [US1] [US2] 要求グラフと検証の記録のフィクスチャ(spec の User Story 1 のシナリオ1〜8、User Story 2 のシナリオ1〜4、M-00〜M-02 の負例)を `tests/fixtures/` に作り、テストを書き、失敗を確かめる(Red)。結果: 21件(T003 を含む)がすべて失敗した(subTest を含め失敗2件・エラー23件)
- [X] T002 [US1] [US2] 検査器の `check` と `gate` を実装する(Green)。結果: T004 とあわせて21件が通った(Python 3.14.3 と 3.9.6)
- [X] T003 [US3] JUnit XML のフィクスチャ(合格・失敗・スキップ・プロパティ・名前の中の ID・DOCTYPE)とテストを書き、失敗を確かめる(Red)。結果: T001 に含めて書いた
- [X] T004 [US3] `collect-junit` を実装する(Green)。結果: 通った
- [X] T005 [US3] `SKILL.md`、`references/manifest.md`、`references/reviewer.md`、例を書く。`tests/run-config-pyramid.sh` の自作スキルの一覧と名前のパターンに `change-assurance` を加え、親子の規則を含めて通ることを確かめる。結果: `run-config-pyramid` 57件が通った。このリポジトリで初めての実際の親スキルであり、宣言した子の名前による参照(spec 058)と、互換モードの S-10 も通った
- [X] T006 `tests/run-change-assurance-skill.sh` を書き、CI の必須ジョブに加える。`tests/run-refinement-checker.sh` の `NOT RUN` の4行を、`change-assurance` のテストで実装済みと示す行に改める(SC-002)。結果: `run-change-assurance-skill` 3件、`run-refinement-checker` 5件が通った。後者の `NOT RUN` の4行は消した
- [X] T007 README の英日を改め、ローカルの検査をすべて実行して件数を記録する。結果: `run-config-pyramid` 57件、`run-readme-skill-index` 33件、`run-removed-guardrails` 4件、`run-package-safety-bundle` 21件、`run-refinement-checker` 5件、`run-change-assurance-skill` 3件、`run-secure-logging-skill` 40件、`run-digital-agency-frontend-skill` 74件、`run-install` 成功、`pyramid-structure` の単体テストが通った
- [X] T008 `/code-review` で差分をレビューし、確かめた指摘を直して記録する。結果: 10件の指摘のうち9件を受け入れ、回帰テスト(12件が失敗する Red、コミット e0d9301)を先に書いてから直した。34件が通る。下の「中断時点の記録」の表の予定どおりに直した。10件目の重複は却下し、文字の出力の二重表示だけを直した

## 中断時点の記録(2026-11-06、利用量の上限による)

T008 の `/code-review`(労力 medium、PR #114)は10件を指摘した。9件を受け入れ、回帰テストを先に書いた(このコミットの時点で12件が失敗する Red)。修正は、中断の後に行った(T008 の結果)。

| # | 指摘 | 予定の対応 |
|---|---|---|
| 1 | 受け入れ条件のない空の要求グラフで `pass` になる | A-01 で、受け入れ条件が1つもなければ `blocked` |
| 2 | すべてを `not_applicable` にすると証拠なしで `pass` になる | A-03 で、各要求に `passed` の検査が1つ以上なければ `blocked` |
| 3 | `rejected` の承認が高リスク以外で無視される | リスクにかかわらず `fail` |
| 4 | 末尾が改行のコミットを受け入れる(`$` の挙動) | `fullmatch` にする |
| 5 | 承認者と実装担当の名前を、大文字小文字と空白を区別して比べる | 両端の空白を除き `casefold` して比べる |
| 6 | CDATA の中の `<!DOCTYPE` で正しいレポートを拒否する | 根の要素より前(プロローグ)だけを調べる |
| 7 | 合格とスキップの混在の理由が「スキップだけ」と誤る | 件数を正しく書く |
| 8 | ID の境界に `.` を含めない | 境界の文字に `.` を加える |
| 9 | `--format` をサブコマンドの後に置けない | サブコマンドにも `--format` を加える(既定は `SUPPRESS`) |
| 10 | goal-refinement の検査器との重複、文字の出力での違反の二重表示 | 重複は却下(spec 058 はパスでの参照を禁じる)。二重表示は、判定の文字の出力で理由だけを示すよう直す |

Phase 4 の作りかけの変更(`load_graph` が要求の ID を返す、判定が検査ごとの結果を返す)は、ワークツリー `my-claude-code-worktrees/review-card` から外し、パッチとして退避した。ブランチ `feat/review-card` には仕様 062 と失敗するテスト10件がコミット済みである。Phase 5 は未着手。

## 2回目のレビュー(2026-11-06)

- [X] T009 積み重ねた PR #112〜#116 をまとめた `/code-review`(労力 xhigh、利用者が実行)の指摘のうち、この PR で入った9件を確かめた。7件を受け入れ、回帰テスト(6つが失敗する Red、コミット 41ddaf3)を先に書いてから直した。36件が通る(collect のテスト3件が継承で2回走っていたのを直したため、件数は以前の34件に新しい5件を足した数より3件少ない)。2件は仕様の判断であり、spec.md の「未決の事項」に書いて利用者に判断を求めた

| # | 指摘 | 対応 |
|---|---|---|
| 1 | JUnit の XML で、コメントや処理命令の中の `<` の後ろに置いた DOCTYPE を見落とし、実体を展開して葉の検査を合格にした(J-01) | 正規表現をやめ、XML の構文解析器(expat)が見つけた文書型宣言を拒む。再現した |
| 2 | 親の受け入れ条件が葉と同じ ID を使うと、葉の検査が親の L2 の検査を兼ね、判定が `pass` になる | 受け入れ条件の ID の重複を、入力を解釈できない誤り(終了コード 2)として拒む。goal-refinement の検査器の S-07 と同じ扱いである。再現した |
| 3 | A-07 の理由が、インフラの変更の種類を加工せずに書くため、改行で結果の行を偽造できる(CWE-117) | 種類を `show()` で表示する。再現した |
| 4 | M-00 で拒んだ証拠を持つ `passed` を、水準ごとの件数で `passed` に数える | M-00 と判定で同じ証拠の検査関数を使い、`blocked` に数える。再現した |
| 5 | 同じコミットを短い SHA と完全な SHA で書くと「古い証拠」と示す | 一致とはみなさない(先頭の数桁が同じコミットは意図して作れるため)。理由を「長さが違う。両方を完全な SHA で書く」に改める。再現した |
| 6 | `references/manifest.md` の段落が規則の表を切り、A-07 が表の行にならない | 段落を表の後ろへ移す |
| 7 | collect のテスト3件が、継承のため2回走る | 共通の基底クラスに分ける |
| 8 | `not_applicable` を実装担当だけの判断で付けられ、親の唯一の L2 の検査を省ける | 利用者の判断待ち。D4 は理由のある `not_applicable` を認めており、変えれば仕様の変更になる |
| 9 | spec 060 の D7 が Phase 3 に残した、リスクの分類による反証役の強制を、本仕様が扱っていない | 利用者の判断待ち。仕様の抜けとして spec.md に書いた |

## 利用者の決定の実装(2026-11-06)

- [X] T010 利用者が決めた2つ(spec.md の D7・D8)の受け入れテストを `tests/test_assure.py` に書き、失敗を確かめる(Red、コミット 7f79337)。決定で期待が変わる既存のテスト6件(`high` の変更を判定するもの4件、すべての検査を `not_applicable` にするもの1件、`L3` の検査を `not_applicable` にして合格するもの1件)は、反証の記録や承認を渡す形、または A-06 も期待する形に改めた。新しいテストのうち2件(別の問題の反証の記録、`approved_by` の形式)は、未知の引数や未定義の欄としての誤りで偶然に通ったため、本来の理由を確かめるよう厳しくしてから Red を確かめた
- [X] T011 判定に `--report` と規則 A-08 を、検査の欄に `approved_by` を、A-06 に `L2`・`L3` の `not_applicable` の承認を加える(Green)。`references/manifest.md`、`SKILL.md` の手順4・5、README の英日、契約(`contracts/manifest.md`)を改める。結果: 43件が Python 3.14.3 と 3.9.6 で通った。契約の出力例の `rules_checked` に M-00〜M-02 が抜けていた食い違いも直した
