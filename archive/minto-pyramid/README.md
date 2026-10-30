# Archived: `minto-pyramid` plugin

Retired from the managed `.claude/` tree by spec 055 and replaced by the authored skill `pyramid-structure`, which keeps this plugin's always-on scope and carries over its completion check, templates and eval cases, reverses its rule against revealing chain-of-thought into a rule that shows how each answer was reached, and adds a mechanical structure checker that runs before each substantive output.

Kept for reference only; `install.sh` does not sync this directory. To restore, move `.claude/skills/minto-pyramid/` back under the repository's `.claude/skills/` and remove `pyramid-structure`, so that only one always-on Minto skill is installed.

The directory layout mirrors the original repository paths.
