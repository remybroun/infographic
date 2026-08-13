# Anti-patterns

Check every document against this list. If your output matches an entry, it is
wrong, fix it before shipping. These are real failure modes, not style
preferences.

---

## The one that produced version 2

**❌ A text document with charts stapled to it.** Paragraphs of reasoning, a
term-and-sentence list, six bullet points, and one bar chart at the bottom of
the page.
Why: it is the default outcome of writing first and illustrating afterwards.
Every paragraph is individually defensible, which is exactly why the failure
survives review. The measured version: 2,086 words across eight A4 pages, 261
per page, against a budget of 130.
Instead: **draw the paragraph.** A sequence is a `process`; a sequence that
changes hands is a `swimlane`; layers are a `stack`; options against criteria
are a `scorecard`; a score against a ceiling is a `gauge`; parallel facts are
`chips`. See [graphic-first.md](graphic-first.md).
Caught by: the build fails at graphic density. The linter also reports
`text-heavy`, `text-heavy-mix` and `prose-only`.

**❌ A bullet list.** Five discs, each carrying a clause.
Why: a bullet list is a paragraph wearing a disc. It has no shape, so it is
neither scannable nor readable, and it never has to justify its own length.
Instead: `chips` for parallel facts, `checklist` for do-and-don't, `process` if
they are secretly ordered, `definitions` if they are secretly a vocabulary.

**❌ Retyping a paragraph as a `table` because table cells are exempt.**
Why: it is the same move as reaching for report density, but it does not feel
like one, because every individual table is defensible and the build stays
green. The tell is a `table` whose cells are sentences rather than values,
usually three columns wide with a verb in the middle one. The measured version:
a five-section explainer whose last section was two tables and a footnote block,
303 words the budget could not see, shipped as "clean".
Instead: ask what shape the rows are. Options against criteria are a `matrix`;
a sequence is a `process`; items with a before and an after are a `dumbbell`;
counts per named thing are a `bar` or a `lollipop`. Keep the table when the
reader genuinely needs to look a value up.
Caught by: `text-heavy` counts authored tables (the twins stay exempt),
`text-heavy-mix` counts `ig-table` as a text block, and `text-only-section`
fires on a section that never draws anything.

**❌ Reaching for `--density report` because the text did not fit.**
Why: the budget is the design constraint, not an obstacle to it. Report density
exists for documents that genuinely are prose with figures, and choosing it to
avoid rewriting is how a graphic document turns back into a written one.
Instead: rewrite to the cap, or draw the idea. If report density really is
right, say why in the document.

---

## The document

### Titles

Titles fail in two opposite directions, and fixing one by reaching for the other
is how this skill spent a version shipping slogans. There are three registers and
only the middle one is correct.

**❌ Too vague: a title that names a topic.** "Retention overview", "H1 metrics",
"Compound interest".
Why: a topic names a folder, not a document. The blocks end up in whatever order
the data arrived in, and the reader is left to assemble the argument themselves.

**❌ Too clever: a title that is a slogan.** "Retention is a pricing problem",
"Compound interest is a shape, not a rate", "Facts an agent may quote, not text
it may paraphrase", "The channel narrows, swells, then narrows again".
Why: it tells the reader how to feel before telling them what they are looking
at. It cannot be scanned, cited, searched, or read out in a meeting without
sounding like an advertisement, and it hides the scope: not one of those four
names a subject, a period, or a unit. The three tells are rhetorical antithesis
("X, not Y"), metaphor ("in shadow", "narrows", "is a shape"), and a bare verb
phrase ("Corroboration saturates").

**✅ Right: literal, specific, sober.** "Retention by acquisition channel, 2024
to 2026". "Compound and simple interest on £10,000 at 7% over 30 years".
"Extraction candidates accepted and rejected across 14 transcripts".
The test: **would this work as the caption of a figure in a journal paper?** It
names the subject, the scope and the period, and it is boring. The finding is not
lost, it moves to the `subtitle` and is stated flatly there: "Compounding ends
2.5 times higher."

This applies to `hero`, `section`, block and step titles alike. Section titles are
where the slogan register returns first, because a one-word title feels clean:
"The mechanism", "The guard", "Answering". Name what the section establishes.

**❌ A chart with no sentence near it.** The single most common failure in the
genre.
Why: the reader decodes the chart, gets a shape, and then invents their own
conclusion, usually a different one from yours.
✅ Every chart has its point stated in the `subtitle`, an adjacent `prose` block,
or both.

**❌ A visual per paragraph.** Twelve charts and no argument.
✅ One claim, one block. If two blocks make the same point, cut one. The test:
would removing it change what the reader concludes?

**❌ No tension anywhere.** Every chart supports the thesis and nothing
complicates it.
Why: it reads as marketing, and readers discount it accordingly.
✅ Include what does not fit, a `callout` naming the caveat, a `matrix` where no
option wins, the metric that moved the wrong way.

**❌ Ending on a chart.** The document stops at its last piece of evidence.
✅ End on the implication. Evidence with no conclusion gets one supplied by the
reader.

**❌ No method block.** Numbers with no source, period, or exclusions.
✅ `footnotes`, always, on anything carrying figures.

## Form choice

**❌ A one-bar bar chart, or a two-slice pie.**
✅ A `stat`. The number is the chart.

**❌ Eight categorical hues when the story is one item.**
✅ **Emphasis**: one series in the accent, the rest in the de-emphasis gray.

**❌ A value ramp on nominal categories**, colouring each bar darker-where-bigger
when the categories have no natural order.
Why: it double-encodes bar length as hue and spends the identity channel on
information the bar already shows.
✅ One series → slot 1 for every bar. `ordinal: true` only for genuinely ordered
categories.

**❌ A "score" bar chart built from qualitative judgements.**
Why: totalling incommensurable criteria invents a ranking the evidence does not
support, and the reader acts on the invented ranking.
✅ A `matrix`. Let the columns disagree.

**❌ A donut for comparing close values.** Angle is the least accurately decoded
channel.
✅ `share_bar`, or the numbers.

**❌ A funnel for values that merely decrease.**
✅ A funnel requires one population moving between stages. Otherwise it is a
`bar` with ordered categories.

**❌ A cycle whose last step does not feed the first.**
✅ That is a `process` drawn in a circle, which is worse than a `process`.

**❌ A Venn with four sets, or one implying area.**
✅ Three sets maximum; a Venn shows which combinations exist, never how big they
are. Four sets is a `matrix`.

**❌ A sankey for a simple decline.**
✅ Sankey earns its complexity only when the flow splits and merges. Otherwise,
`funnel`.

## Charts

**❌ Dual-axis charts (two y-scales on one plot).** The number one chart mistake.
Why: the alignment of the two scales is arbitrary, so the chart invents a
correlation that is not in the data.
✅ Two charts, small multiples, or index both to 100 at t0 on one axis
(`index_to_100`).

**❌ An axis padded across zero.** An all-positive series showing a −20K tick.
✅ Handled by `svg.extent`, which clamps the padded bound at zero. If you see
one, it is a bug.

**❌ Recolour-on-filter.** Assigning colours by current rank, so dropping a series
repaints the survivors.
✅ Colour follows the entity, never its row number.

**❌ Generating a ninth hue.**
✅ Fold the tail into "Other", facet, or change form. `Theme.series()` clamps and
warns rather than wrapping.

**❌ More than three series in a scatter, bubble or small-multiples chart.**
Why: any two marks can sit side by side there, so all-pairs separation binds.
✅ Cut to three, or facet.

**❌ A rainbow sequential ramp, or a hue at the diverging midpoint.**
✅ One hue light→dark for magnitude; two opposite hues plus a neutral gray for
polarity. The midpoint must read as "nothing".

**❌ Status colour used for a plain series**, or a series colour used for status.
✅ Status tokens only when the colour *means* good or bad, always with an icon.

**❌ Smoothed lines through real observations.**
Why: interpolation invents values between data points.
✅ Straight segments. Smoothing is for decorative sparklines only.

**❌ A number on every data point.**
✅ Label selectively, the endpoint, the extreme, the series that matters. Let
the axis, the legend and the table view carry the rest.

**❌ Dashed gridlines.** Dashing reads as "projection" or "threshold".
✅ Solid hairlines, one step off the surface.

**❌ A border drawn around marks to separate them.**
✅ A 2px surface gap between fills and a 2px surface ring on overlapping markers.

**❌ A label clipped by its own mark**, or `overflow: hidden` cropping it.
✅ Only render a label inside a mark when it fits with padding; otherwise move it
outside or drop it to the table view, where the value stays reachable.

**❌ A legend with one entry**, or no legend with four series.
✅ A legend is always present for ≥2 series and never for one.

**❌ Text wearing the series colour.**
✅ Marks carry the hue; labels, values and legends wear ink tokens. A coloured
mark beside the text carries identity.

## Print

**❌ Shipping without opening the PDF.** The linter checks structure, not whether
the argument lands or whether a label collided.
✅ Render it, read it end to end at 100%.

**❌ `--no-tables` on anything that will be printed or read by assistive
technology.**
✅ The table view is the only way a value inside an unlabelled mark stays
reachable on paper.

**❌ Half-empty pages accepted as normal.**
Why: a tall grid row moves to the next page whole, leaving a gap that looks
deliberate and is not.
✅ Reduce block heights, split a 12-span into two, or drop the unnecessary
`break: before`. `check_document.py` reports it as `sparse-pages`.

**❌ `paper: bleed` on a multi-page document.**
✅ Bleed simulates margins with padding, which applies to the first page only.
Single sheets only.

**❌ Relative image paths.**
✅ Chrome renders from a temporary profile. Absolute `file://` or data URIs.

**❌ Colour as the only channel, in a document that will be photocopied.**
✅ Build it once with `--theme mono` and see what stops working.
