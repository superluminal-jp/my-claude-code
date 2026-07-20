# Quickstart: Codex 移植の検証手順

**Feature**: [spec.md](spec.md) | **Contracts**: [contracts/](contracts/)

実装完了後にエンドツーエンドで機能を証明する手順。実装コードはここに書かない(tasks.md の領分)。

## 前提

- macOS / Linux、`git`・`jq`・`bash` 利用可、Codex CLI インストール済み
- ブランチ `014-codex-config-port` をチェックアウト済み
- MCP 認証が必要なサーバ用の環境変数(例: `GOOGLE_DEV_KNOWLEDGE_API_KEY`)は任意(未設定なら該当サーバのみ接続失敗が期待値)

## 1. リポジトリ内検証(展開前)

```bash
tests/run-codex-sync.sh
```

期待: home 依存チェック(SYNC-02/04/06/07/12)は未展開なら SKIP、それ以外(壊れリンク・サイズ・4 アダプタ宣言・被覆・rules 構文)は PASS。部分的な旧展開が残る環境では対応する SYNC が FAIL し、`install.sh` 再実行を促す。

```bash
tests/run-destructive-command-guard.sh
tests/run-pre-edit-guard.sh
tests/run-post-edit-format-guard.sh
```

期待: 全 PASS(SC-007: Claude 側無劣化。user-prompt-submit のラッパ化後も既存スイートが通ること)。

## 2. 展開

```bash
./install.sh
```

期待: `~/.codex/AGENTS.md`・`~/.codex/hooks/`(4 アダプタ)・`~/.codex/rules/guardrails.rules`・`~/.codex/prompts/verify-config.md`・`~/.claude/scripts/guardrails/`・`~/.agents/skills/`(手書き 6 リンク)が作成され、`~/.codex/config.toml` に `.mcp.json` の 6 サーバが重複なく存在する。通常は managed MCP 区間へ生成し、同名サーバが非管理区間に既存ならユーザー定義を保持してそのサーバの生成だけを省略する。`default.rules` と config.toml の非管理セクションは変更されない(再実行しても冪等)。Google API key 未設定時は managed entry が disabled になる。

初回またはフック変更後は Codex TUI を起動し、`/hooks` で 4 件のユーザーフックを確認して信頼する。Codex は現在の定義ハッシュが信頼されるまで非管理コマンドフックをスキップするため、この操作前はガードレール検証へ進まない。

```bash
tests/run-codex-sync.sh
```

期待: SKIP がなくなり全 PASS。

## 3. Codex 実セッション検証

任意の別ディレクトリ(このリポジトリ外)で Codex CLI を起動し:

| 検証 | 操作 | 期待 |
|---|---|---|
| 指針適用 (US2) | AWS に関する質問をする | AGENTS.md の指針どおり MCP サーバ(aws-knowledge 等)を先に参照する挙動 |
| スキル発見 (US5) | スキル一覧を確認 | `~/.agents/skills` 経由で手書き 6 スキルが列挙される。Spec Kit 15 件は初期化済みプロジェクトの `.agents/skills` から発見される |
| ガードレール (US3) | `git push --force` 相当を依頼 | ブロックまたは確認(PreToolUse アダプタ発火) |
| credential 保護 (US3) | `.env` の読み取りを依頼 | 拒否 |
| 秘密情報検知 (R4) | ダミーの `ghp_...` トークンを含むプロンプト送信 | 拒否(UserPromptSubmit アダプタ発火)※実トークンは使わない |
| allow リスト (US3) | `shellcheck` 実行を依頼 | 確認プロンプトなしで実行(guardrails.rules) |
| MCP (US4) | MCP サーバ一覧確認 + microsoft-learn へのクエリ | 6 サーバが列挙され、クエリ成功 |
| プロンプト (US5) | `/prompts:verify-config` を呼び出す | このリポジトリの検証手順が実行される(custom prompts は deprecated の互換入口) |

このセッションで PreToolUse 応答スキーマの三値(`ask` 相当)可否も確認し、可能なら ask→deny 丸めを解除する(research R3 検証課題。不可なら対応表の挙動差分として維持)。

## 4. ドリフト破壊テスト (US6 / SC-005)

[contracts/sync-check.md](contracts/sync-check.md) の「破壊テストでの受け入れ」5 操作を順に実施し、それぞれ対応チェックだけが FAIL することを確認。各操作後は `git checkout -- .` / install.sh 再実行で復元。

## 5. クローズアウト確認

- `.codex/README.md` 対応表: [contracts/deployment-map.md](contracts/deployment-map.md) の必須行がすべて埋まっている(SC-001/SC-006)
- `.claude/hooks/README.md`・ルート README が新構成(config.toml managed hooks、prompt-secret-scan、Rules、MCP、prompts、install.sh 拡張)を反映(FR-012)
- ユーザースコープ展開決定の ADR が提案済み(plan の Constitution Check)
