# Implementation Plan: Automatic Skill Routing

**Branch**: `001-skill-auto-routing` | **Date**: 2026-05-06 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/001-skill-auto-routing/spec.md`

## Summary

`CLAUDE.md` と `rules/skill-routing.md` のスキルルーティング記述を mandatory（常時適用）に変更し、各スキルのトリガー条件を 1 行に削減する。合わせて `tests/skill-routing/` フォルダにプロンプトテストシナリオを整備し、変更後の精度を検証できる環境を構築する。

## Technical Context

**Language/Version**: Markdown（設定ファイル変更のみ）  
**Primary Dependencies**: Claude Code skills system (`.claude/skills/`)  
**Storage**: N/A  
**Testing**: 手動プロンプト実行 + `tests/skill-routing/` シナリオファイル  
**Target Platform**: Claude Code (CLI / IDE)  
**Project Type**: Agent configuration  
**Performance Goals**: N/A  
**Constraints**: spec-kit スラッシュコマンド（`/speckit-*`）は対象外; 既存スキルの動作を破壊しない  
**Scale/Scope**: 変更対象ファイル 2 件、テストシナリオ 4+ 件

## Constitution Check

constitution.md が未記入テンプレートのため、プロジェクト固有のゲートなし。  
一般原則として: 変更は最小限・可逆・ローカルスコープ — ゲート違反なし。

## Project Structure

### Documentation (this feature)

```text
specs/001-skill-auto-routing/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (変更対象)

```text
.claude/
├── CLAUDE.md            # Skills セクション書き換え
└── rules/
    └── skill-routing.md # Routing 3 行のみ残す

tests/
└── skill-routing/       # 新規作成
    ├── 001-code-implement.md
    ├── 002-document-create.md
    ├── 003-mixed-code-and-doc.md
    └── 004-ambiguous-request.md
```

## Complexity Tracking

Constitution 違反なし。Complexity Tracking 不要。
