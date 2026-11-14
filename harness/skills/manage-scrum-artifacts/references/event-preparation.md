# ファイルからイベントの準備をする

人に頼まれたとき、`scrum/` のファイルを読んで、Scrum Team が決めるための材料を下書きする。下書きは会話の中に出すか、「下書き（チームが決める）」と分かる見出しの下に書く。コミットメントの欄には書かず、Product Backlog の行を並べ替えない。

どの準備にも当てはまること:

- ファイルに書かれていることだけを事実として扱う。書かれていない実績、見積もり、反応を作らない。足りないものは「未確認」と書き、誰に尋ねれば分かるかを添える。
- 選択肢を示し、決定はしない。誰が決めるかを、下の表のとおり添える。
- Scrum Guide が述べていない進め方や技法を、Scrum の規則として書かない。

| 準備 | 読むファイル | 下書きするもの | 決める人（下書きしないもの） |
| --- | --- | --- | --- |
| Product Backlog のリファインメント | `product-backlog.md` | 曖昧な項目への問い、分割の案、依存関係 | 並び順は Product Owner [SG20, p.5-6]。大きさは作業を行う Developers [SG20, p.11] |
| Sprint Planning | `product-backlog.md`、`definition-of-done.md`、直前の Sprint のフォルダ | Sprint Goal の候補、選択の候補、作業の案 | Sprint Goal は Scrum Team、選択する項目と進め方は Developers [SG20, p.8] |
| Daily Scrum | 現在の Sprint の `sprint-backlog.md` | Sprint Goal への進捗を検査するための問い、計画を変える候補 | 計画の適応は Developers [SG20, p.9]。個人の状況報告を求める文にしない |
| Sprint Review | 現在の Sprint の `increment.md`、`sprint-backlog.md`、`product-backlog.md` | ステークホルダーに確かめること、Product Backlog を変える候補 | 次に何をするかは Scrum Team とステークホルダーが協働して決める [SG20, p.9]。Definition of Done を満たさない作業を Increment として書かない [SG20, p.12] |
| Sprint Retrospective | 現在の Sprint のフォルダ | 記録にある観察の整理、改善の候補 | 取り組む改善は Scrum Team [SG20, p.10]。記録にない原因を断定しない |

出典：_The Scrum Guide_（Ken Schwaber and Jeff Sutherland、2020年11月）<https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf>。ページ番号は英語版による。
