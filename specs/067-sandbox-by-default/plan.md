# Implementation Plan: OS サンドボックスを既定で有効にし、日常作業に要る出口だけを最小限に開ける

**Branch**: `feat/sandbox-by-default` | **Date**: 2026-11-07(2026-11-08 に利用者の決定 D4、D5 と反証のレビューを反映) | **Spec**: [spec.md](spec.md)

## Summary

すべて `.claude/settings.json` のキーで実現する。`install.sh` は変えない(既存の再帰マージで、利用者のキーを残したまま入る)。

| FR | 実現の手段 |
|---|---|
| FR-001 | `sandbox.enabled: true`。`allowUnsandboxedCommands` と `network.strictAllowlist` は書かない(既定の `true` と `false` のまま=標準) |
| FR-002 | `sandbox.filesystem.denyRead` に GPG の3つと、ほかの資格情報の5つのファイルを列挙する。`~/.aws` は、既存の `permissions.deny` の `Read(~/.aws/**)` から作られる読み取りの拒否に残し、`allowRead` で開け直さない |
| FR-003 | `sandbox.filesystem.denyWrite` に、GPG の秘密・キーリング・信頼度・設定ファイルを列挙する |
| FR-004 | `sandbox.filesystem.allowWrite` に `~/.gnupg` と `~/Library/Fonts`。パスは `~/` で書く(ユーザー設定でもプロジェクト設定でも同じ場所を指す) |
| FR-005 | `sandbox.network.allowUnixSockets` に2つのソケット。`allowAllUnixSockets` は書かない |
| FR-006 | `sandbox.network.allowedDomains` に Google Fonts の2つのホスト |
| FR-007 | `deck.py` に `chromium_args(environ, platform)` を足し、`SANDBOX_RUNTIME=1` かつ `darwin` のときだけ `["--single-process"]` を返す |
| FR-008〜FR-010 | `hooks.SessionStart` に、`settings.json` に直接書いた短いコマンドを3つ置く(ADR-0008 の前例)。Bash の環境は `CLAUDE_ENV_FILE` に `unset` の行を足して変える。文脈は標準出力に書く(SessionStart では標準出力が文脈に加わる)。各フックは `statusMessage` で見分ける |
| FR-011 | `enabledPlugins` の `github@claude-plugins-official: false`、`deniedMcpServers`(GitHub は `serverUrl`、`bedrock-agentcore` は `serverName` と `serverCommand`)、`disableClaudeAiConnectors: true`、`syncClaudeAiPlugins: false` |
| FR-012 | `install.sh` の `jq '.[0] * .[1]'` は、オブジェクトを再帰的にマージする。`enabledPlugins` はリポジトリが1キーだけを宣言するので、利用者のほかのキーは残る。配列はリポジトリの値で置き換わる |
| FR-014 | `sandbox.excludedCommands: ["aws *"]`。Claude Code は、Bash の呼び出し全体がこのパターンに当たるときだけ外で動かす(パイプ、`&&`、`$(...)` を含むものは中に残る) |

フックのコマンドは、sh・bash・zsh のどれで実行されても同じに動くように書く(引用符のない変数とグロブを使わない、語を `=` で始めない)。

## Technical Context

Claude Code 2.1.319(macOS)。設定のキーは 2026-11-07 に読んだ code.claude.com の settings-reference、sandboxing、env-vars、hooks、mcp、plugins に従う。フックは POSIX sh。検査器は Python 3 の標準ライブラリだけ(Playwright は起動の時点でだけ使う)。テストは bash と jq。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲートは次のとおり。

- `.claude/` の下にリポジトリ固有の事実を入れない: 合格。AWS のプロファイル名は書かない。
- ルールは4ファイル、ルールとスキルは他を名指ししない(ADR-0015、spec 058): 合格。ルールを足さず、文脈はフックで足す。
- `.claude/hooks/` と `scripts/` を作らない(ADR-0005、ADR-0007): 合格。フックは `settings.json` に直接書く。
- `permissions` は Read の deny だけ(ADR-0014): 合格。`permissions` は変えない。
- `install.sh` は MCP サーバーを登録も削除もしない(ADR-0016): 合格。止めるのは設定のキーで行い、`claude mcp` も `claude plugin uninstall` も呼ばない。
- README の英日をそろえる: T008 で行う。

## 変えるファイル

- `.claude/settings.json` — `sandbox`、`hooks.SessionStart`、MCP のキー
- `.claude/skills/digital-agency-slides/scripts/deck.py`、`references/deck-checks.md` — Chromium の引数
- `tests/run-sandbox-settings.sh`(新規)、`tests/assert_deck_units.py`、`tests/run-install.sh`、`.github/workflows/ci.yml`
- `docs/adr/0020-enable-sandbox-by-default.md`、`docs/adr/0021-block-mcp-servers-by-settings.md`(新規)、`docs/mcp-servers.md`、`docs/claude-config-design.md`、`README.md`、`README.ja.md`

## 確かめられないこと

`CLAUDE_ENV_FILE` の行がサンドボックスの中と外のコマンドに効くこと、`excludedCommands` の `aws *` が外で動くこと、サンドボックスの中の gpg が `~/.gnupg` のソケット越しに外の gpg-agent で署名できることは、リポジトリのテストでは確かめられない(Claude Code 本体と GnuPG の振る舞いである)。変更を適用した新しいセッションで確かめる(tasks.md の T011)。署名は、このマシンに `~/.gnupg` が無いので、利用者のマシンで確かめる。
