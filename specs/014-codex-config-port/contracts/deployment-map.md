# Contract: 構成要素対応表 (`.codex/README.md`)

**Feature**: [../spec.md](../spec.md) (FR-001/FR-002/FR-011, SC-001/SC-006) | **Data model**: [../data-model.md](../data-model.md)

対応表は `.codex/README.md` に置く(Proximity: Codex 移植物の直近)。この契約は表の**形**と**被覆**を定める。内容の正しさは実装時に確定する。

## 必須列

`| 構成要素 (Claude 側) | Codex 側実体 | 分類 | 同期方式 | 挙動差分・制約 | 根拠 |`

- 分類は `移植済み(013)` / `本機能で移植(014)` / `対象外` の 3 値のみ。
- 同期方式は `単一ソース` / `自動同期` / `検証付き二重管理` / `—`(対象外のみ)。
- 根拠列は `012 Q<n>` / `research R<n>` / spec FR 番号のいずれかへの参照を含む。

## 必須行(被覆リスト)

以下の各項目が最低 1 行に現れなければならない(SC-001 の検証対象):

1. `.claude/CLAUDE.md`(+ `@import` される `rules/` 6 ファイル各行: clarifier / git-workflow / live-documentation / mcp / permissions / skill-routing)
2. `.claude/hooks/` 6 スクリプト各行: pre-bash / pre-edit / post-edit-format / user-prompt-submit / speckit-expand-update / statusline
3. `.claude/skills/`(プロジェクト 21 件は種別単位でよい: 手書き 6 / speckit 15。ユーザースコープ手書き 6 件は `~/.agents/skills` 行として別掲)
4. `.claude/commands/verify-config.md`
5. `settings.json` トップレベルキー各行(まとめ可だが漏れ不可): permissions(allow/ask/deny)、hooks(4 イベント)、statusLine、model/effortLevel/fallbackModel、alwaysThinkingEnabled、autoMemoryEnabled、defaultMode、enableAllProjectMcpServers、tui、$schema
6. `.mcp.json`(6 サーバ)
7. `settings.local.json`(存在すれば — ローカル専用として対象外分類可)

## 不変条件

- 対象外行には理由が必須(空欄・「TBD」不可)。
- `検証付き二重管理` を名乗る行は、`tests/run-codex-sync.sh` に対応するチェック ID(sync-check 契約参照)を根拠列に併記する。
- 表に現れるパスはすべて実在するか、`~` 配下の場合は install.sh が生成するものである(架空パス禁止)。
- 012 の 14 項目の verdict と矛盾する分類を書かない。昇格(user-prompt-submit)は research R4 を根拠として明記する。

## 検証方法

`tests/run-codex-sync.sh` の被覆チェックが、`.claude/` 実ファイル列挙と本表の行を突き合わせ、`unclassified` 要素があれば失敗する(機械検証)。列の形・理由の記載は人手レビュー(または簡易 grep)で確認する。
