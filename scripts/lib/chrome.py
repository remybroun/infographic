"""Chart chrome: the parts that are the same on every plot.

Grid and axes are recessive by contract, hairline, solid, one step off the
surface. Dashing is banned: it reads as "projection" or "threshold" when it is
just a grid. Legends are HTML rather than SVG so they wrap, reflow across a
page break, and stay selectable text in the PDF.
"""

from __future__ import annotations

from . import svg
from .theme import Ctx


# ------------------------------------------------------------------ layout ---

class Plot:
    """Inner plotting rectangle after margins are reserved for axis labels."""

    def __init__(self, ctx: Ctx, height: float, left=0.0, right=0.0, top=0.0, bottom=0.0):
        self.ctx = ctx
        self.width = ctx.width
        self.height = float(height)
        self.left, self.right, self.top, self.bottom = left, right, top, bottom

    @property
    def x0(self): return self.left

    @property
    def x1(self): return self.width - self.right

    @property
    def y0(self): return self.top

    @property
    def y1(self): return self.height - self.bottom

    @property
    def inner_w(self): return max(self.x1 - self.x0, 1.0)

    @property
    def inner_h(self): return max(self.y1 - self.y0, 1.0)


def measure_labels(labels, size=10.5, weight=400, cap=None) -> float:
    widest = max((svg.text_width(str(l), size, weight) for l in labels), default=0.0)
    return min(widest, cap) if cap else widest


# ------------------------------------------------------------------- axes ----

def value_grid(canvas, ctx: Ctx, scale, ticks, x0, x1, fmt=svg.fmt_plain,
               label_side="left", label_gap=8, size=9.5, show_labels=True,
               zero_emphasis=True):
    """Horizontal gridlines with right-aligned tick labels (for column charts)."""
    t = ctx.theme
    for tick in ticks:
        y = scale(tick)
        is_zero = abs(tick) < 1e-9 and zero_emphasis
        canvas.line(x0, y, x1, y,
                    stroke=t.rule("axis") if is_zero else t.rule("grid"),
                    width=1, shape_rendering="crispEdges")
        if show_labels:
            if label_side == "left":
                canvas.text(x0 - label_gap, y + 3.4, fmt(tick), size=size,
                            fill=t.ink("muted"), anchor="end",
                            font_variant_numeric="tabular-nums")
            else:
                canvas.text(x1 + label_gap, y + 3.4, fmt(tick), size=size,
                            fill=t.ink("muted"), anchor="start",
                            font_variant_numeric="tabular-nums")


def value_grid_vertical(canvas, ctx: Ctx, scale, ticks, y0, y1, fmt=svg.fmt_plain,
                        size=9.5, show_labels=True, zero_emphasis=True):
    """Vertical gridlines with labels under the plot (for bar charts)."""
    t = ctx.theme
    for tick in ticks:
        x = scale(tick)
        is_zero = abs(tick) < 1e-9 and zero_emphasis
        canvas.line(x, y0, x, y1,
                    stroke=t.rule("axis") if is_zero else t.rule("grid"),
                    width=1, shape_rendering="crispEdges")
        if show_labels:
            canvas.text(x, y1 + 14, fmt(tick), size=size, fill=t.ink("muted"),
                        anchor="middle", font_variant_numeric="tabular-nums")


def category_axis(canvas, ctx: Ctx, band, labels, y, size=10, max_width=None, rotate=False):
    """Category labels under a column chart. Wraps to two lines before it
    considers rotating, because rotated labels cost more reading effort than a
    horizontal chart does."""
    t = ctx.theme
    limit = max_width or band.bandwidth + band.step * 0.2
    for i, label in enumerate(labels):
        cx = band.center(i)
        if rotate:
            canvas.add(
                f'<text transform="rotate(-38 {svg.num(cx)} {svg.num(y)})" '
                f'x="{svg.num(cx)}" y="{svg.num(y)}" font-size="{svg.num(size)}" '
                f'fill="{svg.esc(t.ink("secondary"))}" text-anchor="end">{svg.esc(label)}</text>'
            )
        else:
            lines = svg.wrap(str(label), size, limit, max_lines=2)
            canvas.text_lines(cx, y, lines, size=size, fill=t.ink("secondary"),
                              anchor="middle", line_height=1.25)


def baseline(canvas, ctx: Ctx, x0, x1, y):
    canvas.line(x0, y, x1, y, stroke=ctx.theme.rule("axis"), width=1,
                shape_rendering="crispEdges")


# ----------------------------------------------------------------- legend ----

def legend_html(ctx: Ctx, items, shape="rect", compact=False) -> str:
    """items: [(label, color)] or [(label, color, texture_angle)].

    A legend is always present for two or more series, and never for one, with
    a single color the title already says what is plotted, and a one-swatch box
    just restates it.
    """
    if len(items) < 2:
        return ""
    t = ctx.theme
    cells = []
    for item in items:
        label, color = item[0], item[1]
        if shape == "line":
            mark = (f'<span class="ig-key ig-key-line" style="background:{svg.esc(color)}">'
                    f"</span>")
        elif shape == "dot":
            mark = (f'<span class="ig-key ig-key-dot" style="background:{svg.esc(color)}">'
                    f"</span>")
        else:
            mark = (f'<span class="ig-key ig-key-rect" style="background:{svg.esc(color)}">'
                    f"</span>")
        cells.append(f'<li class="ig-legend-item">{mark}<span>{svg.esc(label)}</span></li>')
    cls = "ig-legend ig-legend-compact" if compact else "ig-legend"
    return f'<ul class="{cls}">{"".join(cells)}</ul>'


def scale_legend_html(ctx: Ctx, low_label, high_label, steps=7, alt=False,
                      diverging=False, mid_label=None) -> str:
    """A continuous ramp needs a scale legend, not a categorical one."""
    t = ctx.theme
    swatches = []
    for i in range(steps):
        pos = i / (steps - 1)
        color = t.diverging(pos * 2 - 1) if diverging else t.sequential(pos, alt)
        swatches.append(f'<span style="background:{svg.esc(color)}"></span>')
    mid = f'<span class="ig-scale-mid">{svg.esc(mid_label)}</span>' if mid_label else ""
    return (
        f'<div class="ig-scale-legend">'
        f'<span class="ig-scale-label">{svg.esc(low_label)}</span>'
        f'<span class="ig-scale-ramp">{"".join(swatches)}</span>'
        f"{mid}"
        f'<span class="ig-scale-label">{svg.esc(high_label)}</span>'
        f"</div>"
    )


# ------------------------------------------------------------- table view ----

def table_html(columns, rows, align=None, caption=None, cls="ig-table-view") -> str:
    """The WCAG-clean twin of a chart. Every value a mark encodes must be
    reachable here, so no value is gated behind color or a tooltip."""
    align = align or []

    def cell_align(i):
        return align[i] if i < len(align) else ("right" if i else "left")

    head = "".join(
        f'<th scope="col" style="text-align:{cell_align(i)}">{svg.esc(c)}</th>'
        for i, c in enumerate(columns)
    )
    body = []
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            tag = "th" if i == 0 else "td"
            scope = ' scope="row"' if i == 0 else ""
            cells.append(
                f'<{tag}{scope} style="text-align:{cell_align(i)}">{svg.esc(value)}</{tag}>'
            )
        body.append(f"<tr>{''.join(cells)}</tr>")
    cap = f"<caption>{svg.esc(caption)}</caption>" if caption else ""
    return (f'<table class="{cls}">{cap}<thead><tr>{head}</tr></thead>'
            f"<tbody>{''.join(body)}</tbody></table>")


def details_table(columns, rows, label="Show the numbers", align=None) -> str:
    """Collapsed in screen HTML, force-open in print (see document.css)."""
    return (f'<details class="ig-table-toggle"><summary>{svg.esc(label)}</summary>'
            f"{table_html(columns, rows, align)}</details>")


# ------------------------------------------------------------------ misc -----

def note_line(ctx: Ctx, text: str) -> str:
    return f'<p class="ig-note">{svg.esc(text)}</p>' if text else ""


def value_label_fits(text, size, available, padding=12.0, weight=600) -> bool:
    return svg.text_width(str(text), size, weight) + padding <= available


def ordinal_color(ctx: Ctx, index: int, total: int, reverse: bool = False) -> str:
    """A step from the one-hue ordinal ramp.

    `reverse` puts the dark end at the START of the sequence. Use it when the
    first category is the significant one (largest, earliest, most severe), otherwise a light bar sits next to the biggest number and reads as "less",
    which is the ramp fighting the data instead of describing it.
    """
    position = (total - 1 - index) if reverse else index
    return ctx.theme.ordinal(position, total)


def series_colors(ctx: Ctx, count: int, emphasis=None, palette=None):
    """Resolve series colors, honoring an explicit palette or an emphasis index.

    Emphasis is the most underused form: one series in the accent hue and the
    rest in the de-emphasis gray. When `emphasis` is set we do exactly that.
    """
    t = ctx.theme
    if palette:
        return [palette[i % len(palette)] for i in range(count)]
    if emphasis is not None:
        return [t.accent if i == emphasis else t.deemphasis for i in range(count)]
    if count > t.series_count():
        ctx.warn(
            f"{count} series exceeds the {t.series_count()}-slot categorical palette. "
            "Fold the tail into 'Other', facet into small multiples, or switch form, "
            "never generate a ninth hue."
        )
    return [t.series(i) for i in range(count)]
