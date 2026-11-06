#!/usr/bin/env bash
# A CLI whose public --verbose flag is documented in the README.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
cat > cli.py <<'PY'
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print a greeting.")
    parser.add_argument("--verbose", action="store_true", help="print details")
    args = parser.parse_args(argv)
    if args.verbose:
        print("starting")
    print("hello")


if __name__ == "__main__":
    main()
PY
cat > README.md <<'MD'
# greet

    python3 cli.py [--verbose]

- `--verbose`: 詳しい出力を出す。
MD
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
