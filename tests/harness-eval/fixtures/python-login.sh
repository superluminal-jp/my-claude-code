#!/usr/bin/env bash
# A login function with no logging, handling a username and a password.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
cat > auth.py <<'PY'
def login(username, password, users):
    """Return True when the user exists and the password matches."""
    user = users.get(username)
    if user is None or user["password"] != password:
        return False
    return True
PY
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
