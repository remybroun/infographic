#!/usr/bin/env python3
"""Lint a built document for the failures that survive a green palette check.

The palette validator checks colour. This checks *documents*: composition,
accessibility twins, page economy and the anti-patterns that only show up once
everything is assembled. It reads the built HTML (and the PDF when given one),
so it catches problems the spec alone cannot reveal.

    python3 scripts/check_document.py out/doc.html --pdf out/doc.pdf

It is a linter, not a judge. `error` means something is broken or inaccessible.
`warn` means look at it. Neither replaces opening the PDF and reading it.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.density import WORDS_PER_BLOCK, WORDS_PER_PAGE  # noqa: E402


def _count(pattern, text, flags=0):
    return len(re.findall(pattern, text, flags))


def split_document(html: str):
    """Separate the stylesheet from the rendered body.

    Almost every false positive this linter produced came from matching its own
    CSS, a comment mentioning `tabular-nums`, a legitimate `overflow: hidden` on
    a rounded ramp. Checks about *content* must only ever see the body.
    """
    body_start = html.rfind("</style>")
    body = html[body_start + len("</style>"):] if body_start >= 0 else html
    css = html[:body_start] if body_start >= 0 else ""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    # The drawing kit's shared arrowhead defs are document chrome, not content.
    # Left in, they count as a graphic, which would let a document with no
    # drawings at all pass the `no-graphics` check on the strength of a marker.
    body = re.sub(r'<svg\b[^>]*class="ig-defs".*?</svg>', " ", body, flags=re.S | re.I)
    return css, body


def document_classes(html: str) -> set:
    """The classes build.py stamped on `<body>`: density, page target, paper.

    Read from the tag rather than by searching the document, because every one
    of these names is ALSO a CSS selector in the stylesheet. `"ig-continuous" in
    html` is true for every document ever built, paginated or not, which is
    exactly the false positive `split_document` exists to prevent, made once
    again a few lines further down.
    """
    match = re.search(r"<body[^>]*\bclass=\"([^\"]*)\"", html, re.I)
    return set(match.group(1).split()) if match else set()


def _visible_words(body: str) -> int:
    """Words a reader actually reads.

    Table-view twins and SVG mark labels are excluded deliberately. The twins are
    an accessibility duplicate of data that is already on the page, and axis tick
    labels are part of the graphic. Counting either would let a document pass the
    budget by deleting its accessibility layer, which is the opposite of the
    intended pressure.

    A real `table` block is NOT excluded, and the distinction is load-bearing.
    The twins live inside `<details>`, which the first substitution already
    removes, so a blanket `<table>` strip only ever exempted authored tables.
    That exemption was a hole the size of the whole budget: an author who cannot
    fit a paragraph can retype it as three columns and the count drops to zero.
    Table cells are exempt from the per-FIELD caps in density.py, because a cell
    is data; they are not exempt from the document's word count, because a page
    of sentences is a page of sentences whatever it is ruled into.
    """
    text = re.sub(r"<details\b.*?</details>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<svg\b.*?</svg>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;|&#\d+;", " ", text, flags=re.I)
    return len([w for w in re.split(r"\s+", text) if w.strip(".,;:·—-")])


def page_ink(pdf_path: str):
    """Fraction of each page that is not background, page by page.

    Block-per-page arithmetic cannot see a half-empty page: a document with a
    good average happily hides one sheet carrying a single callout, which is
    what `break: before` in front of a tall row produces. So measure it.

    Rasterises at 12dpi to PGM, which is a five-line header and raw bytes, so no
    image library is needed. Returns None when poppler is not installed rather
    than pretending the page is fine.
    """
    if not shutil.which("pdftoppm"):
        return None
    out = tempfile.mkdtemp(prefix="ig-ink-")
    try:
        subprocess.run(["pdftoppm", "-gray", "-r", "12", pdf_path,
                        os.path.join(out, "p")],
                       capture_output=True, timeout=90)
        coverage = []
        for name in sorted(os.listdir(out)):
            with open(os.path.join(out, name), "rb") as fh:
                blob = fh.read()
            if not blob.startswith(b"P5"):
                return None
            # P5 header: magic, width, height, maxval, whitespace separated,
            # with '#' comments legal between any two tokens.
            pos, fields = 2, []
            while len(fields) < 3:
                while pos < len(blob) and blob[pos:pos + 1].isspace():
                    pos += 1
                if blob[pos:pos + 1] == b"#":
                    while pos < len(blob) and blob[pos:pos + 1] != b"\n":
                        pos += 1
                    continue
                start = pos
                while pos < len(blob) and not blob[pos:pos + 1].isspace():
                    pos += 1
                fields.append(int(blob[start:pos]))
            pixels = blob[pos + 1:]
            if not pixels:
                return None
            background = max(set(pixels), key=pixels.count) if len(pixels) < 4096 \
                else max(pixels[::7].__iter__(), key=pixels[::7].count)
            inked = sum(1 for p in pixels if abs(p - background) > 12)
            coverage.append(inked / len(pixels))
        return coverage
    except Exception:
        return None
    finally:
        shutil.rmtree(out, ignore_errors=True)


def check(html_path: str, pdf_path: str = None):
    with open(html_path, encoding="utf-8") as fh:
        html = fh.read()
    css, body = split_document(html)
    classes = document_classes(html)
    findings = []

    def add(level, code, message, fix=""):
        findings.append({"level": level, "code": code, "message": message, "fix": fix})

    # -- structural -------------------------------------------------------
    if "{{" in html:
        add("error", "unsubstituted-token",
            "the template still contains {{TOKEN}} placeholders",
            "a build step did not run; rebuild from the spec")
    if "<title></title>" in html or "<title>Infographic</title>" in html:
        add("warn", "default-title", "the document title is still the default",
            "set meta.title to the claim the document makes")

    blocks = _count(r'class="ig-block[ "]', body)
    if blocks == 0:
        add("error", "empty", "no blocks rendered", "check spec.blocks")
    elif blocks < 3:
        add("warn", "thin", f"only {blocks} blocks, this is a fragment, not a document")

    # -- the argument -----------------------------------------------------
    # These checks used to run the other way round: they warned when prose was
    # ABSENT, which is how this skill talked itself into shipping an eight-page
    # A4 document carrying 2,086 words and one bar chart. The measurement that
    # matters is the inverse, so it is now the inverse.
    graphic_density = "ig-density-graphic" in classes
    charts = _count(r"<svg ", body)
    # `ig-table` is in this list and `ig-table-view` is not: the trailing [ "]
    # keeps the twins out. An authored table is a text block for the purposes of
    # "is this a graphic document", because it is the shape prose takes when an
    # author needs it to stop being counted. Three of them is a chapter.
    text_blocks = sum(_count(rf'class="{cls}[ "]', body) for cls in
                      ("ig-prose", "ig-bullets", "ig-quote", "ig-table"))
    words = _visible_words(body)

    if graphic_density:
        if charts == 0:
            add("error", "no-graphics",
                "a graphic-density document with no graphics at all",
                "this is a text document; draw the ideas or pass --density report")
        ratio = charts / (charts + text_blocks) if (charts + text_blocks) else 1.0
        if charts and ratio < 0.6:
            add("warn", "text-heavy-mix",
                f"{charts} graphics against {text_blocks} prose blocks "
                f"({ratio * 100:.0f}% graphic)",
                "replace the prose blocks with stack, chips, scorecard or process")
        if text_blocks and charts == 0:
            add("error", "prose-only", f"{text_blocks} prose blocks and no graphic")

        # A document-wide ratio hides a section that is entirely text: three
        # figures at the top carry the average while the last section is a
        # wall. The reader does not experience an average, they read a section
        # at a time, so check the run between one section head and the next.
        #
        # Deliberately narrow. A section built from `definitions`, `comparison`
        # or `checklist` draws no SVG and is still doing its job: those forms
        # have structure, and the vocabulary section of a good explainer looks
        # exactly like that. What this catches is a section carried by the two
        # forms with no shape at all, `table` and `prose`, which is what an
        # author reaches for when the budget says no.
        shapeless = re.compile(r'class="(?:ig-table|ig-prose|ig-bullets)[ "]')
        runs = re.split(r'(?=<[^>]+class="ig-section-head")', body)[1:]
        barren = [i + 1 for i, run in enumerate(runs)
                  if "<svg " not in run and shapeless.search(run)]
        if barren:
            add("warn", "undrawn-section",
                f"section(s) {', '.join(map(str, barren))} are carried by tables "
                f"or prose with no graphic at all",
                "ask what shape the rows are: options against criteria are a "
                "`matrix`, a sequence is a `process`, counts are a `bar`")
    else:
        if charts and text_blocks == 0:
            add("note", "no-prose",
                f"{charts} visuals and no explanatory prose",
                "at report density a chart usually wants a sentence; at graphic "
                "density this is correct and expected")

    heroes = _count(r'class="ig-hero-figure"', body)
    if heroes > 1:
        add("warn", "two-heroes", f"{heroes} hero figures; there should be exactly one per view",
            "demote the rest to stat tiles")

    # -- accessibility ----------------------------------------------------
    if charts and "ig-table-view" not in body:
        add("error", "no-table-view",
            "charts are present but no table view exists",
            "every chart needs its WCAG-clean twin; do not pass --no-tables")

    # Count legend containers only, `class="ig-legend` also prefix-matches
    # `ig-legend-item`, which made every document look like it had thin legends.
    legends = _count(r'class="ig-legend(?:-compact)?"', body)
    items = _count(r'class="ig-legend-item"', body)
    if legends and items < legends * 2:
        add("warn", "thin-legend",
            f"{legends} legend(s) carrying {items} entries, at least one has fewer than two",
            "a single-swatch legend restates the title; remove it")

    for match in re.finditer(r"<img [^>]*>", body):
        if 'alt="' not in match.group(0):
            add("error", "img-no-alt", "an <img> has no alt attribute",
                "describe what the image shows, or alt=\"\" if purely decorative")
            break

    # -- anti-patterns ----------------------------------------------------
    if "stroke-dasharray" in body:
        add("warn", "dashed-rule",
            "a dashed stroke is present",
            "gridlines and axes are solid hairlines; dashing reads as 'threshold'")
    # Only inline styles in the body can crop a mark. The stylesheet's own
    # overflow:hidden (on the rounded scale ramp) is legitimate clipping.
    if re.search(r'style="[^"]*overflow\s*:\s*hidden', body):
        add("warn", "overflow-hidden",
            "an inline overflow:hidden appears, it crops labels rather than fixing them",
            "move the label outside the mark or drop it to the table view")
    if re.search(r"-webkit-background-clip:\s*text", css + body):
        add("warn", "gradient-text", "gradient text detected",
            "emphasis comes from weight or size")

    for rule in re.finditer(r"\.ig-(?:hero-figure-value|stat-value)\s*\{([^}]*)\}", css):
        if "tabular-nums" in rule.group(1):
            add("warn", "tabular-hero",
                "tabular-nums on a large standalone number makes it look loose",
                "reserve tabular figures for columns that align vertically")
            break

    # -- economy, on a continuous page ------------------------------------
    # A scroll document has no pages, so every paper check below is not just
    # inapplicable but actively wrong: `sparse-pages` and `near-empty-page` would
    # fire on a document that is behaving exactly as intended. The budget still
    # applies, charged per block instead of per page.
    if "ig-continuous" in classes:
        budget = WORDS_PER_BLOCK["graphic" if graphic_density else "report"]
        per_block = words / blocks if blocks else 0
        if per_block > budget:
            add("error" if graphic_density else "warn", "text-heavy",
                f"{words:,} words across {blocks} blocks "
                f"({per_block:.0f} per block, budget {budget})",
                "the budget is per block here because there are no pages to divide "
                "by; title + subtitle + note is all one block may carry")
        elif per_block > budget * 0.85:
            add("note", "text-near-budget",
                f"{per_block:.0f} words per block against a budget of {budget}")
        if "ig-bleed" not in body:
            add("note", "no-bleed",
                "a continuous document with no full-bleed section",
                "the reason to leave the page box is to be able to do this; if "
                "nothing in the document earns a bleed, `page: a4` is the honest "
                "target and prints properly")
        return findings

    # -- print economy ----------------------------------------------------
    if pdf_path and os.path.isfile(pdf_path):
        import render_pdf
        pages = render_pdf.page_count(pdf_path)
        size = os.path.getsize(pdf_path)
        if pages:
            # The budget that would have caught the document this check was
            # written for: 2,086 words across 8 A4 pages is 261 per page, twice
            # the graphic-density ceiling.
            budget = WORDS_PER_PAGE["graphic" if graphic_density else "report"]
            per_page_words = words / pages
            if per_page_words > budget:
                add("error" if graphic_density else "warn", "text-heavy",
                    f"{words:,} words across {pages} pages "
                    f"({per_page_words:.0f} per page, budget {budget})",
                    "cut to titles and indicators, and move what is left into a "
                    "stack, scorecard, swimlane or chip grid")
            elif per_page_words > budget * 0.85:
                add("note", "text-near-budget",
                    f"{per_page_words:.0f} words per page against a budget of {budget}",
                    "inside the budget, but there is no headroom left for another "
                    "block of text")

            ink = page_ink(pdf_path)
            if ink and len(ink) > 1:
                # Measured across this skill's own output: a full A4 page runs
                # 11-19% covered and a stranded-block page runs 6-8%. The
                # relative test against the median catches the stranded page in
                # an otherwise healthy document; the absolute floor catches a
                # document where every page is bare and the median is no help.
                ordered = sorted(ink)
                median = ordered[len(ordered) // 2]
                for number, share in enumerate(ink, start=1):
                    if share < 0.05 or (share < 0.10 and share < median * 0.62):
                        add("warn", "near-empty-page",
                            f"page {number} is {share * 100:.0f}% covered "
                            f"(median page {median * 100:.0f}%)",
                            "a `break: before` in front of a tall row strands "
                            "whatever precedes it; move the break, shorten the "
                            "row, or split the 12-span into two 6-spans")

            per_page = blocks / pages if pages else 0
            if per_page < 2 and pages > 1:
                add("warn", "sparse-pages",
                    f"{blocks} blocks across {pages} pages ({per_page:.1f} per page)",
                    "a tall grid row moves to the next page whole; reduce block heights, "
                    "split a 12-span into two, or drop an unnecessary break:before")
            if pages > 12:
                add("warn", "long", f"{pages} pages, this is a report, not an infographic",
                    "if that is intended, fine; if not, cut to the argument")
        if size > 6_000_000:
            add("warn", "heavy", f"{size / 1e6:.1f} MB",
                "large embedded rasters; downscale before embedding")
    elif pdf_path:
        add("error", "no-pdf", f"PDF not found: {pdf_path}")

    return findings


LEVEL_ORDER = {"error": 0, "warn": 1, "note": 2}


def report(findings):
    if not findings:
        print("[check] clean, no findings. Now open the PDF and read it: "
              "the linter checks structure, not whether the argument lands.")
        return 0
    for f in sorted(findings, key=lambda f: LEVEL_ORDER.get(f["level"], 9)):
        print(f"[{f['level']:<5}] {f['code']}: {f['message']}")
        if f["fix"]:
            print(f"          → {f['fix']}")
    tally = {level: sum(1 for f in findings if f["level"] == level)
             for level in ("error", "warn", "note")}
    print(f"[check] {tally['error']} error(s), {tally['warn']} warning(s), "
          f"{tally['note']} note(s)")
    return tally["error"]


def main():
    parser = argparse.ArgumentParser(description="Lint a built infographic document.")
    parser.add_argument("html")
    parser.add_argument("--pdf")
    args = parser.parse_args()
    pdf = args.pdf
    if pdf is None:
        guess = os.path.splitext(args.html)[0] + ".pdf"
        pdf = guess if os.path.isfile(guess) else None
    findings = check(args.html, pdf)
    sys.exit(1 if report(findings) else 0)


if __name__ == "__main__":
    main()
