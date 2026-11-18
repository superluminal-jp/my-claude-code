# コンポーネント図: フェーズの木

ハーネスの18の要素（スキル13件、サブエージェント定義5件）は、どれもちょうど1つの場所を持ちます。場所は3段で、AI-DLC Workflows v2 のフェーズ、作業の枝、要素の順です。フェーズは、要素の主な成果物がどのフェーズを支えるかで決まります。Ideation は意図と範囲を確かめる、Inception は要件と設計を定める、Construction は作り、試す、Operation は配備し、運用する、です。どのフェーズにも結び付かない要素は、Cross-phase に置きます。枝は、頂点の指示（`harness/CLAUDE.md`）の3つの節のうち、その要素が支えるものです。どの要素も親は1つなので、この図は木になっています。図は、各要素の前付けの宣言から `tests/assert_role_tree.py --mermaid` で生成したもので、手では書き換えません。

2026-11-18 までは、木の1段目は Scrum の役割でした（[ADR-0026](../../adr/0026-place-skills-and-agents-in-a-scrum-role-tree.md)）。[ADR-0029](../../adr/0029-base-delivery-on-ai-dlc-workflows-v2.md) が、これをフェーズに置き換えました。このページと検査のファイル名（`03-role-tree.md`、`tests/assert_role_tree.py`）は、そのときの名前のままです。

<!-- role-tree-diagram:start -->
```mermaid
flowchart LR
  accTitle: コンポーネント図: フェーズの木
  accDescr: harness のスキルとエージェントを、AI-DLC のフェーズ、作業の枝、要素の3段の木に置いた図。どの要素も親は1つで、各要素の前付けの metadata.phase と metadata.branch から生成している。
  harness["ハーネス<br/>[このシステム: harness/skills/ と harness/agents/]"]:::system
  role_ideation["Ideation<br/>[フェーズ: 意図と範囲を確かめる]"]:::container
  ideation_define["define<br/>[枝: 1 正しい作業を定める]"]:::component
  define_problem["define-problem<br/>[スキル]"]:::component
  role_inception["Inception<br/>[フェーズ: 要件と設計を定める]"]:::container
  inception_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  draw_system_diagrams["draw-system-diagrams<br/>[スキル]"]:::component
  role_construction["Construction<br/>[フェーズ: 作り、試す]"]:::container
  construction_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  apply_dads_frontend["apply-dads-frontend<br/>[スキル]"]:::component
  apply_secure_logging["apply-secure-logging<br/>[スキル]"]:::component
  implement_change["implement-change<br/>[スキル]"]:::component
  role_cross_phase["Cross-phase<br/>[フェーズ: どのフェーズにも重ねて使う]"]:::container
  cross_phase_define["define<br/>[枝: 1 正しい作業を定める]"]:::component
  clarify_intent["clarify-intent<br/>[スキル]"]:::component
  research_aws["research-aws<br/>[スキル]"]:::component
  cross_phase_execute["execute<br/>[枝: 2 統制の下で実行する]"]:::component
  apply_scrum_guide["apply-scrum-guide<br/>[スキル]"]:::component
  build_dads_slides["build-dads-slides<br/>[スキル]"]:::component
  check_runner["check-runner<br/>[エージェント]"]:::component
  file_searcher["file-searcher<br/>[エージェント]"]:::component
  manage_git["manage-git<br/>[スキル]"]:::component
  manage_scrum_artifacts["manage-scrum-artifacts<br/>[スキル]"]:::component
  scrum_master_agent["scrum-master-agent<br/>[エージェント]"]:::component
  task_worker["task-worker<br/>[エージェント]"]:::component
  cross_phase_handoff["handoff<br/>[枝: 3 引き渡す]"]:::component
  read_only_reviewer["read-only-reviewer<br/>[エージェント]"]:::component
  structure_document["structure-document<br/>[スキル]"]:::component
  sync_docs["sync-docs<br/>[スキル]"]:::component
  harness -->|"含む"| role_ideation
  role_ideation -->|"含む"| ideation_define
  ideation_define -->|"含む"| define_problem
  harness -->|"含む"| role_inception
  role_inception -->|"含む"| inception_execute
  inception_execute -->|"含む"| draw_system_diagrams
  harness -->|"含む"| role_construction
  role_construction -->|"含む"| construction_execute
  construction_execute -->|"含む"| apply_dads_frontend
  construction_execute -->|"含む"| apply_secure_logging
  construction_execute -->|"含む"| implement_change
  harness -->|"含む"| role_cross_phase
  role_cross_phase -->|"含む"| cross_phase_define
  cross_phase_define -->|"含む"| clarify_intent
  cross_phase_define -->|"含む"| research_aws
  role_cross_phase -->|"含む"| cross_phase_execute
  cross_phase_execute -->|"含む"| apply_scrum_guide
  cross_phase_execute -->|"含む"| build_dads_slides
  cross_phase_execute -->|"含む"| check_runner
  cross_phase_execute -->|"含む"| file_searcher
  cross_phase_execute -->|"含む"| manage_git
  cross_phase_execute -->|"含む"| manage_scrum_artifacts
  cross_phase_execute -->|"含む"| scrum_master_agent
  cross_phase_execute -->|"含む"| task_worker
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
| `[フェーズ: ...]` の箱 | AI-DLC Workflows v2 のフェーズ、またはどのフェーズにも結び付かない要素を置く Cross-phase。角括弧の後半は、そのフェーズで行うこと |
| `[枝: ...]` の箱 | 頂点の指示の3つの節。define は正しい作業を定める、execute は統制の下で実行する、handoff は引き渡す |
| `[スキル]`、`[エージェント]` の箱 | 1つの要素。スキルは主の会話が読み込む手順、エージェントは別の文脈で動くサブエージェントの定義 |
| 矢印「含む」 | 親が子を含む。木の辺はこの関係だけ |

## 要素の一覧

各要素のフェーズ、枝、目的の一覧は、宣言から生成した [README の表](../../../README.ja.md#フェーズの木) にあります（`<!-- role-tree:start -->` と `<!-- role-tree:end -->` の間）。同じ木は、`python3 tests/assert_role_tree.py --print` で文字として出力できます。この図の節のうち、フェーズと枝の意味は次のとおりです。

| 名前 | 種類 | 意味 | 出典 |
|---|---|---|---|
| Ideation | フェーズ | 成果物が、意図と範囲を確かめることを支える | `tests/assert_role_tree.py` の `PHASE_GLOSS`、[ADR-0029](../../adr/0029-base-delivery-on-ai-dlc-workflows-v2.md) |
| Inception | フェーズ | 成果物が、要件と設計を定めることを支える | 同上 |
| Construction | フェーズ | 成果物が、作り、試すことを支える | 同上 |
| Cross-phase | フェーズ | 成果物が、1つのフェーズに結び付かず、どのフェーズにも重ねて使われる | 同上 |
| define | 枝 | 頂点の指示の「正しい作業を定める」 | `harness/CLAUDE.md`、`docs/harness/capability-map.json` |
| execute | 枝 | 頂点の指示の「統制の下で実行する」 | 同上 |
| handoff | 枝 | 頂点の指示の「引き渡す」 | 同上 |

## 前提と未確認の点

- **要素数の警告は残す**: 図の検査器は、要素数がしきい値（20）を超えるとして警告 M6 を出します。それでも1枚に残すのは、木の辺は交差せず、29の節をフェーズごとに分けると、根からの木の形が読めなくなるからです。
- **Operation の箱はない**: 宣言できるフェーズには Operation（配備し、運用する）もありますが、このフェーズに属する要素は今はないので、図には現れません。ADR-0029 は、Operation のための要素を足さないと決めています。
- **木はステージの順を示さない**: 図が示すのは、要素の成果物が支えるフェーズです。要素を使うフェーズのすべてではありません。たとえば `structure-document` は、どのフェーズの文書にも使われます。AI-DLC Workflows v2 を導入したプロジェクトで、どのステージがどの順で進むかは、そのエンジンが決めます（`harness/CLAUDE.md`:17）。この一式には、その順を描いた図はありません。
- **木の外の関係は別の図にある**: オーバーレイが判断基準を重ねる関係と、スキルがサブエージェントを起動させる関係は、[木の外の関係](04-components-relations.md)にあります。
- **2つの段階にまたがる要素**: 段階が2つ以上の枝にまたがる `implement-change` と `read-only-reviewer` は、`metadata.stage` に主な段階を宣言しています。`implement-change` は E-implement（execute）、`read-only-reviewer` は H-verify（handoff）です。

## 関連する図

- 一段外側: [コンテナ図: ハーネスの層](02-containers.md)
- 木の外の関係: [コンポーネント図: 木の外の関係](04-components-relations.md)
- 一覧: [構成図の一覧](README.md)
