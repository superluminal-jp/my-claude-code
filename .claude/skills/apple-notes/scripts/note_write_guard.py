#!/usr/bin/env python3
"""Decide whether a Notes whole-body overwrite/delete may proceed, and
compute the hash it checks.

Pure Python, standard library only -- this script never calls osascript.

    hash    <stdin: plaintext>                    -> sha256 hexdigest
    decide  <stdin: plaintext> --expect-hash <h>   -> JSON {"decision": ...}

`decide` exits 0 and prints {"decision": "proceed"} on a match; it exits
non-zero and prints {"decision": "refuse", "reason": ...} on a mismatch, so a
caller can gate on the exit code alone without parsing stdout.
"""
import argparse
import hashlib
import json
import sys


def sha256_plaintext(text: str) -> str:
    """Return the SHA-256 hexdigest of `text`, encoded as UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def decide(current_plaintext: str, expect_hash: str) -> str:
    """Return "proceed" if `current_plaintext` hashes to `expect_hash`, else "refuse"."""
    return "proceed" if sha256_plaintext(current_plaintext) == expect_hash else "refuse"


def main(argv):
    parser = argparse.ArgumentParser(prog="note_write_guard.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("hash")

    decide_parser = subparsers.add_parser("decide")
    decide_parser.add_argument("--expect-hash", required=True)

    args = parser.parse_args(argv)
    stdin_text = sys.stdin.read()

    if args.command == "hash":
        print(sha256_plaintext(stdin_text))
        return 0

    if args.command == "decide":
        decision = decide(stdin_text, args.expect_hash)
        if decision == "proceed":
            print(json.dumps({"decision": "proceed"}))
            return 0
        print(json.dumps({"decision": "refuse", "reason": "note changed since last read"}))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
