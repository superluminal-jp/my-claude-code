# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`.claude/` ディレクトリ全体を `~/.claude/` に同期することで、settings/rules/skills/memory を
マシン上の全プロジェクトで共通適用できます。

**Codex CLI 向けの移植物はこのリポジトリでは配布しません。** `install.sh` は Codex 設定を一切展開せず、`~/.codex` にも `~/.agents` にも触れません。Codex 側の設定は OpenAI 公式の `/import` で各自生成します — 手順と、何が得られて何が得られないかは [Codex CLI サポート](#codex-cli-サポート)、判断の記録は [ADR-0004](docs/adr/0004-adopt-official-codex-import.md) を参照してください。

英語版: [README.md](README.md)

## このリポジトリで提供するもの

- **`.claude/CLAUDE.md`**: 常時メモリ（原則、応答スタイル、skill インデックス、MCP 参照）
- **`.claude/settings.json`**: モデル既定値、権限ルール
- **`.claude/rules/`**: 常時読み込まれる共通ルール（権限/安全性、確認ルール、skill ルーティング、サブエージェント委譲（独立コンテキストに切り出すか本体で進めるかの判断）、live-documentation、git ワークフロー、MCP カタログ）
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

インストーラーは `~/.claude` を同期し、Claude Code のユーザースコープ MCP を登録/更新します。**Codex 側には何も展開しません** — `~/.codex` と `~/.agents` はユーザーの所有物として一切触れません。

### 重要: 上書き置換（削除同期）について

- 次の管理対象は **置換同期** されます:
  - `hooks/`
  - `rules/`
  - `skills/`
  - `CLAUDE.md`
  - `settings.json`
  - `install.sh`
- このリポジトリ側で削除されたファイルは、`~/.claude` 側でも削除されます。
- 個人用ファイルは管理対象外の場所に置くか、別バックアップから再適用してください。

## Codex CLI サポート

このリポジトリは **Codex 向けの移植物を配布しません**。Codex 設定は OpenAI 公式の import フローで各自の環境に生成します。判断の記録は [ADR-0004](docs/adr/0004-adopt-official-codex-import.md)、根拠となる実測は [`specs/021-codex-official-import/`](specs/021-codex-official-import/) にあります。

> 以下の挙動に関する記述はすべて **Codex 0.147.0 で 2026-08-10 に測定**したものです。対象は変化するソフトウェアなので、バージョンが動いていたら `tests/run-codex-drift.sh` を実行し、第三者の移行ガイドより実測を優先してください。

### 指示文は import なしで届く

リポジトリ直下の [`AGENTS.md`](AGENTS.md) を Codex はそのまま読みます（git root から作業ディレクトリまでを走査して連結）。インストーラーも import 手順も不要です。

**平坦に保ってください。** Codex は `@path` の import を展開しません（[openai/codex#17401](https://github.com/openai/codex/issues/17401) は未解決）。`CLAUDE.md` のように `.claude/rules/*.md` へ委譲できないため、Codex に届けたい規則は `AGENTS.md` に直接書きます。

### スキル・MCP・フックのセットアップ

**`/import`**（Codex CLI 内の対話コマンド）を使います。`codex import` というサブコマンドは存在せず、実行中タスク・リモートセッション・app-server 接続中は利用できません。

```bash
codex          # 対話セッションを開始
# /import  →  Claude Code を選択  →  取り込む対象を選択
```

指示文は `AGENTS.md` へ、`settings.json` は `config.toml` へ変換され、スキル・MCP・フック・スラッシュコマンド・サブエージェント・メモリ・直近のチャットが取り込まれます。書き込み先は `~/.codex` と**プロジェクト配下（`.codex/`、`.agents/`）の両方**で、後者は gitignore 済みのため import してもコミット対象の差分は出ません。実行後に `git status` で確認してください。

**任意: 事前確認。** `migrate-to-codex` スキルは非対話 CLI を同梱しており、読み取り専用モードで「何が起きるか」を確認できます。

```bash
M=~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate-to-codex.py
python3 "$M" --source ./.claude/ --scan-only
python3 "$M" --source ./.claude/ --target ./.codex/ --doctor
python3 "$M" --source ./.claude/ --target ./.codex/ --dry-run
python3 "$M" --validate-target ./.codex/     # import 後の検証
```

⚠️ **書き込みモードはこのリポジトリでは実行しないでください。** 直下の `AGENTS.md` を `CLAUDE.md` への symlink に置き換えて上記の指示文を破壊し、全スキルをコピーで上書きします。起きた場合は `git checkout AGENTS.md` で復旧できます。`/import` はどちらも行いません。

### Codex が強制するもの／しないもの

Claude Code はもうこの領域で自動的に何も強制しません。`.claude/hooks/` は
全ファイルが削除され、代替の仕組みはありません。Claude Code に残る唯一の
ガードレールは `.claude/settings.json` の `permissions` allow/ask/deny
リストで、これは hooks とは独立しており今回の削除の影響を受けません。
Codex は import して信頼すれば、Claude Code より**多く**強制するように
なりました — import 後に Codex TUI で `/hooks` を開き、**取り込まれた
フックを信頼**してください。非管理フックは定義ハッシュが信頼されるまで
実行されず、フック変更のたびに再確認が必要です。設定すべきフィーチャー
フラグはありません（`hooks` は stable かつ既定で有効）。

| ガードレール | Claude Code | Codex |
|---|---|---|
| 破壊的コマンドの遮断 | **なし**（hooks 削除済み） | **あり**（信頼後）— エンドツーエンドで検証済み |
| プロンプト秘密スキャン | **なし**（hooks 削除済み） | **あり**（信頼後）— ターンが停止しモデル応答なし |
| 編集時保護（`.git/`、`main`/`master`） | **なし**（hooks 削除済み） | **なし** |
| 編集後の自動フォーマット/lint | **なし**（hooks 削除済み） | **なし** |
| コマンドの allow/prompt 方針 | **あり** — `.claude/settings.json` の `permissions` ブロック（hooks とは独立、削除対象外） | **なし** — Codex 既定（確認を求める側）にフォールバック |
| Spec Kit のプロンプト展開 | **なし**（hooks 削除済み） | **なし** — 対応イベントが存在しない |

上記「なし」のうち最初の3つは同一の構造的理由です: **Codex の `PreToolUse`/`PostToolUse` はシェルコマンドにしか発火しません。** Codex の編集は `apply_patch` を通り、これらのイベントからは見えないため、`Edit|Write|Delete` に一致するフックは取り込まれても実行されません。設定では解決できません。hosted tools（WebSearch 等）も対象外です。

さらに2点:

- **フックは設定レイヤーごとに1回ずつ発火します。** Codex はレイヤーを上書きせずマージするため、`~/.codex/hooks.json`・`~/.codex/config.toml`・`.codex/hooks.json` に同じフックがあると毎ターン3回走り、`loading hooks from both … prefer a single representation for this layer` と警告されます。1レイヤーにつき1表現に保ってください。
- **`.codex/hooks/` にスクリプトがあること自体は実行の証拠になりません。** `/import` は登録しないスクリプト（`statusline.sh` など）もコピーします。実際の配線は `.codex/hooks.json` を見て確認してください。

**Claude 側もこの変更の影響を受けます。** `.claude/hooks/pre-edit.sh` はもう存在せず、Claude Code は編集保護を一切強制しません。Claude Code 側に残るガードレールは `.claude/settings.json` の `permissions` ブロックだけで、これは `scripts/guardrails/*.sh` と判定ロジックを共有していません（共有していたのは、今回削除されたフックラッパーの役目でした）。`scripts/guardrails/*.sh` は、引き続き Codex 側で動作する2つのガードが呼び出す共有判定ロジックとして残ります。

### その他の変換ギャップ

- **スキルは symlink ではなくコピーで届きます。** `/import` は不足分だけ追加し既存には触れませんが、以降 `.claude/skills/` を編集しても再 import するまで反映されず、ずれを検出する仕組みもありません。
- **生成されたサブエージェントはサポート対象外です。** `/import` は `.codex/agents/*.toml` を作りますが、Codex のカスタムエージェントは既定値を設定するだけで親ターンからコンテキストを隔離しないため、このリポジトリでは依存しません。
- **`speckit-*` スキルは移行不要**です（`specify init --integration codex` が各プロジェクトで再生成 — [ADR-0001](docs/adr/0001-remove-vendored-speckit-skills.md)）。
- `--doctor` が `readiness: low` と多数の手動確認項目を出すのは想定内です。Claude 固有のスキル frontmatter（`when_to_use`、`metadata`、`argument-hint`、`context`）が挙動ではなく散文になるためです。

### 以前のバージョンをインストールしていた場合

旧版はホームディレクトリに Codex ファイルを展開していました。現在の `install.sh` はユーザー所有の Codex 設定に触れないため、**自動では削除しません**。整理したい場合は手動で削除してください。

- `~/.codex/hooks/*-adapter.sh`
- `~/.codex/rules/guardrails.rules`
- `~/.codex/prompts/verify-config.md`
- `~/.agents/skills/`（8 個の symlink）
- `~/.codex/config.toml` 内の `# >>> my-claude-code managed hooks` / `# >>> my-claude-code managed MCP servers` 区間

managed hooks 区間を残したままにすると、上記の多重発火警告の原因になります。

### この節を古びさせないために

`tests/run-codex-drift.sh` がこの節の前提となる上流の事実（`DRIFT-01`〜`DRIFT-06`）を再導出します。`codex` 未インストール環境では SKIP します。警告が出たら [`quickstart.md`](specs/021-codex-official-import/quickstart.md) の Step 4–5 を再実行し、上記の測定日を更新してください。

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
├── scripts/
│   ├── check-mcp-consistency.sh
│   └── guardrails/
├── AGENTS.md                        # Codex CLI がそのまま読む平坦な指針（@ import 不可）
├── .mcp.json
└── .claude/
    ├── CLAUDE.md
    ├── settings.json
    ├── rules/
    └── skills/
```

## 検証

`.mcp.json` / `install.sh` / `.claude/settings.json` / `.claude/rules/mcp.md` を変更したら:

```sh
./scripts/check-mcp-consistency.sh
bash tests/run-mcp-startup.sh # ネットワーク接続と書き込み可能な uv キャッシュが必要
bash tests/run-digital-agency-frontend-skill.sh
./tests/run-prompt-secret-guard.sh
./tests/run-codex-references.sh
./tests/run-codex-drift.sh
```

リポジトリのファイルを検査するだけの決定的なスイートです。

## MCP サーバー

プロジェクトスコープ定義は `.mcp.json` にあります。  
カタログ（transport / パッケージ更新方針等）は [`.claude/rules/mcp.md`](.claude/rules/mcp.md) を参照してください。

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
# specify init --here --force --integration codex
# specify init --here --force --integration cursor-agent
specify extension add git
```

- `uv tool install ... @vX.Y.Z` — ブランチ追従ではなく、明示的なリリースタグ
  （`vX.Y.Z` を置き換える）を指定してインストールすることで、再現可能な状態を保ちます。
- `specify self upgrade` — 内蔵のアップデーターで `specify` CLI 自体を
  最新リリースに更新します。
- `specify init --here --force --integration <agent>` — `/speckit.*`
  スラッシュコマンドを、そのプロジェクト自身の `.claude/skills/`（または
  指定した `--integration` に対応するパス。例: `codex` なら
  `.agents/skills/`、`cursor-agent` なら `.cursor/skills/`）配下に
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

すでに導入済みのプロジェクトの Spec Kit を最新に保つのは、今では手動の
作業です — 自分で定期的に `specify init` / `specify self upgrade` を実行して
ください。以前は `/speckit-*` コマンド実行前にこれを自動で行っていた hook
（`speckit-expand-update.sh`）は、`.claude/hooks/` の他のファイルとともに
削除され、代替の仕組みはありません。`.specify/` が未導入のプロジェクトへ
`specify init` を提案するのは、引き続き `CLAUDE.md` 自体の指示です。
