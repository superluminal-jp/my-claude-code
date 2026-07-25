# Scrumフレームワーク（Scrum Guide 2020）

## 目次

- [定義](#定義)
- [経験主義の三本柱](#経験主義の三本柱)
- [Scrumの5つの価値基準](#scrumの5つの価値基準)
- [Scrum Teamのアカウンタビリティ](#scrum-teamのアカウンタビリティ)
- [イベント](#イベント)
- [作成物とコミットメント](#作成物とコミットメント)
- [2020年版での変更点](#2020年版での変更点)

一次資料：*The Scrum Guide*（2020年11月版）、Ken Schwaber and Jeff Sutherland、scrumguides.org。Scrumの唯一の規範的な定義である。以下のタイムボックスと規則は、特記なき限りすべてこの資料に基づく。完全な出典は[sources.md](sources.md)を参照。

## 定義

Scrumは、複雑な問題に対する適応的な解決策を通じて人々・チーム・組織が価値を生み出すことを助ける軽量フレームワークである。方法論や技法の集合ではない。**経験主義**と**リーン思考**を基盤とし、意図的に「必要最小限」の構造だけを提供し、残りはチームに委ねる。[SG20, p.3]

## 経験主義の三本柱

1. **透明性**：プロセスと作業は、結果に責任を持つ人々に見える形でなければならない。
2. **検査**：作成物と目標に向けた進捗は、問題を検出できる頻度で検査されなければならない。
3. **適応**：検査によって逸脱が明らかになった場合、プロセスまたはプロダクトはできるだけ早く調整されなければならない。

[SG20, pp.3–4]

## Scrumの5つの価値基準

2016年にGuideへ追加され、2020年版でも維持されている：**確約（Commitment）、集中（Focus）、公開（Openness）、尊敬（Respect）、勇気（Courage）**。これらはイベントと作成物の使い方を通じて経験主義の三本柱を機能させる行動基盤である。[SG20, pp.4–5]

## Scrum Teamのアカウンタビリティ

2020年版は「役割（roles）」を意図的に**アカウンタビリティ**へ改称し、独立した「Development Team」というサブチームを廃止した。作業を行う全員が単一の**Scrum Team**の一員であり、自己管理する（who・how・whatの3つを自分たちで決める——「自己組織化」が対象としていたwho・howより広い権限）。[SG20, p.5]

- **Product Owner**：プロダクトとProduct Backlogの価値を最大化する責任を持つ。Product Goalの策定と伝達を含む。1名であり、委員会ではない（委員会の意向を代表することはある）。
- **Scrum Master**：Guideに定義されたScrumの確立と、Scrum Teamの有効性に責任を持つ。詳細は[scrum-master-role.md](scrum-master-role.md)。
- **Developers**：各Sprintで使用可能なIncrementのいかなる側面も作成することに献身する人々。Sprint Backlogと品質（クラフトマンシップ）に責任を持つ。

Scrum Teamは通常、機敏さを保てるほど小さく、かつSprint内で意味のある作業を完了できるほど大きい——慣習的には10人以下とされるが、2020年版のGuide自体は明確な人数を規定していない。[SG20, p.5]

## イベント

すべてタイムボックス化されている（1か月Sprintの場合）。

| イベント | 目的 | タイムボックス |
|---|---|---|
| **Sprint** | 他のすべてのイベントを包含する容器。アイデアを価値に変える | 1か月以内。前のSprint終了直後に次のSprintが始まる |
| **Sprint Planning** | Sprintの作業を計画する。Why（Sprint Goal）、What（対象のProduct Backlog items）、Howに答える | 最大8時間 |
| **Daily Scrum** | DevelopersがSprint Goalへの進捗を検査し、Sprint Backlogを適応する。翌日の実行可能な計画を作る | 15分、毎日同じ時間・場所 |
| **Sprint Review** | Incrementの成果をステークホルダーと検査し、Product Backlogを適応する。作業セッションであり、状況報告ではない | 最大4時間 |
| **Sprint Retrospective** | 品質と有効性を高める方法を計画する。人、相互作用、プロセス、ツール、Definition of Doneを検査する | 最大3時間 |

[SG20, pp.7–10] 短いSprintでは、通常イベントのタイムボックスも比例して短くする。Daily ScrumはDevelopersのためのイベントであり、POやScrum MasterがSprint Backlogの作業に実際に従事している場合は、監督者としてではなくDevelopersとして参加する。

## 作成物とコミットメント

2020年版は各作成物に明確な**コミットメント**を追加し、透明性と集中のための「北極星」を与えた。[SG20, pp.10–12]

| 作成物 | 内容 | コミットメント |
|---|---|---|
| **Product Backlog** | プロダクト改善に必要なすべてを含む創発的で順序付けられたリスト。継続的に洗練される | **Product Goal**——Scrum Teamが向かう将来的な目的 |
| **Sprint Backlog** | Sprint Goal + そのSprintで選択したProduct Backlog items + それらを届ける計画。全面的にDevelopersが所有する | **Sprint Goal**——Sprintの単一の目的。一貫性を与えつつ厳密なスコープには柔軟性を持たせる |
| **Increment** | Product Goalへの具体的な足がかり。使用可能でDefinition of Doneを満たさなければならない。1つのSprintで複数のIncrementを作れる | **Definition of Done**——プロダクトが満たすべき品質基準の正式な記述。組織的な定義がなければScrum Teamがプロダクトに適したものを作成する |

## 2020年版での変更点

チームが旧版のガイドや資料を参照している場合に有用。[SG20, p.13]

- 「Development Team」という役割を単一の**Scrum Team**へ統合。**自己組織化 → 自己管理**（who/howだけでなくwhatも含む）。
- Sprint Goal、Product Goal、Definition of Doneを各作成物への**コミットメント**として明文化（以前は暗黙的だった）。
- Daily Scrumの「3つの質問」形式を必須要件から削除。Sprint Goalに資する限り、Developers自身が構造を選ぶ。
- Scrum Masterを、以前の「サーバント・リーダー」という表現より明示的に、Scrum Teamと組織のための「真のリーダー」として記述（奉仕してから導くという精神自体は変わっていない）。
- Guideは約13ページに短縮され、IT/ソフトウェア固有の表現が取り除かれた。ソフトウェアに限らず複雑な作業全般で使えるフレームワークとして位置づけている。
- Scrumを部分的にしか実施しないことは可能だが、その結果はScrumではない。[SG20, p.13]
