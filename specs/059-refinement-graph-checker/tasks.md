---
description: "Task list for 059: 要求とスキルの多段の関係を宣言し、その構造を読み取り専用の検査器で検査する"
---

# Tasks: 要求とスキルの多段の関係を宣言し、その構造を読み取り専用の検査器で検査する

背景、用語、Claude が決めた既定 D1〜D14、規則 S-00〜S-11 は、本ファイルと同じディレクトリの `spec.md` にある。技術の選択は `plan.md`、設計の判断は `research.md`、欄ごとの違反の対応は `data-model.md`、コマンドの入出力は `contracts/cli.md` にある。リポジトリは Claude Code の利用者レベルの設定を管理する `my-claude-code` である。作業は、`origin/main`(コミット 34708a5)から作った Git のワークツリー `my-claude-code-worktrees/refinement-graph-checker`(ブランチ `feat/refinement-graph-checker`)で行う。「検査器」は `tools/refinement-checker/check_graph.py`、「受け入れテスト」は `tools/refinement-checker/tests/test_check_graph.py`、「まとめの検査スクリプト」は `tests/run-refinement-checker.sh` を指す。

**Tests**: spec の SC-001 が、各負例のテストを実装より前に書き、失敗を確かめることを求める。このため各 User Story の段階で、テストを先に書き、失敗を記録してから実装する。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: ほかの作業と並行できる(別のファイルで、未完了の作業に依存しない)
- **[Story]**: 対応する User Story(US1、US2、US3)

## Phase 1: Setup

- [X] T001 変更前の状態を記録する: ワークツリーを作った直後、変更を加える前(コミット 34708a5)に、ネットワークを使わないローカルの検査をすべて実行した。結果は spec の SC-002 に書いた件数で、失敗はなかった
- [X] T002 ディレクトリ `tools/refinement-checker/`、`tools/refinement-checker/examples/`、`tools/refinement-checker/tests/fixtures/requirements/`、`tools/refinement-checker/tests/fixtures/skills/` を作る

## Phase 2: Foundational

- [X] T003 受け入れテストの土台を `tools/refinement-checker/tests/test_check_graph.py` に書く。検査器を `sys.executable -B` のサブプロセスとして `--format json` で起動し、終了コードと JSON を返す補助関数と、「終了コードが 1 で、違反の規則 ID の集合が期待する集合と一致する」ことを確かめる補助関数を置く(research.md の R7)
- [X] T004 まとめの検査スクリプト `tests/run-refinement-checker.sh` を書く。リポジトリのほかの `tests/run-*.sh` と同じく `PASS`/`FAIL` の行と `Results: N passed, M failed` を出し、失敗があれば終了コード 1 を返す。中身は、受け入れテストの実行(`PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover`)、2つの例の検査、`.claude/skills` の互換モードの検査、spec の「後の Phase へ送るテスト」T-04・T-05・T-06・T-10 の `NOT RUN` の行(件数に数えない)である

## Phase 3: User Story 1 - 要求の分解の構造の誤りを見つける (Priority: P1)

**Goal**: 要求の論理グラフの宣言ファイルを読み、S-00〜S-08 と S-11 を判定する。

**Independent Test**: 下の T005 の正例と負例を検査器にかけ、終了コードと規則 ID を確かめる。

- [X] T005 [P] [US1] 要求の論理グラフの正例と負例を `tools/refinement-checker/tests/fixtures/requirements/` に JSON で作る。各負例は、期待する違反の1つだけを含み、ほかは正しい(根は1つ、すべてのノードに受け入れ条件がある)。対象は spec の User Story 1 のシナリオ1〜14(P1-01〜P1-08、P1-10 を含む)である。シナリオ15の10,000ノードの直鎖と100,000段の入れ子は、テストの中で生成する。ファイル名は `p1-NN-<内容>.json`(引き継ぎ書の番号があるもの、例 `p1-03-cycle.json`)か `us1-NN-<内容>.json`(本仕様で加えたシナリオ)とし、正例は `valid-<内容>.json` とする
- [X] T006 [US1] 受け入れテストに、User Story 1 のシナリオ1〜15を1つずつ確かめるテストを書く。終了コード 2 を期待するテストは、JSON の `status` が `error` で `error` が空でないことも確かめる(research.md の R7)
- [X] T007 [US1] まとめの検査スクリプトを実行し、検査器がないために T006 のテストがすべて失敗することを記録する(Red)。結果: 22件のテストがすべて失敗した(subTest を含め33件の失敗)。まとめの検査スクリプトの RC-01〜RC-04 も失敗した
- [X] T008 [US1] 検査器に、入力の読み込み(5 MiB の上限、UTF-8、重複キーの拒否、深い入れ子の拒否、最上位の検査、終了コード 2)、要求のノードの読み取り(data-model.md の §1・§2 の表のとおり、欄がないときはその欄の規則の違反)、S-01〜S-08 と S-11 の判定、違反の並べ替え(research.md の R4)、JSON と人が読む形式の出力(contracts/cli.md)を実装する。循環は反復の深さ優先探索で見つけ、宣言の順で最も早いノードから始まるように経路を回転させる(R3)
- [X] T009 [US1] まとめの検査スクリプトを実行し、T006 のテストがすべて通ることを確かめる(Green)。結果: 22件が通った(Python 3.14.3 と macOS 標準の 3.9.6 の両方)。RC-02〜RC-04 は T019 と User Story 3 の作業で通す

## Phase 4: User Story 2 - スキル合成グラフの多段と権限を検査する (Priority: P1)

**Goal**: スキル合成グラフの宣言ファイルを読み、S-00〜S-03、S-08、S-09 を判定する。

**Independent Test**: 下の T010 の正例と負例を検査器にかけ、終了コードと規則 ID を確かめる。

- [X] T010 [P] [US2] スキル合成グラフの正例と負例を `tools/refinement-checker/tests/fixtures/skills/` に JSON で作る。対象は spec の User Story 2 のシナリオ1〜5である。権限は `read_only`・`workspace_write`・`external_effect`、役割は `orchestrator`・`worker`・`auditor`・`checker` だけが正しい値である(spec の D6)
- [X] T011 [US2] 受け入れテストに、User Story 2 のシナリオ1〜5を確かめるテストを書く
- [X] T012 [US2] T011 のテストが失敗することを記録する(Red)。結果: 新しい7件が失敗し、User Story 1 の22件は通った
- [X] T013 [US2] 検査器に、スキルのノードの読み取り(data-model.md の §3)と S-09 の判定を加える。`auditor` と `checker` の子孫は、訪問済みの集合を持つ反復の幅優先探索でたどる
- [X] T014 [US2] T011 のテストが通ることを確かめる(Green)。結果: 29件が通った(Python 3.14.3 と 3.9.6)

## Phase 5: User Story 3 - 既存の一段の宣言を互換モードで検査する (Priority: P2)

**Goal**: 引数 `--skills-dir` でスキルのディレクトリを読み、S-02、S-03、S-08、S-10 を判定する。

**Independent Test**: 一時ディレクトリに架空のスキルを作って互換モードの判定を確かめ、既存の検査スクリプトを実行して件数を比べる。

- [X] T015 [US3] 受け入れテストに、spec の User Story 3 のシナリオ3を確かめるテストを書く。架空のスキル `parent`、`child-a`、`child-b` を一時ディレクトリに作る(`tests/run-config-pyramid.sh` の関数 `write_fixture_skill` と同じ形の `SKILL.md`)。正しい宣言、`ghost` の宣言、`child-a` による `child-b` の宣言、`parent` による自分自身の宣言に加え、コードブロックの中の宣言が数えられないこと、`SKILL.md` のないディレクトリがスキルとして読まれないことを確かめる
- [X] T016 [US3] T015 のテストが失敗することを記録する(Red)。結果: 新しい9件のうち8件が失敗した。残る1件(存在しないディレクトリが終了コード 2 になる)は、互換モードを拒む仮の実装が同じく終了コード 2 を返したために通っていた。互換モードの実装の後も通ることを T018 で確かめた
- [X] T017 [US3] 検査器に互換モードを加える。宣言の読み方は spec の FR-004 のとおりにし、`tests/run-config-pyramid.sh` の関数 `declared_children` と同じ結果になるようにする
- [X] T018 [US3] T015 のテストが通ること、`python3 tools/refinement-checker/check_graph.py --skills-dir .claude/skills` が終了コード 0 を返すこと、`tests/run-config-pyramid.sh` が変更前と同じ57件で通ることを確かめる(Green、P1-11)。結果: 38件が通った(Python 3.14.3 と 3.9.6)。互換モードは、このワークツリーの `.claude/skills` と、生成された `speckit-*` を含む元のチェックアウトの `.claude/skills` の両方で違反なし。`run-config-pyramid` は57件が通った

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T019 [P] 例 `tools/refinement-checker/examples/requirements-graph.example.json` と `tools/refinement-checker/examples/skills-graph.example.json` を、spec の FR-009 のとおりに作る。受け入れテストに、2つが合格することを確かめるテストを先に書き、失敗を確かめてから作る。結果: 2件が失敗した後、例を置いて通った
- [X] T020 受け入れテストに、人が読む形式の出力で ID の中の改行と ESC がエスケープされること(spec の FR-013)と、同じ入力の2回の出力が一致すること(SC-003)のテストを先に書き、失敗を確かめてから検査器を直す。結果: エスケープは T008 でテストより先に実装していたため、このテストは実装の不足では失敗しなかった(TDD からの逸脱)。最初のテストは期待するエスケープの形を誤っており(理由の中の ID は JSON の形 `\n` でエスケープされる)、行頭の ID の経路を通るよう直した。エスケープを外した複製の検査器でこのテストが失敗することを確かめ、退行を検出できることを示した。決定性のテストは JSON と人が読む形式の両方で通った
- [X] T021 `.github/workflows/ci.yml` のジョブ `test` に、`bash tests/run-refinement-checker.sh` のステップを加える(spec の D9、SC-004)
- [X] T022 [P] 検査器の README を `tools/refinement-checker/README.md`(英語)と `tools/refinement-checker/README.ja.md`(日本語)に書く。同じ見出しの構成で、用途、実行主体、配布先、使い方、宣言の形式、規則、終了コード、限界を書く(spec の FR-011)
- [X] T023 `README.md` と `README.ja.md` の「What this provides」、ファイル構成の図、「Verification」、「Repository security automation」(CI の検査スクリプトの数を6から7に)の節を、変更後の内容に合わせる
- [X] T024 ネットワークを使わないローカルの検査をすべて実行し、spec の SC-002 の件数と比べる(P1-12)。あわせて `git diff --stat origin/main -- .claude install.sh tests/run-config-pyramid.sh` が空であることを確かめる(FR-012)。結果: SC-002 の件数と一致し、失敗はなかった(`run-digital-agency-slides-skill` の3件の省略は変更前と同じ)。`run-refinement-checker` は4件が通り、4件が `NOT RUN`。差分は空だった。`run-mcp-startup` はネットワークを要するため実行していない
- [X] T025 変更の差分を `/code-review` でレビューし、確かめた指摘を直す。指摘と対応を本ファイルに記録する。あわせて、検査器がファイルを開く呼び出しが読み取りだけで、ネットワーク・サブプロセス・動的なコードの評価(`eval`、`exec`、`pickle` など)を使わないことを、コードを読んで確かめる(FR-007)。結果: `/code-review`(労力 medium、`main...feat/refinement-graph-checker` のコミット a83e56b まで)は7件を指摘し、7件すべてを受け入れた。各指摘について回帰テストを先に書き、7件が失敗することを確かめてから直した(Red → Green、49件が通る)。

  | # | 指摘 | 対応 |
  |---|---|---|
  | 1 | 互換モードの S-10 が、存在しないスキルだけを宣言した子を親と数えない(spec 058 は数える) | 子の宣言の一覧(存在しない名前を含む)で判定するよう直した |
  | 2 | 重複した ID のノードを丸ごと捨てるため、その子が根に見えて S-11 が誤って出て、そのノード自身の違反も報告されない | 重複したノードも各欄の規則で検査し、子を同じ ID のエッジに加えるよう直した |
  | 3 | FIFO やデバイスでは大きさが 0 と報告され、5 MiB の上限を素通りして読み込みが止まるか、メモリを使い果たす | `O_NONBLOCK` で開き、開いたファイルが通常のファイルでなければ終了コード 2 にし、読み込みを上限+1バイトで打ち切るよう直した |
  | 4 | `--format json` でも、引数の誤りでは JSON の結果が出ない | 引数の解析の前に形式を読み、引数の誤りと検査器自身の異常でも JSON の結果を出すよう直した |
  | 5 | `children` の型の誤り1件が、S-04 と S-11 の違反も引き起こす | `children` が誤ったノードでは S-04・S-05 を、そのようなノードがあるグラフでは S-11 を判定しないよう直した(S-00 で不合格になる) |
  | 6 | 行頭の ID のバックスラッシュをエスケープしないため、エスケープの結果と、もとからある `\x0a` の文字列を見分けられない | バックスラッシュを `\\` にするよう直し、契約の記述(`\n` の例)を実装に合わせた |
  | 7 | 同じノードと規則の違反を理由の文字列で並べるため、`#10` が `#2` より前になる | 検出の順で並べるよう直した(research R4) |

  コードを読んだ確認: 検査器が開くのは入力のファイルと `SKILL.md` だけで、読み取り専用(`os.open` の `O_RDONLY`)である。`socket`、`urllib`、`subprocess`、`eval`、`exec`、`pickle` を使っていない
- [X] T026 README と PR に使う説明を、会話を見ていないサブエージェントに読ませ、指す先の分からない語を直す。結果: 検査器の README を会話を見ていない新しいサブエージェントに2回読ませた。1回目は13項目、2回目は9項目を挙げ、両方を直した。PR は作っていないため、PR の本文は読ませていない

## Dependencies & Execution Order

- T002 → T003・T004 → 各 User Story。User Story 1 の T008 が入力の読み込みと共通の判定(S-01〜S-03、S-08)を作るため、User Story 2 と 3 の実装(T013、T017)は T008 の後に行う。User Story 2 と 3 のテストの作成(T010、T011、T015)は、T004 の後ならいつでもよい。
- Phase 6 は、T019・T020 が User Story 1〜3 の後、T021〜T023 が T019 の後、T024〜T026 が最後である。

## Parallel Example

```text
# T004 の後、別のファイルなので並行できる:
T005 要求の論理グラフのフィクスチャ
T010 スキル合成グラフのフィクスチャ
# Phase 6:
T019 例の JSON と T022 検査器の README
```

## Implementation Strategy

User Story 1 だけで、要求の分解の構造の検査として使える最小の単位になる(spec の User Story 1 の Independent Test)。各 User Story の Green の後に commit と push を行い、途中の状態を残す。
