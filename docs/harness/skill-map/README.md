# 構成図: ハーネスのフェーズの木と要素の関係

この一式は、`harness/` に置いた Claude Code のユーザー設定（以下、ハーネス）を4枚の図で説明します。上から順に読むと、次のことが分かります。

- ハーネスをだれが使い、ハーネスがどの外部のシステムに頼るか
- ハーネスがどの層でできているか
- 18の要素（スキル13件、サブエージェント定義5件）が、AI-DLC Workflows v2 のフェーズと作業の枝の木のどこに属するか
- 木の外で、どのスキルがどのスキルに判断基準を重ね、どのサブエージェントを起動させるか

内容は、2026-11-18 の `harness/` に基づきます。その日に、変更を意図から受け入れまで運ぶ手順の基盤を AI-DLC Workflows v2 にし、ハーネスをその補完に絞りました（[ADR-0029](../../adr/0029-base-delivery-on-ai-dlc-workflows-v2.md)）。AI-DLC Workflows v2 は、利用者が上流の `aidlc` コマンドでプロジェクトごとに導入するもので、`install.sh` は導入しません。この変更で、スキル4件（`deliver-change`、`specify-requirements`、`verify-change`、`define-product-strategy`）を除き、木の1段目を Scrum の役割からフェーズに置き換えました。それまで図 5 だった動的図「変更を1件届ける」は、除いた親スキルの流れを描いていたので、[`archive/delivery-gates/`](../../../archive/delivery-gates/README.md) へ移しました。図 3 は各要素の前付けの宣言から生成し、`tests/assert_role_tree.py` が宣言と一致するかを確かめます。

| # | 図 | 答える問い | 読み手 | 抽象度 |
|---|---|---|---|---|
| 1 | [システムコンテキスト図: ハーネス](01-system-context.md) | だれがハーネスを使い、ハーネスはどの外部のシステムに頼るか | 利用者、初めて読む人 | C4 system context |
| 2 | [コンテナ図: ハーネスの層](02-containers.md) | ハーネスはどの層でできていて、層どうしはどう参照し合うか | ハーネスの保守者 | C4 container |
| 3 | [コンポーネント図: フェーズの木](03-role-tree.md) | 各スキルとサブエージェントは、AI-DLC Workflows v2 のどのフェーズの、どの作業の枝に属するか | 利用者、保守者 | C4 component |
| 4 | [コンポーネント図: 木の外の関係](04-components-relations.md) | どのスキルがどのスキルに判断基準を重ねるか。どのサブエージェントを起動させるか | ハーネスの保守者 | C4 component |

## 用語

- **スキル**: Claude Code が、依頼に合うときだけ読み込む手順書。`SKILL.md` と、それに同梱したファイルでできている。
- **サブエージェント**: 主の会話とは別の文脈で動く子エージェント。定義ファイルが、そのモデル、effort、使える道具を固定する。
- **主の会話**: 利用者と直接やりとりする Claude Code の会話。サブエージェントを起動し、作業が完了したかを判定する。
- **C4**: システムを system context、container、component、code の4段階の抽象度で描く表記法。この一式での当てはめ方は、下の「前提」に書いた。

## 描かなかった図

- **デプロイ図**: ハーネスは利用者のマシンの `~/.claude/` にだけ置かれ、どこで動くかが読み手の問いにならないため描いていません。`install.sh` による同期は、図 1 と図 2 に書いています。
- **ルールとサブエージェント定義のコンポーネント図**: 問いがないため描いていません。ルールの中身は [docs/claude-config-design.md](../../claude-config-design.md) に、サブエージェントの一覧は [README](../../../README.md) にあります。
- **動的図**: 変更を意図から受け入れまで運ぶ順は、プロジェクトに導入した AI-DLC Workflows v2 のエンジンが決め、ハーネスは決めないため描いていません。文書・構成図・スライドを作る、Scrum の作成物を置くといった流れは、スキル1つで完結するため描いていません。各スキルを使う場面は、図 4 の要素の一覧にあります。
- **コード**: 手では描きません。

## 前提

- C4 の container は、本来は別々に動く単位、または別々に配置される単位です。ハーネスはプログラムではないので、Claude Code が別々の時点で読み込む5つの層を container に当てはめました。5つの層とは、頂点の指示、ルール、スキル、サブエージェント定義、設定です。1つの層の中の個々のファイルは component に当てはめました。この当てはめは、この一式だけの決まりです。

## 情報源

- `harness/CLAUDE.md`、`harness/rules/*.md`、`harness/agents/*.md`、`harness/skills/*/SKILL.md`（前付けと本文）、`harness/settings.json`
- このリポジトリの `CLAUDE.md`（`install.sh` が何を同期するか）
- [ADR-0015](../../adr/0015-rule-layer-independence.md): 層どうしを名前で参照しないという決定
- [ADR-0025](../../adr/0025-ai-as-developer-scrum-master-as-subagent.md): AI を Developer とし、Scrum Master をサブエージェントにするという決定
- [ADR-0029](../../adr/0029-base-delivery-on-ai-dlc-workflows-v2.md): 変更の引き渡しの基盤を AI-DLC Workflows v2 にし、スキルとエージェントをフェーズの木に置くという決定。[ADR-0026](../../adr/0026-place-skills-and-agents-in-a-scrum-role-tree.md)（Scrum の役割の木に置くという決定）を置き換えた
- [docs/claude-config-design.md](../../claude-config-design.md) の 136 行目: スキルの種類 worker・overlay・orchestrator の定義
- 作業の段階ごとの担い手は [capability-map.md](../capability-map.md) にあります。この一式は、その表を図にしたものではありません。木の中の場所と、ファイルどうしの参照を描いたものです。
