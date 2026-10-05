#!/usr/bin/env bash
# Seed a Git project with an accepted decision record that the requested change would reverse.
set -euo pipefail
mkdir -p docs/decisions
cat > store.py <<'PY'
import json
from pathlib import Path

DATA = Path("data.json")


def load():
    return json.loads(DATA.read_text()) if DATA.exists() else {}


def save(items):
    DATA.write_text(json.dumps(items))
PY
cat > docs/decisions/0001-store-data-in-a-json-file.md <<'MD'
---
status: accepted
date: 2026-01-10
decision-makers: Maintainers
---

# 0001. Store data in a JSON file

## Context and Problem Statement

The tool keeps a few hundred items and runs on a single machine.

## Considered Options

- JSON file
- SQLite

## Decision Outcome

Chosen option: "JSON file", because it needs no dependency and is easy to inspect.

### Consequences

- Good, because there is nothing to install.
- Bad, because concurrent writers can corrupt the file.
MD
printf '# Store\n\nItems are kept in `data.json` (see [ADR 0001](docs/decisions/0001-store-data-in-a-json-file.md)).\n' > README.md
git init -q
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
