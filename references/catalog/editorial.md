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
 "author": "Analytics", "date": "2026"}
```

`tone`: `plain` (default) or `panel` for a tinted block. There is no `stats`
field: it embedded a row of number tiles, which was removed with `kpi`. If one
number is the finding, follow the hero with a `hero_figure`.

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
{"type": "section",
 "title": "How interest is calculated in each method",
 "lede": "Simple interest applies the rate to the original balance; compound applies it to the running one."}
```

**Numbers only when the sequence is information the reader needs.** Numbering
every section because it looks tidy is grammar you did not choose. If the
sections could be read in any order, drop `number`, which is why it is absent
from the example above and from every fixture in the repo. Ordinals are for a
reader who has to follow them in order; on anything else they turn a drawn page
into a textbook contents list, and eleven of them with a rule over each is what
that looks like. `numbered-throughout` measures it.

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

`tone`: `key` · `note` · `warn` · `danger`. Each carries a mark as well as a
colour, so the severity never depends on hue alone. `warn` and `danger` also
tint the block, because there the hue IS the message; `key` and `note` sit on
the neutral surface, because an idea does not become more important by being
painted blue.

Use sparingly. Three callouts on a page and none of them is a callout any more.

## `stat` / `hero_figure`, numbers as figures

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

There is no row of number tiles. Four labelled integers look like a summary and
cost nothing to write, and they are the same facts a chart further down carries
with its denominator and its shape, printed before the reader has a frame for
them. Four numbers cannot each be the finding. Reach for `hero_figure` when one
number genuinely is, put the rest in the chart that proves it, and lead with
nothing at all when no number is the finding.

`hero_figure` is the one number a page leads with: large, in the sans (never a
serif, that reads as off-brand decoration), **exactly one per view**. Both use
proportional figures rather than `tabular-nums`, which makes a number like
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

## There is no text-in-boxes block

`checklist`, `comparison`, `chips` and `kpi` were deleted. Each one drew no
SVG: two columns of ticked sentences, two tinted panels of bullets, a grid of
labelled pills, a row of number tiles. The registry counted them as graphics, so
a page built from them passed as graphic-first while being text in boxes, which
is the opposite of what this skill is for. The build refuses all four, and the
aliases that pointed at them (`compare`, `kpis`, `stats`, `list`, `tags`,
`pills`, `badges`, `facts`), with the reason.

Draw the thing instead:

| What you were about to write | Draw it as |
|---|---|
| do and don't, a rule and its failure | a `callout` for the one rule that matters, or a `figure` of the failure happening |
| before and after, old framing against new | `dumbbell` or `slope` when both sides are measured; `scorecard` or `matrix` when they are weighed on criteria; a before/after `figure` when the difference is a shape |
| a set of states or parallel facts | `process` if they happen in order, `stack` if they are layers, `pictogram` if they are counts, a `figure` if they are parts of one thing |
| three or four headline numbers | one `hero_figure` or `stat`, and the chart that proves it |

## There is no glossary block

There used to be a `definitions` block: a grid of bold terms over one-line
glosses. It was deleted because it read as filler on every page it reached,
set apart from the chart whose words it explained. `definitions`, `glossary`,
`terms`, `vocabulary` and their spellings are refused by the build with the
reason, and the linter fails a page (`glossary`, an error) that rebuilds it
from other parts: a table with a Definition or Meaning column, a `<dl>`, a
section or block titled as a glossary, or more than four "Term: gloss" lines in
`footnotes`.

A term the reader lacks goes, in order of preference:

1. **Drawn**, in the figure at the rung that teaches it.
2. **Named in words on the mark that carries it**: a scorecard criterion reads
   "Prices match ours", not "Rate parity"; an axis says "listings synced
   without errors", not "Sync health".
3. **Glossed in `footnotes`**, when it is used once and only to read one label.
→ [../anti-patterns.md](../anti-patterns.md)

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
mark that carries it. Use a footnote when the reader needs a term only to read
one label; when they need it to follow the argument at all, it belongs on the
page, drawn or in words. Four term glosses is the cap: past that the footnotes
are a glossary in smaller type, and the linter fails the page.

## `image`: `divider`, `spacer`, `raw`

```json
{"type": "image", "src": "file:///abs/path/lobby.jpg",
 "alt": "The reception desk at Carrer de Balmes, seen from the entrance.",
 "ratio": "16/9", "fit": "cover", "caption": "Balmes, ground floor."}

{"type": "divider"}
{"type": "spacer", "height": 24}
{"type": "raw", "html": "<iframe …></iframe>"}
```

| Key | Block | Default | Notes |
|---|---|---|---|
| `src` | `image` | none | absolute `file://` or a data URI; a relative path does not resolve in the PDF renderer |
| `alt` | `image` | `""` | one sentence saying what the image shows |
| `ratio` | `image` | `16/9` | a CSS `aspect-ratio`, so `4/3`, `1/1`, `3/2` all work |
| `fit` | `image` | `cover` | or `contain`, when cropping would cut the subject |
| `caption` | `image` | none | printed under the frame, charged against the budget |
| `height` | `spacer` | `24` | pixels of vertical air |
| `html` | `raw` | `""` | injected unchanged |

**Omitting `alt` is a decision, not a default.** The renderer emits `alt=""`,
which passes the linter and declares to a screen reader that the image is
decorative. That is right for a texture and wrong for everything else, and the
linter cannot tell them apart. Write the sentence.

`divider` and `spacer` take nothing else: they are a rule and a gap, and both
are the honest answer when a page needs a beat rather than another block.

`raw` injects HTML unchanged. It is the escape hatch, and it costs you theming,
the table view, and every check in this skill. Use it after you have confirmed
the catalog has nothing, and if you reach for it twice for the same shape, that
shape wants to become a real block in `registry.py`.
