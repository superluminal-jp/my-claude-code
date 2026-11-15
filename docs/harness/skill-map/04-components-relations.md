# コンポーネント図: 木の外の関係

この図は、[役割の木](03-role-tree.md)の「属する」以外の関係を描きます。17のスキルは、前付けの `metadata.kind` で3種に分かれます（この枠は種類で、木の中の場所ではありません）。それぞれの関係は次のとおりです。

- **親スキル `deliver-change`**: 子スキル4つを、決まった順で適用します。
- **オーバーレイ3つ**: 一致する作業スキルに、判断基準を重ねます。
- **独立した読み手が要る3つのスキル**: サブエージェントを名指しで起動させます。

残る作業スキル6つは、どれとも上下の関係を持たず、単独で使います。`clarify-intent`、`define-product-strategy`、`structure-document`、`draw-system-diagrams`、`build-dads-slides`、`research-aws` の6つです。

```mermaid
flowchart LR
  accTitle: コンポーネント図: 木の外の関係
  accDescr: 親スキル deliver-change は4つの子スキルを順に適用する。オーバーレイ3つは作業スキルに判断基準を重ねる。specify-requirements と verify-change は read-only-reviewer を、apply-scrum-guide は scrum-master-agent を起動させる。ほかの作業スキルは単独で使う。
  subgraph skills["スキル [コンテナ: harness/skills/]"]
    subgraph kind_orch["親スキル [kind: orchestrator]"]
      deliver_change["deliver-change<br/>[コンポーネント: 親スキル]<br/>合意した問題から受け入れの判断までを4段で進める"]:::component
    end
    subgraph kind_overlay["オーバーレイ [kind: overlay]"]
      apply_scrum_guide["apply-scrum-guide<br/>[コンポーネント: オーバーレイ・読み取り専用]<br/>開発を Scrum の Developer として行う判断を重ねる"]:::component
      apply_secure_logging["apply-secure-logging<br/>[コンポーネント: オーバーレイ]<br/>ログの変更にセキュリティの要件を重ねる"]:::component
      apply_dads_frontend["apply-dads-frontend<br/>[コンポーネント: オーバーレイ]<br/>画面の変更に DADS の基準を重ねる"]:::component
    end
    subgraph kind_worker["作業スキル [kind: worker]"]
      define_problem["define-problem<br/>[コンポーネント: 作業スキル]<br/>問題を現状と理想の差として文にする"]:::component
      specify_requirements["specify-requirements<br/>[コンポーネント: 作業スキル]<br/>問題カードと要件グラフを書き、ゲートを通す"]:::component
      implement_change["implement-change<br/>[コンポーネント: 作業スキル]<br/>失敗する検査から最小の変更を行う"]:::component
      verify_change["verify-change<br/>[コンポーネント: 作業スキル]<br/>受け入れ基準ごとの証拠を記録し、ゲートを通す"]:::component
      sync_docs["sync-docs<br/>[コンポーネント: 作業スキル]<br/>変更が古くする文書を同じ変更で直す"]:::component
      manage_git["manage-git<br/>[コンポーネント: 作業スキル・外部に影響]<br/>頼まれた Git 操作だけを行う"]:::component
      manage_scrum_artifacts["manage-scrum-artifacts<br/>[コンポーネント: 作業スキル]<br/>Scrum の作成物をファイルとして置き、検査する"]:::component
      clarify_intent["clarify-intent<br/>[コンポーネント: 作業スキル]<br/>依頼の読みを明示し、合意を記録する"]:::component
      define_product_strategy["define-product-strategy<br/>[コンポーネント: 作業スキル]<br/>開発の前にプロダクトの方向を定める"]:::component
      structure_document["structure-document<br/>[コンポーネント: 作業スキル]<br/>文書を1つの主張の木に組む"]:::component
      draw_system_diagrams["draw-system-diagrams<br/>[コンポーネント: 作業スキル]<br/>1枚に1つの問いの構成図を描く"]:::component
      build_dads_slides["build-dads-slides<br/>[コンポーネント: 作業スキル]<br/>DADS の素材で HTML のスライドを作る"]:::component
      research_aws["research-aws<br/>[コンポーネント: 作業スキル・読み取り専用]<br/>AWS の主張を公式文書で確かめる"]:::component
    end
  end
  subgraph agents["サブエージェント定義 [コンテナ: harness/agents/]"]
    read_only_reviewer["read-only-reviewer<br/>[コンポーネント: サブエージェント・sonnet・読み取り専用]<br/>作者の推論を見ずに要件と証拠を読む"]:::component
    scrum_master_agent["scrum-master-agent<br/>[コンポーネント: サブエージェント・sonnet・読み取り専用]<br/>Scrum Master として Developer の作業を検査する"]:::component
  end
  deliver_change -->|"1 合意した問題文がなければ、先に問題を定める"| define_problem
  deliver_change -->|"2 要件グラフを書き、ゲートが ready になるまで直す"| specify_requirements
  deliver_change -->|"3 葉の要件ごとに、失敗する検査から実装する"| implement_change
  deliver_change -->|"4 証拠を記録し、ゲートの判断を得る"| verify_change
  specify_requirements -->|"高リスクや証拠が弱いときに、要件の反証を求める"| read_only_reviewer
  verify_change -->|"リスクが medium と high のときに、証拠の保証レビューを求める"| read_only_reviewer
  apply_scrum_guide -->|"完了の報告の前に、Scrum の検査を求める"| scrum_master_agent
  apply_scrum_guide -.->|"コードの変更に Scrum の判断を重ねる"| implement_change
  apply_scrum_guide -.->|"検証に Scrum の判断を重ねる"| verify_change
  apply_scrum_guide -.->|"文書に Scrum の判断を重ねる"| sync_docs
  apply_scrum_guide -.->|"Git の操作に Scrum の判断を重ねる"| manage_git
  apply_scrum_guide -.->|"人が決めたことの記録を委ねる"| manage_scrum_artifacts
  apply_secure_logging -.->|"ログの変更に要件を重ねる"| implement_change
  apply_dads_frontend -.->|"画面の変更に基準を重ねる"| implement_change
  style skills fill:none,stroke:#808080,stroke-dasharray:6 4
  style kind_orch fill:none,stroke:#808080,stroke-dasharray:6 4
  style kind_overlay fill:none,stroke:#808080,stroke-dasharray:6 4
  style kind_worker fill:none,stroke:#808080,stroke-dasharray:6 4
  style agents fill:none,stroke:#808080,stroke-dasharray:6 4
  classDef component fill:#F3F8FD,stroke:#1F4E79,color:#0B1F33
```

## 凡例

| 表記 | 意味 |
|---|---|
| 青い箱、`[コンポーネント: ...]` | 1つのスキル、または1つのサブエージェント定義（C4 の Component をこの一式で当てはめたもの）。角括弧の後半は種類と、書き込みの制限 |
| 灰色の点線の枠 | 層（スキル、サブエージェント定義）、またはスキルの種類（前付けの `metadata.kind`） |
| 実線の矢印 | 矢印の元のスキルが、先のスキルやサブエージェントを名前で指す。番号は適用の順 |
| 点線の矢印 | 名前では指さず、本文が述べる作業の種類で結び付く関係。オーバーレイが判断基準を重ねる関係と、記録を委ねる関係 |
| 線のない箱 | 単独で使うスキル。親スキルにもオーバーレイにも結び付いていない |

スキルの3種の意味は次のとおりです（[docs/claude-config-design.md](../../claude-config-design.md):133）。

- **作業スキル（worker）**: 何かを作るか、変える。
- **オーバーレイ（overlay）**: 一致する作業スキルに、置き換えではなく追加で適用する判断基準。
- **親スキル（orchestrator）**: 宣言した子スキルを、決まった順に適用する。

## 要素の一覧

出典のパスは `harness/` から書いています。3 行目は、どのスキルでも `description`（そのスキルを使う場面と使わない場面）です。

| 名前 | 種類 | 責任 | 使う場面 | 出典 |
|---|---|---|---|---|
| deliver-change | 親スキル | 問題、要件、実装、検証の4つの子スキルを決まった順で適用し、ゲートの判断とレビューカードを人に渡す | 自明でない変更、セキュリティに関わる変更、複数部分にわたる変更を、差分を読み直さずに受け入れたいとき | `skills/deliver-change/SKILL.md`:3, 17-22 |
| apply-scrum-guide | オーバーレイ（読み取り専用） | 作業を Sprint Goal と Definition of Done（DoD）に結び付け、DoD の項目ごとに完了を判定する。作成物のファイルは書かない | Scrum の作成物があるリポジトリでの開発のたび。Scrum の診断や改善を求められたとき | `skills/apply-scrum-guide/SKILL.md`:3, 15, 34 |
| apply-secure-logging | オーバーレイ | ログの出力を、OWASP などのセキュリティ要件のチェックリストに照らす | ログの追加、変更、レビュー | `skills/apply-secure-logging/SKILL.md`:3, 15 |
| apply-dads-frontend | オーバーレイ | DADS（デジタル庁デザインシステム）とアクセシビリティの基準を、公式資料から当てる | React と Tailwind CSS の画面。公共サービスの画面 | `skills/apply-dads-frontend/SKILL.md`:3, 16 |
| define-problem | 作業スキル | 漠然とした不満を、現状と理想の差としての問題文にする | 原因や解決策を考える前に、問題そのものを定めたいとき | `skills/define-problem/SKILL.md`:3 |
| specify-requirements | 作業スキル | 問題カードと要件グラフを書き、ゲートで ready か blocked かを判定する | 実装の前に、受け入れ基準を書き、要件を分解するとき | `skills/specify-requirements/SKILL.md`:3, 38 |
| implement-change | 作業スキル | 失敗する検査を先に見てから最小の変更を行い、検査してから報告する | コード、設定、テスト、スクリプトの変更のすべて | `skills/implement-change/SKILL.md`:3 |
| verify-change | 作業スキル | 受け入れ基準ごとの証拠を記録し、ゲートで pass、fail、blocked を判定する | 要件グラフのある変更を、証拠で受け入れるとき | `skills/verify-change/SKILL.md`:3, 32 |
| sync-docs | 作業スキル | 変更が古くする文書を挙げ、同じ変更で直す | 振る舞い、インターフェース、設定、判断記録が変わるとき。文書のずれを監査するとき | `skills/sync-docs/SKILL.md`:3 |
| manage-git | 作業スキル（外部に影響） | 頼まれた Git の操作だけを行う | ブランチ、コミット、push、Pull Request を明示的に頼まれたとき | `skills/manage-git/SKILL.md`:3 |
| manage-scrum-artifacts | 作業スキル | Scrum の作成物を、リポジトリの `scrum/` にファイルとして置き、形を検査する | 作成物を置く、Sprint を足す、イベントを準備するとき | `skills/manage-scrum-artifacts/SKILL.md`:3 |
| clarify-intent | 作業スキル | 依頼の読みを明示し、合意を記録する | 意図の確認を求められたとき。前の成果物が退けられるなど、ずれが表れたとき | `skills/clarify-intent/SKILL.md`:3 |
| define-product-strategy | 作業スキル | ビジョン、対象の利用者、価値、指標、範囲を1つの戦略文書にする | 開発の前に、プロダクトの方向を考えるとき | `skills/define-product-strategy/SKILL.md`:3 |
| structure-document | 作業スキル | 文書を1つの主張の木に組み、検査器で確かめる | 報告書、提案、README、Pull Request の本文を書くとき、見直すとき | `skills/structure-document/SKILL.md`:3 |
| draw-system-diagrams | 作業スキル | 1枚に1つの問いの構成図を描き、検査器で確かめる | 構成図を作る、分割する、見直すとき | `skills/draw-system-diagrams/SKILL.md`:3 |
| build-dads-slides | 作業スキル | DADS の公式素材で、16:9 の HTML のスライドを作る | DADS に沿ったスライドを作るとき | `skills/build-dads-slides/SKILL.md`:3 |
| research-aws | 作業スキル（読み取り専用） | AWS についての主張を、公式文書で確かめる | 主張が、AWS の現行の機能、API、クォータ、料金などに依存するとき | `skills/research-aws/SKILL.md`:3 |
| read-only-reviewer | サブエージェント（sonnet。道具は Read、Grep、Glob） | 作者の推論から独立して、要件と証拠を読む | 手順が名指ししたときだけ | `agents/read-only-reviewer.md`:3-5 |
| scrum-master-agent | サブエージェント（sonnet。道具は Read、Grep、Glob） | Scrum の確立と、チームの有効性についての所見を返す | 手順が名指ししたときだけ | `agents/scrum-master-agent.md`:3-5 |

## 前提と未確認の点

- `apply-scrum-guide` から4つの作業スキルへの点線は、推定です。本文の「コードの変更、検証、文書、Git の操作は、それぞれを扱う能力と併用し」（`skills/apply-scrum-guide/SKILL.md`:15）を、それぞれの作業を扱うスキルに当てはめました。本文は、スキルを名前では指していません。
- `apply-secure-logging` と `apply-dads-frontend` は「実装かレビュー」に基準を重ねると書いています（各 `SKILL.md` の 13 行目、14 行目）。このうち実装だけを、`implement-change` への線にしました。レビューを担うスキルはハーネスにありません（[capability-map.md](../capability-map.md) の `H-code-review`）。
- サブエージェント定義は別の層の要素ですが、スキルから起動される関係を見せるために、この図に置きました。`check-runner`、`file-searcher`、`task-worker` は、どのスキルからも名指しされないため描いていません。これらは、頂点の指示にある委任の条件で選ばれます（[コンテナ図](02-containers.md)）。
- 作業スキルの間の受け渡し（問題文 → 要件グラフ → 変更 → 証拠）は、使う順の問いなので、[動的図](05-dynamic-deliver-change.md)に描きました。
- 各要素の役割と枝（木の中の場所）は、この図には描いていません。[役割の木](03-role-tree.md)にあります。

## 関連する図

- 一段外側: [コンテナ図: ハーネスの層](02-containers.md)
- 木の中の場所: [コンポーネント図: 役割の木](03-role-tree.md)
- 使う順: [動的図: 変更を1件届ける](05-dynamic-deliver-change.md)
- 一覧: [構成図の一覧](README.md)
