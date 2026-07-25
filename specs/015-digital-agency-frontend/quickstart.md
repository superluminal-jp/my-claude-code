# Quickstart: Validate the Digital Agency Frontend Skill

## Prerequisites

- Run from the repository root on branch `015-digital-agency-frontend`.
- Ensure Bash, Python 3, `jq`, `shfmt`, `shellcheck`, and `yamllint` are available.
- Do not run `install.sh` against the real home directory for fixture validation; the drift suite supplies an isolated home.

## 1. Prove the contract test is red before implementation

```sh
bash tests/run-digital-agency-frontend-skill.sh
```

Expected before the skill exists: non-zero exit with failures for the missing skill package and integration entries.

## 2. Validate the completed skill package

```sh
bash tests/run-digital-agency-frontend-skill.sh
python /Users/taikiogihara/.codex/skills/.system/skill-creator/scripts/quick_validate.py .claude/skills/digital-agency-frontend
```

Expected: every contract check passes and the structural validator reports a valid skill.

## 3. Validate cross-agent deployment and drift detection

```sh
bash tests/run-codex-sync.sh
bash tests/run-codex-sync-drift.sh
```

Expected: repository links resolve; isolated repeated installation creates a matching global Codex skill link; the drift fixture still identifies deliberate failures precisely.

## 4. Run documentation and formatting guards

```sh
bash tests/run-live-documentation.sh
bash tests/run-post-edit-format-guard.sh
git diff --check
```

Expected: all suites pass and the diff contains no whitespace errors.

## 5. Manual representative scenarios

Inspect the skill against these prompts without writing to production systems:

1. “DADSを使って行政手続きの申請状況ページをReact/Tailwindで作って”
2. “デジタル庁デザインシステムの入力コンポーネントに置き換えて”
3. “このReact画面をJIS AA/WCAG 2.2 AAの観点で直して”
4. “政策KPIの提示型Webダッシュボードを作って”
5. “このTailwindダッシュボードをデジタル庁ガイドブックに沿ってレビューして”

Expected: the main DADS reference is always selected, the dashboard reference only for scenarios 4–5, and implementation requests compose with `coder`.
