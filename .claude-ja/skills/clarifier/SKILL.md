---
name: clarifier
description: "重大な曖昧さを、検証可能で範囲が定まった、意思決定可能な要件へと形式化する。未解決のスコープ、制約、成功条件、非機能要件、優先順位付け、受け入れ基準が安全なコミットを妨げている場合、または、ユーザーが明示的に形式的な要件引き出し、ユーザーストーリー、Given/When/Thenシナリオ、INVEST、MoSCoW、FURPS+のカバレッジを求めている場合に使用する。単に依頼が簡潔であるという理由だけでは使用しないこと——それが認識可能な成果物やワークフローを明確に指し示し、着手に十分な情報を提供している場合、また、その作業内での通常のコンテキスト収集についても同様である。他の能力が独立して合致する場合は、これを最初に適用してブロッキングとなる要件のみを解消し、その後、独立して合致した作業を継続すること。"
---

# 正式な要件

目的: 構造化された引き出し（エリシテーション）を通じて、重大な曖昧さを検証可能で範囲の定まった要件へと転換する。未解決の選択が安全なコミットを妨げている場合、またはユーザーが要件成果物を求めている場合にのみ、形式的な技法を適用する。認識可能な成果物やワークフローを明確に指し示す短い依頼は、簡潔であるという理由だけでは曖昧とはみなさない。ISO/IEC/IEEE 29148:2018、INVEST、Gherkin、MoSCoW、FURPS+、SMARTに基づく（[参考文献](#references)を参照）。

## 主要な目的

曖昧な依頼を、検証可能で、範囲が定まり、意思決定可能な要件へと転換する。

## 中核プロセス

1. 意図、スコープ、制約を把握する。
2. 重大なブロッキング・ギャップと、依頼された作業の中で解決できる詳細事項とを分離する。
3. デフォルト案を代替案とともに提示する。
4. チームが検証できる受け入れ基準へと変換する。
5. 前提事項と未解決のリスクを確認する。

他の能力が独立して合致する場合は、まずブロッキングとなる要件作業のみを完了させ、その後その作業を継続する。その作業に固有のコンテキスト収集や成果物手順を置き換えないこと。

## フラグを立てるべき曖昧さのパターン

- **曖昧な数量表現**: 「速く」「たくさん」「多くの」「すぐに」「堅牢な」「スケーラブルな」「使いやすい」 -> 数値＋単位を要求する。
- **未定義の代名詞・スコープ**: 「それ」「システム」「すべて」 -> 対象を明確に名指しする。
- **隠れた複合要件**: 複数の要件を束ねた「〜と〜」「〜または〜」を含む記述 -> 分割する。
- **暗黙の主体・トリガー**: 「必要に応じて」「自動的に」 -> 主体、イベント、前提条件を明示する。
- **要件への実装の混入**: 問題の合意より先に解決策が指定されている -> *何を*と*どうやって*を分離する。
- **肯定形のない否定**: 「遅くしないこと」 -> 測定可能な肯定形（「p95 < 200ms」）で言い換える。

## 引き出し（エリシテーション）ツールボックス（選択的に使用）

- 欠けている次元に対して5W2H。
- 測定可能な目標に対してSMART。
- ユーザーストーリーの品質に対してINVEST。
- テストシナリオに対してGiven/When/Then。
- スコープの優先順位付けに対してMoSCoW。
- 非機能要件に対してFURPS+。

## 品質ゲート

実装に進む前に、各要件は次を満たしているべきである。

- 曖昧でないこと、
- 実現可能であること、
- 検証可能であること、
- 矛盾がないこと、
- 見積もりが可能な程度に範囲が定まっていること。

## アンチパターン

- 複数の解釈が成り立ちうる場合に、黙って一つの解釈を選ぶこと。
- 作業が終わった後で尋ねること（「Xを作りましたが、これで合っていますか？」）。
- 一括で確認せずに、ターンごとに確認事項を積み重ねること。
- 「もっと良くして」のような重大に曖昧な依頼を、合意されたフィット基準なしに実行可能なものとして扱うこと。
- 十分に定義された成果物の依頼を、一般的な要件ヒアリングへとそらしてしまうこと。
- ユーザーが同意していない受け入れ基準を作り出すこと。

## 確認事項のテンプレート

```text
Blocking gaps:
1) <dimension>: <question>
   Default: <X>
   Alternative: <Y>
   Impact: <reversible/irreversible, scope>

Assumptions if proceeding:
- <assumption> (confidence: high/medium/low)
```

## References

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* (2nd ed.) — <https://www.iso.org/standard/72089.html>
- Bill Wake, "INVEST in Good Stories, and SMART Tasks," 2003 (origin of INVEST) — <https://xp123.com/invest-in-good-stories-and-smart-tasks/>
- George T. Doran, "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives," *Management Review* 70(11): 35–36, 1981 (origin of SMART).
- Cucumber, Gherkin reference (Given/When/Then) — <https://cucumber.io/docs/gherkin/>
- Dai Clegg & Richard Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994 (origin of MoSCoW); stewarded by the DSDM / Agile Business Consortium.
- IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide)*, v3, 2015 — <https://www.iiba.org/>
- Robert B. Grady, *Practical Software Metrics for Project Management and Process Improvement*, Prentice Hall, 1992 (FURPS/FURPS+; originally Grady & Caswell, 1987).
