"""Change over time: line, area, sparkline, timeline.

The rule that matters most here is the one people break most: **one axis**.
Two measures of different scale become two charts, small multiples, or both
indexed to 100 at t0, never two y-scales on one plot, which invents a
correlation the data does not contain.
"""

from __future__ import annotations

from . import chrome, svg
from .theme import Ctx
from .blocks_quantity import formatter


def _series_of(b: dict):
    if b.get("series"):
        return [(str(s.get("name", f"Series {i + 1}")), [None if v is None else float(v)
                                                         for v in s.get("values", [])])
                for i, s in enumerate(b["series"])]
    return [(str(b.get("series_name", "Value")),
             [None if v is None else float(v) for v in b.get("values", [])])]


def _index_to_100(series):
    out = []
    for name, values in series:
        base = next((v for v in values if v), None) or 1.0
        out.append((name, [None if v is None else v / base * 100.0 for v in values]))
    return out


def line(b: dict, ctx: Ctx) -> str:
    """Trend over time. Markers appear only when the series is short enough that
    every point is a real observation the reader may want to locate."""
    t = ctx.theme
    x_values = [str(x) for x in b.get("x", [])]
    series = _series_of(b)
    fmt = formatter(b)
    indexed = bool(b.get("index_to_100"))
    if indexed:
        series = _index_to_100(series)
        fmt = lambda v: svg.fmt_plain(v, 0)  # noqa: E731

    if not x_values and series:
        x_values = [str(i + 1) for i in range(len(series[0][1]))]
    height = float(b.get("height", 260))
    area = bool(b.get("area"))
    stacked = bool(b.get("stacked")) and len(series) > 1

    if stacked:
        totals = [sum((s[1][i] or 0) for s in series) for i in range(len(x_values))]
        lo, hi = svg.extent(totals)
    else:
        flat = [v for _, vals in series for v in vals if v is not None]
        lo, hi = svg.extent(flat, pad=0.06,
                            include_zero=bool(b.get("zero", not indexed)))
    ticks = svg.nice_ticks(lo, hi, 5)
    axis_w = chrome.measure_labels([fmt(v) for v in ticks], 9.5) + 12

    plot = chrome.Plot(ctx, height, left=axis_w, right=b.get("right_pad", 46), top=14, bottom=32)
    canvas = svg.Canvas(ctx.width, height, t)
    sy = svg.Linear(min(ticks), max(ticks), plot.y1, plot.y0)
    sx = svg.Linear(0, max(len(x_values) - 1, 1), plot.x0, plot.x1)
    chrome.value_grid(canvas, ctx, sy, ticks, plot.x0, plot.x1, fmt=fmt)

    colors = chrome.series_colors(ctx, len(series), b.get("emphasis_index"), b.get("palette"))
    if b.get("emphasis") is not None:
        names = [s[0] for s in series]
        idx = names.index(b["emphasis"]) if b["emphasis"] in names else None
        if idx is not None:
            colors = [t.accent if i == idx else t.deemphasis for i in range(len(series))]

    if stacked:
        cursor = [0.0] * len(x_values)
        for si, (name, values) in enumerate(series):
            upper, lower = [], []
            for i, value in enumerate(values):
                base = cursor[i]
                top = base + (value or 0)
                upper.append((sx(i), sy(top)))
                lower.append((sx(i), sy(base)))
                cursor[i] = top
            canvas.path(svg.polyline_path(upper + list(reversed(lower)), close=True),
                        fill=t.wash(colors[si], 0.9))
            canvas.path(svg.polyline_path(upper), stroke=colors[si],
                        width=t.geom("line_width", 2))
    else:
        for si, (name, values) in enumerate(series):
            points = [(sx(i), sy(v)) for i, v in enumerate(values) if v is not None]
            if not points:
                continue
            if area and len(series) == 1:
                closed = points + [(points[-1][0], sy(min(ticks))), (points[0][0], sy(min(ticks)))]
                canvas.path(svg.polyline_path(closed, close=True),
                            fill=t.wash(colors[si], 0.10))
            canvas.path(svg.polyline_path(points), stroke=colors[si],
                        width=t.geom("line_width", 2))
            if len(points) <= 14 and b.get("markers", True):
                for px, py in points:
                    canvas.circle(px, py, t.geom("marker_radius", 4.5) - 0.5, colors[si],
                                  stroke=t.surface("card"), width=2)
            if b.get("end_labels", len(series) <= 4):
                last = points[-1]
                canvas.text(last[0] + 9, last[1] + 3.4,
                            fmt(values[-1]) if values[-1] is not None else "", size=10,
                            weight=600, fill=t.ink("primary"))

    chrome.baseline(canvas, ctx, plot.x0, plot.x1, plot.y1)
    step = max(1, len(x_values) // max(int(plot.inner_w // 62), 1))
    for i, label in enumerate(x_values):
        if i % step and i != len(x_values) - 1:
            continue
        canvas.text(sx(i), plot.y1 + 17, label, size=9.5, fill=t.ink("muted"), anchor="middle")

    out = [canvas.render()]
    if len(series) > 1:
        out.append(chrome.legend_html(ctx, [(s[0], colors[i]) for i, s in enumerate(series)],
                                      shape="line"))
    if b.get("table", True):
        cols = [b.get("x_label", "Period")] + [s[0] for s in series]
        rows = [[x_values[i]] + [fmt(s[1][i]) if i < len(s[1]) and s[1][i] is not None else ", "
                                 for s in series] for i in range(len(x_values))]
        out.append(chrome.details_table(cols, rows))
    return "".join(out)


def area(b: dict, ctx: Ctx) -> str:
    payload = dict(b)
    payload["area"] = True
    if len(payload.get("series", [])) > 1:
        payload["stacked"] = payload.get("stacked", True)
    return line(payload, ctx)


def sparkline_svg(values, ctx: Ctx, width=110.0, height=30.0, color=None,
                  highlight_last=True) -> str:
    """A 12-point trend that lives inside a stat tile. No axes, no labels, it
    carries shape only; the tile's value carries the number."""
    t = ctx.theme
    numbers = [float(v) for v in values if v is not None]
    if len(numbers) < 2:
        return ""
    canvas = svg.Canvas(width, height, t)
    lo, hi = min(numbers), max(numbers)
    sy = svg.Linear(lo, hi if hi != lo else lo + 1, height - 4, 4)
    sx = svg.Linear(0, len(numbers) - 1, 2, width - 4)
    points = [(sx(i), sy(v)) for i, v in enumerate(numbers)]
    canvas.path(svg.polyline_path(points + [(points[-1][0], height), (points[0][0], height)],
                                  close=True),
                fill=t.wash(color or t.deemphasis, 0.10))
    canvas.path(svg.polyline_path(points), stroke=color or t.deemphasis, width=1.8)
    if highlight_last:
        canvas.circle(points[-1][0], points[-1][1], 3.2, color or t.accent,
                      stroke=t.surface("card"), width=1.6)
    return canvas.render()


# --------------------------------------------------------------- timeline ----

def timeline(b: dict, ctx: Ctx) -> str:
    """Events in sequence. Vertical by default: it takes real prose per event,
    survives a page break, and never crowds labels the way a horizontal axis does.
    Use horizontal only for short labels and a genuinely spatial span."""
    t = ctx.theme
    events = b.get("events", [])
    orientation = b.get("orientation", "vertical")

    if orientation == "horizontal":
        return _timeline_horizontal(b, ctx, events)

    rail_x = 78.0
    body_w = ctx.width - rail_x - 18
    title_size, text_size, date_size = 12.5, 10.5, 10
    laid, y = [], 10.0
    for event in events:
        title_lines = svg.wrap(str(event.get("title", "")), title_size, body_w, 600, 2)
        text_lines = svg.wrap(str(event.get("text", "")), text_size, body_w) if event.get("text") else []
        block_h = (len(title_lines) * title_size * 1.28
                   + (len(text_lines) * text_size * 1.45 + 4 if text_lines else 0))
        laid.append((y, title_lines, text_lines, event))
        y += block_h + float(b.get("gap", 22))
    height = y + 4

    canvas = svg.Canvas(ctx.width, height, t)
    canvas.line(rail_x, 12, rail_x, height - 16, stroke=t.rule("border"), width=1.5)

    for i, (top, title_lines, text_lines, event) in enumerate(laid):
        color = t.accent if event.get("emphasis") else t.series(0)
        if b.get("ordinal"):
            color = t.ordinal(i, len(laid))
        canvas.circle(rail_x, top + 6, 5.5, t.surface("card"), stroke=color, width=2.5)
        if event.get("done"):
            canvas.circle(rail_x, top + 6, 2.6, color)
        canvas.text(rail_x - 16, top + 9.5, str(event.get("date", "")), size=date_size,
                    weight=600, fill=t.ink("muted"), anchor="end")
        canvas.text_lines(rail_x + 18, top + 10, title_lines, size=title_size, weight=600,
                          fill=t.ink("primary"), line_height=1.28)
        if text_lines:
            canvas.text_lines(rail_x + 18,
                              top + 10 + len(title_lines) * title_size * 1.28 + 6,
                              text_lines, size=text_size, fill=t.ink("secondary"),
                              line_height=1.45)
    return canvas.render()


def _timeline_horizontal(b: dict, ctx: Ctx, events) -> str:
    t = ctx.theme
    height = float(b.get("height", 168))
    rail_y = 64.0
    pad = 26.0
    canvas = svg.Canvas(ctx.width, height, t)
    canvas.line(pad, rail_y, ctx.width - pad, rail_y, stroke=t.rule("border"), width=1.5)
    if not events:
        return canvas.render()
    step = (ctx.width - pad * 2) / max(len(events) - 1, 1) if len(events) > 1 else 0
    slot = (ctx.width - pad * 2) / max(len(events), 1)
    for i, event in enumerate(events):
        x = pad + (step * i if len(events) > 1 else (ctx.width - pad * 2) / 2)
        color = t.ordinal(i, len(events)) if b.get("ordinal") else (
            t.accent if event.get("emphasis") else t.series(0))
        canvas.circle(x, rail_y, 6, t.surface("card"), stroke=color, width=2.5)
        canvas.text(x, rail_y - 22, str(event.get("date", "")), size=10.5, weight=600,
                    fill=t.ink("muted"), anchor="middle")
        title_lines = svg.wrap(str(event.get("title", "")), 11.5, slot * 0.94, 600, 2)
        canvas.text_lines(x, rail_y + 24, title_lines, size=11.5, weight=600,
                          fill=t.ink("primary"), anchor="middle", line_height=1.25)
        if event.get("text"):
            text_lines = svg.wrap(str(event["text"]), 9.5, slot * 0.94, max_lines=2)
            canvas.text_lines(x, rail_y + 24 + len(title_lines) * 11.5 * 1.25 + 6,
                              text_lines, size=9.5, fill=t.ink("secondary"),
                              anchor="middle", line_height=1.35)
    return canvas.render()
