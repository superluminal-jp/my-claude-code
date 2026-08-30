# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`install.sh` は `.claude/` のうちリポジトリが管理する設定、rules、skills、agents、memory を
`~/.claude/` に同期し、管理対象外のユーザーファイルは保持します。

英語版: [README.md](README.md)

## このリポジトリで提供するもの

- **`.claude/CLAUDE.md`**: 常時メモリ（原則、事前チェック、クローズアウト、ルーティングと MCP への参照）。動作に必要な内容のみで、設計根拠は [`docs/claude-config-design.md`](docs/claude-config-design.md) にあります
- **`.claude/settings.json`**: Claude Code のユーザーレベル設定
- **`.claude/rules/`**: 常時読み込まれる共通ルール。Claude の判断を変える内容だけを置く（権限（強制される deny は `settings.json`）、確認ルール、skill ルーティング、思考レンズ（6つの推論セルフチェック）、live-documentation（7つのチェック）、git ワークフロー、MCP サーバー選択）。各ファイルが何を意図的に置いていないかは [`docs/claude-config-design.md`](docs/claude-config-design.md) に記録しています
- **`.claude/skills/`**: 必要時に読み込まれるプレイブック
  - `coder`: 実装作業（TDD/SDD、品質、安全、型安全性、ドキュメント同期）
  - `digital-agency-frontend`: DADS とダッシュボードガイドブックに基づく、アクセシブルな React/Tailwind Web フロントエンド開発・レビュー
  - Minto ドキュメントスイート — `minto-reviewer`（構造診断）、`minto-rewriter`（最終版への書き直し）、`minto-builder`（対話による構築）
  - `clarifier`: 要件定義・受け入れ条件の明確化（INVEST/Gherkin）
  - `adr`: アーキテクチャ決定記録（MADR形式）
  - `scrum-master`: Scrumイベントの設計・ファシリテーション、障害除去、フロー指標
  - Spec Kit の `speckit-*` スキルはこのリポジトリでは vendoring しない。各プロジェクトで
    `specify init` を実行した際に、`--integration` が指す各エージェントのディレクトリ
    （`.claude/skills/`、`.agents/skills/`、`.cursor/skills/`）配下に生成される
    プロジェクトローカルな成果物で、すべて gitignore 対象（後述「spec-kit のオプトイン」参照）

## ユーザー設定としてインストール

以下を実行してください:

```sh
bash path/to/my-claude-code/install.sh
```

インストーラーは `~/.claude` を同期し、Claude Code のユーザースコープ MCP を登録/更新し、
本リポジトリが依存する Claude Code プラグイン（後述「プラグイン」参照）をインストール/有効化します。

実行には `claude` CLI と `uvx` が必要です。Google Developer Knowledge MCP は
`GOOGLE_DEV_KNOWLEDGE_API_KEY` が設定されている場合だけ登録されます。

### 重要: 上書き置換（削除同期）について

- 次の管理対象は **置換同期** されます:
  - `rules/`
  - `skills/`
  - `agents/`
  - `commands/`
  - `CLAUDE.md`
  - `settings.json`
  - `install.sh`
- このリポジトリ側で削除されたファイルは、`~/.claude` 側でも削除されます。
- `settings.local.json` を含む `~/.claude` の管理対象外パスは保持されます。個人用ファイルは上記の管理対象外に置いてください。

## 代替: `CLAUDE.md` から import

コピーせずに参照する場合:

```markdown
@/absolute/path/to/my-claude-code/.claude/CLAUDE.md
```

## 構成

```text
my-claude-code/
├── CLAUDE.md
├── README.md
├── README.ja.md
├── install.sh
├── .mcp.json
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # main への push/PR ごとに tests/run-*.sh を実行(必須チェック)
│   │   └── dependabot-automerge.yml # パッチ/マイナーのDependabotセキュリティ修正PRをCI通過後に自動マージ
│   └── rulesets/main-required-checks.json # main の必須ステータスチェックruleset定義
└── .claude/
    ├── CLAUDE.md
    ├── settings.json
    ├── rules/
    └── skills/
```

## 検証

`.mcp.json` / `install.sh` / `.claude/settings.json` / `.claude/rules/mcp.md` を変更したら:

```sh
bash tests/run-mcp-startup.sh # ネットワーク接続と書き込み可能な uv キャッシュが必要
bash tests/run-install.sh
bash tests/run-digital-agency-frontend-skill.sh
bash tests/run-removed-guardrails.sh
```

`run-removed-guardrails.sh` は特定の変更に紐づかない、常設の回帰防止チェックです —
`.claude/hooks/`・`scripts/` が再導入されたら失敗し
（[ADR-0005](docs/adr/0005-remove-claude-hooks.md)、
[ADR-0007](docs/adr/0007-remove-scripts.md)）、
[ADR-0006](docs/adr/0006-remove-permissions-config.md) の上に
[ADR-0014](docs/adr/0014-restore-credential-deny-rules.md) が復元した
`permissions` ブロックを制約します — 許されるのは `deny` のみで、`allow` や
`ask` のティアがあれば失敗します。また `deny` の各項目は `~/` または `**/` で
アンカーされた `Read` ルールでなければなりません。単一の先頭スラッシュは
`install.sh` がユーザースコープへ複製した時点で別のパスに解決されるためです。

`run-install.sh` は隔離した HOME と外部コマンドの stub を使います。
`run-mcp-startup.sh` だけは設定済み MCP サーバーの起動コマンドを実行するため
ネットワーク接続が必要で、それ以外はローカル検証です。

## リポジトリのセキュリティ自動化

上記4本のスクリプトは `main` への push/PR ごとに CI(`.github/workflows/ci.yml`)でも
自動実行され、`main` はそのチェックを必須とする repository ruleset
(`.github/rulesets/main-required-checks.json`)で保護されています。

これに加えて、GitHub自身が検知する脆弱性への対応も自動化しています:

- **Dependabot**: パッチ/マイナーバージョンのセキュリティ修正PRは、CIが通れば
  自動マージされます(`.github/workflows/dependabot-automerge.yml`)。メジャー
  バージョン更新や `dependabot[bot]` 以外が作成したPRは自動マージされず、手動
  レビューに残ります。`.github/dependabot.yml` は作成していません —
  security updatesはこのファイルなしでもDependency graphから自動的に動作し、
  `updates:` エントリを追加するとスケジュール付きの(非セキュリティ)更新PRが
  意図せず発生してしまうためです([ADR-0012](docs/adr/0012-dependabot-automerge-scope.md) 参照)。
- **CodeQL**: Default setupでこのリポジトリのPythonコードをスキャンします。
  検出結果はcode-scanningアラートとして手動トリアージ対象になり、自動修正・
  自動マージは行いません。
- **Secret scanning + push protection**: リポジトリ全体で有効化済みです。
  push protectionが対応する種類のシークレットパターンを含むpushは、いずれの
  ブランチにも到達する前に拒否されます(対応していない種類は検知のみ —
  詳細はGitHubの
  [supported secret scanning patterns](https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns)
  を参照)。**既知のギャップ**: 実測(`specs/032-github-security-automation/tasks.md`
  T013)の結果、GitHub公式ドキュメントでpush protection・検知の両方に対応と
  記載されているAWS形式(access key ID + secret access keyのペア)が、正しい
  フォーマットで4回試しても本リポジトリでは一度も検知されませんでした。
  原因は特定できておらず、AWS形式の認証情報についてはこのリポジトリの
  secret scanningを検証済みの安全網として扱わないでください。

## MCP サーバー

プロジェクトスコープ定義は [`.mcp.json`](.mcp.json) にあります。transport /
パッケージ / エンドポイントのカタログはこのファイルが正本です。  
どのサーバーを選ぶか、および AWS スキルレジストリの手順 — Claude Code が動作に
必要とする部分 — は [`.claude/rules/mcp.md`](.claude/rules/mcp.md) にあります。
保守者向けの背景（各サーバーのベンダー公式リファレンス、サーバー追加時の更新
手順、出典）は [`docs/mcp-servers.md`](docs/mcp-servers.md) にあります。

## プラグイン

このリポジトリは Anthropic 公式マーケットプレイス `claude-plugins-official`
（`anthropics/claude-plugins-official`。`github` や `microsoft-docs` のような
サードパーティ製プラグインも同じマーケットプレイスに収録）から解決される、
6 つの Claude Code プラグインに依存します: `frontend-design`（UI/UX 実装ガイダンス、
Anthropic）、`code-review`（マルチエージェント PR レビュー、`/code-review ultra` 含む、
Anthropic）、`skill-creator`（skill の雛形作成・評価、Anthropic）、`github`
（GitHub 公式 MCP サーバー、GitHub）、`deploy-on-aws`（AWS アーキテクチャ図 + デプロイ/IaC
skill。[ADR-0009](docs/adr/0009-adopt-deploy-on-aws-plugin.md) に基づき全体採用。
デプロイ/AWS CLI 変更系操作は plugin 側のゲートではなく
[`.claude/rules/permissions.md`](.claude/rules/permissions.md) により毎回確認が必要、AWS)、
`microsoft-docs`（Microsoft 公式ドキュメント MCP サーバー + skill。この plugin が同梱する
MCP エントリ `microsoft-learn` は本リポジトリの `.mcp.json` にある同名エントリと同じ
`https://learn.microsoft.com/api/mcp` を指す重複登録だが、競合ではないため許容
— `deploy-on-aws` の `awsknowledge` 重複と同じパターン、Microsoft）。

`.claude/settings.json` の `enabledPlugins` にプロジェクトスコープで宣言済みのため、
このリポジトリでセッションを開くと未インストールのプラグインについてインストールを
促されます。実際のインストールは `install.sh` が行います（マーケットプレイスが
未登録なら追加し、各プラグインをユーザースコープでインストール/有効化するため、
このリポジトリに限らず全プロジェクトで使えます）。

## プロジェクト単位の上書き

ユーザー設定はベースラインです。各プロジェクトの `.claude/settings.json` で拡張/上書きできます。

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": []
  }
}
```

優先順位（高 -> 低）:
managed > local (`.local.json`) > project (`settings.json`) > user (`~/.claude/settings.json`)

### spec-kit のオプトイン

Spec Kit (https://github.com/github/spec-kit) はプロジェクトごとに個別に
インストール・初期化します。このリポジトリや `~/.claude` に vendoring・配布
されるものではありません。プロジェクトごとに一度、以下の手順を実行してください:

```sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
specify self upgrade
specify init --here --force --integration claude
# specify init --here --force --integration cursor-agent
specify extension add git
```

- `uv tool install ... @vX.Y.Z` — ブランチ追従ではなく、明示的なリリースタグ
  （`vX.Y.Z` を置き換える）を指定してインストールすることで、再現可能な状態を保ちます。
- `specify self upgrade` — 内蔵のアップデーターで `specify` CLI 自体を
  最新リリースに更新します。
- `specify init --here --force --integration <agent>` — `/speckit.*`
  スラッシュコマンドを、そのプロジェクト自身の `.claude/skills/`（または
  指定した `--integration` に対応するパス。例:
  `cursor-agent` なら `.cursor/skills/`）配下に
  `speckit-*` スキルとして生成します — プロジェクトローカルな成果物であり、
  生成先のエージェントディレクトリによらずすべて gitignore 対象です
  （`.gitignore` 参照）。同一プロジェクト内で別のエージェントにも導入する
  場合は、`--integration` の値を変えて再実行してください。各コマンドは
  独自のプレイブックを持ちます。`coder` スキルの SDD セクションは
  spec-kit の導入有無にかかわらず適用されます。
- `specify extension add git` — Git Branching Workflow 拡張
  （`/speckit-git.*`）をインストールします。

追加されるコマンド: `speckit.git.feature`、`speckit.git.validate`、
`speckit.git.remote`、`speckit.git.initialize`、`speckit.git.commit`

すでに導入済みのプロジェクトで生成済みの `speckit-*` スキルを最新に保つのは、
今も手動の作業です — 自分で定期的に `specify init --here --force` を
実行してください。`specify-cli` 本体は別です — `.claude/settings.json` には
`speckit-specify` スキル実行の直前だけ発火する狭い範囲の `PreToolUse` hook
（docs/adr/0008）があり、`github/spec-kit` の最新リリースタグと `uv` の
インストールレシートに記録された `rev=` を比較し、不一致なら
`uv tool install specify-cli --from git+... --force` で再インストールします
（ネットワークエラー時は fail-open で処理を止めません。他の `speckit-*`
スキルではこの hook は発火しません）。これは docs/adr/0005 の「`.claude/hooks/`
なし・自動強制なし」という広い方針に対する、意図的かつ限定的な例外です —
理由は docs/adr/0008 を参照してください。`.specify/` が未導入のプロジェクトへ
`specify init` を提案するのは、引き続き `CLAUDE.md` 自体の指示です。
