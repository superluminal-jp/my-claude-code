# Implementation Plan: 層・配置・近接性の実践を文書化する(スライス S5)

**Branch**: `046-layers-placement-proximity` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/046-layers-placement-proximity/spec.md`(権威: [meta-spec.md](../043-related-doc-discovery/meta-spec.md)、契約 C4)

## Summary

`references/practices.md` に「Layers, placement, and proximity」の節を追加し、`references/bibliography.bib` に確認済みの出典 4 件を追加し、書誌キーの整合と節の必須要素を確認するテストを 1 クラス追加する。文書のみのスライスで、スクリプトは変更しない。

## Technical Context

**Language/Version**: Markdown と BibTeX(テストは Python 3.9 以上の標準ライブラリ)

**Primary Dependencies**: なし

**Storage**: なし

**Testing**: `unittest`(`tests/test_scripts.py` に `PracticesDocumentTests` を追加)と `check_links.py --changed`

**Target Platform**: リポジトリ内のスキル文書

**Project Type**: スキルの参照文書

**Performance Goals**: 該当なし

**Constraints**: 既存の節を変更しない(FR-009)。出典は確認済みのものだけ。`common.py`・スクリプトは無変更。既存 109 件を維持

**Scale/Scope**: 節 1 つ、書誌エントリ 4 つ、テストクラス 1 つ

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレートで、適用される制約はない。CLAUDE.md とグローバル規則(最小変更、変更前の失敗するチェック、確認していない事実を書かない)を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: `practices.md`・`bibliography.bib`・テストのみ |
| 失敗するチェックを先に用意 | 合格: `PracticesDocumentTests` を先に書き、失敗を記録する |
| 確認していない事実を書かない | 合格: 書誌情報は公式ページで確認した範囲のみ。確認できなかった項目は省く |
| 既存の記述の保全 | 合格: 新しい節の挿入のみ |

## 設計の要点

1. **節の位置**: 既存の「Decision records」の後、「Evidence and uncertainty」の前に挿入する。
2. **節の構成**: 導入(根拠の種別の説明)→ 層の表(列: Layer / Reader's question / Placement / Form / Basis。Basis は `Sourced [...]` または `Design decision` で始める)→ コメントの 2 分類 → 置き場所のパターン → 近接性(設計判断)と階層についての注記。
3. **書誌エントリ**(確認できた情報のみ):
   - `GoogleSWE2020`: Software Engineering at Google の 10 章「Documentation」(著者 Tom Manshreck、本の編者は Titus Winters・Tom Manshreck・Hyrum Wright、2020 年 3 月刊、出版社は公式ページに記載がないため記載しない)
   - `PEP8`: PEP 8 – Style Guide for Python Code(Guido van Rossum、Barry Warsaw、Alyssa Coghlan、作成 2001-07-05)
   - `LinuxKernelStyle`: Linux kernel coding style、8 節「Commenting」(著者の記載なし)
   - `Diataxis`: Diátaxis(著者の記載なし)
4. **テスト `PracticesDocumentTests`**:
   - P1 節 `## Layers, placement, and proximity` が存在し、層の表に 9 層がそろい、各行が 5 列で Basis が `Sourced` または `Design decision` で始まる
   - P2 引用された書誌キー(`[Key]` と `[Key; Key]` の形。`(` が続くリンクは除く)がすべて `bibliography.bib` に存在し、新しい 4 キーがすべて引用されている
   - P3 P0〜P4 と README(P1)が設計判断と明記され、「No source reviewed presents a single hierarchy」の文がある

## テスト先行

`PracticesDocumentTests` の 3 メソッド(P1〜P3)を先に追加し、節が無い状態で失敗することを記録する。その後、`bibliography.bib`、`practices.md` の順に変更して通す。

## リスクと分岐

- **書誌情報の誤り**: 確認できなかった項目は書かない。出版社を書かないなどの欠落は許容する。
- **出典の言い回しの引用**: 要約で書き、長い引用をしない。
- **既存の記述との矛盾**: 見つけた場合は変更せずに報告する。

## Complexity Tracking

違反なし。
