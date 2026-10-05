# Purpose of this repository

This repository manages the author's Claude Code **user-level settings** (what lives in `~/.claude/`) under Git. The source of truth is `.claude/` here; `install.sh` synchronizes its managed parts (`rules/`, `skills/`, `agents/`, `commands/`, `CLAUDE.md`, and a merge of `settings.json`) to `~/.claude/`, plus installs this repository's Claude Code plugins. See `README.md` for the full contract.

When working here:

- Files under `.claude/` are the user-level configuration itself, not project config for this repo. Editing them changes the behavior of Claude Code in every project once installed, so keep them universal and free of repo-specific facts.
- This file is the only place for facts about developing this repository. It is not synced to `~/.claude/`; do not move its content into `.claude/CLAUDE.md`.
- Never edit `~/.claude/` directly; change `.claude/` here and re-run `install.sh`.
- Keep `README.md` and `README.ja.md` in sync with any change to the managed paths or installer behavior.

@.claude/CLAUDE.md
