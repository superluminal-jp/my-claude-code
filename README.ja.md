# my-claude-code

Claude Code の公式仕様・ベストプラクティス（https://code.claude.com/docs/）に
沿った、再利用可能な **ユーザーレベル設定** です。

`install.sh` は `harness/` のうちリポジトリが管理する設定、rules、skills、agents、memory を
`~/.claude/` に同期し、管理対象外のユーザーファイルは保持します。

配布元は、このリポジトリ自身の `.claude/` ではなく `harness/` にあります。
サンドボックスの中の Bash のコマンドは `.claude/` の下に書き込めず、そこに置いたファイルは
このリポジトリのプロジェクト設定としても読み込まれ、二重に入るためです。この構成にした再設計は
[`docs/harness-zero-base.md`](docs/harness-zero-base.md)（日本語）に記録しています。

英語版: [README.md](README.md)

自分の設定を作る場合は、常時ロードの各指示が通すべき判断基準と、このリポジトリが
意図的に置いていないものを [`docs/claude-config-design.md`](docs/claude-config-design.md)
にまとめています。

## このリポジトリで提供するもの

- **`harness/CLAUDE.md`**: 常時メモリ。1つの達成目標と、その3つのライフサイクル分岐
  （定義・実行・引き渡し）、独立に一致するすべての能力を適用する汎用マルチマッチ
  アルゴリズム、手順と検証を変更に合わせて重くする定め（局所的で戻せる変更は、失敗する検査と
  通る実行を要る。インターフェース・データの流れ・複数のモジュールにかかる変更は、受け入れ条件ごとの
  証拠と独立したレビューも要る。認証・秘密・個人データ・データ移行・権限・公開・戻しにくい
  変更は、人の承認も要る）、そして委任の方針を持つ。委任の方針では、Claude は利用者に求められるのを
  待たずに、次の3つのいずれかに当たるときサブエージェントに委任する: 出力が長く結果だけが要る、
  互いに独立で並行できる、書いた本人から独立した読み手が要る。委任には、その種類の作業のために
  定義されたサブエージェントの型を使い（モデル・effort・道具はその定義が固定する）、同じファイルを
  2つのサブエージェントに書かせない。それ以外は、サブエージェントが空の文脈から始まるため、自分で行う。
  判断、設計、コードレビュー、作業が完了したかの判定はメインの会話のモデルに残す。
  AI-DLC のワークフローが動いている間（プロジェクトにそのフックがあり、記録が `aidlc/` に
  ある）は、次に進むステージと承認ゲートを開く時点を、そのワークフローのエンジンが決める。
  この文書は各ステージの中の作業に適用し、Claude は人に代わってゲートを承認しない。
  ワークフローの外の作業には、この文書がそのまま適用される（後述「AI-DLC Workflows v2」参照）。
  `harness/CLAUDE.md` はルール・スキル・サーバー・モデルの名前を一切含まない — 設計根拠は
  [`docs/claude-config-design.md`](docs/claude-config-design.md) にあります
- **`harness/settings.json`**: Claude Code のユーザーレベル設定。メインの会話のモデル
  （`opus`）と、`effortLevel` で `xhigh`(設定ファイルが受け付ける最も高い段階)に固定した
  その推論の effort（`claude-opus-5-5` については `modelSettings` にも同じ段階を置く。理由は
  [`docs/harness-zero-base.md`](docs/harness-zero-base.md) に記録）、資格情報の読み取りの拒否、Bash の
  すべてのコマンドにかける OS のサンドボックス（日常作業に要る出口だけを開ける）、3つの
  `SessionStart` フック、Claude が `git commit` を実行する前に宣言された文書の木の誤りを伝える
  `PreToolUse` フック、許可する2つの MCP サーバーと、直接止めるサーバーを持つ（後述「サンドボックスとセッション開始のフック」
  「MCP サーバー」参照）
- **`harness/rules/`**: 常時読み込まれる共通ルール。Claude の判断を変える内容だけを置き、
  各ファイルが apex の3分岐のうち正確に1つだけを支える（要件確実性の確認トリガー、
  推論の完全性（4つの推論セルフチェック: 依存と並行・条件と分岐・反復・推論）、権限と安全性
  （強制される deny は `settings.json`）、および読み手本位の構造（Pyramid Principle セルフチェック、結論先行で並べる論文の構成（要旨・前提・方法・結果・考察・結論）、番号付きの主張の見出しと太字の論点による構造の可視化、初学者向けの前提と平易な定義（ユーザー自身の発言が示す場合を除き、読み手はその主題に不慣れだと想定する）、会話・コード・文書を見ていない読み手を想定し、多義語や指示語が何を指すかを明示すること、用語はその分野で使われる形で書き訳語を作らないこと、比喩・類推による説明の禁止））。他のルール・スキル・設定パスへの言及は持たない。
  各ファイルが何を意図的に置いていないかは [`docs/claude-config-design.md`](docs/claude-config-design.md) に記録しています
- **`harness/agents/`**: 委任する作業の種類ごとに1つ、計5つのサブエージェントの定義。各定義が
  モデル・推論の effort・使える道具を固定し、`harness/CLAUDE.md` の委任の方針はそれを前提にする:
  - `read-only-reviewer`（`sonnet`、`xhigh`）— 書いた本人の推論から始めてはならないレビュー（要件への
    反証、変更の証拠のレビューなど）のための、独立した読み手。書いた本人から独立した読み手が要るときに
    起動する。レビューの手順でこれを起動していた2つのスキルは退役し
    （[ADR-0029](docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md)）、
    定義は汎用の読み手として残している。道具は Read・Grep・Glob だけで、CLAUDE.md を読み込まずに
    始まる（読んだファイルのディレクトリの CLAUDE.md と、MCP サーバーの説明文は、起動の後に入る）。
    渡されたファイルを読めないときは、残りから判断せず `NOT REVIEWED: <パス>: <理由>` と答える
    （[spec 070](specs/070-review-integrity/problem.md)）
  - `check-runner`（`haiku`、`low`）— 出力の長い確認（テスト、ビルド、リンタ、型検査）を実行し、
    各コマンド・終了コード・失敗した出力の原文を報告する。道具は Bash・Read・Grep・Glob で、
    CLAUDE.md を読み込まずに始まり、ファイルを変えず、判断もしない
  - `file-searcher`（`haiku`、`medium`）— コードベースや文書の集まりを読み取り専用で検索し、
    `パス:行` と短い抜粋を返す。道具は Read・Grep・Glob で、CLAUDE.md を読み込まずに始まる
  - `task-worker`（`sonnet`、`xhigh`）— 判断を要する、閉じた1つの作業。互いに独立な作業を並行して
    行うときに使う。定義は道具を制限せず、作業が割り当てたファイルだけを書き、全体の作業が
    完了したとは宣言しない
  - `scrum-master-agent`（`sonnet`、`xhigh`）— `apply-scrum-guide` が、主の会話で働く Developer から
    切り離す Scrum Master のアカウンタビリティを担う。チームの Scrum の作成物と作業の事実を読み、
    阻害要因、透明性の欠け、Sprint Goal や Definition of Done からの逸脱についての所見を返す。
    道具は Read・Grep・Glob だけで、CLAUDE.md を読み込まずに始まる
- **`harness/skills/`**: 必要時に読み込まれるプレイブック。全部で13件あり、中央ルーティング表なしに
  自己記述だけで選択できる。各 `SKILL.md` は `description`（いつ使い、いつ使わないか）と、
  `metadata` に `kind`（`worker` か `overlay`。契約は `orchestrator` も定義しているが、
  今それを宣言するスキルはない）、`permission`（`read_only`・
  `workspace_write`・`external_effect`）、`sandbox` の宣言を持つ。`sandbox` は `inside`（同梱の
  コマンドがすべて、そのまま Bash のサンドボックスの中で動く）か `network`（一部の手順が、スキルの
  宣言したホストを必要とする）。`inside` は10件で、`apply-dads-frontend`・`build-dads-slides`・
  `manage-git` が `network`。スキルは、発動条件1つ・成果物1つ・完了確認（`Done when`）1つの単位であり、
  `tests/assert_skill_contract.py` が検査する契約を満たす（後述「検証」参照）
  - 変更を定め、実装するもの。変更の全体（意図から受け入れまで）のステージの順と承認ゲートは、
    AI-DLC Workflows v2 に任せる（後述「AI-DLC Workflows v2」参照）。残るのは次の3件で、
    `implement-change` はそのコード生成のステージの中で使うテスト先行の手順であり、ほかの2件は
    ワークフローの外でも使う: `clarify-intent`（まず意図の共通認識を
    形成する。AIが自分の理解・前提と確度・スコープ外・未決の点の4つを、ユーザーが却下できる形で述べ、
    事例ではなく基準に合意し、基準を名指しの枠組みに根拠づけ、3往復までに収め、合意をメモに記録する。
    依頼されたとき、または成果物の却下や同じ点の言い直しなどのずれが現れたときに動く。形式的な
    要件は書かない）、
    `define-problem`（曖昧な訴えを、現状とあるべき姿のギャップとその重要性としての、検証可能な
    問題文に変換する。持ち込まれた解決策や未検証の原因は、別の節に置く）、
    `implement-change`（コード・設定・テスト・スクリプト・インターフェースを、テストを先に、
    最小の一貫した歩幅で変える。完了条件を定め、観測できる振る舞いが変わるときは仕様を先に書き、
    検査が正しい理由で失敗するのを見て、それを通す最小の変更を行い、リポジトリ自身の検査を実行し、
    変えた契約を述べる文書を更新し、コミット・push・プルリクエストは依頼があったときだけ行う。
    仕様先行、型安全、入力・エラー・秘密・ログといったシステムの境界についての指針は、当てはまるときだけ読み込む）
  - そのほかの作業:
    `structure-document`（文書 — 報告書、提案書、設計書、仕様書、README、メール、スライドの骨子、
    プルリクエストや issue の本文 — を、結論を先に置く1本の主張の木として組み、同梱の標準ライブラリだけの
    検査器（`check.py`）で本文を検査し、論理の審査では既存の文書から書き起こした主張の木も検査する。
    会話の外に出る文書は、会話を見ていないサブエージェントにも読ませる
    （[spec 057](specs/057-context-free-reader/spec.md)）。このスキルは文書の作成・改訂・審査のときだけ使い、
    回答は常時ロードのルール `pyramid-principle.md` が受け持つ）、
    `sync-docs`（変更に合わせて、コード・仕様・決定・研究の成果物とドキュメントの整合を保ち、
    ドキュメントのずれを監査する。同梱の読み取り専用の標準ライブラリのスクリプトが、プロジェクトを調べ、
    変更された成果物の種類と、変更したファイルの近くにある文書を挙げ、リンクを検査する。更新は同じ変更に入れ、
    報告は `Documentation impact` のブロックを持つ。`.living-documentation.json` はスクリプトの分類を補正し、
    プロダクトと機能フォルダの文書の木を宣言できる。宣言した木の README が親子で互いにリンクしていることを
    `check_tree.py` が検査し、`settings.json` のフックが `git commit` の前にその誤りを Claude に伝える。
    頼まれれば、節の種類ごとの README のひな形からその木を作り、確かめた事実だけを書き、
    残りに `TODO(unfilled)` を付ける）、
    `manage-git`（履歴をレビューできる形に保ち、頼まれた範囲を超えて公開しないための、ブランチ・
    Conventional Commits・プッシュ・プルリクエストの運用。コミット・プッシュ・プルリクエストは、それぞれ
    別の依頼を要する）、
    `research-aws`（記憶ではなく、そのセッションで使える第一者のドキュメントツールで読んだ AWS 公式
    ドキュメントから答える。AWS に固有の主張は、公式ページを引くか、未検証と記す）、
    `draw-system-diagrams`（非エンジニアから専門家まで、初めて見る人が読めるシステム構成図。
    1枚が1つの問い・1種類の読者・1つの抽象度に答える C4 の図の一式を、既定は Markdown 内の Mermaid、
    合う場合は draw.io か Structurizr DSL で、すべての要素を根拠にたどれる形で作り、タイトル・導入文・
    凡例・線のラベル・1枚あたりの要素数の上限・すべての図を結ぶ索引を、同梱の標準ライブラリだけの
    検査器（`check_diagrams.py`）で確かめる。クラウド事業者の公式アイコンで描く図は対象外）、
    `build-dads-slides`（DADS 公式の HTML と CSS の資材で、16:9 スライドを1つの HTML ファイルとして
    作成し、ミント・ピラミッドの木を、聞き手に合わせて選んだ2つの型のどちらかで組み（論文型は
    要旨 → 前提 → 方法 → 結果 → 考察 → 結論、ビジネス型は導入 → 結論 → 論点 → 次の一手で、
    論文型の方法と考察を借りられる）、
    本編の各スライドに全体の中の現在地を、
    全スライドの右上に機密性と公開範囲の表示を置き、同梱のリンタとプレビュー画像で確認する）
  - ドメインオーバーレイ（一致する作業と組み合わさる。置き換えではない）: `apply-dads-frontend`
    （DADS に基づくアクセシブルな React/Tailwind の公共サービスのフロントエンドと Web
    ダッシュボード。同梱の公式ドキュメントの原文の写しを使い、確認した出典・逸脱・アクセシビリティの
    証拠を報告する）、`apply-secure-logging`（OWASP Logging Cheat Sheet・ASVS V16・CWE の項目と、
    各スタックの公式ドキュメントにあるログの作法を載せた同梱のチェックリストに基づく、アプリケーションと
    CI のログの実装と検査。各項目は pass・fail・N/A・未検証のいずれか1つの状態と証拠を持ち、保管・転送・
    保持期間・アラートに関する項目は、アプリケーションのコードから pass にしない）、
    `apply-scrum-guide`（Scrum Guide 2020 だけを規範に、AI が Scrum Team の Developers の一人として
    リポジトリで開発する。作業の前に Product Goal・Sprint Backlog・Definition of Done を読み、作業を
    Sprint Goal に結び付け、Definition of Done の項目ごとの証拠がそろうまで完了としない。Scrum Master の
    アカウンタビリティは、イベント・作成物・逸脱の診断と改善を含め、独立したサブエージェント
    `scrum-master-agent` が担う。Scrum の作成物があるリポジトリでは、依頼に Scrum という語がなくても
    開発のたびに使う。読み取り専用で、Guide の日本語版と US 版の PDF を同梱する。スキルの本文は日本語。
    [ADR-0025](docs/adr/0025-ai-as-developer-scrum-master-as-subagent.md)）、`manage-scrum-artifacts`（プロダクトごとの Scrum の作成物を、リポジトリの中の
    ファイルとして保つ。同梱した9つの Scrum Guide の雛形から、Product Backlog、Definition of Done、
    Sprint ごとの記録をプロダクトのフォルダの `scrum/` に置き、Sprint のフォルダを1つずつ足し、
    同梱の読み取り専用のスクリプトで形を検査する。検査は、まだ書かれていない Product Goal・
    Sprint Goal・Definition of Done も警告する。既存のファイルは書き換えず、Scrum Team が決める値は埋めない）
  - スキルはほかのスキルを名指ししない。例外は親スキル（複数のスキルを決まった順序で適用する取りまとめ役のスキル）で、自分の `SKILL.md` の `## Child skills` 節で宣言した子スキルだけを、パスではなく名前で参照できる。子スキルは自分の子を宣言しない（[spec 058](specs/058-parent-skill-references/spec.md)）。今は親スキルがない。唯一の親スキルだった `deliver-change` は退役した（[ADR-0029](docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md)）。スキルは `harness/agents/` に定義したサブエージェントも名前で名指せる。`apply-scrum-guide` は `scrum-master-agent` を起動し、起動できないときは、自分の検査を独立した Scrum Master の所見ではない自己点検と明記する
  - 以前の構成の17件のスキルは破棄し、新しい名前で、16件に作り直した。新旧の対応は
    [`docs/harness-zero-base.md`](docs/harness-zero-base.md) にある。`manage-scrum-artifacts` は、
    その作り直しの後に加えたもので、これで17件になった（[ADR-0023](docs/adr/0023-keep-scrum-artifacts-in-the-product-repository.md)）。
    その17件のうち4件（`deliver-change`・`specify-requirements`・`verify-change`・`define-product-strategy`）は、
    変更を意図から受け入れまで運ぶ基盤を AI-DLC Workflows v2 にしたときに、それらだけを対象にしていた
    テストとともに [`archive/delivery-gates/`](archive/delivery-gates/README.md) へ退避し、13件が残った
    （[ADR-0029](docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md)）。Apple Notes と Apple Reminders の
    連携は、代わりを置かずに除いた。以前のスキルの一部が持っていたスキル内の README、評価の資料、
    プラグインのマニフェストは引き継いでいない。取り込んでいた `minto-pyramid` プラグイン
    （`pyramid-structure` に置き換え、それは今の `structure-document`）、従来の Minto スイート
    （`minto-builder`・`minto-reviewer`・`minto-rewriter`）、`adr` スキル（採番・言語の規則を
    `maintaining-living-documentation` へ統合した。それは今の `sync-docs`）、`meta-spec` スキル（不要と判断した。
    [spec 058](specs/058-parent-skill-references/spec.md)）は、以前に同期対象外の
    [`archive/`](archive/) に退避している
  - Spec Kit の `speckit-*` スキルはこのリポジトリでは vendoring しない。各プロジェクトで
    `specify init` を実行した際に、`--integration` が指す各エージェントのディレクトリ
    （`.claude/skills/`、`.agents/skills/`、`.cursor/skills/`）配下に生成される
    プロジェクトローカルな成果物で、すべて gitignore 対象（後述「spec-kit のオプトイン」参照）
- **`install.sh`**: `harness/` を `~/.claude/` にコピーし、このリポジトリの Claude Code
  プラグインをインストール/有効化する（後述「プラグイン」参照）。MCP サーバーは
  インストールしない — 許可された2つを各自で登録する（後述「MCP サーバー」参照）
- **`team/package-safety/`**: 他の開発メンバーに配布するパッケージインストール安全化バンドル。
  リポジトリの `.claude/settings.json` としても managed settings の drop-in としても使える
  Claude Code 設定ファイル 1 つと、公開から 7 日以上たった版だけを入れるための npm・pnpm・uv の
  テンプレートからなる。`install.sh` の同期対象ではなく、このリポジトリ自身の設定も変えない。
  詳細は[バンドルの README](team/package-safety/README.ja.md) と
  [ADR-0017](docs/adr/0017-team-package-install-safety-bundle.md) を参照
- **[`chatgpt-system-prompt.md`](chatgpt-system-prompt.md)・
  [`claude-ai-system-prompt.md`](claude-ai-system-prompt.md)**: この設定の作業原則を
  ChatGPT と Claude.ai のカスタム指示欄へ持ち込むための、貼り付け用のポータブル
  プロンプト。Claude.ai 用のファイルには、`harness/skills/` のうち Claude.ai に
  そのままアップロードできるスキルと、その ZIP の作り方も載せている。
  `install.sh` の同期対象ではない

### フェーズの木

すべてのスキルとサブエージェントの定義は、3段の木の中の場所を1つ、自分の前付けに宣言します（`metadata.phase`、`metadata.branch`、段階が2つ以上の枝にまたがるときは `metadata.stage`）。`description` の末尾にも、同じ場所を `[Construction / execute]` のような標識で書きます。フェーズは、その要素の主な成果物が支える AI-DLC Workflows v2 のフェーズで、`ideation`・`inception`・`construction`・`operation` のいずれか、または1つのフェーズに結び付かないときの `cross-phase` です。今、`operation` を宣言する要素はありません。枝は、その要素が支える `harness/CLAUDE.md` の節で、[`docs/harness/capability-map.json`](docs/harness/capability-map.json) と同じ語を使います。下の表は、宣言から `python3 tests/assert_role_tree.py --table ja` で生成したもので、同じスクリプトが宣言と一致するかも確かめます。目的の列は各 `description` の最初の文です。木の図は [`docs/harness/skill-map/03-role-tree.md`](docs/harness/skill-map/03-role-tree.md)、決定は [ADR-0029](docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md) にあります。この木は、Scrum の役割の木（[ADR-0026](docs/adr/0026-place-skills-and-agents-in-a-scrum-role-tree.md)。今は置き換え済み）に代わるものです。検査スクリプト、図のページ、表を囲む目印は、その木のときの名前（`assert_role_tree.py`、`03-role-tree.md`、`role-tree`）のままです。

<!-- role-tree:start -->
| フェーズ | 枝 | 名前 | 種類 | 目的 |
|---|---|---|---|---|
| Ideation | define | `define-problem` | スキル | Turn a vague sense that something is wrong into one verifiable problem statement - the gap between the current state and the ideal state - in any domain, business, technical, personal, or organizational, keeping the problem apart from any solution or unverified cause brought along with it. |
| Inception | execute | `draw-system-diagrams` | スキル | Create, split, or review system architecture diagrams (システム構成図) that a first-time reader, from a non-engineer to a specialist, can follow - a set of views, each answering one question for one audience at one C4 level, written as Mermaid in Markdown by default, draw.io when a person will hand-edit the layout, or Structurizr DSL when many views share one model, and checked by a bundled checker. |
| Construction | execute | `apply-dads-frontend` | スキル | Apply the Digital Agency Design System (DADS), its dashboard guidance, and public-interest accessibility to React and Tailwind CSS frontend work, from a bundled copy of the official documentation. |
| Construction | execute | `apply-secure-logging` | スキル | Implement, change, or review application and CI logging against a bundled checklist of security requirements (OWASP Logging Cheat Sheet, OWASP ASVS V16, related CWE entries) and of the logging practices in the official documentation of Python, React, AWS Lambda, Google Cloud including Cloud Run functions, Azure including Azure Functions, cloud AI inference services, and GitHub Actions. |
| Construction | execute | `implement-change` | スキル | Change code, configuration, tests, scripts, interfaces, or other observable behavior test-first, in the smallest coherent step, and verify it before reporting. |
| Cross-phase | define | `clarify-intent` | スキル | Form an explicit shared understanding of what the person intends before work continues - state the reading as something they can reject, converge on a criterion rather than on cases, and record the agreement. |
| Cross-phase | define | `research-aws` | スキル | Answer a question about a current AWS service from official AWS documentation, read through whatever first-party documentation tools the session has, instead of from recollection. |
| Cross-phase | execute | `apply-scrum-guide` | スキル | Scrum Guide (2020) を唯一の規範として、AI が Scrum Team の Developers の一人としてリポジトリで開発し、Scrum Master のアカウンタビリティは独立したサブエージェントに担わせる。 |
| Cross-phase | execute | `build-dads-slides` | スキル | Build 16:9 presentation slides as one HTML deck on the Digital Agency Design System's official HTML and CSS reference assets, structured as a Minto pyramid in the form its audience needs - a research-paper form (summary, premises, method, results, discussion, conclusion), a business-presentation form (introduction, answer, supporting points, next step), or a business deck that borrows parts of the paper form - with every slide showing where it sits in that structure. |
| Cross-phase | execute | `check-runner` | エージェント | Runs checks whose output is long - tests, builds, linters, type checkers - and reports each command, its exit code, and the verbatim output of every failure. |
| Cross-phase | execute | `file-searcher` | エージェント | Searches a codebase or a set of documents read-only and returns where things are, with paths and line numbers. |
| Cross-phase | execute | `manage-git` | スキル | Create branches, commits, pushes, and pull requests so that history stays reviewable and nothing is published beyond what was asked. |
| Cross-phase | execute | `manage-scrum-artifacts` | スキル | Keep a product's Scrum artifacts as files inside its repository - the Product Backlog with its Product Goal, the Definition of Done, and for each Sprint the Sprint Backlog with its Sprint Goal, the Increment, and the event records - placed from bundled Scrum Guide (2020) templates under the product folder's scrum/ directory, extended one Sprint at a time, and checked by bundled scripts. |
| Cross-phase | execute | `scrum-master-agent` | エージェント | Holds the Scrum Master accountability of the Scrum Guide (2020) for a Scrum Team in which the agent that starts it works as one of the Developers. |
| Cross-phase | execute | `task-worker` | エージェント | Carries out one self-contained task that needs judgment - a piece of research, an analysis, or a change to files that no other agent is writing - and returns a short report. |
| Cross-phase | handoff | `read-only-reviewer` | エージェント | Independent read-only reviewer for a review that must not start from the author's reasoning, such as a challenge of requirements or a review of a change's evidence. |
| Cross-phase | handoff | `structure-document` | スキル | Structure a document as one claim tree, so that a reader finds its one answer first and can check the support under it, and check the result with the bundled checker - a report, proposal, design document, specification, README, email, slide outline, or pull-request or issue body. |
| Cross-phase | handoff | `sync-docs` | スキル | Keep documentation consistent with code, specifications, decisions, and research artifacts as they change, and audit existing documentation for drift, using bundled read-only scripts that list the documents a change may leave out of date. |
<!-- role-tree:end -->

## 補足ドキュメント

`docs/` は保守者向けで、Claude 向けではありません。`install.sh` は `~/.claude/`
へ同期しないため、`harness/` 配下からここへリンクしていません（ルールとスキルは
参照元を自分の中に持っています）。

| ドキュメント | 内容 |
|---|---|
| [`docs/claude-config-design.md`](docs/claude-config-design.md) | 常時ロードの指示が通すべき判断基準と、各ファイルが意図的に置いていないもの、ルールが引く参考文献の一覧 |
| [`docs/harness-zero-base.md`](docs/harness-zero-base.md) | harness の再設計。配布元を `harness/` に移し、17件のスキルを16件に作り直した理由、新旧のスキルの対応、すべてのスキルが満たすサンドボックスの契約、残りの作業。ADR-0029 で4件のスキルを退役させる前の記録 |
| [`docs/mcp-servers.md`](docs/mcp-servers.md) | MCP サーバーをユーザー自身が入れる理由、`.mcp.json` に書けること・書けないこと、各サーバーのベンダー公式リファレンス、`settings.json` で止めているサーバー、サーバー追加時の更新箇所 |
| [`docs/harness-eval.md`](docs/harness-eval.md) | harness 全体の振る舞いの基準。対応表とシナリオ集の検査、2つのコミットを費用の上限の下で `claude plugin eval` にかけて比べる手順、実際の環境との違い |
| [`docs/harness/capability-map.md`](docs/harness/capability-map.md) | 作業の各段階の担い手、担い手のない段階、互いに除外し合うスキル、各段階を覆うシナリオ（`capability-map.json` から生成） |
| [`docs/harness/skill-map/`](docs/harness/skill-map/README.md) | harness の組み立てを示す4枚の図。だれが使い何に頼るか、5つの層、すべてのスキルとサブエージェントを AI-DLC のフェーズと枝の下に置いたフェーズの木（宣言から生成）、どのスキルが判断基準を重ね・サブエージェントを起動させるか。退役した親スキルが子スキルを使う順を描いた5枚目の図は、[`archive/delivery-gates/`](archive/delivery-gates/README.md) にある |
| [`docs/adr/`](docs/adr/) | アーキテクチャ決定記録 — Accepted 後は不変で、supersede のみ |

## ユーザー設定としてインストール

以下を実行してください:

```sh
bash path/to/my-claude-code/install.sh
```

インストーラーは `harness/` から `~/.claude` を同期し、本リポジトリの Claude Code プラグイン
（後述「プラグイン」参照）をインストール/有効化します。

実行には `claude` CLI と `jq` が必要です。

インストーラーは MCP サーバーの登録・更新・削除を行わず、MCP サーバーを同梱する
プラグインもインストールしません。許可された2つのサーバーは、各自で登録してください（後述
「MCP サーバー」参照）。以前のバージョンのインストーラーなどで登録済みの
ユーザースコープ MCP サーバーは、そのまま残ります。ただし `settings.json` は、
許可された2つだけを読み込ませます。

### 重要: 上書き置換（削除同期）について

- 次の管理対象は **置換同期** されます:
  - `rules/`
  - `skills/`
  - `agents/`
  - `commands/`
  - `CLAUDE.md`
  - `install.sh`
- 例外として、`skills/` 内の `~/.claude/skills/synced/` は置換しません。ここは
  Claude アプリが自身のスキルを同期する場所なので、`skills/` を置き換える間だけ
  退避し、そのまま元の場所に戻します。途中で実行が止まった場合は
  `~/.claude/.install-keep.*/synced` に残ります。
- `settings.json` は置換ではなく **マージ同期** されます: このリポジトリが宣言する
  キー（`model`、`permissions`、`hooks` など）は常にリポジトリ側の値が優先されます
  （`permissions` のような共有オブジェクトの内部まで再帰的にマージするため、例えば
  `permissions.deny` は強制されたまま保たれ、同じオブジェクト内の他のキーは影響を
  受けません）。一方、このリポジトリが宣言していないトップレベルのキー——
  `/setup-bedrock` が書き込む `env` や、`agentPushNotifEnabled`、その他ユーザーや
  CLI自身が追加したキー——はそのまま保持されます。`enabledPlugins` について
  このリポジトリが宣言するのは `github@claude-plugins-official: false` だけで、
  ほかの項目は残ります。このリポジトリが宣言する配列（`permissions.deny`、
  `sandbox` のパスの一覧、`hooks.SessionStart`、`hooks.PreToolUse`、`deniedMcpServers`）は、ユーザーの
  配列と合わさらず置き換わります。それらへの自分の追加は、Claude Code がユーザー
  スコープと合わせて読むプロジェクトかローカルの設定に置いてください。
- このリポジトリ側で削除されたファイルは、`~/.claude` 側の置換対象パスでも
  削除されます。
- `agents/` には、5つのサブエージェントの定義（`read-only-reviewer`、
  `check-runner`、`file-searcher`、`task-worker`、`scrum-master-agent`）があります。ほかの管理対象と同じく
  `~/.claude/agents/` を置き換えるので、そこに自分で置いたエージェントのファイルは
  削除されます。自分のエージェントはプロジェクトの `.claude/agents/` に置いてください。
- `commands/` はこのリポジトリに元ファイルがなく、以前のバージョンが入れたものを
  片付けるためだけに管理対象に残しています。そのため実行のたびに
  `~/.claude/commands/` は削除されます。
- `settings.local.json` を含む `~/.claude` の管理対象外パスは保持されます。個人用ファイルは上記の管理対象外に置いてください。

## 代替: `CLAUDE.md` から import

コピーせずに参照する場合:

```markdown
@/absolute/path/to/my-claude-code/harness/CLAUDE.md
```

## AI-DLC Workflows v2

[AI-DLC Workflows](https://github.com/awslabs/aidlc-workflows) は、変更を意図から受け入れまで、フェーズと
ステージに分けて運ぶための、AWS が公開しているワークフローです。実行ファイル `aidlc` が、次に進む
ステージと承認ゲートを開く時点を決め、作業の状態と監査の記録をプロジェクトの `aidlc/` ディレクトリに
残します。この設定は、変更を届ける基盤としてこれを使い、harness はその補完です
（[ADR-0029](docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md)）。
harness のスキル、サブエージェント、ルールは、各ステージの中の作業と、ワークフローの外の作業に
適用します。`harness/CLAUDE.md` は、ステージの順とゲートをエンジンに任せ、人に代わってゲートを
承認しないよう Claude に指示します。

AI-DLC Workflows は、利用者がプロジェクトごとに導入します。このリポジトリの `install.sh` は導入しません。
導入すると、取得したインストーラーを利用者のマシンで実行することになるためです。`aidlc` コマンドを
一度入れ、そのあとプロジェクトごとに設定し、設定を確かめます:

```sh
curl -fsSL https://github.com/awslabs/aidlc-workflows/releases/latest/download/install.sh | sh
cd path/to/your-project
aidlc config --harness claude --mcp none --yes
aidlc doctor
```

- `--mcp none` は、AI-DLC の任意の MCP サーバーを入れません。harness の MCP サーバーの許可リスト
  （[ADR-0021](docs/adr/0021-block-mcp-servers-by-settings.md)。後述「MCP サーバー」参照）に
  それらは含まれず、入れても読み込まれないためです。
- この harness で試した版は v2.11.4 です。
- 未検証: この harness をインストールした状態で、Claude Code の Bash のサンドボックスの中で
  ワークフローを最後まで実行すること。

## 構成

```text
my-claude-code/
├── CLAUDE.md                       # リポジトリの目的と、ここでの作業の定め(リポジトリ内専用, 同期対象外)
├── README.md                       # 英語版ガイド(本書は README.ja.md)
├── README.ja.md
├── install.sh                      # 管理対象の Claude パスを harness/ から同期 + プラグインをインストール(MCP サーバーは入れない)
├── .mcp.json                       # 許可された2つの MCP サーバーの、プロジェクトスコープの定義
├── .living-documentation.json      # sync-docs のスクリプト設定(specs/ を除外)
├── chatgpt-system-prompt.md        # ChatGPT のカスタム指示用ポータブルプロンプト(同期対象外)
├── claude-ai-system-prompt.md      # Claude.ai の指示欄用ポータブルプロンプト(同期対象外)
├── docs/                           # 保守者向け文書: 設計根拠、harness の再設計、MCP の背景、ADR(同期対象外)
├── tests/                          # オフラインの契約テスト(run-*.sh)、assert_*.py の補助、fixture。「検証」参照
├── specs/                          # このリポジトリ自身の変更の Spec Kit 機能仕様
├── .specify/                       # Spec Kit のプロジェクトファイル。チェックアウトごとのローカル(gitignore、ADR-0022)
├── scrum/                          # このリポジトリ自身の Scrum の作成物。manage-scrum-artifacts で置いたもの(同期対象外, ADR-0023)
├── archive/                        # 参照用に残した退役スキルとそのテスト(同期対象外)
├── team/package-safety/            # チーム配布用バンドル: Claude 設定 + npm/pnpm/uv テンプレート(同期対象外, ADR-0017)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # main への push/PR ごとに、挙げた tests/run-*.sh を実行(必須チェック)
│   │   └── dependabot-automerge.yml # パッチ/マイナーのDependabotセキュリティ修正PRをCI通過後に自動マージ
│   └── rulesets/main-required-checks.json # main の必須ステータスチェックruleset定義
└── harness/                        # インストーラーが管理する Claude パスの正本(~/.claude/ にインストールされる)
    ├── CLAUDE.md                   # 達成目標: 定義 → 実行 → 引き渡し。設計根拠は docs/
    ├── settings.json               # ユーザーレベル設定: deny、サンドボックス、SessionStart と PreToolUse のフック、MCP の許可リストと停止
    ├── rules/                      # 常時ロード: 毎セッション読み込む、独立した4つの関心事
    │   ├── clarifier.md            # 要件確実性: 確認するか進めるか
    │   ├── thinking-lenses.md      # 推論の完全性: 毎タスクに適用する4つのセルフチェック
    │   ├── permissions.md          # 権限と安全性。強制される deny は settings.json
    │   └── pyramid-principle.md    # 読み手本位の構造: ピラミッド、論文の構成の順序、前提と用語
    ├── agents/                     # サブエージェントの定義: 委任する作業の種類ごとにモデル・effort・道具を固定
    │   ├── read-only-reviewer.md   # 独立したレビュー: Read/Grep/Glob だけ、CLAUDE.md なしで始まる
    │   ├── check-runner.md         # 出力の長い確認: 各コマンド・終了コード・失敗の原文を報告
    │   ├── file-searcher.md        # 読み取り専用の検索: パス:行 の位置を返す
    │   ├── task-worker.md          # 判断を要する閉じた1つの作業。ほかの作業と並行して行う
    │   └── scrum-master-agent.md   # 主の会話の Developer から独立した Scrum Master: Read/Grep/Glob だけ
    └── skills/                     # 必要時のみ: 関連するときに本文を読み込む、自己記述型。13件
        ├── clarify-intent/         # 意図の共通認識の形成(作業)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   枠組みの在庫(ユーザーに名指す)+ 設計根拠(名指さない)
        ├── define-problem/         # 問題 = 現状とあるべき姿のギャップ(作業)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   枠組みの出典
        ├── implement-change/       # 変更手順、テスト先行(作業)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   仕様先行、型安全、システムの境界(それぞれ当てはまるときだけ読む)
        ├── structure-document/     # 文書の主張の木 + 同梱の構成検査(作業)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   ひな形、文書の種類、主張の木の形式、文脈なしの読み直し
        │   ├── scripts/            #   check.py(読み取り専用、標準ライブラリのみ)
        │   └── tests/              #   単体テスト
        ├── sync-docs/              # 変更とドキュメントの整合(作業)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   実務、規格とその優先順位、規範の根拠、文献表
        │   ├── scripts/            #   inspect_project.py、audit.py、find_related.py、check_links.py、check_tree.py(標準ライブラリのみ)
        │   ├── schemas/            #   .living-documentation.json の config.schema.json
        │   ├── templates/          #   ADR、アーキテクチャ記述、来歴、文書の木の節の種類ごとの README、CI ワークフロー
        │   └── tests/              #   単体テスト
        ├── manage-git/SKILL.md     # ブランチ/コミット/プッシュ/PR 運用(作業。リモートのホストが要る)
        ├── research-aws/SKILL.md   # AWS 公式ドキュメントの最新調査(作業)
        ├── draw-system-diagrams/   # 初めて見る人向けの C4 の図を Mermaid・draw.io・Structurizr DSL で作る(作業)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   図の種類、表記、形式ごとの書き方
        │   ├── assets/templates/   #   図のページ、索引、draw.io ファイル、Structurizr の workspace
        │   ├── examples/           #   検査器を通る図の一式の作例
        │   ├── scripts/            #   check_diagrams.py(読み取り専用、標準ライブラリのみ)
        │   └── tests/              #   単体テスト
        ├── build-dads-slides/      # DADS 16:9 HTML デッキをミント・ピラミッドで、論文型かビジネス型で組む(作業。資材の取得にネットワークが要る)
        │   ├── SKILL.md            #   プレイブック
        │   ├── references/         #   スライド設計、マークアップ契約、検査、資材の出典
        │   ├── assets/             #   1280x720 のレイアウト CSS + 注釈付きデッキテンプレート
        │   └── scripts/            #   セットアップ、公式資材の取得、ブラウザ内の検査、デッキ CLI
        ├── apply-dads-frontend/    # DADS React/Tailwind の手順 + 出典付きの参考資料(オーバーレイ。パッケージの確認にネットワークが要る)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   出典、コンポーネントの実装、アクセシビリティの関門、ダッシュボード、dads-docs/ の原文の写し
        ├── apply-secure-logging/   # OWASP + 各スタックのログ作法のチェックリスト(オーバーレイ)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   出典付きチェックリスト(ASVS V16、CWE、OWASP、各スタックの公式文書)
        ├── apply-scrum-guide/      # Scrum Guide (2020) だけを規範に、AI は Developer、Scrum Master はサブエージェント(オーバーレイ)
        │   ├── SKILL.md            #   プレイブック
        │   └── references/         #   必要時に読む参考文書5件 + Scrum Guide の PDF
        └── manage-scrum-artifacts/ # Scrum の作成物を、各プロダクトの scrum/ の下のファイルとして保つ(作業)
            ├── SKILL.md            #   プレイブック
            ├── references/         #   配置の決まりと検査の規則、イベントの準備
            ├── scripts/            #   scaffold.py(新しいファイルだけを置く)、check_artifacts.py(読み取り専用)
            ├── templates/          #   リポジトリに写す Scrum Guide の雛形9件
            └── tests/              #   スクリプトと手順の文面の単体テスト
```

## 検証

`.mcp.json` / `install.sh` / `harness/settings.json` /
[`harness/skills/research-aws/SKILL.md`](harness/skills/research-aws/SKILL.md) を変更したら:

```sh
bash tests/run-mcp-startup.sh # ネットワーク接続と書き込み可能な uv キャッシュが必要
bash tests/run-install.sh
bash tests/run-removed-guardrails.sh
bash tests/run-sandbox-settings.sh
bash tests/run-commit-tree-hook.sh
```

`harness/skills/` か `harness/agents/` の下を変更したとき、スキルやサブエージェントを追加・削除・
改名したとき、またはどちらかの README を編集したら:

```sh
bash tests/run-harness-skills.sh
bash tests/run-readme-skill-index.sh
```

前者は、スキルをオフラインで、Bash のサンドボックスの中のまま検査する（ネットワークなし、
リポジトリの外への書き込みなし、一時ファイルは `$TMPDIR` の下だけ）。最初に
[`tests/test_skill_contract.py`](tests/test_skill_contract.py) を実行し、契約の各規則が不合格を出せることを
示す: 各テストは、一時ディレクトリに有効な小さなスキルの木を作り、1か所だけ壊し、その箇所を覆う規則を
検査が報告することを確かめる。次に
[`tests/assert_skill_contract.py`](tests/assert_skill_contract.py) を実行し、すべてのスキルに規則 C-01 から
C-11（スクリプトの docstring に一覧がある）を課す: 名前がディレクトリと一致すること、`description` が
1行で1,024字以内であり、使わない場面を述べていること、許された前付けのキーだけを持ち、モデルを切り替える
ものがないこと、`metadata` が定義された `kind`・`permission`・`sandbox`・`phase`・`branch` を持ち、ネットワークが要る
スキルがホストを名指していること、本文が大きさの上限に収まること、`Done when` の節があり、同梱の
参照ファイルのそれぞれに読む条件を書いた `Bundled files` の節があること、サンドボックスを壊す
コマンド（引数なしの `mktemp`、`/tmp` の直書き、リポジトリの外への書き込み、宣言のないスキルでの
`osascript` やネットワークのコマンド）がないこと、廃止したスキルを名指さないこと、宣言した子を名指す取りまとめ役のスキルでなければ、
ほかのスキルを名指さないこと、インストール先に依存するパスや、このリポジトリの `specs/`・`archive/` への
参照がないこと、パッケージ内の相対リンクが解決すること、取りまとめ役のスキルが実在する
子を2件以上宣言し（その子に取りまとめ役はいない）、ほかの種類は子を宣言しないこと。次に [`tests/assert_role_tree.py`](tests/assert_role_tree.py) を実行し、すべてのスキルとサブエージェントの定義の[フェーズの木](#フェーズの木)を確かめる: `metadata.phase` と `metadata.branch` を定義された値で1回ずつ宣言していること、対応表がその要素を持ち、枝が担う段階と合うこと（段階が2つ以上の枝にまたがるときは `metadata.stage` で段階を選ぶ）、`description` の末尾が一致する標識であること、README の表と木の図が宣言から生成したものと一致すること。`--self-test` は、どれか1つの規則を壊した写しが拒まれることを示す。次に
[`tests/assert_reviewer_agent.py`](tests/assert_reviewer_agent.py) を実行し（検査 HS-05）、サブエージェントの
各定義がモデル・effort・道具を固定していること、`read-only-reviewer` と `scrum-master-agent` が Read・Grep・Glob
だけを許すこと、`apply-scrum-guide` が `scrum-master-agent` を名指していること、そのどれか1つを変えた写しが
拒まれることを確かめる。続けて、
`draw-system-diagrams`・`structure-document`・`sync-docs`・`manage-scrum-artifacts` に
同梱した検査スクリプトの単体テストを実行する。1つのスキルの単体テストだけを実行するには:

```sh
python3 -B -m unittest discover -s harness/skills/sync-docs/tests -t harness/skills/sync-docs/tests -v
```

後者は、`harness/skills/` のスキルのディレクトリか、`harness/agents/` のサブエージェントの定義が、
`README.md` と `README.ja.md` の両方に `` `<name>` `` または `<name>/` のパスとして
書かれていなければ失敗する。

[`team/package-safety/`](team/package-safety/) を変更したら:

```sh
bash tests/run-package-safety-bundle.sh
```

バンドル内のファイル同士の整合をネットワークなしで検査する。Claude Code 内での
振る舞いは、[バンドルの README](team/package-safety/README.ja.md#適用されたことの確認)
の手順で手で確認する。

[`harness/CLAUDE.md`](harness/CLAUDE.md)・[`harness/rules/`](harness/rules/) を変更したら:

```sh
bash tests/run-config-pyramid.sh
```

常時ロードの層をオフラインで検査する: apex の3分岐と3つの条件による委任、AI-DLC Workflows を使う
プロジェクトでは apex がステージの順とゲートの承認をそれに委ね、人に代わってゲートを承認しないこと、
ADR-0029 で退役した4件のスキルが `harness/skills/` に戻っていないこと、他のルール・スキル・設定パスを
名指さず参考文献の一覧も持たないちょうど4つのルールファイル、各スキルの description が保つべき語句
（依頼が同じように振り分けられるように）、apex とルールを合わせた大きさが予算の内に収まること。

[`harness/skills/draw-system-diagrams/`](harness/skills/draw-system-diagrams/) を変更したら:

```sh
bash tests/run-draw-system-diagrams-skill.sh
bash tests/run-harness-skills.sh
```

前者は、同梱の検査器の受け入れテスト(Python の標準ライブラリのみ)を実行し、同梱の作例の一式とひな形が
検査器を通ること、ラベルのない線があり凡例のないページが検査器で不合格になることを確かめる。
一式の Mermaid が描画できるかは確かめない。GitHub か `mmdc` で描画して確かめる。

[`harness/skills/apply-secure-logging/`](harness/skills/apply-secure-logging/) を変更したら:

```sh
bash tests/run-apply-secure-logging-skill.sh
bash tests/run-harness-skills.sh
```

前者は、スキルの構造と、チェックリストの出典の規則を検査する。スキルの振る舞いは、
`tests/fixtures/secure-logging/` の見本を使って手で確認する。

[`harness/skills/apply-dads-frontend/`](harness/skills/apply-dads-frontend/) を変更したら:

```sh
bash tests/run-apply-dads-frontend-skill.sh
bash tests/run-harness-skills.sh
```

前者は、スキルの契約を検査する: 出典とライセンスの参考資料、コンポーネントの実装・アクセシビリティ・
ダッシュボードの参考資料、同梱した公式ドキュメントの原文の写し。

[`harness/skills/build-dads-slides/`](harness/skills/build-dads-slides/) を変更したら:

```sh
bash tests/run-build-dads-slides-skill.sh
bash tests/run-harness-skills.sh
```

`tests/fixtures/slides/` の自己完結した fixture に対してデッキの検査ツールを実行し、
最後に公式 DADS スタイルシートを取得して同梱のデッキテンプレートを検査・プレビューする
end-to-end セクションを実行します。どちらも `playwright` を備えた Python 環境が必要です —
`DECK_PYTHON` でその環境を指定してください。指定がない場合、これらは失敗ではなく
スキップとして報告されます。end-to-end セクションはさらにネットワーク接続を必要とします。

`harness/` 配下（apex、ルール、サブエージェント、スキル）か、harness 全体の振る舞いの基準の
対応表・シナリオ集を変更したら:

```sh
bash tests/run-harness-eval.sh
```

モデルを呼ばずに、次を検査する。すべてのルールとスキルが
[`docs/harness/capability-map.json`](docs/harness/capability-map.json) に現れること。
引用した語句が、引用元のファイルにまだあること。作業の各段階に
[`tests/harness-eval/scenarios.json`](tests/harness-eval/scenarios.json) のシナリオがあること。
シナリオそのものを実行するとモデルの呼び出しに費用がかかり、費用の上限
（`harness_eval.py run --max-cost-usd N`）が要る。[`docs/harness-eval.md`](docs/harness-eval.md) を参照。

`run-removed-guardrails.sh` は特定の変更に紐づかない、常設の回帰防止チェックです —
hooks のディレクトリ（`harness/hooks/` と `.claude/hooks/`）や `scripts/` が再導入されたら失敗し
（[ADR-0005](docs/adr/0005-remove-claude-hooks.md)、
[ADR-0007](docs/adr/0007-remove-scripts.md)）、このリポジトリ自身の `.claude/` に管理対象の設定
（`CLAUDE.md`、`rules`、`skills`、`agents`、`settings.json`、`commands`）が再び置かれても失敗します
（そこにある写しは、プロジェクト設定として二重に読み込まれるため）。また
[ADR-0006](docs/adr/0006-remove-permissions-config.md) の上に
[ADR-0014](docs/adr/0014-restore-credential-deny-rules.md) が復元した
`permissions` ブロックを制約します — 許されるのは `deny` のみで、`allow` や
`ask` のティアがあれば失敗します。また `deny` の各項目は `~/` または `**/` で
アンカーされた `Read` ルールでなければなりません。単一の先頭スラッシュは
`install.sh` がユーザースコープへ複製した時点で別のパスに解決されるためです。

`run-sandbox-settings.sh` は、`harness/settings.json` の `sandbox`、`SessionStart`、
MCP のキーを [spec 067](specs/067-sandbox-by-default/spec.md) と
[ADR-0027](docs/adr/0027-open-aws-sso-config-and-caches-to-the-sandbox.md) に照らして検査します。
`~/.aws` の下で開け直すのが設定ファイルと SSO・CLI のキャッシュだけであること、
開け直した場所のどれも `~/.aws/credentials` や GPG の秘密鍵に届かないこと、
開けたパス・ソケット・ホストがレビュー済みのものとちょうど一致し、名前で外に出すコマンドが無いこと、許可する
MCP サーバーが AWS のドキュメントの2つだけで、`.mcp.json` もその2つだけを定義する
こと、止めた MCP サーバーが止まったままであることを確かめます。各 `SessionStart` フックも、
一時的な HOME と stub のコマンドで `sh`・`bash`・`zsh` のもとで実行します。
Claude Code がこれらのキーに従うかは、`install.sh` の後の新しいセッションで
手作業で確かめます。

`run-commit-tree-hook.sh` は、`git commit` の前に文書の木を検査する `PreToolUse` フックを確かめます
（[ADR-0024](docs/adr/0024-warn-claude-of-docs-tree-errors-before-commit.md)）。
一時的な HOME を使い、`sh`・`bash`・`zsh`（入っていれば）のもとで、次のことを確かめます。

- そのフックが1つだけあり、その `if` の絞り込みが、`-C <path>` などの git の大域オプションを挟む
  `git commit` も覆うこと。
- 木の誤りが、許可の判定を伴わない文脈として Claude に届くこと。
- `git status` では何も足さないこと。
- sync-docs や `python3` がなければ何もしないこと。
- 検査のスクリプト自身が終了コード 2（コミットを止めるコード）で落ちても、フックは 0 で終わること。

`run-install.sh` は隔離した HOME と外部コマンドの stub を使います。
`run-mcp-startup.sh` だけは設定済み MCP サーバーの起動コマンドを実行するため
ネットワーク接続が必要で、それ以外はローカル検証です。

## リポジトリのセキュリティ自動化

上記のうちいくつかは `main` への push/PR ごとに CI(`.github/workflows/ci.yml`)でも
自動実行されます。どれが動くかはそのファイルが一覧です。それ以外は手元で実行したときだけ動きます。
`main` はその CI ジョブ(`test`)を必須とする repository ruleset
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

## サンドボックスとセッション開始のフック

`settings.json` は Claude Code の OS サンドボックスを有効にします。サンドボックスは、
Claude が実行する Bash のコマンドを、許したファイルとホストだけに閉じ込める仕組みです
（macOS では Seatbelt）。厳しさは標準です。中で動かないコマンドは、通常の権限の確認
（auto モードの判定か、確認のプロンプト）を経て外で再実行でき、許可リストにないホストは
権限モードに従って決まります。Claude のファイルツール、MCP サーバー、フックは
サンドボックスの外で動きます。決定は [ADR-0020](docs/adr/0020-enable-sandbox-by-default.md)、
要件は [spec 067](specs/067-sandbox-by-default/spec.md) にあります。AWS のコマンドの動かし方は、
[ADR-0027](docs/adr/0027-open-aws-sso-config-and-caches-to-the-sandbox.md) が置き換えました。

このリポジトリのスキルとテストは、サンドボックスの中で動くように書いています。スキルの契約
（`tests/assert_skill_contract.py` の規則 C-07。「検証」参照）は、引数なしの `mktemp`、`/tmp` の直書き、
リポジトリの外への書き込みを退け、ネットワークが要るスキルは `metadata` に接続先のホストを宣言します。

想定した日常作業の動き方:

| 作業 | どこで動くか | 開けるもの | 閉じたままのもの |
|---|---|---|---|
| 署名つきの `git commit`（GnuPG） | 中 | `~/.gnupg` への書き込み、`S.gpg-agent` と `S.keyboxd` のソケット | 秘密鍵（`private-keys-v1.d`、`secring.gpg`）と失効証明書の読み取り。それらとキーリング、`trustdb.gpg`、gpg・gpgsm・gpg-agent のすべての設定ファイル、scdaemon が実行する `scd-event` への書き込み |
| IAM Identity Center（SSO）のプロファイルを使う `aws`、boto3、CDK、SAM、Terraform | 中 | `~/.aws/config`、`~/.aws/sso/cache`、`~/.aws/cli/cache` の読み取り、2つのキャッシュへの書き込み | `~/.aws/credentials`（長期のアクセスキー）の読み取り、`~/.aws/config` への書き込み。AWS のホストはすべて権限モードで決まる。Claude の Read ツールは `~/.aws` の下を読めない |
| Chromium、Playwright | 中。`--single-process` で起動する | 追加なし | — |
| Google Fonts からの Noto Sans のインストール | 中 | `~/Library/Fonts` への書き込み、`fonts.googleapis.com` と `fonts.gstatic.com` への確認なしの接続 | ほかのホストは権限モードで決まる |

ファイルツールの deny に加えて、サンドボックスの中のコマンドは `~/.git-credentials`、
`~/.netrc`、`~/.config/gh/hosts.yml`、`~/.docker/config.json`、`~/.kube/config` も
読めません。名前でサンドボックスの外に出すのは、`gh pr`、`gh issue`、`gh repo view` だけです
（`excludedCommands`）。ほかのコマンドには閉じたままの `~/.config/gh/hosts.yml` のトークンを、
この3つだけが読めます。外で動く `gh pr` と `gh issue` は、権限モードが審査します
（[ADR-0028](docs/adr/0028-run-gh-pr-and-issue-outside-the-sandbox.md)）。
外で動くのは、単独のコマンドとして実行したときだけです。前に `cd` を置く、`$(...)`、ヒアドキュメント、
リダイレクト、`gh -R` のようにサブコマンドの前にフラグを置く、のいずれかを含む呼び出しは中に残り、
認証に失敗します。本文は `--body-file` で渡します。
`~/.aws/credentials` の長期のアクセスキーを使うプロファイルは、中では失敗します。そのコマンドは、
権限の確認を経て外で再実行できます。`aws sso login` は、`--use-device-code` を付けて中で動かします。
ブラウザの起動とローカルのポートでの待ち受けの代わりに、URL とコードを表示する方式です。

セッションの開始時に、`settings.json` に直接書いた3つの `SessionStart` フックが
サンドボックスの外で動きます:

- **Bedrock の変数を Bash から外す。** Claude Code が Amazon Bedrock 経由で Claude を
  呼ぶとき（`CLAUDE_CODE_USE_BEDROCK`）、Bash のコマンドは `AWS_PROFILE`、
  `AWS_DEFAULT_PROFILE`、`AWS_REGION`、`AWS_DEFAULT_REGION`、`AWS_ACCESS_KEY_ID`、
  `AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`、`AWS_BEARER_TOKEN_BEDROCK` を
  引き継ぎません。`--profile` を付け忘れた `aws` のコマンドが、Bedrock 用の
  アカウントとして動くことはありません。
- **gpg-agent。** `gpgconf` と `~/.gnupg` があれば、gpg-agent をサンドボックスの外で
  起動します。サンドボックスの中の署名つきの `git commit` は、鍵を読めて
  パスフレーズの入力を出せるこの agent につながります。
- **Claude への注意。** Bash ツールが zsh で動くとき（`CLAUDE_CODE_SHELL`、なければ
  `SHELL`）、そのことと、Claude のコマンドを最も多く壊した zsh の3つの落とし穴
  （一致しないグロブ、`=` で始まる語、zsh が分割しない引用符なしの変数）を伝えます。
  macOS では、サンドボックスの中の Chromium に `--single-process` が要ることを
  伝えます。`aws` CLI があれば、SSO のプロファイルならサンドボックスの中で認証できること、
  プロファイルをコマンドごとに指定すること（`--profile`、またはそのコマンドの前の
  `AWS_PROFILE=名前`）、ログインには `aws sso login --use-device-code` を使うことを伝えます。

Claude が `git commit` を実行する前には、`PreToolUse` フックが1つ、サンドボックスの外で動きます。
これも `settings.json` に直接書いた短いコマンドです。絞り込みの `"if": "Bash(git *)"` によって、
git のコマンドのたびに起動します（1回あたり約 0.16 秒）。どれがコミットかは、インストールした
`sync-docs` の `check_tree.py --hook` が判定します。

コミットのときは、`cd` や `-C` で移した後の、コミットが走るディレクトリから、その Git の作業ツリーの
根まで上り、最も近い `.living-documentation.json` を使います。その設定が文書の木を宣言していれば、
見つけた誤りを文脈として Claude に伝えます。誤りとは、README がないことや、親子のあいだの
リンクがないことです。誤りの1件は1行 200 字で切ります。

- **コミットは止めません。** 終了コードは常に 0 なので、Claude は次のコミットで直します。
- **それ以外では何もしません。** ほかのリポジトリでも、`sync-docs` や `python3` がないときも同じです。
- **Stop フックにはしていません。** Stop フックは、Claude が応答を終えるたびに動くフックです。
  理由は [ADR-0024](docs/adr/0024-warn-claude-of-docs-tree-errors-before-commit.md) にあります。

この設計で受け入れたリスクと、既知の制限（macOS、Claude Code 2.1.319 で確認）:

- gpg-agent がパスフレーズを覚えている間は、サンドボックスの中のどのコマンドも、
  ソケットを通じてあなたの鍵で署名できます。パスフレーズの無い鍵なら書き出しも
  できます。代わりに `git commit` を外で動かすと、リポジトリの git フックも外で
  動きます。
- サンドボックスの中のどのコマンドも、`~/.aws/sso/cache` の SSO のアクセストークンと、
  キャッシュされた一時的な認証情報を読め、2つのキャッシュを書き換えられます。この
  トークンは、割り当てられた全アカウントの一時的な認証情報を取れます。外へ送るには
  許可リストにないホストへの接続が要り、権限モードが決めます。`Read(~/.aws/**)` の
  deny が閉じたパスを `allowRead` が開け直せるかは、公式ドキュメントの「狭いパスが効く」
  からの推論で、測定していません。macOS で手作業で確かめる5項目は ADR-0027 にあります。
- AWS を呼ぶたびに、接続先のホストを権限モードが判定します。AWS のホストは許可リストに
  入れていません。`*.amazonaws.com` を開けると、どのコマンドも確認なしで任意の S3
  バケットへ送れるためです。
- AWS の許可は `~/.aws` を前提にしています。`AWS_CONFIG_FILE` で場所を変えている場合は
  及びません。ツールが `~/.aws` の外に書く場所（`~/.cdk`、`~/.aws-sam`、`~/.terraform.d`）は
  開けていません。
- `settings.json` の `env` は、Bash だけでなくフックと stdio の MCP サーバーにも
  届きます。そのため、AWS を呼ぶ stdio の MCP サーバーは、Bedrock のセッションでは
  Bedrock 用のアカウントとして動きます。AWS を呼ぶサーバーを持つ `deploy-on-aws`
  プラグインは無効にしてあり、許可された2つのサーバーは、公開されたドキュメントを
  検索します。Bedrock の認証情報を
  `env.AWS_PROFILE` ではなく `awsCredentialExport`（例:
  `aws configure export-credentials --profile <bedrock> --format process`）で渡せば、
  どの子プロセスにもプロファイルは届きません。
- プロジェクトとローカルの設定は、このファイルが設定したサンドボックスを緩められます。
  止められるのは管理設定だけです。
- Chromium（と Playwright、Puppeteer）は、`--single-process` で起動しないと、
  サンドボックスの中で起動の時点で止まります。`build-dads-slides` のスライドの
  検査器は自分でこのフラグを付けます。それ以外は呼び出す側が付ける必要があります。
  サンドボックスのプロキシ経由では、平文の HTTP は読めましたが、HTTPS は時間切れに
  なりました。
- macOS の `mktemp` は、テンプレートを渡さないと `$TMPDIR` を使わず、サンドボックスの
  中で失敗します。それを呼ぶスクリプト（Spec Kit の `setup-plan.sh` など）は外での
  再実行が要ります。
- サンドボックスの中では、`/usr/bin/diff` は `<(...)` が作る `/dev/fd` のパスを
  開けません。
- GnuPG の許可は `~/.gnupg` を前提にしています。`GNUPGHOME` を別の場所にしている
  場合、署名は外での再実行に回ります。keyboxd を使う場合、公開鍵の取り込みは
  keyboxd のソケットを通るので止まりません。

## MCP サーバー

読み込める MCP サーバーは、どのプロジェクトでも、AWS の公式ドキュメントを検索する
2つだけです。`settings.json` がこの2つだけを許可し、ほかは、だれが定義した
サーバーでも読み込みません（ユーザースコープの登録、プロジェクトの `.mcp.json`、
プラグイン、claude.ai）。理由はセキュリティです。MCP サーバーは Bash の
サンドボックスの外で動き、いくつかは起動のたびに公開されたばかりの最新版を実行し、
どれも、コマンドを実行できる同じセッションに、外部の文章と、場合によっては認証情報や
操作を持ち込みます。

| 許可するもの | 照合の方法 | 何をするか |
|---|---|---|
| `aws-knowledge` | URL `https://knowledge-mcp.global.api.aws` | AWS のドキュメントを HTTP で検索して読む。認証情報は使わない |
| `aws-documentation` | コマンド `uvx awslabs.aws-documentation-mcp-server@latest` | AWS のドキュメントを検索して読む。`uvx` で起動し、起動のたびに最新版を実行する |

リモートのサーバーは URL で、ローカルのサーバーはコマンドの完全一致で照合します。
名前では照合しません。名前は、だれでも付けられるラベルだからです。別のサーバーを
使うには、`harness/settings.json` の `allowedMcpServers` を変えて、インストールし直す
必要があります。

このリポジトリが MCP サーバーをユーザー設定に取り込まないことは変わりません。
`install.sh` は MCP サーバーを登録も削除もせず、`harness/` 配下も特定のサーバーが
あることを前提にしていません（`research-aws` は、そのセッションで実際に使える
ドキュメントツールを使います）。2つをユーザースコープに登録するには、次を
実行してください（2つ目には [uv](https://docs.astral.sh/uv/) が必要です）:

```sh
claude mcp add -s user aws-knowledge --transport http https://knowledge-mcp.global.api.aws
claude mcp add -s user aws-documentation -- uvx awslabs.aws-documentation-mcp-server@latest
```

[`.mcp.json`](.mcp.json) は、このリポジトリ内で作業するときのために、同じ2つを
定義します。`.mcp.json` に書けること、各サーバーのベンダー公式リファレンス、
何をいつ止めたかは [`docs/mcp-servers.md`](docs/mcp-servers.md) にあります。

以前に登録していて、許可から外れたサーバーは、設定には残りますが読み込まれません。
登録そのものを消すときは、各自で実行してください（例:
`claude mcp remove -s user wolfram`）。

許可リストに加えて、`settings.json` は次のものを直接拒否します。拒否は、どの
許可リストでも上書きできません
（[ADR-0021](docs/adr/0021-block-mcp-servers-by-settings.md)）:

| 止めるもの | 方法 | 理由 |
|---|---|---|
| 組み込みの Chrome 連携（`claude-in-chrome`） | `deniedMcpServers` の名前 | 組み込みのサーバーは、許可リストの対象にならない。外部の文章を読む同じセッションから、ログイン済みの利用者自身のブラウザを操作する |
| GitHub がホストする MCP サーバーと `github` プラグイン | `deniedMcpServers` の URL（`https://api.githubcopilot.com/*`）、`enabledPlugins` の `false` | 使っていない。作業は `gh` CLI で足りる |
| `deploy-on-aws` と `microsoft-docs` のプラグイン | `enabledPlugins` の `false` | 同梱する MCP サーバーが許可リストにないので、そのサーバーに頼るスキルが働かない（「プラグイン」参照） |
| `bedrock-agentcore` | `deniedMcpServers` の名前とコマンド | Claude Code が持つ AWS の認証情報で、AWS の実際のリソースを作成・変更・削除し、AWS でコードを実行する |
| claude.ai のコネクタ（Gmail、Google Calendar、Google Drive、Notion、Moneytree、Claude Docs、Wolfram） | `disableClaudeAiConnectors: true` | 私的なデータと外部の文章が Bash と同じセッションにそろうと、プロンプトインジェクションでデータを持ち出す経路になる |
| claude.ai から同期されるプラグイン（`productivity`、`pdf-viewer`） | `syncClaudeAiPlugins: false` | SaaS の MCP サーバーを、さらにすべてのセッションに持ち込む |

## プラグイン

`install.sh` は Anthropic 公式マーケットプレイス `claude-plugins-official`
（`anthropics/claude-plugins-official`）から、3 つの Claude Code プラグインを
インストールします: `frontend-design`（UI/UX 実装ガイダンス、Anthropic）、
`code-review`（マルチエージェント PR レビュー、`/code-review ultra` 含む、Anthropic）、
`skill-creator`（skill の雛形作成・評価、Anthropic）。マーケットプレイスが未登録なら
追加し、各プラグインをユーザースコープでインストール/有効化するため、このリポジトリに
限らず全プロジェクトで使えます。

同じマーケットプレイスの3つのプラグインは MCP サーバーを同梱しており、
`settings.json` が3つとも無効にしています。インストーラーはこれらをインストール
せず、各自が入れたものを削除もしません。無効にしたプラグインは、スキルも
サーバーも読み込まれません。

| プラグイン | 提供元 | 同梱するもの | 無効にしている理由 |
|---|---|---|---|
| `github` | GitHub | GitHub がホストする MCP サーバー | 使っていない。作業は `gh` CLI で足りる |
| `deploy-on-aws` | AWS | AWS のアーキテクチャ図とデプロイのスキル、インフラのコードと料金を扱う AWS の MCP サーバー | サーバーが許可リストにない（「MCP サーバー」参照）。デプロイのスキルは、そのサーバーに頼っている |
| `microsoft-docs` | Microsoft | Microsoft のドキュメントの MCP サーバーと、それを検索するスキル | サーバーが許可リストにない。スキルは、サーバーがないと用をなさない |

インストールそのものも消すときは、`claude plugin uninstall <名前>@claude-plugins-official`
を実行してください。

`install.sh` が行う3つのプラグインのインストールは、次のコマンドと同等です:

```sh
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install skill-creator@claude-plugins-official
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
  独自のプレイブックを持ちます。`implement-change` の、仕様を先に書く指針
  （`references/spec-first.md`）は、spec-kit の導入有無にかかわらず適用されます。
- `specify extension add git` — Git Branching Workflow 拡張
  （`/speckit-git.*`）をインストールします。

追加されるコマンド: `speckit.git.feature`、`speckit.git.validate`、
`speckit.git.remote`、`speckit.git.initialize`、`speckit.git.commit`

このリポジトリ自身も同じ扱いです。`.specify/` は gitignore されていて、
チェックアウトごとのローカルのものです（[ADR-0022](docs/adr/0022-keep-spec-kit-project-files-local.md)）。
Spec Kit の何もリモートには上げず、各自が最新のリリースで上の手順を実行します。
そのため、原則（`.specify/memory/constitution.md`）、フックのつなぎ方
（`.specify/extensions.yml`）、git 拡張の設定も、チェックアウトごとのもので、
spec-kit の既定から始まります。

すでに導入済みのプロジェクトで生成済みの `speckit-*` スキルを最新に保つのは、
今も手動の作業です — 自分で定期的に `specify init --here --force` を
実行してください。`specify-cli` 本体は別です — `harness/settings.json` には
`speckit-specify` スキル実行の直前だけ発火する狭い範囲の `PreToolUse` hook
（docs/adr/0008）があり、`github/spec-kit` の最新リリースタグと `uv` の
インストールレシートに記録された `rev=` を比較し、不一致なら
`uv tool install specify-cli --from git+... --force` で再インストールします
（ネットワークエラー時は fail-open で処理を止めません。他の `speckit-*`
スキルではこの hook は発火しません）。これは docs/adr/0005 の「`.claude/hooks/`
なし・自動強制なし」という広い方針に対する、意図的かつ限定的な例外です —
理由は docs/adr/0008 を参照してください。Spec Kit を導入していないプロジェクトへ
`specify init` を勧める指示は `harness/` のどこにもありません。`implement-change` が
Spec Kit の工程に従うのは、プロジェクトがすでに導入している場合だけです。
