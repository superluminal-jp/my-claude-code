# 他環境での導入手順

このリポジトリの内容を別のマシンや環境の `~/.claude` で使う手順です。

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

上書きせずにマージする場合（既存の rules / skills 等は残し、このリポジトリのファイルで**同名のものだけ**更新）:

```bash
rsync -av --exclude='.git' ./ ~/.claude/
```

- `~/.claude/settings.local.json` などローカル専用の設定はリポジトリに含まれていないため、そのまま残ります。
- 同名ファイルはリポジトリ側で上書きされます。必要なら事前にバックアップを取ってください。

### 4. プラグインについて

このリポジトリには `plugins/` を含めていません。他環境では Claude Code のプラグイン機能から必要なプラグインを再インストールしてください。

### 5. ローカルだけの設定（任意）

環境ごとの上書き（許可リストやツール設定など）は `~/.claude/settings.local.json` に記載できます。このファイルはリポジトリに含めていないため、各環境で自由に編集してかまいません。

---

**運用の目安**: 設定を更新したらこのリポジトリに push し、他環境では `git pull` のあと `rsync -av --exclude='.git' ./ ~/.claude/` で再度同期できます。
