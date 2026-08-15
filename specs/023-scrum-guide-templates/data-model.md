# Data Model: Scrum Guide 作成物・イベント テンプレート

本featureはランタイムのデータモデルを持たない。ここでは新規作成するテンプレートファイル（＝「エンティティ」）とその記入欄構成、および編集対象ファイルの一覧を記す。

## 新規テンプレートファイル（`.claude/skills/scrum-master/references/templates/`）

### 作成物テンプレート（3件）

| ファイル | 表す作成物 | 記入欄 | 対応するコミットメント（記入欄） | 出典 |
|---|---|---|---|---|
| `product-backlog.md` | Product Backlog（創発的で順序付けられたリスト） | item一覧：description／order／estimate／value | Product Goal（プロダクトの将来の状態） | [SG20, p.10-11] |
| `sprint-backlog.md` | Sprint Backlog（Sprint Goal＋選択したPBI＋計画） | 選択したProduct Backlog items一覧、Incrementを届ける計画 | Sprint Goal（Sprintの唯一の目的） | [SG20, p.9-11] |
| `increment.md` | Increment（Product Goalへの具体的な足がかり） | Incrementの説明、含まれるPBI | Definition of Done（品質基準を満たした状態の正式な記述） | [SG20, p.11-12] |

### イベントテンプレート（4件）

| ファイル | 表すイベント | 目的（記載） | タイムボックス（記載） | 検討内容の記入欄 | 出典 |
|---|---|---|---|---|---|
| `sprint-planning.md` | Sprint Planning | Sprintの起点、実行する作業の計画 | 1か月Sprintで最大8時間 | Why／What／Howの3つの問い | [SG20, p.8] |
| `daily-scrum.md` | Daily Scrum | Sprint Goalへの進捗の検査とSprint Backlogの適応 | 15分、毎日同じ時間・場所 | 今後の作業の調整 | [SG20, p.9] |
| `sprint-review.md` | Sprint Review | 成果の検査と今後の適応の決定（作業セッション、ステータス報告ではない） | 1か月Sprintで最大4時間 | 成果の提示、Product Goalへの進捗確認 | [SG20, p.9-10, p.12] |
| `sprint-retrospective.md` | Sprint Retrospective | 品質と効果を高める方法の計画 | 1か月Sprintで最大3時間 | 個人・相互作用・プロセス・ツール・Definition of Doneの検査 | [SG20, p.10] |

各テンプレートは、末尾に共通のフッター「出典：`[sources.md](../sources.md)`」を持つ。短いSprintではタイムボックスを比例して短縮する旨の注記（`scrum-framework.md`行67）は、イベント4テンプレート共通の注記として含める。

## 編集対象ファイル（新規作成ではない）

| ファイル | 変更内容 | 対応要件 |
|---|---|---|
| `.claude/skills/scrum-master/SKILL.md` | 「参照ファイル」表に、新規テンプレートディレクトリへのリンクを1行追加 | FR-011 |
| `README.md` | scrum-masterスキルのファイルツリー説明（283-285行目付近）に`templates/`を反映 | research.md Decision 2（Live Documentation） |

## 不変（このfeatureでは変更しない）

- `references/sources.md`、`references/scrum-framework.md`、`references/scrum-master-role.md` — テンプレートはこれらへの参照のみ持ち、内容は変更しない（FR-012）。
- `SKILL.md`の`when_to_use`・「必ず守る原則」・ワークフロー本文（spec.md Assumptions）。
- `docs/adr/0003-vendor-scrum-master-skill.md`（research.md Decision 4）。
