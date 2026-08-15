# templates/

Scrum Guide（2020年版）の作成物・イベントに対応する、記入してすぐ使えるMarkdownテンプレート。各ファイルは単体で完結しており、リポジトリ内の他ファイルへの相対リンクは持たない（出典はScrum Guide公式サイトへの直リンクと`[SG20, p.X]`のみ）。

内容の粒度はScrum Guideが明示する構造（定義・目的・タイムボックス・記入欄）のみで、進行手順やファシリテーション技法などGuideに明記のないHOW的内容は含まない。

配置は下記「運用の目安」の構造と対応させている：プロダクト単位で継続する作成物は`templates/`直下に、Sprintごとに作り直す作成物・イベントは`templates/sprint/`配下に置く。

## プロダクト単位で継続する作成物（`templates/`直下）

| ファイル | 対応する作成物 | 対応するコミットメント |
| --- | --- | --- |
| [product-backlog.md](product-backlog.md) | Product Backlog | Product Goal |
| [definition-of-done.md](definition-of-done.md) | （Incrementの品質基準） | Definition of Done |

## Sprintごとに作り直す作成物・イベント（`templates/sprint/`）

| ファイル | 対応する作成物・イベント |
| --- | --- |
| [sprint/sprint-backlog.md](sprint/sprint-backlog.md) | Sprint Backlog（コミットメント：Sprint Goal） |
| [sprint/increment.md](sprint/increment.md) | Increment |
| [sprint/sprint-planning.md](sprint/sprint-planning.md) | Sprint Planning |
| [sprint/daily-scrum.md](sprint/daily-scrum.md) | Daily Scrum |
| [sprint/sprint-review.md](sprint/sprint-review.md) | Sprint Review |
| [sprint/sprint-retrospective.md](sprint/sprint-retrospective.md) | Sprint Retrospective |

出典・引用ルールの詳細は[../sources.md](../sources.md)を参照。

## 運用の目安（Scrum Guideが規定しない運用上の慣例）

Scrum Guide自体はファイル・フォルダの構造を規定していない（ツール・フォーマットは意図的にフレームワークの範囲外とされている）。以下は、このテンプレート群を複数プロダクトにわたって使う場合の運用上の推奨であり、Guideの規範ではない。使用時は本ディレクトリのテンプレートを目的の場所へコピーし、コピー先で記入する（このディレクトリ自体は雛形として変更しない）。上記のディレクトリ構成はこの運用構造をそのまま反映している。

```text
scrum/
└── projects/
    └── <project_name>/
        ├── product-backlog.md      # product-backlog.md をコピー。継続的に更新する単一のファイル（Sprintごとに複製しない）
        ├── definition-of-done.md   # definition-of-done.md をコピー。プロダクト単位で継続的に更新する
        └── sprints/
            └── <sprint_num>-<date>/
                ├── sprint-backlog.md          # sprint/sprint-backlog.md を毎Sprint新規コピー
                ├── increment.md               # sprint/increment.md を毎Sprint新規コピー
                ├── sprint-planning.md
                ├── sprint-review.md
                └── sprint-retrospective.md
```

根拠：

- Product BacklogとSprint Backlogは、それぞれ「唯一（single）」であるとScrum.orgが明記しており（"There must be a single Product Backlog"／"There should be only one Sprint Backlog"）、Sprintごとに複製すると作成物の性質と矛盾する。Definition of Doneも品質基準としてプロダクト単位で継続するため、同じ扱いとする。
- `<sprint_num>-<date>`はこのリポジトリ自身の`specs/NNN-feature-name/`という命名パターンと同型。dateはSprint Planningの実施日（Sprint開始日）を使う。
- Daily Scrumは正式なコミットメントを持つ作成物ではなく短命な調整情報のため、ファイル化するかどうかはチームの判断に委ねる（アーカイブする価値は一般に低い）。`sprint/`に置いているのはSprintスコープであることを示すためで、必ず使うことを意味しない。
