# Implementation Plan: `.claude` 設定の Codex CLI への包括移植と挙動同期

**Branch**: `014-codex-config-port` | **Date**: 2026-07-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-codex-config-port/spec.md`

## Summary

`.claude/` 設定の未移植分(権限 allow/ask、秘密情報プロンプト検知、MCP カタログ、カスタムプロンプト、ユーザースコープ展開)を Codex CLI のネイティブ機構(Rules / `~/.codex/config.toml` の管理マーカー区間 / prompts / `~/.agents/skills`)で再現し、013 実装分の**未配線フック**と**壊れシンボリックリンク**を修復する。展開モデルは確定前提に従いユーザースコープ主体: リポジトリの `.codex/`・`.agents/` をソースとして `install.sh` が `~/.codex/`・`~/.agents/` へ展開する。恒常同期は新スイート `tests/run-codex-sync.sh` によるドリフト検知で担保し、全体は構成要素対応表(`.codex/README.md`)に 100% 分類で記録する。

## Technical Context

**Language/Version**: Bash(既存フック・スイートと同一規約: `set -euo pipefail`、shellcheck/shfmt 準拠)、Markdown(プロース・プロンプト)、TOML(`config.toml` 断片 — フック登録・MCP カタログ・rules はここに統合、`hooks.json` は使わない)、Starlark(.rules)

**Primary Dependencies**: Codex CLI(AGENTS.md 探索、`~/.agents/skills` 走査、`~/.codex/config.toml`(hooks 登録+MCP を管理マーカー区間で保持)、Rules、`~/.codex/prompts/`)、Claude Code(`settings.json`、`.claude/hooks/`)、`jq`(JSON 処理)、既存 `scripts/guardrails/*.sh`

**Storage**: ファイルのみ(リポジトリ + `~/.codex/`、`~/.agents/`、`~/.claude/`)。DB なし

**Testing**: 既存挙動スイート規約に準拠した bash スイート(`tests/run-codex-sync.sh` 新設、既存 `tests/run-*.sh` は回帰確認)

**Target Platform**: macOS / Linux の開発者ローカル環境(シンボリックリンク前提。Windows は対応表に制約として記録)

**Project Type**: 開発ツーリング設定リポジトリ(アプリケーションコードなし)

**Performance Goals**: N/A(対話セッションのフック応答が体感を損ねない程度 — 既存共有スクリプトと同等)

**Constraints**: `~/.codex/AGENTS.md` は 32 KiB 予算内(research R1)/ Rules はシェルコマンドのプレフィクス判定のみ(R5)/ `default.rules`・`config.toml` の非管理セクションに触れない(R5, R6)/ 秘密情報を版管理ファイル・展開ファイルに平文で書かない / PreToolUse 応答の三値は未検証のため fail closed 維持(R3)

**Scale/Scope**: ユーザースコープ手書きスキル 6 件(プロジェクト初期化時の `speckit-*` 15 件は別管理)、MCP サーバ 6 件、フックアダプタ 4 件(既存 3 + 新規 1)、Rules 1 ファイル、プロンプト 1 件、対応表 1 式、検証スイート 2 本 + install.sh 拡張

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未批准のテンプレートのままであり、プロジェクト固有のゲートは定義されていない。代わりにリポジトリの恒常原則(`.claude/CLAUDE.md` Core Principles、`rules/live-documentation.md`、`rules/permissions.md`)を準用する:

| ゲート | 判定 | 根拠 |
|---|---|---|
| 正確性: 主張は検証可能な事実に基づく | PASS | research.md の全決定に公式ドキュメント + 実地調査の二系統根拠と確信度を付記 |
| Live Documentation: 文書はコードと同一変更で更新 | PASS(設計に内包) | FR-012 / 対応表・README 更新を各実装タスクと同一コミット単位に置く方針 |
| 権限・安全: 破壊的操作の default-deny を弱めない | PASS | fail closed 維持(ask→deny 丸め)、`default.rules` 不可侵、平文秘密情報なし |
| 一方向ドア: アーキテクチャ上の不可逆決定は ADR 化 | 該当あり — 提案 | 「Codex 設定はユーザースコープ展開を主とする」はメンテナ決定済みの構造判断。実装完了時に ADR 化を提案する(spec 決定の転記、再審理ではない) |

Phase 1 設計後の再評価: 新たな違反なし。複雑性の追加(新スイート 1 本、install.sh 関数追加)は既存パターンの反復であり Complexity Tracking 対象なし。

## Project Structure

### Documentation (this feature)

```text
specs/014-codex-config-port/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── deployment-map.md    # 構成要素対応表の契約(列・分類・必須行)
│   └── sync-check.md        # tests/run-codex-sync.sh の CLI 契約
└── tasks.md             # Phase 2 output (/speckit-tasks — 本コマンドでは作らない)
```

### Source Code (repository root)

```text
.codex/                          # Codex ユーザー設定のソース(→ ~/.codex/ へ展開、install.sh 経由)
├── README.md                    # 構成要素対応表(新規 — deployment-map.md 契約に従う)
├── AGENTS.md                    # グローバル指針プロース(新規: リポジトリルート AGENTS.md から中身を移動)
├── hooks/
│   ├── destructive-command-adapter.sh   # 既存(install.sh 1d が config.toml へ登録— 配線先は既存)
│   ├── pre-edit-adapter.sh              # 既存(同上)
│   ├── post-edit-adapter.sh             # 既存(同上)
│   └── prompt-secret-adapter.sh         # 新規(R4/R0: install.sh 1d の ADAPTERS リストに追加)
├── rules/
│   └── guardrails.rules         # 新規(R5: install.sh 1e で ~/.codex/rules/ へ展開)
└── prompts/
    └── verify-config.md         # 新規(R7: install.sh 1f で ~/.codex/prompts/ へ展開)

.agents/skills/                  # プロジェクトスコープのスキル公開(壊れリンク 3 件を削除 — 33c82eb 追従)

.claude/hooks/user-prompt-submit.sh   # 共有スクリプトを呼ぶ薄いラッパへ改修(R4)
scripts/guardrails/
└── prompt-secret-scan.sh        # 新規: 秘密情報検知の共有ロジック(R4)

install.sh                       # 修正(R0/R9):
                                  #  1b: ソースを .codex/AGENTS.md に変更
                                  #  1c: CUSTOM_SKILLS から advisor/domain-model/ubiquitous-language を削除
                                  #  1d: ADAPTERS に prompt-secret-adapter.sh(UserPromptSubmit)を追加
                                  #  1e(新規): guardrails.rules 展開
                                  #  1f(新規): verify-config.md プロンプト展開
                                  #  1g(新規): Codex 側 MCP カタログ upsert(~/.codex/config.toml)
AGENTS.md                        # リポジトリルート: 残骸修復(このリポジトリ固有の内容のみ、または削除)
tests/
└── run-codex-sync.sh            # 新規: 同期健全性スイート(R8)
```

**Structure Decision**: 既存の「共有スクリプト(`scripts/guardrails/`)+ ツール別薄アダプタ」構成(013 確立)、および `install.sh` の「管理マーカー区間による TOML 編集」パターン(013 で `~/.codex/config.toml` の hooks 登録に確立済み)の両方を踏襲する。R0 の訂正により、新規要素の大半は**既存 `install.sh` ステップの修正**であり、新規ファイルは `.codex/` 配下のソースと `tests/run-codex-sync.sh` に限られる。`hooks.json` は作らない(config.toml 方式が既に実装・選択済みのため)。

## Phase 0: Research(完了)

[research.md](research.md) — R0〜R10 で全未知数を解決(R0 は `/speckit-tasks` 直前の `install.sh` 再調査による訂正)。要点:

- 実効位置の確定: グローバル指針 `~/.codex/AGENTS.md`、ユーザースキル `~/.agents/skills`(シンボリックリンク追従)、フック `~/.codex/config.toml`(管理マーカー区間、**hooks.json ではない**)、Rules `~/.codex/rules/*.rules`、MCP `~/.codex/config.toml`、プロンプト `~/.codex/prompts/`。
- **R0 訂正(重要)**: `install.sh` は AGENTS.md 展開・スキルシンボリックリンク・フック登録(config.toml 管理区間)の骨格を**既に実装済み**(013 実装分)。未実装なのは Rules・prompts・Codex 側 MCP カタログ・4 件目のフックのみ。作業の実体は「既存ステップの修正 3 箇所 + 新規ステップ 3 箇所」。
- 発見した欠陥: (1) 013 の 3 アダプタは config.toml 管理区間のコードはあるが、この環境で `install.sh` 未再実行のため未配線。(2) `.agents/skills/` の壊れリンク 3 件は、コミット `33c82eb`(PR #48)でリポジトリ `.claude/skills/` から `advisor`/`domain-model`/`ubiquitous-language` が**意図的に**削除された結果 — install.sh の `CUSTOM_SKILLS` リストが追従できておらず、次回実行時に `~/.claude/skills/` からも同 3 件が消える(既存のリポジトリ内ミラー方式による副作用)。(3) MCP カタログ: Claude 側は upsert 済みだが Codex 側(`~/.codex/config.toml`)は未実装で 2 サーバ欠落+別名重複。
- 判断変更: UserPromptSubmit イベントの存在確認により秘密情報検知をアダプタ移植へ昇格(spec FR-011 修正済み)。

## Phase 1: Design & Contracts(完了)

- [data-model.md](data-model.md) — 対応表の行スキーマ、配置レイヤ、同期方式、分類の状態遷移。
- [contracts/deployment-map.md](contracts/deployment-map.md) — 構成要素対応表(`.codex/README.md`)が満たすべき契約: 必須列、分類値、全 `.claude/` 要素の必須行、検証可能性。
- [contracts/sync-check.md](contracts/sync-check.md) — `tests/run-codex-sync.sh` の入出力契約: チェック項目、exit code、未展開環境でのスキップ挙動、出力形式。
- [quickstart.md](quickstart.md) — エンドツーエンド検証手順(install.sh 実行 → Codex セッションでの実挙動確認 → スイート実行)。
- 既存契約の再利用: アダプタの stdin/stdout は `specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md` に従う(新規 prompt-secret-scan も同契約に載せる)。

## 実装フェーズの構成(/speckit-tasks への指針)

優先度は spec のユーザーストーリー順に対応させる:

1. **修復**: Foundational として `.agents/skills/` 壊れリンク 3 件削除 + `install.sh` の `CUSTOM_SKILLS` 修正(US1/US5 の前提)。US2 側でルート `AGENTS.md` 残骸修復・`.codex/AGENTS.md` 内容確定(32 KiB 検証込み)。あわせて Setup 段階で `CLAUDE.md` の作業ツリー未確定変更(SPECKIT ブロック除去)も確定させる(spec.md Assumptions)。
2. **配線(US3)**: `install.sh` 1d の Python `ADAPTERS` リストに 4 件目(`prompt-secret-adapter.sh`, event=`UserPromptSubmit`)を追加し、既存の `~/.codex/config.toml` 管理マーカー区間に統合する(`hooks.json` は作らない)。`scripts/guardrails/prompt-secret-scan.sh` 抽出 + `prompt-secret-adapter.sh` 新設 + `.claude/hooks/user-prompt-submit.sh` ラッパ化(TDD: 既存 `tests/run-*.sh` 規約で先にテスト)。
3. **権限・MCP・プロンプト(US3/US4/US5)**: `guardrails.rules` 作成、install.sh の Codex 展開関数(AGENTS.md/hooks/rules/prompts/guardrails/`~/.agents/skills` リンク)+ MCP upsert 追加、`verify-config.md` プロンプト作成。
4. **対応表と検証(US1/US6)**: `.codex/README.md` 対応表作成(deployment-map 契約準拠)、`tests/run-codex-sync.sh` 実装(sync-check 契約準拠)、実 Codex セッションでの受け入れ確認(quickstart 手順)、PreToolUse 三値スキーマ検証と ask 復元判断。
5. **クローズアウト**: `.claude/hooks/README.md`・ルート README への反映、ユーザースコープ展開決定の ADR 提案。

## Complexity Tracking

違反なし — 記載事項なし。
