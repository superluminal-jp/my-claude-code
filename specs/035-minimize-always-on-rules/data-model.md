# Phase 1 データモデル: 常時ロードルールの最小化

**仕様**: [spec.md](./spec.md) | **契約**: [contracts/](./contracts/)

本機能に実行時のデータ構造はない。ここでの「エンティティ」は、変更対象となる**成果物の種別**と、それぞれが満たすべき**不変条件**である。不変条件は仕様の機能要求から導出しており、[quickstart.md](./quickstart.md) の検証手順と 1 対 1 に対応する。

---

## E1. 常時ロードルール (Always-on Rule)

`.claude/rules/` 直下の `.md` ファイル。セッション開始時に無条件で読み込まれる。

| 属性 | 値 |
|---|---|
| 所在 | `.claude/rules/*.md` |
| ロード条件 | `paths:` フロントマターを持たない限り無条件。`.claude/CLAUDE.md` と同じ優先度 |
| 発見方法 | ディレクトリ配下を**再帰的に**走査。サブディレクトリも対象 |
| 現存数 | 7 |

**不変条件**:

- **I1.1**: 各ファイルは 200 行を超えない（公式のサイズ指針。SC-002）
- **I1.2**: 全ファイルの合計は 16,000 バイト以下（SC-001）
- **I1.3**: 記載される指示は、モデルのネイティブ挙動でも、ハーネスが自動注入する情報でもない（FR-014）
- **I1.4**: 実体とずれ得る列挙（スキル名、MCP サーバ名）を含まない（FR-012）
- **I1.5**: `@import` によって重ねて読み込まれない（FR-011）

**本機能での状態遷移**: 7 ファイルすべてが「無条件ロード・非最小」から「無条件ロード・最小」へ遷移する。`thinking-lenses.md` のみ内容不変。**`paths:` 付きへの遷移は本機能では行わない**（research.md D9）。

---

## E2. 強制設定 (Enforced Setting)

`.claude/settings.json` の `permissions` ブロック。Claude Code クライアントが評価し、モデルの判断に依存しない。

| 属性 | 値 |
|---|---|
| 所在 | `.claude/settings.json` |
| 評価順 | deny → ask → allow（最初の一致が確定。deny は常に優先） |
| 例外可否 | **deny は allow による例外を持てない** |
| 波及 | `install.sh` により `~/.claude/settings.json` へ同期 → 全プロジェクトに適用 |

**不変条件**:

- **I2.1**: `deny` の各パターンは、プロジェクト設定として読まれる場合とユーザ設定として読まれる場合で同じ対象に解決される。すなわち単一先頭スラッシュ `/path` 形式を含まない（research.md D1）
- **I2.2**: ファイル名の部分一致に基づくパターンを含まない（research.md D2）
- **I2.3**: `Read` deny と重複する `Edit` deny を含まない（research.md D3）
- **I2.4**: 正当なファイル（`.claude/keybindings.json` 等）に一致しない（SC-003）

**関係**: E1 の `permissions.md` は、E2 が強制する項目を**再掲しない**。E2 を正本として参照し、E2 では表現できない項目（部分一致方針、自己適用が必要な破壊的操作、AWS 確認）のみを保持する。

---

## E3. 退避先ドキュメント (Off-context Reference)

常時ロードされない参照資料。

| 属性 | 値 |
|---|---|
| 所在 | `docs/` 配下 |
| 禁止された所在 | `.claude/rules/` 配下（再帰的に自動ロードされるため） |
| 本機能での実体 | `docs/live-documentation-standards.md`（新規） |

**不変条件**:

- **I3.1**: `.claude/rules/` 配下に存在しない（FR-006）
- **I3.2**: 移設元のルールから参照されており、到達可能である（SC-005）
- **I3.3**: 移設によって内容が失われていない（SC-005）

**特記**: `clarifier.md` の References は例外的に `docs/` ではなく `.claude/skills/clarifier/SKILL.md` へ移設する。同 SKILL.md が移設元を名指しで参照しているためであり、`docs/` へ動かすと参照の連鎖が一段深くなる（research.md D7）。スキル本体は常時ロードされない（注入されるのは説明のみ）ため、退避先としての性質は E3 と同じである。

---

## E4. 決定記録 (ADR)

| 属性 | 値 |
|---|---|
| 所在 | `docs/adr/NNNN-<title>.md` |
| 採番 | 連番、再利用しない。既存最大は 0013 → 新規は **0014** |
| 可変性 | Accepted 後は**不変**。supersede のみ可能 |

**不変条件**:

- **I4.1**: ADR-0006 は本機能によって一切変更されない（SC-007）
- **I4.2**: ADR-0014 が存在し、0006 を参照している（SC-007）
- **I4.3**: ADR-0014 は、0006 が検討済みで却下した選択肢（「資格情報の deny のみ残す」）を採用する旨と、当時から何が変わったかを記載する（research.md D10）
- **I4.4**: ADR-0014 は [contracts/permissions-deny.md](./contracts/permissions-deny.md) 「受け入れる帰結」の 3 項目を負の帰結として記録する

**状態遷移**: `（存在しない）` → `Proposed` → `Accepted`。0006 は `Accepted` のまま遷移しない（部分的に効力を失うが、記録としては不変）。

---

## E5. 削除根拠 (Removal Justification)

削除された各指示に付与される分類。成果物としては [contracts/rule-inventory.md](./contracts/rule-inventory.md) の表がこれを保持する。

| 値 | 意味 | 検証方法 |
|---|---|---|
| `N` ネイティブ | モデルの既知知識、またはクライアント自身の挙動 | 公式ドキュメントまたはハーネスのシステムプロンプトを引用できる |
| `H` ハーネス注入済み | セッション開始時に自動で文脈に入る | 本セッションでの直接観測 |
| `S` 設定へ移管 | `.claude/settings.json` が強制する | 移管先の行を指せる |
| `R` 退避 | 別ファイルへ移動 | 移設先のパスと節を指せる |

**不変条件**:

- **I5.1**: 削除された指示のうち、いずれの分類も付与されないものが存在しない（FR-014）

---

## E6. 外部参照 (External Reference)

ルールおよびその節を指す、ルール外部からのリンク。

**本機能で影響を受ける既知の参照**:

| 参照元 | 参照先 | 本機能での扱い |
|---|---|---|
| `.claude/skills/clarifier/SKILL.md` L57 | `rules/clarifier.md § References` | **要更新** — References が SKILL.md 自身へ移設されるため |
| `README.md` L174 | `.claude/rules/mcp.md`（カタログとして） | **要 repoint** — カタログ表が削除されるため |
| `README.ja.md` L138 | 同上 | **要 repoint** |
| `README.md` L98 | ツリー注記「Doc enforcement (7 checks) + lifecycle standards」 | **要更新** — lifecycle standards が移設されるため |
| `README.md` L25 / `README.ja.md` L15 | `.claude/rules/` の内容説明 | **要更新** |
| `README.md` L207 / `README.ja.md` L151 / `install.sh` L119 | `rules/permissions.md`（AWS 確認として） | **変更不要** — AWS 項目は保持される |
| `README.ja.md` L86 | `.claude/rules/mcp.md`（変更時チェックリスト） | **変更不要** |

**不変条件**:

- **I6.1**: 移設・削除された節を指す参照が 0 件である（SC-006）
- **I6.2**: 更新後の参照は Spec Kit 中間成果物（`specs/035-*`）を指さない（`live-documentation.md` §6）
