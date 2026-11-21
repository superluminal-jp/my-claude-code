# my-claude-code

Claude Code のユーザーレベル設定を Git で管理するリポジトリです。すべてのプロジェクトに適用される `CLAUDE.md`、ルール、スキル、サブエージェントを置き、`bash install.sh` で `~/.claude/` にコピーします。

English: [README.md](README.md)

## インストール

```sh
git clone git@github.com:superluminal-jp/my-claude-code.git
cd my-claude-code
bash install.sh
```

必要なものは Bash だけです。インストール後に Claude Code の新しいセッションを開始し、`/context` または `/memory` でファイルが読み込まれたことを確認してください。

`install.sh` は `~/.claude/` の下の 4 つのパスを、`harness/` と完全に一致するように置き換えます。

| パス | 動作 |
|---|---|
| `CLAUDE.md` | 置き換える |
| `rules/` | 置き換える。ここで削除したルールはインストール先からも消える |
| `skills/` | 置き換える。ただし Claude アプリが管理する `skills/synced/` は保持する |
| `agents/` | 置き換える |

`~/.claude/` のそれ以外には触れません。`settings.json` も対象外で、権限、サンドボックス、フック、プラグイン、MCP サーバーはこのリポジトリでは管理しません。別のディレクトリにインストールするには `CLAUDE_CONFIG_DIR` を指定します。

この 4 つのパスに自分のファイルがすでにある場合は、上書きされるので先にバックアップしてください。

## `harness/` の内容

Claude Code が各種類のファイルを読み込むタイミングに合わせて使い分け、毎セッション必要なものだけが毎セッションのコンテキストを消費するようにしています。

| 種類 | 読み込まれるとき | ここでの用途 |
|---|---|---|
| `CLAUDE.md` | 毎セッション | 作業の取り決め。始める前に決めること、進め方、報告前に確かめること |
| ルール | 毎セッション | 伝え方と安全に関する常時の習慣と、従う標準の指定 |
| スキル | 説明文は毎セッション、本文は使うとき | ある種類の作業の手順 |
| サブエージェント | 委任されたとき、独自のコンテキストで | 出力が長い作業や、独立性が必要な作業をメインの会話から切り離す |

### ルール

ルールは標準の中身を書き写さず、標準の名前を挙げます。Claude は PEP 8 や Conventional Commits を既に知っているので、どの標準を使うかと、どの標準にも書かれていないことだけを書きます。より具体的な指示は、同じ誤りを 2 回見たときに足します。

| ルール | 内容 |
|---|---|
| `communication.md` | 答えを先に、根拠をその下に、用語は初めて読む人向けに定義する |
| `safety.md` | 事前に承認が必要な操作、秘密情報・個人情報・信頼できない内容の扱い |
| `standards.md` | プロジェクトが決めていない場合に従う確立された標準（コード、文書、構成図、決定の記録、テスト、Git と GitHub、セキュリティ、ログ）と、どの標準にもない少数の事実 |

### スキル

| スキル | 用途 |
|---|---|
| `clarify-intent` | 作業の前に、依頼の読み方を 1 つに合意する |
| `define-problem` | 問題を、原因や解決策と切り分けた検証可能なギャップとして述べる |

各スキルは、依頼が説明文に一致すると自動で使われます。`/<スキル名>` で直接呼び出すこともできます。

### サブエージェント

| サブエージェント | ツール | 用途 |
|---|---|---|
| `check-runner` | Bash、Read、Grep、Glob | テスト、ビルド、リンターを実行し、終了コードと失敗箇所の原文を報告する |
| `independent-reviewer` | Read、Grep、Glob | 作成者の推論を見ずに、ファイルだけからレビューする |

検索と一般的な委任作業には、Claude Code 組み込みの `Explore` と `general-purpose` エージェントを使います。

## 意図的に含めていないもの

- **`settings.json`。** `/config` を使うか、`~/.claude/settings.json` を直接編集して管理してください。
- **仕様策定と開発プロセスのワークフロー。** Spec Kit と AI-DLC は、使うプロジェクトごとに導入します。このハーネスはプロジェクト側のワークフローに従い、同じ内容を重ねて持ちません。
- **強制。** `CLAUDE.md` とルールの指示は Claude が読む指針であり、保証ではありません。例外なく守らせたいことは、権限設定またはフックに置きます。

## 開発

```sh
bash tests/run.sh
```

`harness/` のすべてのファイルを Claude Code が読む形式（front matter のフィールド、名前と説明文の上限、本文の長さ、参照先ファイルの存在）に照らして検査し、一時ディレクトリに対して `install.sh` を実行します。CI も同じコマンドを実行します。

`harness/` を編集し、検査を実行し、`bash install.sh` を実行してから、新しいセッションで変更を使います。このリポジトリの規約は [CLAUDE.md](CLAUDE.md) にあります。

## 設計の根拠

構成は、2026-11-21 に読んだ Claude Code のドキュメントに従っています。

- [Memory: CLAUDE.md とルール](https://code.claude.com/docs/en/memory) - `CLAUDE.md` は 200 行未満にする。ルールの front matter で読まれるのは `paths` だけ。`paths` 付きのルールは一致するファイルに触れたときに読み込まれる。
- [Skills](https://code.claude.com/docs/en/skills) と [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - 説明文は三人称で、何をするかといつ使うかを書く。本文は 500 行未満。参照ファイルは 1 階層まで。
- [Subagents](https://code.claude.com/docs/en/sub-agents) - 独自のサブエージェントは、コンテキストの分離か、ツールを制限した専門の役割のために作る。
- [Best practices](https://code.claude.com/docs/en/best-practices) と [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - どの仕組みを何に使うか。ガードレールはフックに置く。
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - すべきことを書き、理由を説明し、強調表現を避ける。
