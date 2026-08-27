# Implementation Plan: Apple Notes / Reminders 自動操作スキル

**Branch**: `033-apple-notes-reminders-port` | **Date**: 2026-08-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/033-apple-notes-reminders-port/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Notes.app と Reminders.app を macOS 上で安全かつ汎用的に自動操作する2つの Claude Code スキル（`apple-notes`, `apple-reminders`）を、既存の外部リポジトリから汎用機能のみを再実装して追加する。Notes 側は JXA（`osascript -l JavaScript`）による Apple Events 自動操作、Reminders 側はコンパイル済み Swift/EventKit CLI による自動操作とし、両者とも冪等な「フォルダ／リストの存在保証」、CRUD、書式検証、そして Notes に限った整合性チェック付き全内容上書き・削除（人間の事前承認が前提）を提供する。Scrum 固有の成果物（プロジェクトレジストリ、`--- scrum ---` ブロック、フローメトリクス連携）は対象外。クロスアプリの独自リンク機構も対象外とし、代わりに Apple 公式の手動共有操作（`ファイル > 共有 > Reminders`）を案内する。

## Technical Context

**Language/Version**: JXA (JavaScript for Automation, macOS 付属の JavaScriptCore/OSA ランタイム、バージョン固定なし) for Notes; Swift（操作者のマシンにインストール済みの Xcode Command Line Tools が提供するバージョン、ソーススキル同様バージョン固定なし）for Reminders; Python 3 標準ライブラリのみ（ハッシュゲート計算などの純粋ロジック補助）

**Primary Dependencies**: macOS 付属の Notes AppleScript/JXA スクリプティング辞書（追加インストール不要）; EventKit フレームワーク（Xcode Command Line Tools 経由、`swiftc` によるワンタイムビルドが必要）; Python 標準ライブラリのみ（`hashlib`, `json`, `argparse` 等 — サードパーティ pip パッケージなし、`permissions.md` のプロジェクトスコープ限定インストール方針と整合）

**Storage**: N/A（本機能はデータを自ら保持・所有しない。Notes.app / Reminders.app 自身のオンデバイスストアに対して自動操作を行うのみ）

**Testing**: 純粋ロジック部分（Markdown→Notes-HTML 変換・書式検証、SHA-256 ハッシュゲート計算、名前付き区画の分割・置換ロジック）は自動テスト対象とする — Python は標準ライブラリ `unittest`（パッケージマニフェストなし、`python3 -m unittest discover` で実行）、JS の純粋変換ロジックは `osascript -l JavaScript` で直接実行（Node.js 依存なし。Automation 権限を必要としない Apple Events 非呼び出しコードだけを対象とするため、権限なしでも実行できる）。各テストファイルは本リポジトリの既存慣習に倣い `tests/run-<name>.sh` ラッパーを持つ（例: `tests/run-mcp-startup.sh` 等）。フォルダ作成・ノート読み書き・ハッシュゲート付き上書き/削除・Reminders の CRUD といった実際の Apple Events / EventKit 呼び出しは自動テスト不可能（実機の Mac と両方の権限付与が必要）であるため、`quickstart.md` による手動検証で担保する — ソーススキル自身のテスト方針と同じ非対称性。

**Target Platform**: macOS 14 以降（Sonoma 以降）。Reminders の権限モデル（フルアクセス／書き込み専用の区別）に依拠するための最低バージョン。iOS/iPadOS やヘッドレス実行の経路はない。

**Project Type**: Claude Code スキルバンドル（本リポジトリの既存スキル群 `.claude/skills/*` と同じ形態 — REST API やモバイルアプリではない、スクリプト＋ SKILL.md の組）

**Performance Goals**: 明示的なスループット目標は仕様書にない。成功基準（SC-001〜SC-006）は正しさ・冪等性・安全性を対象とし、レイテンシは対象外。1操作あたり数秒程度の対話的な応答性で十分（ソーススキル自身もバッチ/大量処理ではなく単発の対話的自動操作を想定）。

**Constraints**: macOS 専用。Automation（Notes）と Reminders プライバシーという、いずれも非対話的には取得できない2つの別個の OS 権限、加えてハーネス自体のツール呼び出し許可が必要。CI・ヘッドレス実行での実データ検証経路はない。Reminders CLI はローカルでのワンタイムビルドを要し、`Info.plist` をバイナリの `__TEXT,__info_plist` セクションへリンクすることが必須（TCC が権限ダイアログの説明文をここから読むため — このフラグを欠くビルドは「許可されていない」という、ユーザーが解消不能な状態を生む）。

**Scale/Scope**: 2つのスキル（apple-notes, apple-reminders）。単一操作者・単一アカウントでの個人利用を前提とし、マルチアカウント/マルチテナントは対象外（ソーススキルの前提と同じ — `default account` / `defaultCalendarForNewReminders()` のみを扱う）。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入のテンプレートのままであり、本プロジェクト固有の批准済みゲートは存在しない。そのため、本リポジトリの全体指針（`CLAUDE.md` の Core Principles、`live-documentation.md` の6チェック、`permissions.md` の破壊的操作確認方針）を実質的な constitution として適用する。

| ゲート | 判定 | 根拠 |
|---|---|---|
| Accuracy（検証済み事実に基づく） | PASS | 移植元スキルの主張はすべて本セッション中に現行 Apple 公式ドキュメントへ対して独立に再検証済み（`research.md` 参照）。未検証・矛盾する主張（保持期間の日数、AppleScript辞書ページ）は断定せず、不確実性として明記する方針をスペックの前提条件に反映済み。 |
| Traceability（決定の記録） | PASS（要フォローアップ） | EventKit ベースの Swift CLI 採用（ビルド不要な AppleScript 案を却下）は、本リポジトリにとって新規の、後戻りしにくいアーキテクチャ選択であり、却下した代替案がある。Phase 1 完了後、`adr` スキルで ADR を提案する（Complexity Tracking ではなく本チェックの一部として実施 — 違反ではなく通常の記録義務）。 |
| Proximity Enforcement（`live-documentation.md` §4） | PASS | SKILL.md とスクリプトはいずれも `.claude/skills/apple-notes/` および `.claude/skills/apple-reminders/` に同居させる。トップレベル `docs/` への集約は行わない。 |
| Intermediate-Artifact Isolation（`live-documentation.md` §6） | PASS | 出荷される SKILL.md は本 `specs/033-*/` 配下のファイルにリンクしない。移植元スキルの根拠（Notes削除保持期間の不確実性、AppleScript辞書の出典など）は SKILL.md 本文にプレーンな注記として書き、ADR または本 spec への言及はしない。 |
| 破壊的操作の確認（`permissions.md` / FR-014, FR-015） | PASS | ノートの全内容上書き・削除は、ハッシュゲートによる同時実行チェックに加え、呼び出し前に人間へ置き換え内容（または削除対象）を提示し明示的承認を得ることをスクリプトの外側の運用規約として明記する（フックでは強制できないため、SKILL.md 内で運用者責務として明文化する）。 |

違反なし。Complexity Tracking は該当なしのため空欄のまま。

## Project Structure

### Documentation (this feature)

```text
specs/033-apple-notes-reminders-port/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.claude/skills/apple-notes/
├── SKILL.md
└── scripts/
    ├── ensure_folder.js       # フォルダの存在保証（作成 or 再利用、--parent-id でサブフォルダ）
    ├── list_notes.js          # フォルダ一覧 / 単一ノート取得（--plaintext, --with-body）
    ├── write_note.js          # 作成・追記・名前付き区画置換・ハッシュゲート付き上書き/削除
    └── note_write_guard.py    # SHA-256 ハッシュゲート計算・照合（stdlib のみ）

.claude/skills/apple-reminders/
├── SKILL.md
└── scripts/
    ├── build.sh                # swiftc ワンタイムビルド（Info.plist リンク必須）
    ├── Info.plist               # TCC 権限ダイアログ用の usage description
    └── main.swift                # lists / ensure-list / list / get / create / update / complete

tests/
├── test_note_write_guard.py         # note_write_guard.py の純粋ロジック単体テスト
├── run-note-write-guard.sh          # 上記のラッパー（python3 -m unittest discover）
├── test_note_body_conversion.js     # write_note.js の Markdown→HTML変換・書式拒否ロジック単体テスト
└── run-note-body-conversion.sh      # 上記のラッパー（osascript -l JavaScript）

docs/adr/
└── (Phase 1 完了後、EventKit ベース Reminders CLI 採用の ADR を追加)
```

**Structure Decision**: 単一プロジェクト構成。本リポジトリの既存スキル群（`.claude/skills/scrum-master/` 等）と同じ形（`SKILL.md` + `scripts/`）を2つ並べ、トップレベル `tests/` に純粋ロジックの自動テストのみを置く。Web/モバイル分割は不要（該当しないため Option 2/3 は採用しない）。

## Constitution Check（Phase 1 設計後の再判定）

`data-model.md` / `contracts/*` / `quickstart.md` を作成した結果、Phase 0 時点のゲート判定に変更はない。追加で確認した点:

- `data-model.md` は Notes/Reminders 自身のプロパティ surface を記述するのみで、独自の永続ストアを新設していない（Storage: N/A の判断と整合）。
- `contracts/*` はいずれも既存スクリプト（移植元の設計を踏襲した `ensure_folder.js` / `list_notes.js` / `write_note.js` / `note_write_guard.py` / Reminders CLI）のインターフェースを記述するのみで、SKILL.md 以外の新規ドキュメント階層を作っていない（Proximity Enforcement を維持）。
- `contracts/notes-write.md` のモード4・5（ハッシュゲート付き上書き・削除）は、FR-015 の「呼び出し前に人間の明示的承認を得る」という運用前提条件をコントラクト内に明記しており、Phase 0 のゲート判定を裏切っていない。
- Reminders 側の削除非対応（FR-016）を `contracts/reminders-cli.md` で「サブコマンドを追加してはならない」という禁止形で明記し、実装時に誤って追加されることを防ぐ。

違反なし。ADR フォローアップ（EventKit ベース Reminders CLI 採用）は Phase 1 完了後、本ドキュメント作成に続けて `adr` スキルで提案する。

## Complexity Tracking

*該当なし — Constitution Check に違反はない。*
