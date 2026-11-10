# harness の受け持ちの対応表

この文書は `docs/harness/capability-map.json` と `tests/harness-eval/scenarios.json` から `tests/harness-eval/harness_eval.py render` が生成する。手で編集しない。正本は JSON で、`harness_eval.py check` が実在の部品・引用・シナリオとの整合を検査する。

## 段階と担い手

| 段階 | 枝 | 内容 | 担い手 | シナリオ |
|---|---|---|---|---|
| `D-intent` | 定義 | 目的・範囲・完了条件を定め、結果を変える選択が残るときは着手前に尋ねる | `apex`, `rule:clarifier`, `skill:clarify-intent` | `d-intent-ambiguous` |
| `D-problem` | 定義 | 漠然とした不満を、現状と理想の差としての問題文にする | `skill:define-problem` | `d-problem-vague` |
| `D-product` | 定義 | 開発の前に、プロダクトの方向（対象、価値、指標、範囲）を定める | `skill:define-product-strategy` | `d-product-direction` |
| `D-decompose` | 定義 | 合意した問題を、検査できる要件のグラフに分解する | `skill:specify-requirements`, `agent:read-only-reviewer.md` | `d-decompose-agreed`, `e-proportion-typo` |
| `D-evidence` | 定義 | 事実の主張を、適用できる最新の一次の証拠に基づかせる | `apex`, `rule:thinking-lenses`, `skill:research-aws` | `d-evidence-aws` |
| `D-reasoning` | 定義 | 依存、分岐、反復、推論の完全さを確かめてから決める（観測しない: 内部の判断の形成を律する規則で、出力の形を求めないため、決定的な判定で確かめられない） | `apex`, `rule:thinking-lenses` | — |
| `D-root-cause` | 定義 | 根本原因を分析する | **担い手なし** | `obs-root-cause` |
| `D-solution` | 定義 | 解決策を評価して選ぶ | **担い手なし** | `obs-solution-choice` |
| `D-plan` | 定義 | 実行計画を作る | **担い手なし** | `obs-execution-plan` |
| `D-architecture` | 定義 | アーキテクチャ、技術の選定、自作か調達かを決める | **担い手なし** | `obs-architecture` |
| `D-document` | 定義 | 不完全な材料から、対話しながら文書を組み立てる | **担い手なし** | `obs-document-cocreation` |
| `E-authority` | 実行 | 権限の範囲で動き、破壊的・外部・資格情報に関わる操作の前に承認を得る | `apex`, `rule:permissions` | `e-authority-cleanup` |
| `E-match` | 実行 | 独立に当てはまる能力をすべて、依存の順に適用する | `apex` | `e-match-logging`, `e-dads-frontend` |
| `E-proportion` | 実行 | 手順と検証の重さを、複雑さ・可逆性・影響に比例させる | `apex` | `e-proportion-typo` |
| `E-delegate` | 実行 | 出力が長い確認や広い検索、独立して並べられる作業、作者から独立した読み手が要る作業は、その型のサブエージェントに任せ、それ以外は自分で行う（観測しない: 評価は Agent の道具を許さないので、サブエージェントを起動する振る舞いは観測できない。docs/harness-eval.md §4 の4 に記す） | `apex`, `agent:check-runner.md`, `agent:file-searcher.md`, `agent:read-only-reviewer.md`, `agent:task-worker.md` | — |
| `E-implement` | 実行 | コード・設定・テストを、失敗する検査を先に観測してから変える | `skill:implement-change` | `e-implement-bugfix`, `e-match-logging`, `e-dads-frontend`, `h-docs-flag-rename` |
| `E-git` | 実行 | ブランチ、コミット、push、プルリクエストを、求められた操作だけ行う | `skill:manage-git` | `e-git-commit-only` |
| `E-dads-frontend` | 実行 | DADS に沿った React と Tailwind CSS のフロントエンド | `skill:apply-dads-frontend` | `e-dads-frontend` |
| `E-dads-slides` | 実行 | DADS に沿った 16:9 の HTML スライド | `skill:build-dads-slides` | `e-dads-slides` |
| `E-scrum` | 実行 | Scrum のイベント・作成物・説明責任の診断と改善 | `skill:apply-scrum-guide` | `e-scrum-retro`, `e-scrum-not-pm` |
| `E-logging` | 実行 | ログ出力の実装と確認を、セキュリティの要件に照らして行う | `skill:apply-secure-logging` | `e-match-logging` |
| `E-diagrams` | 実行 | システム構成図を、1枚に1つの問い・1種類の読者・1つの抽象度で作る | `skill:draw-system-diagrams` | `e-system-diagrams`, `e-diagrams-vendor-icons` |
| `H-verify` | 引き渡し | 完了条件を確かめてから報告し、変更を証拠で受け入れられるようにする | `apex`, `skill:deliver-change`, `skill:verify-change`, `skill:implement-change`, `agent:read-only-reviewer.md` | `h-verify-evidence`, `e-proportion-typo` |
| `H-structure` | 引き渡し | 会話の答えで、答えを先に置き、支えを下に組む | `apex`, `rule:pyramid-principle` | `h-structure-recommend` |
| `H-document` | 引き渡し | 文書を1つの主張の木に組み、同梱の検査器で確かめる | `skill:structure-document` | `h-document-proposal` |
| `H-docs` | 引き渡し | 公開の契約と文書を、変更と同期させる | `apex`, `skill:sync-docs`, `skill:implement-change` | `h-docs-flag-rename` |
| `H-code-review` | 引き渡し | 変更をコードレビューする | **担い手なし** | `obs-code-review` |
| `H-report` | 引き渡し | 行ったこと、限界、残るリスク、未完了の作業を報告する（観測しない: 何を書けば満たすかが依頼ごとに違い、決定的な判定で確かめられる形の約束ではない） | `apex` | — |

## 境界グループ

同じグループのスキルは互いの description で除外し合う。グループのスキルを期待するシナリオは、他のメンバー（期待するスキルが宣言した子を除く）が使われないことも判定する。

- `G-define`: `skill:clarify-intent`, `skill:define-problem`, `skill:define-product-strategy`, `skill:specify-requirements`

## settings.json の扱い

| 項目 | 評価に含めるか | 理由 |
|---|---|---|
| `$schema` | 含めない | JSON の検証のための宣言で、振る舞いに効かない |
| `tui` | 含めない | 端末の表示形式で、モデルの振る舞いに効かない |
| `model` | 含める | run は既定でこの値を --model に渡す |
| `effortLevel` | 含めない | 主の会話の推論の努力の水準（xhigh）。claude plugin eval には努力の水準を渡す手段がなく、評価の実行は利用者の settings を読まないので、評価は eval の既定の水準で動く。実際の環境との違いとして docs/harness-eval.md §4 に記す |
| `modelSettings` | 含めない | モデルの ID ごとの設定で、今は claude-opus-5-5 の effortLevel を xhigh にする。claude plugin eval には努力の水準を渡す手段がなく、評価の実行は利用者の settings を読まないので、評価は eval の既定の水準で動く。実際の環境との違いとして docs/harness-eval.md §4 に記す |
| `permissions` | 含めない | defaultMode（auto）と資格情報の読み取り拒否。eval の実行は許可を求めず、許していない道具を外す。シェルのコマンドは OS サンドボックスがホームを読めなくするが、ファイルを読む道具（Read、Glob、Grep）はサンドボックスの外で動き、この読み取り拒否も効かない。run は、結果のうち利用者のホームのパスを含むファイルを記録する。許可の仕組みが実際の環境と違うことは強制の配置（軸4）で扱う |
| `hooks` | 含めない | PreToolUse の1つは speckit-specify が呼ばれたときだけ specify-cli の更新を確かめるもので、speckit-* は harness に含まれないため動く機会がない。SessionStart の3つ（Bash から Bedrock の AWS の変数を外す、gpg-agent を外で起動する、Bash が zsh のとき・macOS のとき・aws CLI があるときに注意を文脈に足す）は、組み立てるプラグインのフックを常時ロードの注入に限るため含めない。そのため注意が振る舞いに与える効果は測らない |
| `sandbox` | 含めない | Bash の OS サンドボックスと、日常作業のために開ける場所。eval の Bash は eval 自身の OS サンドボックスで動き（書き込みは作業領域、ホームは読めず、ネットワークは許さない）、この設定は再現しない。開ける場所と守る場所は tests/run-sandbox-settings.sh で確かめる |
| `enabledPlugins` | 含めない | MCP サーバーを同梱する github・deploy-on-aws・microsoft-docs の各プラグインを無効にする。eval は評価するプラグインのほかのプラグインを読み込まない |
| `allowedMcpServers` | 含めない | 読み込んでよい MCP サーバーを、AWS の文書を検索する2つ（aws-knowledge の URL と aws-documentation のコマンド）に限る。eval は MCP サーバーを読み込まない。許可する内容は tests/run-sandbox-settings.sh で確かめる |
| `deniedMcpServers` | 含めない | 使わない MCP サーバーと、許可リストの対象にならない組み込みの Chrome 連携を拒む。eval は MCP サーバーを読み込まない |
| `disableClaudeAiConnectors` | 含めない | claude.ai のコネクタを止める。eval は一時的なホームと設定で動き、MCP サーバーを読み込まない |
| `syncClaudeAiPlugins` | 含めない | claude.ai からのプラグインの同期を止める。eval は利用者の設定とほかのプラグインを読み込まない |

## シナリオの数

期待 20 件、観測 6 件、到達確認 1 件。
