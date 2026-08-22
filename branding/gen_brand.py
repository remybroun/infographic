#!/usr/bin/env python3
"""
The infographic mark, generated. This directory is the canonical identity.

    python3 branding/gen_brand.py

The mark is called the iris: a disc split down the middle, with an ordered
colour ramp in each half, and the two halves running that ramp in opposite
directions. Pale at the rim and deep at the core on the left; the reverse on
the right. The centre pip repeats the rim rather than the core, so reading
inward on either side gives pale, deep, pale, an alternation rather than a
gradient. The line down the middle is the axis the ramp reverses across, and
below the rim it carries on as a stem.

It is drawn from two paintings, and both are load-bearing:

  * Hilma af Klint, The Swan, Group IX/SUW (1915), for the structure: a donut
    split down the middle with a different stack of rings in each half.
  * Hilma af Klint, Series VIII, Utgångsbild (1920), for the fill: an ordered
    ramp running from a hot core out to a pale rim.

Why an inversion rather than a hue contrast: the duality is then carried by
lightness, so collapsing the eight ramp steps to two values leaves all four
quadrants intact. The mono plate is not a degraded version of this mark, it is
the same drawing. That is also why it survives to 16px, where the small variant
drops to two bands, the fewest that can still show an inversion.

Two kinds of SVG come out of here, and the difference matters:

  * iris.svg and iris-small.svg carry CSS custom properties and a
    prefers-color-scheme query, so one file follows the viewer. Use these on the
    web and in anything that renders SVG properly.
  * Every other file has its colours written out as literal hex. GitHub strips
    <style> from SVG when it renders README images, which would resolve every
    var() to nothing and paint the whole mark black. The flattened files are
    what the README points at.

Exploratory work, including the mandala and three rejected marks, lives under
assets/logo/ and is not the identity. This directory is.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The line under the wordmark. It is a claim about what the tool is for, not a
# description of what it runs on: the thing being made is a representation, and
# the work is finding the shape a subject already has rather than decorating it.
# Four words, no verb to spare, and it survives being set in caps at 24px.
SLOGAN = "Give the world a shape"

# ── palette ─────────────────────────────────────────────────────────────────
# Ground and ink only. The mark's own colour is in RAMPS.
BASE = {
    "light": {"ground": "#F2EFE6", "ink": "#1F1D1A"},
    "dark":  {"ground": "#1F1D1A", "ink": "#F2EFE6"},
    "mono":  {"ground": "#F2EFE6", "ink": "#1F1D1A"},
}

# Four steps per side, both struck from the same two hue angles, 39.9 and 251.1
# degrees in OKLCH. No new hue enters the identity, only new steps along two
# that were already there.
#
# These are ordered ramps, not categories, so they are gated as ramps. The
# categorical checks fail a correct ramp by design: it spans the lightness band,
# and its pale steps drop under the chroma floor. Re-verify after any edit:
#
#   python3 scripts/validate_palette.py "#451A0B,#893411,#B66346,#CE9581" --ordinal --surface "#F2EFE6"
#   python3 scripts/validate_palette.py "#082A4A,#065494,#4481BF,#82A8D3" --ordinal --surface "#F2EFE6"
#   python3 scripts/validate_palette.py "#84432D,#B75D3D,#D4896F,#E7B8A7" --ordinal --surface "#1F1D1A" --mode dark
#   python3 scripts/validate_palette.py "#2B5A8B,#3A7DC1,#6EA3DB,#A8C8EA" --ordinal --surface "#1F1D1A" --mode dark
#
# All four pass: single hue, monotone lightness, every adjacent gap over the
# 0.06 floor, and the pale end still clearing the surface.
#
# The dark ramps sit higher up the lightness scale than the light ones on
# purpose. In dark mode it is the *dark* end that has to clear the surface, and
# an L of 0.40 against #1F1D1A only reaches 1.76:1, under the 2.0 floor.
RAMPS = {
    "light": {"w1": "#451A0B", "w2": "#893411", "w3": "#B66346", "w4": "#CE9581",
              "c1": "#082A4A", "c2": "#065494", "c3": "#4481BF", "c4": "#82A8D3"},
    "dark":  {"w1": "#84432D", "w2": "#B75D3D", "w3": "#D4896F", "w4": "#E7B8A7",
              "c1": "#2B5A8B", "c2": "#3A7DC1", "c3": "#6EA3DB", "c4": "#A8C8EA"},
    # Two values instead of eight, split at the middle of each ramp.
    "mono":  {"w1": "#1F1D1A", "w2": "#1F1D1A", "w3": "#F2EFE6", "w4": "#F2EFE6",
              "c1": "#1F1D1A", "c2": "#1F1D1A", "c3": "#F2EFE6", "c4": "#F2EFE6"},
}

SCHEMES = {s: {**BASE[s], **RAMPS[s]} for s in BASE}

# ── geometry ────────────────────────────────────────────────────────────────
SIZE = 240
C = SIZE / 2

DETAIL = {
    "full":  {"cy": 104, "bands": [92, 69, 46, 23], "pip": 9, "stem": 234, "sw": 2.2},
    # Two bands, no pip, no stem, disc re-centred and grown to fill the tile.
    # The inversion is the whole idea and two bands is the fewest that can show
    # one, so this is the mark reduced to its argument and nothing else.
    "small": {"cy": 120, "bands": [106, 56], "pip": 0, "stem": 0, "sw": 3.8},
}


def half_disc_v(cx, cy, r, left):
    """Half a circle, cut vertically."""
    if left:
        return f"M {cx},{cy - r} A {r},{r} 0 0 0 {cx},{cy + r} Z"
    return f"M {cx},{cy - r} A {r},{r} 0 0 1 {cx},{cy + r} Z"


def half_annulus(cx, cy, ro, ri, left):
    """Half a ring. ri = 0 gives a half disc, which is what the core band is."""
    if ri <= 0:
        return half_disc_v(cx, cy, ro, left)
    a, b = (0, 1) if left else (1, 0)
    return (f"M {cx},{cy - ro} A {ro},{ro} 0 0 {a} {cx},{cy + ro} "
            f"L {cx},{cy + ri} A {ri},{ri} 0 0 {b} {cx},{cy - ri} Z")


def mark_body(detail="full"):
    """Every element of the mark, using var(--x) for colour. Flattened later."""
    g = DETAIL[detail]
    cy, bands, sw = g["cy"], g["bands"], g["sw"]
    r, n = bands[0], len(bands)
    out = []

    # Rim to core. With n bands, take n evenly spaced steps out of the four, so
    # the small variant uses the two extremes and nothing in between.
    steps = [round(i * 3 / (n - 1)) for i in range(n)]
    for i, ro in enumerate(bands):
        ri = bands[i + 1] if i + 1 < n else 0
        out.append(f'<path d="{half_annulus(C, cy, ro, ri, True)}" fill="var(--w{4 - steps[i]})"/>')
        out.append(f'<path d="{half_annulus(C, cy, ro, ri, False)}" fill="var(--c{steps[i] + 1})"/>')

    # Every boundary ruled, so the bands stay countable when two of them
    # collapse to the same value under the mono scheme.
    for i, br in enumerate(bands):
        out.append(f'<circle cx="{C}" cy="{cy}" r="{br}" fill="none" '
                   f'stroke="var(--ink)" stroke-width="{sw if i == 0 else sw * 0.6:.2f}"/>')

    out.append(f'<line x1="{C}" y1="{cy - r}" x2="{C}" y2="{g["stem"] or cy + r}" '
               f'stroke="var(--ink)" stroke-width="{sw * 0.8:.2f}" stroke-linecap="round"/>')

    if g["pip"]:
        p = g["pip"]
        out.append(f'<path d="{half_disc_v(C, cy, p, True)}" fill="var(--w4)"/>')
        out.append(f'<path d="{half_disc_v(C, cy, p, False)}" fill="var(--c1)"/>')
        out.append(f'<circle cx="{C}" cy="{cy}" r="{p}" fill="none" '
                   f'stroke="var(--ink)" stroke-width="1.2"/>')
    return out


# ── emit ────────────────────────────────────────────────────────────────────
def flatten(svg_body, scheme):
    """Write the colours out as literal hex.

    GitHub strips <style> from SVG when rendering README images. A file that
    keeps its custom properties resolves every var() to nothing there and paints
    solid black, which is how this mark would have shipped if it were never
    opened on github.com.
    """
    table = SCHEMES[scheme]
    return re.sub(r"var\(--(\w+)\)", lambda m: table[m.group(1)], svg_body)


def _vars(scheme, selector=":root"):
    return f"{selector} {{ {' '.join(f'--{k}: {v};' for k, v in SCHEMES[scheme].items())} }}"


def mark_svg(scheme=None, detail="full"):
    body = "\n    ".join(mark_body(detail))
    if scheme is None:
        style = (f"\n    {_vars('light')}"
                 f"\n    @media (prefers-color-scheme: dark) {{\n      {_vars('dark')}\n    }}")
    else:
        style, body = "", flatten(body, scheme)
    style = f"\n  <style>{style}\n  </style>" if style else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}"
     width="{SIZE}" height="{SIZE}" role="img" aria-labelledby="t">
  <title id="t">infographic</title>{style}
  <g>
    {body}
  </g>
</svg>
'''


LOCKUP_W, LOCKUP_H = 780, 240


def lockup_svg(scheme="light"):
    """Mark plus wordmark.

    The type is set with presentation attributes, not CSS classes, for the same
    sanitiser reason as flatten(). The wordmark is live text, so on a machine
    without Instrument Serif it falls back to Georgia.
    """
    p = SCHEMES[scheme]
    body = flatten("\n    ".join(mark_body("full")), scheme)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOCKUP_W} {LOCKUP_H}"
     width="{LOCKUP_W}" height="{LOCKUP_H}" role="img" aria-labelledby="t">
  <title id="t">infographic</title>
  <g>
    {body}
  </g>
  <text x="272" y="118" fill="{p['ink']}" font-size="96"
        font-family="Instrument Serif, Georgia, Times New Roman, serif">infographic</text>
  <text x="276" y="176" fill="{p['w2']}" font-size="24" letter-spacing="3.4"
        font-family="Helvetica Neue, Arial, sans-serif">{SLOGAN.upper()}</text>
</svg>
'''


def main():
    files = {
        "iris.svg": mark_svg(),                      # follows the viewer
        "iris-light.svg": mark_svg("light"),
        "iris-dark.svg": mark_svg("dark"),
        "iris-mono.svg": mark_svg("mono"),
        "iris-small.svg": mark_svg(None, "small"),
        "iris-small-light.svg": mark_svg("light", "small"),
        "iris-small-dark.svg": mark_svg("dark", "small"),
        "iris-small-mono.svg": mark_svg("mono", "small"),
        "lockup-light.svg": lockup_svg("light"),
        "lockup-dark.svg": lockup_svg("dark"),
    }
    for name, body in files.items():
        path = os.path.join(HERE, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        print(f"  wrote {os.path.relpath(path, ROOT)}  {len(body):,}b")


if __name__ == "__main__":
    main()
