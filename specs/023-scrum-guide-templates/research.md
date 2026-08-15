# Research: Scrum Guide 作成物・イベント テンプレート

## Decision 1: テンプレート内容の一次ソース

**Decision**: 各テンプレートの記入欄・出典引用は、`references/scrum-framework.md`の「作成物とコミットメント」表（行75-85）と「イベント」表（行55-73）から導出する。PDFを新たに読み直して抽出し直すことはしない。

**Rationale**: `scrum-framework.md`は022番feature（scrum-masterスキル最小化）で既に`[SG20]`のみを出典として整理し直された規範層であり、ページ番号・引用文が確定している。ここから導出すれば、テンプレートと既存リファレンスの間で引用のズレが生じない（plan.md FR-012「既存ファイルと矛盾しない」の担保）。

**Alternatives considered**: PDFから独自に再抽出する — 既存の整理と表記・ページ番号がズレるリスクがあり、022番featureの成果を再検証する二度手間になるため却下。

## Decision 2: README.mdのファイルツリー説明の更新

**Decision**: `README.md`のscrum-masterスキル説明部分（283-285行目付近、「3 on-demand reference documents + the Scrum Guide PDFs」の記述）を、新設の`references/templates/`を反映する形に更新する。

**Rationale**: spec.mdのFRはこのファイルを個別に名指ししていないが、`.claude/rules/live-documentation.md`のDrift Detectionにより、`SKILL.md`の参照ファイル表という公開契約が変わる場合、それを説明するREADMEの記述も同一変更内で更新が必要。022番feature（research.md Decision 3）と同型の判断。

**Alternatives considered**: 更新しない — Live Documentation違反（サイレントな乖離）になるため却下。

## Decision 3: テンプレートの見出し構成の統一

**Decision**: 全7テンプレートを次の統一構成にする。

- 作成物3種（Product Backlog／Sprint Backlog／Increment）：①作成物の定義（Guideの記述の要約＋記入欄）、②対応するコミットメント（Product Goal／Sprint Goal／Definition of Done、原文引用＋記入欄）、③出典（`[SG20, p.X]`＋Scrum Guide公式サイトへの直リンク。実装中にユーザー指示で確定：テンプレートは単体で完結させ、`sources.md`等リポジトリ内ファイルへの相対リンクは持たない）。
- イベント4種（Sprint Planning／Daily Scrum／Sprint Review／Sprint Retrospective）：①目的（原文引用）、②タイムボックス、③Scrum Guideが定める検討内容（該当する場合のみ、例：Sprint Planningの3つの問い）の記入欄、④出典。

**Rationale**: 統一構成にすることで、開いた瞬間に「どこに何を書けばよいか」が分かり、spec.md SC-002（開いてすぐ埋め始められる）を満たす。作成物とイベントで内部構成が異なるのは、Scrum Guideが作成物には「コミットメント」という共通概念を、イベントには「目的とタイムボックス」という共通概念を与えているため、この違いをそのまま反映する。

**Alternatives considered**: 全テンプレート共通の単一フォーマットにする — 作成物とイベントでは書くべき情報の性質が異なるため（例：イベントにコミットメントの概念はない）、無理に共通化すると空欄や不要な見出しが生じ、かえって使いにくくなるため却下。

## Decision 4: ADR 0003との整合性

**Decision**: 本featureはADR 0003（scrum-masterスキルのベンダリング方針）の適用範囲内のコンテンツ追加であり、新しいADRは不要。ADR 0003は変更しない。

**Rationale**: 新規ディレクトリ・ファイルの追加は可逆的（`git rm`一発で削除可能）であり、アーキテクチャ上の一方向ドアの決定ではない。ADR 0003が定めた「本リポジトリを唯一の情報源とする」方針とも矛盾しない。

**Alternatives considered**: 新規ADRを起票する — 一方向ドアでない可逆的変更にADRは過剰であり、`.claude/rules/live-documentation.md`§0のADR基準（一方向ドア・アーキテクチャ上重大）を満たさないため却下。
