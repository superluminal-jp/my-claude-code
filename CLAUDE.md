# Purpose of this repository

This repository manages the author's Claude Code **user-level settings** (what lives in `~/.claude/`) under Git. The source of truth is `harness/` here; `install.sh` synchronizes its managed parts (`rules/`, `skills/`, `agents/`, `commands/`, `CLAUDE.md`, and a merge of `settings.json`) to `~/.claude/`, plus installs this repository's Claude Code plugins. See `README.md` for the full contract.

When working here:

- Files under `harness/` are the user-level configuration itself, not project config for this repo. Editing them changes the behavior of Claude Code in every project once installed, so keep them universal and free of repo-specific facts.
- This file is the only place for facts about developing this repository. It is not synced to `~/.claude/`; do not move its content into `harness/CLAUDE.md`.
- Never edit `~/.claude/` directly; change `harness/` here and re-run `install.sh`. A session in this repository runs on the installed copy, so an edit under `harness/` takes effect only after the next install.
- This repository's own `.claude/` holds no managed configuration. Do not put the source back there: a sandboxed Bash command cannot write under it, and files there load a second time as project configuration.
- Everything a skill or a test runs must work inside the Claude Code Bash sandbox: temporary files under `$TMPDIR` (never a bare `mktemp`), no write outside the repository, no network unless the skill declares its hosts. `bash tests/run-harness-skills.sh` checks every skill against this contract.
- Decision records live in `docs/adr/` as `NNNN-<kebab-title>.md` with four-digit numbers. Front matter is `status` (`Proposed`, `Accepted`, `Deprecated`, or `Superseded by NNNN`), `date` (`YYYY-MM-DD`), and `deciders`; the heading is `# NNNN. <title>`, and the body is written in Japanese.
- Keep `README.md` and `README.ja.md` in sync with any change to the managed paths or installer behavior.
