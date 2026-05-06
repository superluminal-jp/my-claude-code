# Test: Ambiguous Request Auto-Routes to Clarifier

**Category**: ambiguous  
**ID**: 004

## Input Prompt

```
なんとかして
```

## Expected Skill

`clarifier`

## Expected Behavior

`clarifier` スキルが自動的にロードされ、intent gap（目標が不明確）として検出されて要件整理が行われる。不明確なまま作業が進まない。

## Pass Criteria

- `clarifier` スキルが自動的にロードされる
- 何をすべきか不明確な状態で作業が開始されない
- 明確化のための質問がユーザーに提示される
- `coder` や `editor` への誤ルーティングが発生しない

## Additional Test Prompts

以下のプロンプトでも `clarifier` が起動することを確認:

- `「なんか良い感じにして」` — vague quantifier（"良い感じ"の定義がない）
- `「それをどうにかして」` — undefined pronoun（"それ"が何か不明）
- `「早くして」` — negation without positive（"早い"の定義がない）

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-05-06
観察した動作: clarifier
Pass / Fail: Pass
