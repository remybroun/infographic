#!/usr/bin/env python3
"""
The marks that were considered, each traced back to a named painting.

This is the sketchbook, not the identity. The mark that won is the iris, and it
lives in branding/; this file imports it so the comparison below stays honest.
The mandala in gen_logo.py stays exactly as it is. Run it and open
options/options.html:

    python3 assets/logo/gen_options.py

Each option cites its ancestor, because "in the style of" is not a design
brief and cannot be argued with. A specific painting can be.

  dove     What a Human Being Is (1910) and The Dove No. 12 (1915).
           A great circle split down a vertical axis, a heart at the centre
           carrying the split reversed, a prism fanning up from the base, and
           the double helix running the full height, hidden where the heart
           covers it.

  atom     Atom Series No. 8 (1917).
           A square field cut by one diagonal, and at the crossing a small orb,
           half lit and half dark, inside a spiked corona. Her note on the sheet
           says the atom is in constant change between rest and activity, which
           is the half-lit orb.

  trefoil  The Ten Largest, No. 2, Childhood (1907).
           Three fat lobes in a ring of beads, with a small flower at the hub.
           The most unmistakably hers of the three, and the least like a chart.

  iris     Series VIII, Utgångsbild (1920), and The Swan, Group IX/SUW (1915).
           The one that was chosen. The Swan's split donut for the structure,
           the 1920 sheet's ordered ramp for the fill, and the two halves
           running the ramp in opposite directions so the disc inverts across
           its own axis. Defined in branding/gen_brand.py, not here.

The first three reuse the palette from gen_logo.py unchanged, so the colour
result carries over: both schemes clear all six categorical checks in
scripts/validate_palette.py. The iris is a ramp rather than a set of
categories, so it is gated as one, with --ordinal. Nothing here introduces a
new hue.

Rejected on purpose: her eight-sector colour wheel from Series VII No. 7d
(1920). It is the most on-topic thing she ever drew for a tool called
infographic, and that is the problem. Drawn flat it is just a pie chart, and a
pie chart is the one form nobody would read as a painter's hand.
"""
import math
import os
import sys

from gen_logo import PALETTES, SIZE, C, _vars

# The iris was promoted out of this file and into the identity. It is imported
# rather than copied, so the comparison page below cannot drift from what
# branding/ actually ships.
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "branding"))
from gen_brand import RAMPS, mark_body as body_iris  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "options")

W = {k: f"var(--{k})" for k in
     ("ground", "ink", "warm", "warmt", "cool", "coolt")}


def _vars_all(scheme, selector=":root"):
    """The six base colours plus the eight ramp steps, as one custom-property set."""
    body = " ".join(f"--{k}: {v};" for k, v in
                    list(PALETTES[scheme].items()) + list(RAMPS[scheme].items()))
    return f"{selector} {{ {body} }}"


# ── shared shapes ───────────────────────────────────────────────────────────
def heart_half(cx, cy, w, h, left):
    """Half a heart, cut on its own axis of symmetry.

    The notch and the point both sit exactly on x = 0, so a half can be closed
    with a straight line and no clip path is needed. That matters: clip paths
    need ids, and ids collide the moment a mark is inlined twice on one page.
    """
    s = -1 if left else 1
    return (f"M {cx:.1f},{cy + h * 0.30:.1f} "
            f"C {cx + s * w * 0.50:.1f},{cy - h * 0.05:.1f} "
            f"{cx + s * w * 0.50:.1f},{cy - h * 0.42:.1f} "
            f"{cx + s * w * 0.25:.1f},{cy - h * 0.42:.1f} "
            f"C {cx + s * w * 0.10:.1f},{cy - h * 0.42:.1f} "
            f"{cx + s * w * 0.02:.1f},{cy - h * 0.30:.1f} "
            f"{cx:.1f},{cy - h * 0.22:.1f} Z")


def half_disc(cx, cy, r, upper):
    """Half a circle, cut horizontally. SVG y grows down, so upper sweeps left."""
    if upper:
        return f"M {cx - r},{cy} A {r},{r} 0 0 1 {cx + r},{cy} Z"
    return f"M {cx + r},{cy} A {r},{r} 0 0 1 {cx - r},{cy} Z"


def half_disc_v(cx, cy, r, left):
    """Half a circle, cut vertically. The orb's lit and unlit faces."""
    if left:
        return f"M {cx},{cy - r} A {r},{r} 0 0 0 {cx},{cy + r} Z"
    return f"M {cx},{cy - r} A {r},{r} 0 0 1 {cx},{cy + r} Z"


def path(d, fill, stroke=None, sw=1.4, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s}{extra}/>'


# ── option 1: dove ──────────────────────────────────────────────────────────
DOVE = {
    "full":  {"r": 104, "hw": 112, "hh": 120, "hy": 112, "prism": True,
              "helix": True, "sw": 2.0},
    "small": {"r": 108, "hw": 124, "hh": 134, "hy": 124, "prism": False,
              "helix": False, "sw": 3.4},
}


def _helix(cx, y0, y1, amp, period, phase, step=3.0):
    pts, y = [], y0
    while y <= y1:
        x = cx + amp * math.sin(2 * math.pi * (y - y0) / period + phase)
        pts.append(f"{x:.1f},{y:.1f}")
        y += step
    return "M " + " L ".join(pts)


def _prism(cx, cy, r, spread=52.0, reach=0.62):
    """A fan of wedges struck from the foot of the circle, warm left to cool right.

    Bounded by an arc of its own, not by the rim: at full reach the fan fills the
    whole disc and the split above it stops reading, which is how the first
    render of this came out. A ray at angle t from vertical leaves the disc at
    2r*cos(t), so any reach below 2r*cos(spread) is safely inside. At 58 degrees
    that ceiling is 1.06r, and 0.70r sits under it with room to spare.
    """
    px, py = cx, cy + r
    rr = r * reach
    # Cool on the left, matching the heart above it rather than the disc behind
    # it. Under the mono scheme only one end of this fan survives as solid ink,
    # and it has to be the same end the heart fills, or the mark contradicts
    # itself the moment it is printed in one colour.
    fills = [W["cool"], W["coolt"], W["ground"], W["warmt"], W["warm"]]
    n = len(fills)
    out = []
    for i, fill in enumerate(fills):
        t0 = math.radians(-spread + (2 * spread) * i / n)
        t1 = math.radians(-spread + (2 * spread) * (i + 1) / n)
        p = [(px + rr * math.sin(t), py - rr * math.cos(t)) for t in (t0, t1)]
        # sweep 1: as t grows the far end travels left to right across the fan
        d = (f"M {px:.1f},{py:.1f} L {p[0][0]:.1f},{p[0][1]:.1f} "
             f"A {rr:.1f},{rr:.1f} 0 0 1 {p[1][0]:.1f},{p[1][1]:.1f} Z")
        out.append(path(d, fill, W["ink"], 1.0))
    return out


def body_dove(detail="full"):
    g = DOVE[detail]
    r, sw = g["r"], g["sw"]
    out = []

    # The great circle, split down the vertical. Warm left, cool right.
    out.append(path(f"M {C},{C - r} A {r},{r} 0 0 0 {C},{C + r} Z", W["warmt"]))
    out.append(path(f"M {C},{C - r} A {r},{r} 0 0 1 {C},{C + r} Z", W["coolt"]))
    if g["prism"]:
        out += _prism(C, C, r)
    out.append(f'<circle cx="{C}" cy="{C}" r="{r}" fill="none" '
               f'stroke="{W["ink"]}" stroke-width="{sw}"/>')
    out.append(f'<line x1="{C}" y1="{C - r}" x2="{C}" y2="{C + r}" '
               f'stroke="{W["ink"]}" stroke-width="{sw * 0.6:.1f}"/>')

    if g["helix"]:
        # Two strands, half a period apart, wound round the axis for the whole
        # height. Drawn over the disc and under the heart, so the heart hides the
        # middle of it, which is what the painting does.
        for phase in (0.0, math.pi):
            out.append(f'<path d="{_helix(C, 4, SIZE - 4, 9, 44, phase)}" fill="none" '
                       f'stroke="{W["ink"]}" stroke-width="1.3" stroke-linecap="round"/>')

    # The heart, carrying the same split reversed: cool on the warm side.
    out.append(path(heart_half(C, g["hy"], g["hw"], g["hh"], True),
                    W["cool"], W["ink"], sw))
    out.append(path(heart_half(C, g["hy"], g["hw"], g["hh"], False),
                    W["warm"], W["ink"], sw))
    return out


# ── option 2: atom ──────────────────────────────────────────────────────────
ATOM = {
    "full":  {"m": 16, "orb": 33, "pupil": 9, "corona": True, "keyline": True,
              "sw": 2.4},
    "small": {"m": 10, "orb": 46, "pupil": 15, "corona": False, "keyline": False,
              "sw": 4.0},
}


def body_atom(detail="full"):
    g = ATOM[detail]
    m, sw = g["m"], g["sw"]
    a, b = m, SIZE - m
    out = []

    # One diagonal, top-left to bottom-right, and the field it divides.
    out.append(path(f"M {a},{a} L {b},{a} L {b},{b} Z", W["coolt"]))
    out.append(path(f"M {a},{a} L {b},{b} L {a},{b} Z", W["warmt"]))
    out.append(f'<rect x="{a}" y="{a}" width="{b - a}" height="{b - a}" fill="none" '
               f'stroke="{W["ink"]}" stroke-width="{sw}"/>')
    if g["keyline"]:
        # The coloured border she ruled inside the sheet edge.
        k = m + 7
        out.append(f'<rect x="{k}" y="{k}" width="{SIZE - 2 * k}" height="{SIZE - 2 * k}" '
                   f'fill="none" stroke="{W["cool"]}" stroke-width="1.6"/>')
    out.append(f'<line x1="{a}" y1="{a}" x2="{b}" y2="{b}" '
               f'stroke="{W["ink"]}" stroke-width="{sw}"/>')

    if g["corona"]:
        # Activity. Short spikes, struck outward, the sun-fringe she draws round
        # anything charged.
        n, ri, ro, half = 40, g["orb"] + 1, g["orb"] + 17, 4.2
        for i in range(n):
            ang = 360 * i / n
            d = (f"M {-half},{-ri} L 0,{-ro} L {half},{-ri} Z")
            out.append(f'<path d="{d}" transform="translate({C} {C}) rotate({ang:.1f})" '
                       f'fill="{W["warm"]}"/>')

    # Rest and activity in one body: the orb is half lit, half dark.
    ro = g["orb"]
    out.append(path(half_disc_v(C, C, ro, True), W["ground"]))
    out.append(path(half_disc_v(C, C, ro, False), W["warm"]))
    out.append(f'<circle cx="{C}" cy="{C}" r="{ro}" fill="none" '
               f'stroke="{W["ink"]}" stroke-width="{sw}"/>')
    out.append(f'<circle cx="{C}" cy="{C}" r="{g["pupil"]}" fill="{W["cool"]}" '
               f'stroke="{W["ink"]}" stroke-width="{sw * 0.7:.1f}"/>')
    return out


# ── option 3: trefoil ───────────────────────────────────────────────────────
TREFOIL = {
    "full":  {"r": 112, "beads": 24, "bead_r": 96, "lobe": 80, "hub": 24,
              "seed": 7, "sw": 2.0},
    "small": {"r": 112, "beads": 0, "bead_r": 0, "lobe": 88, "hub": 30,
              "seed": 0, "sw": 3.4},
}


def lobe_path(R):
    """One clover leaf: narrow where it leaves the hub, broad and round on top."""
    w = R * 0.60
    return (f"M 0,0 "
            f"C {-w:.1f},{-R * 0.22:.1f} {-w * 1.12:.1f},{-R * 0.80:.1f} 0,{-R:.1f} "
            f"C {w * 1.12:.1f},{-R * 0.80:.1f} {w:.1f},{-R * 0.22:.1f} 0,0 Z")


def body_trefoil(detail="full"):
    g = TREFOIL[detail]
    sw = g["sw"]
    out = [f'<circle cx="{C}" cy="{C}" r="{g["r"]}" fill="{W["warmt"]}" '
           f'stroke="{W["ink"]}" stroke-width="{sw}"/>']

    # The chain of beads. It carries the split so the trefoil does not have to:
    # warm above the horizontal, cool below, and the two on the line take the
    # ground, because they are in neither half.
    if g["beads"]:
        n, R = g["beads"], g["bead_r"]
        for i in range(n):
            ang = 360 * i / n
            s = math.sin(math.radians(ang))
            fill = W["ground"] if abs(s) < 1e-9 else (W["coolt"] if s > 0 else W["warmt"])
            out.append(f'<ellipse cx="0" cy="0" rx="13" ry="8" '
                       f'transform="translate({C + R * math.cos(math.radians(ang)):.1f} '
                       f'{C + R * math.sin(math.radians(ang)):.1f}) rotate({ang + 90:.1f})" '
                       f'fill="{fill}" stroke="{W["ink"]}" stroke-width="1.2"/>')

    for ang in (0, 120, 240):
        out.append(f'<path d="{lobe_path(g["lobe"])}" '
                   f'transform="translate({C} {C}) rotate({ang})" fill="{W["ground"]}" '
                   f'stroke="{W["ink"]}" stroke-width="{sw * 0.8:.1f}" stroke-linejoin="round"/>')

    # The flower at the hub, holding the family split: cool above, warm below.
    h = g["hub"]
    out.append(f'<circle cx="{C}" cy="{C}" r="{h}" fill="{W["ground"]}" '
               f'stroke="{W["ink"]}" stroke-width="{sw}"/>')
    out.append(path(half_disc(C, C, h - 4, True), W["cool"]))
    out.append(path(half_disc(C, C, h - 4, False), W["warm"]))
    if g["seed"]:
        out.append(f'<circle cx="{C}" cy="{C}" r="{g["seed"]}" fill="{W["ground"]}" '
                   f'stroke="{W["ink"]}" stroke-width="1.5"/>')
    return out


# ── registry ────────────────────────────────────────────────────────────────
OPTIONS = {
    "dove": {
        "body": body_dove,
        "source": "What a Human Being Is (1910), The Dove No. 12 (1915)",
        "blurb": "A great circle split down the vertical, a heart at the centre "
                 "carrying that split reversed, and a prism fanning up from the "
                 "foot of the circle. The double helix runs the whole height and "
                 "vanishes behind the heart, which is what she does with it.",
        "note": "Reads at 16px as a two-tone disc with a heart in it. The most "
                "legible of the three, and the least abstract.",
    },
    "atom": {
        "body": body_atom,
        "source": "Atom Series No. 8 (1917)",
        "blurb": "A square sheet cut by one diagonal, and where the diagonal "
                 "passes the centre, an orb half lit and half dark inside a "
                 "spiked corona. Her own caption: the atom is in constant change "
                 "between rest and activity.",
        "note": "The only square option, so it fills an avatar tile edge to edge "
                "with no wasted margin. Loses the corona under about 32px.",
    },
    "trefoil": {
        "body": body_trefoil,
        "source": "The Ten Largest, No. 2, Childhood (1907)",
        "blurb": "Three clover lobes on a rose ground, ringed by a chain of "
                 "beads, with a small flower at the hub. The lobes stay calm and "
                 "the bead ring carries the warm and cool split instead.",
        "note": "The most unmistakably hers, and the one least likely to be "
                "mistaken for a chart. Also the busiest at small sizes.",
    },
    "iris": {
        "body": body_iris,
        "source": "Series VIII, Utgångsbild (1920) and The Swan, Group IX/SUW (1915)",
        "blurb": "Two paintings doing one job. The Swan gives the structure, a "
                 "donut split down the middle with a different stack of rings in "
                 "each half. The 1920 sheet gives the fill, an ordered ramp "
                 "running from a hot core out to a pale rim. Here the two halves "
                 "are the same ramp read in opposite directions, so the disc "
                 "inverts across its own axis: pale outside and deep inside on "
                 "the left, the reverse on the right. The line down the middle "
                 "carries on below the rim as the stem she hangs under the disc.",
        "note": "The duality is carried by lightness, not by hue, which is why "
                "the mono plate is not a reduction of this one. Collapse eight "
                "ramp steps to two values and all four quadrants survive. It is "
                "also the only option here whose fill is a validated ordinal "
                "ramp rather than a set of flat picks.",
    },
}


# ── files ───────────────────────────────────────────────────────────────────
def svg(name, scheme=None, detail="full"):
    if scheme is None:
        style = ("\n    " + _vars_all("light") +
                 "\n    @media (prefers-color-scheme: dark) {\n      " +
                 _vars_all("dark") + "\n    }")
    else:
        style = "\n    " + _vars_all(scheme)
    body = "\n    ".join(OPTIONS[name]["body"](detail))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}"
     width="{SIZE}" height="{SIZE}" role="img" aria-labelledby="t">
  <title id="t">infographic, {name}</title>
  <style>{style}
  </style>
  <g>
    {body}
  </g>
</svg>
'''


PAGE_CSS = """
  * { box-sizing: border-box; }
  body { margin: 0; padding: 64px 48px 120px; background: var(--ground); color: var(--ink);
         font-family: ui-sans-serif, -apple-system, "Helvetica Neue", Arial, sans-serif;
         font-size: 15px; line-height: 1.6; }
  .wrap { max-width: 1100px; margin: 0 auto; }
  h1 { font-family: "Instrument Serif", Georgia, serif; font-weight: 400;
       font-size: 52px; line-height: 1.05; margin: 0 0 10px; }
  h2 { font-family: "Instrument Serif", Georgia, serif; font-weight: 400; font-size: 32px;
       margin: 84px 0 4px; }
  .src { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
         color: var(--warm); margin: 0 0 18px; }
  .rule { border: 0; border-top: 1px solid color-mix(in srgb, var(--ink) 16%, transparent);
          margin: 10px 0 22px; }
  p { max-width: 66ch; color: color-mix(in srgb, var(--ink) 78%, transparent); margin: 0 0 14px; }
  code { font-family: ui-monospace, Menlo, monospace; font-size: 13px;
         background: color-mix(in srgb, var(--ink) 7%, transparent);
         padding: 2px 6px; border-radius: 3px; }
  .row { display: flex; flex-wrap: wrap; gap: 28px; align-items: flex-start; }
  .plate { padding: 34px; border-radius: 4px;
           border: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); }
  .plate.light { background: #F2EFE6; }
  .plate.dark  { background: #1F1D1A; }
  .cap { margin-top: 12px; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
         color: color-mix(in srgb, var(--ink) 55%, transparent); }
  .ramp { display: flex; gap: 30px; align-items: flex-end; margin-top: 26px; }
  .ramp figure { margin: 0; text-align: center; }
  .ramp figcaption { margin-top: 10px; font-size: 11px;
                     color: color-mix(in srgb, var(--ink) 55%, transparent); }
  .note { border-left: 2px solid var(--warm); padding-left: 14px; margin-top: 22px;
          font-size: 14px; }
  svg { display: block; }
"""


def page():
    def scope(scheme):
        return " ".join(f"--{k}: {v};" for k, v in
                        list(PALETTES[scheme].items()) + list(RAMPS[scheme].items()))

    dark, mono = scope("dark"), scope("mono")

    def inline(name, px, detail="full"):
        body = "\n      ".join(OPTIONS[name]["body"](detail))
        return (f'<svg viewBox="0 0 {SIZE} {SIZE}" width="{px}" height="{px}" role="img" '
                f'aria-label="{name}">\n      {body}\n    </svg>')

    sections = ""
    for name, o in OPTIONS.items():
        ramp = ""
        for px, d in ((96, "full"), (64, "full"), (48, "full"),
                      (32, "small"), (24, "small"), (16, "small")):
            ramp += (f'<figure>{inline(name, px, d)}'
                     f'<figcaption>{px}px</figcaption></figure>\n        ')
        sections += f'''
  <h2 id="{name}">{name}</h2>
  <p class="src">after {o["source"]}</p>
  <hr class="rule">
  <p>{o["blurb"]}</p>
  <div class="row">
    <div><div class="plate light">{inline(name, 220)}</div><div class="cap">light</div></div>
    <div><div class="plate dark on-dark">{inline(name, 220)}</div><div class="cap">dark</div></div>
    <div><div class="plate light on-mono">{inline(name, 220)}</div><div class="cap">mono</div></div>
  </div>
  <div class="ramp">
        {ramp}
  </div>
  <p class="note">{o["note"]}</p>
'''

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>infographic, three more marks</title>
<style>
  :root {{ {scope("light")} }}
  .on-dark {{ {dark} }}
  .on-mono {{ {mono} }}
{PAGE_CSS}
</style>
</head>
<body>
<div class="wrap">

  <h1>Options for the mark</h1>
  <p>The mandala in <code>assets/logo/</code> is untouched. These are options next
  to it, each traced to a named painting rather than to a style, so the design can
  be argued with.</p>
  <p>The first three reuse the mandala's six colours exactly, so its colour result
  carries over: both schemes clear all six categorical checks in
  <code>scripts/validate_palette.py</code>. The fourth is a ramp rather than a set
  of categories, so it is gated as one, with <code>--ordinal</code>, and it too
  passes on both schemes. It introduces no new hue: its eight steps are struck
  from the same two hue angles as everything above.</p>
  <p>Every mark is SVG driven by CSS custom properties, which is why the same
  source is a live page and a clean vector file. Rebuild with
  <code>python3 assets/logo/gen_options.py</code>.</p>
{sections}
</div>
</body>
</html>
'''


def main():
    os.makedirs(HERE, exist_ok=True)
    files = {"options.html": page()}
    for name in OPTIONS:
        files[f"{name}.svg"] = svg(name)
        files[f"{name}-light.svg"] = svg(name, "light")
        files[f"{name}-dark.svg"] = svg(name, "dark")
        files[f"{name}-mono.svg"] = svg(name, "mono")
        files[f"{name}-small.svg"] = svg(name, None, "small")
        for sc in ("light", "dark", "mono"):
            files[f"{name}-small-{sc}.svg"] = svg(name, sc, "small")
    root = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    for fname, body in sorted(files.items()):
        p = os.path.join(HERE, fname)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
        print(f"  wrote {os.path.relpath(p, root)}  {len(body):,}b")


if __name__ == "__main__":
    main()
