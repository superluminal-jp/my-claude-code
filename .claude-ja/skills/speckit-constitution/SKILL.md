---
name: "speckit-constitution"
description: "対話的な入力または提供された原則の入力から、プロジェクト憲法を作成または更新する。"
argument-hint: "Principles or values for the project constitution"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/constitution.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

進める前に、ユーザー入力（空でない場合）を必ず考慮しなければなりません。

## Scope Guard

このコマンド自体の作業は、プロジェクト憲法そのものの更新に限定されます。依存するテンプレートや
コマンドは実行時に憲法を読み取りますが、ここでは変更されません。

- ユーザー入力のすべての部分を、憲法（governance）に関する内容か、それとは別の
  非ガバナンス的な意図かに分類してください。
- 入力に機能実装、コード生成、リファクタリング、ビルド、デプロイの依頼が含まれる場合、
  それらを実行してはいけません。代わりに、それらを保留中の意図として抽出してください。
- アプリケーションのソースファイル、機能ルート、コンポーネント、テスト、デプロイファイル、
  その他憲法ワークフローと無関係な成果物を作成・変更・削除してはいけません。
- ある指示が憲法の内容に該当するかどうかが不明な場合は、変更を行う前に確認を求めてください。
- 憲法の更新が完了した後、保留中の各意図について `Next Actions` セクションを含めてください。
  元の意図を記載し、`/speckit-specify` のような適切なフォローアップの Spec Kit コマンドを
  提案してください（呼び出しは行わない）。
- 非ガバナンス的な意図が存在しない場合は、`Next Actions` セクションを省略してください。

## Pre-Execution Checks

**拡張フックの確認（憲法更新の前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認してください。
- 存在する場合は、それを読み込み、`hooks.before_constitution` キーの配下のエントリを探してください
- YAML が解析できない、または無効な場合は、フックの確認を黙ってスキップし、通常どおり続行してください
- `enabled` が明示的に `false` であるフックは除外してください。`enabled` フィールドがないフックは、デフォルトで有効として扱ってください。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしないでください：
  - フックに `condition` フィールドがない、または null/空である場合、そのフックは実行可能として扱ってください
  - フックが空でない `condition` を定義している場合、そのフックはスキップし、条件評価は HookExecutor の実装に委ねてください
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換えてください。例えば、`speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに基づいて以下を出力してください：
  - **オプションのフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須のフック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前にその完了を待たなければなりません。この agent/session で自分がそのコマンドを実行するのと同じ方法で実行してください（実際の呼び出し方は、上記に示された文字通りの `{command}` の ID とは異なる場合があります。例えば skills モードの agent では `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
- フックが登録されていない場合、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップしてください

## Outline

あなたは `.specify/memory/constitution.md` にあるプロジェクト憲法を更新しています。このファイルは角括弧内のプレースホルダートークン（例：`[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）を含む TEMPLATE です。あなたの仕事は、(a) 具体的な値を収集・導出し、(b) テンプレートを正確に埋めることです。

**注記**: `.specify/memory/constitution.md` がまだ存在しない場合、プロジェクトのセットアップ時に `.specify/templates/constitution-template.md` から初期化されているはずです。もし存在しない場合は、まずテンプレートをコピーしてください。

以下の実行フローに従ってください：

1. `.specify/memory/constitution.md` にある既存の憲法を読み込みます。
   - `[ALL_CAPS_IDENTIFIER]` 形式のすべてのプレースホルダートークンを特定します。
   **重要**: ユーザーはテンプレートで使われている数よりも少ない、あるいは多い原則を必要とする場合があります。数が指定されている場合は、それに従ってください - 一般的なテンプレートには従います。それに応じてドキュメントを更新してください。

2. プレースホルダーの値を収集・導出します：
   - ユーザー入力（会話）が値を提供している場合は、それを使用します。
   - そうでない場合は、既存のリポジトリのコンテキスト（README、ドキュメント、埋め込まれた過去の憲法バージョンなど）から推測します。
   - ガバナンスの日付について：`RATIFICATION_DATE` は元の採択日です（不明な場合は確認するか TODO とします）。`LAST_AMENDED_DATE` は、変更が行われた場合は本日の日付、そうでない場合は以前の値を保持します。
   - `CONSTITUTION_VERSION` はセマンティックバージョニングのルールに従ってインクリメントしなければなりません：
     - MAJOR：後方互換性のないガバナンス/原則の削除または再定義。
     - MINOR：新しい原則/セクションの追加、または実質的に拡充されたガイダンス。
     - PATCH：明確化、文言修正、誤字修正、非意味的な微修正。
   - バージョンアップの種類が曖昧な場合は、確定させる前に理由を提示してください。

3. 更新された憲法の内容を起草します：
   - すべてのプレースホルダーを具体的なテキストに置き換えます（プロジェクトが意図的にまだ定義しないと選んだテンプレートのスロットを除き、角括弧のトークンを残してはいけません。残す場合は明示的にその理由を述べてください）。
   - 見出しの階層を保持し、コメントは、それらがまだ明確化に役立つガイダンスを提供していない限り、置き換え後は削除してもかまいません。
   - 各原則セクションが、簡潔な名前の行、非交渉可能なルールを捉えた段落（または箇条書き）、自明でない場合は明示的な根拠を持つことを確認してください。
   - Governance セクションが、改訂手続き、バージョニングポリシー、遵守レビューの期待事項を記載していることを確認してください。

4. Sync Impact Report を作成します（更新後の憲法ファイルの先頭に HTML コメントとして追加します）：
   - バージョンの変更：旧 → 新
   - 変更された原則の一覧（リネームされた場合は旧タイトル → 新タイトル）
   - 追加されたセクション
   - 削除されたセクション
   - 意図的に先送りされたプレースホルダーがある場合の、フォローアップの TODO。

5. 最終出力前の検証：
   - 説明のつかない角括弧トークンが残っていないこと。
   - バージョン行がレポートと一致していること。
   - 日付が ISO 形式（YYYY-MM-DD）であること。
   - 原則が宣言的で検証可能であり、曖昧な言葉が含まれていないこと（"should" は適宜 MUST/SHOULD とその根拠に置き換える）。

6. 完成した憲法を `.specify/memory/constitution.md` に書き戻します（上書き）。

7. ユーザーへの最終サマリーを出力します。内容は以下の通りです：
   - 新しいバージョンと、そのバージョンアップの理由。
   - 手動でのフォローアップが必要な TODO プレースホルダーや先送りされた項目。
   - 提案するコミットメッセージ（例：`docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。
   - 先送りされた非ガバナンス的な意図がある場合の `Next Actions` セクション。

Formatting & Style Requirements:

- テンプレートにあるとおりの Markdown の見出しを使用してください（レベルを下げたり上げたりしないでください）。
- 長い根拠の文は読みやすさを保つために折り返してください（理想的には 100 文字未満）が、不自然な改行で無理に強制しないでください。
- セクション間は空行を 1 行だけ入れてください。
- 行末の余分な空白を避けてください。

ユーザーが部分的な更新（例：1 つの原則の改訂のみ）を提供した場合でも、検証とバージョン決定のステップは実行してください。

重要な情報が欠けている場合（例：採択日が本当に不明な場合）は、`TODO(<FIELD_NAME>): explanation` を挿入し、Sync Impact Report の先送り項目に含めてください。

新しいテンプレートを作成しないでください。常に既存の `.specify/memory/constitution.md` ファイルに対して操作してください。

## Post-Execution Checks

**拡張フックの確認（憲法更新の後）**:
プロジェクトルートに `.specify/extensions.yml` が存在するか確認してください。
- 存在する場合は、それを読み込み、`hooks.after_constitution` キーの配下のエントリを探してください
- YAML が解析できない、または無効な場合は、フックの確認を黙ってスキップし、通常どおり続行してください
- `enabled` が明示的に `false` であるフックは除外してください。`enabled` フィールドがないフックは、デフォルトで有効として扱ってください。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしないでください：
  - フックに `condition` フィールドがない、または null/空である場合、そのフックは実行可能として扱ってください
  - フックが空でない `condition` を定義している場合、そのフックはスキップし、条件評価は HookExecutor の実装に委ねてください
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換えてください。例えば、`speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに基づいて以下を出力してください：
  - **オプションのフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須のフック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前にその完了を待たなければなりません。この agent/session で自分がそのコマンドを実行するのと同じ方法で実行してください（実際の呼び出し方は、上記に示された文字通りの `{command}` の ID とは異なる場合があります。例えば skills モードの agent では `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
- フックが登録されていない場合、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップしてください
