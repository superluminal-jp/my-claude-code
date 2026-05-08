# Feature Specification: Ubiquitous Language Auto-Builder

**Feature Branch**: `feature/003-ubiquitous-language`
**Created**: 2026-05-08
**Status**: Draft
**Input**: User description: "Eric Evans の DDD におけるユビキタス言語をプロジェクトごとに自動的に作成する。必要に応じて自動発火し、作成のための質問をユーザーに与える。10 のベストプラクティス（業務イベント起点・状態と振る舞い・境界づけられた文脈ごとの差・コード/DB/API/画面文言反映・曖昧語回避・反例定義・状態遷移明示・ドメイン専門家起点・軽量保持・継続更新）を適用し、加えてコンテキスト長圧縮のための専門用語など他のプラクティスも調査して取り込む。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 新規プロジェクトでのユビキタス言語ブートストラップ (Priority: P1)

スペック作成を始めた段階で、システムが当該プロジェクトのユビキタス言語（以下 UL）が未整備であることを検知し、業務イベント起点の対話的質問でドメイン専門家・開発者から最小限の語彙を引き出す。出力として、境界づけられた文脈（Bounded Context、以下 BC）ごとの軽量な UL 表が 1 ファイルずつ生成される。

**Why this priority**: UL は仕様作成・実装・テストすべての出発点となる設計資産であり、これが欠落するとそれ以降の生成物（spec/plan/tasks/コード）が曖昧語ベースで進み、後段で手戻りが発生する。最初の 1 回が最大の価値を生む。

**Independent Test**: 任意の業務領域の自然文（例: 「契約の更新と解約を扱う SaaS」）だけを入力として与え、システムが (a) 業務イベント候補のリスト、(b) BC 候補、(c) 各 BC の UL 表（用語・定義・文脈・状態/ルール・例・反例・実装名）を作成すること。完成した UL をドメイン担当役のユーザーがレビューし、80% 以上の用語を「自分たちの業務語と一致する」と確認できれば成功。

**Acceptance Scenarios**:

1. **Given** 既存プロジェクトに UL ファイルが存在しない、**When** ユーザーが `/speckit-specify` を起動する、**Then** システムは UL 不在を検知し「業務で実際に起きる出来事を 5〜10 個挙げてください」という業務イベント起点の質問から対話を始める
2. **Given** ユーザーが業務イベントを列挙した、**When** システムが用語抽出を行う、**Then** 各イベントに登場する役割・概念・状態を抽出し、軽量 UL 表（用語/定義/文脈/状態・ルール/例/反例/実装名の 7 項目）を BC ごとに 1 ファイル生成する
3. **Given** UL 生成中にユーザーが「顧客」のような複数 BC で意味の異なる語を出した、**When** システムが意味の差を検知する、**Then** 「営業」「請求」「サポート」など BC 候補を提示し、それぞれの定義を別個に問い直す
4. **Given** 軽量保持の方針、**When** 1 BC あたりの用語数が任意の上限（既定 30 語）を超えそうになる、**Then** システムは新 BC 分割か用語統合を提案する

---

### User Story 2 - 通常会話・仕様/計画/タスク生成時の自動発火と曖昧語検知 (Priority: P2)

スペックキットコマンド（`/speckit-specify` `/speckit-clarify` `/speckit-plan` `/speckit-tasks` 等）の各ライフサイクルイベントに加え、コマンドを使わない通常の会話中にも、システムは (a) 既存 UL に未登録の業務概念、(b) 曖昧語ウォッチリスト（データ・情報・処理・管理・ステータス・フラグ・有効・完了・対象・ユーザー など）の出現、(c) UL 用語と実装名候補のドリフトを継続検出する。検知した候補は中断なくキューに蓄積し、会話の自然な区切りまたは次のライフサイクルイベント時に一括提示する。

**Why this priority**: UL 収集のきっかけは speckit コマンドの外にある。設計相談・障害分析・コードレビュー依頼など日常会話の中でこそドメイン語が最も素直に出る。コマンド起動時に限定すると、最も価値ある収集機会を取りこぼす。

**Independent Test**: speckit コマンドを一切使わず、業務説明（例: 「注文が確定されると在庫引当が走る」）を含む通常のチャットメッセージを送ると、システムが (a) 「注文」「確定」「在庫引当」を UL 候補として検出し、(b) 曖昧語があれば引用付きで置換候補を提示し、(c) 会話の区切りに「以下の用語を UL に追加しますか？」という一括確認を行うこと。確認後、UL ファイルが正しく更新される。

**Acceptance Scenarios**:

1. **Given** UL に「契約管理者」が登録済み、**When** ユーザーが通常会話中に「ユーザーが…」と書く、**Then** システムはキューに記録し、会話区切りで引用付きの置換候補（「契約管理者・利用者・請求担当者」）を提示する
2. **Given** speckit コマンドを使わない日常会話中、**When** 「注文が確定された」「在庫が引き当てられた」などの業務イベント表現が登場する、**Then** システムはそれらを UL 未登録候補として検出しキューに積む
3. **Given** プラン生成中（speckit コマンド経由）、**When** 状態を持つ UL 用語（例: 注文）に対して状態遷移が未記述である、**Then** システムは「正常遷移と例外遷移をそれぞれ列挙してください」と促し、得られた遷移を UL の「状態/ルール」欄に追記する
4. **Given** タスク生成中、**When** 実装名候補（例: `Order.process()`）が UL の振る舞い名（例: `Order.confirm()`）と乖離する、**Then** システムはドリフトをハイライトし整合化を提案する
5. **Given** ユーザーが提案を却下しカスタム名を選択した、**When** 提案が確定する、**Then** UL 側の「実装名」欄が当該カスタム名で更新され、以降の整合性検査の基準になる

---

### User Story 3 - 境界づけられた文脈ごとの分割と意味衝突の解決 (Priority: P2)

複数の BC で同一語が異なる意味を持つ状況をシステムが検出し、BC ごとの定義に分割して保持する。全社共通語への過度な統一を抑止する。各 BC の UL は独立ファイルで保持され、同じ語が複数 BC に存在する場合は対応関係（コンテキストマップ風メタデータ）が記録される。

**Why this priority**: ベストプラクティス #3（同じ単語の意味が違う領域を分ける）の実装。単一プロジェクト内でも BC が複数に育つことが多く、初期に分割の枠組みがないと用語が肥大化し意味が混ざる。

**Independent Test**: 同じ語（例: 「顧客」）について、ユーザーが「営業では商談中または契約済みの法人」「請求では請求先として登録された法人」「サポートでは問い合わせ権限を持つ利用者」と異なる定義を入力すると、3 つの BC 別 UL ファイルにそれぞれ「顧客」のエントリが作成され、各エントリに対応する実装名（例: `SalesAccount` / `BillingParty` / `SupportContact`）が記録されること。

**Acceptance Scenarios**:

1. **Given** UL に複数の BC が登録済み、**When** 同じ語に異なる定義が入力される、**Then** システムは衝突を提示し「同名・異義として BC ごとに別エントリ化する」「BC を統合する」「片方の名前を変える」の 3 選択肢を提示する
2. **Given** BC 別エントリ化が選択された、**When** UL が更新される、**Then** 各 BC ファイルに独立エントリが作られ、コンテキストマップに「同名異義（synonym across BCs）」のメタが記録される

---

### User Story 4 - コンテキスト長圧縮のための語彙運用 (Priority: P3)

UL 自体を AI 対話のコンテキスト長圧縮資産として運用する。確定した UL 用語は (a) 後続の AI 生成物（spec/plan/tasks/レビュー）で短縮シンボルとして優先使用され、(b) 長い説明文の代わりに 1 語で参照可能になる。これにより複雑概念の繰り返し説明が減り、コンテキスト枠を温存できる。

**Why this priority**: スペックキット運用は長コンテキスト化しやすい。UL を「圧縮辞書」としても扱う発想は本タスクで明示的に求められた追加プラクティスであり、副次的だが大きな実利がある。基本機能（P1/P2）が動いた後の最適化として位置付ける。

**Independent Test**: UL に 20 語登録済みの状態で、長文スペックを入力すると、システムが (a) UL 用語に置き換え可能な冗長な記述を検出、(b) 用語置換による短縮版を提示、(c) 短縮後の意味が原文と等価であることをユーザーが確認できる差分形式で示すこと。

**Acceptance Scenarios**:

1. **Given** UL に「支払い承認済み」が登録済み、**When** スペックに「決済事業者から承認コードを受領した状態」と書かれている、**Then** システムは UL 用語による参照「支払い承認済み」への置換候補を提示する
2. **Given** UL 用語が安定運用フェーズに入った、**When** AI が新規アーティファクトを生成する、**Then** 説明的な長文より UL 用語を優先利用する

---

### Edge Cases

- ドメイン専門家が物理的に不在で、ユーザーが開発者のみのとき → 契約書・FAQ・運用マニュアル等の供給文書からの抽出に切り替え、抽出元を出典として記録する
- 既存ソースコードが UL より先行しており命名規則が崩壊しているとき → コード走査は本機能の必須範囲外（Assumptions 参照）。検知範囲は AI 生成アーティファクトのみとし、既存コードのリネームは別タスクとして提案するに留める
- 現場語が曖昧（例: 「アクティブ契約」とだけ呼ばれ境界が不明）なとき → そのまま採用せず、含む/含まない（反例）の対話で精緻化してから登録する
- ユーザーが質問に回答しない／スキップを希望するとき → 該当用語を `[NEEDS DOMAIN INPUT]` マーカーで保留し、後続のいずれかのライフサイクルイベントで再質問する。スキップが連続する用語は警告対象
- BC が初期段階で 1 つしかないとき → 単一 BC で開始し、用語数が閾値超または意味衝突が検知された時点で分割提案する
- 自動発火がユーザーの作業を中断するノイズになるとき → 提案はキューに蓄積し、会話の自然な区切りまたはライフサイクルイベント終端で一括提示する（中断ではなく集約）
- 通常会話中に speckit コンテキスト（`.specify/` ディレクトリ）が存在しないとき → UL 収集は行わず「プロジェクトに spec-kit を初期化すると UL を蓄積できます」と一度だけ案内する
- UL ファイルとスペックの整合チェックが循環参照になるとき → UL を信頼源とし、スペック側を更新候補として提示する一方向の整合方針を採る
- プロジェクト言語が日本語と英語の混在のとき → 業務語は原語（日本語）、実装名は英語、両方のフィールドを 1 エントリ内で保持する

## Requirements *(mandatory)*

### Functional Requirements

#### A. ライフサイクルとトリガ

- **FR-001**: System MUST detect whether the project has an existing UL artifact at the conventional location and, if absent, initiate UL bootstrapping when invoked — whether triggered by an external lifecycle hook (e.g., `extensions.yml`), a direct slash command, or a general conversation in which domain vocabulary or business events are detected in the user's first message
- **FR-002**: The UL skill MUST respond when invoked at the following lifecycle points: spec creation, clarification, plan, tasks, checklist, implement, analyze, user-reported incidents/inquiries, **and any general conversational exchange where domain vocabulary not present in the UL appears**. Registration of lifecycle triggers is the responsibility of the calling system (e.g., via `extensions.yml` hooks); the skill remains caller-agnostic
- **FR-003**: System MUST allow users to defer or skip auto-firing per invocation or per conversational session, while still recording the deferred prompts so they re-surface at the next trigger point

#### A2. 通常会話中のパッシブ収集

- **FR-030**: During any conversational exchange where no spec-kit command is active, System MUST passively monitor user messages for business events (verb-form occurrences), domain roles, state names, and business rules; candidate terms MUST be queued without interrupting the conversation
- **FR-031**: Queued candidates from general conversation MUST be surfaced as a batch proposal ("以下の用語を UL に追加しますか？") at the first natural conversation pause (defined as a user message that does not introduce new business vocabulary) or at the next spec-kit lifecycle event, whichever comes first
- **FR-032**: System MUST NOT initiate passive collection when no UL store is discoverable (default path: `.specify/ubiquitous-language/`); in that case the system MAY note once that UL collection requires initializing the UL store, regardless of which project tooling is in use

#### B. 業務イベント起点の対話

- **FR-004**: System MUST begin elicitation with business events (verb-form occurrences, e.g., "注文が確定された") rather than nouns, and only derive concepts/states/exceptions from those events
- **FR-005**: System MUST extract from each elicited event the affected roles, concepts, states, and exception paths, and map them into draft UL entries
- **FR-006**: System MUST source candidate terms from domain-expert language artifacts when supplied (contracts, manuals, FAQs, ops docs); when domain-expert input is unavailable, the system MUST mark resulting entries as developer-derived and flag them for later confirmation

#### C. 用語エントリ構造

- **FR-007**: Each UL entry MUST carry the seven fields: 用語 (term), 定義 (definition), 文脈 (bounded context), 状態・ルール (state/rules), 例 (positive example), 反例 (counter-example), 対応する実装名 (implementation names: class/method/table/API/event/UI label)
- **FR-008**: System MUST require both 例 and 反例 for every entry; entries missing either MUST be marked incomplete and re-surfaced at the next lifecycle event
- **FR-009**: For terms with lifecycle, System MUST capture explicit state transitions including normal paths and exception paths (e.g., 在庫引当失敗 → 入荷待ち, 出荷指示済み → キャンセル不可)

#### D. 曖昧語・否定語の検出と置換

- **FR-010**: System MUST maintain a watchlist of vague/forbidden terms (initial set: データ, 情報, 処理, 管理, ステータス, フラグ, 有効, 完了, 対象, ユーザー) and detect their occurrence in any AI-generated artifact (spec, plan, tasks, conversation)
- **FR-011**: On detection, System MUST quote the offending location and propose UL-grounded replacements (e.g., "ユーザー" → "契約管理者 / 利用者 / 請求担当者") before the artifact is finalized
- **FR-012**: System MUST allow the user to extend or override the watchlist per project

#### E. 境界づけられた文脈

- **FR-013**: System MUST support multiple BCs per project, with one UL artifact file per BC
- **FR-014**: When a single term receives conflicting definitions, System MUST prompt the user to choose: (a) split into BC-specific entries, (b) merge BCs, or (c) rename one term — and MUST NOT silently unify into a global glossary
- **FR-015**: System MUST record cross-BC term relationships (synonym, identical concept, same-name-different-meaning) in a lightweight context map metadata file

#### F. 実装名との整合とドリフト検知

- **FR-016**: For each UL entry with an implementation-name field, System MUST compare AI-generated artifact contents (spec/plan/tasks) against the recorded implementation names and flag drift (e.g., spec says `Order.process()` while UL says `Order.confirm()`)
- **FR-017**: On drift detection, System MUST present the divergent location and offer three resolutions: align artifact to UL, update UL implementation-name field, or split into a new term
- **FR-018**: System MUST NOT silently rewrite either the UL or the artifact without explicit user confirmation

#### G. 軽量保持

- **FR-019**: System MUST keep each BC's UL artifact within a configurable size budget (default: ≤ 30 entries, fits on one screen at standard reading width); when the budget is exceeded the system MUST propose BC split or term consolidation rather than allowing unbounded growth
- **FR-020**: System MUST keep entries to a single tabular row; multi-paragraph definitions are rejected and replaced with the structured 7-field form
- **FR-021**: System MUST avoid duplicating any term within a BC; same-term-different-BC is allowed and tracked via FR-015

#### H. コンテキスト長圧縮

- **FR-022**: After UL stabilizes for a BC, System SHOULD prefer UL terms as compressed shorthand in subsequent AI-generated artifacts, replacing long descriptive paraphrases with the canonical term
- **FR-023**: System MUST detect AI-generated paraphrases that match an existing UL definition and propose substitution with the canonical term
- **FR-024**: System MUST preserve linkability — every UL term used in an artifact MUST resolve to its BC's UL entry without ambiguity

#### I. 継続更新と運用

- **FR-025**: System MUST re-validate UL completeness at each lifecycle event and surface any entries with missing 例/反例/状態遷移/実装名
- **FR-026**: System MUST treat any conversational moment where the question "つまり何を指していますか？" arises as a maintenance trigger and immediately propose adding/refining the relevant entry
- **FR-027**: System MUST record the lifecycle event under which each UL entry was created or last modified, to support auditability without growing the entry itself

#### J. 言語と多言語

- **FR-028**: System MUST support bilingual entries: 用語 in the project's domain language (Japanese by default for this project), 実装名 in the implementation-code language (English by default)
- **FR-029**: System MUST not force translation — if the domain expert speaks only Japanese, the canonical term remains Japanese and only the implementation-name field uses English

### Key Entities

- **Ubiquitous Language Artifact (BC-scoped)**: One markdown file per BC. Contains the UL table and metadata (BC name, owner, last-update lifecycle event, size budget)
- **Term Entry**: 用語 / 定義 / 文脈 / 状態・ルール / 例 / 反例 / 実装名 — the seven canonical fields plus modification metadata
- **Bounded Context (BC)**: Named scope within which the UL is internally consistent. Identified explicitly by user or inferred from feature areas
- **Domain Event**: Past-tense business occurrence (e.g., 「注文が確定された」). Primary unit of elicitation; the source from which terms/states/exceptions are derived
- **State Transition**: For stateful terms, the directed graph of normal and exception transitions, attached to the entry's 状態・ルール field
- **Vague-Term Watchlist**: Per-project list of terms whose occurrence triggers a clarification prompt. Default seeded with 10 forbidden words; user-extensible
- **Lifecycle Trigger**: Named event at which UL re-validation and candidate surfacing runs. Two classes: (1) spec-kit command events (specify, clarify, plan, tasks, checklist, implement, analyze, user-reported incident); (2) general conversational trigger — any exchange outside spec-kit commands where domain vocabulary appears. Both classes share the same queue and batch-proposal mechanism
- **Context Map**: Lightweight metadata file recording cross-BC term relationships (same-name-different-meaning, identical concept, synonym)
- **Drift Report (transient)**: In-conversation finding listing artifact locations that diverge from UL implementation names, presented at lifecycle event boundaries rather than mid-task

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a new project with a 1–2 paragraph domain description, an initial UL with at least 5 core terms across at least 1 BC can be produced in under 15 minutes of elicitation
- **SC-002**: 100% of UL entries contain all seven canonical fields, including 例 and 反例; entries missing any field are flagged as incomplete in the artifact
- **SC-003**: 100% of vague-watchlist terms appearing in a finalized AI-generated artifact are flagged before the artifact is accepted; zero silent slip-throughs
- **SC-004**: 100% of stateful terms include explicit normal and exception state transitions
- **SC-005**: When a term's meaning conflicts across BCs, 100% of cases are split into per-BC entries and recorded in the context map; zero silent unifications
- **SC-006**: Each BC's UL artifact stays within the configured size budget (default ≤ 30 entries); when exceeded, the system surfaces a split/consolidate proposal within the same lifecycle event
- **SC-007**: At domain-expert review, ≥ 80% of UL terms are confirmed as "wording the business actually uses"; terms below this threshold are flagged for refinement
- **SC-008**: Drift between UL implementation names and AI-generated artifact identifiers is detected with zero false negatives on the test corpus; user confirmation is requested on 100% of detected drifts before any update
- **SC-009**: After UL stabilization, the average AI-generated artifact length for a recurring concept reduces by ≥ 20% via UL-term substitution, without loss of meaning verifiable in diff review
- **SC-010**: UL re-validation and candidate detection — whether triggered by a spec-kit lifecycle event or a general conversational exchange — completes within a budget that does not noticeably interrupt user flow (target: under 5 seconds per trigger); conversational collection must not delay AI responses in the main conversation thread
- **SC-011**: A UL artifact remains readable on a single screen per BC at standard reading width (verifiable by line/character budget)

## Assumptions

- The system operates in two modes: (1) spec-kit mode — triggered by speckit commands and integrated via the existing `extensions.yml` lifecycle hook mechanism; (2) conversational mode — active in any AI conversation where a `.specify/` project context is detected, regardless of whether a speckit command was issued. Both modes share the same UL artifact store and queue mechanism
- UL artifacts are stored as markdown files under a project-conventional path (default: `.specify/ubiquitous-language/<bounded-context>.md`), with a sibling `context-map.md` for cross-BC relationships. Storage path is configurable
- The default canonical domain language is Japanese for this project; implementation names default to English. Bilingual support is required, machine translation is not
- Drift detection scope is limited to AI-generated spec-kit artifacts (spec/plan/tasks/clarify/checklist/implement/analyze outputs and conversational drafts). Active scanning of project source code, databases, or external APIs is out of scope for v1 and will be addressed via a future code-walker integration; v1 still records the implementation-name field for human-driven verification
- BCs are user-declared with system-suggested defaults inferred from feature areas; the system never silently merges BCs
- All UL writes (creation, edit, deletion of entries) require explicit user confirmation; the system never auto-commits UL changes without surfacing a diff
- Vague-term watchlist defaults to the 10 Japanese forbidden words listed in the source request; localization to other languages is straightforward but out of scope for v1
- Auto-firing is opt-out per invocation, not opt-in; users can defer with a single keystroke and prompts re-surface at the next lifecycle event
- The system relies on the user (or domain expert in conversation) for ground truth; no external knowledge sources are queried for term meanings
- Domain expert availability is intermittent. The system degrades gracefully: if no domain expert is present, terms are tagged as "developer-derived (pending domain confirmation)" rather than blocked
- The 30-entries-per-BC default budget is heuristic and adjustable per project via config; the budget exists to enforce ベストプラクティス #9 (軽量保持)
- "Context length compression" is treated as a secondary benefit, not a primary feature; its measurable target (SC-009) is opportunistic, not a blocking criterion
- The system does not enforce naming conventions on implementation names beyond UL/artifact consistency — it only flags drift, not style
- This feature does not replace `/speckit-clarify`; clarification questions raised by the UL builder feed into, and may anticipate, the existing clarify workflow
