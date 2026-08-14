#!/usr/bin/env python3
"""README graphics for this skill. Purpose-built, not page screenshots.

WHY THIS WAS REWRITTEN. Version 1 sliced a `scroll` document into four PNGs.
Looked at on the real GitHub page, in dark mode, at the real column width, that
gave: five frozen "Show the numbers" disclosures (a picture of a control nobody
can operate), four light slabs on a dark page, images half empty because a
scroll layout puts blocks on a narrow measure inside a wide viewport, and 8px
axis labels once GitHub scaled 1280px into its ~890px column.

TARGET `slide`, 338x190mm. A README image is a fixed 16:9 frame, and a
paginated target fills its page instead of leaving the dead right-hand column a
scroll layout leaves.

`tables: false`, which this skill normally forbids. The accessibility twin is a
<details> element; in a raster image it is an affordance that cannot be
operated. The values it carries are in the README prose beside every image, and
the HTML document keeps its twins. That is the trade, stated rather than hidden.

WHAT IS DELIBERATELY NOT AN IMAGE. The eleven pipeline steps and the
guard/failure table were images in version 1. They are markdown now: an ordered
list and a table render natively, are searchable and copyable, and follow the
reader's theme. An image earns its place when the idea is spatial. A numbered
list is not.
"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


def fig_before_after():
    p = []
    p.append('<text class="ig-fig-kicker" x="40" y="28">what you would write</text>')
    p.append('<text class="ig-fig-kicker ig-fig-accent" x="620" y="28">what it renders</text>')

    # A wall of prose.
    p.append('<rect class="ig-fig-node-mute" x="40" y="46" width="380" height="286" rx="6"/>')
    for i in range(15):
        y = 70 + i * 18
        w = 320 if i % 4 != 3 else 210
        p.append(f'<line class="ig-fig-rule" x1="64" y1="{y}" x2="{64 + w}" y2="{y}"/>')
    p.append('<text class="ig-fig-label ig-fig-mute" x="230" y="356" text-anchor="middle">2,086 words, one chart</text>')

    p.append('<line class="ig-fig-edge-strong" x1="452" y1="189" x2="588" y2="189" '
             'marker-end="url(#ig-arrow-accent)"/>')
    p.append('<text class="ig-fig-kicker" x="520" y="176" text-anchor="middle">budget</text>')

    # The rendered page: a title, a chart, two labels.
    p.append('<rect class="ig-fig-node-strong" x="620" y="46" width="420" height="286" rx="6"/>')
    p.append('<rect class="ig-fig-solid" x="648" y="74" width="220" height="12" rx="3"/>')
    p.append('<line class="ig-fig-rule" x1="648" y1="104" x2="920" y2="104"/>')
    for i, h in enumerate((54, 92, 132, 76, 110)):
        x = 648 + i * 58
        p.append(f'<rect class="ig-fig-solid-accent" x="{x}" y="{270 - h}" width="38" height="{h}" rx="3"/>')
    p.append('<line class="ig-fig-rule" x1="648" y1="272" x2="1012" y2="272"/>')
    p.append('<line class="ig-fig-rule" x1="648" y1="298" x2="820" y2="298"/>')
    p.append('<text class="ig-fig-label ig-fig-accent" x="830" y="356" text-anchor="middle">150 words a page</text>')

    return {
        "type": "figure",
        "span": 12,
        "id": "before-after",
        "title": "The same material as prose, and as a rendered explainer",
        "subtitle": "The word budget runs before anything renders, and a breach fails the build.",
        "viewbox": "0 0 1060 430",
        "alt": "On the left, a page filled with lines of body text. An arrow labelled budget leads to the right, where the same material is a page carrying a title, a bar chart and two short labels.",
        "encodes": {
            "columns": ["", "Words", "Graphics"],
            "rows": [["The document that failed review", 2086, 1],
                     ["Budget, per page at graphic density", 150, "unbounded"]],
        },
        "svg": "".join(p),
    }


# --------------------------------------------------------------------------
# Scene 2: a specimen sheet of the six families
# --------------------------------------------------------------------------
def fig_specimens():
    def bars(x, y):
        out = []
        for i, h in enumerate((16, 30, 22, 38)):
            out.append(f'<rect class="ig-fig-solid-accent" x="{x + i * 13}" y="{y + 44 - h}" '
                       f'width="9" height="{h}" rx="2"/>')
        return out

    def lolli(x, y):
        out = []
        for i, w in enumerate((18, 34, 26)):
            yy = y + 8 + i * 14
            out.append(f'<line class="ig-fig-edge" x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}"/>')
            out.append(f'<circle class="ig-fig-solid-accent" cx="{x + w}" cy="{yy}" r="4"/>')
        return out

    def heat(x, y):
        out = []
        for r in range(3):
            for c in range(3):
                op = 0.25 + 0.25 * ((r + c) % 3)
                out.append(f'<rect class="ig-fig-solid-accent" x="{x + c * 16}" y="{y + 6 + r * 14}" '
                           f'width="13" height="11" rx="2" opacity="{op}"/>')
        return out

    def line(x, y):
        pts = " ".join(f"{x + i * 12},{y + 40 - v}" for i, v in enumerate((8, 20, 14, 30, 26, 38)))
        return [f'<polyline class="ig-fig-edge-strong" fill="none" points="{pts}"/>']

    def slope(x, y):
        return [f'<line class="ig-fig-edge" x1="{x}" y1="{y + 34}" x2="{x + 44}" y2="{y + 10}"/>',
                f'<line class="ig-fig-edge-mute" x1="{x}" y1="{y + 14}" x2="{x + 44}" y2="{y + 30}"/>',
                f'<circle class="ig-fig-solid-accent" cx="{x}" cy="{y + 34}" r="4"/>',
                f'<circle class="ig-fig-solid-accent" cx="{x + 44}" cy="{y + 10}" r="4"/>']

    def dumb(x, y):
        out = []
        for i in range(3):
            yy = y + 10 + i * 14
            out.append(f'<line class="ig-fig-edge" x1="{x + 4}" y1="{yy}" x2="{x + 40}" y2="{yy}"/>')
            out.append(f'<circle class="ig-fig-solid" cx="{x + 4}" cy="{yy}" r="3.5"/>')
            out.append(f'<circle class="ig-fig-solid-accent" cx="{x + 40}" cy="{yy}" r="3.5"/>')
        return out

    def ring(x, y):
        return [f'<circle class="ig-fig-ring-accent" cx="{x + 24}" cy="{y + 24}" r="17" '
                f'stroke-width="9"/>']

    def waffle(x, y):
        out = []
        for r in range(4):
            for c in range(4):
                cls = "ig-fig-solid-accent" if r * 4 + c < 9 else "ig-fig-node"
                out.append(f'<rect class="{cls}" x="{x + c * 12}" y="{y + 4 + r * 12}" '
                           f'width="9" height="9" rx="1.5"/>')
        return out

    def sharebar(x, y):
        out, cx = [], x
        for w, cls in ((26, "ig-fig-solid-accent"), (14, "ig-fig-solid"), (10, "ig-fig-node")):
            out.append(f'<rect class="{cls}" x="{cx}" y="{y + 18}" width="{w}" height="14" rx="2"/>')
            cx += w + 2
        return out

    def proc(x, y):
        out = []
        for i in range(3):
            out.append(f'<rect class="ig-fig-node" x="{x + i * 20}" y="{y + 18}" width="15" height="14" rx="2"/>')
            if i < 2:
                out.append(f'<line class="ig-fig-edge" x1="{x + 15 + i * 20}" y1="{y + 25}" '
                           f'x2="{x + 20 + i * 20}" y2="{y + 25}"/>')
        return out

    def tree(x, y):
        return [f'<rect class="ig-fig-node" x="{x + 16}" y="{y + 6}" width="16" height="11" rx="2"/>',
                f'<rect class="ig-fig-node" x="{x}" y="{y + 32}" width="16" height="11" rx="2"/>',
                f'<rect class="ig-fig-node" x="{x + 32}" y="{y + 32}" width="16" height="11" rx="2"/>',
                f'<line class="ig-fig-edge-mute" x1="{x + 24}" y1="{y + 17}" x2="{x + 8}" y2="{y + 32}"/>',
                f'<line class="ig-fig-edge-mute" x1="{x + 24}" y1="{y + 17}" x2="{x + 40}" y2="{y + 32}"/>']

    def venn(x, y):
        return [f'<circle class="ig-fig-ring-accent" cx="{x + 18}" cy="{y + 24}" r="14"/>',
                f'<circle class="ig-fig-ring" cx="{x + 32}" cy="{y + 24}" r="14"/>']

    def stack(x, y):
        return [f'<rect class="ig-fig-node" x="{x}" y="{y + 6 + i * 13}" width="48" height="11" rx="2"/>'
                for i in range(3)]

    def lanes(x, y):
        out = []
        for r in range(3):
            yy = y + 8 + r * 13
            out.append(f'<line class="ig-fig-rule" x1="{x}" y1="{yy + 10}" x2="{x + 50}" y2="{yy + 10}"/>')
            out.append(f'<rect class="ig-fig-solid-accent" x="{x + r * 16}" y="{yy}" '
                       f'width="14" height="9" rx="2"/>')
        return out

    def chips(x, y):
        return [f'<rect class="ig-fig-node" x="{x + (i % 2) * 26}" y="{y + 12 + (i // 2) * 14}" '
                f'width="22" height="10" rx="5"/>' for i in range(4)]

    def kpis(x, y):
        out = []
        for i in range(3):
            out.append(f'<line class="ig-fig-rule" x1="{x + i * 18}" y1="{y + 14}" x2="{x + 12 + i * 18}" y2="{y + 14}"/>')
            out.append(f'<rect class="ig-fig-solid" x="{x + i * 18}" y="{y + 20}" width="12" height="13" rx="2"/>')
        return out

    def callout(x, y):
        return [f'<rect class="ig-fig-node" x="{x}" y="{y + 12}" width="52" height="22" rx="3"/>',
                f'<rect class="ig-fig-solid-accent" x="{x}" y="{y + 12}" width="4" height="22" rx="2"/>']

    def rows(x, y):
        out = [f'<line class="ig-fig-rule" x1="{x}" y1="{y + 10 + i * 9}" x2="{x + 50}" y2="{y + 10 + i * 9}"/>'
               for i in range(4)]
        return out

    families = [
        ("Quantity", 8, (bars, lolli, heat)),
        ("Change", 5, (line, slope, dumb)),
        ("Part-to-whole", 7, (ring, waffle, sharebar)),
        ("Structure", 7, (proc, tree, venn)),
        ("Diagram", 6, (stack, lanes, chips)),
        ("Editorial", 19, (kpis, callout, rows)),
    ]

    p = []
    for i, (name, count, glyphs) in enumerate(families):
        cx = 12 + (i % 3) * 352
        cy = 44 + (i // 3) * 226
        p.append(f'<text class="ig-fig-title" x="{cx}" y="{cy}">{name}</text>')
        p.append(f'<text class="ig-fig-mute" x="{cx + 250}" y="{cy}" text-anchor="end">{count}</text>')
        p.append(f'<line class="ig-fig-rule" x1="{cx}" y1="{cy + 12}" x2="{cx + 250}" y2="{cy + 12}"/>')
        for j, glyph in enumerate(glyphs):
            p.extend(glyph(cx + j * 84, cy + 26))
    return {
        "type": "figure",
        "span": 12,
        "id": "specimens",
        "title": "The six families of block, three specimens from each",
        "subtitle": "52 forms. Editorial is the largest and the one to reach for least.",
        "viewbox": "0 0 1060 430",
        "alt": "Six labelled groups, each showing three miniature specimens of the block shapes in that family: bars and grids for quantity, lines and slopes for change, rings and waffles for part-to-whole, chains and trees for structure, layers and lanes for diagram, tiles and rules for editorial.",
        "encodes": {
            "columns": ["Family", "Block types"],
            "rows": [["Editorial", 19], ["Quantity", 8], ["Part-to-whole", 7],
                     ["Structure", 7], ["Diagram", 6], ["Change", 5]],
        },
        "svg": "".join(p),
    }


spec = {
    "meta": {
        "title": "infographic, README figures",
        # The same theme as the specimen sheets. With the slides on `default` and
        # the gallery on `rentos`, the README read as two documents: the figure
        # above the vocabulary section and the sheets below it disagreed about
        # what a heading and an accent look like.
        "theme": "rentos",
        "page": "slide",
        "density": "graphic",
        "tables": False,
        "footer_left": " ",
        "footer_right": " ",
    },
    "blocks": [
        fig_before_after(),
        dict(fig_specimens(), **{"break": "before"}),
        {"type": "bar", "span": 12, "break": "before",
         "title": "Words allowed in each text field, at graphic density",
         "subtitle": "A drawing may carry 40 words of labels; a label on a mark may carry six.",
         "categories": ["Figure text", "Quote", "Callout", "Note", "Subtitle",
                        "Title", "Item detail", "Chart label"],
         "values": [40, 26, 24, 18, 16, 14, 12, 6],
         "sort": None, "compact": False, "value_label": "Words",
         "note": "Footnotes and table cells are exempt from the per-field caps, never from the page total."},
    ],
}

path = os.path.join(OUT, "readme_spec.json")
with open(path, "w") as f:
    json.dump(spec, f, indent=1)
print(path)
