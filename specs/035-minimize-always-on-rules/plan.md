# 実装計画: 常時ロードルールの最小化と強制力の復元

**ブランチ**: `035-minimize-always-on-rules` | **日付**: 2026-08-30 | **仕様**: [spec.md](./spec.md)

**入力**: `specs/035-minimize-always-on-rules/spec.md` の機能仕様

## サマリ

`.claude/rules/` の 7 ファイル（合計 36,165 バイト）を、全セッションに課金される固定費とみなして最小化する。判断基準は一つ — **その指示が非自明か**。モデルのネイティブ知識でも、ハーネスが自動注入する情報でもなく、かつオンデマンドのスキルへ委ねられないものだけが常時ロードに残る。

同時に、散文へ退化していた資格情報保護を `.claude/settings.json` の `permissions.deny` として復元する。公式ドキュメントは設定とコンテキストを明確に区別しており（「設定による規則はクライアントが強制する。CLAUDE.md は強制層ではない」）、散文で書かれた「never read」は強制ではなく助言でしかない。この復元は ADR-0006 の決定の一部を覆すため、0006 を不変のまま supersede する ADR-0014 を伴う。

技術的アプローチは 3 段階: (1) 強制可能な方針を設定へ移す、(2) 参照資料を自動ロード対象外の `docs/` へ移す、(3) 残りを非自明な最小核へ圧縮する。

## 技術コンテキスト

**対象物**: Markdown 指示ファイルと JSON 設定ファイル（実行コードなし）

**主要依存**: Claude Code のコンテキストロード機構（`.claude/rules/` 再帰自動ロード、`@import` 展開、スキル説明の自動注入）と権限評価機構（`permissions` の deny → ask → allow 順評価）

**保存**: ファイルのみ。Git 管理下。`install.sh` により `~/.claude/` へ複製同期される

**テスト**: **本項は計画時点で誤っていた（実装中に訂正）。** 当初「自動テストなし」と記載したが、`tests/` に 5 つのローカルスイートが存在する。うち 2 つは本変更で失敗した — `run-removed-guardrails.sh` は `settings.json` に `permissions` ブロックが無いことを表明しており、`run-digital-agency-frontend-skill.sh` の `SYNC-SKILL-05` は `CLAUDE.md` がスキル名を列挙していることを表明していた。両者は本機能が意図的に変える不変条件そのものであり、T025 / T026 で更新した。hooks とスクリプトは ADR-0005 / 0007 のとおり復活させていない

**対象プラットフォーム**: Claude Code（macOS/Linux/Windows）。`install.sh` は POSIX シェル前提

**プロジェクト種別**: エージェント設定リポジトリ。外部インタフェースはルール文書そのもの（対エージェント契約）と `settings.json`（対 Claude Code クライアント契約）

**性能目標**: `.claude/rules/*.md` 合計 16,000 バイト以下（現状 36,165 バイトから 55% 以上削減）

**制約**:
- `.claude/rules/` 配下は全 `.md` が再帰的に自動ロードされる → 退避先を同ディレクトリに置けない
- `.claude/settings.json` はプロジェクト設定であると同時に、`install.sh` 経由でユーザ設定にもなる → 設定ソース基準でアンカーされる `/path` 形式のパターンは二重の意味を持つため使用不可（research.md D1）
- deny 規則は allow による例外を持てない → 過剰阻害を後から緩和できない（research.md D2）
- ADR は Accepted 後は不変。supersede のみ

**規模**: ルール 7 ファイル + `CLAUDE.md` + `settings.json` + 新規ドキュメント 2 件 + 参照更新 3 ファイル

## Constitution Check

*ゲート: Phase 0 リサーチ前に通過必須。Phase 1 設計後に再確認。*

`.specify/memory/constitution.md` は Spec Kit のテンプレート未記入状態であり、全フィールドが `[PLACEHOLDER]`、批准日もバージョンも存在しない。**評価すべきプロジェクト固有のゲートは存在しない**（`specs/022-minimize-scrum-master-skill/plan.md` と同じ状況・同じ扱い）。

代わりに、リポジトリの全体規則を直接遵守対象として観測する:

| 規則 | 本機能への適用 | 判定 |
|---|---|---|
| Core Principle #1 Accuracy | 削除の根拠はすべて公式ドキュメントまたは本セッションでの直接観測に基づく。推測による削除は行わない | 通過 |
| Core Principle #3 Traceability | 移設は削除ではなく、退避先から到達可能。ADR-0014 が方針転換を記録 | 通過 |
| `live-documentation.md` §1 Drift | ルールの記述が変わる以上、それを説明する `README.md` / `README.ja.md` は同一変更内で更新する（FR-013） | 通過 |
| `live-documentation.md` §4 Proximity | 退避先を `.claude/rules/` 隣接に置けないのは技術的制約。`docs/` が次善かつリポジトリ既定の散文置き場 | 通過（制約による逸脱を明記） |
| `live-documentation.md` §5 No Redundancy | `clarifier` SKILL.md は `rules/clarifier.md § References` を明示参照している。References は削除ではなく SKILL.md へ移設し、参照文言を更新する | 通過 |
| `live-documentation.md` §6 Intermediate-Artifact Isolation | 更新後の `README.md` / ルール / ADR は `specs/035-*` を参照しない。根拠は ADR-0014 または平文で示す | 通過 |
| `live-documentation.md` §7 Granularity Layering | §7 の規範は残す。移設するのは論拠と解説のみ | 通過 |
| `permissions.md` 最小権限 | deny は必要最小限のパターンに限定し、過剰阻害を避ける（FR-002） | 通過 |
| `git-workflow.md` | ブランチは `/speckit-git-feature` 採番に従う（`035-minimize-always-on-rules`）。コミットは明示依頼時のみ | 通過 |

**Phase 1 設計後の再確認**: 違反なし。Complexity Tracking への記入項目なし。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/035-minimize-always-on-rules/
├── spec.md                      # 機能仕様（/speckit-specify 出力）
├── plan.md                      # 本ファイル（/speckit-plan 出力）
├── research.md                  # Phase 0 出力: 決定・根拠・却下案
├── data-model.md                # Phase 1 出力: エンティティと不変条件
├── quickstart.md                # Phase 1 出力: SC-001〜007 の検証手順
├── contracts/
│   ├── rule-inventory.md        # 全ルールの保持/削除/移設の逐条対応表
│   └── permissions-deny.md      # deny 規則の確定形とアンカー根拠
└── tasks.md                     # Phase 2 出力（/speckit-tasks — 本コマンドでは作成しない）
```

### 変更対象（リポジトリルート）

```text
.claude/
├── CLAUDE.md                    # 変更: @import 5行削除、スキル列挙削除
├── settings.json                # 変更: permissions.deny 新設
├── rules/
│   ├── clarifier.md             # 縮小: ask/proceed ゲートのみ
│   ├── git-workflow.md          # 縮小: リポジトリ固有規約のみ
│   ├── live-documentation.md    # 縮小: 強制中核のみ
│   ├── mcp.md                   # 縮小: ルーティング + AWS スキルレジストリ手順
│   ├── permissions.md           # 縮小: 設定で表現できない項目のみ
│   ├── skill-routing.md         # 縮小: 複合連鎖 + 否定的境界のみ
│   └── thinking-lenses.md       # 変更なし
└── skills/clarifier/SKILL.md    # 変更: References を受け入れ、参照文言を更新

docs/
├── live-documentation-standards.md   # 新規: §0 標準規格表・§7 論拠・References
└── adr/
    └── 0014-restore-credential-deny-rules.md  # 新規: ADR-0006 の部分 supersede

README.md                        # 変更: rules 説明・ツリー注記・mcp カタログ参照の repoint
README.ja.md                     # 変更: 同上
```

**構造の決定**: 新規ディレクトリは作らない。退避先が `docs/` 直下なのは Proximity（§4）の理想ではなく**技術的制約による次善**である — `.claude/rules/` 配下は全 `.md` が自動ロードされるため、そこに置けば削減効果が丸ごと消える。`docs/` は `docs/adr/`・`docs/claude-code-config-tips.md`・`docs/minto-*.ja.md` により散文ドキュメントの置き場としてすでに確立している。

## Complexity Tracking

> Constitution Check に正当化を要する違反がある場合のみ記入

違反なし。記入項目なし。
