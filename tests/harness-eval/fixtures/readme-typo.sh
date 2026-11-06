#!/usr/bin/env bash
# A README with one typo.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
printf '# tool\n\nThis tool reads teh config file and prints it.\n' > README.md
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
