# Feature Specification: Scrum Guide 作成物・イベント テンプレート

**Feature Branch**: `023-scrum-guide-templates`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "公式Scrum Guide（2020年版）が定めるArtifacts（Product Backlog、Sprint Backlog、Increment）と、それぞれに対応し透明性と集中を高めるCommitment（Product Backlog→Product Goal、Sprint Backlog→Sprint Goal、Increment→Definition of Done）、および各Scrumイベント（Sprint Planning、Daily Scrum、Sprint Review、Sprint Retrospective）について、すぐに使い始められるMarkdown形式のテンプレートを作成する。配置場所：.claude/skills/scrum-master/ スキル配下の新規ディレクトリ（例：references/templates/）。形式：Markdownファイル。中身の粒度：Scrum Guideが明示する構造（各作成物・コミットメントの定義、各イベントの目的・タイムボックス・扱う内容）のみ。進行手順やファシリテーション技法など、Scrum Guideに明記のないHOW的内容は含めない。出典：既存の references/sources.md（[SG20]のみ）、references/scrum-framework.md、references/scrum-master-role.md と整合させる。SKILL.mdの参照ファイル表・成果物を作るセクションから新規テンプレートへ導線を張る。"

## Clarifications

`/clarifier`（AskUserQuestion）で以下を確定した。

- **対象範囲**: 「作成物」はScrum Guideが定める作成物（Product Backlog／Sprint Backlog／Increment）そのものを指す。scrum-masterスキルの「成果物を作る」節が指す軽量成果物（アジェンダ等）や、pptx/docxで作るレトロデッキ等は対象外。
- **対象成果物**: Markdown形式で、(1) Product Backlogのための Product Goal、(2) Sprint Backlogのための Sprint Goal、(3) Incrementのための Definition of Done ——それぞれの作成物と、透明性・集中を高める対応コミットメントをセットで扱う。加えて、Scrum Guideに明示があるイベント（Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）用テンプレートも作成する。
- **粒度**: 構造のみ。見出し・記入欄などScrum Guideが定める範囲に限定し、進行手順やファシリテーション技法は含めない（022番feature「scrum-masterスキル最小化」で確立した「Scrum Guideのみを規範とする」方針を継続する）。
- **配置場所**: `.claude/skills/scrum-master/` スキル配下の新規ディレクトリ（Proximity原則に沿う）。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 作成物（Product Backlog／Sprint Backlog／Increment）のテンプレートをすぐ使う (Priority: P1)

チームやScrum Masterが、Product Backlog・Sprint Backlog・Incrementを整理する際、白紙から項目を洗い出すのではなく、Scrum Guideが定める属性とコミットメント（Product Goal／Sprint Goal／Definition of Done）の記入欄が揃ったテンプレートを開いて、そのまま埋め始められる。

**Why this priority**: 3つの作成物とそのコミットメントはScrumの中核であり、他の何を後回しにしても最初に整えるべき土台である。

**Independent Test**: `.claude/skills/scrum-master/references/templates/` 配下の3ファイル（Product Backlog／Sprint Backlog／Increment）を開き、Scrum Guideが定める属性・コミットメント欄が過不足なく揃っていることを確認できる。

**Acceptance Scenarios**:

1. **Given** 新しいプロダクトのProduct Backlogを整理したい、**When** Product Backlogテンプレートを開く、**Then** description／order／estimate／valueの記入欄と、Product Goalの記入欄がある。
2. **Given** Sprintを計画したい、**When** Sprint Backlogテンプレートを開く、**Then** Sprint Goal（why）・選択したProduct Backlog items（what）・Incrementを届ける計画（how）の3欄がある。
3. **Given** Incrementの完成条件を明確にしたい、**When** Incrementテンプレートを開く、**Then** Definition of Doneの記入欄と、DoDを満たした時点でIncrementが生まれるという説明がある。

---

### User Story 2 - Scrumイベント（Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）のテンプレートをすぐ使う (Priority: P2)

Scrum Masterやチームが各イベントを準備する際、目的とタイムボックス、Scrum Guideが明示する検討項目が整理されたテンプレートを開いて、そのまま進行の骨組みとして使える。

**Why this priority**: 作成物の土台（P1）ほど基盤的ではないが、日々の運用で最も繰り返し使われる成果物であり、次に価値が高い。

**Independent Test**: `.claude/skills/scrum-master/references/templates/` 配下の4ファイル（Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）を開き、各イベントの目的・タイムボックス・Scrum Guideが定める検討項目が記載されていることを確認できる。

**Acceptance Scenarios**:

1. **Given** Sprint Planningを準備したい、**When** テンプレートを開く、**Then** Why／What／Howの3つの問いと、一月Sprintでの最大タイムボックス（8時間）が記載されている。
2. **Given** Daily Scrumを準備したい、**When** テンプレートを開く、**Then** 目的（Sprint Goalへの進捗の検査と適応）とタイムボックス（15分）が記載されている。
3. **Given** Sprint Reviewを準備したい、**When** テンプレートを開く、**Then** 目的（成果の提示とProduct Goalへの進捗確認、作業セッションでありステータス報告ではない旨）とタイムボックス（一月Sprintで最大4時間）が記載されている。
4. **Given** Sprint Retrospectiveを準備したい、**When** テンプレートを開く、**Then** 検査対象（個人・相互作用・プロセス・ツール・Definition of Done）とタイムボックス（一月Sprintで最大3時間）が記載されている。

---

### User Story 3 - SKILL.mdからテンプレートへ迷わず到達する (Priority: P3)

scrum-masterスキルを使う人が、既存の「参照ファイル」表または「成果物を作る」節から、新規テンプレート群の存在と場所を発見できる。

**Why this priority**: テンプレート自体の価値（P1・P2）に対し、発見可能性は補助的だが、導線がなければ死蔵する。

**Independent Test**: `SKILL.md` を開き、テンプレート群へのリンクが「参照ファイル」表または「成果物を作る」節のいずれかにあることを確認できる。

**Acceptance Scenarios**:

1. **Given** SKILL.mdを読んでいる、**When** 「成果物を作る」節または「参照ファイル」表を見る、**Then** 新規テンプレートディレクトリへのリンクがある。

---

### Edge Cases

- Scrum Guideに明記のない項目（見積もり手法の指定、レトロスペクティブの具体的技法など）を書きたくなった場合はどうするか？ → テンプレートにはそのための記入欄を設けない。Scrum Guide外の内容はテンプレートの範囲外である。
- 日本語版Scrum GuideのPDFは目次分だけページ番号が英語版より後ろにずれる（sources.mdに既知）。テンプレート内の出典表記はどう扱うか？ → 英語版のページ番号（`[SG20, p.X]`）と、Scrum Guide公式サイトの直リンクを用いる（実装中にユーザー指示で確定：テンプレートは単体で完結させ、リポジトリ内への相対リンクは一切排除する。公式URLへの直リンクのみ許容）。
- 新規テンプレートの内容が既存の `scrum-framework.md` や `scrum-master-role.md` の説明と重複する場合は？ → テンプレートは記入用の構造（見出し・記入欄）のみを持ち、詳細な説明・出典ページは既存ファイルに委ねる。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 新規ディレクトリ `.claude/skills/scrum-master/references/templates/` を作成すること。
- **FR-002**: `product-backlog.md` テンプレートを作成し、Product Backlog itemsの属性（description、order、estimate、value）の記入欄と、Product Goalの記入欄を含むこと [SG20, p.10]。
- **FR-003**: `sprint-backlog.md` テンプレートを作成し、Sprint Goal（why）・選択したProduct Backlog items（what）・Incrementを届けるための実行可能な計画（how）の3要素の記入欄を含むこと [SG20, p.9]。
- **FR-004**: `increment.md` テンプレートを作成し、Definition of Doneの記入欄と、DoDを満たした時点でIncrementが生まれるという定義の記載を含むこと [SG20, p.11]。
- **FR-005**: `sprint-planning.md` テンプレートを作成し、Scrum Guideが定める3つの問い（Why is this Sprint valuable? What can be Done? How will the work get done?）と、一月Sprintでの最大タイムボックス（8時間、Sprintが短い場合は通常より短い）を含むこと [SG20, p.8]。
- **FR-006**: `daily-scrum.md` テンプレートを作成し、目的（Sprint Goalへの進捗の検査とSprint Backlogの適応）とタイムボックス（15分）を含むこと [SG20, p.9]。
- **FR-007**: `sprint-review.md` テンプレートを作成し、目的（Sprintの成果を提示しProduct Goalへの進捗を検討する作業セッションであり、ステータス報告の場ではない旨）とタイムボックス（一月Sprintで最大4時間）を含むこと [SG20, p.9-10]。
- **FR-008**: `sprint-retrospective.md` テンプレートを作成し、検査対象（個人・相互作用・プロセス・ツール・Definition of Done）、目的（品質と効果を高める改善計画の作成）、タイムボックス（一月Sprintで最大3時間）を含むこと [SG20, p.10]。
- **FR-009**: 全テンプレートは、Scrum Guideに明示されていない進行手順・ファシリテーション技法・見積もり手法などのHOW的内容を一切含まないこと。
- **FR-010**: 各テンプレートは単体で完結すること（リポジトリ内の他ファイルへの相対リンクを含まない）。Scrum Guide由来の主張には `[SG20, p.X]` 形式の出典と、Scrum Guide公式サイト（scrumguides.org）への直リンクを付けること。
- **FR-011**: `SKILL.md` の「参照ファイル」表または「成果物を作る」節に、新規テンプレート群への導線（リンク）を追加すること。
- **FR-012**: 新規テンプレートは既存の `references/scrum-framework.md` および `references/scrum-master-role.md` の記述内容と矛盾しないこと。内容が重複する場合、詳細な説明・出典ページは既存ファイルに委ね、テンプレートは記入用の構造のみを提供する。
- **FR-013**: 新規テンプレートは全てMarkdown形式（`.md` 拡張子）で作成すること。

### Key Entities

- **Product Backlogテンプレート**: description／order／estimate／value属性を持つitem一覧の記入欄、Product Goalの記入欄。
- **Sprint Backlogテンプレート**: Sprint Goal欄、選択済みProduct Backlog items一覧欄、Incrementを届けるための計画欄。
- **Incrementテンプレート**: Definition of Doneの記入欄、Incrementの定義の記載。
- **イベントテンプレート（4種）**: Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospectiveそれぞれについて、目的欄・タイムボックス表示・Scrum Guideが定める検討項目の記入欄。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 7つのテンプレートファイル（Product Backlog／Sprint Backlog／Increment／Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）が `.claude/skills/scrum-master/references/templates/` 配下に存在する。
- **SC-002**: 各テンプレートは、開いた時点で見出しと記入欄が揃っており、追加の説明を読まずにそのまま埋め始められる。
- **SC-003**: 全テンプレートを対象に、022番feature（scrum-masterスキル最小化）で削除対象となった語彙（スケーリング、フロー指標、アンチパターン分類、コーチングスタンス、Nexus、LeSS、SAFe、Scrum@Scale等）を検索しても一致しない。
- **SC-004**: `SKILL.md` から新規テンプレート一覧への到達に必要な参照（クリック）が1回以内である。
- **SC-005**: 各テンプレートの主要な記入欄に対応する `[SG20, p.X]` 形式の出典と、Scrum Guide公式サイトへの直リンクが明示されている。テンプレート内にリポジトリ内ファイルへの相対リンクは存在しない。

## Assumptions

- テンプレートはこのリポジトリ内で人間またはAIが直接編集して使うMarkdownファイルであり、変数埋め込みや自動生成の仕組み（テンプレートエンジン）は不要である。
- Product Backlog refinement（作成物ではなくGuideが定める活動）は独立したテンプレートを持たない。既存の `scrum-framework.md` の記述で十分とする。
- Sprintそのもの（他のイベントを内包する1か月以内のタイムボックス）は独立したテンプレートを持たない。Sprint Planning／Review／Retrospectiveのテンプレートで実質的にカバーされる。
- 既存のスキル起動トリガー（`.claude/rules/skill-routing.md`、`SKILL.md` の `when_to_use`）はこの変更で変えない。
