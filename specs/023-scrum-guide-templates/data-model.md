# Data Model: Scrum Guide 作成物・イベント テンプレート

本featureはランタイムのデータモデルを持たない。ここでは新規作成するテンプレートファイル（＝「エンティティ」）とその記入欄構成、および編集対象ファイルの一覧を記す。

## 新規テンプレートファイル（`.claude/skills/scrum-master/references/templates/`）

**実装後の訂正（ユーザー指示による再構成、2段階）**：当初は`templates/`直下にフラットな7ファイルとして配置した。1回目の訂正で「プロダクト単位で継続する作成物」と「Sprintごとに作り直す作成物・イベント」を`product/`・`sprint/`という並列サブディレクトリに分け、`increment.md`を`product/definition-of-done.md`（Definition of Doneのみ）と`sprint/increment.md`（Increment本体）に分割した。しかし運用構造（`scrum/projects/<project_name>/product-backlog.md` + `.../definition-of-done.md` + `.../sprints/<num>-<date>/`）ではプロダクト単位のファイルはプロジェクト直下に置かれ、Sprint単位のものだけがサブディレクトリに入るため、`product/`という並列フォルダは運用構造と食い違うと指摘を受けた。2回目の訂正で、プロダクト単位の2ファイルを`templates/`直下（`sprint/`と兄弟ではなく、`sprint/`を子に持つ側）へ移動し、運用構造とディレクトリ階層を一致させた。計8ファイルとなる。

### templates/直下（プロダクト単位で継続、2件）

| ファイル | 表す作成物 | 記入欄 | 対応するコミットメント（記入欄） | 出典 |
|---|---|---|---|---|
| `product-backlog.md` | Product Backlog（創発的で順序付けられたリスト） | item一覧：description／order／estimate／value | Product Goal（プロダクトの将来の状態） | [SG20, p.10-11] |
| `definition-of-done.md` | （Incrementの品質基準） | Definition of Doneの記入欄 | Definition of Done（品質基準を満たした状態の正式な記述） | [SG20, p.12] |

### templates/sprint/（Sprintごとに作り直す、6件）

| ファイル | 表す作成物・イベント | 記入欄 | 出典 |
|---|---|---|---|
| `sprint/sprint-backlog.md` | Sprint Backlog（コミットメント：Sprint Goal） | 選択したProduct Backlog items一覧、Incrementを届ける計画 | [SG20, p.9-11] |
| `sprint/increment.md` | Increment（Product Goalへの具体的な足がかり） | Incrementの説明、含まれるPBI | [SG20, p.11-12] |
| `sprint/sprint-planning.md` | Sprint Planning（目的：Sprintの起点、実行する作業の計画。タイムボックス：1か月Sprintで最大8時間） | Why／What／Howの3つの問い | [SG20, p.8] |
| `sprint/daily-scrum.md` | Daily Scrum（目的：進捗の検査とSprint Backlogの適応。タイムボックス：15分） | 今後の作業の調整 | [SG20, p.9] |
| `sprint/sprint-review.md` | Sprint Review（目的：成果の検査と今後の適応の決定、作業セッション。タイムボックス：1か月Sprintで最大4時間） | 成果の提示、Product Goalへの進捗確認 | [SG20, p.9-10, p.12] |
| `sprint/sprint-retrospective.md` | Sprint Retrospective（目的：品質と効果を高める方法の計画。タイムボックス：1か月Sprintで最大3時間） | 個人・相互作用・プロセス・ツール・Definition of Doneの検査 | [SG20, p.10] |

各テンプレートは、冒頭に共通の出典行「出典：_The Scrum Guide_（Ken Schwaber and Jeff Sutherland、2020年11月）+ scrumguides.orgへの直リンク + `[SG20, p.X]`」を持つ。テンプレートは単体で完結させるため、リポジトリ内ファイルへの相対リンクは含まない（`sprint/increment.md`が`definition-of-done.md`を参照する箇所も、リンクではなくプレーンテキストの説明にとどめる）。短いSprintではタイムボックスを比例して短縮する旨の注記（`scrum-framework.md`行67）は、イベント4テンプレート共通の注記として含める。

## 編集対象ファイル（新規作成ではない）

| ファイル | 変更内容 | 対応要件 |
|---|---|---|
| `.claude/skills/scrum-master/SKILL.md` | 「参照ファイル」表に、新規テンプレートディレクトリへのリンクを1行追加 | FR-011 |
| `README.md` | scrum-masterスキルのファイルツリー説明（283-285行目付近）に`templates/`を反映 | research.md Decision 2（Live Documentation） |

## 不変（このfeatureでは変更しない）

- `references/sources.md`、`references/scrum-framework.md`、`references/scrum-master-role.md` — テンプレートはこれらへの参照のみ持ち、内容は変更しない（FR-012）。
- `SKILL.md`の`when_to_use`・「必ず守る原則」・ワークフロー本文（spec.md Assumptions）。
- `docs/adr/0003-vendor-scrum-master-skill.md`（research.md Decision 4）。
