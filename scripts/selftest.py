#!/usr/bin/env python3
"""Assertions over the block library, the spec compiler and the extractor.

Expectations here are derived from the contract in references/, not from
whatever the renderers happen to emit. When one fails, check the expectation
against the reference doc first, if the doc is right, the code is wrong.

    python3 scripts/selftest.py            # assertions only
    python3 scripts/selftest.py --render    # also build every fixture to PDF
"""

from __future__ import annotations

import argparse
import json
import tempfile
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build import Document  # noqa: E402
from lib import derivation  # noqa: E402
from lib import leading_numbers  # noqa: E402
from lib import density, registry, svg  # noqa: E402
from lib.blocks_diagram import CHIP_PAD, _chip_rows, balanced_columns  # noqa: E402
from lib.theme import Ctx, Theme  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FIXTURES = os.path.join(SKILL, "fixtures")

PASSED, FAILED = [], []


def check(name, condition, detail=""):
    (PASSED if condition else FAILED).append((name, detail))
    print(f"  [{'ok  ' if condition else 'FAIL'}] {name}" + (f", {detail}" if detail and not condition else ""))


def ctx(theme="default", width=672.0):
    return Ctx(Theme.load(theme), width)


# ------------------------------------------------------------ svg helpers ---

def test_svg_primitives():
    print("\nsvg primitives")
    # A bar rounded at the data end must have exactly one arc pair, and a bar
    # rounded on all sides would detach from its baseline.
    top = svg.bar_path(0, 0, 40, 100, 4, "top")
    check("bar_path rounds only the data end", top.count("A") == 2, top)
    check("bar_path(end=none) is a plain rect", "A" not in svg.bar_path(0, 0, 40, 100, 4, "none"))
    check("bar_path clamps radius to half the short side",
          svg.bar_path(0, 0, 4, 100, 40, "top").count("A") == 2)

    # Text measurement must OVER-estimate: a label that is predicted to fit but
    # does not is a clipped label, which is worse than one moved outside.
    check("text_width scales with size",
          svg.text_width("hello", 20) > svg.text_width("hello", 10) * 1.9)
    check("text_width over-estimates a narrow string",
          svg.text_width("iiiii", 10) < svg.text_width("MMMMM", 10))
    check("truncate fits inside the budget",
          svg.text_width(svg.truncate("a very long label indeed", 10, 50), 10) <= 50)
    check("truncate leaves short text alone", svg.truncate("ok", 10, 500) == "ok")
    check("wrap respects max_lines", len(svg.wrap("one two three four five six", 10, 30, max_lines=2)) == 2)

    check("esc neutralizes markup", svg.esc("<b>&") == "&lt;b&gt;&amp;")
    check("fmt_compact 1284 -> 1.3K", svg.fmt_compact(1284) == "1.3K")
    check("fmt_compact 4.2M with currency", svg.fmt_compact(4_200_000, 1, "$") == "$4.2M")
    check("fmt_plain thousands-separates", svg.fmt_plain(1234567) == "1,234,567")
    check("fmt_delta signs with a real minus", svg.fmt_delta(-3.5) == "−3.5%")
    # A real quantity must never print as "0" because it rounded away: displaying
    # 0.031 as "0%" states something the data does not say.
    check("fmt_compact keeps a significant digit on small values",
          svg.fmt_compact(0.031, 1) not in ("0", "0.0"), svg.fmt_compact(0.031, 1))
    check("fmt_compact still prints a true zero as 0", svg.fmt_compact(0, 1) == "0")
    check("fmt_compact leaves whole numbers clean", svg.fmt_compact(12, 1) == "12")

    # Padding must not carry an all-positive domain below zero.
    lo, hi = svg.extent([10000, 76123], pad=0.06, include_zero=True)
    check("padding never drags a positive domain under zero", lo == 0.0, f"lo={lo}")
    lo, hi = svg.extent([-40, -10], pad=0.1, include_zero=True)
    check("padding never drags a negative domain above zero", hi == 0.0, f"hi={hi}")

    ticks = svg.nice_ticks(0, 97, 5)
    check("nice_ticks are round numbers", all(abs(t % 20) < 1e-9 for t in ticks), str(ticks))
    check("nice_ticks cover the domain", max(ticks) >= 97 and min(ticks) <= 0, str(ticks))
    check("extent includes zero by default", svg.extent([10, 20])[0] == 0.0)
    check("extent can exclude zero", svg.extent([10, 20], include_zero=False)[0] == 10.0)

    check("contrast is symmetric", abs(svg.contrast("#000", "#fff") - 21.0) < 0.01)
    check("ink_on picks white on a dark fill", svg.ink_on("#0d366b") == "#ffffff")
    check("ink_on picks dark on a pale fill", svg.ink_on("#cde2fb") == "#0b0b0b")
    check("mix midpoint", svg.mix("#000000", "#ffffff", 0.5) == "#808080")


# ------------------------------------------------------------------ theme ---

def test_theme():
    print("\ntheme")
    for name in Theme.available():
        t = Theme.load(name)
        check(f"{name}: 8 categorical slots", t.series_count() == 8)
        # Slot assignment is fixed order and must NEVER cycle: a 9th series
        # asking for a hue is a design error, so we clamp instead of wrapping.
        check(f"{name}: slot 9 clamps rather than cycling", t.series(8) == t.series(7))
        check(f"{name}: ordinal ramp is monotone-usable", len(t.ordinal_steps()) >= 4)
        check(f"{name}: ordinal(0) is the lightest step", t.ordinal(0, 5) == t.ordinal_steps()[0])
        check(f"{name}: ordinal(last) is the darkest step", t.ordinal(4, 5) == t.ordinal_steps()[-1])
        check(f"{name}: diverging(0) is the neutral midpoint",
              t.diverging(0).lower() == t.data["diverging"]["mid"].lower())
        check(f"{name}: sequential(0) is lighter than sequential(1)",
              svg.luminance(t.sequential(0)) > svg.luminance(t.sequential(1)))
        check(f"{name}: has an accent_text role", "accent_text" in t.data["ink"])
        # The de-emphasis gray is still a data mark, not chrome: below 3:1 the
        # context series it carries disappears in print.
        check(f"{name}: de-emphasis clears 3:1 as a mark",
              svg.contrast(t.deemphasis, t.surface("card")) >= 3.0,
              f"{t.deemphasis} at {svg.contrast(t.deemphasis, t.surface('card')):.2f}:1")
        check(f"{name}: wash returns an opaque hex",
              re.fullmatch(r"#[0-9a-f]{6}", t.wash(t.accent, 0.1)) is not None)


# ----------------------------------------------------------------- blocks ---

MINIMAL = {
    # Doubles as the drawing kit's proof: every class in this payload is one the
    # kit must provide, so if a kit class is renamed the catalog sheet shows it.
    "figure": {
        "viewbox": "0 0 360 120", "encodes": "concept",
        "alt": "Two nodes joined by an arrow, the second one emphasised.",
        "svg": '<rect class="ig-fig-node" x="8" y="34" width="120" height="52" rx="8"/>'
               '<text class="ig-fig-title" x="24" y="58">Source</text>'
               '<text class="ig-fig-mute" x="24" y="76">upstream</text>'
               '<line class="ig-fig-edge" x1="136" y1="60" x2="216" y2="60" '
               'marker-end="url(#ig-arrow)"/>'
               '<rect class="ig-fig-node-strong" x="228" y="34" width="120" height="52" rx="8"/>'
               '<text class="ig-fig-title ig-fig-accent" x="244" y="58">Target</text>'
               '<text class="ig-fig-mute" x="244" y="76">one deployment</text>',
    },
    "bar": {"categories": ["Alpha", "Beta", "Gamma"], "values": [12, 30, 21]},
    "column": {"categories": ["Q1", "Q2", "Q3"], "series": [
        {"name": "New", "values": [10, 14, 18]}, {"name": "Renewal", "values": [6, 9, 11]}]},
    "lollipop": {"categories": ["A", "B", "C", "D"], "values": [4, 9, 2, 7]},
    "diverging": {"items": [{"label": "Up", "value": 12}, {"label": "Down", "value": -8}]},
    "likert": {"items": [{"label": "Onboarding", "values": [5, 10, 20, 40, 25]}]},
    "scatter": {"points": [{"x": 1, "y": 2, "label": "a"}, {"x": 3, "y": 5, "label": "b"}]},
    "heatmap": {"rows": ["Mon", "Tue"], "cols": ["AM", "PM"], "values": [[3, 9], [7, 2]]},
    "matrix": {"cols": ["Fast", "Cheap"], "rows": [
        {"label": "Option A", "cells": [True, False]},
        {"label": "Option B", "cells": ["partial", True]}]},
    "line": {"x": ["Jan", "Feb", "Mar"], "series": [{"name": "Users", "values": [3, 6, 5]}]},
    "area": {"x": ["Jan", "Feb"], "values": [3, 6]},
    "dumbbell": {"items": [{"label": "Latency", "from": 400, "to": 180}]},
    "slope": {"items": [{"label": "EU", "from": 12, "to": 20}, {"label": "US", "from": 18, "to": 15}]},
    "timeline": {"events": [{"date": "2024", "title": "Start", "text": "Kickoff."},
                            {"date": "2025", "title": "Ship", "text": "Launched."}]},
    "share_bar": {"parts": [{"label": "Direct", "value": 60}, {"label": "Partner", "value": 40}]},
    "unit": {"parts": [{"label": "Retained", "value": 68}, {"label": "Churned", "value": 32}]},
    "donut": {"parts": [{"label": "A", "value": 3}, {"label": "B", "value": 7}]},
    "treemap": {"parts": [{"label": "Big", "value": 60}, {"label": "Mid", "value": 25},
                          {"label": "Small", "value": 15}]},
    "funnel": {"stages": [{"label": "Visited", "value": 1000}, {"label": "Signed up", "value": 220},
                          {"label": "Paid", "value": 60}]},
    "pyramid": {"levels": [{"title": "Base", "text": "Foundations"},
                           {"title": "Middle"}, {"title": "Top"}]},
    "meter": {"label": "Capacity", "value": 72, "max": 100,
              "thresholds": [{"at": 80, "status": "warning", "label": "80%"}]},
    "process": {"steps": [{"title": "Collect", "text": "Gather."},
                          {"title": "Decide", "text": "Choose."},
                          {"title": "Build", "text": "Make."}]},
    "cycle": {"steps": [{"title": "Plan"}, {"title": "Do"}, {"title": "Check"}, {"title": "Act"}]},
    "quadrant": {"x_label": "Effort", "y_label": "Impact",
                 "quadrants": [{"label": "Fill-ins"}, {"label": "Big bets"},
                               {"label": "Skip"}, {"label": "Quick wins", "highlight": True}],
                 "items": [{"label": "Search", "x": 0.3, "y": 0.8}]},
    "venn": {"sets": [{"label": "Design"}, {"label": "Code"}], "overlap": "Systems"},
    "tree": {"root": {"label": "Platform", "children": [
        {"label": "Web"}, {"label": "Mobile", "children": [{"label": "iOS"}, {"label": "Android"}]}]}},
    "sankey": {"links": [{"source": "Traffic", "target": "Signup", "value": 100},
                         {"source": "Traffic", "target": "Bounce", "value": 60},
                         {"source": "Signup", "target": "Paid", "value": 30}]},
    "anatomy": {"callouts": [{"x": 0.3, "y": 0.4, "title": "Header", "text": "The top bar."}]},
    "hero": {"kicker": "Report", "title": "A claim", "subtitle": "Supporting line."},
    "section": {"number": "01", "title": "The setup", "lede": "Why this matters."},
    "heading": {"text": "A sub-part"},
    "prose": {"text": "First paragraph.\n\nSecond paragraph with **bold**."},
    "bullets": {"items": ["One", "Two"]},
    "quote": {"text": "Words matter.", "attribution": "Someone"},
    "callout": {"tone": "warn", "title": "Careful", "text": "A caveat."},
    "stat": {"label": "Revenue", "value": 4200000, "currency": "$", "delta": 12.4,
             "trend": [1, 3, 2, 5, 4, 7]},
    "kpi": {"items": [{"label": "A", "value": 12}, {"label": "B", "value": 34}]},
    "hero_figure": {"value": 0.68, "decimals": 2, "label": "of the total"},
    "table": {"columns": ["Name", "Value"], "rows": [["A", "1"], ["B", "2"]]},
    "checklist": {"do": ["Label the endpoint"], "dont": ["Number every point"]},
    "definitions": {"items": [{"term": "Churn", "text": "Customers who leave."}]},
    "comparison": {"left": {"label": "Before", "headline": "Slow", "points": ["Manual"]},
                   "right": {"label": "After", "headline": "Fast", "points": ["Automatic"]}},
    "image": {"src": "x.png", "alt": "An image"},
    "footnotes": {"items": ["Source: internal data."]},
    "divider": {}, "spacer": {}, "raw": {"html": "<p>raw</p>"},

    "stack": {"layers": [
        {"label": "Edge", "meta": "cached", "items": ["CDN", "TLS"]},
        {"label": "App", "items": ["Router", "Render"]},
    ]},
    "chips": {"items": [{"label": "Draft", "tone": "mute"},
                        {"label": "Live", "tone": "good", "value": "42"}]},
    "scorecard": {"choices": ["Hybrid", "Split"], "criteria": ["Cost", "Scale", "Risk"],
                  "scores": [[5, 4, 3], [2, 2, 1]], "max": 5},
    "gauge": {"value": 66, "max": 75, "label": "Hybrid", "caption": "recommended"},
    "swimlane": {"stages": ["Add", "Verify"],
                 "lanes": [{"label": "Provider", "cells": ["Adds domain", None]},
                           {"label": "System", "cells": [None, "Polls DNS"]}]},
}


def test_every_block_renders():
    print("\nblock catalog, every registered type renders on every theme")
    missing = sorted(set(registry.REGISTRY) - set(MINIMAL))
    check("every registered block has a fixture", not missing, f"missing: {missing}")
    for theme_name in Theme.available():
        broken = []
        for name in sorted(registry.REGISTRY):
            payload = dict(MINIMAL.get(name, {}))
            payload["type"] = name
            try:
                out = registry.render_block(payload, ctx(theme_name))
            except Exception as exc:  # noqa: BLE001
                broken.append(f"{name}: {type(exc).__name__} {exc}")
                continue
            if not isinstance(out, str):
                broken.append(f"{name}: returned {type(out).__name__}")
            elif name not in ("divider", "spacer", "raw") and len(out) < 20:
                broken.append(f"{name}: suspiciously short output")
            elif "None" in out and name not in ("raw",):
                broken.append(f"{name}: leaked a literal None into output")
        check(f"{theme_name}: all {len(registry.REGISTRY)} blocks render",
              not broken, "; ".join(broken[:4]))


def test_block_contracts():
    print("\nblock contracts")
    c = ctx()

    # A legend is always present for >= 2 series and NEVER for one: a single
    # swatch just restates the title.
    one = registry.render_block({"type": "column", "categories": ["A", "B"],
                                 "series": [{"name": "Only", "values": [1, 2]}]}, c)
    two = registry.render_block({"type": "column", "categories": ["A", "B"],
                                 "series": [{"name": "One", "values": [1, 2]},
                                            {"name": "Two", "values": [2, 1]}]}, c)
    check("no legend for a single series", "ig-legend" not in one)
    check("legend present for two series", "ig-legend" in two)

    # Every chart ships its table-view twin so no value is gated.
    for name in ("bar", "column", "line", "share_bar", "funnel", "heatmap", "unit"):
        out = registry.render_block(dict(MINIMAL[name], type=name), c)
        check(f"{name} ships a table view", "ig-table-view" in out)
    off = registry.render_block(dict(MINIMAL["bar"], type="bar", table=False), c)
    check("table view can be suppressed explicitly", "ig-table-view" not in off)

    # Gridlines are solid hairlines. Dashing reads as "threshold".
    grid = registry.render_block(dict(MINIMAL["column"], type="column"), c)
    check("no dashed gridlines anywhere", "stroke-dasharray" not in grid)

    # Emphasis: one series in the accent, everything else in the de-emphasis gray.
    t = Theme.load("default")
    emph = registry.render_block({"type": "bar", "categories": ["A", "B", "C"],
                                  "values": [1, 2, 3], "emphasis": "B", "sort": None}, c)
    check("emphasis uses the accent hue", t.accent in emph)
    check("emphasis grays the rest", t.deemphasis in emph)

    # A 9th series must warn rather than invent a hue.
    warn_ctx = ctx()
    registry.render_block({"type": "column", "categories": ["A"],
                           "series": [{"name": f"S{i}", "values": [1]} for i in range(9)]}, warn_ctx)
    check("9 series raises a palette warning",
          any("ninth hue" in w or "exceeds" in w for w in warn_ctx.warnings),
          str(warn_ctx.warnings))

    # Scatter is an all-pairs form, so it caps at three series.
    sc = ctx()
    registry.render_block({"type": "scatter", "points": [
        {"x": i, "y": i, "series": f"S{i}"} for i in range(4)]}, sc)
    check("4-series scatter warns about all-pairs separation",
          any("all-pairs" in w for w in sc.warnings), str(sc.warnings))

    # Donut past six segments, and venn past three sets, are undrawable honestly.
    dc = ctx()
    registry.render_block({"type": "donut", "parts": [
        {"label": f"P{i}", "value": 1} for i in range(7)]}, dc)
    check("7-segment donut warns", any("6 segments" in w for w in dc.warnings))
    vc = ctx()
    registry.render_block({"type": "venn", "sets": [{"label": f"S{i}"} for i in range(4)]}, vc)
    check("4-set venn warns", any("more than 3 sets" in w for w in vc.warnings))

    # The unit chart must place exactly `cells` glyphs, with rounding drift
    # distributed, otherwise "68 in 100" silently becomes 67.
    unit = registry.render_block({"type": "unit", "cells": 100, "parts": [
        {"label": "A", "value": 33.4}, {"label": "B", "value": 33.3}, {"label": "C", "value": 33.3}]}, c)
    glyphs = unit.count("<rect")
    check("unit chart draws exactly 100 glyphs", glyphs == 100, f"drew {glyphs}")

    # Untrusted labels must never reach the DOM as markup.
    inj = registry.render_block({"type": "bar", "categories": ["<script>x</script>"],
                                 "values": [1]}, c)
    check("category labels are escaped", "<script>" not in inj)
    inj2 = registry.render_block({"type": "prose", "text": "<img src=x onerror=1>"}, c)
    check("prose escapes raw HTML", "<img" not in inj2)
    md = registry.render_block({"type": "prose", "text": "a **bold** word"}, c)
    check("prose keeps its inline markdown subset", "<strong>bold</strong>" in md)

    # A block that renders a payload key itself must not also get the compiler's
    # chrome for it, or the text prints twice.
    from build import Document
    for block_type, key, text in (("hero", "subtitle", "SUBTITLE_MARKER"),
                                  ("callout", "title", "TITLE_MARKER"),
                                  ("hero_figure", "note", "NOTE_MARKER"),
                                  ("stat", "note", "NOTE_MARKER"),
                                  ("footnotes", "title", "TITLE_MARKER"),
                                  ("section", "title", "TITLE_MARKER")):
        payload = dict(MINIMAL[block_type], type=block_type)
        payload[key] = text
        html = Document({"meta": {}, "blocks": [payload]}).render()
        check(f"{block_type}.{key} is rendered once, not twice",
              html.count(text) == 1, f"appeared {html.count(text)} times")
    # …and a block that does NOT own the key still gets the chrome.
    html = Document({"meta": {}, "blocks": [dict(MINIMAL["bar"], type="bar",
                                                 title="CHROME_MARKER")]}).render()
    check("a chart still receives its figure caption", "CHROME_MARKER" in html)

    # Sankey terminal labels must fit inside the viewBox.
    sk = registry.render_block(dict(MINIMAL["sankey"], type="sankey"), ctx(width=400))
    width = float(re.search(r'viewBox="0 0 ([\d.]+)', sk).group(1))
    xs = [float(m) for m in re.findall(r'<text x="([\d.]+)"', sk.split("</svg>")[0])]
    check("sankey labels stay inside the canvas",
          all(x < width for x in xs), f"max x {max(xs, default=0)} vs width {width}")

    # Aliases resolve so a spec written in ordinary words still builds.
    check("alias pie -> donut", registry.resolve("pie")[0] == "donut")
    check("alias waffle -> unit", registry.resolve("waffle")[0] == "unit")
    check("alias 2x2 -> quadrant", registry.resolve("2x2")[0] == "quadrant")
    check("unknown type is rejected loudly", registry.resolve("nonsense")[1] is None)


def test_delta_direction():
    print("\ndelta direction")
    from lib import blocks_editorial as ed
    c = ctx()
    # The arrow carries direction; the number must not also carry a sign, or the
    # two can contradict each other.
    down = ed.stat({"label": "Tickets", "value": 100, "delta": -14.2}, c)
    check("a negative delta shows a down arrow", "↓" in down)
    check("a negative delta shows no plus sign", "+" not in down, down)
    check("a negative delta shows the magnitude", "14.2%" in down)
    up = ed.stat({"label": "Tickets", "value": 100, "delta": 14.2}, c)
    check("a positive delta shows an up arrow", "↑" in up)
    check("a positive delta shows no minus sign", "−" not in up)
    # up_is_good flips which colour class the direction earns.
    # A figure that does not fit its tile must SHRINK, never wrap: wrapping
    # stacks a big number one character per line.
    narrow = ed.stat({"label": "Revenue", "value": 4_200_000, "currency": "$"}, ctx(width=120))
    match = re.search(r'ig-stat-value" style="font-size:([\d.]+)px', narrow)
    check("a figure in a narrow tile is shrunk to fit", match is not None, narrow[:160])
    if match:
        check("the shrunk figure actually fits",
              svg.text_width("$4.2M", float(match.group(1)), 650) <= 120 - 40 + 1,
              f"size {match.group(1)}px")
    wide = ed.stat({"label": "Revenue", "value": 4_200_000, "currency": "$"}, ctx(width=672))
    check("a figure with room keeps the full type scale", "font-size:" not in wide)
    check("stat values never wrap", "overflow-wrap" not in wide)

    bad_up = ed.stat({"label": "Latency", "value": 1, "delta": 22.0, "up_is_good": False}, c)
    check("a rise in a bad metric is coloured as bad", "ig-delta-down" in bad_up)
    good_up = ed.stat({"label": "Revenue", "value": 1, "delta": 22.0}, c)
    check("a rise in a good metric is coloured as good", "ig-delta-up" in good_up)


def test_label_fitting():
    print("\nlabel fitting")
    from lib import chrome
    check("a label that fits is allowed", chrome.value_label_fits("12", 10, 80))
    check("a label that does not fit is refused",
          not chrome.value_label_fits("1,234,567", 10, 20))
    # A segment too small for its label must DROP the label, not clip it. With a
    # 1:999 split the tiny segment is under a pixel wide, so exactly one of the
    # two percentages may be drawn inside the bar.
    out = registry.render_block({"type": "share_bar", "parts": [
        {"label": "Tiny", "value": 1}, {"label": "Huge", "value": 999}]}, ctx())
    plot = out.split("</svg>")[0]
    check("sub-pixel share segment drops its inline label",
          plot.count("<text") == 1, f"{plot.count('<text')} inline labels drawn")
    # Both values stay reachable: the legend and the table view carry them.
    check("the dropped value survives in the legend", "Tiny" in out)
    check("the dropped value survives in the table view", "ig-table-view" in out)
    check("no mark is cropped with overflow:hidden", "overflow: hidden" not in out
          and "overflow:hidden" not in out)


# --------------------------------------------------------------- compiler ---

def test_compiler():
    print("\nspec compiler")
    spec = {
        "meta": {"title": "T", "theme": "default", "page": "a4"},
        "blocks": [
            {"type": "hero", "title": "A claim"},
            {"type": "bar", "span": 6, "categories": ["A"], "values": [1], "title": "Chart"},
            {"type": "chips", "span": 6, "items": ["Live"], "break": "before"},
        ],
    }
    doc = Document(spec)
    html = doc.render()
    check("the compiler defaults to graphic density", doc.density == "graphic")
    check("density is stamped on the document for the linter",
          "ig-density-graphic" in html)
    check("output is a complete HTML document",
          html.startswith("<!doctype html>") and html.rstrip().endswith("</html>"))
    check("every template token is substituted", "{{" not in html)
    check("theme tokens are inlined", "--ig-accent:" in html)
    check("span class is emitted", "ig-span-6" in html)
    check("page break is emitted", "ig-break-before" in html)
    check("block title becomes a figure caption", "ig-block-title" in html)
    check("@page carries the right size", "--ig-page-size:A4 portrait" in html)
    check("print-color-adjust is forced", "print-color-adjust: exact" in html)

    # Geometry: 12 spans must exactly reconstruct the content width.
    check("span arithmetic reconstructs the content width",
          abs(doc.span_width(12) - doc.content_px) < 0.01,
          f"{doc.span_width(12)} vs {doc.content_px}")
    check("two 6-spans plus a gutter equal a 12-span",
          abs(doc.span_width(6) * 2 + 20.0 - doc.span_width(12)) < 0.01)
    check("A4 content width is ~672px", 670 < doc.content_px < 675, f"{doc.content_px:.1f}")

    a3 = Document(dict(spec, meta=dict(spec["meta"], page="a3")))
    check("A3 is wider than A4", a3.content_px > doc.content_px)
    check("A3 scales body type up", a3.body_size > doc.body_size)

    themed = Document(spec, theme_name="rentos").render()
    check("theme override reaches the tokens", "--ig-accent:#5C6B2E" in themed)
    check("brand fonts are embedded when the theme has them", "@font-face" in themed)
    check("unknown theme fails loudly", _raises(lambda: Theme.load("nope")))
    check("unknown page fails loudly",
          _raises(lambda: Document({"meta": {"page": "a9"}, "blocks": []})))


def _raises(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True
    except Exception:  # noqa: BLE001
        return False


# -------------------------------------------------------------- extractor ---

def test_extractor():
    print("\nextractor")
    import extract_source as ex

    numbers = ex.extract_numbers("Revenue grew to $4.2M in 2024. Churn fell to 3.1%.")
    by_raw = {n["raw"]: n for n in numbers}
    check("parses a currency figure with a magnitude suffix",
          any(abs(n["value"] - 4_200_000) < 1 for n in numbers), str(numbers))
    check("parses a percentage and tags the unit",
          any(n["unit"] == "%" and abs(n["value"] - 3.1) < 0.01 for n in numbers))
    check("every number keeps its source sentence",
          all(n.get("context") for n in numbers))

    rows = [["Region", "2023", "2024"], ["EU", "10", "14"], ["US", "20", "18"], ["APAC", "5", "9"]]
    table = {"columns": rows[0], "rows": rows[1:], "origin": "test"}
    forms = [c["form"] for c in ex.table_candidates(table, 0)]
    check("year columns suggest a line", "line" in forms, str(forms))
    check("exactly two periods also suggests a slope", "slope" in forms, str(forms))

    shares = {"columns": ["Channel", "Share"],
              "rows": [["Direct", "60"], ["Partner", "30"], ["Other", "10"]], "origin": "test"}
    forms = [c["form"] for c in ex.table_candidates(shares, 0)]
    check("a column summing to 100 suggests a share bar", "share_bar" in forms, str(forms))
    check("it also offers the plain magnitude form", "bar" in forms, str(forms))

    negatives = {"columns": ["Team", "Change"],
                 "rows": [["A", "12"], ["B", "-8"], ["C", "3"]], "origin": "test"}
    check("values either side of zero suggest diverging",
          "diverging" in [c["form"] for c in ex.table_candidates(negatives, 0)])

    ba = {"columns": ["Metric", "Before", "After"],
          "rows": [["Latency", "400", "180"], ["Errors", "20", "4"]], "origin": "test"}
    check("before/after headers suggest a dumbbell",
          "dumbbell" in [c["form"] for c in ex.table_candidates(ba, 0)])

    prose = ("First we collect the data. Then we clean it. Finally we publish it. "
             "In 2021 the team formed. In 2022 it shipped. In 2023 it scaled.")
    forms = [c["form"] for c in ex.text_candidates(prose, [], [])]
    check("ordering language suggests a process", "process" in forms, str(forms))
    check("dated sentences suggest a timeline", "timeline" in forms, str(forms))

    # Pros/cons headings normally wear markdown furniture.
    for heading in ("### Pros\n- a\n### Cons\n- b",
                    "**Pros**\n- a\n**Cons**\n- b",
                    "Pros\n- a\nCons\n- b"):
        forms = [c["form"] for c in ex.text_candidates(heading, [], [])]
        check(f"pros/cons detected in {heading.splitlines()[0]!r}",
              "checklist" in forms, str(forms))

    md = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
    found = ex.extract_tables_from_text(md)
    check("recovers a markdown pipe table", found and found[0]["columns"] == ["A", "B"], str(found))

    check("candidates are ranked with high confidence first",
          [c["confidence"] for c in ex.rank([{"form": "x", "confidence": "low"},
                                             {"form": "y", "confidence": "high"}])]
          == ["high", "low"])


# --------------------------------------------------------------- fixtures ---

def test_linter():
    """The linter must not fire on its own stylesheet.

    Every false positive it produced came from matching CSS instead of content:
    a comment mentioning tabular-nums, a legitimate overflow:hidden, a class
    prefix that also matches a longer class. These assertions pin that shut.
    """
    print("\ndocument linter")
    import check_document as cd
    from build import Document

    spec_path = os.path.join(FIXTURES, "specs", "concept-explainer.json")
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    html = Document(spec).render()
    tmp = os.path.join(SKILL, "examples", "out", "_lint_probe.html")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html)

    codes = {f["code"] for f in cd.check(tmp)}
    for bogus in ("tabular-hero", "overflow-hidden", "thin-legend", "gradient-text",
                  "dashed-rule", "no-table-view", "empty"):
        check(f"a good document does not trip '{bogus}'", bogus not in codes, str(sorted(codes)))

    css, body = cd.split_document(html)
    check("the splitter finds a stylesheet", len(css) > 2000)
    check("the splitter finds a body", "<main" in body)
    check("CSS comments are stripped before matching", "/*" not in css)
    check("the body carries no stylesheet", "ig-block-title {" not in body)

    # …and it must still catch real problems.
    broken = html.replace("</style>", "</style>", 1).replace(
        '<main class="ig-doc">',
        '<main class="ig-doc"><img src="x.png"><p style="overflow:hidden">x</p>')
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(broken)
    codes = {f["code"] for f in cd.check(tmp)}
    check("the linter still catches a missing alt", "img-no-alt" in codes, str(sorted(codes)))
    check("the linter still catches an inline overflow:hidden",
          "overflow-hidden" in codes, str(sorted(codes)))

    empty = Document({"meta": {}, "blocks": []}).render()
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(empty)
    check("the linter catches an empty document",
          "empty" in {f["code"] for f in cd.check(tmp)})

    # The checks that were inverted. The old linter warned when prose was
    # ABSENT, which is how it blessed an eight-page text document. A
    # graphic-density document with no graphic at all must now be an error.
    text_only = Document({
        "meta": {"title": "T", "density": "report"},
        "blocks": [{"type": "prose", "text": "One. " * 40},
                   {"type": "prose", "text": "Two. " * 40}],
    }).render().replace("ig-density-report", "ig-density-graphic")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text_only)
    codes = {f["code"] for f in cd.check(tmp)}
    check("a graphic-density document with no graphics is an error",
          "no-graphics" in codes, str(sorted(codes)))
    check("prose-only is reported as such", "prose-only" in codes, str(sorted(codes)))

    check("table twins do not count toward the word budget",
          cd._visible_words('<p>one two</p><details><table><tr><td>'
                            + " ".join(["x"] * 50) + "</td></tr></table></details>") == 2,
          str(cd._visible_words('<p>one two</p><details><table><tr><td>'
                                + " ".join(["x"] * 50) + "</td></tr></table></details>")))
    check("svg tick labels do not count toward the word budget",
          cd._visible_words('<p>one two</p><svg><text>ten twenty thirty</text></svg>') == 2)
    check("visible prose does count",
          cd._visible_words("<p>one two three</p><p>four</p>") == 4)

    os.remove(tmp)


def test_leading_numbers():
    """A kpi row that restates what the document explains properly.

    Expectations come from the failure: a row of four whose every figure a
    chart further down carries with a denominator and a shape. The rule is
    stated before the implementation is consulted: warn when at least half a
    row's figures appear elsewhere, and never warn for hero_figure or stat,
    which are claims that evidence below them is supposed to support.
    """
    print("\nleading numbers, the row added because a slot existed")

    restated = {"blocks": [
        {"type": "kpi", "items": [{"label": "Kinds", "value": 61},
                                  {"label": "Places", "value": 20}]},
        {"type": "bar", "categories": ["a", "b"], "values": [61, 20]},
    ]}
    found = leading_numbers.check(restated, registry)
    check("a row restating the chart below is reported",
          found and "2 of 2" in found[0], found)

    fresh = {"blocks": [
        {"type": "kpi", "items": [{"label": "Kinds", "value": 61},
                                  {"label": "Places", "value": 20}]},
        {"type": "bar", "categories": ["a", "b"], "values": [7, 9]},
    ]}
    check("a row carrying numbers nothing else states is silent",
          leading_numbers.check(fresh, registry) == [])

    half = {"blocks": [
        {"type": "kpi", "items": [{"label": "a", "value": 5}, {"label": "b", "value": 6},
                                  {"label": "c", "value": 7}, {"label": "d", "value": 8}]},
        {"type": "bar", "categories": ["x"], "values": [5, 6]},
    ]}
    check("half restated is enough to report",
          leading_numbers.check(half, registry) != [])

    # A claim supported by evidence underneath is the correct relationship.
    claim = {"blocks": [
        {"type": "hero_figure", "label": "Conversion", "value": 3.1, "unit": "%"},
        {"type": "funnel", "stages": [{"label": "a", "value": 3.1}]},
    ]}
    check("a hero figure evidenced below it is not a restatement",
          leading_numbers.check(claim, registry) == [])
    single = {"blocks": [
        {"type": "stat", "label": "Median", "value": 31},
        {"type": "bar", "categories": ["a"], "values": [31]},
    ]}
    check("a stat evidenced below it is not a restatement",
          leading_numbers.check(single, registry) == [])

    # Numbers are found inside strings too, so a figure quoted in a title counts.
    quoted = {"blocks": [
        {"type": "kpi", "items": [{"label": "Kinds", "value": 61}]},
        {"type": "callout", "title": "All 61 of them", "text": "x"},
    ]}
    check("a figure restated in prose is found",
          leading_numbers.check(quoted, registry) != [])

    check("a document with no leading row is silent",
          leading_numbers.check({"blocks": [{"type": "bar", "categories": ["a"],
                                             "values": [1]}]}, registry) == [])


def test_derivation():
    """Whether a regeneration re-derived anything, or edited the last one.

    Expectations come from the failure this check was written for: a document
    regenerated "from the top" that came out with an identical set of graphic
    forms. The overlap of two identical form lists is 1.0 by definition, not by
    reading anything back from the implementation.
    """
    print("\nderivation, the check on a regeneration that changed nothing")

    same = ["figure", "figure", "bar", "chips"]
    check("identical form lists overlap completely",
          derivation.overlap(same, list(same)) == 1.0)
    check("disjoint form lists do not overlap",
          derivation.overlap(["bar", "line"], ["tree", "venn"]) == 0.0)
    check("forms are a multiset, so three figures differ from one",
          derivation.overlap(["figure", "figure", "figure"], ["figure"]) < 1.0,
          derivation.overlap(["figure", "figure", "figure"], ["figure"]))
    # Jaccard, not Dice: one shared form across three distinct forms is a
    # third, not a half. The union is the denominator.
    check("one shared form among three distinct reads as a third",
          abs(derivation.overlap(["bar", "line"], ["bar", "venn"]) - 1 / 3) < 1e-9,
          derivation.overlap(["bar", "line"], ["bar", "venn"]))

    spec = {"blocks": [{"type": "hero", "title": "t"}, {"type": "section"},
                       {"type": "bar", "categories": ["a"], "values": [1]},
                       {"type": "footnotes", "items": ["x"]}]}
    forms = derivation.graphic_forms(spec, registry)
    check("editorial scaffolding is not counted as a form",
          forms == ["bar"], forms)

    skipped = {"blocks": [{"type": "bar", "categories": ["a"], "values": [1], "skip": True}]}
    check("a skipped block is not counted",
          derivation.graphic_forms(skipped, registry) == [])

    check("no supersedes means no derivation check",
          derivation.check({"meta": {}, "blocks": []}, registry) == [])
    check("a supersedes that does not exist is reported, not ignored",
          "does not exist" in " ".join(
              derivation.check({"meta": {"supersedes": "/nope/absent.json"},
                                "blocks": []}, registry)))

    with tempfile.TemporaryDirectory() as tmp:
        previous = {"blocks": [{"type": "figure", "viewbox": "0 0 10 10", "alt": "a",
                                "encodes": "concept", "svg": "<text>x</text>"},
                               {"type": "bar", "categories": ["a"], "values": [1]}]}
        prev_path = os.path.join(tmp, "prev.json")
        with open(prev_path, "w", encoding="utf-8") as fh:
            json.dump(previous, fh)

        unchanged = dict(previous, meta={"supersedes": "prev.json"})
        found = derivation.check(unchanged, registry, os.path.join(tmp, "new.json"))
        check("a regeneration onto the same forms is reported",
              found and "100%" in found[0], found)

        diverged = {"meta": {"supersedes": "prev.json"},
                    "blocks": [{"type": "tree", "nodes": [{"label": "a"}]},
                               {"type": "timeline", "events": [{"date": "2026", "title": "a"}]}]}
        check("a regeneration onto different forms is silent",
              derivation.check(diverged, registry, os.path.join(tmp, "new.json")) == [])


def test_fixtures(render=False):
    print("\nfixtures")
    spec_dir = os.path.join(FIXTURES, "specs")
    if not os.path.isdir(spec_dir):
        check("fixtures/specs exists", False, spec_dir)
        return
    specs = sorted(f for f in os.listdir(spec_dir) if f.endswith(".json"))
    check("at least three worked example specs ship", len(specs) >= 3, str(specs))
    for name in specs:
        path = os.path.join(spec_dir, name)
        try:
            with open(path, encoding="utf-8") as fh:
                spec = json.load(fh)
            doc = Document(spec)
            html = doc.render()
            ok = "{{" not in html and len(html) > 3000
            check(f"{name} compiles", ok, f"{len(html)} bytes")
            for w in doc.warnings:
                print(f"        warn: {w}")
        except Exception as exc:  # noqa: BLE001
            check(f"{name} compiles", False, f"{type(exc).__name__}: {exc}")
            continue
        if render:
            out_dir = os.path.join(SKILL, "examples", "out")
            os.makedirs(out_dir, exist_ok=True)
            html_path = os.path.join(out_dir, name.replace(".json", ".html"))
            with open(html_path, "w", encoding="utf-8") as fh:
                fh.write(html)
            import render_pdf
            pdf = render_pdf.render(html_path, html_path.replace(".html", ".pdf"))
            pages = render_pdf.page_count(pdf)
            check(f"{name} renders to PDF", os.path.getsize(pdf) > 8000,
                  f"{os.path.getsize(pdf)} bytes, {pages} pages")


def test_density():
    """The text budget. Expectations come from the CAPS table in density.py,
    which is the contract; none of them are read back from renderer output."""
    print("\ntext budget, the rule that keeps a document graphic")

    check("markup does not inflate the word count",
          density.words("**one** two `three`") == 3, density.words("**one** two `three`"))
    check("a link counts as its label, not its URL",
          density.words("see [the docs](https://example.com/x)") == 3,
          density.words("see [the docs](https://example.com/x)"))
    check("density defaults to graphic", density.resolve(None) == "graphic")
    check("an explicit override beats meta", density.resolve("report", "graphic") == "graphic")
    check("an unknown density is refused", _raises(lambda: density.resolve("pretty")))

    def audit(block, mode="graphic"):
        return density.audit({"blocks": [block]}, mode, registry)

    # Body prose is refused outright at graphic density, and allowed at report.
    prose = {"type": "prose", "text": "This is a sentence with quite a few words in it."}
    graphic_violations = audit(prose)
    check("prose is refused at graphic density", len(graphic_violations) == 1,
          str(graphic_violations))
    check("the refusal names the body cap of zero",
          graphic_violations[0].cap == 0, str(graphic_violations[0].cap))
    check("prose is allowed at report density", not audit(prose, "report"))

    # Titles: the cap is 14, so 14 passes and 15 fails. Both sides get asserted,
    # because a check that only tests the failing side passes when the cap is
    # accidentally zero.
    #
    # 14 rather than 9 because a title must literally describe what is shown, and
    # nine words cannot name a subject, a scope and a period. At 9 the only thing
    # that fit was an aphorism, so the budget was quietly selecting for the exact
    # register anti-patterns.md bans.
    at_cap = {"type": "bar", "title": " ".join(["word"] * 14)}
    over_cap = {"type": "bar", "title": " ".join(["word"] * 15)}
    check("a 14-word title is inside the cap", not audit(at_cap))
    check("a 15-word title breaches the cap", len(audit(over_cap)) == 1)

    # The hero opens the document and gets its own, larger allowance.
    check("a 16-word hero title is allowed",
          not audit({"type": "hero", "title": " ".join(["word"] * 16)}))

    long_line = " ".join(["word"] * 40)
    check("footnotes are exempt so sources stay citable",
          not audit({"type": "footnotes", "items": [long_line]}))
    check("table cells are exempt because they are data",
          not audit({"type": "table", "columns": ["A"], "rows": [[long_line]]}))
    check("raw is exempt", not audit({"type": "raw", "html": long_line}))

    check("chip labels are charged as labels, not details",
          audit({"type": "chips", "items": [" ".join(["word"] * 7)]})[0].role == "label")
    check("nested item text is charged",
          len(audit({"type": "process",
                     "steps": [{"title": "Go", "text": " ".join(["word"] * 20)}]})) == 1)
    check("a skipped block is not charged",
          not audit({"type": "prose", "text": long_line, "skip": True}))

    # enforce() reports every violation at once: fixing a long document one
    # error per rebuild is how an author gives up and switches to report mode.
    many = {"blocks": [prose, over_cap, {"type": "callout", "text": long_line}]}
    try:
        density.enforce(many, "graphic", registry)
        check("enforce raises on violations", False, "no SystemExit")
    except SystemExit as exc:
        check("enforce reports all violations at once", "3 text-budget" in str(exc), str(exc)[:90])
        check("enforce names the offending block", "blocks[1]" in str(exc), str(exc)[:90])

    check("a compliant spec enforces cleanly",
          density.enforce({"blocks": [at_cap]}, "graphic", registry) is None)


def test_graphic_layout():
    """Layout maths for the forms that replaced the paragraphs."""
    print("\ngraphic layout, columns and chip fitting")

    # A chip sized to its own label must not be ellipsized. This failed for
    # real: width was stored as `text + 2*pad` and the inner width recovered by
    # subtracting, which does not round-trip in floating point.
    for label in ("TLS / ACME", "Availability", "Booking + payment", "SNI"):
        rows = _chip_rows([label], 560.0)
        _, _, width, inner = rows[0][0]
        check(f"a chip fits its own label: {label!r}",
              svg.truncate(label, 10, inner, 600) == label,
              svg.truncate(label, 10, inner, 600))
        check(f"the chip is wider than its text: {label!r}", width >= inner + CHIP_PAD)

    rows = _chip_rows(["one", "two", "three"], 120.0)
    check("chips wrap when the row is full", len(rows) > 1, str(len(rows)))
    over = _chip_rows(["a label far too long to ever fit here"], 80.0)
    check("an oversized chip is clamped to the available width",
          over[0][0][2] <= 80.0, str(over[0][0][2]))

    # Six tiles across four columns leaves a stray row of two; three columns is
    # two full rows. Ten tiles must NOT collapse to two, which the first
    # implementation did while calling it balance.
    check("6 tiles balance to 3 columns", balanced_columns(6, 672.0, 168.0) == 3,
          str(balanced_columns(6, 672.0, 168.0)))
    check("10 tiles stay at 4 columns", balanced_columns(10, 672.0, 150.0) == 4,
          str(balanced_columns(10, 672.0, 150.0)))
    check("5 tiles balance to 3 columns", balanced_columns(5, 672.0, 150.0) == 3,
          str(balanced_columns(5, 672.0, 150.0)))
    check("4 tiles stay at 4 columns", balanced_columns(4, 672.0, 150.0) == 4,
          str(balanced_columns(4, 672.0, 150.0)))
    check("balancing never returns zero columns", balanced_columns(1, 40.0, 150.0) >= 1)
    check("a narrow block collapses to one column",
          balanced_columns(6, 150.0, 150.0) == 1, str(balanced_columns(6, 150.0, 150.0)))

    # Every registered block declares whether it carries its idea in a picture,
    # because the linter's graphic-ratio check counts on it.
    unflagged = [n for n, e in registry.REGISTRY.items() if "graphic" not in e]
    check("every block declares a graphic flag", not unflagged, str(unflagged))
    diagram = [n for n, e in registry.REGISTRY.items() if e["family"] == "diagram"]
    check("the diagram family is entirely graphic",
          all(registry.REGISTRY[n]["graphic"] for n in diagram), str(diagram))
    check("prose is not counted as a graphic", not registry.REGISTRY["prose"]["graphic"])
    check("`list` now resolves to chips, not bullets",
          registry.resolve("list")[0] == "chips", registry.resolve("list")[0])


def test_figure():
    """The authored-figure contract.

    `figure` is the escape from the catalog, so it is the place where every
    guarantee this skill makes is most likely to leak: unthemed colour, a
    drawing nobody can read without seeing it, an essay hidden inside `<text>`
    elements, or a document that abandons the catalog entirely. Each of those is
    a build error, and each is asserted here from both sides.
    """
    print("\nauthored figures, the escape hatch that keeps its guarantees")

    def fig(**kw):
        base = {"type": "figure", "viewbox": "0 0 720 300",
                "alt": "A description of the drawing.", "encodes": "concept",
                "svg": '<rect class="ig-fig-node" x="0" y="0" width="80" height="40"/>'}
        base.update(kw)
        return base

    def build(*blocks, **meta):
        """Returns the rendered BODY, not the whole document. Matching against
        the full HTML matches the stylesheet too, which is how `ig-table-view`
        silently passed both directions at once."""
        spec = {"meta": dict({"title": "t"}, **meta), "blocks": list(blocks)}
        import check_document
        return check_document.split_document(Document(spec).render())[1]

    check("a well-formed figure compiles", "ig-fig-node" in build(fig()))

    # R1: a drawing that is only readable by looking at it is not accessible.
    check("a figure without alt is refused", _raises(lambda: build(fig(alt=""))))
    check("the refusal explains what alt is for",
          "alt" in _error(lambda: build(fig(alt=None))).lower())

    # R2: without a viewBox the drawing cannot scale to its grid column.
    check("a figure without a viewbox is refused", _raises(lambda: build(fig(viewbox=None))))
    check("a malformed viewbox is refused", _raises(lambda: build(fig(viewbox="0 0 720"))))

    # R3: colour is computed, not chosen, the rule that hand-drawing is most
    # likely to break. Literals are refused; theme tokens and currentColor pass.
    for literal in ('<rect fill="#c0392b"/>', '<rect fill="#e33"/>',
                    '<path stroke="rgb(12,12,12)"/>', '<rect style="fill:#ffffff"/>'):
        check(f"a colour literal is refused: {literal[:26]}…",
              _raises(lambda: build(fig(svg=literal))))
    check("the refusal names the literal it found",
          "#c0392b" in _error(lambda: build(fig(svg='<rect fill="#c0392b"/>'))))
    for allowed in ('<rect fill="var(--ig-accent)"/>', '<path stroke="currentColor"/>',
                    '<rect fill="none" class="ig-fig-node"/>',
                    '<path marker-end="url(#ig-arrow)"/>'):
        check(f"a themed value is allowed: {allowed[:30]}…", build(fig(svg=allowed)))

    # R4: `encodes` forces one honest declaration, either the drawing carries
    # values, which then need a reachable twin, or it is a concept drawing.
    check("a figure with no `encodes` is refused", _raises(lambda: build(fig(encodes=None))))
    table = {"columns": ["Layer", "Requests"], "rows": [["Edge", 80], ["Core", 2]]}
    html = build(fig(encodes=table))
    check("a quantitative figure renders its table twin", "ig-table-view" in html)
    check("the twin carries the real values", ">80<" in html and ">2<" in html)
    check("a concept figure ships no twin", "ig-table-view" not in build(fig()))

    # R5: the cap. This is what stops "draw the shape the catalog lacks" from
    # decaying into "hand-draw everything", which is how consistency was lost.
    check("three figures are allowed", build(fig(), fig(), fig()))
    check("a fourth figure is refused", _raises(lambda: build(fig(), fig(), fig(), fig())))
    check("the refusal states the cap and the count",
          "3" in _error(lambda: build(*[fig()] * 4)) and
          "4" in _error(lambda: build(*[fig()] * 4)))

    # R6: text inside the drawing is still text. Without this the budget has a
    # hole exactly the size of a `<text>` element.
    long_svg = "".join(f"<text>{'word ' * 6}</text>" for _ in range(8))  # 48 words
    check("prose smuggled into <text> breaches the budget",
          _raises(lambda: build(fig(svg=long_svg))))
    check("a normally-labelled drawing is inside the budget",
          build(fig(svg="".join(f"<text>Layer {i}</text>" for i in range(8)))))
    check("the figure text budget is a third of a page's whole allowance",
          density.CAPS["graphic"]["figure_text"] * 3 <= density.WORDS_PER_PAGE["graphic"],
          str(density.CAPS["graphic"]["figure_text"]))

    # The kit exists and is themed, because a hand-drawn figure with no kit is
    # from-scratch work and the author goes back to picking off the menu.
    with open(os.path.join(SKILL, "templates", "document.css"), encoding="utf-8") as fh:
        css = fh.read()
    for cls in ("ig-fig-node", "ig-fig-edge", "ig-fig-label", "ig-fig-title",
                "ig-fig-mute", "ig-fig-accent", "ig-fig-invert"):
        check(f"the drawing kit ships .{cls}", f".{cls}" in css)
    check("the kit defines arrowhead markers", "ig-arrow" in
          open(os.path.join(SKILL, "templates", "document.html"), encoding="utf-8").read())
    check("figure is registered as a graphic", registry.REGISTRY["figure"]["graphic"])
    check("`draw` and `scene` resolve to figure",
          registry.resolve("draw")[0] == "figure" and registry.resolve("scene")[0] == "figure")


def test_scroll():
    """The non-paginated target.

    Half of what makes a designed explainer breathe is not being cut into A4
    sheets: a full-bleed section, a real type scale, and vertical air that a
    page box cannot give. Paper checks must not follow it there.
    """
    print("\nscroll target, the non-paginated output")

    import check_document

    def build(blocks, **meta):
        """Returns the doc, its body-tag classes, and the BODY. Never the whole
        file: every one of these class names is also a selector in the
        stylesheet, so `"ig-continuous" in html` is true for every document ever
        built. That false positive is real, it shipped in the linter and made
        four paginated fixtures report as continuous."""
        spec = {"meta": dict({"title": "t", "page": "scroll"}, **meta), "blocks": blocks}
        doc = Document(spec)
        html = doc.render()
        return doc, check_document.document_classes(html), check_document.split_document(html)[1]

    doc, classes, body = build([{"type": "chips", "items": ["One", "Two"]}])
    check("scroll is a known page", doc.page_key == "scroll")
    check("scroll stamps its own body class", "ig-page-scroll" in classes, str(classes))
    check("a scroll document is marked continuous", "ig-continuous" in classes)
    check("a scroll document is not paginated", not doc.paginated)
    check("a4 is still paginated", Document({"blocks": []}).paginated)
    check("a paginated document is not marked continuous",
          "ig-continuous" not in
          check_document.document_classes(Document({"blocks": []}).render()))

    # A bleed block escapes the measure. That is the whole point of the target,
    # and it is meaningless (and breaks the page box) on paper.
    doc, classes, body = build([{"type": "chips", "items": ["A"], "bleed": True}])
    check("a bleed block is marked", "ig-bleed" in body)
    paper, _ = Document({"meta": {"page": "a4"},
                         "blocks": [{"type": "chips", "items": ["A"], "bleed": True}]}), None
    check("bleed on paper warns rather than silently doing nothing",
          any("bleed" in w for w in paper.warnings), str(paper.warnings))

    # The word budget follows the document to the new target. Per page is
    # meaningless with no pages, so it is charged per block instead.
    check("the per-block budget is the most chrome one block may legally carry",
          density.WORDS_PER_BLOCK["graphic"] >=
          density.CAPS["graphic"]["title"] + density.CAPS["graphic"]["subtitle"]
          + density.CAPS["graphic"]["note"],
          str(density.WORDS_PER_BLOCK["graphic"]))
    check("report gets a larger per-block budget",
          density.WORDS_PER_BLOCK["report"] > density.WORDS_PER_BLOCK["graphic"])

    # Paper checks must not follow the document off paper. `sparse-pages` and
    # `near-empty-page` describe a sheet; on a continuous document they would
    # fire on behaviour that is exactly correct.
    import tempfile
    spec = {"meta": {"title": "Scroll", "page": "scroll"}, "blocks": [
        {"type": "hero", "title": "A claim", "subtitle": "One line under it."},
        {"type": "chips", "items": ["One", "Two", "Three"], "bleed": True},
        {"type": "bar", "categories": ["A", "B"], "values": [3, 5], "title": "Two things"},
    ]}
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "scroll.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(Document(spec).render())
        codes = {f["code"] for f in check_document.check(path)}
    for paper_check in ("sparse-pages", "near-empty-page", "long", "no-pdf"):
        check(f"a continuous document is not judged as paper: {paper_check}",
              paper_check not in codes, str(sorted(codes)))
    check("a continuous document with a bleed does not get the no-bleed note",
          "no-bleed" not in codes, str(sorted(codes)))


def _error(fn) -> str:
    try:
        fn()
    except BaseException as exc:  # noqa: BLE001
        return str(exc)
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true", help="also build fixtures to PDF")
    args = parser.parse_args()

    test_svg_primitives()
    test_theme()
    test_density()
    test_figure()
    test_scroll()
    test_graphic_layout()
    test_every_block_renders()
    test_block_contracts()
    test_delta_direction()
    test_label_fitting()
    test_compiler()
    test_extractor()
    test_linter()
    test_derivation()
    test_leading_numbers()
    test_fixtures(args.render)

    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        print("\nfailures:")
        for name, detail in FAILED:
            print(f"  - {name}" + (f", {detail}" if detail else ""))
        sys.exit(1)


if __name__ == "__main__":
    main()
