# Anti-patterns

Two lists, for two different moments. **[Before you write](#before-you-write)**
holds the process failures: by review time, nothing can be done about them.
**[Before you ship](#before-you-ship)** is the checklist to run against a
finished document.

Every entry is a failure this skill actually shipped, not a style preference.
Where an entry has a postmortem, the file that owns the rule keeps the full
account and the measured numbers; this list keeps the tell and the fix.

---

# Before you write

**❌ A text document with charts stapled to it.** Paragraphs of reasoning, a
term-and-sentence list, six bullet points, and one bar chart at the bottom of
the page.
The tell: every paragraph is individually defensible, which is exactly why the
failure survives review. It is the default outcome of writing first and
illustrating afterwards.
Instead: **draw the paragraph.**
→ [graphic-first.md](graphic-first.md#the-procedure) for the table, and for what
this cost the first version of the skill.
Caught by: the build fails at graphic density. The linter also reports
`text-heavy`, `text-heavy-mix` and `prose-only`.

**❌ A regeneration that reproduces the document it replaces.** Asked for a
fresh pass, you re-run the pipeline, write every step down, and arrive at the
same blocks.
The tell: the previous document was open while you did it. A prior artifact is a
tighter frame than the catalog, because it has already decided everything, and
the reasoning still feels like reasoning. Reporting the convergence honestly
("all three scenes survived re-derivation") dresses anchoring up as
transparency.
Instead: derive from the facts with the old spec closed until the scenes are
named. If you cannot say what a different spine would have looked like, you did
not pick one, you inherited one.
→ [pipeline.md](pipeline.md#1--establish-the-source)
Caught by: `meta.supersedes`. Nothing else in this skill can see it: the linter
reads one finished document and cannot ask whether a different one would have
been better.

**❌ Four numbers at the top of the page, because that is what goes there.**
A `kpi` row of labelled integers, every one of which a chart further down
explains properly.
The tell is arithmetic: **four numbers cannot each be the finding.** If they
could, you would have four documents. The block is the cheapest in the catalog:
it looks like a summary, needs no argument, and takes ten seconds, so it gets
added by reflex rather than chosen.
Instead: `hero_figure` when one number genuinely is the whole finding, and
nothing at all when none is. An empty slot is a better document, not an
incomplete one.
→ [narrative.md](narrative.md#the-spine-that-works-for-almost-every-argument)
Caught by: `leading-numbers`, which counts how many of a row's figures the rest
of the document restates.

**❌ A document that opens on its conclusion, for a reader who does not have the
subject.** The hero states the finding, the second block compares two designs,
the fourth is a glossary, and every section title is a noun phrase.
The tell: **the source material had this shape already.** A design document, a
spec, a codebase and a post-mortem all begin from the assumption that the
subject exists, is worth having, and is understood. Reasoning from them
reproduces that assumption, and a fact ledger, a claim and a claim-first spine
are all the frame of an argument. None is an explanation.
Instead: set `meta.mode` to `lesson`, write the ladder before choosing a single
form, and open on what the thing **is**.
→ [teaching.md](teaching.md)
Caught by: `forward-reference` and `ladder-order`, but only once a ladder is
declared. Nothing catches a document that never declared one, which is why the
mode is chosen at step 2 and stated in the handoff.

**❌ A glossary before the lesson.** A `definitions` block near the top, holding
the eight terms the document is about to use.
Why: it looks like exactly the right thing to do, and it is the back of a
textbook printed at the front. The reader is asked to memorise definitions for
things they have not seen, in words drawn from the same vocabulary they do not
have: "Tenant resolution: Host header looked up in a cached domains table"
teaches nobody anything.
Instead: introduce a term by **drawing the thing** at the rung that teaches it,
and keep `definitions` for the end, as the map from the plain words the page
taught back to the names the team uses.

**❌ One idea, never contested.** The document is built from the first angle
that occurred to you, and no alternative was ever written down.
The tell: every step in this pipeline is convergent, so the first angle is also
the last, and it is nearly always the *mechanism* angle, because that is the
shape the source material already has.
Instead: three spines, the images each would live on, then choose one yourself.
Handing the three back as a question is the work undone.
→ [pipeline.md](pipeline.md#3--write-three-spines-then-choose-one)

**❌ One composition, never contested.** The scene was chosen against a named
alternative, and then drawn exactly once.
The tell: the drawing runs left to right in the order the source listed things,
one box per noun, arrows between them. That arrangement was not decided, it was
inherited from the paragraph, which makes it the drawn version of picking the
nearest catalog block.
Instead: two compositions differing in something structural (what is at the
centre, what contains what, where the quantity lives), `ig.py sketch` both, keep
one, write one sentence on what the other could not show.
→ [scenes.md](scenes.md#draw-it-twice)

**❌ A bullet list.** Five discs, each carrying a clause.
Why: a bullet list is a paragraph wearing a disc. It has no shape, so it is
neither scannable nor readable, and it never has to justify its own length.
Instead: `chips` for parallel facts, `checklist` for do-and-don't, `process` if
they are secretly ordered, `definitions` if they are secretly a vocabulary.

**❌ Retyping a paragraph as a `table` because table cells are exempt.**
Why: it is the same move as reaching for report density, but it does not feel
like one, because every individual table is defensible and the build stays
green. The tell is a `table` whose cells are sentences rather than values,
usually three columns wide with a verb in the middle one.
Instead: ask what shape the rows are. Options against criteria are a `matrix`;
a sequence is a `process`; items with a before and an after are a `dumbbell`;
counts per named thing are a `bar` or a `lollipop`. Keep the table when the
reader genuinely needs to look a value up.
Caught by: `text-heavy` counts authored tables (the twins stay exempt),
`text-heavy-mix` counts `ig-table` as a text block, and `undrawn-section`
fires on a section carried by tables or prose with nothing drawn in it.

**❌ Reaching for `--density report` because the text did not fit.**
Why: the budget is the design constraint, not an obstacle to it. Report density
exists for documents that genuinely are prose with figures, and choosing it to
avoid rewriting is how a graphic document turns back into a written one.
Instead: rewrite to the cap, or draw the idea. If report density really is
right, say why in the document.

---

**❌ A diagram labelled in the system's own identifiers.** Nodes reading
`skipped_bucket`, `is_active`, `AccountPrimary`, `provider_email_sends`.
Why: it is what the word budget selects for. Under a 6-word label cap the
identifier is the cheapest possible label, and it is accurate, which makes it
feel rigorous rather than lazy. The document then passes every check in this
skill while being readable only by the person who wrote the code.
The tell: you chose a name because it was short and true, and you have not
asked whether the reader has ever seen it.
Instead: label the mark in words and demote the identifier to the table twin,
where it stays exact and reachable without being the only thing on offer. When
the term itself is the subject, define it in `definitions` **before** the
section that uses it.
Caught by: `undefined-vocabulary`, which counts identifier-shaped tokens outside
footnotes and twins. It cannot see an ordinary word you have redefined, and
"bucket", "audience" and "category" are how that failure usually looks.

**❌ Vocabulary invented in the document and never defined in it.** A word from
ordinary English, given a private meaning, then used forty times.
Why: it never looks like jargon, so no reviewer flags it and no linter can. The
worst cases are words whose everyday sense actively misleads: an "audience" that
is not the people who read it but the rule for computing an address.
Instead: name it in step 2, and either define it or rename it to what it is.

---

# Before you ship

Run every entry below against the rendered document, with the PDF or the shots
open. Everything above this line is already decided by now.

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

**❌ A subtitle with nothing to say.** A restated title, a mood, a category:
"An overview of the pipeline."
Why: it spends the reader's first line teaching them that the small text on
this page can be skipped.
✅ A subtitle exists only when there is a finding to state flatly. Otherwise it
is deleted, not filled.

This applies to `hero`, block and step titles alike. Section titles are where the
slogan register returns first, because a one-word title feels clean: "The
mechanism", "The guard", "Answering". Name what the section establishes.

**❌ The journal-caption test, applied to a lesson's section openers.** "Custom
domains and TLS certificate issuance." "Tenant resolution." "Certificate
lifecycle."
Why: the test is right and its range is not universal. A journal caption is
written by a specialist for peers who have already been introduced to the
subject, so using it as the register for a *section opener in a lesson* selects
precisely for the voice that makes a document unreadable to a newcomer.
✅ **In `lesson` mode a section title is the question that section answers**, in
the reader's words, and the `lede` is the answer: "Why does one program serve a
hundred addresses?" / "The answer is the only thing a visitor actually types."
Chart titles are unaffected: a chart of data still names its subject, its scope
and its period, and the journal-caption test is still exactly how to check it.
The tell that the insider register has returned is a **noun phrase with no
verb**. Nobody has ever asked a question in that shape.
→ [teaching.md](teaching.md#the-register)

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
option wins, the metric that moved the wrong way. **In a lesson, this is
`misconception`**: the thing being contradicted is what the reader already
wrongly believes, not a rival position, and a lesson without one is a document
telling a newcomer that everything is straightforward.

**❌ An analogy with no mapping.** "Think of it like a hotel," and then the
document moves on.
Why: an analogy with no named correspondences is a mood, and the reader will
import everything else they know about hotels, including the parts that are
wrong. The failure lands later, in something they conclude on their own and you
never see.
✅ `analogy` with a `pairs` row per correspondence, and a `note` naming where it
breaks: "unlike a hotel, no company can ever see inside another company's site".

**❌ A bridge doing a block's job.** A connective sentence that turns out to
carry a fact nothing else on the page carries.
Why: it is how a lesson quietly turns back into prose with pictures beside it.
The test is mechanical: **would cutting this bridge remove information from the
document?** If yes, that information belonged in a block, and the bridge is
narrating rather than handing off.
✅ Draw it. The build caps bridges at one per section and refuses two in a row,
and a build that fails that cap is telling you something more useful than "you
are over budget": each bridge you cannot cut is a rung whose picture does not
stand on its own.

**❌ Ending on a chart.** The document stops at its last piece of evidence.
✅ End on the implication. Evidence with no conclusion gets one supplied by the
reader.

**❌ No method block.** Numbers with no source, period, or exclusions.
✅ `footnotes`, always, on anything carrying figures.

### The look

**❌ Emoji or icon-font glyphs anywhere.**
✅ An icon is SVG, drawn in the page's own visual language, or absent.

**❌ The AI-slop look.** Gradient heroes, glassmorphism cards, glow effects,
generic dashboard chrome.
Why: it is the costume of a thousand generated pages, and a reader who has
seen it discounts the content on sight.
✅ The page looks composed for this subject and no other.

**❌ Your own default composition.** Every mechanism a left-to-right chain of
rounded rectangles and arrows, every establishing shot one centred object
floating in whitespace, three spines that are one spine reworded.
Why: these are not decisions, they are the shapes a model reaches for on any
subject, which makes them the drawn equivalent of slop.
✅ Treat the first composition that comes to mind as already spent, and draw
the second. When a default is caught, rewrite the element; a softened cliché
is still the cliché.

**❌ Decoration that encodes nothing.** Abstract shapes, dividers and
flourishes placed to fill space.
✅ Every visual element encodes something. The whitespace is the ornament.

**❌ Marketing words, anywhere.** "Unlock", "seamless", "powerful", and the
slogan cadence they travel in, including labels and legends.
✅ Museum-plaque register: sober, literal, flat. The imagination is spent on
the drawings, never the words.

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

**❌ Shipping without looking at the render.** The linter checks structure, not
whether the argument lands or whether a label collided.
✅ `shoot` it and read the shots end to end at 100%; when a PDF was asked for,
read the PDF too.

**❌ `--no-tables` on anything that will be printed or read by assistive
technology.**
✅ The table view is the only way a value inside an unlabelled mark stays
reachable on paper.

**❌ Half-empty pages accepted as normal.**
Why: a tall grid row moves to the next page whole, leaving a gap that looks
deliberate and is not.
✅ `check_document.py` reports it as `sparse-pages`; the fixes, in order, are
[print-pdf.md](print-pdf.md#the-rules-that-actually-bite) rule 3.

**❌ `paper: bleed` on a multi-page document.**
✅ Bleed simulates margins with padding, which applies to the first page only.
Single sheets only.

**❌ Relative image paths.**
✅ Chrome renders from a temporary profile. Absolute `file://` or data URIs.

**❌ Colour as the only channel, in a document that will be photocopied.**
✅ Build it once with `--theme mono` and see what stops working.

## The stranger

**❌ Passing your own review.** You read the page, it reads clearly, you ship.
Why: you are the one reader who cannot read this document. You know what every
label means, which picture the argument turns on, and what the page was meant to
say, so you see the intended document rather than the printed one. This is not
carelessness, and care does not fix it. Every check in this file that you run on
your own document is run by someone who already knows the answer.
✅ `python3 scripts/ig.py blind out/doc.html` prints a brief for a reader with no
context. Send it verbatim to a subagent: retelling it in your own words leaks the
answer into the question. What comes back is evidence about the document, not a
request for changes.
→ [pipeline.md](pipeline.md#then-give-it-to-someone-who-has-not-seen-it)

**❌ A stranger who cannot say what it is about, treated as a stranger problem.**
The tell: "they would get it with the context." The document is the context.
✅ Their one-sentence summary is the document's actual claim. If it is not the
claim you wrote at step 2, the spine is not on the page, and the fix is
structural, not a polish pass.
