# コンテナ図: 蔵書予約システム

蔵書予約システムは、画面を出す Web アプリ、予約を受け付ける API、予約を保存するデータベース、お知らせを送るワーカーと、その依頼をためるキューの5つでできています。API が図書館業務システムに本の所在を問い合わせ、ワーカーがメール配信サービスにお知らせを頼みます。

```mermaid
flowchart LR
  accTitle: コンテナ図: 蔵書予約システム
  accDescr: 利用者と職員は Web アプリを使い、Web アプリは API を呼ぶ。API はデータベースに予約を保存し、図書館業務システムに所在を問い合わせ、お知らせの依頼をキューに積む。ワーカーがキューから依頼を取り出してメール配信サービスに送らせる。
  member(["利用者<br/>[Person]<br/>本を探して予約し、窓口で受け取る"]):::person
  librarian(["図書館職員<br/>[Person]<br/>予約された本を棚から取り置く"]):::person
  subgraph sys["蔵書予約システム [Software System]"]
    web["Web アプリ<br/>[Container: React]<br/>検索と予約の画面を出す"]:::container
    api["API<br/>[Container: Python / FastAPI]<br/>検索と予約を受け付ける"]:::container
    db[("予約データベース<br/>[Container: PostgreSQL]<br/>予約と取り置きの状態を保存する")]:::container
    queue[["お知らせキュー<br/>[Container: Redis]<br/>送るお知らせの依頼をためる"]]:::container
    worker["お知らせワーカー<br/>[Container: Python]<br/>依頼を取り出してメールを頼む"]:::container
  end
  ils["図書館業務システム<br/>[Software System: 外部]<br/>蔵書の目録と貸出を管理する"]:::external
  mail["メール配信サービス<br/>[Software System: 外部]<br/>メールを届ける"]:::external
  member -->|"本を探して予約する<br/>[HTTPS]"| web
  librarian -->|"取り置きの準備完了を登録する<br/>[HTTPS]"| web
  web -->|"検索と予約を送る<br/>[JSON/HTTPS]"| api
  api -->|"予約を読み書きする<br/>[SQL/TLS]"| db
  api -->|"本の所在と貸出状況を問い合わせる<br/>[REST/HTTPS]"| ils
  api -->|"お知らせの依頼を積む<br/>[Redis/TLS]"| queue
  worker -->|"お知らせの依頼を取り出す<br/>[Redis/TLS]"| queue
  worker -->|"お知らせメールの送信を頼む<br/>[SMTP/TLS]"| mail
  mail -->|"本の用意ができたことを知らせる"| member
  style sys fill:none,stroke:#808080,stroke-dasharray:6 4
  classDef person fill:#CFE0F3,stroke:#1F4E79,color:#0B1F33
  classDef container fill:#E8F1FB,stroke:#1F4E79,color:#0B1F33
  classDef external fill:#EDEDED,stroke:#4D4D4D,stroke-dasharray:5 3,color:#0B1F33
```

## 凡例

| 表記 | 意味 |
|---|---|
| 角の丸い横長の形、`[Person]` | 人。業務での役割で呼ぶ |
| 薄い青の四角、`[Container: 技術]` | システムの中で別々に動く部品(アプリやサービス) |
| 円柱 | データを保存する部品 |
| 両端に縦線のある四角 | 依頼をためておく部品(キュー) |
| 灰色の四角、点線の枠、`[Software System: 外部]` | 対象の外にあるシステム |
| 灰色の点線の大枠 | 蔵書予約システムの範囲 |
| 矢印 | 頼む側から頼まれる側への向き。ラベルは何をなぜ頼むか、角括弧は通信の方式 |

## 要素の一覧

| 名前 | 種類 | 役割 | 技術 | 根拠 |
|---|---|---|---|---|
| Web アプリ | Container | 利用者と職員に、検索・予約・取り置き登録の画面を出す | React | 作例の設定 |
| API | Container | 検索と予約を受け付け、所在の問い合わせとお知らせの依頼を行う | Python / FastAPI | 作例の設定 |
| 予約データベース | Container | 予約と取り置きの状態を保存する | PostgreSQL | 作例の設定 |
| お知らせキュー | Container | 送るべきお知らせの依頼を、ワーカーが取り出すまでためる | Redis | 作例の設定 |
| お知らせワーカー | Container | キューから依頼を取り出し、メール配信サービスに送信を頼む | Python | 作例の設定 |

用語: キュー(queue)は、依頼を受け取った順にためておき、別の部品が後から取り出して処理するための部品です。API はメールの送信を待たずに利用者へ応答できます。

## 前提と未確認の点

- 利用者と職員が同じ Web アプリを使う設定にしています。職員向けの画面が別のアプリかどうかは、この作例では決めていません。

## 関連する図

- 外側: [システムコンテキスト図](01-system-context.md)
- 流れ: [動的図: 本を予約する](03-dynamic-reservation.md)
- 配置: [デプロイ図: 本番環境](04-deployment.md)
