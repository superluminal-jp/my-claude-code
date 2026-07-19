# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`.claude/` ディレクトリ全体を `~/.claude/` に同期することで、settings/rules/skills/hooks/memory を
マシン上の全プロジェクトで共通適用できます。

英語版: [README.md](README.md)

## このリポジトリで提供するもの

- **`.claude/CLAUDE.md`**: 常時メモリ（原則、応答スタイル、skill インデックス、MCP 参照）
- **`.claude/settings.json`**: モデル既定値、権限ルール、hook 設定
- **`.claude/rules/`**: 常時読み込まれる共通ルール（権限/安全性、ツール選択、確認ルール、skill ルーティング、live-documentation、advisor、MCP カタログ）
- **`.claude/skills/`**: 必要時に読み込まれるプレイブック
  - `coder`: 実装作業（TDD/SDD、品質、安全、型安全性、ドキュメント同期）
  - `editor`: 文書/スライド/図表/翻訳など成果物作成
  - `clarifier`: 要件定義・受け入れ条件の明確化（INVEST/Gherkin）
  - `domain-model` / `ubiquitous-language`: DDD ドメインモデル/ユビキタス言語
  - Spec Kit の `speckit-*` スキルはこのリポジトリでは vendoring しない。各プロジェクトで
    `specify init` を実行した際に、`--integration` が指す各エージェントのディレクトリ
    （`.claude/skills/`、`.agents/skills/`、`.cursor/skills/`）配下に生成される
    プロジェクトローカルな成果物で、すべて gitignore 対象（後述「spec-kit のオプトイン」参照）
- **`.claude/hooks/pre-bash.sh`**: 破壊的コマンドや危険な Bash を事前ブロック
- **`.claude/hooks/user-prompt-submit.sh`**: キー/トークン等の秘密情報を含むプロンプト送信をブロック
- **`.claude/hooks/session-start.sh`**: SessionStart（Claude Code on the web 限定）。`post-edit-format.sh` が使う lint ツール（`shellcheck`/`shfmt`/`yamllint`、欠落時は `jq`）を新規リモートコンテナへ導入。冪等・非致命的で、ローカルではスキップ

## ユーザー設定としてインストール

以下を実行してください:

```sh
bash path/to/my-claude-code/install.sh
```

インストーラーは `~/.claude` を同期し、ユーザースコープ MCP を登録/更新します。

### 重要: 上書き置換（削除同期）について

- 次の管理対象は **置換同期** されます:
  - `hooks/`
  - `rules/`
  - `skills/`
  - `CLAUDE.md`
  - `settings.json`
  - `install.sh`
- このリポジトリ側で削除されたファイルは、`~/.claude` 側でも削除されます。
- 個人用ファイルは管理対象外の場所に置くか、別バックアップから再適用してください。

## 代替: `CLAUDE.md` から import

コピーせずに参照する場合:

```markdown
@/absolute/path/to/my-claude-code/.claude/CLAUDE.md
```

## 構成

```text
my-claude-code/
├── CLAUDE.md
├── README.md
├── README.ja.md
├── install.sh
├── scripts/
│   └── check-mcp-consistency.sh
├── .mcp.json
└── .claude/
    ├── CLAUDE.md
    ├── settings.json
    ├── rules/
    ├── skills/
    └── hooks/
```

## 検証

`.mcp.json` / `install.sh` / `.claude/settings.json` / `.claude/rules/mcp.md` を変更したら:

```sh
./scripts/check-mcp-consistency.sh
```

## MCP サーバー

プロジェクトスコープ定義は `.mcp.json` にあります。  
カタログ（transport / バージョン等）は [`.claude/rules/mcp.md`](.claude/rules/mcp.md) を参照してください。

## プロジェクト単位の上書き

ユーザー設定はベースラインです。各プロジェクトの `.claude/settings.json` で拡張/上書きできます。

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": []
  }
}
```

優先順位（高 -> 低）:
managed > local (`.local.json`) > project (`settings.json`) > user (`~/.claude/settings.json`)

### spec-kit のオプトイン

Spec Kit (https://github.com/github/spec-kit) はプロジェクトごとに個別に
インストール・初期化します。このリポジトリや `~/.claude` に vendoring・配布
されるものではありません。プロジェクトごとに一度、以下の手順を実行してください:

```sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
specify self upgrade
specify init --here --force --integration claude
# specify init --here --force --integration codex
# specify init --here --force --integration cursor-agent
specify extension add git
```

- `uv tool install ... @vX.Y.Z` — ブランチ追従ではなく、明示的なリリースタグ
  （`vX.Y.Z` を置き換える）を指定してインストールすることで、再現可能な状態を保ちます。
- `specify self upgrade` — 内蔵のアップデーターで `specify` CLI 自体を
  最新リリースに更新します。
- `specify init --here --force --integration <agent>` — `/speckit.*`
  スラッシュコマンドを、そのプロジェクト自身の `.claude/skills/`（または
  指定した `--integration` に対応するパス。例: `codex` なら
  `.agents/skills/`、`cursor-agent` なら `.cursor/skills/`）配下に
  `speckit-*` スキルとして生成します — プロジェクトローカルな成果物であり、
  生成先のエージェントディレクトリによらずすべて gitignore 対象です
  （`.gitignore` 参照）。同一プロジェクト内で別のエージェントにも導入する
  場合は、`--integration` の値を変えて再実行してください。各コマンドは
  独自のプレイブックを持ちます。`coder` スキルの SDD セクションは
  spec-kit の導入有無にかかわらず適用されます。
- `specify extension add git` — Git Branching Workflow 拡張
  （`/speckit-git.*`）をインストールします。

追加されるコマンド: `speckit.git.feature`、`speckit.git.validate`、
`speckit.git.remote`、`speckit.git.initialize`、`speckit.git.commit`

このプロジェクト単位のワークフローを支える2つのhookがあります(詳細は
[`.claude/hooks/README.md`](.claude/hooks/README.md)):
`recommend-speckit.sh` は、`.specify/` が未導入のプロジェクトで非自明な実装依頼らしき
プロンプトを検知すると `specify init` の導入を提案し、`speckit-expand-update.sh` は
すでに導入済みのプロジェクトの Spec Kit を最新に保ちます — いずれも `/speckit-*`
コマンド実行前だけでなく、セッション開始時にも動作します。
