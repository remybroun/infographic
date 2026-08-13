# Diagram

**The family that absorbs paragraphs.** Every block here exists because a real
document tried to explain something in prose and should have drawn it instead.

When a paragraph appears in your draft, it is almost always one of these.
Read the "you are about to write" column, find the sentence you were reaching
for, and draw that instead.

| You are about to write… | Draw |
|---|---|
| "the edge handles X and Y, the app handles Z" | `stack` |
| "first the provider does A, then the system does B" | `swimlane` |
| "we scored five options against fifteen criteria and E won" | `scorecard` |
| "it scored 66 out of 75" | `gauge` |
| "the states are draft, pending, live, suspended" | `chips` |
| "imagine a beam that gets thinner as it goes deeper" | **`figure`** |

That last row is the one to notice. **The catalog is a floor, not a ceiling.**
When a claim has a shape nothing here has, the answer is to draw the shape, not
to ship the nearest thing that exists.

---

## `figure`

An authored drawing. You supply the SVG; the block supplies the frame, the
theme, the accessible name and the table twin.

```json
{
  "type": "figure",
  "span": 12,
  "title": "The request cross-section",
  "viewbox": "0 0 1080 300",
  "alt": "A beam of 100 requests entering at the left narrows as it passes through the edge, the cache and the application, so that only 2 reach the core.",
  "encodes": {
    "columns": ["Layer", "Requests in", "Requests through"],
    "rows": [["Edge", 100, 40], ["Cache", 40, 12], ["Application", 12, 2]]
  },
  "svg": "<path class=\"ig-fig-s0\" d=\"M0,60 L270,96 …Z\"/><text class=\"ig-fig-figure\" x=\"8\" y=\"288\">100</text>"
}
```

| Key | Meaning |
|---|---|
| `viewbox` | **required**, four numbers. What lets the drawing scale to its column |
| `alt` | **required**, one sentence saying what the picture shows |
| `encodes` | **required**: `"concept"`, or `{columns, rows}` which renders the twin |
| `svg` | the drawing. A bare fragment or a whole `<svg>`; the root is rewritten either way |
| `invert` | draw on a dark field, the kit classes follow |
| `bleed` | `page: scroll` only: run the block edge to edge |

**Use when the geometry is the argument**: containment, distance, spread, depth,
convergence, a shape that changes along its length. **Not** for anything the
catalog already draws. A hand-drawn bar chart loses the axis maths, the label-fit
logic, the ordinal ramp and the twin, and drifts from every other chart in the
document.

### The four things the build will refuse

Not paperwork. Each one is a guarantee the rest of the skill makes, and a
hand-drawn figure is where each is most likely to leak.

1. **No `alt`.** A drawing readable only by looking at it is not readable by a
   screen reader, a search index, or anyone printing in mono.
2. **A colour literal.** `fill="#c0392b"` fails and names itself. Paint is
   `var(--ig-…)`, `currentColor`, `none`, or `url(#…)`. See
   [drawing.md](../drawing.md).
3. **A fourth figure.** The cap is three per document, and it is a ranking
   exercise, not a budget. See [scenes.md](../scenes.md).
4. **Sentences inside `<text>`.** Charged as `figure_text`, capped at 40 words,
   a third of a page's whole allowance. A drawing labels; it does not narrate.

`encodes: "concept"` is the honest declaration for a drawing with no data in it,
and it is not a way to skip the twin. If the drawing shows quantities, give them:
a picture of numbers that only exists as a picture is the same accessibility
failure as a chart with no table.

→ [scenes.md](../scenes.md) decides *what* to author ·
[drawing.md](../drawing.md) is the kit you author *with*

---

## `stack`

Layers resting on each other, each holding named parts. Reads top to bottom,
because that is how people draw and describe stacks. The layer label sits in a
fixed left column so the eye can run down the spine.

```json
{
  "type": "stack",
  "title": "The stack, top to bottom",
  "layers": [
    {"label": "Edge", "meta": "80% of traffic stops here",
     "items": ["CDN + WAF", "TLS / ACME", "Full-page cache"]},
    {"label": "Application", "meta": "One deployment",
     "items": ["Routing", "Render", "SEO"]},
    {"label": "Core", "meta": "Source of truth",
     "items": ["Pricing", "Booking", "Database"]}
  ],
  "note": "One database, keyed per tenant."
}
```

| Key | Meaning |
|---|---|
| `layers[].label` | the tier name, ≤6 words |
| `layers[].meta` | one short qualifier under the label |
| `layers[].items` | the parts inside that tier, drawn as chips and wrapped |
| `layers[].note` | a single line under the chips |
| `ordinal` | `false` to use one hue instead of the ordinal ramp |

**Use when** the containment is the explanation. **Not** for a sequence: three
layers that happen in order are a `process`. If a layer needs more than about
six items, the drawing has become a list and a `tree` or `table` serves better.

## `swimlane`

Lanes are actors, columns are stages. The cell says what that actor does at that
stage; an empty cell says they are not involved, which is usually the point.

```json
{
  "type": "swimlane",
  "stages": ["Add domain", "Verify", "Issue cert", "Go live"],
  "lanes": [
    {"label": "Provider", "cells": ["Adds domain", "Sets DNS", null, null]},
    {"label": "System",   "cells": ["Issues token", "Polls DNS", null, "Publishes"]},
    {"label": "Proxy",    "cells": [null, null, "ACME issues", "Routes by SNI"]}
  ]
}
```

`cells` is positional and must be the same length as `stages`. Use `null` for a
gap. `row_height` (default 52) and `color_lanes` are the only knobs.

**Use when ownership changes across the sequence and the hand-off is the thing
being explained.** If every step has the same owner, the extra axis is empty
structure and `process` is the honest form.

## `scorecard`

Options scored against criteria, with the totals as the punchline. The cell grid
shows the shape of *why* one option won; the total bar shows that it did.

```json
{
  "type": "scorecard",
  "choices": ["Hybrid", "Central", "Separate"],
  "criteria": ["Cost", "Scale", "Risk", "Effort"],
  "scores": [[5, 4, 4, 3], [4, 4, 3, 3], [1, 2, 1, 2]],
  "max": 5,
  "winner": 0
}
```

The axis key is **`choices`, not `options`**. `options` is reserved for
per-block render settings, and using it here makes the compiler try to merge a
list into a dict. The build fails with that explanation if you get it wrong.

`winner` defaults to the highest total. Cell size and colour both encode the
score, so it survives greyscale.

**Never invent per-criterion scores you do not have.** If you only know the
totals, draw the totals as a `bar` with `emphasis`. A scorecard full of made-up
cells looks like far more evidence than you actually hold, which is the exact
failure `integrity.md` exists to prevent.

## `gauge`

One score against its ceiling, as an arc.

```json
{"type": "gauge", "span": 4, "value": 66, "max": 75,
 "label": "Hybrid", "caption": "recommended"}
```

| Key | Meaning |
|---|---|
| `value`, `max` | the score and its ceiling |
| `display` | override the centre text |
| `show_max` | `false` to print `66` rather than `66/75` |
| `sweep` | arc degrees, default 260 |
| `thresholds` | `[{"at": 80, "status": "warning"}]`, recolours past a share |

**Use only when the ceiling is part of the claim.** With no real maximum, an arc
invents its own scale, and the honest form is a `stat`. Three gauges in a row at
`span: 4` compare well; more than three, use a `bar`.

## `chips`

Indicator chips: the graphic-density replacement for a bullet list. A bullet
list is a paragraph wearing a disc. A chip grid is scannable, has a shape, and
costs you your adjectives, because a chip needing twelve words is not a chip.

```json
{
  "type": "chips",
  "items": [
    {"label": "Published", "tone": "good"},
    {"label": "SSL pending", "tone": "warn"},
    {"label": "Failed", "tone": "danger", "note": "retry in 24h"},
    {"label": "Archived", "tone": "mute"},
    {"label": "Sessions", "value": "12.4K", "tone": "accent"}
  ]
}
```

`items` also accepts bare strings. Tones are `plain`, `mute`, `good`, `warn`,
`danger`, `accent`; each carries an icon as well as a colour, so the state never
depends on hue alone. `value` sits right-aligned, `note` drops to its own line.

Labels are charged against the **label** budget (6 words), not the detail
budget. That is deliberate.

Columns are computed from the block's real width and balanced so the last row is
not a straggler, unless you set `columns` explicitly. Six chips across a 12-span
become three columns of two rather than four and a gap.
