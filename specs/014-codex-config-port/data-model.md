# Data Model: `.claude` 設定の Codex CLI への包括移植と挙動同期

**Date**: 2026-07-20 | **Feature**: [spec.md](spec.md)

本フィーチャーに DB・API のデータはない。「データ」は設定ファイル群とそれらの対応関係であり、中核エンティティは**構成要素対応表**の行である。

## エンティティ

### 構成要素対応表エントリ (DeploymentMapEntry)

`.codex/README.md` の表 1 行。全 `.claude/` 構成要素 + `.mcp.json` を漏れなく被覆する(SC-001)。

| フィールド | 型 / 値域 | 説明 |
|---|---|---|
| `claude_source` | リポジトリ相対パス | Claude Code 側ソース(例: `.claude/hooks/pre-bash.sh`、`settings.json#permissions.allow`) |
| `codex_artifact` | リポジトリ相対パス or `~` パス or `—` | Codex 側実体(例: `.codex/hooks/destructive-command-adapter.sh`、`~/.agents/skills/<name>`)。対象外は `—` |
| `classification` | `ported-013` \| `ported-014` \| `out-of-scope` | 分類(移植済み(013 まで)/ 本機能で移植 / 対象外) |
| `sync_method` | `single-source` \| `auto-sync` \| `verified-copy` \| `—` | 単一ソース参照(リンク/共有スクリプト)/ 自動同期(install.sh・既存フック)/ 検証付き二重管理(run-codex-sync が diff)/ 対象外 |
| `behavior_delta` | 自由記述 or `none` | 既知の挙動差分・制約(例: 「ask は deny に丸め(fail closed)」「Rules はシェルのみ」) |
| `rationale` | 参照(012 Q 番号 / research R 番号) | 分類・差分の根拠への参照。対象外行は理由必須 |

**バリデーション**:

- `.claude/` 配下の全ファイル・`settings.json` の全トップレベルキー・`.claude/commands/*`・`.mcp.json` が最低 1 行に現れる(被覆 100%)。
- `classification != out-of-scope` ⇒ `codex_artifact` と `sync_method` は `—` 不可。
- `classification == out-of-scope` ⇒ `rationale` に理由必須。
- `sync_method == verified-copy` ⇒ `tests/run-codex-sync.sh` に対応チェックが存在すること(sync-check 契約)。

### 配置レイヤ (DeploymentLayer)

| 値 | Claude Code 側 | Codex 側 | 展開手段 |
|---|---|---|---|
| `repo-source` | `.claude/`、`scripts/guardrails/`、`.mcp.json` | `.codex/`、`.agents/skills/` | 版管理のみ(git) |
| `user-scope` | `~/.claude/` | `~/.codex/`、`~/.agents/` | `install.sh`(冪等) |
| `project-scope-live` | `.claude/`(Claude Code は直接読む) | ルート `AGENTS.md`、`.agents/skills/`(Codex が直接読む) | なし(その場で有効) |

**ルール**: Codex のユーザー設定は必ず `repo-source` → `user-scope` の展開で成立する(メンテナ決定 2026-07-20)。`project-scope-live` はこのリポジトリで作業する場合の補助。

### 同期ペア (SyncPair)

`tests/run-codex-sync.sh` が検証する対応関係。

| フィールド | 説明 |
|---|---|
| `left` / `right` | 比較対象パス(片方が `~` 配下の場合あり) |
| `relation` | `symlink-resolves`(リンク先実在)\| `set-subset`(集合包含: `.mcp.json` ⊆ config.toml)\| `content-equal`(diff 一致)\| `size-budget`(≤ 32 KiB)\| `path-executable`(hooks 参照先が実行可能)\| `list-subset-per-category`(代表カテゴリ単位で allow 宣言が双方に存在、SYNC-11)\| `secret-pattern-absent`(既知の秘密情報正規表現に平文一致しない、SYNC-12) |
| `on_missing_home` | `skip-warn`(未展開環境ではスキップ+警告)\| `fail`(リポジトリ内で完結する検証は常に実施) |

### ガードレール判定 (GuardrailDecision) — 既存契約の再掲

共有スクリプト(`scripts/guardrails/*.sh`)の出力。013 の `contracts/guardrail-script-io.md` に準拠。

- 値域: `allow` | `ask` | `deny`(+ 理由文字列)
- Codex アダプタでの写像: `allow`→続行、`ask`→**`deny` に丸め(fail closed、三値スキーマ検証まで)**、`deny`→拒否。
- 新規 `prompt-secret-scan.sh` も同契約: 入力はプロンプト本文、出力は `allow`/`deny` + 検知パターン名(秘密情報の値そのものは出力に含めない)。

### 権限ルール (PermissionRule)

`settings.json#permissions` と `guardrails.rules` の対応単位。

- 値域: `allow` | `prompt`(= Claude の `ask`)| `forbidden`(= `deny`)
- 制約: Rules で表現するのはシェルコマンドのプレフィクスで書ける allow/prompt のみ。deny 系・正規表現系・ファイルツール系は共有スクリプト(フック)側の担当(research R5)。
- 状態: 複数マッチ時は最も制限的な決定が勝つ(Codex 仕様)。フックとの重畳でも同様(制限側優先)。

## 状態遷移

### 対応表エントリのライフサイクル

```text
(要素追加/発見)
   → unclassified          … 対応表に行がない状態。run-codex-sync が被覆チェックで検出(失敗)
   → classified            … 行が追加され classification 確定
   → deployed              … codex_artifact が存在し install.sh 展開済み
   → drifted               … SyncPair 検証が失敗(片側変更・リンク切れ・集合不一致)
        → (修正 or 再展開) → deployed
```

`drifted` の検出が US6、`unclassified` の検出が US1/SC-001 に対応する。

### 壊れリンク 3 件の解消(初期状態の遷移)

```text
.agents/skills/{advisor,domain-model,ubiquitous-language}
  現状: broken-symlink(参照先が .claude/skills/ から剪定済み)
  → 削除(プロジェクトスコープの被覆対象から除外)
  → 同スキルは user-scope で提供: ~/.agents/skills/<name> → ~/.claude/skills/<name>
  → 対応表では classification=ported-014, sync_method=single-source(user-scope 行)として記録
```
