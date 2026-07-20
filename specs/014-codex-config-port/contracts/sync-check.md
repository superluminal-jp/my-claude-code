# Contract: 同期健全性スイート (`tests/run-codex-sync.sh`)

**Feature**: [../spec.md](../spec.md) (FR-009, SC-005) | **Data model**: [../data-model.md](../data-model.md) (SyncPair)

既存挙動スイート(`tests/run-*.sh`)と同じ規約: 自己完結 bash、引数なしで実行、人間可読の PASS/FAIL 行を逐次出力、最後にサマリ。

## CLI

```text
tests/run-codex-sync.sh        # 全チェック実行
```

- **exit 0**: 全チェック PASS(SKIP を含んでよい)
- **exit 非 0**: 1 件以上 FAIL。FAIL 行は「チェック ID / 対象パス / 期待と実際」を 1 行で特定できること
- `~` 配下に依存するチェックは、展開先が存在しない環境では **SKIP(警告表示)** とし FAIL にしない(`on_missing_home: skip-warn`)— CI・未展開マシンでも意味を保つ

## チェック項目(ID は対応表の根拠列から参照される)

| ID | 内容 | relation | 失敗条件 | home 依存 |
|---|---|---|---|---|
| SYNC-01 | `.agents/skills/` の全エントリのリンク先実在 | symlink-resolves | 壊れリンク ≥ 1 | no |
| SYNC-02 | `~/.agents/skills/` の全エントリのリンク先実在 | symlink-resolves | 壊れリンク ≥ 1 | skip-warn |
| SYNC-03 | `.codex/AGENTS.md` サイズ ≤ 32 KiB(28 KiB 超で WARN) | size-budget | > 32768 bytes | no |
| SYNC-04 | `.mcp.json` サーバ集合 ⊆ `~/.codex/config.toml` の `[mcp_servers.*]` 集合、かつ各サーバのトップレベル定義が引用形式を含めてちょうど 1 件 | set-subset + unique | 欠落サーバ ≥ 1 または同名定義 ≥ 2 | skip-warn |
| SYNC-05 | `.codex/hooks/` の 4 アダプタの実在+実行可能、および `install.sh` の ADAPTERS 宣言との一致 | path-executable | 欠落・非実行可能・宣言乖離 | no |
| SYNC-06 | 展開コピー(`~/.codex/AGENTS.md`・`hooks/*`・`rules/guardrails.rules`・`prompts/verify-config.md`)とリポジトリソースの一致 | content-equal | diff 非空 | skip-warn |
| SYNC-07 | `~/.claude/scripts/guardrails/` に共有スクリプト全件が実在+実行可能 | path-executable | 欠落 | skip-warn |
| SYNC-08 | 対応表(`.codex/README.md`)の被覆: `.claude/` 実要素で表に現れないものがない | coverage | unclassified ≥ 1 | no |
| SYNC-09 | `.codex/prompts/verify-config.md` と `.claude/commands/verify-config.md` の参照手順の対応(双方が同一の検証入口を指す) | content-equal(緩和: 手順参照の一致) | 参照乖離 | no |
| SYNC-10 | `guardrails.rules` の構文健全性(`prefix_rule(` 形式・decision 値域の静的検査) | lint | 不正行 ≥ 1 | no |
| SYNC-11 | 代表カテゴリ(検証スイート `tests/run-*.sh`、`scripts/check-mcp-consistency.sh`、`shellcheck`/`shfmt`/`jq`/`yamllint`、git 読み取り系)について、`settings.json` の `permissions.allow` と `guardrails.rules` の `allow` 宣言の双方に対応エントリが存在すること(静的な集合突合せ。実際の許可判定エンジンは模擬しない) | list-subset-per-category | いずれかのカテゴリが片方にしか無い | no |
| SYNC-12 | `~/.codex/config.toml` の `[mcp_servers.*]` 管理区間に、`scripts/guardrails/prompt-secret-scan.sh` と同じ秘密情報パターン(AWS/GitHub/Slack/Google キー、秘密鍵ヘッダ)が平文で一致しないこと | secret-pattern-absent | パターン一致 ≥ 1 | skip-warn |

## 破壊テストでの受け入れ(SC-005)

以下の操作単体で対応チェックが FAIL になること:

1. `.claude/skills/` からスキル 1 件削除(コミットせず)→ SYNC-01 または SYNC-02 FAIL
2. `.mcp.json` にダミーサーバ追加 → SYNC-04 FAIL(展開済み環境)
3. `.codex/AGENTS.md` に 33 KiB 超のパディング追加 → SYNC-03 FAIL
4. `.codex/hooks/` のアダプタ 1 件を改名 → SYNC-05 FAIL
5. `~/.codex/AGENTS.md` のみ手編集 → SYNC-06 FAIL(展開済み環境)

## 禁止事項

- チェックは読み取り専用(自動修復・自動展開をしない — 修復は install.sh の再実行に誘導するメッセージのみ)
- `default.rules`・`config.toml` の非管理セクション・`auth.json` 等ユーザー所有物の内容を出力に含めない(セクション名・サーバ名の列挙まで)
- 秘密情報(環境変数値等)を出力しない
