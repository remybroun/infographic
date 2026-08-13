"""Quantity, comparison and change: the blocks that answer "how much".

Every renderer here obeys the same four rules:
  * one axis, never two y-scales;
  * bars are capped at 24px and rounded only at the data end;
  * a 2px surface gap does the separating, never a stroke around a mark;
  * labels are selective, the endpoint, the extreme, the series that matters.
"""

from __future__ import annotations

from . import chrome, svg
from .theme import Ctx


# ------------------------------------------------------------------ shared ---

def resolve_series(b: dict):
    """Normalize the two accepted shapes into (categories, [(name, values)])."""
    categories = [str(c) for c in b.get("categories", [])]
    if "series" in b and b["series"]:
        series = [(str(s.get("name", f"Series {i + 1}")), list(s.get("values", [])))
                  for i, s in enumerate(b["series"])]
    elif "items" in b:
        categories = [str(i.get("label", "")) for i in b["items"]]
        series = [(str(b.get("series_name", b.get("value_label", "Value"))),
                   [i.get("value") for i in b["items"]])]
    else:
        series = [(str(b.get("series_name", b.get("value_label", "Value"))),
                   list(b.get("values", [])))]
    if not categories and series:
        categories = [f"{i + 1}" for i in range(len(series[0][1]))]
    return categories, series


def formatter(b: dict):
    currency = b.get("currency", "")
    unit = b.get("unit", "")
    decimals = int(b.get("decimals", 0))
    compact = bool(b.get("compact", False))

    def fmt(value):
        if value is None:
            return ", "
        if compact:
            return svg.fmt_compact(value, max(decimals, 1), currency, unit)
        return svg.fmt_plain(value, decimals, currency, unit)

    return fmt


def emphasis_index(b: dict, categories):
    emph = b.get("emphasis")
    if emph is None:
        return None
    if isinstance(emph, int):
        return emph
    return categories.index(str(emph)) if str(emph) in categories else None


def _sorted_pairs(categories, values, order):
    pairs = list(zip(categories, values))
    if order == "desc":
        pairs.sort(key=lambda p: (p[1] is None, -(p[1] or 0)))
    elif order == "asc":
        pairs.sort(key=lambda p: (p[1] is None, p[1] or 0))
    return [p[0] for p in pairs], [p[1] for p in pairs]


# --------------------------------------------------------------------- bar ---

def bar(b: dict, ctx: Ctx) -> str:
    """Horizontal bars. The default for magnitude comparison, it takes long
    category names without rotating anything, which columns cannot."""
    t = ctx.theme
    categories, series = resolve_series(b)
    fmt = formatter(b)
    values = [v or 0 for v in series[0][1]]
    if b.get("sort"):
        categories, values = _sorted_pairs(categories, values, b["sort"])

    label_size, value_size = 10.5, 10.5
    label_w = min(chrome.measure_labels(categories, label_size) + 12, ctx.width * 0.38)
    value_w = chrome.measure_labels([fmt(v) for v in values], value_size, 600) + 14
    thickness = min(t.geom("bar_max_thickness", 24), b.get("thickness", 24))
    row_h = thickness + max(10, thickness * 0.55)
    height = len(categories) * row_h + 26

    plot = chrome.Plot(ctx, height, left=label_w, right=value_w, top=4, bottom=22)
    canvas = svg.Canvas(ctx.width, height, t)

    lo, hi = svg.extent(values, pad=0.0)
    ticks = svg.nice_ticks(lo, hi, 4)
    scale = svg.Linear(min(ticks), max(ticks), plot.x0, plot.x1)
    chrome.value_grid_vertical(canvas, ctx, scale, ticks, plot.y0, plot.y1, fmt=fmt,
                               show_labels=b.get("axis", True))

    emph = emphasis_index(b, categories)
    ordinal = bool(b.get("ordinal"))
    zero = scale(0)

    for i, (label, value) in enumerate(zip(categories, values)):
        y = plot.y0 + i * row_h + (row_h - thickness) / 2
        x = scale(value)
        if ordinal:
            color = chrome.ordinal_color(ctx, i, len(categories), b.get("ordinal_reverse", False))
        elif emph is not None:
            color = t.accent if i == emph else t.deemphasis
        else:
            color = t.series(0)
        left, width = (zero, x - zero) if value >= 0 else (x, zero - x)
        canvas.bar(left, y, width, thickness, color,
                   r=t.geom("radius", 4), end="right" if value >= 0 else "left")
        canvas.text(plot.x0 - 10, y + thickness / 2 + 3.6, svg.truncate(label, label_size, label_w - 12),
                    size=label_size, fill=t.ink("secondary"), anchor="end")
        if b.get("value_labels", True):
            canvas.text(x + (7 if value >= 0 else -7), y + thickness / 2 + 3.8, fmt(value),
                        size=value_size, weight=600, fill=t.ink("primary"),
                        anchor="start" if value >= 0 else "end")

    chrome.baseline(canvas, ctx, plot.x0, plot.x0, plot.y1) if False else None
    canvas.line(zero, plot.y0, zero, plot.y1, stroke=t.rule("axis"), width=1,
                shape_rendering="crispEdges")

    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            [b.get("category_label", "Category"), b.get("value_label", "Value")],
            [[c, fmt(v)] for c, v in zip(categories, values)]))
    return "".join(out)


# ------------------------------------------------------------------ column ---

def column(b: dict, ctx: Ctx) -> str:
    """Vertical bars. Use when the x axis is genuinely ordered, time, stages,
    buckets. For nominal names, `bar` reads better."""
    t = ctx.theme
    categories, series = resolve_series(b)
    fmt = formatter(b)
    grouped = len(series) > 1 and not b.get("stacked")
    stacked = bool(b.get("stacked")) and len(series) > 1

    colors = chrome.series_colors(ctx, len(series), emphasis_index(b, [s[0] for s in series]),
                                  b.get("palette"))
    height = float(b.get("height", 250))
    label_size = 10
    axis_fmt = fmt
    if stacked:
        totals = [sum((s[1][i] or 0) for s in series) for i in range(len(categories))]
        lo, hi = svg.extent(totals)
    else:
        flat = [v for _, vals in series for v in vals if v is not None]
        lo, hi = svg.extent(flat)
    ticks = svg.nice_ticks(lo, hi, 5)
    axis_w = chrome.measure_labels([axis_fmt(x) for x in ticks], 9.5) + 12
    cat_lines = max(len(svg.wrap(c, label_size, ctx.width / max(len(categories), 1) * 0.95, max_lines=2))
                    for c in categories) if categories else 1
    bottom = 16 + cat_lines * label_size * 1.25

    plot = chrome.Plot(ctx, height, left=axis_w, right=6, top=12, bottom=bottom)
    canvas = svg.Canvas(ctx.width, height, t)
    scale = svg.Linear(min(ticks), max(ticks), plot.y1, plot.y0)
    chrome.value_grid(canvas, ctx, scale, ticks, plot.x0, plot.x1, fmt=axis_fmt)

    band = svg.Band(len(categories), plot.x0, plot.x1, padding=b.get("padding", 0.32))
    gap = t.geom("surface_gap", 2)
    radius = t.geom("radius", 4)
    zero = scale(0)

    if grouped:
        inner = svg.Band(len(series), 0, band.bandwidth, padding=0.12)
        thickness = min(inner.bandwidth, t.geom("bar_max_thickness", 24))
        for si, (name, values) in enumerate(series):
            for i, value in enumerate(values):
                if value is None:
                    continue
                x = band(i) + inner(si) + (inner.bandwidth - thickness) / 2
                y = scale(value)
                canvas.bar(x, min(y, zero), thickness, abs(zero - y), colors[si],
                           r=radius, end="top" if value >= 0 else "bottom")
    elif stacked:
        thickness = min(band.bandwidth, t.geom("bar_max_thickness", 24) * 1.6)
        for i in range(len(categories)):
            cursor = 0.0
            x = band.center(i) - thickness / 2
            parts = [(si, series[si][1][i] or 0) for si in range(len(series))]
            for order, (si, value) in enumerate(parts):
                if value <= 0:
                    continue
                y_top = scale(cursor + value)
                y_bot = scale(cursor)
                seg_h = max(y_bot - y_top - (gap if order < len(parts) - 1 else 0), 0.5)
                is_top = order == len(parts) - 1
                canvas.bar(x, y_top, thickness, seg_h, colors[si],
                           r=radius if is_top else 0, end="top" if is_top else "none")
                cursor += value
    else:
        thickness = min(band.bandwidth, t.geom("bar_max_thickness", 24))
        emph = emphasis_index(b, categories)
        ordinal = bool(b.get("ordinal"))
        for i, value in enumerate(series[0][1]):
            if value is None:
                continue
            x = band.center(i) - thickness / 2
            y = scale(value)
            if ordinal:
                color = chrome.ordinal_color(ctx, i, len(categories), b.get("ordinal_reverse", False))
            elif emph is not None:
                color = t.accent if i == emph else t.deemphasis
            else:
                color = colors[0]
            canvas.bar(x, min(y, zero), thickness, abs(zero - y), color,
                       r=radius, end="top" if value >= 0 else "bottom")
            if b.get("value_labels", len(categories) <= 8):
                canvas.text(band.center(i), min(y, zero) - 7, fmt(value), size=10,
                            weight=600, fill=t.ink("primary"), anchor="middle")

    chrome.baseline(canvas, ctx, plot.x0, plot.x1, zero)
    chrome.category_axis(canvas, ctx, band, categories, plot.y1 + 16, size=label_size,
                         rotate=bool(b.get("rotate_labels")))

    out = [canvas.render()]
    if len(series) > 1:
        out.append(chrome.legend_html(ctx, [(s[0], colors[i]) for i, s in enumerate(series)]))
    if b.get("table", True):
        cols = [b.get("category_label", "Category")] + [s[0] for s in series]
        rows = [[categories[i]] + [fmt(s[1][i] if i < len(s[1]) else None) for s in series]
                for i in range(len(categories))]
        out.append(chrome.details_table(cols, rows))
    return "".join(out)


# --------------------------------------------------------------- lollipop ----

def lollipop(b: dict, ctx: Ctx) -> str:
    """A bar chart on a diet. Use when there are many categories and the bar
    mass would dominate the page, or when values cluster far from zero."""
    t = ctx.theme
    categories, series = resolve_series(b)
    fmt = formatter(b)
    values = [v or 0 for v in series[0][1]]
    if b.get("sort", "desc"):
        categories, values = _sorted_pairs(categories, values, b.get("sort", "desc"))

    label_w = min(chrome.measure_labels(categories, 10.5) + 12, ctx.width * 0.38)
    value_w = chrome.measure_labels([fmt(v) for v in values], 10.5, 600) + 16
    row_h = float(b.get("row_height", 24))
    height = len(categories) * row_h + 24

    plot = chrome.Plot(ctx, height, left=label_w, right=value_w, top=6, bottom=18)
    canvas = svg.Canvas(ctx.width, height, t)
    lo, hi = svg.extent(values)
    ticks = svg.nice_ticks(lo, hi, 4)
    scale = svg.Linear(min(ticks), max(ticks), plot.x0, plot.x1)
    chrome.value_grid_vertical(canvas, ctx, scale, ticks, plot.y0, plot.y1, fmt=fmt)

    emph = emphasis_index(b, categories)
    zero = scale(0)
    for i, (label, value) in enumerate(zip(categories, values)):
        y = plot.y0 + i * row_h + row_h / 2
        color = t.accent if emph is None or i == emph else t.deemphasis
        canvas.line(zero, y, scale(value), y, stroke=color, width=2, cap="round")
        canvas.circle(scale(value), y, t.geom("marker_radius", 4.5) + 1, color,
                      stroke=t.surface("card"), width=2)
        canvas.text(plot.x0 - 10, y + 3.6, svg.truncate(label, 10.5, label_w - 12),
                    size=10.5, fill=t.ink("secondary"), anchor="end")
        canvas.text(scale(value) + 10, y + 3.6, fmt(value), size=10.5, weight=600,
                    fill=t.ink("primary"), anchor="start")

    canvas.line(zero, plot.y0, zero, plot.y1, stroke=t.rule("axis"), width=1)
    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            [b.get("category_label", "Category"), b.get("value_label", "Value")],
            [[c, fmt(v)] for c, v in zip(categories, values)]))
    return "".join(out)


# --------------------------------------------------------------- dumbbell ----

def dumbbell(b: dict, ctx: Ctx) -> str:
    """Before → after per item. The gap between the dots IS the message, which
    is why this beats two grouped bars: the reader sees change, not two heights."""
    t = ctx.theme
    items = b.get("items", [])
    fmt = formatter(b)
    from_label = b.get("from_label", "Before")
    to_label = b.get("to_label", "After")
    labels = [str(i.get("label", "")) for i in items]

    label_w = min(chrome.measure_labels(labels, 10.5) + 12, ctx.width * 0.34)
    value_w = 78.0
    row_h = float(b.get("row_height", 30))
    height = len(items) * row_h + 30

    plot = chrome.Plot(ctx, height, left=label_w, right=value_w, top=8, bottom=22)
    canvas = svg.Canvas(ctx.width, height, t)
    flat = [v for i in items for v in (i.get("from"), i.get("to")) if v is not None]
    lo, hi = svg.extent(flat, pad=0.08, include_zero=bool(b.get("zero", False)))
    ticks = svg.nice_ticks(lo, hi, 4)
    scale = svg.Linear(min(ticks), max(ticks), plot.x0, plot.x1)
    chrome.value_grid_vertical(canvas, ctx, scale, ticks, plot.y0, plot.y1, fmt=fmt)

    c_from = t.deemphasis if b.get("gray_start", True) else t.series(0)
    c_to = t.accent
    r = t.geom("marker_radius", 4.5) + 1

    for i, item in enumerate(items):
        y = plot.y0 + i * row_h + row_h / 2
        v0, v1 = item.get("from"), item.get("to")
        if v0 is None or v1 is None:
            continue
        x0, x1 = scale(v0), scale(v1)
        canvas.line(x0, y, x1, y, stroke=t.rule("axis"), width=2, cap="round")
        canvas.circle(x0, y, r, c_from, stroke=t.surface("card"), width=2)
        canvas.circle(x1, y, r, c_to, stroke=t.surface("card"), width=2)
        canvas.text(plot.x0 - 10, y + 3.6, svg.truncate(labels[i], 10.5, label_w - 12),
                    size=10.5, fill=t.ink("secondary"), anchor="end")
        delta = v1 - v0
        canvas.text(plot.x1 + 10, y + 3.6, svg.fmt_delta(delta, 1, b.get("unit", "")),
                    size=10, weight=600, anchor="start",
                    fill=t.status("good_text") if delta >= 0 else t.status("critical_text"))

    out = [canvas.render(),
           chrome.legend_html(ctx, [(from_label, c_from), (to_label, c_to)], shape="dot")]
    if b.get("table", True):
        out.append(chrome.details_table(
            [b.get("category_label", "Item"), from_label, to_label, "Change"],
            [[str(i.get("label", "")), fmt(i.get("from")), fmt(i.get("to")),
              svg.fmt_delta((i.get("to") or 0) - (i.get("from") or 0), 1, b.get("unit", ""))]
             for i in items]))
    return "".join(out)


# ------------------------------------------------------------------ slope ----

def slope(b: dict, ctx: Ctx) -> str:
    """Two time points, many items. Shows rank change and rate of change at once, the one form where crossing lines are the point rather than a defect."""
    t = ctx.theme
    items = b.get("items", [])
    fmt = formatter(b)
    from_label, to_label = b.get("from_label", "Start"), b.get("to_label", "End")
    height = float(b.get("height", 300))

    left_w = min(chrome.measure_labels([str(i.get("label", "")) for i in items], 10.5) + 58,
                 ctx.width * 0.3)
    right_w = left_w
    plot = chrome.Plot(ctx, height, left=left_w, right=right_w, top=34, bottom=18)
    canvas = svg.Canvas(ctx.width, height, t)

    flat = [v for i in items for v in (i.get("from"), i.get("to")) if v is not None]
    lo, hi = svg.extent(flat, pad=0.1, include_zero=False)
    scale = svg.Linear(lo, hi, plot.y1, plot.y0)

    canvas.line(plot.x0, plot.y0, plot.x0, plot.y1, stroke=t.rule("grid"), width=1)
    canvas.line(plot.x1, plot.y0, plot.x1, plot.y1, stroke=t.rule("grid"), width=1)
    canvas.text(plot.x0, plot.y0 - 14, from_label, size=10, weight=600,
                fill=t.ink("muted"), anchor="middle")
    canvas.text(plot.x1, plot.y0 - 14, to_label, size=10, weight=600,
                fill=t.ink("muted"), anchor="middle")

    highlight = b.get("emphasis")
    for i, item in enumerate(items):
        v0, v1 = item.get("from"), item.get("to")
        if v0 is None or v1 is None:
            continue
        label = str(item.get("label", ""))
        on = (highlight is None) or (label == str(highlight)) or (i == highlight)
        color = t.accent if on and highlight is not None else (
            t.series(i) if highlight is None else t.deemphasis)
        y0, y1 = scale(v0), scale(v1)
        canvas.line(plot.x0, y0, plot.x1, y1, stroke=color, width=2 if on else 1.4,
                    cap="round", opacity=None if on else 0.75)
        canvas.circle(plot.x0, y0, 3.6, color)
        canvas.circle(plot.x1, y1, 3.6, color)
        canvas.text(plot.x0 - 9, y0 + 3.4, f"{label}  {fmt(v0)}", size=9.8,
                    fill=t.ink("secondary") if on else t.ink("muted"), anchor="end")
        canvas.text(plot.x1 + 9, y1 + 3.4, f"{fmt(v1)}  {label}", size=9.8,
                    fill=t.ink("secondary") if on else t.ink("muted"), anchor="start")

    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Item", from_label, to_label],
            [[str(i.get("label", "")), fmt(i.get("from")), fmt(i.get("to"))] for i in items]))
    return "".join(out)


# -------------------------------------------------------------- diverging ----

def diverging(b: dict, ctx: Ctx) -> str:
    """Above / below a baseline. The midpoint must read as nothing, so the
    neutral is gray and the two poles are warm vs cool."""
    t = ctx.theme
    items = b.get("items", [])
    fmt = formatter(b)
    labels = [str(i.get("label", "")) for i in items]
    values = [float(i.get("value") or 0) for i in items]
    if b.get("sort", "desc"):
        labels, values = _sorted_pairs(labels, values, b.get("sort", "desc"))

    label_w = min(chrome.measure_labels(labels, 10.5) + 12, ctx.width * 0.32)
    thickness = min(t.geom("bar_max_thickness", 24), 20)
    row_h = thickness + 12
    height = len(items) * row_h + 34

    plot = chrome.Plot(ctx, height, left=label_w, right=54, top=6, bottom=24)
    canvas = svg.Canvas(ctx.width, height, t)
    span = max((abs(v) for v in values), default=1)
    ticks = svg.nice_ticks(-span, span, 4)
    scale = svg.Linear(min(ticks), max(ticks), plot.x0, plot.x1)
    chrome.value_grid_vertical(canvas, ctx, scale, ticks, plot.y0, plot.y1, fmt=fmt)

    zero = scale(0)
    for i, (label, value) in enumerate(zip(labels, values)):
        y = plot.y0 + i * row_h + (row_h - thickness) / 2
        x = scale(value)
        color = t.diverging(value / span if span else 0)
        left, width = (zero, x - zero) if value >= 0 else (x, zero - x)
        canvas.bar(left, y, max(width, 1.5), thickness, color,
                   r=t.geom("radius", 4), end="right" if value >= 0 else "left")
        canvas.text(plot.x0 - 10, y + thickness / 2 + 3.6,
                    svg.truncate(label, 10.5, label_w - 12), size=10.5,
                    fill=t.ink("secondary"), anchor="end")
        canvas.text(x + (7 if value >= 0 else -7), y + thickness / 2 + 3.6, fmt(value),
                    size=10, weight=600, fill=t.ink("primary"),
                    anchor="start" if value >= 0 else "end")

    canvas.line(zero, plot.y0, zero, plot.y1, stroke=t.rule("axis"), width=1)
    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Item", b.get("value_label", "Change")],
            [[l, fmt(v)] for l, v in zip(labels, values)]))
    return "".join(out)


# ----------------------------------------------------------------- likert ----

def likert(b: dict, ctx: Ctx) -> str:
    """Ordered-scale share, centred on the neutral point. Never a grouped bar:
    the reader must see agree and disagree grow away from a shared middle."""
    t = ctx.theme
    scale_labels = b.get("scale", ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"])
    items = b.get("items", [])
    n = len(scale_labels)
    mid = (n - 1) / 2.0
    colors = [t.diverging((i - mid) / mid if mid else 0) for i in range(n)]

    labels = [str(i.get("label", "")) for i in items]
    label_w = min(chrome.measure_labels(labels, 10.5) + 12, ctx.width * 0.34)
    thickness = 20
    row_h = thickness + 12
    height = len(items) * row_h + 26

    plot = chrome.Plot(ctx, height, left=label_w, right=10, top=6, bottom=18)
    canvas = svg.Canvas(ctx.width, height, t)
    gap = t.geom("surface_gap", 2)

    for i, item in enumerate(items):
        values = [float(v or 0) for v in item.get("values", [])]
        total = sum(values) or 1.0
        shares = [v / total for v in values]
        # centre on the middle of the neutral bucket
        before = sum(shares[:n // 2]) + (shares[n // 2] / 2 if n % 2 else 0)
        y = plot.y0 + i * row_h + (row_h - thickness) / 2
        origin = plot.x0 + plot.inner_w * 0.5 - before * plot.inner_w * 0.92
        cursor = origin
        for si, share in enumerate(shares):
            w = share * plot.inner_w * 0.92
            seg = max(w - (gap if si < n - 1 else 0), 0.5)
            canvas.bar(cursor, y, seg, thickness, colors[si],
                       r=t.geom("radius", 4) if si in (0, n - 1) else 0,
                       end="left" if si == 0 else ("right" if si == n - 1 else "none"))
            pct = f"{share * 100:.0f}%"
            if share > 0.001 and chrome.value_label_fits(pct, 9.5, seg, 10):
                canvas.text(cursor + seg / 2, y + thickness / 2 + 3.3, pct, size=9.5,
                            weight=600, fill=t.ink_on(colors[si]), anchor="middle")
            cursor += w
        canvas.text(plot.x0 - 10, y + thickness / 2 + 3.6,
                    svg.truncate(labels[i], 10.5, label_w - 12), size=10.5,
                    fill=t.ink("secondary"), anchor="end")

    canvas.line(plot.x0 + plot.inner_w * 0.5, plot.y0 - 2, plot.x0 + plot.inner_w * 0.5,
                plot.y1, stroke=t.rule("axis"), width=1)

    out = [canvas.render(),
           chrome.legend_html(ctx, list(zip(scale_labels, colors)))]
    if b.get("table", True):
        rows = [[str(i.get("label", ""))] + [f"{v}" for v in i.get("values", [])] for i in items]
        out.append(chrome.details_table(["Item"] + list(scale_labels), rows))
    return "".join(out)


# ---------------------------------------------------------------- scatter ----

def scatter(b: dict, ctx: Ctx) -> str:
    """Two measures per item. All-pairs colour separation binds here: cap at
    three series and fold the rest, rather than seating a fourth hue."""
    t = ctx.theme
    points = b.get("points", [])
    height = float(b.get("height", 300))
    fmt_x = svg.fmt_plain
    fmt_y = svg.fmt_plain

    names = []
    for p in points:
        name = p.get("series")
        if name and name not in names:
            names.append(name)
    if len(names) > 3:
        ctx.warn("scatter with more than 3 series: any two marks can sit side by side, "
                 "so all-pairs separation binds. Fold to 'Other' or facet into small multiples.")
    colors = chrome.series_colors(ctx, max(len(names), 1), palette=b.get("palette"))

    xs = [float(p.get("x", 0)) for p in points]
    ys = [float(p.get("y", 0)) for p in points]
    xt = svg.nice_ticks(*svg.extent(xs, 0.08, include_zero=bool(b.get("zero_x", False))), 5)
    yt = svg.nice_ticks(*svg.extent(ys, 0.08, include_zero=bool(b.get("zero_y", False))), 5)
    axis_w = chrome.measure_labels([fmt_y(v) for v in yt], 9.5) + 12

    plot = chrome.Plot(ctx, height, left=axis_w, right=14, top=12, bottom=40)
    canvas = svg.Canvas(ctx.width, height, t)
    sx = svg.Linear(min(xt), max(xt), plot.x0, plot.x1)
    sy = svg.Linear(min(yt), max(yt), plot.y1, plot.y0)
    chrome.value_grid(canvas, ctx, sy, yt, plot.x0, plot.x1, fmt=fmt_y)
    chrome.value_grid_vertical(canvas, ctx, sx, xt, plot.y0, plot.y1, fmt=fmt_x)

    for p in points:
        ci = names.index(p["series"]) if p.get("series") in names else 0
        color = colors[min(ci, len(colors) - 1)]
        r = float(p.get("r", t.geom("marker_radius", 4.5) + 0.5))
        canvas.circle(sx(float(p.get("x", 0))), sy(float(p.get("y", 0))), r, color,
                      stroke=t.surface("card"), width=2)
        if p.get("label") and b.get("point_labels", True):
            canvas.text(sx(float(p.get("x", 0))) + r + 5,
                        sy(float(p.get("y", 0))) + 3.2, str(p["label"]), size=9,
                        fill=t.ink("secondary"))

    if b.get("x_label"):
        canvas.text((plot.x0 + plot.x1) / 2, height - 6, b["x_label"], size=9.5,
                    weight=600, fill=t.ink("muted"), anchor="middle")
    if b.get("y_label"):
        canvas.add(f'<text transform="rotate(-90 12 {svg.num((plot.y0 + plot.y1) / 2)})" '
                   f'x="12" y="{svg.num((plot.y0 + plot.y1) / 2)}" font-size="9.5" '
                   f'font-weight="600" fill="{svg.esc(t.ink("muted"))}" '
                   f'text-anchor="middle">{svg.esc(b["y_label"])}</text>')

    out = [canvas.render()]
    if len(names) > 1:
        out.append(chrome.legend_html(ctx, list(zip(names, colors)), shape="dot"))
    if b.get("table", True):
        out.append(chrome.details_table(
            ["Point", b.get("x_label", "X"), b.get("y_label", "Y")],
            [[str(p.get("label", "")), fmt_x(p.get("x")), fmt_y(p.get("y"))] for p in points]))
    return "".join(out)


# ---------------------------------------------------------------- heatmap ----

def heatmap(b: dict, ctx: Ctx) -> str:
    """A grid of magnitude. Sequential single hue only, a rainbow grid is
    unreadable and a diverging grid needs a real baseline."""
    t = ctx.theme
    rows = b.get("rows", [])
    cols = b.get("cols", [])
    values = b.get("values", [])
    fmt = formatter(b)
    flat = [v for row in values for v in row if v is not None]
    lo = float(b.get("min", min(flat) if flat else 0))
    hi = float(b.get("max", max(flat) if flat else 1))
    span = (hi - lo) or 1.0

    label_w = min(chrome.measure_labels([str(r) for r in rows], 10) + 12, ctx.width * 0.3)
    head_h = 26.0
    cell_w = (ctx.width - label_w - 4) / max(len(cols), 1)
    cell_h = float(b.get("cell_height", min(max(cell_w * 0.62, 22), 40)))
    height = head_h + len(rows) * cell_h + 8
    canvas = svg.Canvas(ctx.width, height, t)
    gap = t.geom("surface_gap", 2)

    for ci, col in enumerate(cols):
        canvas.text(label_w + ci * cell_w + cell_w / 2, head_h - 10,
                    svg.truncate(str(col), 9.5, cell_w - 4), size=9.5,
                    weight=600, fill=t.ink("muted"), anchor="middle")

    for ri, row in enumerate(rows):
        y = head_h + ri * cell_h
        canvas.text(label_w - 10, y + cell_h / 2 + 3.4,
                    svg.truncate(str(row), 10, label_w - 12), size=10,
                    fill=t.ink("secondary"), anchor="end")
        for ci in range(len(cols)):
            value = values[ri][ci] if ri < len(values) and ci < len(values[ri]) else None
            x = label_w + ci * cell_w
            if value is None:
                canvas.rect(x, y, cell_w - gap, cell_h - gap, t.surface("sunken"),
                            r=t.geom("radius", 4) / 2)
                continue
            color = t.sequential((float(value) - lo) / span, alt=bool(b.get("alt_hue")))
            canvas.rect(x, y, cell_w - gap, cell_h - gap, color, r=t.geom("radius", 4) / 2)
            if b.get("cell_labels", True):
                text = fmt(value)
                if chrome.value_label_fits(text, 9.5, cell_w - gap, 8):
                    canvas.text(x + (cell_w - gap) / 2, y + cell_h / 2 + 3.3, text,
                                size=9.5, weight=600, fill=t.ink_on(color), anchor="middle")

    out = [canvas.render(),
           chrome.scale_legend_html(ctx, fmt(lo), fmt(hi), alt=bool(b.get("alt_hue")))]
    if b.get("table", True):
        out.append(chrome.details_table(
            [b.get("row_label", "")] + [str(c) for c in cols],
            [[str(rows[ri])] + [fmt(values[ri][ci]) if ri < len(values) and ci < len(values[ri]) else ", "
                                for ci in range(len(cols))] for ri in range(len(rows))]))
    return "".join(out)
