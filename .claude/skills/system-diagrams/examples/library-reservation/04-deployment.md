# デプロイ図: 蔵書予約システム、本番環境

本番環境では、API とお知らせワーカーがコンテナ実行基盤(Kubernetes)で動き、予約データベースとお知らせキューはクラウドのマネージドサービスにあります。Web アプリは利用者と職員のブラウザで動き、図書館業務システムは図書館のデータセンターに置かれたままです。

```mermaid
flowchart LR
  accTitle: デプロイ図: 蔵書予約システム、本番環境
  accDescr: ブラウザで動く Web アプリが本番環境の API を呼ぶ。API とワーカーは Kubernetes で動き、マネージドの PostgreSQL と Redis を使う。API は VPN 経由で図書館のデータセンターにある業務システムに問い合わせる。
  subgraph browser["利用者と職員のブラウザ [Deployment Node: Web ブラウザ]"]
    web["Web アプリ<br/>[Container: React]<br/>検索と予約の画面を出す"]:::container
  end
  subgraph prod["本番環境 [Deployment Environment]"]
    subgraph cluster["アプリケーション実行基盤 [Deployment Node: Kubernetes]"]
      api["API<br/>[Container: Python / FastAPI]<br/>検索と予約を受け付ける、3 台で動く"]:::container
      worker["お知らせワーカー<br/>[Container: Python]<br/>依頼を取り出してメールを頼む、1 台で動く"]:::container
    end
    subgraph pg["マネージドデータベース [Deployment Node: PostgreSQL 16]"]
      db[("予約データベース<br/>[Container: PostgreSQL]<br/>予約と取り置きの状態を保存する")]:::container
    end
    subgraph redis["マネージドキャッシュ [Deployment Node: Redis 7]"]
      queue[["お知らせキュー<br/>[Container: Redis]<br/>送るお知らせの依頼をためる"]]:::container
    end
  end
  subgraph library["図書館のデータセンター [Deployment Node: オンプレミス]"]
    ils["図書館業務システム<br/>[Software System: 外部]<br/>蔵書の目録と貸出を管理する"]:::external
  end
  mail["メール配信サービス<br/>[Software System: 外部]<br/>メールを届ける"]:::external
  web -->|"検索と予約を送る<br/>[JSON/HTTPS]"| api
  api -->|"予約を読み書きする<br/>[SQL/TLS]"| db
  api -->|"お知らせの依頼を積む<br/>[Redis/TLS]"| queue
  worker -->|"お知らせの依頼を取り出す<br/>[Redis/TLS]"| queue
  api -->|"本の所在と貸出状況を問い合わせる<br/>[REST/HTTPS、VPN 経由]"| ils
  worker -->|"お知らせメールの送信を頼む<br/>[SMTP/TLS]"| mail
  style browser fill:none,stroke:#808080,stroke-dasharray:6 4
  style prod fill:none,stroke:#808080,stroke-dasharray:6 4
  style cluster fill:none,stroke:#808080,stroke-dasharray:6 4
  style pg fill:none,stroke:#808080,stroke-dasharray:6 4
  style redis fill:none,stroke:#808080,stroke-dasharray:6 4
  style library fill:none,stroke:#808080,stroke-dasharray:6 4
  classDef container fill:#E8F1FB,stroke:#1F4E79,color:#0B1F33
  classDef external fill:#EDEDED,stroke:#4D4D4D,stroke-dasharray:5 3,color:#0B1F33
```

## 凡例

| 表記 | 意味 |
|---|---|
| 灰色の点線の大枠、`[Deployment Node: 技術]` | 部品が動く場所(ブラウザ、実行基盤、マネージドサービス、データセンター)。枠の中の枠は、その場所の中の場所 |
| 薄い青の四角、`[Container: 技術]` | そこで動く部品。名前はコンテナ図と同じ |
| 円柱 | データを保存する部品 |
| 両端に縦線のある四角 | 依頼をためておく部品(キュー) |
| 灰色の四角、点線の枠、`[Software System: 外部]` | 対象の外にあるシステム |
| 矢印 | 通信を始める側から受ける側への向き。角括弧は通信の方式 |

## 要素の一覧

| 名前 | 種類 | 役割 | 技術 | 根拠 |
|---|---|---|---|---|
| 利用者と職員のブラウザ | Deployment Node | Web アプリを動かす | Web ブラウザ | 作例の設定 |
| 本番環境 | Deployment Environment | 利用者に提供している環境 | — | 作例の設定 |
| アプリケーション実行基盤 | Deployment Node | API とワーカーのコンテナを動かす | Kubernetes | 作例の設定 |
| マネージドデータベース | Deployment Node | 予約データベースを動かす | PostgreSQL 16 | 作例の設定 |
| マネージドキャッシュ | Deployment Node | お知らせキューを動かす | Redis 7 | 作例の設定 |
| 図書館のデータセンター | Deployment Node | 図書館業務システムを置いている | オンプレミス | 作例の設定 |

用語: マネージドサービスは、クラウド事業者が運用(更新、バックアップ、障害時の切り替え)を引き受けるサービスです。VPN は、離れた拠点の間を暗号化された専用の経路で結ぶ仕組みです。

## 前提と未確認の点

- Web アプリの画面ファイルをどこから配っているか(静的ホスティングや CDN)は、この作例では省いています。
- 検証環境は描いていません。必要なら、環境ごとに1枚描きます。

## 関連する図

- 部品の全体: [コンテナ図](02-containers.md)
- 一覧: [構成図の一覧](README.md)
