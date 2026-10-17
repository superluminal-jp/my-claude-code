# Feature Specification: 公開文書の同期と振る舞い eval(スライス S6)

**Feature Branch**: `049-sync-readme-evals`

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "specs/043-related-doc-discovery/meta-spec.md のスライス S6。スキル側の README を新しい挙動に同期し、重複した Local modifications を統合して上流との差分を記録し、振る舞い eval の足場(3 ケース)を用意する。eval の実行は費用上限の承認後に別途行う。"

**Authority**: 範囲は [meta-spec.md](../043-related-doc-discovery/meta-spec.md) に従う。S1〜S5(前スライス)の挙動を記述する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - README が現在の挙動を正しく説明している (Priority: P1)

スキルを導入・利用する人が、スキル側の `README.md` を読んで、スクリプトの一覧(`find_related.py` を含む)、Stop ゲートの挙動(未処分の関連文書、報告の理由の質、助言のコメント、候補の上限)、設定(`related.*`)、既知の限界を、実際の挙動と一致した形で知る。

**Why this priority**: README は公開契約の入口で、以前の挙動のままだと、利用者が新しいゲートの止まる理由を理解できない。

**Independent Test**: README に、`find_related.py` のスクリプト表の行、ゲートの新しい検査の説明、`related.max_candidates` と `related.min_name_length` の記述、既知の限界(意味の妥当性は検査できない、パスの言及による処分の限界、定型句の一覧は固定)があり、リンク検査が通る。

**Acceptance Scenarios**:

1. **Given** 更新後の README、**When** スクリプトの表を読む、**Then** `find_related.py` の目的と Git が必要なことが書かれている。
2. **Given** 同じ README、**When** ゲートの挙動を読む、**Then** 未処分の関連文書(同じディレクトリ、名前参照、変更履歴)、報告の理由の質(空・定型句の拒否、文書の変更が無いときの根拠)、助言のみのコメント、上限と切り捨ての扱いが書かれている。
3. **Given** 同じ README、**When** 設定の節を読む、**Then** `related` の 2 つのキー、既定値、下限が書かれている。
4. **Given** 同じ README、**When** 既知の限界を読む、**Then** 少なくとも、意味の妥当性を検査できないこと、パスを言及すれば形式的でも通ること、履歴文書の多いプロジェクトでは `exclude_globs` の調整が前提であることが書かれている。

---

### User Story 2 - 上流との差分が 1 か所に記録されている (Priority: P2)

このスキルを上流から更新する人が、このコピーの上流との差分を、1 つの「Local modifications」の節で、漏れなく知る。

**Why this priority**: 現在は同名の節が 2 つあり内容が食い違っている。更新時に再適用すべき差分を誤る。

**Independent Test**: README に「Local modifications」の見出しが 1 つだけあり、決定記録のローカル規約(以前の 2 つの節の内容)と、近接文書の発見・処分の追加(スクリプト、ゲート、設定の検証、スキーマ、配置規則、書誌、手順書・規則の文言)が列挙されている。

**Acceptance Scenarios**:

1. **Given** 更新後の README、**When** 見出しを数える、**Then** 「Local modifications」は 1 つ。
2. **Given** その節、**When** 読む、**Then** 以前の 2 つの節の内容(Numbering と Language の追加、Local convention の追加)がすべて含まれ、新しい差分(`find_related.py`、`stop_gate.py`、`common.py` の検証の拡張、スキーマの `related`、`practices.md` の層・配置・近接性の節、書誌 4 件、`SKILL.md` と `rule.md` の文言、eval 3 件)が含まれる。

---

### User Story 3 - 振る舞いの eval 3 件の足場がある (Priority: P3)

保守者が、関連文書の更新、新しい公開契約への文書作成、内部リファクタでは何も作らない、の 3 つの振る舞いを `claude plugin eval` で測れる。実行は費用の上限をユーザーが承認した後に行う。

**Why this priority**: 仮定 A4(処分規則が効果を持つ)の検証手段を用意する。ただし実行にはモデル呼び出しの費用がかかるため、足場までをこのスライスの範囲とする。

**Independent Test**: `evals/` に新しいケース 3 つがあり、それぞれ `case.yaml`、`prompt.md`、`fixture.sh`(実行すると Git リポジトリを作る)、1 つ以上の採点基準を持つ。単体テストが構造を検査し、`claude plugin validate --strict .`(CLI があれば)が通る。

**Acceptance Scenarios**:

1. **Given** 隣に README を持つモジュールにオプションを追加する依頼、**When** eval の足場を見る、**Then** README が新しいオプションに言及していること、完了報告があること、スキルが呼ばれたことを採点する基準がある。
2. **Given** 文書が無いパッケージに新しい公開モジュールを追加する依頼、**When** eval の足場を見る、**Then** Markdown の文書が書かれたこと、決定記録と変更履歴が作られていないこと、完了報告があることを採点する基準がある。
3. **Given** 非公開の補助関数の名前変更、**When** eval の足場を見る、**Then** 文書が作られも編集もされないこと、`Documentation impact: none` と報告されることを採点する基準がある。
4. **Given** 各ケースの `fixture.sh`、**When** 一時ディレクトリで実行する、**Then** 初期コミットのある Git リポジトリができる。

---

### Edge Cases

- README の節の順序と、既存の記述(インストール、要件、セキュリティ)は変えない。
- eval のケース名は既存の 3 つと重複しない。
- eval の実行結果(`evals/results/`)は無視される(既存の `.gitignore`)。
- 実行しないため、eval の採点基準が実際の出力に合うかは未検証である。README の eval の節に、その旨を書く。
- 上流との差分の一覧は、事実(実際に変更したファイル)に基づき、推測を書かない。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: スキル側の `README.md` は、スクリプトの表に `find_related.py`(目的、Git が必要)を加え、レイアウトの節にも反映しなければならない。
- **FR-002**: README の「How the gate behaves」と「Making it mandatory」の表は、ゲートの新しい検査(未処分の関連文書、報告の理由の質、文書の変更が無いときの根拠)を記述しなければならない。
- **FR-003**: README の設定の節は、`related.max_candidates`(既定 10、1 以上の整数)と `related.min_name_length`(既定 6、1 以上の整数)を記述しなければならない。
- **FR-004**: README は、既知の限界を明記しなければならない: 意味の妥当性は検査できない、パスの言及によって形式的でも処分済みになる、定型句の一覧は固定で設定では拡張できない、履歴文書(凍結された仕様など)が多いプロジェクトでは `exclude_globs` の調整が前提である。
- **FR-005**: README の「Local modifications」は 1 つの節に統合され、以前の 2 つの節の内容と、新しい差分(FR の User Story 2 に列挙したもの)をすべて含まなければならない。
- **FR-006**: `evals/` に、ケース `updates-adjacent-doc`、`creates-doc-for-new-contract`、`no-creation-for-internal-refactor` を追加しなければならない。各ケースは既存のケースと同じ形式(`case.yaml`、`prompt.md`、実行可能な `fixture.sh`、`graders/`)で、決定的な採点基準のみを持つ(判定用のモデルは使わない)。
- **FR-007**: README の eval の節は、6 つのケースの目的を述べ、新しい 3 ケースは足場のみで実行結果が未検証であること、実行は費用の上限を承認した後に行うことを書かなければならない。
- **FR-008**: 次を自動テストにしなければならない(実装より先に書き、失敗を確認する): (a) eval の 6 ケースの構造(`case.yaml` の名前がディレクトリ名と一致、`prompt.md` の front matter に `description`、`fixture.sh` を実行すると初期コミット付きの Git リポジトリができる、採点基準が 1 つ以上)、(b) README の「Local modifications」が 1 つ、(c) README が `find_related.py` と `related.max_candidates` に言及。
- **FR-009**: 既存の単体テスト 136 件は変更後もすべて通らなければならない。リンク検査はエラー 0。スクリプト、スキーマ、`SKILL.md`、`rule.md` は変更しない。eval は実行しない。

### Key Entities

- **eval ケース(Eval case)**: 依頼文、初期状態を作る手順、採点基準の組。
- **Local modifications**: 上流のパッケージとの、このコピーの差分の一覧。
- **既知の限界(Known limits)**: 検査できないこと、または形式的に通ることの記録。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: eval の 6 ケースすべてが構造検査を通り、新しい 3 ケースの `fixture.sh` が初期コミットのある Git リポジトリを作る(テストで確認)。
- **SC-002**: README の「Local modifications」の見出しが 1 つで、以前の 2 つの節の差分と新しい差分の全項目が含まれる(テストで項目の語句を確認)。
- **SC-003**: README が `find_related.py`、`related.max_candidates`、`related.min_name_length`、既知の限界の 4 項目に言及する(テストで確認)。
- **SC-004**: 既存の単体テスト 136 件がすべて通り、追加したテストにより合計が増える。`check_links.py --changed` のエラーが 0。

## Assumptions

- eval の採点基準が実際のモデル出力に合うかは、実行するまで分からない。足場の妥当性は、構造検査と fixture の実行までで確認する。
- 実行の費用上限(`--max-cost-usd`)はユーザーが決める。このスライスでは実行しない。
- README は英語で書かれている(既存に合わせる)。
- スキル側の README の更新は、リポジトリ直下の `README.md` / `README.ja.md` の更新を要しない(管理対象パスとインストーラの挙動は変わらない)。
