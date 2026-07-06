# Claude Code 個人設定を作るときのTips

このリポジトリ(`.claude/` 一式)を10回近い改善サイクルで育ててきた過程から、他のユーザーが自分の設定を作る・育てるときに転用できる知見をまとめる。構成(ファイル・フックの組み方)と指示内容(文章の書き方)の2軸、および改善の進め方の3部構成。個々のファイルの役割そのものは [README.md](../README.md) を参照— ここでは「なぜそう作ったか」「どう改善してきたか」を扱う。

## 1. 構成面のTips

### 常時ロードとオンデマンドを分離する

`CLAUDE.md` に全部書かず、3層に分ける。

| 層 | 置き場所 | ロードタイミング |
|---|---|---|
| 常時コンテキスト | `CLAUDE.md` + `@import` される `rules/*.md` | 毎セッション |
| オンデマンド playbook | `skills/*/SKILL.md` | ルーティング条件に合致したとき |
| 自動化 | `hooks/*.sh` | イベント発火時(PreToolUse等) |

毎回読まれる層が太ると、無関係なタスクでもトークンを消費し続ける。判断基準や条件分岐が多い内容(TDDの手順、DDDの用語集など)はskillに逃がし、rulesには「いつそのskillを読むか」というルーティング条件だけを残す。

### 各ファイルを一つの関心事に絞り、行数の目安を持つ

このリポジトリでは `rules/*.md` を200行以内に収める方針を明文化している(`specs/010-claude-config-optimization/spec.md` FR-011)。実測は [tools.md](../.claude/rules/tools.md) の127行が最大で、他は20〜90行台([mcp.md](../.claude/rules/mcp.md) 28行、[git-workflow.md](../.claude/rules/git-workflow.md) 30行など)。1ファイル1関心事にすると、後述の「重複ゼロ」原則も自然に守りやすくなる。

### `CLAUDE.md` は薄い索引にする

[`.claude/CLAUDE.md`](../.claude/CLAUDE.md) 自体は88行で、原則・応答スタイル・skillルーティング表・`@import`のリストのみを持つ。詳細ロジックは全て `rules/` 側に委譲している。ルートの `CLAUDE.md` はさらに薄く、`@.claude/CLAUDE.md` の再エクスポート1行のみ。プロジェクト固有の詳細を積む場所と、恒久的な行動規範を積む場所を分けておくと、プロジェクトが変わっても後者を使い回せる。

### `settings.json` の permission は allow/ask/deny の3段で明示する

読み取り系(`git status`/`diff`/`log`)は `allow`、書き込み系(`git commit`/`checkout`/`branch`)は `ask`、資格情報パス(`.env`, `.ssh/`, `*.pem` 等)は `deny` に固定する。曖昧な単一リストにせず、3段に分けることで「確認なしに進めてよい操作」と「必ず人に聞く操作」の境界をツール側にも強制させられる([settings.json](../.claude/settings.json)、[permissions.md](../.claude/rules/permissions.md))。

### hookは「exit codeで許可/拒否」「JSONで ask に格上げ」を使い分ける

[`pre-bash.sh`](../.claude/hooks/pre-bash.sh) は破壊的コマンドを検出したら `exit 2` で完全ブロックする一方、`rm -rf`(root/home以外)や `sudo` のようにケースバイケースの判断が要るものは、`permissionDecision: "ask"` を含むJSONを標準出力してユーザー確認に格上げする。「常に禁止」と「状況次第で確認」を同じスクリプト内で書き分けられるのが分かると、hookの表現力を過小評価せずに済む。

### user-scope と project-scope の同期経路を1本化する

`.claude/` 一式を丸ごと `~/.claude/` にコピーする [`install.sh`](../install.sh) を用意し、個人設定をどのプロジェクトでも使い回せるようにしている。プロジェクト固有の上書きは各リポジトリの `.claude/settings.json` 側で行い、優先順位(`managed > local > project > user`)に委ねる。2箇所に同じルールを別々に書かない。

### 設定自体の整合性をスクリプトで検証する

MCPサーバーの名前・URL・バージョンが `.mcp.json` / `install.sh` / `settings.json` / `mcp.md` の4箇所に散りがちな問題を、[`scripts/check-mcp-consistency.sh`](../scripts/check-mcp-consistency.sh) で機械チェックしている。「指示文書同士が矛盾していないか」を目視レビューだけに頼らない。

### プロンプトの振る舞いを実行可能テストにする

`tests/skill-routing/`・`tests/live-documentation/` 配下にシナリオ(入力プロンプトと期待される挙動)をMarkdownで並べ、`tests/run-*.sh` が実際に `claude` CLIをヘッドレス実行して検証する。コードのTDDと同じ発想を、指示文(プロンプト)そのものに適用している。ルーティングやガードを変更したら、このスイートを流してから次の変更に進む。

### 他ツール向けシステムプロンプトは「変換元を1つに保つ」

`.claude/rules/*.md` を正とし、ChatGPT/Claude.ai(Web版)向けの [`chatgpt-system-prompt.md`](../chatgpt-system-prompt.md) / [`claude-ai-system-prompt.md`](../claude-ai-system-prompt.md) はそこから手動で移植・同期する運用にしている。ツールごとに書き味が異なる(ChatGPTはdual-field指示形式など)ため完全自動生成はせず、直近のコミット(`docs(prompts): sync portable system prompts with .claude rules`)のように「ルール変更→移植」をワンセットの作業として扱う。

## 2. 指示内容(文章)面のTips

### 「短くする」より「誤解なく実行できる」を優先する

10番目の改善サイクル([`specs/010-claude-config-optimization/spec.md`](../specs/010-claude-config-optimization/spec.md))で明文化した転換点: 当初は「常時コンテキストを20%以上削減」という圧縮目標を掲げていたが、削るほど曖昧な指示が残ることに気づき、目標を「重複ゼロ + 冗長さの除去」に変更した。モデルが正しく実行するために必要な具体例・境界条件はむしろ書き足す(comprehension supplement)。行数削減それ自体を成功指標にしない。

### 全ルール・全skillの冒頭に「これは何のためか」を1文で書く

[`research.md`](../specs/010-claude-config-optimization/research.md) R4: `rules/*.md` は各ファイル冒頭に "Purpose: ... / Applies when: ..." 相当の1文を必ず置く(例: [live-documentation.md](../.claude/rules/live-documentation.md) 冒頭)。skillはYAML frontmatterの`description`とは別に、本文冒頭にも平文の目的文を置く。ルーティング用メタデータと、人間・モデルが読んで理解するための文章は役割が違うため、両方要る。

### 同じルールを2箇所に書かない。1箇所に書いて相互参照する

`clarifier`(要件の曖昧さを埋める)・`advisor`(選択肢を比較して推奨する)・`live-documentation`(ドキュメント鮮度)は、それぞれ唯一の正本を持ち、他のファイルからは `rules/clarifier.md` のように参照するだけで内容を繰り返さない。実際、以前は clarify判断の基準が `CLAUDE.md` / `clarifier.md` / `clarifier` skill の3箇所に別々の言い回しで存在しており、これを一本化したのが最大の重複除去だった。

### 閾値は「テスト可能な言葉」で書く

「非自明なタスクか」「曖昧な依頼か」のような判定を、感覚的な形容詞のままにしない。例えば skill-routing.md では「スラッシュコマンドとパスを除いた残りのテキストが32文字以下」という具体的な閾値でclarifierの発火条件を書いている。CLAUDE.mdの「Pre-execution discipline」でも「非自明=複数ファイルに跨る/観測可能な挙動を変える/後戻りしにくい、自明=単一ファイル・可逆・1ステップ以下」と対で定義している。「うまく」「適切に」で終わらせない。

### 規範的な指示には実在する権威ある基準を紐づける(ただし機能する場合のみ)

「ちゃんとバリデーションする」ではなく「OWASP ASVSに沿って境界でバリデーションする」のように、実在し正確に帰属できる基準(OWASP Top 10/ASVS、ISO/IEC/IEEE 29148、INVEST、Gherkin Given/When/Then、MECE、SCQA、Tufteのdata-ink、Cleveland–McGillの知覚ランキング等)を根拠として添える。ただし2条件を満たすときだけ: (a) 本物で誤帰属でないこと、(b) 名前を出すことで解釈が実際に狭まること。装飾目的で名前を出すだけなら削る、という基準([research.md](../specs/010-claude-config-optimization/research.md) R9)。

### フレームワーク名は内部推論用、ユーザー向け出力には出さない

`CLAUDE.md` は「BLUF/MECE/SCQA/FURPS+/INVESTは内部推論でのみ使い、ユーザー向けの回答や成果物では名前を出さず暗黙に適用する」と明記している。フレームワークは思考の型を与えるためのものであり、それを名指しすることが読者への価値にはならない、という切り分け。

### 設定を削るときは「振る舞いの棚卸し」を先に作る

大がかりなリファクタ(spec 010)では、着手前に permission の allow/ask/deny、hookのガード条件、skillルーティングの発火条件、skillの義務(TDD必須など)を全て列挙した「behavior inventory」を作り、変更後に1行ずつ再確認した。「短くなった」ことと「安全装置が生きている」ことは別の検証軸であり、目視のdiffレビューだけでは片方しか見えない。

## 3. これまでの改善の歩み(spec 001 → 010)

| # | テーマ | 要点 |
|---|---|---|
| 001 | skill自動ルーティング | プロンプト内容からskillを自動選択する仕組みを導入 |
| 002 | speckit skill同期 | Spec Kit本体のアップデートにskillを追従させる仕組み |
| 003 | ubiquitous-language | ドメイン用語を会話から拾い`docs/`に蓄積するskill |
| 004–005 | domain-model / DDD skill | 構造(集約・エンティティ等)を蓄積するskillを追加、英語化+初心者向け言い回しへ改稿 |
| 006 | CLAUDE.md/MCP/effort/TUI | MCPカタログ整備、モデルeffort・TUI設定を追加 |
| 007→(撤回) | Codex reviewスキル | 一度追加したが後に撤去(`chore: remove Codex review skill and hooks`) — 使われない/合わない機能は残さず消す判断も改善の一部 |
| 008 | clarify pretrigger | 曖昧な依頼を`/speckit-specify`前に検知するヒューリスティックを追加 |
| 009 | Live Documentation enforcement | ドキュメント鮮度を守る5原則をルール化 |
| 010 | 設定全体の最適化 | 「圧縮」から「理解可能性+権威付け」へKPIを転換した最大の改訂。Spec Kitの spec→plan→tasks を自分自身の設定変更にも適用(ドッグフーディング) |

補足として、`docs/accuracy-instruction` や `feature/sync-ai-system-prompt` のように、Accuracy優先順位の明文化やシステムプロンプト移植といった小さな改善が個別ブランチ→PRマージのサイクルで継続的に積み重ねられている。

## 4. 今後どう改善していくか

- **重複ゼロを回帰させない**: rulesやskillが増えるたびに、同じ判断基準を違う言葉で書いていないか確認する。新設したくなったら、まず既存ファイルへの追記・相互参照で足りないか検討する。
- **behavior inventoryを重い変更のたびに作る**: permission/hook/routing/skill義務を一覧化してから編集し、編集後に再チェックする習慣を「大きな変更」の定義に組み込む。
- **プロンプトの振る舞いテストを増やす**: `tests/run-*.sh` パターンを新しいルール・skillにも広げ、レビューを人手のみに頼らない。
- **行数の目安を継続的に測る**: `rules/*.md` が200行を超えそうになったら、関心事の分割か既存内容への統合を検討するタイミングとする。
- **権威付けは追加のたびに真偽を検証する**: 新しい基準名を書き足すときは「本物か」「解釈を実際に狭めるか」の2条件を毎回チェックし、装飾的な引用を混入させない。
- **不要になった機能は撤去する**: 007の Codex review skill撤去のように、使われなくなった/合わなくなった仕組みは維持コストをかけて残さず消す。
