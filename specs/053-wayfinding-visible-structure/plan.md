# Implementation Plan: 現在地の分かるスライドと、見て分かる文章構造

**Branch**: `claude/digital-agency-slide-skill-vqe5ky` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

本編の各スライドの右上に、資料の構成を並べて現在の部分を示す `sld-tracker` を置き、フッターを「n / 全体」にする。`lint` は現在地の表示と実際の位置の食い違いを検査する。設計の参照文書に、現在地の示し方と、木の階層ごとの見た目の区別を加える。常時規則と Claude.ai 用プロンプトには、長い文章の見出しを木の位置で番号付けして主張として書くこと、支える論点の主張を太字で先頭に置き根拠を入れ子にすること、順序は番号付きリスト・比較は表にすることを加える。

## Technical Context

**Language/Version**: HTML、CSS、JavaScript(ブラウザ内)、Markdown

**Testing**: fixture `tracker.html` と `assert_lint.py`(LINT-13、LINT-14)、契約テスト(DSN-19・20、CHK-06、CSS-11、TPL-15〜17、TOOL-19)、RULE-16・17、E2E

**Constraints**: 常時ロードの合計 20,126 バイト未満。Claude.ai 用ブロック 7,000 字以下。本編の上限 k + 4 は変えない

## 設計の要点

1. **現在地の表示**: 表紙を除く本編の部分を並べた `<ol>` を、見出しの後、肩書き(ショルダー)の行の右端に絶対配置で置く。本文の高さを使わない。現在の項目は太字・キーカラーの下線・`aria-current="step"` で示し、色だけに頼らない。DADS のステップナビゲーションは約90px の高さがあり各スライドに置けないため、`aria-current` で現在を示す慣行だけを取り入れる。
2. **検査**: 表示のあるスライドが1枚でもあれば、表紙と付録以外の各スライドについて、項目数=本編(表紙を除く)の枚数、現在の項目=そのスライドの位置、を確かめる。食い違いはエラー `tracker`、欠落は警告 `tracker-missing`。現在地の表示は内容ではないため、箇条の密度の検査から除く。
3. **文章**: 「Parts」の節に2行を加える。容量の残りは約230バイト。
4. **Claude.ai**: 重複していた2つの記述(送信前点検の「answer early」、部の順序と重なる「Expose answer, … uncertainty」)を除いて 7,000 字以下に収める。

## Complexity Tracking

違反なし。
