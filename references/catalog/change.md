# Change over time

Blocks that answer *what moved*. The rule that gets broken most often lives
here, so it goes first:

> **One axis. Never two y-scales on one plot.** The alignment between two scales
> is arbitrary, so a dual-axis chart invents a correlation that is not in the
> data. Two measures of different magnitude become two charts, small multiples,
> or both indexed to 100 at t0, on one axis. `line` supports
> `"index_to_100": true` for exactly this.

---

## `line`: a value over time

```json
{
  "type": "line",
  "title": "The same 7% rate, compounded and not",
  "x": ["0", "5", "10", "15", "20", "25", "30"],
  "series": [
    {"name": "Compounded", "values": [10000, 14026, 19672, 27590, 38697, 54274, 76123]},
    {"name": "Simple",     "values": [10000, 13500, 17000, 20500, 24000, 27500, 31000]}
  ],
  "currency": "£", "compact": true, "height": 260
}
```

| Key | Default | Notes |
|---|---|---|
| `x` | index numbers | tick labels; thinned automatically when they would collide |
| `series` | none | `[{name, values}]`; `null` inside `values` breaks the line |
| `area` | `false` | wash under a single series at ~10% opacity |
| `stacked` | `false` | stacked areas for a composition that grows |
| `zero` | `true` | include zero in the domain |
| `index_to_100` | `false` | rebase every series to 100 at its first point |
| `markers` | `true` | drawn only when there are ≤14 points |
| `end_labels` | `true` for ≤4 series | value printed at the end of each line |
| `emphasis` | none | series name; that one takes the accent, the rest go gray |

Gotchas:
- **Padding never crosses zero.** An all-positive series will not pick up a
  negative axis tick from headroom; `svg.extent` clamps it. If you see one, that
  is a bug, not a style choice.
- **Do not smooth.** `svg.smooth_path` exists for decorative sparklines only.
  Curve interpolation invents values between real observations, which is wrong
  for anything read precisely.
- **Converging end-labels.** When lines converge at the right edge, nudging the
  labels apart detaches them from their lines. Past ~4 converging series, drop
  `end_labels` and let the legend carry identity, or facet into small multiples.

## `area`: a total over time

A `line` with `area: true`, and `stacked: true` when there is more than one
series. Use it when the *accumulated total* is the subject. Use a plain `line`
when the individual values are.

Stacked areas hide everything except the bottom band and the total, the middle
bands are read against a moving baseline, which humans do badly. If the middle
series matters, it needs its own chart.

## `dumbbell`: before and after, per item

```json
{"type": "dumbbell",
 "from_label": "H2", "to_label": "H1", "compact": true,
 "items": [{"label": "Password & access", "from": 5120, "to": 1880},
           {"label": "Payouts", "from": 2610, "to": 3180}]}
```

The **gap between the dots is the message**, which is why this beats two grouped
bars per item: the reader sees change directly instead of comparing two heights
and doing the subtraction. The signed delta is printed at the right, coloured by
direction.

| Key | Default | Notes |
|---|---|---|
| `gray_start` | `true` | the "before" dot is the de-emphasis gray, so "after" leads |
| `zero` | `false` | the domain fits the data; forcing zero flattens the gaps |
| `row_height` | `30` | |

**Not when** there are more than two states, that is a `line` or a `slope`.

## `slope`: two points, many items

```json
{"type": "slope", "from_label": "Last year", "to_label": "This year",
 "unit": "%", "decimals": 1,
 "items": [{"label": "Lisbon", "from": 4.1, "to": 5.2},
           {"label": "Madrid", "from": 3.8, "to": 3.1}]}
```

The one chart where **crossing lines are the finding, not a defect**, a crossing
is a rank change. Set `emphasis` to a label to gray everything else.

**Use it when** rank change matters. **Not when** you have three or more time
points (use `line`), or when only the magnitudes matter (use `dumbbell`).

## `timeline`: events in sequence

```json
{"type": "timeline", "orientation": "vertical", "ordinal": true,
 "events": [{"date": "Day 0", "title": "Enquiry sent", "text": "Guest messages three operators."},
            {"date": "Day 2", "title": "Terms agreed", "text": "Price settles.", "emphasis": true}]}
```

| Key | Default | Notes |
|---|---|---|
| `orientation` | `vertical` | `horizontal` only for short labels and few events |
| `ordinal` | `false` | ramp the markers by position |
| `gap` | `22` | vertical spacing between events |
| `events[].done` | `false` | fills the marker, for a completed step |

**Vertical is the default on purpose.** It takes real prose per event, survives a
page break, and never crowds labels the way a horizontal axis does. Reach for
`horizontal` only when the labels are short and the span is genuinely spatial.

A timeline is not a Gantt chart: it marks *moments*, not durations. If bars of
duration are the point, that is a `bar` with a non-zero baseline, or a table.
