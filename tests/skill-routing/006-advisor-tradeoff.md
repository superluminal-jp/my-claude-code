# Test: Trade-off Request Auto-Routes to Advisor

**Category**: advisor  
**ID**: 006

## Input Prompt

```
キャッシュに Redis と Memcached どちらを使うべきか比較しておすすめを教えて
```

## Expected Skill

`advisor`

## Expected Behavior

`advisor` スキルが自動的にロードされ、選択肢の比較と推奨が行われる。要件が不明確な clarifier ではなく、比較可能なオプションに対する判断依頼として扱われる。

## Pass Criteria

- `advisor` スキルが自動的にロードされる
- BLUF 形式で推奨が提示される
- `clarifier` や `coder` への誤ルーティングが発生しない

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-07-20
観察した動作: advisor
Pass / Fail: Pass
