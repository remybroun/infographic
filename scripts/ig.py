#!/usr/bin/env python3
"""One entry point for the infographic skill.

    ig.py extract  <source>          read a document into a fact ledger + candidate forms
    ig.py ladder   <rungs.json>      check the explanation ORDER, before anything is drawn
    ig.py build    <spec.json>       compile a spec into HTML
    ig.py render   <spec.json>       compile AND render to PDF (the usual command)
    ig.py check    <doc.html>        lint a built document
    ig.py shoot    <doc.html>        render it to PNGs so you can LOOK at it
    ig.py sketch   <blocks.json>     ONE block, on its own, in two seconds
    ig.py blind    <doc.html>        the stranger test, briefed for a fresh reader
    ig.py measure  <spec.json>       per-block height and words: will it fit?
    ig.py catalog                    list every block type
    ig.py catalog  <type>            one block: payload example, keys, use-when
    ig.py catalog  --sheet out.pdf   render a proof sheet of every block
    ig.py themes                     list themes
    ig.py validate <theme>           run a theme through the colour checks
    ig.py new      <out.json>        write a starter spec

Everything is also usable as a library: `from build import build`.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from lib import pictograms  # noqa: E402
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


# ------------------------------------------------------------------ sketch --

# One block, drawn on its own, at the width it will really land on, in about two
# seconds.
#
# WHY THIS EXISTS. Looking at an authored figure used to cost a full build, a
# full PDF render and a hunt for the right page. That is slow enough that it
# happens once, and "draw the other composition and compare the two" is exactly
# the move that has to be cheap or it never happens at all. Mandating iteration
# without a fast loop mandates nothing: the first drawing that renders wins by
# being the only one anybody ever saw.
#
# It also computes the one failure references/drawing.md says can only be caught
# by eye: a viewbox and a column that disagree, which silently rescales every
# label in the drawing.

def _sketch_load(path):
    """A spec, a bare block, or a list of blocks. All three are things an author
    actually has on disk mid-draft, and a comp file is usually not a spec yet."""
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    if isinstance(payload, dict) and isinstance(payload.get("blocks"), list):
        return dict(payload.get("meta") or {}), list(payload["blocks"])
    if isinstance(payload, list):
        return {}, list(payload)
    if isinstance(payload, dict) and payload.get("type"):
        return {}, [payload]
    return None, None


def _sketch_selection(blocks, args):
    """Which blocks to draw. Defaults to the authored figures, because they are
    the blocks whose geometry is not on rails and therefore the only ones whose
    appearance is genuinely unknown before rendering."""
    if args.id or args.index:
        wanted, missing = [], []
        for ident in args.id or []:
            hits = [i for i, b in enumerate(blocks) if str(b.get("id")) == ident]
            if hits:
                wanted.extend(hits)
            else:
                missing.append(ident)
        for number in args.index or []:
            if 0 <= number < len(blocks):
                wanted.append(number)
            else:
                missing.append(str(number))
        if missing:
            listing = ", ".join(
                f"{i}:{b.get('type')}" + (f"#{b['id']}" if b.get("id") else "")
                for i, b in enumerate(blocks))
            print(f"[sketch] no block at {', '.join(missing)}. This file has "
                  f"{len(blocks)}: {listing}", file=sys.stderr)
            return None
        return sorted(set(wanted))

    figures = [i for i, b in enumerate(blocks)
               if isinstance(b, dict) and registry.resolve(b.get("type"))[0] == "figure"]
    if figures and len(figures) < len(blocks):
        print(f"[sketch] drawing the {len(figures)} authored figure(s); "
              f"--index or --id for anything else")
        return figures
    if len(blocks) <= 6:
        return list(range(len(blocks)))
    print(f"[sketch] {len(blocks)} blocks and no authored figure among them. "
          f"Name what to draw with --index or --id.", file=sys.stderr)
    return None


def cmd_sketch(args):
    import build as build_mod
    import render_pdf

    src = os.path.abspath(args.spec)
    if not os.path.isfile(src):
        print(f"[sketch] not found: {src}", file=sys.stderr)
        return 1
    meta, blocks = _sketch_load(src)
    if blocks is None:
        try:
            with open(src, encoding="utf-8") as fh:
                probe = json.load(fh)
        except Exception:  # noqa: BLE001
            probe = None
        if isinstance(probe, dict) and str(probe.get("body") or "").strip():
            print("[sketch] this is an authored spec: the page is its own "
                  "composition,\n         so there are no blocks to render one "
                  "at a time.\n         Build it and look at the whole thing:\n"
                  "           python3 scripts/ig.py render <spec> --out-dir out\n"
                  "           python3 scripts/ig.py shoot out/<name>.html",
                  file=sys.stderr)
            return 1
        print("[sketch] expected a spec, one block, or a list of blocks",
              file=sys.stderr)
        return 1
    if not blocks:
        print("[sketch] no blocks in that file", file=sys.stderr)
        return 1

    chosen = _sketch_selection(blocks, args)
    if chosen is None:
        return 1

    out_dir = args.out_dir or os.path.join(os.path.dirname(src), "sketches")
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(src))[0]
    binary = render_pdf.find_chrome(args.chrome)
    sys.path.insert(0, os.path.join(SKILL, "assets"))
    import trim_png

    written = []
    for index in chosen:
        block = dict(blocks[index])
        if args.span:
            block["span"] = args.span
        mini = {"meta": dict(meta), "blocks": [block]}
        # `ladder` and `mode` go the same way `supersedes` does: they are claims
        # about a whole document, and one block drawn alone is not one. A sketch
        # that failed the ladder check would be reporting a fault in a document
        # the author never asked to build.
        for key in ("footer_left", "footer_right", "supersedes", "ladder", "mode"):
            mini["meta"].pop(key, None)

        doc = build_mod.Document(mini, args.theme, args.page)
        html = doc.render()
        width = int(round(float(str(doc.doc_width_css).rstrip("px")))) or 800

        name = block.get("id") or block.get("type") or "block"
        label = f"{index:02d}-{re.sub(r'[^A-Za-z0-9_-]+', '-', str(name))}"
        tmp = os.path.join(out_dir, f".{stem}-{label}.html")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(html.replace("</head>", SHOT_CSS + "</head>", 1))
        png = os.path.join(out_dir, f"{stem}-{label}.png")
        subprocess.run([binary, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--no-first-run", "--no-default-browser-check",
                        f"--window-size={width},{args.height}",
                        f"--virtual-time-budget={args.wait}",
                        f"--screenshot={png}", f"file://{tmp}"],
                       capture_output=True, timeout=120)
        os.remove(tmp)
        if not os.path.isfile(png):
            print(f"[sketch] Chrome wrote nothing for blocks[{index}]", file=sys.stderr)
            continue

        kept = trim_png.trim(png)
        written.append(png)
        print(f"[sketch] {png}   {width}px wide"
              + (f", {kept}px tall" if kept else ""))
        if kept and kept >= args.height:
            print(f"         it fills the {args.height}px window, so it may be cut "
                  f"off: re-run with --height {args.height * 2}")
        for warning in doc.warnings:
            print(f"[warn]   {warning}")
        _sketch_viewbox(block, doc)

    if written:
        print(f"[sketch] {len(written)} drawing(s), now LOOK at them")
    return 0 if written else 1


def _sketch_viewbox(block, doc):
    """Whether the drawing's own units and the column it lands in agree.

    A figure is laid out in user units and then scaled to fit its column, so the
    scale factor lands on the type too: a 1080-unit drawing in a 640px column
    renders its 12px labels at 7px. Every size in references/drawing.md is only
    true at 1:1, and nothing else in the toolchain can see this.
    """
    viewbox = str(block.get("viewbox") or block.get("viewBox") or "").split()
    if len(viewbox) != 4:
        return
    try:
        units = float(viewbox[2])
    except ValueError:
        return
    span = int(block.get("span", 12) or 12)
    column = doc.column_px * span + doc.gutter * (span - 1)
    if units <= 0 or column <= 0:
        return
    scale = column / units
    if 0.85 <= scale <= 1.18:
        return
    print(f"         viewbox is {units:.0f} units wide in a {column:.0f}px column, "
          f"so it scales by {scale:.2f}:")
    print(f"         a 12px ig-fig-label renders at {12 * scale:.1f}px and a 1.6px "
          f"hairline at {1.6 * scale:.1f}px.")
    print(f"         Author at \"viewbox\": \"0 0 {column:.0f} …\" instead.")


# ------------------------------------------------------------------- blind --

# The one check nothing in this repository can perform.
#
# The skill's whole success condition is that a stranger can look at the page
# and say what the subject is. The linter has never looked at a document, and
# the author cannot be the reader: they know what it was supposed to say, so
# they see the intended document rather than the printed one. A reader with no
# context is the only instrument that measures the actual claim.
#
# This prints the brief verbatim rather than describing it, because a brief
# retold in the caller's words leaks the answer into the question. "Does this
# read as a document about deposit refunds?" is not the test. "What is this
# about?" is.

BLIND_BRIEF = """\
You are being shown a document you have never seen before. Do not go looking
for its source, its spec, or the conversation that produced it: your entire
value here is that you do not know what it was meant to say.

Read these images, in order:

{paths}

Then answer five things, briefly and literally:

1. What is this document about? One sentence, in your own words.
2. What is it claiming? The single thing it wants you to believe by the end.
3. Quote every word, label or abbreviation on the page that you could not
   confidently define to a colleague. Quote them exactly. Do not guess at
   meanings, and do not skip one because you can infer it from context: that
   inference is the thing being measured.
4. Which picture did you look at first, and which did you understand last?
5. Was there anything you had to read the body text to understand, that the
   pictures should have carried?

Do not review the design, suggest improvements, praise it, or soften anything.
If you cannot tell what the document is about, say exactly that and stop.\
"""


def cmd_blind(args):
    html_path = os.path.abspath(args.html)
    shots = []
    if os.path.isdir(html_path):
        shots = [os.path.join(html_path, f) for f in sorted(os.listdir(html_path))
                 if f.endswith(".png")]
    else:
        if not os.path.isfile(html_path):
            print(f"[blind] not found: {html_path}", file=sys.stderr)
            return 1
        shot_dir = os.path.join(os.path.dirname(html_path), "shots")
        stem = os.path.splitext(os.path.basename(html_path))[0]
        if os.path.isdir(shot_dir):
            shots = [os.path.join(shot_dir, f) for f in sorted(os.listdir(shot_dir))
                     if f.endswith(".png") and f.startswith(stem)]
        if not shots:
            print("[blind] no shots yet, rendering them")
            code = cmd_shoot(argparse.Namespace(
                html=html_path, pdf=None, out_dir=None, chrome=args.chrome,
                dpi=args.dpi, per_shot=6, width=1280, height=1600, wait=1500))
            if code:
                return code
            shots = [os.path.join(shot_dir, f) for f in sorted(os.listdir(shot_dir))
                     if f.endswith(".png") and f.startswith(stem)]

    if not shots:
        print("[blind] no PNGs to show anyone", file=sys.stderr)
        return 1

    rule = "-" * 72
    print(f"\n[blind] {len(shots)} shot(s). Send a subagent the text between the "
          f"rules, and\n        nothing else: no source, no spec, no claim, no "
          f"summary of either.\n\n{rule}")
    print(BLIND_BRIEF.format(paths="\n".join(f"  {p}" for p in shots)))
    print(rule)
    print("\n  Then compare what comes back with the claim you wrote at step 2:")
    if args.claim:
        print(f"\n    the claim: {args.claim}\n")
    print("""\
    · answer 1 names the subject in the reader's own words → it landed
    · answer 1 describes the layout ("a diagram and some charts"), hedges, or
      names the mechanism when the claim was about a reader → the spine is
      not on the page, and no amount of polish adds it
    · answer 2 is not your claim → the document argues something you did not
      write, which is the failure the two cover-tests are meant to catch
    · every term in answer 3 needed a `definitions` block or a rewrite into
      words. That list is a work item, not an opinion
    · answer 4 out of order → hierarchy problem: the biggest thing on the page
      is not the most important thing on it
    · anything in answer 5 is a picture that was not drawn""")
    print("\n  Their reading is evidence about the document, not a request for "
          "changes.\n  A stranger who misreads it is the document being wrong, "
          "not the stranger.")
    return 0


# ------------------------------------------------------------------ ladder --

LADDER_BRIEF = """\
Below is an explanation of a subject, written as a numbered sequence. You have
no other context, and you are not expected to have any.

Read it once, in order, and answer:

1. What is this about? One sentence, in your own words.
2. At which number did you first lose the thread, if any? Say which and why.
3. Which words did you have to already know to get through it? List them.
4. What question does the sequence leave you asking that it never answers?
5. Is anything explained before the thing it depends on? Name the pair.

Do not review the writing, suggest improvements, or be encouraging. If it never
became clear what the subject is, say exactly that and stop.

{rungs}
"""


def cmd_ladder(args):
    """The ladder, checked and read back, before a single block is chosen.

    This is the cheapest instrument in the skill and the earliest. `blind` is
    the only real test of whether a stranger understands the document, and it
    runs at step 10, against a built artifact, where its verdict costs a
    rebuild and therefore gets rationalised away. The same question asked of
    the ladder alone costs one turn and no rendering, and the answer arrives
    while the order is still free to change.
    """
    from lib import ladder as ladder_mod

    path = os.path.abspath(args.spec)
    if not os.path.isfile(path):
        print(f"[ladder] not found: {path}", file=sys.stderr)
        return 1
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    # A bare list of rungs is legal input, because the ladder is written at step
    # 2.5 and the spec does not exist until step 7. Requiring a spec would mean
    # the check can only run after the document has been built around it, which
    # is the ordering this whole step exists to break.
    spec = data if isinstance(data, dict) and "blocks" in data else None
    if spec is None:
        rungs = data if isinstance(data, list) else (data or {}).get("ladder")
        if not isinstance(rungs, list):
            print("[ladder] expected a spec, or a JSON list of rungs",
                  file=sys.stderr)
            return 1
        spec = {"meta": {"mode": "lesson", "ladder": rungs}, "blocks": []}

    print("\n  The ladder, as a reader climbs it:\n")
    print(ladder_mod.summary(spec))

    if args.brief:
        rule = "-" * 72
        numbered = "\n".join(
            f"{n}. {r.get('says', '')}"
            for n, r in enumerate(spec["meta"].get("ladder") or [], 1)
            if isinstance(r, dict))
        print(f"\n[ladder] send a subagent the text between the rules, and "
              f"nothing else:\n        no source, no spec, no subject line, no "
              f"summary of any of them.\n\n{rule}")
        print(LADDER_BRIEF.format(rungs=numbered))
        print(rule)
        print("\n  What comes back is evidence about the explanation, not a "
              "request for changes:\n"
              "    · answer 1 is not the subject → the ladder teaches something "
              "else than\n      you think it does, and the document will too\n"
              "    · answer 2 names a rung → that rung is doing two jobs; split "
              "it\n"
              "    · anything in answer 3 you did not plan to teach is a missing "
              "rung\n"
              "    · answer 5 is the forward reference the build cannot see yet, "
              "because\n      the terms are still in your head rather than in "
              "`introduces`")
        return 0

    errors, warnings = ladder_mod.audit(spec, registry)
    for warning in warnings:
        print(f"\n[warn] {warning}")
    if errors:
        print()
        for error in errors:
            print(f"[error] {error}")
        print(f"\n  {len(errors)} fault(s). A lesson is the one order in which "
              f"each idea can be\n  understood using only the ones before it.")
        return 1
    if spec.get("blocks"):
        print("\n  Order holds, and no term is used before the rung that "
              "teaches it.")
    else:
        print("\n  Shape is legal. Nothing is checked against a page yet: rerun "
              "this against\n  the spec once the rungs have blocks to land on.")
    print("  Now hand it to someone who has never met the subject: "
          "ig.py ladder <file> --brief")
    return 0


# ----------------------------------------------------------------- measure --

def cmd_measure(args):
    """What the spec costs, in pixels and in words, before anything is rendered.

    Both numbers were previously only knowable by rendering and reading the
    linter, which turns fitting a page into a guessing loop: the height of a
    block comes out of text wrapping and the theme's type scale, and the word
    total comes out of every `<text>` in every authored figure.
    """
    sys.path.insert(0, os.path.join(SKILL, "assets"))
    import build as build_mod
    import measure_blocks
    from check_document import _visible_words, split_document
    from lib import density as den

    measured = measure_blocks.measure(args.spec)
    blocks, heights = measured["blocks"], measured["heights"]
    meta = measured["spec"].get("meta", {})
    mode = den.resolve(meta.get("density"), args.density)
    page_key = (meta.get("page") or "a4").lower()

    if measured["authored"]:
        # An authored page has no blocks to add up, and the earlier version of
        # this branch said so and stopped. That was worse than useless: the
        # linter's overflow hint sends you here, and being told "there is
        # nothing to measure" on a document that is spilling leaves you fitting
        # the sheet by rendering, screenshotting and guessing at pixels. So
        # measure the thing that actually has a height, which is <main>.
        height = measured["main_px"]
        total_words = _visible_words(split_document(measured["html"])[1])
        # Hand-written SVG labels are reading matter and the rendered-document
        # word count strips every <svg> wholesale, so they are added back from
        # the source, where a placeholder has not yet expanded into a chart full
        # of axis ticks that are NOT the author's prose.
        drawn = den.svg_words(measured["spec"].get("body", ""))
        if page_key == "scroll":
            print(f"\n  {height}px tall, continuous, so nothing to fit")
            _verdict(f"{total_words + drawn} words ({drawn} of them inside "
                     f"drawings), budget {den.WORDS_PER_BLOCK[mode]} per block",
                     total_words + drawn, den.WORDS_PER_BLOCK[mode] * 6, "words")
            return 0
        size, _w, h_mm, margins = build_mod.PAGES[page_key]
        per_page = (h_mm - margins[0] - margins[2]) * build_mod.MM
        pages = max(1, -(-height // int(per_page)))
        print(f"\n  authored page: {height}px tall, {size} holds {per_page:.0f}px a sheet")
        if height > per_page:
            print(f"  → {height - per_page:.0f}px past one sheet, so the render "
                  f"is {pages} or more:\n    an element that cannot break moves "
                  f"to the next sheet whole, exactly as a grid row\n    does, so "
                  f"`ig.py render` is still the count that counts. Your CSS owns "
                  f"this\n    height: shrink a viewBox, cut a row, or take the "
                  f"extra sheet.")
        else:
            print(f"  → one sheet, {per_page - height:.0f}px spare")
        _verdict(f"{total_words + drawn} words ({drawn} of them inside drawings), "
                 f"budget {den.WORDS_PER_PAGE[mode] * pages} at {mode} density",
                 total_words + drawn, den.WORDS_PER_PAGE[mode] * pages, "words")
        return 0

    print(f"\n  #  height  span  {'type':<12} words  title")
    for index, block in enumerate(blocks):
        words = den.block_words(block, registry)
        title = block.get("title") or block.get("label") or ""
        print(f"{index:3d}  {heights.get(index, 0):5d}px  {int(block.get('span', 12)):>4}  "
              f"{block.get('type', '?'):<12} {words:5d}  {title[:40]}")

    total_words = _visible_words(split_document(measured["html"])[1])

    if page_key == "scroll":
        cap = den.WORDS_PER_BLOCK[mode]
        per = total_words / len(blocks) if blocks else 0
        print(f"\n  {measured['grid_px']}px tall, continuous, so nothing to fit")
        _verdict(f"{total_words} words over {len(blocks)} blocks, {per:.0f} each",
                 per, cap, "per block")
        return 0

    size, _w_mm, h_mm, margins = build_mod.PAGES[page_key]
    per_page = (h_mm - margins[0] - margins[2]) * build_mod.MM
    grid = measured["grid_px"]
    pages = max(1, -(-grid // int(per_page)))
    print(f"\n  {grid}px of blocks, {size} holds {per_page:.0f}px a page")
    if grid > per_page:
        print(f"  → {grid - per_page:.0f}px past one sheet. Shave that, or take "
              f"{pages} pages. A row never splits,\n    so the render is "
              f"{pages} or more: `ig.py render` is the count that counts.")
    else:
        print(f"  → one sheet, {per_page - grid:.0f}px spare")
    _verdict(f"{total_words} words, budget {den.WORDS_PER_PAGE[mode] * pages} "
             f"at {mode} density", total_words,
             den.WORDS_PER_PAGE[mode] * pages, "words")
    return 0


def _verdict(label, value, cap, unit):
    over = value - cap
    if over > 0:
        print(f"  {label}  → {over:.0f} {unit} over, cut that much")
    else:
        print(f"  {label}  → fits, {abs(over):.0f} {unit} spare")


# ----------------------------------------------------------------- catalog --

SAMPLES_PATH = os.path.join(SKILL, "fixtures", "catalog-samples.json")
DOCS_DIR = os.path.join(SKILL, "references", "catalog")
DOCS_REL = os.path.join("references", "catalog")


def _doc_index():
    """Map every block name to the doc section(s) that describe it.

    Built by scanning headings rather than hard-coding a table, because the
    registry's families and the files on disk deliberately do not line up:
    `funnel` is documented under both part-to-whole and process, `matrix` under
    both quantity and structure, and one heading can cover four blocks at once.
    Longest section wins as the primary; the rest become cross-references.
    """
    index = {}
    if not os.path.isdir(DOCS_DIR):
        return index
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".md") or filename == "README.md":
            continue
        with open(os.path.join(DOCS_DIR, filename), encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        heads = [i for i, line in enumerate(lines) if line.startswith("## ")]
        for pos, start in enumerate(heads):
            end = heads[pos + 1] if pos + 1 < len(heads) else len(lines)
            body = "\n".join(lines[start:end]).rstrip()
            for name in re.findall(r"`([a-z_]+)`", lines[start]):
                if name in registry.REGISTRY:
                    index.setdefault(name, []).append((filename, start + 1, body))
    for sections in index.values():
        sections.sort(key=lambda section: -len(section[2]))
    return index


def _catalog_list():
    """Every block, grouped by family, with the file that documents each family."""
    index = _doc_index()
    for family, blocks in registry.by_family().items():
        files = {}
        for name, _ in blocks:
            for filename, _, _ in index.get(name, []):
                files[filename] = files.get(filename, 0) + 1
        where = ""
        if files:
            ranked = sorted(files, key=lambda f: (-files[f], f))
            where = "   → " + " · ".join(os.path.join(DOCS_REL, f) for f in ranked)
        print(f"\n{family.upper()}, {registry.FAMILIES[family]}{where}")
        for name, entry in blocks:
            print(f"  {name:<14} span {entry.get('span', 12):>2}   {entry['use_when']}")
            if entry.get("instead_of"):
                print(f"  {'':<14}            instead of: {entry['instead_of']}")
    print(f"\n{len(registry.REGISTRY)} block types. "
          f"Aliases: {', '.join(sorted(registry.ALIASES))}")
    print("\nOne block in full, payload example and all its keys: "
          "python3 scripts/ig.py catalog <type>")
    return 0


def _catalog_block(query):
    """One block in full: the registry facts, then its documentation verbatim.

    This exists because the list above answers "which block" and nothing
    answered "what keys does it take", which sent readers hunting through files
    whose names they had to guess.
    """
    name, entry = registry.resolve(query)
    if not entry:
        known = sorted(set(registry.REGISTRY) | set(registry.ALIASES))
        near = difflib.get_close_matches(str(query).lower(), known, n=4, cutoff=0.5)
        print(f"[catalog] unknown block type {query!r}")
        if near:
            print("          did you mean: " + ", ".join(near))
        print("          python3 scripts/ig.py catalog   lists all "
              f"{len(registry.REGISTRY)}")
        return 1

    asked = str(query).strip().lower().replace("-", "_")
    if asked != name:
        print(f"[catalog] {asked} is an alias for {name}")

    print(f"\n{name}   {entry['family']} family, default span "
          f"{entry.get('span', 12)}")
    print(f"  use when      {entry['use_when']}")
    if entry.get("instead_of"):
        print(f"  instead of    {entry['instead_of']}")
    aliases = sorted(a for a, target in registry.ALIASES.items() if target == name)
    if aliases:
        print(f"  aliases       {', '.join(aliases)}")
    if entry.get("text_exempt"):
        print("  text budget   exempt: citations and data, not argument")
    for key, role in sorted((entry.get("text_roles") or {}).items()):
        print(f"  text budget   {key} is charged as `{role}`")
    if not entry.get("graphic"):
        print("  graphic       no, it counts against the linter's graphic ratio")

    sections = _doc_index().get(name, [])
    if not sections:
        print(f"\n  No section in {DOCS_REL}/ yet. The registry above is the "
              "whole contract;\n  see fixtures/specs/ for a block used in anger.")
    else:
        filename, line, body = sections[0]
        print(f"  docs          {os.path.join(DOCS_REL, filename)}:{line}")
        print("\n" + "-" * 72 + "\n")
        print(body)
        for other_file, other_line, _ in sections[1:]:
            print(f"\nAlso documented in "
                  f"{os.path.join(DOCS_REL, other_file)}:{other_line}, from the "
                  "other family's point of view.")

    extra = _undocumented_keys(entry, sections[0][2] if sections else "")
    if extra:
        print(f"\n  Also accepted, absent from the prose above: "
              f"{', '.join(extra)}")

    print(f"\nKeys every block takes (span, title, note, frame, break, the "
          f"value formatters,\nthe colour keys): {DOCS_REL}/README.md")
    return 0


# Keys documented once in catalog/README.md rather than per block. Listing them
# again under every type would drown the handful that are actually specific.
SHARED_KEYS = {
    "type", "id", "span", "title", "subtitle", "note", "source", "frame",
    "break", "allow_break", "class", "skip", "options", "label", "height",
    "width", "currency", "unit", "decimals", "compact", "table", "value_label",
    "category_label", "emphasis", "ordinal", "ordinal_reverse", "palette",
    "alt_hue",
}


def _undocumented_keys(entry, doc):
    """Payload keys the renderer reads that its documentation never shows.

    Read off the function itself, because the alternative is what actually
    happened: an author wanting to rename a checklist's second column found no
    `dont_title` in the docs, grepped `scripts/`, and ended up reverse
    engineering the payload from `blocks_editorial.py`. A key the code accepts
    and the prose omits is a key someone will go looking for in the source.
    """
    import inspect
    try:
        body = inspect.getsource(entry["fn"])
    except (OSError, TypeError):
        return []
    found = set(re.findall(r'b\.get\(\s*"([a-z_]+)"', body))
    found |= set(re.findall(r'b\[\s*"([a-z_]+)"\s*\]', body))
    return sorted(key for key in found - SHARED_KEYS
                  if f"`{key}`" not in doc and f'"{key}"' not in doc)


def cmd_pictograms(args):
    """The optional shape library, listed or drawn.

    Listed rather than left to be guessed: a name that does not exist is a build
    error, and the only way to avoid guessing is to be able to see the set.
    """
    if not args.sheet:
        print(f"  {len(pictograms.PICTOGRAMS)} pictograms, on a shared 24-unit grid.")
        print("  Optional everywhere. A `unit` chart with no `glyph` still draws squares.\n")
        for category, members in pictograms.by_category():
            print(f"  {category:<9} {' '.join(members)}")
        print("\n  unit:      \"glyph\": \"home\"          100 little houses, 24 filled")
        print("  pictogram: \"glyph\": \"home\"          rows of houses, one per unit_value")
        print("  chips:     \"icon\": \"key\"            the shape instead of the tone mark")
        print("  figure:    <use href=\"#ig-pic-home\" x=\"0\" y=\"0\" width=\"40\" height=\"40\"")
        print("                  class=\"ig-fig-solid-accent\"/>")
        print("\n  references/drawing.md decides whether a drawn subject earns its place.")
        return 0

    # Proof sheet: every shape drawn at working size, so the set can be looked
    # at rather than read. The linter has never seen a silhouette.
    import build as build_mod
    import render_pdf

    blocks = [{
        "type": "hero",
        "kicker": f"theme: {args.theme or 'default'}",
        "title": "The pictogram library",
        "subtitle": "Every shape, at the size a unit chart draws it. None of them is "
                    "required, and a plain square is often the better mark.",
    }]
    # `raw`, not `figure`, and deliberately: eight figures would trip the
    # three-per-document cap, and every name under every shape would blow the
    # figure text budget several times over. Both limits are right for a
    # document making an argument, and this is a contact sheet.
    # A fixed grid, not one row scaled to the column: with `width="100%"` a row
    # of three shapes draws them four times the size of a row of twelve, and a
    # contact sheet whose cell size depends on how many things are in the
    # category cannot be used to compare them.
    per_row, cell, rows_h = 10, 64, 74
    for category, members in pictograms.by_category():
        blocks.append({"type": "heading", "text": category})
        lines = [members[i:i + per_row] for i in range(0, len(members), per_row)]
        marks = "".join(
            f'<use href="#{pictograms.ID_PREFIX}{name}" x="{col * cell + 12}" '
            f'y="{row * rows_h + 4}" width="40" height="40" class="ig-fig-solid"/>'
            f'<text class="ig-fig-mono" x="{col * cell + 32}" '
            f'y="{row * rows_h + 60}" text-anchor="middle">{name}</text>'
            for row, line in enumerate(lines) for col, name in enumerate(line))
        blocks.append({
            "type": "raw", "span": 12,
            "html": f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'viewBox="0 0 {per_row * cell} {len(lines) * rows_h}" role="img" '
                    f'aria-label="The {category} pictograms: {", ".join(members)}." '
                    f'style="width:100%;height:auto;display:block">{marks}</svg>',
        })

    spec = {"meta": {"title": "Pictogram library", "theme": args.theme or "default",
                     "page": "a3-land", "density": "report",
                     "footer_left": "Pictogram library",
                     "footer_right": args.theme or "default"},
            "blocks": blocks}
    html_path = os.path.splitext(args.sheet)[0] + ".html"
    build_mod.build(spec, html_path, args.theme)
    render_pdf.render(html_path, args.sheet)
    print(f"  {args.sheet}")
    return 0


def cmd_catalog(args):
    if not args.sheet:
        return _catalog_block(args.type) if args.type else _catalog_list()

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
    p.add_argument("--density", choices=("graphic", "lesson", "report"),
                   help="graphic (default): titles and indicators only. "
                        "lesson: the same, with room to teach from zero. "
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

    p = sub.add_parser("sketch", help="one block on its own, at its real column width")
    p.add_argument("spec", help="a spec, a single block, or a list of blocks")
    p.add_argument("--id", action="append", help="block id to draw (repeatable)")
    p.add_argument("--index", action="append", type=int,
                   help="block position to draw (repeatable)")
    p.add_argument("--span", type=int, help="override the span, to try another width")
    p.add_argument("--theme")
    p.add_argument("--page")
    p.add_argument("--out-dir")
    p.add_argument("--chrome")
    p.add_argument("--height", type=int, default=2400,
                   help="window height before trimming; raise it for a tall drawing")
    p.add_argument("--wait", type=int, default=1200)
    p.set_defaults(fn=cmd_sketch)

    p = sub.add_parser("blind", help="brief a reader who has never seen the source")
    p.add_argument("html", help="a built document, or a directory of PNGs")
    p.add_argument("--claim", help="the claim from step 2, printed for comparison")
    p.add_argument("--chrome")
    p.add_argument("--dpi", type=int, default=80)
    p.set_defaults(fn=cmd_blind)

    p = sub.add_parser("ladder", help="the explanation, checked, before anything is drawn")
    p.add_argument("spec", help="a spec, or a JSON list of rungs written at step 2.5")
    p.add_argument("--brief", action="store_true",
                   help="print the brief for a reader who has never met the subject")
    p.set_defaults(fn=cmd_ladder)

    p = sub.add_parser("check", help="lint a built document")
    p.add_argument("html")
    p.add_argument("--pdf")
    p.set_defaults(fn=lambda a: _run("check_document.py", a.html,
                                     *(["--pdf", a.pdf] if a.pdf else [])))

    p = sub.add_parser("measure", help="per-block height and words, before rendering")
    p.add_argument("spec")
    p.add_argument("--density")
    p.set_defaults(fn=cmd_measure)

    p = sub.add_parser("catalog", help="list every block type, or explain one")
    p.add_argument("type", nargs="?",
                   help="one block type or alias: print its payload example and keys")
    p.add_argument("--sheet", help="render a proof-sheet PDF here")
    p.add_argument("--theme")
    p.set_defaults(fn=cmd_catalog)

    p = sub.add_parser("pictograms", help="list the optional shape library, or draw it")
    p.add_argument("--sheet", help="render a contact-sheet PDF here")
    p.add_argument("--theme")
    p.set_defaults(fn=cmd_pictograms)

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
