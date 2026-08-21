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

**Which is why the viewbox width has to be near the real column width.** The
drawing is laid out in user units and then scaled to fit its column, so the
scale factor lands on the type too. A `viewbox` of `0 0 1080 300` in a 640px
column shrinks by 0.59, and every 12px `ig-fig-label` above renders at 7px. The
sizes in that table are only true at 1:1.

| Target and span | Roughly the column | So author at |
|---|---|---|
| A4, span 12 | 640 | `0 0 640 …` |
| A4, span 6 | 310 | `0 0 310 …` |
| A3 or a4-land, span 12 | 950 | `0 0 950 …` |
| `scroll`, span 12 | 1080 | `0 0 1080 …` |
| `scroll` with `bleed` | the viewport | 1440 is a fair guess |

Those are approximations, and the only real check is to render and look. Being
wrong the other way is milder but still wrong: a 320-unit drawing in a
640px column doubles, and a 1.6px hairline edge becomes a 3.2px rule. Either
way the tell is the same, so look at it: type that is too small or strokes that
are too heavy mean the viewbox and the column disagree.

`sketch` does both halves of that in one go: it renders the block alone at its
real column width, and it prints the scale factor when the two disagree.

```bash
python3 scripts/ig.py sketch out/spec.json --id beam
```
```
[sketch] out/sketches/spec-06-beam.png   1160px wide, 335px tall
         viewbox is 1080 units wide in a 530px column, so it scales by 0.49:
         a 12px ig-fig-label renders at 5.9px and a 1.6px hairline at 0.8px.
         Author at "viewbox": "0 0 530 …" instead.
```

Add `--span 6` to try the drawing at another width without editing the spec, and
`--height` when a tall figure fills the window and gets cut off.

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

## Pictograms: when the subject has a shape

Everything above this line is abstract. Nodes, edges, fields, rings: the
vocabulary of containment, convergence and spread, which is what most documents
worth drawing are about.

Some are not. A document about apartments, or people, or aeroplanes has a
subject with a shape, and the abstract vocabulary quietly forces a translation
on it: "properties by city" becomes a bar chart because a bar is what the kit
has. So there is a library of fifty-two silhouettes on the same 24-unit grid.

```bash
python3 scripts/ig.py pictograms                    # every name, grouped
python3 scripts/ig.py pictograms --sheet out/p.pdf  # all of them drawn, to look at
```

```
place     home building apartment city door key bed map_pin globe
people    person people group
travel    suitcase plane car calendar clock
money     money coins card chart
document  document folder envelope chat phone bell
tech      laptop server cloud database lock shield gear wifi
mark      check cross warning star heart plus arrow_right flag search eye
thing     box tool tree sun leaf bolt layers
```

Four places take them, and every one is opt-in. Nothing changes if you never
name one:

```xml
<use href="#ig-pic-home" x="0" y="0" width="40" height="40" class="ig-fig-solid-accent"/>
```
```json
{"type": "unit", "glyph": "person", "parts": [ … ]}
{"type": "pictogram", "glyph": "apartment", "unit_value": 500, "rows": [ … ]}
{"type": "chips", "items": [{"label": "Keys issued", "icon": "key"}]}
```

They carry no `fill` of their own, so a pictogram takes the colour of wherever
it is placed. That is why a `<use>` with a kit class works inside a `figure`
without the colour-literal check having anything to object to: there is no
colour in the symbol to be a literal.

### Deciding, which is the part that matters

**This is a judgement and it stays yours.** Nothing in the skill asks for a
pictogram, no check warns when one is absent, and the defaults are what they
were before the library existed. Most documents should not use it. The reason
the library did not exist for three versions is that pictograms are the fastest
route to a document that looks cheap, and clip-art infographics are a real
genre with real conventions, all of them bad.

The test is the one this skill applies to everything else. **Cover the picture.
If nothing was lost, it was decoration**, and decoration that takes space is
worse than the plain mark it replaced.

In practice a drawn subject earns its place when one of these is true:

| Signal | Example |
|---|---|
| Recognising the symbol says something the label does not | a row of people, so the unit is obviously human |
| The document is *about* the object, not about a quantity of it | keys, doors, buildings as the actors in a figure |
| Two units are being counted side by side | apartments and cars in the same chart, told apart by shape |
| The reader is outside the team and the noun is the whole point | see [graphic-first.md](graphic-first.md#checking-it-landed) |

And it does not when:

- **The shape is the same for every row.** Then it is a bar chart with a texture,
  and `bar` does bar charts better: axis maths, label fitting, the ordinal ramp.
- **The mark is under about 16px.** `person` and `home` survive small; `gear`,
  `car` and `apartment` turn to mud. Look at it before believing otherwise.
- **The nearest shape is only nearly right.** A `building` standing in for a
  hospital is a lie the reader cannot detect, and unlike a wrong number nothing
  will ever contradict it. Use a plain mark and label it.
- **You reached for it because the page felt empty.** An empty page is a missing
  claim, and no amount of iconography supplies one.

### A pictogram is not a scene

A library shape does not count against the three-figure cap, and should not:
the cap exists to stop *bespoke* drawings proliferating and drifting apart from
each other, and a library symbol is the opposite of bespoke. It re-themes, it
is identical in every document, it needs no review.

What that means in the other direction: **reaching for a pictogram is not the
same as deciding a claim needs an authored figure.** [scenes.md](scenes.md) is
still the decision about which two or three images the document lives on, and
"it has a house in it" is not an answer to that question.

### Drawing your own

The library is a floor too. If the subject is a wind turbine, draw a wind
turbine, in the same register as the fifty-two: one closed silhouette, no
interior detail that dies below 20px, holes via `fill-rule="evenodd"`, and no
`fill` attribute anywhere so it inherits like the rest. Put it in the figure's
own markup. If it recurs across documents it belongs in
`scripts/lib/pictograms.py` instead, which is a one-line addition.

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
| status | `--ig-good` `--ig-warn` `--ig-danger`, the text roles `--ig-warn-text` `--ig-danger-text`, and their washes |
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
- **Having been drawn twice.** Two compositions differing in something
  structural, both sketched, one kept, one sentence on what the loser could not
  show. → [scenes.md](scenes.md#draw-it-twice)
- **Being looked at**, `python3 scripts/ig.py sketch` while drawing it and
  `python3 scripts/ig.py shoot out/doc.html` once it is in the document. Nothing
  in the linter can see a collision.
