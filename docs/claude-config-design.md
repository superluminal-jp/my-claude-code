# 常時ロード設定の設計方針

`.claude/CLAUDE.md` と `.claude/rules/` は、セッション開始時に無条件で読み込まれる。全プロジェクト・全セッションに課金される固定費であり、書けば書くほど良くなるものではない。本書は、それらのファイルが**なぜ今の形なのか**を記録する。

設定ファイル自体には、この種の説明を置かない。Claude の判断を変えない文はコンテキストを消費するだけだからである。本書は `.claude/rules/` の外にあり自動ロードされない。

## 1. 設定は強制しない。設定 *ファイル* が強制する

Claude Code は `CLAUDE.md` と `.claude/rules/` を **advisory（助言）** として扱い、`.claude/settings.json`（permissions、hooks）だけを**強制**する [1]。この区別は程度差ではなく種類の差である。

帰結として、原則をどれだけ巧く書いても保証にはならない。だから `CLAUDE.md` の各原則は「徳目」ではなく**観測可能な義務**として書かれている — transcript や diff で第三者が確認できる形。「正確であれ」は検証不能だが、「実行したコマンドと出力を示せ」は検証できる。検証できないものは当てにできない。

強制が必要な項目は設定側へ移してある。資格情報の読み取り拒否がその唯一の実例で、経緯と受け入れた副作用は [ADR-0014](adr/0014-restore-credential-deny-rules.md) にある。hooks とガードレールスクリプトを全廃した経緯は [ADR-0005](adr/0005-remove-claude-hooks.md) と [ADR-0007](adr/0007-remove-scripts.md)。

## 2. 常時ロードに残す判断基準

一文ごとに問う — **これが無いと Claude は間違えるか。**

間違えないなら消す。具体的には、次のいずれかに当たる記述は常時ロードに置かない:

| 分類 | 意味 | 例 |
|---|---|---|
| ネイティブ | モデルが既に知っている、またはクライアント自身の挙動 | Conventional Commits の文法、命令形、50/72 規則、権限の評価順 |
| ハーネス注入済み | セッション開始時に自動で文脈に入る | 全スキルの名称・説明・トリガー語句、MCP サーバーの `instructions` |
| 参照資料 | 判断ではなく裏取りに使う | 準拠規格の一覧、参考文献、ベンダー公式 URL |
| 設計説明 | なぜその形なのか | 本書の内容そのもの |

この基準は公式ベストプラクティスの「Claude が指示なしで既に正しくできることは削除するか hook に変換せよ」「self-evident な徳目は除外せよ」に対応する [2]。

## 3. ファイル別 — 何を意図的に置いていないか

| ファイル | 置いていないもの | 所在 |
|---|---|---|
| `CLAUDE.md` | スキル一覧 | ハーネスが全スキルの説明を注入する。手書きの列挙は重複であり、実際に 10 個中 7 個しか挙がっていない状態でドリフトしていた |
| `CLAUDE.md` | `@.claude/rules/...` の import | `paths:` を持たないルールは無条件ロードされるため冗長 [1] |
| `permissions.md` | 資格情報パスの列挙 | `settings.json` の `permissions.deny` が正本 |
| `permissions.md` | 部分一致をグロブ化しない理由 | [ADR-0014](adr/0014-restore-credential-deny-rules.md) |
| `live-documentation.md` | ライフサイクル標準規格表、§7 の論拠、参考文献 | [live-documentation-standards.md](live-documentation-standards.md) |
| `clarifier.md` | 曖昧性パターン目録、品質ゲート、出典 | `.claude/skills/clarifier/SKILL.md` |
| `git-workflow.md` | Conventional Commits の解説、trailer の慣習、出典 | ネイティブ知識およびハーネス既定 |
| `mcp.md` | サーバーカタログ、ベンダー URL、機構の解説、出典 | [mcp-servers.md](mcp-servers.md) および `.mcp.json` |
| `skill-routing.md` | スキルの列挙とトリガー語句 | ハーネスが注入する |

残っているのは、いずれの分類にも当たらないもの — **非自明で、判断を変え、他のどこにも存在しない**記述だけである。

## 4. 番号ではなく名前で参照する

`CLAUDE.md` の原則は「Core Principle #3」のような番号ではなく **Traceability のように名前で** 参照する。原則を 1 つ足せば番号参照は全て壊れるためで、実際に Traceability は #3 から #4 へ動いた。`specs/` 配下の過去の記録は当時の番号のまま残してある（当時の事実の記録であり、遡及修正の対象ではない）。

## 5. 変更するとき

設定ファイルに文を足す前に §2 の問いを通す。説明を書きたくなったら、それは本書か、対応する `docs/` の解説か、ADR に属する。

サイズの目安は公式指針の 1 ファイル 200 行未満 [2]。ルール群の合計はコミット履歴で追える。

## References

1. Claude Code — How Claude remembers your project: <https://code.claude.com/docs/en/memory>
2. Claude Code — Best practices: <https://code.claude.com/docs/en/best-practices>
