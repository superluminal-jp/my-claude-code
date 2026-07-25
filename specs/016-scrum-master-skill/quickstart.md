# Quickstart: Validating the `scrum-master` integration

**Feature**: 016-scrum-master-skill | **Date**: 2026-07-25

How to prove the feature works end to end. Steps 1–3 and 6–7 are deterministic and need nothing installed. Step 4 needs a live Claude Code session. Step 5 modifies `~/.claude` and `~/.agents`, so run it only when you intend to install.

Each step names the requirements and success criteria it discharges. Details of *what* must hold live in [contracts/skill-integration.md](./contracts/skill-integration.md) and [data-model.md](./data-model.md); this file is only about running the checks.

## Prerequisites

- Repository checked out, branch `016-scrum-master-skill`
- `jq` and `python3` on `PATH`
- For step 4: Claude Code CLI (`claude`)
- For step 5: willingness to write to `~/.claude` and `~/.agents`

---

## 1. Payload is present and coherent — C1, C2, C3 / FR-001, FR-003, SC-005

Confirm the skill directory holds the playbook, nine references, and the executable helper, and that every link in the playbook resolves.

```bash
ls -R .claude/skills/scrum-master && test -x .claude/skills/scrum-master/scripts/flow_metrics.py && echo "executable OK"
```

Then check the links — every relative Markdown target in the skill must exist:

```bash
cd .claude/skills/scrum-master && grep -rhoE '\]\(([^)]+\.md)\)' . | sed -E 's/^\]\(//; s/\)$//' | sort -u | while read -r t; do [ -e "$t" ] || [ -e "references/$t" ] || echo "BROKEN: $t"; done; echo "link check done"
```

**Expected**: eleven files listed, `executable OK`, and no `BROKEN:` lines.

---

## 2. Nothing excludes the skill from version control — C1 / FR-004

```bash
git check-ignore -v .claude/skills/scrum-master/SKILL.md || echo "not ignored — correct"
```

**Expected**: `not ignored — correct`. A path printed here means a `.gitignore` rule is swallowing the skill.

---

## 3. Frontmatter identity preserved, tool declaration corrected — C4, C7 / FR-002, FR-015

```bash
diff <(sed -n '/^---$/,/^---$/p' /Users/taikiogihara/work/scrum-master-skill/scrum-master/SKILL.md) <(sed -n '/^---$/,/^---$/p' .claude/skills/scrum-master/SKILL.md)
```

**Expected**: the *only* difference is the removed `allowed-tools:` line (research R0). Any difference in `name`, `description`, or `when_to_use` is a C4 violation — revert it.

Then confirm the permission landed in the enforced location, scoped:

```bash
jq -r '.permissions.allow[] | select(contains("flow_metrics"))' .claude/settings.json
```

**Expected**: two entries, each anchored on a path ending `scrum-master/scripts/flow_metrics.py`. A bare `Bash(python3 *)` here is a C7 violation.

---

## 4. The skill loads on its own, and the helper runs unprompted — FR-005, FR-014, SC-001, SC-007, SC-009

**This is the step that cannot be faked and must be observed, not assumed** (research R1 flags the permission pattern as inferred).

Open a Claude Code session in this repository and issue these prompts, one per fresh session, none of them naming a skill:

| # | Prompt | Expect |
|---|---|---|
| 4a | `チームのレトロがマンネリ化している` | `scrum-master` loads (team facilitation, JA) |
| 4b | `sprint planning のアジェンダを作って` | `scrum-master` loads (specific event) |
| 4c | `自分ひとりの作業を週次で振り返りたい` | `scrum-master` loads (solo practice) |
| 4d | `our stand-ups keep running long` | `scrum-master` loads (**EN — the case most likely to fail**, since the body is Japanese and only `when_to_use` is English) |
| 4e | `プロジェクトのガントチャートを引き直したい` | `scrum-master` does **not** load — SC-009 boundary |
| 4f | a routine code change request | `coder` loads, unchanged — FR-008 |

SC-001 requires **both** languages, not either — 4d is not optional.

Then, with the skill loaded, exercise the helper on a throwaway CSV:

```bash
printf 'item_id,started_at,completed_at\nA-1,2026-06-01,2026-06-05\nA-2,2026-06-02,2026-06-09\nA-3,2026-06-08,\n' > /tmp/tickets.csv && python3 .claude/skills/scrum-master/scripts/flow_metrics.py /tmp/tickets.csv
```

**Expected**: cycle-time, throughput, and WIP figures, **with no permission prompt**. If a prompt appears, the pattern in `settings.json` did not match — record the exact command Claude Code reports and correct the pattern. This degrades FR-014 only; the rest of the feature still stands.

Also confirm the failure path is legible (FR-016):

```bash
python3 .claude/skills/scrum-master/scripts/flow_metrics.py /tmp/does-not-exist.csv; echo "exit=$?"
```

**Expected**: a readable error and a non-zero exit — never fabricated numbers.

Finally, re-check the guardrail against the command form the playbook actually documents (research R2 verified only a hypothetical path):

```bash
echo '{"command":"python3 .claude/skills/scrum-master/scripts/flow_metrics.py tickets.csv"}' | bash scripts/guardrails/destructive-command.sh
```

**Expected**: `{"decision": "allow", ...}`, exit 0.

---

## 5. Distribution reaches both agents, idempotently — C6 / FR-010, FR-011, FR-012, SC-003, SC-004

```bash
bash install.sh && ls ~/.claude/skills/scrum-master/references | wc -l && readlink ~/.agents/skills/scrum-master
```

**Expected**: `9`, and a link resolving to `~/.claude/skills/scrum-master` — *not* to a path under `work/my-claude-code` (C6).

You do **not** need to wipe an existing profile first. `sync_path()` runs `rm -rf` on each managed path before copying, so one run on a populated profile is equivalent to a clean install for the paths in scope (SC-003, research R4).

Confirm the links still resolve from the installed copy — US2's fourth acceptance scenario is about the *installed* tree, not the repo one:

```bash
cd ~/.claude/skills/scrum-master && grep -rhoE '\]\(([^)]+\.md)\)' . | sed -E 's/^\]\(//; s/\)$//' | sort -u | while read -r t; do [ -e "$t" ] || [ -e "references/$t" ] || echo "BROKEN: $t"; done; echo "installed-copy link check done"
```

Idempotence — run it again and compare:

```bash
find ~/.claude/skills/scrum-master ~/.agents/skills/scrum-master | sort > /tmp/install-1.txt && bash install.sh >/dev/null && find ~/.claude/skills/scrum-master ~/.agents/skills/scrum-master | sort > /tmp/install-2.txt && diff /tmp/install-1.txt /tmp/install-2.txt && echo "idempotent OK"
```

**Expected**: `idempotent OK`.

And confirm Spec Kit's generated skills are still excluded (FR-013):

```bash
ls ~/.claude/skills | grep -c '^speckit-' || echo "0 speckit skills — correct"
```

---

## 6. Catalog agreement across all eleven sites — I1, C5, C8 / FR-006, FR-007, FR-009, FR-017

```bash
for f in .claude/CLAUDE.md .claude/rules/skill-routing.md .codex/AGENTS.md README.md README.ja.md install.sh tests/run-codex-sync.sh tests/run-skill-routing.sh; do printf '%-40s %s\n' "$f" "$(grep -c 'scrum-master' "$f")"; done
```

**Expected**: every line non-zero. A zero is drift — the agents would disagree about what exists.

`.codex/README.md` is deliberately absent from that list: it is a deployment map keyed by path pattern (`.claude/skills/*`) and names no individual skill, so it is verified by its hand-written count instead — `grep -c '手書き 7 件' .codex/README.md` must return `2`.

Counts stated in prose must match reality:

```bash
ls .claude/skills | grep -vc '^speckit-'
```

**Expected**: `7` — and both `README.ja.md`'s「スキルリンク」count and `.codex/README.md`'s two「手書き」rows must say 7.

---

## 7. Full regression gate — C9, C10 / FR-019, FR-020, SC-002, SC-008

```bash
for s in tests/run-*.sh; do echo "=== $s ==="; bash "$s" || echo "FAILED: $s"; done
```

**Expected**: every suite passes. Notes on two of them:

- `run-codex-sync.sh` SKIPs its post-install checks when `~/.codex` is absent; SKIP is not failure.
- `run-skill-routing.sh` hard-errors without the `claude` CLI. Where it does run, the new case `007-scrum-facilitation.md` must pass **and** all six pre-existing cases must resolve to their previously recorded skills (SC-002).

---

## Done when

- [ ] Steps 1, 2, 3, 6 pass (deterministic, no install required)
- [ ] Step 4 observed in a live session, including the 4d boundary case and the unprompted helper run
- [ ] Step 5 passes on a machine where installing is acceptable
- [ ] Step 7 shows no suite regressed
