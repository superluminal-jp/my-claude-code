# my-claude-code

Claude Code のユーザーレベル設定を Git で管理するリポジトリです。すべてのプロジェクトに適用される `CLAUDE.md` 1 本、ルール 4 本、サブエージェント 1 本を置き、`bash install.sh` で `~/.claude/` にコピーします。

English: [README.md](README.md)

## インストール

```sh
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
bash install.sh
```

インストールに必要なものは Bash だけです。検査の実行には Python 3 も必要です。インストール後に Claude Code の新しいセッションを開始し、`/context` または `/memory` でファイルが読み込まれたことを確認してください。

`install.sh` は `~/.claude/` の下の 3 つのパスを、`harness/` と完全に一致するように置き換えます。

| パス | 動作 |
|---|---|
| `CLAUDE.md` | 置き換える |
| `rules/` | 置き換える。ここで削除したルールはインストール先からも消える |
| `agents/` | 置き換える。ここで削除したエージェントはインストール先からも消える |

`~/.claude/` のそれ以外には触れません。`settings.json` と `skills/` も対象外で、権限、サンドボックス、フック、プラグイン、MCP サーバー、スキルはこのリポジトリでは管理しません。別のディレクトリにインストールするには `CLAUDE_CONFIG_DIR` を指定します。

この 3 つのパスに自分のファイルがすでにある場合は、上書きされるので先にバックアップしてください。このリポジトリの以前の版は、`~/.claude/skills/` へのスキルと `~/.claude/commands/` へのコマンドのインストール、`~/.claude/settings.json` へのキーのマージ（モデル、権限、サンドボックス、フック、MCP サーバーの一覧）、プラグインのインストールも行っていました。この版はそれらを削除しません。不要なものは自分で削除してください。特に、削除済みのスキルの下のスクリプトを呼ぶ `settings.json` のフックは、何もせずに終わります。

## `harness/` の内容

| 種類 | 読み込まれるとき | ここでの用途 |
|---|---|---|
| `CLAUDE.md` | 毎セッション | 作業の取り決め。始める前に決めること、進め方、報告前に確かめること |
| ルール | 毎セッション | 伝え方、安全、委任に関する常時の習慣と、従う標準の指定 |
| サブエージェント | 委任されたとき、独自のコンテキストで | 出力が長い作業や、独立性が必要な作業をメインの会話から切り離す |

### 方針: 標準は名前を挙げる

このハーネスは、確立された標準の中身を書き写さず、名前を挙げます。Claude は PEP 8、Conventional Commits、C4 モデルを既に知っているので、ルールにはどの標準を使うかと、どの標準にも書かれていないことだけを書きます。より具体的な指示は、同じ誤りを 2 回見たときに足します。毎セッション読み込まれる分量には 16,000 バイトの上限を設け、検査で守らせています。

### ルール

| ルール | 内容 |
|---|---|
| `communication.md` | 答えを先に、根拠をその下に、用語は初めて読む人向けに定義する |
| `delegation.md` | サブエージェントに任せる場面、依頼の書き方、報告をどこまで信頼するか |
| `safety.md` | 事前に承認が必要な操作、秘密情報・個人情報・信頼できない内容の扱い |
| `standards.md` | プロジェクトが決めていない場合に従う確立された標準（コード、API、クラウドと AI、セキュリティ、文書、問題の定義、Git と GitHub）と、どの標準にもない少数の事実 |

### サブエージェント

| サブエージェント | ツール | 用途 |
|---|---|---|
| `independent-reviewer` | Read、Grep、Glob | 作成者の推論を見ずに、ファイルだけからレビューする |

検索、検査の実行、一般的な委任作業には、Claude Code 組み込みの `Explore` と `general-purpose` エージェントを使い、`rules/delegation.md` に沿って依頼します。独自のサブエージェントは、ツールの制限そのものが役に立つ場合だけ残しています。レビュー用のエージェントは、編集もコマンド実行もできません。

## 意図的に含めていないもの

- **`settings.json`。** `/config` を使うか、`~/.claude/settings.json` を直接編集して管理してください。
- **スキル。** このリポジトリが以前スキルとして持っていた手順は、どれも名前のある標準かフレームワークだったので、いまは `rules/standards.md` の 1 行になっています。
- **仕様策定と開発プロセスのワークフロー。** Spec Kit と AI-DLC は、使うプロジェクトごとに導入します。このハーネスはプロジェクト側のワークフローに従い、同じ内容を重ねて持ちません。
- **強制。** `CLAUDE.md` とルールの指示は Claude が読む指針であり、保証ではありません。例外なく守らせたいことは、権限設定またはフックに置きます。

## 開発

```sh
bash tests/run.sh
```

`harness/` のすべてのファイルを Claude Code が読む形式（front matter のフィールド、必須のフィールド、毎セッション読み込まれる分量）に照らして検査し、一時ディレクトリに対して `install.sh` を実行します。CI も同じコマンドを Ubuntu と macOS で実行します。

`harness/` を編集し、検査を実行し、`bash install.sh` を実行してから、新しいセッションで変更を使います。このリポジトリの規約は [CLAUDE.md](CLAUDE.md) にあります。

## 設計の根拠

構成は、2026-11-21 に読んだ Claude Code のドキュメントに従っています。

- [Memory: CLAUDE.md とルール](https://code.claude.com/docs/en/memory) - `CLAUDE.md` は 200 行未満にする。`paths` のないルールは毎セッション読み込まれる。
- [Subagents](https://code.claude.com/docs/en/sub-agents) - 独自のサブエージェントは、コンテキストの分離か、ツールを制限した専門の役割のために作る。
- [Best practices](https://code.claude.com/docs/en/best-practices) と [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - どの仕組みを何に使うか。ガードレールはフックに置く。
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Claude がまだ知らないことだけを足す。
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - すべきことを書き、理由を説明し、強調表現を避ける。
