# Codex CLI Config — Deployment Map

Purpose: map every `.claude/` configuration element to its Codex CLI counterpart, so "does the same thing exist for Codex?" has one place to check. See `specs/014-codex-config-port/contracts/deployment-map.md` for the contract this table satisfies (required columns, required rows, validation rules), `specs/014-codex-config-port/spec.md` for the feature this map closes out (FR-001/FR-002/FR-011, SC-001/SC-006), and `specs/012-cross-agent-guardrail-migration/decision-record.md` + `specs/013-cross-agent-guardrail-implementation/` for the prior decisions this map records rather than re-litigates.

Classification legend: **移植済み(013)** = shipped before this feature; **本機能で移植(014)** = shipped by this feature; **対象外** = intentionally not ported (reason required).

Sync method legend: **単一ソース** = one file/link, no duplication; **自動同期** = `install.sh` regenerates the Codex artifact from the Claude source on every run; **検証付き二重管理** = two independently-maintained files whose consistency `tests/run-codex-sync.sh` verifies; **—** = not applicable (対象外 rows only).

| 構成要素 (Claude 側) | Codex 側実体 | 分類 | 同期方式 | 挙動差分・制約 | 根拠 |
|---|---|---|---|---|---|
| `.claude/CLAUDE.md` | `.codex/AGENTS.md` → `~/.codex/AGENTS.md` | 本機能で移植(014) | 検証付き二重管理 | Claude の import 構造は使わず、Codex の 32 KiB 予算内に共通指針を要約。SYNC-03/06 でサイズと展開コピーを検証 | research R1; FR-003; SYNC-03/06 |
| `.claude/rules/clarifier.md` | `.codex/AGENTS.md`「Clarification」 | 本機能で移植(014) | 検証付き二重管理 | 詳細な elicitation 手法はスキル側、常時指針は判断ゲートのみ | research R1; FR-003; SYNC-03 |
| `.claude/rules/git-workflow.md` | `.codex/AGENTS.md`「Git workflow」+ `.codex/rules/guardrails.rules` | 本機能で移植(014) | 検証付き二重管理 | コミット規約はプロース、コマンド承認は Rules。Rules は完全一致 prefix のみ | research R5; FR-005; SYNC-10/11 |
| `.claude/rules/live-documentation.md` | `.codex/AGENTS.md`「Live documentation」 | 本機能で移植(014) | 検証付き二重管理 | 詳細な標準一覧は省き、同一変更での文書同期と ADR ゲートを保持 | FR-003/012; SYNC-03 |
| `.claude/rules/mcp.md` | `.codex/AGENTS.md` の MCP 表 + `~/.codex/config.toml` | 本機能で移植(014) | 検証付き二重管理 | 接続形式は非互換。サーバ集合と秘密情報非平文を検証 | 012 Q4; research R6; SYNC-04/12 |
| `.claude/rules/permissions.md` | `.codex/rules/guardrails.rules` + `.codex/hooks/*` | 本機能で移植(014) | 検証付き二重管理 | Rules は shell prefix 限定。正規表現・ファイル境界の判定は共有フック、ネイティブ非 shell 読取には残差あり | 012 Q6; research R5; FR-005; SYNC-10/11 |
| `.claude/rules/skill-routing.md` | `.codex/AGENTS.md`「Skill routing」+ `.agents/skills/*` | 本機能で移植(014) | 検証付き二重管理 | 用途ごとに `@.agents/skills/<name>/SKILL.md` を直接参照。実体はリンクで単一ソース | 012 Q3; research R2; FR-007; SYNC-01/02/03 |
| `.claude/hooks/README.md` | `.codex/README.md` + 各 `.codex/hooks/*-adapter.sh` のヘッダ | 本機能で移植(014) | 検証付き二重管理 | ツール固有のイベント/応答差分は各近接文書で管理 | FR-012; research R4; SYNC-05 |
| `.claude/hooks/pre-bash.sh` | `.codex/hooks/destructive-command-adapter.sh` | 移植済み(013) | 単一ソース | 両ラッパが `scripts/guardrails/destructive-command.sh` を使用。Codex の未確認 ask は安全側に deny | 012 Q6; research R3; FR-004; SYNC-05 |
| `.claude/hooks/pre-edit.sh` | `.codex/hooks/pre-edit-adapter.sh` | 移植済み(013) | 単一ソース | 共有判定は `.git/` と main/master を block。Claude 固有の警告文は AGENTS の編集規約へ要約 | 012 Q1/Q9/Q10; FR-004; SYNC-05 |
| `.claude/hooks/post-edit-format.sh` | `.codex/hooks/post-edit-adapter.sh` | 移植済み(013) | 単一ソース | 両ラッパが `scripts/guardrails/post-edit-format.sh` を使用 | 012 Q7; FR-004; SYNC-05 |
| `.claude/hooks/user-prompt-submit.sh` | `.codex/hooks/prompt-secret-adapter.sh` | 本機能で移植(014) | 単一ソース | 両ラッパが `scripts/guardrails/prompt-secret-scan.sh` を使用。Codex は matcher なし、`continue=false` で拒否 | research R4; FR-011; SYNC-05 |
| `.claude/hooks/speckit-expand-update.sh` | — | 対象外 | — | Codex に Claude の `UserPromptExpansion` 相当を配線しない。`AGENTS.md` から `specify init` を案内し、Spec Kit 自身の integration を利用 | 012 Q12; FR-011 |
| `.claude/hooks/statusline.sh` | — | 対象外 | — | Claude TUI 固有の statusLine で、Codex に同一レンダリング契約はない | research R10; FR-011 |
| `.claude/skills/*`(手書き 6 件 + `speckit-*` 15 件、プロジェクトスコープ) | `.agents/skills/*` | 移植済み(013) | 単一ソース | 相対シンボリックリンク。シンボリックリンク非対応環境は対象外 | research R2; FR-007; SYNC-01 |
| `.claude/skills/*`(ユーザースコープ展開、手書き 6 件) | `~/.agents/skills/*` → `~/.claude/skills/*` | 本機能で移植(014) | 単一ソース | `install.sh` が展開先を指すリンクを再生成。削除済み 3 スキルは 33c82eb に追従して除外 | research R0/R2; FR-010; SYNC-02 |
| `.claude/commands/verify-config.md` | `.codex/prompts/verify-config.md` → `~/.codex/prompts/verify-config.md` | 本機能で移植(014) | 検証付き二重管理 | `/prompts:verify-config` として明示起動。Codex custom prompts は deprecated のため将来は skill へ移行 | research R7; FR-008; SYNC-09 |
| `settings.json#permissions.allow` | `.codex/rules/guardrails.rules`(`decision="allow"`) | 本機能で移植(014) | 検証付き二重管理 | `tests/run-*.sh` は Rules の glob 非対応により現在の各スイートを列挙 | research R5; FR-005; SYNC-10/11 |
| `settings.json#permissions.ask` | `.codex/rules/guardrails.rules`(`decision="prompt"`) | 本機能で移植(014) | 検証付き二重管理 | git 書込系 prefix は prompt。共有 destructive 判定の ask は実セッション確認まで deny に丸め | research R3/R5; FR-005; SYNC-10 |
| `settings.json#permissions.deny` | `.codex/hooks/*-adapter.sh` + `scripts/guardrails/*.sh` | 本機能で移植(014) | 単一ソース | shell/編集/prompt 境界は共有判定。Codex の非 shell ファイル読取を Rules だけでは拒否できない | research R5; FR-005 |
| `settings.json#hooks.PreToolUse` / `#hooks.PostToolUse` | `~/.codex/config.toml` の managed hooks 区間 | 移植済み(013) | 自動同期 | `install.sh` が 3 アダプタを inline TOML として生成。非 managed hook は Codex で trust が必要 | research R0/R3; FR-004; SYNC-05/06 |
| `settings.json#hooks.UserPromptSubmit` | 同 managed hooks 区間 + `.codex/hooks/prompt-secret-adapter.sh` | 本機能で移植(014) | 自動同期 | matcher は公式仕様上無視されるため生成しない | research R4; FR-011; SYNC-05/06 |
| `settings.json#hooks.UserPromptExpansion` | — | 対象外 | — | Codex 側は Spec Kit スキルと手動 `specify init` を使用し、Claude 固有 expansion hook は配線しない | 012 Q12; FR-011 |
| `settings.json#statusLine` | — | 対象外 | — | Claude TUI 固有表示 | FR-011; research R10 |
| `settings.json#model` / `#effortLevel` / `#fallbackModel` | — | 対象外 | — | ベンダー固有モデル名・推論設定で意味が一致しないため同期しない | FR-011; research R10 |
| `settings.json#alwaysThinkingEnabled` | — | 対象外 | — | Claude 固有推論トグル | FR-011; research R10 |
| `settings.json#autoMemoryEnabled` | `.codex/AGENTS.md` の機構非依存な「persist decisions」指針 | 対象外 | — | Claude Memory 設定自体は同期せず、永続化の意図だけをプロース化 | 012 Q13; FR-011 |
| `settings.json#defaultMode` | — | 対象外 | — | Codex の approval/sandbox と意味が一致しないため暗黙変換しない | research R5; FR-011 |
| `settings.json#enableAllProjectMcpServers` | — | 対象外 | — | Claude 固有の一括有効化。Codex は各 `[mcp_servers.*]` を個別管理 | research R6; FR-011 |
| `settings.json#tui` | — | 対象外 | — | Claude TUI 固有 | FR-011; research R10 |
| `settings.json#$schema` | — | 対象外 | — | Claude settings JSON の編集支援メタデータ | FR-011; research R10 |
| `.claude/settings.local.json` | — | 対象外 | — | 端末ローカル・非共有の許可状態であり、ユーザー所有の Codex 設定へ上書きしない | FR-011; research R5 |
| `.mcp.json`(6 サーバ) | `~/.codex/config.toml` の managed MCP servers 区間 | 本機能で移植(014) | 自動同期 | `install.sh` が JSON を TOML へ変換。同名の非管理定義は保持して生成を省略し、TOML 重複を防ぐ。Google キー未設定時は managed entry を disabled、値は `env_http_headers` で環境参照 | research R6/R9; FR-006; SYNC-04/12 |

**Notes**:

- 被覆(全 `.claude/` 要素が最低 1 行に現れること)は `tests/run-codex-sync.sh` の SYNC-08 が機械検証する。
- `~` 配下の実体は `install.sh` 実行後に有効になる。Codex の非 managed hooks は初回または変更後に `/hooks` で trust が必要。
- Windows のシンボリックリンク非対応構成は対象外。macOS / Linux をサポート対象とする。
