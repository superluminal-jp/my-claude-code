# Scrum Master の所見と、Developer の対応（spec 073）

`scrum-master-agent` サブエージェント（2026-11-15）に、`apply-scrum-guide` の4つの問いで、完了を報告する前の検査を頼んだ。渡したのは事実だけで、次のとおりである。

- 依頼の原文
- `git diff --stat main..c90a58a`
- 検査の終了コード
- 利用者の決定（decisions.md）
- 作成物のパス

所見は、要約せずに項目ごとに残す。Developers のアカウンタビリティ（計画、Definition of Done による品質、計画の適応）に当たるものには Developer が対応した。それ以外は、決める人とともに利用者に示す。同じ作業のために Scrum Master を再び起動はしない。

## Scrum Master の結論（そのまま）

1. 作業は Sprint Goal と Sprint Backlog に結び付いていない。Sprint の記録も、Sprint Goal も、選ばれた Product Backlog の項目もない。そのため「Sprint Goal を危うくしていない」とは言えず、判定は未確認である。危うくしている証拠も見つからない。
2. Definition of Done の項目が 0 件なので、項目ごとの「満たした」は1つも言えない（全部未確認）。
3. 透明性の欠けは、作業の内側ではなく上位の作成物にある。作業の内側（利用者の決定、独立した反証、レビュー3回、緩めた検査の承認、環境で失敗した検査の理由）は spec 073 に残っていて、透明に保たれている。
4. Developers だけでは除けない阻害要因が3つある。空のコミットメント、サンドボックスで動かない `run-mcp-startup.sh`、デプロイの後にしか確かめられない AC-AGENT-META-2。

## 所見と対応

| 所見 | 種別 | 要点 | 決める人 | 対応 |
|---|---|---|---|---|
| F-1 | 透明性の欠け | 作業が Sprint と Product Backlog の項目に結び付かない（`scrum/product-backlog.md`:5 と :13-15 が空、`scrum/sprints/` がない） | Product Goal と Product Backlog は Product Owner、Sprint Goal は Scrum Team | 利用者に示す。Developer は埋めない |
| F-2 | 透明性の欠け | Definition of Done が空で、完了の判定に共通の物差しがない（`scrum/definition-of-done.md`:5） | 組織の標準、なければ Scrum Team | 利用者に示す。Developer の判定は「Definition of Done の項目がないので未確認」とした。項目の候補として、所見は次の3つを挙げた。CI の実行スクリプトの結果、独立した保証レビューの所見への回答、検査を緩めるときの Product Owner の承認 |
| F-3 | 透明性の欠け | Scrum Team の担い手の欄が空（`scrum/README.md`:19-21） | Scrum Team | 利用者に示す。Developer は埋めない |
| F-4 | 改善 | 役割の木の基準が Scrum Guide の定めと読めうる（`docs/harness/skill-map/03-role-tree.md`:3）。`shared-understanding.md` は、Definition of Done を埋めることを「Product Owner の決定」と書いていた | 利用者 | 後者は事実の誤りなので、Developer が `shared-understanding.md` を直した（記録だけの変更）。03-role-tree.md に「この基準はこのリポジトリの取り決めで、Guide の定めではない」と書き足すかは、利用者に示す。書き足すと、変更のコミットが新しくなり、保証レビューがもう1回要る |
| F-5 | 阻害要因 | `run-mcp-startup.sh` がサンドボックスで動かない（`evidence/c90a58a/ci/16-run-mcp-startup.txt`） | 利用者 | 利用者に示す。push の後の GitHub の CI か、サンドボックスの外での実行で結果を得られる |
| F-6 | 阻害要因 | AC-AGENT-META-2 はデプロイの後にしか確かめられない | 利用者（順序は D-10 で決定済み） | 利用者に示す。merge と install.sh の後に /agents を確かめ、結果を manifest に記録してゲートをやり直す |
| F-7 | 透明性の欠け | ゲートの状態とレビューカードの読みやすさ。依頼の事実（A-10 が残り、3回目を実行中）とカードが食い違う。緩めた検査とその承認がカードに出ない | ゲートとカードは Developers、カードの設計は利用者 | 食い違いは、検査を頼んだ時点の事実が古くなったためである。Developer は、3回目のレビュー（所見なし）を記録した後でゲートをやり直した。--stage pre_deploy では pass で、残るのは AC-AGENT-META-2 だけである。カードも作り直した（review-card.md）。緩めた検査をカードに載せるかは、verify-change のカードの設計として利用者に示す |
| F-8 | 改善 | 標識の影響が未測定のまま、気づく手がない | Product Owner（利用者） | 利用者に示す。戻すときの兆候と戻し方を、Pull Request か ADR に1〜2行書くかを決める |

## Definition of Done に照らした完了の判定（apply-scrum-guide の手順6）

- `scrum/definition-of-done.md` に項目がない。そのため、項目ごとの判定は「満たした」「満たしていない」のどちらも言えず、すべて未確認である。この作業は、Definition of Done の上では Increment と言えない [SG20, p.12]。
- 変更ごとの受け入れ基準（requirements-graph.json）では、ゲートが --stage pre_deploy で pass を出した。これは Definition of Done の判定ではない。
