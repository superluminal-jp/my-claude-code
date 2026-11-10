# 動的図: 本を予約する

利用者が本を予約すると、API はまず図書館業務システムに所在と貸出状況を確かめ、予約をデータベースに保存してから予約番号を返します(手順 1〜12)。受付のお知らせメールは、その後にワーカーが別に送ります(手順 13〜14)。そのため、メールの遅れで画面が待たされることはありません。

```mermaid
sequenceDiagram
  accTitle: 動的図: 本を予約する
  accDescr: 利用者が検索して予約すると、API が所在を確かめ、予約を保存し、予約番号を返す。受付メールはワーカーが後からキューの依頼を取り出して送らせる。
  autonumber
  actor member as 利用者 [Person]
  participant web as Web アプリ [Container: React]
  participant api as API [Container: Python / FastAPI]
  participant ils as 図書館業務システム [Software System: 外部]
  participant db as 予約データベース [Container: PostgreSQL]
  participant queue as お知らせキュー [Container: Redis]
  participant worker as お知らせワーカー [Container: Python]
  participant mail as メール配信サービス [Software System: 外部]
  member->>web: 書名で本を検索する
  web->>api: 検索を送る [JSON/HTTPS]
  api->>ils: 所在と貸出状況を問い合わせる [REST/HTTPS]
  ils-->>api: 所蔵館と貸出状況を返す
  api-->>web: 検索結果を返す
  web-->>member: 予約できる本を表示する
  member->>web: 「予約する」を押す
  web->>api: 予約を送る [JSON/HTTPS]
  api->>db: 予約を保存する [SQL/TLS]
  api->>queue: 受付メールの依頼を積む [Redis/TLS]
  api-->>web: 予約番号を返す
  web-->>member: 予約番号を表示する
  worker->>queue: 依頼を取り出す [Redis/TLS]
  worker->>mail: 受付メールの送信を頼む [SMTP/TLS]
```

## 凡例

| 表記 | 意味 |
|---|---|
| 人の形、`[Person]` | 人 |
| 上下の箱と縦の点線 | 流れに加わる部品。角括弧は種類と技術 |
| 実線の矢印 | 依頼 |
| 点線の矢印 | 依頼への応答 |
| 矢印の番号 | 起きる順番 |

## 要素の一覧

この図に出る部品は、[コンテナ図](02-containers.md)の要素と同じものです。新しい部品はありません。

## 前提と未確認の点

- 本が貸出中のときに順番待ちの予約を受け付けるかどうかは、この流れに含めていません。受け付けるなら、別の動的図にします。

## 関連する図

- 部品の全体: [コンテナ図](02-containers.md)
- 一覧: [構成図の一覧](README.md)
