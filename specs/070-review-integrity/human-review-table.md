# spec 070 の対応表（人の確認用、reviewed_commit f05ce79）

各行の受け入れ条件を、右の列の場所の文と突き合わせて確かめてください。行番号は `f05ce79` のものです。手順の本文は英語です。

| 行 | 受け入れ条件 | 確かめる場所 | 確かめること |
|---|---|---|---|
| 1 | R1b-A2 | `.claude/skills/requirements-decomposition/SKILL.md:16`、`references/challenger.md:3` と `:62`、`.claude/skills/verified-delivery/SKILL.md:22`、`references/reviewer.md:26`・`:30`・`:97`・`:101` | `read-only-reviewer` で起動する（プラグインでは接頭辞付き）。その型が無ければ別の型で代えずに止まり、人に伝える。reviewer の欄に、型、agentId、日付、読んだファイルの数を書く |
| 2 | R1c-A2 | `README.md:66`・`:152-157`・`:236-242`・`:284-285`、`README.ja.md:45`・`:100`・`:176-182`・`:224-225`（`tests/run-readme-skill-index.sh` は合格） | `agents/` に `read-only-reviewer.md` があること、`~/.claude/agents/` を置き換えること、スキルが agents の定義を名前で名指してよいことを、英語と日本語の両方で書いている |
| 3 | R1e-A1 | `references/reviewer.md:26`（資料の説明）、`:37-39` と `:48-53`（1回目のプロンプト）、`:108-110` と `:118-123`（2回目以降のプロンプト） | レビュー役はコマンドもスクリプトも実行できない。作業ツリーの記録の場所の外のファイルは reviewed_commit と同じ。足りない版や出力は、NOT REVIEWED ではなく指摘として報告させる |
| 4 | R2-A1 | `requirements-decomposition/SKILL.md:16`、`references/challenger.md:43-62`、`verified-delivery/SKILL.md:22`、`references/reviewer.md:37-39`・`:78-97`・`:108-110`・`:148-154`、`references/checker.md:48`、`references/manifest.md:83` | 答えに `read` を含めさせる。エラー・停止・時間切れ・`NOT REVIEWED`・JSON でない答え・渡したファイルを `read` に挙げない答えを、レビューしていないとする。1回だけやり直し、駄目なら記録を書かずに止まって人に伝える。空の findings は、ファイルを読んで指摘が無かったときだけ。assurance review のプロンプトは、名指したファイルをそれぞれ全部読み、evidence/ の中は要るものだけ読むと書く（f05ce79）。2つのスキルで同じ規則 |
| 5 | R3-A1 | `requirements-decomposition/SKILL.md:16`、`verified-delivery/SKILL.md:22`、`references/reviewer.md:97` | 却下の理由は2つの形だけ。読めるファイルと行（challenger では problem card か graph、assurance review では bundle かリポジトリのコミット済みのファイル）か、人に尋ねて得た決定（誰が、いつ、答えの言葉） |
| 6 | R3-A2 | 同じ2つの手順の文 | 読めない事実は、読めるファイルに書いて引くか人に尋ねる。人がまだ答えていない決定を書かない。却下したい気持ちは証拠でない |
| 7 | R3-A3 | `references/reviewer.md:134-140` | 2回目以降のレビュー役に、読めるものも人の決定も引かない却下を報告させる |
| 8 | R4-A1 | `verified-delivery/SKILL.md:22`（手順5の終わり）と `:26` | 6回目の前とその後5回ごと、往復の指摘のときに、3つの選択肢（もう1回、残る指摘を人が決める、手順2に戻る）で尋ねる。回は書いた記録で数え、レビューしなかった回は数えない。往復の判断は主のモデルがし、前の指摘の id を resolution に書き、迷えば尋ねる |
| 9 | R0-A2 | ほかの行（1〜8、10、11）のすべてと `.claude/agents/read-only-reviewer.md` | G1〜G4 がそれぞれ閉じていて、2つのスキルが同じ規則（型、失敗の扱い、却下の根拠）を書いている |
| 10 | R1a-A1 | `.claude/agents/read-only-reviewer.md:3`（description）。試験 `tests/assert_reviewer_agent.py` は合格（`evidence/f05ce79/reviewer-agent.txt`） | description が、手順がこの型を名指したときにだけ起動すると書いている |
| 11 | R1d-A2 | `docs/harness-eval.md:3`（導入）と `:74`（§4 の9）。`tests/run-harness-eval.sh` は合格（`evidence/f05ce79/harness-eval.txt`） | 評価ではこの型がプラグインの接頭辞の付いた名前（`harness:read-only-reviewer`）になること、プラグインの定義で omitClaudeMd と tools が効くことは確かめていないことを書いている |

## 承認が要る試験の置き換え（gate の A-06）

| 試験 | 置き換えた理由 | 置き換えた先 |
|---|---|---|
| `tests/harness-eval/test_harness_eval.py::ReviewRound7::test_a_harness_with_a_mapped_agent_stops_the_build`（消した） | ハーネスの評価の組み立てが、agents を止めずにプラグインに写すように変わったため、「止まる」ことを確かめる試験は成り立たなくなった | `test_a_harness_with_a_mapped_agent_builds_it_into_the_plugin`（写った中身が同じことを確かめる）、`test_an_agent_the_map_leaves_out_of_the_eval_stops_the_build`（評価から外す agents は止める） |
| `tests/run-install.sh` の `assert_absent "$TARGET/agents" "absent managed agents are removed"`（消した） | `.claude/agents/` に中身ができ、install は `~/.claude/agents/` を空にせず、リポジトリと同じにするようになった | `agents directory matches the repository`（`diff -r` で同じこと）と `an agent file removed from the repository is removed`。install.sh から agents を外すと落ちることを確かめた（`evidence/mutation-install.txt`） |

このほか、`test_a_harness_with_a_mapped_command_stops_the_build` の `assertRaisesRegex` の文を「agents and commands」から「has commands, which the eval does not build」に変えました。エラーの文が変わったためで、commands で組み立てが止まることを確かめる点は同じです。
