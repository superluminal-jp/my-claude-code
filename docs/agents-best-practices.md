# Claude Code Agents ベストプラクティス

**目的**: Agents (サブエージェント・エージェントチーム) の設計・実装・運用に関する公式仕様とベストプラクティスをまとめたリファレンス。
**対象バージョン**: Claude Code v1.0.33+
**最終更新**: 2026-03-28

---

## 1. Agents とは

Agents は隔離されたコンテキストで専門タスクを実行する Claude Code の委譲メカニズム。メイン会話のコンテキストを消費せず、結果のサマリーのみを返す。

**2つの形態**:

| 形態 | 説明 | 用途 |
|------|------|------|
| **Subagent** | メインセッションから生成される単一ヘルパー | 調査、分析、冗長な操作の隔離 |
| **Agent Team** | 複数の独立セッションが協調 | 並列レビュー、競合仮説、レイヤー横断作業 |

---

## 2. フロントマター完全リファレンス

```yaml
---
# ID (必須)
name: my-agent                         # 一意識別子。小文字・ハイフンのみ
description: 用途と委譲条件の説明        # Claude の自動委譲判定に使用

# ツール設定
tools: Read, Grep, Glob, Bash          # ホワイトリスト (カンマ区切り)
disallowedTools: Write, Edit           # ブラックリスト (カンマ区切り)

# モデル・実行設定
model: sonnet                          # sonnet | opus | haiku | inherit | フル ID
effort: high                           # low | medium | high | max (Opus 4.6 のみ)
permissionMode: default                # default | acceptEdits | dontAsk | bypassPermissions | plan
maxTurns: 15                           # 最大エージェンティックターン数

# スキル注入
skills: api-conventions, error-handling # 起動時にスキル内容を注入

# MCP サーバー
mcpServers:
  - github                             # 名前参照
  - postgres:                          # インライン定義
      type: stdio
      command: npx
      args: ["pg-cli-mcp"]

# メモリ
memory: project                        # user | project | local

# 実行モード
background: true                       # 常にバックグラウンド実行
isolation: worktree                    # git worktree で隔離実行

# 初期プロンプト (メインスレッドとして実行時)
initialPrompt: "Review recent changes" # --agent 実行時の初期入力

# フック (エージェントライフサイクルにスコープ)
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---

エージェントのシステムプロンプトをここに記述...
```

### フィールド詳細

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `name` | string | エージェント識別子。Agent ツールの `subagent_type` で参照 |
| `description` | string | Claude が自動委譲を判定する際に使用。「いつ使うか」を明記 |
| `tools` | string | 使用可能ツールのホワイトリスト。省略時は親セッションを継承 |
| `disallowedTools` | string | 使用禁止ツールのブラックリスト。`tools` より先に適用 |
| `model` | string | モデルオーバーライド。`inherit` でセッションと同じ |
| `effort` | string | 推論努力レベルのオーバーライド |
| `permissionMode` | string | 権限モード。`plan` で編集前に承認要求 |
| `maxTurns` | int | ターン数上限。暴走防止 |
| `skills` | string | 起動時に注入するスキル名 (カンマ区切り) |
| `mcpServers` | YAML | エージェントにスコープされた MCP サーバー |
| `memory` | string | 永続メモリのスコープ。セッション間で学習を保持 |
| `background` | bool | 常にバックグラウンド実行するか |
| `isolation` | string | `worktree` で隔離された git worktree で実行 |
| `initialPrompt` | string | `--agent` 実行時の自動初期入力 |
| `hooks` | YAML | エージェントライフサイクルにスコープされたフック |

---

## 3. ビルトインエージェント

ファイル作成不要で常時利用可能:

| 名前 | モデル | ツール | 用途 |
|------|--------|--------|------|
| `Explore` | Haiku (高速) | Read のみ | コードベース探索・分析 |
| `Plan` | inherit | Read のみ | 計画前のコンテキスト収集 |
| `general-purpose` | inherit | 全ツール | 探索 + 変更が必要な複合タスク |
| `Bash` | inherit | Bash のみ | 隔離されたターミナル操作 |
| `claude-code-guide` | Haiku | Read のみ | Claude Code 自体に関する質問回答 |

---

## 4. エージェントの起動方法

### Agent ツール (プログラム的)

```
Agent tool parameters:
- prompt (必須): タスク内容
- description (必須): 短い説明 (3-5語)
- subagent_type: ビルトイン名 or カスタム名
- model: モデルオーバーライド
- isolation: "worktree" で隔離実行
- run_in_background: true でバックグラウンド
```

### 自然言語

```
Use the code-reviewer agent to analyze my recent changes
```

### @メンション

```
@"code-reviewer (agent)" look at the authentication changes
```

`@` でタイプアヘッド表示。確実にそのエージェントが実行される。

### セッションデフォルト

```bash
claude --agent code-reviewer
```

または `settings.json`:
```json
{ "agent": "code-reviewer" }
```

### CLI フラグ (一時的)

```bash
claude --agents '{
  "reviewer": {
    "description": "Code reviewer",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob"],
    "model": "sonnet"
  }
}'
```

---

## 5. スコープ優先度

高い順:

1. **Session** (`--agents` CLI フラグ) — 最高優先度
2. **Project** (`.claude/agents/`) — git でチーム共有
3. **User** (`~/.claude/agents/`) — 全プロジェクトで利用可能
4. **Plugin** — プラグイン経由
5. **Built-in** — 常時利用可能

同名エージェントは高優先度が勝つ。

---

## 6. エージェントの通信

### Subagent の結果返却

- 隔離コンテキストで実行
- 完了時にサマリーをメイン会話へ返却
- トランスクリプトは別途保存: `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`
- サブエージェントは他のサブエージェントを生成できない (ネスト不可)

### SendMessage による継続

サブエージェント完了後、`SendMessage` で agent_id を指定して続行可能。コンテキストは保持される。

### Agent Team の通信

- 各チームメイトは独立セッション
- `SendMessage` で直接メッセージング (リード経由不要)
- 共有タスクリストで調整
- 共有メールボックスでメッセージング

---

## 7. Agent Team

### 有効化

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### アーキテクチャ

| コンポーネント | 役割 |
|--------------|------|
| **Team Lead** | メインセッション。チームメイトの生成・調整 |
| **Teammates** | 個別セッションで割り当てタスクを実行 |
| **Task List** | 依存関係付きの共有作業項目 |
| **Mailbox** | エージェント間メッセージングシステム |

### 表示モード

| モード | 要件 | 表示 |
|--------|------|------|
| `in-process` (デフォルト) | なし | Shift+Down で切替 |
| `split-panes (tmux)` | tmux | 全チームメイト同時表示 |
| `split-panes (iTerm2)` | it2 CLI | ネイティブ分割ペイン |

### タスク管理

- **状態**: Pending → In progress → Completed
- **依存関係**: リードが定義。依存完了後に実行可能に
- **ファイルロック**: 競合条件防止

### チームサイズ

推奨 3-5 人。6 人超で収穫逓減。

---

## 8. エージェントメモリ

### 設定

```yaml
---
name: code-reviewer
memory: project
---
```

### スコープ

| スコープ | 保存先 | 用途 |
|---------|--------|------|
| `user` | `~/.claude/agent-memory/<agent-name>/` | 全プロジェクト共通の知識 |
| `project` | `.claude/agent-memory/<agent-name>/` | プロジェクト固有。git で共有可能 |
| `local` | `.claude/agent-memory-local/<agent-name>/` | プロジェクト固有。git 対象外 |

### 動作

1. `MEMORY.md` の先頭 200 行 or 25KB がコンテキストに自動読込 (小さい方)
2. トピックファイル (例: `debugging.md`) はオンデマンド読込
3. Read, Write, Edit ツールがメモリ管理用に自動有効化

### ベストプラクティス

- デフォルトで `project` スコープを使用
- エージェントプロンプトにメモリ参照の指示を含める:

```markdown
---
memory: project
---

Before starting, review your memory for relevant patterns.
After completing analysis, save findings to memory.
```

---

## 9. フック

### エージェント内フック

エージェント実行中のみ有効:

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
```

### プロジェクトレベルのエージェントフック

`settings.json` で設定:

| イベント | 入力 | ブロック可能 | タイミング |
|---------|------|:-----------:|----------|
| `SubagentStart` | agent_id, agent_type, session_id, cwd | x | サブエージェント実行前 |
| `SubagentStop` | agent_id, agent_type, last_assistant_message | o (exit 2) | サブエージェント完了後 |
| `TeammateIdle` | チームメイト情報, コンテキスト使用量 | o (exit 2) | チームメイトがアイドル前 |
| `TaskCompleted` | タスク情報, ステータス | o (exit 2) | タスク完了マーク時 |

exit code 2 で操作をブロックし、フィードバックをエージェントに送信。

---

## 10. 設計パターン

### パターン 1: 読み取り専用レビュアー

```yaml
---
name: code-reviewer
description: Reviews code for quality and correctness. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
model: sonnet
maxTurns: 15
---

You are a senior code reviewer...
```

変更権限なし。分析とフィードバックのみ。

### パターン 2: 隔離ワーカー (worktree)

```yaml
---
name: experimental-refactor
description: Refactor code in isolated worktree
isolation: worktree
model: sonnet
---
```

リスクのある変更を隔離実行。変更がなければ worktree は自動クリーンアップ。

### パターン 3: バックグラウンド実行

```yaml
---
name: test-runner
description: Run test suite in background
background: true
tools: Bash, Read
---
```

メイン会話をブロックせず並行実行。権限プロンプトは事前承認済みのみ通過。

### パターン 4: メモリ付き専門エージェント

```yaml
---
name: architecture-advisor
description: Architectural decisions advisor with project memory
model: opus
memory: project
effort: high
---

You are a senior architect. Consult your memory for prior decisions.
Update memory with new architectural patterns and decisions.
```

### パターン 5: MCP サーバー付きエージェント

```yaml
---
name: db-analyst
description: Analyze database with read-only access
tools: Read, Bash
mcpServers:
  - postgres:
      type: stdio
      command: npx
      args: ["pg-cli-mcp"]
---
```

### パターン 6: サブエージェント生成制限

```yaml
tools: Agent(worker, researcher), Read, Bash
```

`worker` と `researcher` のみ生成可能。`Agent` を省略で全ブロック。

---

## 11. ベストプラクティス

### 設計

- 1エージェント = 1専門領域。汎用エージェントは避ける
- description に「いつ使うか」を明記。"Use proactively after..." のパターンが効果的
- ツールアクセスは最小限。レビュアーに Write 権限は不要
- `.claude/agents/` を git 管理してチーム共有

### メモリ

- デフォルトで `project` スコープ (共有可能、バージョン管理)
- エージェントプロンプトにメモリの参照・更新指示を含める
- `MEMORY.md` が肥大化しないよう 200 行以内を維持

### チーム

- チームメイトには spawn プロンプトでタスク固有のコンテキストを渡す
- 各チームメイトが異なるファイルを担当するようタスクをサイジング
- 3-5 人で構成 (6 人超は収穫逓減)
- 終了時はチームメイトを先にシャットダウン、その後クリーンアップ

### サブエージェント

- 調査や分析など、メイン会話のコンテキストを消費したくない操作に使用
- 長時間実行のサブエージェントはリスタートより SendMessage で継続
- 冗長な操作 (テスト、ドキュメント生成) はサブエージェントに委譲

### コスト管理

| 種類 | コスト | 推奨用途 |
|------|--------|---------|
| Subagent (Explore) | 低: Haiku, サマリー返却 | 高速コードベース探索 |
| Subagent (general) | 中: フルコンテキスト | 集中タスク |
| Agent Team | 高: 各メンバー = 別セッション | 複雑な並列作業 |

---

## 12. アンチパターン

| アンチパターン | 問題 | 対策 |
|--------------|------|------|
| 曖昧な description | Claude が委譲タイミングを判断できない | 具体的なトリガー条件と専門領域を明記 |
| ツール過剰付与 | 専門化の意味がない | ホワイトリストで必要最小限に |
| tools と disallowedTools の混在 | 動作が不明瞭 | どちらか一方のみ使用 |
| チームメイトへのコンテキスト不足 | 情報収集にターンを浪費 | spawn プロンプトに十分な背景情報を含める |
| サブエージェントのネスト試行 | サポートされていない | メイン会話でエージェントを順次呼び出し |
| メモリ設定のみで指示なし | エージェントがメモリを活用しない | プロンプトに参照・更新の明示的指示を含める |
| チームの非グレースフル終了 | リソースが不整合に | 先にチームメイト停止、その後クリーンアップ |
| `maxTurns` 未設定 | エージェントの暴走リスク | 適切なターン上限を設定 |

---

## 13. ファイル構成リファレンス

### プロジェクトレベル

```
.claude/
├── agents/                    # プロジェクトエージェント (git 管理)
│   ├── code-reviewer.md
│   ├── security-reviewer.md
│   └── debugger.md
├── agent-memory/              # エージェントメモリ (git 管理)
│   ├── code-reviewer/
│   │   └── MEMORY.md
│   └── security-reviewer/
│       └── MEMORY.md
└── agent-memory-local/        # ローカルメモリ (gitignore)
```

### ユーザーレベル

```
~/.claude/
├── agents/                    # 個人エージェント
├── agent-memory/              # 個人メモリ
└── teams/                     # チーム設定
    └── {team-name}/
        └── config.json
```

---

## 参考リンク

- [Subagents Guide](https://code.claude.com/docs/en/sub-agents.md)
- [Agent Teams](https://code.claude.com/docs/en/agent-teams.md)
- [Memory](https://code.claude.com/docs/en/memory.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)
- [Best Practices](https://code.claude.com/docs/en/best-practices.md)
- [Settings Reference](https://code.claude.com/docs/en/settings.md)
