#!/usr/bin/env python3
"""Check and preview a 16:9 HTML slide deck built on the Digital Agency Design System.

The deck is one HTML document whose slides are fixed 1280x720 CSS pixel
canvases. Chromium lays it out, and scripts/check_slides.js reads the measured
result, so every finding is about what the browser actually rendered.

Subcommands:
    lint      report structure, document, layout, legibility and accessibility findings
    preview   write one PNG per slide

Requires: playwright (with chromium) — see scripts/setup.sh.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "safe_area_px": 32,
    "min_font_px": 14,
    "body_font_px": 18,
    "max_list_items": 5,
    "max_slide_items": 10,
    # Cover, premises, answer, at most five key-line points, and a closing.
    "max_slides": 9,
    # The Digital Agency's colour foundation removes WCAG's large-text
    # relaxation: all text clears 4.5:1 whatever its size.
    "text_contrast": 4.5,
    "nontext_contrast": 3.0,
    "slide_selector": ".sld-slide",
    "secondary_selector": (
        "footer, figcaption, caption, small, .dads-heading__shoulder, .dads-chip-label, "
        ".sld-kpi__label, .sld-steps__index"
    ),
}


@dataclass
class Inspection:
    deck: dict[str, Any] | None
    slides: list[dict[str, Any]]
    findings: list[dict[str, Any]]
    previews: list[bytes]


def inspect(deck_path: Path, options: dict[str, Any], *, want_previews: bool) -> Inspection:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:  # pragma: no cover - environment guard
        sys.exit("playwright is not installed. Run scripts/setup.sh first.")

    script = (Path(__file__).parent / "check_slides.js").read_text(encoding="utf-8")

    launch_kwargs: dict[str, Any] = {}
    executable = options.get("chromium_path") or os.environ.get("DECK_CHROMIUM")
    if executable:
        launch_kwargs["executable_path"] = executable

    with sync_playwright() as pw:
        browser = pw.chromium.launch(**launch_kwargs)
        context = browser.new_context(
            viewport={"width": int(options["viewport_px"]), "height": 720},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(deck_path.resolve().as_uri(), wait_until="load")
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(options["settle_ms"])
        page.add_script_tag(content=script)
        result = page.evaluate("(opts) => window.__checkDeck(opts)", options)

        previews: list[bytes] = []
        if want_previews:
            handles = page.query_selector_all(options["slide_selector"])
            previews = [handle.screenshot() for handle in handles]

        browser.close()

    return Inspection(
        deck=result["deck"],
        slides=result["slides"],
        findings=result["findings"],
        previews=previews,
    )


def report_findings(findings: Iterable[dict[str, Any]], stream=sys.stderr) -> int:
    """Print one line per finding and a summary; return the number of errors."""
    findings = sorted(findings, key=lambda f: (f["slide"], f["level"] != "error", f["code"]))
    errors = 0
    for finding in findings:
        if finding["level"] == "error":
            errors += 1
        location = finding.get("element") or ""
        excerpt = (finding.get("text") or "").strip()
        suffix = f"  [{location} {excerpt!r}]" if location else ""
        where = f"slide {finding['slide']:>2}" if finding["slide"] else "document"
        print(f"{where}  {finding['level']:<5} {finding['code']:<16} {finding['message']}{suffix}", file=stream)
    warnings = len(findings) - errors
    print(f"\n{errors} error(s), {warnings} warning(s)", file=stream)
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["lint", "preview"])
    parser.add_argument("deck", type=Path, help="path to the deck HTML file")
    parser.add_argument("-o", "--out", type=Path, help="output directory (preview)")
    parser.add_argument("--json", action="store_true", help="lint: print the slides and findings as JSON on stdout")
    parser.add_argument("--selector", default=DEFAULTS["slide_selector"], help="CSS selector matching one slide")
    parser.add_argument(
        "--secondary-selector",
        default=DEFAULTS["secondary_selector"],
        help="CSS selector for content exempt from the body-size warning",
    )
    parser.add_argument("--safe-area", type=float, default=DEFAULTS["safe_area_px"], help="safe-area inset in px")
    parser.add_argument("--min-font", type=float, default=DEFAULTS["min_font_px"], help="minimum font size in px")
    parser.add_argument("--body-font", type=float, default=DEFAULTS["body_font_px"], help="comfortable body size in px")
    parser.add_argument("--max-list-items", type=int, default=DEFAULTS["max_list_items"], help="items in any one list")
    parser.add_argument(
        "--max-slide-items", type=int, default=DEFAULTS["max_slide_items"], help="list items on a slide, pooled"
    )
    parser.add_argument(
        "--max-slides", type=int, default=DEFAULTS["max_slides"], help="slides in the main deck, appendix excluded"
    )
    parser.add_argument(
        "--text-contrast", type=float, default=DEFAULTS["text_contrast"], help="minimum contrast ratio for text"
    )
    parser.add_argument(
        "--nontext-contrast",
        type=float,
        default=DEFAULTS["nontext_contrast"],
        help="minimum contrast ratio for borders and rules",
    )
    parser.add_argument("--viewport", type=int, default=1440, help="browser viewport width in px")
    parser.add_argument("--settle-ms", type=int, default=250, help="wait after load before measuring")
    parser.add_argument(
        "--chromium",
        default=None,
        metavar="PATH",
        help="Chromium executable to measure with (default: Playwright's own; env DECK_CHROMIUM)",
    )
    return parser


def _options(args: argparse.Namespace) -> dict[str, Any]:
    options = dict(DEFAULTS)
    options.update(
        {
            "safe_area_px": args.safe_area,
            "min_font_px": args.min_font,
            "body_font_px": args.body_font,
            "max_list_items": args.max_list_items,
            "max_slide_items": args.max_slide_items,
            "max_slides": args.max_slides,
            "text_contrast": args.text_contrast,
            "nontext_contrast": args.nontext_contrast,
            "slide_selector": args.selector,
            "secondary_selector": args.secondary_selector,
            "viewport_px": args.viewport,
            "settle_ms": args.settle_ms,
            "chromium_path": args.chromium,
        }
    )
    return options


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.deck.is_file():
        print(f"no such deck: {args.deck}", file=sys.stderr)
        return 2

    inspection = inspect(args.deck, _options(args), want_previews=args.command == "preview")

    if args.command == "lint" and args.json:
        payload = {"deck": inspection.deck, "slides": inspection.slides, "findings": inspection.findings}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        errors = sum(1 for finding in inspection.findings if finding["level"] == "error")
        return 1 if errors else 0

    errors = report_findings(inspection.findings)
    if inspection.deck is None:
        return 1

    if args.command == "preview":
        out_dir = args.out or args.deck.parent / "preview"
        out_dir.mkdir(parents=True, exist_ok=True)
        for index, blob in enumerate(inspection.previews, start=1):
            (out_dir / f"slide-{index:02d}.png").write_bytes(blob)
        print(f"wrote {len(inspection.previews)} PNG(s) to {out_dir}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
