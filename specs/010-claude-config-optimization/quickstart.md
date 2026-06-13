# Quickstart: Validate the Optimized Configuration

Run these checks after `/speckit-implement` to confirm the spec's success criteria. No app to launch — validation is static analysis of the config plus spot-checking hook guards.

## 1. Standing-context efficiency (SC-002, SC-008)

```sh
# Baseline (spec time) = 146 lines. No hard line target — gate is
# "zero duplication + no verbosity bloat", comprehension outranks compression.
wc -l CLAUDE.md .claude/CLAUDE.md \
      .claude/rules/skill-routing.md \
      .claude/rules/live-documentation.md \
      .claude/rules/mcp.md | tail -1
# Every CLAUDE.md import ≤ 200 lines:
wc -l .claude/rules/*.md
# Clarification guidance stated once (single canonical source):
grep -rliE 'clarif' .claude/CLAUDE.md .claude/rules/ .claude/skills/clarifier/SKILL.md
```

Pass: duplicated guidance eliminated (clarification lives in `rules/clarifier.md`, others cross-reference it); no enforced behavior removed (section 4); any net line increase over baseline is traceable to a recorded comprehension supplement or anchor, not verbosity.

## 2. Intent-line coverage (SC-001)

```sh
# Each rule file's first non-blank line states Purpose/Applies-when:
for f in .claude/rules/*.md; do printf '%s: ' "$f"; grep -m1 . "$f"; done
# Each owner skill states intent in its body first sentence:
for f in coder editor clarifier domain-model ubiquitous-language; do
  printf '%s: ' "$f"; sed -n '/^---$/,/^---$/!{/./{p;q}}' ".claude/skills/$f/SKILL.md"
done
```

Pass: 7/7 rules and 5/5 owner skills show an explicit intent statement.

## 3. Memory + Subagent guidance (SC-003)

```sh
grep -niE 'memory' .claude/rules/tools.md
grep -niE 'subagent|delegat' .claude/rules/tools.md
```

Pass: both have a usage trigger **and** an explicit anti-pattern (when NOT to use).

## 4. Behavior inventory — zero loss (SC-002, SC-004)

Walk `contracts/behavior-inventory.md` top to bottom:

```sh
# Permissions intact:
grep -cE '"Read\(|"Bash\(git' .claude/settings.json
# Hook guards intact (spot-check the high-risk ones):
grep -c 'exit 2' .claude/hooks/pre-bash.sh        # destructive/network/credential blocks
grep -c 'exit 2' .claude/hooks/user-prompt-submit.sh   # secret patterns
grep -nE 'main|master' .claude/hooks/pre-edit.sh       # branch guard
# Hooks executable:
ls -l .claude/hooks/*.sh   # all 0755
# Hook scripts still valid:
shellcheck .claude/hooks/*.sh
jq empty .claude/settings.json && echo "settings.json valid"
```

Optional live spot-checks (should each be blocked):

```sh
echo '{"tool_input":{"command":"git push -f"}}' | .claude/hooks/pre-bash.sh; echo "exit=$?"   # expect 2
echo '{"prompt":"AKIAIOSFODNN7EXAMPLE"}'        | .claude/hooks/user-prompt-submit.sh; echo "exit=$?"  # expect 2
```

Pass: every inventory item present; spot-checks exit 2 where expected.

## 5. Routing triggers intact (behavior inventory C)

```sh
grep -niE 'coder|editor|clarifier|ubiquitous-language|domain-model' .claude/CLAUDE.md
```

Pass: all five routing triggers and the mixed-request order survive.

## 6. Internal design→plan→task discipline (SC-006)

Manual: issue a non-trivial request without a slash command (e.g. "add input validation across the three parsers") in a fresh session and confirm Claude states approach → plan → task breakdown before editing. Then issue a trivial request (e.g. "fix this typo") and confirm no planning overhead is added. Pass: non-trivial gets the phase; trivial skips it.

## 7. Live Documentation audit (SC-007)

Manual: review the refreshed `.claude/CLAUDE.md`, `rules/*`, and owner skills against `.claude/rules/live-documentation.md` — proximity, no redundancy, explicit intent, auto-gen preference. Pass: zero unresolved violations (clarification guidance exists in one canonical place; Memory/Subagent guidance co-located in `tools.md`).

## 8. Actionability of every directive (SC-009)

Manual: read each refreshed rule/skill directive and ask "what observable behavior does this produce?". Pass: every directive has an answer; zero vacuous or un-executable directives remain. Any directive that was ambiguous now carries a clarifying supplement (example/boundary/precise verb).

## 9. Authoritative grounding accuracy (SC-010)

```sh
# Surface the named authorities for a correctness/attribution check:
grep -rniE 'OWASP|ASVS|CWE|29148|INVEST|MoSCoW|FURPS|SMART|Gherkin|MECE|SCQA|BLUF|Pyramid|Minto|Tufte|Cleveland|Strunk|pre-mortem|Fermi' \
  .claude/CLAUDE.md .claude/rules/ .claude/skills/{coder,editor,clarifier,advisor,domain-model,ubiquitous-language}/SKILL.md 2>/dev/null
```

Manual check on the output: each anchor is (a) real and correctly named, (b) current, (c) functional — it narrows interpretation rather than decorating. Pass: zero fabricated, misattributed, or decorative-only anchors.

## Done criteria

All nine sections pass and `git diff` shows only intended config edits. Then commit and push to `claude/speckit-claude-code-settings-lrldfc`.
