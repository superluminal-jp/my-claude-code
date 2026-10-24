# パッケージインストール安全化バンドル

English: [README.md](README.md)

開発チームに配布できる Claude Code の設定です。これを適用したプロジェクトで Claude が作業するとき、パッケージインストーラーが第三者のコードを実行するのは次の 5 つの条件を満たす場合だけになります。

1. **通常は公開から 7 日以上たった版だけを解決する**。最新版ではなく、その期間を過ぎた中での最新版を使います。
2. **新しいパッケージの追加、その場限りのパッケージ実行、マシン全体へのインストールは、毎回人が承認する。**
3. **Python のパッケージは uv で扱う。** Claude は `pip install` を実行できません。
4. **パッケージはマシンではなくプロジェクトに入れる。** npm・pnpm のグローバルインストールと `uv pip install --system` は拒否され、pip は仮想環境の外ではインストールしません（[グローバルインストールの禁止](#グローバルインストールの禁止)を参照）。
5. **インストールは OS のサンドボックス内で実行する。** 通信先は公開 npm / PyPI レジストリだけで、主な認証情報ファイルとトークンは読めません。

`gh`、Terraform、SSH 経由の git はサンドボックス内では動かないため、これらのコマンドだけはサンドボックスの外で普段の認証情報を使って動き、リモートに変更を加える操作は毎回承認が必要です（[サンドボックス外で動かすツール](#サンドボックス外で動かすツール)を参照）。

設計判断は [ADR-0017](../../docs/adr/0017-team-package-install-safety-bundle.md) に記録しています。

## 内容

| ファイル | 置き場所 | 役割 |
|---|---|---|
| [`claude-settings.json`](claude-settings.json) | 各リポジトリの `.claude/settings.json`、または managed settings の drop-in | Claude 側の制御：サンドボックスとその除外コマンド、`ask`/`deny` ルール、7 日ルールの `env` |
| [`project/.npmrc`](project/.npmrc) | リポジトリ直下 | npm：7 日ルール、依存の install スクリプト停止 |
| [`project/pnpm-workspace.yaml`](project/pnpm-workspace.yaml) | リポジトリ直下 | pnpm：7 日ルール |
| [`project/uv.toml`](project/uv.toml) | リポジトリ直下（または `pyproject.toml` の `[tool.uv]`） | uv：7 日ルール |

`project/` のファイルは、そのリポジトリでパッケージマネージャーを使う全員（人、CI、Claude）に効きます。`claude-settings.json` が効くのは Claude Code のセッションだけです。

## 適用方法

同じ `claude-settings.json` をどちらの経路でも使えます。まずリポジトリ経由で配り、ルールを無効化できないようにする必要が出たら managed settings に移します。

### リポジトリごと（管理者権限不要・各メンバーが上書き可能）

対象リポジトリの直下で、`BUNDLE` をこのディレクトリに向けて実行します。

```bash
BUNDLE=path/to/my-claude-code/team/package-safety
mkdir -p .claude
[ -f .claude/settings.json ] || echo '{}' > .claude/settings.json
jq -s 'def merge($a; $b): reduce ($b | keys_unsorted[]) as $k ($a; .[$k] = (if ($a[$k] | type) == "object" and ($b[$k] | type) == "object" then merge($a[$k]; $b[$k]) elif ($a[$k] | type) == "array" and ($b[$k] | type) == "array" then $a[$k] + ($b[$k] - $a[$k]) else $b[$k] end)); merge(.[0]; .[1])' .claude/settings.json "$BUNDLE/claude-settings.json" > .claude/settings.json.new && mv .claude/settings.json.new .claude/settings.json
cp -n "$BUNDLE/project/.npmrc" "$BUNDLE/project/pnpm-workspace.yaml" "$BUNDLE/project/uv.toml" .
echo '.pnpm-store/' >> .gitignore
```

マージはリポジトリに既にあるキーとリストの要素をすべて残し、バンドルの分を追加します。2 回実行しても結果は変わりません。`cp -n` は既存のファイルを上書きしないので、既にある場合は各テンプレートのコメントに従って手でキーを追加してください。テンプレートは、そのリポジトリで使うパッケージマネージャーの分だけ置きます。`pyproject.toml` に `[tool.uv]` が既にある場合は、`uv.toml` を置かずにそこへ `exclude-newer` を書きます。結果を commit してください。

メンバーには `ask`/`deny` ルールがすぐに効き、`env` はフォルダーを信頼した後に効きます。メンバーは自分の user / local 設定で `sandbox.enabled: false` にすればサンドボックスを切れるので、この経路は既定値であって保証ではありません。

### Managed settings（管理者権限か MDM が必要・上書き不可）

各端末の managed drop-in ディレクトリにファイルをコピーします。

```bash
sudo mkdir -p "/Library/Application Support/ClaudeCode/managed-settings.d"
sudo cp claude-settings.json "/Library/Application Support/ClaudeCode/managed-settings.d/package-safety.json"
```

Linux と WSL では `/etc/claude-code/managed-settings.d/` です。MDM プロファイルや claude.ai の管理コンソール（server-managed settings）でも同じキーを使えます。managed settings では追加で `"sandbox": {"allowUnsandboxedCommands": false}` を設定でき、サンドボックス外での再実行ができなくなります。このときリポジトリ側のサンドボックスを緩める設定も無視されます。バンドル自身の除外コマンドは managed のファイルに含まれるので引き続き動きます。それ以外のサンドボックス内で動かないコマンド（`docker` や、サンドボックス外に書き込む `brew` など）は、managed の `sandbox.excludedCommands` に追加しない限り Claude から実行できなくなります。

## ツールごとの挙動

| ツール | 7 日ルール | 必要なバージョン | 古いバージョンでは |
|---|---|---|---|
| npm | `.npmrc` と `env` の `min-release-age=7`（日数） | 11.10 | `Unknown … config "min-release-age"` と表示して**無視する**。バージョンを確認すること |
| pnpm | `pnpm-workspace.yaml` の `minimumReleaseAge: 10080`（分） | 10.16 | 非対応（挙動は未確認） |
| pnpm（Claude の `env`） | `pnpm_config_minimum_release_age` | 11 | pnpm 10 は `npm_config_*` しか読まない。リポジトリのテンプレートでは効く |
| uv | `uv.toml` / `[tool.uv]` の `exclude-newer = "P7D"` | 0.9.17 | ファイルを解析できず**失敗する**。更新するまで uv のコマンドはすべて止まる |
| pip | 使わない。Claude の `pip install` は禁止し、uv を使う | — | — |
| Homebrew | 相当する設定がない | — | `brew install`/`upgrade`/`tap` は毎回 Claude が確認を求める。承認する人が公開日を確認する |

uv のルールはあえて `env` に入れていません。プロジェクト自身の設定と異なる `UV_EXCLUDE_NEWER` があると `uv.lock` が無効になり、`uv sync --locked` は失敗し、`uv lock` はファイルを書き換えます。

## グローバルインストールの禁止

パッケージはプロジェクトごとに持ちます（npm と pnpm は `node_modules/`、Python は `.venv/`）。こうすると、Claude が入れたものが他のプロジェクトやマシン全体を変えることはありません。次の 3 層で強制します。

| 層 | 止めるもの |
|---|---|
| `deny` ルール | `npm install -g`、`npm i -g`、`npm install --global`、`pnpm add -g`、`uv pip install --system`、すべての形の `pip install` |
| `PIP_REQUIRE_VIRTUALENV=true` | 他のツールが内部で呼ぶ pip が、仮想環境が有効でないときに `Could not find an activated virtualenv (required).` で終了する |
| サンドボックス | プロジェクト外への書き込み。macOS では npm のグローバル prefix、`~/.local`（pip の `--user`、uv のツール）、pyenv の `site-packages`、`/opt/homebrew` への書き込みを拒否した |

uv はもともとこの方式で動きます。`uv add`・`uv sync`・`uv run` はプロジェクトの `.venv` を使い、`uv pip install` は仮想環境がなければ `--system` を付けない限り止まります。その場限りの実行には、`uvx <tool>`、`uv run --with <package>`、依存をスクリプト内に書いた `uv run script.py` を使えば、それぞれ一時的な環境で動き、何も残りません。

CLI ツールなど、マシンに置くのが正しいものもあります。`uv tool install`・`pipx`・`brew` は使えますが毎回確認が出ます。プロジェクト外に書き込むため、サンドボックス外での再実行を人が承認したときにだけ実行されます。

`deny` ルールはコマンドの文字列で照合するので、フラグの位置が違う形（`npm install some-tool -g`）には効きません。その場合もサンドボックスが書き込みを拒否します。また、人が自分のターミナルで打つコマンドにはどれも効きません。そこでも pip をグローバルな Python に入れないようにするには、各開発者が `pip config set global.require-virtualenv true` を実行するか、シェルの設定に `export PIP_REQUIRE_VIRTUALENV=true` を追加します。PEP 668 の externally managed の印がある Python（Homebrew の Python など）はもともと拒否しますが、pyenv の Python には印がありません。

## サンドボックス外で動かすツール

macOS では、`gh` と `terraform` はサンドボックス内で TLS 検証に失敗し、git は SSH をサンドボックスのプロキシ経由でトンネルできません。サンドボックス内で動かすには、これらが必要とする GitHub トークン・SSH 鍵・クラウドの認証情報を、install スクリプトを含むサンドボックス内のすべてのコマンドに読ませることになります。そこで `sandbox.excludedCommands` で次のコマンドだけを外に出しています。

| 除外するコマンド | 毎回確認する操作 |
|---|---|
| `gh *` | `gh pr merge`、`gh repo delete`、`gh release create`、`gh api` |
| `terraform *` | `terraform apply`、`terraform destroy`、`terraform import` |
| `git fetch`、`git pull`、`git push`、`git clone`、`git ls-remote` | `git push` |

除外したコマンドは普段どおりの権限で動きます。SSH 鍵とエージェント、`gh` に保存したログイン、クラウドの認証情報を使え、どのホストにも接続できます。それでも権限チェック（default モードなら確認、auto mode なら分類器）は通り、右列の操作は必ず確認が出ます。パッケージインストーラーは除外しないので、その install スクリプトはサンドボックス内に留まります。

照合はコマンドの文字列で行い、複合コマンドはすべての部分が一致する必要があります。`git -C dir fetch`、`cd dir && git pull`、`env gh …`、後ろにパイプを付けた形はサンドボックス内に留まって失敗します。たとえば `git -C . ls-remote origin` は SSH のリモートに届かず、`env gh repo view` は `gh` の設定を読めません。これらのコマンドは単独で実行してください。

`terraform init` はプロバイダーをダウンロードし、後でサンドボックス外でクラウドの認証情報とともに実行します。7 日ルールはプロバイダーには効かないので、`.terraform.lock.hcl` を commit し、プロバイダーのバージョン変更は PR でレビューしてください。

## 例外（公開 7 日未満の緊急修正を入れる場合）

例外は人が、見える形で判断します。

- **npm**：自分で `npm install <package>@<version> --min-release-age=0` を実行する。
- **pnpm**：`pnpm-workspace.yaml` の `minimumReleaseAgeExclude` にパッケージ名を追加し、PR でレビューする。
- **uv**：`[exclude-newer-package]` に `some-package = false` を追加し、PR でレビューする。

Claude がこれらを提案した場合も、`ask` ルールにより実行前にそのコマンドが表示されます。

## Python プロジェクトの uv への移行

| これまで | uv では |
|---|---|
| `python -m venv .venv && pip install -r requirements.txt` | `uv venv && uv pip install -r requirements.txt`、または lockfile に移行：`uv init --bare && uv add -r requirements.txt` |
| `pip install <package>` | `uv add <package>`（プロジェクト）または `uv pip install <package>`（環境） |
| `pipx install <tool>` | `uv tool install <tool>` |

`uv sync --locked` は `uv.lock` に記録された内容を、ハッシュも含めてそのとおりにインストールします。

## 既知の限界

- **ルールはコマンドの文字列で照合する。** `deny` と `ask` が効くのは Claude が普段書く形だけで、`/usr/bin/pip`、`sh -c '…'`、`python3.12 -m pip` には効きません。書き方に左右されない境界はサンドボックスです。
- **サンドボックスも完全な境界ではない。** 悪性の install スクリプトはプロジェクト内（`node_modules/` や `.venv/` など）には書き込めて、その内容は後でサンドボックス外で実行されます。auto mode では、許可リスト外のホストを明記したコマンドは auto mode の分類器に回され、許可されることがあります。
- **macOS で確認したサンドボックスの副作用**：
  - npm と uv はキャッシュ（`~/.npm/_cacache`、`~/.cache/uv`）への書き込みが必要で、バンドルで許可しています。npm がキャッシュの root 所有ファイルを理由に `sudo chown` を勧めても、原因は所有者ではなくサンドボックスなので実行しないでください。
  - pnpm はサンドボックスからホームのストアを使えず、プロジェクト直下に `.pnpm-store/` を作ります。`.gitignore` に入れてください。`failed to copy trust settings of system certificate` という表示も出ますが、害はありません。
  - pip は macOS の信頼ストアの参照がサンドボックス内で失敗するため、pip を内部で呼ぶツール向けに `env` で `PIP_USE_DEPRECATED=legacy-certs` を設定しています。TLS を検査するプロキシの内側では、`PIP_CERT` に社内 CA のバンドルも指定してください。
  - `docker` はサンドボックス内で動きません。Claude から使う必要があれば、`docker compose *` のような狭いパターンをリポジトリ側の `sandbox.excludedCommands` に追加します。
- **`.env.example` も読めなくなる。** `Read(**/.env.*)` に含まれるためです。
- **プラットフォーム**：Linux と WSL2 では `bubblewrap` と `socat` が必要です。Windows ネイティブにはサンドボックスがなく、`failIfUnavailable` によって Claude Code が起動しなくなるので、WSL2 を使ってください。
- **プライベートレジストリ**：ホストを `sandbox.network.allowedDomains` に追加します。バンドルは `NPM_TOKEN` などのトークンをサンドボックス内のコマンドから外します。トークンを見せずに認証させるには `mask` エントリーを使いますが、これは user か managed settings からしか有効になりません。

## 適用されたことの確認

リポジトリで Claude Code を再起動し、`/status` の `Setting sources` に project（または managed）settings が出ていることを確認します。続けて次を実行します。

```bash
npm --version
pnpm --version
uv --version
npm config get min-release-age
```

バージョンが上の表を満たし、最後のコマンドが `Unknown` の警告なしに `7` を表示すれば適用されています。Claude に `ls ~/.ssh` を実行させると `Operation not permitted` で失敗し、`pip install requests` や `npm install -g some-tool` を実行させると権限ルールで拒否され、`git ls-remote origin` と `gh auth status` は動くはずです。
