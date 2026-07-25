# 根拠資料

## 目次

- [使い方](#使い方)
- [規範的な基準](#規範的な基準)
- [補完的な実践と研究](#補完的な実践と研究)
- [反パターンとコーチングの実務資料](#反パターンとコーチングの実務資料)
- [スケーリングフレームワークの資料](#スケーリングフレームワークの資料)
- [Claude Codeスキル仕様](#claude-codeスキル仕様)
- [引用ルール](#引用ルール)

## 使い方

Scrumそのものの定義はScrum Guideを最優先する。ほかの資料は、Scrumを置き換えず、測定、フロー、ファシリテーション、反パターン、スケーリング、チーム環境を補完するために使う。

根拠の強さを次のように区別する。

1. **規範**：Scrum Guideに明記されたScrumの定義
2. **公式補完**：Scrum.orgなどが公開する補完ガイド、Nexus Guideなど公式のスケーリング拡張
3. **研究・実務知見**：査読研究、継続的な業界研究、広く参照される実務書
4. **文脈依存の技法**：現場で試し、結果を検査すべきプラクティス（レトロ形式など、特定の単一の出典を持たない慣行を含む）

## 規範的な基準

### [SG20] The Scrum Guide

Ken Schwaber and Jeff Sutherland, *The Scrum Guide: The Definitive Guide to Scrum—The Rules of the Game*, November 2020.

https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf

適用する主要箇所：

- Scrumは複雑な問題に対する適応的な解決を通じて価値を生む軽量なフレームワーク（p.3）。
- 経験主義の柱は透明性、検査、適応（pp.3–4）。
- Scrum ValuesはCommitment、Focus、Openness、Respect、Courage（pp.4–5）。
- Scrum Teamは階層やサブチームを持たず、自己管理し、通常10人以下（p.5）。
- Scrum MasterはScrumの確立とScrum Teamの有効性に責任を持つ（p.6）。
- Product Ownerは価値最大化とProduct Backlog管理、DevelopersはSprint Backlog、品質、日々の適応に責任を持つ（pp.5–6）。
- Scrumイベントの目的と最大タイムボックス（pp.7–10）。
- Product Goal、Sprint Goal、Definition of Doneは各作成物へのコミットメント（pp.10–12）。
- Scrumを部分的に実施することは可能だが、その結果はScrumではない（p.13）。

Scrum Guideの最新版表示と各言語版：

https://scrumguides.org/

### [NXG] The Nexus Guide

Scrum.org, *The Nexus Guide*（最新版、2026-07-25取得）。

https://www.scrum.org/resources/online-nexus-guide

適用する主要箇所：Scrumを最小限の変更でスケールする公式拡張。約3〜9チームが単一のProduct Backlogから1つのIntegrated Increment を届け、参加チームから選出されるNexus Integration Teamと、チーム横断の依存管理のためのNexusレベルイベントを追加する。

### [AM01] Manifesto for Agile Software Development and Principles

Beck et al., *Manifesto for Agile Software Development*, 2001.

https://agilemanifesto.org/

https://agilemanifesto.org/principles.html

適用する主要箇所：

- 価値あるソフトウェアの早期・継続的な提供を優先する。
- ビジネス側と開発者の継続的な協働、持続可能なペース、技術的卓越性、自己組織化、定期的な振り返りを重視する。
- 右側にも価値があると認めつつ、左側をより重視する。文書、計画、プロセスを否定する根拠に使わない。

## 補完的な実践と研究

### [EBM24] Evidence-Based Management Guide

Scrum.org, *Evidence-Based Management Guide*, updated 2024.

https://www.scrum.org/resources/evidence-based-management-guide

更新内容の説明：

https://www.scrum.org/resources/blog/evidence-based-management-guide-2024-whats-new

Scrum Teamの活動量ではなく、顧客成果、組織能力、事業成果を改善するために使う。Strategic Goal、Intermediate Goal、Immediate Tactical Goalと、Current Value、Unrealized Value、Ability to Innovate、Time to Marketの4 Key Value Areasを文脈に応じて参照する。

### [KGS21] The Kanban Guide for Scrum Teams

Scrum.org, Daniel Vacanti, and Yuval Yeret, *The Kanban Guide for Scrum Teams*, January 2021.

https://scrumorg-website-prod.s3.amazonaws.com/drupal/2021-01/01-2021%20Kanban%20Guide.pdf

Scrumを置き換えず、価値のフローを改善する補完策として使う（p.3）。基本フロー指標はWIP、Cycle Time、Work Item Age、Throughput（p.4）。ワークフローの可視化、WIP制限、進行中作業の能動的管理、Definition of Workflowの検査と適応を扱う（pp.4–6）。

### [DORA26] DORA software delivery performance metrics

DORA / Google Cloud, *DORA's software delivery performance metrics*, current page retrieved 2026-07-25.

https://dora.dev/guides/dora-metrics/

ソフトウェア提供の改善に限って、Change Lead Time、Deployment Frequency、Failed Deployment Recovery Time、Change Fail Rate、Deployment Rework Rateを使う。異なる文脈のチーム比較、単一指標の目標化、チーム間競争を避け、同一アプリケーションまたはサービスの経時改善に使う。

### [EDM99] Psychological safety and learning behavior

Amy C. Edmondson, "Psychological Safety and Learning Behavior in Work Teams," *Administrative Science Quarterly*, 44(2), 350–383, 1999.

https://doi.org/10.2307/2666999

心理的安全性を、チームが対人的リスクを取っても安全だという共有信念として扱い、学習行動との関係を検討した査読研究。心理的安全性を「対立がない」「要求水準が低い」状態と混同しない。

補助的な実務向け解説：American Psychological Association, "What is psychological safety at work?" 2023.

https://www.apa.org/topics/healthy-workplaces/psychological-safety

### [ART] Agile Retrospectives

Esther Derby & Diana Larsen, *Agile Retrospectives: Making Good Teams Great*, Pragmatic Bookshelf, 2006.

レトロスペクティブの5段階構造（場を整える・データを集める・意味を探る・選ぶ・閉じる）の出典。[event-playbooks.md](event-playbooks.md)で使用。

### [ICA] Coaching Agile Teams

Lyssa Adkins, *Coaching Agile Teams: A Companion for ScrumMasters, Agile Coaches, and Project Managers in Transition*, Addison-Wesley, 2010.

Scrum Master／アジャイルコーチのスタンス（ファシリテーター、コーチ、ティーチャー、メンター、対立の航行者）の出典。[scrum-master-role.md](scrum-master-role.md)で使用。

## 反パターンとコーチングの実務資料

### [SAP] Scrum.org anti-patterns series

- 27 Sprint Anti-Patterns — https://www.scrum.org/resources/blog/27-sprint-anti-patterns
- Scrum Anti-Patterns Taxonomy — https://www.scrum.org/resources/blog/scrum-anti-patterns-taxonomy
- How the Scrum Master supports the Product Owner — https://www.scrum.org/resources/blog/how-can-scrum-master-support-product-owner

### [ZBS] Zombie Scrum

Christiaan Verwijs & Johannes Schartau, zombiescrum.org。Scrum.org経由の解説：

Zombie Scrum: Symptoms, Causes and Treatment — https://www.scrum.org/resources/blog/zombie-scrum-symptoms-causes-and-treatment

### [AAP] Agile Alliance

Scrum Master Anti-Patterns — https://agilealliance.org/scrum-master-anti-patterns/

Agile Allianceの用語集・リソース全般 — https://agilealliance.org

### Scrum Alliance（補足）

- Scrum Events（タイムボックスの目安） — https://resources.scrumalliance.org/Article/scrum-events
- What Is Timeboxing in Scrum — https://resources.scrumalliance.org/Article/timeboxing-scrum
- Agile Glossary — https://www.scrumalliance.org/glossary

## スケーリングフレームワークの資料

### [LESS] LeSS（Large-Scale Scrum）

Craig Larman & Bas Vodde。https://less.works

役割を追加せず組織的複雑さを取り除くことでScrumをスケールするフレームワーク。単一のProduct Backlog／Product Owner／Definition of Doneを多数チームで共有する。

### [SAFE] SAFe（Scaled Agile Framework）

Scaled Agile, Inc.。https://scaledagileframework.com

Agile Release TrainsとProgram Incrementsを軸とする、より規定的な大規模フレームワーク。

## Claude Codeスキル仕様

### [CC26] Extend Claude with skills / Skill authoring best practices

Anthropic, *Extend Claude with skills*, current page retrieved 2026-07-25.

https://code.claude.com/docs/en/skills

Anthropic, *Skill authoring best practices*, current page retrieved 2026-07-25.

https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

本スキルが従う仕様・慣行：

- エントリーポイントは`SKILL.md`。個人スキルは`~/.claude/skills/<skill-name>/SKILL.md`、プロジェクトスキルは`.claude/skills/<skill-name>/SKILL.md`。
- YAML frontmatterの`description`は第三者視点で、何を行い、いつ使うかを具体的なトリガー語とともに示す。`when_to_use`は追加のトリガー表現に使える。
- 詳細資料はスキルディレクトリ内に置き、`SKILL.md`から直接（1階層で）参照する。参照ファイル同士のネストした参照は避ける。
- 100行を超える参照ファイルには目次を置く。
- `SKILL.md`本体は500行未満に保ち、詳細は参照資料へ分離する。
- 決定的な計算はClaudeに再現させず、`scripts/`配下のスクリプトを実行させる。`${CLAUDE_SKILL_DIR}`でスキルの設置場所によらずスクリプトを参照できる。

## 引用ルール

- Scrumの必須事項を述べるときは`[SG20, p.X]`を付ける。
- アジャイルの価値・原則を根拠にするときは`[AM01]`を付ける。
- フロー指標やWIP制限は`[KGS21, p.X]`を付ける。
- EBMまたはDORAの指標は、適用範囲と注意点を併記する。
- スケーリングフレームワーク（Nexus/LeSS/SAFe）は、Scrum Guide自体の一部ではなく別の実践体系として出典を分けて引用する。
- 心理的安全性について因果を断定しない。研究の設計と適用範囲を超えて一般化しない。
- 原文引用は必要最小限にし、引用符とページを付ける。通常は正確に要約して出典を示す。
- 出典間で矛盾があれば、Scrumの定義はScrum Guideを優先し、相違を明示する。
