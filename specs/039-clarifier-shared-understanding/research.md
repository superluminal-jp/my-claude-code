# Phase 0 リサーチ: `clarifier` の「意図の共通認識形成 ＋ 形式的要件化」への拡張

**ブランチ**: `039-clarifier-shared-understanding` | **日付**: 2026-09-08 | **仕様**: [spec.md](./spec.md)

**利用者からの追加指示**: 「権威ある文献などの引用元を合わせて調査」——D1 がこれに応答する。

---

## D1. 引用元の検証（spec.md 参考文献の一次情報照合）

**決定**: spec.md の参考文献25件を一次情報・出版元記録に照合した。**24件は正確**であり、**1件に帰属誤り**を発見したため spec.md を修正した。加えて7件に書誌情報を補完した。

**根拠**: 各文献の出版元・書誌データベース・原典 PDF に当たった。検証結果は下表のとおり。

### 検証結果

| 文献 | 検証状態 | 確定した書誌 |
|---|---|---|
| Clark & Brennan, "Grounding in Communication" | ✅ 正確・**補完** | Resnick, Levine & Teasley (Eds.), *Perspectives on Socially Shared Cognition*, APA, 1991, **Ch. 7, pp. 127–149** |
| Clark & Wilkes-Gibbs, "Referring as a collaborative process" | ✅ 正確・**補完** | *Cognition* **22(1): 1–39**, 1986 |
| Newton, *The Rocky Road from Actions to Intentions* | ✅ 正確 | Stanford University 博士論文, 1990。**タッパーの予測約50%に対し実測 3/120 = 2.5%** — spec の記述と一致 |
| Camerer, Loewenstein & Weber, "The Curse of Knowledge in Economic Settings" | ✅ 正確・**補完** | *Journal of Political Economy* **97(5): 1232–1254**, 1989 |
| Gilovich, Savitsky & Medvec, "The Illusion of Transparency" | ✅ 正確・**補完** | *JPSP* **75(2): 332–346**, 1998。副題 "Biased Assessments of Others' Ability to Read One's Emotional States" |
| Ross, Greene & House, "The False Consensus Effect" | ✅ 正確・**補完** | *JESP* **13(3): 279–301**, 1977 |
| Collins, Brown & Newman, "Cognitive Apprenticeship" | ✅ 正確・**補完** | 副題 "Teaching the Crafts of Reading, Writing, and Mathematics"。Resnick (Ed.), *Knowing, Learning, and Instruction: Essays in Honor of Robert Glaser*, Erlbaum, 1989, **pp. 453–494** |
| Sweller & Cooper, "The Use of Worked Examples..." | ✅ 正確・**補完** | 完全題は "...as a Substitute for Problem Solving **in Learning Algebra**"。*Cognition and Instruction* **2(1): 59–89**, 1985 |
| Wood, Bruner & Ross, "The Role of Tutoring in Problem Solving" | ✅ 正確・**補完** | *Journal of Child Psychology and Psychiatry* **17(2): 89–100**, 1976 |
| Mavin et al., EARS | ✅ 正確・**補完** | *RE'09*（第17回 IEEE International Requirements Engineering Conference）, IEEE, 2009, **pp. 317–322**。Rolls-Royce にて航空機エンジン制御系の要件抽出中に開発 |
| Starmer et al., I-PASS | ✅ 正確 | *NEJM* 371, 2014。**医療エラー率 23%減（24.5 → 18.8 / 100入院）、予防可能有害事象 30%減（4.7 → 3.3）** — spec の「23%減」は医療エラー率を指し、正確 |
| Wynne, "Introducing Example Mapping" | ✅ 正確・**補完** | Cucumber ブログ, **2015年12月8日** |
| Klein, "Performing a Project Premortem" | ✅ 正確・**補完** | *Harvard Business Review* **85(9): 18–19**, 2007年9月 |
| ICAO Doc 9432 *Manual of Radiotelephony* | ✅ 正確・**補完** | **第4版, 2007**。"Issue of clearance and read-back requirements" の節を含む |
| US Army ADP 6-0 | ✅ 正確・**補完** | 完全題は *ADP 6-0: Mission Command — **Command and Control of Army Forces***, 2019年7月 |
| Gilb, *Competitive Engineering* | ✅ 正確 | Butterworth-Heinemann, 2005。Planguage の原典 |
| Robertson & Robertson, *Mastering the Requirements Process* | ⚠️ **部分検証** | fit criterion が Volere の中核概念であることは確認。**第3版の刊行年（2012, Addison-Wesley）は一次情報で未確認** |
| **Argyris, 推論のはしご** | ❌ **帰属誤り — 修正済み** | 下記参照 |
| Toulmin, *The Uses of Argument* (1958) / Adzic (2011) / Evans (2003) / Lave & Wenger (1991) / Grice (1975) / Winograd & Flores (1986) / Clark, *Using Language* (1996) / AHRQ ティーチバック | 未照合（低リスク） | 広く流通した標準的書誌であり、spec の記述に固有の数値・版・頁の主張を含まないため個別照合を省略した |

### 発見した帰属誤りとその修正

**問題**: spec.md は「推論のはしご」を Argyris, *Overcoming Organizational Defenses* (1990) に帰属させたうえで、その段を「データ→選択→意味づけ→前提→結論→信念→行動」と記述していた。

**事実**: Argyris (1990) が概念の起源であることは正しい（同書 p. 88）。しかし spec が記述した**7段の形は Rick Ross が *The Fifth Discipline Fieldbook* (1994) pp. 242–246 で提示した版**であり、Argyris の原版は段数が異なる。Argyris 版と Ross/Senge 版は別物である。

**なぜ重大か**: これは spec.md 自身が **R4（枠組み劇場）**として定義した失敗——「実際にはその標準がその判断を支持していないのに、権威づけのために名前を借りる」——の実例である。FR-035 が禁じる当のものを spec 自身が犯していた。本機能が導入する規律の妥当性を、その規律自身が検出した形になる。

**修正**: spec.md の参考文献と FR-037 群Cの出典欄を、起源（Argyris 1990）と流通形（Ross in Senge et al. 1994）の両方を明示する形に更新した。

**却下した代替案**: Argyris のみを引き続き引用し段数の記述を削る案は、実際に運用される7段の形が出典を失うため却下。Ross のみに帰属させる案は、概念の起源を消すため却下。

---

## D2. 現行メカニズムの再検証（`037` / `038` からの継承）

**決定**: `038` が確立した実装メカニズムをそのまま用いる。ただし `038` と異なり、**テストハーネスの `authored_skills` 配列への追加は不要**である。

**根拠**: `tests/run-config-pyramid.sh:46-59` の `authored_skills` に `clarifier` は**既に含まれている**（`037` / `038` は新規スキルだったため追加が必要だった）。本機能は既存スキルの内容拡張であり、登録作業が発生しない。

| 対象 | `037`/`038` での作業 | 本機能での作業 |
|---|---|---|
| `authored_skills` への追加 | 必要 | **不要**（登録済み） |
| `run_routing_fixtures()` への追加 | 必要 | **不要**（ROUTE-06 が既存） |
| README 2件 | 一行追加 | **説明文の書き換え** |
| `install.sh` | 無編集 | **無編集**（`skills` ディレクトリ一括同期のため） |
| `.claude/rules/*.md` | 無編集 | **無編集**（FR-025） |

**バジェット制約**: `BASELINE_BYTES=20126` は「無条件コーパス」（`.claude/CLAUDE.md` + `.claude/rules/*.md`）にのみ適用される（`tests/run-config-pyramid.sh:199-202`）。本機能はルールファイルを一切変更しないため、BUDGET-01 に抵触しない。スキル本体のサイズに上限契約は存在しない。

---

## D3. R6 の解消 — 34種の在庫の配置

**決定**: 適用在庫（群A〜D）と設計根拠層（群E〜G）を `.claude/skills/clarifier/references/` 配下の参照ファイルへ分離し、`SKILL.md` 本体には二段構成の手順と群レベルの索引のみを置く。

**根拠**: `references/` サブディレクトリは本リポジトリで確立済みのパターンである。

| スキル | 参照ファイル |
|---|---|
| `digital-agency-frontend` | `references/` 配下4ファイル（＋バンドル資料） |
| `scrum-master` | `references/` 配下6ファイル（Scrum Guide PDF 2言語を含む） |
| `apple-notes` | `references/reference.md` |

FR-041 が一回の提示での名指しを2つに制限し、FR-040 が群単位の選択を強制するため、実行時に必要なのは「どの群か」の判断までであり、34種の全文が常時 `SKILL.md` に存在する必要はない。分離は R1（単一スキルへの二関心事の同居）の緩和にも寄与する。

**制約**: `run_owned_link_contract`（`tests/run-config-pyramid.sh:173`）が、authored skill 配下の `*.md` 内の相対リンクをすべて解決可能であることを要求する。参照ファイルへのリンクは実在パスでなければならない。

**却下した代替案**: 全34種を `SKILL.md` 本体に置く案は、R1 の悪化とファイル肥大により却下。在庫を持たず実行時に推論する案は、FR-037 が保持を明示的に要求するため却下。

---

## D4. テスト契約と FR-023 の衝突 — 兄弟スキルの名指し禁止

**決定**: FR-023 の「`problem-definition`・`product-strategy`・`minto-builder` との境界を明示」は、**兄弟スキル名を書かずに、除外される作業の性質を記述する**ことで満たす。

**根拠**: `tests/run-config-pyramid.sh:136-150` の **SKILL-05** は、authored skill パッケージ配下の**すべての `*.md`**（将来の `references/` を含む）を走査し、他の authored skill 名の出現を失敗として扱う。パターンは `` (`|/|skills/)<target>(`|/|[^[:alnum:]_-]) ``。FR-023 を字義どおり「名前を書く」と実装すると **SKILL-05 が失敗する**。

既存スキルはこの制約下で境界を表現している。実例:

- `problem-definition` の description: 「a separate **requirements-clarification capability's** job」——`clarifier` と書かずに指している
- `product-strategy` の description: 「a separate **document-creation capability**」——`minto-builder` と書かずに指している

**帰結**: FR-023 は充足可能だが、実装は能力の記述による指示に限られる。これは spec.md の変更を要さない——FR-023 は「境界を明示」としか述べておらず、名指しを要求していない。tasks.md で実装時の制約として明示する。

**却下した代替案**: SKILL-05 を緩和する案は、`028-independent-skills` が確立したスキル独立性原則を掘り崩すため却下。

---

## D5. その他のテスト契約（実装が必ず満たすべきもの）

`tests/run-config-pyramid.sh` が `clarifier` に課す契約を洗い出した。実装後にこれらが通ることが完了条件となる。

| 契約 | 要求 | 本機能への影響 |
|---|---|---|
| **SKILL-02** | `when_to_use:` フロントマターを持たない | 現状維持 |
| **SKILL-03** | description に除外境界の語（`Do not use` / `out of scope` / `対象外` / `使わない` 等）を含む | 書き換え後も維持が必要 |
| **SKILL-04** | `SKILL.md` が設定パス（`.claude/rules` / `.claude/skills` / `rules/*.md`）に依存しない | **R3 の注意点**——常時ルールとの乖離を `SKILL.md` 内で `rules/clarifier.md` と書いて説明してはならない。この記述は `docs/claude-config-design.md` 側に置く |
| **SKILL-05** | 兄弟パッケージ名を含まない | D4 のとおり |
| **SKILL-06** | 自身の配置パス `.claude/skills/clarifier` をハードコードしない | 参照ファイルへのリンクは相対パスで書く |
| **ROUTE-06** | description が `(before\|prerequisite\|independent\|compound)` にマッチ | 書き換え後も維持が必要 |
| **OWNED-LINK** | 配下 `*.md` の相対リンクがすべて解決する | D3 の参照ファイル分離に伴い要確認 |

---

## D6. A2 の解消 — 共通認識メモのファイル名

**決定**: `shared-understanding.md` を確定する。

**根拠**: 兄弟スキルの規約と整合する（`problem-definition` は `problem.md`、`product-strategy` は `strategy.md` を `specs/<N>-*` 配下に置く）。FR-011 の同一性判定が保存先パスに依存するため、規約からの逸脱は同一性判定の不安定化を招く。A2 の確信度「中」を確定へ引き上げる材料として、既存2スキルの一貫した先例で足りると判断した。

**却下した代替案**: `agreement.md` / `common-ground.md` は、兄弟スキルの命名（内容を表す普通名詞1語）と揃うものの、先例がなく利点もないため却下。

---

## D7. A3 の解消 — `.claude-ja` ミラーの範囲

**決定**: `.claude-ja/skills/clarifier/SKILL.md` を英語版と同構成に同期する。ただし**参照ファイル（`references/`）の日本語版は作成しない**。

**根拠**: 観測された事実として、`.claude-ja/skills/` には `problem-definition` と `product-strategy` が**存在しない**——ミラーは新規スキルに追随していない。一方 `clarifier` は英日双方が存在するため、既存ファイルを陳腐化させないことが `live-documentation.md`（契約同期）の要求である。

参照ファイルを対象外とするのは、ミラーが現に SKILL.md 単位でしか維持されていない実態に合わせるためである。全34種の在庫を二重に保守する義務を新設すると、追随できずに陳腐化する蓋然性が高い。

**却下した代替案**: ミラー全体を対象外とする案は、既存の日本語 `clarifier` を陳腐化させるため却下。参照ファイルまで訳す案は、保守負担に対して読者価値が不明なため却下。

**残る前提**: `.claude-ja` の同期方針そのもの（新規スキルを追随させるか）は本機能の範囲外であり、別途の判断を要する。

---

## D8. テスト方式（spec の Completion Signals Outstanding の解消）

**決定**: 検証は `tests/run-config-pyramid.sh` の静的構造契約（D5）に限定し、SC-007〜SC-016 の**振る舞い系成功基準に自動テストを新設しない**。

**根拠**: SC-007〜SC-016 は実行時のモデルの振る舞い（内包で提示したか、名指しが2つ以下か、機微情報を書いていないか）に関する基準であり、オフラインの静的検査では判定できない。本リポジトリのテストハーネスは一貫してオフライン静的構造契約のみを扱う（`037` / `038` の research で確立済みの方針）。

**帰結**: SC-007〜SC-016 は**人手によるレビュー基準**として位置づけ、自動化しない。この限界は spec.md の可観測性 Deferred と整合する。tasks.md では quickstart.md のシナリオを手動検証手順として扱う。

**却下した代替案**: モデルを実行して出力を検査する統合テストの新設は、オフライン実行の前提を壊し、本リポジトリのテスト方針から逸脱するため却下。

---

## まとめ: NEEDS CLARIFICATION の解消状況

| 項目 | 状態 |
|---|---|
| 引用元の検証（利用者指示） | **完了** — 24件正確、1件修正、7件補完、1件部分検証（D1） |
| A2（メモのファイル名） | **解消** — `shared-understanding.md`（D6） |
| A3（`.claude-ja` の範囲） | **解消** — SKILL.md のみ同期、参照ファイルは対象外（D7） |
| R6（在庫の配置） | **解消** — `references/` へ分離（D3） |
| テスト方式 | **解消** — 静的契約のみ、振る舞い系は人手レビュー（D8） |
| FR-023 の実装方法 | **解消** — 能力の記述で指す、名指ししない（D4） |
| Robertson & Robertson 第3版の刊行年 | **未解決（低影響）** — 一次情報で未確認。実装時に版表記を落とすか確認する |
