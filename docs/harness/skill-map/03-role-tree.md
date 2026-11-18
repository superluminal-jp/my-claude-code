# コンポーネント図: 役割の木

ハーネスの22の要素（スキル17件、サブエージェント定義5件）は、どれもちょうど1つの場所を持ちます。場所は3段で、Scrum の役割、作業の枝、要素の順です。役割は、要素の主な成果物がだれのアカウンタビリティに属するかで決まります。Product Owner は何をなぜ作るか、Developers はどう作りどう確かめるか、Scrum Master は Scrum が成り立っているかです。枝は、頂点の指示（`harness/CLAUDE.md`）の3つの節のうち、その要素が支えるものです。どの要素も親は1つなので、この図は木になっています。図は、各要素の前付けの宣言から `tests/assert_role_tree.py --mermaid` で生成したもので、手では書き換えません。

<!-- role-tree-diagram:start -->
```mermaid
flowchart LR
  accTitle: コンポーネント図: フェーズの木
  accDescr: harness のスキルとエージェントを、AI-DLC のフェーズ、作業の枝、要素の3段の木に置いた図。どの要素も親は1つで、各要素の前付けの metadata.phase と metadata.branch から生成している。
  harness["ハーネス<br/>[このシステム: harness/skills/ と harness/agents/]"]:::system
  role_ideation["Ideation<br/>[フェーズ: 意図と範囲を確かめる]"]:::container
  ideation_define["define<br/>[枝: 1 正しい作業を定める]"]:::component
  clarify_intent["clarify-intent<br/>[スキル]"]:::component
  define_problem["define-problem<br/>[スキル]"]:::component
  role_inception["Inception<br/>[フェーズ: 要件と設計を定める]"]:::container
  inception_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  draw_system_diagrams["draw-system-diagrams<br/>[スキル]"]:::component
  role_construction["Construction<br/>[フェーズ: 作り、試す]"]:::container
  construction_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  apply_dads_frontend["apply-dads-frontend<br/>[スキル]"]:::component
  apply_secure_logging["apply-secure-logging<br/>[スキル]"]:::component
  check_runner["check-runner<br/>[エージェント]"]:::component
  implement_change["implement-change<br/>[スキル]"]:::component
  task_worker["task-worker<br/>[エージェント]"]:::component
  role_cross_phase["Cross-phase<br/>[フェーズ: どのフェーズにも重ねて使う]"]:::container
  cross_phase_define["define<br/>[枝: 1 正しい作業を定める]"]:::component
  research_aws["research-aws<br/>[スキル]"]:::component
  cross_phase_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  apply_scrum_guide["apply-scrum-guide<br/>[スキル]"]:::component
  build_dads_slides["build-dads-slides<br/>[スキル]"]:::component
  file_searcher["file-searcher<br/>[エージェント]"]:::component
  manage_git["manage-git<br/>[スキル]"]:::component
  manage_scrum_artifacts["manage-scrum-artifacts<br/>[スキル]"]:::component
  scrum_master_agent["scrum-master-agent<br/>[エージェント]"]:::component
  cross_phase_handoff["handoff<br/>[枝: 3 引き渡す]"]:::component
  read_only_reviewer["read-only-reviewer<br/>[エージェント]"]:::component
  structure_document["structure-document<br/>[スキル]"]:::component
  sync_docs["sync-docs<br/>[スキル]"]:::component
  harness -->|"含む"| role_ideation
  role_ideation -->|"含む"| ideation_define
  ideation_define -->|"含む"| clarify_intent
  ideation_define -->|"含む"| define_problem
  harness -->|"含む"| role_inception
  role_inception -->|"含む"| inception_execute
  inception_execute -->|"含む"| draw_system_diagrams
  harness -->|"含む"| role_construction
  role_construction -->|"含む"| construction_execute
  construction_execute -->|"含む"| apply_dads_frontend
  construction_execute -->|"含む"| apply_secure_logging
  construction_execute -->|"含む"| check_runner
  construction_execute -->|"含む"| implement_change
  construction_execute -->|"含む"| task_worker
  harness -->|"含む"| role_cross_phase
  role_cross_phase -->|"含む"| cross_phase_define
  cross_phase_define -->|"含む"| research_aws
  role_cross_phase -->|"含む"| cross_phase_execute
  cross_phase_execute -->|"含む"| apply_scrum_guide
  cross_phase_execute -->|"含む"| build_dads_slides
  cross_phase_execute -->|"含む"| file_searcher
  cross_phase_execute -->|"含む"| manage_git
  cross_phase_execute -->|"含む"| manage_scrum_artifacts
  cross_phase_execute -->|"含む"| scrum_master_agent
  role_cross_phase -->|"含む"| cross_phase_handoff
  cross_phase_handoff -->|"含む"| read_only_reviewer
  cross_phase_handoff -->|"含む"| structure_document
  cross_phase_handoff -->|"含む"| sync_docs
  classDef system fill:#DCE9F7,stroke:#1F4E79,stroke-width:2px,color:#0B1F33
  classDef container fill:#E8F1FB,stroke:#1F4E79,color:#0B1F33
  classDef component fill:#F3F8FD,stroke:#1F4E79,color:#0B1F33
```
<!-- role-tree-diagram:end -->

## 凡例

| 表記 | 意味 |
|---|---|
| 太枠の箱、`[このシステム: ...]` | ハーネス全体。木の根 |
| `[役割: ...]` の箱 | Scrum の3つのアカウンタビリティ [SG20, pp.5-7]。角括弧の後半は、その役割に属する成果物が決めること |
| `[枝: ...]` の箱 | 頂点の指示の3つの節。define は正しい作業を定める、execute は統制の下で実行する、handoff は引き渡す |
| `[スキル]`、`[エージェント]` の箱 | 1つの要素。スキルは主の会話が読み込む手順、エージェントは別の文脈で動くサブエージェントの定義 |
| 矢印「含む」 | 親が子を含む。木の辺はこの関係だけ |

## 要素の一覧

各要素の役割、枝、目的の一覧は、宣言から生成した [README の表](../../../README.ja.md#役割の木) にあります。この図の節のうち、役割と枝の意味は次のとおりです。

| 名前 | 種類 | 意味 | 出典 |
|---|---|---|---|
| Product Owner | 役割 | 成果物が、Product Goal と Product Backlog の項目の中身と、その理解を決める（何をなぜ作るか） | [SG20, pp.5-6]、[ADR-0026](../../adr/0026-place-skills-and-agents-in-a-scrum-role-tree.md) |
| Developers | 役割 | 成果物が、Sprint の計画と、Definition of Done を満たす Increment を決める（どう作り、どう確かめるか） | [SG20, p.5]、ADR-0026 |
| Scrum Master | 役割 | 成果物が、Scrum の確立（作成物とイベント）と、チームの有効性を決める | [SG20, pp.6-7]、ADR-0026 |
| define | 枝 | 頂点の指示の「正しい作業を定める」 | `harness/CLAUDE.md`、`docs/harness/capability-map.json` |
| execute | 枝 | 頂点の指示の「統制の下で実行する」 | 同上 |
| handoff | 枝 | 頂点の指示の「引き渡す」 | 同上 |

## 前提と未確認の点

- **要素数の警告は残す**: 図の検査器は、要素数がしきい値（20）を超えるとして警告 M6 を出します。それでも1枚に残すのは、木の辺は交差せず、30を超える節を役割ごとに分けると、根からの木の形が読めなくなるからです。
- **木は使う役割を示さない**: 図が示すのは、要素の成果物が属する役割です。要素を使う役割のすべてではありません。たとえば `structure-document` は Product Owner に渡す文書にも使われます。どの作業でどの要素が使われるかは、[動的図](05-dynamic-deliver-change.md)にあります。
- **木の外の関係は別の図にある**: 親スキルが子スキルを従える関係、オーバーレイが判断基準を重ねる関係、スキルがサブエージェントを起動させる関係は、[木の外の関係](04-components-relations.md)にあります。
- **2つの段階にまたがる要素**: 段階が2つ以上の枝にまたがる `implement-change` と `read-only-reviewer` は、`metadata.stage` に主な段階を宣言しています。`implement-change` は E-implement（execute）、`read-only-reviewer` は H-verify（handoff）です。

## 関連する図

- 一段外側: [コンテナ図: ハーネスの層](02-containers.md)
- 木の外の関係: [コンポーネント図: 木の外の関係](04-components-relations.md)
- 一覧: [構成図の一覧](README.md)
