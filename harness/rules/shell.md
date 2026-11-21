---
paths:
  - "**/*.{sh,bash,zsh}"
---

# Shell scripts

- Start a Bash script with `#!/usr/bin/env bash` and `set -euo pipefail`, so that a failed command, an unset variable, or a failed pipeline stage stops the script instead of continuing on bad state.
- Quote every expansion (`"$var"`, `"$@"`, `"$(cmd)"`). Keep a command with arguments in an array and run it as `"${cmd[@]}"`.
- Create temporary files under `"${TMPDIR:-/tmp}"` with `mktemp`, and remove them in a `trap ... EXIT`.
- Check that a required command exists (`command -v name >/dev/null`) before the first step that changes anything, and fail with a message that names it.
- Before `rm -rf` or an overwrite on a path built from variables, make sure no variable can be empty (`"${dir:?}"`).
- Send diagnostics to standard error and exit non-zero on failure, so callers can rely on the exit code.
- macOS ships BSD `sed`, `date`, `readlink`, and `grep` and an old Bash 3.2. When a script must run on both macOS and Linux, keep to options both accept, or state the requirement at the top.
- Run `shellcheck` on the script when it is installed.
