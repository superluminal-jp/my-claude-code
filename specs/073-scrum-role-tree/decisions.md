# 利用者が決めたこと（spec 073）

この変更のうち、実装者（Claude）ではなく利用者 Taiki Ogihara が決めたことを、日付と回答の文言とともに記録する。どれも 2026-11-15 の会話で、AskUserQuestion の選択肢を利用者が選んだものである。選択肢の文は、質問のときに示した文のとおりに写した。

| # | 問い | 利用者の回答（選んだ選択肢） | 記録した先 |
|---|---|---|---|
| D-1 | 「綺麗な木構造に再整理」の対象はどちらか | 「ハーネス自体を再編する」 | shared-understanding.md の「依頼」 |
| D-2 | 図を木にするとき、親子を決める基準はどれか | 「Scrum の役割」。メモ「Scrumの役割の下に 1 正しい作業を定める 2 統制の下で実行する 3 引き渡す といったさらなる構造を作って位置付ける」 | shared-understanding.md の「依頼」 |
| D-3 | 木を表す仕組み、形と名前の調整 | 「A. 現状スキルとして組まれているものも、エージェントとした方が適切なものがあれば変更してよい。エージェントをスキルに変えるのも許可。スキル・エージェントの名称や内容を一覧したときに役割や目的がわかりやすくなるよう適切に調整するのも良い。」 | requirements-graph.json の REQ-FORM の origin |
| D-4 | 問題文で合意してよいか | 「合意する」 | problem.md |
| D-5 | ADR に記録するか | 「書く (推奨)」 | requirements-graph.json の REQ-ADR の origin |
| D-6 | 役割の置き方（反証 CH-01、CH-05 を受けて） | 「Criterion above, artifacts under SM (Recommended)」 | problem-card.json の evidence、REQ-DECLARE の origin |
| D-7 | 標識が選ばれ方に与える影響の扱い（反証 CH-06 を受けて） | 「Tag at end, accept risk (Recommended)」。選択肢の文は「Put the tag at the end of the description so the phrases about when to use the skill stay first. Don't run the paid eval, and record the effect on selection as an unverified risk you accept.」 | problem-card.json の evidence、REQ-TAG の origin |
| D-8 | feat/scrum-role-tree にコミットしてよいか | 「Commit to the branch (Recommended)」 | このブランチのコミット |
| D-9 | 緩めた2つの検査を承認するか（保証レビュー2回目の AR-01、ゲートの A-06） | 「Approve both (Recommended)」。選択肢の文は「I'll record your name in approved_by for both test changes in the manifest, answer AR-01 as resolved, and the A-06 block is cleared.」。対象は、問いが示した次の2つである。(1) C-08 は、前付けの `role:` の行だけを廃止名の走査から外し、本文の同じ文字列はこれまでどおり拒む。(2) read-only-reviewer の前付けの検査（R1a）は `metadata` の欄を受け入れ、キーを role、branch、stage に限り、ほかのキーを拒む | verification-manifest.json の test_changes の approved_by |
| D-10 | いつ ~/.claude/ に入れるか（AC-AGENT-META-2 はデプロイの後にしか確かめられない） | 「After merging (Recommended)」。選択肢の文は「Same order as this repo's usual practice: decide the gate before deploy (pre_deploy), then do push, PR, and merge, then install.sh from main, then check /agents. This session ends with the result "may be deployed"; acceptance is decided after the check.」 | ゲートを --stage pre_deploy で判断する |
