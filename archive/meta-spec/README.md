# Archived: `meta-spec` skill

Retired from the managed `.claude/` tree by spec 058
(`specs/058-parent-skill-references/`): the owner judged the decomposition of
one initiative into independently specifiable slices no longer needed as a
standalone skill. Kept for reference only; `install.sh` does not sync this
directory, so the next install removes `~/.claude/skills/meta-spec/`. To
restore, move it back under `.claude/skills/`, re-add it to `authored_skills`
and to the skill-name patterns of checks RULE-03 and SKILL-06 in
`tests/run-config-pyramid.sh`, and drop check SKILL-08 there.
