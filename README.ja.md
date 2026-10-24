# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`install.sh` は `.claude/` のうちリポジトリが管理する設定、rules、skills、memory を
`~/.claude/` に同期し、管理対象外のユーザーファイルは保持します。

英語版: [README.md](README.md)

自分の設定を作る場合は、常時ロードの各指示が通すべき判断基準と、このリポジトリが
意図的に置いていないものを [`docs/claude-config-design.md`](docs/claude-config-design.md)
にまとめています。

## このリポジトリで提供するもの

- **`.claude/CLAUDE.md`**: 常時メモリ。1つの達成目標と、その3つのライフサイクル分岐
  （定義・実行・引き渡し）、および独立に一致するすべての能力を適用する汎用マルチマッチ
  アルゴリズムだけを持つ。ルール・スキル・サーバーの名前は一切含まない — 設計根拠は
  [`docs/claude-config-design.md`](docs/claude-config-design.md) にあります
- **`.claude/settings.json`**: Claude Code のユーザーレベル設定
- **`.claude/rules/`**: 常時読み込まれる共通ルール。Claude の判断を変える内容だけを置き、
  各ファイルが apex の3分岐のうち正確に1つだけを支える（要件確実性の確認トリガー、
  推論の完全性（4つの推論セルフチェック: 依存と並行・条件と分岐・反復・推論）、権限と安全性
  （強制される deny は `settings.json`）、読み手本位の構造（Pyramid Principle セルフチェック）、
  モデルと労力のルーティング（能力層、閉じたエスカレーション条件、サブエージェントのモデルと労力））。他のルール・スキル・設定パスへの言及は持たない。
  各ファイルが何を意図的に置いていないかは [`docs/claude-config-design.md`](docs/claude-config-design.md) に記録しています
- **`.claude/skills/`**: 必要時に読み込まれるプレイブック。中央ルーティング表なしに
  自己記述だけで選択できるよう、2つの独立した軸で分類する
  - ライフサイクル操作: `coder`（変更手順、TDD/SDD、品質、安全、型安全性、ドキュメント同期）、
    `clarifier`
    （まず意図の共通認識を形成し——AIが自分の理解・前提・スコープを述べ、
    ユーザーが却下できる形にする——その後、形式的要件へ変換。INVEST/Gherkin）、`problem-definition`
    （曖昧な訴えを、現状とあるべき姿のギャップとしての検証可能な問題文に変換）、
    `product-strategy`
    （ビジョン・ターゲットユーザー・提供価値・成功指標・MoSCoWによるスコープを、
    開発着手前に整理）、`meta-spec`
    （1つの大きな取り組みを、独立して仕様化できるフィーチャに分割し、
    仕様駆動フローが1スライスずつ消費する1枚のメタスペックとして記録）、
    `git-workflow`（ブランチ/コミット/プッシュ/PR 運用）、
    `aws-research`（AWS 公式ドキュメントの最新調査）
  - ドメインオーバーレイ（一致するライフサイクル操作と組み合わさる。置き換えではない）:
    `digital-agency-frontend`（DADS とダッシュボードガイドブックに基づく、アクセシブルな
    React/Tailwind Web フロントエンド開発・レビュー）、`digital-agency-slides`
    （DADS 公式資材で 16:9 スライドを HTML として作成し、同梱ツールで編集可能な
    PowerPoint に変換）、`scrum-master`（Scrum Guide 2020 だけを規範に、
    Scrumイベント・作成物・アカウンタビリティ・逸脱を診断・改善）、`secure-logging`
    （OWASP Logging Cheat Sheet・ASVS 5.0.0 V16・CWE と、Python・React・AWS Lambda と CDK・
    Google Cloud（Cloud Run functions を含む）・Azure（Azure Functions を含む）・各クラウドの
    AI 推論サービス・GitHub Actions のワークフローの公式ドキュメントにあるログの作法に基づく、アプリケーションと CI のログの実装と
    検査。コードで検証できる項目のみ判定し、運用項目は、リポジトリのインフラコード
    （AWS CDK、Terraform、Bicep）で決まる場合を除き未検証として報告）。
    `secure-logging` は自作の skills ディレクトリ型プラグインとしても構成している
    （`.claude-plugin/plugin.json`、フックなし。詳細は同パッケージの `README.md`）
  - どちらの軸にも分類していない macOS アプリ連携2件: `apple-notes`（同梱の JXA
    スクリプトで Notes.app を読み書き。上書きと削除は SHA-256 ハッシュのゲート付き）、
    `apple-reminders`（Swift ファイル1つからビルドする小さな EventKit CLI で
    Reminders.app を読み書き。[ADR-0013](docs/adr/0013-eventkit-for-reminders-automation.md) 参照）
  - skills ディレクトリ型プラグイン2件を上流のパッケージから取り込んでいる:
    `maintaining-living-documentation`（変更とドキュメントの整合を保つワークフロー。
    フックなし）、`minto-pyramid`
    （あらゆる実質的タスクに Minto 構造を助言的ガイダンスとして適用。`Stop`
    フックの検査はない）。どちらのローカルコピーも上流のフックを削除している
    （`maintaining-living-documentation` は `hooks/hooks.json`、`minto-pyramid` は `Stop` フック）。上流からそのまま再コピーするとフックが復活する。
    オプションは各パッケージの `README.md` を参照。従来の Minto スイート
    （`minto-builder`・`minto-reviewer`・`minto-rewriter`）は同期対象外の
    [`archive/minto-suite/`](archive/minto-suite/) に退避している。`adr` スキルも、採番・言語の規則を `maintaining-living-documentation` へ統合したうえで [`archive/adr/`](archive/adr/) に退避した
  - Spec Kit の `speckit-*` スキルはこのリポジトリでは vendoring しない。各プロジェクトで
    `specify init` を実行した際に、`--integration` が指す各エージェントのディレクトリ
    （`.claude/skills/`、`.agents/skills/`、`.cursor/skills/`）配下に生成される
    プロジェクトローカルな成果物で、すべて gitignore 対象（後述「spec-kit のオプトイン」参照）
- **`team/package-safety/`**: 他の開発メンバーに配布するパッケージインストール安全化バンドル。
  リポジトリの `.claude/settings.json` としても managed settings の drop-in としても使える
  Claude Code 設定ファイル 1 つと、公開から 7 日以上たった版だけを入れるための npm・pnpm・uv の
  テンプレートからなる。`install.sh` の同期対象ではなく、このリポジトリ自身の設定も変えない。
  詳細は[バンドルの README](team/package-safety/README.ja.md) と
  [ADR-0017](docs/adr/0017-team-package-install-safety-bundle.md) を参照
- **[`chatgpt-system-prompt.md`](chatgpt-system-prompt.md)・
  [`claude-ai-system-prompt.md`](claude-ai-system-prompt.md)**: この設定の作業原則を
  ChatGPT と Claude.ai のカスタム指示欄へ持ち込むための、貼り付け用のポータブル
  プロンプト。`install.sh` の同期対象ではない

## 補足ドキュメント

`docs/` は保守者向けで、Claude 向けではありません。`install.sh` は `~/.claude/`
へ同期しないため、`.claude/` 配下からここへリンクしていません（ルールとスキルは
参照元を自分の中に持っています）。

| ドキュメント | 内容 |
|---|---|
| [`docs/claude-config-design.md`](docs/claude-config-design.md) | 常時ロードの指示が通すべき判断基準と、各ファイルが意図的に置いていないもの |
| [`docs/mcp-servers.md`](docs/mcp-servers.md) | MCP サーバーをユーザー自身が入れる理由、`.mcp.json` に書けること・書けないこと、各サーバーのベンダー公式リファレンス、サーバー追加時の更新箇所 |
| [`docs/adr/`](docs/adr/) | アーキテクチャ決定記録 — Accepted 後は不変で、supersede のみ |

## ユーザー設定としてインストール

以下を実行してください:

```sh
bash path/to/my-claude-code/install.sh
```

インストーラーは `~/.claude` を同期し、本リポジトリの Claude Code プラグイン
（後述「プラグイン」参照）をインストール/有効化します。

実行には `claude` CLI と `jq` が必要です。

インストーラーは MCP サーバーの登録・更新・削除を行わず、MCP サーバーを同梱する
プラグインもインストールしません。必要なものは各自で追加してください（後述
「MCP サーバー」参照）。以前のバージョンのインストーラーなどで登録済みの
ユーザースコープ MCP サーバーは、そのまま残ります。

### 重要: 上書き置換（削除同期）について

- 次の管理対象は **置換同期** されます:
  - `rules/`
  - `skills/`
  - `agents/`
  - `commands/`
  - `CLAUDE.md`
  - `install.sh`
- `settings.json` は置換ではなく **マージ同期** されます: このリポジトリが宣言する
  キー（`model`、`permissions`、`hooks` など）は常にリポジトリ側の値が優先されます
  （`permissions` のような共有オブジェクトの内部まで再帰的にマージするため、例えば
  `permissions.deny` は強制されたまま保たれ、同じオブジェクト内の他のキーは影響を
  受けません）。一方、このリポジトリが宣言していないトップレベルのキー——
  `/setup-bedrock` が書き込む `env` や、`enabledPlugins`、
  `agentPushNotifEnabled`、その他ユーザーやCLI自身が追加したキー——はそのまま
  保持されます。
- このリポジトリ側で削除されたファイルは、`~/.claude` 側の置換対象パスでも
  削除されます。
- `agents/` と `commands/` はこのリポジトリに元ファイルがなく、以前のバージョンが
  入れたものを片付けるためだけに管理対象に残しています。そのため実行のたびに
  `~/.claude/agents/` と `~/.claude/commands/` は削除されます。
- `settings.local.json` を含む `~/.claude` の管理対象外パスは保持されます。個人用ファイルは上記の管理対象外に置いてください。

## 代替: `CLAUDE.md` から import

コピーせずに参照する場合:

```markdown
@/absolute/path/to/my-claude-code/.claude/CLAUDE.md
```

## 構成

```text
my-claude-code/
├── CLAUDE.md                       # リポジトリの目的 + @.claude/CLAUDE.md の再エクスポート(リポジトリ内専用, 同期対象外)
├── README.md                       # 英語版ガイド(本書は README.ja.md)
├── README.ja.md
├── install.sh                      # 管理対象の Claude パスを同期 + プラグインをインストール(MCP サーバーは入れない)
├── .mcp.json                       # プロジェクトスコープの MCP サーバー定義。自分で追加するときの参照
├── .living-documentation.json      # maintaining-living-documentation のスクリプト設定(specs/ を除外)
├── chatgpt-system-prompt.md        # ChatGPT のカスタム指示用ポータブルプロンプト(同期対象外)
├── claude-ai-system-prompt.md      # Claude.ai の指示欄用ポータブルプロンプト(同期対象外)
├── docs/                           # 保守者向け文書: 設計根拠、MCP の背景、ADR(同期対象外)
├── tests/                          # オフラインの契約テスト(run-*.sh)と fixture。「検証」参照
├── specs/                          # このリポジトリ自身の変更の Spec Kit 機能仕様
├── .specify/                       # このリポジトリの Spec Kit プロジェクトファイル(テンプレート、スクリプト、git 拡張)
├── archive/                        # 参照用に残した退役スキル(同期対象外)
├── team/package-safety/            # チーム配布用バンドル: Claude 設定 + npm/pnpm/uv テンプレート(同期対象外, ADR-0017)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # main への push/PR ごとに tests/run-*.sh を実行(必須チェック)
│   │   └── dependabot-automerge.yml # パッチ/マイナーのDependabotセキュリティ修正PRをCI通過後に自動マージ
│   └── rulesets/main-required-checks.json # main の必須ステータスチェックruleset定義
└── .claude/                        # インストーラーが管理する Claude パスの正本
    ├── CLAUDE.md                   # 達成目標: 定義 → 実行 → 引き渡し。設計根拠は docs/
    ├── settings.json               # Claude Code のユーザーレベル設定
    ├── rules/                      # 常時ロード: 毎セッション読み込む、独立した5つの関心事
    │   ├── clarifier.md            # 要件確実性: 確認するか進めるか
    │   ├── thinking-lenses.md      # 推論の完全性: 毎タスクに適用する4つのセルフチェック
    │   ├── model-routing.md        # モデルと労力のルーティング: 足りる最小の層、閉じたエスカレーション条件
    │   ├── permissions.md          # 権限と安全性。強制される deny は settings.json
    │   └── pyramid-principle.md    # 実質的な出力に対する読み手本位の構造セルフチェック
    └── skills/                     # 必要時のみ: 関連するときに本文を読み込む、自己記述型
        ├── coder/SKILL.md          # 変更手順 + TDD + SDD + 品質 + 安全 + 型安全性 + ドキュメント
        ├── minto-pyramid/          # 取り込んだプラグイン: 全実質タスクに Minto 構造(ローカル変更: Stop フックなし)
        ├── maintaining-living-documentation/ # 取り込んだプラグイン: 変更とドキュメントの整合(ローカル変更: フックなし)
        ├── clarifier/              # 意図の共通認識を形成し、その後に形式的要件へ
        │   ├── SKILL.md            #   二段構成のプレイブック
        │   └── references/         #   枠組みの在庫(ユーザーに名指す)+ 設計根拠(名指さない)
        ├── problem-definition/SKILL.md # 問題 = 現状とあるべき姿のギャップ
        ├── product-strategy/SKILL.md # 開発着手前のビジョン・ユーザー・提供価値・指標
        ├── meta-spec/SKILL.md      # 1つの取り組み -> 独立して仕様化できるスライスのメタスペック
        ├── git-workflow/SKILL.md   # ブランチ/コミット/プッシュ/PR 運用
        ├── aws-research/SKILL.md   # AWS 公式ドキュメントの最新調査
        ├── digital-agency-frontend/ # DADS React/Tailwind の手順 + 出典付きの参考資料(ドメインオーバーレイ)
        ├── digital-agency-slides/  # DADS 16:9 デッキを HTML で作り編集可能な .pptx へ(ドメインオーバーレイ)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   スライド設計、マークアップ契約、変換、資材の出典
        │   ├── assets/             #   1280x720 のレイアウト CSS + 注釈付きデッキテンプレート
        │   └── scripts/            #   セットアップ、公式資材の取得、DOM 抽出、デッキ CLI
        ├── scrum-master/           # Scrum Guide (2020) だけを規範に、イベント・作成物・アカウンタビリティを診断(ドメインオーバーレイ)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   必要時に読む参考文書3件 + Scrum Guide の PDF
        │       └── templates/      #   すぐ使える Markdown テンプレート8件(作成物 + イベント)
        ├── secure-logging/         # 自作プラグイン: OWASP + 各スタックのログ作法のチェックリスト(ドメインオーバーレイ, フックなし)
        │   ├── SKILL.md            #   プレイブック
        │   ├── README.md           #   インストール、モード、検査の仕組み(README.ja.md: 日本語)
        │   ├── .claude-plugin/     #   プラグインのマニフェスト(secure-logging@skills-dir)
        │   └── references/         #   出典付きチェックリスト(ASVS 5.0.0 V16、CWE、OWASP、各スタックの公式文書)
        ├── apple-notes/            # JXA で Notes.app を操作(macOS アプリ連携)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   プロパティ、スクリプトの使い方、安全な Markdown サブセット、ハッシュゲート
        │   └── scripts/            #   JXA スクリプト + Python のハッシュゲート
        └── apple-reminders/        # EventKit で Reminders.app を操作(macOS アプリ連携)
            ├── SKILL.md            #   プレイブック、ビルド手順、権限モデル
            └── scripts/            #   Swift ソース1つ、Info.plist、build.sh(ビルドした remind-cli は gitignore)
```

## 検証

`.mcp.json` / `install.sh` / `.claude/settings.json` /
`.claude/skills/aws-research/SKILL.md` を変更したら:

```sh
bash tests/run-mcp-startup.sh # ネットワーク接続と書き込み可能な uv キャッシュが必要
bash tests/run-install.sh
bash tests/run-digital-agency-frontend-skill.sh
bash tests/run-digital-agency-slides-skill.sh
bash tests/run-removed-guardrails.sh
```

[`.claude/skills/secure-logging/`](.claude/skills/secure-logging/) を変更したら:

```sh
bash tests/run-secure-logging-skill.sh
bash tests/run-config-pyramid.sh
```

前者は、スキルの構造、チェックリストの出典の規則、プラグインのマニフェスト、
2つの README の見出し構造が一致することを検査し、Claude Code CLI があれば
`claude plugin validate --strict` も実行する。スキルの振る舞いは、
`tests/fixtures/secure-logging/` の見本を使って手で確認する。

[`team/package-safety/`](team/package-safety/) を変更したら:

```sh
bash tests/run-package-safety-bundle.sh
```

バンドル内のファイル同士の整合をネットワークなしで検査する。Claude Code 内での
振る舞いは、[バンドルの README](team/package-safety/README.ja.md#適用されたことの確認)
の手順で手で確認する。

[`.claude/CLAUDE.md`](.claude/CLAUDE.md)・[`.claude/rules/`](.claude/rules/)・
自作スキルを変更したら:

```sh
bash tests/run-config-pyramid.sh
```

設定のピラミッド構造をオフラインで検査する: apex の3分岐、他のルール・スキル・設定
パスを名指さないちょうど5つのルールファイル、自身の除外境界を記述し兄弟スキルを
名指さない自作スキル。対象とする自作スキルは、スクリプト冒頭の `authored_skills`
の一覧である。

[`.claude/skills/apple-notes/`](.claude/skills/apple-notes/) を変更したら:

```sh
bash tests/run-note-write-guard.sh
bash tests/run-note-body-conversion.sh # Node.js が必要
```

どちらもスクリプトから切り出したロジックを検査し、macOS を必要としない。
Notes.app への呼び出しそのものは対象外。`apple-reminders` には自動テストがない。

取り込んだプラグイン（[`maintaining-living-documentation`](.claude/skills/maintaining-living-documentation/)
または [`minto-pyramid`](.claude/skills/minto-pyramid/)）を変更したら、その README の
とおり、そのフォルダで単体テストを実行する:

```sh
python3 -B -m unittest discover -s tests -v
```

`run-digital-agency-slides-skill.sh` の末尾は、公式 DADS スタイルシートを取得して
同梱のデッキテンプレートを変換する end-to-end セクションです。ネットワーク接続と、
`python-pptx` および `playwright` を備えた Python 環境が必要です — `DECK_PYTHON` で
その環境を指定してください。指定がない場合、このセクションは失敗ではなく
スキップとして報告されます。

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

上記のうち5本は `main` への push/PR ごとに CI(`.github/workflows/ci.yml`)でも
自動実行されます: `run-install.sh`、`run-digital-agency-frontend-skill.sh`、
`run-removed-guardrails.sh`、`run-package-safety-bundle.sh`、`run-mcp-startup.sh`。
それ以外は手元で実行したときだけ動きます。`main` はその CI ジョブ(`test`)を必須と
する repository ruleset(`.github/rulesets/main-required-checks.json`)で保護されています。

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

このリポジトリは MCP サーバーをユーザー設定に取り込みません。`install.sh` は
MCP サーバーを登録も削除もせず、`.claude/` 配下も特定のサーバーがあることを
前提にしていません（`aws-research` は、そのセッションで実際に使える
ドキュメントツールを使います）。必要なサーバーは各自で追加してください。

[`.mcp.json`](.mcp.json) は、このリポジトリ内で作業するときのプロジェクトスコープ
定義で、自分で登録するときの参照カタログも兼ねます。`.mcp.json` に書けることや
各サーバーのベンダー公式リファレンスは [`docs/mcp-servers.md`](docs/mcp-servers.md)
にあります。

ユーザースコープに登録するときは、必要な行だけを実行してください（`uvx` を使う
サーバーには [uv](https://docs.astral.sh/uv/) が必要です）:

```sh
claude mcp add -s user aws-knowledge --transport http https://knowledge-mcp.global.api.aws
claude mcp add -s user aws-documentation -- uvx awslabs.aws-documentation-mcp-server@latest
claude mcp add -s user \
  --transport http \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp \
  --header "X-Goog-Api-Key: ${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}"
claude mcp add -s user microsoft-learn --transport http https://learn.microsoft.com/api/mcp
claude mcp add -s user wolfram --transport http https://agenttools.wolfram.com/mcp
```

## プラグイン

`install.sh` は Anthropic 公式マーケットプレイス `claude-plugins-official`
（`anthropics/claude-plugins-official`）から、3 つの Claude Code プラグインを
インストールします: `frontend-design`（UI/UX 実装ガイダンス、Anthropic）、
`code-review`（マルチエージェント PR レビュー、`/code-review ultra` 含む、Anthropic）、
`skill-creator`（skill の雛形作成・評価、Anthropic）。マーケットプレイスが未登録なら
追加し、各プラグインをユーザースコープでインストール/有効化するため、このリポジトリに
限らず全プロジェクトで使えます。

MCP サーバーを同梱するプラグインは、MCP サーバーと同じく必要に応じて各自で
追加してください。インストーラーはインストールも削除もしません。同じ
マーケットプレイスには、たとえば `github`（GitHub 公式 MCP サーバー、GitHub）、
`deploy-on-aws`（AWS アーキテクチャ図 + デプロイ/IaC skill と AWS の MCP サーバー。
デプロイ/AWS CLI 変更系操作は
[`.claude/rules/permissions.md`](.claude/rules/permissions.md) により毎回確認が必要、AWS）、
`microsoft-docs`（Microsoft 公式ドキュメント MCP サーバー + skill、Microsoft）があります。

同等のコマンド:

```sh
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install skill-creator@claude-plugins-official
```

MCP サーバーを同梱するプラグインを入れる場合:

```sh
claude plugin install github@claude-plugins-official
claude plugin install deploy-on-aws@claude-plugins-official
claude plugin install microsoft-docs@claude-plugins-official
```

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
理由は docs/adr/0008 を参照してください。Spec Kit を導入していないプロジェクトへ
`specify init` を勧める指示は `.claude/` のどこにもありません。`coder` スキルが
Spec Kit の工程に従うのは、プロジェクトがすでに導入している場合だけです。
