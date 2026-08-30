---
name: "speckit-converge"
description: "現在のコードベースをその機能の spec、plan、tasks と照らし合わせて評価し、未実装の残作業を新しいタスクとして tasks.md に追記することで、implement が完了できるようにする。"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/converge.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力を（空でなければ）**必ず**考慮しなければなりません。

## Pre-Execution Checks

**拡張フックの確認（収束処理の前）**:

- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は読み込み、`hooks.before_converge` キー配下のエントリを探す。
- YAML がパースできない、または無効な場合は、フックの確認を黙って（サイレントに）スキップし、通常どおり処理を続行する。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**いけません**。
  - フックに `condition` フィールドがない、または null/空の場合は、そのフックを実行可能として扱う。
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる。
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例: `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する。
  - **オプションのフック**（`optional: true`）:

    ```text
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **必須のフック**（`optional: false`）:

    ```text
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Goal.
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、処理を続ける前に完了を待た**なければなりません**。あなた自身がこのエージェント／セッションでコマンドを実行するのと同じ方法で実行してください（呼び出し方法は、上記に示された文字どおりの `{command}` の ID とは異なる場合があります。例えば、skills モードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。

- 登録されたフックがない場合、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする。

## Goal

機能の仕様（spec）、計画（plan）、タスク（tasks）が求めるものと、コードベースが現在実装している内容との間のギャップを埋めます。`spec.md`・`plan.md`・`tasks.md` を**唯一の意図の情報源**として読み込み（憲法（constitution）を統治する制約として扱う）、コードの現状を評価し、どの要件・受け入れ基準・計画上の決定・既存タスクが未達成／不完全／部分的にしか満たされていないかを判断し、**残っている作業をそれぞれ新しい、追跡可能なタスクとして** `tasks.md` の末尾に**追記**して、`/speckit-implement` がそれを完了できるようにします。このコマンドは、現在の `tasks.md` に対して `/speckit-implement` が実行済みであり、かつ `/speckit-tasks` が完全な `tasks.md` を生成した後にのみ実行しなければなりません。

これは差分（diff）ツールでは**なく**、変更履歴を追跡するものでも**ありません**。コードの現在の状態を機能のアーティファクトと照らして評価するだけであり、git もブランチ比較も履歴も使いません。

## Operating Constraints

**追記専用（APPEND-ONLY）、書き換え禁止（NEVER REWRITE）**: このコマンドの唯一の書き込みは、`tasks.md` への新しい `## Phase N: Convergence` セクションの追記です。以下を行っては**いけません**。

- `spec.md` や `plan.md` をいかなる形であれ変更すること。
- 既存のタスク（以前の Convergence フェーズのタスクを含む）を書き換え・番号振り直し・並べ替え・削除すること。
- アプリケーションコードを変更・作成・削除すること — 追記されたタスクを完了させるのは `/speckit-implement` の仕事です。

コードベースがすでにすべてを満たしている場合、このコマンドは `tasks.md` を**一バイトも変えずに**そのまま維持し（空の Convergence ヘッダーも作らない）、クリーンな結果を報告しなければなりません。

**憲法の権威（Constitution Authority）**: プロジェクトの憲法（`.specify/memory/constitution.md`）は**交渉の余地がありません**。MUST 原則に違反するコードは最高重大度の指摘事項であり、対応する是正タスクを生成します。憲法が未記入のテンプレートのままである場合は、失敗するのではなく、憲法チェックを適切にスキップします。

## Execution Steps

### 1. Initialize Convergence Context

リポジトリのルートから `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` を一度実行し、JSON をパースして FEATURE_DIR と AVAILABLE_DOCS を取得します。以下の絶対パスを導出します。

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md
- CONSTITUTION = `.specify/memory/constitution.md`（存在する場合）

`spec.md`、`plan.md`、`tasks.md` のいずれかが欠けている場合は、実行すべき前提コマンドを明示した、わかりやすく実行可能なメッセージとともに停止します（spec が欠けていれば `/speckit-specify`、plan が欠けていれば `/speckit-plan`、tasks が欠けていれば `/speckit-tasks`）。部分的な出力は生成しません。
"I'm Groot" のような引数中のシングルクォートには、エスケープ構文を使用してください。例: 'I'\''m Groot'（可能であればダブルクォートでの囲み: "I'm Groot"）。

### 2. Load Artifacts (Progressive Disclosure)

各アーティファクトから必要最小限のコンテキストのみを読み込みます。

**spec.md から:**

- Functional Requirements（FR-###）
- Success Criteria（SC-###）— ビルド可能な作業を必要とする項目のみを含める。ローンチ後の成果指標やビジネス KPI は除外する。
- User Stories とその Acceptance Scenarios
- Edge Cases（存在する場合）

**plan.md から:**

- アーキテクチャ／スタックの選択と技術的な決定事項
- Data Model への参照
- フェーズと、計画が作成または編集すると述べている名前付きのタッチポイント（ファイル／コンポーネント）
- 技術的な制約

**tasks.md から:**

- タスク ID（次の ID と次のフェーズ番号を計算するため）
- 説明、フェーズごとのグルーピング、参照されているファイルパス

**憲法から（未記入のテンプレートでなければ）:**

- 原則の名前と MUST／SHOULD の規範的な記述

### 3. Build the Intent Inventory

内部モデルを構築します（生のアーティファクトをそのまま出力しない）。

- **要件インベントリ**: FR-### / SC-### / ユーザーストーリーの受け入れシナリオ（例: `US1/AC2`）ごとに安定したキーを1つ持たせ、加えてビルド可能な義務を課す計画上の決定事項や憲法の原則も含める。
- **コードスコープマップ**: `plan.md` と `tasks.md` に記載されたファイルパスと、各要件が説明する概念に対するキーワード検索から、評価対象となるソースファイルとコンポーネントの集合を導出する。評価はこの範囲に限定し、アーティファクトが定義する範囲を超えてスコープを推測しては**いけません**。

### 4. Assess the Codebase and Classify Findings

意図インベントリの各項目について、対象範囲内の現在のコードを検査し、ギャップがある場合にのみ `Finding`（所見）を作成します。すべての所見を**ギャップ種別（gap type）**で分類します。

- **`missing`**: 必要な作業がコードに完全に存在しない。
- **`partial`**: 作業は存在するが、要件／受け入れ基準／計画上の決定をまだ完全には満たしていない。
- **`contradicts`**: コードが、記載された意図または憲法の MUST 原則と矛盾する何かを行っている。
- **`unrequested`**: コードに、spec、plan、tasks のいずれからも求められていない作業が含まれている（気づきのために表面化させるものであり、converge はコードを削除**しません** — レビュー／正当化または削除のためのタスクを追記するだけです）。

各 `Finding` には、安定した ID、それが遡る `source-ref`、`gap-type`、重大度、そして観測された証拠（ファイル／領域）を伴う簡潔な人間可読の説明を記録します。

**エッジケース:**

- **コードがほとんど、または全く存在しない場合**: 失敗させるのではなく、指定されたスコープ全体を残作業として `missing` 扱いにする。
- **何も残っていない場合**: 所見をゼロ件として、ステップ7の収束済み分岐に従う。

### 5. Assign Severity

- **CRITICAL**: 憲法の MUST 原則に違反する、または P1 ユーザーストーリーの基本機能をブロックする `missing`／`contradicts` のギャップ。
- **HIGH**: コアとなる機能要件または受け入れ基準に対する `missing` または `partial` のギャップ。
- **MEDIUM**: 二次的な要件に対する `partial` のギャップ、または正当性が不明瞭な `unrequested` の追加。
- **LOW**: 軽微な部分的ギャップ、仕上げ（polish）、またはリスクの低い `unrequested` の追加。

### 6. Present the In-Session Findings Summary

何かを追記する前に、簡潔で重大度別に整理された要約を出力します（この段階ではまだファイル書き込みは行わない）。

## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | missing  | HIGH     | FR-008 | Example: no append-only guard detected in path/to/module.py when writing tasks.md | Add append-only enforcement |

**要約メトリクス:**

- 確認した要件／受け入れ基準の数
- 確認した計画上の決定の数
- 確認した憲法の原則の数（または「skipped — template」）
- ギャップ種別別の所見数（missing / partial / contradicts / unrequested）
- 重大度別の所見数

### 7. Append Convergence Tasks (or report converged)

**1件以上の実行可能な所見がある場合**（`tasks_appended` の結果）:

追記契約（append contract）に従い、`tasks.md` の**末尾**に追記します。

1. 既存のすべてのタスク ID をスキャンし、最大値を `M` とする。次のフェーズ番号 `N`（既存の最大フェーズ + 1）を決定する。
2. 新しいセクションヘッダー `## Phase N: Convergence` を1つだけ書き込む。
3. 実行可能な所見1件につき1つのチェックリスト項目を発行し、CRITICAL／HIGH を先頭に並べ、ゼロ埋めされた ID `T{M+1:03d}, T{M+2:03d}, …` を割り当てる。

   ```markdown
   - [ ] T042 <imperative description> per <source-ref> (<gap-type>)
   ```

   `<source-ref>` はタスクの由来を示す。例: `FR-003`、`SC-002`、`US1/AC2`、`plan: storage decision`、`Constitution II`。

   `<gap-type>` は `missing`、`partial`、`contradicts`、`unrequested` のいずれか。

   憲法違反に関するタスクは必ず最初に発行し、`CRITICAL` として記述しなければなりません。
4. 既存の ID を再利用または番号振り直ししてはいけません。以前の Convergence フェーズが既に存在する場合は、その下に別番号のフェーズを新たに追加し、古いものには手を触れません。

**実行可能な所見が1件もない場合**（`converged` の結果）:

- `tasks.md` はいかなる形であれ変更**しません** — 空のフェーズヘッダーも作りません。
- 次のように報告します: **"✅ Converged — the implementation satisfies the spec, plan, and tasks."**
- 確認した内容の要約カウントを含めます。

### 8. Provide Next Actions (Handoff)

- `tasks_appended` の場合: どのフェーズの下に何件のタスクを追記したかを述べ、それらを完了させるために `/speckit-implement` の実行を推奨する。以降の converge 実行では残作業がより少なくなる、または無くなることを補足する。
- `converged` の場合: レビューへの移行、または PR のオープンを推奨する。この機能の指定されたスコープに関しては、これ以上の implement パスは不要である。

### 9. Check for extension hooks

結果を生成した後、プロジェクトルートに `.specify/extensions.yml` が存在するか確認します。

- 存在する場合は読み込み、`hooks.after_converge` キー配下のエントリを探す。
- YAML がパースできない、または無効な場合は、フックの確認を黙ってスキップし、通常どおり処理を続行する。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**いけません**。
  - フックに `condition` フィールドがない、または null/空の場合は、そのフックを実行可能として扱う。
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる。
- ユーザーがオプションの後続コマンドを実行するかどうかを判断できるよう、フックを列挙する前に、収束の結果（`converged` または `tasks_appended`）をセッション内で報告します。
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例: `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する。
  - **オプションのフック**（`optional: true`）:

    ```text
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

  - **必須のフック**（`optional: false`）:

    ```text
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、処理を続ける前に完了を待た**なければなりません**。あなた自身がこのエージェント／セッションでコマンドを実行するのと同じ方法で実行してください（呼び出し方法は、上記に示された文字どおりの `{command}` の ID とは異なる場合があります。例えば、skills モードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。

- 登録されたフックがない場合、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする。
