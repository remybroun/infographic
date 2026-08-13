#!/usr/bin/env python3
"""One entry point for the infographic skill.

    ig.py extract  <source>          read a document into a fact ledger + candidate forms
    ig.py build    <spec.json>       compile a spec into HTML
    ig.py render   <spec.json>       compile AND render to PDF (the usual command)
    ig.py check    <doc.html>        lint a built document
    ig.py shoot    <doc.html>        render it to PNGs so you can LOOK at it
    ig.py catalog                    list every block type
    ig.py catalog  --sheet out.pdf   render a proof sheet of every block
    ig.py themes                     list themes
    ig.py validate <theme>           run a theme through the colour checks
    ig.py new      <out.json>        write a starter spec

Everything is also usable as a library: `from build import build`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from lib import registry  # noqa: E402
from lib.theme import Theme  # noqa: E402


def _run(script, *args):
    return subprocess.call([sys.executable, os.path.join(HERE, script), *args])


# ------------------------------------------------------------------ render --

def cmd_render(args):
    import build as build_mod
    import render_pdf

    spec_path = args.spec
    stem = os.path.splitext(os.path.basename(spec_path))[0]
    out_dir = args.out_dir or os.path.join(os.getcwd(), "out")
    os.makedirs(out_dir, exist_ok=True)
    html_path = args.html or os.path.join(out_dir, f"{stem}.html")
    pdf_path = args.pdf or os.path.join(out_dir, f"{stem}.pdf")

    html, warnings = build_mod.build(spec_path, html_path, args.theme, args.page,
                                     tables=False if args.no_tables else None,
                                     texture=True if args.texture else None,
                                     density=getattr(args, "density", None))
    print(f"[build] {html_path}")
    for warning in warnings:
        print(f"[warn]  {warning}")

    # A continuous document's deliverable is the HTML. Rendering it to PDF by
    # default would be quietly reintroducing the page box it exists to escape,
    # and the resulting file is a fallback, not the artifact. Ask for it.
    import check_document
    continuous = "ig-continuous" in check_document.document_classes(html)
    if continuous and not args.pdf:
        pdf_path = None
    if pdf_path:
        render_pdf.render(html_path, pdf_path, args.chrome, args.wait)
        pages = render_pdf.page_count(pdf_path)
        print(f"[pdf]   {pdf_path}"
              + (f"  ({pages} page{'s' if pages != 1 else ''})" if pages else ""))

    if args.shoot or (continuous and not args.no_shoot):
        cmd_shoot(argparse.Namespace(
            html=html_path, pdf=pdf_path, out_dir=None, chrome=args.chrome,
            dpi=80, per_shot=6, width=1280, height=1600, wait=args.wait))

    if not args.no_check:
        findings = check_document.check(html_path, pdf_path)
        check_document.report(findings)
        if any(f["level"] == "error" for f in findings):
            return 1
    return 0


# ------------------------------------------------------------------- shoot --

# Everything the linter cannot see. It measures word counts, ink coverage and
# structure; it has never once looked at the document. Label collisions,
# overflowing shapes, an arrow pointing at nothing, a drawing that is simply
# ugly, all of those survive a clean check and none survive being looked at.
#
# Be honest about the ceiling: this renders the document to images so that
# somebody (or something) can look at them. It catches geometry. It cannot tell
# you the drawing was the wrong drawing.

SHOT_CSS = """
<style>
  .ig-shot-hide { display: none !important; }
  .ig-running-footer { display: none !important; }
  body { padding: 0 !important; }
</style>
"""


def _shot_slices(html: str, per_shot: int = 6):
    """Split a built document into shots, one per section where it has them.

    Sections are the author's own grouping, so they are better shot boundaries
    than an arbitrary block count. A document with no sections falls back to
    fixed-size windows.
    """
    import re
    starts = [m.start() for m in re.finditer(r'<(?:figure|div) class="ig-block[ "]', html)]
    if not starts:
        return []
    section_at = {i for i, pos in enumerate(starts)
                  if 'ig-section-head' in html[pos:starts[i + 1] if i + 1 < len(starts)
                                               else len(html)]}
    groups, current = [], []
    for index in range(len(starts)):
        if current and (index in section_at or len(current) >= per_shot):
            groups.append(current)
            current = []
        current.append(index)
    if current:
        groups.append(current)
    return groups


def cmd_shoot(args):
    """Render a built document to PNGs so it can actually be looked at."""
    import check_document
    import render_pdf

    html_path = os.path.abspath(args.html)
    if not os.path.isfile(html_path):
        print(f"[shoot] not found: {html_path}", file=sys.stderr)
        return 1
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    # From the body tag, never from the document: `.ig-continuous` is also a
    # selector in the stylesheet, so searching the whole file always matches.
    continuous = "ig-continuous" in check_document.document_classes(html)
    out_dir = args.out_dir or os.path.join(os.path.dirname(html_path), "shots")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(html_path))[0]

    # A paginated document already has an exact rendering: its PDF. Rasterising
    # that is both faster and truer than re-rendering the HTML, because it is
    # the artifact the reader gets.
    pdf = args.pdf or os.path.splitext(html_path)[0] + ".pdf"
    if not continuous and os.path.isfile(pdf):
        if not shutil.which("pdftoppm"):
            print("[shoot] pdftoppm not found (install poppler), cannot rasterise the PDF",
                  file=sys.stderr)
            return 1
        subprocess.run(["pdftoppm", "-png", "-r", str(args.dpi), pdf,
                        os.path.join(out_dir, stem)], check=False)
        shots = sorted(f for f in os.listdir(out_dir) if f.startswith(stem) and f.endswith(".png"))
        for name in shots:
            print(f"[shoot] {os.path.join(out_dir, name)}")
        print(f"[shoot] {len(shots)} page(s), now LOOK at them")
        return 0

    # A continuous document has no pages, so shots are built by hiding every
    # block outside the window and screenshotting what is left. One Chrome run
    # per shot: slower than a PDF, but it is the only way to see a document
    # whose whole point is not fitting in a page box.
    groups = _shot_slices(html, args.per_shot)
    if not groups:
        print("[shoot] no blocks found", file=sys.stderr)
        return 1

    import re as _re
    binary = render_pdf.find_chrome(args.chrome)
    written = []
    for number, group in enumerate(groups, start=1):
        keep = set(group)
        index = [-1]

        def mark(match):
            index[0] += 1
            if index[0] in keep:
                return match.group(0)
            return match.group(0).replace('class="ig-block', 'class="ig-shot-hide ig-block', 1)

        shot_html = _re.sub(r'<(?:figure|div) class="ig-block[ "][^>]*>', mark, html)
        shot_html = shot_html.replace("</head>", SHOT_CSS + "</head>", 1)
        tmp = os.path.join(out_dir, f".{stem}-shot-{number:02d}.html")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(shot_html)
        png = os.path.join(out_dir, f"{stem}-{number:02d}.png")
        subprocess.run([binary, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--no-first-run", "--no-default-browser-check",
                        f"--window-size={args.width},{args.height}",
                        f"--virtual-time-budget={args.wait}",
                        f"--screenshot={png}", f"file://{tmp}"],
                       capture_output=True, timeout=120)
        os.remove(tmp)
        if os.path.isfile(png):
            written.append(png)
            print(f"[shoot] {png}")
    print(f"[shoot] {len(written)} shot(s), now LOOK at them")
    return 0 if written else 1


# ----------------------------------------------------------------- catalog --

SAMPLES_PATH = os.path.join(SKILL, "fixtures", "catalog-samples.json")


def cmd_catalog(args):
    if not args.sheet:
        grouped = registry.by_family()
        for family, blocks in grouped.items():
            print(f"\n{family.upper()}, {registry.FAMILIES[family]}")
            for name, entry in blocks:
                print(f"  {name:<14} span {entry.get('span', 12):>2}   {entry['use_when']}")
                if entry.get("instead_of"):
                    print(f"  {'':<14}            instead of: {entry['instead_of']}")
        print(f"\n{len(registry.REGISTRY)} block types. "
              f"Aliases: {', '.join(sorted(registry.ALIASES))}")
        return 0

    # Proof sheet: every block drawn with sample data, in the chosen theme.
    import build as build_mod
    import render_pdf
    from selftest import MINIMAL

    blocks = [{
        "type": "hero",
        "kicker": f"theme: {args.theme or 'default'}",
        "title": "Block catalog",
        "subtitle": "Every registered block, drawn with sample data. Use this to check a "
                    "theme change against the whole vocabulary at once.",
    }]
    for family, entries in registry.by_family().items():
        blocks.append({"type": "section", "title": family.title(),
                       "lede": registry.FAMILIES[family]})
        for name, entry in entries:
            if name in ("hero", "section", "raw", "spacer"):
                continue
            payload = dict(MINIMAL.get(name, {}))
            payload["type"] = name
            # The sheet is a legibility check, so nothing is drawn below the
            # width where it stops being readable.
            payload["span"] = max(entry.get("span", 12), 5)
            payload.setdefault("subtitle", entry["use_when"])
            payload["title"] = f"{name}"
            payload["frame"] = "card"
            blocks.append(payload)

    # The sheet draws `prose` and the other report-only blocks on purpose, since
    # it is a proof of the whole vocabulary rather than a document making an
    # argument. It is the one place report density is the right default.
    spec = {"meta": {"title": "Block catalog", "theme": args.theme or "default",
                     "page": "a4", "density": "report",
                     "footer_left": "Block catalog",
                     "footer_right": args.theme or "default"},
            "blocks": blocks}
    html_path = os.path.splitext(args.sheet)[0] + ".html"
    _, warnings = build_mod.build(spec, html_path, args.theme)
    render_pdf.render(html_path, args.sheet)
    pages = render_pdf.page_count(args.sheet)
    print(f"[catalog] {args.sheet}" + (f"  ({pages} pages)" if pages else ""))
    for warning in warnings:
        print(f"[warn]  {warning}")
    return 0


# --------------------------------------------------------------------- new --

STARTER = {
    "meta": {
        "title": "Replace me with the claim, not the topic",
        "theme": "default",
        "page": "a4",
        "paper": "panel",
        "footer_left": "Replace me",
        "footer_right": ""
    },
    "blocks": [
        {"type": "hero", "kicker": "Explainer",
         "title": "State the finding as a sentence",
         "subtitle": "One line saying what the reader should now believe.",
         "lede": "Two or three sentences of setup. Say what the document covers and "
                 "what it does not."},
        {"type": "section", "number": "01", "title": "First move",
         "lede": "Why this section exists."},
        {"type": "prose", "span": 12, "text": "Explain the mechanism here. The chart "
         "below is evidence for this paragraph, not a replacement for it."},
        {"type": "bar", "span": 8, "title": "Replace with a real comparison",
         "categories": ["Alpha", "Beta", "Gamma"], "values": [12, 30, 21],
         "sort": "desc", "value_label": "Count",
         "note": "Say where the numbers came from."},
        {"type": "kpi", "span": 4, "items": [
            {"label": "Headline number", "value": 1284, "compact": True,
             "delta": 12.4, "delta_period": "vs last period"}]},
        {"type": "footnotes", "items": ["Source: replace me.", "Method: replace me."]}
    ]
}


def cmd_new(args):
    path = args.out
    if os.path.exists(path) and not args.force:
        print(f"[new] {path} exists; pass --force to overwrite", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    spec = dict(STARTER)
    spec["meta"] = dict(STARTER["meta"], theme=args.theme or "default",
                        page=args.page or "a4")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"[new] wrote {path}")
    return 0


# -------------------------------------------------------------------- main --

def main():
    parser = argparse.ArgumentParser(prog="ig.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("extract", help="read a document into a fact ledger")
    p.add_argument("source")
    p.add_argument("-o", "--out")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=lambda a: _run("extract_source.py", a.source,
                                     *(["-o", a.out] if a.out else []),
                                     *(["--json"] if a.json else [])))

    p = sub.add_parser("build", help="compile a spec into HTML")
    p.add_argument("spec")
    p.add_argument("-o", "--out")
    p.add_argument("--theme")
    p.add_argument("--page")
    p.set_defaults(fn=lambda a: _run("build.py", a.spec,
                                     *(["-o", a.out] if a.out else []),
                                     *(["--theme", a.theme] if a.theme else []),
                                     *(["--page", a.page] if a.page else [])))

    p = sub.add_parser("render", help="compile a spec and render it to PDF")
    p.add_argument("spec")
    p.add_argument("--out-dir")
    p.add_argument("--html")
    p.add_argument("--pdf")
    p.add_argument("--theme")
    p.add_argument("--page")
    p.add_argument("--chrome")
    p.add_argument("--wait", type=int, default=1800)
    p.add_argument("--no-tables", action="store_true")
    p.add_argument("--texture", action="store_true")
    p.add_argument("--density", choices=("graphic", "report"),
                   help="graphic (default): titles and indicators only. "
                        "report: allow body prose")
    p.add_argument("--no-check", action="store_true")
    p.add_argument("--shoot", action="store_true",
                   help="also render section screenshots (automatic for page: scroll)")
    p.add_argument("--no-shoot", action="store_true")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("shoot", help="render a built document to PNGs so you can look at it")
    p.add_argument("html")
    p.add_argument("--pdf")
    p.add_argument("--out-dir")
    p.add_argument("--chrome")
    p.add_argument("--dpi", type=int, default=80, help="raster DPI for paginated documents")
    p.add_argument("--per-shot", type=int, default=6,
                   help="max blocks per shot when the document has no sections")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=1600)
    p.add_argument("--wait", type=int, default=1500)
    p.set_defaults(fn=cmd_shoot)

    p = sub.add_parser("check", help="lint a built document")
    p.add_argument("html")
    p.add_argument("--pdf")
    p.set_defaults(fn=lambda a: _run("check_document.py", a.html,
                                     *(["--pdf", a.pdf] if a.pdf else [])))

    p = sub.add_parser("catalog", help="list or draw every block type")
    p.add_argument("--sheet", help="render a proof-sheet PDF here")
    p.add_argument("--theme")
    p.set_defaults(fn=cmd_catalog)

    p = sub.add_parser("themes", help="list available themes")
    p.set_defaults(fn=lambda a: [print(f"  {n:<10} {Theme.load(n).data.get('label', '')}")
                                 for n in Theme.available()] and 0 or 0)

    p = sub.add_parser("validate", help="run a theme through the colour checks")
    p.add_argument("theme", nargs="?", default="default")
    p.add_argument("--all", action="store_true")
    p.set_defaults(fn=lambda a: _run("validate_theme.py",
                                     *(["--all"] if a.all else [a.theme])))

    p = sub.add_parser("new", help="write a starter spec")
    p.add_argument("out")
    p.add_argument("--theme")
    p.add_argument("--page")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("selftest", help="run the assertion suite")
    p.add_argument("--render", action="store_true")
    p.set_defaults(fn=lambda a: _run("selftest.py", *(["--render"] if a.render else [])))

    args = parser.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
