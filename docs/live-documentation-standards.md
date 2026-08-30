# Live Documentation — 準拠標準と設計論拠

このリポジトリのドキュメンテーション規則は `.claude/rules/live-documentation.md` にある。そちらが**規範**（何をすれば違反にならないか）で、本書はその**論拠**（なぜその形なのか、どの標準に依拠しているか）である。

本書は `.claude/rules/` の外に置かれている。同ディレクトリ配下の `.md` は Claude Code が再帰的にすべて自動ロードするため、参照資料をそこに置くと全セッションのコンテキストを消費してしまう。判断を下すのに必要なのは規範だけで、論拠は必要になったときに人が読めばよい。

読む順序: 規則本体を先に読み、そこに書かれた判断が「なぜそう決まっているのか」を知りたくなったときに本書へ来る。本書は規則本体の用語（Documentation Artifact、粒度層、圧縮要約）を既知として扱う。

---

## 1. ライフサイクル全体にわたる文書化標準

規則本体の §§ 1–7 は「作業中」の局面だけを操作可能な形にしたものである。実際には文書化の作法は作業前・作業中・全体にわたって存在し、ソフトウェア工学とプロジェクトマネジメントの両分野に確立された標準がある。以下はそれぞれの局面で参照すべき標準の一覧である。

名前の付いた実践から逸脱すること自体は問題ない。逸脱するなら理由を述べる（`.claude/CLAUDE.md` の Grounding 原則）。

| 局面 | 分野 | 実践 / 標準 | 規定する対象 |
|---|---|---|---|
| 作業前 | ソフトウェア工学 | ISO/IEC/IEEE 29148:2018 | 実装開始前に要求が曖昧でなく、検証可能で、実現可能であること（`rules/clarifier.md`） |
| 作業前 | ソフトウェア工学 | README-Driven Development (Preston-Werner, 2010) | README / インタフェースを先に書く — 「間違った仕様の完璧な実装は無価値」 |
| 作業前 | ソフトウェア工学 | arc42 (Starke & Hruschka, 2005) | 非自明な設計作業におけるアーキテクチャ文書のテンプレート |
| 作業前 / 決定時 | ソフトウェア工学 | MADR / Nygard ADR | 一方通行の決定を、下される前または下されると同時に根拠つきで記録する（`adr` スキル） |
| 作業前 | プロジェクト管理 | ISO 21502:2020 | ライフサイクル全体のプロジェクトマネジメント指針。プロジェクト計画書・ビジネスケースが記載すべき内容を含む |
| 作業前 | プロジェクト管理 | PMBOK® Guide 第7版 (PMI, 2021) | プロジェクト憲章、プロジェクトマネジメント計画書、プロジェクト文書（要求／リスク／ステークホルダー登録簿）を実行前に作成する |
| 作業前 | プロジェクト管理 | PRINCE2（英国内閣府発、2021年より PeopleCert） | Project Initiation Documentation (PID) — ビジネスケース、計画、品質／リスク方針 — をステージ開始前にベースライン化する |
| 作業中 | ソフトウェア工学 | Docs as Code / *Docs Like Code* (Gentle, 2017) | 文書をコードと同じツールでバージョン管理・レビューし、同一の変更で更新する |
| 作業中 | ソフトウェア工学 | Living Documentation (Martraire, 2019) | 文書が真実であり続け、コードに co-located であること — 規則本体の §§ 1–7 として操作可能化 |
| 作業中（構造） | ソフトウェア工学 | Diátaxis (Procida, 2020) | 文書の出力を tutorial / how-to guide / reference / explanation に分類する |
| 作業中 | プロジェクト管理 | PRINCE2 management products | Highlight Report / End Stage Report が PID に対する進捗を追跡する |
| ライフサイクル全体 | ソフトウェア工学 | ISO/IEC/IEEE 15289:2019 | プロセス全体を通じたライフサイクル文書項目の必要記載内容を定義する |
| ライフサイクル全体 | プロジェクト管理 | ISO 10006:2017 | プロジェクト文書（プロジェクト品質計画書等）の品質管理指針 |
| 利用者向け文書 | ソフトウェア工学 | ISO/IEC/IEEE 26514:2022 | 利用者に向けた情報の設計・開発要件 |

---

## 2. なぜ「すべての成果物はピラミッドである」のか

規則本体 § 7.2 は、あらゆる粒度層の Documentation Artifact に 4 つの条件を課す — 前提の共有が先、結論が支持に先行、兄弟は MECE、各グループはひとつの論理に統一。

これらは新しい基準ではない。すでにリポジトリ内に存在する 2 つの規範を、文書という対象に適用しただけである:

- **Logic tree レンズと Parallel レンズ**（`.claude/rules/thinking-lenses.md`）— 各結論が演繹か帰納かを区別すること、兄弟枝が MECE であること、同一階層の項目が同じ種類のものであることを要求する。§ 7.2 の第 3・第 4 条件はこれを文書に適用したものにすぎない。
- **Minto のピラミッド原則**（Minto, 1987）— 前提の共有 → 結論 → MECE な支持要素、という順序。§ 7.2 の第 1・第 2 条件がこれにあたる。

つまり § 7.2 は、思考に対してすでに課している規律を、書かれたものに対しても課すというだけの話である。新しい判断基準を導入していないからこそ、思考と成果物が乖離しない。

---

## 3. なぜ読者レベルを「層をどこまで降りたか」で測るのか

規則本体 § 7.3 は、読者の専門性を「初級／上級」といったラベルではなく、**粒度層をどこまで降りたか**で定義する。

ラベルによる指定には検証可能性がない。「この文書は中級者向けである」という主張は、誰にも反証できないし、確認もできない。書き手の想定が読み手と一致しているかを確かめる手段がない以上、それは判断の根拠として機能しない。

対して「層をどこまで降りたか」は観測可能である。L1（リポジトリ）を読み終えた読者が L2（サブツリー）を読む、という関係は文書の構造そのものに現れる。だからこそ次の依存規則が**検査可能な規則**になる:

> 成果物は、より**上位**の層で導入された用語に依拠してよい。より**下位**の層でしか定義されていない用語に依拠してはならない。

README が docstring にしか書かれていない用語に寄りかかっていれば、それは意見の相違ではなく、規則違反として指摘できる。専門性は読者に貼るラベルではなく、読者が降りてきた距離である — この置き換えによって、粒度の判断が裁量から検査に変わる。

---

## References

- Cyrille Martraire, *Living Documentation: Continuous Knowledge Sharing by Design*, Addison-Wesley, 2019 — <https://www.oreilly.com/library/view/living-documentation-continuous/9780134689418/>
- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* (2nd ed.) — <https://www.iso.org/standard/72089.html>
- Tom Preston-Werner, "Readme Driven Development," 2010 — <https://tom.preston-werner.com/2010/08/23/readme-driven-development>
- arc42 template (Gernot Starke & Peter Hruschka), since 2005 — <https://arc42.org/>
- Michael Nygard, "Documenting Architecture Decisions," Cognitect, 2011; MADR 4.0.0 — `adr` スキル § References を参照
- Anne Gentle, *Docs Like Code*, 2017 (3rd ed. 2022) — <https://www.docslikecode.com/>
- Daniele Procida, Diátaxis framework, 2020 — <https://diataxis.fr/>
- Barbara Minto, *The Minto Pyramid Principle: Logic in Writing, Thinking, and Problem Solving*, 1987（§ 7.2 が適用するピラミッド構造）
- ISO/IEC/IEEE 15289:2019, *Systems and software engineering — Content of life-cycle information items (documentation)* — <https://www.iso.org/standard/74909.html>
- ISO/IEC/IEEE 26514:2022, *Systems and software engineering — Design and development of information for users* — <https://www.iso.org/standard/77451.html>
- ISO 21502:2020, *Project, programme and portfolio management — Guidance on project management* — <https://www.iso.org/standard/74947.html>
- Project Management Institute, *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)*, 7th ed., 2021 — <https://www.pmi.org/standards/pmbok>
- PRINCE2 (PeopleCert / formerly AXELOS), project management method — <https://www.axelos.com/certifications/propath/prince2-project-management>
- ISO 10006:2017, *Quality management — Guidelines for quality management in projects* — <https://www.iso.org/standard/70376.html>
