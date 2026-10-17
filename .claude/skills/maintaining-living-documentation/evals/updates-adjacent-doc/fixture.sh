#!/usr/bin/env bash
# Seed a small Git project whose tool is documented by the README in its own directory.
set -euo pipefail
mkdir -p tools
cat > tools/convert.py <<'PY'
import argparse


def main():
    parser = argparse.ArgumentParser(description="Convert a file")
    parser.add_argument("path")
    parser.add_argument("--format", default="json", help="output format")
    args = parser.parse_args()
    print(f"converting {args.path} to {args.format}")
    print("done")


if __name__ == "__main__":
    main()
PY
cat > tools/README.md <<'MD'
# convert

Converts a file to another format.

| Option | Meaning |
|---|---|
| `--format` | Output format (`json` by default) |
MD
git init -q
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
