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


def lint(python: str, deck_cli: str, deck: Path, *extra: str) -> tuple[int, dict]:
    result = subprocess.run(
        [python, deck_cli, "lint", str(deck), "--json", *extra],
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
    check(
        "LINT-03 the report names each slide's role, in the order of a paper",
        layouts == ["title", "answer", "premise", "method", "point", "point", "discussion", "closing", "appendix"],
        str(layouts),
    )

    status, report = lint(python, deck_cli, fixture_dir / "structure.html")
    found = codes(report)
    check(
        "LINT-04 structure breaches are reported as late-answer, part-order and appendix-order only; length is not a breach",
        set(found) == {"late-answer", "part-order", "appendix-order"},
        str(dict(found)),
    )
    check(
        "LINT-18 a part out of the paper's order is reported on the slide that breaks it, the method after a result",
        sorted(f["slide"] for f in report.get("findings", []) if f["code"] == "part-order") == [4],
        str([f for f in report.get("findings", []) if f["code"] == "part-order"]),
    )
    _, report = lint(python, deck_cli, fixture_dir / "structure.html", "--max-slides", "9")
    check(
        "LINT-04b a budget asked for with --max-slides is reported as deck-long",
        "deck-long" in codes(report),
        str(dict(codes(report))),
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
        found == {("tracker", 5), ("tracker-missing", 6)},
        str(sorted(found)),
    )
    check("LINT-14 a wrong tracker is an error", status != 0, f"exit {status}")

    status, report = lint(python, deck_cli, fixture_dir / "continues.html")
    found = {(f["code"], f["slide"]) for f in report.get("findings", [])}
    check(
        "LINT-17 continued premises and a continued point share their part; only the continuation marking the wrong part is reported",
        found == {("tracker", 9)},
        str(sorted(found)),
    )

    status, report = lint(python, deck_cli, fixture_dir / "premise-first.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-19 a deck with one premise slide and the answer third reports the late summary and the missing parts, and nothing else",
        found == [("late-answer", 3), ("missing-part", 0), ("missing-part", 0)],
        str(found),
    )
    missing = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "missing-part")
    check(
        "LINT-20 each missing part is named: the method and the discussion, not the premises or the conclusion",
        'data-layout="method"' in missing
        and 'data-layout="discussion"' in missing
        and 'data-layout="premise"' not in missing
        and 'data-layout="closing"' not in missing,
        missing,
    )
    check("LINT-21 order findings are warnings, so lint exits zero", status == 0, f"exit {status}")

    status, report = lint(python, deck_cli, fixture_dir / "paper-order.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-22 each part out of order is reported once, on the slide that breaks the order, and a slide after the appendix only as appendix-order",
        found == [("appendix-order", 12), ("part-order", 4), ("part-order", 6), ("part-order", 10)],
        str(found),
    )

    status, report = lint(python, deck_cli, fixture_dir / "cover-only.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-23 a deck that is only its cover reports the missing summary and the five missing parts, and nothing else",
        found == [("late-answer", 0)] + [("missing-part", 0)] * 5,
        str(found),
    )
    missing = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "missing-part")
    absent = [role for role in ("premise", "method", "point", "discussion", "closing") if f'data-layout="{role}"' not in missing]
    check("LINT-24 every missing part is named, the results included", not absent, f"not named: {absent}")
    check(
        "LINT-28a a deck that declares no form is checked as a paper deck",
        report.get("deck", {}).get("form") == "paper",
        str(report.get("deck")),
    )

    status, report = lint(python, deck_cli, fixture_dir / "business.html")
    check(
        "LINT-25 a business deck with one introduction slide, the answer third and no method reports nothing",
        report.get("findings") == [],
        str(report.get("findings"))[:400],
    )
    check(
        "LINT-28b the report names the form the deck declares",
        report.get("deck", {}).get("form") == "business",
        str(report.get("deck")),
    )

    status, report = lint(python, deck_cli, fixture_dir / "business-late.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-26 a business deck with two introduction slides reports the late answer and the missing next step, and nothing else",
        found == [("late-answer", 4), ("missing-part", 0)],
        str(found),
    )
    missing = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "missing-part")
    check(
        "LINT-26b the business form requires the next step but not the premises, the method or the discussion",
        'data-layout="closing"' in missing
        and not any(f'data-layout="{role}"' in missing for role in ("premise", "method", "discussion")),
        missing,
    )

    status, report = lint(python, deck_cli, fixture_dir / "form-unknown.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    missing = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "missing-part")
    check(
        "LINT-27 an unknown form is reported once and the paper form's rules apply, so the missing method is reported",
        found == [("form-unknown", 0), ("missing-part", 0)]
        and 'data-layout="method"' in missing
        and report.get("deck", {}).get("form") == "paper",
        f"{found} {missing} {report.get('deck')}",
    )

    status, report = lint(python, deck_cli, fixture_dir / "form-misplaced.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-29 a form declared on another element than <body> is reported, and the deck is checked as a paper deck",
        found == [("form-unknown", 0), ("late-answer", 3), ("missing-part", 0), ("missing-part", 0)]
        and report.get("deck", {}).get("form") == "paper",
        f"{found} {report.get('deck')}",
    )

    status, report = lint(python, deck_cli, fixture_dir / "business-bare.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    missing = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "missing-part")
    check(
        "LINT-30 a business deck may put its answer on slide 2 without an introduction, and needs no premise, method or discussion, but needs its points",
        found == [("missing-part", 0)] and 'data-layout="point"' in missing,
        f"{found} {missing}",
    )

    status, report = lint(python, deck_cli, fixture_dir / "business-order.html")
    found = sorted((f["code"], f["slide"]) for f in report.get("findings", []))
    check(
        "LINT-31 in the business form a late answer, a premise after the answer, a part out of order and a slide after the appendix are each reported once",
        found == [("appendix-order", 9), ("late-answer", 3), ("part-order", 4), ("part-order", 6)],
        str(found),
    )
    intro = " ".join(f["message"] for f in report.get("findings", []) if f["code"] == "part-order" and f["slide"] == 4)
    check("LINT-31b the premise after the answer is reported as a misplaced introduction", "introduction" in intro, intro)

    status, report = lint(python, deck_cli, fixture_dir / "clean.html")
    check(
        "LINT-28c a deck that declares the paper form is checked as one",
        report.get("deck", {}).get("form") == "paper",
        str(report.get("deck")),
    )

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
