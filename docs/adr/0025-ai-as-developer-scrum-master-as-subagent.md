---
status: Proposed
date: 2026-11-14
deciders: 利用者（このリポジトリの保守者）
---

# 0025. AI を Scrum Team の Developers の一人として働かせ、Scrum Master は独立したサブエージェントに担わせる

## コンテキストと問題

変更の前、`apply-scrum-guide` は、Scrum Master の立場から人のチームの Scrum を診断し、改善を提案する読み取り専用のスキルだった。使われるのは、依頼が Scrum のイベント、作成物、アカウンタビリティに触れるときだけだった。[ADR-0023](0023-keep-scrum-artifacts-in-the-product-repository.md) は、作成物を書く `manage-scrum-artifacts` を別に加え、`apply-scrum-guide` を「読み取り専用の診断のまま残す」と決めていた。

このため、`manage-scrum-artifacts` が Product Goal、Sprint Backlog、Definition of Done をリポジトリに置いても、そのリポジトリで開発する AI に、それらを読むこと、作業を Sprint Goal に結び付けること、Definition of Done を完了の条件にすることを指示するものがなかった。依頼に Scrum という語がなければ、`apply-scrum-guide` も読み込まれなかった。

利用者は 2026-11-14 に、`apply-scrum-guide` について「レポジトリ内にAIが開発者として利活用することを前提に。AIエージェントに対して利活用するように指示。」と求めた。

## 決定

利用者は、3つの問いに次のとおり答えた。

- **役割**: 「開発する際に開発者としてとスクラムマスターとしての役割を独立したエージェントとしてそれぞれの役割を果たす。」
- **いつ使うか**: Scrum の作成物があるリポジトリでは、依頼に Scrum という語がなくても、開発のたびに使う。使う条件はスキルの `description` に書く。[ADR-0015](0015-rule-layer-independence.md) により、`CLAUDE.md`、ルール、エージェントの定義はスキルを名指さないためである。
- **書き込み**: スキルは読み取り専用のまま。Sprint Backlog の計画や進捗の変更は、記録する文面の案として人に示す。

次の点は、利用者の決定から実装者が導いた。利用者の確認はまだ受けていない。

- **主の会話が Developer、Scrum Master はサブエージェント `scrum-master-agent` とする。** サブエージェントは別のサブエージェントを起動できない。また `harness/CLAUDE.md` は、判断と完了の判定をメインの会話に残すと定めている。定義は sonnet、effort xhigh、道具は Read・Grep・Glob だけで、`CLAUDE.md` を読み込まない。名前を `scrum-master` にしないのは、それが廃止したスキルの名前で、スキルの契約 C-08 がその名指しを拒むからである。
- **Scrum Master を起動するのは3つの場合に限る。** 1つ目は、ファイルを変えた作業を完了と報告する前の1回である。2つ目は、Developers だけでは除けない阻害要因、Sprint Goal を危うくする見込み、Definition of Done を満たせない見込みに気づいたとき。3つ目は、Scrum の診断や改善を求められたときである。振る舞いを変えない小さな変更（誤字、書式、コメント）は、Sprint Backlog の項目の進捗や完了を主張しない限り起動せず、その理由を報告に書く。所見に対応してファイルを変えたら完了の判定をやり直す。同じ作業のために Scrum Master を再び起動はしない。
- **サブエージェントに渡すのは事実であり、Developer の結論ではない。** 作成物のパス、変えたファイル、変更の一覧、検査のコマンドと終了コード、依頼の原文を渡す。
- **サブエージェントを起動できない環境では、主の会話が自分で同じ問いを検査する。** その結果は「独立した Scrum Master の所見ではない自己点検」と明記する。Claude.ai に上げた写しでも使えるようにするためである。
- **チームの記録が人を Scrum Master として挙げていても、サブエージェントは起動する。** 所見はその人への材料とし、決定はその人に委ねる。記録の Scrum Master の欄が空でも、AI はその欄を埋めない。
- **Sprint の記録がなくても作業は止めない。** Sprint Goal、選択した項目、Definition of Done が空のときも同じで、透明性の欠けとして報告する。現在の Sprint は、開始日が最も新しい Sprint の記録とする。
- **従来の診断の手順は、サブエージェントが従う手順として残す。** 置き場所は `references/scrum-master-diagnosis.md` である。

## 検討した選択肢

- **今の診断の手順に Developer の節を足す**: 変更は小さい。Scrum Master と Developer の2つの立場が1つの会話に同居し、自分の作業を自分で検査することになる。利用者は、独立したエージェントに分けることを選んだ。
- **Developer もサブエージェントにする**: 2つの役を対称に扱える。ただし、サブエージェントは別のサブエージェントを起動できないので、主の会話が両方を取りまとめることになる。そのうえ、判断と完了の判定をサブエージェントに移すことになり、`harness/CLAUDE.md` の委任の方針に反する。
- **既存の `read-only-reviewer` を Scrum Master に使う**: 定義は増えない。ただし、その定義は要件の反証役と保証レビューのためのもので、Scrum Master の責任と境界を持たない。
- **従来どおり、Scrum に触れる依頼だけで使う**: 読み込まれるセッションは増えない。普通の開発の依頼では作成物が読まれず、利用者の求めを満たさない。
- **`harness/CLAUDE.md` にも、このスキルを使うよう書く**: 読み込まれる確度は上がる。[ADR-0015](0015-rule-layer-independence.md) の、頂点がスキルを名指さないという決定を変える必要がある。利用者は `description` だけを選んだ。
- **Developer である AI が、計画と進捗を Sprint Backlog に書く**: Scrum Guide の「Developers による、Developers のための計画」に近い。一方で、`manage-scrum-artifacts` の「人がチームの決定として示した値だけを書く」と食い違う。利用者は読み取り専用を選んだ。
- **ファイルを変えるたびに必ず Scrum Master を起動する**: 漏れはない。誤字1つの修正にも sonnet・xhigh のサブエージェントを起動することになり、`harness/CLAUDE.md` の、手順を影響に比例させるという方針に反する。
- **サブエージェントを起動できないときは止まる**: 独立性は崩れない。この挙動は `specify-requirements` と同じである。Claude.ai に上げた写しでは診断にも使えなくなるので、`apply-secure-logging` と同じく、自己点検と明記して続ける方を採った。

## 結果

- Scrum の作成物があるリポジトリでは、開発のたびにこのスキルが読み込まれる。このリポジトリのルートにある `scrum/` も対象になる。ファイルを変えた作業ごとに、サブエージェントの実行が1回増える。
- サブエージェントの定義は4件から5件になる。両方の README、`docs/claude-config-design.md`、`docs/harness-eval.md`、`claude-ai-system-prompt.md`、`chatgpt-system-prompt.md`、評価の対応表とシナリオ集を更新した。
- [ADR-0023](0023-keep-scrum-artifacts-in-the-product-repository.md) のうち、`apply-scrum-guide` を読み取り専用に保つ点は変わらない。スキルの役割を Scrum Master の立場からの診断とする点は、この記録が置き換える。ADR-0023 自体は書き換えない。
- `install.sh` を次に実行するまで、`~/.claude/` には反映されない。Claude.ai に上げた写しは、作り直して上げ直すまで古いままである。
- 評価は `Agent` の道具を許していない。このため、主の会話が `scrum-master-agent` を起動することは評価で観測できない。評価で観測できるのは、スキルが選ばれることだけである。

## 確認方法

- `bash tests/run-verify-change-skill.sh` が `tests/assert_reviewer_agent.py` を走らせる。このスクリプトは2点を確かめる。`scrum-master-agent` の定義が sonnet・xhigh・Read/Grep/Glob・`CLAUDE.md` なしであること。`apply-scrum-guide` の `SKILL.md` がそれを名指していること。
- `bash tests/run-harness-skills.sh` が、17スキルの契約を通す。
- `bash tests/run-harness-eval.sh` が、対応表に `scrum-master-agent` があること、シナリオ `e-scrum-developer-work` の根拠の語句が `SKILL.md` にあることを確かめる。
- `bash tests/run-readme-skill-index.sh` が、両方の README が新しい定義を名指すことを確かめる。
- まだ測っていないことが2つある。1つは、Scrum という語のない開発の依頼（`e-scrum-developer-work`）でこのスキルが選ばれるかで、モデルを呼ぶ有料の評価 `python3 tests/harness-eval/harness_eval.py run` で測る。もう1つは、主の会話が実際に `scrum-master-agent` を起動するかである。

## 補足情報

- [ADR-0015](0015-rule-layer-independence.md): 設定の層が互いを名指さない決まり。
- [ADR-0023](0023-keep-scrum-artifacts-in-the-product-repository.md): 作成物を書くスキルを分け、`apply-scrum-guide` を読み取り専用に保った決定。
- _The Scrum Guide_（Ken Schwaber and Jeff Sutherland、2020年11月）<https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf>。Developers の責任は p.5、Scrum Master の責任は pp.6-7、Sprint の規則は p.7、進め方が Developers の裁量であることは p.8、Definition of Done は p.12 にある。
