# Problem Statement: 自作のスキルの手順と、実際に要った進め方が食い違い、レビューの指摘や手作業が増えた

**Status**: Complete
**Generated**: 2026-11-08

この問題文の対象は、このリポジトリの `.claude/skills/` のうち verified-delivery・requirements-decomposition・coder の3つのスキルと、その2つの検査器（`verified-delivery/scripts/assure.py`、`requirements-decomposition/scripts/check_graph.py`）である。問題文の本文は、利用者が会話に貼った振り返りの第4節（2026-11-08）による。

## 理想の状態

スキルの手順が、記録の置き方・証跡の形・レビューの範囲・deploy の前後の判定・red の取り方を前もって決めていて、レビューの指摘が変更そのものの問題に集中する。

## 現在の状態

3つのスキルで、手順に書かれていないことが要り、次のことが起きた（利用者の報告）。

| 行 | スキル | 手順と実際の食い違い | 起きたこと |
|---|---|---|---|
| 1 | verified-delivery | 検証の記録（manifest・証跡）は、審査したコミットの後の、記録だけのコミットでしか入れられないが、手順はそれを書いていない | 独立のレビュー（assurance review）が「記録が別のコミットを指す」と2回指摘した |
| 2 | verified-delivery | 証跡のファイルの拡張子を決めていない | 全体の gitignore の `*.log` に当たり、`.log` の証跡がコミットに入らず、後で `.txt` に直した |
| 3 | verified-delivery | 指摘を直した後のレビューも、毎回すべての差分を読み直す | 3回のレビューが、それぞれ約20万トークンを使った |
| 4 | verified-delivery | deploy の後でしか確かめられない検査も、deploy の前の gate の判定で、まだ通っていない検査として数える | deploy の前の gate の判定は必ず blocked になり、レビューカードで「deploy してよい状態」と「受け入れ済み」を見分けられなかった |
| 5 | verified-delivery | 試験の結果の取り込みは JUnit の形式だけを読む | jest の結果は JSON から手で記録に起こした |
| 6 | verified-delivery | 独立のレビューと批判の役の指摘を、記録に原文のまま写すよう求める | サブエージェントが英語で返した指摘の文が、日本語で書く記録とレビューカードにそのまま混ざった |
| 7 | requirements-decomposition | 要件がどこから来たか（問題の分析か、ユーザーの指示か）を書く欄が無い | ユーザーの指示で入れた要件も、批判の役に「手段を問題にしている」と指摘された |
| 8 | coder | 新しい関数の試験の red の取り方を決めていない | red が import の失敗にしかならず、レビューで指摘された。ミューテーション検査で補った |
| 9 | coder | spec-kit を使うリポジトリでは、spec-kit の手順に従うよう求める | verified-delivery の requirements graph と `spec.md` に、同じ受け入れ条件を2度書いた |

このリポジトリの main（9cd7932）で、各行の手順と検査器の穴を本文とコードで確かめた。行2・3・6 は、このリポジトリの spec 066 の記録にも現れている。7回目のレビューの AR-01（`.gitignore:74` の `*.log`）、10回のすべての `context_given` が `git diff main..<sha>` であること、指摘の文が英語で記録の他の欄が日本語であることである。行1・4・5・7・8・9 で起きたことの根拠は、利用者の報告だけである。spec 066 の10回目の AR-03（f9dbf00 でコミットした manifest が 2822abe を指す）は、間にコードの変更があったので正しい指摘で、行1の例ではない（批判の役の CH-03）。行9 は、このリポジトリでは起きていない（spec 066 は `spec.md` を書かなかった）。

## ギャップ

スキルの手順が、記録と証跡の扱い、deploy の前後の判定、red の取り方を決めておらず、その穴がレビューの指摘と手作業になって出た。

## 重要性

同じ穴は、次に同じスキルを使う案件でも同じ指摘と手作業を生む。レビューのトークンと時間が、変更の中身ではなく記録の形に使われる。

## Identified unverified cause (not part of the problem statement)

スキルは、このリポジトリの spec 059–066 の進め方から作られた。それらは deploy の無い、Python の試験の案件だったので、deploy のある案件や jest の案件で要る手順が抜けた。これは検証前の仮説である。

## 合意済みの決定（利用者の回答、2026-11-08）

- 行4: requirements graph の受け入れ条件に任意の `stage: "post_deploy"` を付ける。`gate --stage pre_deploy` はそれを除いて判定し、カードは deploy の前の判定と受け入れの判定を並べて出す。
- 行3: 2回目以降のレビューには、前回の記録と、前回審査したコミットからの差分を渡す。requirements graph か risk class が変わったときだけ、すべての差分を読み直す。
- 行9: 受け入れ条件の正本は requirements graph とし、`spec.md` は graph の受け入れ条件の id を引く。
- 行7: 要件に任意の `origin`（`{"kind": "instruction", "by", "ref"}`）を加え、批判の役はそれを与えられた制約として扱う。

行1・2・5・6・8 は、Claude が既定の直し方を示し、利用者は異を唱えなかった（2026-11-08）。
