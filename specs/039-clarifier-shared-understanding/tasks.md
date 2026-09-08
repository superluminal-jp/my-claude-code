# Tasks: `clarifier` の「意図の共通認識形成 ＋ 形式的要件化」への拡張

**入力**: `specs/039-clarifier-shared-understanding/` の設計文書
**前提**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**構成**: タスクはユーザーストーリー単位でグループ化される。

**テストタスクの位置づけ**: spec.md は TDD を要求していない。`clarifier` は `tests/run-config-pyramid.sh` の `authored_skills` に**登録済み**であり、テストハーネス自体の変更は発生しない（research.md D2）。既存の静的契約（SKILL-02〜06、ROUTE-06、LINK-01）が実装後も通ることが完了条件であり、これは Phase 8 の検証タスクとして扱う。振る舞い系の成功基準 SC-007〜SC-016 は自動検証できないため（D8）、[quickstart.md](./quickstart.md) S2 の人手検証に委ねる。

**ストーリーの実施順**: US1・US2・US5 はいずれも P1 だが、spec.md が「US5 は US1 が成立するための前提条件」と定めるため、US5 を先に置く。また `SKILL.md` の索引が `references/` へリンクするため、参照ファイルの作成が先行しなければ LINK-01 が通らない。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（別ファイル・未完了タスクへの依存なし）
- **[Story]**: US1〜US5（Setup / Foundational / Polish には付かない）

## Path Conventions

リポジトリルートは `/Users/taikiogihara/work/my-claude-code`。以下のパスはすべてルート相対。

## 全タスク共通の禁止事項

すべての編集タスクで次を守る。違反は Phase 8 の T023 で検出される。

- `SKILL.md` に設定パス（`.claude/rules` / `.claude/skills` / `rules/*.md`）を書かない（SKILL-04）
- パッケージ配下の**すべての `*.md`** に兄弟スキル名（`problem-definition` / `product-strategy` / `minto-builder` / `coder` / `adr` / `scrum-master` 等）を書かない（SKILL-05）。境界は能力の記述で指す（contracts C1-6）
- 自身の配置パス `.claude/skills/clarifier` をハードコードしない（SKILL-06）
- `.claude/rules/clarifier.md` を変更しない（FR-025）
- `specs/001`〜`038` を変更しない（FR-028）
- `install.sh` と `tests/run-config-pyramid.sh` を変更しない（research.md D2）

---

## Phase 1: Setup

- [ ] T001 `.claude/skills/clarifier/references/` ディレクトリを作成し、`applied-frameworks.md`（適用在庫）と `design-basis.md`（設計根拠層）を見出しのみのプレースホルダとして置く（research.md D3 の二層化に対応）

---

## Phase 2: Foundational (Blocking Prerequisites)

**目的**: 全ストーリーが書き込む `SKILL.md` の骨格と、ルーティングを決めるフロントマターを先に固める。ここが終わるまで各ストーリーの本文は書けない。

- [ ] T002 `.claude/skills/clarifier/SKILL.md` のフロントマター `description` を書き換える — `name: clarifier` は不変（FR-022）、意図の共通認識形成と形式的要件化の双方を反映（FR-023）、除外境界の語を含む（SKILL-03）、`before`/`prerequisite`/`independent`/`compound` のいずれかを含む（ROUTE-06）、兄弟スキル名を含まず能力の記述で境界を指す（SKILL-05 / contracts C1-6）
- [ ] T003 `.claude/skills/clarifier/SKILL.md` の本文を二段構成の骨格に置き換える — 第1段「意図の共通認識」、第2段「形式的要件化」、第2段は第1段の後にのみ適用（FR-017）。R1 緩和として段の境界を明示する
- [ ] T004 `.claude/skills/clarifier/SKILL.md` に群レベルの索引を追加し、`references/applied-frameworks.md` と `references/design-basis.md` へ相対リンクを張る（research.md D3、LINK-01）

---

## Phase 3: User Story 5 — 判断基準を名前のある枠組みに接地する (Priority: P1)

**目的**: AIが提示する判断基準の出所を、名前のある枠組みに固定する。基準を外部情報源に照らして検証可能にし、同時にユーザーが枠組みを暗黙的に習得する経路を作る。

**独立した検証**: 完了条件が測定不能な依頼を持ち込み、SMART が適用されて測定可能な形が提示され、SMART の名前がその判断に添えて示され、かつ SMART の解説そのものは提示されないことを確認する（quickstart.md S2-2）。

- [ ] T005 [P] [US5] `.claude/skills/clarifier/references/applied-frameworks.md` に適用在庫（群A〜D）24種を記述する — 群A 接地の確認5種、群B 意図の渡し方4種、群C 分岐点の特定4種、群D 要件の記述と検証11種。各エントリに「生成する基準」と出典を付す（FR-037）。除外条件2つ——ドメイン固有標準、および同席・同時発話を前提とする実践（Event Storming / Three Amigos / Impact Mapping / CRM）——を明記し、これらを在庫に含めない（FR-039）
- [ ] T006 [P] [US5] `.claude/skills/clarifier/references/design-basis.md` に設計根拠層（群E〜G）10種を記述する — 群E 学習の設計4種、群F 認知バイアス3種、群G 協調の理論3種。各群が `SKILL.md` のどの振る舞いを規定するかを対応づける（FR-038）。適用在庫と合わせて在庫は計34種になる
- [ ] T007 [US5] `.claude/skills/clarifier/references/applied-frameworks.md` の群C「推論のはしご」の出典を、起源（Argyris 1990）と7段の流通形（Ross in Senge et al. 1994）の両方を明示する形で記述する — research.md D1 が検出した帰属誤りの再発防止
- [ ] T008 [US5] `.claude/skills/clarifier/SKILL.md` に枠組みの名指し規律を記述する — 判断基準は名前のある枠組みから引く（FR-033）、名前は判断に添えてのみ示し単独解説しない（FR-034）、実際に支持している場合のみ名指し（FR-035）、無い場合は名前を借りずその旨を明示（FR-036）
- [ ] T009 [US5] `.claude/skills/clarifier/SKILL.md` に選択規律を記述する — 群単位で選ぶ（FR-040）、一回の提示で名指しは最大2つ（FR-041）、平坦な一覧から選ばない。R5 緩和の3層を明示する
- [ ] T010 [US5] `.claude/skills/clarifier/SKILL.md` に群Fの例外を記述する — 認知バイアスは AI自身の振る舞いの理由としてのみ名指し可、ユーザーの認知状態への適用は禁止（FR-044）。群E・群G は名指ししない

**チェックポイント**: T005〜T010 完了時点で、枠組みの在庫と名指し規律が揃う。`bash tests/run-config-pyramid.sh` で SKILL-05 と LINK-01 が通ることを先行確認できる。

---

## Phase 4: User Story 1 — AIの理解を言語化して突き合わせる (Priority: P1) 🎯 MVP

**目的**: AIが理解した意図を明示的に言語化して提示し、ユーザーの訂正または承認を経て合意を成立させる。

**独立した検証**: 複数解釈が成立する依頼をスキル名を出さずに持ち込み、AIの理解・前提・スコープ外・未解決点が分離して提示され、承認まで実装に着手しないことを確認する（quickstart.md S2-1）。

- [ ] T011 [US1] `.claude/skills/clarifier/SKILL.md` の第1段に突き合わせループを記述する — 理解の言語化（FR-001）、AIの理解／前提／スコープ外／未解決点の分離（FR-002）、前提への確信度付与（FR-003）、承認まで着手しない（FR-004）
- [ ] T012 [US1] `.claude/skills/clarifier/SKILL.md` に3往復上限とその収束根拠を記述する（FR-005） — 恣意的な打ち切りではなく、内包で詰めていれば収束するはずという前提に立ち、収束しない場合は基準の立て方が FR-029/FR-030 を満たさない兆候として扱う
- [ ] T013 [US1] `.claude/skills/clarifier/SKILL.md` に判断基準の提示形式を記述する — 内包（判断基準）を提示し外延（ケース一覧）で詰めない（FR-029）、反例を挙げられる具体性で述べる（FR-030）、質問は AIが原理的にアクセスできない事項に限る（FR-031）、解釈・境界・既定値は質問せず候補提示（FR-032）
- [ ] T014 [US1] `.claude/skills/clarifier/SKILL.md` に共通認識メモの生成手順を記述する — 6セクション構成と順序（FR-008）、保存先の解決規則（FR-009）、自身が作成していないファイルへ書き込まない（FR-010）、記述言語は対話言語で枠組み名と出典は原語（FR-042）
- [ ] T015 [US1] `.claude/skills/clarifier/SKILL.md` にメモの同一性判定と中断時の扱いを記述する — 同一性は FR-009 で解決したパスの一致で判定し内容類似度では判定しない（FR-011）、既存時は上書きか新バージョンかをユーザーに確認、合意成立前の終了時は未完成マーカー付きドラフトとして保存（FR-012）

**チェックポイント**: MVP 成立。US5 と合わせて、枠組みに接地した基準を提示し合意をファイルに残すところまで動作する。

---

## Phase 5: User Story 2 — 齟齬の兆候を検知して自発的に立ち止まる (Priority: P1)

**目的**: ユーザーが明示的に求めなくても、理解の食い違いの兆候が出た時点で起動し、作業を続ける前に共通認識を取り直す。

**独立した検証**: AIの成果物をユーザーが否定してやり直しを求める会話を再現し、同じ理解のまま作り直さずに分岐点を特定することを確認する（quickstart.md S2-5）。

- [ ] T016 [US2] `.claude/skills/clarifier/SKILL.md` に起動条件を記述する — 明示要求時、および齟齬の5兆候（直前成果の否定、同一論点の2回以上の言い直し、AI要約への訂正、既存合意との矛盾、2つ以上の解釈成立）の少なくとも一つが成立した時のみ（FR-006）。いずれも不成立なら起動しない（FR-007）
- [ ] T017 [US2] `.claude/skills/clarifier/SKILL.md` に分岐点の特定手順を記述する — 群C（推論のはしご等）を用いて、どの段で理解が分かれたかを特定してから再着手する。R2（自己参照的な限界）に対し、ユーザーによる明示要求という経路を必ず残す
- [ ] T018 [US2] `.claude/skills/clarifier/SKILL.md` にエッジケース7件を記述する — 単一解釈しか許さない依頼、合意成立前の終了、同一パスの既存メモ、ユーザーが確認を拒否、複数の枠組みが該当、習熟した相手への名指し維持、3往復で未収束（spec.md エッジケース）

---

## Phase 6: User Story 3 — 合意を検証可能な要件へ落とす (Priority: P2)

**目的**: 意図の共通認識が成立した後、その合意を検証可能な受け入れ基準へ変換する。

**独立した検証**: 意図が合意された状態から要件化を依頼し、曖昧な数量表現が数値＋単位に変換され Given/When/Then が生成されることを確認する。

- [ ] T019 [US3] `.claude/skills/clarifier/SKILL.md` の第2段に形式的要件化を記述する — 既存の曖昧性パターン目録（FR-013）、引き出しツールボックス（FR-014）、品質ゲート（FR-015）、出典（FR-016）を維持し、第1段の成立後にのみ適用する（FR-017）。群Dの在庫を参照する

---

## Phase 7: User Story 4 — 恒久的ユーザーモデルへの蓄積 (Priority: P3)

**目的**: 今回の依頼を超えて有効な事実を、リポジトリ内のファイルとして蓄積する。

**独立した検証**: 恒久的に有効な好みが表明された会話を再現し、記録候補として提案され、ユーザー承認後にのみ書き込まれることを確認する。

- [ ] T020 [US4] `.claude/skills/clarifier/SKILL.md` に恒久的ユーザーモデルの扱いを記述する — 候補の提案（FR-018）、明示承認後にのみ書き込む（FR-019）、`docs/shared-understanding/user-profile.md` にプロジェクトごと1つ（FR-020）、矛盾時は現在有効な方を確認して更新（FR-021）
- [ ] T021 [US4] `.claude/skills/clarifier/SKILL.md` に記録対象の制限を記述する — 作業の進め方に関する事実のみ。能力評価・業務上の機微・第三者に関する記述は禁止（FR-043）。理由（コミット履歴への永続化と可視性、FR-019 の承認だけでは不十分であること）を併記する

---

## Phase 8: Polish & 契約同期

**目的**: 変更された公開契約の説明を同じ変更内で同期し（`live-documentation.md`）、静的契約と人手検証で完了を確認する。

- [ ] T022 [P] `.claude-ja/skills/clarifier/SKILL.md` を英語版と同構成に同期する（FR-024）。`references/` の日本語版は**作成しない**（research.md D7）
- [ ] T023 [P] `.specify/extensions.yml` L11-13 の `prompt` と `description` を拡張後の目的に更新する。`command: clarifier` と `optional: true` は変更しない（FR-026）
- [ ] T024 [P] `README.md` L39 と L139 の `clarifier` 説明を拡張後の内容に更新する（FR-027）
- [ ] T025 [P] `README.ja.md` L28 の `clarifier` 言及を拡張後の内容に更新する（FR-027）
- [ ] T026 [P] `docs/claude-config-design.md` L44 の対応表を更新し、R3（常時ルール `clarifier.md` とスキルの責務の乖離）を明示的に記述する（FR-027）。この記述を `SKILL.md` 側に書くと SKILL-04 が失敗するため、必ず本ファイルに置く
- [ ] T027 `bash tests/run-config-pyramid.sh` を実行し、**36 passed, 0 failed** を確認する（quickstart.md S1）。ベースラインは実装前の実測値
- [ ] T028 不変対象の確認 — `git diff --name-only main...HEAD` に `.claude/rules/` と `specs/0[0-3][0-8]` が含まれないこと、`install.sh` と `tests/run-config-pyramid.sh` の差分が空であることを確認する（quickstart.md S1）
- [ ] T029 [quickstart.md](./quickstart.md) S2-1〜S2-6 の人手検証を実施する — 自動化できない成功基準（research.md D8）を各シナリオで確認する。対応は S2-1 → SC-007、S2-2 → SC-008・SC-011、S2-3 → SC-009、S2-4 → SC-010、S2-5 → FR-006・FR-007、S2-6 → SC-003・SC-013・SC-014・SC-015・SC-016。あわせて SC-001・SC-002・SC-004・SC-005・SC-006・SC-012 を確認する
- [ ] T030 [P] `.claude/skills/clarifier/references/applied-frameworks.md` の Robertson & Robertson の版・刊行年を一次情報で確認し、確認できない場合は版表記を落とす（research.md D1 の未解決項目）
- [ ] T031 [quickstart.md](./quickstart.md) S3 と S4 を実行し、文書同期とミラー構成を確認する — README 2件・`docs/claude-config-design.md` に拡張前の説明が残っていないこと、`docs/claude-config-design.md` に R3 の記述があること、`.specify/extensions.yml` の `command`/`optional` が不変であること、日本語ミラーの見出し数が英語版と一致すること

---

## 依存関係

```text
Phase 1 (T001)
   ↓
Phase 2 (T002-T004)  ← 全ストーリーの前提
   ↓
Phase 3 US5 (T005-T010)  ← spec.md により US1 の前提。references/ が SKILL.md の索引先
   ↓
Phase 4 US1 (T011-T015)  🎯 MVP
   ↓
Phase 5 US2 (T016-T018)
   ↓
Phase 6 US3 (T019)
   ↓
Phase 7 US4 (T020-T021)
   ↓
Phase 8 (T022-T031)
```

**ストーリー間の実質的独立性**: US2・US3・US4 は互いに独立で、US1 完了後は任意の順序で実施できる。上図の直列は `SKILL.md` という単一ファイルを共有することによる編集競合の回避であって、論理的依存ではない。

**真の依存**:

- T005/T006（参照ファイル）→ T004（索引のリンク先）。ただし T004 を最後に回せば逆順も可
- T007 は T005 の中の1エントリの精緻化であり、T005 完了後
- T019（第2段）→ T011-T013（第1段）。FR-017 が順序を定める
- T027/T028 → T001〜T026 のすべて
- T029 → T027（静的契約が通ってから振る舞いを見る）
- T031 → T022-T026（同期を終えてから同期結果を検証する）

## 並列実行の機会

| フェーズ | 並列可能なタスク | 理由 |
|---|---|---|
| Phase 3 | T005 ∥ T006 | 別ファイル（`applied-frameworks.md` / `design-basis.md`） |
| Phase 8 | T022 ∥ T023 ∥ T024 ∥ T025 ∥ T026 | すべて別ファイル。相互依存なし |
| Phase 8 | T030 ∥ T031 | 別ファイル・別検証対象 |

Phase 4〜7 のタスクはすべて `.claude/skills/clarifier/SKILL.md` を編集するため並列化できない。

## 実装戦略

**MVP スコープ**: Phase 1 → Phase 2 → **Phase 3 (US5)** → **Phase 4 (US1)**。

US1 単独を MVP としない理由は spec.md が US5 を US1 の前提条件と定めているためである。US5 なしでも US1 は動作するが、その場合 AIが提示する判断基準の出所が AIのその場の判断となり、ユーザーには直感以外に却下の根拠が存在しない——本機能が解こうとした問題がそのまま残る。

**増分デリバリ**: MVP 到達後、US2（自発的な起動）→ US3（形式的要件化）→ US4（恒久モデル）の順に価値を追加できる。各段階で `bash tests/run-config-pyramid.sh` は通り続けるべきであり、通らなくなった時点が回帰の発生点である。

**Phase 8 の位置づけ**: T022〜T026 の契約同期は `live-documentation.md` が同一変更内での実施を求めるため、後回しにできない。MVP のみをコミットする場合でも、その時点の内容に合わせて README と `docs/` を同期する必要がある。
