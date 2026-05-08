# Implementation Plan: DDD ドメインモデル管理スキル

**Branch**: `005-ddd-domain-model-skill` | **Date**: 2026-05-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-ddd-domain-model-skill/spec.md`

## Summary

Claude Code 会話環境で DDD のドメインモデルを維持するスキルを実装する。受動収集（会話中の DDD 語彙パターン検出）と明示コマンド（モデルファイルの生成・更新）の 2 モードを持つ Markdown プレイブック。出力は `docs/models/<context-kebab>.md`（Mermaid + 5 種テーブル）と `docs/models/index.md`（BC 一覧）。ubiquitous-language スキルと連携し、UL をドメインイベント命名の正とする。

## Technical Context

**Language/Version**: N/A — Markdown スキルファイルのみ（コード実装なし）
**Primary Dependencies**: Claude Code スキルシステム（SKILL.md ローディング機構）
**Storage**: ユーザープロジェクト内 `docs/models/` ディレクトリ（Markdown ファイル）
**Testing**: 手動（会話での実行確認）— 自動テストなし
**Target Platform**: Claude Code（CLI / デスクトップ / Web / IDE 拡張、すべて同一）
**Project Type**: Claude Code スキル（Markdown プレイブック + テンプレート）
**Performance Goals**: N/A
**Constraints**: 既存スキルのパターン（`SKILL.md` + テンプレートディレクトリ）に準拠すること
**Scale/Scope**: 成果物 3 ファイル（SKILL.md + index-template.md + context-template.md）+ CLAUDE.md 更新 1 行

## Constitution Check

プロジェクトのコンスティテューションはプレースホルダー状態（未記入）のため、ゲートチェックは N/A。

## Project Structure

### Documentation (this feature)

```text
specs/005-ddd-domain-model-skill/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
.claude/skills/domain-model/
├── SKILL.md                   # メインプレイブック（フロー定義・不変条件）
├── index-template.md          # docs/models/index.md の初期テンプレート
└── context-template.md        # docs/models/<context-kebab>.md の初期テンプレート
```

**Structure Decision**: ubiquitous-language スキルと同じ「ディレクトリ + SKILL.md + テンプレート群」パターンを採用。

## Complexity Tracking

Constitution が未定義のため省略。
