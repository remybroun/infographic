"""`figure`: the authored drawing, and the guarantees it still owes.

Every other block in this skill turns a payload into a picture the skill already
knows how to draw. This one takes the picture. It exists because the catalog was
being used as the boundary of imagination: faced with an idea that is a
shockwave, or a beam narrowing as it goes deeper, or one application wearing five
hundred faces, the reflex was to scan the catalog for the closest existing shape
and ship that. The closest shape is not the shape.

So `figure` is deliberately NOT the old `raw` block with a friendlier name. `raw`
was written as a confession, "nothing fits and you accept losing theming and the
table view", and a penalty is not something an author reaches for. It voided
every guarantee, so using it felt like cheating, so nobody used it, so the
catalog stayed the ceiling.

A `figure` keeps all four guarantees and gives up none of them:

* **Colour is still computed.** Colour is where hand-drawing slips first, and it
  is the one part of this skill that is measured rather than judged. Every paint
  value must be a theme token, `currentColor`, `none`, or a `url(#…)` reference.
  A hex literal is a build error naming the literal. This is the check that keeps
  a hand-drawn figure inside the validated palette instead of beside it.
* **It is still readable without seeing it.** `alt` is required.
* **Its values are still reachable.** `encodes` forces one honest declaration:
  either the drawing carries data, which then ships a table twin, or it is a
  concept drawing and says so.
* **Its text is still budgeted.** Words inside `<text>` are charged as
  `figure_text` in density.py. A drawing labels; it does not narrate.

And one guarantee the others do not need: **a cap of three per document**, in
build.py. Without it, "draw the shape the catalog lacks" decays into "hand-draw
everything", every output stops resembling its siblings, and the consistency the
catalog buys is gone. Three forces the ranking that matters: which two or three
images does this document live or die by? Those get authored. The rest is
supporting material, and supporting material belongs on rails.
"""

from __future__ import annotations

import re

from . import svg
from .chrome import details_table
from .theme import Ctx

# Paint-carrying properties, as attributes and as inline style declarations.
_PAINT = ("fill", "stroke", "stop-color", "color", "flood-color",
          "lighting-color", "background", "background-color", "border-color")

_ATTR = re.compile(
    r'\b(' + "|".join(_PAINT) + r')\s*=\s*["\']([^"\']*)["\']', re.I)
_STYLE = re.compile(r'\bstyle\s*=\s*["\']([^"\']*)["\']', re.I)
_DECL = re.compile(r'([a-z-]+)\s*:\s*([^;]+)', re.I)

# The whitelist is deliberately a whitelist. A blacklist of hex patterns and
# named colours misses `color-mix()`, `oklch()`, and the next syntax Chrome
# ships; an allow-list of four shapes cannot.
_ALLOWED = re.compile(
    r'^(?:none|transparent|inherit|unset|initial|currentcolor'
    r'|url\(\s*#[^)]+\s*\)'
    r'|var\(\s*--ig-[a-z0-9-]+\s*\))$', re.I)

_VIEWBOX = re.compile(r'^\s*-?[\d.]+\s+-?[\d.]+\s+-?[\d.]+\s+-?[\d.]+\s*$')


def paint_literals(markup: str):
    """Every paint value in `markup` that is not a theme token.

    Returns `[(property, value), …]` in document order, deduplicated. Used by
    the build to refuse a drawing that picks its own colours, and importable so
    a test can assert on the same rule the build enforces.
    """
    found, seen = [], set()

    def consider(prop, value):
        value = str(value).strip()
        if not value or _ALLOWED.match(value):
            return
        if (prop.lower(), value) in seen:
            return
        seen.add((prop.lower(), value))
        found.append((prop.lower(), value))

    for match in _ATTR.finditer(markup):
        consider(match.group(1), match.group(2))
    for match in _STYLE.finditer(markup):
        for decl in _DECL.finditer(match.group(1)):
            if decl.group(1).lower() in _PAINT:
                consider(decl.group(1), decl.group(2))
    return found


def validate(block: dict, where: str = "figure") -> None:
    """Raise a build error, with the fix, for anything a figure owes.

    Called from the compiler before render so a bad figure fails on the reason
    it is bad rather than on some downstream symptom.
    """
    alt = str(block.get("alt") or "").strip()
    if not alt:
        raise SystemExit(
            f"[figure] {where}: no `alt`.\n"
            f"  A drawing that can only be read by looking at it is not readable by\n"
            f"  a screen reader, a search index, or anyone printing in mono. Write one\n"
            f"  sentence saying what the picture shows, not what it is called.\n"
            f'    "alt": "500 hostnames converge on one door and leave as one deployment."')

    viewbox = str(block.get("viewbox") or block.get("viewBox") or "").strip()
    if not _VIEWBOX.match(viewbox):
        raise SystemExit(
            f"[figure] {where}: `viewbox` must be four numbers, got {viewbox!r}.\n"
            f"  It is what lets the drawing scale to whatever grid column it lands in,\n"
            f"  so it is required rather than guessed.\n"
            f'    "viewbox": "0 0 720 320"')

    encodes = block.get("encodes")
    if encodes is None:
        raise SystemExit(
            f"[figure] {where}: no `encodes`.\n"
            f"  One declaration, and it is not paperwork: it decides whether the values\n"
            f"  in this drawing are reachable by someone who cannot see it.\n"
            f'    "encodes": "concept"                       a drawing with no data in it\n'
            f'    "encodes": {{"columns": […], "rows": […]}}   values, and their table twin')
    if not isinstance(encodes, str) and not (
            isinstance(encodes, dict) and encodes.get("columns") and encodes.get("rows")):
        raise SystemExit(
            f"[figure] {where}: `encodes` must be \"concept\" or an object with "
            f"`columns` and `rows`.")
    if isinstance(encodes, str) and encodes.strip().lower() != "concept":
        raise SystemExit(
            f"[figure] {where}: `encodes` as a string must be exactly \"concept\" "
            f"(got {encodes!r}).\n"
            f"  If the drawing does carry values, give them: "
            f'{{"columns": […], "rows": […]}}.')

    markup = str(block.get("svg") or "")
    if not markup.strip():
        raise SystemExit(f"[figure] {where}: `svg` is empty. There is nothing to draw.")

    literals = paint_literals(markup)
    if literals:
        listed = "\n".join(f"      {prop}=\"{value}\"" for prop, value in literals[:8])
        more = f"\n      … and {len(literals) - 8} more" if len(literals) > 8 else ""
        raise SystemExit(
            f"[figure] {where}: {len(literals)} colour literal(s) in the drawing.\n"
            f"{listed}{more}\n\n"
            f"  Colour in this skill is computed, not chosen, and a hand-drawn figure is\n"
            f"  where that slips first. Every theme slot is available as a custom\n"
            f"  property, so the drawing re-skins with the document instead of sitting\n"
            f"  beside it in last month's brand:\n"
            f"    ink        var(--ig-ink) var(--ig-secondary) var(--ig-muted)\n"
            f"    surface    var(--ig-page) var(--ig-card) var(--ig-sunken)\n"
            f"    accent     var(--ig-accent) var(--ig-accent-wash)\n"
            f"    series     var(--ig-series-0) … var(--ig-series-7)\n"
            f"    status     var(--ig-good) var(--ig-warn) var(--ig-danger)\n"
            f"    rules      var(--ig-border) var(--ig-hairline) var(--ig-axis)\n"
            f"  Or use the kit classes, which is shorter: class=\"ig-fig-node\",\n"
            f"  ig-fig-edge, ig-fig-label, ig-fig-accent, ig-fig-mute, ig-fig-s0…s7.\n"
            f"  See references/drawing.md.")


def figure(b: dict, ctx: Ctx) -> str:
    """Render an authored drawing into the grid.

    The markup is wrapped rather than reproduced: the caller supplies the
    contents of the drawing, and this adds the root `<svg>` with the viewBox,
    the accessible name, and the scaling style, so a figure cannot accidentally
    be authored at a fixed pixel size that overflows its column.
    """
    validate(b, f'blocks[?] ({b.get("id") or "figure"})')

    alt = str(b.get("alt")).strip()
    viewbox = str(b.get("viewbox") or b.get("viewBox")).strip()
    markup = str(b.get("svg"))

    # An author may supply either a bare fragment or a whole <svg>. Unwrapping a
    # whole one is friendlier than refusing it, and keeps the viewBox single-
    # sourced from the payload where the validator can see it.
    outer = re.match(r"\s*<svg\b[^>]*>(.*)</svg>\s*$", markup, re.S | re.I)
    if outer:
        markup = outer.group(1)

    classes = ["ig-figure"]
    if b.get("invert"):
        classes.append("ig-fig-invert")
    if b.get("class"):
        classes.append(str(b["class"]))

    body = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{svg.esc(viewbox)}" '
        f'class="{" ".join(classes)}" role="img" aria-label="{svg.esc(alt)}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;height:auto;display:block;overflow:visible">'
        f"<title>{svg.esc(alt)}</title>{markup}</svg>"
    )

    encodes = b.get("encodes")
    if isinstance(encodes, dict) and b.get("table", True):
        body += details_table(encodes["columns"], encodes["rows"],
                              encodes.get("label", "Show the numbers"),
                              encodes.get("align"))
    return body
