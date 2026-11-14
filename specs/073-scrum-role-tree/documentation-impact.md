# Documentation impact

`python3 -B harness/skills/sync-docs/scripts/find_related.py --root . --base main` を 2026-11-15 に実行した。変更されたファイルは37件で、関係する文書として挙がったのは `CLAUDE.md` と `docs/harness-zero-base.md` の2件だった。同じ日に `audit.py --base main` も実行した。そこで挙がった、決定の記録、生成した出力、検査が述べる主張の3つも、下の各行で扱う。

```text
Documentation impact
- Updated: CLAUDE.md - 役割の木の宣言、標識、README の表と木の図の作り直し、新しい要素の段階を足すことを、このリポジトリで開発するときの事実として1項目足した。agrees with tests/assert_role_tree.py の docstring と、ADR-0026 の「検査」
- Updated: README.md, README.ja.md - 「Role tree」と「役割の木」の節に、宣言から生成した表を置いた。検証の節に、C-04 の role と branch、C-08 の例外、assert_role_tree.py とその自己検査を足した。agrees with tests/assert_role_tree.py --table en / ja と、tests/assert_skill_contract.py の docstring
- Updated: docs/claude-config-design.md - スキルの種類の説明の後に、役割と枝の軸の段落を足した。agrees with tests/assert_skill_contract.py の ROLES と BRANCHES、ADR-0026
- Updated: docs/harness/skill-map/ - 5枚の図に組み直した。03-role-tree.md の木は宣言から生成した。03-components-skills.md は 04-components-relations.md（木の外の関係）に、04-dynamic-deliver-change.md は 05-dynamic-deliver-change.md に移した。一覧のページと相互のリンクも直した。agrees with tests/assert_role_tree.py --mermaid と specs/073-scrum-role-tree/evidence/check_skill_map.py
- Updated: tests/assert_skill_contract.py の docstring - C-04 に role と branch を、C-08 に metadata.role の値を名前に数えないことを書いた。agrees with 同じファイルの検査の本体
- Updated: tests/assert_reviewer_agent.py の docstring - R1a の欄に metadata を足した。agrees with 同じファイルの FIELDS と、パーサーの metadata の扱い
- Created: docs/adr/0026-place-skills-and-agents-in-a-scrum-role-tree.md - 利用者が書くことを選んだ決定の記録。Proposed にした。agrees with specs/073-scrum-role-tree/ の問題カード、要件グラフ、反証の記録
- No change needed: docs/harness-zero-base.md - 再設計（spec 066〜）の時点の記録で、契約の現在の規則は、スクリプトの docstring と README の検証の節が述べる。過去の記録は書き換えない
- No change needed: docs/adr/0015-rule-layer-independence.md、docs/adr/0025-ai-as-developer-scrum-master-as-subagent.md - 決定の記録は書き換えない。0026 は 0015 を置き換えない（役割と枝は名前による参照ではないので、名指さない決まりは保たれる）。0025 の前提の食い違いは、0026 の「ADR-0025 の前提について」に記録した
- No change needed: docs/harness/capability-map.json、capability-map.md - 段階と担い手は変えていない。assert_role_tree.py は読むだけで、22件すべてが components にある
- No change needed: claude-ai-system-prompt.md、chatgpt-system-prompt.md - Claude.ai 用の写しの作り直しは、範囲外（問題カードの out_of_scope）
- Unverified: harness/skills/*/SKILL.md と harness/agents/*.md の description の末尾の標識 - スキルの選ばれ方への影響は測っていない。利用者が未検証のリスクとして受け入れた（問題カードの evidence）
- Checks: python3 harness/skills/sync-docs/scripts/check_links.py --root . - 下の「結果」に記録する
- Checks: python3 -B tests/assert_role_tree.py - 22 elements, 0 violations
- Checks: python3 -B harness/skills/draw-system-diagrams/scripts/check_diagrams.py docs/harness/skill-map - 0 error(s), 1 warning(s)（03-role-tree.md の M6。理由はそのページに書いた）
```

## 結果

check_links.py の結果は、[evidence/checks-after.md](evidence/checks-after.md) に記録する。
