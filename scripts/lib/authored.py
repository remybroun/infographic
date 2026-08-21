"""Authored composition: the model writes the page, the skill keeps the promises.

Every other path in this skill turns a payload into a picture the skill already
knows how to draw. The model's whole creative surface is choosing a `type` and
filling a dict, and the page it lands on is a 12-column grid of stacked
full-width rows that no document may vary. That buys real things, consistency
across siblings, free table twins, computed contrast, re-theming, and it is the
right trade for a data poster.

It is the wrong trade for an explainer that lives on its pictures, and the
failure is structural rather than a matter of taste. `figure` was the escape
hatch, and it is one drawing inside one grid cell, capped at three, with no CSS
of its own. `raw` was the other, and the catalog says out loud that it "counts
against the linter's graphic ratio", so the one unrestricted door is scored as
prose and penalised for existing. Between them there is no way to compose a
page: no layered or overlapping arrangement, no per-scene layout, no full-bleed
art on paper, no drawing that spans two ideas. Faced with that, an agent does
not treat the catalog as inspiration. It treats it as an instruction set, and
emits valid input.

So this module inverts the relationship. The spec carries `body` (the document's
markup, including as much inline SVG as it wants) and `style` (its CSS). The
skill stops being the compiler and becomes four things it is genuinely better at
than the model:

* **the palette**, enforced. Every colour in the CSS and in the markup must be a
  theme token, so an authored page re-skins with `--theme` exactly like a chart
  does and cannot drift into last month's brand.
* **the accessibility floor**, enforced. Every drawing carries an accessible
  name, every image carries `alt`, and `meta.encodes` makes the same honest
  declaration `figure` does: either there is no data in here, or here are the
  numbers as a table.
* **inertness**, enforced. The deliverable is a PDF or a screenshot. Anything
  that needs a script to appear is blank on paper, and anything fetched over the
  network is a race the renderer usually loses.
* **the tooling**, unchanged. Build, render, screenshot, lint, the word budget,
  the ladder, the blind-reader brief. None of it cared how the markup was
  produced.

The catalog does not go away and is not demoted to a fallback. A comparison of
values really is a `bar`, and hand-drawing one is strictly worse: no axis maths,
no label fitting, no table twin, no ordinal ramp. So an authored body can drop
any catalog block into any position it likes:

    <div data-block="cost-by-year" data-width="480"></div>

which renders that block from `spec.blocks` at that width, inside whatever
layout the page has invented around it.
"""

from __future__ import annotations

import re

from .blocks_figure import has_literal, paint_literals

# ---------------------------------------------------------------- colour ----

_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_QUOTED = re.compile(r"""(['"])(?:\\.|(?!\1).)*\1""", re.S)
_URL = re.compile(r"url\(\s*[^)]*\)", re.I)
_RULE_BODY = re.compile(r"\{([^{}]*)\}")


def _scrub(value: str) -> str:
    """A declaration value with the parts that cannot carry a colour removed.

    `url(#ig-arrow)` matters: `#ig-arrow` is not a hex colour but `url(#face)`
    would be read as one, and a marker reference is the single most common `#`
    in this skill's own markup.
    """
    return _URL.sub(" ", _QUOTED.sub(" ", value))


def css_literals(css: str):
    """Every colour literal in a stylesheet, as `[(property, value), …]`.

    Declaration-level rather than a scan of the raw text, because a selector is
    allowed to be called `.gold-rule` and a font may be called `Salmon`. Only
    what sits to the right of a colon is a value.
    """
    css = _COMMENT.sub(" ", css or "")
    found, seen = [], set()
    for rule_body in _RULE_BODY.findall(css):
        for declaration in rule_body.split(";"):
            prop, colon, value = declaration.partition(":")
            if not colon:
                continue
            prop, value = prop.strip(), _scrub(value)
            if not prop or prop.startswith("@"):
                continue
            # Shorthands (`border`, `background`, `box-shadow`) carry a colour
            # among lengths and keywords, so the test is on the value as a whole
            # rather than on a whitelist of paint properties: there is no list of
            # properties that reliably contains every place a colour can hide.
            hit = has_literal(value)
            if hit and (prop, hit) not in seen:
                seen.add((prop, hit))
                found.append((prop, hit))
    return found


_TOKEN_HELP = (
    "    ink        var(--ig-ink) var(--ig-secondary) var(--ig-muted)\n"
    "    surface    var(--ig-page) var(--ig-card) var(--ig-sunken)\n"
    "    accent     var(--ig-accent) var(--ig-accent-text) var(--ig-accent-wash)\n"
    "    series     var(--ig-series-0) … var(--ig-series-7)\n"
    "    status     var(--ig-good) var(--ig-warn) var(--ig-danger) and -wash\n"
    "    rules      var(--ig-border) var(--ig-hairline) var(--ig-axis)\n"
    "  `color-mix()`, the gradient functions, `opacity` and `mix-blend-mode` all\n"
    "  pass, so a wash, a soft field or a tinted overlay is available without\n"
    "  leaving the palette:\n"
    "    background: color-mix(in srgb, var(--ig-accent) 12%, transparent);\n")


# -------------------------------------------------------- self-containment --

_SCRIPT = re.compile(r"<script\b", re.I)
_HANDLER = re.compile(r"\son[a-z]+\s*=\s*[\"']", re.I)
_STYLE_TAG = re.compile(r"<style\b", re.I)
_REMOTE = re.compile(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.I)
_CSS_REMOTE = re.compile(r"url\(\s*[\"']?\s*(?:https?:)?//", re.I)
_IMPORT = re.compile(r"@import\b", re.I)

# ------------------------------------------------------------ a11y floor ----

_IMG = re.compile(r"<img\b[^>]*>", re.I)
_HAS_ALT = re.compile(r"\balt\s*=", re.I)
_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
_ARIA_HIDDEN = re.compile(r'\baria-hidden\s*=\s*["\']true["\']', re.I)
_ARIA_LABEL = re.compile(r"\baria-label\s*=", re.I)


def _svg_has_name(markup: str, open_match) -> bool:
    tag = open_match.group(0)
    if _ARIA_HIDDEN.search(tag) or _ARIA_LABEL.search(tag):
        return True
    close = markup.find("</svg", open_match.end())
    inner = markup[open_match.end():close if close >= 0 else len(markup)]
    return "<title" in inner.lower()


def validate(spec: dict) -> None:
    """Raise a build error, with the fix, for anything an authored page owes."""
    body = str(spec.get("body") or "")
    style = str(spec.get("style") or "")

    if not body.strip():
        raise SystemExit(
            "[authored] `body` is empty. There is nothing to draw.\n"
            "  An authored spec carries the document's markup in `body` and its\n"
            "  CSS in `style`. → references/authored.md")

    if _STYLE_TAG.search(body):
        raise SystemExit(
            "[authored] a <style> tag in `body`.\n"
            "  CSS goes in the spec's `style` key, not inside the markup, so the\n"
            "  colour check can see it. A stylesheet the validator cannot read is\n"
            "  a stylesheet that can quietly leave the palette.")

    literals = css_literals(style) + paint_literals(body)
    if literals:
        listed = "\n".join(f'      {prop}: {value}' for prop, value in literals[:10])
        more = f"\n      … and {len(literals) - 10} more" if len(literals) > 10 else ""
        raise SystemExit(
            f"[authored] {len(literals)} colour literal(s).\n{listed}{more}\n\n"
            f"  Colour in this skill is computed, not chosen, and it is the one\n"
            f"  thing an authored page must not invent: a document that picks its\n"
            f"  own hues stops re-skinning with `--theme` and stops being checked\n"
            f"  by the contrast validator. Everything else about the page is yours.\n"
            + _TOKEN_HELP + "  → references/authored.md")

    if _SCRIPT.search(body) or _HANDLER.search(body):
        raise SystemExit(
            "[authored] a <script> or an inline event handler.\n"
            "  The deliverable is a PDF or a screenshot, so the page is printed as\n"
            "  a snapshot: anything that needs a script to appear is blank on\n"
            "  paper. Draw the end state. CSS transforms, gradients and\n"
            "  `mix-blend-mode` all render; behaviour does not.")

    if _REMOTE.search(body) or _CSS_REMOTE.search(style) or _IMPORT.search(style):
        raise SystemExit(
            "[authored] a remote asset (http, https or protocol-relative).\n"
            "  The renderer does not wait for the network, so a remote image is a\n"
            "  race it usually loses and prints as a gap. Inline the drawing as\n"
            "  SVG, or embed the file as a `data:` URI.")

    for match in _IMG.finditer(body):
        if not _HAS_ALT.search(match.group(0)):
            raise SystemExit(
                f"[authored] an <img> with no alt attribute:\n"
                f"      {match.group(0)[:90]}\n"
                f'  Describe what it shows, or alt="" if it is purely decorative.\n'
                f"  Omitting it is not the same as deciding it.")

    for match in _SVG_OPEN.finditer(body):
        if not _svg_has_name(body, match):
            raise SystemExit(
                f"[authored] an <svg> with no accessible name:\n"
                f"      {match.group(0)[:90]}\n"
                f"  A drawing that can only be read by looking at it is unreadable\n"
                f"  to a screen reader, a search index, and anyone printing in mono.\n"
                f'  Add role="img" aria-label="…", or a <title> as its first child,\n'
                f'  or aria-hidden="true" if another element already names it.')

    encodes = spec.get("encodes", (spec.get("meta") or {}).get("encodes"))
    if encodes is None:
        raise SystemExit(
            "[authored] no `encodes` in meta.\n"
            "  One declaration, and it is not paperwork: it decides whether the\n"
            "  values in this page are reachable by someone who cannot see it.\n"
            '    "encodes": "concept"        no data is drawn here\n'
            '    "encodes": {"columns": […], "rows": […]}      one table twin\n'
            '    "encodes": [{…}, {…}]                        several')
    if isinstance(encodes, str):
        if encodes.strip().lower() != "concept":
            raise SystemExit(
                f"[authored] `encodes` as a string must be exactly \"concept\" "
                f"(got {encodes!r}).\n"
                f"  If the page does draw values, give them: "
                f'{{"columns": […], "rows": […]}}.')
    else:
        for twin in (encodes if isinstance(encodes, list) else [encodes]):
            if not (isinstance(twin, dict) and twin.get("columns") and twin.get("rows")):
                raise SystemExit(
                    "[authored] every `encodes` twin needs `columns` and `rows`.")


def twins(spec: dict) -> list:
    """The declared table twins, normalised to a list. Empty for a concept page."""
    encodes = spec.get("encodes", (spec.get("meta") or {}).get("encodes"))
    if isinstance(encodes, str) or encodes is None:
        return []
    return list(encodes) if isinstance(encodes, list) else [encodes]


def is_concept(spec: dict) -> bool:
    encodes = spec.get("encodes", (spec.get("meta") or {}).get("encodes"))
    return isinstance(encodes, str) and encodes.strip().lower() == "concept"


# ------------------------------------------------------------ composition --

_PLACEHOLDER = re.compile(
    r"<(?P<tag>[a-zA-Z][\w-]*)\b(?P<before>[^>]*?)"
    r'\bdata-block\s*=\s*"(?P<id>[^"]+)"(?P<after>[^>]*?)'
    r"\s*(?:/>|>\s*</(?P=tag)\s*>)", re.S)

_WIDTH = re.compile(r'\bdata-width\s*=\s*"(\d+(?:\.\d+)?)"')


def compose(spec: dict, render, default_width: float) -> tuple:
    """Substitute every `data-block` placeholder with its rendered block.

    `render(block, width)` is the caller's block renderer. Returns
    `(html, warnings)`. A placeholder naming a block that does not exist is an
    error; a block that no placeholder names is a warning, because it silently
    will not appear on the page.
    """
    body = str(spec.get("body") or "")
    blocks = {}
    for block in spec.get("blocks", []) or []:
        if isinstance(block, dict) and block.get("id"):
            blocks[str(block["id"])] = block

    used, warnings = set(), []

    def substitute(match):
        block_id = match.group("id")
        if block_id not in blocks:
            known = ", ".join(sorted(blocks)) or "none"
            raise SystemExit(
                f'[authored] the body places a block "{block_id}", which is not '
                f"in `blocks`.\n"
                f"  Blocks with an id: {known}\n"
                f'  A placeholder is <div data-block="the-id"></div>, and the '
                f"block itself\n  is an ordinary catalog block in the spec's "
                f"`blocks` list.")
        used.add(block_id)
        attrs = match.group("before") + match.group("after")
        width_match = _WIDTH.search(attrs)
        width = float(width_match.group(1)) if width_match else default_width
        return render(blocks[block_id], width)

    html = _PLACEHOLDER.sub(substitute, body)

    for block_id in blocks:
        if block_id not in used:
            warnings.append(
                f'authored-unplaced: block "{block_id}" is in `blocks` but no '
                f"placeholder in `body` calls for it, so it does not appear on "
                f'the page. Add <div data-block="{block_id}"></div> where it '
                f"belongs, or delete it.")
    return html, warnings


# Elements whose `id` is a reference target, not a place on the page. A gradient
# or a clip path is addressed by `url(#…)` from somewhere else in the drawing;
# treating one as a ladder landmark inserts a phantom rung position and shifts
# every real one after it, so a correct document starts failing `ladder-order`
# for a reason nothing in the error message could explain.
_DEF_TAGS = ("defs", "lineargradient", "radialgradient", "pattern", "mask",
             "clippath", "filter", "marker", "symbol")
_DEFS_BLOCK = re.compile(r"<defs\b.*?</defs\s*>", re.S | re.I)
_TAG_BEFORE_ID = re.compile(r"<([a-zA-Z][\w-]*)\b[^>]*$", re.S)


def landmarks(body: str, block_text=None) -> list:
    """`[(id, text), …]` in document order, for the ladder.

    A ladder rung lands `at` an id. In block mode that is a block's `id`; here it
    is any element in the authored markup carrying one, and the text belonging to
    it is everything up to the next such element. Approximate by construction,
    because an authored page has no block boundaries, and good enough for the
    only question the ladder asks: does a word appear before the thing that
    teaches it?

    `block_text` maps a placed block's id to its reading matter. Without it a
    `<div data-block="x"></div>` contributes zero text to its chunk, so a term
    the block introduces looks absent to `ladder-unused`, and a forward
    reference *inside* a placed block is invisible to the check entirely.
    """
    body = _DEFS_BLOCK.sub(" ", body)

    # Placed blocks are a hole in the text otherwise: the placeholder is an
    # empty element here and only becomes a chart at render.
    if block_text:
        def expand(match):
            return " " + str(block_text.get(match.group("id"), "")) + " "
        body = _PLACEHOLDER.sub(expand, body)

    marks = []
    for match in re.finditer(r'\bid\s*=\s*"([^"]+)"', body):
        tag = _TAG_BEFORE_ID.search(body[:match.start()])
        if tag and tag.group(1).lower() in _DEF_TAGS:
            continue
        marks.append((match.group(1), match.start()))

    out = []
    for index, (name, start) in enumerate(marks):
        end = marks[index + 1][1] if index + 1 < len(marks) else len(body)
        chunk = re.sub(r"<[^>]+>", " ", body[start:end])
        out.append((name, re.sub(r"\s+", " ", chunk).strip()))
    return out
