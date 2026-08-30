# MCP サーバー — 背景と参照先

このリポジトリの MCP 運用手順は `.claude/skills/cloud-platform-research/SKILL.md` にある。サーバー選択と AWS スキルレジストリ手順は、クラウド提供元の現行ドキュメントが要る条件付き調査であり全セッション共通のルールではないため、常時ロードではなく必要時にだけ読み込まれるスキルとして持つ（[ADR-0015](adr/0015-rule-layer-independence.md)）。そちらは Claude Code が判断に使う最小限の情報だけを持ち、本書がその背景（なぜその形なのか、情報がどこから来ているのか、サーバーを増やしたとき何を更新するのか）を持つ。

本書は `.claude/rules/` にも `.claude/skills/` にもないため自動ロードされない。読むのは人間で、Claude が読むのは必要になったときだけである。

## 1. `.mcp.json` に書けること、書けないこと

接続定義は `.mcp.json` にある。持てるのは**接続のためのフィールドだけ**で、`description` や `when_to_use` に相当するものは存在しない [1]。

| 用途 | フィールド |
|---|---|
| 転送方式 | `type`（`http` / `sse` / `stdio` / `ws`） |
| 接続先 | `url`（HTTP 系）、`command` / `args`（stdio） |
| 認証 | `headers`、`headersHelper`、`oauth`、`env` |
| 挙動 | `timeout`、`alwaysLoad` |

つまり **「このサーバーをいつ呼ぶべきか」を `.mcp.json` から渡す手段はない**。個々の MCP サーバー定義はスキルの `description` / `when_to_use` フロントマターに相当するものを持てないためで、この非対称性が、サーバー選択の判断を `cloud-platform-research` skill 自身の `description` に集約している理由である。

## 2. Claude Code が実際に受け取るもの

接続後、サーバー側から protocol 経由で 2 種類の情報が来る。

| 経路 | 中身 | 書くのは |
|---|---|---|
| `tools/list` | ツール名、説明、入力スキーマ | サーバー作者 |
| `initialize` レスポンスの `instructions`（任意） | サーバー全体の使い方。Claude Code は "MCP Server Instructions" として注入する | サーバー作者 |

`instructions` は MCP 仕様で `InitializeResult` の任意フィールドとして定義されている [2]。**サーバー作者が書くもので、利用者が手元で補うことはできない。**

さらに tool search が既定で有効なため、ツール**名**はコンテキストにあるが、説明とスキーマは入っていない。必要になった時点で ToolSearch が取得する [1]。`cloud-platform-research/SKILL.md` の「利用可能なツール発見の仕組みを使ってから、提供元のドキュメントが手に入らないと判断せよ」はこの挙動に対応している。

`alwaysLoad: true` を設定すると、そのサーバーだけ遅延読み込みから除外され、初回ターンから完全なスキーマが載る [1]。設定側から「把握の度合い」を上げられる唯一のレバーだが、内容そのものを足すことはできない。

## 3. 各サーバーのベンダー公式リファレンス

`cloud-platform-research/SKILL.md` の「Subject / Preferred official capability」表は、セッションに注入された各サーバーの `instructions` とツール名の観測から起こしている。以下はその裏取り先。

| サーバー | ベンダー公式リファレンス |
|---|---|
| `aws-documentation` | <https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/> |
| `aws-knowledge` | <https://awslabs.github.io/mcp/servers/aws-knowledge-mcp-server/> |
| `bedrock-agentcore` | <https://awslabs.github.io/mcp/servers/amazon-bedrock-agentcore-mcp-server/> |
| `strands-agents` | <https://github.com/strands-agents/harness-sdk> |
| `google-developer-knowledge` | <https://developers.google.com/knowledge/mcp> |
| `microsoft-learn` | <https://learn.microsoft.com/training/support/mcp> |

stdio の 3 件（`aws-documentation` / `bedrock-agentcore` / `strands-agents`）は PyPI のパッケージメタデータ（`https://pypi.org/pypi/<package>/json` の `project_urls`）から取得した。HTTP の 3 件はベンダーの公式ドキュメントページ。`aws-knowledge` の URL のみ、掲載一覧が返した末尾スラッシュなしの形に、他と揃えてスラッシュを補っている。

## 4. サーバーを追加・削除したとき

`.mcp.json` を変更したら `.claude/skills/cloud-platform-research/SKILL.md` の表と本書の表を同時に更新する。自動チェックは存在しない（`docs/adr/0007-remove-scripts.md` で整合性チェックスクリプトを撤去済み）。README の検証セクションにも同じ手動チェックリストがある。

新しいサーバーについて記入するのは 3 点:

1. **主題（Subject）** — 何を扱うか。注入された `instructions` があればそこから、なければツール名から。`cloud-platform-research/SKILL.md` の表に1行追加する。
2. **自己記述の有無** — `instructions` を提供しているか。`/mcp` パネルまたはセッションの "MCP Server Instructions" ブロックの有無で判断する。自己記述しないサーバーは、そのぶん本書とスキル側の記述の正確さに依存する。
3. **ベンダー公式リファレンス** — 本書の表に追加。stdio なら PyPI メタデータ、HTTP ならベンダーの公式ページ。推測で URL を書かない。

## References

1. Claude Code — MCP: <https://code.claude.com/docs/en/mcp>
2. MCP specification — Lifecycle, `InitializeResult.instructions`: <https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle>
