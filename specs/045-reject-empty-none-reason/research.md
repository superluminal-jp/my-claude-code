# Research: 空の「不要」理由を弾く(S3)

未解決の NEEDS CLARIFICATION は無い。

## R1. 定型句の判定方法

- **Decision**: 正規化(NFKC、大文字小文字の畳み込み、`<…>` と強調記号の除去、両端の空白・句読点・記号の除去)の後、(1) 空、(2) 英数字・かなを含まない、(3) 固定の一覧に一致、のいずれかなら定型句とする。
- **Rationale**: 一覧は小さく監査でき、決定的でテストしやすい。意味の妥当性(具体的に見えて無意味)は機械的に判定できないため、範囲外として限界に明記する。
- **Alternatives considered**: 文字数の下限(短くても具体的な理由 `comment only` を誤って弾く)。LLM による妥当性判定(非決定的でゲートに不向き)。設定で一覧を拡張(設定キーは範囲外)。

## R2. 不要宣言の行の解析

- **Decision**: 行頭(空白、引用 `>`、箇条書き `-`/`*`/`•`、強調 `*`/`_`、見出し `#` を許す)から `Documentation impact`、任意のコロン、強調記号、`none` の語境界の順に一致させ、その後ろの区切り(`—`、`–`、`-`、`:`、`：`)に続く部分を理由とする。区切りが無ければ理由は空。
- **Rationale**: 既存の単一行の書式(`Documentation impact: none — <reason>`)と、複数行の報告の見出し(`Documentation impact`)を区別でき、文中の言及を対象にしない。
- **Alternatives considered**: 行のどこにあっても一致させる(説明文中の引用を誤検出する)。

## R3. 「根拠」として認める行

- **Decision**: 文書の変更が無い場合の根拠は、内容のある `Updated:` 行、定型句でない理由の `No change needed:` 行、有効な不要宣言のいずれか。`No change needed:` の理由は、最初の `—` / `–` / 空白に挟まれた `-` より後ろ。区切りが無ければ行全体。
- **Rationale**: 仕様 FR-004 と既存の単一行の書式の両方を満たす。パスに含まれるハイフン(`my-file`)で誤って分割しない。
- **Alternatives considered**: `No change needed:` に区切りを必須にする(既存の書き方を不必要に厳しくする)。

## R4. 無効な不要宣言と根拠の欠落の重複報告

- **Decision**: 不要宣言が 1 つでもある場合は、無効なら問題 A のみを出し、根拠の欠落(問題 B)は出さない。不要宣言が 1 つも無く、見出しのみのときに問題 B を出す。
- **Rationale**: 同じ直し(理由を書く)を 2 回言わない。A を直せば B も満たされる。
- **Alternatives considered**: 両方を常に出す(冗長)。

## R5. 「実装系の変更」の範囲

- **Decision**: 既存の `REPORT_REQUIRED_FOR`(実装、仕様、設定、インフラ、決定)と同じ範囲を使い、新しい一覧は作らない。
- **Rationale**: 仕様の仮定。判定を一貫させる。
- **Alternatives considered**: 実装のみに限定する(設定やインフラの変更で空の報告が通る)。

## R6. 既存テストとの整合の事前確認

- **Decision**: 既存テストの最終メッセージ(`x`、`Done.`、`Implemented the feature.`、`Documentation impact: none — internal refactor.`、`Documentation impact\n- Updated: docs/guide.md`)は、本スライスの検査で結果が変わらない。
- **Rationale**: 見出しが無い場合は既存の「報告なし」の問題のまま。有効な不要宣言・文書の変更ありの報告は新しい問題を生まない。
