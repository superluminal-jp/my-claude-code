# 常時ロード設定の設計方針

`harness/CLAUDE.md` と `harness/rules/` は、`install.sh` が `~/.claude/` に写し、セッション開始時に無条件で読み込まれる。全プロジェクト・全セッションに課金される固定費であり、書けば書くほど良くなるものではない。本書は、それらのファイルが**なぜ今の形なのか**を記録する。

設定ファイル自体には、この種の説明を置かない。Claude の判断を変えない文はコンテキストを消費するだけだからである。本書は `harness/` の外にあり、インストールも自動ロードもされない。

2026-11-10 に、ハーネス全体を組み直した。配布元は、このリポジトリの `.claude/` から `harness/` へ移り、スキルは 17 件を破棄して 16 件に作り直された。理由と旧名との対応は [`harness-zero-base.md`](harness-zero-base.md) にある。本書のうち、その日付を記した箇所が、組み直しで変わった点である。

## 1. 設定は強制しない。設定 *ファイル* が強制する

Claude Code は `CLAUDE.md` と `rules/` を **advisory（助言）** として扱い、`settings.json`（permissions、hooks）だけを**強制**する [1]。この区別は程度差ではなく種類の差である。

帰結として、原則をどれだけ巧く書いても保証にはならない。だから `CLAUDE.md` の各原則は「徳目」ではなく**観測可能な義務**として書かれている — transcript や diff で第三者が確認できる形。「正確であれ」は検証不能だが、「実行したコマンドと出力を示せ」は検証できる。検証できないものは当てにできない。

強制が必要な項目は設定側へ移してある。実例は3つある。ファイルツールに対する資格情報の読み取り拒否(経緯と受け入れた副作用は [ADR-0014](adr/0014-restore-credential-deny-rules.md))、Bash のコマンドを OS の制限で閉じ込めるサンドボックス、使わない MCP サーバーの拒否である([ADR-0020](adr/0020-enable-sandbox-by-default.md)、[ADR-0021](adr/0021-block-mcp-servers-by-settings.md))。hooks とガードレールスクリプトを全廃した経緯は [ADR-0005](adr/0005-remove-claude-hooks.md) と [ADR-0007](adr/0007-remove-scripts.md)。

例外として、`settings.json` の `SessionStart` フックが、条件に当たるセッションにだけ短い注意を文脈に足す(Bash ツールが zsh のとき、macOS のとき、aws CLI があるとき)。中身は §2 の問い「これが無いと Claude は間違えるか」を、会話記録とこのマシンでの観察で通したものに限る(zsh の3種類の誤り、サンドボックスの中の Chromium、サンドボックスの外に出る aws の書き方)。条件に当たらない環境では何も足さないので、ルールとして全セッションに課金しない。経緯は ADR-0020。

同じく文脈に足すだけの例として、`PreToolUse` フックが1つある。`.living-documentation.json` に文書の木を宣言したリポジトリで、Claude が `git commit` を実行する前にだけ、`check_tree.py` が見つけた誤り（README がない、親子のリンクがない）を伝える。コミットは止めない。経緯は [ADR-0024](adr/0024-warn-claude-of-docs-tree-errors-before-commit.md)。

## 2. 常時ロードに残す判断基準

一文ごとに問う — **これが無いと Claude は間違えるか。**

間違えないなら消す。具体的には、次のいずれかに当たる記述は常時ロードに置かない:

| 分類 | 意味 | 例 |
|---|---|---|
| ネイティブ | モデルが既に知っている、またはクライアント自身の挙動 | Conventional Commits の文法、命令形、50/72 規則、権限の評価順 |
| ハーネス注入済み | セッション開始時に自動で文脈に入る | 全スキルの名称・説明・トリガー語句、MCP サーバーの `instructions` |
| 参照資料 | 判断ではなく裏取りに使う | 準拠規格の一覧、参考文献、ベンダー公式 URL |
| 設計説明 | なぜその形なのか | 本書の内容そのもの |

この基準は公式ベストプラクティスの「Claude が指示なしで既に正しくできることは削除するか hook に変換せよ」「self-evident な徳目は除外せよ」に対応する [2]。

2026-11-10 まで、4つのルールはそれぞれ末尾に `## References` 節を持っていた。合計 3,062 字で、常時ロードの 17% を占め、上の表の「参照資料」に当たっていた。この基準を適用して、参考文献は本書の §6 へ移した。検査 RULE-25 は、ルールに参考文献の節が戻ると失敗する。

## 3. ファイル別 — 何を意図的に置いていないか

### 3.1 常時ロードに残る4つのルール

各ルールは apex の3分岐（定義・実行・引き渡し）のうち正確に1つだけを支え、他のルールが既に持つ関心事は持たない。

| ファイル | 置いていないもの | 所在 |
|---|---|---|
| `CLAUDE.md` | スキル一覧 | ハーネスが全スキルの説明を注入する。手書きの列挙は重複であり、以前はスキル数が増えるたびにドリフトしていた |
| `CLAUDE.md` | ルールの import | `paths:` を持たないルールは無条件ロードされるため冗長 [1] |
| `CLAUDE.md` | ルール・スキル・サブエージェント・コマンド・サーバーいずれの個別名、モデルの名前 | apex は意味で子を支えるのであり、名指しで委譲しない。名指しすると、子の改名・分割・削除のたびに apex 自体が壊れる |
| `permissions.md` | 資格情報パスの列挙 | `settings.json` の `permissions.deny` が正本 |
| `permissions.md` | 部分一致をグロブ化しない理由 | [ADR-0014](adr/0014-restore-credential-deny-rules.md) |
| `clarifier.md` | 意図の共通認識を形成する手順、判断基準の接地先となる枠組みの在庫、出典 | `harness/skills/clarify-intent/` |
| `clarifier.md` | 合意を検査できる要件に変換する手順、曖昧性パターン目録、品質ゲート | `harness/skills/specify-requirements/` |
| `pyramid-principle.md` | Minto の4条件の詳述そのもの、構成の機械検査、成果物を会話を見ていないサブエージェントに読ませる手順（spec 057） | `harness/skills/structure-document/`（spec 055 の `pyramid-structure` を作り直したもの。従来の対話・診断・書き直し向け Minto スキル3件は `archive/minto-suite/` へ、取り込みプラグイン `minto-pyramid` は `archive/minto-pyramid/` へ退避済み） |
| `thinking-lenses.md` | 4つのセルフチェック（依存と並行・条件と分岐・反復・推論）を出力へ強制する書式 | 自然な置き場がある成果物（要件の Given/When/Then、Spec Kit の依存順タスクリストなど）にだけ表出させる |
| 4ルールすべて | 参考文献 | 本書 §6 |

残っているのは、いずれの分類にも当たらないもの — **非自明で、判断を変え、他のどこにも存在しない**記述だけである。

#### 補足 — ルール `clarifier.md` とスキル `clarify-intent` は責務が異なる

ルール `clarifier.md`（Requirements Certainty）が定めるのは、**いつコミットしてよいか**の判定基準である
——重大な結果ギャップが残るなら着手前に解消せよ、という常時適用の不変条件。一方スキル `clarify-intent` が持つのは、
**その解消をどう実行するか**の手順である——AIが理解を言語化して突き合わせ、名前のある枠組みから判断基準を引き、
合意を共通認識メモに残す。合意を形式的要件へ変換する後半は、2026-11-10 にスキル `specify-requirements` へ移った。

2026-11-10 まで、スキルの名前もルールと同じ `clarifier` だった。[ADR-0015](adr/0015-rule-layer-independence.md) のルール層独立原則により、
ルールがスキルを名指しできず、スキル側の拡張に追随して改名する経路も持たなかったためである。作り直しでスキルの名前を
「動詞-対象」の形にそろえたので、同名による取り違えはなくなった。ルールは判定、スキルは手順である。

#### 補足 — `pyramid-principle.md` とスキル `structure-document` の分担

会話の回答の構成（答えを先に置く、前提と用語を示す、支えを下に組む）は、ルール `pyramid-principle.md` だけが受け持つ。
スキル `structure-document` は、文書を書く・直す・レビューするときにだけ読み込まれ、検査スクリプトと、会話を見ていない
サブエージェントによる読み直しを受け持つ。

2026-11-10 まで、スキル（当時の `pyramid-structure`）は「実質的な作業のすべて」で読み込む定めだった（spec 055、057）。
これを文書に絞ったのは、回答のたびにスキルの本文を読み込み、検査スクリプトを実行する費用を、会話では払わないためである。
会話を見ていないサブエージェントによる読み直しは、約 490 行の文書で1回 11万〜12万トークンを使った（`harness-zero-base.md` §4.3 d）。
この読み直しは、文書が会話の外に出るときにだけ行う。

### 3.2 常時ロードから条件付きスキルへ移した3ファイル

以前はルールが8ファイルあった。次の3件は全セッション共通のユニバーサルな判断基準ではなく、特定の作業が発生したときだけ必要な条件付き手順だったため、常時ロードの対象から外した。

| 旧ファイル | 移動先・置き換え先 | 理由 |
|---|---|---|
| `rules/git-workflow.md` | `harness/skills/manage-git/SKILL.md`（移した時点の名前は `git-workflow`） | ブランチ・コミット・push・PR の作業は Git 協業が発生するときだけの条件付き手順で、全セッションに課金する理由がない |
| `rules/mcp.md` | `harness/skills/research-aws/SKILL.md`（移した時点の名前は `aws-research`） | サーバー選択と AWS スキルレジストリ手順も、クラウド提供元の現行ドキュメントが要る条件付き調査であり、同様の理由で移した |
| `rules/skill-routing.md` | 削除（復元先なし） | 中央ルーティング表はスキルの `description` と重複する第二の状態で、スキル境界が変わるたびにドリフトしていた。apex 内の汎用マルチマッチ不変条件と、各スキル自身の記述に置き換えた |

移動した2件は、移動先スキル自身が「いつ呼ぶか」を `description` で自己記述する。削除した1件は、その自己記述の仕組みそのものに置き換わっている。経緯と却下した代替案は [ADR-0015](adr/0015-rule-layer-independence.md) にある。

### 3.3 廃止したルールと、サブエージェントへの委任

`rules/model-routing.md`（作業の単位ごとに、モデルの能力層と推論の労力を選ぶルール）は、利用者が不要と判断し、[spec 058](../specs/058-parent-skill-references/spec.md) で削除した。移動先はなく、戻すときは Git の履歴から復元する。

2026-11-07、利用者がトークン使用料の節約と処理の高速化を求めたため、サブエージェント（メインの会話から起動され、別の文脈で作業して結果だけを返す Claude）への委任の指示を、ルールのファイルではなく `CLAUDE.md` の「Execute under control」の1項目として加えた。その時点では、委任する作業の種類ごとに `haiku` か `sonnet` を名指しし、モデルと effort を、Claude が Agent ツールを呼ぶときの引数で渡す方式だった。エージェントの定義ファイルは置かなかった。会話の記録に、`model` の指定なしに起動されてメインの会話と同じモデルで動いたサブエージェントが見つかったら、定義を置く方式に移る、と定めていた。

2026-11-10、利用者の決定により、定義を置く方式に移った。その例が見つかったからではない。理由は3つある。

- 組み込みの検索用サブエージェント Explore が、メインの会話のモデルで動くようになった [3]。モデルの引数を渡し忘れた検索は、小型のモデルではなくメインのモデルで動く。
- 定義ファイルは、指示文と違って、使える道具の制限を強制できる。
- Anthropic の指針は、サブエージェントの効用を、文脈の分離と並行と独立した読み手に限り、答えの質は上がらないとしている [2]。常設の「委任せよ」という指示は、モデルが変わるたびに見直す項目に挙げられている。

現在の項目は、次の4点を決めている。

- **委任してよい条件は3つである。** 出力が長く結果だけが要る（テスト、ビルド、lint、広い範囲の検索）、互いに独立で並行できる、書いた本人から独立した読み手が要る。どれにも当たらないときは、メインの会話が自分で行う。サブエージェントは空の文脈から始まるので、小さな変更1件や出力の短い確認を委任すると、自分で行うより費用がかかる。
- **モデル、effort、道具は、作業の種類ごとの定義ファイルが固定する。** apex はモデルの名前もサブエージェントの名前も挙げない（検査 APEX-12）。定義は `harness/agents/` に4件ある。

  | 定義 | 条件 | モデルと effort | 道具 |
  |---|---|---|---|
  | `check-runner` | 出力の長い検査を実行する | haiku、low | Bash、Read、Grep、Glob。`CLAUDE.md` を読み込まない |
  | `file-searcher` | 広い範囲を検索する | haiku、medium | Read、Grep、Glob。`CLAUDE.md` を読み込まない |
  | `task-worker` | 判断を要する独立した作業を並行で行う | sonnet、xhigh | 制限なし。`CLAUDE.md` を読み込む |
  | `read-only-reviewer` | 独立したレビュー（[spec 070](../specs/070-review-integrity/problem.md)） | sonnet、xhigh | Read、Grep、Glob。`CLAUDE.md` を読み込まない |

- **同じファイルへの書き込みを、複数のサブエージェントに並行させない。**
- **判断、設計、コードレビュー、作業が完了したかの判定はメインの会話のモデルに残す。** サブエージェントが確認のコマンドを実行してもよいが、実行した各コマンドとその終了コードを報告させ、失敗した出力は原文のまま引用させる。完了は、メインの会話のモデルがその報告から判定する。小型のモデルが出力を誤って要約しても、メインの会話のモデルがその要約を根拠に完了と判定しないようにするためである。

利用者に求められるのを待たずに委任する、という点は 2026-11-07 から変わらない。Claude Code の既定のシステムプロンプトは、利用者が求めない限りサブエージェントを起動しないよう指示している（2.1.319 で確認）。`CLAUDE.md` の指示はこの既定より優先されるため、この項目が既定を上書きする。

メインの会話の effort（推論の深さとトークンの消費量を決める水準。low, medium, high, xhigh, max がある）は、`harness/settings.json` で `xhigh` に固定した。effort を課題ごとに自動で切り替える設定はなく、何も設定しないとモデルの既定値で動く（Opus 5.5 は `medium`）[4]。最上位の `effortLevel` は、ユーザー設定に書いた場合、Opus 5.5 には適用されない [4]。このため 2026-11-10 に、`modelSettings`（モデルごとの設定）にも Opus 5.5 の `xhigh` を加えた。環境変数 `CLAUDE_CODE_EFFORT_LEVEL` やセッション中の指定は、さらに優先される [4]。

サブエージェントのモデルは、呼び出しのときに渡す `model` の指定、エージェントの定義の `model` 欄、環境変数 `CLAUDE_CODE_SUBAGENT_MODEL`、呼び出し元の会話のモデルの順で決まり、先に挙げたものほど優先される [3]。

## 4. 番号ではなく名前で参照する

`CLAUDE.md` の原則は「Core Principle #3」のような番号ではなく **Traceability のように名前で** 参照する。原則を 1 つ足せば番号参照は全て壊れるためで、実際に Traceability は #3 から #4 へ動いた。`specs/` 配下の過去の記録は当時の番号と当時のスキル名のまま残してある（当時の事実の記録であり、遡及修正の対象ではない）。

## 5. 変更するとき

構成は `CLAUDE.md` を唯一の頂点とする独立ピラミッドとして保つ。各層は**意味**でのみ親の主張を支え、名前やパスで他ノードを名指ししない（唯一の例外は下の親スキル）。第2層は4個のユニバーサルルール（品質の関心事1つにつき1ファイル）、第3層はスキルである。スキルは `SKILL.md` の前付けの `metadata.kind` で型を宣言する。作業（`worker`）は何かを作るか変える。オーバーレイ（`overlay`）は、一致する作業に**追加で**適用する判断基準であり、置き換えではない。親スキル（`orchestrator`）は、宣言した子スキルを決まった順に適用する。第3層の分類がなぜルールへの1対1対応ではないのかは [ADR-0015](adr/0015-rule-layer-independence.md) にある。

| 層 | 依存できる上位層 | 分類原理 | 許可する参照 | 禁止する参照 |
|---|---|---|---|---|
| `harness/CLAUDE.md`（1件） | なし | ライフサイクル段階（定義→実行→引き渡し） | なし | ルール・スキル・サブエージェント・コマンド・サーバーいずれの個別名も、モデルの名前も不可 |
| `harness/rules/*.md`（4件） | `CLAUDE.md` | 品質の関心事1つにつき1ファイル | なし（参考文献は本書 §6） | 他のルールのファイル名・パス・それと分かる言及、スキルへの名指し |
| `harness/skills/*/SKILL.md`（17件） | `CLAUDE.md` と、自身が支える品質の関心事 | 型（作業、オーバーレイ、親スキル） | 自身のパッケージ内リソース（`references/`、スクリプト等）、外部一次情報源、サブエージェントの定義の名前。親スキルに限り、自身の `SKILL.md` で宣言した子スキルの名前 | 他スキルへの名指し（親スキルが宣言した子を除く）・パス参照、インストール先のパスのハードコード、このリポジトリの `specs/` と `archive/` の参照(インストール先にないため) |

スキルの層の定めは、`tests/assert_skill_contract.py` が、`harness/skills/` にあるすべてのスキルに対して検査する（契約 C-01〜C-11）。対象は、ディレクトリから読み取る。2026-11-10 までは、検査の対象を `tests/run-config-pyramid.sh` の中の手書きの一覧に列挙しており、17 件のうち 13 件しか載っていなかった。契約の各規則が違反を実際に検出することは、`tests/test_skill_contract.py` が、一時ディレクトリに作る架空のスキルで確かめる。

**親スキルは、宣言した子スキルを名前で参照できる**（[spec 058](../specs/058-parent-skill-references/spec.md)）。親スキルは、複数のスキルを決まった順序で適用する取りまとめ役のスキルである。`SKILL.md` に `## Child skills` 節を置き、子を1行に1つ「- `名前`」の形で宣言する。契約 C-08 は、パッケージ内の Markdown が、宣言した子以外のスキルを名指しすると失敗する。契約 C-11 は次を確かめる: 親は子を2つ以上宣言する。子は実在し、自分が親スキルではない（階層は1段）。親スキル以外は子を宣言しない。現在の親スキルは `deliver-change` の1件で、子は `define-problem`、`specify-requirements`、`implement-change`、`verify-change` である。

この例外は、[ADR-0015](adr/0015-rule-layer-independence.md) が却下した「下向き参照と中央ルーターを許可する案」とは別物である。ADR-0015 の却下理由は2つあった。発見の情報（どのスキルをいつ使うか）を二重に管理すること、スキルの追加や改名のたびに常時ロードの設定を変えることである。親スキルはどちらにも当たらない。親スキルは常時ロードではなく、条件付きで読み込まれる。子がいつ呼ばれるかは、引き続き子自身の `description` が決め、親が持つのは自分の手順の中で子を使う順序だけである。子を改名して壊れるのは、その子を宣言した親だけで、契約 C-11 がそれを見つける。ただし ADR-0015 の「参照境界」節（設定ノードは上位・下位・横の別ノードを名前やパスで参照しない）は、スキル層ではもう成り立たない。ADR-0015 の本文は変えていない。

スキルは、Claude Code のサンドボックスの中で動くことも契約にしている（C-04、C-07）。一時ファイルは `$TMPDIR` の下に作る。リポジトリの外へ書く手順は `$TMPDIR` を指定する。ネットワークが要るスキルは、必要なホストを `metadata` に宣言する。理由と、確かめた制約は `harness-zero-base.md` §6.8 にある。

同一階層にしかない情報が必要になったら、参照を足すのではなく、次のどちらかを行う。

1. そのファイル自身の判断基準として短く言い直す。
2. 複数の子が共有すべき内容なら、共通の親へ引き上げる。

設定ファイルに文を足す前に §2 の問いを通す。説明を書きたくなったら、それは本書か、対応する `docs/` の解説か、ADR に属する。新しいルールを作って設計理由を常時ロードさせない。

サイズの目安は公式指針の 1 ファイル 200 行未満 [2]。頂点の方針と4ルールの合計は、検査 BUDGET-01 が 16,000 バイト未満であることを確かめる（2026-11-10 の時点で 15,404 バイト）。16,000 は spec 035 が定めた目標である。それまでの上限 20,126 バイトは、ルールが8ファイルあった時期の大きさで、再増加を検出できなかった。

この依存方向、対象範囲、却下した代替案は [ADR-0015](adr/0015-rule-layer-independence.md) に記録する。

## 6. ルールの参考文献

ルールの各節が拠る資料である。2026-11-10 まで、各ルールの末尾にあった（§2）。括弧の中は、その資料が支えるルールの節の名前である。

### `clarifier.md`（Requirements Certainty）

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* — the international standard for eliciting, analyzing, validating, and managing requirements that this rule's material-gap test operationalizes: <https://www.iso.org/standard/72089.html>
- Barry W. Boehm, *Software Engineering Economics*, Prentice-Hall, 1981 — the empirical basis for resolving a material gap before committing rather than after: cost-to-fix escalates roughly an order of magnitude at each later lifecycle stage.

### `permissions.md`（Authorization and Safety）

- Jerome H. Saltzer and Michael D. Schroeder, “The Protection of Information in Computer Systems,” *Proceedings of the IEEE* 63(9), 1975 — least privilege, fail-safe defaults, and complete mediation: <https://www.cs.virginia.edu/~evans/cs551/saltzer/>

### `pyramid-principle.md`（Reader-Facing Structure）

- Barbara Minto, *The Minto Pyramid Principle*, 1987.
- International Committee of Medical Journal Editors, *Recommendations*, "Preparing a Manuscript for Submission to a Medical Journal" — original research is divided into Introduction, Methods, Results, and Discussion (Parts): <https://icmje.org/recommendations/browse/manuscript-preparation/preparing-for-submission.html>
- L. B. Sollaci and M. G. Pereira, "The introduction, methods, results, and discussion (IMRAD) structure: a fifty-year survey," *Journal of the Medical Library Association* 92(3), 2004 (Parts).
- 木下是雄『理科系の作文技術』中公新書, 1981 — putting the main point first, and the topic sentence that opens each paragraph (Parts).
- ISO 24495-1:2023, *Plain language — Part 1: Governing principles and guidelines* — principle 3, readers can easily understand what they find, and its guideline 5.3.2, choose familiar words (Premises and terms).
- R. J. Spiro et al., "Multiple analogies for complex concepts: antidotes for analogy-induced misconception in advanced knowledge acquisition," in S. Vosniadou and A. Ortony (eds.), *Similarity and Analogical Reasoning*, Cambridge University Press, 1989 — a single analogy leads learners to carry properties of the source into the subject where they do not hold (Premises and terms).

### `thinking-lenses.md`（Reasoning Completeness）

- C. Böhm and G. Jacopini, "Flow diagrams, Turing machines and languages with only two formation rules," *Communications of the ACM* 9(5), 1966 — proves sequence, selection, and iteration are the complete, sufficient set of control structures (Dependencies and concurrency; Conditions and branches; Iteration).
- J. E. Kelley Jr. and M. R. Walker, "Critical-Path Planning and Scheduling," *Proceedings of the Eastern Joint Computer Conference*, 1959 — the origin of distinguishing a true prerequisite from independently schedulable work (Dependencies and concurrency).
- Barbara Minto, *The Minto Pyramid Principle*, 1987 — MECE branch partitioning and the deductive/inductive distinction in argument structure (Conditions and branches; Inference).
- Karl Popper, *The Logic of Scientific Discovery*, 1959 — falsifiability as the standard an inductive conclusion must meet rather than overclaiming certainty (Inference).

## References

1. Claude Code — How Claude remembers your project: <https://code.claude.com/docs/en/memory>
2. Claude Code — Best practices: <https://code.claude.com/docs/en/best-practices>
3. Claude Code — Create custom subagents, "Choose a model": <https://code.claude.com/docs/en/sub-agents>
4. Claude Code — Model configuration, "Adjust effort level": <https://code.claude.com/docs/en/model-config#adjust-effort-level>
