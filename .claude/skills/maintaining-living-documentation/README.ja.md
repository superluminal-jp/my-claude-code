# Maintaining Living Documentation — Claude Code スキルとプラグイン

プロジェクトの変化に合わせて、実装・仕様・意思決定・証拠・ドキュメントの整合を保つための、持ち運べる Claude Code スキルです。同じフォルダーは Claude Code プラグインでもあります。上流ではフックでワークフローを強制しますが、このコピーはフックを登録しません（[チェックの仕組み](#チェックの仕組み)を参照）。

## インストール

個人インストール（自分のすべてのプロジェクト）:

```bash
cp -R maintaining-living-documentation ~/.claude/skills/
```

プロジェクトインストール（リポジトリをクローンする全員。CI テンプレートもこの配置を前提とする）:

```bash
mkdir -p .claude/skills
cp -R maintaining-living-documentation .claude/skills/
```

フォルダーに `.claude-plugin/plugin.json` があるため、Claude Code はどちらの場所からでも skills ディレクトリのプラグイン（`maintaining-living-documentation@skills-dir`）として読み込みます。

- スキル（`SKILL.md`）が使えるようになります。
- このコピーは `hooks/hooks.json` を削除しているため、フックは登録されず、自動では何も強制されません。以下のフックに関する節は、上流からこのファイルを戻した場合にだけ当てはまります（[必須にする方法](#必須にする方法)を参照）。

プロジェクトスコープのプラグインは、プロジェクトフォルダーのワークスペース信頼ダイアログを承認した後にだけ、しかもセッションを開始したフォルダーの `.claude/skills/` からだけ読み込まれます。`-p` での実行は信頼の承認とみなされません。ファイルを残したままプラグインを無効にするには、設定ファイルで `"enabledPlugins": {"maintaining-living-documentation@skills-dir": false}` を指定します。スキルは残してフックの効果だけを止めるには、プロジェクトの `.living-documentation.json` で `"enforcement": "off"` を指定します。

その他の読み込み方法として、1セッションだけ使う `claude --plugin-dir ./maintaining-living-documentation` と、プラグインマーケットプレイスでの公開があります。これらから読み込んだ場合、スキル名は `/maintaining-living-documentation:maintaining-living-documentation` になります。

## 必要なもの

- Python 3.9 以降（標準ライブラリのみ）。フックは `python3` を呼び出します。Python 3 の名前が異なる環境（例: Windows の `py`）では `hooks/hooks.json` を編集します。
- Git は任意です。Git があると、ファイル一覧が `.gitignore` に従い、`audit.py`、`check_links.py --changed`、Stop フックのゲートが使えるようになります。
- Claude Code v2.1.196 以降では、`SKILL.md` のプロジェクトルートが自動で埋められます。それより古いバージョンや他のエージェント実行環境では、`SKILL.md` に書かれているとおりリポジトリルートを使います。
- `claude plugin eval` には Claude Code v2.1.269 以降が必要です。

## 構成

- `SKILL.md` — 規範の根拠、常時の指示、ワークフロー、完了報告の書式。
- `README.md`、`README.ja.md` — このガイドの英語版と日本語版。両方を同期させる。
- `.claude-plugin/plugin.json` — プラグインのマニフェスト。公開前にプレースホルダーの `author` を置き換える。
- `hooks/hooks.json`（このコピーでは削除済み。上流のみ） — `SessionStart`、`UserPromptSubmit`、`Stop` のフック。シェルを必要としないよう exec 形式（`command` と `args`）で書かれている。
- `hooks/rule.md` — `SessionStart` フックが Claude のコンテキストに追加する必須ルール。`hooks.json` がない間は使われないが、ワークフローの説明としては有効。
- `references/` — 規格の適用範囲、実践、参考文献。
- `scripts/` — 読み取り専用の調査、変更監査、関連文書の検出、リンク検査の補助スクリプトと、フック用スクリプト。
- `schemas/` — 任意のプロジェクト設定の JSON Schema。スクリプトが実行時に読み込むため、受け付けるキーの唯一の定義になる。
- `templates/` — 予備の文書テンプレート（対象プロジェクトに慣習がない場合だけ使う）と CI ワークフローのテンプレート。
- `evals/` — `claude plugin eval` 用の振る舞いテスト。
- `tests/` — スクリプトの単体テスト。

このスキルは `docs/`、`specs/`、ADR の配置、プログラミング言語、ビルドシステム、CI プロバイダーを**指定しません**。対象プロジェクトの構造を見つけて、それに従います。

## スクリプト

| スクリプト | 目的 | Git が必要か |
|---|---|---|
| `scripts/inspect_project.py` | 成果物の種類（実装、ドキュメント、仕様、意思決定、証拠、生成物、インフラ、設定）と変更履歴ファイルを一覧にする | いいえ |
| `scripts/audit.py` | 変更ファイルを分類し、ドキュメントへの影響の可能性を挙げる。名前変更・削除されたファイル、変更履歴の記載漏れ、承認済み意思決定記録の編集も含む | はい |
| `scripts/find_related.py` | 変更で古くなりうる文書を近い順に挙げる。変更ファイルの隣（P1）、それに言及する文書（P2）、プロジェクトの変更履歴（P3）、変更ファイル自身のコメント（P0、助言のみ）。`related.*` 設定に従う | はい |
| `scripts/check_links.py` | ローカルの Markdown リンク、画像、参照定義、HTML の `href`/`src`、見出しアンカーを検査する。コードブロックとコメントは無視する | `--changed` の場合のみ |
| `scripts/stop_gate.py` | ルールを注入し、ワークフローを強制する `SessionStart`/`UserPromptSubmit`/`Stop` フック | はい（Git がなければ何もしない） |

どこからでも実行できます:

```bash
SKILL_DIR=~/.claude/skills/maintaining-living-documentation
python3 "$SKILL_DIR/scripts/inspect_project.py" --root /path/to/repo
python3 "$SKILL_DIR/scripts/audit.py" --root /path/to/repo --base origin/main
python3 "$SKILL_DIR/scripts/find_related.py" --root /path/to/repo --base origin/main
python3 "$SKILL_DIR/scripts/check_links.py" --root /path/to/repo --changed --base origin/main
```

すべてのスクリプトが `--json` を受け付けます。終了コードは、`0` が成功、`1` が指摘あり（`check_links.py` のエラー）、`2` が使い方・設定・Git のエラーです。

`check_links.py` はリンクの検査であり、整合性の検証ではありません。ドキュメントと振る舞いは比較しません。ルート相対リンク（`/path`）とアンカーは、静的サイトジェネレーターごとに解決方法が異なるため、警告として報告します。サイト絶対リンクには `--site-root <dir>` を、警告を失敗として扱うには `--strict` を指定します。

### 読み取り専用スクリプトの事前承認

Claude が4つの読み取り専用スクリプトを確認なしで実行できるようにするには、設定ファイルの `permissions.allow` に次のルールを追加します:

```json
"Bash(python3 *maintaining-living-documentation/scripts/inspect_project.py*)",
"Bash(python3 *maintaining-living-documentation/scripts/audit.py*)",
"Bash(python3 *maintaining-living-documentation/scripts/find_related.py*)",
"Bash(python3 *maintaining-living-documentation/scripts/check_links.py*)"
```

末尾の `*` を `.py` の直後に置くのは、引用符で囲んだパスの閉じ引用符まで含めるためです。このスキルは `allowed-tools` を宣言しません。Claude Code 2.1.289 では、`allowed-tools` を宣言するとスキルの呼び出し自体に承認が必要になり、非対話の実行ではスキルを読み込めなくなりました。

## 任意のプロジェクト設定

スクリプトは設定なしで動きます。分類や強制の度合いを調整するには、対象プロジェクトのルートに `.living-documentation.json` を置きます。例:

```json
{
  "enforcement": "warn",
  "implementation_globs": ["spec/support/**"],
  "exclude_globs": ["fixtures/**"]
}
```

すべてのキーは `schemas/config.schema.json` で定義されています。

- `enforcement`: Stop フックのゲートとセッション開始時のルールについて、`block`（既定）、`warn`、`off` のいずれかを指定する。環境変数 `LIVING_DOCS_GATE` がこれを上書きする。
- `<category>_globs`: いずれかのパターンがファイルに一致すると、そのファイルには組み込みの判定の代わりにこれらの種類が使われる。誤検出の修正に使う。例: `"implementation_globs": ["spec/support/**"]`。
- `exclude_globs`: 組み込みの除外に追加する。組み込みの除外は、任意の深さの VCS メタデータ、`node_modules`、仮想環境、キャッシュと、トップレベルの `dist`、`build`、`target`、`vendor`、`out`、`site`、`_build`。
- パターンはプロジェクト相対の POSIX パスに一致する。`*` は `/` もまたぎ、先頭の `**/` はトップレベルにも一致する。
- エディターで `schemas/config.schema.json` に照らして検証できるよう、`"$schema"` キーを置いてよい。
- `related`: 関連文書の検出の設定。`related.max_candidates`（1以上の整数、既定 10）は、`find_related.py` が挙げ、ゲートが強制する関連文書の数で、近いものを残し、残りは `truncated` に数える。`related.min_name_length`（1以上の整数、既定 6）は、変更ファイルへの言及とみなすファイル名の最短の長さで、それより短い名前はパス全体が現れた場合だけ一致する。不正な値はキー名とともに拒否される。

## チェックの仕組み

ワークフローの正本は `SKILL.md` です。この節は、このコピーでそのチェックがどう行われるかをまとめたものです。

チェックはスキルが呼び出されたときにだけ行われます。Claude が `SKILL.md` に従って、自分の変更を自分で確認します。このコピーはフックを登録しないため、自動では何も動きません。スクリプトとプロジェクト自身の検査が機械的に確かめるのは、変更が影響しうる文書と、ローカルリンクが解決するかどうかだけです。文書の内容が正しいかどうかは Claude 自身が読んで判断するため、自己点検にとどまります。

### ワークフロー内のチェック

| ワークフローのステップ | 確認する内容 | 方法 |
|---|---|---|
| 3. 影響の評価 | どの種類の成果物が変わり、どのドキュメントに影響しうるか | `audit.py`。ヒントは判定ではなく、答えるべき問い |
| 3. 影響の評価 | 変更で古くなりうる文書。変更ファイルの隣（P1）、それに言及する文書（P2）、変更履歴（P3）。変更ファイル内のコメント（P0）は助言のみ | `find_related.py`。Claude は挙がった文書をそれぞれ更新するか、変更不要の理由とパスを最終メッセージに書く |
| 5. 検査 | Markdown のローカルリンクとアンカー | `check_links.py --changed`。ドキュメントと振る舞いは比較しない |
| 5. 検査 | プロジェクトのテスト、文書ビルド、スキーマ検査、linter、generator | Claude が実行し、失敗を直して再実行する。全部通るか、2回直しても失敗が残るか、失敗が変更の範囲外なら止める。残ったものは `Unresolved` か `Checks` に書き、実行できなかった検査は理由とともに書く |
| 5. 検査 | ドキュメントが変更と一致しているか | Claude 自身が読んで判断する。破壊的変更や公開契約の追加・変更では、別のコンテキストのサブエージェントがドキュメントと差分を比べるべき（SHOULD）。アーキテクチャ記述、仕様、利用者向け文書のその他の変更では任意（MAY） |

### 報告での判定

`Documentation impact` の下の報告には、1行に1つの判定を書きます。

| 行 | 判定 |
|---|---|
| `Updated:` / `Created:` | 文書が、その行に書いた正本と一致している |
| `No change needed:` | 適用外。理由を添える |
| `Unresolved:` | 分かっている不一致と、それを解消する方法 |
| `Unverified:` | 未確認。判断に必要な証拠を添える |
| `Checks:` | 実行した検査とその結果、または実行できなかった理由 |

文書を編集しただけでは、正しい証拠になりません。正本との一致を確かめていない文書は `Unverified:` に入れます。ドキュメントに影響しない変更は、`Documentation impact: none — <理由>` の1行で済ませます。

### このコピーが強制しないもの

| 仕組み | 確認する内容 | このコピーでの状態 |
|---|---|---|
| Stop フック（`scripts/stop_gate.py`） | 報告があり実質的な理由か根拠を示していること、リンクが切れていないこと、関連文書がすべて処理されたこと | `hooks/hooks.json` を削除しているため未登録。[必須にする方法](#必須にする方法)を参照 |
| CI（`templates/ci/github-actions.yml`） | プルリクエストでの影響監査（助言）と変更範囲のリンク検査 | テンプレートのみ。プロジェクトがワークフローにコピーした後にだけ動く（[CI 連携](#ci-連携)を参照） |
| 振る舞い eval（`evals/`） | Claude が更新すべき文書を更新し、それ以外に触れないか | `claude plugin eval` で実行したときだけ動き、あなたの認証情報でモデルを呼び出す（[Evals](#evals)を参照） |
| 単体テスト（`tests/`） | スクリプトと `SKILL.md` の構造 | 必要なときに実行する（[テスト](#テスト)を参照）。ドキュメントの正しさは判定しない |

Stop フックは、登録されていても、ドキュメントが正しいかどうかまでは判定できません（[既知の限界](#既知の限界)を参照）。正しさを支えるのは、Claude 自身が読んでの確認、別のコンテキストでの比較、人によるレビューです。

## 必須にする方法

Claude はスキルが関連すると判断したときにスキルを適用します。Claude Code がスキルを事前に読み込んだり強制したりすることはできません。CLAUDE.md と `.claude/rules/` は毎セッション読み込まれますが、指針にとどまります（Claude Code のドキュメントの表現では "context, not enforced configuration"）。機械的に強制するのはフックと CI です。各層は次のとおりです。

| 層 | 役割 | 強さ |
|---|---|---|
| スキル（`SKILL.md`） | 規範の根拠、ワークフロー、参照資料、スクリプト | Claude が関連すると判断したときに適用 |
| ルール（`SessionStart` フックが注入、または `.claude/rules/living-documentation.md`） | セッション開始時とコンパクション後に毎回、スキルを使い `Documentation impact` 報告で終えるよう Claude に伝える | 強い指針だが強制ではない |
| Stop フック（`scripts/stop_gate.py`） | セッション中にファイルが変更された場合、次のいずれかが続く間は Claude の終了を止める。変更範囲のリンクが切れている。コード・仕様・設定・インフラ・意思決定のファイルが報告なしに変更された。報告が「none」に実質的な理由を示していない、またはドキュメントが変更されていないのに根拠を示していない。変更ファイルの関連文書が更新も言及もされていない | Claude Code 内で強制 |
| CI（`templates/ci/github-actions.yml`） | プルリクエストでのリンク検査 | マージ前に、すべての貢献者とツールに対して強制 |

フォルダーがプラグインとして読み込まれる場合、最初の3層は設定不要です。CLAUDE.md への記載も不要です。ルールはフックかルールファイルで Claude に届き、CLAUDE.md に写すと重複になります。プロジェクトで他のコーディングエージェントも使う場合は、ルールの箇条書きをそのエージェントの指示ファイル（例: `AGENTS.md`）に入れます。

### プラグインとして読み込まれない場合

ポリシーでプラグインが制限されている場合や、フォルダーが skills ディレクトリの外にある場合は、`hooks/hooks.json` の `hooks` オブジェクトを設定ファイルにコピーし、`${CLAUDE_PLUGIN_ROOT}` をフォルダーのパス（プロジェクトなら `${CLAUDE_PROJECT_DIR}/<path>`）に置き換えます。フックに頼らず、ルールを目に見えるファイルとしてコミットするには、`hooks/rule.md` を `.claude/rules/living-documentation.md` にコピーします。そうするとフックはルールを追加しなくなります。

### ゲートの動作

- セッション開始時に未コミットの変更の状態を記録するため、セッション前からあった変更ではゲートは発動しない。また、`.claude/rules/living-documentation.md` がプロジェクトにも `~/.claude/` にもなければ、`hooks/rule.md` をスキルのインストールパスとともに Claude のコンテキストに追加する。
- 各ターンの開始時（`UserPromptSubmit`）にもワークツリーの状態を記録する。`end_turn` の後の各停止では、ワークツリーがそのターン開始時の状態、セッションの基準状態、前回通過した検査のいずれとも異なる場合にだけゲートが動くため、ターンの合間の編集では発動しない。
- 検査に失敗すると停止を止め、何が足りないかを Claude に伝える。止めるときには、前の回答を繰り返さないよう Claude に求める。同じワークツリー状態を止めるのは最大2回（`LIVING_DOCS_GATE_MAX_BLOCKS`）で、ゲート自身が止めた直後（`stop_hook_active`）には止めない。その後は停止が許され、利用者には警告が表示される。Claude Code も、連続する Stop のブロック回数に上限を設けている。
- ゲートが確認するのは次の点である。報告があること。リンクが切れていないこと。`Documentation impact: none` の行が、空でも定型句でもない理由を示していること。ドキュメントファイルが変更されていないときの報告に、`Updated:` 行、実質的な理由のある `No change needed:` 行、またはそのような `none` 行があること。関連文書（変更ファイルの隣、それに言及する文書、プロジェクトの変更履歴）がすべて変更されたか、最終メッセージでパスが挙げられていること。助言用のコメント記録（P0）は強制しない。ドキュメントが正しいかどうかは判定できないため、レビューと CI は引き続き必要である。

### 既知の限界

- 正しさは判定しない。具体的に聞こえるが中身のない理由でも通る。定型句の一覧は固定で、設定では拡張できない。
- 関連文書のパスを最終メッセージで挙げれば足りる。ゲートを通すためだけに挙げた場合でも同じである。
- 言及の判定は単語単位の文字列一致である。ファイル名を出さずにそのファイルを説明する文書は見つからず、多くのパスを挙げる文書は多くの変更の候補になる。凍結した履歴文書（例: 完了した機能仕様）を持つプロジェクトは、それらを `exclude_globs` に入れる。このリポジトリの直近30件の非マージコミットで測ったところ、変更あたりの関連文書数の中央値は、`specs/**` を除外する前は既定の上限 10 に張り付き、除外後は 1 だった。
- 数えるのは、プロジェクトルートにあるプロジェクト自身の変更履歴だけである。vendor したサブツリー内の changelog は無視する。
- コメントは関数単位ではなくファイル単位で、助言としてだけ確認する。
- 以下の振る舞い eval はこのリポジトリでは実行していない。ルールがモデルの書くものを変えるかどうかは測定していない。
- Git のワークツリー外、Git がない場合、内部エラーの場合、ゲートは何もしない（fail open）。状態はプロジェクトではなく、システムの一時ディレクトリに保存する。

## CI 連携

`templates/ci/github-actions.yml` は、プルリクエストで影響監査（助言）と変更範囲のリンク検査を実行します。プロジェクトインストールのパスを前提としているため、対象プロジェクトの `.github/workflows/` にコピーして調整します。他の CI システムでも同じコマンドを実行できます。

## Evals

`evals/` には `claude plugin eval` 用の振る舞いケースがあります。各ケースは小さな Git プロジェクトを用意し、決定的な grader（judge モデルなし）で結果を確認します。3つのケースは次を確認します。設定の既定値を変えると、設定文書、変更履歴、報告も更新されること。振る舞いを保つ名前変更ではドキュメントに触れず、`Documentation impact: none` と報告すること。承認済みの決定を覆す変更では、記録を作ったり承認済みの記録を編集したりせず、新しい記録を提案すること。さらに3つのケースは関連文書の規則を確認します。`updates-adjacent-doc`（新しいオプションが、ツールの隣の README に反映される）、`creates-doc-for-new-contract`（扱う文書のない新しい公開モジュールに Markdown 文書が作られ、意思決定記録と changelog は作られない）、`no-creation-for-internal-refactor`（非公開ヘルパーの名前変更では文書を作成も編集もしない）です。この3つは足場です。fixture はテスト済みですが実行はしていないため、承認された費用上限で実行するまでは grading パターンは未検証です。このフォルダーから次を実行します:

```bash
claude plugin eval . --scaffold --allow-tools Edit Write --trust-plugin --no-publish --max-cost-usd 10
```

`--scaffold` は各ケースの `fixture.sh` を実行して、テストプロジェクトを作ります。各ケースはプラグインありとなしで実行し、その差（`Δ`）がプラグインの寄与です。実行時はあなたの認証情報でモデルを呼び出します。モデルの更新を回帰と取り違えないよう、CI では `--model` を固定します。

## テスト

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate --strict .
```

Claude Code CLI がインストールされていれば、単体テストは `claude plugin validate` も実行します。

## ローカルでの変更

このコピーは my-claude-code に vendor したもので、上流のパッケージとは以下の点が異なります。上流から更新するときは、これらを再適用します。

- `references/practices.md` の Decision records: *Numbering* と *Language* の項目（廃止した `adr` スキルから。`archive/adr/` を参照）と、*Local convention (my-claude-code)* の項目（意思決定記録の配置、状態の値、言語）。
- 関連文書の検出と処分（`specs/` 配下の仕様 043〜049）:
  - `scripts/find_related.py` は新規。
  - `scripts/stop_gate.py` は、関連文書、`none` 宣言の理由、ドキュメントが変更されていないときの報告の根拠を確認する。
  - `scripts/common.py` は整数とオブジェクトの設定を検証する（追加のみ: `_check_type` と `_check_members`）。
  - `schemas/config.schema.json` に `related` 設定を追加。
  - `references/practices.md` に *Layers, placement, and proximity* の節を追加。`references/bibliography.bib` に `GoogleSWE2020`、`PEP8`、`LinuxKernelStyle`、`Diataxis` を追加。
  - `SKILL.md` に `find_related.py` のコマンド、処分と作成の規則、報告の `Created:` 行を追加。`hooks/rule.md` にそのための1文を追加。
  - `evals/` に3ケースを追加（未実行）。`tests/test_scripts.py` は以上すべてを扱う。
- 検証の判定（仕様なし）: `SKILL.md` で、報告の `Updated:` 行と `Created:` 行に正本を明記し、`Unverified:` 行を追加して `Unresolved:` を既知の不一致に絞り、Step 5 の再実行に上限を設け、Step 5 を自己点検と明記したうえで、破壊的変更や公開契約の変更では別のコンテキストでの比較を SHOULD に上げた。`tests/test_scripts.py` が報告の行を扱う。
- ドキュメント: `README.md` に *How checks work* の節を追加し、冒頭の説明をフックのないこのコピーに合わせた。`README.ja.md` は `README.md` の日本語訳（新規）。
- スタックの慣習（仕様なし）:
  - `references/practices.md` に *Stack conventions* の節（Python、TypeScript、Terraform、Bicep、GitHub Actions のファイル内リファレンス文書）を追加。`references/bibliography.bib` に `PEP257`、`TSDoc`、`TFModuleStructure`、`BicepParameters`、`BicepLintDescription`、`GHActionMetadata` を追加。
  - `SKILL.md` の Step 4 からその節を参照する。
  - `scripts/common.py` は、`.bicepparam`、`action.yml`、`action.yaml`、`cdk.json` をインフラに、`host.json`、`function.json`、`<name>.config.{js,cjs,mjs,ts,cts,mts}` を設定に分類する。
  - `tests/test_scripts.py` は以上すべてを扱う。

## セキュリティ

同梱のスクリプトは、ネットワークにアクセスせず、パッケージをインストールせず、プロジェクト設定から得たコマンドを実行しません。呼び出すのは読み取り専用の Git コマンド（`rev-parse`、`ls-files`、`diff`、`merge-base`、`status`）だけです。どのスクリプトもプロジェクトのファイルに書き込みません。`stop_gate.py` は状態をシステムの一時ディレクトリに保存します。eval の fixture は `--scaffold` を指定したときだけ実行されます。
