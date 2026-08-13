#!/usr/bin/env python3
"""The visual explainer that illustrates this skill's own README.

STEP 2. READER: a developer landing on the repo cold. Knows what a README is,
has never seen this tool, and is deciding in ten seconds whether it does
anything a chart library does not.

TERMS THEY DO NOT HAVE -> where each goes:
  block, form, spine, scene, the twin  -> `definitions`, before the argument
  density, target                      -> footnotes

STEP 3. SPINES considered:
  A  what it makes      - input, output, the catalog, the themes   <- TAKEN
  B  what it refuses    - the budget, the build errors, the guards  <- act two
  C  how you use it     - the eleven steps, the CLI                 <- README prose
A is taken because a cold reader asks "what does this produce" first, and B is
folded in as the second act rather than a separate document, because the
refusals are the *cause* of the output rather than a different subject.

STEP 5. SCENES, before the catalog was opened:
  1. a wall of prose collapsing into a designed page
  2. a specimen sheet: what the 52 forms actually look like, at a glance
Neither is a catalog shape. The third slot is deliberately unused.
"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# Scene 1: the document you would have written, and the one it renders
# --------------------------------------------------------------------------
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
        "viewbox": "0 0 1080 372",
        "alt": "On the left, a page filled with lines of body text. An arrow labelled budget leads to the right, where the same material is a page carrying a title, a bar chart and two short labels.",
        "encodes": {
            "columns": ["", "Words", "Graphics"],
            "rows": [["The document that failed review", 2086, 1],
                     ["Budget, per page at graphic density", 150, "unbounded"]],
        },
        "svg": "".join(p),
        "note": "The 2,086-word figure is this skill's own version 1, which is why the budget exists.",
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

    p = ['<text class="ig-fig-kicker ig-fig-accent" x="0" y="18">52 forms, six families</text>']
    for i, (name, count, glyphs) in enumerate(families):
        cx = 20 + (i % 3) * 360
        cy = 52 + (i // 3) * 168
        p.append(f'<text class="ig-fig-title" x="{cx}" y="{cy}">{name}</text>')
        p.append(f'<text class="ig-fig-mute" x="{cx + 250}" y="{cy}" text-anchor="end">{count}</text>')
        p.append(f'<line class="ig-fig-rule" x1="{cx}" y1="{cy + 12}" x2="{cx + 250}" y2="{cy + 12}"/>')
        for j, glyph in enumerate(glyphs):
            p.extend(glyph(cx + j * 86, cy + 26))
    return {
        "type": "figure",
        "span": 12,
        "id": "specimens",
        "bleed": True,
        "invert": True,
        "title": "The six families of block, three specimens from each",
        "subtitle": "Editorial is the largest family and the one to reach for least.",
        "viewbox": "0 0 1080 372",
        "alt": "Six labelled groups, each showing three miniature specimens of the block shapes in that family: bars and grids for quantity, lines and slopes for change, rings and waffles for part-to-whole, chains and trees for structure, layers and lanes for diagram, tiles and rules for editorial.",
        "encodes": {
            "columns": ["Family", "Block types"],
            "rows": [["Editorial", 19], ["Quantity", 8], ["Part-to-whole", 7],
                     ["Structure", 7], ["Diagram", 6], ["Change", 5]],
        },
        "svg": "".join(p),
        "note": "Specimens are drawn to scale with each other, not to any particular data.",
    }


spec = {
    "meta": {
        "title": "infographic: a graphic-first document skill for Claude Code",
        "theme": "default",
        "page": "scroll",
        "density": "graphic",
        "footer_left": "infographic",
        "footer_right": "github.com/remybroun/infographic",
    },
    "blocks": [
        {"type": "hero", "kicker": "Claude Code skill",
         "title": "A skill that turns a document or a topic into a designed explainer",
         "subtitle": "It caps every text field and fails the build when a page becomes an essay."},
        {"type": "kpi", "span": 12, "items": [
            {"label": "Block types", "value": 52, "compact": False},
            {"label": "Families", "value": 6, "compact": False},
            {"label": "Themes", "value": 3, "compact": False},
            {"label": "Test assertions", "value": 269, "compact": False},
        ]},
        {"type": "definitions", "span": 12, "title": "Four words used throughout",
         "items": [
             {"term": "Block", "text": "One unit of the page: a chart, a diagram, a callout."},
             {"term": "Spine", "text": "The argument a document makes, chosen from three."},
             {"term": "Scene", "text": "An image the catalog has no shape for, drawn by hand."},
             {"term": "Twin", "text": "The data table shipped beside every chart."},
         ]},

        {"type": "section", "number": "01", "title": "What it produces",
         "lede": "A print-ready PDF, or a continuous page whose HTML is the deliverable."},
        fig_before_after(),
        {"type": "process", "span": 12, "orientation": "vertical", "numbered": True,
         "title": "The eleven steps from source to finished document",
         "subtitle": "One to six are judgement and cannot be automated; seven to eleven mostly are.",
         "steps": [
             {"title": "Source", "text": "Read or extract the facts"},
             {"title": "Reader and claim", "text": "Who reads it, what they lack"},
             {"title": "Three spines", "text": "Three arguments, then choose"},
             {"title": "Target", "text": "Paper, poster or scrolling page"},
             {"title": "Scenes", "text": "Before the catalog is opened"},
             {"title": "Forms", "text": "One per remaining claim"},
             {"title": "Spec", "text": "Blocks in reading order"},
             {"title": "Theme", "text": "Validated, never hand-picked"},
             {"title": "Render", "text": "Compile, rasterise, lint"},
             {"title": "Look at it", "text": "The linter never has"},
             {"title": "Hand off", "text": "Spec, document and method"},
         ]},

        {"type": "section", "number": "02", "title": "The vocabulary it draws with"},
        fig_specimens(),
        {"type": "bar", "span": 12,
         "title": "Block types available in each family",
         "subtitle": "Editorial is largest because it holds the page furniture, not because it is used most.",
         "categories": ["Editorial", "Quantity", "Part-to-whole", "Structure", "Diagram", "Change"],
         "values": [19, 8, 7, 7, 6, 5], "sort": None, "compact": False,
         "value_label": "Block types",
         "note": "49 aliases map ordinary words onto these: pie to donut, waffle to unit, 2x2 to quadrant."},

        {"type": "section", "number": "03", "title": "What the build refuses to render",
         "lede": "Every guard below exists because a document shipped without it."},
        {"type": "bar", "span": 12,
         "title": "Words allowed in each text field, at graphic density",
         "subtitle": "A drawing may carry 40 words of labels; a chart label may carry six.",
         "categories": ["Figure text", "Quote", "Callout", "Note", "Subtitle",
                        "Title", "Item detail", "Chart label"],
         "values": [40, 26, 24, 18, 16, 14, 12, 6], "sort": None, "compact": False,
         "value_label": "Words",
         "note": "Footnotes and table cells are exempt from the per-field caps, not from the page total."},
        {"type": "chips", "span": 12,
         "title": "How each guard fails",
         "items": [
             {"label": "Word budget", "tone": "danger", "note": "build error"},
             {"label": "Over three figures", "tone": "danger", "note": "build error"},
             {"label": "Colour literal in a drawing", "tone": "danger", "note": "build error"},
             {"label": "No chart has a data twin", "tone": "danger", "note": "lint error"},
             {"label": "Tables standing in for prose", "tone": "warn", "note": "warning"},
             {"label": "Undefined vocabulary", "tone": "warn", "note": "warning"},
             {"label": "Same forms as last time", "tone": "warn", "note": "warning"},
         ]},
        {"type": "table", "span": 12,
         "columns": ["Guard", "The failure that produced it"],
         "align": ["left", "left"],
         "rows": [
             ["Word budget, enforced in code",
              "Version 1 shipped 2,086 words across eight pages carrying one chart"],
             ["At most three hand-drawn figures",
              "Version 2 fixed the word count and hand-drew everything, losing all consistency"],
             ["Colour literals refused inside a drawing",
              "Hand-drawn figures are where computed colour slips first"],
             ["Authored tables count toward the budget",
              "A section retyped as three tables passed as clean; the cells were exempt"],
             ["Identifiers counted, definitions required",
              "A page carried 30 identifiers and no definitions block, and passed"],
             ["Graphic forms compared against the last version",
              "A regeneration came back 93% identical, with every step performed honestly"],
         ],
         "caption": "Each guard is a specific document that shipped and should not have"},

        {"type": "callout", "span": 12, "tone": "key",
         "title": "The linter has never looked at a document",
         "text": "It checks structure. Whether a label collided, an arrow points at nothing, or the argument lands is only ever answered by opening the render."},

        {"type": "footnotes", "span": 12, "items": [
            "Density: graphic is the default and refuses body prose; report allows it and is opt-in per document.",
            "Target: the page geometry, one of seven paper sizes or the continuous scrolling page.",
            "Counts read from lib/registry.py and lib/density.py at the current commit: 52 block types, 6 families, 49 aliases.",
            "Requirements: Python 3.9+ standard library, and a Chromium-family browser for rendering. Poppler optional.",
        ]},
    ],
}

path = os.path.join(OUT, "readme_spec.json")
with open(path, "w") as f:
    json.dump(spec, f, indent=1)
print(path)
