# 配置の決まりと検査の規則

## 目次

- [Scrum Guide が定めること](#scrum-guide-が定めること)
- [このスキルの運用上の決まり](#このスキルの運用上の決まり)
- [どのファイルに何を書くか](#どのファイルに何を書くか)
- [検査の規則](#検査の規則)
- [雛形](#雛形)

## Scrum Guide が定めること

出典は Scrum Guide（2020年版）だけである。ページ番号は英語版による。

- 作成物は3つで、それぞれにコミットメントがある: Product Backlog と Product Goal、Sprint Backlog と Sprint Goal、Increment と Definition of Done。[SG20, p.10-12]
- Product Backlog は、プロダクトの改善に必要なものの、創発的で順序付けられた一覧であり、Scrum Team が行う作業の唯一の情報源である。[SG20, p.10]
- Sprint Backlog は、Sprint Goal、その Sprint に選択した Product Backlog items、Increment を届けるための実行可能な計画で構成される、Developers による Developers のための計画である。[SG20, p.11]
- Product Backlog item は、Definition of Done を満たしたときに Increment になる。[SG20, p.12]

## このスキルの運用上の決まり

Scrum Guide は、フォルダの構造、ファイルの名前、道具を定めない。以下は Scrum の規則ではなく、このスキルの決まりである。

```text
<プロダクトのフォルダ>/
└── scrum/
    ├── README.md               # 作成物とファイルの対応、アカウンタビリティの記入欄
    ├── product-backlog.md      # Product Backlog と Product Goal。プロダクトに1つ
    ├── definition-of-done.md   # Definition of Done。プロダクトに1つ
    └── sprints/
        └── <3桁の番号>-<開始日 YYYY-MM-DD>/
            ├── sprint-backlog.md        # Sprint Backlog と Sprint Goal
            ├── increment.md             # Increment（Pull Request・リリース・コミットへのリンク）
            ├── sprint-planning.md
            ├── sprint-review.md
            ├── sprint-retrospective.md
            └── daily-scrum.md           # 頼まれたときだけ置く
```

- **プロダクトのフォルダごとに1つの `scrum/` を置く。** 1つのリポジトリに1つのプロダクトなら、リポジトリのルートがプロダクトのフォルダである。作成物をプロダクトのコードと同じ場所に置き、プロダクトごとに1つの Product Backlog を保つためである。
- **`product-backlog.md` と `definition-of-done.md` は Sprint ごとに複製しない。** Product Backlog は作業の唯一の情報源であり [SG20, p.10]、複製すると2つの順序ができる。Definition of Done も同じ扱いにする。
- **Sprint のフォルダの番号は 001 から1ずつ増やし、日付は Sprint の開始日にする。** 名前の順が Sprint の順になる。
- **`sprints/` は最初の Sprint を足すときにできる。** Git は空のフォルダを保たない。
- **Daily Scrum の記録は既定では置かない。** Daily Scrum はコミットメントを持つ作成物ではない。残すかどうかは Developers が決める。
- **作業の単位（Issue、Pull Request）と Increment の実体はこのフォルダに写さない。** リンクで指す。写しは元と食い違う。

## どのファイルに何を書くか

| チームが決めたこと | 書く場所 | 決める人 |
| --- | --- | --- |
| Product Goal | `product-backlog.md` の `- **Product Goal**：` | Product Owner が作成し、明示的に伝える [SG20, p.6] |
| Product Backlog items と並び順 | `product-backlog.md` の表。上の行ほど順序が先 | Product Owner [SG20, p.5-6] |
| 項目の大きさ（見積もり） | `product-backlog.md` の表の Estimate | 作業を行う Developers [SG20, p.11] |
| Definition of Done | `definition-of-done.md` の `- **Definition of Done**：`。欄の次の行から字下げした箇条書きで書ける | 組織の基準がなければ Scrum Team [SG20, p.12] |
| Sprint Goal | その Sprint の `sprint-backlog.md` の `- **Sprint Goal**：` | Scrum Team が Sprint Planning で定める [SG20, p.8] |
| Sprint に選択した項目と計画 | その Sprint の `sprint-backlog.md` | Developers [SG20, p.8, p.11] |
| Increment | その Sprint の `increment.md`。実体へのリンクを書く | Definition of Done を満たしたものだけが Increment である [SG20, p.12] |
| アカウンタビリティを担う人 | `README.md` の「アカウンタビリティ」 | チーム |

## 検査の規則

`scripts/check_artifacts.py` は形だけを見る。エラーが1件でもあれば終了コード 1、なければ 0、プロダクトを検査できなければ 2 を返す。`--format json` は `product`、`errors`、`warnings` を持つ1つのオブジェクトを出し、各項目は `rule`、`path`（プロダクトのフォルダからの相対パス）、`message` を持つ。

| 規則 | エラーになるとき |
| --- | --- |
| SA-01 | `scrum/product-backlog.md` がない |
| SA-02 | `scrum/definition-of-done.md` がない |
| SA-03 | `scrum/` の下に、2つ目の `product-backlog.md` または `definition-of-done.md` がある |
| SA-04 | `scrum/sprints/` の直下のフォルダの名前が `<3桁の番号>-<実在する日付 YYYY-MM-DD>` でない |
| SA-05 | 2つの Sprint のフォルダが同じ番号を持つ |
| SA-06 | Sprint のフォルダに `sprint-backlog.md` がない |
| SA-07 | Sprint の開始日が、1つ前の番号の Sprint の開始日より後でない |

| 規則 | 警告になるとき（終了コードは変わらない） |
| --- | --- |
| SW-01 | `product-backlog.md` の Product Goal の欄が空 |
| SW-02 | `definition-of-done.md` の Definition of Done の欄が空 |
| SW-03 | Sprint の `sprint-backlog.md` の Sprint Goal の欄が空 |

欄は `- **<名前>**：` の行で、同じ行に値があるか、次の空でない行が字下げされていれば、書かれているとみなす。欄の行そのものを消すと、警告が出る。

検査が見ないもの: Product Backlog の順序が Product Goal に合っているか。Increment が Definition of Done を満たすか。Sprint の長さが1か月以内で一定か。書かれた値が本当にチームの決定か。

`scripts/scaffold.py` は、すでに在るファイルを書き換えず、`kept` として報告する。`--product` は `--root` からの相対パスで、シンボリックリンクをたどった先がルートの中になければ拒む（終了コード 2）。拒んだときは何も書かない。

## 雛形

`templates/` の雛形は、Scrum Guide が明示する構造（定義、目的、タイムボックス、記入欄）だけを持ち、進行の手順や技法は含まない。各ファイルは単体で完結し、出典として Scrum Guide の公式サイトへのリンクと `[SG20, p.X]` を持つ。

| 雛形 | 置かれる場所 | 対応する作成物・イベント |
| --- | --- | --- |
| `templates/scrum-readme.md` | `scrum/README.md` | （索引） |
| `templates/product-backlog.md` | `scrum/product-backlog.md` | Product Backlog（Product Goal） |
| `templates/definition-of-done.md` | `scrum/definition-of-done.md` | Definition of Done |
| `templates/sprint/sprint-backlog.md` | Sprint のフォルダ | Sprint Backlog（Sprint Goal） |
| `templates/sprint/increment.md` | Sprint のフォルダ | Increment |
| `templates/sprint/sprint-planning.md` | Sprint のフォルダ | Sprint Planning |
| `templates/sprint/sprint-review.md` | Sprint のフォルダ | Sprint Review |
| `templates/sprint/sprint-retrospective.md` | Sprint のフォルダ | Sprint Retrospective |
| `templates/sprint/daily-scrum.md` | Sprint のフォルダ（`--daily` のとき） | Daily Scrum |
