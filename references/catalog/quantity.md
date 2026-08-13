# Quantity & comparison

Blocks that answer *how much* and *which is bigger*. Length on a common baseline
is the most accurately decoded visual channel there is, which is why almost
everything here is a bar of some kind. Reach past bars only when bars genuinely
fail.

---

## `bar`: horizontal bars

The default. Takes long category names without rotating anything, which is the
one thing columns cannot do.

```json
{
  "type": "bar",
  "title": "Tickets by category",
  "categories": ["Password & access", "Billing questions", "Booking changes"],
  "values": [1880, 2240, 4110],
  "sort": "desc",
  "compact": true,
  "value_label": "Tickets"
}
```

| Key | Default | Notes |
|---|---|---|
| `categories` | none | list of labels |
| `values` | none | list of numbers, same length |
| `items` | none | alternative shape: `[{label, value}]` |
| `sort` | `null` | `"desc"`, `"asc"`, or `null` to keep the given order |
| `thickness` | `24` | capped at 24px, a bar that fills its band leaves no air |
| `value_labels` | `true` | value printed at the bar tip |
| `axis` | `true` | show the value axis |

**Use it when** magnitudes are compared across named things.
**Not when** the categories are ordered periods (use `column`), or there is only
one value (use `stat`).

Gotchas:
- `sort: null` matters whenever the category order carries information. Sorting a
  set of ordered bands by value destroys the thing the reader needed.
- Set `ordinal: true` only for genuinely ordered categories. Colouring nominal
  bars darker-where-bigger double-encodes length as hue and spends the identity
  channel on information the bar already shows.
- Negative values grow left from the zero rule automatically.

## `column`: vertical bars, grouped or stacked

```json
{
  "type": "column",
  "categories": ["Q1", "Q2", "Q3"],
  "series": [
    {"name": "New", "values": [10, 14, 18]},
    {"name": "Renewal", "values": [6, 9, 11]}
  ],
  "stacked": false,
  "height": 250
}
```

| Key | Default | Notes |
|---|---|---|
| `series` | none | `[{name, values}]`; one series may use `values` directly |
| `stacked` | `false` | stacked segments carry a 2px surface gap between them |
| `height` | `250` | SVG design height |
| `padding` | `0.32` | band padding; higher means thinner bars |
| `rotate_labels` | `false` | last resort, wrapping to two lines is tried first |

**Use it when** the x axis is genuinely ordered.
**Not when** you have more than about three grouped series: past that, grouped
bars stop being comparable and small multiples win.

Gotchas:
- Grouped and stacked answer different questions. Grouped compares series within
  a category; stacked compares totals and hides the middle segments. Pick by
  which comparison the sentence needs.
- `value_labels` defaults on only for ≤8 categories, because a number over every
  column is noise.

## `lollipop`: stem and dot

A bar chart on a diet. Same encoding, a tenth of the ink.

```json
{"type": "lollipop", "categories": ["1 property", "2-5", "6-20"],
 "values": [7, 11, 19], "unit": "h", "sort": null, "row_height": 24}
```

**Use it when** there are many categories and solid bars would flood the page.
**Not when** there are fewer than about five items, a bar is friendlier.

## `diverging`: above and below a baseline

```json
{"type": "diverging", "items": [{"label": "Search to listing", "value": 4.2},
                                {"label": "Enquiry to reply", "value": -11.4}],
 "unit": "%", "decimals": 1, "sort": null}
```

The midpoint must read as *nothing*, so the neutral is gray and the two poles
are warm against cool. Two cool hues as the poles fails: they do not read as
opposite.

**Use it when** the baseline is meaningful, zero change, a target, a
break-even.
**Not when** all values share a sign; that is a plain `bar`.

## `likert`: ordered-scale share

```json
{"type": "likert",
 "scale": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
 "items": [{"label": "I can reply within an hour", "values": [22, 31, 18, 19, 10]}]}
```

Each row is normalized to its own total and centred on the middle of the neutral
bucket, so agreement and disagreement grow away from a shared middle. Segment
labels appear only where the percentage fits with padding.

**Use it when** responses run along an ordered scale.
**Not when** the options are unordered choices, that is a `share_bar`.

## `scatter`: two measures per item

```json
{"type": "scatter", "x_label": "Effort", "y_label": "Impact",
 "points": [{"x": 3, "y": 8, "label": "Search", "series": "Now"}]}
```

**Capped at three series.** Any two marks can land side by side, so all-pairs
colour separation binds rather than adjacent-pairs. A fourth series is a warning,
not a hue. Fold to "Other" or facet.

Set `zero_x` / `zero_y` when zero belongs on the axis; by default the domain
fits the data, because forcing zero onto a scatter of tightly-clustered values
flattens the very relationship you are showing.

## `heatmap`: magnitude across a grid

```json
{"type": "heatmap", "rows": ["Mon", "Tue"], "cols": ["AM", "PM"],
 "values": [[3, 9], [7, 2]], "cell_height": 30}
```

One hue, light→dark, always with a scale legend. Cell labels appear only where
they fit; every value stays in the table view regardless. `min` / `max` pin the
ramp when several heatmaps must be comparable, without pinning, each one
normalizes to itself and they silently mean different things.

**Never** a rainbow ramp. A multi-hue heat scale has no natural order, so readers
invent one and get it wrong.

## `matrix`: options against criteria

```json
{"type": "matrix",
 "cols": ["No new headcount", "Ships this quarter", "Reversible"],
 "rows": [{"label": "Assign owner at triage", "cells": [true, true, true]},
          {"label": "Weekend cover", "cells": [false, true, "partial"]}]}
```

Cell values: `true` / `false` / `"partial"` render as a check, a cross and a
dash, each with a shape as well as a colour. Any other string renders as text.

**Use it when** options are scored on criteria and no axis is numeric. This is
the honest home for a comparison people try to force into a chart: turning the
columns into a score and drawing bars invents a total order the data does not
support, and that invented ranking is what the reader will act on.
