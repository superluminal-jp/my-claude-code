# Quickstart: Validating the `scrum-master` citation rewrite

This is a validation guide for a human (or reviewing agent) to confirm the rewrite meets `spec.md`'s success criteria. It does not duplicate the citation rules themselves — see `contracts/citation-contract.md` for what "correct" means, and `data-model.md` for which file is canonical for which explanation.

## Prerequisites

- The rewritten `.claude/skills/scrum-master/SKILL.md` and `references/*.md`.
- Read access to `/Users/taikiogihara/Downloads/scrum_official_docs/` (to re-verify a sample of quotations against primary sources).
- A shell in the repository root, on branch `017-scrum-master-rewrite`.

## 1. Sample normative claims for citation + quotation (SC-001)

Pick at least 8 sentences across `SKILL.md` and `scrum-framework.md`/`event-playbooks.md`/`scrum-master-role.md` that state a Scrum Guide rule (event timebox, accountability, artifact, value). For each:

1. Confirm a `[SG20, p.X]` tag is present.
2. Open `Scrum-Guide-2020.pdf` (or the Japanese edition, adjusting for the +1 page offset — see `research.md` R2) at page X.
3. Confirm the quoted phrase appears on that page.

Pass condition: all sampled sentences pass (target: 100%, per SC-001).

## 2. Sample complementary claims for tag + scope note (SC-002)

Pick at least 5 sentences citing `[KGS21]`, `[EBM24]`, `[DORA26]`, `[EDM99]`, `[NXG]`, `[SAP]`/`[AAP]`/`[ZBS]`, or `[LESS]`/`[SAFE]`. For each, confirm the tag resolves to a `sources.md` entry and that any scope/caveat note `sources.md` attaches to that source (e.g. DORA's software-delivery-only framing) is present at or near the point of use.

## 3. Scan for unlabeled factual claims (SC-003)

```bash
grep -n . .claude/skills/scrum-master/SKILL.md .claude/skills/scrum-master/references/*.md
```

Read the output and flag any declarative sentence that is neither (a) carrying a citation tag nor (b) legible as the skill's own stance or an explicitly context-dependent technique. Target: zero.

## 4. Confirm the three duplication clusters were consolidated (SC-004)

For each row of `data-model.md`'s "Canonical location" table:

```bash
grep -n "支援モードを選ぶ\|コーチングスタンス\|アカウンタビリティの境界\|共通設計" \
  .claude/skills/scrum-master/SKILL.md \
  .claude/skills/scrum-master/references/scrum-master-role.md \
  .claude/skills/scrum-master/references/facilitation-and-coaching.md \
  .claude/skills/scrum-master/references/scrum-framework.md \
  .claude/skills/scrum-master/references/event-playbooks.md
```

Confirm the full table/enumeration exists only in its designated canonical file, and other locations show a link instead.

## 5. Word count delta (SC-005)

```bash
wc -w .claude/skills/scrum-master/SKILL.md .claude/skills/scrum-master/references/*.md | tail -1
```

Compare against the pre-rewrite baseline (`git show main:.claude/skills/scrum-master/SKILL.md ... | wc -w`, summed across all 9 files). Confirm the rewritten total is lower.

## 6. Link integrity (SC-006)

```bash
for f in .claude/skills/scrum-master/SKILL.md .claude/skills/scrum-master/references/*.md; do
  grep -oE '\]\([^)]+\)' "$f" | sed -E 's/^\]\((.*)\)$/\1/' | grep -v '^https\?://' | while read -r target; do
    dir=$(dirname "$f")
    path="${target%%#*}"
    [ -f "$dir/$path" ] || echo "BROKEN in $f: $target"
  done
done
```

Confirm no output (zero broken links).

## 7. Evidence tier legibility (SC-008)

Open each `references/*.md` file in isolation (no `sources.md` open). For each section, confirm you can state its evidence tier (規範/公式補完/研究・実務知見/文脈依存の技法) from the heading or immediate context alone.

## 8. Frontmatter and routing untouched (C7 of the citation contract)

```bash
git diff main -- .claude/skills/scrum-master/SKILL.md | sed -n '/^@@/,/^## /p' | head -20
git diff main -- .claude/rules/skill-routing.md .claude/settings.json
```

Confirm the frontmatter block (lines 1–5 of `SKILL.md`) shows no diff, and `skill-routing.md` shows no diff.

## 9. Regression suites (SC-007)

```bash
bash tests/run-skill-routing.sh
bash tests/run-codex-sync.sh
```

Both must pass exactly as before the rewrite.

## Done when

All nine checks above pass. Report any failing check by its number, the specific sentence/file, and whether it's a citation gap (fix in that file), a missed duplication (fix per `data-model.md`), or a broken link.
