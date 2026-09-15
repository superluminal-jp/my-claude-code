#!/usr/bin/env python3
"""Assert the slide extractor's classification and geometry against a fixture.

Each case is a defect that once shipped silently. The fixture is static and
needs no network, so this runs wherever Chromium and python-pptx are available.

Usage: assert_classification.py <ir.json> [built.pptx]
"""

from __future__ import annotations

import json
import re
import sys
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
        FAILURES.append(f"{name}{f' — {detail}' if detail else ''}")
        print(f"FAIL {name}{f' — {detail}' if detail else ''}")


def slide_by_case(ir: dict, case: str) -> dict:
    for slide in ir["slides"]:
        if slide.get("layout") == case or slide.get("case") == case:
            return slide
    # The fixture marks cases with data-case; layout falls back to "custom", so
    # match on the heading text the case slide carries.
    for slide in ir["slides"]:
        if slide["title"].replace(" ", "") == case.replace("-", ""):
            return slide
    raise SystemExit(f"fixture case not found: {case}")


def all_text(slide: dict) -> str:
    out = []
    for shape in slide["shapes"]:
        if shape["kind"] == "text":
            for para in shape["paragraphs"]:
                out.extend(run["text"] for run in para["runs"])
    return "".join(out)


def text_shapes(slide: dict) -> list[dict]:
    return [s for s in slide["shapes"] if s["kind"] == "text"]


def main(argv: list[str]) -> int:
    ir = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    findings = ir["findings"]

    # 1. Bare text beside block children must survive.
    mixed = slide_by_case(ir, "mixedcontent")
    body = all_text(mixed)
    check("IR-01 bare text before a block child is kept", "BARE-BEFORE" in body, body[:60])
    check("IR-02 bare text after a block child is kept", "BARE-AFTER" in body, body[:60])

    # 2. An un-annotated inline <svg> is rasterized, not read as text.
    svg = slide_by_case(ir, "inlinesvg")
    check("IR-03 inline svg becomes a raster shape", any(s["kind"] == "raster" for s in svg["shapes"]))
    check("IR-04 inline svg text is not emitted as a text run", "SVGTEXT" not in all_text(svg))

    # 3. A translucent fill keeps its alpha instead of painting solid.
    tile = slide_by_case(ir, "translucentfill")
    fills = [s for s in tile["shapes"] if s["kind"] == "shape" and s.get("fill")]
    check("IR-05 a translucent fill is emitted", len(fills) == 1, str(len(fills)))
    if fills:
        check("IR-06 its alpha is carried through", fills[0].get("fill_alpha", 1) < 0.2, str(fills[0].get("fill_alpha")))

    # 4. Centred text must not carry the centring offset as a paragraph margin.
    centred = slide_by_case(ir, "centredtext")
    paras = [p for s in text_shapes(centred) for p in s["paragraphs"] if "CENTERED" in "".join(r["text"] for r in p["runs"])]
    check("IR-07 centred paragraph found", len(paras) == 1)
    if paras:
        check("IR-08 centred paragraph has no bullet marker", paras[0].get("marker") is None)

    # 5. Paragraph spacing must fit the box it was measured in.
    collapse = slide_by_case(ir, "margincollapse")
    for shape in text_shapes(collapse):
        if len(shape["paragraphs"]) < 3:
            continue
        needed = sum(
            p.get("space_before_px", 0) + p.get("space_after_px", 0) + p.get("lines", 1) * p.get("line_px", 0)
            for p in shape["paragraphs"]
        )
        check(
            "IR-09 stacked paragraph spacing fits its measured box",
            needed <= shape["rect"]["h"] + 1,
            f"needs {needed:.1f}px in {shape['rect']['h']:.1f}px",
        )

    # 6. Out-of-flow children keep their own positions.
    flow = slide_by_case(ir, "outofflow")
    tops = {round(s["rect"]["y"]) for s in text_shapes(flow) if "TOP-LEFT" in all_text({"shapes": [s]})}
    bottoms = {round(s["rect"]["y"]) for s in text_shapes(flow) if "BOT-RIGHT" in all_text({"shapes": [s]})}
    check("IR-10 out-of-flow children become separate shapes", bool(tops) and bool(bottoms) and tops != bottoms)
    if tops and bottoms:
        check("IR-11 their vertical offset is preserved", abs(max(bottoms) - max(tops)) > 200,
              f"{max(tops)} vs {max(bottoms)}")

    # 7. inline-flex siblings must not be welded into one run.
    iflex = slide_by_case(ir, "inlineflex")
    holders = [s for s in text_shapes(iflex) if "IFLEX" in all_text({"shapes": [s]})]
    check(
        "IR-12 side-by-side labels stay side by side, not stacked as paragraphs",
        len(holders) == 2 and round(holders[0]["rect"]["x"]) != round(holders[1]["rect"]["x"]),
        f"{len(holders)} shape(s)",
    )

    # 8. Strikethrough reaches the IR.
    struck = slide_by_case(ir, "strike")
    runs = [r for s in text_shapes(struck) for p in s["paragraphs"] for r in p["runs"] if r["text"].strip() == "STRUCK"]
    check("IR-13 strikethrough is recorded", bool(runs) and runs[0].get("strike") is True)

    # 9. A padded inline highlight is not clipping.
    highlight = slide_by_case(ir, "inlinehighlight")
    clipped = [f for f in findings if f["code"] == "clipped" and f["slide"] == highlight["index"]]
    check("IR-14 a padded inline highlight is not reported as clipped", not clipped, str(clipped[:1]))

    # 10. A transformed slide is refused rather than silently mis-scaled.
    check(
        "IR-15 a transformed slide is an error",
        any(f["code"] == "slide-transformed" for f in findings),
    )

    # Colours are never invented.
    check(
        "IR-16 no run carries an unresolved colour silently",
        not any(f["code"] == "color-unreadable" for f in findings),
    )

    if len(argv) > 2 and Path(argv[2]).exists():
        with zipfile.ZipFile(argv[2]) as pptx:
            slides = [pptx.read(n).decode("utf-8") for n in pptx.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
            themes = [pptx.read(n) for n in pptx.namelist() if n.startswith("ppt/theme/") and n.endswith(".xml")]
        joined = "".join(slides)
        check("XML-01 strikethrough reaches the file", 'strike="sngStrike"' in joined)
        check("XML-02 a translucent fill reaches the file", "<a:alpha" in joined)
        check(
            "XML-03 no unbulleted paragraph carries a left margin",
            not re.search(r'<a:pPr[^>]*marL="(?!0")\d+"[^>]*>(?:(?!</a:pPr>).)*<a:buNone/>', joined, re.S),
        )
        from lxml import etree

        ok = True
        for theme in themes:
            try:
                etree.fromstring(theme)
            except Exception as exc:  # noqa: BLE001 - the assertion is that it parses
                ok = False
                print(f"       theme did not parse: {exc}")
        check("XML-04 every theme part is well-formed", ok)

    print(f"\n{CHECKS - len(FAILURES)} passed, {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
