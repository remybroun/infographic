"""Editorial blocks: the prose, figures and framing that carry the argument.

An infographic that is all charts explains nothing. These blocks are where the
*claim* lives, the chart beside them is evidence. Most of them emit HTML rather
than SVG so the text stays selectable, reflowable and searchable in the PDF.
"""

from __future__ import annotations

import html
import re

from . import chrome, svg
from .blocks_time import sparkline_svg
from .theme import Ctx

_INLINE = (
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])"), r"<em>\1</em>"),
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
    (re.compile(r"\[(.+?)\]\((https?://[^)\s]+)\)"), r'<a href="\2">\1</a>'),
)


def inline(text) -> str:
    """Escape first, then re-enable a tiny inline subset. Order matters: doing
    it the other way round would let source text inject markup."""
    out = html.escape(str(text or ""), quote=False)
    for pattern, replacement in _INLINE:
        out = pattern.sub(replacement, out)
    return out


def _paragraphs(text) -> str:
    if isinstance(text, list):
        chunks = [str(t) for t in text]
    else:
        chunks = [c for c in re.split(r"\n\s*\n", str(text or "")) if c.strip()]
    return "".join(f"<p>{inline(c.strip())}</p>" for c in chunks)


# ------------------------------------------------------------------- hero ----

def hero(b: dict, ctx: Ctx) -> str:
    """The cover. One idea, stated as a claim rather than a topic, "Retention
    is a pricing problem" beats "Retention overview"."""
    parts = []
    if b.get("kicker"):
        parts.append(f'<p class="ig-kicker">{inline(b["kicker"])}</p>')
    parts.append(f'<h1 class="ig-hero-title">{inline(b.get("title", ""))}</h1>')
    if b.get("subtitle"):
        parts.append(f'<p class="ig-hero-subtitle">{inline(b["subtitle"])}</p>')
    if b.get("lede"):
        parts.append(f'<div class="ig-hero-lede">{_paragraphs(b["lede"])}</div>')
    if b.get("stats"):
        parts.append(kpi({"items": b["stats"], "compact": True}, ctx))
    meta = []
    for key in ("author", "date", "source"):
        if b.get(key):
            meta.append(inline(b[key]))
    if meta:
        parts.append(f'<p class="ig-hero-meta">{" · ".join(meta)}</p>')
    tone = b.get("tone", "plain")
    return f'<header class="ig-hero ig-hero-{svg.esc(tone)}">{"".join(parts)}</header>'


def section(b: dict, ctx: Ctx) -> str:
    """A section opener. Numbers only when the sequence itself is information
    the reader needs, never as decoration."""
    parts = []
    if b.get("number"):
        parts.append(f'<span class="ig-section-number">{inline(b["number"])}</span>')
    if b.get("kicker"):
        parts.append(f'<p class="ig-kicker">{inline(b["kicker"])}</p>')
    parts.append(f'<h2 class="ig-section-title">{inline(b.get("title", ""))}</h2>')
    if b.get("lede"):
        parts.append(f'<p class="ig-section-lede">{inline(b["lede"])}</p>')
    return f'<div class="ig-section-head">{"".join(parts)}</div>'


def heading(b: dict, ctx: Ctx) -> str:
    level = int(b.get("level", 3))
    return f'<h{level} class="ig-heading">{inline(b.get("text", b.get("title", "")))}</h{level}>'


def prose(b: dict, ctx: Ctx) -> str:
    body = _paragraphs(b.get("text", b.get("body", "")))
    cls = "ig-prose ig-prose-lead" if b.get("lead") else "ig-prose"
    if b.get("columns", 1) > 1:
        cls += f" ig-cols-{int(b['columns'])}"
    return f'<div class="{cls}">{body}</div>'


def bullets(b: dict, ctx: Ctx) -> str:
    tag = "ol" if b.get("ordered") else "ul"
    items = "".join(f"<li>{inline(i)}</li>" for i in b.get("items", []))
    return f'<{tag} class="ig-bullets">{items}</{tag}>'


def quote(b: dict, ctx: Ctx) -> str:
    attribution = (f'<footer class="ig-quote-attr">{inline(b["attribution"])}</footer>'
                   if b.get("attribution") else "")
    return (f'<blockquote class="ig-quote"><p>{inline(b.get("text", ""))}</p>'
            f"{attribution}</blockquote>")


def callout(b: dict, ctx: Ctx) -> str:
    """One of: key, note, warn, danger. The tone maps to a status color and an
    icon, never to color alone."""
    tone = b.get("tone", "key")
    icons = {"key": "◆", "note": "i", "warn": "!", "danger": "!"}
    title = (f'<p class="ig-callout-title">{inline(b["title"])}</p>' if b.get("title") else "")
    return (f'<aside class="ig-callout ig-callout-{svg.esc(tone)}">'
            f'<span class="ig-callout-icon" aria-hidden="true">{svg.esc(icons.get(tone, "◆"))}</span>'
            f'<div>{title}{_paragraphs(b.get("text", ""))}</div></aside>')


# ------------------------------------------------------------------ stats ----

def _delta_html(item, ctx: Ctx):
    if item.get("delta") is None:
        return ""
    value = float(item["delta"])
    up_is_good = item.get("up_is_good", True)
    good = (value >= 0) == bool(up_is_good)
    arrow = "↑" if value > 0 else ("↓" if value < 0 else "→")
    cls = "up" if good else "down"
    unit = item.get("delta_unit", "%")
    period = f' <span class="ig-delta-period">{inline(item["delta_period"])}</span>' \
        if item.get("delta_period") else ""
    # The arrow carries direction, so the number is an unsigned magnitude. Doing
    # both invites "↓ +14.2%", where the glyph and the sign contradict each
    # other and the reader has to guess which one is lying.
    decimals = int(item.get("delta_decimals", 1))
    magnitude = f"{abs(value):.{decimals}f}".rstrip("0").rstrip(".")
    return (f'<span class="ig-delta ig-delta-{cls}">{svg.esc(arrow)} '
            f'{svg.esc(magnitude + unit)}</span>{period}')


def stat(b: dict, ctx: Ctx) -> str:
    """label · value · optional delta · optional sparkline. The number IS the
    chart, never draw a one-bar bar chart instead of this."""
    t = ctx.theme
    value = b.get("value")
    if isinstance(value, (int, float)):
        text = svg.fmt_compact(value, int(b.get("decimals", 1)), b.get("currency", ""),
                               b.get("unit", "")) if b.get("compact", True) \
            else svg.fmt_plain(value, int(b.get("decimals", 0)), b.get("currency", ""),
                               b.get("unit", ""))
    else:
        text = str(value if value is not None else ", ")
    spark = ""
    if b.get("trend"):
        spark = f'<div class="ig-spark">{sparkline_svg(b["trend"], ctx, color=t.accent)}</div>'
    note = f'<p class="ig-stat-note">{inline(b["note"])}</p>' if b.get("note") else ""

    # Fit the figure to the tile in Python rather than hoping CSS copes. A value
    # that does not fit must get SMALLER, never wrap: `overflow-wrap` on a big
    # number stacks it one character per line, which is the worst of both.
    base = float(ctx.opt("stat_size", 30.8))
    available = max(ctx.width - 40.0, 40.0)
    size = base
    while size > 13.0 and svg.text_width(text, size, 650) > available:
        size -= 1.0
    style = f' style="font-size:{svg.num(size)}px"' if size < base - 0.5 else ""

    return (f'<div class="ig-stat">'
            f'<p class="ig-stat-label">{inline(b.get("label", ""))}</p>'
            f'<p class="ig-stat-value"{style}>{svg.esc(text)}</p>'
            f'<p class="ig-stat-delta">{_delta_html(b, ctx)}</p>'
            f"{spark}{note}</div>")


MIN_TILE_PX = 132.0


def kpi(b: dict, ctx: Ctx) -> str:
    """A row of stat tiles. Three or four; past that it stops being a headline
    and becomes a table.

    The column count is decided here, in Python, from the block's real width, CSS cannot know how wide a grid column is without container queries, and a
    four-tile row squeezed into a 4-span column is how big numbers end up
    colliding with each other in print.
    """
    items = b.get("items", [])
    if len(items) > 5:
        ctx.warn("more than 5 KPI tiles in a row stops reading as headlines. "
                 "Keep 3-4 and move the rest to a table.")
    count = len(items) or 1
    columns = max(1, min(count, int(ctx.width // MIN_TILE_PX) or 1))
    if columns < count:
        ctx.warn(f"{count} KPI tiles will not fit across {ctx.width:.0f}px; "
                 f"laid out {columns} per row. Widen the block's span or use fewer tiles.")
    cells = "".join(f"<li>{stat(i, ctx.sub(ctx.width / columns))}</li>" for i in items)
    cls = "ig-kpi ig-kpi-compact" if b.get("compact") or columns == 1 else "ig-kpi"
    if columns == 1:
        cls += " ig-kpi-stacked"
    return f'<ul class="{cls}" style="--ig-kpi-n:{columns}">{cells}</ul>'


def hero_figure(b: dict, ctx: Ctx) -> str:
    """The single number a page leads with. Exactly one per view, in the same
    sans as everything else, a serif here reads as off-brand decoration."""
    value = b.get("value")
    text = svg.fmt_compact(value, int(b.get("decimals", 1)), b.get("currency", ""),
                           b.get("unit", "")) if isinstance(value, (int, float)) else str(value)
    note = f'<p class="ig-hero-figure-note">{inline(b["note"])}</p>' if b.get("note") else ""
    return (f'<div class="ig-hero-figure">'
            f'<p class="ig-hero-figure-value">{svg.esc(text)}</p>'
            f'<p class="ig-hero-figure-label">{inline(b.get("label", ""))}</p>'
            f"{note}</div>")


# ------------------------------------------------------------------ table ----

def table(b: dict, ctx: Ctx) -> str:
    columns = [str(c) for c in b.get("columns", [])]
    rows = [[("" if c is None else c) for c in row] for row in b.get("rows", [])]
    return chrome.table_html(columns, rows, b.get("align"), b.get("caption"),
                             cls="ig-table")


def checklist(b: dict, ctx: Ctx) -> str:
    """Do / don't. Two columns of concrete instructions, never abstractions."""
    def column(kind, title, items):
        cells = "".join(f'<li><span aria-hidden="true">{"✓" if kind == "do" else "✕"}</span>'
                        f"<span>{inline(i)}</span></li>" for i in items)
        return (f'<div class="ig-check ig-check-{kind}">'
                f'<p class="ig-check-title">{inline(title)}</p>'
                f"<ul>{cells}</ul></div>")

    return (f'<div class="ig-checklist">'
            f'{column("do", b.get("do_title", "Do"), b.get("do", []))}'
            f'{column("dont", b.get("dont_title", "Don\'t"), b.get("dont", []))}'
            f"</div>")


DEF_TILE_PX = 168.0


def definitions(b: dict, ctx: Ctx) -> str:
    """Terms the reader may not share.

    At graphic density this is a tile grid, not a two-column list. The list form
    invites a sentence per term and stacks into a wall; tiles cap each entry at
    roughly a line and put the terms side by side, where they read as a
    vocabulary rather than as prose with bold lead-ins.
    """
    items = b.get("items", [])
    rows = "".join(
        f'<div class="ig-def"><dt>{inline(i.get("term", ""))}</dt>'
        f'<dd>{inline(i.get("text", ""))}</dd></div>'
        for i in items
    )
    if not ctx.graphic or b.get("layout") == "list":
        return f'<dl class="ig-definitions">{rows}</dl>'
    from .blocks_diagram import balanced_columns
    columns = balanced_columns(len(items), ctx.width, DEF_TILE_PX)
    return (f'<dl class="ig-definitions ig-definitions-grid" '
            f'style="--ig-def-n:{columns}">{rows}</dl>')


def comparison(b: dict, ctx: Ctx) -> str:
    """Two framings side by side, old vs new, myth vs fact, A vs B. The
    asymmetry is deliberate: the right-hand side is the one you are arguing for."""
    t = ctx.theme

    def side(data, kind):
        points = "".join(f"<li>{inline(p)}</li>" for p in data.get("points", []))
        return (f'<div class="ig-compare-side ig-compare-{kind}">'
                f'<p class="ig-compare-label">{inline(data.get("label", ""))}</p>'
                f'<p class="ig-compare-headline">{inline(data.get("headline", ""))}</p>'
                f"<ul>{points}</ul></div>")

    return (f'<div class="ig-compare">{side(b.get("left", {}), "left")}'
            f'<div class="ig-compare-vs" aria-hidden="true">{svg.esc(b.get("vs", "vs"))}</div>'
            f'{side(b.get("right", {}), "right")}</div>')


def image(b: dict, ctx: Ctx) -> str:
    caption = f'<figcaption>{inline(b["caption"])}</figcaption>' if b.get("caption") else ""
    fit = b.get("fit", "cover")
    ratio = b.get("ratio", "16/9")
    return (f'<figure class="ig-image" style="aspect-ratio:{svg.esc(ratio)}">'
            f'<img src="{svg.esc(b.get("src", ""))}" alt="{svg.esc(b.get("alt", ""))}" '
            f'style="object-fit:{svg.esc(fit)}"/>{caption}</figure>')


def footnotes(b: dict, ctx: Ctx) -> str:
    items = "".join(f"<li>{inline(i)}</li>" for i in b.get("items", []))
    title = f'<p class="ig-footnotes-title">{inline(b.get("title", "Sources & method"))}</p>'
    return f'<div class="ig-footnotes">{title}<ol>{items}</ol></div>'


def divider(b: dict, ctx: Ctx) -> str:
    return '<hr class="ig-divider"/>'


def spacer(b: dict, ctx: Ctx) -> str:
    return f'<div class="ig-spacer" style="height:{float(b.get("height", 24))}px"></div>'


def raw(b: dict, ctx: Ctx) -> str:
    """Escape hatch for anything the catalog does not cover. Use it rarely and
    only after checking the catalog, an unregistered one-off cannot be
    re-themed, validated, or given a table view."""
    return str(b.get("html", ""))
