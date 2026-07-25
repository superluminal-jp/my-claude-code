# スケーリングフレームワーク

## 目次

- [位置づけ](#位置づけ)
- [Nexus](#nexus)
- [LeSS](#less large-scale-scrum)
- [SAFe](#safe scaled-agile-framework)
- [スケーリングを勧めるときの進め方](#スケーリングを勧めるときの進め方)

## 位置づけ

Scrum Guide自体は指標にもスケーリングにも中立であり、意図的にベロシティ、ストーリーポイント、特定のスケーリングモデルを規定しない。以下はいずれもGuideの上に積み重なる実務であり、Scrum Guide自体の一部であるかのように語らない。それぞれ独自の統治ガイドを持つ別の実践体系として、出典を分けて引用する。

## Nexus

Scrum.orgによる公式のScrum拡張で、単一の**Product Backlog**から1つの**Integrated Increment**を毎Sprint届ける、およそ3〜9のScrum Teamを対象とする。参加チームから選出される（別の恒久チームではない）**Nexus Integration Team**を追加し、結合したIncrementが実際に統合されていることに責任を持たせる。加えて、チーム横断の依存関係を管理するため、Nexusレベルのイベント（Sprint Planning、Daily Scrum、Review、Retrospective）を設ける。Scrumへの変更を最小限にすることを明示的に意図している。出典：*The Nexus Guide*、Scrum.org。[NXG]

## LeSS（Large-Scale Scrum）

Craig LarmanとBas Voddeによるフレームワークで、役割を追加するのではなく組織的な複雑さを**取り除く**ことでScrumをスケールする——多数のチームにまたがる単一のProduct Backlog、単一のProduct Owner、単一のDefinition of Doneを保つ。非常に大きなプロダクトグループ向けの「LeSS Huge」派生形もある。追加構造を最小限にすることを重視し、思想的にはNexusに近いが、独立したガイダンス体系である。[LESS]

## SAFe（Scaled Agile Framework）

Scaled Agile, Inc.によるはるかに規定的なフレームワークで、複数のチームを固定ケイデンスの**Program Increment**を持つ**Agile Release Trains**にまとめ、追加の役割（Release Train Engineerなど）とポートフォリオレベルの構造を持つ。トップダウンの調整をより必要とする大企業で普及している。Scrumが最小化しようとしている階層を再導入しているとScrum純粋主義者から頻繁に批判されるが、これは片側に加担せず、根拠のある実際の論争として提示する。[SAFE]

## スケーリングを勧めるときの進め方

チーム数、実際に存在するチーム横断の依存関係の量、組織が構造変化に対してどれだけ意欲があるかを尋ねる（または文脈から推測する）。そのうえで、Nexus/LeSS（より軽量）とSAFe（より重く規定的）を、単一の正解としてではなく実際のトレードオフとして提示する。スケーリングフレームワークは調整の問題を解決するものであり、単一チームの不健全なScrum運用を修正するものではない——単一チームの問題はまずそちらを先に対処すべきである。
