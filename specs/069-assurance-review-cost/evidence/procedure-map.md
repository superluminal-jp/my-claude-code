# 対応表: spec 069 の4つの方策と、変更の前後の本文

この表は、利用者が読んで確かめる検査（`human_review`）の材料である。対象は R0-A4・RA-A2・RB-A2・RD-A2・RC-A1 の5件で、行ごとに対応する検査の id を書いた。各行には、変更の前（main b5363b4）の本文と、変更の後（reviewed_commit）の本文の場所と要旨を並べる。本文はスキルの中なので英語である。全文は `git diff b5363b4 <reviewed_commit> -- .claude/skills/verified-delivery` で読める。

略記: VD = `.claude/skills/verified-delivery/`

## 方策 A: レビュー役に読ませるものを絞る（RA-A2）

- **前**: VD `SKILL.md` の手順5は、レビュー役に「the requirements graph, the diff up to `reviewed_commit`, and the raw evidence」を渡すと書いた。`references/reviewer.md` は「the diff of the change up to reviewed_commit」を渡すと書いた。どちらも、記録の場所を外すことも、その回の証跡だけを渡すことも定めていなかった。
- **後**:
  - VD `SKILL.md:22`（手順5）は、`review_prep.py bundle` を走らせ、レビュー役に bundle のディレクトリだけを渡すと書く。会話や実装者の要約は渡さない。
  - VD `references/reviewer.md:15-22` は、bundle の8つのファイルを表で示す。`change.diff` は記録の場所のデータのファイルだけを外し、そこに置いたスクリプトは変更の一部として残す。`manifest.json` は verification manifest の全体（検査・リスクの分類・承認・テストと基盤の変更）で、「the implementer's claims, to check against the diff and the evidence」とする。
  - 1回目のプロンプト（`:26-` の text、とくに `:38` と `:44`）は、bundle を読ませる。bundle の外を読むのは、bundle では判断できないときだけで、読んだものを指摘に書かせる。
  - この直しは、1回目のレビュー（AR-01・AR-02・AR-06）を受けたものである。最初の bundle には manifest の検査しか入らず、証跡を作るスクリプトと CI のログも入らなかった。そのため、レビュー役はリポジトリの記録の場所を3回読んだ。
- **確かめてほしいこと**: 次の2つです。
  - レビュー役に、実装者の要約や説明を渡す道が残っていないか。manifest.json は主張として渡しています。
  - bundle の中身で、レビュー役が5種類の問題を判断できるか。

## 方策 B: すべての差分に戻すのは構造かリスクが変わったときだけ（RB-A2）

- **前**: VD `SKILL.md` の手順5と reviewer.md は、「the requirements graph or the risk class changed since the previous round」なら、すべての差分を読み直すと書いていた。文だけの直しも、これに当たった。
- **後**:
  - VD `references/reviewer.md:24` は、`--previous` が `fixes` にする条件を定める。graph が文の欄（要件の statement・assumptions・counterexamples、受け入れ条件の description、selection の条件の文）だけで変わり、problem card が変わらず、前の回の manifest とリスクの分類が同じとき、である。それ以外は `whole` にする。
  - VD `SKILL.md:22` は、`scope.json` に従って、プロンプトを選ばせる。
  - 2回目以降のプロンプト（`references/reviewer.md:88-` の text）は、4つを確かめさせる。3つ目（`:120`）は、graph.diff の文の変更が、確かめる内容を弱めていないかである。
- **確かめてほしいこと**: 次の2つです。
  - 文の欄の範囲（何を「言い回し」とみなすか）が広すぎないか。
  - 文の変更で受け入れ条件を弱める道を、差分の回のレビュー役が見る形になっているか。

## 方策 D: 機械的な確かめをレビューの前に（RD-A2）

- **前**: 手順5は、レビュー役を始める前に何も確かめさせなかった。gate は手順6で、レビューの後に初めて走った。
- **後**:
  - VD `SKILL.md:22`（手順5）は、各回の前に記録をコミットし、`review_prep.py check` と gate を走らせると書く。そして、このレビュー・人・CI を待つもの以外の理由をすべて直してから始める。
  - VD `references/reviewer.md:11` は、`check` が P-01〜P-03 で何を見つけるかを書く。P-02 は、審査対象のコミットの後に記録でないファイルが変わったときの違反である。記録とは、記録の場所のデータのファイルを指す。記録の場所に置いたスクリプトの変更と、記録の場所へ移したファイルも、この違反になる（1回目のレビューの AR-02・AR-05 への直し）。
  - VD `SKILL.md:23`（手順6）は、gate の前の確かめも `review_prep.py check` で行うと書く。
  - VD `references/manifest.md:15` は、git を読めない gate に代わって、`check` が記録の置き場所を確かめると書く。
- **確かめてほしいこと**: 「待つもの以外の理由を直してから始める」が、手順の流れの中で無理なく行えるか。

## CI の証跡: 審査対象のコミットを先に push する（RC-A1）

- **前**: 手順4は、CI のジョブを「its URL and the commit it ran on」で記録するとだけ書き、push の順序を書かなかった。
- **後**: VD `SKILL.md:21`（手順4）は、プロジェクトの CI が push か pull request で走るときの順序を書く。
  - 記録より先に `reviewed_commit` を push する。CI が pull request でだけ走るなら、先に PR を開く。
  - CI が終わるのを待ち、CI のジョブの証跡が `reviewed_commit` を指すようにする。
  - そのあとで記録をコミットし、レビューを受け、記録はレビューの後に push する（1回目のレビューの AR-03 への直し）。
  - 直しのコミットのたびに、同じ順で進める。
  - CI のジョブの結果の行は、URL とコミットと一緒に記録の場所のファイルに保存し、それを参照として引く（AR-06 への直し）。
- **確かめてほしいこと**: この順序が、手順5の「記録をコミットしてから check と gate」と食い違わないか。この変更自身は、その順で進めました。PR #124 を先に開き、ba76e65 を push し、CI を待ってから記録をコミットしています。直しのコミット 3d0a0e4 も、記録より先に push して CI を待っています。

## 4つの方策どうしの整合（R0-A4）

確かめてほしい組み合わせは次の3つです。

- **A と D**: `check` は記録をコミットしてから走り、bundle はその後に作る。そのため、bundle の `evidence/` は、コミットされた証跡の写しになる。
- **B と gate の A-10**: `fixes` の回でも、記録の `reviewed_commit` はその回に審査したコミットである。gate は最新の記録だけを読むので、A-10 は変わらず満たされる。
- **RC と D**: CI を待ってから記録をコミットし、その後で `check` と gate を走らせる。この順序で、CI のジョブの証跡が `reviewed_commit` を指したまま、レビューに入れる。
