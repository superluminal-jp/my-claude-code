#!/usr/bin/env python3
"""Assert what `deck.py lint --json` reports for each self-contained fixture.

The fixtures carry their own CSS and no Digital Agency assets, so these checks
need a browser but no network. Each case states both what must be reported and
what must not be: a checker that reports everything would pass a presence-only
test.

Usage: assert_lint.py <python> <path to deck.py> <fixture dir>
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
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


def lint(python: str, deck_cli: str, deck: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [python, deck_cli, "lint", str(deck), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {"findings": [], "slides": [], "error": result.stdout + result.stderr}
    return result.returncode, report


def codes(report: dict) -> Counter:
    return Counter(f["code"] for f in report.get("findings", []))


def main(argv: list[str]) -> int:
    python, deck_cli, fixture_dir = argv[1], argv[2], Path(argv[3])

    status, report = lint(python, deck_cli, fixture_dir / "clean.html")
    check("LINT-01 a deck that breaks no rule reports nothing", report.get("findings") == [], str(report)[:400])
    check("LINT-02 and lint exits zero", status == 0, f"exit {status}")
    layouts = [slide["layout"] for slide in report.get("slides", [])]
    check("LINT-03 the report names each slide's role", layouts[:3] == ["title", "premise", "answer"], str(layouts))

    status, report = lint(python, deck_cli, fixture_dir / "structure.html")
    found = codes(report)
    check(
        "LINT-04 structure breaches are reported as deck-long, late-answer and appendix-order only",
        set(found) == {"deck-long", "late-answer", "appendix-order"},
        str(dict(found)),
    )
    check("LINT-05 structure findings are warnings, so lint exits zero", status == 0, f"exit {status}")

    status, report = lint(python, deck_cli, fixture_dir / "document.html")
    found = codes(report)
    expected_errors = {
        "no-lang",
        "no-title",
        "h1-count",
        "heading-skip",
        "no-heading",
        "no-alt",
        "table-no-header",
        "contrast",
        "font-too-small",
        "off-slide",
        "clipped",
        "size-mismatch",
    }
    missing = expected_errors - set(found)
    check("LINT-06 every document and legibility breach is reported", not missing, f"missing {sorted(missing)}")
    levels = {f["code"]: f["level"] for f in report.get("findings", [])}
    wrong = sorted(code for code in expected_errors & set(levels) if levels[code] != "error")
    check("LINT-07 they are reported as errors", not wrong, f"not errors: {wrong}")
    check("LINT-08 and lint exits non-zero", status != 0, f"exit {status}")
    expected_warnings = {"dense", "nontext-contrast", "safe-area"}
    missing = expected_warnings - set(found)
    check("LINT-09 density, border contrast and the safe area are warned about", not missing, f"missing {sorted(missing)}")
    check(
        "LINT-10 a decorative svg is not reported, so only the image and the unnamed svg lack alternatives",
        found["no-alt"] == 2,
        str(found["no-alt"]),
    )
    check("LINT-11 hidden notes are not checked, so one small text is reported", found["font-too-small"] == 1, str(found["font-too-small"]))
    check("LINT-12 a padded inline highlight is not reported as clipped", found["clipped"] == 1, str(found["clipped"]))

    status, report = lint(python, deck_cli, fixture_dir / "tracker.html")
    found = {(f["code"], f["slide"]) for f in report.get("findings", [])}
    check(
        "LINT-13 a tracker marking the wrong part, and a slide without one, are the only findings",
        found == {("tracker", 4), ("tracker-missing", 5)},
        str(sorted(found)),
    )
    check("LINT-14 a wrong tracker is an error", status != 0, f"exit {status}")

    status, report = lint(python, deck_cli, fixture_dir / "marking.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-15 a differing, missing, misplaced, unknown or mislabelled marking is each reported, and nothing else",
        found == [("marking", 2), ("marking", 4), ("marking", 5), ("marking", 6), ("marking-missing", 3)],
        str(found),
    )
    status, report = lint(python, deck_cli, fixture_dir / "document.html")
    check(
        "LINT-16 a deck with no marking at all is reported once, for the whole document",
        [f["slide"] for f in report.get("findings", []) if f["code"] == "marking-missing"] == [0],
        str([f for f in report.get("findings", []) if f["code"] == "marking-missing"]),
    )

    print(f"\n{CHECKS - len(FAILURES)} passed, {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
