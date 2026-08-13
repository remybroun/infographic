"""Part-to-whole: share, composition and proportion.

Ranked by how accurately a reader decodes them: stacked bar > unit/waffle >
treemap > donut. Reach down the list only when the form buys something the one
above it cannot, a donut is here because briefs ask for it, not because it is
the best answer for comparing close values.
"""

from __future__ import annotations

import math

from . import chrome, svg
from .theme import Ctx
from .blocks_quantity import formatter


def _parts(b: dict):
    parts = b.get("parts", b.get("items", []))
    out = []
    for p in parts:
        out.append((str(p.get("label", "")), float(p.get("value") or 0), p.get("color")))
    return out


def _part_colors(ctx: Ctx, parts, b):
    if b.get("ordinal"):
        return [ctx.theme.ordinal(i, len(parts)) for i in range(len(parts))]
    explicit = [p[2] for p in parts]
    base = chrome.series_colors(ctx, len(parts), palette=b.get("palette"))
    return [explicit[i] or base[i] for i in range(len(parts))]


# --------------------------------------------------------- 100% stacked bar --

def share_bar(b: dict, ctx: Ctx) -> str:
    """One bar, normalized to the whole. The most accurately-decoded
    part-to-whole form there is, and the default answer to "show the split"."""
    t = ctx.theme
    parts = _parts(b)
    colors = _part_colors(ctx, parts, b)
    total = sum(p[1] for p in parts) or 1.0
    thickness = float(b.get("thickness", 42))
    gap = t.geom("surface_gap", 2)
    height = thickness + 16
    canvas = svg.Canvas(ctx.width, height, t)

    cursor = 0.0
    for i, (label, value, _) in enumerate(parts):
        share = value / total
        w = share * ctx.width
        seg = max(w - (gap if i < len(parts) - 1 else 0), 0.5)
        first, last = i == 0, i == len(parts) - 1
        canvas.bar(cursor, 4, seg, thickness, colors[i],
                   r=t.geom("radius", 4) if (first or last) else 0,
                   end="left" if first else ("right" if last else "none"))
        pct = f"{share * 100:.0f}%"
        if chrome.value_label_fits(pct, 12, seg, 14):
            canvas.text(cursor + seg / 2, 4 + thickness / 2 + 4.4, pct, size=12, weight=700,
                        fill=t.ink_on(colors[i]), anchor="middle")
        cursor += w

    fmt = formatter(b)
    out = [canvas.render(),
           chrome.legend_html(ctx, [(f"{p[0]} · {fmt(p[1])}", colors[i])
                                    for i, p in enumerate(parts)])]
    if b.get("table", True):
        out.append(chrome.details_table(
            [b.get("category_label", "Part"), b.get("value_label", "Value"), "Share"],
            [[p[0], fmt(p[1]), f"{p[1] / total * 100:.1f}%"] for p in parts]))
    return "".join(out)


# ------------------------------------------------------------------- donut ---

def donut(b: dict, ctx: Ctx) -> str:
    """Part-to-whole at a glance, at most about six segments. Never for
    comparing close values, angle is the least accurately decoded channel."""
    t = ctx.theme
    parts = _parts(b)
    if len(parts) > 6:
        ctx.warn("donut with more than 6 segments: adjacent slices stop being "
                 "distinguishable. Use a stacked share bar or a table.")
    colors = _part_colors(ctx, parts, b)
    total = sum(p[1] for p in parts) or 1.0
    fmt = formatter(b)

    size = min(ctx.width, float(b.get("size", 220)))
    height = size + 10
    cx, cy = ctx.width / 2, size / 2 + 4
    r_out = size / 2 - 4
    r_in = r_out * float(b.get("inner_ratio", 0.62))
    canvas = svg.Canvas(ctx.width, height, t)

    angle = 0.0
    for i, (label, value, _) in enumerate(parts):
        sweep = value / total * 360.0
        if sweep <= 0:
            continue
        canvas.path(svg.arc_path(cx, cy, r_out, r_in, angle, angle + sweep),
                    fill=colors[i], stroke=t.surface("card"),
                    width=t.geom("surface_gap", 2))
        angle += sweep

    if b.get("center_value") or b.get("center_label"):
        canvas.text(cx, cy + 2, str(b.get("center_value", "")), size=size * 0.16,
                    weight=700, fill=t.ink("primary"), anchor="middle",
                    family=t.font("sans"))
        canvas.text(cx, cy + size * 0.14, str(b.get("center_label", "")), size=10.5,
                    fill=t.ink("muted"), anchor="middle")

    out = [canvas.render(),
           chrome.legend_html(ctx, [(f"{p[0]} · {p[1] / total * 100:.0f}%", colors[i])
                                    for i, p in enumerate(parts)])]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Part", b.get("value_label", "Value"), "Share"],
            [[p[0], fmt(p[1]), f"{p[1] / total * 100:.1f}%"] for p in parts]))
    return "".join(out)


# -------------------------------------------------------------- unit chart ---

def unit(b: dict, ctx: Ctx) -> str:
    """Isotype / waffle. One glyph is one countable thing, so "3 in 10" stays
    literally countable. The strongest form for a human-scale ratio."""
    t = ctx.theme
    parts = _parts(b)
    colors = _part_colors(ctx, parts, b)
    total = float(b.get("total", sum(p[1] for p in parts))) or 1.0
    cells = int(b.get("cells", 100))
    per_row = int(b.get("per_row", 10 if cells % 10 == 0 else 20))
    rows = math.ceil(cells / per_row)

    cell = min((ctx.width - 4) / per_row, float(b.get("cell", 26)))
    pad = cell * 0.16
    height = rows * cell + 6
    canvas = svg.Canvas(ctx.width, height, t)

    counts, remainder = [], []
    for _, value, _ in parts:
        exact = value / total * cells
        counts.append(int(exact))
        remainder.append(exact - int(exact))
    # distribute rounding drift to the largest remainders so the glyphs total exactly
    short = cells - sum(counts)
    for idx in sorted(range(len(parts)), key=lambda i: -remainder[i])[:max(short, 0)]:
        counts[idx] += 1

    assignment = []
    for i, count in enumerate(counts):
        assignment.extend([i] * count)
    assignment = assignment[:cells] + [None] * max(cells - len(assignment), 0)

    glyph = b.get("glyph", "square")
    for index in range(cells):
        row, col = divmod(index, per_row)
        x = col * cell
        y = row * cell
        who = assignment[index]
        color = colors[who] if who is not None else t.surface("sunken")
        if glyph == "circle":
            canvas.circle(x + cell / 2, y + cell / 2, (cell - pad * 2) / 2, color)
        else:
            canvas.rect(x + pad / 2, y + pad / 2, cell - pad, cell - pad, color,
                        r=t.geom("radius", 4) / 2)

    fmt = formatter(b)
    out = [canvas.render(),
           chrome.legend_html(ctx, [(f"{p[0]} · {counts[i]} in {cells}", colors[i])
                                    for i, p in enumerate(parts)])]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Part", b.get("value_label", "Value"), f"Glyphs of {cells}"],
            [[p[0], fmt(p[1]), str(counts[i])] for i, p in enumerate(parts)]))
    return "".join(out)


# ----------------------------------------------------------------- treemap ---

def _squarify(values, x, y, w, h):
    """Squarified treemap layout. Returns rects in input order."""
    total = sum(values) or 1.0
    scale = (w * h) / total
    items = sorted(((v * scale, i) for i, v in enumerate(values)), key=lambda p: -p[0])
    rects = [None] * len(values)

    def worst(row, side):
        s = sum(a for a, _ in row)
        if s <= 0 or side <= 0:
            return float("inf")
        mx = max(a for a, _ in row)
        mn = min(a for a, _ in row)
        return max(side * side * mx / (s * s), (s * s) / (side * side * mn))

    def layout_row(row, x, y, w, h, horizontal):
        s = sum(a for a, _ in row)
        if horizontal:
            depth = s / w if w else 0
            cursor = x
            for area, idx in row:
                width = area / depth if depth else 0
                rects[idx] = (cursor, y, width, depth)
                cursor += width
            return x, y + depth, w, h - depth
        depth = s / h if h else 0
        cursor = y
        for area, idx in row:
            height = area / depth if depth else 0
            rects[idx] = (x, cursor, depth, height)
            cursor += height
        return x + depth, y, w - depth, h

    row = []
    while items:
        horizontal = w <= h
        side = w if horizontal else h
        head = items[0]
        if not row or worst(row + [head], side) <= worst(row, side):
            row.append(items.pop(0))
        else:
            x, y, w, h = layout_row(row, x, y, w, h, horizontal)
            row = []
    if row:
        layout_row(row, x, y, w, h, w <= h)
    return rects


def treemap(b: dict, ctx: Ctx) -> str:
    """Magnitude inside a hierarchy, when the item count is too high for bars
    and the relative area is the point. Areas are decoded loosely, always
    label, and keep the table view."""
    t = ctx.theme
    parts = _parts(b)
    parts = sorted(parts, key=lambda p: -p[1])
    total = sum(p[1] for p in parts) or 1.0
    height = float(b.get("height", 260))
    gap = t.geom("surface_gap", 2)
    canvas = svg.Canvas(ctx.width, height, t)
    rects = _squarify([p[1] for p in parts], 0, 0, ctx.width, height)
    fmt = formatter(b)

    for i, ((label, value, _), rect) in enumerate(zip(parts, rects)):
        if not rect:
            continue
        x, y, w, h = rect
        color = t.ordinal(len(parts) - 1 - i, len(parts)) if b.get("ordinal") else \
            t.sequential(0.35 + 0.5 * (value / (parts[0][1] or 1)), alt=bool(b.get("alt_hue")))
        canvas.rect(x, y, max(w - gap, 0.5), max(h - gap, 0.5), color,
                    r=t.geom("radius", 4) / 2)
        ink = t.ink_on(color)
        if w > 54 and h > 30:
            lines = svg.wrap(label, 11, w - 16, 600, 2)
            canvas.text_lines(x + 8, y + 18, lines, size=11, weight=600, fill=ink,
                              line_height=1.2)
            if h > 46:
                canvas.text(x + 8, y + 18 + len(lines) * 13.2 + 4,
                            f"{value / total * 100:.0f}%", size=10.5, fill=ink, opacity=0.82)

    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Item", b.get("value_label", "Value"), "Share"],
            [[p[0], fmt(p[1]), f"{p[1] / total * 100:.1f}%"] for p in parts]))
    return "".join(out)


# ------------------------------------------------------------------ funnel ---

def funnel(b: dict, ctx: Ctx) -> str:
    """Stage-to-stage drop-off. Width encodes the count; the labelled loss
    between stages is the actual story, so it is drawn, not left to arithmetic."""
    t = ctx.theme
    stages = b.get("stages", b.get("items", []))
    fmt = formatter(b)
    if not stages:
        return ""
    top = float(stages[0].get("value") or 1)
    row_h = float(b.get("row_height", 54))
    height = len(stages) * row_h + 12
    canvas = svg.Canvas(ctx.width, height, t)
    label_w = ctx.width * 0.34
    chart_w = ctx.width - label_w - 76

    for i, stage in enumerate(stages):
        value = float(stage.get("value") or 0)
        share = value / top if top else 0
        y = i * row_h + 6
        w = max(chart_w * share, 3)
        x = label_w + (chart_w - w) / 2
        color = t.ordinal(i, len(stages))
        canvas.bar(x, y, w, row_h - 16, color, r=t.geom("radius", 4), end="none")
        canvas.text(label_w - 12, y + (row_h - 16) / 2 + 4,
                    svg.truncate(str(stage.get("label", "")), 11, label_w - 16),
                    size=11, weight=600, fill=t.ink("secondary"), anchor="end")
        text = fmt(value)
        if chrome.value_label_fits(text, 11.5, w, 16):
            canvas.text(x + w / 2, y + (row_h - 16) / 2 + 4.4, text, size=11.5, weight=700,
                        fill=t.ink_on(color), anchor="middle")
        else:
            canvas.text(x + w + 8, y + (row_h - 16) / 2 + 4.4, text, size=11, weight=600,
                        fill=t.ink("primary"), anchor="start")
        canvas.text(ctx.width - 4, y + (row_h - 16) / 2 + 4, f"{share * 100:.0f}%",
                    size=10.5, weight=600, fill=t.ink("muted"), anchor="end")
        if i < len(stages) - 1:
            nxt = float(stages[i + 1].get("value") or 0)
            drop = (value - nxt) / value * 100 if value else 0
            canvas.text(label_w + chart_w / 2, y + row_h - 3,
                        f"−{drop:.0f}% drop-off", size=9, weight=600,
                        fill=t.ink("muted"), anchor="middle")

    out = [canvas.render()]
    if b.get("table", True):
        rows = []
        for i, s in enumerate(stages):
            value = float(s.get("value") or 0)
            prev = float(stages[i - 1].get("value") or 0) if i else None
            rows.append([str(s.get("label", "")), fmt(value),
                         f"{value / top * 100:.1f}%",
                         f"−{(prev - value) / prev * 100:.1f}%" if prev else ", "])
        out.append(chrome.details_table(
            ["Stage", b.get("value_label", "Count"), "Of top", "Drop-off"], rows))
    return "".join(out)


# ----------------------------------------------------------------- pyramid ---

def pyramid(b: dict, ctx: Ctx) -> str:
    """Layered hierarchy where each level rests on the one below, needs,
    maturity, evidence. Not a funnel: nothing is flowing, and the widths are
    conceptual rather than counted."""
    t = ctx.theme
    levels = b.get("levels", b.get("items", []))
    invert = bool(b.get("inverted"))
    row_h = float(b.get("row_height", 56))
    height = len(levels) * row_h + 8
    canvas = svg.Canvas(ctx.width, height, t)
    n = len(levels) or 1

    for i, level in enumerate(levels):
        pos = i if not invert else n - 1 - i
        frac = 0.34 + 0.66 * (pos + 1) / n
        w = ctx.width * frac
        x = (ctx.width - w) / 2
        y = i * row_h + 4
        color = t.ordinal(pos, n)
        canvas.bar(x, y, w, row_h - 10, color, r=t.geom("radius", 4), end="none")
        ink = t.ink_on(color)
        title = str(level.get("title", level.get("label", "")))
        canvas.text(ctx.width / 2, y + (row_h - 10) / 2 - (2 if level.get("text") else -4),
                    svg.truncate(title, 12.5, w - 24, 700), size=12.5, weight=700,
                    fill=ink, anchor="middle")
        if level.get("text"):
            canvas.text(ctx.width / 2, y + (row_h - 10) / 2 + 13,
                        svg.truncate(str(level["text"]), 10, w - 24), size=10,
                        fill=ink, anchor="middle", opacity=0.85)
    return canvas.render()


# ------------------------------------------------------------------- meter ---

def meter(b: dict, ctx: Ctx) -> str:
    """A single ratio against a limit. The unfilled track is a lighter step of
    the same ramp, so state reads across the whole bar rather than only the fill."""
    t = ctx.theme
    value = float(b.get("value") or 0)
    maximum = float(b.get("max") or 100)
    share = max(0.0, min(1.0, value / maximum if maximum else 0))
    fmt = formatter(b)
    thickness = float(b.get("thickness", 16))
    thresholds = b.get("thresholds", [])

    color = t.accent
    for threshold in sorted(thresholds, key=lambda x: float(x.get("at", 0))):
        if share * 100 >= float(threshold.get("at", 0)):
            color = t.status(threshold.get("status", "warning"))
    track = t.wash(color, 0.16, on=t.surface("card"))

    height = thickness + 34
    canvas = svg.Canvas(ctx.width, height, t)
    canvas.text(0, 12, str(b.get("label", "")), size=11, weight=600, fill=t.ink("secondary"))
    canvas.text(ctx.width, 12, f"{fmt(value)} / {fmt(maximum)}", size=11, weight=600,
                fill=t.ink("primary"), anchor="end")
    canvas.bar(0, 20, ctx.width, thickness, track, r=thickness / 2, end="none")
    canvas.bar(0, 20, max(ctx.width * share, thickness if share > 0 else 0), thickness,
               color, r=thickness / 2, end="none")
    for threshold in thresholds:
        x = ctx.width * float(threshold.get("at", 0)) / 100.0
        canvas.line(x, 18, x, 20 + thickness + 2, stroke=t.ink("muted"), width=1)
        if threshold.get("label"):
            canvas.text(x, height - 2, str(threshold["label"]), size=8.5,
                        fill=t.ink("muted"), anchor="middle")
    return canvas.render()
