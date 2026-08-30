# Tasks: 常時ロードルールの最小化と強制力の復元

**入力**: `specs/035-minimize-always-on-rules/` の設計文書
**前提**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**構成**: タスクはユーザーストーリー単位でグループ化され、各ストーリーは独立して検証できる。

**テストタスクなし**: 仕様はテストを要求していない。ADR-0005 / 0007 により hooks とスクリプトは撤去済みで、本機能でも復活させない。検証は [quickstart.md](./quickstart.md) の手動手順による。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（別ファイル・未完了タスクへの依存なし）
- **[Story]**: US1〜US4（Setup / Foundational / Polish には付かない）

## Path Conventions

リポジトリルートは `/Users/taikiogihara/work/my-claude-code`。以下のパスはすべてルート相対。

---

## Phase 1: Setup

- [X] T001 変更前のベースラインを記録する — `wc -c .claude/rules/*.md` と `wc -l .claude/rules/*.md` の出力を控え、[quickstart.md](./quickstart.md) 「前提」の表（合計 36,165 B、`live-documentation.md` 158 行）と一致することを確認する

---

## Phase 2: Foundational (Blocking Prerequisites)

**目的**: 「消す前に移す」を保証する。ここが終わるまで US1 の削減タスクは開始できない — 順序が逆になると内容が失われる。

- [X] T002 `docs/live-documentation-standards.md` を新規作成し、`.claude/rules/live-documentation.md` から § 0 ライフサイクル標準規格表（15 行）、§ 7.2 の解説（Minto と thinking-lenses への帰属）、§ 7.3 の解説（「読者レベルはラベルではない」の議論）、References（Martraire / ISO 各種 / Diátaxis / Minto 等）を**逐語で**移す。冒頭に、これが `.claude/rules/live-documentation.md` の論拠であり自動ロードされない旨を書く
- [X] T003 `.claude/skills/clarifier/SKILL.md` の References セクションに、`.claude/rules/clarifier.md` の References（ISO/IEC/IEEE 29148:2018、INVEST、SMART、Gherkin、MoSCoW、BABOK）を統合し、57 行目付近の「full citations at `rules/clarifier.md` § References」という文言を、SKILL.md 自身を指す形に更新する（research.md D7）

**チェックポイント**: T002 / T003 の移設先に内容が存在することを確認してから Phase 3 へ進む。

---

## Phase 3: User Story 2 - 資格情報保護が実際に効く (Priority: P1) 🎯 MVP

**目的**: 散文の「never read」を、クライアントが強制する設定に変換する。

**独立した検証**: [quickstart.md](./quickstart.md) § 3（拒否・非拒否・既知の副作用）と § 7（ADR）。他のストーリーを実装しなくても、この Phase だけで保護が有効になる。

**US1 より先に実行する理由**: T007（`permissions.md` の書き換え）は `permissions.deny` の実在を前提に「設定を正本として参照する」形になるため、設定が先に存在しなければならない。

### Implementation for User Story 2

- [X] T004 [US2] `.claude/settings.json` に `permissions.deny` を追加する — [contracts/permissions-deny.md](./contracts/permissions-deny.md) 「確定形」の 11 パターンを逐語で。単一先頭スラッシュ `/` で始まるパターンを含めないこと（research.md D1）
- [X] T005 [US2] `docs/adr/0014-restore-credential-deny-rules.md` を `adr` スキルで作成する — MADR 形式、status: Accepted。Context に ADR-0006 が同じ選択肢（「資格情報の deny のみ残す」）を検討して却下していた事実と、その後何が変わったか（research.md D10 の 3 点）を記載。Consequences に [contracts/permissions-deny.md](./contracts/permissions-deny.md) 「受け入れる帰結」の 3 項目（Edit/Write も塞がる、`.env.example` も塞がる、全プロジェクトへ波及）を負の帰結として記載。`permissions.md` から移設する Saltzer & Schroeder 1975 の出典をここに置く
- [X] T006 [US2] `docs/adr/0006-remove-permissions-config.md` を**変更しないこと**を確認する — `git diff a884d6f..HEAD -- docs/adr/0006-remove-permissions-config.md` が 0 行であること（ADR 不変性）
- [X] T007 [US2] `.claude/rules/permissions.md` を書き換える — [contracts/rule-inventory.md](./contracts/rule-inventory.md) の `permissions.md` 表に従う。資格情報リストは設定を正本として参照する形に置換、ファイル名部分一致の方針は散文で保持、**強制の到達範囲（Bash の `cat` 等は塞ぐ／任意サブプロセスは塞がない／OS レベルはサンドボックスが必要）を新規に明記**、「permissions: None anymore」節を現状に合わせて書き換え ADR-0014 を参照、References は T005 へ移設済みなので削除。目標 1,500 B

**チェックポイント**: quickstart.md § 3a / § 7 が通ること。§ 3b / § 3c / § 3d は新規セッションが必要なため Phase 7 で実施する。

---

## Phase 4: User Story 1 - 作業用の文脈を取り戻す (Priority: P1)

**目的**: 常時ロードの固定費を削減する。

**独立した検証**: [quickstart.md](./quickstart.md) § 1（合計 16,000 B 以下）と § 2（全ファイル 200 行未満）。

**依存**: Phase 2（移設完了）と T007（`permissions.md` の縮小。SC-001 の達成に必要）。

### Implementation for User Story 1

- [X] T008 [P] [US1] `.claude/rules/live-documentation.md` を強制中核のみに縮小する — [contracts/rule-inventory.md](./contracts/rule-inventory.md) の該当表に従い、§ 1〜§ 7 の判定規則・§ 7 の 5 層表・§ 7.1 必須度・§ 7.2 の四条件・§ 7.3 の依存方向規則・§ 7.4 違反類型・§ 7 非遡及注記・Override Handling・Out of Scope を保持。T002 の退避先へのリンクを 1 件置く。目標 5,000 B
- [X] T009 [P] [US1] `.claude/rules/clarifier.md` を ask/proceed ゲートのみに縮小する — 6 トリガー、「軽微かつ既定が自明なら進めて前提を明示」、How to ask（バッチ化・既定と仮定コスト・確信度タグ）、他ルールとの関係 1 行を保持。Minimal quality checks / Ambiguity patterns / Anti-patterns / References は T003 で移設済みのため削除。目標 1,300 B
- [X] T010 [P] [US1] `.claude/rules/git-workflow.md` をリポジトリ固有規約のみに縮小する — Conventional Commits の採用宣言 1 行、One logical change per commit、ブランチ命名 `<type>/<short-kebab-summary>`、Spec Kit ブランチ例外、short-lived/trunk-based 1 行、PR のタイトル文法と What/Why/How verified、`git push -u` と 4 回指数バックオフ（2/4/8/16s）を保持。破壊的 git 操作は `permissions.md` に既出のため削除。目標 1,100 B
- [X] T011 [P] [US1] `.claude/rules/mcp.md` をルーティングとレジストリ手順のみに縮小する — Usage rule、到達不能時の作法、付随的言及の例外、**AWS 公式スキルレジストリの 2 段呼び出し手順（`aws___search_documentation` を `topics: ["agent_skills"]` で → 返却された正確な `skill_name` で `aws___retrieve_skill`）**、GCP/Azure の否定情報を保持。カタログ表は削除。目標 1,300 B
- [X] T012 [US1] `.claude/CLAUDE.md` から 5 行の `@.claude/rules/...` インポートを削除する（`skill-routing.md`、`clarifier.md`、`thinking-lenses.md`、`live-documentation.md`、`mcp.md`）。Close-out 節の `live-documentation` 7 チェック列挙を 1 行に圧縮する
- [X] T013 [US1] quickstart.md § 1 と § 2 を実行し、合計 16,000 B 以下・全ファイル 200 行未満を確認する

**チェックポイント**: SC-001 / SC-002 達成。

---

## Phase 5: User Story 3 - 列挙の二重管理をやめる (Priority: P2)

**目的**: 実体とずれ得る列挙を構造的に排除する。

**独立した検証**: [quickstart.md](./quickstart.md) § 4。

- [X] T014 [US3] `.claude/rules/skill-routing.md` を縮小する — 複合作業の連鎖（コード変更 + 既存文書更新 → `coder` → `minto-rewriter`）、DADS のペアリング、reviewer→rewriter の順序と「結論未確定の初期草稿は builder」、`scrum-master` の否定的境界（一般的なプロジェクト管理は対象外）、`scrum-master` を含む複合規則、同点優先（成果物と動作が明示された簡潔な依頼は `minto-builder`）、`clarifier` フォールバックと 32 文字ヒューリスティックを保持。**スキル名の網羅的列挙は削除**。目標 1,000 B
- [X] T015 [US3] `.claude/CLAUDE.md` の「Skills（必須ルーティング）」節の 7 項目列挙を削除し、ルーティングは `rules/skill-routing.md` が担うこと・スキルの説明はハーネスが注入することを 1〜2 行で述べる形に置き換える
- [X] T016 [US3] quickstart.md § 4 を実行し、`.claude/skills/` の実体（speckit 以外 10 個）と矛盾する網羅的列挙が 0 件であることを確認する

**チェックポイント**: SC-004 達成。

---

## Phase 6: User Story 4 - 移設した根拠を辿れる (Priority: P3)

**目的**: 移設が削除になっていないことと、外部参照が壊れていないことを保証する。

**独立した検証**: [quickstart.md](./quickstart.md) § 5 と § 6。

- [X] T017 [P] [US4] `README.md` を更新する — L25 の `.claude/rules/` 説明を現状に合わせる、L98 のツリー注記から「lifecycle standards」を外し退避先に言及する、L174 の「カタログ（transport / パッケージ更新方針等）は `.claude/rules/mcp.md`」を実在する正本（`.mcp.json` および README 自身の Plugins 表）へ repoint する
- [X] T018 [P] [US4] `README.ja.md` を更新する — L15 の `.claude/rules/` 説明、L138 の mcp.md カタログ参照を `README.md` と同じ方針で repoint する
- [X] T019 [US4] quickstart.md § 5 を実行し、移設した規格名がすべて退避先に存在すること、`live-documentation.md` から退避先へ到達できること、`clarifier` SKILL.md に References が存在すること、`.claude/rules/` の `.md` が 7 件のままであることを確認する
- [X] T020 [US4] quickstart.md § 6 を実行し、壊れた参照が 0 件であること、およびシップされる成果物が `specs/035` を参照していないこと（`live-documentation.md` § 6 Intermediate-Artifact Isolation）を確認する

**チェックポイント**: SC-005 / SC-006 達成。

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T021 **未実施（新規セッション必須）** 新規セッションで quickstart.md § 3b / § 3c / § 3d を実行する — `.env` の読み取りが（`cat` 経由でも）拒否されること、`.claude/keybindings.json` 等が拒否**されない**こと、`.env.example` が読めなくなり `.env` の作成も拒否されること（意図した副作用）
- [ ] T022 **未実施（新規セッション必須）** 新規セッションで quickstart.md § 8 を実行する — `/context` の **Memory files** にルール 7 件と `CLAUDE.md` が現れ、`docs/live-documentation-standards.md` が現れないことを確認する。**`@import` 削除後もルール 7 件が読み込まれることが FR-011 の前提の実証**であり、1 件でも欠ければ import を戻す
- [X] T023 変更全体に対して `live-documentation.md` の 7 チェックを自己適用する — 特に § 1 Drift（公開契約が変わったファイルの説明文書が同一変更で更新されているか）、§ 5 No Redundancy（退避先とルールが矛盾していないか）、§ 6 Intermediate-Artifact Isolation、§ 7 Granularity Layering（新規 `docs/live-documentation-standards.md` がピラミッド構造を満たすか）
- [X] T024 最終計測を記録する — 削減率（36,165 B からの差）、ファイル別内訳、および `.claude/CLAUDE.md` の変化量

- [X] T025 `tests/run-removed-guardrails.sh` を ADR-0014 に合わせて更新する — **実装中に判明**: 同スイートは `settings.json` に `permissions` ブロックが存在しないことを表明しており、T004 で失敗した。表明を「`deny` のみ許容、`allow`/`ask` があれば失敗」へ変更し、加えて「`deny` の各項目は `~/` または `**/` でアンカーされた `Read` ルール」という ADR-0014 固有の制約を新規表明として追加。陽性1件・陰性2件（単一先頭スラッシュ混入、`Read` 以外のツール混入）で動作確認済み
- [X] T026 `tests/run-digital-agency-frontend-skill.sh` の `SYNC-SKILL-05` を更新する — **実装中に判明**: 同表明は `.claude/CLAUDE.md` がスキル名を列挙していることを不変条件としており、T015 で失敗した。列挙ではなく「CLAUDE.md がルーティング規則を指していること」の表明に変更。実際の合成順序を守る `SYNC-SKILL-05A` は変更なし
- [X] T027 両 README の `run-removed-guardrails.sh` 説明を更新する（§ 1 Drift — テストの契約が変わったため）

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (Setup)
   ↓
Phase 2 (Foundational — 移設) ← ブロッキング。ここを飛ばすと内容が失われる
   ↓
Phase 3 (US2 — 設定 + ADR)   ← T007 が Phase 4 の SC-001 達成に必要
   ↓
Phase 4 (US1 — ルール縮小)
   ↓
Phase 5 (US3 — 列挙廃止)      ← Phase 4 と独立に実行可能だが、計測の一貫性のため後段に置く
   ↓
Phase 6 (US4 — 参照修復)      ← Phase 3〜5 の結果に依存（何を repoint するかが確定してから）
   ↓
Phase 7 (Polish)
```

### User Story Dependencies

- **US2** は Foundational にのみ依存。単独で価値を出す（MVP）
- **US1** は Foundational と T007 に依存
- **US3** は Foundational にのみ依存。US1 と並行可能
- **US4** は US1 / US2 / US3 の結果に依存（参照先が確定してから修復する）

### Parallel Opportunities

- **Phase 2**: T002 と T003 は別ファイル → 並列可
- **Phase 4**: T008 / T009 / T010 / T011 は 4 つの別ルールファイル → 並列可。T012 は `CLAUDE.md` で単独
- **Phase 6**: T017 と T018 は別ファイル → 並列可

## Parallel Example: Phase 4

```text
# 4 つのルールファイルを同時に縮小する（互いに依存なし）:
T008 live-documentation.md
T009 clarifier.md
T010 git-workflow.md
T011 mcp.md
```

## Implementation Strategy

### MVP (Phase 1 → 3)

Phase 3（US2）まで完了すれば、**最も深刻度の高い保護が散文から強制に変わる**。この時点でルールの縮小が一切進んでいなくても、資格情報保護という単独の価値が成立する。

### Incremental Delivery

1. Phase 1–3 → 資格情報保護が有効（SC-003 / SC-007）
2. + Phase 4 → 常時コストが 16,000 B 以下（SC-001 / SC-002）
3. + Phase 5 → 列挙ドリフトが構造的に解消（SC-004）
4. + Phase 6–7 → 参照の整合と実挙動の確認（SC-005 / SC-006）

## Notes

- **順序の逆転が唯一の不可逆リスク**: Phase 2 の移設を飛ばして Phase 4 の削減を実行すると内容が失われる。Git 履歴から復元は可能だが、それは「traceability があるから壊してよい」理由にはならない
- **T021 / T022 は新規セッションを要する**: 設定変更とコンテキストロードの効果は、実行中のセッションには反映されない
- **コミットは明示依頼時のみ**（`git-workflow.md`）。本タスク群にコミット操作は含まれない
