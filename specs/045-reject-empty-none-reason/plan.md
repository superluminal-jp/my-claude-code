# Implementation Plan: 空の「不要」理由を弾く(スライス S3)

**Branch**: `045-reject-empty-none-reason` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/045-reject-empty-none-reason/spec.md`(権威: [meta-spec.md](../043-related-doc-discovery/meta-spec.md)、契約 C2 の理由の文法)

## Summary

`stop_gate.py` に、完了報告の質を検査する純粋関数(理由の正規化と定型句判定、不要宣言・`Updated:`・`No change needed:` 行の解析)と、`evaluate()` からの呼び出しを追加する。(a) `Documentation impact: none` の理由が空・定型句なら常に問題、(b) 完了報告が必要で文書の変更がゼロなら、更新内容または具体的な変更不要の理由を必須にする。`common.py` は変更しない。

## Technical Context

**Language/Version**: Python 3.9 以上(標準ライブラリのみ: `re`、`unicodedata`)

**Primary Dependencies**: なし。既存の `stop_gate.evaluate()`(`changes`、`categories`、`REPORT_MARKER`、`REPORT_REQUIRED_FOR`)を拡張する

**Storage**: なし

**Testing**: `unittest`(`tests/test_scripts.py`)。純粋関数は `import stop_gate` で直接、ゲートの統合は既存の `StopGateTests.hook` を使う

**Target Platform**: macOS / Linux(既存のスキルと同じ)

**Project Type**: CLI スクリプト群を持つスキル(単一プロジェクト)

**Performance Goals**: 最終メッセージの正規表現走査のみ。ゲートのタイムアウト 30 秒に影響しない

**Constraints**: 読み取り専用、`common.py` 無変更、既存 90 件のテストを維持、S1 の「未処分の候補」の検査を壊さない

**Scale/Scope**: 最終メッセージは数 KB 規模。定型句の一覧は固定(設定キーは範囲外)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入のテンプレートで、適用される制約はない。代わりに CLAUDE.md とグローバル規則を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: `stop_gate.py` と `tests/test_scripts.py` のみ。設定・SKILL.md・README は範囲外 |
| 失敗するチェックを先に用意 | 合格: 下記「テスト先行」 |
| 契約の同期 | 合格(予定): 報告の文法は C2 の `contracts/report-grammar.md` に記録。SKILL.md の文言の同期は S4、README は S6 |
| 既存挙動の維持 | 合格(予定): 既存の単一行・複数行の報告で、既存 90 件が通ることを確認 |

設計後の再確認: 上記のままで違反なし。複雑さの追跡は不要。

## Project Structure

### Documentation (this feature)

```text
specs/045-reject-empty-none-reason/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/report-grammar.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks で作成
```

### Source Code (repository root)

```text
.claude/skills/maintaining-living-documentation/
├── scripts/stop_gate.py     # 変更: 理由の判定、行の解析、evaluate() への検査の追加
└── tests/test_scripts.py    # 変更: ReportQualityTests(純粋関数)と StopGateTests への統合テストを追加
```

**Structure Decision**: 新しいファイルは作らない。判定は `stop_gate.py` の純粋関数にまとめ、ゲートの既存の流れ(`evaluate()` → `on_stop`)に乗せる。

## 設計の要点

1. **純粋関数**(すべて `stop_gate.py`)
   - `normalize_reason(text) -> str`: Unicode 互換正規化(NFKC)、大文字小文字の畳み込み、`<…>` のテンプレート表記の除去、強調記号の除去、両端の空白・句読点・記号(Unicode カテゴリ P*/S*/Z*)の除去
   - `is_boilerplate(text) -> bool`: 正規化後に空、英数字・かなを 1 文字も含まない、または固定の一覧(`BOILERPLATE_REASONS`)に一致
   - `none_declarations(message) -> list[str]`: 行頭(箇条書き・引用・強調の記号を許す)の `Documentation impact: none` の理由の一覧。`none` の後ろの区切り(`—`、`–`、`-`、`:`、全角コロン)に続く部分が理由。区切りが無い場合は空文字列
   - `report_lines(message) -> tuple[list[str], list[str]]`: `Updated:` 行の内容の一覧と、`No change needed:` 行の理由(最初の `—` / `–` / 空白に挟まれた `-` より後ろ。区切りが無ければ行全体)の一覧
2. **`report_quality_problems(message, needs_report, docs_changed) -> list[str]`**
   - 無効な不要宣言が 1 つでもあれば問題 A(文書の変更の有無によらず)
   - 完了報告が必要(`needs_report` が空でない)で、見出し(`REPORT_MARKER`)があり、文書の変更が無く、不要宣言が 1 つも無いときに限り、有効な根拠(内容のある `Updated:`、定型句でない理由の `No change needed:`)が無ければ問題 B。有効な不要宣言が根拠になる
3. **`evaluate()`**: 既存の「見出しが無い」問題の後、S1 の `unaddressed_related` の前に `report_quality_problems` を呼ぶ。`last_message is None` なら呼ばない。`docs_changed` は既存の `categories` に `documentation` が含まれるかで求める
4. **強制の度合い・回数・再入**: `on_stop` は変更しない。問題は既存と同じ `problems` に加わり、1 回のブロックに並ぶ(S1 の問題とも同居する)

## テスト先行(実装前に書く、失敗を確認するテスト)

**ReportQualityTests**(新しいクラス。`import stop_gate` の純粋関数。表形式は `subTest`)

| ID | 検証 | 対応 |
|---|---|---|
| R1 | 定型句の表がすべて `is_boilerplate == True`: 空、空白のみ、`n/a`、`N/A`、`na`、`none`、`nil`、`no`、`nothing`、`no impact`、`No changes.`、`not applicable`、`なし`、`なし。`、`無し`、`該当なし`、`変更なし`、`影響なし`、`-`、`—`、`...`、`<reason>`、`<what is unchanged and why>`、全角の `ＮＯＮＥ` | FR-001, FR-002, SC-001 |
| R2 | 具体的な理由の表がすべて `False`: `internal refactor`、`comment only`(短くても可)、`内部の変数名のみの変更で公開される挙動は不変`、`no behavior change: only renames a private helper` | FR-003, SC-001 |
| R3 | `none_declarations`: 区切り 4 種と全角コロン、箇条書き・強調・引用の接頭辞、大文字小文字、複数行(順序どおり)、区切りなし → 空文字列、文中(行頭でない)の言及は対象外 | FR-001, エッジケース |
| R4 | `report_lines`: `Updated:`(接頭辞あり・なし、内容が空)、`No change needed: <area> — <reason>`、区切りなしの行全体、テンプレート表記のまま | FR-004 |

**StopGateTests への統合**(S1 の `add_src_tree` とは別に、実装系の変更だけがある既存のリポジトリを使う)

| ID | 検証 | 対応 |
|---|---|---|
| G1 | `Documentation impact: none —`(理由なし)で `block`、理由に直し方(`reason`)が含まれる | US1-1, FR-006 |
| G2 | 定型句の理由(`n/a`、`なし。`)で `block` | US1-2 |
| G3 | 具体的な理由(英語・日本語)で通る | US1-3 |
| G4 | 見出しのみの報告 + 実装系の変更のみ → `block` | US2-1 |
| G5 | 見出しのみの報告 + 文書も変更 → 通る | US2-5 |
| G6 | `Updated:` 行で通る。`No change needed: x — <具体的な理由>` で通る。`No change needed: x — n/a` で `block` | US2-2〜4 |
| G7 | 複数行の報告(`Updated` / `No change needed` / `Unresolved` / `Proposed decision record` / `Checks`)が具体的な内容で通る | US2-6, FR-007 |
| G8 | 文書が変更されていても、無効な不要宣言は `block`。複数の不要宣言のうち 1 つでも無効なら `block` | FR-001, FR-005, エッジケース |
| G9 | `warn` は `systemMessage` のみ、`off` は何も出さない | US1-4 |
| G10 | 同じ状態の最大 2 回のブロック、`stop_hook_active` の再入でブロックしない | FR-007, SC-004 |
| G11 | S1 の「未処分の候補」の問題と同時に発生した場合、1 回のブロックの `reason` に両方が含まれる | エッジケース |
| G12 | `last_assistant_message` が無いと、この検査は行われない | エッジケース |

既存の `test_report_satisfies_the_gate`(`none — internal refactor.`)と `test_broken_link_in_changed_docs_is_blocked_even_with_report` は変更なしで通る必要がある。

## 実装の順序

1. R1〜R4 と G1〜G12 を追加し、失敗を記録する
2. 純粋関数を実装し、R1〜R4 を通す
3. `report_quality_problems` と `evaluate()` の呼び出しを実装し、G1〜G12 と既存の全テストを通す
4. 全体(既存 90 件を含む)、`check_links.py --changed`、`quickstart.md` を実行する

## リスクと分岐

- **意味の妥当性は検査できない**: 具体的に見えて無意味な理由(例: `その他の理由`)は通る。限界として S6 の README に記載する
- **過検出**: 一覧にない定型句は通り、反対に具体的だが短い理由が誤って弾かれることはない(一覧は固定の語のみ)。誤検出の報告があれば一覧を見直す
- **既存の報告の書式への影響**: 既存の単一行・複数行の書式は G3・G7 と既存テストで固定する
- **B2 との関係**: S1 の「パスの言及で処分済み」の限界は、本スライスでも変わらない(理由の質は検査するが、意味の妥当性は検査しない)

## Complexity Tracking

違反なし。記入不要。
