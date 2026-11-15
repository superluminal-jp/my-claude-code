---
status: Proposed
date: 2026-11-15
deciders: Taiki Ogihara
---

# 0026. スキルとサブエージェントを、Scrum の役割と作業の枝の木に置く

## コンテキストと問題

harness には、スキル17件とサブエージェントの定義5件がある。2026-11-15 にスキルの構成図（`docs/harness/skill-map/`）を描くと、上下の関係は木になっていなかった。親子の宣言は `deliver-change` から子スキル4つへの1件だけだった。オーバーレイ3つは、本文の意味で作業スキルに重なっていた。6つの作業スキルは、どの要素とも上下の関係を持たなかった。要素に役割や枝を宣言する欄はなかった。作業の枝は `docs/harness/capability-map.json` にしかなく、`install.sh` が `~/.claude/` に入れるファイルには含まれていなかった。モデルが一覧で見る `description` も、要素の役割を示していなかった。

利用者はこれを見て「綺麗な木構造になるように再整理できるか」と求め、その後の問いに次のとおり答えた。

- 対象は「ハーネス自体を再編する」。
- 分類の軸は「Scrum の役割」。補足は「Scrumの役割の下に 1 正しい作業を定める 2 統制の下で実行する 3 引き渡す といったさらなる構造を作って位置付ける」。
- 仕組みは、前付けで宣言する方式 A。あわせて「現状スキルとして組まれているものも、エージェントとした方が適切なものがあれば変更してよい。エージェントをスキルに変えるのも許可。スキル・エージェントの名称や内容を一覧したときに役割や目的がわかりやすくなるよう適切に調整するのも良い。」と書いた。

経緯の記録（問題文、要件グラフ、独立した反証、判定の表）は `specs/073-scrum-role-tree/` にある。

## 決定

### 木の形

ハーネスの下に3段の木を置く。第1段は役割、第2段は作業の枝、第3段は要素である。どの要素も親は1つである。

- **役割**（`metadata.role`）: 要素の主な成果物が何を決めるかで分ける。この基準は、独立した反証（CH-01、CH-05）を受けて利用者に尋ね、利用者が選んだ。
  - `product-owner`: 何をなぜ作るか。Product Goal と Product Backlog の項目の中身と、その理解 [SG20, pp.5-6]。
  - `developers`: どう作り、どう確かめるか。Sprint の計画と、Definition of Done を満たす Increment [SG20, p.5]。
  - `scrum-master`: Scrum が成り立っているか。作成物とイベントの確立と、チームの有効性 [SG20, pp.6-7]。
- **枝**（`metadata.branch`）: 要素が支える `harness/CLAUDE.md` の節で、`capability-map.json` の `branch` と同じ語を使う。値は `define`、`execute`、`handoff` の3つ。要素の段階の枝が1つなら、その枝にする。2つ以上の枝にまたがる要素は、`metadata.stage` に主な段階を1つ宣言し、枝はその段階の枝にする。2026-11-15 時点で、またがる要素は `implement-change`（E-implement）と `read-only-reviewer`（H-verify）の2件だけである。
- **木の辺は「属する」だけにする。** 次の3つの関係は木の外に残し、別の図（`docs/harness/skill-map/04-components-relations.md`）に描く。親スキルが子スキルを従える関係、オーバーレイが判断基準を重ねる関係、スキルがサブエージェントを起動させる関係である。木が示すのは成果物の属する役割で、要素を使う役割のすべてではない。
- **頂点の指示とルールは木に入れない。** どちらも全役割に共通で、汎用に保つ。

配置は、Product Owner に3件（define に `clarify-intent`、`define-product-strategy`、`define-problem`）、Developers に17件、Scrum Master に2件（execute に `manage-scrum-artifacts`、`scrum-master-agent`）である。`manage-scrum-artifacts` は作成物を置いて形を検査するので、Scrum の確立として Scrum Master に置いた。

### 一覧での見え方

- **標識:** 各要素の `description` の末尾に `[<役割> / <枝>]`（たとえば `[Developers / execute]`）を付ける。末尾に置くのは、使う場面を述べる語を先頭に残すためである。
- **未検証のリスク:** 標識を足すとスキルの選ばれ方が変わりうるが、有料の評価は回さず、影響は未検証のリスクとして受け入れる。この扱いは利用者が選んだ（反証 CH-06）。
- **README の表:** `README.md` と `README.ja.md` に、宣言から生成した表を置く。列は役割、枝、名前、種類、目的である。

### 形と名前

形の基準では、主な用途で次の (a) と (b) が常に成り立つ要素をエージェントにし、それ以外をスキルにする。

- (a) 作者から独立した読み手が要る、出力が長く結果だけが要る、または独立に並べて進められる。
- (b) 人との対話も、完了の判定も要らない。

改名の基準では、名前が実際の目的と違うことを述べている場合か、一覧の読み手が役割を取り違える場合だけ改名する。

22件に当てた結果、変える要素はなかった（`specs/073-scrum-role-tree/form-and-name-review.md`）。唯一の候補だった `research-aws` は、主な用途の1つの主張の確認では出力が短いことも多く、(a) が常には成り立たない。また、エージェントにすると評価のシナリオ `uses-research-aws` で振る舞いを観測できなくなるので、スキルのまま残した。

### 検査

- **契約の拡張:** スキルの契約（`tests/assert_skill_contract.py` の C-04）が、`role` と `branch` の値を確かめる。C-08 は、前付けの `metadata.role` の値だけを名前に数えなくなった。値 `scrum-master` が、廃止したスキルの名前と同じだからである。本文の同じ文字列は、これまでどおり数える。エージェント定義の検査（`tests/assert_reviewer_agent.py`）は `metadata` の欄を受け入れるが、キーは `role`、`branch`、`stage` に限る。どちらも検査を緩める変更なので、検証の記録に、利用者の承認を求める項目として載せた。
- **新しい検査:** `tests/assert_role_tree.py` が、すべてのスキルとサブエージェントの定義について次の一致を確かめ、`tests/run-harness-skills.sh` から毎回実行される。
  - 宣言
  - 対応表との整合
  - 標識
  - README の表
  - 木の図
- **自己検査:** `--self-test` は、規則を1つずつ壊した写しがすべて拒まれることを示す。

## 検討した選択肢

- **ディレクトリを入れ子にする**（`harness/skills/<役割>/<枝>/<スキル>/`）: 置き場所がディレクトリの形で見える。その代わり、`install.sh` が入れるときに平らに直す必要があり、すべてのテストのパスが変わる。公式文書は、`~/.claude/skills/<グループ>/<名前>/SKILL.md` のように、グループのためだけのフォルダを読むとは述べていない（<https://code.claude.com/docs/en/skills.md>）。
- **役割ごとの親スキルを足す**: 親子の宣言で木ができる。その代わり、契約 C-11（親スキルの子に親スキルを置かない）を変える必要がある。読み込まれる `description` が増え、振る舞いも変わる。
- **木の辺に、従える関係と重ねる関係も含める**: 1枚の図で済む。その代わり、`define-problem` が Product Owner と `deliver-change` の2つを親に持ち、木にならない。
- **標識を先頭に置き、変更の前後で評価を回す**: 選ばれ方への影響を測れる。その代わり、プランの使用量と時間がかかる。利用者は、標識を末尾に置き、評価は回さない方を選んだ。
- **`description` は変えず、役割は README と構成図だけで見せる**: 選ばれ方は変わらない。その代わり、モデルの見る一覧に役割が出ず、合意した理想の一部が満たされない。
- **`manage-scrum-artifacts` を Product Owner に置く**、**`specify-requirements` も Product Owner に置く**: 利用者は、どちらも選ばなかった。

## 結果

- スキル17件とエージェント5件の前付けが、役割と枝を宣言する。2件は段階も宣言する。手順の本文は変えていない（`specs/073-scrum-role-tree/evidence/frontmatter_only.py`）。
- Claude Code は、スキルの `metadata` の中身に従って動作しない。サブエージェント定義の前付けの未知の欄は、エラーにならずに無視される（<https://code.claude.com/docs/en/sub-agents.md>）。宣言は、このリポジトリの検査と文書のためのものである。
- 一覧（`description`）が変わるので、スキルの選ばれ方が変わる可能性がある。測っていない。
- Claude.ai に上げた写しは古いまま残り、標識を持たない。
- `install.sh` を次に実行するまで、`~/.claude/` には反映されない。

## ADR-0025 の前提について

[ADR-0025](0025-ai-as-developer-scrum-master-as-subagent.md) は、Developer もサブエージェントにする案を退ける理由の1つに、「サブエージェントは別のサブエージェントを起動できない」ことを挙げている。現行の公式文書は「By default, a subagent can spawn subagents of its own, up to three layers below the main conversation.」と述べている（<https://code.claude.com/docs/en/sub-agents.md>、2026-11-15 に確かめた）。ADR-0025 の結論（主の会話を Developer とし、判断と完了の判定を主の会話に残す）は、`harness/CLAUDE.md` の委任の方針という、もう1つの理由でも成り立つ。それでも、前提の1つは現行の文書と食い違っている。この記録は ADR-0025 を書き換えない。

## 確認方法

- `bash tests/run-harness-skills.sh` が、契約（C-04、C-08）、`tests/assert_role_tree.py`、`tests/assert_role_tree.py --self-test` を通す。
- `bash tests/run-verify-change-skill.sh` が、`metadata` を持つエージェント定義を受け入れ、既存の変えた写しをすべて拒む。
- `python3 -B harness/skills/draw-system-diagrams/scripts/check_diagrams.py docs/harness/skill-map` が、エラー0で通る。
- `install.sh` で入れた後の新しいセッションで、`/agents` に5件のエージェントが読み込みの誤りなしに並ぶことを、利用者が確かめる。Claude Code が未知の欄を無視するという公式文書の記述を、実際の環境で確かめるためである（要件グラフの AC-AGENT-META-2、デプロイの後）。
- 測っていないことが2つある。1つは、標識によってスキルの選ばれ方が変わるかどうか。もう1つは、主の会話が実際に `scrum-master-agent` を起動するかどうか（ADR-0025 から引き続き未観測）である。

## 補足情報

- [ADR-0015](0015-rule-layer-independence.md): 設定の層が互いを名指さない決まり。役割と枝は名前ではなく抽象的な節なので、この決まりは変わらない。
- [ADR-0025](0025-ai-as-developer-scrum-master-as-subagent.md): AI を Developer とし、Scrum Master をサブエージェントにした決定。
- _The Scrum Guide_（Ken Schwaber and Jeff Sutherland、2020年11月）<https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf>。Product Owner の責任は pp.5-6、Developers の責任は p.5、Scrum Master の責任は pp.6-7 にある。
