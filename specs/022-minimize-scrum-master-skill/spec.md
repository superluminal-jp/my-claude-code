# 機能仕様書: scrum-masterスキルを公式Scrum Guideの内容へ最小化する

**フィーチャーブランチ**: `022-minimize-scrum-master-skill`

**作成日**: 2026-08-15

**ステータス**: Draft

**入力**: ユーザーからの説明: 「@.claude/skills/scrum-master/references/2020-Scrum-Guide-US.pdf @.claude/skills/scrum-master/references/2020-Scrum-Guide-Japanese.pdf 公式スクラムガイドの内容に基づくものに @.claude/skills/scrum-master/ スキルを最小化。/clarifier」

## 明確化

### セッション 2026-08-15

- Q: scrum-masterスキルを「公式Scrum Guide(2020)ベース」に最小化するとして、どこまで削るか？ → A: Scrum Guideのみに厳格化——SG20（英語版／日本語版PDF）に明記された定義・役割・イベント・作成物・価値基準のみを残し、Nexus Guide, EBM Guide, Kanban Guide, DORA, 心理的安全性研究, Agile Retrospectives, Coaching Agile Teams, アンチパターン記事（SAP/ZBS/AAP）, LeSS/SAFe/Scrum@Scaleへの参照・引用・推奨内容を全て削除する。
- Q: scripts/flow_metrics.py（Kanban Guide由来）はどうするか？ → A: 削除する。
- Q: Scrum Guideが規定しないHOW（レトロスペクティブの進め方、コーチングスタンス、ファシリテーション技法）はどうするか？ → A: 削除し、Scrum Guideが言う各イベントの目的とタイムボックスのみ残す。

## ユーザーシナリオとテスト *(必須)*

### ユーザーストーリー1 - 出典を単一の規範資料に絞り込む（優先度: P1）

scrum-masterスキルの保守担当者として、スキルの参照資料が公式Scrum Guide（2020年版）のみを出典とするようにしたい。現状は補完的なフレームワークや研究知見が入り混じっているため、スキル内のあらゆる主張を単一の規範的出典まで遡れるようにする。

**この優先度である理由**: これが今回の依頼の中核であり、これが実施されない限り他の変更に意味がない。同時に最も削除範囲が大きく（=リスクが高い）ステップでもあるため、最初に検証することで、実は他の部分の前提になっていた内容が残っていないかを早期に洗い出せる。

**独立したテスト方法**: `.claude/skills/scrum-master/` 配下の全ファイルを対象に `[SG20]` 以外の引用タグ（例：`[NXG]`, `[AM01]`, `[EBM24]`, `[KGS21]`, `[DORA26]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]`, `[SC@S]`）を検索し、一致がゼロであることを確認する。あわせて `references/sources.md` にScrum Guideのエントリのみが残っていることを確認する。

**受け入れシナリオ**:

1. **Given** 現状の`references/sources.md`が14種類の出典を引用している、**When** 最小化を適用する、**Then** `references/sources.md`にはScrum Guide（2020年版）のエントリとその引用ルールのみが残る。
2. **Given** `references/scaling-frameworks.md`、`references/measurement-and-diagnostics.md`、`references/anti-patterns-and-coaching.md`、`references/facilitation-and-coaching.md`、`scripts/flow_metrics.py`（および`__pycache__`）が現在存在し、いずれも非Scrum-Guide資料のみを出典とする、**When** 最小化を適用する、**Then** これらのファイルはスキルディレクトリ内に一つも存在しない。
3. **Given** `references/scrum-master-role.md`に「コーチングスタンス」セクションが存在し、当該ファイル自身がGuide本文に記載がない（`[ICA]`由来）と明記している、**When** 最小化を適用する、**Then** そのセクションはファイルから削除されている。

---

### ユーザーストーリー2 - イベントに関する記述をGuideが述べる目的とタイムボックスに限定する（優先度: P2）

scrum-masterスキルを使うScrum Masterとして、各Scrumイベントに関する記述をScrum Guide自身が述べる目的とタイムボックスのみに限定したい。実務上の慣行（レトロスペクティブの形式、ファシリテーションの進行例、コーチングスタンスの選び方）を、あたかもGuideが要求しているかのように提示されたくない。

**この優先度である理由**: これは非Scrum-Guide資料のうち分量として2番目に大きく、かつ最も「有用そうだから」という理由で暗黙のうちに復活しやすい部分である。ユーザーストーリー1の出典整理が済んでいることを前提とする。

**独立したテスト方法**: スキルに「スプリントレトロスペクティブはどう進めればよいか」と尋ね、回答がGuideの目的（「品質と効果を高める方法を計画する」）とタイムボックス（1か月Sprintで最大3時間）のみを述べ、段階的なファシリテーション構造や特定のレトロ形式を提示しないことを確認する。

**受け入れシナリオ**:

1. **Given** ユーザーがスプリントレトロスペクティブの進め方を尋ねる、**When** 最小化されたスキルが回答する、**Then** 回答はそのイベントに関するGuide記載の目的とタイムボックスのみを述べ、段階的なファシリテーション構造・特定のレトロ形式・改善実験テンプレートを提示しない。
2. **Given** ユーザーがどのコーチングスタンス（ティーチャー／メンター／ファシリテーター／コーチ）を取るべきか尋ねる、**When** 最小化されたスキルが回答する、**Then** Guideがそのようなスタンス分類を定義していないため、スタンスの分類を提示しない。
3. **Given** ユーザーがデイリースクラム、スプリントプランニング、スプリントレビュー、プロダクトバックログリファインメントについて尋ねる、**When** 最小化されたスキルが回答する、**Then** 回答はScrum Guideに記載された目的・参加者・（Guideがタイムボックスを定めている場合は）タイムボックスに限定される。

---

### ユーザーストーリー3 - スキル自身のルーティングにリンク切れや範囲逸脱を残さない（優先度: P3）

このリポジトリの保守担当者として、`SKILL.md`の参照ファイル表とワークフロー記述が、最小化後も存在するファイルと実践のみを指すようにしたい。リンク切れや、スキル自身が宣言する縮小後のスコープと矛盾する記述を残したくない。

**この優先度である理由**: これはユーザーストーリー1・2が完了して初めて意味を持つ後始末であり、それ自体に独立したコンテンツはなく、残った内容との整合性を取るだけの作業である。リスクは最も低いが、上記の削除後にスキルを実用可能な状態に保つためには必須である。

**独立したテスト方法**: 変更後に`SKILL.md`（および残存する`references/*.md`）を読み、すべての相対Markdownリンクが実在するファイルに解決すること、およびフロー指標の計算・スケーリングフレームワークの推奨・コーチングスタンスの選択をスキルに指示するセクションが存在しないことを確認する。

**受け入れシナリオ**:

1. **Given** `SKILL.md`の参照ファイル表に、削除対象の各ファイルへの行が現状存在する、**When** 最小化を適用する、**Then** 残る各行はすべて実在するファイルを指す。
2. **Given** ユーザーが新しいスコープの範囲外の質問をする（例：「私たちのチームのサイクルタイムを計算して」「どのスケーリングフレームワークを採用すべきか」）、**When** 最小化されたスキルが回答する、**Then** スキルは削除済みの資料に基づいて回答するのではなく、それが範囲外である旨を述べる。

---

### エッジケース

- 最小化後にユーザーがNexus/LeSS/SAFe/Scrum@Scaleの推奨を明示的に求めた場合はどうなるか？ スキルは範囲外である旨を述べ、削除済みの内容の記憶から回答することはない。
- ユーザーがチケットデータからフロー指標（Cycle Time、WIP、Throughput、Work Item Age）の計算をスキルに求めた場合はどうなるか？ スキルはその機能が削除され範囲外になったことを述べ、その場しのぎの計算や代替の見積もりを行わない。
- 残すファイル内の相互参照（例：`scrum-master-role.md`や`scrum-framework.md`が削除済みファイルへリンクしている箇所）はどうなるか？ そうしたリンクはすべて削除または更新し、スキル内のどこにもリンク切れが残らないようにする。
- 現行のより広いスコープの設計を確立した過去のscrum-master関連スペック（016, 017, 018）はどう扱うか？ それらは遡って修正しない。本フィーチャーは、それらと矛盾する箇所についてはスコープを上書きする決定として扱う。

## 要件 *(必須)*

### 機能要件

- **FR-001**: スキルの出典一覧（`references/sources.md`）は、公式Scrum Guide（2020年版、`references/`配下に既に存在する英語版・日本語版PDF）のみを規範的または補完的出典として引用しなければならない（MUST）。現在含まれる他の出典エントリ（Nexus Guide, Manifesto for Agile Software Development, Evidence-Based Management Guide, The Kanban Guide for Scrum Teams, DORA metrics, Edmondsonの心理的安全性研究, Agile Retrospectives, Coaching Agile Teams, Scrum.org/Zombie Scrum/Agile Allianceのアンチパターン資料, LeSS, SAFe, Scrum@Scale）はすべて削除しなければならない（MUST）。
- **FR-002**: `references/scaling-frameworks.md`は削除しなければならない（MUST）。その内容（Nexus, LeSS, SAFe, Scrum@Scale）はいずれもScrum Guideが定義するものではない。
- **FR-003**: `references/measurement-and-diagnostics.md`は削除しなければならない（MUST）。その指標に関する記述（フロー指標、EBMの重要価値領域、DORA指標）はKanban Guide、EBM Guide、DORAを出典としており、Scrum Guideを出典としていない。
- **FR-004**: `references/anti-patterns-and-coaching.md`は削除しなければならない（MUST）。そのアンチパターン分類はScrum.org、Zombie Scrum、Agile Allianceの資料を出典としており、Scrum Guideを出典としていない。
- **FR-005**: `references/facilitation-and-coaching.md`は削除しなければならない（MUST）。そのファシリテーション技法とコーチングスタンスのモデルはCoaching Agile Teams、心理的安全性研究、出典のない実務慣行を出典としており、Scrum Guideを出典としていない。
- **FR-006**: `scripts/flow_metrics.py`およびその`__pycache__`成果物は削除しなければならない（MUST）。それが計算するフロー指標（Cycle Time、Work Item Age、Throughput、SLE）はKanban Guideの概念であり、Scrum Guideの概念ではない。
- **FR-007**: `references/scrum-master-role.md`は、Scrum Masterの中核的アカウンタビリティ、Scrum Team／Product Owner／組織への奉仕、役割の境界に関するScrum Guide根拠の内容のみを残さなければならない（MUST）。コーチングスタンスの分類（ティーチャー／メンター／ファシリテーター／コーチ／対立の航行者）は削除しなければならない（MUST）。
- **FR-008**: スキル内のどこかに残る各Scrumイベント（Sprint、Sprint Planning、Daily Scrum、Sprint Review、Sprint Retrospective、Product Backlog Refinement）に関する記述は、Scrum Guide自身が述べる目的・参加者・タイムボックスに限定しなければならない（MUST）。Scrum Guideに記載のない進行技法、レトロスペクティブの形式、アジェンダの内訳、改善実験のテンプレート、ファシリテーションの手順は残してはならない（MUST NOT）。
- **FR-009**: 残存するいかなるファイルも、FR-002からFR-006で削除される対象（コーチングスタンス、アンチパターン分類、フロー指標スクリプト、スケーリングフレームワーク、測定・診断ガイダンス）へのリンク・参照・誘導を含んではならない（MUST NOT）——すべての相対リンクは実在するファイルに解決しなければならない（MUST）。
- **FR-010**: `SKILL.md`の説明文、`when_to_use`のトリガー文言、および明記された原則は、スキルを公式Scrum Guide（2020年版）のみに限定されたものとして記述しなければならない（MUST）。スケーリング、フロー指標の計算、アンチパターン分類、ファシリテーション技法のコーチングをカバーしているかのような含意を残してはならない（MUST NOT）。
- **FR-011**: ユーザーが最小化後のスキルではカバーしなくなった話題（Nexus/LeSS/SAFe/Scrum@Scaleのスケーリング、フロー指標／ベロシティの計算、特定のレトロスペクティブ形式、コーチングスタンスの選択など）について尋ねた場合、スキルは削除済みの資料から回答を作り上げるのではなく、それがScrum Guideのみに基づくガイダンスの範囲外である旨を明示しなければならない（MUST）。
- **FR-012**: スキル内に現在存在するScrum Guide直接根拠の内容——経験主義の三本柱、Scrumの5つの価値基準、Product Owner／Scrum Master／Developersのアカウンタビリティ、各イベントのGuide記載の目的とタイムボックス、作成物のコミットメント、「スクラムの一部だけを導入することはスクラムとは言えない」という規定（Guide p.13）、Guide本文が文字通り述べるScrum Masterの境界——は、最小化後のスキルでも参照可能な状態を維持しなければならない（MUST）。

## 成功基準 *(必須)*

### 測定可能な成果

- **SC-001**: スキル内の全ファイルに対して、Scrum Guide（2020年版）以外の出典を検索した結果が0件になる。
- **SC-002**: スキルの`references/`ディレクトリには、Scrum Guideの2つのPDFと、内容がすべてScrum Guideのみに遡れるMarkdownファイルのみが残る。`scripts/`ディレクトリには計算用スクリプトが一つも残らない。
- **SC-003**: 6つのScrumイベントそれぞれについて「このイベントはどう進めるか」とスキルに尋ねると、Guide記載の目的・参加者・タイムボックスのみが返り、追加のファシリテーション技法・形式・テンプレートは回答に含まれない。
- **SC-004**: 削除された話題（スケーリングフレームワークの選定、フロー指標の計算、コーチングスタンスの選択、アンチパターン分類）についてスキルに尋ねると、試行の100%で明示的な範囲外表明が返り、削除済み資料に基づく回答は返らない。
- **SC-005**: スキル内に残るすべての相対Markdownリンクが、スキルディレクトリ内に実在するファイルに解決する（リンク切れゼロ）。

## 前提条件

- `references/`配下に既に存在する2つのScrum Guide PDF（`2020-Scrum-Guide-US.pdf`、`2020-Scrum-Guide-Japanese.pdf`）が引き続き唯一の規範的出典資料であり、本変更によって新たな出典資料は追加しない。
- 「公式Scrum Guide」とは、現在`references/sources.md`で`[SG20]`として引用されているものと同じ、2020年11月版（Ken Schwaber and Jeff Sutherland）を指す。他の版や将来の改訂版は対象外とする。
- 日本語版Scrum GuideのPDF自身に含まれる訳者付録（「2020年版での変更点」セクション、日本語版pp.16–17）は、第三者資料ではなく公式翻訳PDFに内包された公式Guide文書の一部として扱い、`[SG20, JA pp.16–17]`として引用し続けてよい。
- 本最小化は、より広いスコープの設計を確立した過去のscrum-master関連スペック（`016-scrum-master-skill`、`017-scrum-master-rewrite`、`018-remove-solo-practice`）と矛盾する箇所について、それらを上書きする決定として扱う。これらのスペック自体を遡って編集することはしない。
- スキルの起動トリガー（`.claude/rules/skill-routing.md`、`when_to_use`フィールド）は本変更の対象外である——本フィーチャーはスキルの内容を絞り込むものであり、いつスキルにルーティングされるかを変更するものではない。
- FR-011で定める範囲外応答を超える移行ガイドやユーザー向けの告知は不要である。過去に削除対象の内容（スケーリングの助言、フロー指標、コーチングスタンス）に依拠していた会話には、今後はその話題が範囲外であると伝えるのみでよい。
