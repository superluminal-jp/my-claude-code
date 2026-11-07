# MCP サーバー — 背景と参照先

このリポジトリは MCP サーバーをユーザー設定に取り込まない。`install.sh` は MCP サーバーを登録も削除もせず、MCP サーバーを同梱するプラグイン（`github` / `deploy-on-aws` / `microsoft-docs`）もインストールしない。必要なサーバーは各ユーザーが自分で登録する（手順は README の「MCP Servers」節、判断の経緯は [ADR-0016](adr/0016-do-not-install-mcp-servers-at-user-scope.md)）。`.claude/` 配下のルールとスキルも、特定の MCP サーバー名を前提にしない。ただし `.claude/settings.json` は、使わないと決めたサーバーを読み込ませない設定を持つ（§5、[ADR-0021](adr/0021-block-mcp-servers-by-settings.md)）。

`.mcp.json` は、このリポジトリ内で作業するときのプロジェクトスコープ定義であり、ユーザーが自分で登録するときの参照カタログでもある。本書はその背景（`.mcp.json` に何が書けるのか、各サーバーの情報がどこから来ているのか、サーバーを増やしたとき何を更新するのか、どのサーバーを止めているのか）を持つ。

本書は `.claude/rules/` にも `.claude/skills/` にもないため自動ロードされない。読むのは人間で、Claude が読むのは必要になったときだけである。

## 1. `.mcp.json` に書けること、書けないこと

接続定義は `.mcp.json` にある。持てるのは**接続のためのフィールドだけ**で、`description` や `when_to_use` に相当するものは存在しない [1]。

| 用途 | フィールド |
|---|---|
| 転送方式 | `type`（`http` / `sse` / `stdio` / `ws`） |
| 接続先 | `url`（HTTP 系）、`command` / `args`（stdio） |
| 認証 | `headers`、`headersHelper`、`oauth`、`env` |
| 挙動 | `timeout`、`alwaysLoad` |

つまり **「このサーバーをいつ呼ぶべきか」を `.mcp.json` から渡す手段はない**。個々の MCP サーバー定義はスキルの `description` / `when_to_use` フロントマターに相当するものを持てない。いつ呼ぶかの手がかりは、サーバー自身が返す `instructions` とツール説明に頼ることになる（次節）。

## 2. Claude Code が実際に受け取るもの

接続後、サーバー側から protocol 経由で 2 種類の情報が来る。

| 経路 | 中身 | 書くのは |
|---|---|---|
| `tools/list` | ツール名、説明、入力スキーマ | サーバー作者 |
| `initialize` レスポンスの `instructions`（任意） | サーバー全体の使い方。Claude Code は "MCP Server Instructions" として注入する | サーバー作者 |

`instructions` は MCP 仕様で `InitializeResult` の任意フィールドとして定義されている [2]。**サーバー作者が書くもので、利用者が手元で補うことはできない。**

さらに tool search が既定で有効なため、ツール**名**はコンテキストにあるが、説明とスキーマは入っていない。必要になった時点で ToolSearch が取得する [1]。`aws-research/SKILL.md` が「利用可能なツール発見の仕組みを使ってから、提供元のドキュメントが手に入らないと判断せよ」とだけ書き、サーバー名を挙げないのはこの挙動に対応している。どのサーバーが入っているかはユーザーごとに異なる。

`alwaysLoad: true` を設定すると、そのサーバーだけ遅延読み込みから除外され、初回ターンから完全なスキーマが載る [1]。設定側から「把握の度合い」を上げられる唯一のレバーだが、内容そのものを足すことはできない。

## 3. 各サーバーのベンダー公式リファレンス

`.mcp.json` に載せている各サーバーの裏取り先。

| サーバー | ベンダー公式リファレンス |
|---|---|
| `aws-documentation` | <https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/> |
| `aws-knowledge` | <https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/> |
| `google-developer-knowledge` | <https://developers.google.com/knowledge/mcp> |
| `microsoft-learn` | <https://learn.microsoft.com/training/support/mcp> |
| `wolfram` | <https://www.wolfram.com/artificial-intelligence/mcp/cloud/wolfram-mcp-cloud/> |

stdio の 1 件（`aws-documentation`）は PyPI のパッケージメタデータ（`https://pypi.org/pypi/<package>/json` の `project_urls`）から取得した。HTTP の 4 件はベンダーの公式ドキュメントページ。`aws-knowledge` の URL のみ、掲載一覧が返した末尾スラッシュなしの形に、他と揃えてスラッシュを補っている。

## 4. サーバーを追加・削除したとき

`.mcp.json` を変更したら、次の2つを同じ変更で更新する。自動チェックは存在しない（`docs/adr/0007-remove-scripts.md` で整合性チェックスクリプトを撤去済み）。

1. **本書の表** — ベンダー公式リファレンスを追加・削除する。stdio なら PyPI メタデータ、HTTP ならベンダーの公式ページから取る。推測で URL を書かない。
2. **README / README.ja の「MCP Servers」節** — ユーザーが自分で実行する `claude mcp add -s user …` のコマンド例。

`.claude/` 配下のルールとスキルにはサーバー名を書かない。ユーザーが入れていないサーバーを前提にした指示になるためである。止めるサーバーを増やす・減らすときは、`.claude/settings.json` のキー、§5 の表、`tests/run-sandbox-settings.sh` の MCP-* を同じ変更で更新する。

## 5. 止めているサーバーと、棚卸しの結果

`.claude/settings.json` は、次のサーバーを、どこで定義されていても読み込ませない。ユーザー設定から効くキーだけを使う（`deniedMcpServers` と `disableClaudeAiConnectors` はどの設定ファイルからも効き、`syncClaudeAiPlugins` はユーザー・ローカル・管理の設定から効く）[1]。

| 止めるもの | キー | 理由 |
|---|---|---|
| GitHub がホストする MCP サーバー | `deniedMcpServers` の `serverUrl: https://api.githubcopilot.com/*` | 使っていない。GitHub の作業は `gh` CLI で足りる |
| `github` プラグイン | `enabledPlugins` の `github@claude-plugins-official: false` | 上のサーバーを同梱するだけのプラグインである |
| `bedrock-agentcore` | `deniedMcpServers` の `serverName` と `serverCommand` | Claude Code が持つ AWS の認証情報で、AWS の実際のリソースを作成・変更・削除し、AWS でコードを実行する。起動のたびに `uvx …@latest` で最新版を実行する |
| claude.ai のコネクタ（Gmail、Google Calendar、Google Drive、Notion、Moneytree、Claude Docs、Wolfram） | `disableClaudeAiConnectors: true` | 私的なデータと外部の文章が Bash と同じセッションにそろうと、プロンプトインジェクションでデータを持ち出す経路になる |
| claude.ai から同期されるプラグイン（`productivity`、`pdf-viewer`） | `syncClaudeAiPlugins: false` | SaaS の MCP サーバー（Slack、Notion、Asana、Linear、Atlassian、monday、ClickUp）を、さらにすべてのセッションに持ち込む。`false` にすると、同期済みのものも `~/.claude/plugins/.trash/` へ移されて読み込まれない |

2026-11-07 の棚卸しで残したもの（ドキュメントの検索か計算に使う）:

| サーバー | 定義の場所 | 注意 |
|---|---|---|
| `aws-knowledge` | ユーザー登録、`.mcp.json`、`deploy-on-aws` プラグイン（`awsknowledge`） | HTTP、認証なし |
| `aws-documentation` | ユーザー登録、`.mcp.json` | 起動のたびに `uvx …@latest` で最新版を実行する |
| `strands-agents` | ユーザー登録 | 起動のたびに `uvx …@latest` で最新版を実行する |
| `google-developer-knowledge` | ユーザー登録、`.mcp.json` | API キーを環境変数 `GOOGLE_DEV_KNOWLEDGE_API_KEY` から渡す |
| `microsoft-learn` | ユーザー登録、`.mcp.json`、`microsoft-docs` プラグイン | HTTP、認証なし。2か所で同じサーバーを定義している |
| `wolfram` | ユーザー登録、`.mcp.json` | 計算の内容を Wolfram に送る |
| `deploy-on-aws`（`awsiac`、`awspricing`） | プラグイン | 起動のたびに `uvx …@latest` で最新版を実行する。AWS の API を、Claude Code の環境の AWS の認証情報で呼ぶ。Bedrock のセッションでは Bedrock 用のアカウントになる（[ADR-0020](adr/0020-enable-sandbox-by-default.md)） |

MCP サーバーはサンドボックスの外で動く。`uvx …@latest` で起動するサーバーは、公開されたばかりの悪意ある版も、起動のたびにサンドボックスの制限なしに実行する。版を固定するかどうかは、各ユーザーが自分の登録で決める（このリポジトリは登録しない。ADR-0016）。

## References

1. Claude Code — MCP: <https://code.claude.com/docs/en/mcp>
2. MCP specification — Lifecycle, `InitializeResult.instructions`: <https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle>
