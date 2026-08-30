# 契約: ルール逐条の保持/削除/移設対応表

**満たす要求**: FR-004〜FR-012, FR-014（削除根拠の分類）
**根拠**: [research.md](../research.md)

## 分類記号

| 記号 | 意味 | FR-014 の分類 |
|---|---|---|
| **K** | 常時ロードに保持（必要なら圧縮） | — |
| **N** | 削除。モデルのネイティブ知識・挙動、または Claude Code クライアント自身の挙動 | ネイティブ挙動 |
| **H** | 削除。ハーネスが自動注入済み | ハーネス注入済み |
| **S** | 設定へ移管（`.claude/settings.json`） | 移設 |
| **R** | 退避（移設先を明記） | 移設 |

---

## `.claude/rules/permissions.md` — 3,754 B → 目標 1,500 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（圧縮） | 適用範囲の宣言 |
| 評価順 deny → ask → allow | N | Claude Code クライアント自身の評価順。モデルへの指示ではない |
| 破壊的操作: `rm -rf` / `reset --hard` / `push --force` / `clean -f` | K（1 行に圧縮） | ハーネスも「取り消しにくい操作は事前確認」を持つが、対象の明示は安全上の冗長性として残す |
| 破壊的操作: DB テーブル削除、未コミット変更の上書き | K | 非自明。ツールが検出できず自己適用が必要 |
| 破壊的操作: AWS リソース変更（毎回確認、ADR-0009） | K | 非自明。`README.md` と `install.sh` が本節を名指しで参照 |
| パッケージインストールはプロジェクトスコープのみ | K（圧縮） | 非自明なリポジトリ方針 |
| 資格情報リスト（`.env`、`secrets/`、`.ssh/`、`.aws/`、秘密鍵） | **S** | [permissions-deny.md](./permissions-deny.md) へ |
| 資格情報: ファイル名部分一致（`secret`/`credential`/`token`/`key`） | K | グロブ化不可（research.md D2）。散文として残す唯一の資格情報項目 |
| 強制の到達範囲（Bash の `cat` 等は塞ぐ／任意サブプロセスは塞がない） | **K（新規追加）** | research.md D4。境界を書かないと強制範囲を誤認させる |
| ネットワーク default deny（`curl \| bash`、非 HTTPS） | K（圧縮） | 非自明 |
| 「`.claude/settings.json` permissions: None anymore」節 | K（**書き換え**） | 事実が変わる。deny が存在する状態を正しく記述し、ADR-0014 を参照 |
| References（Saltzer & Schroeder 1975） | **R** → `docs/adr/0014-*.md` | 最小権限・fail-safe defaults は ADR-0014 の決定根拠そのもの。ADR に置くのが正しい所在 |

## `.claude/rules/live-documentation.md` — 14,760 B → 目標 5,000 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（圧縮） | |
| § 0 ライフサイクル標準規格表（15 行、ISO/PMBOK/PRINCE2/arc42 等） | **R** → `docs/live-documentation-standards.md` | 典型的な diff の判定を一切変えない参照資料。単独で最大の削減源 |
| § 1 Drift Detection の判定規則 | K | 強制中核 |
| § 2 Separate-Doc-PR Detection | K（圧縮） | 強制中核 |
| § 3 Auto-generation Recommendation | K（圧縮） | 強制中核 |
| § 4 Proximity Enforcement | K（圧縮） | 強制中核 |
| § 5 No Redundancy + Compression exception | K | 強制中核。§7 と不可分 |
| § 6 Intermediate-Artifact Isolation | K（圧縮） | 強制中核 |
| § 7 粒度層の表（L1〜L5） | K | 規範 |
| § 7.1 必須度（L1 MUST / L2–L5 SHOULD） | K | 規範 |
| § 7.2 四条件（shared ground / answer first / MECE / one logic） | K | 規範 |
| § 7.2 の解説（Minto と thinking-lenses への帰属説明） | **R** → `docs/live-documentation-standards.md` | 論拠であって規範ではない |
| § 7.3 依存方向の規則（上位層の用語には依拠可、下位層の用語には不可） | K | 規範 |
| § 7.3 の解説（「読者レベルはラベルではない」の議論） | **R** → `docs/live-documentation-standards.md` | 論拠 |
| § 7.4 違反類型 | K（圧縮） | 規範 |
| § 7 の非遡及注記 | K | 適用範囲の限定。落とすと遡及適用と誤読される |
| Override Handling | K | 強制中核 |
| Out of Scope | K | 強制中核（過剰適用の抑制） |
| References（Martraire、ISO 各種、Diátaxis、Minto 等） | **R** → `docs/live-documentation-standards.md` | |

## `.claude/rules/clarifier.md` — 4,589 B → 目標 1,300 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（圧縮） | 「唯一の正典的ゲート」という位置づけは維持が必要 |
| When to clarify — 6 トリガー | K（圧縮） | ゲートの本体 |
| 「軽微かつ既定が自明なら進めて前提を明示」 | K | ゲートの本体。ハーネスの「判断できるなら動け」と整合させる要 |
| Minimal quality checks | **R** → `.claude/skills/clarifier/SKILL.md` | スキルの品質チェックと重複 |
| Ambiguity patterns（vague quantifiers 他 6 類型） | **R** → `.claude/skills/clarifier/SKILL.md` | 目録は elicitation 実施時にのみ要る |
| How to ask（バッチ化、既定と仮定コスト、確信度タグ） | K（圧縮） | 非自明な作法 |
| Anti-patterns | **R** → `.claude/skills/clarifier/SKILL.md` | |
| Interaction with other rules and skills | K（1 行に圧縮） | 相互参照は残すが列挙は不要 |
| References（ISO 29148、INVEST、SMART、Gherkin、MoSCoW、BABOK） | **R** → `.claude/skills/clarifier/SKILL.md` | **SKILL.md 57 行目が本節を名指しで参照している。削除すると §1 Drift 違反になるため、移設と同時に SKILL.md の文言も更新する**（research.md D7） |

## `.claude/rules/git-workflow.md` — 4,598 B → 目標 1,100 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（1 行） | |
| Conventional Commits の採用宣言 `<type>(<scope>)?: <subject>` | K（1 行） | 「このリポジトリが採用している」ことは非自明 |
| types 一覧と「spec 必須は feat/fix のみ、他は Angular 由来」の考証 | **N** | 出力を一切変えない考証 |
| Subject: 命令形・≤50字・句点なし | K（採用宣言に統合した 1 行） | 規約値は非自明だが、様式の説明は N |
| Body の書き方・72 桁折返し・why not what | **N** | |
| Footers / trailer の git 慣習解説、`Co-authored-by` の GitHub 挙動 | **N**+**H** | ハーネスが trailer を出力済み |
| Breaking change の `!` と `BREAKING CHANGE:` の等価性 | **N** | |
| One logical change per commit | K | |
| Branch naming `<type>/<short-kebab-summary>` | K | リポジトリ固有規約 |
| `git check-ref-format` の禁則文字解説 | **N** | |
| Spec Kit ブランチの例外（手で命名しない） | K | リポジトリ固有 |
| short-lived / trunk-based | K（1 行） | |
| PR: タイトル文法、本文 What / Why / How verified | K | リポジトリ固有 |
| `git push -u`、失敗時 4 回指数バックオフ（2/4/8/16s） | K | 非自明な具体値 |
| 「頼まれた時だけ commit / push」「指定ブランチ以外へ push しない」 | **H** | ハーネスのシステムプロンプトが同内容を規定 |
| 破壊的 git 操作は確認 | **R** → `permissions.md`（既存） | 同一内容の二重記載を解消 |
| References（Conventional Commits、Tim Pope、Pro Git、trunk-based 他） | **N** | 周知の出典 |

## `.claude/rules/skill-routing.md` — 3,595 B → 目標 1,000 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（1 行） | |
| 複合作業を先に解決（コード変更 + 既存文書更新 → `coder` → `minto-rewriter`） | K | description からは導けない |
| DADS: `coder` → `digital-agency-frontend` の並び、レビュー単独時 | K | 同上 |
| 「コード実装・挙動変更 → `coder`」 | **H** | description が同内容を持つ |
| 文書 3 スキルの各行（reviewer / rewriter / builder の説明） | **H** | description が同内容を持つ |
| reviewer → rewriter の順序、および「結論未確定の初期草稿は builder」 | K（圧縮） | 使い分けの境界は非自明 |
| `scrum-master` の対象範囲説明・多言語トリガー例 | **H** | description と `when_to_use` が同内容を持つ |
| `scrum-master` の否定的境界（一般的なプロジェクト管理は対象外） | K | 否定情報は description に無い |
| `scrum-master` の複合規則（成果物を伴う場合は文書スキルを後段に） | K（複合規則へ統合） | |
| 同点優先（成果物と動作が明示された簡潔な依頼は `clarifier` ではなく `minto-builder`） | K | 非自明な優先規則 |
| `clarifier` フォールバックと 32 文字ヒューリスティック | K（圧縮） | 具体的な閾値は非自明 |
| **スキル名の列挙そのもの** | **H** | 実測でドリフト済み（10 個中 3 個欠落）。二重管理の構造的解消（research.md D6） |

## `.claude/rules/mcp.md` — 2,927 B → 目標 1,300 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Purpose 段落 | K（1 行） | |
| サーバカタログ表（6 行、transport / endpoint / use case） | **H** | `.mcp.json` が正本であり、各サーバの自己記述はハーネスが注入する。**`README.md` 174 行目と `README.ja.md` 138 行目がこの表を参照しているため、同一変更内で repoint が必要**（FR-013） |
| Usage rule（AWS / GCP / Azure → 各サーバ、必須呼び出し） | K | 強制中核 |
| 到達不能時は警告してから訓練知識で答える | K | 非自明な作法 |
| 付随的言及は MCP 呼び出し不要 | K | 過剰適用の抑制 |
| AWS 公式スキルレジストリの 2 段呼び出し手順 | K | **推測不能。本ファイル最大の価値**。`topics: ["agent_skills"]` での検索 → 返却された正確な `skill_name` での取得 |
| GCP に同等物なし / Azure は未検証（OAuth 未認可） | K（圧縮） | 否定情報は再調査の重複を防ぐ |

## `.claude/rules/thinking-lenses.md` — 1,942 B → 変更なし

既に最小。削減余地が乏しい。遵守が観測不能であるという既知の論点は [spec.md](../spec.md) 前提条件に記録済みで、本機能では扱わない。

## `.claude/CLAUDE.md` — 4,893 B

| 節 | 処置 | 根拠 |
|---|---|---|
| Core Principles 1〜4 | K | |
| `@.claude/rules/skill-routing.md` | **削除** | 冗長。`paths:` なしの `.claude/rules/*.md` は無条件ロードされる（FR-011） |
| Before the first answer 4 項目 | K | |
| `@.claude/rules/clarifier.md`、`@.claude/rules/thinking-lenses.md` | **削除** | 同上 |
| Close-out 節 | K（`live-documentation` の 7 チェック列挙を圧縮） | |
| `@.claude/rules/live-documentation.md` | **削除** | 同上 |
| Skills（必須ルーティング）の 7 項目列挙 | **H** | research.md D6 |
| MCP 節 | K（1 行） | |
| `@.claude/rules/mcp.md` | **削除** | 同上 |

---

## 目標値の集計

| ファイル | 現状 (B) | 目標 (B) |
|---|---:|---:|
| `clarifier.md` | 4,589 | 1,300 |
| `git-workflow.md` | 4,598 | 1,100 |
| `live-documentation.md` | 14,760 | 5,000 |
| `mcp.md` | 2,927 | 1,300 |
| `permissions.md` | 3,754 | 1,500 |
| `skill-routing.md` | 3,595 | 1,000 |
| `thinking-lenses.md` | 1,942 | 1,942 |
| **合計** | **36,165** | **13,142** |

目標合計 13,142 B は SC-001 の上限 16,000 B を下回る（削減率 約 64%）。個々の目標値は上限ではなく見込みであり、判定は**合計値**で行う。
