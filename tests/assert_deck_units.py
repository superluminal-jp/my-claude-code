#!/usr/bin/env python3
"""Unit assertions for deck.py's command line and reporting.

Usage: assert_deck_units.py <path to deck.py>
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from pathlib import Path

FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if ok:
        print(f"PASS {name}")
    else:
        FAILURES.append(name)
        print(f"FAIL {name}{f' — {detail}' if detail else ''}")


def load(path: str):
    spec = importlib.util.spec_from_file_location("deck", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["deck"] = module  # dataclasses resolves annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def exits_with_usage_error(deck, argv: list[str]) -> bool:
    stderr, sys.stderr = sys.stderr, io.StringIO()
    try:
        deck.build_parser().parse_args(argv)
    except SystemExit as exc:
        return exc.code == 2
    finally:
        sys.stderr = stderr
    return False


def main(argv: list[str]) -> int:
    deck = load(argv[1])

    # PowerPoint conversion and its debugging dump were removed (ADR-0018).
    check("UNIT-01 the removed pptx subcommand is rejected", exits_with_usage_error(deck, ["pptx", "deck.html"]))
    check("UNIT-02 the removed ir subcommand is rejected", exits_with_usage_error(deck, ["ir", "deck.html"]))

    # The slide budget is derived from the tree: cover, premise, answer, up to
    # five key-line points and a closing.
    check("UNIT-03 the default main-deck budget is nine slides", deck.DEFAULTS["max_slides"] == 9)
    args = deck.build_parser().parse_args(["lint", "deck.html", "--max-slides", "6"])
    check("UNIT-04 --max-slides reaches the checker's options", deck._options(args)["max_slides"] == 6)

    findings = [
        {"slide": 2, "level": "warn", "code": "dense", "message": "m"},
        {"slide": 1, "level": "error", "code": "contrast", "message": "m"},
        {"slide": 0, "level": "error", "code": "no-lang", "message": "m"},
    ]
    stream = io.StringIO()
    check("UNIT-05 report_findings counts errors, not warnings", deck.report_findings(findings, stream) == 2)
    check("UNIT-06 the summary line states both counts", "2 error(s), 1 warning(s)" in stream.getvalue(), stream.getvalue())

    # A missing deck is a usage mistake, not a traceback.
    try:
        code = deck.main(["lint", "/nonexistent/deck.html"])
        ok, detail = code != 0, f"returned {code}"
    except SystemExit as exc:
        ok, detail = exc.code not in (0, None), f"exited {exc.code}"
    except Exception as exc:  # noqa: BLE001 - the assertion is that it does not raise
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    check("UNIT-07 a missing deck reports instead of crashing", ok, detail)

    # A page with no slides must report, not raise.
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty.html"
        empty.write_text("<!DOCTYPE html><html lang='ja'><title>t</title><body><p>no slides</p></body></html>", encoding="utf-8")
        try:
            code = deck.main(["lint", str(empty)])
            ok, detail = code != 0, f"returned {code}"
        except SystemExit as exc:
            ok, detail = exc.code not in (0, None), f"exited {exc.code}"
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        check("UNIT-08 a page with no slides reports instead of crashing", ok, detail)

    print(f"\n{CHECKS - len(FAILURES)} passed, {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
