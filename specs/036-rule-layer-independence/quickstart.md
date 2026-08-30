# Quickstart: Verify the Independent Configuration Pyramid

Run from the repository root on branch `036-rule-layer-independence`.

## 1. Confirm scope and baseline

```sh
git status --short --branch
wc -c .claude/CLAUDE.md .claude/rules/*.md
```

The recorded pre-rewrite total is **20,126 bytes**. The verified post-rule-rewrite total is **14,317 bytes**, a reduction of 5,809 bytes (28.9%). Existing user changes must remain visible and preserved.

## 2. Run the durable structural contract

Before implementation, the new suite must fail against the legacy apex/rules. After implementation it must pass.

```sh
tests/run-config-pyramid.sh
```

The suite owns exact file topology, prohibited runtime-configuration references, description contracts, package-relative links, representative compound routing, deleted legacy paths, and unconditional byte budget.

## 3. Inspect the apex alone

```sh
sed -n '1,220p' .claude/CLAUDE.md
rg -n '(\.claude/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' .claude/CLAUDE.md
```

Expected after the apex phase: the first command shows one outcome and three lifecycle branches; the second command has no output.

## 4. Inspect universal rules against the apex and siblings

```sh
find .claude/rules -maxdepth 1 -type f -name '*.md' -print | sort
rg -n '(\.claude/|rules/|skills/|SKILL\.md|settings(\.local)?\.json|\.mcp\.json|/speckit-[[:alnum:]-]+)' .claude/rules
```

Expected files:

```text
.claude/rules/clarifier.md
.claude/rules/live-documentation.md
.claude/rules/permissions.md
.claude/rules/pyramid-principle.md
.claude/rules/thinking-lenses.md
```

Use the relation table in [data-model.md](./data-model.md) to verify each rule supports one apex branch and does not own a sibling concern.

## 5. Inspect skill independence and owned resources

```sh
rg -n 'rules/|\.claude/(rules|skills)|\.agents/skills' .claude/skills --glob 'SKILL.md'
rg -n 'skill-routing\.md|rules/mcp\.md|rules/git-workflow\.md' .claude README.md README.ja.md docs tests --glob '!docs/adr/00{01..14}-*.md' --glob '!specs/**'
```

Expected: no runtime dependency match. Historical Accepted ADRs are intentionally immutable; third-party archives are excluded from authored-package checks.

Run the dedicated suite for pairwise authored-skill name scans, portable package paths, relative-link resolution, and routing fixtures.

## 6. Run targeted compatibility tests

```sh
tests/run-digital-agency-frontend-skill.sh
tests/run-install.sh
tests/run-mcp-startup.sh
```

If a test legitimately requires network access and fails because the sandbox blocks it, rerun only that test with approved network access and report both results.

## 7. Run the complete repository suite

```sh
for test_script in tests/run-*.sh; do
  "$test_script"
done
git diff --check
```

Do not report completion until every applicable suite passes or an environment-only failure is explicitly isolated with evidence.

## 8. Review the logical checklist

Read [logic-architecture.md](./checklists/logic-architecture.md) and confirm all 26 requirement-quality questions are checked. Then compare the final runtime files to the relation table; grep evidence does not replace the semantic review.

## 9. Confirm preserved scope

```sh
git diff -- .claude/skills/digital-agency-frontend/references/dads-docs
git status --short
```

Expected: no vendored-archive diff, no remote publication, and ADR-0015 remains `Proposed`.
