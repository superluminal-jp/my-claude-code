# Feature Specification: 常時適用の構成スキル `pyramid-structure` と機械検査

**Feature Branch**: `feat/pyramid-structure-always-on`

**Created**: 2026-10-30

**Status**: Draft

**Input**: User description: "今回作成したスキルを常時適用する方針" 確認のうえ、次の2点で合意した: (1) 取り込みプラグイン `minto-pyramid` は外して `pyramid-structure` に置き換え、`minto-pyramid` にしかない機能(思考過程の扱いの規則、完了前チェック、回答・意思決定・文書のテンプレート、評価ケース)を移す、(2) 機械検査スクリプトは実質的な回答すべてで実行する。その後の指示 "どのように考えて回答しているかは積極的にユーザーに提供した方が良い" により、思考過程の規則は「出さない」から「どう答えに至ったかを構造化して示す」へ反転した。

**Authority**: 本仕様が正である。spec 052 の制約「外部から取り込んだ `minto-pyramid` スキルは編集しない」は、本仕様で `minto-pyramid` を退避するため対象がなくなる。spec 051・052 が常時ロードの規則 `pyramid-principle.md` に定めた内容(結論先行、前提と用語、部の順序、段落の先頭文)は変えない。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 実質的な出力はすべて、送る前に構成を機械検査される (Priority: P1)

利用者が分析・説明・計画・意思決定・レビュー・文書を求める。Claude は `pyramid-structure` を読み込み、下書きを `scripts/check.py md -` に標準入力で渡し、エラー(E)をすべて直し、警告(W)は意図的なものを除いて直してから送る。

**Why this priority**: 利用者が選んだ方針そのもの。検査が判断だけに頼らず、毎回同じ基準で実行される。

**Independent Test**: スキルの単体テストが、見出し・箇条書き・冒頭の文の検査(S1〜S8)と標準入力の読み取りを確かめる。

**Acceptance Scenarios**:

1. **Given** 箇条書きで始まる回答、**When** `check.py md -` に渡す、**Then** 冒頭を文で答えるよう求める警告 S8 が出る。
2. **Given** 太字の先頭が「理由」「Reasons」のような主題ラベルの箇条書き、**When** 検査する、**Then** 警告 S5 が出る。主張文が先頭なら出ない。
3. **Given** 下位項目が1つだけの箇条書き、または項目が1つだけのリスト、**When** 検査する、**Then** 警告 S2 が出る。
4. **Given** 冒頭の文で答え、主張を先頭にした箇条書きで支える回答、**When** 検査する、**Then** 所見は0件で `ok` を出し、終了コードは0である。

---

### User Story 2 - 置き換えても `minto-pyramid` の機能を失わず、推論はむしろ示す (Priority: P1)

利用者は `minto-pyramid` が担っていた常時適用の振る舞い(完了前に自己点検する、意思決定を推奨から示す)を引き続き受ける。加えて、どう考えて答えに至ったか(前提と情報源、推論の種類と手順、退けた選択肢とその理由、前提条件、不確かさ)を、答えを支える位置に構造化して受け取る。

**Why this priority**: 置き換えで機能が欠けると、常時の振る舞いが後退する。推論が見えれば、利用者は答えをどこまで信頼するかを自分で判断できる。

**Independent Test**: `SKILL.md` が推論の開示と完了前チェックを持ち、`references/templates.md` が回答・意思決定・長い文書の形を持ち、評価ケース4件(うち1件は推論の開示向けに書き換え)が移っている。

**Acceptance Scenarios**:

1. **Given** `SKILL.md`、**When** 読む、**Then** 説明文が実質的なタスクすべてでの使用を求め、除外の境界(単一の事実、短い直接の答え、機械の出力)を述べている。
2. **Given** `SKILL.md`、**When** 読む、**Then** 優先順位(利用者の指示、安全とシステムの制約、求められた書式、このスキル)と推論の開示が書かれている。推論は検討の生の流れではなく構造化した説明として示し、内部の過程を説明するときは再構成であると明記する。
3. **Given** `evals/`、**When** 一覧する、**Then** `lead-with-answer`、`avoid-topic-only-headings`、`respect-user-format`、`no-chain-of-thought` を書き換えた `explains-reasoning`、新しい `review-finds-structure-gaps` がある。

---

### User Story 3 - 依頼されたレビューでは、主張の木の論理まで検査できる (Priority: P2)

利用者が文書の構成レビューを依頼する。Claude は見出しを検査し、深いレビューでは本文から主張の木(JSON)を書き出して、演繹の妥当性(真理表、反例つき)と宣言された範囲の重複・漏れを検査する。

**Independent Test**: 単体テストが T1〜T12 を確かめる。

### Edge Cases

- 利用者が別の順序(時系列のみ等)を指定した場合は、その指定が優先する。警告 S8 は意図的なものとして直さない。
- 見出しが主張文になっている親に本文の導入がない場合、スクリプトは判断できないので警告 S3 にとどめ、判断は J2 で行う。
- 検査は形式だけを保証する。主張か否か、子が親に答えるか、木が本文に忠実かは判断(J1〜J6)に残る。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `.claude/skills/pyramid-structure/` を自作スキルとして置き、`tests/run-config-pyramid.sh` の `authored_skills` に加える。
- **FR-002**: `minto-pyramid` を `archive/minto-pyramid/` へ退避する。`install.sh` は `skills/` を正確に置き換えるため、再実行で `~/.claude/skills/minto-pyramid/` も消える。
- **FR-003**: `check.py md` は標準入力(`-`)を読み、箇条書きを木として検査し(S2・S5・S6)、見出し代わりの太字だけの行も主題ラベルか検査し(S5)、文書が箇条書き・表・コードで始まる場合に S8 を出し、所見を行番号順に並べる。参考文献などの木の外の節にある箇条書きは検査しない。`--template` で宣言した名前は、見出しでも箇条書きの先頭でもラベルとして扱わない。
- **FR-004**: README(英・日)、`docs/claude-config-design.md` の該当行、スキルの README を変更後の挙動と一致させる。
- **FR-005**: スキルのフォルダを skills ディレクトリ型プラグインとしてもパッケージ化する(`.claude-plugin/plugin.json`、フックなし)。`claude plugin validate --strict` がプラグインとしても、スキルとしても受け入れる。
- **FR-006**: 各評価ケースは、費用のかからない決定的な判定を2つ持つ。スキルが呼ばれたこと(`tool_used: Skill`)と、検査スクリプトが実行されたこと(`tool_used: Bash`、プラグインありの側だけで判定)。どのケースも試験対象のモデルを固定しない。判定役(`llm` 判定)には Haiku を、試験対象には利用者が実際に使うモデルを、実行時に指定する。

## Success Criteria *(mandatory)*

- **SC-001**: `tests/run-config-pyramid.sh` と `tests/run-readme-skill-index.sh` がすべて通る。
- **SC-002**: スキルの単体テスト(`python3 -B -m unittest discover -s tests -v`)がすべて通り、ruff と `mypy --strict` が所見0件である。

## Alternatives considered

- **思考過程を出さない(`minto-pyramid` の規則のまま)**: 利用者の指示に反し、答えの信頼性を利用者が判断する材料を減らすため採らない。
- **検討の生の流れをそのまま貼る**: 構造がなく読み手が検証しにくい。また、推論モデルが述べる推論は、実際に答えを左右した要因を省くことがある(Anthropic, "Reasoning models don't always say what they think", 2025: Claude 3.7 Sonnet が使ったヒントに言及したのは平均25%)。そのため構造化した説明を示し、再構成であることを明記する。

- **併存(両方を常時適用)**: 変更は小さいが、毎回 Minto の指示が二重に読み込まれ、用語のずれ(`inductive`・`ranked` と `comparative`)が残るため採らない。
- **新スキルを依頼時のみにする**: 常時適用という利用者の方針に反するため採らない。
- **Stop フックで自動検査**: モデル呼び出しを増やさずに実行できるが、spec 042 でループを理由に Stop フックを外した経緯があるため採らない。

- **評価の試験対象もHaikuにする**: 費用は下がるが、常時適用のスキルに求めるのは、利用者が実際に使うモデルが指示に従い、毎回検査を実行することである。Haikuでの得点はそのモデルの振る舞いを示さないため、既定にはしない。ケースでモデルを固定しないので、安価な予備試験として `--model haiku` で実行することはできる。

## Assumptions

- 実行環境に Python 3.10 以上がある。スクリプトは標準ライブラリだけを使う。
- `.claude/settings.json` の `defaultMode` が `auto` なので、毎回のスクリプト実行に許可の確認は要らない。
- 毎回の検査で、実質的な回答ごとにツール呼び出しが1回増える。

## Out of scope

- Claude.ai・ChatGPT 用の移植プロンプト(`claude-ai-system-prompt.md`、`chatgpt-system-prompt.md`)の出典の記述は変えない。中身の Minto の規則は引き続き有効である。
- 評価(`claude plugin eval`)の実行。モデル呼び出しを伴うため、利用者の手元で行う。
