# Test: Scrum Facilitation Request Auto-Routes to Scrum Master

**Category**: scrum
**ID**: 007

## Input Prompt

```
チームのデイリースクラムが進捗報告会になっていて、15分では終わらない
```

## Expected Skill

`scrum-master`

## Expected Behavior

`scrum-master` スキルが自動的にロードされる。プロンプトは「スキル」「Scrum Master」のいずれも明示していないが、Scrumイベント（Daily Scrum）の機能不全という主題からルーティングされる。

## Pass Criteria

- `scrum-master` スキルが自動的にロードされる
- ユーザーの明示的な指定なしにルーティングされる
- 会議運営の話題であっても `minto-*` や `clarifier` に誤ルーティングされない
- `/speckit-*` スラッシュコマンドへの誤ルーティングが発生しない

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-07-25
観察した動作: scrum-master
Pass / Fail: Pass
