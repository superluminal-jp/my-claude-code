# Archived: the delivery gates

Retired from the managed `harness/` tree by
[ADR-0029](../../docs/adr/0029-base-delivery-on-ai-dlc-workflows-v2.md): the
owner chose AI-DLC Workflows v2 as the base for carrying a change from intent
to acceptance, and the harness keeps only what complements it. Kept for
reference only; `install.sh` does not sync this directory, so the next install
removes the four skills from `~/.claude/skills/`.

- `skills/deliver-change/`, `skills/specify-requirements/`,
  `skills/verify-change/`, `skills/define-product-strategy/`: the skills as
  they stood when they were retired, with their `metadata.role` declarations
  of the earlier role tree.
- `tests/`: the checks that ran only against those skills
  (`run-specify-requirements-skill.sh`, `run-verify-change-skill.sh`, and the
  three `assert_*.py` flows they called). Their paths still point at
  `harness/skills/`, so they do not run from here.
- `05-dynamic-deliver-change.md`: the dynamic diagram of the parent skill,
  formerly in `docs/harness/skill-map/`.

To restore a skill, move it back under `harness/skills/`, replace
`metadata.role` with `metadata.phase` and the tag at the end of its
`description`, add it to `docs/harness/capability-map.json` and the evaluation
scenarios, move its tests back, and drop check SKILL-09 in
`tests/run-config-pyramid.sh`.
