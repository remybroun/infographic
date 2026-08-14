#!/usr/bin/env python3
"""Print the laid-out height of every block in a spec.

    python3 assets/measure_blocks.py assets/gallery_spec.json

WHY THIS EXISTS. A grid row is as tall as its tallest block, so a 444px block
beside a 137px one buys 307px of blank page. Across the gallery that mistake was
worth 1,400px, an entire wasted sheet. The fix is to order specimens by height
so the pairs match, and block height is not guessable from the payload: it comes
out of text wrapping, legend rows, category counts and the theme's type scale.

Chrome runs the injected script before `--dump-dom` serializes, so these are real
layout numbers. Adding up SVG `height` attributes would miss every block with an
HTML body: definitions, comparison, checklist, callout, chips.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import build as build_mod  # noqa: E402
import render_pdf  # noqa: E402

PROBE = """<script>
window.addEventListener('load', function () {
  var out = [];
  document.querySelectorAll('.ig-block').forEach(function (el, i) {
    out.push([i, Math.round(el.getBoundingClientRect().height)]);
  });
  document.body.setAttribute('data-measured', JSON.stringify(out));
});
</script>"""


def measure(spec_path: str):
    spec = json.load(open(spec_path, encoding="utf-8"))
    html, _warnings = build_mod.build(spec_path)
    tmp = os.path.join(os.path.dirname(os.path.abspath(spec_path)), ".measure.html")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html.replace("</head>", PROBE + "</head>", 1))
    try:
        dom = subprocess.run(
            [render_pdf.find_chrome(None), "--headless", "--disable-gpu",
             "--no-first-run", "--virtual-time-budget=3000", "--dump-dom",
             f"file://{tmp}"],
            capture_output=True, text=True, timeout=120).stdout
    finally:
        os.remove(tmp)
    found = re.search(r'data-measured="([^"]+)"', dom)
    if not found:
        raise SystemExit("[measure] Chrome returned no measurements")
    heights = dict(json.loads(found.group(1).replace("&quot;", '"')))
    return [b for b in spec.get("blocks", []) if not b.get("skip")], heights


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    blocks, heights = measure(sys.argv[1])
    waste, previous = 0, None
    for index, block in enumerate(blocks):
        height = heights.get(index, 0)
        span = int(block.get("span", 12))
        gap = ""
        if span == 6 and previous is not None:
            gap = f"  +{abs(height - previous):d} blank"
            waste += abs(height - previous)
            previous = None
        elif span == 6:
            previous = height
        else:
            previous = None
        title = block.get("title") or block.get("label") or ""
        print(f"{index:3d}  {height:5d}px  span{span:<3} {block['type']:<12} "
              f"{title[:44]:<44}{gap}")
    print(f"\n{waste}px of blank page in mismatched half-width pairs")


if __name__ == "__main__":
    main()
