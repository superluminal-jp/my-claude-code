# Quickstart: Validate Skill Independence

## 1. Confirm no skill body instructs loading/routing to a sibling skill

```sh
grep -RnoE '(Load|Route|Implement through|Complements) `[a-z][a-z-]*`' \
  .claude/skills/digital-agency-frontend/SKILL.md \
  .claude/skills/coder/SKILL.md \
  .claude/skills/adr/SKILL.md \
  .claude/skills/minto-builder/SKILL.md \
  .claude/skills/minto-reviewer/SKILL.md \
  .claude/skills/minto-rewriter/SKILL.md
```
Expected: no output.

## 2. Confirm digital-agency-frontend still states its own TDD/security/doc-sync/ambiguity requirements

```sh
grep -niE 'failing (behavior|accessibility) test|type-safe|documentation artifact|material ambiguity|before implementation' \
  .claude/skills/digital-agency-frontend/SKILL.md
```
Expected: multiple matches — the substantive behavior formerly obtained by naming `coder`/`clarifier` is present in the skill's own words.

## 3. Confirm the router layer is untouched

```sh
git diff --stat .claude/CLAUDE.md .claude/rules/skill-routing.md README.md README.ja.md AGENTS.md
```
Expected: empty (no changes to any of these five files).

## 4. Confirm FR-004 in spec 015 was superseded, not silently left contradicting the code

```sh
grep -n 'FR-004' specs/015-digital-agency-frontend/spec.md
```
Expected: the requirement text now describes self-containment and states it supersedes the original composition wording.

## 5. Run the digital-agency-frontend contract suite

```sh
bash tests/run-digital-agency-frontend-skill.sh
```
Expected: all checks pass, including SYNC-SKILL-05A (unchanged) and the rewritten DADS-06/DADS-07.

## 6. Run the full remaining behavior suite

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```
Expected: every suite passes.

## 7. Confirm no ADR was needed but the decision is traceable

```sh
git diff --stat docs/adr/
ls specs/028-independent-skills/
```
Expected: empty diff for `docs/adr/` (no new ADR — see research.md R11); `specs/028-independent-skills/` contains spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md as the decision's record.
