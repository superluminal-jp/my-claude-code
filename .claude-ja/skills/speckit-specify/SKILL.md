---
name: "speckit-specify"
description: "自然言語による機能説明から、機能仕様書を作成または更新する。"
argument-hint: "Describe the feature you want to specify"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/specify.md"
user-invocable: true
disable-model-invocation: false
---


## ユーザー入力

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力を必ず考慮しなければならない（空でない場合）。

## 実行前チェック

**拡張フックの確認（仕様作成前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は読み込み、`hooks.before_specify` キー配下のエントリを探す
- YAML が解析できない、または不正な場合は、フックの確認を黙って中止し、通常どおり処理を継続する
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、または null/空の場合は、そのフックを実行可能として扱う
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて以下を出力する:
  - **オプションのフック** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須のフック** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、処理を続ける前に完了を待たなければならない。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行すること（呼び出し方は上記で示したリテラルな `{command}` の ID とは異なる場合がある。例えば skills モードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行される）。ブロックを出力するだけではフックは実行されない。
- フックが1つも登録されていない、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする

## アウトライン

トリガーとなったメッセージ内で、ユーザーが `/speckit-specify` の後に入力したテキストが機能説明**である**。以下に `$ARGUMENTS` が文字どおり現れていても、この会話の中で常にそれが利用可能だと仮定すること。ユーザーが空のコマンドを送った場合を除き、再入力を求めてはならない。

その機能説明が与えられたら、以下を行う:

1. **簡潔な短い名前を生成する**（2〜4語）:
   - 機能説明を分析し、最も意味のあるキーワードを抽出する
   - 機能の本質を捉えた2〜4語の短い名前を作成する
   - 可能な限り「動詞＋名詞」形式を使う（例: "add-user-auth", "fix-payment-bug"）
   - 技術用語や略語（OAuth2、API、JWT など）は保持する
   - 簡潔さを保ちつつ、機能が一目でわかる程度の説明性を持たせる
   - 例:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **ブランチ作成**（任意、フック経由）:

   上記の実行前チェックで `before_specify` フックが正常に実行された場合、そのフックが git ブランチを作成／切り替え、`BRANCH_NAME` と `FEATURE_NUM` を含む JSON を出力している。これらの値は参照用に控えておくが、ブランチ名は仕様ディレクトリ名を決定するものでは**ない**。

   ユーザーが `GIT_BRANCH_NAME` を明示的に指定していた場合は、それをフックに渡し、ブランチスクリプトがすべてのプレフィックス／サフィックス生成をバイパスしてその値をそのままブランチ名として使うようにする。

3. **仕様の機能ディレクトリを作成する**:

   ユーザーが `SPECIFY_FEATURE_DIRECTORY` を明示的に指定しない限り、仕様はデフォルトの `specs/` ディレクトリ配下に置かれる。

   **`SPECIFY_FEATURE_DIRECTORY` の解決順序**:
   1. ユーザーが `SPECIFY_FEATURE_DIRECTORY` を明示的に指定していた場合（環境変数、引数、設定など経由）、それをそのまま使用する
   2. それ以外の場合は、`specs/` 配下に自動生成する:
      - `.specify/init-options.json` の `feature_numbering`（推奨）または `branch_numbering`（非推奨、移行専用 — 将来のリリースで削除予定）を確認する
      - `"timestamp"` の場合: プレフィックスは `YYYYMMDD-HHMMSS`（現在のタイムスタンプ）
      - `"sequential"` またはフィールドが存在しない場合: プレフィックスは `NNN`（`specs/` 内の既存ディレクトリを走査した後の、次に使用可能な3桁の番号）
      - ディレクトリ名を構築する: `<prefix>-<short-name>`（例: `003-user-auth` または `20260319-143022-user-auth`）
      - `SPECIFY_FEATURE_DIRECTORY` を `specs/<directory-name>` に設定する
      - `branch_numbering` が使われていた（かつ `feature_numbering` が存在しなかった）場合は、1行の警告を出す: "⚠️ `branch_numbering` in init-options.json is deprecated. Rename to `feature_numbering`."

   **ディレクトリと仕様ファイルを作成する**:
   - `mkdir -p SPECIFY_FEATURE_DIRECTORY`
   - Spec Kit のプリセット／テンプレート解決スタックを通じて有効な `spec-template` を解決する（`specify preset resolve spec-template` と同等）
   - 解決された `spec-template` ファイルを、出発点として `SPECIFY_FEATURE_DIRECTORY/spec.md` にコピーする
   - `SPEC_FILE` を `SPECIFY_FEATURE_DIRECTORY/spec.md` に設定する
   - 解決済みのパスを `.specify/feature.json` に永続化する:
     ```json
     {
       "feature_directory": "<resolved feature dir>"
     }
     ```
     リテラル文字列 `SPECIFY_FEATURE_DIRECTORY` ではなく、実際に解決されたディレクトリのパス値（例えば `specs/003-user-auth`）を書き込むこと。
     これにより、下流のコマンド（`/speckit-plan`、`/speckit-tasks` など）が git ブランチ名の慣習に依存せずに機能ディレクトリを特定できるようになる。

   **重要**:
   - `/speckit-specify` の1回の呼び出しにつき、作成する機能は1つのみでなければならない
   - 仕様ディレクトリ名と git ブランチ名は独立している — 同じにすることもできるが、それはユーザーの選択次第である
   - 仕様ディレクトリとファイルは常にこのコマンドが作成するものであり、フックが作成することはない

4. 必要なセクションを把握するため、解決された有効な `spec-template` ファイルを読み込む。

5. **存在する場合**: プロジェクトの原則と統治上の制約について `.specify/memory/constitution.md` を読み込む。

6. 以下の実行フローに従う:
    1. 引数からユーザーの説明を解析する
       空の場合: ERROR "No feature description provided"
    2. 説明から主要な概念を抽出する
       特定するもの: アクター、アクション、データ、制約
    3. 不明瞭な点について:
       - 文脈と業界標準に基づいて妥当な推測を行う
       - 以下のいずれかに該当する場合のみ [NEEDS CLARIFICATION: 具体的な質問] を付ける:
         - その選択が機能のスコープやユーザー体験に大きく影響する
         - 異なる含意を持つ複数の妥当な解釈が存在する
         - 妥当なデフォルトが存在しない
       - **上限: [NEEDS CLARIFICATION] マーカーは合計最大3個まで**
       - 影響度に基づいて明確化の優先順位を付ける: スコープ > セキュリティ／プライバシー > ユーザー体験 > 技術的詳細
    4. User Scenarios & Testing セクションを埋める
       明確なユーザーフローが特定できない場合: ERROR "Cannot determine user scenarios"
    5. Functional Requirements を生成する
       各要件はテスト可能でなければならない
       未指定の詳細については妥当なデフォルトを用いる（前提事項は Assumptions セクションに記録する）
    6. Success Criteria を定義する
       測定可能で、技術非依存な成果を作成する
       定量的な指標（時間、パフォーマンス、量）と定性的な指標（ユーザー満足度、タスク完了率）の両方を含める
       各基準は実装の詳細を知らなくても検証可能でなければならない
    7. Key Entities を特定する（データが関与する場合）
    8. 返す: SUCCESS（仕様は計画フェーズに進む準備が整った）

7. セクションの順序と見出しを保ちながら、機能説明（引数）から導いた具体的な内容でプレースホルダーを置き換え、テンプレートの構造を用いて SPEC_FILE に仕様を書き込む。

8. **仕様品質の検証**: 最初の仕様書を書き終えたら、品質基準に照らして検証する:

   a. **仕様品質チェックリストの作成**: チェックリストのテンプレート構造を用いて、以下の検証項目を含むチェックリストファイルを `SPECIFY_FEATURE_DIRECTORY/checklists/requirements.md` に生成する:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
      ```

   b. **検証チェックの実行**: チェックリストの各項目に照らして仕様書をレビューする:
      - 各項目について、合格か不合格かを判定する
      - 発見した具体的な問題点を記録する（該当する仕様書のセクションを引用する）

   c. **検証結果への対応**:

      - **すべての項目が合格した場合**: チェックリストを完了とマークし、Mandatory Post-Execution Hooks セクションに進む

      - **項目が不合格の場合（[NEEDS CLARIFICATION] を除く）**:
        1. 不合格の項目と具体的な問題点を列挙する
        2. 各問題に対処するよう仕様書を更新する
        3. すべての項目が合格するまで検証を再実行する（最大3回まで）
        4. 3回繰り返してもなお不合格の場合は、残っている問題をチェックリストの Notes に記録し、ユーザーに警告する

      - **[NEEDS CLARIFICATION] マーカーが残っている場合**:
        1. 仕様書からすべての [NEEDS CLARIFICATION: ...] マーカーを抽出する
        2. **上限チェック**: マーカーが3個を超える場合は、最も重要な3個（スコープ／セキュリティ／UX への影響で判断）だけを残し、残りについては妥当な推測を行う
        3. 必要な明確化ごとに（最大3個）、以下の形式でユーザーに選択肢を提示する:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **重要 — 表のフォーマット**: Markdown の表が適切に整形されていることを確認する:
           - パイプの位置を揃え、一貫した間隔にする
           - 各セルの内容の前後にスペースを入れる: `|Content|` ではなく `| Content |`
           - ヘッダー区切り行にはダッシュを3個以上入れる: `|--------|`
           - 表が Markdown プレビューで正しく表示されることを確認する
        5. 質問には順に番号を振る（Q1, Q2, Q3 — 最大3個まで）
        6. すべての質問を、回答を待つ前にまとめて提示する
        7. ユーザーがすべての質問に対する選択を回答するまで待つ（例: "Q1: A, Q2: Custom - [details], Q3: B"）
        8. 各 [NEEDS CLARIFICATION] マーカーを、ユーザーが選択または提供した回答に置き換えて仕様書を更新する
        9. すべての明確化が解消された後、検証を再実行する

   d. **チェックリストの更新**: 各検証イテレーションの後、チェックリストファイルを現在の合格／不合格状況で更新する

## 必須の実行後フック

**このセクションを完了してからでなければ、ユーザーに完了を報告してはならない。**

プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在しない場合、または `hooks.after_specify` 配下にフックが1つも登録されていない場合は、Completion Report に進む。
- 存在する場合は読み込み、`hooks.after_specify` キー配下のエントリを探す。
- YAML が解析できない、または不正な場合は、フックの確認を黙って中止し、Completion Report に進む。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、または null/空の場合は、そのフックを実行可能として扱う
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて以下を出力する:
  - **必須のフック** (`optional: false`) — **必須の各フックについて `EXECUTE_COMMAND:` を出力しなければならない**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、処理を続ける前に完了を待たなければならない。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行すること（呼び出し方は上記で示したリテラルな `{command}` の ID とは異なる場合がある。例えば skills モードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行される）。ブロックを出力するだけではフックは実行されない。
  - **オプションのフック** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## 完了報告

以下を添えてユーザーに完了を報告する:
- `SPECIFY_FEATURE_DIRECTORY` — 機能ディレクトリのパス
- `SPEC_FILE` — 仕様ファイルのパス
- チェックリスト結果の要約
- 次フェーズ（`/speckit-clarify` または `/speckit-plan`）への準備状況

**注:** ブランチの作成は `before_specify` フック（git 拡張）が担当する。仕様ディレクトリとファイルの作成は常にこのコアコマンドが担当する。

## クイックガイドライン

- ユーザーが**何を**必要としているか、そして**なぜ**必要としているかに焦点を当てる。
- どう実装するかは避ける（技術スタック、API、コード構造は書かない）。
- 開発者ではなく、ビジネス関係者向けに書く。
- 仕様書に埋め込まれたチェックリストは作成しない。それは別のコマンドで行う。

### セクション要件

- **必須セクション**: すべての機能で完成させなければならない
- **任意セクション**: その機能に関連する場合のみ含める
- セクションが該当しない場合は、「N/A」として残すのではなく、完全に削除する

### AI 生成にあたって

ユーザーのプロンプトからこの仕様書を作成する際:

1. **妥当な推測を行う**: 文脈、業界標準、一般的なパターンを用いてギャップを埋める
2. **前提事項を記録する**: 妥当なデフォルトは Assumptions セクションに記録する
3. **明確化を制限する**: [NEEDS CLARIFICATION] マーカーは最大3個まで — 以下に該当する重要な判断にのみ使う:
   - 機能のスコープやユーザー体験に大きく影響する
   - 異なる含意を持つ複数の妥当な解釈が存在する
   - 妥当なデフォルトが一切存在しない
4. **明確化の優先順位を付ける**: スコープ > セキュリティ／プライバシー > ユーザー体験 > 技術的詳細
5. **テスターのように考える**: 曖昧な要件はすべて「テスト可能で曖昧さがない」というチェックリスト項目に不合格になるはずである
6. **明確化がよく必要となる領域**（妥当なデフォルトが存在しない場合のみ）:
   - 機能のスコープと境界（特定のユースケースの包含／除外）
   - ユーザー種別と権限（複数の矛盾する解釈があり得る場合）
   - セキュリティ／コンプライアンス要件（法的・財務的に重要な場合）

**妥当なデフォルトの例**（これらについては尋ねない）:

- データ保持: そのドメインにおける業界標準の慣行
- パフォーマンス目標: 指定がない限り、標準的な Web／モバイルアプリの期待値
- エラーハンドリング: 適切なフォールバックを備えた、ユーザーにわかりやすいメッセージ
- 認証方式: Web アプリでは標準的なセッションベースまたは OAuth2
- 統合パターン: プロジェクトに適したパターンを用いる（Web サービスなら REST/GraphQL、ライブラリなら関数呼び出し、ツールなら CLI 引数など）

### Success Criteria のガイドライン

Success Criteria は以下を満たさなければならない:

1. **測定可能であること**: 具体的な指標（時間、割合、件数、率）を含める
2. **技術非依存であること**: フレームワーク、言語、データベース、ツールに言及しない
3. **ユーザー中心であること**: システム内部ではなく、ユーザー／ビジネスの視点から成果を記述する
4. **検証可能であること**: 実装の詳細を知らなくてもテスト／検証できる

**良い例**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**悪い例**（実装寄りのもの）:

- "API response time is under 200ms"（技術的すぎる。"Users see results instantly" を使う）
- "Database can handle 1000 TPS"（実装の詳細。ユーザー向けの指標を使う）
- "React components render efficiently"（フレームワーク固有）
- "Redis cache hit rate above 80%"（技術固有）

## 完了条件

- [ ] 仕様が `SPEC_FILE` に書き込まれ、品質チェックリストに照らして検証されている
- [ ] 上記の Mandatory Post-Execution Hooks のルールに従い、拡張フックが実行またはスキップされている
- [ ] 機能ディレクトリ、仕様ファイルのパス、チェックリスト結果を添えてユーザーに完了が報告されている
</content>
</invoke>
