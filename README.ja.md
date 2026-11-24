# my-claude-code

Claude Code のユーザーレベル設定を Git で管理するリポジトリです。すべてのプロジェクトに適用される `CLAUDE.md` 1 本、ルール 4 本、サブエージェント 1 本を置き、`bash install.sh` で `~/.claude/` にコピーします。これとは別に、プラグイン `writing-check` を置いています。インストールは別の手順です。

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

`~/.claude/` のそれ以外には触れません。`settings.json` と `skills/` も対象外で、権限、サンドボックス、フック、プラグイン、MCP サーバー、スキルは `install.sh` では管理しません。このリポジトリのプラグインは `writing-check` だけで、[`writing-check` プラグイン](#writing-check-プラグイン)に書いたとおり、Claude Code のプラグイン用コマンドでインストールします。別のディレクトリにインストールするには `CLAUDE_CONFIG_DIR` を指定します。

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
| `communication.md` | 答えを先に、根拠をその下に、用語は初めて読む人向けに定義する。複数の手順からなる作業では、先に方法と手順を挙げ、各回答がどの手順にあるかを示す。すべての回答の末尾に前提、仮定、方法を示す |
| `delegation.md` | サブエージェントに任せる場面、依頼の書き方、報告をどこまで信頼するか |
| `safety.md` | 事前に承認が必要な操作、秘密情報・個人情報・信頼できない内容の扱い |
| `standards.md` | プロジェクトが決めていない場合に従う確立された標準（コード、API、クラウドと AI、セキュリティ、文書、問題の定義、Git と GitHub）と、どの標準にもない少数の事実 |

### サブエージェント

| サブエージェント | ツール | 用途 |
|---|---|---|
| `independent-reviewer` | Read、Grep、Glob | 作成者の推論を見ずに、ファイルだけからレビューする |

検索、検査の実行、一般的な委任作業には、Claude Code 組み込みの `Explore` と `general-purpose` エージェントを使い、`rules/delegation.md` に沿って依頼します。独自のサブエージェントは、ツールの制限そのものが役に立つ場合だけ残しています。レビュー用のエージェントは、編集もコマンド実行もできません。

## `writing-check` プラグイン

`plugins/writing-check/` は、ターンが終わる前に文章を 1 回レビューする Claude Code のプラグインです。回答と、そのターンで書いた文書を、次の 3 点で検査します。言葉づかい（日本語では、翻訳調、です・ます体とだ・である体の混在、助詞）、用語（その分野で使われている形か、訳語を作っていないか、同じものを同じ名前で呼んでいるか）、構成（`rules/communication.md` が求めるとおりか）。読み手が誤解する欠陥があれば Claude に差し戻し、Claude は同じターンの中で直します。

### プラグインのインストール

```sh
claude plugin marketplace add /path/to/my-claude-code
claude plugin install writing-check@local-harness
```

プラグインの実行には Python 3 が必要です。Claude Code はこのチェックアウトにあるファイルをそのまま読みます。編集した内容は、次のセッションか `/reload-plugins` の後に有効になり、再インストールは不要です。`install.sh` はプラグインに触れません。削除するには `claude plugin uninstall writing-check@local-harness` を実行します。

### 仕組み

| フック | 型 | 動作 |
|---|---|---|
| `UserPromptSubmit` | command | そのセッションの「書いた文書の一覧」を空にする。これにより、一覧は 1 ターン分になる |
| `PostToolUse`（`Write\|Edit`） | command | 書いたファイルが文書（`.md`、`.mdx`、`.markdown`、`.txt`、`.rst`、`.adoc`）なら、全体を書いたのか一部を編集したのかの印を付けて一覧に加える。モデルは呼ばない |
| `Stop` | agent | レビュー担当のエージェントが、回答、一覧にある文書（5 件まで）、インストール済みの `rules/communication.md` を読み、合格、または直すべき欠陥を返す |

- **差し戻しは 1 ターンに 1 回です。** Claude が差し戻しを受けて続行している間（フックの入力の `stop_hook_active` が true）は、エージェントは何も読まずに合格を返します。このリポジトリに以前あったフックは、差し戻しの繰り返しで Claude が出力を言い直すことを理由に廃止しました。
- **文書は編集のたびではなく、ターンの終わりに検査します。** 差し戻しに応じた編集で `PostToolUse` フックが再び動くのを止める方法が、Claude Code のドキュメントにありません。編集のたびに検査すると、差し戻しを 1 回に抑えられません。
- **費用。** ターンが終わるたびに、エージェントが 1 回動きます。制限時間は 120 秒です。フックではモデルを指定していません。Claude Code のドキュメントによると、その場合 agent 型のフックは、Claude Code がバックグラウンド処理に使うモデルで動きます。文書を書いておらず、回答が一言で済む返事であれば、エージェントは基準を読まずに合格を返します。
- **編集した文書。** 既存のファイルの一部を編集した場合、文章の大半はそのターンより前のものかもしれません。エージェントはそこでは読み手が誤解する欠陥だけを報告し、Claude にはそのターンで書いた文章だけを直すよう伝えます。
- **一覧**は、Claude の設定ディレクトリ（既定では `~/.claude/`）の `writing-check/<session_id>.txt` で、本人だけが読めるディレクトリに置きます。スクリプトもエージェントも、フックの入力にあるトランスクリプトのパスからこのディレクトリを求めます。
- **基準。** 用語と構成は、インストール済みの `rules/communication.md` に照らして判定します。基準を変えるときはこのルールを変えます。言葉づかいの基準は、ルールに書かれていないので、フックのプロンプトに置いています。
- **限界。** agent 型のフックは、Claude Code のドキュメントで experimental（実験的）とされており、仕様が変わる可能性があります。レビューはモデルの判断であり、保証ではありません。

## 意図的に含めていないもの

- **`settings.json`。** `/config` を使うか、`~/.claude/settings.json` を直接編集して管理してください。
- **スキル。** このリポジトリが以前スキルとして持っていた手順は、どれも名前のある標準かフレームワークだったので、いまは `rules/standards.md` の 1 行になっています。
- **仕様策定と開発プロセスのワークフロー。** Spec Kit と AI-DLC は、使うプロジェクトごとに導入します。このハーネスはプロジェクト側のワークフローに従い、同じ内容を重ねて持ちません。
- **強制。** `CLAUDE.md` とルールの指示は Claude が読む指針であり、保証ではありません。例外なく守らせたいことは、権限設定またはフックに置きます。`writing-check` プラグインはここに置いている唯一のフックで、修正を求めるものであり、修正を保証するものではありません。

## 開発

```sh
bash tests/run.sh
```

`harness/` のすべてのファイルを Claude Code が読む形式（front matter のフィールド、必須のフィールド、毎セッション読み込まれる分量）に照らして検査し、`writing-check` プラグインのテストを実行し、一時ディレクトリに対して `install.sh` を実行します。CI も同じコマンドを Ubuntu と macOS で実行します。

`claude plugin validate . --strict` と `claude plugin validate plugins/writing-check --strict` は、プラグインのマニフェストを検査します。この 2 つは Claude Code が必要で、`tests/run.sh` と CI には含めていません。

`harness/` を編集し、検査を実行し、`bash install.sh` を実行してから、新しいセッションで変更を使います。このリポジトリの規約は [CLAUDE.md](CLAUDE.md) にあります。

## 設計の根拠

構成は、2026-11-21 に読んだ Claude Code のドキュメントに従っています。

- [Memory: CLAUDE.md とルール](https://code.claude.com/docs/en/memory) - `CLAUDE.md` は 200 行未満にする。`paths` のないルールは毎セッション読み込まれる。
- [Subagents](https://code.claude.com/docs/en/sub-agents) - 独自のサブエージェントは、コンテキストの分離か、ツールを制限した専門の役割のために作る。
- [Best practices](https://code.claude.com/docs/en/best-practices) と [Extending Claude Code](https://code.claude.com/docs/en/features-overview) - どの仕組みを何に使うか。ガードレールはフックに置く。
- [Hooks](https://code.claude.com/docs/en/hooks) と [Plugins](https://code.claude.com/docs/en/plugins)（2026-11-24 に読んだもの） - `Stop` の agent 型フック、入力の `stop_hook_active`、ローカルのマーケットプレイスからその場で読まれるプラグイン。
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Claude がまだ知らないことだけを足す。
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) - すべきことを書き、理由を説明し、強調表現を避ける。
