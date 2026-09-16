#!/usr/bin/env python3
"""Unit assertions for deck.py that need no browser.

Each case is a failure mode that produced either a corrupt file python-pptx
would happily reopen, or a traceback where a warning was the contract.

Usage: assert_deck_units.py <path to deck.py>
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import zipfile
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


def main(argv: list[str]) -> int:
    deck = load(argv[1])
    from lxml import etree

    # The geometry invariant the whole pipeline rests on.
    check("UNIT-01 one px is exactly 9525 EMU", deck.EMU_PER_PX == 9525)
    check("UNIT-02 one px is exactly 0.75 pt", deck.PT_PER_PX == 0.75)
    check("UNIT-03 the canvas is exactly a 16:9 slide",
          deck.px_to_emu(1280) == 12192000 and deck.px_to_emu(720) == 6858000)

    # A font name with XML metacharacters must not corrupt the theme, and a
    # backslash in it must not be read as a regex group reference.
    for hostile in ("P&G Sans", "O'Hara Gothic", "Foo\\1Bar"):
        tokens = {"--font-family-sans": hostile}
        try:
            clr, font, _ = deck._theme_xml(tokens, {})
            etree.fromstring(font.encode("utf-8"))
            ok, detail = True, ""
        except Exception as exc:  # noqa: BLE001 - the assertion is that it survives
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        check(f"UNIT-04 a theme font named {hostile!r} produces well-formed XML", ok, detail)

    # An unresolved token must leave the default scheme alone rather than
    # substituting a remembered palette.
    clr, _, warnings = deck._theme_xml({"--color-key-900": "0017C1"}, {})
    check("UNIT-05 an unresolved token leaves the colour scheme alone", clr is None and bool(warnings))

    # The package rewrite must not damage the zip.
    from pptx import Presentation

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "t.pptx"
        Presentation().save(path)
        with zipfile.ZipFile(path) as before:
            names, kinds = before.namelist(), {i.filename: i.compress_type for i in before.infolist()}
        deck._patch_package(path, {}, {}, "ja-JP")
        with zipfile.ZipFile(path) as after:
            check("UNIT-06 the package rewrite preserves every entry", after.namelist() == names)
            check("UNIT-07 it preserves each entry's compression",
                  {i.filename: i.compress_type for i in after.infolist()} == kinds)
            check("UNIT-08 the rewritten zip is intact", after.testzip() is None)
            themes_ok = True
            for name in after.namelist():
                if name.startswith("ppt/theme/") and name.endswith(".xml"):
                    try:
                        etree.fromstring(after.read(name))
                    except Exception:  # noqa: BLE001
                        themes_ok = False
            check("UNIT-09 every rewritten theme part parses", themes_ok)
            check("UNIT-10 the presentation language is rewritten",
                  b'lang="ja-JP"' in after.read("ppt/presentation.xml"))
        check("UNIT-11 the rewritten package still opens", Presentation(path) is not None)

    # A broken image reference is an authoring mistake, not a crash.
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        cases = [
            ("a missing file", f"file://{base}/nope.png"),
            ("a non-base64 data URI", "data:image/svg+xml,%3Csvg%3E%3C/svg%3E"),
            ("an unreachable host", "http://127.0.0.1:9/none.png"),
            ("a relative path that does not exist", "nope.png"),
        ]
        for label, src in cases:
            try:
                result = deck._load_image_bytes(src, base)
                ok = result is None or isinstance(result, bytes)
                detail = ""
            except Exception as exc:  # noqa: BLE001 - the assertion is that it does not raise
                ok, detail = False, f"{type(exc).__name__}: {exc}"
            check(f"UNIT-12 {label} degrades instead of raising", ok, detail)

    # Slack widens a box away from the edge its text is anchored to.
    rect = {"x": 100.0, "y": 0.0, "w": 800.0, "h": 50.0}
    x, w = deck._slack_rect(rect, "left", 6)
    check("UNIT-13 slack keeps a left-aligned box's left edge", x == 100.0 and w == 806.0)
    x, w = deck._slack_rect(rect, "right", 6)
    check("UNIT-14 slack keeps a right-aligned box's right edge", x + w == 900.0)
    x, w = deck._slack_rect(rect, "center", 6)
    check("UNIT-15 slack keeps a centred box's centre", x + w / 2 == 500.0)

    # A deck with no slides must report, not raise.
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty.html"
        empty.write_text("<!DOCTYPE html><html lang='ja'><body><p>no slides</p></body></html>", encoding="utf-8")
        try:
            code = deck.main(["pptx", str(empty), "-o", str(Path(tmp) / "o.pptx"), "--allow-findings"])
            ok, detail = code != 0, f"returned {code}"
        except SystemExit as exc:
            ok, detail = exc.code != 0, f"exited {exc.code}"
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {exc}"
        check("UNIT-16 a deck with no slides reports instead of crashing", ok, detail)

    print(f"\n{CHECKS - len(FAILURES)} passed, {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
