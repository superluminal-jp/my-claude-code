---
status: Proposed
date: 2026-11-18
deciders: Taiki Ogihara
---

# 0029. 変更の引き渡しの基盤を AI-DLC Workflows v2 にし、harness はその補完に絞る

## コンテキストと問題

harness は、変更を問題の定義から受け入れの判定まで運ぶ手順を、自前のスキル（`deliver-change` と、その子の `define-problem`、`specify-requirements`、`implement-change`、`verify-change`）で持っている。要素の置き場所は、Scrum の役割と作業の枝の木である（[ADR-0026](0026-place-skills-and-agents-in-a-scrum-role-tree.md)）。次に進む段階を決めるのはモデルで、段階の状態と監査の記録を保つ仕組みは、スキルごとのゲートのスクリプトだけである。

AWS は AI-DLC Workflows の 2.x 系（以下 AI-DLC v2）を公開している。2026-11-18 に `awslabs/aidlc-workflows` の `main`（コミット `e67406f`）を読んで確かめた事実は次のとおりである。

- 最新の安定版は v2.11.4（2026-11-13）、ライセンスは MIT-0。
- 5つのフェーズ（Initialization、Ideation、Inception、Construction、Operation）に33のステージがあり、11のスコープ（`classic`、`feature`、`bugfix` など）が実行するステージを選ぶ（`harness/claude/settings.json`、`docs/guide/05-scopes-and-depth.md`）。
- 次のステージを決めるのは `aidlc` という実行ファイル（エンジン）で、モデルではない。状態と監査の記録は、プロジェクトの `aidlc/spaces/<space>/intents/<intent-id>/` に残る。
- 導入はプロジェクト単位である。`aidlc config --harness claude` が、プロジェクトの `.claude/`（`/aidlc` スキル、エージェント14件、ステージ、フック）と `aidlc/` を書く。`~/.claude/` に入れる方法は文書にない。
- プロジェクトの `.claude/settings.json` に、フック（`PreToolUse`、`PostToolUse`、`UserPromptSubmit`、`SessionStart`、`SessionEnd`、`PreCompact`、`SubagentStart`、`SubagentStop`、`Stop`）と、`Edit(/**)`、`Task`、`WebSearch`、エンジンの Bash コマンドの事前許可を書く。
- Claude Code の Bash サンドボックスの中で動くコマンドを想定した記述がある（`docs/guide/03-spaces-and-intents.md`、`SANDBOX_RUNTIME=1`）。
- 任意で、MCP サーバー5件（`context7`、`aws-mcp`、`aws-pricing`、`aws-iac`、`aws-serverless`）を `.mcp.json` に書く。
- 読んだ文書に、Scrum と Sprint の語はない。

利用者は 2026-11-18 に「AI-DLC V2をベースにするように刷新できるか」と尋ね、示した3つの案から B（公式ツールを実行基盤にし、harness は重複するスキルを削って補完だけにする）を選んだ。

## 決定

この記録は案である。「利用者が決めた」と書いていない点は、実装者の提案であり、利用者の承認を待つ。

1. **AI-DLC v2 を、変更の引き渡しの基盤にする。**（利用者が決めた）公式の `aidlc` をプロジェクトごとに導入して使う。公式のファイルを `harness/` に写さない。
2. **harness から、AI-DLC v2 のステージと重なるスキルを除く。** 対象は `deliver-change`、`specify-requirements`、`verify-change`、`define-product-strategy` の4件とする。対応するステージは、順に、ワークフロー全体、Requirements Analysis と User Stories、Build and Test と各ステージのレビュー、Ideation である。除いたものは `archive/` に移す。
3. **次のスキルは残す。** AI-DLC v2 に同じ役目のものがないか、ステージの中で重ねて使えるためである。
   - `implement-change`（Code Generation の中で使うテストファーストの手順）
   - `define-problem`、`clarify-intent`（ワークフローの外でも使う）
   - `manage-git`、`sync-docs`、`structure-document`、`draw-system-diagrams`、`research-aws`、`apply-secure-logging`、`apply-dads-frontend`、`build-dads-slides`
   - `apply-scrum-guide`、`manage-scrum-artifacts`、`scrum-master-agent`（Scrum の作成物があるリポジトリのためのもの）
4. **木を、Scrum の役割の木から AI-DLC v2 のフェーズの木に置き換える。** `metadata.role` と `metadata.branch` に代えて、要素が支えるフェーズ（`ideation`、`inception`、`construction`、`operation`、またはフェーズをまたぐ `cross-phase`）を宣言し、`description` の末尾の標識もフェーズにする。ADR-0026 は「Superseded by 0029」にする。
5. **`harness/CLAUDE.md` とルールは、AI-DLC v2 が導入されたプロジェクトでは、ステージの進行と承認をエンジンに委ねると述べる。** 導入の有無は、プロジェクトのルートの `.aidlc-version` で見分ける。導入されていないプロジェクトでは、今の「定める、実行する、引き渡す」の指示がそのまま働く。
6. **`harness/settings.json` を、エンジンが Bash サンドボックスの中で動くように調整する。** 必要な項目は試行で確かめてから決める。拒否の規則（認証情報の読み取り）は緩めない。
7. **`install.sh` は `aidlc` を導入しない。** 取得したインストーラーを利用者の機械で走らせることになるためである。導入の手順は README に書く。
8. **MCP サーバーの許可リスト（[ADR-0021](0021-block-mcp-servers-by-settings.md)）は変えない。** AI-DLC v2 の任意の MCP サーバーは、`--mcp none` で入れない。
9. **対象のフェーズは Ideation から Construction までとする。** Operation のための要素は、この変更では足さない。

## 検討した選択肢

- **A. 考え方だけ採る**: 役割の木をフェーズの木に組み替え、自前のスキルを残す。全プロジェクトで働き、既存の決定との衝突は少ない。エンジンと監査の記録は得られない。利用者は B を選んだ。
- **C. 公式のファイルを `harness/` に取り込む**: 全プロジェクトで働く。上流はプロジェクト単位の導入しか述べておらず、フックが `$CLAUDE_PROJECT_DIR` の下の道具を呼ぶので、利用者レベルで動く保証がない。上流は数日ごとに版を出しており、写しは古くなる。
- **重なるスキルを残し、AI-DLC v2 がないプロジェクトでだけ使わせる**: 導入していないプロジェクトで今の手順を失わない。同じ役目の手順を2つ保守することになり、B の「補完だけにする」に反する。
- **`install.sh` で `aidlc` も入れる**: 導入が1回で済む。取得したコードを承認なしに実行する経路を、インストーラーに足すことになる。

## 結果

- スキルは17件から13件になる。`deliver-change` を前提にする検査（`tests/assert_delivery_flow.py`、`tests/assert_assurance_parity.py`、`tests/run-specify-requirements-skill.sh`、`tests/run-verify-change-skill.sh` など）と評価のシナリオは、除くか書き換える。
- AI-DLC v2 を導入していないプロジェクトでは、要件グラフと検証の記録によるゲートがなくなる。このリポジトリ自身も `specs/` の手順を失うので、このリポジトリに AI-DLC v2 を導入するかどうかを別に決める必要がある。
- `read-only-reviewer` の用途（要件の反証、保証レビュー）は、呼び出すスキルがなくなる。残すか除くかを実装の中で決める。
- 両方の README、`docs/claude-config-design.md`、`docs/harness-eval.md`、`docs/harness/`、`claude-ai-system-prompt.md`、`chatgpt-system-prompt.md` を更新する。
- AI-DLC v2 のフックは、すべての道具の呼び出しの前後で走る。応答の時間と、harness のフックとの相互作用は測っていない。

## 確認方法

受け入れ基準は次のとおりである。番号は、後で作る要件グラフの識別子の元にする。

- **AC-1**: 空の Git リポジトリに `aidlc config --harness claude --mcp none --yes` を実行し、`install.sh` で入れた harness の設定の下で `aidlc doctor` が終了コード0で終わる。
- **AC-2**: 同じリポジトリで、サンドボックスを有効にしたまま、`bugfix` スコープのワークフローが最初の承認ゲートまで進み、`aidlc/spaces/` に状態と監査の記録が残る。サンドボックスの外での再実行を求められない。
- **AC-3**: `harness/skills/` に `deliver-change`、`specify-requirements`、`verify-change`、`define-product-strategy` がなく、残りのスキルとエージェントの本文がそれらを名指さない。
- **AC-4**: `python3 tests/assert_role_tree.py` と `--self-test` が、フェーズの宣言、標識、README の表、図の一致を確かめて通る。
- **AC-5**: `bash tests/run-harness-skills.sh`、`bash tests/run-install.sh`、`bash tests/run-sandbox-settings.sh` が通る。
- **AC-6**: `harness/settings.json` の `permissions.deny` と `sandbox.filesystem.denyRead` が、変更の前の項目をすべて含む。
- **AC-7**: AI-DLC v2 を導入していないリポジトリで、harness のフックと指示が `aidlc` を呼ばず、エラーを出さない。
- **AC-8**: `README.md` と `README.ja.md` が、AI-DLC v2 の導入の手順、対象の版、harness が補う範囲を述べ、互いに一致する。

確かめていないことは次のとおりである。

- `aidlc` をまだ実行していない。AC-1 と AC-2 が成り立つか、サンドボックスにどの項目が要るかは未検証である。
- 公式サイト（`awslabs.github.io`）と仕様書の PDF は読んでいない。
- harness のルール（着手前に尋ねる、答えを先に書く）と、AI-DLC v2 のステージごとの問いと承認が、1つの会話でどう重なるかは観測していない。

## 補足情報

- AI-DLC Workflows: <https://github.com/awslabs/aidlc-workflows>（`main`、`e67406f`、2026-11-18 に読んだ）
- [ADR-0015](0015-rule-layer-independence.md): 設定の層が互いを名指さない決まり。AI-DLC v2 は harness の層ではないので、導入の有無を見分ける記述はこの決まりに触れない。
- [ADR-0020](0020-enable-sandbox-by-default.md)、[ADR-0021](0021-block-mcp-servers-by-settings.md): サンドボックスと MCP サーバーの決定。この記録は、どちらも保つ。
- [ADR-0025](0025-ai-as-developer-scrum-master-as-subagent.md)、[ADR-0026](0026-place-skills-and-agents-in-a-scrum-role-tree.md): Scrum の役割についての決定。この記録は 0026 を置き換え、0025 は Scrum の作成物があるリポジトリのために残す。
