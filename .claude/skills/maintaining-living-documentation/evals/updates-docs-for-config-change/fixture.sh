#!/usr/bin/env bash
# Seed a small Git project whose configuration default is documented in two places.
set -euo pipefail
mkdir -p docs
cat > app.py <<'PY'
import os


def timeout_seconds():
    t = int(os.environ.get("APP_TIMEOUT", "30"))
    return t
PY
cat > docs/configuration.md <<'MD'
# Configuration

| Variable | Default | Meaning |
|---|---|---|
| `APP_TIMEOUT` | `30` | Request timeout in seconds |
MD
printf '# Changelog\n\n## Unreleased\n' > CHANGELOG.md
git init -q
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
