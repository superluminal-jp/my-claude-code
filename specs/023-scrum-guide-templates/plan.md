# Implementation Plan: Scrum Guide 作成物・イベント テンプレート

**Branch**: `023-scrum-guide-templates` | **Date**: 2026-08-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/023-scrum-guide-templates/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`.claude/skills/scrum-master/references/templates/` を新設し、Scrum Guide (2020)が定める3つの作成物（Product Backlog／Sprint Backlog／Increment、それぞれ対応するCommitment込み）と4つのタイムボックス化イベント（Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）に対応する、記入してすぐ使えるMarkdownテンプレートを計7ファイル作成する。内容は`scrum-framework.md`の「作成物とコミットメント」表・「イベント」表が既に規範として保持している`[SG20, p.X]`引用の範囲に厳密に限定し（research.md Decision 1）、進行手順やファシリテーション技法などGuideに明記のないHOW的内容は一切含めない。`SKILL.md`の「参照ファイル」表に新規テンプレート群への導線を追加し（FR-011）、`README.md`のファイルツリー説明も新規ディレクトリを反映するよう更新する（research.md Decision 2 — spec.mdが個別に名指ししていないが、Live Documentationルールにより必要）。

## Technical Context

**Language/Version**: N/A — 新しいソースコードは書かない。作成するのはMarkdownコンテンツファイルのみ。

**Primary Dependencies**: N/A。

**Storage**: N/A — フラットなMarkdownファイルのみ。

**Testing**: `tests/skill-routing/007-scrum-facilitation.md`（`tests/run-skill-routing.sh`で実行）が変更後も通ること — `SKILL.md`を編集するため。spec.mdのSC-001〜SC-005は`quickstart.md`のgrep/findコマンドで検証する（新規自動テストは追加しない）。

**Target Platform**: Claude Code（および既存のCodexミラー、ADR 0003参照）のスキルファイルシステム、本リポジトリ内のみ。

**Project Type**: Single — 既存スキルパッケージへのコンテンツ追加。src/testsのアプリケーション分割は適用されない。

**Performance Goals**: N/A。

**Constraints**: 新規テンプレートはScrum Guideに明示のない進行手順・ファシリテーション技法を含まないこと（FR-009）。各テンプレートの主要記入欄に`[SG20, p.X]`形式の出典を付けること（FR-010）。既存の`when_to_use`／スキル起動トリガーを変更しないこと（spec.md Assumptions）。スキル内に文切れリンクを作らないこと（FR-009相当、022番featureで確立したFR-009パターンを踏襲）。

**Scale/Scope**: 新規ディレクトリ1つ、新規ファイル7つ、既存2ファイル（`SKILL.md`、`README.md`）の追記編集。完全な一覧：`data-model.md`。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md`は未記入のSpec Kitテンプレートのままであり（全フィールドが`[PLACEHOLDER]`、バージョン・批准日なし）、批准されたことがない。プロジェクト固有のゲートは存在しない。本featureはconstitutionファイルではなく、リポジトリ横断的なルールを直接遵守する：`.claude/rules/live-documentation.md`（Drift Detection — `SKILL.md`の参照ファイル表という公開契約が変わるため、同一変更内での更新を要求。Proximity Enforcement — テンプレートはスキル配下に配置し、トップレベル`docs/`等には置かない）。違反は識別されず、Complexity Trackingへの記載は不要。

**Post-Phase-1 re-check**: 変更なし。Phase 1設計（data-model.md、quickstart.md）は新しい依存関係・サービス・アーキテクチャ層を導入せず、Phase 0で確定した範囲のファイル追加・編集を列挙したのみ。ゲートは引き続き空虚に通過する。

## Project Structure

### Documentation (this feature)

```text
specs/023-scrum-guide-templates/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── checklists/
│   └── requirements.md  # Spec quality checklist (/speckit-specify command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

`contracts/`ディレクトリは生成しない：本featureに外部API・CLIスキーマ・サービスエンドポイントは存在しない。テンプレート自体が唯一の「インターフェース」だが、これは`data-model.md`のエンティティ一覧として文書化する方が実態に即している。

### Source Code (repository root)

```text
.claude/skills/scrum-master/
├── SKILL.md                              # 追記 — 参照ファイル表に新規テンプレート群への導線を追加
└── references/
    ├── sources.md                        # 変更なし — 唯一の規範的出典 [SG20]
    ├── scrum-framework.md                # 変更なし — テンプレート内容の一次規範ソース
    ├── scrum-master-role.md              # 変更なし
    └── templates/                         # 新規ディレクトリ
        ├── product-backlog.md            # 新規
        ├── sprint-backlog.md             # 新規
        ├── increment.md                  # 新規
        ├── sprint-planning.md            # 新規
        ├── daily-scrum.md                # 新規
        ├── sprint-review.md              # 新規
        └── sprint-retrospective.md       # 新規

README.md                                 # 追記 — ファイルツリー説明に templates/ を反映
```

**Structure Decision**: 既存スキルパッケージへのin-placeコンテンツ追加。新規ディレクトリは`references/templates/`のみで、既存の`references/*.md`は変更しない（テンプレートは既存ファイルへの参照のみを持つ）。`SKILL.md`と`README.md`は導線・説明の追記にとどめ、既存の`when_to_use`・原則・ワークフロー本文は変更しない（spec.md Assumptions）。

## Complexity Tracking

*記載なし — Constitution Checkで正当化が必要な違反は識別されなかった。*
