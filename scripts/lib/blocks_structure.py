"""Structure and relation: how things connect, not how much there is.

These are the blocks that make an infographic explain a *concept* rather than
report a number. Most concept documents need more of these than they need
charts, and the commonest failure is reaching for a bar chart when the claim is
actually a sequence, a hierarchy, or a trade-off.
"""

from __future__ import annotations

import math

from . import chrome, svg
from .theme import Ctx


# ---------------------------------------------------------------- process ----

def process(b: dict, ctx: Ctx) -> str:
    """A linear sequence with a direction. Horizontal while the steps are few
    and short; vertical as soon as each step carries real prose, because
    stacking keeps the measure readable and survives a page break."""
    t = ctx.theme
    steps = b.get("steps", b.get("items", []))
    if not steps:
        return ""
    longest = max((len(str(s.get("text", ""))) for s in steps), default=0)
    orientation = b.get("orientation") or ("vertical" if len(steps) > 4 or longest > 90 else "horizontal")
    numbered = b.get("numbered", True)

    if orientation == "vertical":
        return _process_vertical(b, ctx, steps, numbered)

    n = len(steps)
    gap = 30.0
    col_w = (ctx.width - gap * (n - 1)) / n
    title_size, text_size = 12, 10
    laid = []
    for step in steps:
        title_lines = svg.wrap(str(step.get("title", "")), title_size, col_w - 24, 600, 2)
        text_lines = svg.wrap(str(step.get("text", "")), text_size, col_w - 24, max_lines=5) \
            if step.get("text") else []
        laid.append((title_lines, text_lines))
    body_h = max(len(tl) * title_size * 1.25 + len(xl) * text_size * 1.45 for tl, xl in laid)
    card_h = 46 + body_h
    height = card_h + 8
    canvas = svg.Canvas(ctx.width, height, t)

    for i, (step, (title_lines, text_lines)) in enumerate(zip(steps, laid)):
        x = i * (col_w + gap)
        color = t.ordinal(i, n) if b.get("ordinal", True) else t.series(0)
        canvas.rect(x, 4, col_w, card_h, t.wash(color, 0.10), r=t.geom("radius", 4) * 2)
        canvas.bar(x, 4, col_w, 3, color, r=0, end="none")
        if numbered:
            canvas.circle(x + 18, 30, 11, color)
            canvas.text(x + 18, 34, str(i + 1), size=11.5, weight=700,
                        fill=t.ink_on(color), anchor="middle")
        tx = x + (36 if numbered else 12)
        canvas.text_lines(tx, 34, title_lines, size=title_size, weight=600,
                          fill=t.ink("primary"), line_height=1.25)
        if text_lines:
            canvas.text_lines(x + 12, 34 + len(title_lines) * title_size * 1.25 + 12,
                              text_lines, size=text_size, fill=t.ink("secondary"),
                              line_height=1.45)
        if i < n - 1:
            canvas.add(svg.arrow_marker(x + col_w + gap / 2 - 4, 4 + card_h / 2, 11,
                                        "right", t.rule("axis")))
    return canvas.render()


def _process_vertical(b: dict, ctx: Ctx, steps, numbered) -> str:
    t = ctx.theme
    n = len(steps)
    rail_x = 22.0
    body_x = rail_x + 28
    body_w = ctx.width - body_x - 6
    title_size, text_size = 12.5, 10.5
    laid, y = [], 6.0
    for step in steps:
        title_lines = svg.wrap(str(step.get("title", "")), title_size, body_w, 600, 2)
        text_lines = svg.wrap(str(step.get("text", "")), text_size, body_w) if step.get("text") else []
        h = len(title_lines) * title_size * 1.28 + (len(text_lines) * text_size * 1.45 + 5 if text_lines else 0)
        laid.append((y, title_lines, text_lines, h))
        y += h + 24
    height = y
    canvas = svg.Canvas(ctx.width, height, t)

    for i, (step, (top, title_lines, text_lines, h)) in enumerate(zip(steps, laid)):
        color = t.ordinal(i, n) if b.get("ordinal", True) else t.series(0)
        if i < n - 1:
            canvas.line(rail_x, top + 24, rail_x, laid[i + 1][0] + 2,
                        stroke=t.rule("border"), width=1.5)
        canvas.circle(rail_x, top + 11, 11, color)
        canvas.text(rail_x, top + 15, str(i + 1) if numbered else "",
                    size=11.5, weight=700, fill=t.ink_on(color), anchor="middle")
        canvas.text_lines(body_x, top + 15, title_lines, size=title_size, weight=600,
                          fill=t.ink("primary"), line_height=1.28)
        if text_lines:
            canvas.text_lines(body_x, top + 15 + len(title_lines) * title_size * 1.28 + 7,
                              text_lines, size=text_size, fill=t.ink("secondary"),
                              line_height=1.45)
    return canvas.render()


# ------------------------------------------------------------------ cycle ----

def cycle(b: dict, ctx: Ctx) -> str:
    """A process with no end. The closing arrow is the whole point, if the last
    step does not feed the first, this is a `process`, not a cycle."""
    t = ctx.theme
    steps = b.get("steps", b.get("items", []))
    n = len(steps)
    if n < 3:
        ctx.warn("cycle with fewer than 3 steps reads as a two-way arrow, not a loop.")
    wanted = float(b.get("size", 380))
    size = min(ctx.width, wanted)
    height = size
    cx, cy = ctx.width / 2, size / 2
    ring_r = size * 0.30
    node_r = min(size * 0.115, 52)
    # A ring is the one form here whose height IS its width, so a narrow column
    # does not make it shorter, it makes it illegible: the node radius falls with
    # the column and the label text does not. The tell is not that the ring is
    # small, it is that the column squeezed it below the size it asked for, so
    # that is what this measures. At a half column on A4 the result is a 326px
    # square holding 38px nodes with three-line labels, and nothing in the
    # payload hints at it, because `size` reads like a control rather than a
    # ceiling.
    if ctx.width < wanted:
        ctx.warn(
            f"cycle asked for {wanted:.0f}px and the column is {ctx.width:.0f}px, "
            f"so it renders as a {size:.0f}px-tall square with {node_r:.0f}px "
            f"nodes and the labels will not fit. A cycle wants a full-width span. "
            f"Narrower than that, a `process` says the same sequence and reads at "
            f"any width.")
    canvas = svg.Canvas(ctx.width, height, t)

    canvas.circle(cx, cy, ring_r, "none", stroke=t.rule("border"), width=1.5)
    for i in range(n):
        a0 = (360.0 / n) * i + 16
        a1 = (360.0 / n) * (i + 1) - 16
        mid = math.radians(a1 - 90)
        canvas.path(svg.arc_path(cx, cy, ring_r + 1, ring_r - 1, a0, a1),
                    fill=t.rule("axis"))
        canvas.add(svg.arrow_marker(cx + ring_r * math.cos(mid), cy + ring_r * math.sin(mid),
                                    9, "right", t.rule("axis")))

    for i, step in enumerate(steps):
        angle = math.radians((360.0 / n) * i - 90)
        x, y = cx + ring_r * math.cos(angle), cy + ring_r * math.sin(angle)
        color = t.ordinal(i, n)
        canvas.circle(x, y, node_r, color, stroke=t.surface("card"), width=4)
        title = str(step.get("title", step.get("label", "")))
        lines = svg.wrap(title, 10.5, node_r * 1.75, 600, 3)
        canvas.text_lines(x, y - (len(lines) - 1) * 6.5 + 3.5, lines, size=10.5,
                          weight=600, fill=t.ink_on(color), anchor="middle",
                          line_height=1.24)

    if b.get("center_label"):
        lines = svg.wrap(str(b["center_label"]), 12, ring_r * 1.1, 600, 3)
        canvas.text_lines(cx, cy - (len(lines) - 1) * 7 + 4, lines, size=12, weight=600,
                          fill=t.ink("secondary"), anchor="middle", line_height=1.3)
    return canvas.render()


# --------------------------------------------------------------- quadrant ----

def quadrant(b: dict, ctx: Ctx) -> str:
    """Two independent axes turning into four named positions. The value is the
    naming: an unlabelled 2x2 is a scatter plot with extra lines."""
    t = ctx.theme
    items = b.get("items", [])
    size = float(b.get("height", 340))
    pad_l, pad_b, pad_t, pad_r = 46.0, 40.0, 14.0, 14.0
    canvas = svg.Canvas(ctx.width, size, t)
    x0, x1 = pad_l, ctx.width - pad_r
    y0, y1 = pad_t, size - pad_b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2

    quads = b.get("quadrants", [])
    tints = [0.06, 0.06, 0.06, 0.10]
    boxes = [(x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1)]
    for i, (bx0, by0, bx1, by1) in enumerate(boxes):
        label = quads[i] if i < len(quads) else None
        fill = t.wash(t.accent, tints[i % len(tints)]) if label and label.get("highlight") \
            else t.surface("sunken")
        canvas.rect(bx0 + 1, by0 + 1, bx1 - bx0 - 2, by1 - by0 - 2, fill,
                    r=t.geom("radius", 4))
        if label:
            canvas.text(bx0 + 12, by0 + 20, str(label.get("label", "")), size=10.5,
                        weight=700, fill=t.ink("muted"),
                        tracking="0.06em")

    canvas.line(x0, my, x1, my, stroke=t.rule("axis"), width=1)
    canvas.line(mx, y0, mx, y1, stroke=t.rule("axis"), width=1)

    for i, item in enumerate(items):
        px = x0 + (x1 - x0) * max(0.0, min(1.0, float(item.get("x", 0.5))))
        py = y1 - (y1 - y0) * max(0.0, min(1.0, float(item.get("y", 0.5))))
        color = t.accent if item.get("emphasis") else t.series(0)
        canvas.circle(px, py, t.geom("marker_radius", 4.5) + 1.5, color,
                      stroke=t.surface("card"), width=2)
        label = str(item.get("label", ""))
        anchor = "end" if px > mx else "start"
        canvas.text(px + (-9 if anchor == "end" else 9), py + 3.4,
                    svg.truncate(label, 10, (x1 - x0) / 2 - 20), size=10,
                    weight=600, fill=t.ink("secondary"), anchor=anchor)

    canvas.text((x0 + x1) / 2, size - 8, str(b.get("x_label", "")), size=10,
                weight=600, fill=t.ink("muted"), anchor="middle")
    canvas.add(f'<text transform="rotate(-90 14 {svg.num((y0 + y1) / 2)})" x="14" '
               f'y="{svg.num((y0 + y1) / 2)}" font-size="10" font-weight="600" '
               f'fill="{svg.esc(t.ink("muted"))}" text-anchor="middle">'
               f'{svg.esc(b.get("y_label", ""))}</text>')
    canvas.text(x0, size - 8, str(b.get("x_low", "")), size=9, fill=t.ink("muted"))
    canvas.text(x1, size - 8, str(b.get("x_high", "")), size=9, fill=t.ink("muted"),
                anchor="end")
    return canvas.render()


# ------------------------------------------------------------------- venn ----

def venn(b: dict, ctx: Ctx) -> str:
    """Overlapping membership, two or three sets. Four sets cannot be drawn
    honestly with circles, that is a matrix."""
    t = ctx.theme
    sets = b.get("sets", [])
    if len(sets) > 3:
        ctx.warn("venn with more than 3 sets cannot be drawn to scale with circles. "
                 "Use a comparison matrix instead.")
        sets = sets[:3]
    size = float(b.get("height", 300))
    canvas = svg.Canvas(ctx.width, size, t)
    cx, cy = ctx.width / 2, size * 0.47
    r = min(size * 0.30, ctx.width * 0.26)

    if len(sets) == 2:
        centers = [(cx - r * 0.56, cy), (cx + r * 0.56, cy)]
    else:
        centers = [(cx, cy - r * 0.50), (cx - r * 0.56, cy + r * 0.36),
                   (cx + r * 0.56, cy + r * 0.36)]

    for i, (s, (px, py)) in enumerate(zip(sets, centers)):
        color = t.series(i)
        canvas.circle(px, py, r, t.wash(color, 0.30), stroke=color, width=1.6)

    for i, (s, (px, py)) in enumerate(zip(sets, centers)):
        dx = px - cx
        dy = py - cy
        lx = px + (dx / abs(dx) if dx else 0) * r * 0.55
        ly = py + (dy / abs(dy) if dy else -1) * r * 0.62
        lines = svg.wrap(str(s.get("label", "")), 11.5, r * 1.1, 700, 2)
        canvas.text_lines(lx, ly, lines, size=11.5, weight=700, fill=t.ink("primary"),
                          anchor="middle", line_height=1.2)

    if b.get("overlap"):
        lines = svg.wrap(str(b["overlap"]), 10.5, r * 0.95, 600, 3)
        oy = cy if len(sets) == 2 else cy + r * 0.18
        canvas.text_lines(cx, oy - (len(lines) - 1) * 6.5 + 3.5, lines, size=10.5,
                          weight=600, fill=t.ink("primary"), anchor="middle",
                          line_height=1.25)
    return canvas.render()


# ------------------------------------------------------------------- tree ----

def _tree_layout(node, depth, cursor, nodes, edges, leaf_w):
    children = node.get("children", [])
    if not children:
        x = cursor[0] * leaf_w + leaf_w / 2
        cursor[0] += 1
    else:
        xs = []
        for child in children:
            xs.append(_tree_layout(child, depth + 1, cursor, nodes, edges, leaf_w))
        x = (min(xs) + max(xs)) / 2
    nodes.append((x, depth, node))
    for child_x in ([] if not children else [n[0] for n in nodes if n[2] in children]):
        edges.append((x, depth, child_x, depth + 1))
    return x


def tree(b: dict, ctx: Ctx) -> str:
    """Hierarchy: what contains or reports to what. Depth is the message, so
    keep it to three levels, past that a nested list outperforms a drawing."""
    t = ctx.theme
    root = b.get("root")
    if not root:
        return ""

    def count_leaves(node):
        children = node.get("children", [])
        return sum(count_leaves(c) for c in children) if children else 1

    def depth_of(node):
        children = node.get("children", [])
        return 1 + max((depth_of(c) for c in children), default=0)

    leaves = count_leaves(root)
    depth = depth_of(root)
    leaf_w = ctx.width / max(leaves, 1)
    level_h = float(b.get("level_height", 84))
    height = depth * level_h
    canvas = svg.Canvas(ctx.width, height, t)

    placed = {}

    def place(node, level, cursor):
        children = node.get("children", [])
        if children:
            xs = [place(c, level + 1, cursor) for c in children]
            x = (min(xs) + max(xs)) / 2
        else:
            x = cursor[0] * leaf_w + leaf_w / 2
            cursor[0] += 1
        placed[id(node)] = (x, level)
        return x

    place(root, 0, [0])

    def draw_edges(node):
        x, level = placed[id(node)]
        for child in node.get("children", []):
            cx_, cl = placed[id(child)]
            y0 = level * level_h + 34
            y1 = cl * level_h + 8
            midy = (y0 + y1) / 2
            canvas.path(f"M{svg.num(x)},{svg.num(y0)}V{svg.num(midy)}"
                        f"H{svg.num(cx_)}V{svg.num(y1)}",
                        stroke=t.rule("border"), width=1.4)
            draw_edges(child)

    draw_edges(root)

    def draw_nodes(node, level=0):
        x, lvl = placed[id(node)]
        label = str(node.get("label", ""))
        box_w = min(leaf_w * max(count_leaves(node), 1) - 12, float(b.get("node_width", 150)))
        box_w = max(box_w, 74)
        lines = svg.wrap(label, 10.5, box_w - 14, 600, 2)
        box_h = 18 + len(lines) * 13
        color = t.ordinal(lvl, max(depth, 2))
        y = lvl * level_h + 8
        filled = lvl == 0 or node.get("emphasis")
        canvas.rect(x - box_w / 2, y, box_w, box_h,
                    color if filled else t.wash(color, 0.14),
                    r=t.geom("radius", 4) * 1.5,
                    stroke=None if filled else color, stroke_width=None if filled else 1)
        canvas.text_lines(x, y + 15, lines, size=10.5, weight=600,
                          fill=t.ink_on(color) if filled else t.ink("primary"),
                          anchor="middle", line_height=1.24)
        for child in node.get("children", []):
            draw_nodes(child, lvl + 1)

    draw_nodes(root)
    return canvas.render()


# ----------------------------------------------------------------- sankey ----

def sankey(b: dict, ctx: Ctx) -> str:
    """Where a quantity goes as it moves between stages. Only worth the ink when
    the *splitting and merging* is the message; a simple decline is a funnel."""
    t = ctx.theme
    links = b.get("links", [])
    if not links:
        return ""
    height = float(b.get("height", 320))
    node_w = 13.0
    pad = 14.0

    names = []
    for link in links:
        for key in ("source", "target"):
            if link.get(key) and link[key] not in names:
                names.append(link[key])

    level = {}

    def assign(name, depth=0, seen=None):
        seen = seen or set()
        if name in seen:
            return
        level[name] = max(level.get(name, 0), depth)
        for link in links:
            if link.get("source") == name:
                assign(link["target"], depth + 1, seen | {name})

    roots = [n for n in names if not any(l.get("target") == n for l in links)]
    for r in roots or names[:1]:
        assign(r)
    for n in names:
        level.setdefault(n, 0)
    depth_max = max(level.values()) or 1

    totals = {}
    for name in names:
        out_v = sum(float(l.get("value") or 0) for l in links if l.get("source") == name)
        in_v = sum(float(l.get("value") or 0) for l in links if l.get("target") == name)
        totals[name] = max(out_v, in_v)

    columns = {}
    for name in names:
        columns.setdefault(level[name], []).append(name)
    col_total = {d: sum(totals[n] for n in ns) for d, ns in columns.items()}
    max_total = max(col_total.values()) or 1
    usable_h = height - 26

    pos = {}
    for d, ns in columns.items():
        gap = pad if len(ns) > 1 else 0
        avail = usable_h - gap * (len(ns) - 1)
        y = 14 + (usable_h - (sum(totals[n] for n in ns) / max_total * avail
                             + gap * (len(ns) - 1))) / 2
        for name in ns:
            h = totals[name] / max_total * avail
            pos[name] = (d, y, max(h, 3))
            y += max(h, 3) + gap

    # Reserve room on the right for the terminal column's labels, which are the
    # only ones drawn beside a node. Without it they run off the viewBox.
    last_labels = [n for n in names if level[n] == depth_max]
    right_pad = min(
        max((svg.text_width(n, 10, 600) for n in last_labels), default=0) + 14,
        ctx.width * 0.28,
    )
    col_x = {d: 4 + (ctx.width - node_w - 8 - right_pad) * (d / depth_max if depth_max else 0)
             for d in columns}
    canvas = svg.Canvas(ctx.width, height, t)

    cursor_out, cursor_in = {}, {}
    for i, link in enumerate(sorted(links, key=lambda l: -float(l.get("value") or 0))):
        s, tg = link.get("source"), link.get("target")
        if s not in pos or tg not in pos:
            continue
        value = float(link.get("value") or 0)
        sd, sy, sh = pos[s]
        td, ty, th = pos[tg]
        s_off = cursor_out.get(s, 0.0)
        t_off = cursor_in.get(tg, 0.0)
        band_s = value / (totals[s] or 1) * sh
        band_t = value / (totals[tg] or 1) * th
        x0 = col_x[sd] + node_w
        x1 = col_x[td]
        color = t.series(names.index(s) % t.series_count())
        canvas.path(svg.ribbon_path(x0, sy + s_off, sy + s_off + band_s,
                                    x1, ty + t_off, ty + t_off + band_t),
                    fill=t.wash(color, 0.42))
        cursor_out[s] = s_off + band_s
        cursor_in[tg] = t_off + band_t

    for name in names:
        d, y, h = pos[name]
        color = t.series(names.index(name) % t.series_count())
        canvas.rect(col_x[d], y, node_w, h, color, r=2)
        if d == depth_max:
            # Terminal nodes have nothing to their right, so the label sits
            # beside them in the reserved gutter.
            canvas.text(col_x[d] + node_w + 6, y + h / 2 + 3.4,
                        svg.truncate(name, 10, right_pad - 10, 600),
                        size=10, weight=600, fill=t.ink("secondary"), anchor="start")
        else:
            # Everywhere else the space to the right is full of ribbons, so the
            # label goes above the node rather than on top of the flow.
            canvas.text(col_x[d], max(y - 5, 8),
                        svg.truncate(name, 10, (ctx.width - right_pad) / (depth_max + 1) - 8, 600),
                        size=10, weight=600, fill=t.ink("secondary"), anchor="start")

    out = [canvas.render()]
    if b.get("table", True):
        out.append(chrome.details_table(
            ["From", "To", b.get("value_label", "Value")],
            [[str(l.get("source", "")), str(l.get("target", "")),
              svg.fmt_plain(l.get("value"))] for l in links]))
    return "".join(out)


# ----------------------------------------------------------------- matrix ----

def matrix(b: dict, ctx: Ctx) -> str:
    """Options against criteria. This is the honest home for a comparison that
    people try to force into a chart, and the only correct form for four or
    more overlapping sets."""
    t = ctx.theme
    rows = b.get("rows", [])
    cols = [str(c) for c in b.get("cols", [])]
    label_w = min(chrome.measure_labels([str(r.get("label", "")) for r in rows], 11, 600) + 16,
                  ctx.width * 0.34)
    cell_w = (ctx.width - label_w) / max(len(cols), 1)
    head_lines = max((len(svg.wrap(c, 10, cell_w - 10, 600, 2)) for c in cols), default=1)
    head_h = 14 + head_lines * 13
    row_h = float(b.get("row_height", 38))
    height = head_h + len(rows) * row_h + 4
    canvas = svg.Canvas(ctx.width, height, t)

    for ci, col in enumerate(cols):
        x = label_w + ci * cell_w
        lines = svg.wrap(col, 10, cell_w - 10, 600, 2)
        canvas.text_lines(x + cell_w / 2, 12, lines, size=10, weight=600,
                          fill=t.ink("muted"), anchor="middle", line_height=1.25)
    canvas.line(0, head_h - 4, ctx.width, head_h - 4, stroke=t.rule("axis"), width=1)

    for ri, row in enumerate(rows):
        y = head_h + ri * row_h
        if ri % 2 == 1:
            canvas.rect(0, y, ctx.width, row_h, t.surface("sunken"), r=t.geom("radius", 4) / 2)
        canvas.text(6, y + row_h / 2 + 4, svg.truncate(str(row.get("label", "")), 11,
                                                       label_w - 14, 600),
                    size=11, weight=600, fill=t.ink("primary"))
        for ci in range(len(cols)):
            cells = row.get("cells", [])
            value = cells[ci] if ci < len(cells) else None
            cx = label_w + ci * cell_w + cell_w / 2
            cy = y + row_h / 2
            if value in (True, "yes", "y", "✓", "true"):
                canvas.circle(cx, cy, 9, t.wash(t.status("good"), 0.20))
                canvas.path(f"M{svg.num(cx - 4)},{svg.num(cy)}l3,3.4l5.4,-6.4",
                            stroke=t.status("good_text"), width=2)
            elif value in (False, "no", "n", "×", "false"):
                canvas.circle(cx, cy, 9, t.surface("sunken"))
                canvas.line(cx - 3.6, cy - 3.6, cx + 3.6, cy + 3.6,
                            stroke=t.ink("muted"), width=1.8, cap="round")
                canvas.line(cx + 3.6, cy - 3.6, cx - 3.6, cy + 3.6,
                            stroke=t.ink("muted"), width=1.8, cap="round")
            elif value in ("partial", "~", "some"):
                canvas.circle(cx, cy, 9, t.wash(t.status("warning"), 0.24))
                canvas.line(cx - 4, cy, cx + 4, cy, stroke=t.ink("secondary"), width=2,
                            cap="round")
            elif value is not None and str(value) != "":
                canvas.text(cx, cy + 3.6, svg.truncate(str(value), 10, cell_w - 10),
                            size=10, fill=t.ink("secondary"), anchor="middle")
    return canvas.render()


# ---------------------------------------------------------------- anatomy ----

def anatomy(b: dict, ctx: Ctx) -> str:
    """An image or diagram with numbered callouts. The one block that expects a
    raster: do not replace a real photograph or screenshot with CSS scenery."""
    t = ctx.theme
    src = b.get("image", "")
    callouts = b.get("callouts", [])
    height = float(b.get("height", 320))
    canvas = svg.Canvas(ctx.width, height, t)
    if src:
        canvas.add(f'<image href="{svg.esc(src)}" x="0" y="0" width="{svg.num(ctx.width)}" '
                   f'height="{svg.num(height)}" preserveAspectRatio="xMidYMid slice"/>')
    else:
        canvas.rect(0, 0, ctx.width, height, t.surface("sunken"), r=t.geom("radius", 4) * 2)
        canvas.text(ctx.width / 2, height / 2, "image not supplied", size=11,
                    fill=t.ink("muted"), anchor="middle")

    for i, callout in enumerate(callouts):
        x = ctx.width * float(callout.get("x", 0.5))
        y = height * float(callout.get("y", 0.5))
        canvas.circle(x, y, 13, t.accent, stroke=t.surface("card"), width=2.5)
        canvas.text(x, y + 4.2, str(i + 1), size=11.5, weight=700,
                    fill=t.ink_on(t.accent), anchor="middle")

    items = "".join(
        f'<li><span class="ig-callout-num">{i + 1}</span>'
        f'<div><strong>{svg.esc(c.get("title", ""))}</strong>'
        f'{(" " + svg.esc(c.get("text", ""))) if c.get("text") else ""}</div></li>'
        for i, c in enumerate(callouts)
    )
    legend = f'<ol class="ig-callouts">{items}</ol>' if callouts else ""
    return canvas.render() + legend
