# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`.claude/` ディレクトリ全体を `~/.claude/` に同期することで、settings/rules/skills/hooks/memory を
マシン上の全プロジェクトで共通適用できます。

英語版: [README.md](README.md)

## このリポジトリで提供するもの

- **`.claude/CLAUDE.md`**: 常時メモリ（原則、応答スタイル、skill インデックス、MCP 参照）
- **`.claude/settings.json`**: モデル既定値、権限ルール、hook 設定
- **`.claude/rules/`**: 常時読み込まれる共通ルール（安全性、ツール選択、確認ルール、MCP カタログ）
- **`.claude/skills/`**: 必要時に読み込まれるプレイブック
  - `development`: 実装作業（TDD/SDD、品質、安全、ドキュメント同期）
  - `advisor`: 分析・意思決定支援
  - `deliverables`: 文書/資料/翻訳など成果物作成
  - `requirements`: 要件定義・受け入れ条件の明確化
- **`.claude/hooks/pre-bash.sh`**: 破壊的コマンドや危険な Bash を事前ブロック
- **`.claude/hooks/user-prompt-submit.sh`**: キー/トークン等の秘密情報を含むプロンプト送信をブロック

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
