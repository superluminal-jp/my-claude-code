# Meta-Spec: 近接ドキュメントの発見と処分(maintaining-living-documentation スキル)

**Status**: Complete
**Generated**: 2026-10-17
**Slices**: 6

## Purpose and end state

`.claude/skills/maintaining-living-documentation` が、変更に対して「更新すべき近接ドキュメントの候補」を決定的に列挙し、LLM が各候補を「更新 / 作成 / 不要(理由)」に処分し、Stop ゲートが「未処分の候補」と「空の不要理由」を検出して止める状態にする。

完了条件(観察可能):

- 兄弟ディレクトリの README を持つコードを変更し、その README を更新も言及もしないと、ゲートが終了をブロックする。更新または言及すれば通る。
- `Documentation impact: none —` の後ろが空または定型句だけなら、ゲートがブロックする。
- 新しい公開契約を追加し候補が無い変更で、処分規則により文書が作成される(ADR と、無かった CHANGELOG は作られない)。
- 既存の単体テスト 67 件が引き続き通る。

## Out of scope

- 関数・hunk 単位のコメント検出(P0 はファイル単位の助言のみ)
- 所有者・鮮度(最終確認日)の管理
- CI で違反を失敗にするオプション
- description の整理
- `install.sh` の実行と `~/.claude/` への反映
- eval の実行(ユーザーが費用上限を承認した後に別途)
- コミット・プッシュ(依頼があるまで行わない。ただし Open points の「Spec Kit の自動コミット」を参照)

## Slices

| ID | Name | Purpose | End state (observable) | Depends on | Exposes | Priority | Feature |
|----|------|---------|------------------------|------------|---------|----------|---------|
| S1 | 未処分の兄弟 README を検出する(ウォーキングスケルトン) | 発見→処分→ゲートの最小経路を端から端まで通す | 一時 Git リポジトリで、`src/x.py` を変更し隣の `README.md` が未変更・未言及なら Stop ゲートがブロックし、README を更新または最終メッセージで言及すれば通る。`find_related.py --json` が P1 候補を C1 の形で出す | — | C1, C2 | Must | — |
| S2 | 候補の発見を広げる | 宣言なしに、名前参照・変更履歴・ファイル内コメントまで候補を拾う | `find_related.py` が P2(本文にパスまたはファイル名を含む Markdown)、変更履歴(ユーザーに見える変更種別のみ)、P0(変更コード自身、助言のみ)を出し、変更済み文書と `exclude_globs` を除き、上限で切り詰める。`related.*` を含む設定がスキーマ検証を通り、不正な型は拒否される | S1 | C1(拡張), C3 | Must | — |
| S3 | 空の「不要」理由を弾く | `none —` が理由なしで通る穴を塞ぐ | ゲートが、理由が空または定型句だけの `Documentation impact: none —` を不合格にし、具体的な理由付きは通す。実装系の変更があるのに文書変更ゼロで `No change needed` の理由も無い報告も不合格にする | — | C2(理由の文法) | Must | — |
| S4 | 処分規則と作成条件を手順に入れる | LLM が候補ごとに更新・作成・不要・提案を判断できる基準を明文化する | `SKILL.md` と `hooks/rule.md` に、既存候補は更新、候補が無く新しい公開契約が増えた場合のみ作成(1 変更につき最大 3 ファイル、超過は提案)、ADR は作成しない、CHANGELOG が無ければ新設しない、が記載され、完了報告に `Created:` 行が加わる。`SKILL.md` は 500 行未満のまま、既存の定義テストが通る | S1, S5 | C2(報告の文法) | Must | — |
| S5 | 層・配置・近接性の実践を文書化する | 作成先の配置規則と、調査で得た根拠を一箇所に置く | `references/practices.md` に「層・配置・近接性」の節があり、コメントは API 用と実装用に分け、5 段階の近接性と P1 の README はこのスキルの設計判断と明記し、根拠は出典付きで区別して記す。`bibliography.bib` に Software Engineering at Google 10 章、PEP 8、Linux kernel コーディングスタイルがあり、`check_links.py` が通る | — | C4 | Must | — |
| S6 | 公開文書の同期と振る舞い eval | 変更後の挙動をスキル README に反映し、効果を測る足場を用意する | スキル README のスクリプト表、ゲートの挙動、eval、テストの記述が新挙動と一致し、重複した「Local modifications」が 1 つに統合されて上流との差分が記録されている。eval ケース 3 件(隣接文書の更新、新しい公開契約への作成、内部リファクタでは作らない)の fixture が生成でき、`claude plugin validate` が通る。eval の実行結果は費用承認後に別途 | S1, S2, S3, S4, S5 | — | Must | — |

## Contracts

**C1 — 候補レコード**: `find_related.py --json` の出力。`changed`(変更パスの配列)、`candidates`(各要素は `source`、`path`、`kind`(`comment` / `sibling` / `mention` / `changelog`)、`proximity`(`P0`〜`P3`)、`reason`)、`truncated`(切り捨て件数)。生産者は S1(S2 で `kind` を拡張)、消費者は `stop_gate.py` と SKILL の手順。P0(`comment`)は変更コード自身を指すため、ゲートは強制せず助言とする。

**C2 — 処分と報告の文法**: 候補が「処分済み」とは、そのパスが変更集合に含まれるか、最終メッセージにパスが現れること。`Documentation impact: none —` の理由は空・定型句であってはならない。報告の行は `Updated:` / `Created:` / `No change needed:` / `Unresolved:` / `Proposed decision record:` / `Checks:`。生産者は SKILL の完了報告(S1 で最小形、S3 で理由の文法、S4 で `Created:`)、消費者は `stop_gate.py`。

**C3 — 設定キー**: `.living-documentation.json` の `related.max_candidates`(整数、候補の上限)と `related.min_name_length`(整数、名前参照の最小長)。`schemas/config.schema.json` が唯一の定義で、`common.load_config` がスキーマから検証する。生産者は S2、消費者は `find_related.py` と `stop_gate.py`。

**C4 — 配置規則の所在**: `references/practices.md` の「層・配置・近接性」の節にある、層ごとの置き場所と作成条件の表。生産者は S5、消費者は S4(`SKILL.md` から参照)。

## Assumptions

| ID | Assumption | Basis | Confidence | Applies to | Validation signal | If false |
|----|------------|-------|------------|------------|-------------------|----------|
| A1 | パス・ファイル名の本文参照による候補は、実用に耐えるノイズ水準に収まる | 設計時の推測のみ。実測なし | Low | S2, C3 | このリポジトリの直近の変更範囲(`--base` を変えて複数)で `find_related.py` を実行し、1 変更あたりの候補数の分布と、サンプル 20 件の無関係率を観察する。上限(既定 10)を中央値が超えない、かつ無関係率が過半でない | B1 |
| A2 | 「最終メッセージにパスが現れる」ことは、候補への処分の十分な代理指標になる | 設計時の推測。LLM が形式的に列挙して通す可能性は既知 | Medium | S1, C2, S3 | S1 の統合テストで、形式的な言及でも通ることを確認し、eval(費用承認後)で実際の処分の質を観察する | B2 |
| A3 | `common.py` の既存関数(`changed_files`、`classify`、`excluded`、`load_config`、`list_files`)を変更せずに再利用できる | 関数名と import 文のみ確認し、内部は未読 | Medium | S1, S2 | S1 の実装が `common.py` を変更せず既存 67 件を通す | B3 |
| A4 | 処分規則を入れると、LLM の更新・作成の判断が測定可能に改善する | 設計時の推測 | Low | S4, S6 | 費用承認後の eval で、プラグインあり/なしの差(Δ)が正である | B4 |

## Predicted branches

| ID | Applies to | Condition | Evidence | If true | If false | Authority |
|----|------------|-----------|----------|---------|----------|-----------|
| B1 | A1, S2 | 実測のノイズが許容範囲 | A1 の分布と無関係率 | Continue | `min_name_length` や上限の調整で収まるなら Re-plan(S2)。調整しても収まらなければ Re-specify(S2: P2 の条件を厳しくするか、P2 を助言のみにする) | S2 の仕様の所有者(ユーザー) |
| B2 | A2, S1 | 形式的な言及で通ることが実害になる | A2 の統合テストと eval の観察 | Continue(既知の限界として README に明記) | Re-specify(S1/C2: 構造化された処分行を要求する) | C2 の所有者(ユーザー) |
| B3 | A3, S1, S2 | `common.py` の変更なしで実装できる | S1 実装時の差分 | Continue | Re-plan(S1/S2: `common.py` の拡張を計画に含め、既存テストの回帰確認を追加)。公開関数の契約を変える必要があれば Re-decompose | S1 の仕様の所有者 |
| B4 | A4, S4, S6 | eval で Δ が正 | eval の結果 | Continue | Re-specify(S4: 規則の書き方を見直す)。規則自体に効果が無いとみなす場合は Escalate(続けるか撤回するかはユーザー) | ユーザー |

未登録の観察が重要な範囲(スコープ、受け入れ境界、契約、依存、スライス境界)に影響し得る場合は、既存の分岐に当てはめず、影響する下流作業を止めて、証拠とともにユーザーへ報告する。

## Sequence

依存行列(行が列に依存):

| | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|
| S1 | | | | | | |
| S2 | ● | | | | | |
| S3 | | | | | | |
| S4 | ● | | | | ● | |
| S5 | | | | | | |
| S6 | ● | ● | ● | ● | ● | |

循環はありません。順序は **S1 → S3 → S5 → S2 → S4 → S6** を推奨します。

- **S1 をウォーキングスケルトンにする理由:** 発見(`find_related.py`)、ゲート、手順の最小形、報告の文法(C1・C2)を一度に通し、契約の不整合を早期に表に出すためです。
- **S3 を S1 の直後に置く理由:** S3 は S1 に依存しませんが、同じ `stop_gate.py` を編集します。同時に進めず、逐次で行います。
- **S5 を S2 の前に置く理由:** S4 が S5 に依存するため、S4 の前に終えます。S2 とは独立なので、S2 の前でも後でもかまいません。
- **同一ファイルの編集:** `stop_gate.py`(S1, S3)、`SKILL.md`(S1, S4)、`find_related.py` と `config.schema.json`(S1, S2)は、重なるスライスを並行せず逐次で進めます。
- **S6 を最後にする理由:** README が最終的な挙動を記述するためです。

承認済みの計画(層ごとの 3 段階)からの変更点: スライスを「スクリプト/ゲート/文書」の層ではなく、観察できる成果の単位に切り直しました。スキーマの `related` キーは、キーを読む `find_related.py` と同じ S2 に移しました。README の統合は S6 に含めました。

## Open points

**Open point**: Spec Kit の `before_specify` フックはスライスごとに新しい機能ブランチを作り(`optional: false`)、`git-config.yml` の自動コミットが有効です。これは「依頼があるまでコミットしない」という制約と衝突します。
**Default**: ローカルの自動コミットは Spec Kit の既定どおり許可し、プッシュとマージは行わない。スライスごとの機能ブランチは `043-related-doc-discovery` を起点に順に作る(同一ファイルを編集するため逐次)。
**Alternative**: 自動コミットを無効にして実行する(ワークフローの設定を一時的に変える必要がある)。または、機能ブランチを作らず `043-related-doc-discovery` 1 本で進める。
**Impact**: 履歴の粒度と、スライスごとのレビュー・マージの方法が変わる。

**Open point**: スライスの切り方が、承認済みの層ごとの 3 段階から変わっています。
**Default**: 本書の 6 スライス(S1〜S6)で進める。
**Alternative**: 元の 3 段階のまま進める(S1+S2、S3、S4+S5+S6 に相当)。1 スライスが大きくなり、各スライスを単独で検証しにくくなる。
**Impact**: 仕様の数、ブランチの数、検証の単位。

## Change log

| Date | Change | Reason |
|------|--------|--------|
| 2026-10-17 | 初版(6 スライス) | 承認済みの計画を、観察できる成果の単位に分解した |
