---
description: "Task list for 055: 常時適用の構成スキル pyramid-structure と機械検査"
---

# Tasks: 常時適用の構成スキル `pyramid-structure` と機械検査

- [X] T001 基準を記録する: `tests/run-config-pyramid.sh` 42件・`tests/run-readme-skill-index.sh` 31件がすべて通る
- [X] T002 単体テストを `unittest` に移し、標準入力・箇条書きの木・冒頭の文(S8)のテストを加える
- [X] T003 実行して、新しいテスト7件だけが失敗することを確認する
- [X] T004 `check.py` に標準入力、箇条書きの木の検査、S8、行番号順の並べ替えを加え、テスト49件を通す。ruff と `mypy --strict` を通す
- [X] T004a 既存の2つのガイドで試し、見出し代わりの太字の行が検査されないこと、参考文献の箇条書きで誤検出が出ることを見つけた。テスト4件を先に足して失敗を確かめ、実装してテスト53件を通す
- [X] T005 `SKILL.md` を常時適用型に書き直し、思考過程の非開示・完了前チェック・優先順位を移す。`references/templates.md` を加える
- [X] T006 `minto-pyramid` を `archive/minto-pyramid/` へ `git mv` し、評価ケース4件を移して `allowed_tools` に `Bash` を加える。`review-finds-structure-gaps` を加える
- [X] T007 `authored_skills` と SKILL-06 の一覧に `pyramid-structure` を加え、取り込みプラグインの説明から `minto-pyramid` を外す
- [X] T008 README(英・日)、`docs/claude-config-design.md`、スキルと退避先の README を更新する
- [X] T009 全テストを実行する: `run-config-pyramid` 42件、`run-readme-skill-index` 31件、`run-removed-guardrails` 4件、`run-install`、`run-package-safety-bundle` 21件、`run-secure-logging-skill` 40件、`run-digital-agency-frontend-skill` 74件がすべて通る。`run-mcp-startup` はネットワークを要し、変更対象外のため実行していない
