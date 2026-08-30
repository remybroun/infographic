# Choosing a visual

This is the decision engine. Work it in order. The commonest failure in an
infographic is not an ugly chart, it is a **correct chart answering a question
nobody asked**, because the form was chosen before the claim was.

> The one-line rule: **name the claim as a sentence first.** If you cannot write
> the sentence, no chart will rescue you. If you can, the sentence names the form.

---

## Step 0: The sentence becomes the drawing, not the caption

Read [graphic-first.md](graphic-first.md) before this file. The claim you write
in step 1 is the thing to **draw**. It is not the thing to print beside a
drawing. Every sentence that survives into the document as a sentence is a form
you did not choose, and at graphic density body prose is a build error rather
than a style note.

The move is **draw the paragraph**, and the table from sentence to block is in
[graphic-first.md](graphic-first.md#the-procedure). Have it open. The rest of
this file assumes the sentence has already survived it and genuinely wants a
chart.

---

## Step 1: Write the claim as a sentence

Every block earns its space by carrying exactly one claim. Write it out.

| A claim sounds like | A topic sounds like |
|---|---|
| "Reply time, not price, decides conversion." | "Conversion overview" |
| "Two thirds of the balance is interest on interest." | "Compound interest" |
| "The work did not fall when the ticket count did." | "H1 support metrics" |

A topic produces a dashboard. A claim produces an argument. You are making an
argument.

## Step 2: Classify the claim, not the data

Read your sentence and find its **verb**. The verb picks the family.

| The sentence says… | Family | Go to |
|---|---|---|
| X is bigger / smaller than Y | quantity | [catalog/quantity.md](catalog/quantity.md) |
| X moved, grew, fell, changed | change | [catalog/change.md](catalog/change.md) |
| X is made of A, B and C | part-to-whole | [catalog/part-to-whole.md](catalog/part-to-whole.md) |
| X happens, then Y, then Z | sequence | [catalog/process-and-time.md](catalog/process-and-time.md) |
| X contains / depends on / connects to Y | structure | [catalog/structure-and-relation.md](catalog/structure-and-relation.md) |
| X and Y trade off against each other | position | [catalog/structure-and-relation.md](catalog/structure-and-relation.md) |
| X means this; here is why it matters | editorial | [catalog/editorial.md](catalog/editorial.md) |
| X is a kind of thing you have never met | teaching | [catalog/teaching.md](catalog/teaching.md) |

**A claim with no verb of comparison is not a chart.** "Churn is when customers
leave" is a `definitions` block. "We should assign an owner at triage" is a
`callout`. Neither improves by being plotted.

**Before any of the above: what must the reader *do* with this sentence?** Meet
it for the first time, compare, follow, locate, or weigh? Four of those five
presume the reader already has the concept and is now operating on it, which is
why "meet it for the first time" was missing from this file for three versions
and why every document it produced read as though written for an insider. When
that is the answer, the family is teaching, and the next question is not *which
chart* but **what does this reader already own that has the same shape?**

## Step 3: Ask whether it is a chart at all

Run this before picking a chart type. Most concept documents need **more
non-chart blocks than chart blocks**, and the single most common mistake in the
genre is plotting a number that was already the whole message.

| The content is… | Use | Never |
|---|---|---|
| One current value, maybe with a trend | `stat` | a one-bar bar chart |
| The number the page leads with | `hero_figure` (one per view) | none |
| Three or four numbers, **none of which the document explains further down** | `kpi`, and answer per tile why it is not its own chart | a row restating figures the charts below carry properly. `kpi` is not a slot: see [narrative.md](narrative.md#the-spine-that-works-for-almost-every-argument) |
| One ratio against a limit | `meter` | a two-slice pie |
| A rule, a caveat, a definition | `callout`, `definitions` | a chart with two bars |
| A subject the reader has never met | `analogy` | a diagram of its parts |
| A thing with more parts than anyone can meet at once | `progressive` | one complete diagram |
| More than ~7 classes that all matter | `table`, or table + chart | more colours |
| Options scored on criteria, no numeric axis | `matrix` | a "score" bar chart |
| A person's own words | `quote` | a paraphrase in a box |
| Two competing framings | `comparison` | a chart of one of them |
| What to do and what not to | `checklist` | prose |

## Step 4: Pick the form from the reader's job

Once you know it *is* a chart, the reader's job picks the type.

| The reader must… | Form | Colour job |
|---|---|---|
| Rank named things by size | `bar` (horizontal) | one hue, all bars |
| Read an ordered axis: periods, stages, buckets | `column` | one hue, or ordinal ramp |
| Compare many things without ink flooding the page | `lollipop` | one hue |
| See a value move over time | `line` | 1 hue, or categorical for ≤4 series |
| See a total accumulate over time | `area` | one hue |
| See before and after per item | `dumbbell` | 1 hue, 2 shades |
| See rank change between two points | `slope` | categorical or emphasis |
| See which side of a baseline | `diverging` | diverging pair + gray middle |
| Read an agree↔disagree scale | `likert` | diverging, centred on neutral |
| Read a split of one whole | `share_bar` | categorical, or ordinal if ordered |
| Count a human-scale ratio | `unit` | 2-3 categorical |
| Judge relative area across many items | `treemap` | sequential |
| See drop-off between stages | `funnel` | ordinal ramp |
| See a quantity split and merge | `sankey` | categorical by source |
| Find hot and cold in a grid | `heatmap` | sequential, one hue |
| See how two measures relate | `scatter` (≤3 series) | categorical |
| Follow steps in order | `process` | ordinal ramp |
| See a loop with no end | `cycle` | ordinal ramp |
| Locate events in time | `timeline` | ordinal or single hue |
| Place things on two axes | `quadrant` | emphasis |
| See overlapping membership (≤3 sets) | `venn` | categorical |
| See what contains what (≤3 levels) | `tree` | ordinal by depth |
| See levels resting on each other | `pyramid` | ordinal ramp |
| Understand a real image | `anatomy` | accent numerals |

## Step 5: Check the disqualifiers

Each of these overrides the table above.

- **Is the story one item?** Then it is **emphasis**, not categorical. One series
  in the accent, the rest in the de-emphasis gray. This is the single most
  underused form and usually the honest answer to "make this clearer".
- **Are the categories ordered?** Funnel stages, tiers, age bands, maturity
  levels, swapping them would change the meaning. Set `"ordinal": true` and take
  the one-hue ramp, so the reader sees the order in the colour. Product names,
  teams and regions are *nominal*: they all take slot 1.
- **Are there more than 8 series?** Fold the tail into "Other", facet into small
  multiples, or switch form. **Never** generate a ninth hue.
- **Is it a scatter, bubble or small-multiples form?** Any two marks can sit side
  by side, so all-pairs colour separation binds: cap at **three** series.
- **Do two measures have different scales?** Two charts, small multiples, or index
  both to 100 at t0, on **one** axis. Never a dual axis.
- **Is the count small and the difference large?** Consider whether the sentence
  plus a `stat` beats the chart entirely.

## Step 6: Decide how many visuals

A document is not improved by having a visual per paragraph. **One claim, one
block**: if two blocks make the same point, cut one.

Rough budget: an A4 explainer runs 6-12 blocks, of which 3-6 are charts; an A3
poster 12-20. Past that, nothing is the focus.

Rhythm (alternating register, varying the family and the span, one dominant
element) is ordering rather than form choice, and lives in
[narrative.md](narrative.md#rhythm).

## Step 7: Write down what you rejected

In your handoff message, name the forms you considered and why you did not use
them. "Used a dumbbell rather than grouped bars, because the gap is the finding"
is the difference between a decision and a default.

---

## Worked traces

**"Two thirds of the final balance is interest on the interest."**
→ Verb is *is made of* → part-to-whole. Human-scale ratio the reader should be
able to count → `unit` with 100 cells. Not a donut: three parts of very
different size compared by angle is exactly what donuts are bad at.

**"Ticket volume fell but total work did not."**
→ Two facts in tension. Not one chart. The tension goes in the `hero` subtitle, a
`dumbbell` per category shows the fall is concentrated, and a `share_bar` of
handling time shows where the work went. Two blocks, one argument. **No `kpi`
row:** both numbers are explained properly by the blocks below, so a tile would
be those facts with their denominator, comparison and shape stripped off,
printed before the reader has a frame for them.

**"Reply time degrades as portfolio grows."**
→ Verb is *degrades as* → a relationship across an ordered axis. Five ordered
bands → `lollipop` with `sort: null` so the band order survives. Not a scatter:
there are five points and the x axis is categorical.

**"Nine steps, and the loss is between two of them."**
→ Sequence with drop-off. `process` for the steps (what happens), `funnel` for
the counts (how many survive). Two blocks because they answer two questions;
merging them would do neither well.

**"No option wins on every constraint."**
→ Position, no numeric axis. `matrix`. Scoring the options and drawing a bar
chart would invent a total order the data does not support, and that invented
ranking is exactly what a reader would act on.
