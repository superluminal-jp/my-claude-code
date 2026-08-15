# Quickstart: Validating the scrum-master Minimization

Run these after implementation to confirm the feature meets `spec.md`'s Success Criteria. All commands run from the repository root. None require network access or a running model, except the two "live invocation" checks explicitly marked as such.

## Prerequisites

- Repository checked out at branch `022-minimize-scrum-master-skill`
- No setup beyond a POSIX shell and `grep`/`find` (already used throughout this repo's `tests/`)

## SC-001 — Zero non-`[SG20]` citations remain

```sh
grep -rEn '\[(NXG|AM01|EBM24|KGS21|DORA26|EDM99|ART|ICA|SAP|ZBS|AAP|LESS|SAFE|SC@S)\b' \
  .claude/skills/scrum-master/
```

**Expected outcome**: no output (exit status 1 from grep — no matches).

## SC-002 — Deleted files and directories are gone

```sh
for f in \
  .claude/skills/scrum-master/references/scaling-frameworks.md \
  .claude/skills/scrum-master/references/measurement-and-diagnostics.md \
  .claude/skills/scrum-master/references/anti-patterns-and-coaching.md \
  .claude/skills/scrum-master/references/facilitation-and-coaching.md \
  .claude/skills/scrum-master/references/event-playbooks.md \
  .claude/skills/scrum-master/scripts/flow_metrics.py \
  tests/run-flow-metrics.sh \
  tests/test_flow_metrics.py \
  ; do
  test -e "$f" && echo "STILL PRESENT: $f"
done
find .claude/skills/scrum-master/scripts -mindepth 1 2>/dev/null
```

**Expected outcome**: no "STILL PRESENT" lines; `scripts/` is empty or absent (no `__pycache__`).

## SC-003 — Event guidance is purpose+timebox only (live invocation, manual)

In a Claude Code session, ask: 「スプリントレトロスペクティブはどう進めればよいですか」

**Expected outcome**: the answer states only the Guide's purpose ("品質と効果を高める方法を計画する") and the 3-hour timebox for a one-month Sprint. It must not include a staged facilitation structure, a named retro format (Start/Stop/Continue, 4Ls, etc.), or an improvement-experiment template.

Repeat for Sprint Planning, Daily Scrum, Sprint Review, and Product Backlog Refinement — each answer should be limited to purpose, participants, and (where the Guide defines one) timebox.

## SC-004 — Out-of-scope topics get an explicit decline (live invocation, manual)

Ask each of:

- 「どのスケーリングフレームワーク（Nexus/LeSS/SAFe）を採用すべきですか」
- 「このCSVからサイクルタイムを計算してください」
- 「レトロではどのコーチングスタンスを取るべきですか」

**Expected outcome**: each response states the topic is out of scope for this Scrum-Guide-only skill, and does not answer from the deleted material.

## SC-005 — No dead relative links anywhere in the skill

```sh
grep -rEon '\]\(([^)#]+\.md)(#[^)]*)?\)' .claude/skills/scrum-master/ \
  | while IFS=: read -r file line rest; do
      target=$(echo "$rest" | sed -E 's/.*\(([^)#]+)(#.*)?\)/\1/')
      dir=$(dirname "$file")
      resolved="$dir/$target"
      test -f "$resolved" || echo "DEAD LINK in $file:$line -> $target"
    done
```

**Expected outcome**: no "DEAD LINK" lines.

## Repo-wide consistency (Decision 3, research.md)

```sh
# README no longer promises flow metrics or the deleted script
grep -n 'flow_metrics\|flow metrics' README.md   # expect: no output

# settings.json still valid JSON, no dangling permission for a deleted script
jq . .claude/settings.json > /dev/null && echo "settings.json OK"
grep -n 'flow_metrics' .claude/settings.json     # expect: no output

# routing regression for scrum-master is untouched and still passes
# (run via this repo's existing skill-routing harness, per its own README)
```

## Full suite sanity check

```sh
./scripts/check-mcp-consistency.sh
bash tests/run-codex-sync.sh
bash tests/run-codex-references.sh
bash tests/run-codex-drift.sh
```

**Expected outcome**: all pass — the `scrum-master` skill is still discovered, routed, and mirrored correctly; only its internal content changed. `tests/run-flow-metrics.sh` is intentionally absent from this list, since it is deleted by this feature.
