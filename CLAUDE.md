# About this repository

This repository keeps the author's Claude Code user-level configuration under Git. The source is `harness/`; `bash install.sh` copies its three managed paths (`CLAUDE.md`, `rules/`, `agents/`) into `~/.claude/`, replacing each so that it matches. `settings.json` and `skills/` are not managed here.

- Files under `harness/` apply in every project once installed. Keep them universal: no facts about this repository, and nothing that duplicates a per-project workflow (Spec Kit and AI-DLC are set up in each project, not here).
- This file is for developing this repository only. It is not installed.
- Change `harness/` and run `bash install.sh`; do not edit `~/.claude/` directly. A session here runs on the installed copy, so an edit takes effect after the next install and a new session. Inside the Bash sandbox `install.sh` cannot write to `~/.claude/`, so it needs the person's approval to run outside it.
- Run `bash tests/run.sh` before committing. It checks the format of `harness/`, the `writing-check` plugin, and the installer, and writes only under `$TMPDIR`.
- `harness/plugins/writing-check/` is a Claude Code plugin, listed in `.claude-plugin/marketplace.json`. It is the one part of `harness/` that `install.sh` does not copy, because `~/.claude/plugins/` belongs to Claude Code; it is installed at user scope with `claude plugin marketplace add` and `claude plugin install`, and Claude Code reads it in place from this checkout. Its Stop hook judges text against the installed `rules/communication.md`, `rules/standards.md`, and `rules/safety.md`, so the criteria are changed there; the hook's prompt says which of their requirements can be judged from text, and adds only the criteria for language that no rule states. When a rule is added, renamed, or gains a requirement that shows in the text, update the prompt in `harness/plugins/writing-check/hooks/hooks.json`.
- Front matter uses only the fields Claude Code reads.
- There are no skills at present. Add one only for a procedure that no named standard covers; `harness/skills/<name>/SKILL.md` is checked by `tests/check_harness.py` when present, and `skills` then has to be added to `MANAGED_PATHS` in `install.sh`.
- Name the established standard instead of restating its contents, and add a specific instruction only for what no standard covers or for a mistake seen twice.
- Every always-loaded line costs context in every session. Before adding to `harness/CLAUDE.md` or to a rule without `paths`, consider a path-scoped rule.
- Keep `README.md` and `README.ja.md` in step with each other and with the contents of `harness/`.
