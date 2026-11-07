# 対応表: 第4節の9行と、変更の前後の本文

この表は、利用者が読んで確かめる検査（`human_review`）の材料である。対象は R0-A2・R1-A1・R2-A1・R3-A1・R4d-A1・R5-A2・R6-A1・R7-A2・R8-A1・R9-A1 で、行ごとに対応する検査の id を書いた。各行には、変更の前（main 9cd7932）の本文と、変更の後（直しのコミット）の本文の場所と要旨を並べる。本文はスキルの中なので英語である。全文は `git diff 9cd7932 <reviewed_commit> -- .claude/skills` で読める。

略記:

- VD = `.claude/skills/verified-delivery/`
- RD = `.claude/skills/requirements-decomposition/`
- coder = `.claude/skills/coder/SKILL.md`

## 行1 記録をどのコミットに入れるか（R1-A1）

- **前**: VD `SKILL.md` の手順4は「Set `reviewed_commit` to the commit under review」とだけ書き、記録をどのコミットに入れるかを書いていない。`references/reviewer.md` のプロンプトも、記録のコミットに触れていない。
- **後**:
  - VD `SKILL.md:21`（手順4）は、変更を先にコミットしてそれを `reviewed_commit` にすると書く。記録は1つの記録の場所に置く。実装の前に書く記録（problem card・graph・challenge report）とその直しは、変更と一緒に入れる。`reviewed_commit` を指す記録（manifest・証跡・レビューの記録・カード）は、その外を変えない後のコミットにだけ入れる。理由は「a commit cannot contain its own SHA」である（2回目のレビューの AR-03 への直し）。
  - VD `SKILL.md:23`（手順6）は、gate の前に `git diff --name-only <reviewed_commit> HEAD` が記録の場所のファイルだけを示すことを確かめる、と書く。
  - VD `references/reviewer.md:15-22`（1回目）と `:75-77`（2回目以降）は、`reviewed_commit` を指す記録が前のコミットを指すのは正しいと伝える。指摘させるのは、証跡が `reviewed_commit` 以外を指すとき、または後のコミットが記録の場所の外を変えるときだけである。
  - VD `references/manifest.md:15` は、検査器が git を読めないので、これが手順の側の確かめであることを書く。

## 行2 証跡のファイル名（R2-A1）

- **前**: 証跡のファイル名・拡張子の定めは無い。
- **後**: VD `SKILL.md:21`（手順4）は、生の証跡を記録の場所に `.txt` か道具の形式（`.xml`・`.json`）で置くと書く。また、記録のコミットの前に `git check-ignore -v` が何も出さないこと、後に `git ls-files --error-unmatch` が manifest の引くすべての証跡を示すことを確かめる、と書く。

## 行3 直しの後のレビューの範囲（R3-A1）

- **前**: VD `SKILL.md` の手順5は「run the review again for that commit」と書き、`references/reviewer.md` は「the diff of the change up to reviewed_commit」を渡すと書く。
- **後**:
  - VD `SKILL.md:22`（手順5）は、直しのコミットを2回目以降のプロンプトでレビューすると書く。渡すのは、前回のレビューの記録と、前回審査したコミットからの差分だけである。requirements graph か risk class が前回から変わったときは、すべての差分を読み直す。回ごとの記録を残し、gate には最新の記録を渡す。
  - VD `references/reviewer.md:58-96`（Later rounds）は、2回目以降のプロンプトを持つ。前回の resolution は実装者の主張として渡し、事実として扱わない。見るのは (1) accepted の指摘が本当に直ったか、(2) 直しの差分の5種類の問題、の2つである。範囲は `context_given` に書く。

## 行4 deploy の前後の判定（R4d-A1）

- **前**: 受け入れ条件に段階の欄が無く、gate は not_run をすべて A-03 で blocked にする。
- **後**:
  - RD `SKILL.md:15`（手順2）は、deploy の後でしか確かめられない条件に `"stage": "post_deploy"` を付けると書く。決めるのは分解の段階（批判の役が見る）で、もっと早く確かめられる条件を移してはならない。各要件と各親の固有の水準に、deploy の前に確かめられる条件を1つは持たせる。
  - VD `SKILL.md:23`（手順6）は、deploy の前は `--stage pre_deploy` で判定すると書く。除いた結果、deploy の前に何も確かめられない要件や、固有の `L2`・`L3` が確かめられない親は止まる（1回目のレビューの AR-01 への直し）。その `pass` は deploy してよいことで、受け入れではない。deploy の後は、残りの検査を記録して `--stage` なしで受け入れを判定する。また、gate を通すためだけに stage を変えることを禁じる。
  - VD `SKILL.md:24`（手順7）は、カードが2つの判定を示すと書く。
  - RD `references/checker.md:40,70` と VD `references/manifest.md:44-46,89` は、欄と規則（S-07、`stage`・`left_out`、カードの表示）を書く。

## 行5 jest の結果の取り込み（R5-A2）

- **前**: 取り込みは `collect-junit`（JUnit XML）だけである。
- **後**:
  - VD `SKILL.md:21`（手順4）は、`jest --json` の出力には同じ引数の `collect-jest` を使うと書く。
  - VD `references/manifest.md:7-11` は命令を、`:95-97`（Jest JSON）は使い方と限界を書く。限界は次のとおりである。
    - 実行できなかったファイルや中断された実行では、合格を出さない。
    - 読むのは Jest の型の欄だけである。
    - Vitest の互換は試験していない。

## 行6 指摘の言語（R6-A1）

- **前**: 2つのプロンプトは英語で、statement の言語を指定しない。challenger.md は「unchanged except for the two paths」で渡すと書く。
- **後**:
  - VD `references/reviewer.md:41,91` と RD `references/challenger.md:40` は、プロンプトに「every statement written in <language of the records>」を持つ。RD `references/challenger.md:3` は、渡すとき変えてよいものに言語を加える。
  - VD `SKILL.md:22`（手順5）と RD `SKILL.md:16`（手順3）は、記録の言語を渡し、返った指摘を「as they are」写すと書く。

## 行7 要件の出所（R7-A2）

- **前**: 要件に出所の欄が無く、challenger のプロンプトは指示の要件も solution_as_problem として見る。
- **後**:
  - RD `SKILL.md:15`（手順2）は、人の指示で入れた要件にだけ `origin` を書くと定める。自分で導いた要件には付けず、`by` にエージェントを書かない。`ref` には指示を読める場所を書く。
  - RD `references/challenger.md:15-21` は、origin が instruction の要件を与えられた制約として扱わせる。指摘させるのは、ギャップか他の要件と矛盾するとき、`ref` が人の指示を特定しないとき、`by` が人でないときだけである。
  - RD `references/checker.md:40,63` は欄と S-00 を書く。VD `references/manifest.md:89` は、カードが by と ref を示すと書く。

## 行8 新しい関数の red（R8-A1）

- **前**: coder の TDD 節は「run it to observe the expected failure」とだけ書く。
- **後**:
  - coder `SKILL.md:18` は、red を、新しい検査がその assertion で失敗することと定める。まだ無い関数・モジュール・エンドポイント・オプションは、最終形のシグネチャで型の合った誤った結果を返すスタブを先に足してから、assertion の失敗を見る。import・名前・コンパイル・使い方の誤りや、スタブが投げる例外は red ではない。壊れた検査と見分けられないためである（2回目のレビューの AR-02 への直し）。変更の前に assertion で失敗させられない検査は、実装をわざと壊して失敗を見て、元に戻す（ミューテーション検査）。
  - coder `SKILL.md:41`（変更の手順3）は、この節を引く。
  - この変更自身もこれに従った（`mutations.txt`。新しい試験のすべてが、red かミューテーション検査で assertion の失敗になり、error は0）。

## 行9 受け入れ条件の正本（R9-A1）

- **前**: coder の SDD 節は、spec-kit を使うプロジェクトでは spec-kit の手順に従うとだけ書く。VD と RD は spec.md との関係を書かない。
- **後**:
  - VD `SKILL.md:19`（手順2）と RD `SKILL.md:15`（手順2）は、受け入れ条件を graph にだけ書き、spec（spec-kit の `spec.md` など）は graph の受け入れ条件の id を引く、と同じ言葉で書く。
  - coder `SKILL.md:33` は、spec-kit の手順に従う文に「One exception」を続ける。受け入れ条件を検査器で判定する要求グラフがある変更では、そのグラフが受け入れ条件の唯一の源で、`spec.md` はその id を引く。それ以外の手順は変わらない。ほかのスキルを名前で呼ばない（SKILL-05 は合格。名前の参照を見つける側の PARENT-02〜09 も合格した、サンドボックスの外の実行。`config-pyramid.txt`）。

## 行どうしの整合（R0-A2）

確かめてほしい組み合わせは次の3つである。

- **記録だけのコミット（行1）と A-02**: 証跡の commit は `reviewed_commit` と同じで、記録はその後のコミットに入るので、A-02 の「古い証拠」にはならない。
- **差分のレビュー（行3）と A-10**: 2回目以降の記録も、その回に審査したコミットを `reviewed_commit` に書く。そのため A-10 の「審査したコミットのレビュー」を満たす。
- **deploy の前の判定（行4）と受け入れ**: `--stage pre_deploy` の `pass` は受け入れではない。カードの最上段の判定は、受け入れの判定のままである。
