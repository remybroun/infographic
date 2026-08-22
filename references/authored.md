# Authored composition: when you write the page

Custom HTML is not a fallback, it is the medium of an improvised page. Blocks
are word art, called in where a claim happens to have their shape.

**The catalog is a library. It is not the runtime.** Every block in it turns a
payload into a picture the skill already knows how to draw, and the page they
land on is a 12-column grid of stacked full-width rows that no document may
vary. That buys consistency across siblings, table twins for free, computed
contrast, and a document that re-skins with `--theme`. It is the right trade for
a data poster.

It is the wrong trade for an explainer that lives on its pictures, and the
failure is structural rather than a matter of taste:

| What you want | What block mode allows |
|---|---|
| a drawing that spans two ideas | one drawing, in one grid cell |
| something layered over something else | rows, stacked, never overlapping |
| a scene that fills the sheet | `bleed`, and only on `page: scroll` |
| a layout this document invents | 12 columns and a span |
| more than three hand-drawn images | a build error at four |

Faced with that, the honest move is not to pick the nearest block. It is to
write the page.

```json
{
  "meta": {"title": "…", "theme": "rentos", "page": "a4", "encodes": "concept"},
  "style": "…the document's CSS…",
  "body": "…the document's markup, inline SVG and all…",
  "blocks": [ { "id": "cost-by-year", "type": "line", "…": "…" } ]
}
```

**A spec is authored when it carries `body`.** There is no flag to remember. The
grid is not emitted, `.ig-doc` gives you the page box and its margins, and
everything inside it is yours.

## What the skill still holds you to

Four promises, and they are the reason this is a mode of the skill rather than a
suggestion that you write HTML somewhere else. Each is a build error.

### Colour is computed, not chosen

Every colour in `style` and in `body` must be a theme token. This is checked as
a *value* test on every CSS declaration and every paint attribute, so shorthands
are covered too: `border: 1px solid red` fails on the `red`.

```
ink        var(--ig-ink) var(--ig-secondary) var(--ig-muted)
surface    var(--ig-page) var(--ig-card) var(--ig-sunken)
accent     var(--ig-accent) var(--ig-accent-text) var(--ig-accent-wash)
series     var(--ig-series-0) … var(--ig-series-7)
status     var(--ig-good) var(--ig-warn) var(--ig-danger), each with -wash
rules      var(--ig-border) var(--ig-hairline) var(--ig-axis)
geometry   var(--ig-radius) var(--ig-gutter) var(--ig-content-width)
type       var(--ig-sans) var(--ig-display) var(--ig-mono)
           var(--ig-display-weight) var(--ig-display-tracking)
```

**`color-mix()` and the gradient functions pass**, and so do `opacity` and
`mix-blend-mode`, as long as every colour inside them is a token. That is
deliberate and it is most of what a drawing actually needs:

```css
background: color-mix(in srgb, var(--ig-accent) 12%, transparent);
background: linear-gradient(to bottom, var(--ig-card), var(--ig-page));
```

Refusing those bought the palette nothing and cost the drawing a great deal:
with no themed way to say "a wash", the only route left was a hex literal, which
is the thing the rule exists to prevent.

The drawing kit is still there and still shorter than writing it out:
`ig-fig-node`, `ig-fig-edge`, `ig-fig-label`, `ig-fig-title`, `ig-fig-kicker`,
`ig-fig-mono`, `ig-fig-figure`, `ig-fig-s0`…`s7`, and the shared arrowheads at
`url(#ig-arrow)`. → [drawing.md](drawing.md)

### Every drawing has a name

Every `<svg>` needs `role="img"` with an `aria-label`, or a `<title>` as its
first child, or `aria-hidden="true"` when something adjacent already names it.
Every `<img>` needs an `alt` attribute. Omitting it is not the same as deciding
it; `alt=""` is the decision, and it is available.

### One honest declaration about data

`meta.encodes` is required, exactly as it is on a `figure`:

```json
"encodes": "concept"
"encodes": {"columns": ["Year", "Cost"], "rows": [[2024, 12], [2025, 19]]}
"encodes": [ {…}, {…} ]
```

`"concept"` says there are no values in this page, and waives the table-twin
check. Anything else is rendered as a `<details>` twin after the body, so the
numbers are reachable by someone who cannot see the drawing. There is no third
option, because the third option is always "the values are in the picture and
nowhere else".

### The page is inert and self-contained

No `<script>`, no `on*=` handlers, no remote `src`/`href`/`url()`, no `@import`.
The page is consumed as a snapshot (shots always, a PDF when one was asked
for), so
anything that needs a script to appear is blank on paper, and anything fetched
over the network is a race the renderer usually loses. CSS transforms,
gradients, `clip-path`, `mask` and `mix-blend-mode` all render. Behaviour does
not. Embed a raster as a `data:` URI if you need one.

CSS goes in `style`, not in a `<style>` tag inside `body`, so the colour check
can see it. A stylesheet the validator cannot read is one that can quietly leave
the palette.

## Dropping catalog blocks into your layout

A comparison of values really is a `bar`, and hand-drawing one is strictly
worse: no axis maths, no label fitting, no table twin, no ordinal ramp, and it
will drift from every other chart you ever make. So place it:

```html
<div class="my-sidebar">
  <div data-block="cost-by-year" data-width="380"></div>
</div>
```

The block itself is an ordinary catalog block in `blocks`, with an `id`. It
renders at `data-width` (defaulting to the full content width), wrapped in a
bare `.ig-placed` div with no grid rules attached, inside whatever layout you
built around it. A placeholder naming a block that does not exist is an error; a
block no placeholder calls for is a warning, because it silently will not
appear.

## Fitting the sheet

**This, not the word budget, is what will actually fight you.** Everything else
in this skill is built around 150 or 260 words a page, and on an authored
one-pager you will typically land well inside that and then spend four render
cycles hunting ninety pixels. `measure` is the instrument:

```bash
python3 scripts/ig.py measure out/spec.json
```

```
  authored page: 941px tall, A4 portrait holds 1005px a sheet
  → one sheet, 64px spare
  252 words (85 of them inside drawings), budget 260 at lesson density
```

It lays the page out in Chrome and measures `<main>`, so the number is real
rather than derived from the payload, and it measures the content box, so it
matches what prints. Past one sheet it reports a floor and not a count: an
element that cannot break moves to the next sheet whole, exactly as a grid row
does, so `ig.py render` remains the count that counts.

## What does not change

- **The word budget.** 150 words a page at graphic density, 260 at `lesson`.
  Text inside your `<text>` elements **is** charged: the build counts it from
  the source, before a placeholder expands, so your labels count and a placed
  chart's axis ticks do not. A drawing labels; it does not narrate.
- **The ladder.** In `lesson` mode a rung lands `at` an `id`, and here that is
  any element in your markup carrying one. The forward-reference check is
  unchanged: the text belonging to a rung is everything up to the next id.
- **The linter**, minus the findings that count blocks you do not have.
  `no-graphics`, the word budget, page economy, the anti-patterns and the
  accessibility checks all still run.
- **`shoot` and `blind`.** Look at it, then hand it to a reader with no context.
  Authoring the page removes none of the reasons to.

## What the build cannot check here, and you must

**The three-figure cap does not apply.** It counts `figure` blocks, and your
drawings are inline `<svg>` in `body`. Nothing stops an authored page holding
eight hand-drawn scenes, and nothing will tell you that you have. The cap was
never really a budget: it is the ranking exercise made mandatory, and the
question survives the mechanism that used to force it. **Which two or three
images does this page live or die by?** Rank them yourself and write the losers
down. The [draw-it-twice](scenes.md#draw-it-twice) discipline is likewise on
your honour here, and it is the step that most often changes a drawing.

**Nothing checks that a scene earned its space.** Cover the picture: if nothing
was lost, it was decoration, and decoration on an authored page costs more than
it did in a grid cell because you gave it the room deliberately.

## When NOT to author

**When the document is a set of comparisons, shares, sequences and scores.**
That is what the catalog is for, it draws them better than you will by hand, and
a page of hand-built bar charts is a worse document that also took longer.

The test is the one in [scenes.md](scenes.md), applied to the page rather than
to one block: can you finish "the grid carries this document completely,
because ___"? A report, a data poster, a findings summary: yes, easily. An
explainer whose whole argument is a shape, a boundary, a thing inside another
thing, a scene the reader has to picture: no, and that is what this mode is for.

→ [drawing.md](drawing.md) for the kit · [scenes.md](scenes.md) for deciding
what gets drawn · [integrity.md](integrity.md) for the chart invariants, which
bind whether you drew it or the catalog did
