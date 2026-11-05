# Feature Specification: 実行の証拠で、葉・親・システムの検証を別々に判定する(引き継ぎ書 Phase 3)

**Feature Branch**: `feat/change-assurance`(`feat/goal-refinement` から分岐)

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "Phase 2 から先も順に実装"(2026-11-06)

**要旨**: 新しい自作の親スキル `change-assurance` を加える。このスキルは、実装の後に、要求グラフの受け入れ条件ごとの検証の結果と、その証拠(どのコミットで、何が、どこで実行されたか)を**検証の記録**に集め、同梱の検査器の**保証の判定**で `pass`・`fail`・`blocked` を返す。判定は、葉の合格から親の合格を合成せず、別のコミットの証拠、AI の自己申告だけの証拠、実行していない検査、分類できないリスク、承認のない高リスクの変更、承認のないテストの弱体化を、合格とみなさない。テスト結果の JUnit XML から検証の記録の項目を作る取り込みも同梱する。判定が保証するのは記録の整合だけであり、記録された証拠が真であることは、証拠の出どころ(CI など)が担う。

**利用者の指示と、Claude が決めた既定**: 利用者は Phase 2 以降を順に実装するよう指示した。Claude は次の既定を選んだ。いずれも Git の履歴から戻せる。

| # | 論点 | 根拠 | Claude が選んだ既定と理由 |
|---|---|---|---|
| D1 | 範囲 | 引き継ぎ書 §21.3 | 検証の記録、保証の判定、JUnit XML の取り込み、保証レビュー役の指示文までとする。業務のリポジトリの CI・CodeQL・IaC の実際の経路への接続は、それらが分からないため作らず、取り込みは JUnit XML(pytest と Jest が出力できる)と手で書く項目に限る |
| D2 | 置き場所 | 引き継ぎ書 §19.3 の `change-assurance`(親スキル) | 自作スキル `.claude/skills/change-assurance/` を作る。spec 058 の親スキルとして、子に `problem-definition`、`goal-refinement`、`coder` を宣言する。子はどれも自分の子を宣言しないため、一段の制限に合う |
| D3 | 要求グラフの読み方 | spec 058 はパスでの参照を禁じる | 検査器は `goal-refinement` の検査器を呼ばず、判定に要る範囲(ノードの ID、受け入れ条件の ID と水準)だけを自分で読む。要求グラフの構造の検査は、手順の中で先に `goal-refinement` の判定で行う |
| D4 | 失敗と止まるの区別 | 引き継ぎ書 §21.3 の判定規則 | `fail` は、必須の検査が `failed` か、承認が却下されたとき。`blocked` は、検査の証拠が足りない(`not_run`、`blocked`、別のコミット、AI の申告だけ、理由のない `not_applicable`)、リスクを分類できない、必要な承認がないとき。どちらも合格ではない |
| D5 | リスクの分類 | 引き継ぎ書 §19.7(高・中・低・未分類を排他的に評価する) | 検証の記録の `risk.class` は `low`・`medium`・`high`・`unclassified` のいずれかとする。`unclassified` と欠落は `blocked`。`high` は、実装担当と別の人の `approved` の承認を要する。権限の拡大、公開範囲の拡大、資源の削除・置換を記録した変更は `high` でなければならない |
| D6 | AI のレビューの扱い | 引き継ぎ書 §21.3「独立したAIの同意も証拠ではなく仮説的な指摘」 | 証拠の種類が `ai_review` だけの検査は `passed` とみなさない |

**Authority**: 本仕様が正である。設計の出典は引き継ぎ書 §21.3(Phase 3)と §19.7(リスク別の処理)、要求グラフの形式は spec 059 と spec 060 である。

## 用語

spec 059 と spec 060 の用語(要求グラフ、受け入れ条件、水準 L1〜L3、問題カード、判定、反証役、引き継ぎ書)は、そのまま使う。

- **検証の記録**: 1つの変更について、審査の対象のコミット、実装担当、リスクの分類、承認、受け入れ条件ごとの検査の状態と証拠、テストの変更、インフラの変更を書いた JSON。引き継ぎ書の `verification-manifest` に当たる。
- **検査の状態**: `passed`(合格)、`failed`(不合格)、`not_run`(実行していない)、`blocked`(証拠を集められなかった)、`not_applicable`(この変更に当てはまらない。理由が要る)のいずれか。
- **証拠**: 検査の結果を示す記録。種類(`ci_job`・`local_run`・`scanner`・`human_review`・`ai_review`)、参照先(CI のジョブの URL、ログのパスなど)、その結果を得たコミットを持つ。
- **保証の判定**: 要求グラフと検証の記録を受け取り、`pass`・`fail`・`blocked` を理由とともに返す検査器の動き方。
- **保証レビュー役**: 実装の文脈から切り離され、要求グラフ、差分、生の証拠だけを読み、親とシステムの合格の主張に異議を出す、読み取り専用のサブエージェント。その指摘は証拠ではなく、反証の記録と同じく対応を要する指摘である。
- **規則 M-xx、A-xx、J-xx**: 本仕様の規則の名前。M は検証の記録の形式、A は保証の判定、J は JUnit XML の取り込みの規則である。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 葉が合格でも、親やシステムの検証の失敗・欠落を合格にしない (Priority: P1)

**Independent Test**: 要求グラフと検証の記録の正例と負例を判定にかけ、判定と規則を確かめる。

**Acceptance Scenarios**:

1. **P3-01・T-04** **Given** 葉の L1 はすべて `passed`、親の L2 の統合認可の検査が `failed`、**When** 判定する、**Then** `fail` である。
2. **P3-02** **Given** L1 と L2 は `passed`、L3 の API 互換の検査が `failed`、**Then** `fail` である。
3. **P3-03** **Given** 通常系は `passed`、他者の ID での取得を拒否する負例の検査が `failed`、**Then** `fail` である。
4. **P3-04・T-06** **Given** 証拠のコミットが審査の対象と異なる `passed`、**Then** `blocked` で、理由は古い証拠である。
5. **P3-05・T-05** **Given** 証拠の種類が `ai_review` だけの `passed`(例: 「CodeQL に問題なし」という AI の文)、**Then** `blocked` である。
6. **P3-08** **Given** 証拠の収集が失敗して `blocked` の検査、**Then** `blocked` である。
7. **Given** 要求グラフの受け入れ条件のうち、検証の記録にない条件、**Then** `blocked` である(未実行として扱う)。
8. **Given** すべての受け入れ条件が、審査の対象のコミットの `ci_job` か `local_run` の証拠で `passed`、リスクが `low`、**Then** `pass` で、終了コードは 0 である。

### User Story 2 - リスクと承認、テストの弱体化、インフラの変更で止める (Priority: P1)

**Acceptance Scenarios**:

1. **T-10** **Given** リスクが `unclassified`、または `risk` がない検証の記録、**Then** `blocked` である。
2. **Given** リスクが `high` で承認がない、または承認者が実装担当と同じ、**Then** `blocked` である。**Given** 実装担当と別の人の `approved`、**Then** 承認の規則を満たす。**Given** `rejected` の承認、**Then** `fail` である。
3. **P3-06** **Given** 承認のないテストの削除・スキップ・期待値の弱体化を記録した検証の記録、**Then** `blocked` である。
4. **P3-07** **Given** 権限の拡大を記録したのに、リスクが `high` でない検証の記録、**Then** `blocked` で、理由は高リスクへの格上げである。

### User Story 3 - テスト結果を検証の記録へ取り込み、親スキルの手順で回す (Priority: P2)

**Acceptance Scenarios**:

1. **Given** JUnit XML(テストケースの名前か、プロパティ `acceptance_id` に受け入れ条件の ID を持つ)と要求グラフ、**When** 取り込む、**Then** 受け入れ条件ごとに、すべて合格なら `passed`、1件でも失敗・エラーなら `failed`、スキップだけ・該当なしなら `not_run` の項目が、指定したコミットと参照先とともに出力される。
2. **Given** `<!DOCTYPE` や `<!ENTITY` を含む XML、**When** 取り込む、**Then** 終了コード 2 で拒否する(外部実体や実体の展開による攻撃を避ける)。
3. **Given** 変更後のリポジトリ、**When** `tests/run-config-pyramid.sh` を実行する、**Then** 親スキル `change-assurance` と宣言した子の規則(spec 058)を含め、すべて通る。

### Edge Cases

- **判定の合格の意味**: `pass` は、すべての受け入れ条件に、審査の対象のコミットに対する人や機械の実行の証拠があり、リスクと承認とテストとインフラの規則に合うことだけを意味する。証拠の参照先が本当にその結果を示すかは確かめない。
- **複数の検査を1つの受け入れ条件に**: 1つの受け入れ条件には1つの検査の項目を対応させる。複数のテストケースは、取り込みで1つの項目にまとめる。

## Requirements *(mandatory)*

- **FR-001**: 検査器 `scripts/assure.py` は、`check MANIFEST`(検証の記録の形式の検査、規則 M-00〜M-02)、`gate GRAPH MANIFEST`(保証の判定、規則 A-01〜A-07)、`collect-junit REPORT --graph GRAPH --commit SHA --ref REF`(取り込み、規則 J-01〜J-02)の3つの動き方を持つ。欄と規則の詳細は [contracts/manifest.md](contracts/manifest.md) にある。
- **FR-002**: 判定の規則は次のとおりとする。どれか1つでも満たさなければ、D4 に従い `fail` か `blocked` とし、理由をすべて示す。

  | 規則 | 満たす条件 | 満たさないとき |
  |---|---|---|
  | A-01 | 要求グラフのすべての受け入れ条件に、検証の記録の検査がちょうど1つある。グラフにない ID の検査がない | `blocked` |
  | A-02 | `passed` の検査の証拠は、種類が `ai_review` でなく、参照先が空でなく、コミットが `reviewed_commit` と一致する | `blocked` |
  | A-03 | すべての検査が `passed` か、理由のある `not_applicable` である | `failed` があれば `fail`、ほかは `blocked` |
  | A-04 | `risk.class` が `low`・`medium`・`high` のいずれかである | `blocked` |
  | A-05 | `high` なら、`implementer` と別の人の `approved` の承認が1件以上あり、`rejected` の承認がない | 承認がなければ `blocked`、`rejected` なら `fail` |
  | A-06 | テストの変更(削除・スキップ・弱体化)には、`implementer` と別の人の `approved_by` がある | `blocked` |
  | A-07 | 権限の拡大、公開範囲の拡大、資源の削除・置換を記録したなら、`risk.class` が `high` である | `blocked` |

- **FR-003**: 判定の結果は、spec 059 の出力の欄に加えて、`decision`(`pass`・`fail`・`blocked`)、`reasons`(`{rule_id, message}`)、`levels`(水準ごとの状態の件数)を持つ。終了コードは `pass` で 0、`fail` と `blocked` で 1、入力を解釈できなければ 2 とする。
- **FR-004**: 検査器は、読み取りだけを行い、ネットワークに接続せず、入力をコードとして実行しない。XML は `<!DOCTYPE` と `<!ENTITY` を含めば読まない。入力は 5 MiB までとする。
- **FR-005**: `change-assurance` の `SKILL.md` は、親スキルとして子を宣言し、問題の定義 → 分解と判定(`goal-refinement`)→ 実装 → 証拠の収集 → 保証の判定 → 必要なら保証レビュー役、の手順と、`fail` と `blocked` のそれぞれの戻り先を定める。保証レビュー役の指示文を `references/` に置く。
- **FR-006**: `tests/run-config-pyramid.sh` の自作スキルの一覧と名前のパターン、README の英日、まとめの検査スクリプトを更新する。

## Success Criteria *(mandatory)*

- **SC-001**: User Story 1〜3 の各負例が期待する判定と規則で失敗し、正例が合格することを、実装の前に失敗するテストで確かめる。
- **SC-002**: spec 059 の「後の Phase へ送るテスト」T-04・T-05・T-06・T-10 が、本仕様のテストとして実装され、まとめの検査スクリプトの `NOT RUN` から外れる。
- **SC-003**: 既存の検査がすべて通る。

## Assumptions

- 業務のリポジトリの CI の結果は、JUnit XML として得られるか、手で検証の記録に書ける(確度: 中)。
- 承認者の本人確認は、この検査器の範囲外である。`approvals` の `by` は記録された名前であり、なりすましは防がない(確度: 高)。

## Out of Scope

CI のジョブの結果の自動取得(GitHub の API など)、CodeQL・Dependabot・IaC の plan の解析、レビューカード(Phase 4)、比較実験(Phase 5)、承認者の本人確認。
