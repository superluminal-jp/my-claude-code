# Test: Document Creation Request Auto-Routes to Interactive Document Builder

**Category**: document  
**ID**: 002

## Input Prompt

```
READMEを書いて
```

## Expected Skill

`minto-builder`

## Expected Behavior

`minto-builder` スキルが自動的にロードされる。既存のドラフトがない状態で文書作成を求められたため、対話で読者・目的・中心的な主張を整理しながら文書を構築する。ユーザーが明示的にスキルを指定する必要がない。

## Pass Criteria

- `minto-builder` スキルが自動的にロードされる
- ユーザーの明示的な指定なしに文書構築が開始される
- `coder` スキルへの誤ルーティングが発生しない

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-07-20
観察した動作: clarifier
Pass / Fail: FAIL (got: clarifier)
