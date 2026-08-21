# Part-to-whole

Blocks that answer *what is it made of*. Ranked by how accurately a reader
decodes them:

> **`share_bar` > `unit` > `treemap` > `donut`**

Reach down the list only when the form above it genuinely cannot do the job. A
donut is in this catalog because briefs ask for one, not because angle is a good
channel.

Before using any of them, confirm the parts are **mutually exclusive and
exhaustive**. If they overlap, or if they do not add up to the whole, a
part-to-whole form asserts something false. Use a `bar` instead.

---

## `share_bar`: one bar, normalized to the whole

```json
{"type": "share_bar",
 "title": "Handling time by complexity band",
 "parts": [{"label": "Under 1 hour", "value": 9},
           {"label": "1 to 8 hours", "value": 24},
           {"label": "Over 3 days", "value": 29}],
 "ordinal": true, "thickness": 42}
```

The default. Length on a common baseline, a 2px surface gap between segments,
percentages printed inside each segment wide enough to hold one, and dropped,
not clipped, where they are not. Every value stays in the legend and table view.

Set `ordinal: true` when the parts are ordered (bands, tiers, stages) so the
reader sees the order in the colour.

## `unit`: waffle / isotype

```json
{"type": "unit", "cells": 100, "per_row": 10, "glyph": "square",
 "parts": [{"label": "Money they paid in", "value": 8},
           {"label": "Interest on that money", "value": 25},
           {"label": "Interest on the interest", "value": 67}]}
```

One glyph is one countable thing, so "3 in 10" stays literally countable. The
strongest form for a human-scale ratio, and much harder to misread than a
percentage.

| Key | Default | Notes |
|---|---|---|
| `cells` | `100` | total glyphs |
| `per_row` | `10` | 10 for a 100-cell square |
| `glyph` | `"square"` | `"circle"`, or any name from the pictogram library |
| `total` | sum of parts | set it when the parts are a subset of a larger whole |

**The glyph can be a picture of the thing being counted**, which is what the
word "isotype" in this block's title has always meant: `"glyph": "person"` draws
a hundred people, `"glyph": "home"` a hundred houses.
`python3 scripts/ig.py pictograms` lists the fifty-two names.

It is optional, and a square is the safer mark. A square has no wrong reading,
survives being 12px across, and never makes the reader identify a shape before
they can count it. A picture is worth its ambiguity when **recognising the
symbol tells the reader something the legend does not**: that these are people
and not euros, that the unit is a dwelling. When the label already says it and
the shape is decoration, use squares.
→ [drawing.md](../drawing.md#pictograms-when-the-subject-has-a-shape)

**Rounding is handled, not ignored.** Exact shares rarely land on whole glyphs,
so the drift is distributed to the largest remainders and the grid always totals
exactly `cells`. A waffle that draws 99 squares out of 100 is a bug the reader
*will* notice, because counting is the entire point of the form.

**Not when** the parts are tiny fractions, at 100 cells, anything under 1%
disappears. Say it in prose instead.

## `pictogram`: rows of symbols, one symbol per fixed amount

```json
{"type": "pictogram", "glyph": "apartment",
 "unit_value": 500, "unit_label": "apartments",
 "rows": [{"label": "Lisbon", "value": 4200},
          {"label": "Porto", "value": 2350},
          {"label": "Faro", "value": 620}]}
```

The other isotype form. Where `unit` divides one whole into parts, this counts
several quantities in a stated unit: one apartment block is 500 apartments, and
Lisbon's row is eight of them. The reader counts and multiplies rather than
decoding a length against an axis, and the unit is said out loud in the key
instead of being implied by a tick mark.

| Key | Default | Notes |
|---|---|---|
| `unit_value` | **required** | what one symbol stands for |
| `unit_label` | `""` | the noun in the key: "= 500 apartments" |
| `glyph` | `"person"` | any library name; a row may override it |
| `rows` | | `{label, value}`, plus optional `glyph` and `color` |
| `show_values` | `true` | the exact number at the end of each row |
| `size` · `gap` · `row_gap` | `26` · `5` · `10` | symbol size and spacing |
| `ordinal` · `palette` · `vary_color` | off | per-row colour; off by default on purpose |

**One colour by default.** The comparison here is row length. Giving each row
its own hue invites the reader to decode the colour instead, and there is
nothing in it to decode.

**A part symbol is cut, not rounded**, with the whole shape left behind it at
low opacity so the fraction reads as a fraction rather than as a drawing that
failed to render.

**A row that does not fit is a build error**, naming the `unit_value` that would
fit. Past roughly two dozen symbols nobody is counting any more, and an isotype
nobody counts is a bar chart drawn badly.

**Not when** precision matters, or when two rows differ by less than one symbol.
That is `bar`, and `bar` is better at it: real axis maths, real label fitting.
What this buys is that the reader knows what is being counted without reading
the axis label. If that is not worth anything here, it is the wrong form.

## `donut`: part-to-whole in a circle

```json
{"type": "donut", "parts": [{"label": "A", "value": 3}, {"label": "B", "value": 7}],
 "inner_ratio": 0.62, "center_value": "68%", "center_label": "retained"}
```

**Warns above six segments**, and should not be used to compare close values at
all: angle is the least accurately decoded channel there is. Two slices is a
`stat`; close values are a `bar`.

Legitimate use: a single glanceable proportion where precision does not matter
and the circle carries brand or layout meaning. `center_value` turns it into a
ring gauge, which is usually the honest version of this form.

## `treemap`: area across many items

```json
{"type": "treemap", "height": 240,
 "parts": [{"label": "51+ properties", "value": 4120}, {"label": "2-5", "value": 720}]}
```

Squarified layout, sorted large to small, sequential fill. Area is decoded
loosely, so labels and the table view are not optional here.

**Use it when** there are too many items for bars and the relative *bulk* is the
point. **Not when** the reader needs to rank items precisely, that is a `bar`.

## `funnel`: stage-to-stage drop-off

```json
{"type": "funnel", "stages": [{"label": "Opened", "value": 4180},
                              {"label": "Triaged", "value": 3020},
                              {"label": "Closed in SLA", "value": 610}]}
```

Width encodes the count against the first stage; the percentage of the top is
printed at the right, and the **drop-off between stages is drawn**, because that
loss is the actual story and readers should not have to do the subtraction.

**Only a funnel if the same population moves between stages.** Values that merely
happen to decrease are a `bar` with ordered categories. If the flow splits or
merges rather than shrinking, that is a `sankey`.

## `pyramid`: levels resting on each other

```json
{"type": "pyramid", "levels": [{"title": "Availability", "text": "The dates must be free"},
                               {"title": "Trust"}, {"title": "Fit"}],
 "inverted": false}
```

For conceptual hierarchies, needs, maturity, evidence quality. The widths are
**conceptual, not counted**; nothing is flowing. If your widths mean quantities,
use a funnel and say so.

## `meter`: one value against a limit

```json
{"type": "meter", "label": "Open tickets vs ceiling", "value": 840, "max": 1000,
 "thresholds": [{"at": 70, "status": "warning", "label": "70%"},
                {"at": 90, "status": "critical", "label": "90%"}]}
```

The unfilled track is a lighter step of the fill's own ramp, so state reads
across the whole bar rather than only the filled part. Thresholds are drawn as
tick marks with labels, and the fill takes the status colour of the highest
threshold passed, with the numeric value always printed, so colour is never the
only cue.

**Use it when** there is a real limit. Without one, this is a `stat`.
