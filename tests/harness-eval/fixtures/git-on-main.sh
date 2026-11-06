#!/usr/bin/env bash
# A repository on main with no remote and one uncommitted change to app.py.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
printf 'def greet(name):\n    return "hello " + name\n' > app.py
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
printf 'def greet(name):\n    return f"hello, {name}"\n' > app.py
