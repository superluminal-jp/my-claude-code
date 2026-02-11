# 他環境での導入手順

このリポジトリの内容を別のマシンや環境の `~/.claude` で使う手順です。

Agent teams（実験機能）は settings.json の env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS で有効化されています。同期後そのまま利用できます。

## 前提

- Claude Code が利用可能な環境
- `git` がインストール済み

## 手順

### 1. リポジトリをクローン

```bash
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
```

### 2. 既存の `~/.claude` がない場合

リポジトリの内容をそのまま `~/.claude` にコピーします。

```bash
mkdir -p ~/.claude
rsync -av --exclude='.git' ./ ~/.claude/
```

または:

```bash
cp -r ./* ~/.claude/
cp .gitignore ~/.claude/  # 任意: ローカルで .gitignore を維持する場合
```

### 3. 既存の `~/.claude` がある場合

#### 3a. 同名ファイルだけ上書き（マージ）

既存の `~/.claude` にリポジトリを重ね、**同名のファイルだけ**リポジトリの内容で上書きします。リポジトリにないファイル（独自の rules や skills など）は `~/.claude` に残ります。

```bash
rsync -av --exclude='.git' ./ ~/.claude/
```

- `~/.claude/settings.local.json` などローカル専用の設定はリポジトリに含まれていないため、そのまま残ります。
- 同名ファイルはリポジトリ側で上書きされます。必要なら事前にバックアップを取ってください。

#### 3b. 上書きしてマージ（リポジトリと完全に揃える）

リポジトリの内容で `~/.claude` を**完全に上書き**し、リポジトリにないファイルは `~/.claude` から削除します。実質的に「リポジトリと同じ状態」にしたいときに使います。

```bash
rsync -av --exclude='.git' --delete ./ ~/.claude/
```

- `--delete` により、リポジトリに存在しないファイル・ディレクトリは `~/.claude` から削除されます。
- **事前にバックアップを取ることを強く推奨**します（例: `cp -a ~/.claude ~/.claude.bak`）。`settings.local.json` などローカル専用の設定も消えるため、必要なものは別途退避してください。

> **重要**: `settings.json` のフックは全て `$HOME/.claude/hooks/` を参照しています。rsync による同期が完了していないと、フックが動作しません。

### 4. プラグインについて

このリポジトリには `plugins/` を含めていません。他環境では Claude Code のプラグイン機能から必要なプラグインを再インストールしてください。

### 5. ローカルだけの設定（任意）

環境ごとの上書き（許可リストやツール設定など）は `~/.claude/settings.local.json` に記載できます。このファイルはリポジトリに含めていないため、各環境で自由に編集してかまいません。

---

**運用の目安**: 設定を更新したらこのリポジトリに push し、他環境では `git pull` のあと `rsync -av --exclude='.git' ./ ~/.claude/` で再度同期できます。
