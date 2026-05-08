# Feature Specification: Ubiquitous Language Skill Simplification

**Feature Branch**: `feature/003-ubiquitous-language`
**Created**: 2026-05-09
**Status**: Draft
**Input**: User description: "ユビキタス言語作成のスキル の実装をより簡潔なものに改善。ユビキタス言語とcontext boundaryのファイルは docs/ フォルダ内に格納するようにする。 claude の skill としてスラッシュコマンド一つ ubiquitous-language のみとする。トリガーする際の自動検出の方法をベストプラクティスを参照して CLAUDE.md に端的に記載。最初にトリガーした時にファイルがなかったらファイルを作成するようにする。 speckitへの言及は排除。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 初回実行：UL ファイルの自動作成 (Priority: P1)

`docs/ubiquitous-language.md` が存在しないプロジェクトで `/ubiquitous-language` を実行すると、スキルがファイル不在を検知し、業務イベント起点の対話でドメイン語彙を引き出したのち `docs/ubiquitous-language.md` と `docs/context-map.md` を作成する。

**Why this priority**: ファイルが存在しなければそれ以降のすべての機能が動かない。存在確認と初期ファイル作成は最小 MVP そのもの。

**Independent Test**: UL ファイルのないプロジェクトで `/ubiquitous-language` を実行すると、(a) スキルがファイル不在を告知し、(b) 業務イベント起点の質問を 1 問以上行い、(c) 回答後に `docs/ubiquitous-language.md` と `docs/context-map.md` が生成されること。

**Acceptance Scenarios**:

1. **Given** `docs/ubiquitous-language.md` が存在しない、**When** ユーザーが `/ubiquitous-language` を実行する、**Then** スキルはファイル不在を検知し「業務で実際に起きる出来事を 5〜10 個挙げてください」という業務イベント起点の質問から対話を始める
2. **Given** ユーザーが業務イベントを列挙した、**When** スキルが用語を抽出する、**Then** 用語・定義・文脈・状態/ルール・例・反例・実装名の 7 フィールドを持つ UL テーブルを含む `docs/ubiquitous-language.md` を作成する（ユーザー確認後に書き込む）
3. **Given** ファイルを書き込む前、**When** スキルが差分を提示する、**Then** ユーザーが明示的に確認した後に限りファイルへの書き込みが行われる

---

### User Story 2 - 既存 UL のメンテナンスと用語追加 (Priority: P1)

`docs/ubiquitous-language.md` が存在するプロジェクトで `/ubiquitous-language` を実行すると、スキルは現在の会話から新規ドメイン用語を検出し、既存 UL との整合性を確認して更新候補を提示する。

**Why this priority**: 初期作成と同じくらい重要な継続更新ユースケース。UL は 1 回作って終わりではなく、会話のたびに育てるものである。

**Independent Test**: UL ファイルが存在する状態で `/ubiquitous-language` を実行すると、(a) セッション中に検出した未登録の業務用語の一覧が提示され、(b) 追加・スキップ・カスタム定義が選択でき、(c) 確認後に UL ファイルが更新されること。

**Acceptance Scenarios**:

1. **Given** `docs/ubiquitous-language.md` が存在する、**When** ユーザーが `/ubiquitous-language` を実行する、**Then** スキルはセッション中に検出した未登録用語の一括提案を提示する
2. **Given** 用語追加の提案が表示された、**When** ユーザーが「全て追加」または個別に選択する、**Then** ユーザー確認後に `docs/ubiquitous-language.md` が更新される
3. **Given** 同一用語が複数のコンテキストで異なる意味を持つ、**When** スキルが衝突を検出する、**Then** (a) BC ごとに別エントリ化、(b) 片方を改名、の 2 択を提示し、`docs/context-map.md` を更新する

---

### User Story 3 - 会話中の自動検出（パッシブ収集） (Priority: P2)

`docs/ubiquitous-language.md` が存在するプロジェクトでは、Claude が通常会話中に業務用語の候補をパッシブに検出してキューに積み、会話の自然な区切りで `/ubiquitous-language` 実行を促す。

**Why this priority**: 最も価値あるドメイン語は設計相談や障害分析など日常会話の中で自然に登場する。コマンド外でも収集できることで UL の鮮度が保たれる。

**Independent Test**: UL ファイルが存在する状態で、コマンドなしの通常会話に「注文が確定された」のような業務イベント表現を含めると、(a) 会話の区切りに「以下の用語を UL に追加しますか？」という提案が表示され、(b) ユーザーが承認後に UL ファイルが更新されること。

**Acceptance Scenarios**:

1. **Given** `docs/ubiquitous-language.md` が存在する、**When** ユーザーが通常会話で業務用語を含むメッセージを送る、**Then** スキルは応答を中断せず候補をキューに積む
2. **Given** キューに候補がある、**When** 新規業務語を含まない会話ターンが来る（自然な区切り）、**Then** 未登録候補の一括提案を表示する
3. **Given** 曖昧語（データ・情報・管理・ユーザー等）がアーティファクトに含まれる、**When** スキルが検出する、**Then** 引用付きで UL 登録済みの代替候補を提示する

---

### Edge Cases

- `docs/` ディレクトリが存在しない → スキルが `docs/` を作成してからファイルを生成する
- ユーザーが初回質問をスキップ → `[NEEDS DOMAIN INPUT]` マーカーで保留し次回再提示
- 同一用語が複数 BC に存在 → context-map に記録、BC 修飾子（例: 「顧客（販売）」）を提案
- 会話言語が日本語・英語混在 → 用語フィールドは原語、実装名フィールドは英語

## Requirements *(mandatory)*

### Functional Requirements

#### A. ファイル管理

- **FR-001**: スキルは `/ubiquitous-language` 実行時に `docs/ubiquitous-language.md` の存在を確認し、不在の場合はブートストラップフローを開始する
- **FR-002**: UL ファイルのパスは `docs/ubiquitous-language.md`、コンテキストマップのパスは `docs/context-map.md` とする（`.specify/` を使わない）
- **FR-003**: `docs/` ディレクトリが存在しない場合、スキルは自動的に作成してからファイルを生成する
- **FR-003b**: ブートストラップ時に `docs/ubiquitous-language.md` と `docs/context-map.md` を同時に作成する。`docs/context-map.md` は空のテーブル（見出し行のみ）で初期化し、Bounded Context 間の関係が生じたタイミングで追記する
- **FR-004**: ファイルへの書き込みは必ずユーザー確認後に行う（差分提示 → 確認 → 書き込みの順）

#### B. スラッシュコマンド

- **FR-005**: ユーザー向けインタフェースはスラッシュコマンド `/ubiquitous-language` 一つのみとする（サブコマンドなし）
- **FR-006**: コマンド実行時の動作は `docs/ubiquitous-language.md` の存在有無で自動的に切り替わる（初回ブートストラップ / 既存メンテナンス）

#### C. ブートストラップ（初回作成）

- **FR-007**: ファイル不在時は業務イベント起点の質問（「業務で実際に起きる出来事を 5〜10 個挙げてください」）からエリシテーションを開始する
- **FR-008**: 各用語エントリは 7 フィールド（用語・定義・文脈・状態/ルール・例・反例・実装名）を持つ単一テーブル行として作成する
- **FR-009**: 未入力フィールドは `[NEEDS DOMAIN INPUT]` マーカーで保留し、次回実行時に再提示する

#### D. 既存 UL のメンテナンス

- **FR-010**: `/ubiquitous-language` 実行時、セッション中に検出した未登録用語を一括提案として表示する
- **FR-011**: 同一用語の意味が複数の Bounded Context で衝突する場合、コンテキスト別エントリ化または改名の 2 択を提示し、`docs/context-map.md` を更新する
- **FR-012**: 曖昧語ウォッチリスト（データ・情報・処理・管理・ステータス・フラグ・有効・完了・対象・ユーザー）の出現を検出し、UL 登録済みの代替候補を提示する。ユーザーは `/ubiquitous-language` 実行中のインタラクションでウォッチリストへの語の追加・削除を行える（変更は差分確認後に `docs/ubiquitous-language.md` の `## Watchlist` セクションへ書き込む）

#### E. パッシブ収集（自動検出）

- **FR-013**: 通常会話中に業務イベント表現（動詞+名詞の過去形・受動形）またはドメイン固有語が検出されたとき、スキルはパッシブに候補をキューに積む（応答を中断しない）。`docs/ubiquitous-language.md` の存在は前提としない
- **FR-014**: キューに 1 件以上の候補がある状態で、直前のターンに新規業務語の候補がゼロだった場合（自然な区切り）、または `/ubiquitous-language` を明示実行した場合に、一括提案として表示する
- **FR-015**: ファイル不在状態で業務用語が検出された場合、スキルはブートストラップフロー（FR-007）を提案する。ファイルが存在すれば既存エントリとの整合確認に進む

#### F. 非機能

- **FR-016**: スキルの記述（SKILL.md）に speckit/spec-kit への言及を含めない
- **FR-017**: CLAUDE.md の自動検出ルールに、会話内容（業務イベント表現・ドメイン固有語の出現）によるトリガー条件を 1〜2 文で記載する

### Key Entities

- **UL ファイル**: `docs/ubiquitous-language.md` — 用語テーブルを `## Bounded Context: <名前>` セクションで保持するマークダウンファイル
- **コンテキストマップ**: `docs/context-map.md` — Bounded Context 間の用語関係（同名異義・同義語・同一）を記録するマークダウンファイル
- **用語エントリ**: 7 フィールド（用語・定義・文脈・状態/ルール・例・反例・実装名）を持つテーブル行
- **候補キュー**: セッション内メモリ。会話中に検出した未登録用語を保持し、区切りで一括提案する

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/ubiquitous-language.md` が存在しない状態で `/ubiquitous-language` を実行すると、1 回の対話セッション（15 分以内）で 5 語以上のエントリを持つ UL ファイルが生成される
- **SC-002**: 100% のファイル書き込みがユーザー確認後に行われる（差分未提示のサイレント書き込みがゼロ）
- **SC-003**: スキルの SKILL.md と CLAUDE.md に speckit/spec-kit への言及が一切含まれない
- **SC-004**: 会話中の業務用語検出が AI の応答を遅延させない（ユーザーが気づくような遅延なし）
- **SC-005**: 曖昧語ウォッチリストのいずれかを含む会話で `/ubiquitous-language` を実行すると、100% の出現箇所に代替候補が提示される
- **SC-006**: 同一語の Bounded Context 間意味衝突が検出された場合、100% のケースで分割または改名の選択肢が提示される（サイレント統合ゼロ）

## Assumptions

- UL ファイルは `docs/ubiquitous-language.md` の単一ファイルとする（Bounded Context が増えた場合は同ファイル内に `## Bounded Context: <名前>` セクションで分割）
- コンテキストマップは `docs/context-map.md` の単一ファイルとする
- 自動検出のトリガー条件は「`docs/ubiquitous-language.md` の存在」であり、speckit の `.specify/` ディレクトリは参照しない
- CLAUDE.md への自動検出ルール記載は `.claude/CLAUDE.md`（プロジェクトスコープ）に行う
- 既存の `.claude/skills/ubiquitous-language/` ディレクトリは引き続き使用し、SKILL.md を書き換える
- テンプレートファイル（`ubiquitous-language-template.md`、`context-map-template.md`）は `docs/` 配置に合わせて内容を調整するが、ファイルの場所はスキルディレクトリ内に留める
- パッシブ収集のキューはセッション内メモリのみ（ファイルに書き込まない）
- v1 では Bounded Context ごとのファイル分割は行わない（単一ファイル内のセクション分割で対応）

## Clarifications

### Session 2026-05-09

- Q: CLAUDE.md の自動検出トリガー条件はどのアプローチか（ファイル存在 / ディレクトリ存在 / 会話内容検知）→ A: 会話内容チェック。業務イベント表現を検知したときだけ有効化（ファイル存在不問）
- Q: 複数 Bounded Context を単一ファイルで管理する際のセクション見出し形式 → A: `## Bounded Context: <bc-name>` 形式。略語 "BC" は使用せず、ファイル最上位では "Bounded Context" の略さない形で示す
- Q: ウォッチリストの拡張方法（FR-012） → A: `/ubiquitous-language` 実行中のインタラクションで追加・削除。変更は差分確認後に `docs/ubiquitous-language.md` の `## Watchlist` セクションへ書き込む
- Q: `docs/context-map.md` の作成タイミング → A: ブートストラップ時に `docs/ubiquitous-language.md` と同時に空ファイルとして作成
- Q: パッシブ収集候補の提示タイミング（「自然な区切り」の定義） → A: キューに 1 件以上ある状態で直前のターンの新規候補がゼロだったとき
