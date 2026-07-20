# Research: `.claude` 設定の Codex CLI への包括移植と挙動同期

**Date**: 2026-07-20 | **Feature**: [spec.md](spec.md)

事実は 2 系統で確認した: (a) 公式ドキュメント(learn.chatgpt.com、2026-07-20 取得)、(b) 手元環境の実地調査(`~/.codex/`、`~/.claude/`、リポジトリ)。確信度は High = 公式記述と実地の両方で確認 / Medium = 片方のみ。

## R0. `/speckit-tasks` 時点で判明した是正 — install.sh は既に部分実装済み(研究更新)

タスク生成に着手する直前、`install.sh`(255 行)を再確認したところ、R1・R2・R3・R6 の一部が**既に実装済み**(013 実装 #46 の一部)だが、(a) 現在の実行環境には未反映、(b) 一部が壊れている、(c) 設計と食い違う箇所がある、ことが判明した。以下は元の R1/R2/R3 の**訂正**である(元記述は撤回せず、差分として残す)。

- **R1 訂正**: `install.sh` 1b は既に「リポジトリルート `AGENTS.md` → `~/.codex/AGENTS.md`」をコピーで展開している(コード自体は存在)。ソースは `.codex/AGENTS.md` **ではなくリポジトリルート `AGENTS.md`**。したがって R1 の決定(ソースを `.codex/AGENTS.md` にする)を実現するには、**`install.sh` 1b のソースパスをリポジトリルート `AGENTS.md` から `.codex/AGENTS.md` に変更する**タスクが必要(新規コード追加ではなく既存コードの 1 行修正)。現在ルート `AGENTS.md` が壊れている(1 行のみ)のは、この誤ったソース位置のまま編集を試みた結果と整合する。
- **R2 訂正**: `install.sh` 1c は既に `~/.agents/skills/<name>` → `~/.claude/skills/<name>`(展開済みコピー)のシンボリックリンクを 9 スキール分生成するコードを持つ(`CUSTOM_SKILLS="adr advisor clarifier coder domain-model minto-builder minto-reviewer minto-rewriter ubiquitous-language"`)。**このリストのうち `advisor`・`domain-model`・`ubiquitous-language` の 3 件は、コミット `33c82eb`(PR #48, `docs: restructure CLAUDE.md and prune rules/hooks`)でリポジトリの `.claude/skills/` から意図的に削除済み**(コミットメッセージ: "unused after the [restructure]")。`install.sh` の `sync_path("skills")` はリポジトリ `.claude/skills/` を `~/.claude/skills/` へ**完全ミラー**するため、次回 `install.sh` 実行時にこの 3 スキルは `~/.claude/skills/` からも削除され、`~/.agents/skills/` のシンボリックリンクは(`CUSTOM_SKILLS` に残ったままだと)壊れる。**修正は `CUSTOM_SKILLS` からこの 3 件を削除**し、リポジトリ `.agents/skills/` の同名の壊れリンク 3 件と合わせて、プロジェクトの既存決定(33c82eb)に一貫させる。スキル内容自体の復元は本フィーチャーのスコープ外(013/33c82eb で既に確定した Claude Code 側の決定であり、014 は Codex 側を追従させるだけ)。
- **R3 訂正**: フックは `hooks.json` ではなく、`install.sh` 1d が `~/.codex/config.toml` に管理マーカー区間(`# >>> my-claude-code managed hooks ... <<<`)を書き込む方式で**既に実装済み**(Python ヒアドキュメントで `[[hooks.PreToolUse]]` 等の TOML ブロックを生成)。対象は既存 3 アダプタのみ(`ADAPTERS` タプルリスト)。**新規実装は「hooks.json を作る」ではなく「`ADAPTERS` リストに 4 件目(`prompt-secret-adapter.sh`, event=`UserPromptSubmit`)を追加する」に変更**。`UserPromptSubmit` は Bash/apply_patch のようなツール限定イベントではないため matcher の要否を実装時に公式仕様・実 Codex セッションで確認する(未確認: Medium)。現在 `~/.codex/config.toml` に該当ブロックが存在しないのは、コードが存在してもこの環境で `install.sh` が(この実装以降)再実行されていないためであり、「フック機構が存在しない」わけではない。

この訂正を踏まえ、R9(install.sh の展開範囲拡張)は「新規関数を足す」ではなく「**既存の 1b/1c/1d を修正 + 1e(rules)・1f(prompts)・1g(Codex MCP)を追加**」に変わる。Project Structure と tasks.md はこの訂正後の姿を反映する。

---

## R1. Codex の AGENTS.md 探索仕様(配置決定の根拠)

**Decision**: 指針プロースのソースはリポジトリの `.codex/AGENTS.md` とし、`~/.codex/AGENTS.md`(グローバルスコープ)へ展開する。リポジトリルートの `AGENTS.md` は「このリポジトリ固有の内容」専用とし、現在の残骸(1 行のみの壊れた状態)は修復する。

**Rationale** (High): 公式仕様([agents-md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)) — 探索は (1) グローバル: `~/.codex/AGENTS.override.md` → `~/.codex/AGENTS.md`(最初の非空 1 ファイルのみ)、(2) プロジェクト: Git ルートから cwd まで各ディレクトリで `AGENTS.override.md` → `AGENTS.md`(各ディレクトリ最大 1 ファイル)、ルート→下位の順に連結、近い方が後勝ち。合計 `project_doc_max_bytes`(既定 32 KiB)で打ち切り。**リポジトリ内の `.codex/AGENTS.md` は探索対象ではない** — 展開されない限り読まれない。これはメンテナ決定(ユーザールート前提)と整合: `.codex/AGENTS.md` は版管理用ソース、実効位置は `~/.codex/AGENTS.md`。

**Alternatives considered**: (a) ルート `AGENTS.md` のみ(013 当初の形) — このリポジトリでしか効かず、ユーザー設定前提に反するため降格。(b) `AGENTS.override.md` の使用 — 通常ファイルを覆い隠す挙動は不要、不採用。

**現状の欠陥**: 作業ツリーのルート `AGENTS.md` は `` `.codex/agents/` `` という 1 行のみ(編集途中の残骸)。このまま残すとグローバル指針と無関係なノイズがプロジェクトスコープとして全セッションに注入される。修復対象。

## R2. スキルのユーザースコープ走査位置

**Decision**: ユーザースコープのスキルは `~/.agents/skills/<name>` → `~/.claude/skills/<name>` へのシンボリックリンクとして展開する。リポジトリの `.agents/skills/` はプロジェクトスコープ用に維持するが、エントリはプロジェクトの `.claude/skills/` に実在するスキルのみに限定し、壊れリンク 3 件(`advisor`、`domain-model`、`ubiquitous-language`)は削除する(これらはユーザースコープ側で提供される)。

**Rationale** (High): 公式仕様([build-skills](https://learn.chatgpt.com/docs/build-skills)) — 走査位置は `$CWD/.agents/skills`、`$REPO_ROOT/.agents/skills`(プロジェクト)、**`$HOME/.agents/skills`(ユーザー)**、`/etc/codex/skills`(システム)。「シンボリックリンクされたスキルフォルダに対応し、走査時にリンク先を追う」と明記。`~/.claude/skills/` には全 24 スキル(手書き 9 + `speckit-*` 15)が存在することを実地確認済み — ユーザースコープでリンクすれば壊れリンクの根因(プロジェクト `.claude/skills/` からの剪定)に影響されない。同名スキルが複数スコープにあるとマージされず両方表示されるため、プロジェクトスコープとユーザースコープの重複は避ける(プロジェクト側は最小化)。

**Alternatives considered**: (a) リポジトリ `.agents/skills/` の壊れリンクを `~/.claude/skills/` 絶対パスに付け替え — リポジトリに他ユーザー環境で壊れる絶対パスを版管理することになり不採用。(b) スキル実体の複製 — 単一ソース原則(FR-007)違反で不採用。

**現状の欠陥**: `~/.agents/` は存在しない(未展開)。リポジトリ `.agents/skills/` に壊れリンク 3 件。

## R3. ガードレールフックの配線(最重要ギャップ)

**Decision**: `~/.codex/hooks.json`(ユーザースコープ)で 4 アダプタ(既存 3 + R4 の新規 1)を登録する。ソースはリポジトリ `.codex/hooks.json` + `.codex/hooks/*.sh` とし、install.sh が `~/.codex/` へ展開する。あわせて install.sh に `scripts/guardrails/` → `~/.claude/scripts/guardrails/` の展開を追加する(アダプタが参照する共有スクリプトの実効位置)。

**Rationale** (High): 公式仕様([hooks](https://learn.chatgpt.com/docs/hooks)) — フックは `~/.codex/hooks.json` または `~/.codex/config.toml`(ユーザー)、`<repo>/.codex/hooks.json` または `.codex/config.toml`(プロジェクト、`.codex/` レイヤーが信頼された場合のみ)から読み込まれ、全レイヤーのマッチするフックが実行される。イベントは `PreToolUse`/`PostToolUse`/`UserPromptSubmit`/`SessionStart` 等、matcher は `Bash`、`apply_patch` または `Edit|Write` 等。実地調査: **`~/.codex/hooks.json`・`~/.codex/hooks/`・リポジトリ `.codex/hooks.json`・`.codex/config.toml` はいずれも存在しない** — 013 で作られた 3 アダプタは現在どこにも配線されておらず、一度も実行されない。さらにアダプタが第 2 候補として参照する `~/.claude/scripts/guardrails/` も未展開。ユーザースコープを主とするのは、プロジェクトスコープが信頼操作(`/hooks` でのレビュー)を要し、かつ「ユーザー設定」前提に沿うため。

**Alternatives considered**: (a) プロジェクト `.codex/hooks.json` のみ — このリポジトリ以外で効かず前提に反する。(b) `config.toml` 内へのフック定義 — MCP 等と混在し diff が追いにくい。hooks.json 分離を採用(同一レイヤーで両形式併存は警告が出るため hooks.json に一本化)。

**検証課題**: アダプタ自身のヘッダに「PreToolUse 応答スキーマは二次資料ベースで未検証、`ask` は `deny` に丸めている(fail closed)」と明記されている。配線後、実 Codex セッションで応答スキーマ(`hookSpecificOutput.permissionDecision`、exit 2 + stderr での拒否、`ask` 三値の可否)を検証し、可能なら `ask` を復元する。

**実装時再確認 (2026-07-20)**: 最新の公式 Codex manual の Hooks セクションで、`UserPromptSubmit` は matcher をサポートせず、設定された matcher は無視されることを確認した。このため `install.sh` は同イベントだけ matcher 行を生成しない。拒否応答は同セクションの共通出力契約に従い `{ "continue": false, "stopReason": "..." }` とした。実セッションでのフック trust・発火確認は T033 に残す。

**実 Codex CLI 検証 (2026-07-20, v0.145.0-alpha.18)**: `/Applications/ChatGPT.app/Contents/Resources/codex exec --ephemeral` と一時的な config override を使い、ユーザー設定を上書きせず検証した。`UserPromptSubmit` はダミー GitHub token 形状を `Stopped`、安全な prompt を `Completed` と判定した。PreToolUse の旧 `hookSpecificOutput` + `continue` JSON は `PreToolUse Failed` となり tool が続行したため、アダプタを現行 command-hook 契約(exit 0 + 出力なし=allow、exit 2 + stderr=block)へ修正した。修正後は安全な `/bin/echo` が `Completed`、`git push --force` が実行前に `Blocked` となった。したがって ask は JSON 三値へ復元せず exit 2 に丸める fail-closed を維持する。`codex execpolicy check` でも検証/lint/git 読取は allow、`git add`/`git pull` は prompt と確認した。

**実ホーム T033 検証 (2026-07-20, 11:31–11:41 JST, v0.145.0-alpha.18)**: 明示承認後に `install.sh` を実ホームへ展開し、`codex mcp list` で `.mcp.json` の 6 サーバが一意に列挙されることを確認した。初回は非管理 `[mcp_servers."strands-agents"]` と管理定義が重複して Codex が設定を拒否したため、R9 の補正どおり同名非管理定義を保持して管理生成を省略する実装と SYNC-04 unique 検査を追加した。修正後の実 Codex セッションはグローバル AGENTS 指針に従って AWS documentation MCP と `microsoft-learn` を実際に呼び、Microsoft Learn クエリに成功した。`adr`、`clarifier`、`coder`、Minto 3 スキルも発見済み一覧から確認した。

非管理コマンドフックは公式仕様どおり現在の定義ハッシュを TUI `/hooks` で信頼するまでスキップされた。信頼前はダミー secret prompt、`git push --force`、一時 `.env` 読取が通過し、信頼後は secret prompt がモデル呼出前に停止、force push と `.env` 読取が PreToolUse で block された。実機に `shellcheck` がないため一時 PATH の無害なスタブで allow rule を確認し、確認なしで `shellcheck --version` が実行された。`/prompts:verify-config` は展開先 prompt を読み、Claude 側検証手順、Codex sync、prompt-secret suite を実行した。PreToolUse の ask は三値 JSON に戻さず、exit 2 への fail-closed 丸めを維持する。インストーラーと Quickstart には `/hooks` 信頼手順を必須 post-install step として追加した。

**T032 最終全スイート (2026-07-20, 13:07–13:12 JST)**: Claude CLI の Pro 利用枠リセット後、認証状態を通常ホスト環境で再確認し、`tests/run-*.sh` 全件を一続きで実行して終了コード 0 を確認した。内訳は Codex drift 8/8、Codex sync 15/15、destructive guard 23/23、live documentation 5/5、post-edit guard 3/3、pre-edit guard 10/10、prompt-secret guard 15/15、skill routing 6/6、Spec Kit update 6/6、type-safety coder 4/4。`shfmt` 未導入のため post-edit suite 内の shfmt 依存 2 assertion はスイート仕様どおり skip され、残る assertion と全スイートは PASS した。最初の再実行で短い文書作成要求が `clarifier`、次の再実行でコード＋README依頼が `coder` 単独へ揺れたため、複合依頼→具体単一カテゴリ→一般 ambiguity の優先順位を `.claude/rules/skill-routing.md` と評価queryへ明示し、6/6 PASS に収束させた。

実ホームへの `install.sh` 展開は、既存 `~/.claude`/`~/.codex`/`~/.agents` を置換するため安全審査で拒否された。このため、グローバル AGENTS 読込、実 `~/.agents/skills` 発見、6 MCP の live 接続、`/prompts:verify-config` の実 UI 起動は未確認。代わりに一時 HOME への完全 install と全 SYNC baseline、5 種の drift 破壊テストを自動検証済み。実ホーム項目はメンテナの明示承認後に再実施する。

## R4. UserPromptSubmit イベントの存在(012 判断の前提変化)

**Decision**: `.claude/hooks/user-prompt-submit.sh`(プロンプト内秘密情報のハードブロック)を、共有スクリプト + Codex `UserPromptSubmit` フックアダプタとして移植する。012 の Q5 判断(「Codex は代替なし → プロース注意書きのみ」)は、当時なかった新事実(公式 hooks ドキュメントに `UserPromptSubmit` イベントが明記)により、確立済みの「共有スクリプト + 薄いアダプタ」パターンの適用対象に昇格する。

**Rationale** (High): 公式 hooks ドキュメントがイベント一覧に `UserPromptSubmit` を明記。013 が同種の昇格(Q9/Q10/Q7 — pre-edit/post-edit の hooks 対応発見)を行った前例に倣う。判定ロジック(AWS キー、GitHub/Slack トークン、Google API キー、秘密鍵ブロックの検知)は既に `user-prompt-submit.sh` に存在し、`scripts/guardrails/` へ抽出して両ツールの薄いラッパから呼ぶ。spec FR-011 の「対応機構なし」例示から本項を除外する修正が必要(spec 修正は本 research と同時に実施)。

**Alternatives considered**: 012 判断の維持(プロースのみ) — 実効性で劣り、「同様に使える」というユーザー目標に反する。新事実がある以上、記録付きで昇格する方が 012 の趣旨(実効性ベースの判断)に忠実。

## R5. 権限(allow / ask / deny)の Codex 側再現

**Decision**: 二層で再現する。(1) **Rules**(`prefix_rule`、リポジトリソース `.codex/rules/guardrails.rules` → `~/.codex/rules/guardrails.rules` へ展開): `settings.json` の allow リスト相当(検証スイート `tests/run-*.sh`、`scripts/check-mcp-consistency.sh`、`shellcheck`/`shfmt`/`jq`/`yamllint`、git 読み取り系 + `commit`)を `decision="allow"`、git 書き込み系(`add`/`checkout`/`branch`/`stash`/`pull`)を `decision="prompt"` で宣言。(2) **フック**(R3 の destructive-command アダプタ): deny 相当(credential パス読み書き、破壊的コマンド、非 HTTPS、グローバルインストール)は既存の共有スクリプトが担う。Codex が Rules とフックの両方を評価する場合、より制限的な側が勝つ構成とし、挙動差分(既知の丸め)は対応表に記録する。

**Rationale** (High): 公式仕様([rules](https://learn.chatgpt.com/docs/agent-configuration/rules)) — `.rules`(Starlark)は `~/.codex/rules/` と信頼済みプロジェクトの `<repo>/.codex/rules/` から読み込まれ、`allow`(既定)/`prompt`/`forbidden` の三値、複数マッチ時は最も制限的な決定が適用。対象はシェルコマンドのみで、`&&`/`||`/`;`/`|` で安全に分割可能なスクリプトは個別評価される。プレフィクスマッチは `pre-bash.sh` の正規表現(文中の `rm -rf` 検出等)より表現力が低い — deny 側を Rules に寄せず共有スクリプトに残すのはこのため(012 Q6 の決定とも整合)。`Read` ツールの credential-path deny(`settings.json` の `Read` deny 相当)はシェル限定の Rules では表現不能 — 共有スクリプトが `cat` 等のシェル経由読み取りを塞ぎ、残差(Codex ネイティブのファイル読み取りツール)は対応表に制約として記録する。

**実地確認**: `~/.codex/rules/default.rules` が既存 — Codex がセッション中の承認から自動蓄積するユーザー所有ファイル。**上書き・編集しない**。リポジトリ管理のルールは別ファイル名(`guardrails.rules`)で並置する(rules/ フォルダは全ファイル走査されるため共存可能)。

**Alternatives considered**: (a) 全 permissions を Rules 化 — 表現力不足(正規表現・ファイルツール非対応)で不採用。(b) 全部フック任せ — allow リスト(確認なし実行)はフックでは表現できない(フックは拒否/続行のみで「事前承認」を宣言できない)ため Rules が適所。

## R6. MCP 接続カタログ

**Decision**: install.sh に `~/.codex/config.toml` への `[mcp_servers.<name>]` 冪等 upsert を追加し、`.mcp.json` の 6 サーバと同一カタログ(名称も `.mcp.json` に揃える)を登録する。既存の別名重複(`AWSknowledge-mcp-server` ≈ `aws-knowledge`、`aws-docs` ≈ `aws-documentation`、`bedrock-agentcore-mcp-server` ≈ `bedrock-agentcore`)は正名へ統合を提案し、`.mcp.json` にない私物サーバ(`aws-api`、`node_repl`、`computer-use` 等)には触れない。同期健全性チェック(R8)が `.mcp.json` のサーバ集合 ⊆ `~/.codex/config.toml` の集合を検証する。

**Rationale** (High): 公式仕様([extend/mcp](https://learn.chatgpt.com/codex/extend/mcp)) — stdio は `command`/`args`/`env`/`env_vars`、HTTP は `url`/`bearer_token_env_var`/`auth`/`http_headers`。`~/.codex/config.toml` と信頼済みプロジェクトの `.codex/config.toml` の両方が読まれる。認証は環境変数参照(`bearer_token_env_var`)か `codex mcp login` — 平文キーを書かない要件(FR-006)を満たせる。実地調査: 現在の `~/.codex/config.toml` には 6 サーバ中 4 相当が別名で存在し、`google-developer-knowledge` と `microsoft-learn` が欠落 — カタログドリフトの実例。install.sh には既に Claude 側 MCP の upsert 関数(`upsert_user_mcp`)があり、同型の Codex 版を追加する。

**Alternatives considered**: (a) プロジェクト `.codex/config.toml` に接続を版管理 — 信頼操作が必要な上、`env` にキーを書けない制約は同じで、ユーザー設定前提にも反する。(b) `.mcp.json` からの完全自動生成 — 形式非互換(JSON→TOML、フィールド名差)の変換層を持つ価値はあるが、6 サーバ規模では upsert + 集合チェックで十分。過剰工学として不採用(将来サーバ数が増えたら再検討)。

## R7. カスタムプロンプト(`/verify-config` 相当)

**Decision**: リポジトリソース `.codex/prompts/verify-config.md` を新設し、`~/.codex/prompts/verify-config.md` へ展開する。内容は `.claude/commands/verify-config.md` と同じ検証手順を指す薄いプロンプトとし、検証ロジック本体(スクリプト群・スイート)は共有のまま二重実装しない。両ファイルの実質的同一性は R8 のチェックで担保する。

**Rationale** (Medium): 公式 customization overview はカスタムプロンプトの配置を明記していないが、実地調査で `~/.codex/prompts/*.md` に Spec Kit のプロンプト(`speckit.*.md`)が配置され、スラッシュコマンドとして機能している(Spec Kit の `speckit-expand-update.sh` フローが書き込んでいる実績)。この実効位置に合わせる。フロントマター形式が Claude Code コマンドと異なる可能性があるためシンボリックリンクではなくソース分離 + ドリフトチェックとする。

**Alternatives considered**: シンボリックリンク(単一ファイル共有) — 形式差(フロントマター、引数プレースホルダ)が未確認のため初版では見送り。plan 実装中に形式互換が確認できればリンクに昇格してよい。

## R8. 同期健全性チェック(ドリフト検知)

**Decision**: 新スイート `tests/run-codex-sync.sh` を追加し、既存スイート群と同じ規約(自己完結 bash、exit 非 0 で失敗箇所を列挙)で以下を検証する: (1) `.agents/skills/`(リポジトリ)と `~/.agents/skills/`(展開済みの場合)の壊れシンボリックリンク 0 件、(2) `.codex/AGENTS.md` のサイズ ≤ 32 KiB(閾値近接で警告)、(3) `.mcp.json` サーバ集合 ⊆ `~/.codex/config.toml`(未展開環境ではスキップ+警告)、(4) `.codex/hooks/` の 4 アダプタと `install.sh` の ADAPTERS 宣言の一致、(5) 展開済みコピー(`~/.codex/AGENTS.md`、hooks、rules、prompts)とリポジトリソースの一致(diff)、(6) `.codex/prompts/verify-config.md` と `.claude/commands/verify-config.md` の検証手順の対応。

**Rationale** (High): 壊れリンク 3 件・未配線フック・MCP カタログ欠落という 3 種のドリフトが現に発生している(実地調査)。リポジトリの既存文化(`tests/run-*.sh` 挙動スイート、`scripts/check-mcp-consistency.sh`)に同型で載せるのが最小驚き。`~` 依存のチェックは未展開環境で「失敗」ではなく「スキップ+警告」とし、CI(リポジトリのみ)とローカル(展開済み)の両方で意味を持たせる。

**Alternatives considered**: 完全自動同期(展開スクリプトの常時再実行) — 検知なしの上書きはユーザー所有ファイル(`default.rules` 等)を壊すリスクがあり、検知→明示的 install.sh 再実行のフローを採用。

## R9. install.sh の展開範囲拡張(R0 訂正後)

**Decision**: `install.sh` の**既存ステップを修正**する: 1b のソースを `.codex/AGENTS.md` に変更、1c の `CUSTOM_SKILLS` から `advisor`/`domain-model`/`ubiquitous-language` を削除、1d の `ADAPTERS` に `prompt-secret-adapter.sh`(event=`UserPromptSubmit`)を追加。加えて**新規ステップ**を足す: 1e(`.codex/rules/guardrails.rules` → `~/.codex/rules/guardrails.rules`、`default.rules` 等の既存ファイルには触れない)、1f(`.codex/prompts/verify-config.md` → `~/.codex/prompts/verify-config.md`)、1g(`.mcp.json` の 6 サーバを `~/.codex/config.toml` の `[mcp_servers.*]` へ、1d と同じ管理マーカー区間パターンで upsert)。既存の `GUARDRAILS_DST`(`~/.claude/scripts/guardrails/`)展開ステップ(1a)は既に実装済みのため変更不要 — 013 アダプタが前提とする実体は既にある。

**Rationale** (High, R0 で実地確認済み): install.sh はこのリポジトリに版管理されており、`.claude/` → `~/.claude/` ミラー・MCP upsert(Claude 側)・Codex 側 AGENTS.md/skills/hooks 展開の骨格まで**既に実装済み**。「作る」のではなく「直す・足す」が正確な作業内容。同じ入口(1 スクリプト)に統一する方針は既存設計を踏襲。

**Alternatives considered**: 別スクリプト(install-codex.sh) — 入口が割れて実行忘れの温床になるため不採用。TOML 編集を `codex` CLI サブコマンド(存在すれば `codex mcp add` 等)に委ねる案 — 実装時に確認し、あれば優先(1d が既に生の TOML 編集で実装されているため、一貫性を優先するなら 1g も同パターンでよい)。

**実ホーム検証での補正 (2026-07-20)**: 非管理区間に引用形式の `[mcp_servers."strands-agents"]` が既存する環境で、初版インストーラーが管理区間へ同名の非引用テーブルを追加し、Codex が duplicate key で設定全体を拒否した。非管理設定を削除・上書きしない原則を維持するため、同名の非管理サーバまたはそのサブテーブルを検出した場合は、そのサーバだけ管理ブロックへの生成を省略する。SYNC-04 は引用・非引用を同一名として数え、各カタログサーバのトップレベル定義がちょうど 1 件であることも検証する。

## R10. Claude Code 側の事実(再確認)

**Decision**: Claude Code 側は変更最小とする — `CLAUDE.md`/`.claude/rules/`/`settings.json` の現行構成は維持し、user-prompt-submit の共有スクリプト抽出(R4)と `verify-config` の参照整理以外は触れない。

**Rationale** (High): spec 013 が公式ドキュメント(code.claude.com/docs: features-overview、claude-directory、mcp-quickstart)から確認済み: Claude Code は `AGENTS.md` を読まず `CLAUDE.md` + `.claude/rules/` を読む、`.mcp.json` がプロジェクト MCP 接続、`@path` インポート対応。スキル構造(`<name>/SKILL.md`)は Codex と同一。SC-007(Claude 側無劣化)を守るには既存フック(`pre-bash.sh` 等)のラッパ構造を変えず、共有スクリプトの抽出だけ増やすのが最小。

## 解決済みの Technical Context 未知数

| 未知数 | 解 | 根拠 |
|---|---|---|
| グローバル AGENTS.md の実効位置 | `~/.codex/AGENTS.md` | R1 (High) |
| ユーザースコープのスキル走査位置 | `$HOME/.agents/skills`(シンボリックリンク追従) | R2 (High) |
| フック登録の場所・形式 | `~/.codex/config.toml` の managed inline `[hooks]` 区間 | R0/R3 訂正 (High) |
| UserPromptSubmit 相当の有無 | あり — アダプタで移植 | R4 (High) |
| allow リストの Codex 表現 | Rules `prefix_rule`(`allow`/`prompt`) | R5 (High) |
| MCP 接続の Codex 形式 | `~/.codex/config.toml` `[mcp_servers.*]` | R6 (High) |
| カスタムプロンプト位置 | `~/.codex/prompts/*.md` | R7 (Medium — 実地実績ベース) |
| PreToolUse 応答スキーマの三値可否 | 未検証 — 実装中に実セッションで確認(fail closed で安全側) | R3 検証課題 |
