# Research: secure-logging

仕様に未解決の確認事項は無い。計画で決める点を記録する。

## 出典の確認(2026-10-17)

| 出典 | 確認内容 | 使い方 |
|---|---|---|
| OWASP Logging Cheat Sheet | 節構成と要件を一次情報から取得 | 主たる根拠。節名で引用する |
| OWASP ASVS 5.0.0 V16 | 要件 16.1.1〜16.5.4 の 17 件。16.5.4 のみ最上位レベル | 判定文の根拠。ASVS のサイトは 5.0.0 を「stable」と「bleeding edge」の両方で表示するため、版を明記する |
| OWASP Top 10:2025 A09 | 名称は Security Logging & Alerting Failures。対応する CWE は 117、221、223、532、778 | 背景。CWE-221、223 の本文は読んでいないので要件の根拠にしない |
| CWE-117、532、778、779 | 名称と説明を取得 | 指摘の分類。779 は A09 の対応一覧に無い |
| OWASP Logging Vocabulary | イベント名の接頭辞の方式 | 任意の語彙 |
| OpenTelemetry Logs Data Model | 状態は Stable。LogRecord のフィールド一覧 | 任意の形式の参考 |
| NIST SP 800-92 Rev.1 | 2023-10-11 の Initial Public Draft | 背景のみ。要件として引用しない |

## 決定

### D1: 検査の検証手段

- **Decision**: 契約テストは構造と出典の規則に限り、検査の挙動は検証用サンプルと手動手順で確認する。
- **Rationale**: 検査の挙動はモデルの振る舞いで、決定的なテストにならない。偽の自動化を作ると、確認していないことを確認済みに見せる。
- **Alternatives considered**: 振る舞い eval の追加(別スライスで足場が作られているが、費用上限の承認が必要なため今回は対象外)。

### D2: 除外した規格

- **Decision**: ISO/IEC 27002、PCI DSS、NIST SP 800-53 は含めない。
- **Rationale**: 一次情報を取得できず(403、目次のみ、民間ブログのみ)、確認なしに項番を載せると誤りを広める。
- **Alternatives considered**: 記憶に基づく項番の掲載(却下: 検証不能)。

### D3: 試作の扱い

- **Decision**: 試作を捨てず、FR ごとの差分表で保持・修正・追加に分ける。
- **Rationale**: 18 件の FR のうち 14 件は満たしており、作り直すと変更が大きくなる。誤りは 2 件、不足は 2 件と Edge Cases。
- **Alternatives considered**: 白紙から作り直す(却下: 変更が最小でない)。
