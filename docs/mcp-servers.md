# MCP サーバー — 背景と参照先

このリポジトリは MCP サーバーをユーザー設定に取り込まない。`install.sh` は MCP サーバーを登録も削除もせず、MCP サーバーを同梱するプラグイン（`github` / `deploy-on-aws` / `microsoft-docs`）もインストールしない。必要なサーバーは各ユーザーが自分で登録する（手順は README の「MCP Servers」節）。`.claude/` 配下のルールとスキルも、特定の MCP サーバー名を前提にしない。

`.mcp.json` は、このリポジトリ内で作業するときのプロジェクトスコープ定義であり、ユーザーが自分で登録するときの参照カタログでもある。本書はその背景（`.mcp.json` に何が書けるのか、各サーバーの情報がどこから来ているのか、サーバーを増やしたとき何を更新するのか）を持つ。

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

さらに tool search が既定で有効なため、ツール**名**はコンテキストにあるが、説明とスキーマは入っていない。必要になった時点で ToolSearch が取得する [1]。`cloud-platform-research/SKILL.md` が「利用可能なツール発見の仕組みを使ってから、提供元のドキュメントが手に入らないと判断せよ」とだけ書き、サーバー名を挙げないのはこの挙動に対応している。どのサーバーが入っているかはユーザーごとに異なる。

`alwaysLoad: true` を設定すると、そのサーバーだけ遅延読み込みから除外され、初回ターンから完全なスキーマが載る [1]。設定側から「把握の度合い」を上げられる唯一のレバーだが、内容そのものを足すことはできない。

## 3. 各サーバーのベンダー公式リファレンス

`.mcp.json` に載せている各サーバーの裏取り先。

| サーバー | ベンダー公式リファレンス |
|---|---|
| `aws-documentation` | <https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/> |
| `aws-knowledge` | <https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/> |
| `bedrock-agentcore` | <https://awslabs.github.io/mcp/servers/amazon-bedrock-agentcore-mcp-server/> |
| `strands-agents` | <https://github.com/strands-agents/harness-sdk> |
| `google-developer-knowledge` | <https://developers.google.com/knowledge/mcp> |
| `microsoft-learn` | <https://learn.microsoft.com/training/support/mcp> |
| `wolfram` | <https://www.wolfram.com/artificial-intelligence/mcp/cloud/wolfram-mcp-cloud/> |

stdio の 3 件（`aws-documentation` / `bedrock-agentcore` / `strands-agents`）は PyPI のパッケージメタデータ（`https://pypi.org/pypi/<package>/json` の `project_urls`）から取得した。HTTP の 4 件はベンダーの公式ドキュメントページ。`aws-knowledge` の URL のみ、掲載一覧が返した末尾スラッシュなしの形に、他と揃えてスラッシュを補っている。

## 4. サーバーを追加・削除したとき

`.mcp.json` を変更したら、次の2つを同じ変更で更新する。自動チェックは存在しない（`docs/adr/0007-remove-scripts.md` で整合性チェックスクリプトを撤去済み）。

1. **本書の表** — ベンダー公式リファレンスを追加・削除する。stdio なら PyPI メタデータ、HTTP ならベンダーの公式ページから取る。推測で URL を書かない。
2. **README / README.ja の「MCP Servers」節** — ユーザーが自分で実行する `claude mcp add -s user …` のコマンド例。

`.claude/` 配下のルールとスキルにはサーバー名を書かない。ユーザーが入れていないサーバーを前提にした指示になるためである。

## References

1. Claude Code — MCP: <https://code.claude.com/docs/en/mcp>
2. MCP specification — Lifecycle, `InitializeResult.instructions`: <https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle>
