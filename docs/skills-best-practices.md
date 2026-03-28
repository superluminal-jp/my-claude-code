# Claude Code Skills ベストプラクティス

**目的**: Skills の設計・実装・運用に関する公式仕様とベストプラクティスをまとめたリファレンス。
**対象バージョン**: Claude Code v1.0.33+
**最終更新**: 2026-03-28

---

## 1. Skills とは

Skills は Claude Code の拡張コンポーネントで、YAML フロントマターと Markdown 指示で構成される。[Agent Skills](https://agentskills.io) オープンスタンダードに準拠し、Claude Code 固有の拡張を持つ。

**Skills の役割**:
- 再利用可能なワークフローや手順を定義
- Claude が文脈に応じて自動起動、またはユーザーが `/name` で明示的に呼び出し
- ツールアクセスやモデルの制御が可能

**Skills vs Rules vs Agents**:

| 項目 | Rules | Skills | Agents |
|------|-------|--------|--------|
| 役割 | 常時適用される制約・標準 | オンデマンドのワークフロー・知識 | 隔離されたコンテキストでのタスク委譲 |
| ロード | 毎セッション (CLAUDE.md 経由) | タスク一致時 or `/name` 呼び出し時 | 委譲時 (subagent spawn) |
| 用途 | 「このリポジトリでは常に X する」 | 「タスク Y にはこの手順を使う」 | 「Z を専門家に委譲して結果を受け取る」 |

---

## 2. フロントマター完全リファレンス

```yaml
---
# ID (任意)
name: my-skill                        # デフォルト: ディレクトリ名。[a-z0-9-]{1,64}
description: 用途と起動条件の説明       # 推奨。Claude の自動起動判定に使用

# 起動制御
user-invocable: true                   # false = Claude のみ起動可、/ メニュー非表示
disable-model-invocation: false        # true = ユーザーのみ起動可、Claude 自動起動不可

# ツール・モデル設定
allowed-tools: Read, Grep, Bash        # 許可ツールのホワイトリスト (カンマ区切り)
model: sonnet                          # sonnet | opus | haiku | inherit | フル ID
effort: high                           # low | medium | high | max (Opus 4.6 のみ)

# 実行コンテキスト
context: fork                          # fork = 隔離されたサブエージェントで実行
agent: Explore                         # context: fork 時に使用するエージェント型

# 引数
argument-hint: "[filename] [format]"   # オートコンプリートに表示

# 条件・自動化
paths: "src/**/*.ts, tests/**/*.test.ts"  # glob パターン。一致時のみ自動起動
shell: bash                            # bash (デフォルト) | powershell

# フック (このスキルのライフサイクルにスコープ)
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
          once: true                   # スキル限定: セッションで1回のみ実行
---
```

### フィールド詳細

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `name` | string | スキル識別子。小文字・数字・ハイフンのみ |
| `description` | string | Claude が自動起動を判定する際に使用。ユーザーが自然に言いそうなキーワードを含める |
| `user-invocable` | bool | `false` で `/` メニュー非表示。Claude のみ自動起動可能 |
| `disable-model-invocation` | bool | `true` でユーザーのみ起動可。デプロイなど意図的な操作に使用 |
| `allowed-tools` | string | ホワイトリスト。指定時はこれ以外のツールが使用不可に |
| `model` | string | モデルオーバーライド。`inherit` でセッションと同じ |
| `effort` | string | 推論努力レベルのオーバーライド |
| `context` | string | `fork` で隔離サブエージェント実行。冗長な出力をメイン会話から分離 |
| `agent` | string | `context: fork` 時のエージェント型 (Explore, Plan, general-purpose, カスタム名) |
| `argument-hint` | string | `/skill-name` 時のオートコンプリートヒント |
| `paths` | string/list | glob パターン。対象ファイル作業時のみ自動起動 |
| `shell` | string | `!command` ブロック実行時のシェル |
| `hooks` | YAML | スキルライフサイクルにスコープされたフック |

### 起動制御の組み合わせ

| 設定 | ユーザー起動 | Claude 自動起動 | `/` メニュー |
|------|:-----------:|:--------------:|:----------:|
| デフォルト | o | o | o |
| `disable-model-invocation: true` | o | x | o |
| `user-invocable: false` | x | o | x |

---

## 3. 動的コンテンツ

### 変数置換

| 変数 | 説明 |
|------|------|
| `$ARGUMENTS` | スキルに渡された全引数 |
| `$ARGUMENTS[N]` / `$N` | N 番目の引数 (0始まり) |
| `${CLAUDE_SESSION_ID}` | セッション UUID |
| `${CLAUDE_SKILL_DIR}` | スキルディレクトリの絶対パス |

### シェルコマンド前処理 (`!command`)

````markdown
- **Diff**: !`gh pr diff`
- **Files**: !`gh pr diff --name-only`
````

`!command` は Claude が見る前に実行され、出力で置換される。動的データの注入に使用。

---

## 4. ディレクトリ構成

### 標準レイアウト

```
.claude/skills/
├── my-skill/
│   ├── SKILL.md              # 必須: フロントマター + 指示
│   ├── reference.md          # 詳細リファレンス (オンデマンド読込)
│   ├── examples.md           # 使用例
│   └── templates/            # テンプレート
│       └── output-template.md
└── another-skill/
    └── SKILL.md
```

### スコープ優先度 (高い順)

1. **Enterprise 設定** (最高)
2. **Personal** (`~/.claude/skills/`)
3. **Project** (`./.claude/skills/`)
4. **Plugin** (`--plugin-dir` 経由、名前空間付き)

同名スキルは高優先度が勝つ。Plugin スキルは常に名前空間付き (`/plugin-name:skill-name`)。

### コンテキストバジェット

スキルの description は常にコンテキストに含まれる (自動起動判定のため)。フルコンテンツは起動時のみ読込。

- バジェット上限: コンテキストウィンドウの 2% (最小 16,000 文字)
- 変更: `export SLASH_COMMAND_TOOL_CHAR_BUDGET=32000`

---

## 5. 設計パターン

### パターン 1: リファレンス知識 (Claude のみ)

```yaml
---
name: api-conventions
description: API design patterns for this codebase
user-invocable: false
---

## REST Conventions
- RESTful naming
- Consistent error format: { "error": { "code": "...", "message": "..." } }
```

Claude がコンテキストに応じて自動読込。ユーザーからは見えない。

### パターン 2: ユーザー起動タスク

```yaml
---
name: deploy
description: Deploy to production
disable-model-invocation: true
argument-hint: "[environment]"
allowed-tools: Bash
---

Deploy to $0:
1. Run tests
2. Build
3. Deploy
```

ユーザーが `/deploy staging` で明示的に呼び出し。Claude は自動起動しない。

### パターン 3: 隔離実行

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly...
```

冗長な出力をメイン会話から分離。結果のみサマリーで返却。

### パターン 4: 引数付きスキル

```yaml
---
name: migrate-component
description: Migrate a component between frameworks
argument-hint: "[component] [from] [to]"
---

Migrate $0 from $1 to $2.
```

呼び出し: `/migrate-component SearchBar React Vue`

### パターン 5: スコープ付きフック

```yaml
---
name: secure-bash
description: Run bash commands with security validation
allowed-tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

フックはスキル実行中のみ有効。終了後に自動解除。

### パターン 6: 拡張思考 (ultrathink)

スキル本文に "ultrathink" を含めると拡張思考が有効になる。

---

## 6. ベストプラクティス

### description を具体的に書く

```yaml
# x 曖昧
description: A helpful tool

# o 具体的
description: Refactor code for performance. Use when optimizing critical functions or when user asks "how can I speed this up?"
```

Claude の自動起動精度は description の質に直結する。

### SKILL.md は 500 行以内

詳細なリファレンスやテンプレートは別ファイルに分離し、SKILL.md から参照:

```markdown
For details, see [reference.md](reference.md).
For examples, see [examples.md](examples.md).
```

### ツールアクセスは最小限に

```yaml
# x 過剰
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch

# o 必要最小限
allowed-tools: Read, Grep, Glob
```

### Skills と Rules を混同しない

常時適用される制約は Rules (`CLAUDE.md` / `.claude/rules/`) に置く。Skills はオンデマンド。

```
常時適用 → Rules
オンデマンド → Skills
タスク委譲 → Agents
```

---

## 7. アンチパターン

| アンチパターン | 問題 | 対策 |
|--------------|------|------|
| 曖昧な description | Claude が起動タイミングを判断できない | ユーザーの自然な発話を想定して具体的に書く |
| 巨大な SKILL.md | コンテキスト圧迫 | 500 行以内。補足は別ファイル |
| `$ARGUMENTS` のドキュメント不足 | ユーザーが何を渡すか分からない | `argument-hint` で明示 |
| プロンプト内の直接シェルコマンド | Claude が Bash ツールとして実行してしまう | `!command` プリプロセッシングを使用 |
| 制約を Skills に入れる | 起動されないと適用されない | Rules に移動 |
| description の長文化 | 毎セッション 5KB+ のコンテキスト消費 | 1-2 文で簡潔に |

---

## 8. トラブルシューティング

### スキルが起動しない

1. description がユーザーの意図とマッチしているか確認
2. `disable-model-invocation: true` になっていないか確認
3. `paths` 指定がある場合、現在のファイルがパターンに一致するか確認
4. `/skill-name` で直接呼び出してテスト

### スキルが頻繁に誤起動する

- description をより具体的にする
- `disable-model-invocation: true` で手動起動のみにする

### 補足ファイルが読み込まれない

SKILL.md から明示的に参照する:
```markdown
For configuration details, see [reference.md](reference.md).
```

### バジェット超過で一部スキルが見えない

```bash
export SLASH_COMMAND_TOOL_CHAR_BUDGET=32000
```

---

## 9. Plugins によるスキル配布

### Plugin 構造

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # { "name": "...", "description": "...", "version": "1.0.0" }
└── skills/
    └── code-review/
        └── SKILL.md
```

Plugin スキルは名前空間付きで呼び出し: `/my-plugin:code-review`

テスト: `claude --plugin-dir ./my-plugin`

---

## 参考リンク

- [Claude Code Skills](https://code.claude.com/docs/en/skills.md)
- [Subagents](https://code.claude.com/docs/en/sub-agents.md)
- [Hooks](https://code.claude.com/docs/en/hooks.md)
- [Plugins](https://code.claude.com/docs/en/plugins.md)
- [Agent Skills Standard](https://agentskills.io)
