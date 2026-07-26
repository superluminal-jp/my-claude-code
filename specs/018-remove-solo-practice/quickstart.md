# Quickstart: Validating the solo-practice removal

## 1. Confirm the file is gone and nothing links to it

```bash
test -f .claude/skills/scrum-master/references/solo-practice.md && echo "STILL EXISTS" || echo "deleted OK"
grep -rln "solo-practice" .claude/ .codex/ README.md 2>/dev/null
```

Expect: "deleted OK" and no grep matches.

## 2. Confirm no solo/individual language remains in the five routing declarations

```bash
grep -n "ソロ\|solo\|個人利用" \
  .claude/skills/scrum-master/SKILL.md \
  .claude/rules/skill-routing.md \
  .claude/CLAUDE.md \
  .codex/AGENTS.md \
  README.md
```

Expect: no output (SC-001).

## 3. Sample routing behavior (SC-003, SC-004)

Using an agent session in this repository, issue these prompts and note which skill loads:

- Previously-solo prompts (expect: NOT `scrum-master`): "自分ひとりの作業を週次で振り返りたい", "help me run my own weekly planning as if I were my own Scrum Master", "個人のタスクをカンバンで管理したい、サイクルタイムを見たい".
- Team-facing prompts (expect: still `scrum-master`, unchanged): "うちのチームのデイリースクラムが報告会になっている", "スプリントレビューを承認ゲートにせず、ワーキングセッションにしたい", "レトロがマンネリ化しているので新しい形式を試したい".

## 4. Confirm the 017 citation work survived (FR-011, SC-005)

```bash
grep -c '\[SG20' .claude/skills/scrum-master/references/scrum-framework.md
```

Expect: same count as at the end of `017-scrum-master-rewrite` (25, per that feature's verification pass) — not fewer.

## 5. Link integrity (SC-006)

Re-run the same link-resolution check used in `017-scrum-master-rewrite`'s quickstart, scoped to the surviving files (no `solo-practice.md` in the file list this time). Expect zero broken links.

## 6. Regression suites (SC-007)

```bash
bash tests/run-skill-routing.sh
bash tests/run-codex-sync.sh
```

Both must pass exactly as they did at the end of `017-scrum-master-rewrite` (the one pre-existing CLI-harness flake and the one pre-existing `.DS_Store`-related failure, if still present, are environmental and unrelated to this change — not a regression to fix here).

## Done when

All six checks above pass, with the explicit expectation that checks 4–6 show **no change** from `017-scrum-master-rewrite`'s own verified end-state, only checks 1–3 showing the new removal taking effect.
