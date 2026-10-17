#!/usr/bin/env bash
# Seed a small Git project whose package has no documentation of its own.
set -euo pipefail
mkdir -p pkg
cat > pkg/__init__.py <<'PY'
PY
cat > pkg/cache.py <<'PY'
def key(name):
    return name.strip().lower()
PY
printf '# Demo project\n\nA small demo project.\n' > README.md
git init -q
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
