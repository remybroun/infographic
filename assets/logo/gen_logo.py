#!/usr/bin/env python3
"""
The mandala, generated. Superseded, and kept.

This was the first mark. It is no longer the identity: the mark that shipped is
the iris, in branding/. This file stays because the reasoning in it is still
worth reading and because the mandala is still the better answer to a different
question, one where the mark can be large and ornamental. It is not the answer
to this one.

One geometry, four outputs: the standalone SVGs, and an HTML page that shows
them with the same colours bound to CSS custom properties. Nothing is typed
twice, so the page and the exported files cannot drift.

    python3 assets/logo/gen_logo.py

The design, stated so it can be argued with:

  * Anthropic's visual language, not its mark: a cream ground, one warm clay
    accent, flat fills, no gradients, and geometry that radiates from a centre.
  * Hilma af Klint's grammar: a mandala inside an enclosing circle, two orders
    of petal, and a duality split across the horizontal axis, warm above and
    cool below, with the heart carrying that duality reversed.
  * The two petals that land exactly on the axis belong to neither half, so
    they are drawn as outline and left unfilled.

Colours are not chosen by eye. Both schemes pass all six checks in
scripts/validate_palette.py; see PALETTES for the exact command.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ── palette ─────────────────────────────────────────────────────────────────
# Verified with, and re-verify after any edit:
#   python3 scripts/validate_palette.py "#C15F3C,#1F5C97" --surface "#F2EFE6" --pairs all
#   python3 scripts/validate_palette.py "#CE7454,#3F86C6" --surface "#1F1D1A" --pairs all --mode dark
PALETTES = {
    "light": {
        "ground": "#F2EFE6",   # cream
        "ink":    "#1F1D1A",   # warm near-black, all linework
        "warm":   "#C15F3C",   # clay, the upper half
        "warmt":  "#E2A88E",   # clay tint, the minor petals above
        "cool":   "#1F5C97",   # blue, the lower half
        "coolt":  "#8FB0CE",   # blue tint, the minor petals below
    },
    "dark": {
        "ground": "#1F1D1A",
        "ink":    "#F2EFE6",
        "warm":   "#CE7454",
        "warmt":  "#8A4C36",
        "cool":   "#3F86C6",
        "coolt":  "#2A4E70",
    },
    # One ink, so the duality cannot be carried by hue. It is carried by
    # filled against unfilled instead, which is af Klint's own solution and
    # the only one that survives a rubber stamp or a fax.
    "mono": {
        "ground": "#F2EFE6",
        "ink":    "#1F1D1A",
        "warm":   "#1F1D1A",   # upper half, solid
        "warmt":  "#F2EFE6",   # its minor petals, outline only
        "cool":   "#F2EFE6",   # lower half, outline only
        "coolt":  "#F2EFE6",
    },
}

# ── geometry ────────────────────────────────────────────────────────────────
SIZE = 240
C = SIZE / 2

# full detail: 12 major petals and 12 minor, offset by half a step.
# small detail: 6 major only, for anything under about 32px.
DETAIL = {
    "full":  {"major": 12, "minor": 12, "r_in": 34, "r_major": 97, "r_minor": 70,
              "w_major": 13.5, "w_minor": 9.0, "ring": 108, "heart": 30, "seed": 8},
    # Six, not eight: at eight, two petals land on the horizontal axis and are
    # drawn unfilled, which at 16px is two blank gaps spending the budget of two
    # petals. Six puts three in each half and none on the axis.
    "small": {"major": 6,  "minor": 0,  "r_in": 30, "r_major": 96, "r_minor": 0,
              "w_major": 22.0, "w_minor": 0.0, "ring": 0, "heart": 34, "seed": 0},
}


def petal(angle_deg, r_in, r_out, half_w):
    """One teardrop: wide at the base, tapering to a point at the tip.

    Built pointing up from the centre, then rotated. Two cubics, mirrored,
    so the petal is symmetric about its own spine.
    """
    span = r_out - r_in
    shoulder = r_in + span * 0.30      # where the petal is widest
    neck = r_out - span * 0.16         # where it starts closing to a point
    d = (f"M 0,{-r_in:.2f} "
         f"C {half_w * 1.05:.2f},{-shoulder:.2f} {half_w:.2f},{-neck:.2f} 0,{-r_out:.2f} "
         f"C {-half_w:.2f},{-neck:.2f} {-half_w * 1.05:.2f},{-shoulder:.2f} 0,{-r_in:.2f} Z")
    return d, f"translate({C} {C}) rotate({angle_deg})"


def half_disc(r, upper):
    """The heart's two halves. SVG y grows downward, so 'upper' sweeps left."""
    if upper:
        return f"M {C - r},{C} A {r},{r} 0 0 1 {C + r},{C} Z"
    return f"M {C + r},{C} A {r},{r} 0 0 1 {C - r},{C} Z"


def _rotations(count, offset):
    """The rotate() values, which are not directions. See _side."""
    return [offset + i * (360 / count) for i in range(count)]


def _side(rotation_deg):
    """Which half a petal points into: 'warm' above, 'cool' below, None on the axis.

    A petal is built pointing up, so rotate(r) aims it at direction r - 90.
    Reading the rotation as if it were the direction turns the whole split a
    quarter turn, which is exactly how the first render of this file came out.
    """
    s = math.sin(math.radians(rotation_deg - 90))
    if abs(s) < 1e-9:
        return None
    return "warm" if s < 0 else "cool"


def mark_body(detail="full"):
    """Every element of the mark, as SVG source, using var(--x) for colour."""
    g = DETAIL[detail]
    out = []

    if g["ring"]:
        out.append(f'<circle cx="{C}" cy="{C}" r="{g["ring"]}" fill="none" '
                   f'stroke="var(--ink)" stroke-width="2"/>')
        # Cardinal marks. Top and bottom name the two halves; the two on the
        # axis are ink, because the axis belongs to neither half.
        for angle, fill in ((-90, "var(--warm)"), (90, "var(--cool)"),
                            (0, "var(--ink)"), (180, "var(--ink)")):
            r = g["ring"]
            x = C + r * math.cos(math.radians(angle))
            y = C + r * math.sin(math.radians(angle))
            rad = 5 if angle in (-90, 90) else 3.5
            # Stroked, so that a dot filled with the ground colour reads as an
            # open circle rather than as a bite taken out of the ring. That is
            # what the mono scheme does with the lower half.
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{rad}" fill="{fill}" '
                       f'stroke="var(--ink)" stroke-width="1.2"/>')

    # Minor petals sit under the major ones, offset by half a step. The major
    # order takes the un-offset angles, so a long petal points straight up and
    # straight down onto the cardinal dots, and the two petals that land on the
    # horizontal axis, belonging to neither half, are long enough to be read.
    if g["minor"]:
        step = 360 / g["minor"]
        for angle in _rotations(g["minor"], step / 2):
            side = _side(angle)
            d, tf = petal(angle, g["r_in"], g["r_minor"], g["w_minor"])
            if side is None:
                fill, stroke = "var(--ground)", "var(--ink)"
            else:
                fill = "var(--warmt)" if side == "warm" else "var(--coolt)"
                stroke = "var(--ink)"
            out.append(f'<path d="{d}" transform="{tf}" fill="{fill}" '
                       f'stroke="{stroke}" stroke-width="1" stroke-linejoin="round"/>')

    for angle in _rotations(g["major"], 0):
        side = _side(angle)
        # None means the petal lies exactly on the split. It is in neither
        # half, so it is given the ground and reads as outline only.
        fill = {"warm": "var(--warm)", "cool": "var(--cool)",
                None: "var(--ground)"}[side]
        d, tf = petal(angle, g["r_in"], g["r_major"], g["w_major"])
        out.append(f'<path d="{d}" transform="{tf}" fill="{fill}" '
                   f'stroke="var(--ink)" stroke-width="1.2" stroke-linejoin="round"/>')

    # The heart, carrying the duality reversed: cool above, warm below.
    out.append(f'<circle cx="{C}" cy="{C}" r="{g["heart"]}" fill="var(--ground)" '
               f'stroke="var(--ink)" stroke-width="2"/>')
    inner = g["heart"] - 4
    out.append(f'<path d="{half_disc(inner, True)}" fill="var(--cool)"/>')
    out.append(f'<path d="{half_disc(inner, False)}" fill="var(--warm)"/>')
    if g["seed"]:
        out.append(f'<circle cx="{C}" cy="{C}" r="{g["seed"]}" fill="var(--ground)" '
                   f'stroke="var(--ink)" stroke-width="1.5"/>')
    return "\n    ".join(out)


# ── svg files ───────────────────────────────────────────────────────────────
def _vars(scheme, selector=":root"):
    p = PALETTES[scheme]
    body = " ".join(f"--{k}: {v};" for k, v in p.items())
    return f"{selector} {{ {body} }}"


def mark_svg(scheme=None, detail="full", title="infographic"):
    """A standalone mark. scheme=None emits one file that follows the viewer."""
    if scheme is None:
        style = ("\n    " + _vars("light") +
                 "\n    @media (prefers-color-scheme: dark) {\n      " +
                 _vars("dark") + "\n    }")
    else:
        style = "\n    " + _vars(scheme)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}"
     width="{SIZE}" height="{SIZE}" role="img" aria-labelledby="t">
  <title id="t">{title}</title>
  <style>{style}
  </style>
  <g>
    {mark_body(detail)}
  </g>
</svg>
'''


LOCKUP_W, LOCKUP_H = 760, 240


def lockup_svg(scheme="light"):
    """Mark plus wordmark. The wordmark is live text, so the font must resolve."""
    p = PALETTES[scheme]
    body = mark_body("full")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOCKUP_W} {LOCKUP_H}"
     width="{LOCKUP_W}" height="{LOCKUP_H}" role="img" aria-labelledby="t">
  <title id="t">infographic</title>
  <style>
    {_vars(scheme)}
    .word {{ font-family: "Instrument Serif", Georgia, "Times New Roman", serif;
             font-weight: 400; font-size: 96px; fill: var(--ink); }}
    .tag  {{ font-family: ui-sans-serif, "Helvetica Neue", Arial, sans-serif;
             font-size: 24px; letter-spacing: 0.14em; fill: var(--warm);
             text-transform: uppercase; }}
  </style>
  <g>
    {body}
  </g>
  <text class="word" x="272" y="118">infographic</text>
  <text class="tag" x="276" y="176">give the world a shape</text>
</svg>
'''


# ── the page ────────────────────────────────────────────────────────────────
PAGE_CSS = """
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 64px 48px 96px;
    background: var(--ground); color: var(--ink);
    font-family: ui-sans-serif, -apple-system, "Helvetica Neue", Arial, sans-serif;
    font-size: 15px; line-height: 1.6;
  }
  .wrap { max-width: 1040px; margin: 0 auto; }
  h1 { font-family: "Instrument Serif", Georgia, serif; font-weight: 400;
       font-size: 52px; line-height: 1.05; margin: 0 0 8px; letter-spacing: -0.01em; }
  h2 { font-family: ui-sans-serif, Arial, sans-serif; font-size: 12px; font-weight: 600;
       letter-spacing: 0.16em; text-transform: uppercase; color: var(--warm);
       margin: 72px 0 20px; padding-bottom: 8px;
       border-bottom: 1px solid color-mix(in srgb, var(--ink) 16%, transparent); }
  p  { max-width: 62ch; color: color-mix(in srgb, var(--ink) 78%, transparent); margin: 0 0 14px; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px;
         background: color-mix(in srgb, var(--ink) 7%, transparent);
         padding: 2px 6px; border-radius: 3px; }
  .row { display: flex; flex-wrap: wrap; gap: 32px; align-items: flex-end; }
  .plate { padding: 40px; border-radius: 4px;
           border: 1px solid color-mix(in srgb, var(--ink) 14%, transparent); }
  .plate.light { background: #F2EFE6; }
  .plate.dark  { background: #1F1D1A; }
  .cap { margin-top: 14px; font-size: 12px; letter-spacing: 0.06em;
         text-transform: uppercase; color: color-mix(in srgb, var(--ink) 55%, transparent); }
  .ramp { display: flex; gap: 36px; align-items: flex-end; }
  .ramp figure { margin: 0; text-align: center; }
  .ramp figcaption { margin-top: 10px; font-size: 11px;
                     color: color-mix(in srgb, var(--ink) 55%, transparent); }
  .sw { display: flex; flex-wrap: wrap; gap: 14px; }
  .sw div { width: 152px; }
  .chip { height: 68px; border-radius: 3px;
          border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent); }
  .name { margin-top: 8px; font-size: 12px; font-weight: 600; }
  .hex  { font-family: ui-monospace, Menlo, monospace; font-size: 12px;
          color: color-mix(in srgb, var(--ink) 58%, transparent); }
  .pass { color: var(--cool); font-weight: 600; }
  .super { border-left: 3px solid var(--warm); padding: 10px 0 10px 14px;
           background: color-mix(in srgb, var(--warm) 7%, transparent); }
  svg { display: block; }
"""


def page():
    light = _vars("light")
    dark_scope = " ".join(f"--{k}: {v};" for k, v in PALETTES["dark"].items())
    mono_scope = " ".join(f"--{k}: {v};" for k, v in PALETTES["mono"].items())

    def inline(cls, px, detail="full"):
        return (f'<svg class="{cls}" viewBox="0 0 {SIZE} {SIZE}" width="{px}" height="{px}" '
                f'role="img" aria-label="infographic mark">\n    {mark_body(detail)}\n  </svg>')

    swatches = ""
    for name, hexv, label in (
        ("ground", PALETTES["light"]["ground"], "cream, the ground"),
        ("ink", PALETTES["light"]["ink"], "warm near-black, all linework"),
        ("warm", PALETTES["light"]["warm"], "clay, the upper half"),
        ("warmt", PALETTES["light"]["warmt"], "clay tint, minor petals"),
        ("cool", PALETTES["light"]["cool"], "blue, the lower half"),
        ("coolt", PALETTES["light"]["coolt"], "blue tint, minor petals"),
    ):
        swatches += (f'<div><div class="chip" style="background:{hexv}"></div>'
                     f'<div class="name">{name}</div><div class="hex">{hexv}</div>'
                     f'<div class="hex">{label}</div></div>\n      ')

    ramp = ""
    for px, detail in ((128, "full"), (64, "full"), (48, "full"),
                       (32, "small"), (24, "small"), (16, "small")):
        ramp += (f'<figure>{inline("m", px, detail)}'
                 f'<figcaption>{px}px · {detail}</figcaption></figure>\n      ')

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>infographic, the mandala</title>
<style>
  :root {{ {" ".join(f"--{k}: {v};" for k, v in PALETTES["light"].items())} }}
  .on-dark {{ {dark_scope} }}
  .on-mono {{ {mono_scope} }}
{PAGE_CSS}
</style>
</head>
<body>
<div class="wrap">

  <h1>The mandala</h1>
  <p class="super"><strong>Superseded.</strong> This was the first mark. The one
  that shipped is the iris, in <code>branding/</code>, and that is the identity.
  This page is kept as a record of the reasoning, not as a source of assets.</p>
  <p>The mandala is Anthropic's visual language, which is a cream ground,
  one clay accent, flat fills and geometry that radiates from a centre, drawn in
  Hilma af Klint's grammar, which is an enclosing circle, two orders of petal, and
  a duality split across the horizontal axis. Warm above, cool below. The heart
  carries the same duality reversed. The two petals that land exactly on the axis
  belong to neither half, so they are left unfilled.</p>
  <p>What it could not do is get small. Twenty-four petals turn to mush below
  about 32px, and the fix below, dropping to six fat petals, keeps the split but
  throws away the ornament that made it worth drawing. The iris carries its
  duality in lightness instead of in shape, so it loses nothing on the way down.
  That is why it won.</p>

  <h2>The mandala</h2>
  <div class="row">
    <div>
      <div class="plate light">{inline("m", 240)}</div>
      <div class="cap">light</div>
    </div>
    <div>
      <div class="plate dark on-dark">{inline("m", 240)}</div>
      <div class="cap">dark</div>
    </div>
    <div>
      <div class="plate light on-mono">{inline("m", 240)}</div>
      <div class="cap">mono, for one-colour print</div>
    </div>
  </div>

  <h2>Down to a favicon</h2>
  <p>Twenty-four petals turn to mush below about 32px, so the small variant drops
  the minor ring, the enclosing circle and the seed, keeps six fat petals and
  grows the heart. The split survives; the ornament does not have to.</p>
  <div class="ramp">
      {ramp}
  </div>

  <h2>Lockup</h2>
  <div class="plate light">
    <div style="display:flex; align-items:center; gap:36px;">
      {inline("m", 132)}
      <div>
        <div style="font-family:'Instrument Serif',Georgia,serif; font-size:64px; line-height:1;">infographic</div>
        <div style="font-size:14px; letter-spacing:0.14em; text-transform:uppercase; color:var(--warm); margin-top:10px;">give the world a shape</div>
      </div>
    </div>
  </div>

  <h2>Palette</h2>
  <p>Not picked by eye. Both schemes clear all six checks in
  <code>scripts/validate_palette.py</code>: lightness band, chroma floor, CVD
  separation, normal-vision floor, and contrast against the ground.
  Clay against blue measures <span class="pass">ΔE 17.9 for a protanope</span>,
  which is why the duality is warm and cool rather than two warms.</p>
  <div class="sw">
      {swatches}
  </div>

  <h2>Export</h2>
  <p>Every shape here is SVG driven by CSS custom properties, so the same source
  is a live themeable page and a clean vector file. Regenerate both with
  <code>python3 assets/logo/gen_logo.py</code>.</p>
  <p>For anything you actually intend to ship, use <code>branding/</code>
  instead. Those files have their colours written out as literal hex, because a
  file that keeps its custom properties renders solid black anywhere the host
  strips <code>&lt;style&gt;</code>, GitHub included.</p>

</div>
</body>
</html>
'''


# ── write ───────────────────────────────────────────────────────────────────
def main():
    files = {
        "mark.svg": mark_svg(None),
        "mark-light.svg": mark_svg("light"),
        "mark-dark.svg": mark_svg("dark"),
        "mark-mono.svg": mark_svg("mono"),
        "mark-small.svg": mark_svg(None, detail="small"),
        "mark-small-light.svg": mark_svg("light", detail="small"),
        "mark-small-dark.svg": mark_svg("dark", detail="small"),
        "mark-small-mono.svg": mark_svg("mono", detail="small"),
        "lockup-light.svg": lockup_svg("light"),
        "lockup-dark.svg": lockup_svg("dark"),
        "logo.html": page(),
    }
    for name, body in files.items():
        path = os.path.join(HERE, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        print(f"  wrote {os.path.relpath(path, os.path.dirname(os.path.dirname(HERE)))}"
              f"  {len(body):,}b")


if __name__ == "__main__":
    main()
