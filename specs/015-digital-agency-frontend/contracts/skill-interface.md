# Contract: `digital-agency-frontend`

## Discovery

- Authored path: `.claude/skills/digital-agency-frontend/SKILL.md`
- Codex discovery path: `.agents/skills/digital-agency-frontend`
- Installed Claude path: `~/.claude/skills/digital-agency-frontend/`
- Installed Codex path: `~/.agents/skills/digital-agency-frontend`
- Invocation name: `$digital-agency-frontend`

## Trigger contract

Load this skill for React and Tailwind CSS work involving one or more of:

- the Digital Agency Design System or DADS;
- Japanese government, local-government, public-service, or high-public-interest frontends that request DADS application;
- accessible implementation or remediation of DADS components and foundations;
- web dashboards using the Digital Agency dashboard guidebook;
- review of an existing React/Tailwind interface against those sources.

Do not load it for unrelated generic frontend work, non-web artifacts, or Power BI artifact generation.

## Composition contract

1. Load `coder` for any implementation or modification.
2. Load `digital-agency-frontend` for the domain workflow and quality gates.
3. Load `clarifier` when user, task, success, data meaning, constraints, or an accessibility-sensitive decision remains materially ambiguous.
4. Keep generic TDD, security, typing, and documentation obligations in `coder`; do not reproduce them in this skill.

## Execution contract

1. Inspect the target project and confirm it uses React and Tailwind CSS.
2. Capture users, task or decision, context, content/data, constraints, and measurable completion criteria.
3. Check current official sources when network access is available; record any drift from bundled references.
4. Read `references/dads-react-tailwind.md` for every matching task.
5. Read `references/dashboard-design.md` only for dashboard tasks.
6. Design and implement within project conventions, adapting official examples when applicable.
7. Verify automated project checks plus the skill's manual accessibility and information-design gates.
8. Report source freshness, deviations, verification evidence, and unresolved risks.

## Failure behavior

- Unsupported stack: report the mismatch and do not introduce React or Tailwind CSS solely to activate the skill.
- Official source unavailable: continue from the dated bundled reference, explicitly mark freshness as unverified, and avoid claims about current versions.
- Live/local conflict: use the live official source, disclose the conflict, and recommend updating the bundled reference.
- Missing product requirement: pause the affected decision and route through `clarifier`.
- Power BI request: state the web-only boundary and do not create or edit `.pbit` or Power BI theme assets.
- Accessibility failure: do not report the work complete while a known level-A or level-AA failure remains undisclosed.

## Verification contract

The package is accepted only when:

- its structural validator passes;
- the dedicated static contract suite passes;
- both repository and installed-fixture symlinks resolve;
- installer registration is idempotent;
- routing guidance and English/Japanese documentation name the skill;
- the repository's standard sync, formatting, and live-documentation suites pass.
