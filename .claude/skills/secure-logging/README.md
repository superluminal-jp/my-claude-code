# Secure Logging — Claude Code Skill and plugin

A Claude Code Skill for implementing, changing, or reviewing application logging against the OWASP Logging Cheat Sheet, OWASP ASVS 5.0.0 V16, and the related CWE entries. It is a domain overlay: it supplements an implementation, review, or documentation task rather than replacing it. The same folder is also a Claude Code plugin; it registers no hooks (see [How checks work](#how-checks-work)).

## Install

Personal installation (all your projects):

```bash
cp -R secure-logging ~/.claude/skills/
```

Project installation (everyone who clones the repository):

```bash
mkdir -p .claude/skills
cp -R secure-logging .claude/skills/
```

Because the folder contains `.claude-plugin/plugin.json`, Claude Code loads it from either location as a skills-directory plugin (`secure-logging@skills-dir`), and the Skill (`SKILL.md`) becomes available. `claude plugin list` shows it under *Skills-directory plugins*.

- A personal copy shadows a project copy, because both carry the same plugin name; `claude plugin list` then reports the project copy as not loaded. To use the project copy, rename or move the personal one.
- To disable the plugin while keeping the files, set `"enabledPlugins": {"secure-logging@skills-dir": false}` in a settings file.

Other ways to load it: `claude --plugin-dir ./secure-logging` for one session, or publish it through a plugin marketplace. When loaded from those sources, the Skill is named `/secure-logging:secure-logging`.

## Requirements

- Claude Code. The plugin contains only Markdown and a manifest, so it needs no runtime or dependency.
- The checks run with the target project's own test runner, linters, and type checkers.

## Layout

- `SKILL.md` — scope, workflow, edge cases, and the completion check.
- `README.md`, `README.ja.md` — this guide in English and Japanese; keep the two in sync.
- `.claude-plugin/plugin.json` — plugin manifest.
- `references/logging-checklist.md` — the sources and the checklist: group A items, judged from code (`LOG-INV`, `LOG-EVT`, `LOG-ATT`, `LOG-DATA`, `LOG-INJ`, `LOG-ERR`, `LOG-CFG`, `LOG-TST`), and group B operational items (`LOG-OPS`).

## Scope

- Use it when code adds or modifies log output, security event logging, audit trails, error handling that logs, or logging configuration, and when asked whether logging follows best practice.
- Do not use it for log infrastructure operations (SIEM, retention, alert tuning), observability or metrics design unrelated to security events, or changes that touch no logging behavior.
- Standards outside the checklist, such as ISO/IEC 27002, PCI DSS, and NIST SP 800-53, are not mapped, because no primary text was read for them.

## Modes

| Mode | When | Workflow steps |
|---|---|---|
| Review | The request asks whether logging is right | 2 (inventory) and 5 (check); nothing changes |
| Implement or fix | The request asks for a logging change; fixing a finding counts | 2 to 6 |

When the request names no target, the Skill uses the working-tree diff if there is one, otherwise the whole repository, and says so in the report.

## How checks work

`SKILL.md` is authoritative for the workflow and `references/logging-checklist.md` for the requirements; this section summarizes how they are checked.

Checks run only when the Skill is invoked: Claude follows `SKILL.md` and evaluates the code in scope against the checklist. Nothing runs automatically, because the plugin registers no hooks. The mechanical checks are the test Claude writes first, when the contract is automatable, and the project's own tests, linters, and type checks. Every other status comes from Claude's reading of the code, so in implement mode the check is a self-check.

### Checks in the workflow

| Workflow step | What is checked | How |
|---|---|---|
| 2. Inventory | The shared logging entry point, direct print or ad hoc logging calls, events already logged, redaction helpers, and logging tests | Claude reads the code; the inventory is the baseline for both modes |
| 4. Implement | The event, its required attributes, redaction of a secret sentinel, and neutralization of input with CR, LF, and delimiter characters | A test written first and observed to fail, where the contract is automatable; otherwise the current behavior is recorded with how the change will be checked |
| 4. Implement | The project's tests, linters, and type checks | Claude runs them before step 5 |
| 5. Check | Every checklist item for the scope | Claude gives each item one status, with evidence |
| 5. Check (implement mode) | A Fail in code the change adds or modifies | It blocks the report: Claude fixes it and checks again, and after two rounds that leave the same Fail reports it as remaining. A Fail in untouched code is reported as pre-existing and fixed only on request |
| 5. Check (implement mode) | Independence, when the scope handles authentication, payment, or personal data | A subagent should evaluate the group A items against the diff in a fresh context; without one, the report says the result is a self-check only |

### Statuses

| Status | Meaning | Evidence |
|---|---|---|
| Pass | Satisfied | `file:line` or the test that shows it |
| Fail | Violated or missing for code in scope | The location and the item ID |
| N/A | The condition does not occur in scope | Why |
| Unverified | Group B, or group A with no available evidence | What evidence would settle it |

Group B items (storage permissions, transport, retention, clock synchronization, tamper detection, alerting, network separation) are never marked Pass from application code. They are judged only when infrastructure code or logger configuration in the repository settles them, and that file is cited. Unverified is never turned into Pass by inference.

### Report and completion

The report leads with the verdict: counts of Fail and Unverified and the most serious failures, with remaining and pre-existing Fail apart in implement mode. Then come the item table in checklist order (N/A items may share one row per checklist section that lists their IDs), the changes made with the checks run and their results, the group B evidence the user must supply, and what was not checked.

An implementation is complete only when every item has a status, `LOG-DATA-1`, `LOG-DATA-2`, `LOG-INJ-1`, and `LOG-INJ-4` are Pass or N/A for the code the change adds or modifies, the test written first passes, and the project's checks still pass. If one of those items is still Fail after the stop condition, the report says the work is incomplete.

### What the plugin does not enforce

| Mechanism | In this plugin |
|---|---|
| Hooks | None; the workflow runs only when the Skill is invoked |
| Behavior evals | None bundled; whether a model follows the workflow is not measured automatically |
| Independent review | Only the fresh-context evaluation above, and only for authentication, payment, or personal-data scope |

Whether each status is right rests on Claude's reading of the code, the test written first, the fresh-context evaluation where it applies, and human review.

## Validation

From this folder:

```bash
claude plugin validate --strict .
```

## Security

The plugin contains only Markdown and a manifest: no scripts, hooks, or executables. The Skill tells Claude never to log secrets, tokens, session identifiers, or personal data in clear text, and never to mark an operational item passed from application code.
