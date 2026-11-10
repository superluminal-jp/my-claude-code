# MCP サーバー — 背景と参照先

読み込める MCP サーバーは、AWS の公式ドキュメントを検索する2つ（`aws-knowledge` と `aws-documentation`）だけである。`harness/settings.json` の許可リストが、だれが定義したサーバーにも、これを適用する（§5）。理由はセキュリティである。

このリポジトリは MCP サーバーをユーザー設定に取り込まない。`install.sh` は MCP サーバーを登録も削除もせず、MCP サーバーを同梱するプラグイン（`github` / `deploy-on-aws` / `microsoft-docs`）もインストールせず、`harness/settings.json` がこの3つを無効にする（§5.2）。許可された2つは、各ユーザーが自分で登録する（手順は README の「MCP Servers」節、判断の経緯は [ADR-0016](adr/0016-do-not-install-mcp-servers-at-user-scope.md)）。`harness/` 配下のルールとスキルも、特定の MCP サーバー名を前提にしない。

`.mcp.json` は、このリポジトリ内で作業するときのプロジェクトスコープ定義である。本書はその背景（`.mcp.json` に何が書けるのか、各サーバーの情報がどこから来ているのか、許可するサーバーを変えたとき何を更新するのか、何を止めているのか）を持つ。

本書は `harness/rules/` にも `harness/skills/` にもないため自動ロードされない。読むのは人間で、Claude が読むのは必要になったときだけである。

## 1. `.mcp.json` に書けること、書けないこと

接続定義は `.mcp.json` にある。持てるのは**接続のためのフィールドだけ**で、`description` や `when_to_use` に相当するものは存在しない [1]。

| 用途 | フィールド |
|---|---|
| 転送方式 | `type`（`http` / `sse` / `stdio` / `ws`） |
| 接続先 | `url`（HTTP 系）、`command` / `args`（stdio） |
| 認証 | `headers`、`headersHelper`、`oauth`、`env` |
| 挙動 | `timeout`、`alwaysLoad` |

つまり **「このサーバーをいつ呼ぶべきか」を `.mcp.json` から渡す手段はない**。個々の MCP サーバー定義は、スキルの `description` に相当するものを持てない。いつ呼ぶかの手がかりは、サーバー自身が返す `instructions` とツール説明に頼ることになる（次節）。

## 2. Claude Code が実際に受け取るもの

接続後、サーバー側から protocol 経由で 2 種類の情報が来る。

| 経路 | 中身 | 書くのは |
|---|---|---|
| `tools/list` | ツール名、説明、入力スキーマ | サーバー作者 |
| `initialize` レスポンスの `instructions`（任意） | サーバー全体の使い方。Claude Code は "MCP Server Instructions" として注入する | サーバー作者 |

`instructions` は MCP 仕様で `InitializeResult` の任意フィールドとして定義されている [2]。**サーバー作者が書くもので、利用者が手元で補うことはできない。**

さらに tool search が既定で有効なため、ツール**名**はコンテキストにあるが、説明とスキーマは入っていない。必要になった時点で ToolSearch が取得する [1]。`research-aws/SKILL.md` が「利用可能なツール発見の仕組みを使ってから、提供元のドキュメントが手に入らないと判断せよ」とだけ書き、サーバー名を挙げないのはこの挙動に対応している。許可された2つを登録しているかどうかは、ユーザーごとに異なる。

`alwaysLoad: true` を設定すると、そのサーバーだけ遅延読み込みから除外され、初回ターンから完全なスキーマが載る [1]。設定側から「把握の度合い」を上げられる唯一のレバーだが、内容そのものを足すことはできない。

## 3. 各サーバーのベンダー公式リファレンス

`.mcp.json` に載せている各サーバーの裏取り先。

| サーバー | ベンダー公式リファレンス |
|---|---|
| `aws-documentation` | <https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/> |
| `aws-knowledge` | <https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/> |

stdio の `aws-documentation` は PyPI のパッケージメタデータ（`https://pypi.org/pypi/<package>/json` の `project_urls`）から取得した。HTTP の `aws-knowledge` はベンダーの公式ドキュメントページで、掲載一覧が返した末尾スラッシュなしの形に、スラッシュを補っている。

2026-11-10 まで、`.mcp.json` は `google-developer-knowledge`、`microsoft-learn`、`wolfram` も定義していた。その記述は Git の履歴にある。

## 4. 許可するサーバーを変えたとき

許可するサーバーを足す・外すときは、次の5つを同じ変更で更新する。

1. **`harness/settings.json` の `allowedMcpServers`** — リモートのサーバーは `serverUrl`、ローカルのサーバーは `serverCommand`（コマンドと引数のすべてを、順序どおりに）で書く。名前（`serverName`）では書かない（§5）。
2. **`.mcp.json`** — このリポジトリ内で使うなら、同じ URL かコマンドで定義する。
3. **`tests/run-sandbox-settings.sh` の MCP-07 と MCP-10** — 許可リストの中身と、`.mcp.json` との一致を確かめている。
4. **本書の §3 と §5 の表** — ベンダー公式リファレンスは、stdio なら PyPI メタデータ、HTTP ならベンダーの公式ページから取る。推測で URL を書かない。
5. **README / README.ja の「MCP Servers」節** — 表と、ユーザーが自分で実行する `claude mcp add -s user …` のコマンド例。

`harness/` 配下のルールとスキルにはサーバー名を書かない。ユーザーが入れていないサーバーを前提にした指示になるためである。直接止めるサーバー（拒否リスト）を増やす・減らすときは、`harness/settings.json` の `deniedMcpServers`、§5 の表、`tests/run-sandbox-settings.sh` の MCP-01〜MCP-06 と MCP-09 を同じ変更で更新する。

## 5. 許可しているサーバーと、止めているもの

`harness/settings.json` は、2つの仕組みを重ねている。許可リストが、読み込めるサーバーを2つに限る。拒否リストなどが、許可リストの照合を受けないものと、特に危険なものを、直接止める。

### 5.1 許可リスト: 2つだけを読み込ませる

`harness/settings.json` の `allowedMcpServers` は、次の2つに一致するサーバーだけを読み込ませる。許可リストはどの設定ファイルからも効き、ユーザーが登録したサーバーにも、プロジェクトの `.mcp.json` のサーバーにも、プラグインや claude.ai が足すサーバーにも適用される [3]。

| 許可するもの | 照合の方法 | 注意 |
|---|---|---|
| `aws-knowledge` | `serverUrl: https://knowledge-mcp.global.api.aws` | HTTP、認証なし |
| `aws-documentation` | `serverCommand: ["uvx", "awslabs.aws-documentation-mcp-server@latest"]` | 起動のたびに `uvx …@latest` で最新版を実行する。引数が1つでも違う登録（たとえば版を固定した登録）は、一致しない |

照合の規則は次のとおりである [3]。

- リモートのサーバーは `serverUrl` の項目と、stdio のサーバーは `serverCommand` の項目と照合される。コマンドは、すべての引数が順序どおりに一致したときだけ一致する。`env` は比べられない。
- 名前（`serverName`）の一致が数えられるのは、許可リストに、そのサーバーと同じ種類（URL かコマンド）の項目が1つもないときだけである。名前は、登録する人が自由に付けられるラベルで、公式文書も、名前をセキュリティの制御として扱わないとしている。このため、許可リストには名前の項目を置かない（検査 MCP-08）。
- 許可リストは、すべての設定ファイルのものが合わさる。プロジェクトやローカルの設定が項目を足せば、許可は広がる。これを防げるのは、管理設定（managed settings）の `allowManagedMcpServersOnly` だけで、このリポジトリは管理設定を扱わない。
- 拒否リスト（`deniedMcpServers`）に一致したサーバーは、許可リストに一致しても読み込まれない。

### 5.2 拒否リストなど: 直接止めるもの

次のものは、許可リストとは別に、直接止めている（[ADR-0021](adr/0021-block-mcp-servers-by-settings.md)）。`deniedMcpServers` と `disableClaudeAiConnectors` はどの設定ファイルからも効き、`syncClaudeAiPlugins` はユーザー・ローカル・管理の設定から効く [1]。

| 止めるもの | キー | 理由 |
|---|---|---|
| 組み込みの Chrome 連携（`claude-in-chrome`） | `deniedMcpServers` の `serverName` | 組み込みのサーバーは、許可リストの照合を受けない [3]。外部の文章を読む同じセッションから、ログイン済みの利用者自身のブラウザを操作する |
| GitHub がホストする MCP サーバー | `deniedMcpServers` の `serverUrl: https://api.githubcopilot.com/*` | 使っていない。GitHub の作業は `gh` CLI で足りる |
| `github` プラグイン | `enabledPlugins` の `github@claude-plugins-official: false` | 上のサーバーを同梱するだけのプラグインである |
| `deploy-on-aws` プラグイン | `enabledPlugins` の `deploy-on-aws@claude-plugins-official: false` | 同梱する `awsiac` と `awspricing` は許可リストにない。デプロイのスキルはそのサーバーに頼るので、サーバーだけを止めると、働かないスキルが一覧に残る |
| `microsoft-docs` プラグイン | `enabledPlugins` の `microsoft-docs@claude-plugins-official: false` | 同梱するサーバーは許可リストにない。スキルは、そのサーバーを検索するためのもので、サーバーがないと用をなさない |
| `bedrock-agentcore` | `deniedMcpServers` の `serverName` と `serverCommand` | Claude Code が持つ AWS の認証情報で、AWS の実際のリソースを作成・変更・削除し、AWS でコードを実行する。起動のたびに `uvx …@latest` で最新版を実行する |
| claude.ai のコネクタ（Gmail、Google Calendar、Google Drive、Notion、Moneytree、Claude Docs、Wolfram） | `disableClaudeAiConnectors: true` | 私的なデータと外部の文章が Bash と同じセッションにそろうと、プロンプトインジェクションでデータを持ち出す経路になる |
| claude.ai から同期されるプラグイン（`productivity`、`pdf-viewer`） | `syncClaudeAiPlugins: false` | SaaS の MCP サーバー（Slack、Notion、Asana、Linear、Atlassian、monday、ClickUp）を、さらにすべてのセッションに持ち込む。`false` にすると、同期済みのものも `~/.claude/plugins/.trash/` へ移されて読み込まれない |

GitHub と `bedrock-agentcore` の拒否は、許可リストができた今は重なっているが、残してある。拒否は、許可リストがどこかの設定で広げられても効くためである。

### 5.3 2026-11-10 に止めたもの

2026-11-07 の棚卸しでは、ドキュメントの検索か計算に使うサーバーを残していた。2026-11-10 に、利用者がセキュリティを理由に、AWS のドキュメントの2つ以外を廃止すると決めた。許可リストによって、次のものが読み込まれなくなる。

| サーバー | 定義の場所 | 止める前の注意 |
|---|---|---|
| `strands-agents` | ユーザー登録 | 起動のたびに `uvx …@latest` で最新版を実行する |
| `google-developer-knowledge` | ユーザー登録、`.mcp.json`（削除済み） | API キーを環境変数 `GOOGLE_DEV_KNOWLEDGE_API_KEY` から渡す |
| `microsoft-learn` | ユーザー登録、`.mcp.json`（削除済み）、`microsoft-docs` プラグイン（無効にした） | HTTP、認証なし |
| `wolfram` | ユーザー登録、`.mcp.json`（削除済み） | 計算の内容を Wolfram に送る |
| `deploy-on-aws` の `awsiac` と `awspricing` | プラグイン（無効にした） | 起動のたびに `uvx …@latest` で最新版を実行する。AWS の API を、Claude Code の環境の AWS の認証情報で呼ぶ |

止める理由は、どれにも共通する。MCP サーバーはサンドボックスの外で動く。`uvx …@latest` で起動するサーバーは、公開されたばかりの悪意ある版も、起動のたびにサンドボックスの制限なしに実行する。リモートのサーバーは、外部の文章を、コマンドを実行できる同じセッションに持ち込む。

残る注意が2つある。

- **登録は残る。** 許可リストは読み込みを止めるだけで、ユーザースコープの登録は消さない（このリポジトリは登録を変えない。ADR-0016）。消すときは、各ユーザーが `claude mcp remove -s user <名前>` を実行する。
- **プラグインのインストールは残る。** `deploy-on-aws` と `microsoft-docs` は無効にしたので、スキルもサーバーも読み込まれない。インストールそのものは消さない。消すときは、各ユーザーが `claude plugin uninstall <名前>@claude-plugins-official` を実行する。AWS の公式アイコンを使う構成図のスキルは `deploy-on-aws` にあったので、その依頼を受け持つスキルは、今はない。

許可された `aws-documentation` も、起動のたびに `uvx …@latest` で最新版を実行する。版を固定して登録すると、コマンドが許可リストの項目と一致しなくなるので、固定するときは許可リストの項目も同じ引数に変える。

## References

1. Claude Code — MCP: <https://code.claude.com/docs/en/mcp>
2. MCP specification — Lifecycle, `InitializeResult.instructions`: <https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle>
3. Claude Code — Managed MCP configuration（許可リストと拒否リストの照合の規則、適用される範囲、組み込みのサーバーの扱い）: <https://code.claude.com/docs/en/managed-mcp>
