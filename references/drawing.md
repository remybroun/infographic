# The drawing kit

Everything an authored [`figure`](catalog/diagram.md) needs, so hand-drawing is
not from-scratch work.

That matters more than it looks. A `figure` block with no kit means every drawing
starts by re-deriving what a node looks like, what colour an edge is, how big a
label should be. That is slow enough that the author quietly goes back to picking
the nearest catalog block, which is the exact reflex `figure` exists to break. A
kit is not convenience; it is what makes the escape hatch usable often enough to
matter.

---

## The rule that shapes everything here

**Colour is computed, not chosen**, and a hand-drawn figure is where that slips
first. So the build refuses colour literals in a figure's markup:

```
[figure] blocks[3]: 2 colour literal(s) in the drawing.
      fill="#c0392b"
      stroke="rgb(12,12,12)"
```

Allowed paint values are exactly four shapes: `var(--ig-…)`, `currentColor`,
`none` / `transparent`, and `url(#…)`. It is an allow-list rather than a
blacklist of hex patterns on purpose, because a blacklist misses `color-mix()`,
`oklch()`, and whatever Chrome ships next.

Two ways to satisfy it. Prefer the classes.

---

## Classes

Every one of these is themed, so a drawing re-skins with the document instead of
sitting beside it in last month's brand.

### Containers

| Class | What it is |
|---|---|
| `ig-fig-node` | a thing: card surface, hairline border |
| `ig-fig-node-strong` | the emphasised thing: accent wash and accent border |
| `ig-fig-node-mute` | a thing that is present but not the point |
| `ig-fig-field` | a *region* that contains things |
| `ig-fig-field-accent` · `ig-fig-field-danger` | the same, coloured by meaning |
| `ig-fig-solid` · `ig-fig-solid-accent` · `ig-fig-solid-good` · `ig-fig-solid-danger` | filled marks: dots, blocks, arrows |

### Connections

| Class | What it is |
|---|---|
| `ig-fig-edge` | the default connector: axis colour, 1.6px, round caps |
| `ig-fig-edge-strong` | the path that matters: accent, 2.4px |
| `ig-fig-edge-mute` | background structure |
| `ig-fig-edge-danger` | a failure path |
| `ig-fig-edge-dashed` | **conditional or failure only**, never decoration |
| `ig-fig-rule` | a hairline divider inside the drawing |
| `ig-fig-ring` · `-accent` · `-good` · `-danger` | stroke, no fill: blasts, boundaries, highlights |

`ig-fig-edge-dashed` carries the same reservation the linter enforces on
gridlines: dashing means "threshold, conditional, not-real". A dashed line used
for variety makes every future dashed line ambiguous.

### Text

| Class | Size | Use |
|---|---|---|
| `ig-fig-title` | 15px 600 | the name of a thing in the drawing |
| `ig-fig-label` | 12px 500 | an ordinary label |
| `ig-fig-mute` | 10.5px | a qualifier under a label |
| `ig-fig-kicker` | 9.5px 700 caps | a region heading inside the drawing |
| `ig-fig-figure` | 30px 650 | a number that is the point |
| `ig-fig-mono` | 11px mono | identifiers, hostnames, code |

Colour modifiers, combinable with any of the above: `ig-fig-accent`,
`ig-fig-good`, `ig-fig-warn`, `ig-fig-danger`.

Sizes are absolute in the drawing's own user units, not `em`. A figure scales as
a whole, so `em` would make a wide drawing's labels shrink relative to its
shapes.

### Series

`ig-fig-s0` … `ig-fig-s7` fill from the validated categorical palette, in the
same fixed order every chart uses. `ig-fig-stroke-s0` … `-s2` for outlines.

Never generate a ninth. The rule is the same as everywhere else: fold the tail
into "other", facet, or change form.

### Markers

Arrowheads are defined once per document, so use them by reference:

```xml
<line class="ig-fig-edge" x1="0" y1="20" x2="180" y2="20"
      marker-end="url(#ig-arrow)"/>
```

`ig-arrow` · `ig-arrow-accent` · `ig-arrow-mute` · `ig-arrow-danger` · `ig-dot`.
All orient automatically, including on a path that runs right to left.

### Inversion

`"invert": true` on the block puts `ig-fig-invert` on the drawing, which
redefines the ink and surface custom properties so **the same kit classes keep
working on a dark field**. You do not override each shape; you flip the context.

On a continuous document, pair it with `"bleed": true` and the whole section goes
edge to edge in ink. That combination is the single move that most often makes a
document read as designed rather than as laid out. Use it once.

---

## Tokens

When a class does not fit, the raw theme slots are all published as custom
properties, and they work in a presentation attribute:

```xml
<rect fill="var(--ig-sunken)" stroke="var(--ig-accent)"/>
```

| Group | Tokens |
|---|---|
| ink | `--ig-ink` `--ig-secondary` `--ig-muted` |
| surface | `--ig-page` `--ig-card` `--ig-sunken` |
| accent | `--ig-accent` `--ig-accent-text` `--ig-accent-wash` |
| series | `--ig-series-0` … `--ig-series-7` |
| ordinal | `--ig-ordinal-0` … (the one-hue ordered ramp) |
| status | `--ig-good` `--ig-warn` `--ig-danger` `--ig-danger-text` and their washes |
| rules | `--ig-border` `--ig-hairline` `--ig-axis` |
| type | `--ig-sans` `--ig-display` `--ig-mono` |

`opacity` is not a colour and is not policed, so it is the right tool for a
spreading ring or a receding layer.

---

## The Python side

`scripts/lib/svg.py` is the same module every built-in block draws with, and it
is importable. Reach for it when the geometry needs computing rather than typing:
a 50-tile grid, an arc, a curve through points, a scale.

```python
import sys; sys.path.insert(0, "scripts")
from lib import svg
```

| Function | What it gives you |
|---|---|
| `svg.text_width(text, size, weight)` | approximate rendered width; **over-estimates by design**, so labels move out rather than clip |
| `svg.truncate(text, size, max_width)` | ellipsize to fit |
| `svg.wrap(text, size, max_width, max_lines)` | greedy word wrap into lines |
| `svg.Linear(d0, d1, r0, r1)` | continuous scale, domain to range |
| `svg.Band(count, r0, r1, padding)` | discrete scale, like `d3.scaleBand` |
| `svg.nice_ticks(lo, hi)` · `svg.extent(values)` | axis maths that never crosses zero by accident |
| `svg.arc_path(cx, cy, r_out, r_in, a0, a1)` | a ring segment; 0 is 12 o'clock |
| `svg.smooth_path(points)` · `svg.polyline_path(points)` | curves and polylines |
| `svg.ribbon_path(...)` | a flow band with bezier sides |
| `svg.bar_path(x, y, w, h, r, end)` | a bar rounded **only** at the data end |
| `svg.fmt_compact` · `fmt_plain` · `fmt_delta` | number formatting matching the rest of the document |
| `svg.esc(value)` | XML-escape anything caller-supplied |

Generate the markup, write it into the spec's `svg` key, and keep the generator
script next to the spec. A figure computed by a script that no longer exists is
a figure nobody can adjust.

One caution: **never recover a width by subtracting padding back off a total.**
`(w + 26) - 26 != w` in floating point, and a chip sized to fit its own label
came out ellipsized because of exactly that. Carry the inner width; do not
re-derive it.

---

## Worked patterns

Four shapes that recur once you are drawing rather than picking. All four are in
`fixtures/specs/scroll-architecture.json` as live examples.

### Convergence, many things becoming one

Bezier curves from evenly spaced left-hand y positions to a single point, one of
them emphasised. The emphasised path is the reader's entry point; without it the
eye has nowhere to start.

```xml
<path class="ig-fig-edge-mute" d="M0,54 C220,54 300,190 470,190" fill="none"/>
<path class="ig-fig-edge"      d="M0,198 C220,198 300,190 470,190" fill="none"/>
```

### Attenuation, a quantity thinning as it goes

One filled polygon whose half-height at each stage is proportional to the value.
Two stage lines, the labels above and the figures below. This is what a `sankey`
gets wrong when there is no branching: it draws plumbing when the point is
narrowing.

### Containment, a boundary that means something

A `ig-fig-field` rectangle with the contained marks inside it, and the excluded
thing drawn *outside*, touching the edge. The gap between them is the claim.
Label the boundary, not the contents.

### Spread, reach from a single point

Concentric `ig-fig-ring-danger` circles at decreasing opacity, centred on the
compromised mark. Restraint matters here: three rings read as spread, six read as
a target.

---

## What a figure still owes

Nothing in this document relaxes any of it:

- **`alt`**, one sentence saying what the picture shows. Required.
- **`encodes`**, `"concept"`, or `{"columns": …, "rows": …}` which renders the
  table twin. Required, and it decides whether the values are reachable by
  someone who cannot see the drawing.
- **The word budget**, text inside `<text>` is charged as `figure_text`, capped
  at 40 words at graphic density, a third of a whole page's allowance. A drawing
  labels; it does not narrate. Sentences belong in the block's own `title` and
  `subtitle`.
- **The cap**, three per document. See [scenes.md](scenes.md).
- **Being looked at**, `python3 scripts/ig.py shoot out/doc.html` renders it to
  PNGs. Nothing in the linter can see a collision.
