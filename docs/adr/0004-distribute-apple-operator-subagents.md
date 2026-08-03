---
status: Proposed
date: 2026-08-03
deciders: repository maintainer
---

# 0004. Apple 操作はスキル＋サブエージェントの対で提供し、サブエージェントは名前指定でユーザースコープへ配布する

## Context and problem statement

Apple Reminders と Apple Notes を Claude Code から操作する能力を、本リポジトリの
成果物として提供する。`scrum-master` スキルが、Sprint Backlog や
レトロ記録がそれらのアプリにあるときにこの能力を使う。

決めなければならないことが3つある。

**(1) スキルか、サブエージェントか。** 本リポジトリの
[`rules/subagent-delegation.md`](../../.claude/rules/subagent-delegation.md) は
機構の選び方を表で定めている。「標準的な作法を持ち、タスクは呼び出しごとに
与えられるワーカー」は `skills:` を持つサブエージェント、と規定されている。
Apple 操作はまさにこれで、加えて委譲の第一条件——「結論に必要な量より遥かに
多い出力を生む作業」——にも当てはまる。リマインダー一覧の JSON ダンプや
ノート本文の HTML は、必要なのは結論だけなのに、以後のセッション全体の
コンテキストを占有する。

一方でサブエージェントは毎回コールドスタートし、会話履歴を持たない。
AppleScript 辞書の公開範囲、TCC の権限モデル、`--- scrum ---` ブロックの書式と
いった標準的な作法を、起動時に持っている必要がある。

**(2) 常時読み込まれるルーティング表に載せるか。** `.claude/CLAUDE.md` の
スキル一覧は毎ターン読み込まれる。`rules/skill-routing.md` は `scrum-master`
について「常時読み込まれるルーティング一覧に載るため、意図的に狭くしている」と
明記している。

**(3) 配布経路。** サブエージェント定義は現在 `.claude/agents/` にあるが、
`install.sh` はこのディレクトリを一切同期していない。README は
「プロジェクトスコープ、`~/.claude` へは展開しない」と明記している。
Reminders と Notes はユーザー個人のデータであり、本リポジトリの作業中だけ
操作したいものではない——どのプロジェクトからでも使えなければ意味がない。

ここで既存の同期関数 `sync_path()` をそのまま使えない事情がある。同関数は
コピー前に対象を `rm -rf` する。`hooks` / `rules` / `skills` は本リポジトリが
所有するので正しい挙動だが、**`~/.claude/agents/` は利用者自身が自作の
サブエージェントを置く場所**であり、同じことをすれば利用者のファイルを
破壊する。

## Decision

**スキルとサブエージェントを対で提供する。スキルが作法を持ち、サブエージェントが
`skills:` でそれを起動時に読み込む。常時ルーティング表には追加しない。
配布は `sync_path()` ではなく、`MANAGED_AGENTS` の名前指定で行う。**

したがって：

- `.claude/skills/apple-reminders/` と `.claude/skills/apple-notes/` が
  作法とスクリプトを持つ。単体でも使える（Codex CLI にはサブエージェントの
  概念が無いため、そちらではスキルだけが動く）。
- `.claude/agents/apple-reminders-operator.md` と
  `apple-notes-operator.md` が、対応するスキルを `skills:` で読み込み、
  `tools: Bash, Read, Grep, Glob` に制限される。**Edit と Write を持たない**ため、
  「リポジトリのファイルを変更しない」が指示ではなく構造になる。
- `.claude/CLAUDE.md` のスキル一覧と `rules/skill-routing.md` は変更しない。
  スキルもサブエージェントも自身の `description` で発見される。
- `install.sh` は `MANAGED_AGENTS`（現在は Apple 系2つ）を名前指定でコピーし、
  リストから消えた名前だけを削除する。ディレクトリ全体は触らない。
- `verification-runner` は配布しない。本リポジトリの `tests/run-*.sh` を
  実行するものであり、他プロジェクトでは意味を持たない。
- 判断は委譲しない。Sprint Goal の検査、停滞項目の解釈、改善実験の設計は
  `scrum-master` スキルに残る。サブエージェントは事実を持ってくるだけである。

### Alternatives considered

**スキルだけを作る（サブエージェントを作らない）。** 却下。追加の成果物カテゴリも
配布経路も不要で、費用が最も低いという実利があった。却下理由は2つ。
(1) スキルは本体の会話にロードされるため、CLI の生出力——リスト全件の
JSON、ノート本文の HTML——がそのまま会話に入る。これは委譲の第一条件そのもので
あり、機構の選択を誤ることになる。(2) 「リポジトリのファイルを変更しない」を
ツール許可リストで構造的に保証できない。スキルの `disallowed-tools` は
現在のターンにしか効かない。

**サブエージェントだけを作る（スキルを作らない）。** 却下。成果物が半分で済む。
しかし `skills:` は**スキルとして存在するもの**しか読み込めないため、作法を
サブエージェント本文に直書きすることになる。すると (1) 同じ AppleScript の
作法が2つの定義に重複し、(2) Codex CLI 側に提供できるものが何も無くなり、
(3) 対話的に「ノートを1つ作って」と頼むだけの場面でもコールドスタートの
サブエージェントを起動することになる。

**`.claude/CLAUDE.md` のスキル一覧に追加する。** 却下。発見性は最大になるが、
`rules/skill-routing.md` が意図的に狭く保っている常時読み込みの分岐を
2つ増やす。Apple 製アプリの操作は、Scrum やコード実装と同格の作業カテゴリでは
なく、特定の環境でだけ現れる能力である。`description` による発見で足りる。

**`sync_path "agents"` を使う（既存関数をそのまま流用）。** 却下。他の管理
パスと完全に一貫し、追加コードがゼロという強い利点があった。却下理由は、
同関数が対象を `rm -rf` することである。`~/.claude/agents/` は利用者自身の
サブエージェントの置き場所であり、`install.sh` の実行で利用者の成果物を
黙って削除することは、`rules/permissions.md` が規範とする fail-safe defaults に
正面から反する。一貫性より、リポジトリ外のユーザーデータを壊さないことを取る。

**サブエージェント一式をディレクトリごと配布する（名前指定をしない）。** 却下。
`verification-runner` が全プロジェクトに配布され、`tests/run-*.sh` が存在しない
場所で「検証してほしい」という依頼に選ばれうる。何を配るかは明示的な判断で
あるべきで、ディレクトリの中身という偶然に委ねない。

## Consequences

- 肯定：CLI の生出力が本体の会話に入らない。委譲の第一条件を満たす
  使い方になる。
- 肯定：「リポジトリを変更しない」が `tools` 許可リストによる構造的保証になる。
  `verification-runner` で確立した設計をそのまま踏襲している。
- 肯定：常時読み込まれるルーティング表が増えない。
  [apple-task-manager の ADR 0002](https://github.com/superluminal-jp/apple-task-manager/blob/main/docs/adr/0002-role-separation-via-subagents.md)
  が予告した「配布機構は my-claude-code 側の決定であり、別途 ADR が必要」に
  本 ADR が対応する。
- 肯定：`install.sh` が利用者自身のサブエージェントを削除しない。
- 否定：**成果物が2カテゴリに分かれ、対で保守する必要が生じる。** スキルの
  スクリプト名を変えたら、サブエージェント本文の記述も追随させなければ
  ならない。`tests/run-apple-operators.sh` がこの対応関係を検査する。
- 否定：`install.sh` に、他の管理パスと異なる同期規則が1つ増える。読む側は
  「なぜ agents だけ違うのか」を理解する必要がある（コメントで明示した）。
- 否定：`MANAGED_AGENTS` は手動リストである。新しいサブエージェントを
  配布したくなったら、追加を忘れると配布されない。
- 否定：サブエージェントはコールドスタートし、`AskUserQuestion` を持たない。
  曖昧な依頼（どのリスト、どのノート）を自力で解決できないため、
  「推測せず候補を報告して止まる」を本文で規定する必要がある。
- 中立：macOS 以外では両サブエージェントとも動作しない。`description` に
  macOS と明記し、失敗時は権限とプラットフォームのどちらが原因かを報告する。

## Confirmation

- `tests/run-apple-operators.sh` が、(a) 2つのサブエージェントが対応するスキルを
  `skills:` で読み込むこと、(b) `tools` に `Edit` / `Write` が無いこと、
  (c) スキルが `disable-model-invocation: true` を持たないこと
  （持つと preload できない）、(d) `install.sh` が両スキルと両エージェントを
  配布すること、(e) `scrum-master` が両者を参照すること、
  (f) `scrum-master` の routing 定義に個人利用の記述が戻っていないこと、
  (g) Reminders 側の EventKit ビルドが `-sectcreate` で `Info.plist` を
  埋め込むこと（欠けると許可ダイアログが出ず利用者が回復できない）、
  (h) どちらの write 経路にも削除機能が無いことを検査する。
- `tests/run-scrum-block.sh` が、`scrum_block.py` の出力が
  `flow_metrics.py` に無改造で通ることを含めて検証する。
- `.claude/CLAUDE.md` と `rules/skill-routing.md` に Apple 系の記述が
  無いことで、ルーティング表を汚さない決定の遵守が確認できる。
- **未検証**：本決定を記録した環境（Linux コンテナ、macOS なし）では
  ネイティブコードを一切実行していない。`remind-cli` は `swiftc` が無いため
  コンパイルすらされておらず（EventKit は Darwin 専用）、Notes の JXA も
  実行されていない。ビルドの成否、2種類の TCC ダイアログの挙動、
  Notes の `body` が HTML であることの取り扱いは macOS 上で初めて検証される。
  Python 側（`scrum_block.py`）は 46 件の単体テストで検証済みである。

## More information

- 委譲の判断基準 — [`rules/subagent-delegation.md`](../../.claude/rules/subagent-delegation.md)
- サブエージェントの `skills:` フィールド — [Create custom subagents](https://code.claude.com/docs/en/sub-agents)（2026-08-03 閲覧）
- 破壊的操作の自己適用規定 — [`rules/permissions.md`](../../.claude/rules/permissions.md)
- 記録源とデータモデルの決定、`--- scrum ---` ブロックの由来 —
  apple-task-manager の ADR 0001 / 0003
