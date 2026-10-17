#!/usr/bin/env bash
# Seed a small Git project with a private helper and a general README.
set -euo pipefail
mkdir -p pkg
cat > pkg/text.py <<'PY'
def _norm(value):
    return value.strip().lower()


def same(a, b):
    return _norm(a) == _norm(b)
PY
printf '# Demo project\n\nA small demo project.\n' > README.md
git init -q
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
