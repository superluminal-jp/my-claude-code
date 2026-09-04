# Phase 0 リサーチ: 開発着手前の戦略整理を支援する `product-strategy` スキルの追加

**日付**: 2026-09-04 | **仕様**: [spec.md](./spec.md) | **計画**: [plan.md](./plan.md)

ユーザー指示: 「どんなベストプラクティス、フレームワーク、パターン、項目があるかを調査。権威ある出典を調査。」に基づき、(1) スキル本文が使うプロダクト戦略フレームワークの権威ある出典、(2) 現行リポジトリにおける実装先（テスト・配布・ドキュメントの実体）の両方を調査した。

---

## D1. プロダクト戦略フレームワークのツールボックス

**決定**: spec.md の FR-003a〜FR-003g・参考文献に列挙した10件の一次資料（Business Model Canvas / Lean Canvas / Cagan *INSPIRED* / JTBD / ISO 9241-210 / Torres のオポチュニティ・ソリューション・ツリー / Value Proposition Design / OKR / Balanced Scorecard / North Star Metric の出典 / MoSCoW / Porter "What Is Strategy?" / 狩野モデル）を採用する。

**根拠**: Web調査により、以下の2点で当初のツールボックス（4文献）に実質的なギャップがあることが判明したため、3件を追加した:

- **North Star Metric という語自体が、当初のドラフトでは出典なしに使われていた**（"North-Star-style" という形容のみ）。FR-003 自身が「出典のないフレームワークがあってはならない」と定めているにもかかわらず、この語だけが自己言及的に違反していた。調査の結果、Sean Ellis による2010年代初頭の命名と、Amplitude / John Cutler による "North Star Playbook" としての体系化が一次的な出典として特定できたため、FR-003d に追加した。
- **狩野モデル（Kano, Seraku, Takahashi, Tsuji, 1984, 『品質』14(2), pp.39-48）** は、MoSCoW が担う「イン/アウト」の二値判断と直交する「当たり前品質か魅力的品質か」という質的な軸を提供する。日本発の学術的に確立した枠組みであり、スペック全体を日本語で作成するという文脈にも整合するため、スコープ/優先順位セクションの補助的な引用として追加した（MUST ではなく SHOULD——MoSCoW を置き換えるものではなく補うものであるため）。
- **Teresa Torres のオポチュニティ・ソリューション・ツリー（*Continuous Discovery Habits*, 2021）** は、JTBD が説明する「なぜユーザーはこの製品を"雇う"のか」という理論を、実際にどう引き出すか（ユーザー発言から機会=opportunityを木構造にマッピングする具体的な手順）という点で補完する。JTBD 単独では「引き出しの理論的根拠」はあっても「引き出しの手順」が薄いというギャップがあった。
- **Marty Cagan *INSPIRED*（第2版, 2017/2018, Silicon Valley Product Group）** は、Business Model Canvas / Lean Canvas が一般的な事業モデル一般を対象とするのに対し、ソフトウェア/テックプロダクト特有の「戦略とロードマップ/バックログの違い」という、本スキルの FR-004（アーキテクチャ決定を含めない）と FR-003f（Porter による戦略の定義）を実務レベルで橋渡しする、プロダクトマネジメント分野で最も広く参照される一次資料である。

**却下した代替案**:

- **Wardley Mapping（Simon Wardley）**: 状況認識のための地図作成手法であり強力だが、本スキルが一発の引き出しセッションで生成する単一ドキュメントの粒度には重すぎる。継続的な地図の更新を前提とする手法であり、FR-006 が定める6セクション構成のブリーフとは形が合わない。
- **Impact Mapping（Gojko Adzic）**: ゴール→アクター→インパクト→施策というツリー構造で、Torres の Opportunity Solution Tree と機能的に重複する。後者の方がプロダクトディスカバリー分野でより広く採用されており（2021年以降の業界標準に近い）、二重に採用する必要性が薄いため見送った。
- **Kano モデルを MUST 要件にする**: MoSCoW と役割が異なるとはいえ、あらゆるブリーフに Kano 分類を強制すると、単発の軽量な引き出しという FR-006/前提条件の性質と衝突する（引き出しの手数が増えすぎる）。そのため SHOULD（FR-003g）とし、スコープが広い・機能項目が多いブリーフでのみ実際に使う設計とした。

---

## D2. 「ルーティング回帰スイート」の実体（FR-015/FR-016 の技術的な着地点）

**決定**: spec.md の FR-015/FR-016 が言う「ルーティング回帰スイート」は、**現行のリポジトリには存在しない**。実装時にこれらの FR を満たす先は `tests/run-config-pyramid.sh` である。

**事実**: リポジトリを直接検査した結果:

- `tests/` 配下に、016 系スキル（`scrum-master`）追加時に存在した `run-skill-routing.sh` や `tests/skill-routing/<N>-*.md`（プロンプト→期待スキルのケースファイル、ライブの `claude` CLI 実行が前提）は存在しない。
- 代わりに `tests/run-config-pyramid.sh` が、spec 036（`036-rule-layer-independence`、PR #70 で `main` にマージ済み）の FR-008「中央集権的な named skill-routing ルールを廃止し、各スキルのメタデータ + 汎用 apex アルゴリズムから解決する」・FR-015「オフラインの構造契約テストが禁止パターン・ルールトポロジ・スキルパッケージ境界・ポータブルな所有リンク・代表的な複合ルーティングのメタデータ契約を検証する」を実装したものとして存在する。
- この `run_routing_fixtures()`（`run-config-pyramid.sh` 157〜166行目）は、ライブでプロンプトを実行して実際にどのスキルがロードされるかを見るのではなく、**各スキルの `SKILL.md` の `description:` 行が特定のキーワードパターンを含んでいるかを静的に grep するだけ**のオフライン契約である。
- さらに、この構造契約が適用される「対象スキル」は `authored_skills` というハードコードされた配列（46〜57行目: `adr, clarifier, cloud-platform-research, coder, digital-agency-frontend, git-workflow, minto-builder, minto-reviewer, minto-rewriter, scrum-master`）で明示的に列挙されており、新しいスキルを対象に含めるにはこの配列へ1行追加する必要がある。

**帰結**: FR-015「ルーティング回帰スイートには product-strategy を期待するケースを少なくとも1つ含める」は、実装時には次の3箇所への追加として具体化する:
1. `authored_skills` 配列に `product-strategy` を追加する（SKILL-01〜SKILL-06 の構造契約が自動的に適用されるようになる）。
2. `run_rule_contract()` の RULE-03 正規表現リストと `run_skill_contract()` の SKILL-06 正規表現リストに `product-strategy` を追加する（サイバーリング参照の禁止を新スキルにも適用する）。
3. `run_routing_fixtures()` に、`product-strategy` の `description:` が「戦略/strategy」「before/prerequisite/before development」等、他スキル（`clarifier`・`scrum-master`・`minto-builder`）との境界を示すキーワードを含むことを検証する新規アサーション（例: `ROUTE-09`）を1件追加する。

FR-016「既存のルーティング回帰ケースはすべて変更なく成功しなければならない」は、そのまま `run-config-pyramid.sh` の既存アサーションが全てPASSし続けることとして検証できる（意味は変わらない）。

**FR-014 も同じ事実（RULE-10）から帰結する。** FR-014「スキルの境界を列挙するルーティングルール文書があれば、`product-strategy` のエントリを含める」は、`run_rule_contract()` の `RULE-10`——`skill-routing.md` 等の「legacy conditional and routing rules」がリポジトリに存在しないことを検証するアサーション——により、その前提条件（「あれば」）が現状満たされないことが確認できる。したがって FR-014 には対応するタスクが1件も無くてよい——単に未対応なのではなく、条件文の前件が偽であるために要求自体が空虚に真となる（vacuously satisfied）。将来 `skill-routing.md` 相当の文書が復活した場合にのみ、FR-014 は具体的なタスクを要求するようになる。

SC-001 が求める「表現の異なる4プロンプト（日英各1以上）での検証」は、この静的契約テストでは検証できない——静的 grep はライブなルーティング判断そのものを再現しないため。実装後、ライブの `claude` CLI セッションで4プロンプトを手動投入し、`product-strategy` がロードされることを目視確認する手動検証として実施する（自動化された回帰ファイルへの追加ではない）。

**根拠**: `tests/run-config-pyramid.sh` の全文検査、および spec 036 の `spec.md`（FR-008、FR-015、SC-002、SC-006）との突き合わせ。

**却下した代替案**: 旧来のライブプロンプト回帰スイート（`run-skill-routing.sh` 相当）を本機能で復活させる——却下理由: spec 036 は central routing table・個別ケースファイル方式をまさに廃止する決定を下しており、本機能の中でそれを再導入することは spec 036 の決定を覆す独立した大きな決定になる。本機能のスコープ外であり、必要であれば別機能として提案すべき。

---

## D3. 「既存カスタムスキル」のピア集合の確定

**決定**: `product-strategy` が実装・テスト・ドキュメントの両面で実際にピアとして扱うべき集合は、`README.md` と `run-config-pyramid.sh` の双方が一致して扱う **authored_skills 群**（`adr, clarifier, cloud-platform-research, coder, digital-agency-frontend, git-workflow, minto-builder, minto-reviewer, minto-rewriter, scrum-master`）である。

**事実**: `README.md`・`README.ja.md` 全文を検索したところ、`apple-notes` / `apple-reminders` への言及は一件もなかった（スキル一覧の散文にも、`.claude/skills/` のツリー表示にも含まれない）。`run-config-pyramid.sh` の `authored_skills` 配列にも同様に含まれない。両スキルは `.claude/skills/` 配下には物理的に存在するが、README の讀者向け一覧にも構造契約テストにも現れない、別の統治カテゴリ（spec 033 で移植された、ポート起源のユーティリティスキル）として扱われている。

**帰結**: spec.md FR-001 の「既存のカスタムスキル群（`adr`、`clarifier`、`coder`、`minto-*`、`scrum-master`、`digital-agency-frontend`、`apple-notes`、`apple-reminders`、`git-workflow`、`cloud-platform-research`）と並んで配置」という記述は、**物理的な配置先**（`.claude/skills/` 配下）としては正しいが、**FR-013（ドキュメント一覧への追加）・FR-015（構造契約テストへの追加）が実際に対象とすべきピア集合**は authored_skills の10件に限られる。apple-notes/apple-reminders 側の一覧やテストへ product-strategy を追加する作業は生じない。

**根拠**: `README.md`・`README.ja.md`・`run-config-pyramid.sh` の直接検査（`grep -n "apple-notes\|apple-reminders"` が両READMEで0件）。

**却下した代替案**: なし——事実確認であり、設計上の選択肢の比較ではない。

---

## D4. Constitution Check の扱い

**決定**: `.specify/memory/constitution.md` は未記入のテンプレート（全フィールドが `[PLACEHOLDER_NAME]` のまま）であるため、批准された具体的なプロジェクト原則は存在せず、本ゲートは形式的な意味では自動的に通過する。実質的なガバナンス制約としては、本リポジトリの5つの常時ロードルール（`clarifier.md`、`live-documentation.md`、`permissions.md`、`pyramid-principle.md`、`thinking-lenses.md`）を代わりに照合する。

**根拠**: `constitution.md` の内容確認。過去の類似機能（spec 016、035）の `plan.md` も同じ扱いを採っており、本リポジトリでは Spec Kit 標準の `constitution.md` ではなく `.claude/rules/*.md` が実質的な統治文書として機能している（`docs/adr/` に記録された過去の意思決定と整合）。

**却下した代替案**: `constitution.md` を本機能のついでに記入する——却下理由: 本機能のスコープ外であり、無関係な変更を混入させないという最小差分の原則（`.claude/CLAUDE.md` "Execute under control"）に反する。

---

## D5. `install.sh` は変更不要

**決定**: `install.sh` は `.claude/skills/` ディレクトリ全体を一括で `~/.claude/skills/` へ同期する（`skills` を含む管理対象パスのループ処理、59〜71行目）。旧来のスキル別 `CUSTOM_SKILLS` 配列（spec 016 の時代に存在した個別列挙方式）は既に廃止されている。したがって FR-012 を満たすために `install.sh` 自体へコードを追加する必要はない——`product-strategy/` ディレクトリを作成するだけで、次回の `install.sh` 実行時に自動的に含まれる。

**根拠**: `install.sh` の全文検査（`CUSTOM_SKILLS` という文字列が現行ファイルに存在しない、`skills` はディレクトリ単位の一括同期対象として扱われている）。

**却下した代替案**: なし——事実確認。

---

## まとめ: NEEDS CLARIFICATION の解消状況

Technical Context に置いた不明点はすべて本リサーチで解消した:

| 不明点 | 解消内容 |
|---|---|
| 言語/依存関係 | Markdown（スキル本文）+ Bash（テスト）。実行時コード依存なし |
| テスト機構の実体 | `tests/run-config-pyramid.sh`（静的構造契約）。旧来のライブ回帰スイートは撤去済み（D2） |
| 配布機構 | `install.sh` の一括ディレクトリ同期。コード変更不要（D5） |
| ドキュメント対象の一覧 | README 一覧 = `authored_skills` 群（D3） |
| フレームワークの出典 | 10件の一次資料に確定、うち3件は本リサーチで新規に特定（D1） |
