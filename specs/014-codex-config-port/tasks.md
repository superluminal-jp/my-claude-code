# Tasks: `.claude` 設定の Codex CLI への包括移植と挙動同期

**Input**: Design documents from `/specs/014-codex-config-port/`

**Prerequisites**: [plan.md](plan.md)(必須)、[spec.md](spec.md)(必須、ユーザーストーリー)、[research.md](research.md)、[data-model.md](data-model.md)、[contracts/](contracts/)

**Tests**: 挙動テスト(behavior suites)はこのリポジトリの既存文化(`tests/run-*.sh`)であり、spec が明示的に要求(FR-009/SC-005)しているため含む。ユニットテストの新設は求められていない。

**Organization**: ユーザーストーリー別にタスクをグループ化。**US1(構成要素対応表)は優先度 P1 だが、受け入れ基準が他ストーリーの成果物の存在を前提とする集約監査のため、意図的に他ストーリーの後(Phase 8)に配置する** — spec 本文にも「他のすべてのストーリーの受け入れ判定の基準になる」と明記されている。

**改訂履歴**: `/speckit-analyze` の指摘(C1/C2/C3)を反映し、T003(CLAUDE.md 確定)・T018(SYNC-11 allow 一致検証)・T021(SYNC-12 秘密情報非平文検証)を追加(30→33 タスク)。それに伴い T003 以降の ID を振り直した。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可(別ファイル、依存なし)
- **[Story]**: 対応するユーザーストーリー(US1〜US6)
- 各タスクは正確なファイルパスを含む

## Path Conventions

このリポジトリは単一プロジェクト構成。主な変更対象: `.codex/`(新規ソース)、`install.sh`(既存、修正)、`scripts/guardrails/`(既存、追加)、`.claude/hooks/`(既存、1 ファイル改修)、`tests/`(新規スイート追加)、`.agents/skills/`(既存、削除)、`CLAUDE.md`(既存、作業ツリー未確定変更の確定)。

---

## Phase 1: Setup

**Purpose**: 後続タスクが埋めていく骨格ファイルを用意し、作業ツリーに残る未確定変更を確定させる

- [X] T001 `tests/run-codex-sync.sh` の骨格を作成: shebang・`set -euo pipefail`・PASS/FAIL カウンタ・色付き出力を `tests/run-destructive-command-guard.sh` と同じ規約で用意する(チェック本体はまだ入れない)
- [X] T002 [P] `.codex/README.md` の骨格を作成: [contracts/deployment-map.md](contracts/deployment-map.md) の必須列(構成要素/Codex 側実体/分類/同期方式/挙動差分・制約/根拠)を持つ表を作り、同契約の必須行(全項目)を分類 `TODO` で先に列挙する
- [X] T003 [P] `CLAUDE.md` の作業ツリー未確定変更を確定させる(`/speckit-analyze` C1): 現状ルートの `CLAUDE.md` から SPECKIT ブロック(`<!-- SPECKIT START -->`〜`<!-- SPECKIT END -->`)が除去され末尾改行もない状態になっている。この除去が意図的(spec 011 完了に伴う通常のクリーンアップ)かを確認し、意図的なら末尾に改行を付けてそのまま確定、そうでなければ SPECKIT ブロックを復元する。いずれの場合も spec.md Assumptions(作業ツリーの未確定変更)が満たされたことになる — **完了**: SPECKIT ブロックはこのリポジトリの実際のワークフロー(スキルベースの `/speckit-*`)では使われておらず、spec 011 完了後の陳腐化した参照だったため、除去済み(意図的なクリーンアップ)として確定。末尾改行を復元した

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 複数ストーリー(US1・US5)に影響する既存ドリフトの解消。**この解消自体は Claude Code 側の既存決定(コミット `33c82eb`, PR #48)への追従であり、新しい判断ではない**

**⚠️ CRITICAL**: この解消なしに US1 の対応表(SYNC-08)も US5 のリンク健全性(SYNC-01/02)も正しく検証できない

- [X] T004 [P] `install.sh` の `CUSTOM_SKILLS` から `advisor`・`domain-model`・`ubiquitous-language` を削除する(コミット `33c82eb` でリポジトリ `.claude/skills/` から意図的に削除済みのため — research.md R0/R2 参照)。削除箇所にコミットハッシュを根拠として一言コメントを添える
- [X] T005 [P] リポジトリの壊れたシンボリックリンク 3 件 `.agents/skills/advisor`・`.agents/skills/domain-model`・`.agents/skills/ubiquitous-language` を削除する

**Checkpoint**: スキル一覧のドリフトが解消され、以降のストーリーが正しい前提の上に積み上がる

---

## Phase 3: User Story 2 - 指針プロースが Codex に確実に読まれる (Priority: P1) 🎯 MVP

**Goal**: `CLAUDE.md`+`rules/` 相当の指針が `~/.codex/AGENTS.md`(Codex の公式グローバル探索位置)から確実に、サイズ予算内で読まれる

**Independent Test**: [quickstart.md](quickstart.md) §1〜2 — `install.sh` 実行後、`~/.codex/AGENTS.md` が `.codex/AGENTS.md` と一致し 32 KiB 以内であることを確認する

### Implementation for User Story 2

- [X] T006 [US2] リポジトリルート `AGENTS.md` を修復する: 現在の残骸(`` `.codex/agents/` `` の 1 行のみ)を削除し、このリポジトリ固有の内容のみを残す(このリポジトリ固有の追加指針はない旨の短い注記をデフォルトとする)。共通プロースはここに置かない(research R1/R0、FR-003)
- [X] T007 [US2] `.codex/AGENTS.md` を新設し、共有プロース(ツール使用原則、MCP 使い分け表、編集規約、リクエスト時の注意、ガードレール概要)を記述する。ガードレール概要は R0 訂正後の実態(`~/.codex/config.toml` 管理区間による 4 アダプタ登録)に合わせて書く — `hooks.json` には言及しない — **完了**: 7924 バイト(32 KiB 予算内)
- [X] T008 [US2] `install.sh` の 1b(`AGENTS_MD_SRC`)を `"$SCRIPT_DIR/AGENTS.md"` から `"$SCRIPT_DIR/.codex/AGENTS.md"` に変更する(T007 に依存)
- [X] T009 [US2] `tests/run-codex-sync.sh`(T001)に SYNC-03(`.codex/AGENTS.md` サイズ ≤ 32 KiB、28 KiB 超で WARN)と SYNC-06(`.codex/AGENTS.md` と `~/.codex/AGENTS.md` の内容一致、home 未展開時は skip-warn)を追加する(T007, T008 に依存)。SYNC-06 は現状 FAIL(`~/.codex/AGENTS.md` が旧内容のまま — `install.sh` 再実行で解消、意図通りの検出)

**Checkpoint**: US2 は独立して検証可能 — `install.sh` 実行 → `~/.codex/AGENTS.md` の内容とサイズを確認

---

## Phase 4: User Story 3 - 権限・承認挙動の同等再現 (Priority: P2)

**Goal**: allow/ask/deny 相当の挙動を Codex ネイティブ機構(Rules)+ 既存フック構成で再現し、プロンプト内秘密情報検知(research R4 で昇格)も移植する

**Independent Test**: [quickstart.md](quickstart.md) §3 の破壊的コマンド・credential 保護・秘密情報検知・allow リストの各行

### Implementation for User Story 3

- [X] T010 [P] [US3] `scripts/guardrails/prompt-secret-scan.sh` を新設する: `.claude/hooks/user-prompt-submit.sh` の検知ロジック(AWS/GitHub/Slack/Google キー、秘密鍵ヘッダ)を移し、`specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md` と同型の契約(stdin `{"prompt": "..."}` → stdout `{"decision":"allow"|"deny","reason":"..."}`、秘密情報の値自体は reason に含めない)にする
- [X] T011 [US3] `.claude/hooks/user-prompt-submit.sh` を薄いラッパーに改修する: `pre-bash.sh` と同じ 3 段解決順(プロジェクト内 `scripts/guardrails/` → `~/.claude/scripts/guardrails/` → リポジトリ相対フォールバック)で T010 のスクリプトを呼び、既存の `exit 2`/`exit 0` 挙動を維持する(T010 に依存)
- [X] T012 [P] [US3] `.codex/hooks/prompt-secret-adapter.sh` を新設する: 他 3 アダプタと同じ解決順で T010 のスクリプトを呼び、Codex `UserPromptSubmit` の応答形状に変換する(T010 に依存)
- [X] T013 [US3] 挙動テスト `tests/run-prompt-secret-guard.sh` を新設する: `tests/run-destructive-command-guard.sh` と同じ構造で、共有スクリプト・Claude ラッパー・Codex アダプタの 3 点を検証する(T011, T012 に依存)
- [X] T014 [US3] `install.sh` 1d の Python `ADAPTERS` リストに `("prompt-secret-adapter.sh", "UserPromptSubmit", None)` を追加し、TOML 生成ループを matcher が `None` のときは `matcher = "..."` 行を出力しないよう修正する(`UserPromptSubmit` に matcher 概念が必要か公式仕様・実セッションで要確認 — 未確認なら matcher なしで先に進め、research.md に確認結果を追記する)(T012 に依存)
- [X] T015 [P] [US3] `.codex/rules/guardrails.rules` を新設する: allow に `tests/run-*.sh`・`scripts/check-mcp-consistency.sh`・`shellcheck`・`shfmt`・`jq`・`yamllint`・git 読み取り系(`status`/`diff`/`log`/`fetch`)+`commit`、prompt に git 書き込み系(`add`/`checkout`/`branch`/`stash`/`pull`)を `prefix_rule` で宣言する(research R5)。既存の `~/.codex/rules/default.rules` は参照・編集しない
- [X] T016 [US3] `install.sh` に新規ステップ 1e を追加する: `.codex/rules/guardrails.rules` → `~/.codex/rules/guardrails.rules` へコピー(`default.rules` には一切触れない)(T015 に依存)
- [X] T017 [US3] `tests/run-codex-sync.sh` に SYNC-05(`.codex/hooks/` の 4 アダプタ全件の実在+実行可能、install.sh 側 `ADAPTERS` リストとの整合)と SYNC-10(`guardrails.rules` の `prefix_rule(` 構文・`decision` 値域の静的検査)を追加する(T014, T016 に依存)
- [X] T018 [US3] `tests/run-codex-sync.sh` に SYNC-11 を追加する(`/speckit-analyze` C2): 代表カテゴリ(検証スイート・lint ツール・git 読み取り系)について、`.claude/settings.json` の `permissions.allow` と `.codex/rules/guardrails.rules` の `allow` 宣言の双方に対応エントリが存在することを `jq`(settings.json 側)と `grep`(rules 側)で突き合わせる静的チェックを実装する(実際の許可判定エンジンは模擬しない、contracts/sync-check.md SYNC-11 契約に従う)(T015 に依存)

**Checkpoint**: US3 は独立して検証可能 — 破壊的コマンド・credential 読み書き・秘密情報プロンプト・allow リストの代表操作を試行

---

## Phase 5: User Story 4 - MCP サーバが Codex でも同じカタログで使える (Priority: P2)

**Goal**: `.mcp.json` の 6 サーバと同一カタログを `~/.codex/config.toml` の `[mcp_servers.*]` に提供する

**Independent Test**: [quickstart.md](quickstart.md) §3 の MCP 行 — Codex CLI から 6 サーバが列挙・利用でき、秘密情報が平文で含まれない

### Implementation for User Story 4

- [X] T019 [US4] `install.sh` に新規ステップ 1g を追加する: 1d と同じ「管理マーカー区間を `~/.codex/config.toml` に追記」パターンで、`.mcp.json` の 6 サーバ(aws-knowledge, aws-documentation, bedrock-agentcore, strands-agents, google-developer-knowledge, microsoft-learn)を `[mcp_servers.*]` として upsert する。stdio は `command`/`args`/`env`、HTTP は `url`/`bearer_token_env_var` を使い、平文キーを書かない。`google-developer-knowledge` は `GOOGLE_DEV_KNOWLEDGE_API_KEY` 未設定時にスキップする(既存の Claude 側 `upsert_user_mcp` 呼び出し群と同じ判定ロジックを踏襲)
- [X] T020 [US4] `tests/run-codex-sync.sh` に SYNC-04(`.mcp.json` サーバ集合 ⊆ `~/.codex/config.toml` の `mcp_servers` 集合、home 未展開時は skip-warn)を追加する(T019 に依存)
- [X] T021 [US4] `tests/run-codex-sync.sh` に SYNC-12 を追加する(`/speckit-analyze` C3): `~/.codex/config.toml` の `[mcp_servers.*]` 管理区間に対し、T010 の `prompt-secret-scan.sh` と同じ秘密情報正規表現(AWS/GitHub/Slack/Google キー、秘密鍵ヘッダ)を grep し、平文一致が 0 件であることを確認する(home 依存 skip-warn、contracts/sync-check.md SYNC-12 契約に従う)(T019, T010 に依存)

**Checkpoint**: US4 は独立して検証可能 — Codex セッションで MCP サーバ一覧確認 + 代表クエリ + 秘密情報非平文確認

---

## Phase 6: User Story 5 - スキルとカスタムコマンドの単一ソース利用 (Priority: P2)

**Goal**: 対応表で移植対象とされた全スキルが `~/.agents/skills` から発見・起動でき、`/verify-config` 相当のカスタムプロンプトが使える

**Independent Test**: [quickstart.md](quickstart.md) §3 のスキル発見・プロンプト行 — 壊れたリンクが 0 件、検証入口が呼べる

### Implementation for User Story 5

- [X] T022 [P] [US5] `.codex/prompts/verify-config.md` を新設する: `.claude/commands/verify-config.md` と同じ検証手順を指す薄いプロンプトとし、検証ロジック自体は複製しない(research R7)
- [X] T023 [US5] `install.sh` に新規ステップ 1f を追加する: `.codex/prompts/verify-config.md` → `~/.codex/prompts/verify-config.md` へコピー(T022 に依存)
- [X] T024 [US5] `tests/run-codex-sync.sh` に SYNC-01(リポジトリ `.agents/skills/` の壊れリンク 0 件、T005 が前提)、SYNC-02(`~/.agents/skills/` の壊れリンク 0 件、home 依存 skip-warn)、SYNC-09(`.codex/prompts/verify-config.md` と `.claude/commands/verify-config.md` の手順対応)を追加する(T005, T023 に依存)

**Checkpoint**: US5 は独立して検証可能 — スキル一覧・カスタムプロンプト呼び出し

---

## Phase 7: User Story 6 - ドリフト検知による恒常同期 (Priority: P3)

**Goal**: 対応ペアの片側だけの変更を検証スイートが検出する

**Independent Test**: [quickstart.md](quickstart.md) §4 の 5 破壊テストすべてで対応チェックのみが FAIL する

### Implementation for User Story 6

- [X] T025 [US6] `tests/run-codex-sync.sh` に SYNC-07(`~/.claude/scripts/guardrails/` の実在+実行可能)と SYNC-08(`.codex/README.md` の被覆: `.claude/` 実要素との突合せで未分類 0 件)を追加する(T009・T017・T018・T020・T021・T024 の全 SYNC 項目が出揃っていることに依存)
- [X] T026 [US6] [contracts/sync-check.md](contracts/sync-check.md) の「破壊テストでの受け入れ」5 操作を実際に行い、それぞれ対応チェックのみが FAIL することを確認する。期待どおり FAIL しないチェックがあれば `tests/run-codex-sync.sh` を修正する(T025 に依存)

**Checkpoint**: 同期健全性スイートが完成し、実際にドリフトを検出できることを検証済み

---

## Phase 8: User Story 1 - 構成要素の完全対応表と移植完了 (Priority: P1、集約監査のため最後に配置)

**Goal**: `.codex/README.md` が全 `.claude/` 構成要素を 100% 分類し、移植対象の実体がすべて存在する

**Independent Test**: [quickstart.md](quickstart.md) §5 — 対応表と実ファイルの突合せ、SYNC-08 の PASS

### Implementation for User Story 1

- [X] T027 [US1] `.codex/README.md`(T002 の骨格)の全行を実内容で埋める: 各構成要素について分類(移植済み(013)/本機能で移植(014)/対象外)、Codex 側実体パス、同期方式、挙動差分・制約、根拠(012 Q番号/research R番号/spec FR番号)を記載する。対象外行には理由を必須で書く(T006〜T026 の全実装が確定していることに依存 — 実体パスと既知の挙動差分を正確に転記するため)
- [X] T028 [US1] `tests/run-codex-sync.sh` の SYNC-08 を実行し、未分類要素が 0 件になることを確認する。検出された漏れは T027 に戻って対応表に追記する(T027, T025 に依存)

**Checkpoint**: SC-001(分類率 100%)・SC-006(所在と同期方式の記載)を満たす

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: 複数ストーリーにまたがる仕上げ

- [X] T029 [P] `.claude/hooks/README.md` の Hook index 表に `user-prompt-submit.sh` の共有スクリプト化(`scripts/guardrails/prompt-secret-scan.sh`)と対応する `.codex/hooks/prompt-secret-adapter.sh` の存在を追記する(FR-012, Live Documentation)
- [X] T030 [P] ルート `README.md`・`README.ja.md` が Codex 対応に言及している箇所があれば、完了後の実態(4 アダプタ・Rules・MCP カタログ・プロンプト・対応表)に合わせて更新する。言及箇所がなければ何もしない(FR-012)
- [X] T031 「Codex 設定はユーザースコープ展開を主とする」というメンテナ決定について、`adr` スキルを使い ADR を提案する(plan.md Constitution Check の指摘事項)
- [X] T032 既存挙動スイート全体(`tests/run-*.sh`)+ 新規 `tests/run-codex-sync.sh` + `tests/run-prompt-secret-guard.sh` を実行し、全 PASS を確認する(SC-007: Claude Code 側無劣化)
- [X] T033 [quickstart.md](quickstart.md) §3 の実 Codex セッション検証チェックリストを手動で実施し、結果(特に PreToolUse 三値スキーマの検証結果 — research R3 の未解決事項)を research.md に日付付きで追記する

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — 即開始可
- **Foundational (Phase 2)**: Setup 完了後。US1(Phase 8)と US5(Phase 6)の前提
- **User Story 2 (Phase 3, P1)**: Foundational 完了後。他ストーリーに依存しない
- **User Story 3 (Phase 4, P2)**: Foundational 完了後。US2 に依存しない(並行可)
- **User Story 4 (Phase 5, P2)**: Foundational 完了後。US3(T010)の秘密情報検知ロジックに SYNC-12(T021)のみ依存(それ以外は独立)
- **User Story 5 (Phase 6, P2)**: Foundational(T005)完了後。他ストーリーに依存しない(並行可)
- **User Story 6 (Phase 7, P3)**: US2・US3・US4・US5 が追加した SYNC チェック項目に依存(それらの完了後)
- **User Story 1 (Phase 8, P1 だが最後)**: US2〜US6 すべての実体・挙動差分に依存(対応表が正確な内容を転記するため)
- **Polish (Phase 9)**: 全ストーリー完了後

### Parallel Opportunities

- Setup: T001, T002, T003 は並列
- Foundational: T004, T005 は並列
- US2〜US5(Phase 3〜6)は Foundational 完了後、**フェーズ単位でおおむね並列着手可能**(US4 の T021 のみ US3 の T010 完了を待つ。US6 と US1 は他フェーズの成果物待ち)
- 各フェーズ内の [P] タスク(T010/T012、T015、T022 等)は並列
- Polish の T029, T030 は並列

---

## Parallel Example: Foundational + User Story 2/3/4/5 の並列着手

```bash
# Foundational を先に完了させたあと:
Task: "T004 install.sh の CUSTOM_SKILLS から advisor/domain-model/ubiquitous-language を削除"
Task: "T005 .agents/skills/ の壊れリンク3件を削除"

# Foundational 完了後、4ストーリーを並列着手(US4 の SYNC-12 のみ US3 の T010 完了を待つ):
Task: "T006-T009 (US2) AGENTS.md 修復・.codex/AGENTS.md 新設・install.sh 1b 修正・SYNC-03/06"
Task: "T010-T018 (US3) prompt-secret 共有スクリプト・アダプタ・guardrails.rules・SYNC-05/10/11"
Task: "T019-T021 (US4) install.sh 1g で Codex MCP カタログ upsert・SYNC-04/12"
Task: "T022-T024 (US5) verify-config プロンプト・install.sh 1f・SYNC-01/02/09"
```

---

## Implementation Strategy

### MVP First (User Story 2 のみ)

1. Phase 1: Setup 完了
2. Phase 2: Foundational 完了(CRITICAL — US1/US5 の前提)
3. Phase 3: User Story 2 完了
4. **STOP and VALIDATE**: [quickstart.md](quickstart.md) §1〜2 で指針プロースが `~/.codex/AGENTS.md` から読まれることを確認
5. これが最小の「Codex で指針が効く」状態(MVP)

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US2 追加 → 指針プロース到達を検証 → MVP
3. US3 追加 → ガードレール・権限パリティを検証
4. US4 追加 → MCP カタログ一致・秘密情報非平文を検証
5. US5 追加 → スキル・プロンプト単一ソース利用を検証
6. US6 追加 → ドリフト検知の実効性を検証
7. US1 追加(集約監査) → 対応表の完全性を検証、全体のクローズアウト
8. Polish → ドキュメント整合・ADR 提案・全回帰確認

### Parallel Team Strategy

複数人で作業する場合、Foundational 完了後に US2/US3/US4/US5 を並行アサイン可能(US4 の T021 のみ US3 の T010 完了を待つ点に注意)。US6 と US1 は他ストーリーの成果物が揃うまで着手できない。

---

## Notes

- [P] タスク = 別ファイル、依存なし
- [Story] ラベルはトレーサビリティのため必須(US1〜US6)
- US1 が最後に来るのは優先度の格下げではなく、受け入れ基準が集約監査である構造上の必然(spec.md 本文にも明記)
- `install.sh` への変更は既存の 1b/1c/1d ステップの**修正**(T004, T008, T014)と、既存パターンを踏襲した新規ステップ 1e/1f/1g の**追加**(T016, T023, T019)に限られる — `hooks.json` 等の新方式は導入しない(research.md R0)
- T003(CLAUDE.md)・T018(SYNC-11)・T021(SYNC-12)は `/speckit-analyze` の指摘(C1/C2/C3)を受けて追加したタスク
- タスクごと、または論理単位でコミットする
- 各チェックポイントで独立検証してから次へ進む
