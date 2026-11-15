# AC-README-1: README の表が宣言と一致し、目的の欄が1文で、手で書き換えた写しと2文の写しを拒む
# reviewed_commit: c90a58af546f66a26ecee909fa2962c2d1fb96f0
# この記録は、下に挙げたファイルをそのまま連結したものである（行を選んだ部分は、そう書いた）。各部の見出しに元のファイルを書いた。

## 全規則の検査（README と PURPOSE の違反がないこと）（specs/073-scrum-role-tree/evidence/c90a58a/ac-root-1.txt）

# command: python3 -B tests/assert_role_tree.py
# reviewed_commit: c90a58af546f66a26ecee909fa2962c2d1fb96f0 (files outside specs/073-scrum-role-tree/ identical at HEAD 97d42c5)
# date: 2026-11-15T00:22:45Z

role-tree: 22 elements, 0 violations

exit=0

## 変更前（PURPOSE の規則を足し、purpose() を直す前）（specs/073-scrum-role-tree/evidence/red-purpose.txt）

# python3 -B tests/assert_role_tree.py (2026-11-15, round-1 fix of AR-02: the PURPOSE rule added, before purpose() cuts a Japanese sentence)
FAIL PURPOSE apply-scrum-guide: the purpose 'Scrum Guide (2020) を唯一の規範として、AI が Scrum Team の Developers の一'... is more than one sentence
role-tree: 22 elements, 1 violations
exit=1

## 自己検査の README と PURPOSE の行（specs/073-scrum-role-tree/evidence/c90a58a/ac-tree-check-1.txt）

# command: python3 -B tests/assert_role_tree.py --self-test
refused README   a README table row edited by hand
refused README   a README.ja table row edited by hand
refused PURPOSE  a README.ja purpose cell of two sentences
role-tree self-test: 15 of 15 broken copies refused

