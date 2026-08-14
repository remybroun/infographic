#!/usr/bin/env python3
"""Compile a document spec (JSON) into a single self-contained HTML file.

The spec is the contract, see references/spec-schema.md. Everything about the
page that a renderer needs to know arrives through `Ctx`, so a block never has
to guess how wide it is or which theme is active.

    python3 scripts/build.py spec.json -o out/doc.html --theme rentos
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib import blocks_figure as figure_mod  # noqa: E402
from lib import density as density_mod  # noqa: E402
from lib import derivation  # noqa: E402
from lib import leading_numbers  # noqa: E402
from lib import registry, svg  # noqa: E402
from lib.blocks_editorial import inline  # noqa: E402
from lib.theme import Ctx, Theme  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
TEMPLATES = os.path.join(SKILL_ROOT, "templates")

MM = 96.0 / 25.4  # CSS px per millimetre at the 96dpi print baseline

PAGES = {
    #             css size            width_mm  height_mm  margin_top/side/bottom (mm)
    "a4":        ("A4 portrait",        210, 297, (16, 16, 15)),
    "a4-land":   ("A4 landscape",       297, 210, (14, 16, 13)),
    "letter":    ("Letter portrait",    215.9, 279.4, (16, 16, 15)),
    "letter-land": ("Letter landscape", 279.4, 215.9, (14, 16, 13)),
    "a3":        ("A3 portrait",        297, 420, (20, 20, 18)),
    "a3-land":   ("A3 landscape",       420, 297, (18, 20, 16)),
    "slide":     ("338mm 190mm",        338, 190, (14, 16, 12)),
    "poster":    ("A2 portrait",        420, 594, (24, 24, 22)),
    # `scroll` is the non-paginated target: one continuous page, read on a
    # screen. Half of what makes a designed explainer breathe is not being cut
    # into sheets, a full-bleed section, real vertical air, a type scale that
    # is not rationed by a page box. Its `@page` values are only the print
    # fallback for someone who hits Cmd-P anyway.
    "scroll":    ("A4 portrait",        210, 297, (16, 16, 15)),
}

# Measure and margins for `scroll`, in CSS px. 1080 is a comfortable reading
# column on a laptop while leaving room for a bleed section to be visibly wider.
SCROLL_MEASURE = 1080.0
SCROLL_MARGINS = (72.0, 40.0, 96.0)

TYPE_SCALE = {
    #          body   hero  section  figure
    "a4":      (13.4, 40.0, 25.0, 58.0),
    "a4-land": (13.0, 36.0, 23.0, 54.0),
    "letter":  (13.4, 40.0, 25.0, 58.0),
    "letter-land": (13.0, 36.0, 23.0, 54.0),
    "a3":      (15.5, 56.0, 33.0, 82.0),
    "a3-land": (15.0, 52.0, 31.0, 78.0),
    "slide":   (14.5, 42.0, 27.0, 64.0),
    "poster":  (18.0, 78.0, 44.0, 112.0),
    # Screen reading takes more size than paper at the same apparent scale, and
    # there is no sheet to ration it against.
    "scroll":  (16.0, 66.0, 36.0, 84.0),
}

GUTTER = 20.0
ROW_GAP = 26.0
SCROLL_ROW_GAP = 40.0
FRAME_PAD = 18.0

# `meta.spacing` scales the three distances that separate one block from the
# next: the column gutter, the row gap, and the padding inside a framed block.
# It scales all three together on purpose. Cutting the gap alone barely reads as
# tighter, because two framed charts are held apart by pad + gap + pad, and at
# the default that is 62px of which the gap is only 26.
#
# `tight` is for a sheet whose subject IS the blocks: a specimen page, a
# dashboard, a reference card, where air between panels is dead space rather
# than rhythm. It is not the default, because in a document that argues, the gap
# is what tells a reader one idea has finished and the next has begun.
SPACING = {"tight": 0.62, "normal": 1.0, "airy": 1.35}

# How many drawings one document may author. See blocks_figure.py for why this
# exists at all: without it, "draw the shape the catalog lacks" becomes
# "hand-draw everything", and every output stops resembling its siblings.
FIGURE_CAP = 3


class Document:
    def __init__(self, spec: dict, theme_name: str = None, page: str = None,
                 tables: bool = None, texture: bool = None, density: str = None):
        self.spec = spec
        meta = spec.get("meta", {})
        self.meta = meta

        # The text budget runs first, before geometry or theme resolution. A
        # spec that is really an essay should fail on the essay, not on some
        # downstream detail that happens to be checked earlier.
        self.density = density_mod.resolve(meta.get("density"), density)
        density_mod.enforce(spec, self.density, registry)
        self.check_figures(spec)

        self.page_key = (page or meta.get("page") or "a4").lower()
        if self.page_key not in PAGES:
            raise SystemExit(f"[build] unknown page {self.page_key!r}. "
                             f"Known: {', '.join(sorted(PAGES))}")
        self.paginated = self.page_key != "scroll"
        self.theme = Theme.load(theme_name or meta.get("theme") or "default")
        self.show_tables = meta.get("tables", True) if tables is None else tables
        self.texture = bool(meta.get("texture", False)) if texture is None else texture
        self.warnings = []

        missing = self.theme.missing_font_files()
        if missing:
            self.warnings.append(
                f"theme {self.theme.name!r} declares {len(missing)} font file(s) that "
                f"are not at {self.theme.fonts_dir()!r}: {', '.join(missing[:4])}"
                f"{'...' if len(missing) > 4 else ''}. Chrome will fall back silently, "
                f"so the document renders in a substitute face.")

        self.spacing = str(meta.get("spacing", "normal")).lower()
        if self.spacing not in SPACING:
            raise SystemExit(f"[build] meta.spacing must be one of "
                             f"{', '.join(sorted(SPACING))} (got {self.spacing!r})")
        scale = SPACING[self.spacing]
        self.gutter = GUTTER * scale
        self.frame_pad = FRAME_PAD * scale

        css_size, w_mm, h_mm, margins = PAGES[self.page_key]
        self.css_page_size = css_size if not css_size[0].isdigit() else css_size
        self.margin_top, self.margin_side, self.margin_bottom = margins
        if self.paginated:
            self.unit = "mm"
            self.content_px = (w_mm - self.margin_side * 2) * MM
            self.doc_width_css = f"{self.content_px + self.margin_side * 2 * MM:.1f}px"
            self.row_gap = ROW_GAP * scale
        else:
            self.unit = "px"
            self.margin_top, self.margin_side, self.margin_bottom = SCROLL_MARGINS
            self.content_px = SCROLL_MEASURE
            self.doc_width_css = f"{SCROLL_MEASURE + self.margin_side * 2:.0f}px"
            self.row_gap = SCROLL_ROW_GAP * scale
        self.column_px = (self.content_px - self.gutter * 11) / 12.0
        self.body_size, self.hero_size, self.section_size, self.figure_size = \
            TYPE_SCALE.get(self.page_key, TYPE_SCALE["a4"])

        for index, block in enumerate(spec.get("blocks", [])):
            if isinstance(block, dict) and block.get("bleed") and self.paginated:
                self.warnings.append(
                    f"blocks[{index}] ({block.get('type')}) sets `bleed`, which only "
                    f"means something on `page: scroll`. Inside a page box there is no "
                    f"viewport to break out of, so it is ignored.")

        self.paper = str(meta.get("paper", "panel")).lower()
        if self.paper not in ("panel", "none", "bleed"):
            raise SystemExit(f"[build] meta.paper must be panel, none or bleed "
                             f"(got {self.paper!r})")
        if self.paper == "bleed" and len(spec.get("blocks", [])) > 24:
            self.warnings.append(
                "meta.paper 'bleed' simulates margins with padding, which only "
                "applies on the first page. This document looks multi-page; use "
                "'panel' unless it really is a single sheet.")

    # -- authored figures --------------------------------------------------

    def check_figures(self, spec: dict) -> None:
        """Validate every authored drawing, and cap how many there may be.

        The cap runs with the text budget, before geometry, because both answer
        the same question: is this document still the thing this skill makes?
        The budget stops it becoming an essay. The cap stops it becoming a
        bespoke one-off that happens to have been built here.
        """
        figures = []
        for index, block in enumerate(spec.get("blocks", [])):
            if not isinstance(block, dict) or block.get("skip"):
                continue
            key, _ = registry.resolve(block.get("type"))
            if key == "figure":
                figures.append((index, block))

        for index, block in figures:
            label = f'blocks[{index}]' + (f' (#{block["id"]})' if block.get("id") else "")
            figure_mod.validate(block, label)

        if len(figures) > FIGURE_CAP:
            listed = "\n".join(
                f'    blocks[{i}]  {(b.get("title") or b.get("alt") or "")[:64]}'
                for i, b in figures)
            raise SystemExit(
                f"[figure] {len(figures)} authored figures; the cap is {FIGURE_CAP}.\n\n"
                f"{listed}\n\n"
                f"  The cap is not a budget, it is a ranking exercise. Which two or three\n"
                f"  images does this document live or die by? Those get drawn by hand.\n"
                f"  Everything else is supporting material, and supporting material is\n"
                f"  better on rails: it stays consistent, it re-themes, it gets a table\n"
                f"  twin for free, and it does not need reviewing pixel by pixel.\n\n"
                f"  Demote the weakest ones. A layered thing is a `stack`, a sequence that\n"
                f"  changes hands is a `swimlane`, options against criteria is a\n"
                f"  `scorecard`, a set of states is `chips`. If all {len(figures)} really are\n"
                f"  load-bearing, the honest answer is that this is two documents.")

    # -- geometry ----------------------------------------------------------

    def span_width(self, span: int) -> float:
        span = max(1, min(12, int(span)))
        return self.column_px * span + self.gutter * (span - 1)

    # -- rendering ---------------------------------------------------------

    def render_block(self, block: dict) -> str:
        if block.get("skip"):
            return ""
        span = int(block.get("span", registry.default_span(block)))
        span = max(1, min(12, span))
        width = self.span_width(span)
        options = dict(self.spec.get("options", {}))
        block_options = block.get("options", {})
        if not isinstance(block_options, dict):
            raise SystemExit(
                f"[build] block {block.get('type')!r} has a non-dict `options`. "
                f"`options` is reserved for per-block render settings; a payload "
                f"list belongs under its own key (scorecard uses `choices`).")
        options.update(block_options)
        ctx = Ctx(self.theme, width, options, self.texture, self.spec, self.density)
        payload = dict(block)
        if not self.show_tables:
            payload.setdefault("table", False)

        body = registry.render_block(payload, ctx)
        for warning in ctx.warnings:
            self.warnings.append(f"{block.get('type')}#{block.get('id', '?')}: {warning}")

        classes = ["ig-block", f"ig-span-{span}"]
        frame = block.get("frame")
        if frame == "card":
            classes.append("ig-block-framed")
        elif frame == "tint":
            classes.append("ig-block-tinted")
        if block.get("break") in ("before", "page"):
            classes.append("ig-break-before")
        if block.get("break") == "after":
            classes.append("ig-break-after")
        if block.get("allow_break"):
            classes.append("ig-allow-break")
        if block.get("bleed") and not self.paginated:
            classes.append("ig-bleed")
            if block.get("invert"):
                classes.append("ig-bleed-dark")
        if block.get("class"):
            classes.append(str(block["class"]))

        head = ""
        if block.get("title") and not registry.owns(block, "title"):
            head += f'<p class="ig-block-title">{inline(block["title"])}</p>'
        if block.get("subtitle") and not registry.owns(block, "subtitle"):
            head += f'<p class="ig-block-sub">{inline(block["subtitle"])}</p>'
        note = (f'<p class="ig-block-note">{inline(block["note"])}</p>'
                if block.get("note") and not registry.owns(block, "note") else "")
        source = (f'<p class="ig-block-note">Source: {inline(block["source"])}</p>'
                  if block.get("source") else "")

        block_id = f' id="{svg.esc(block["id"])}"' if block.get("id") else ""
        tag = "figure" if head or note or source else "div"
        return (f'<{tag} class="{" ".join(classes)}"{block_id}>'
                f"{head}{body}{note}{source}</{tag}>")

    def page_rule(self) -> str:
        """`@page` with literal values, it cannot be class-scoped, and custom
        properties are unreliable inside it.

        A scroll document still emits one. It is not paginated, but somebody will
        print it anyway, and an A4 box with sane margins is a far better fallback
        than Chrome's default letter-with-headers.
        """
        size_value = PAGES[self.page_key][0]
        if not self.paginated:
            return f"@page{{size:{size_value};margin:14mm 12mm}}"
        if self.paper == "bleed":
            margin = "0"
        else:
            margin = f"{self.margin_top}mm {self.margin_side}mm {self.margin_bottom}mm"
        return f"@page{{size:{size_value};margin:{margin}}}"

    def tokens_css(self) -> str:
        t = self.theme
        size_value = PAGES[self.page_key][0]
        return self.page_rule() + ":root{" + ";".join([
            f"--ig-page:{t.surface('page')}",
            f"--ig-card:{t.surface('card')}",
            f"--ig-sunken:{t.surface('sunken')}",
            f"--ig-ink:{t.ink('primary')}",
            f"--ig-secondary:{t.ink('secondary')}",
            f"--ig-muted:{t.ink('muted')}",
            f"--ig-border:{t.rule('border')}",
            f"--ig-hairline:{t.rule('hairline')}",
            f"--ig-axis:{t.rule('axis')}",
            f"--ig-accent:{t.accent}",
            # A separate role on purpose: the accent as SMALL TEXT must clear
            # 4.5:1, while the accent as a FILL only needs 3:1.
            f"--ig-accent-text:{t.ink('accent_text') if 'accent_text' in t.data['ink'] else t.accent}",
            f"--ig-accent-wash:{t.wash(t.accent, 0.10, on=t.surface('page'))}",
            f"--ig-good:{t.status('good_text')}",
            f"--ig-good-wash:{t.wash(t.status('good'), 0.10, on=t.surface('page'))}",
            f"--ig-warn:{t.status('warning')}",
            f"--ig-warn-wash:{t.wash(t.status('warning'), 0.14, on=t.surface('page'))}",
            f"--ig-danger:{t.status('critical')}",
            f"--ig-danger-text:{t.status('critical_text')}",
            f"--ig-danger-wash:{t.wash(t.status('critical'), 0.10, on=t.surface('page'))}",
            f"--ig-sans:{t.font('sans')}",
            f"--ig-display:{t.font('display')}",
            f"--ig-mono:{t.font('mono')}",
            f"--ig-display-weight:{t.display_weight}",
            # A block title is the one heading small enough that the choice of
            # face is a real decision rather than a foregone one. A theme whose
            # display face IS its sans (default, mono) gains nothing by using it
            # here, so this is opt-in per theme: `type.block_title: "display"`.
            # A 400-weight serif needs more size than a 600-weight sans to hold
            # the same presence, hence the separate scale rather than one size.
            f"--ig-title-font:{t.font('display' if t.title_face == 'display' else 'sans')}",
            f"--ig-title-weight:{t.display_weight if t.title_face == 'display' else 600}",
            # 1.2, not 1.3. A 400-weight serif does need more size than a
            # 600-weight sans to hold the same presence, but at 1.3 the extra
            # leading pushed the architecture fixture's last note into the
            # running footer. A theme is allowed to reflow a document; it is not
            # allowed to print one line on top of another.
            f"--ig-title-scale:{1.2 if t.title_face == 'display' else 1.12}",
            f"--ig-display-tracking:{t.data['type'].get('display_tracking', '-0.02em')}",
            f"--ig-radius:{t.geom('radius', 4)}px",
            f"--ig-body-size:{self.body_size}px",
            f"--ig-hero-size:{self.hero_size}px",
            f"--ig-section-size:{self.section_size}px",
            f"--ig-figure-size:{self.figure_size}px",
            f"--ig-page-size:{size_value}",
            f"--ig-margin-top:{self.margin_top}{self.unit}",
            f"--ig-margin-side:{self.margin_side}{self.unit}",
            f"--ig-margin-bottom:{self.margin_bottom}{self.unit}",
            f"--ig-content-width:{self.doc_width_css}",
            f"--ig-gutter:{self.gutter:.1f}px",
            f"--ig-row-gap:{self.row_gap:.1f}px",
            f"--ig-frame-pad:{self.frame_pad:.1f}px",
        ] + [
            # The categorical slots, published so an authored `figure` can paint
            # from the same validated palette every chart uses. Without these a
            # hand-drawn figure has no themed way to say "series 3" and reaches
            # for a hex literal, which the figure validator then refuses with no
            # alternative to offer.
            f"--ig-series-{i}:{t.series(i)}" for i in range(t.series_count())
        ] + [
            f"--ig-ordinal-{i}:{step}" for i, step in enumerate(t.ordinal_steps())
        ]) + "}"

    def footer_html(self) -> str:
        left = self.meta.get("footer_left", self.meta.get("title", ""))
        right = self.meta.get("footer_right", self.meta.get("date", ""))
        if not left and not right:
            return ""
        return (f'<div class="ig-running-footer"><span>{inline(left)}</span>'
                f"<span>{inline(right)}</span></div>")

    def render(self) -> str:
        with open(os.path.join(TEMPLATES, "document.html"), encoding="utf-8") as fh:
            template = fh.read()
        with open(os.path.join(TEMPLATES, "document.css"), encoding="utf-8") as fh:
            css = fh.read()

        blocks = "\n".join(filter(None, (self.render_block(b) for b in self.spec.get("blocks", []))))
        footer = self.footer_html()
        classes = [f"ig-paper-{self.paper}", f"ig-density-{self.density}",
                   f"ig-page-{self.page_key}",
                   "ig-paginated" if self.paginated else "ig-continuous"]
        if not self.show_tables:
            classes.append("ig-tables-hidden")
        if footer:
            classes.append("ig-has-footer")
        body_class = " ".join(classes)

        html = template
        for token, value in (
            ("{{LANG}}", self.meta.get("lang", "en")),
            ("{{TITLE}}", svg.esc(self.meta.get("title", "Infographic"))),
            ("{{FONTS}}", self.theme.fonts_css()),
            ("{{TOKENS}}", self.tokens_css()),
            ("{{CSS}}", css),
            ("{{BODY_CLASS}}", body_class),
            ("{{BLOCKS}}", blocks),
            ("{{FOOTER}}", footer),
        ):
            html = html.replace(token, value)
        return html


def load_spec(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build(spec, out_path: str = None, theme: str = None, page: str = None,
          tables: bool = None, texture: bool = None, density: str = None):
    spec_path = spec if isinstance(spec, str) else None
    if isinstance(spec, str):
        spec = load_spec(spec)
    doc = Document(spec, theme, page, tables, texture, density)
    html = doc.render()
    # A regeneration that declares what it replaces gets measured against it.
    # Nothing else in the toolchain can see this: the linter reads one finished
    # document and cannot ask whether a different one would have been better.
    doc.warnings.extend(derivation.check(spec, registry, spec_path))
    doc.warnings.extend(leading_numbers.check(spec, registry))
    doc.warnings.extend(leading_numbers.inverted_without_ground(spec))
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html)
    return html, doc.warnings


def main():
    parser = argparse.ArgumentParser(description="Compile an infographic spec into HTML.")
    parser.add_argument("spec", help="path to spec JSON, or - for stdin")
    parser.add_argument("-o", "--out", help="output HTML path")
    parser.add_argument("--theme", help="override meta.theme")
    parser.add_argument("--page", help="override meta.page")
    parser.add_argument("--no-tables", action="store_true",
                        help="drop the table-view twins (accessibility regression; "
                             "only for a deck destined for a screen)")
    parser.add_argument("--texture", action="store_true",
                        help="turn on the texture channel for CVD / mono print")
    parser.add_argument("--density", choices=density_mod.DENSITIES,
                        help="graphic (default): titles and indicators, the picture "
                             "carries the idea. report: allow body prose")
    args = parser.parse_args()

    html, warnings = build(args.spec, args.out, args.theme, args.page,
                           tables=False if args.no_tables else None,
                           texture=True if args.texture else None,
                           density=args.density)
    if not args.out:
        sys.stdout.write(html)
    else:
        print(f"[build] wrote {args.out} ({len(html):,} bytes)")
    for warning in warnings:
        print(f"[warn] {warning}", file=sys.stderr)


if __name__ == "__main__":
    main()
