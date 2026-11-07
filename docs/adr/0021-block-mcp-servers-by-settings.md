---
status: Accepted
date: 2026-11-08
deciders: Taiki Ogihara
---

# 0021. 使わない MCP サーバーを、ユーザー設定のキーで読み込ませない

## コンテキストと問題

[ADR-0016](0016-do-not-install-mcp-servers-at-user-scope.md) は、`install.sh` が MCP サーバーを登録も削除もしないと決めた。登録済みのサーバーとインストール済みのプラグインは、利用者自身が消すまで残る。

2026-11-07 にこのマシンで棚卸しをすると、セッションには次のものが読み込まれていた。

- ユーザー登録の stdio サーバー `bedrock-agentcore`(`uvx awslabs.amazon-bedrock-agentcore-mcp-server@latest`)。AWS の実際のリソースを作成・変更・削除し、AWS でコードを実行するツールを持つ。
- `github` プラグイン(GitHub がホストする MCP サーバー)。認証ヘッダーの不備で接続に失敗していた。
- claude.ai のコネクタ7件(Gmail、Google Calendar、Google Drive、Notion、Moneytree、Claude Docs、Wolfram)。
- claude.ai から同期されたプラグイン2件(`productivity` は Slack など7つの SaaS の MCP、`pdf-viewer`)。

利用者は、GitHub MCP の設定を削除し、ほかの MCP も棚卸しするよう求めた。棚卸しの結果から、上の4種類を止めると選んだ(2026-11-07)。

## 決定

`.claude/settings.json` に次のキーを置き、`install.sh` でユーザー設定に入れる。

| 止めるもの | キー |
|---|---|
| GitHub がホストする MCP サーバー | `deniedMcpServers` の `{"serverUrl": "https://api.githubcopilot.com/*"}` |
| `github` プラグイン | `enabledPlugins` の `"github@claude-plugins-official": false` |
| `bedrock-agentcore` | `deniedMcpServers` の `{"serverName": "bedrock-agentcore"}` と、そのコマンドの `serverCommand` |
| claude.ai のコネクタ | `disableClaudeAiConnectors: true` |
| claude.ai から同期されるプラグイン | `syncClaudeAiPlugins: false` |

これらは設定のキーであり、`install.sh` は今までどおり `claude mcp` も `claude plugin uninstall` も呼ばない。ADR-0016 の決定(登録も削除もしない)は変わらない。マシンに残る登録とプラグインの実体は、利用者が自分で消せる。消さなくても、読み込まれない。

### 結果

- 良い点: 定義された場所(ユーザー登録、プロジェクトの `.mcp.json`、プラグイン、`--mcp-config`)を問わず、止めたサーバーは読み込まれない。`deniedMcpServers` は、どのスコープの設定からも効く。
- 良い点: 私的なデータ(メール、カレンダー、金融)と外部の文章が、Bash を持つセッションにそろわない。AWS の実際のリソースを変更できる MCP のツールが消える。
- 悪い点: claude.ai のコネクタは、Claude Code からは一括でしか止められない。必要になったら、キーを外すか、プロジェクトの設定で個別に扱う。
- 悪い点: GitHub の MCP サーバーを別の名前のローカルのコマンド(`github-mcp-server` や Docker)として登録し直すと、URL の拒否には当たらない。
- 悪い点: `install.sh` のマージは配列を置き換えるので、利用者が自分の `~/.claude/settings.json` に書いた `deniedMcpServers` は、インストールのたびにこのリポジトリの値になる。
- 中立: `.claude/` のルールとスキルにはサーバー名を書かない、という ADR-0016 の取り決めは保つ。サーバー名が現れるのは `settings.json` の拒否の一覧だけである。

## 検討した選択肢

- **設定のキーで止める(採用)**: 上記のとおり。どのマシンでも、`install.sh` を実行すれば同じに効く。
- **`install.sh` で `claude plugin uninstall` と `claude mcp remove` を実行する**: マシンから実体が消える。代わりに ADR-0016 が避けた「利用者が自分で入れた同名の設定を消す」問題が戻り、別の経路で入れ直されると防げない。
- **このマシンでだけ手作業で消す**: リポジトリは変わらず、ほかのマシンには及ばない。利用者は設定として残すことを求めた。
- **`permissions.deny` に `mcp__github` などのツールの拒否を書く**: ツールは呼べなくなるが、サーバーは接続し、ツールの説明は文脈に入る。また ADR-0014 の「deny は Read の規則だけ」の制約(`tests/run-removed-guardrails.sh`)に反する。

## 確認方法

- `tests/run-sandbox-settings.sh` の MCP-01〜06 が、5つのキーの値を確かめる。
- `tests/run-install.sh` が、利用者が `github` プラグインを有効にしていても、インストールの後は `false` になることを確かめる。
- 読み込まれないことは、`install.sh` の後の新しいセッションで、止めたサーバーのツールが現れないことで確かめる([spec 067](../../specs/067-sandbox-by-default/spec.md) の SC-004)。2026-11-08 に、ワークツリーの設定をプロジェクト設定として読み込んだこのセッションで、claude.ai のコネクタが止まったことを観察した。

## 補足情報

- [ADR-0016](0016-do-not-install-mcp-servers-at-user-scope.md) — `install.sh` が MCP サーバーを登録も削除もしない決定。本 ADR は変更しない。
- [`docs/mcp-servers.md`](../mcp-servers.md) §5 — 止めたサーバーと、棚卸しで残したサーバーの一覧。
- [ADR-0020](0020-enable-sandbox-by-default.md) — 同じ変更で有効にしたサンドボックス。
- Claude Code — Settings reference(`deniedMcpServers`、`disableClaudeAiConnectors`、`syncClaudeAiPlugins`、`enabledPlugins`): <https://code.claude.com/docs/en/settings-reference>、MCP: <https://code.claude.com/docs/en/mcp>、Plugins の読み込み: <https://code.claude.com/docs/en/plugins/loading>
