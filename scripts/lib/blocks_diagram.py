"""Diagram blocks: the forms that absorb what would otherwise become paragraphs.

Every block here exists because a real document tried to explain something in
prose and should not have. When an author writes three sentences about which
component sits in which layer, that is a `stack`. When they write a paragraph
justifying why option E beat option A, that is a `scorecard`. When they write
"the score was 66 out of 75", that is a `gauge`.

The test each of these has to pass: **the reader gets the idea from the picture
with the caption covered.** If a block only makes sense once you have read the
sentence underneath it, the block is decoration and the sentence is the content,
which is the arrangement this whole family exists to prevent.
"""

from __future__ import annotations

import math

from . import chrome, pictograms, svg
from .blocks_editorial import inline
from .theme import Ctx

CHIP_PAD = 13.0
CHIP_GAP = 7.0
CHIP_H = 25.0


def _chip_rows(labels, available, size=10.0, weight=600):
    """Lay chips into rows that fit `available`.

    Returns rows of `(label, x, width, inner)`. `inner` is the text width this
    chip is guaranteed, and it is carried rather than recomputed as
    `width - 2 * CHIP_PAD` because that round-trip does not survive floating
    point: a label measuring 62.05 produced an inner width of 62.049999…, so a
    chip sized to fit its own label exactly came out ellipsized.

    Widths come from the same over-estimating text metric the rest of the skill
    uses. A chip a little too wide looks considered; one a little too narrow
    clips its own label.
    """
    rows, row, x = [], [], 0.0
    for label in labels:
        text = str(label)
        inner = svg.text_width(text, size, weight)
        w = max(inner + CHIP_PAD * 2, 56.0)
        if w > available:
            w, inner = available, max(available - CHIP_PAD * 2, 8.0)
        if row and x + w > available:
            rows.append(row)
            row, x = [], 0.0
        row.append((text, x, w, inner))
        x += w + CHIP_GAP
    if row:
        rows.append(row)
    return rows


def balanced_columns(count: int, width: float, min_tile: float) -> int:
    """How many columns to lay `count` tiles across `width`.

    Six tiles across four columns leaves a row of two and reads as a mistake;
    three columns of two reads as a grid. So drop a column when it tidies the
    last row, but only while the row COUNT stays the same. Without that guard
    the rule runs away: ten tiles walk 4 → 3 → 2, each step "more balanced" and
    each step wasting more of the page.
    """
    fit = max(1, int(width // min_tile))
    columns = min(fit, max(count, 1))
    rows = math.ceil(count / columns)
    best = columns
    for candidate in range(columns - 1, 1, -1):
        if math.ceil(count / candidate) != rows:
            break
        if count % candidate == 0 or (count % candidate) > (count % best or 0):
            best = candidate
    return best


# ------------------------------------------------------------------ stack ----

def stack(b: dict, ctx: Ctx) -> str:
    """Layers resting on each other, each holding named parts.

    The canonical use is an architecture: edge, application, data. It reads top
    to bottom because that is how people draw and describe stacks, and the layer
    label sits in a fixed left column so the eye can run down the spine.
    """
    t = ctx.theme
    layers = b.get("layers", b.get("items", []))
    if not layers:
        return ""
    n = len(layers)
    label_w = max(96.0, min(ctx.width * 0.24, 190.0))
    gap = 10.0
    body_x = label_w + 16.0
    body_w = ctx.width - body_x

    laid, total_h = [], 0.0
    for layer in layers:
        items = [i.get("label", i) if isinstance(i, dict) else i
                 for i in layer.get("items", [])]
        rows = _chip_rows(items, body_w)
        note = str(layer.get("note", ""))
        note_lines = svg.wrap(note, 9.5, body_w, max_lines=1) if note else []
        h = max(len(rows) * CHIP_H + max(len(rows) - 1, 0) * CHIP_GAP + 26.0, 54.0)
        h += len(note_lines) * 14.0
        laid.append((layer, rows, note_lines, h))
        total_h += h + gap

    height = total_h - gap + 2
    canvas = svg.Canvas(ctx.width, height, t)
    y = 0.0
    for index, (layer, rows, note_lines, h) in enumerate(laid):
        color = t.ordinal(index, n) if b.get("ordinal", True) else t.series(0)
        band = t.wash(color, 0.09, on=t.surface("page"))
        canvas.rect(0, y, ctx.width, h, band, r=t.geom("radius", 4) * 2)
        canvas.rect(0, y, 4, h, color, r=0)

        label_lines = svg.wrap(str(layer.get("label", "")), 11.5, label_w - 22, 600, 3)
        canvas.text_lines(16, y + 22, label_lines, size=11.5, weight=650,
                          fill=t.ink("primary"), line_height=1.2)
        if layer.get("meta"):
            canvas.text(16, y + 22 + len(label_lines) * 14 + 2, str(layer["meta"]),
                        size=9, weight=500, fill=t.ink("muted"))

        cy = y + 13.0
        for row in rows:
            for label, x, w, inner in row:
                canvas.rect(body_x + x, cy, w, CHIP_H, t.surface("card"),
                            r=t.geom("radius", 4) + 1,
                            stroke=t.wash(color, 0.55, on=t.surface("page")),
                            stroke_width=1)
                canvas.text(body_x + x + w / 2, cy + 16.5,
                            svg.truncate(label, 10, inner, 600),
                            size=10, weight=600, fill=t.ink("primary"), anchor="middle")
            cy += CHIP_H + CHIP_GAP
        for line in note_lines:
            canvas.text(body_x, cy + 8, line, size=9.5, fill=t.ink("muted"))
        y += h + gap

    rows_out = [[str(l.get("label", "")),
                 ", ".join(str(i.get("label", i) if isinstance(i, dict) else i)
                           for i in l.get("items", []))] for l in layers]
    twin = chrome.details_table(["Layer", "Contains"], rows_out, "Show the layers") \
        if b.get("table", True) else ""
    return canvas.render() + twin


# ------------------------------------------------------------------ chips ----

def chips(b: dict, ctx: Ctx) -> str:
    """Indicator chips: the graphic-density replacement for a bullet list.

    A bullet list is a paragraph wearing a disc. A chip grid is scannable, has a
    shape, and costs the author their adjectives, because a chip that needs
    twelve words is not a chip.
    """
    items = b.get("items", [])
    if not items:
        return ""
    tones = {"good": "good", "warn": "warn", "danger": "danger",
             "accent": "accent", "plain": "plain", "mute": "mute"}
    icons = {"good": "✓", "warn": "!", "danger": "✕", "accent": "◆"}
    cells = []
    for item in items:
        if not isinstance(item, dict):
            item = {"label": item}
        tone = tones.get(str(item.get("tone", "plain")), "plain")
        icon = item.get("icon", icons.get(tone, ""))
        # An `icon` has always been a literal character, and still is. A name
        # from the pictogram library is recognised instead, which is the
        # difference between a chip row about apartments carrying "◆" and
        # carrying an apartment. Neither is required; the tone marks are the
        # default and they say the thing that usually matters, which is whether
        # the item is good or bad.
        if pictograms.has(icon):
            glyph = (f'<svg class="ig-chip-icon ig-chip-pic" aria-hidden="true" '
                     f'focusable="false" viewBox="0 0 24 24" fill="currentColor">'
                     f'<use href="#{pictograms.ID_PREFIX}{icon}"/></svg>')
        elif icon:
            glyph = f'<span class="ig-chip-icon" aria-hidden="true">{svg.esc(icon)}</span>'
        else:
            glyph = ""
        value = (f'<span class="ig-chip-value">{inline(item["value"])}</span>'
                 if item.get("value") is not None else "")
        note = (f'<span class="ig-chip-note">{inline(item["note"])}</span>'
                if item.get("note") else "")
        cells.append((glyph, f'<li class="ig-chip ig-chip-{tone}">',
                      f'<span class="ig-chip-label">{inline(item.get("label", ""))}</span>'
                      f"{value}{note}</li>"))
    # A grid whose labels start at different distances from the left edge is not
    # a grid. Once ONE chip carries a mark, the plain ones hold the gutter open
    # rather than sliding under it; a block where nothing is toned keeps the
    # gutter closed and reads as the plain list it is.
    blank = ('<span class="ig-chip-icon" aria-hidden="true"></span>'
             if any(glyph for glyph, _, _ in cells) else "")
    cells = [open_tag + (glyph or blank) + rest for glyph, open_tag, rest in cells]
    # Column count is decided here for the same reason the KPI row decides its
    # own: CSS cannot see how wide this block's grid column actually is.
    requested = int(b.get("columns", 0) or 0)
    columns = (min(requested, len(cells)) if requested
               else balanced_columns(len(cells), ctx.width, 150.0))
    return (f'<ul class="ig-chips" style="--ig-chip-n:{columns}">'
            f'{"".join(cells)}</ul>')


# -------------------------------------------------------------- scorecard ----

def scorecard(b: dict, ctx: Ctx) -> str:
    """Options scored against criteria, with the totals as the punchline.

    This is the block that replaces "we evaluated five architectures against
    fifteen criteria and hybrid won" plus a bar chart. The cell grid shows the
    shape of *why* one option won; the total bar shows that it did.
    """
    t = ctx.theme
    # `choices`, not `options`: `options` is the reserved per-block render
    # settings dict, and naming the axis after it made the compiler try to merge
    # a list of strings into a dict.
    choices = b.get("choices", [])
    criteria = [str(c) for c in b.get("criteria", [])]
    scores = b.get("scores", [])
    if not choices or not scores:
        return ""
    names = [o.get("label", o) if isinstance(o, dict) else o for o in choices]
    maximum = float(b.get("max", 5))
    winner = b.get("winner")
    if winner is None:
        winner = max(range(len(scores)), key=lambda i: sum(scores[i]))

    label_w = max(92.0, min(ctx.width * 0.26, 210.0))
    total_w = 108.0
    grid_w = ctx.width - label_w - total_w - 24.0
    cols = max(len(criteria), 1)
    cell = min(grid_w / cols, 34.0)
    grid_w = cell * cols
    head_h = 12.0 + chrome.measure_labels(criteria, 8.5, cap=76.0) if criteria else 12.0
    row_h = max(cell + 8.0, 26.0)
    height = head_h + len(scores) * row_h + 16.0

    canvas = svg.Canvas(ctx.width, height, t)
    grid_x = label_w + 12.0

    for index, name in enumerate(criteria):
        x = grid_x + index * cell + cell / 2
        canvas.add(f'<g transform="rotate(-52 {svg.num(x)} {svg.num(head_h - 6)})">'
                   f'<text x="{svg.num(x)}" y="{svg.num(head_h - 6)}" font-size="8.5" '
                   f'fill="{svg.esc(t.ink("muted"))}" text-anchor="start">'
                   f"{svg.esc(svg.truncate(name, 8.5, 76))}</text></g>")

    totals = [sum(float(v or 0) for v in row) for row in scores]
    best = max(totals) if totals else 1.0
    for r, row in enumerate(scores):
        y = head_h + r * row_h
        is_winner = (r == winner)
        if is_winner:
            canvas.rect(0, y - 2, ctx.width, row_h, t.wash(t.accent, 0.08, on=t.surface("page")),
                        r=t.geom("radius", 4))
        canvas.text(4, y + row_h / 2 + 3.5,
                    svg.truncate(str(names[r]), 10.5, label_w - 12, 650 if is_winner else 500),
                    size=10.5, weight=650 if is_winner else 500,
                    fill=t.ink("primary") if is_winner else t.ink("secondary"))
        for c in range(cols):
            value = float(row[c]) if c < len(row) and row[c] is not None else 0.0
            share = max(0.0, min(1.0, value / maximum if maximum else 0))
            x = grid_x + c * cell
            size = 6.0 + (cell - 14.0) * share
            fill = t.sequential(0.25 + share * 0.7) if share > 0 \
                else t.wash(t.ink("muted"), 0.10, on=t.surface("page"))
            canvas.rect(x + (cell - size) / 2, y + (row_h - size) / 2, size, size,
                        fill, r=2)
        # The total bar is the only place length encodes anything, which is why
        # it reads as the answer rather than as one more cell.
        tx = grid_x + grid_w + 12.0
        bar_w = (total_w - 46.0) * (totals[r] / best if best else 0)
        canvas.bar(tx, y + row_h / 2 - 5, max(bar_w, 2.0), 10,
                   t.accent if is_winner else t.deemphasis, r=2, end="right")
        canvas.text(ctx.width, y + row_h / 2 + 3.5,
                    f"{svg.num(totals[r], 0)}", size=10.5,
                    weight=700 if is_winner else 500,
                    fill=t.ink("primary") if is_winner else t.ink("secondary"),
                    anchor="end")

    twin = ""
    if b.get("table", True):
        rows_out = [[str(names[r])] + [str(v) for v in scores[r]] + [str(int(totals[r]))]
                    for r in range(len(scores))]
        twin = chrome.details_table(["Option"] + criteria + ["Total"], rows_out,
                                    "Show the scores")
    return canvas.render() + twin


# ------------------------------------------------------------------ gauge ----

def gauge(b: dict, ctx: Ctx) -> str:
    """One score against its ceiling, as an arc.

    Use it when the ceiling is part of the claim ("66 of 75"). When there is no
    ceiling, the honest form is a `stat`. An arc with an invented maximum is a
    chart that fabricates its own scale.
    """
    t = ctx.theme
    value = float(b.get("value") or 0)
    maximum = float(b.get("max") or 100)
    share = max(0.0, min(1.0, value / maximum if maximum else 0))
    sweep = float(b.get("sweep", 260))
    start = -sweep / 2.0

    size = min(ctx.width, float(b.get("size", 190)))
    cx, cy = ctx.width / 2, size / 2 + 4
    r_out = size / 2 - 4
    thickness = float(b.get("thickness", 16))
    r_in = r_out - thickness

    color = t.accent
    for threshold in sorted(b.get("thresholds", []), key=lambda x: float(x.get("at", 0))):
        if share * 100 >= float(threshold.get("at", 0)):
            color = t.status(threshold.get("status", "warning"))

    label_h = 34.0 if b.get("label") else 14.0
    canvas = svg.Canvas(ctx.width, size / 2 + r_out * math.sin(math.radians(sweep / 2 - 90)) + size / 2 + label_h, t)
    canvas.path(svg.arc_path(cx, cy, r_out, r_in, start, start + sweep),
                fill=t.wash(color, 0.14, on=t.surface("page")))
    if share > 0:
        canvas.path(svg.arc_path(cx, cy, r_out, r_in, start, start + sweep * share),
                    fill=color)

    figure = b.get("display") or (f"{svg.num(value, 0)}"
                                  f"{'/' + svg.num(maximum, 0) if b.get('show_max', True) else ''}")
    canvas.text(cx, cy + 6, str(figure), size=size * 0.19, weight=700,
                fill=t.ink("primary"), anchor="middle")
    if b.get("caption"):
        canvas.text(cx, cy + 6 + size * 0.14, str(b["caption"]), size=9.5,
                    fill=t.ink("muted"), anchor="middle")
    if b.get("label"):
        canvas.text(cx, cy + r_out + 22, str(b["label"]), size=11, weight=600,
                    fill=t.ink("secondary"), anchor="middle")
    return canvas.render()


# --------------------------------------------------------------- swimlane ----

def swimlane(b: dict, ctx: Ctx) -> str:
    """Who does what, in what order. Lanes are actors; columns are stages.

    A sequence alone is a `process`. Reach for a swimlane only when *ownership*
    changes across the sequence and the hand-off is the thing being explained,
    otherwise the extra axis is empty structure.
    """
    t = ctx.theme
    lanes = b.get("lanes", [])
    stages = [str(s) for s in b.get("stages", [])]
    if not lanes or not stages:
        return ""
    label_w = max(88.0, min(ctx.width * 0.20, 170.0))
    grid_x = label_w + 10.0
    col_w = (ctx.width - grid_x) / len(stages)
    head_h = 26.0
    row_h = float(b.get("row_height", 52))
    height = head_h + len(lanes) * row_h + 6

    canvas = svg.Canvas(ctx.width, height, t)
    for index, stage in enumerate(stages):
        x = grid_x + index * col_w
        canvas.text(x + col_w / 2, 12, svg.truncate(stage, 9.5, col_w - 8, 600),
                    size=9.5, weight=650, fill=t.ink("secondary"), anchor="middle")
        if index:
            canvas.line(x, head_h - 8, x, height - 4, stroke=t.rule("hairline"), width=1)

    for r, lane in enumerate(lanes):
        y = head_h + r * row_h
        color = t.series(r) if b.get("color_lanes", True) else t.accent
        if r % 2 == 0:
            canvas.rect(0, y, ctx.width, row_h,
                        t.wash(t.ink("muted"), 0.045, on=t.surface("page")), r=3)
        canvas.rect(0, y + 8, 3, row_h - 16, color, r=1.5)
        canvas.text(10, y + row_h / 2 + 3.5,
                    svg.truncate(str(lane.get("label", "")), 10, label_w - 16, 600),
                    size=10, weight=600, fill=t.ink("primary"))
        for index, cell in enumerate(lane.get("cells", [])):
            if not cell:
                continue
            text = cell.get("label", cell) if isinstance(cell, dict) else cell
            x = grid_x + index * col_w
            pad = 5.0
            canvas.rect(x + pad, y + 10, col_w - pad * 2, row_h - 20,
                        t.wash(color, 0.16, on=t.surface("page")),
                        r=t.geom("radius", 4) + 1)
            lines = svg.wrap(str(text), 9.5, col_w - pad * 2 - 12, 600, 2)
            canvas.text_lines(x + col_w / 2, y + row_h / 2 - (len(lines) - 1) * 6 + 3.5,
                              lines, size=9.5, weight=600, fill=t.ink("primary"),
                              anchor="middle", line_height=1.25)
    return canvas.render()
