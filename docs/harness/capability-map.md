# harness の受け持ちの対応表

この文書は `docs/harness/capability-map.json` と `tests/harness-eval/scenarios.json` から `tests/harness-eval/harness_eval.py render` が生成する。手で編集しない。正本は JSON で、`harness_eval.py check` が実在の部品・引用・シナリオとの整合を検査する。

## 段階と担い手

| 段階 | 枝 | 内容 | 担い手 | シナリオ |
|---|---|---|---|---|
| `D-intent` | 定義 | 目的・範囲・完了条件を定め、結果を変える選択が残るときは着手前に尋ねる | `apex`, `rule:clarifier`, `skill:clarifier` | `d-intent-ambiguous` |
| `D-problem` | 定義 | 漠然とした不満を、現状と理想の差としての問題文にする | `skill:problem-definition` | `d-problem-vague` |
| `D-product` | 定義 | 開発の前に、プロダクトの方向（対象、価値、指標、範囲）を定める | `skill:product-strategy` | `d-product-direction` |
| `D-decompose` | 定義 | 合意した問題を、検査できる要件のグラフに分解する | `skill:requirements-decomposition` | `d-decompose-agreed`, `e-proportion-typo` |
| `D-evidence` | 定義 | 事実の主張を、適用できる最新の一次の証拠に基づかせる | `apex`, `rule:thinking-lenses`, `skill:aws-research` | `d-evidence-aws` |
| `D-reasoning` | 定義 | 依存、分岐、反復、推論の完全さを確かめてから決める（観測しない: 内部の判断の形成を律する規則で、出力の形を求めないため、決定的な判定で確かめられない） | `apex`, `rule:thinking-lenses` | — |
| `D-root-cause` | 定義 | 根本原因を分析する | **担い手なし** | `obs-root-cause` |
| `D-solution` | 定義 | 解決策を評価して選ぶ | **担い手なし** | `obs-solution-choice` |
| `D-plan` | 定義 | 実行計画を作る | **担い手なし** | `obs-execution-plan` |
| `D-architecture` | 定義 | アーキテクチャ、技術の選定、自作か調達かを決める | **担い手なし** | `obs-architecture` |
| `D-document` | 定義 | 不完全な材料から、対話しながら文書を組み立てる | **担い手なし** | `obs-document-cocreation` |
| `E-authority` | 実行 | 権限の範囲で動き、破壊的・外部・資格情報に関わる操作の前に承認を得る | `apex`, `rule:permissions` | `e-authority-cleanup` |
| `E-match` | 実行 | 独立に当てはまる能力をすべて、依存の順に適用する | `apex` | `e-match-logging`, `e-dads-frontend` |
| `E-proportion` | 実行 | 手順と検証の重さを、複雑さ・可逆性・影響に比例させる | `apex` | `e-proportion-typo` |
| `E-implement` | 実行 | コード・設定・テストを、失敗する検査を先に観測してから変える | `skill:coder` | `e-implement-bugfix`, `e-match-logging`, `e-dads-frontend`, `h-docs-flag-rename` |
| `E-git` | 実行 | ブランチ、コミット、push、プルリクエストを、求められた操作だけ行う | `skill:git-workflow` | `e-git-commit-only` |
| `E-dads-frontend` | 実行 | DADS に沿った React と Tailwind CSS のフロントエンド | `skill:digital-agency-frontend` | `e-dads-frontend` |
| `E-dads-slides` | 実行 | DADS に沿った 16:9 の HTML スライド | `skill:digital-agency-slides` | `e-dads-slides` |
| `E-scrum` | 実行 | Scrum のイベント・作成物・説明責任の診断と改善 | `skill:scrum-master` | `e-scrum-retro`, `e-scrum-not-pm` |
| `E-logging` | 実行 | ログ出力の実装と確認を、セキュリティの要件に照らして行う | `skill:secure-logging` | `e-match-logging` |
| `E-diagrams` | 実行 | システム構成図を、1枚に1つの問い・1種類の読者・1つの抽象度で作る | `skill:system-diagrams` | `e-system-diagrams`, `e-diagrams-vendor-icons` |
| `E-notes` | 実行 | Apple のメモの読み書き（観測しない: 評価のエージェントが利用者の実際のメモやリマインダーを変えうる。eval のサンドボックスがファイルの書き込みを作業領域に限ることは公式文書にあるが、Apple Events と EventKit による変更を止めることは確かめられていないので、この段階は評価しない） | `skill:apple-notes` | — |
| `E-reminders` | 実行 | Apple のリマインダーの読み書き（観測しない: 評価のエージェントが利用者の実際のメモやリマインダーを変えうる。eval のサンドボックスがファイルの書き込みを作業領域に限ることは公式文書にあるが、Apple Events と EventKit による変更を止めることは確かめられていないので、この段階は評価しない） | `skill:apple-reminders` | — |
| `H-verify` | 引き渡し | 完了条件を確かめてから報告し、変更を証拠で受け入れられるようにする | `apex`, `skill:verified-delivery`, `skill:coder` | `h-verify-evidence`, `e-proportion-typo` |
| `H-structure` | 引き渡し | 答えを先に置き、支えを下に組む | `apex`, `rule:pyramid-principle`, `skill:pyramid-structure` | `h-structure-recommend` |
| `H-docs` | 引き渡し | 公開の契約と文書を、変更と同期させる | `apex`, `skill:maintaining-living-documentation`, `skill:coder` | `h-docs-flag-rename` |
| `H-code-review` | 引き渡し | 変更をコードレビューする | **担い手なし** | `obs-code-review` |
| `H-report` | 引き渡し | 行ったこと、限界、残るリスク、未完了の作業を報告する（観測しない: 何を書けば満たすかが依頼ごとに違い、決定的な判定で確かめられる形の約束ではない） | `apex` | — |

## 境界グループ

同じグループのスキルは互いの description で除外し合う。グループのスキルを期待するシナリオは、他のメンバー（期待するスキルが宣言した子を除く）が使われないことも判定する。

- `G-define`: `skill:clarifier`, `skill:problem-definition`, `skill:product-strategy`, `skill:requirements-decomposition`

## 評価に含めないスキル

| スキル | 理由 |
|---|---|
| `skill:apple-notes` | 評価のエージェントが Bash でこのスキルのスクリプトを動かすと、利用者の実際のメモやリマインダーを変えうる。eval のサンドボックスが Apple Events と EventKit を止めることは確かめていないので、組み立てるプラグインに含めない |
| `skill:apple-reminders` | 評価のエージェントが Bash でこのスキルのスクリプトを動かすと、利用者の実際のメモやリマインダーを変えうる。eval のサンドボックスが Apple Events と EventKit を止めることは確かめていないので、組み立てるプラグインに含めない |

## settings.json の扱い

| 項目 | 評価に含めるか | 理由 |
|---|---|---|
| `$schema` | 含めない | JSON の検証のための宣言で、振る舞いに効かない |
| `tui` | 含めない | 端末の表示形式で、モデルの振る舞いに効かない |
| `model` | 含める | run は既定でこの値を --model に渡す |
| `effortLevel` | 含めない | 主の会話の推論の努力の水準（xhigh）。claude plugin eval には努力の水準を渡す手段がなく、評価の実行は利用者の settings を読まないので、評価は eval の既定の水準で動く。実際の環境との違いとして docs/harness-eval.md §4 に記す |
| `permissions` | 含めない | defaultMode（auto）と資格情報の読み取り拒否。eval の実行は許可を求めず、許していない道具を外す。シェルのコマンドは OS サンドボックスがホームを読めなくするが、ファイルを読む道具（Read、Glob、Grep）はサンドボックスの外で動き、この読み取り拒否も効かない。run は、結果のうち利用者のホームのパスを含むファイルを記録する。許可の仕組みが実際の環境と違うことは強制の配置（軸4）で扱う |
| `hooks` | 含めない | PreToolUse の1つは speckit-specify が呼ばれたときだけ specify-cli の更新を確かめるもので、speckit-* は harness に含まれないため動く機会がない。SessionStart の3つ（Bash から Bedrock の AWS の変数を外す、gpg-agent を外で起動する、Bash が zsh のとき・macOS のとき・aws CLI があるときに注意を文脈に足す）は、組み立てるプラグインのフックを常時ロードの注入に限るため含めない。そのため注意が振る舞いに与える効果は測らない |
| `sandbox` | 含めない | Bash の OS サンドボックスと、日常作業のために開ける場所。eval の Bash は eval 自身の OS サンドボックスで動き（書き込みは作業領域、ホームは読めず、ネットワークは許さない）、この設定は再現しない。開ける場所と守る場所は tests/run-sandbox-settings.sh で確かめる |
| `enabledPlugins` | 含めない | github プラグインを無効にする。eval は評価するプラグインのほかのプラグインを読み込まない |
| `deniedMcpServers` | 含めない | 使わない MCP サーバーを拒む。eval は MCP サーバーを読み込まない |
| `disableClaudeAiConnectors` | 含めない | claude.ai のコネクタを止める。eval は一時的なホームと設定で動き、MCP サーバーを読み込まない |
| `syncClaudeAiPlugins` | 含めない | claude.ai からのプラグインの同期を止める。eval は利用者の設定とほかのプラグインを読み込まない |

## シナリオの数

期待 19 件、観測 6 件、到達確認 1 件。
