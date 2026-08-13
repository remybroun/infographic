# Editorial blocks

Where the argument actually lives. A document made only of charts explains
nothing: the chart is evidence, and these blocks are the claim the evidence is
for. Expect roughly half of a good concept document to be these.

---

## `hero`: the cover

```json
{"type": "hero", "tone": "panel", "kicker": "Explainer",
 "title": "Compound and simple interest on £10,000 at 7% over 30 years",
 "subtitle": "Compounding ends 2.5 times higher; the gap is interest earned on interest.",
 "lede": "Two or three sentences of setup.",
 "author": "Analytics", "date": "2026",
 "stats": [{"label": "Tickets received", "value": 18420, "compact": true, "delta": -14.2}]}
```

`tone`: `plain` (default) or `panel` for a tinted block. `stats` embeds a KPI row.

**The title names the subject, the scope and the period, literally.** A reader
who sees only the title should know what the document covers and be able to
predict what is inside it. "Compound and simple interest on £10,000 at 7% over 30
years" does that. "Compound interest is a shape, not a rate" does not: it is a
slogan, and a slogan tells the reader how to feel before it tells them what they
are looking at.

**The finding goes in the subtitle, stated flatly.** Not withheld, not turned
into a rhetorical figure. "Compounding ends 2.5 times higher; the gap is interest
earned on interest" is the entire point of the document in one plain sentence.
The register to aim for is a paper abstract, not a headline.

A bare topic is still wrong. "Retention overview" and "H1 metrics" name a folder,
not a document. The fix is to be **more specific, never more clever**: "Retention
by acquisition channel, 2024 to 2026". See
[anti-patterns.md](../anti-patterns.md#titles) for the three-way test.

## `section`: a new argument begins

```json
{"type": "section", "number": "01",
 "title": "How interest is calculated in each method",
 "lede": "Simple interest applies the rate to the original balance; compound applies it to the running one."}
```

**Numbers only when the sequence is information the reader needs.** Numbering
every section because it looks tidy is grammar you did not choose. If the
sections could be read in any order, drop `number`.

**Section titles are literal too**, and they are where the slogan register creeps
back in first, because a one-word title feels clean. "The mechanism", "The guard",
"Answering" are labels on a filing cabinet: they read as structure while carrying
no information. Name the thing the section establishes.

## `prose`: the reasoning

```json
{"type": "prose", "text": "First paragraph.\n\nSecond paragraph.", "lead": false, "columns": 1}
```

Blank lines split paragraphs. Supports a small inline subset: `**bold**`,
`*italic*`, `` `code` ``, and `[text](https://url)`. Everything else is escaped, source text is untrusted and never reaches the DOM as markup.

Capped at 68ch regardless of span, because a 12-span paragraph on A4 would run
to about 100 characters per line and stop being readable. Set `columns: 2` when
you genuinely have enough copy to justify it.

**Put a prose block between charts.** A reader who has just decoded a chart wants
to be told what it means; without that sentence, the chart is decoration and its
point is left to chance.

## `quote`: a human voice

```json
{"type": "quote", "text": "We lose bookings because we answered on Tuesday.",
 "attribution": "Operator, 30 properties, Madrid"}
```

Set in the display face at larger size with a rule down the left. Use a real
quotation. A paraphrase in a box is just prose that has been made harder to read.

## `callout`: do not skim past this

```json
{"type": "callout", "tone": "warn", "title": "One caveat on the median",
 "text": "Time to close is a median, so the long tail is invisible."}
```

`tone`: `key` · `note` · `warn` · `danger`. Each carries an icon as well as a
colour, so the severity never depends on hue alone.

Use sparingly. Three callouts on a page and none of them is a callout any more.

## `stat` / `kpi` / `hero_figure`, numbers as figures

```json
{"type": "stat", "label": "Median time to close", "value": 31, "unit": "h",
 "compact": false, "delta": 22.0, "delta_period": "vs H2", "up_is_good": false,
 "trend": [24, 26, 25, 28, 30, 31], "note": "Medians hide the tail."}
```

| Key | Notes |
|---|---|
| `delta` | signed number; the arrow and colour follow direction × `up_is_good` |
| `up_is_good` | default `true`; set `false` for latency, churn, cost |
| `delta_period` | name the comparison, a delta against nothing means nothing |
| `trend` | 6-14 points; renders a sparkline in the accent |

`kpi` wraps 3-4 stats in a row. **The column count is computed from the block's
real width**, so a 4-span KPI stacks vertically instead of colliding, and warns
when it does, so you know to widen the span.

`hero_figure` is the one number a page leads with: large, in the sans (never a
serif, that reads as off-brand decoration), **exactly one per view**. All three
use proportional figures rather than `tabular-nums`, which makes a number like
121 look loose at display size.

## `table`: when exact values matter

```json
{"type": "table", "columns": ["Region", "2024", "Change"],
 "rows": [["EU", "14,200", "+12%"]], "align": ["left", "right", "right"],
 "caption": "Bookings by region"}
```

Not a fallback, the right answer whenever there are more than about seven
classes that all carry meaning, or when the reader needs to look a number up
rather than compare shapes.

## `checklist`: what to do and what not to

```json
{"type": "checklist", "do_title": "What moves the outcome",
 "do": ["Starting earlier, even with less"],
 "dont": ["Chasing an extra 0.2% of headline rate"]}
```

Both columns carry a shape as well as a colour. Keep the items **concrete and
parallel**: "Label the endpoint" beats "Be thoughtful about labelling".

## `comparison`: two competing framings

```json
{"type": "comparison", "vs": "vs",
 "left":  {"label": "Before", "headline": "Slow", "points": ["Manual triage"]},
 "right": {"label": "After",  "headline": "Fast", "points": ["Owner at triage"]}}
```

Deliberately asymmetric: the right side takes the accent tint, because it is the
one you are arguing for. If you are genuinely neutral between the two, use a
`matrix` instead, the styling here is not neutral and pretending otherwise
misleads.

## `definitions`: shared vocabulary

```json
{"type": "definitions", "items": [{"term": "Churn", "text": "Customers who leave."}]}
```

Put this **before** the argument that depends on the terms, not in an appendix.

## `footnotes`: sources, method, and terms

```json
{"type": "footnotes", "title": "Method",
 "items": ["Source: support platform export.", "Medians, not means.",
           "PMS: the property management system a provider runs their inventory in."]}
```

**Every document carrying numbers needs one.** Where the data came from, what
period, what was excluded, and what the reader should not conclude. This is the
block that makes the difference between an infographic and a poster of
assertions.

**It is also the right home for a term the document uses once.** `footnotes` is
exempt from the word budget, so a gloss here is free, and free is what a
one-off term is worth: expanding an acronym inline costs label space on every
mark that carries it. Use `definitions` when the reader needs the term to follow
the argument at all, and put it before the argument; use a footnote when they
need it only to read one label. Neither is an appendix for vocabulary you could
not be bothered to explain.

## `image`: `divider`, `spacer`, `raw`

`image` takes `src` (absolute `file://` or data URI), `alt` (required for the
linter to pass), `ratio`, `fit`, `caption`.

`raw` injects HTML unchanged. It is the escape hatch, and it costs you theming,
the table view, and every check in this skill. Use it after you have confirmed
the catalog has nothing, and if you reach for it twice for the same shape, that
shape wants to become a real block in `registry.py`.
