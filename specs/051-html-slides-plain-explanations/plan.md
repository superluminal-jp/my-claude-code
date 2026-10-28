# Implementation Plan: HTML専用のDADSスライドと、初学者が追える説明

**Branch**: `claude/digital-agency-slide-skill-vqe5ky` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

`digital-agency-slides` から PowerPoint 変換を取り除き、HTMLデッキそのものを成果物とする。変換のために置いていた制約(擬似要素の禁止、`data-pptx`、px/pt/EMU の換算、`sld-*` による見出しの再実装)を外し、DADSの見出し・説明リスト・リンク・チップラベルを公開どおりに使う。構成の指針を「前提 → 結論 → 論点の木」に改め、枚数の上限を木から導き、`lint` に構成の警告を加える。あわせて、常時ロードの読み手向け構造の規則と Claude.ai 用の移植プロンプトに、前提と用語の提示、比喩の禁止を加える。

## Technical Context

**Language/Version**: Markdown、HTML、CSS、JavaScript(ブラウザ内で実行)、Python 3(標準ライブラリ + Playwright)、bash

**Primary Dependencies**: Playwright(Chromium)。`python-pptx` は削除する

**Testing**: `tests/run-digital-agency-slides-skill.sh`(契約、単体、オフラインの fixture、ネットワークを要する E2E)、`tests/run-config-pyramid.sh`

**Constraints**: 公式DADSのコードは同梱しない(ADR-0011)。DADSのトークン・クラス・版を記憶から書かない。常時ロードの規則は5ファイルのまま、合計は基準値未満。ChatGPT 用の移植プロンプトは文字数上限のため変更しない

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレート。CLAUDE.md とグローバル規則を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: 変換に属するものだけを削除し、検査とプレビューは残す |
| 失敗するチェックを先に用意 | 合格: 契約テストと fixture を先に書き換え、失敗を記録する |
| 規則層の独立 | 合格: 新しい義務は既存の規則に加え、他の規則やスキルを名指ししない |
| 公開契約の同期 | 合格: README(英・日)、ADR、設計記録を同じ変更で更新する |

## 設計の要点

1. **構成**: スライドの役割(`data-layout`)を木の位置で定める — `title`、`premise`、`answer`、`point`、`closing`、`appendix`。根拠の見せ方(数値タイル、比較、手順、表、図、定義、箇条書き)は役割と独立した本文の型とする。区切りスライドと目次スライドは廃止し、結論スライドの木が目次を兼ねる。本編の上限は k + 4(k は論点の数)で、既定の警告は9枚を超えたとき。
2. **マークアップ**: `<main>` の中に1スライド1 `<section aria-labelledby>`。表紙の見出しは `h1`(文書で1つ、`<title>` の主題と一致)、各スライドの見出しは `h2`、スライド内のブロックの見出しは `h3`。見出しは `hgroup.dads-heading` とショルダー。表紙は白地とし、DADSの見出しを上書きしない。
3. **検査**: `extract_slides.js`(変換用の中間表現を作る)を `check_slides.js`(所見だけを返す)に置き換える。文書の検査(`no-lang`、`no-title`、`h1-count`、`heading-skip`)と構成の検査(`deck-long`、`late-answer`、`appendix-order`)を加え、変換のための検査(`pseudo-decoration`、`dropped`、`slide-transformed`、`color-unreadable`)を除く。`deck.py` は `lint`(`--json` で機械可読の出力)と `preview` だけにする。
4. **テスト**: IR と .pptx の XML を検査していた `assert_classification.py` と `classification.html` を、所見のコードを検査する `assert_lint.py` と3つの自己完結した fixture(違反のある構成、違反のある文書、所見0件の最小デッキ)に置き換える。fixture は公式資材に依存しないためネットワークなしで動く。
5. **規則**: 読み手向け構造の規則に「前提と用語」の節を加える。根拠は ISO 24495-1:2023(原則3「読み手が容易に理解できる」、指針5.3.2「なじみのある語を選ぶ」)と Spiro ほか(1989、単一の類推が誤った推論を生む)。

## テスト先行

契約テスト、単体テスト、fixture テスト、E2E の期待値を先に新しい契約へ書き換え、現行の実装に対して失敗することを記録する。その後、スキルの文書・資材・スクリプトを実装して通す。規則は構造テストに所有権の検査 RULE-12 を先に加え、失敗を確認してから規則を書く。

## リスクと分岐

- **E2E はネットワークが必要**: 公式資材を取得できない環境では E2E が skip になる。fixture テストはオフラインで検査の挙動を担保する。
- **上流の変更**: 公式の見出しコンポーネントのクラスや属性が変わると、テンプレートが崩れる。`fetch-dads-assets.sh` は存在しないコンポーネントを報告して止まる。
- **表示の確認**: 自動検査は見た目の良し悪しを判定できない。`preview` の画像を目で確認する。

## Complexity Tracking

違反なし。
