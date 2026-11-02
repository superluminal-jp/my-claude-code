---
description: "Task list for 056: 用語の形をその分野で決め、訳語を作らない"
---

# Tasks: 用語の形をその分野で決め、訳語を作らない

- [X] T001 基準を記録する: `tests/run-config-pyramid.sh` 42件がすべて通る
- [X] T002 `tests/run-config-pyramid.sh` に RULE-18(用語の形を分野で決める)と RULE-19(訳語を作らない)を加え、2件だけが失敗することを確かめる
- [X] T003 `.claude/rules/pyramid-principle.md` の「Prefer the plain word when it is exact」の文を、分野の形・原語を残すこと・訳語を作らない理由・定義で平易にすることの1項目に置き換える。例は入れない。テスト44件が通り、常時ロードの合計は 20,065 バイト(基準 20,126 未満)
- [X] T004 `claude-ai-system-prompt.md` の Language 行に同じ義務を加え、定義の項に「(not replace)」を加える。7,000字に収めるため、他の行と重複する記述を3か所削る(Pre-send の「every first-level point supports it」「siblings comparable」「parents synthesize」、hierarchy 行の「expose trade-offs」)。記載を 6,988 字に更新する
- [X] T005 `chatgpt-system-prompt.md` の「More about you」の Language 行に同じ義務を加え、記載を 1,299 字に更新する。この欄の上限は公式資料に書かれていないため、照合していないことを明記する
- [X] T006 README(英・日)のルールの要約を更新する。日本語版の同じ項目にあった「論文の部」は「論文の構成」に改める
- [X] T007 全テストを実行する: `run-config-pyramid` 44件、`run-readme-skill-index` 31件、`run-removed-guardrails` 4件、`run-install`、`run-package-safety-bundle` 21件、`run-secure-logging-skill` 40件、`run-digital-agency-frontend-skill` 74件がすべて通る。`run-mcp-startup` はネットワークを要し、`run-digital-agency-slides-skill` は変更対象外のため実行していない
