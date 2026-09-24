# Contract: `model-routing.md` and its synchronized artifacts

The interface this feature exposes is a file that the harness loads every session, plus the checks and documents that describe it.

## 1. Rule file (English)

Path: `.claude/rules/model-routing.md`. No frontmatter (unconditional loading, like siblings).

| Order | Element | Required content |
|---|---|---|
| 1 | `# Model and Effort Routing` | — |
| 2 | Purpose paragraph | lowest capability and lowest effort that reliably completes each independent unit; route by required judgment, ambiguity, dependency breadth, blast radius, not size alone |
| 3 | `## Capability tiers` | four-row table (tier · alias · use when) and the decide / implement / execute-mechanically line |
| 4 | `## Escalation and hand-back` | escalate only on the four conditions; size or repetition → decompose or parallelize; hand bounded work back down once uncertainty is resolved |
| 5 | `## Effort and delegation` | capability and effort are separate controls; five levels with `medium` default; `xhigh`/`max` only where useful and supported; choose subagent model and effort deliberately; direct execution for trivial sequential or single-file work |
| 6 | Closing sufficiency sentence | routing is sufficient when each unit's tier and effort follow from the stated basis and any escalation names one of the closed conditions |

Prohibited content (mechanically checked by RULE-02..04): `.claude/`, `rules/`, `skills/`, `SKILL.md`, `settings.json`, `.mcp.json`, `/speckit-*`, any authored skill name in backticks, any sibling rule filename. Also prohibited: content owned by another rule (authorization, verification, requirements certainty).

Size: ≤ 40 lines.

## 2. Japanese counterpart

Path: `.claude-ja/rules/model-routing.md`. Same elements and order. Headings are the English heading followed by a Japanese gloss in full-width parentheses; body in Japanese. Aliases, effort level names, and tier names in the table remain as in English.

## 3. Structure check

`tests/run-config-pyramid.sh`:

| ID | Assertion | Change |
|---|---|---|
| RULE-01 | the set of files in the rules directory equals exactly the six names, alphabetical | edit (list + name) |
| RULE-02..04 | path/skill/sibling-name scans over the whole directory | none; now also cover the new file |
| RULE-11 | `model-routing.md` matches `tier|capabilit|effort` | new |

## 4. Documentation synchronization

| Artifact | Required state |
|---|---|
| `README.md` | tree lists `model-routing.md` with a one-line purpose; `rules/` comment says 6 independent concerns; rules paragraph names the routing concern |
| `README.ja.md` | rules paragraph names the routing concern in Japanese |
| `docs/claude-config-design.md` | §3.1 heading says six; a row records what `model-routing.md` leaves out (model IDs, prices, limits, and setting syntax → harness and vendor documentation); §5 body and layer table say six |

## 5. Non-regression

`git diff` against `main` must show no change to the existing five rule files, `.claude/CLAUDE.md`, any skill, `install.sh`, `specs/001`–`039`, or `docs/adr/`.
