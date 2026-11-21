# About this repository

This repository keeps the author's Claude Code user-level configuration under Git. The source is `harness/`; `bash install.sh` copies its four managed paths (`CLAUDE.md`, `rules/`, `skills/`, `agents/`) into `~/.claude/`, replacing each so that it matches. `settings.json` is not managed here.

- Files under `harness/` apply in every project once installed. Keep them universal: no facts about this repository, and nothing that duplicates a per-project workflow (Spec Kit and AI-DLC are set up in each project, not here).
- This file is for developing this repository only. It is not installed.
- Change `harness/` and run `bash install.sh`; do not edit `~/.claude/` directly. A session here runs on the installed copy, so an edit takes effect after the next install and a new session. Inside the Bash sandbox `install.sh` cannot write to `~/.claude/`, so it needs the person's approval to run outside it.
- Run `bash tests/run.sh` before committing. It checks the format of `harness/` and the installer, and writes only under `$TMPDIR`.
- Front matter uses only the fields Claude Code reads. A skill description says what the skill does and when to use it, in the third person, within 1,024 characters. A `SKILL.md` body stays under 500 lines, with detail in `references/` one level down.
- Every always-loaded line costs context in every session. Before adding to `harness/CLAUDE.md` or to a rule without `paths`, consider a path-scoped rule or a skill.
- `harness/skills/apply-dads-frontend/references/dads-docs/` is an unmodified copy of official documentation; do not edit it.
- Keep `README.md` and `README.ja.md` in step with each other and with the contents of `harness/`.
