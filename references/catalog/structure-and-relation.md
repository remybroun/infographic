# Structure & relation

Blocks that answer *how do these things relate*. No quantity is required for any
of them, which is exactly why they are the backbone of a document explaining a
concept rather than reporting a result.

---

## `tree`: what contains or reports to what

```json
{"type": "tree", "level_height": 84, "node_width": 150,
 "root": {"label": "Booking", "children": [
   {"label": "Demand", "children": [{"label": "Search"}, {"label": "Listing page"}]},
   {"label": "Supply", "emphasis": true, "children": [{"label": "Reply"}]}
 ]}}
```

Recursive layout: leaves take equal slots, parents centre over their children,
edges are orthogonal. Depth drives the ordinal ramp, so the level reads from the
colour. `emphasis: true` on a node fills it.

**Keep it to three levels.** Past that the boxes shrink below a readable label
and a nested list outperforms the drawing. If you need four levels, you are
describing a taxonomy, and a `definitions` block or an indented list is kinder.

## `venn`: overlapping membership

```json
{"type": "venn", "sets": [{"label": "Instant reply"}, {"label": "Photos over 12"},
                          {"label": "Flexible dates"}],
 "overlap": "9% of listings, 41% of bookings"}
```

Two or three sets. **Warns and truncates above three**, because four sets cannot
be drawn with circles without misrepresenting some intersections, that is a
`matrix`.

The circles are *not* area-proportional. A Venn shows which combinations exist,
never how big they are. If size is the point, put the number in `overlap` (as
above) or use a different form entirely.

## `quadrant`: two axes, four named positions

```json
{"type": "quadrant", "x_label": "Effort to build", "y_label": "Effect on conversion",
 "x_low": "Low", "x_high": "High",
 "quadrants": [{"label": "Worth doing"}, {"label": "Big bets"},
               {"label": "Skip"}, {"label": "Do first", "highlight": true}],
 "items": [{"label": "Reply SLA nudge", "x": 0.18, "y": 0.82, "emphasis": true}]}
```

`quadrants` are given in reading order: top-left, top-right, bottom-left,
bottom-right. Item `x` and `y` are **0-1 normalized positions, not data**, this
is a judgement instrument, so say so in the note rather than implying measurement.

**The naming is the value.** An unlabelled 2x2 is a scatter plot with extra
lines. If you cannot name all four quadrants, the axes are probably not the right
two.

## `matrix`: options against criteria

See [quantity.md](quantity.md#matrix-options-against-criteria).

The most under-used block here, and the correct answer far more often than it
gets chosen. Whenever someone asks to "score" qualitative options and chart the
result, this is what they actually needed: scoring invents a total order the
evidence does not support, and the reader acts on the invented ranking.

## `sankey`: flow between stages

See [process-and-time.md](process-and-time.md#sankey-a-quantity-moving-between-stages).

## `anatomy`: a real image with numbered callouts

```json
{"type": "anatomy", "image": "file:///abs/path/screenshot.png", "height": 320,
 "callouts": [{"x": 0.3, "y": 0.4, "title": "Filter row",
               "text": "Scopes every chart below it."}]}
```

Numbered discs are placed at normalized coordinates over the image, with a
matching numbered list underneath. The list is HTML, so the text stays
selectable and reflows.

**This is the one block that expects a raster.** If the concept depends on a
photograph, a screenshot, a product, a place or a person, supply that image, do
not silently substitute CSS scenery for it. Without `image` the block renders a
labelled placeholder, deliberately obvious, so a missing asset cannot ship
unnoticed.

Use absolute `file://` paths or data URIs. Chrome renders from a temporary
profile and will not resolve relative paths the way your editor does.
