# Scrum の作成物

このフォルダは、1つのプロダクトの Scrum の作成物と、Sprint ごとの記録を置く。規範は Scrum Guide（2020年版）だけである。

## Scrum Guide が定めること

| 作成物 | コミットメント | ファイル | 責任を持つ人 |
| --- | --- | --- | --- |
| Product Backlog | Product Goal | [product-backlog.md](product-backlog.md) | Product Owner |
| Sprint Backlog | Sprint Goal | `sprints/<Sprint>/sprint-backlog.md` | Developers |
| Increment | Definition of Done | `sprints/<Sprint>/increment.md` と [definition-of-done.md](definition-of-done.md) | Scrum Team |

作成物とコミットメントの対応は `[SG20, p.10-12]` による。Product Backlog の内容と並び順は Product Owner が、Sprint Backlog は Developers が責任を持つ `[SG20, p.5-6, p.11]`。Sprint Goal は Scrum Team が Sprint Planning で定め `[SG20, p.8]`、Definition of Done は、組織の基準がなければ Scrum Team が作成する `[SG20, p.12]`。

### アカウンタビリティ

Scrum Team は、1人の Scrum Master、1人の Product Owner、Developers で構成される `[SG20, p.5]`。誰が担うかは、このチームが決めて書く。

- **Product Owner**：
- **Scrum Master**：
- **Developers**：

## このリポジトリでの運用上の決まり

Scrum Guide は、フォルダの構造もファイルの名前も道具も定めない。以下は、このフォルダの運用上の決まりである。

- `product-backlog.md` と `definition-of-done.md` は、このプロダクトに1つずつ置き、Sprint ごとに複製しない。
- Sprint ごとの記録は `sprints/<3桁の番号>-<Sprint の開始日 YYYY-MM-DD>/` に置く。
- Increment の実体はコードにある。`increment.md` には、Pull Request、リリース、コミットへのリンクを書く。
- 作業の単位（Issue、Pull Request）は、このフォルダに写さず、リンクで指す。
- Daily Scrum の記録を残すかどうかは、Developers が決める。

---

出典：_The Scrum Guide_（Ken Schwaber and Jeff Sutherland、2020年11月）<https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf> — `[SG20, p.5-6, p.8, p.10-12]`。ページ番号は英語版による。
