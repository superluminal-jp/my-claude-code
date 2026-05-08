# Implementation Plan: Ubiquitous Language Auto-Builder

**Branch**: `feature/003-ubiquitous-language` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-ubiquitous-language/spec.md`

## Summary

DDD のユビキタス言語をプロジェクトごとに自動収集・維持する Claude Code スキル `ubiquitous-language` を新規作成する。speckit ライフサイクルフック（`before_specify` 等）と CLAUDE.md の常駐ルールの 2 経路でトリガーし、業務イベント起点の対話・曖昧語検知・BC 別分割・ドリフト検知・コンテキスト長圧縮の 5 機能を 1 スキルで提供する。

## Technical Context

**Language/Version**: Markdown（Claude Code スキルシステム）
**Primary Dependencies**: Claude Code skills system (`.claude/skills/`)、spec-kit `extensions.yml` フック機構
**Storage**: `.specify/ubiquitous-language/<bc-name>.md`（BC ごと）、`.specify/ubiquitous-language/context-map.md`、`.specify/ubiquitous-language/watchlist.md`（オプション）
**Testing**: 手動プロンプト実行 + `tests/ubiquitous-language/` シナリオファイル（8 件）
**Target Platform**: Claude Code CLI / IDE（`.specify/` プロジェクトコンテキスト必須）
**Project Type**: Agent configuration / Skill playbook
**Performance Goals**: 各トリガー時 5 秒未満（SC-010）; 会話レスポンスを遅延させない
**Constraints**: v1 はソースコード走査なし（AI 生成アーティファクトのみ対象）; UL 書き込みは常にユーザー確認
**Scale/Scope**: 新規ファイル 5 件 + 既存ファイル 2 件変更 + テスト 8 件

## Constitution Check

constitution.md が未記入テンプレートのため、プロジェクト固有のゲートなし。
一般原則として: 変更は最小限・可逆・ローカルスコープ — ゲート違反なし。

## Project Structure

### Documentation (this feature)

```text
specs/003-ubiquitous-language/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── skill-interface.md          # Phase 1 output
│   └── extensions-yml-additions.md # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (変更・追加対象)

```text
.claude/
├── CLAUDE.md                        # Skills ルーティング 1 行追加
└── skills/
    └── ubiquitous-language/
        └── SKILL.md                 # 新規作成（本機能のコア）

.specify/
├── extensions.yml                   # before_{specify,clarify,plan,tasks,analyze} に hook 追加
├── templates/
│   ├── ubiquitous-language-template.md  # 新規作成（BC ファイル雛形）
│   └── context-map-template.md          # 新規作成
└── ubiquitous-language/             # 実行時に生成（実装対象外）
    ├── <bc-name>.md
    └── context-map.md

tests/
└── ubiquitous-language/             # 新規作成
    ├── 001-bootstrap-new-project.md
    ├── 002-vague-term-detection.md
    ├── 003-conversational-collection.md
    ├── 004-bc-split-conflict.md
    ├── 005-drift-detection.md
    ├── 006-context-compression.md
    ├── 007-state-transition-elicitation.md
    └── 008-size-budget-enforcement.md
```

**Structure Decision**: Single-project（既存 `.claude/skills/` パターンに準拠）。新規ファイルは `.claude/skills/ubiquitous-language/SKILL.md` のみ。設定変更は `.specify/extensions.yml` と `.claude/CLAUDE.md` の 2 ファイル。

## Complexity Tracking

Constitution 違反なし。Complexity Tracking 不要。
