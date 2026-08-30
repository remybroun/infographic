"""Teaching blocks: the forms a schoolbook uses and a chart catalog does not.

Every other family in this skill draws a relation between *things the reader
already accepts*: a quantity against a category, a stage after a stage, a part
of a whole. That vocabulary assumes the reader has the concept and is now
operating on it. It has no shape at all for the moment before that, when someone
meets a subject for the first time, and the result was documents that were
formally correct and read like minutes of a meeting you were not at.

Three shapes, taken from how a subject is actually taught:

- `analogy` puts something the reader already owns beside the new thing, part
  for part. It is the single most reliable teaching move there is, and the
  catalog's nearest neighbour, `comparison`, is its opposite: comparison exists
  to argue that the right-hand side is better, analogy exists to claim the two
  sides are the same shape. It draws both subjects and numbers the parts across
  them, because a mapping the reader has to read line by line is a table, and a
  table is what this block spent a version being.
- `progressive` draws one picture several times, gaining a part each time. A
  finished architecture diagram shows a reader what a system contains; it never
  shows them how to think about it, because every part arrives at once and
  nothing says which parts were there first and why the rest became necessary.
All of them carry their idea in the picture, so they count as graphics.
`progressive` draws real SVG; `analogy` is an HTML and CSS
composition for the same reason `checklist` is, their content is sentences that
must stay selectable, reflowable, and never silently truncated to fit a row.
"""

from __future__ import annotations

import re

from . import chrome, pictograms, svg
from .blocks_editorial import inline
from .blocks_figure import paint_literals
from .theme import Ctx

# ---------------------------------------------------------------- analogy ----

_SCENE_VIEWBOX = re.compile(r"^\s*-?[\d.]+\s+-?[\d.]+\s+[\d.]+\s+[\d.]+\s*$")


def _scene(scene: dict, where: str) -> str:
    """One authored drawing inside an analogy stage, held to a figure's rules.

    The same three guarantees, for the same three reasons: a viewbox so the
    drawing scales to whatever width the stage lands at, an `alt` so it is
    readable without being seen, and no colour literal so it re-skins with the
    document. A drawing that escapes those inside a block is a drawing that
    escapes them everywhere, and this key exists precisely so that authors stop
    reaching for a category icon.
    """
    markup = str(scene.get("svg") or "")
    viewbox = str(scene.get("viewbox") or scene.get("viewBox") or "").strip()
    alt = str(scene.get("alt") or "").strip()

    if not _SCENE_VIEWBOX.match(viewbox):
        raise SystemExit(
            f"[analogy] {where}: `viewbox` must be four numbers, got {viewbox!r}.\n"
            f"  It is what lets the drawing scale to the stage it lands in.\n"
            f'    "viewbox": "0 0 260 140"')
    if not alt:
        raise SystemExit(
            f"[analogy] {where}: no `alt`.\n"
            f"  Say in one sentence what the picture shows. The whole point of a\n"
            f"  scene is that it shows the situation, so it has something to say.")
    literals = paint_literals(markup)
    if literals:
        listed = "\n".join(f'      {p}="{v}"' for p, v in literals[:6])
        raise SystemExit(
            f"[analogy] {where}: {len(literals)} colour literal(s) in the drawing.\n"
            f"{listed}\n"
            f"  Paint is var(--ig-…), currentColor, none, or url(#…). The kit classes\n"
            f"  are shorter: ig-fig-solid, ig-fig-edge, ig-fig-node-mute, ig-fig-accent.\n"
            f"  See references/drawing.md.")

    outer = re.match(r"\s*<svg\b[^>]*>(.*)</svg>\s*$", markup, re.S | re.I)
    if outer:
        markup = outer.group(1)
    return (f'<svg class="ig-anl-scene" viewBox="{svg.esc(viewbox)}" role="img" '
            f'aria-label="{svg.esc(alt)}" preserveAspectRatio="xMidYMid meet">'
            f"<title>{svg.esc(alt)}</title>{markup}</svg>")


def analogy(b: dict, ctx: Ctx) -> str:
    """Two scenes side by side, each carrying its subject, annotated in step.

    Drawn as HTML rather than SVG, and as two *things* rather than two columns
    of cells. The version this replaces was a ruled list with a connector glyph
    down the middle: a table wearing a diagram's name. It made the reader *read*
    the mapping instead of seeing it, it silently truncated any label too long
    for its row, and the two things being likened never appeared on the page at
    all, which is a strange outcome for the one block whose whole job is to put
    something you can already picture beside something you cannot.

    So each side is a stage holding the subject itself, drawn large, and the
    mapping is carried the way an exploded drawing carries one: the same
    numbers, in the same order, at the same height on both sides. Position is
    the correspondence. An arrow or an equals sign would claim a direction or an
    identity, and an analogy has neither.

    **Draw the two sides with `scene`, not `glyph`.** A `scene` is authored SVG,
    held to the same rules as a `figure`: a viewbox, an `alt`, and no colour
    literal. `glyph` names one of the 52 library silhouettes and is the fallback,
    not the recommendation, because a library symbol names a *category* and an
    analogy is never about a category. A situation drawn as the nearest icon
    shows none of the parts the pairs are about, and it is wrong in a way the
    reader cannot detect. The strongest thing this block can do is draw both
    sides in the *same composition* with one object swapped, so the likeness is
    seen before a single pair is read.
    """
    known = b.get("known", {}) or {}
    new = b.get("new", {}) or {}
    pairs = [p for p in (b.get("pairs", []) or []) if isinstance(p, dict)]
    where = f'analogy ({b.get("id") or "?"})'

    def stage(data: dict, side: str, kicker: str) -> str:
        scene = data.get("scene")
        glyph = data.get("glyph")
        art, kind = "", "ig-anl-bare"
        if isinstance(scene, dict) and str(scene.get("svg") or "").strip():
            art, kind = _scene(scene, f"{where}.{side}.scene"), "ig-anl-drawn"
        elif glyph and pictograms.has(glyph):
            art = (f'<svg class="ig-anl-glyph" viewBox="0 0 24 24" '
                   f'aria-hidden="true">{pictograms.use(glyph, 0, 0, 24, "analogy")}'
                   f'</svg>')
            kind = "ig-anl-iconic"
        return (f'<div class="ig-anl-stage ig-anl-{side} {kind}">'
                f'<p class="ig-anl-kicker">{kicker}</p>{art}'
                f'<p class="ig-anl-name">{inline(data.get("label", ""))}</p></div>')

    def part(text: str, number: int, side: str) -> str:
        return (f'<div class="ig-anl-part ig-anl-{side}">'
                f'<span class="ig-anl-no" aria-hidden="true">{number}</span>'
                f'<span>{inline(text)}</span></div>')

    rows = "".join(
        part(pair.get("known", ""), index, "known") +
        part(pair.get("new", ""), index, "new")
        for index, pair in enumerate(pairs, 1))

    body = (stage(known, "known", "You already know") +
            stage(new, "new", "So this is") + rows)

    # No table twin by default, for the reason `checklist` has none: every pair is already selectable, reflowable text sitting in
    # the page, so the twin is a verbatim second copy. It is not free, either.
    # Twins are collapsed on screen and forced open in print, so `ig.py measure`
    # cannot see one and an authored one-pager measures as fitting and then
    # renders onto two sheets. Ask for it with "table": true if the mapping is
    # long enough that a reader would want to look a row up.
    twin = chrome.details_table(
        [known.get("label", "Known"), new.get("label", "This")],
        [[p.get("known", ""), p.get("new", "")] for p in pairs],
        label="Show the mapping") if b.get("table") else ""
    return f'<div class="ig-analogy">{body}</div>{twin}'


# ------------------------------------------------------------ progressive ----

STAGE_GAP = 16.0
PART_H = 26.0
PART_GAP = 6.0
STAGE_LABEL_H = 30.0


def progressive(b: dict, ctx: Ctx) -> str:
    """One picture, drawn two to four times, gaining a part each time.

    `parts` is the full vocabulary in the order it will be built up. Each stage
    `adds` one or more of them; everything added earlier stays, drawn plainly,
    and everything not yet added is a dashed ghost so the reader can see where
    the picture is going. The new part in each stage is the only thing wearing
    the accent, which is what makes the sequence readable as *growth* rather
    than as four similar diagrams.
    """
    t = ctx.theme
    parts = [str(p) for p in (b.get("parts", []) or [])]
    stages = [s for s in (b.get("stages", []) or []) if isinstance(s, dict)]
    ghost = b.get("ghost", True)
    if not parts or not stages:
        return '<p class="ig-block-note">progressive needs `parts` and `stages`</p>'

    count = len(stages)
    width = ctx.width
    col = (width - STAGE_GAP * (count - 1)) / count
    height = STAGE_LABEL_H + len(parts) * (PART_H + PART_GAP)

    canvas = svg.Canvas(width, height)
    ink, muted, border = t.ink("primary"), t.ink("muted"), t.rule("border")
    accent = t.accent

    radius = t.geom("radius", 4)
    inner = col - 18.0
    present = []
    for index, stage in enumerate(stages):
        x = index * (col + STAGE_GAP)
        adds = stage.get("adds", [])
        adds = [adds] if isinstance(adds, str) else [str(a) for a in adds]
        present = present + [a for a in adds if a not in present]

        canvas.text(x, 14.0, svg.truncate(stage.get("label", str(index + 1)), 10.5,
                                          col, 700),
                    size=10.5, weight=700, fill=ink)
        if stage.get("detail"):
            canvas.text(x, 26.0, svg.truncate(stage["detail"], 9.5, col),
                        size=9.5, fill=muted)

        for row, part in enumerate(parts):
            y = STAGE_LABEL_H + row * (PART_H + PART_GAP)
            if part in adds:
                canvas.rect(x, y, col, PART_H,
                            t.wash(accent, 0.14, on=t.surface("page")),
                            r=radius, stroke=accent)
                canvas.text(x + 9.0, y + PART_H / 2 + 3.5,
                            svg.truncate(part, 10, inner, 700),
                            size=10, weight=700, fill=ink)
            elif part in present:
                canvas.rect(x, y, col, PART_H, t.surface("sunken"),
                            r=radius, stroke=border)
                canvas.text(x + 9.0, y + PART_H / 2 + 3.5,
                            svg.truncate(part, 10, inner),
                            size=10, fill=ink)
            elif ghost:
                # A hairline at half strength, not a dashed outline. Dashing
                # would read as "threshold" here the way it does on a gridline,
                # and the linter refuses a `stroke-dasharray` anywhere in a
                # document for exactly that reason. Absence is carried by having
                # no fill and no label, which is unambiguous on its own.
                canvas.rect(x, y, col, PART_H, "none", r=radius, stroke=border,
                            opacity=0.55)

    missing = [p for s in stages for p in
               ([s.get("adds")] if isinstance(s.get("adds"), str) else s.get("adds", []) or [])
               if p not in parts]
    if missing:
        ctx.warn(f"progressive: stage adds {missing[0]!r}, which is not in `parts`. "
                 f"Nothing will be drawn for it.")

    rows = []
    seen = []
    for stage in stages:
        adds = stage.get("adds", [])
        adds = [adds] if isinstance(adds, str) else [str(a) for a in adds]
        seen = seen + [a for a in adds if a not in seen]
        rows.append([stage.get("label", ""), ", ".join(adds), ", ".join(seen)])
    twin = chrome.details_table(["Stage", "Adds", "Now present"], rows,
                                label="Show the build-up") if b.get("table", True) else ""
    return canvas.render() + twin


# ----------------------------------------------------------------- bridge ----

def bridge(b: dict, ctx: Ctx) -> str:
    """One sentence carrying the reader from one rung to the next.

    The sanctioned, capped, counted channel for the connective tissue a lesson
    needs and graphic density has nowhere to put. Without it that sentence goes
    into the next block's `subtitle`, which then stops stating what the picture
    shows, and a document loses its findings one bridge at a time.
    """
    return f'<p class="ig-bridge">{inline(b.get("text", ""))}</p>'
