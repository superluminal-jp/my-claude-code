# Data Model: secure-logging

スキルは永続データを持たない。ここでは、チェックリストと検査報告が扱う概念の形を定める。

## チェックリスト項目

| 属性 | 内容 | 規則 |
|---|---|---|
| id | `LOG-<群>-<番号>`(例: `LOG-INJ-1`) | 一意。群は INV、EVT、ATT、DATA、INJ、ERR、CFG、TST、OPS |
| requirement | 要件の文 | 1 項目 1 要件 |
| group | A(コードで検証)または B(コードでは検証不能) | OPS は B |
| basis | 出典名と節または要件ID | 1 件以上。確認済みの一次情報に限る |

## 判定

| 属性 | 内容 | 規則 |
|---|---|---|
| item | チェックリスト項目の id | |
| status | Pass、Fail、N/A、Unverified | group B は、リポジトリ内の設定が根拠になる場合を除き Pass にならない |
| evidence | `file:line` またはテスト、または理由 | Pass と Fail は場所が必須。N/A と Unverified は理由が必須 |

状態の遷移はなく、1 回の検査ごとに独立する。

## 一次情報

| 属性 | 内容 |
|---|---|
| name | 出典名 |
| version | 版または状態(例: ASVS 5.0.0、NIST 草案) |
| verified_on | 確認日(2026-10-17) |
| role | 要件の根拠、または背景のみ |

## 検査報告

| 属性 | 内容 |
|---|---|
| verdict | 不合格と未検証の件数、重大なもの |
| assessments | 判定の一覧(チェックリストの順) |
| changes | 実装モードで行った変更と、実行したテストの結果 |
| evidence_needed | 利用者が用意すべき運用側の証拠 |
| not_checked | 未検査の範囲 |
