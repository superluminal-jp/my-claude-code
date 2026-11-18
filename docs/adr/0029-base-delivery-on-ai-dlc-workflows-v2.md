---
status: Accepted
date: 2026-11-18
deciders: Taiki Ogihara
---

# 0029. 変更の引き渡しの基盤を AI-DLC Workflows v2 にし、harness はその補完に絞る

## コンテキストと問題

変更の前、harness は、変更を問題の定義から受け入れの判定まで運ぶ手順を、自前のスキル（`deliver-change` と、その子の `define-problem`、`specify-requirements`、`implement-change`、`verify-change`）で持っていた。要素の置き場所は、Scrum の役割と作業の枝の木だった（[ADR-0026](0026-place-skills-and-agents-in-a-scrum-role-tree.md)）。次に進む段階を決めるのはモデルで、段階の状態と監査の記録を保つ仕組みは、スキルごとのゲートのスクリプトだけだった。

AWS は AI-DLC Workflows の 2.x 系（以下 AI-DLC v2）を公開している。2026-11-18 に `awslabs/aidlc-workflows` の `main`（コミット `e67406f`）を読み、v2.11.4 を試して確かめた事実は次のとおりである。

- 最新の安定版は v2.11.4（2026-11-13）、ライセンスは MIT-0。
- 5つのフェーズ（Initialization、Ideation、Inception、Construction、Operation）に33のステージがあり、11のスコープ（`classic`、`feature`、`bugfix` など）が実行するステージを選ぶ。
- 次のステージを決めるのは `aidlc` という実行ファイル（エンジン）で、モデルではない。状態と監査の記録は、プロジェクトの `aidlc/spaces/<space>/intents/<intent-id>/` に残る。
- 導入はプロジェクト単位である。`aidlc config --harness claude` が、プロジェクトの `.claude/`（スキル43件、エージェント14件、ステージ、フック）と `aidlc/` を書く。`~/.claude/` に入れる方法は文書にない。
- プロジェクトの `.claude/settings.json` に、9種類のフック（`PreToolUse`、`PostToolUse`、`UserPromptSubmit`、`SessionStart`、`SessionEnd`、`PreCompact`、`SubagentStart`、`SubagentStop`、`Stop`）と、`Edit(/**)`、`Task`、`WebSearch`、`Bash(aidlc engine *)` などの事前許可を書く。
- エンジンは、Claude Code がフックを実行していないプロジェクトでは、ワークフローを進めない。
- 任意で、MCP サーバー5件（`context7`、`aws-mcp`、`aws-pricing`、`aws-iac`、`aws-serverless`）を `.mcp.json` に書く。
- 読んだ文書に、Scrum と Sprint の語はない。

利用者は 2026-11-18 に「AI-DLC V2をベースにするように刷新できるか」と尋ね、示した3つの案から B（公式ツールを実行基盤にし、harness は重複するスキルを削って補完だけにする）を選んだ。続いて、実装者が示した7つの提案を承認し、`aidlc` をクラウドのコンテナで試すことを許した。

## 決定

1 は利用者が選び、2 から 9 は実装者が提案して利用者が承認した。10 は実装の中で実装者が決めた。

1. **AI-DLC v2 を、変更の引き渡しの基盤にする。** 公式の `aidlc` をプロジェクトごとに導入して使う。公式のファイルを `harness/` に写さない。
2. **harness から、AI-DLC v2 のステージと重なるスキルを除く。** 対象は `deliver-change`、`specify-requirements`、`verify-change`、`define-product-strategy` の4件である。対応するステージは、順に、ワークフロー全体、Requirements Analysis と User Stories、Build and Test と各ステージのレビュー、Ideation である。除いたものは、それだけを確かめていた検査とともに `archive/delivery-gates/` に移した。
3. **次の要素は残す。** AI-DLC v2 に同じ役目のものがないか、ステージの中で重ねて使えるためである。
   - `implement-change`（Code Generation の中で使うテストファーストの手順）
   - `define-problem`、`clarify-intent`（ワークフローの外でも使う）
   - `manage-git`、`sync-docs`、`structure-document`、`draw-system-diagrams`、`research-aws`、`apply-secure-logging`、`apply-dads-frontend`、`build-dads-slides`
   - `apply-scrum-guide`、`manage-scrum-artifacts`、`scrum-master-agent`（Scrum の作成物があるリポジトリのためのもの）
4. **木の第1段を、Scrum の役割から AI-DLC v2 のフェーズに置き換える。** 各要素は `metadata.role` に代えて `metadata.phase` を宣言する。値は `ideation`、`inception`、`construction`、`operation` と、どのフェーズにも結び付かない `cross-phase` である。`description` の末尾の標識は `[<フェーズ> / <枝>]` にする。第2段の枝（`metadata.branch`）と、枝をまたぐ要素の `metadata.stage` は残す。枝は `harness/CLAUDE.md` の節であり、Scrum に由来しないためである。ADR-0026 は「Superseded by 0029」にした。
5. **`harness/CLAUDE.md` は、AI-DLC v2 を使うプロジェクトでは、ステージの順とゲートをエンジンに委ねると述べる。** 見分ける手がかりは、プロジェクトのルートの `aidlc/` ディレクトリである。モデルは、人に代わってゲートを承認せず、ステージを進めない。導入されていないプロジェクトでは、今の「定める、実行する、引き渡す」の指示がそのまま働く。
6. **`harness/settings.json` は変えない。** 試行で、エンジンの最初の一歩は、プロジェクトと `$TMPDIR` の外に書かず、ネットワークにも出なかった。足すべき項目は見つかっていない。拒否の規則（認証情報の読み取り）もそのままである。
7. **`install.sh` は `aidlc` を導入しない。** 取得したインストーラーを利用者の機械で走らせることになるためである。導入の手順は README に書く。
8. **MCP サーバーの許可リスト（[ADR-0021](0021-block-mcp-servers-by-settings.md)）は変えない。** AI-DLC v2 の任意の MCP サーバーは、`--mcp none` で入れない。
9. **対象のフェーズは Ideation から Construction までとする。** Operation のための要素は、この変更では足さない。このリポジトリ自身に AI-DLC v2 を導入するかどうかは、別に決める。
10. **`read-only-reviewer` は、作者から独立した読み手として残す。** 起動させていた2つの手順（要件の反証、保証レビュー）はなくなったので、`description` を、作者から独立した読み手が要るときに使う、と書き換えた。`harness/CLAUDE.md` の委任の条件の1つが、その読み手を求めているためである。

## 検討した選択肢

- **A. 考え方だけ採る**: 役割の木をフェーズの木に組み替え、自前のスキルを残す。全プロジェクトで働き、既存の決定との衝突は少ない。エンジンと監査の記録は得られない。利用者は B を選んだ。
- **C. 公式のファイルを `harness/` に取り込む**: 全プロジェクトで働く。上流はプロジェクト単位の導入しか述べておらず、フックが `aidlc` をプロジェクトの記録に対して呼ぶので、利用者レベルで動く保証がない。上流は数日ごとに版を出しており、写しは古くなる。
- **重なるスキルを残し、AI-DLC v2 がないプロジェクトでだけ使わせる**: 導入していないプロジェクトで今の手順を失わない。同じ役目の手順を2つ保守することになり、B の「補完だけにする」に反する。
- **`install.sh` で `aidlc` も入れる**: 導入が1回で済む。取得したコードを承認なしに実行する経路を、インストーラーに足すことになる。
- **枝も除き、フェーズと要素の2段の木にする**: 木は浅くなる。枝と段階の整合（`tests/assert_role_tree.py` の BRANCH と STAGE）を確かめる検査を失う。
- **検査と図のファイル名も `phase-tree` に変える**: 名前と中身が合う。`tests/assert_role_tree.py`、`docs/harness/skill-map/03-role-tree.md`、README の目印を指す文書と検査をすべて変えることになるので、名前は残した。

## 結果

- スキルは17件から13件になった。サブエージェントの定義は5件のままである。
- 除いたスキルだけを確かめていた検査（`tests/run-specify-requirements-skill.sh`、`tests/run-verify-change-skill.sh`、`tests/assert_assurance_parity.py`、`tests/assert_delivery_flow.py`、`tests/assert_review_prep_flow.py`）は、CI から外して `archive/delivery-gates/tests/` に移した。サブエージェントの定義の検査（`tests/assert_reviewer_agent.py`）は、手順が定義を名指すことの確認を除き、`tests/run-harness-skills.sh` から実行する。
- 対応表（`docs/harness/capability-map.json`）から、段階 `D-product` と `D-decompose` を除いた。評価のシナリオは、`d-product-direction`、`d-decompose-agreed`、`h-verify-evidence` を除き、除いたスキルを判定に使っていた項目を、残るスキルの項目に替えた。
- スキルの契約（`tests/assert_skill_contract.py`）の C-04 は `metadata.phase` を確かめる。C-08 が `metadata.role` の値だけを名前に数えなかった例外は、なくした。
- AI-DLC v2 を導入していないプロジェクトでは、要件グラフと検証の記録によるゲートがなくなる。このリポジトリ自身も、`specs/` の手順を進めるスキルを失った。
- AI-DLC v2 のフックは、すべての道具の呼び出しの前後で走る。応答の時間と、harness のフックとの相互作用は測っていない。
- 一覧（`description`）が変わるので、スキルの選ばれ方が変わる可能性がある。測っていない。
- Claude.ai に上げた写しは古いまま残る。
- `install.sh` を次に実行するまで、`~/.claude/` には反映されない。次の実行で、除いた4つのスキルは `~/.claude/skills/` から消える。

## 確認方法

- **AC-1（一部を確かめた）**: クラウドのコンテナ（Linux、root）で、公式の `install.sh` が来歴の検証（`gh attestation verify`）を通して v2.11.4 を入れた。空の Git リポジトリで `aidlc config --harness claude --mcp none --yes` と `aidlc doctor` が、どちらも終了コード0で終わった（問題0件、警告3件）。harness を `~/.claude/` に入れた状態では試していない。
- **AC-2（確かめていない）**: サンドボックスを有効にした Claude Code の会話で、`bugfix` スコープのワークフローが最初の承認ゲートまで進むこと。確かめたのは、`aidlc engine hook session-start` と `aidlc engine orchestrate next --scope bugfix` を `strace` で追い、プロジェクトと `$TMPDIR` の外への書き込みが、フックによる `~/.bun/install/cache` の作成だけで、ネットワークへの接続がないことまでである。エンジンは、フックが動いていないので進めないと答えた。利用者が、自分の機械で確かめる。
- **AC-3**: `harness/skills/` に4つのスキルがない（`tests/run-config-pyramid.sh` の SKILL-09）。残りのスキルとエージェントの本文は、それらを名指さない。
- **AC-4**: `python3 tests/assert_role_tree.py` と `--self-test` が、フェーズの宣言、標識、README の表、図の一致を確かめて通る。
- **AC-5**: `bash tests/run-harness-skills.sh`、`bash tests/run-config-pyramid.sh`、`bash tests/run-install.sh`、`bash tests/run-harness-eval.sh` が通る。`bash tests/run-sandbox-settings.sh` と `bash tests/run-commit-tree-hook.sh` は、変更の前と同じ項目（GPG-02、TREE-05、TREE-06）だけがクラウドのコンテナで失敗する。
- **AC-6**: `harness/settings.json` を変えていない。
- **AC-7**: `harness/CLAUDE.md` の記述は、`aidlc/` があるプロジェクトだけを条件にする（APEX-14、APEX-15）。harness のフックは `aidlc` を呼ばない。
- **AC-8**: `README.md` と `README.ja.md` が、AI-DLC v2 の導入の手順と、harness が補う範囲を述べる。

確かめていないことは、ほかに次のとおりである。

- macOS での動作。試したのは Linux だけである。上流の `main` には、Claude Code の Linux のサンドボックスについての修正（`e67406f`）が v2.11.4 の後に入っている。
- harness のルール（着手前に尋ねる、答えを先に書く）と、AI-DLC v2 のステージごとの問いと承認が、1つの会話でどう重なるか。
- AI-DLC v2 がプロジェクトに書く事前許可（`Edit(/**)` など）と、harness の `permissions.defaultMode`（`auto`）の組み合わせ。
- 公式サイト（`awslabs.github.io`）と仕様書の PDF は読んでいない。

## 補足情報

- AI-DLC Workflows: <https://github.com/awslabs/aidlc-workflows>（`main`、`e67406f`、2026-11-18 に読んだ。試した版は v2.11.4）
- [ADR-0015](0015-rule-layer-independence.md): 設定の層が互いを名指さない決まり。AI-DLC v2 は harness の層ではないので、`harness/CLAUDE.md` がその名を挙げても、この決まりに触れない。
- [ADR-0020](0020-enable-sandbox-by-default.md)、[ADR-0021](0021-block-mcp-servers-by-settings.md): サンドボックスと MCP サーバーの決定。この記録は、どちらも保つ。
- [ADR-0025](0025-ai-as-developer-scrum-master-as-subagent.md)、[ADR-0026](0026-place-skills-and-agents-in-a-scrum-role-tree.md): Scrum の役割についての決定。この記録は 0026 を置き換え、0025 は Scrum の作成物があるリポジトリのために残す。
