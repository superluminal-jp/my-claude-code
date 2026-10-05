# Problem Statement: Spec Kit の一連の工程を、権威ある根拠付きで一貫して完走できない

**Status**: Complete
**Generated**: 2026-10-06

## 1. 現状 (Current state)

出典の区別: 【観測】はこのリポジトリで確認した事実、【申告】はユーザーの申告、【未検証】は裏付けのない点。

- 【観測】Spec Kit の各工程は個別のスキルとして独立に存在する（`speckit-specify` / `-plan` / `-tasks` / `-analyze` / `-implement` / `-converge` / `-git-commit`）。工程を通しで束ねるスキルは `.claude/skills/` に無い。
- 【観測】`.specify/extensions.yml` には工程の前後で `speckit.git.commit` などを呼ぶ hook がある。ただし `optional: true` が大半で、工程の連結ではなくコミットの自動化にとどまる。
- 【申告】ユーザーは、specify → plan → tasks → analyze → analyze 推奨の適用 → implement → converge → converge 推奨の実装 → commit → code-review(`--fix`) → commit → push → PR 作成を、現状は工程ごとに手動で呼び出し・受け渡している。
- 【申告】plan 工程で参照する業界のベストプラクティス・国際標準・学術的知見・公式ドキュメント（AWS なら AWS knowledge / documentation MCP）の適用と引用は、プロンプト次第で、工程間で一貫しない。
- 【未検証】手動実行で工程の抜け・順序違い・根拠の欠落が実際にどの頻度で起きているかを示すデータは無い。定量的な現状値は存在しないため、定性的な記述にとどめる。

## 2. あるべき姿 (Ideal state)

ユーザーが確認した内容:

- 1 回の起動で、機能の記述から **PR が作成され、検証結果が報告された状態** までが完走する。PR 作成後に CI がエラーを報告した場合は、そのエラーを修正する（完了状態: PR 作成 + チェック結果の報告 + CI エラーの修正）。
- 実行は **ハンズオフで、定義済みの停止条件でのみ中断する**。停止条件の例は、失敗した検証、未解決の曖昧性、push の拒否。
- Claude Code と Codex のどちらからでも同じ流れを実行できる（ユーザー確認済み、2026-10-06）。
- 起動は、その 1 回の run における commit・push・PR 作成の明示的な認可として扱う（ユーザー確認済み）。
- converge で必要とされた推奨の実装は **1 回だけ** 行う（反復上限 = 1、ユーザー確認済み）。
- plan では、対象領域に関する業界のベストプラクティス、国際標準、科学的法則、学術的に広く受け入れられた知見、公式ドキュメントを参照・引用して適用する。plan 以外の工程でも適宜、権威ある出典を引用する。AWS 関連では AWS knowledge / documentation MCP を使う。

## 3. ギャップ (The problem)

Spec Kit の工程列を、手動の逐次呼び出しではなく **1 回の起動で、権威ある出典に裏付けられた成果物を伴って PR 作成まで** 完走させる手段が存在しない。現状は「工程ごとの手動呼び出しと、不均一な根拠付け」、あるべき姿は「停止条件付きのハンズオフ実行と、全工程での一貫した権威ある引用」であり、その差が本問題である。

## 4. 重要性 (Significance)

ユーザーが選んだ痛点は次の 2 つ。

1. **手動の工程連結の手間**: 約 14 の呼び出しを人が順序どおりに繋ぐ必要がある。
2. **権威ある根拠付けの不均一**: 標準や公式資料の参照・引用が工程ごと・実行ごとにばらつく。

「分析・収束・レビューの指摘が遅れて発覚する」「実行ごとの再現性」は、ユーザーが選ばなかったため重要性の根拠に含めない。

## Identified solution (not part of the problem statement)

Spec Kit の一連の工程を通しで実行する新しいスキルを作成する。このスキルが解消しようとしているギャップ: 上記「3. ギャップ」の、手動の逐次呼び出しと不均一な根拠付けに対する、1 回の起動での権威ある引用付き完走。

## Resolved decisions (2026-10-06, ユーザー確認済み)

- **独立性制約**: `specs/028-independent-skills` と ADR-0015 を supersede する方針を確認したが、解決策を「薄いスキル + Spec Kit ワークフローの overlay」とした結果、スキルは別スキルを名指しで呼ばず外部の CLI を起動するだけになり、supersede は不要になった（2026-10-06）。
- **外向き操作の認可**: 起動をもって commit・push・PR 作成を認可する。push・PR の直前確認は行わない。ただし `git-workflow` が定める破壊的操作（force push、履歴の書き換えなど）の個別認可は、この認可に含まれない。
- **反復上限**: converge→implement は 1 回。
- **CI**: エラーがあれば修正する。修正は 1 回まで（ユーザー確認済み）。なお失敗する場合は停止条件として報告する。完了状態に CI の結果が加わる。

## Open points

**Open point**: Codex 対応と既存の Codex 削除方針の整合
**Default**: Codex 対応は、Spec Kit の `codex` 統合（`.agents/skills/` 配置、`codex exec` 実行）を使う形で扱う。リポジトリ本体の管理対象（`.claude/` 配下）にはまだ Codex 向けの成果物を戻さない。
**Alternative**: `specs/029-remove-codex-plugin` と `specs/031-remove-codex-support` の方針を改め、Codex 向け成果物をリポジトリで管理する。
**Impact**: 前者は変更範囲が小さい代わりに、Codex 側の配置は利用者の環境任せになる。後者は両対応を保証できるが、過去に削除した範囲を再び持つことになる。

**Open point**: 品質レビュー工程（`code-review --fix`）の Codex 側の等価手段
**Default**: Claude Code では `/code-review --fix` を使い、Codex 側の等価手段は解決策の設計で調べる。
**Alternative**: レビュー工程は Claude Code 限定とし、Codex では省く。
**Impact**: 等価手段が無い場合、Codex 側の出力品質の保証が Claude Code と揃わない。

**Open point**: 停止条件の具体的な一覧
**Default**: 解決策の設計で、失敗した検証、未解決の曖昧性、push の拒否、認証・権限エラー、反復上限の超過を定義する。
**Alternative**: ideal state の一部として本書で固定する。
**Impact**: 一覧が曖昧だと、ハンズオフの途中で人の介入が必要な箇所が不明になる。
