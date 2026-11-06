---
description: "Task list for 065: 2つのスキルを目的に合う名前に変え、検査器のレビューの指摘14件を直す"
---

# Tasks: 2つのスキルを目的に合う名前に変え、検査器のレビューの指摘14件を直す

背景と決めた事項 D1〜D5 は同じディレクトリの `spec.md` にある。作業は、`origin/main`(コミット faafbd0)から作ったブランチ `refactor/verified-delivery` で行った。

- [X] T001 [US1] 2つのスキルの名前を変える(コミット e1f9ec3)。結果: `tests/run-*.sh` の13本がすべて終了コード 0 で、各検査の件数は変更の前と同じだった
- [X] T002 [US2] [US3] [US4] [US5] 振る舞いを変える9件(F1〜F9)の回帰テストを先に書き、失敗を確かめる(Red、コミット 73004a5)。結果: `verified-delivery` の119件のうち21件、`requirements-decomposition` の78件のうち5件、`tests/run-config-pyramid.sh` の PARENT-09 と PARENT-10 が失敗した
- [X] T003 F1〜F14 を直す(Green)。F10〜F14 は振る舞いを変えない整理で、既存のテストと、`.claude/` の下の `specs/` への参照の検索で確かめた
- [X] T004 `references/manifest.md`(名前の比較、反証の記録の外枠、カードのエスケープ、読めない数)と `references/checker.md`(読めない数、コードブロックの規則)を書く
- [X] T005 検査をすべて実行する。結果: `verified-delivery` の119件と `requirements-decomposition` の78件が Python 3.11、3.12、3.13 で通る。`tests/run-*.sh` はすべて終了コード 0。mypy の指摘は `origin/main` と同じで、新しいものはない。Python 3.9 では実行していない(この環境にない)

範囲外として残したもの: `pyramid-structure` の README の `spec 055` の参照、`pilot.py` の使われていない `import argparse`(どちらも本仕様の前からあり、今回の指摘に含まれない)。
