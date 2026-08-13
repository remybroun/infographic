---
name: infographic
description: Turn text, a document, or a topic into a designed, graphic-first visual explainer: a print-ready PDF or a continuous scrolling page. Extracts the facts, decides which images the document lives on, draws them, and renders a themed document where the pictures carry the ideas and the text is titles and indicators only. Use when the user wants an infographic, a visual explainer, a one-pager, a data poster, a concept diagram, an architecture diagram, a chart-driven report, or asks to "visualize", "explain visually", "make a diagram of", or "turn this into a graphic". Covers 52 visual forms (bar, line, dumbbell, slope, funnel, sankey, treemap, waffle, quadrant, venn, tree, timeline, process, cycle, matrix, stack, swimlane, scorecard, gauge, chips, plus authored figures for shapes the catalog lacks), an enforced text budget, validated colour, print and screen layout, and accessibility. Not for interactive web dashboards or slide decks.
version: 3.0.0
user-invocable: true
argument-hint: "[source file, or the topic to explain] [--theme default|rentos|mono] [--page a4|a3|slide|scroll]"
allowed-tools:
  - Bash(python3 *)
---

You are producing a **graphic document**, not a written one. The pictures carry
the ideas. The text is titles and small indicators.

**The catalog is a floor, not a ceiling. When a claim has a shape the catalog
does not, draw the shape.**

Those two lines are in tension, and both are enforced. The first is a word budget
that fails the build: `scripts/lib/density.py` runs before anything renders, and
version 1 of this skill made it advice and shipped an eight-page explainer with
2,086 words and one chart. The second is the `figure` block, capped at three per
document: version 2 fixed the word count and then shipped an airless document
because the catalog had quietly become the boundary of imagination.

Five principles, in priority order:

1. **The graphic makes the point.** Cover the text: if the page still teaches
   you something, it is working. If not, start again from the claim.
2. **Draw the idea, not the nearest available shape.** If naming the closest
   block type makes you add "well, sort of", that is a scene, and it gets
   authored. → [scenes.md](references/scenes.md)
3. **The claim comes before the chart.** Every block earns its space by carrying
   one sentence. If you cannot write the sentence, do not draw the block.
4. **Never fabricate to complete a shape.** A missing series stays missing and
   gets said in words. Invented data is worse than no chart because it looks
   like evidence.
5. **Colour and contrast are computed, not chosen.** There is a validator. Run
   it. This holds inside an authored figure too, where the build refuses colour
   literals outright.

## Setup

Run once per session, from the skill directory:

```bash
cd <skill-base-dir> && python3 scripts/ig.py catalog
```

That prints every block with its "use when". If anything downstream misbehaves,
`python3 scripts/ig.py selftest` should be green before you debug your own spec.

## The pipeline

```bash
python3 scripts/ig.py extract source.pdf -o out/ledger.json   # 1. facts
                                                              # 2. name the reader, write the claim
                                                              # 3. THREE SPINES, then pick one
                                                              # 4. pick the target
                                                              # 5. NAME THE SCENES
                                                              # 6. pick a form per claim
python3 scripts/ig.py new out/spec.json                       # 7. write the spec
python3 scripts/ig.py render out/spec.json --out-dir out      # 8-9. build, render, lint
python3 scripts/ig.py shoot out/doc.html                      # 10. LOOK AT IT
```

Steps 2, 3, 5 and 6 are the skill. The rest is tooling. Two orderings are
load-bearing: step 3 forces three candidate arguments before one is chosen,
because the first one to arrive always wins otherwise and it is nearly always
the *mechanism* rather than the thing the reader cares about; and step 5 comes
before the catalog is opened, because once it is open it frames every idea and
the question silently changes from *what does this look like?* to *which of the
52 shapes is closest?* Full detail in [pipeline.md](references/pipeline.md).

## Which reference to load

Load the one that owns the decision in front of you. Do not read them all.

| You are… | Load |
|---|---|
| writing any spec at all | **[graphic-first.md](references/graphic-first.md)** |
| deciding what the document lives on | **[scenes.md](references/scenes.md)** |
| drawing one of those by hand | **[drawing.md](references/drawing.md)** |
| deciding what form a claim needs | **[choosing-a-visual.md](references/choosing-a-visual.md)** |
| running the whole job | [pipeline.md](references/pipeline.md) |
| reading a source document | [extraction.md](references/extraction.md) |
| ordering the blocks into an argument | [narrative.md](references/narrative.md) |
| writing block payloads | [catalog/](references/catalog/README.md) · [spec-schema.md](references/spec-schema.md) |
| building a scrolling page | [continuous.md](references/continuous.md) |
| setting spans, or fixing a half-empty page | [layout-grid.md](references/layout-grid.md) |
| adding a brand theme, or picking colours | [color-and-type.md](references/color-and-type.md) |
| debugging the PDF | [print-pdf.md](references/print-pdf.md) |
| checking honesty and accessibility | [integrity.md](references/integrity.md) |
| reviewing the finished document | **[anti-patterns.md](references/anti-patterns.md)** |

## The block catalog

52 block types across six families. Full detail in
[references/catalog/](references/catalog/README.md).

- **Diagram:** `figure` `stack` `swimlane` `scorecard` `gauge` `chips`
  → **reach here first when you catch yourself writing a paragraph**
  → `figure` is the authored drawing, for the shape nothing else has
- **Structure:** `process` `cycle` `quadrant` `venn` `tree` `sankey` `anatomy`
- **Quantity:** `bar` `column` `lollipop` `diverging` `likert` `scatter`
  `heatmap` `matrix`
- **Change:** `line` `area` `dumbbell` `slope` `timeline`
- **Part-to-whole:** `share_bar` `unit` `donut` `treemap` `funnel` `pyramid`
  `meter`
- **Editorial:** `hero` `section` `heading` `stat` `kpi` `hero_figure`
  `definitions` `checklist` `comparison` `callout` `quote` `table` `image`
  `footnotes` `chips` `divider` `spacer` `raw` · plus `prose` and `bullets`,
  which are report-density only

Aliases mean a spec can be written in ordinary words: `pie` → `donut`,
`waffle` → `unit`, `2x2` → `quadrant`, `flow` → `process`, `layers` → `stack`,
`criteria` → `scorecard`, `list` → `chips`, `draw`/`scene` → `figure`.

**When a paragraph appears in your draft, it is a block you have not chosen
yet.** A sequence is a `process`; a sequence that changes hands is a `swimlane`;
layers are a `stack`; options against criteria are a `scorecard`; a score
against a ceiling is a `gauge`; parallel short facts are `chips`. And when the
paragraph is asking you to *imagine* something (a beam thinning, a boundary
holding, a blast spreading), it is a `figure`.

## Rules that never bend

- **Text is titles and indicators.** Body prose is refused at graphic density.
  `--density report` exists for real prose documents and is opt-in only.
- **Titles are literal, specific and sober. Never slogans.** A title names the
  subject, the scope and the period, and would work as the caption of a figure in
  a journal paper: "Compound and simple interest on £10,000 at 7% over 30 years",
  not "Compound interest is a shape, not a rate". No antithesis ("X, not Y"), no
  metaphor, no bare verb phrases, no one-word section labels. The finding goes in
  the `subtitle`, stated flatly. A vague topic title is equally wrong: the fix is
  always **more specific, never more clever**.
  → [anti-patterns.md](references/anti-patterns.md#titles)
- **Three spines before one is chosen, and ask which.** The same facts support
  several documents; the first that occurs to you describes the mechanism,
  because that is the shape the source is already in. Write three, name the
  images each would live on, and present them with `AskUserQuestion`.
  **A regeneration never opens the previous spec before the scenes are named**,
  and declares `meta.supersedes` so the build can measure what actually moved.
  → [pipeline.md](references/pipeline.md) steps 1 and 3
- **Name the reader before the claim, and list what they will not know.** Every
  such term is either defined in `definitions` before it is used, or rewritten
  into words with the identifier demoted to the table twin. **An identifier is
  not a free word:** the budget makes `skipped_bucket` cost one and "recipient
  opted out" cost three, so jargon wins unless you spend against it.
  → [pipeline.md](references/pipeline.md) step 2
- **At most three authored figures.** Not a budget, a ranking exercise: which
  two or three images does this live or die by? Everything else goes on rails.
- **A figure keeps every guarantee.** `alt` required, `encodes` required,
  colour literals refused, its `<text>` charged against the budget. It is not
  `raw` with a nicer name.
- **One axis.** Never two y-scales. Two measures of different scale → two charts,
  small multiples, or `index_to_100`.
- **Fixed colour slots, never cycled.** A ninth series folds into "Other",
  facets, or changes form. It never gets a generated hue.
- **Every value stays reachable.** Every chart ships a table-view twin, and the
  twin does not count against the word budget. Never pass `--no-tables` on
  something that will be printed or read by assistive tech.
- **Colour is never the only channel.** Legends for ≥2 series, icons on status,
  arrows on deltas, shapes in matrix cells.
- **Bars start at zero.** Length encodes magnitude.
- **Look at it.** `ig.py shoot` renders the document to PNGs so you can. The
  linter checks structure; it has never once looked at the document.

## Targets

`a4` `a4-land` `letter` `a3` `a3-land` `slide` `poster` are paginated and print.

`scroll` is not paginated: full-bleed sections, real vertical air, and the HTML
is the deliverable. Choose it when the document will be read on a screen and at
least one section earns going edge to edge. → [continuous.md](references/continuous.md)

## Themes

`default` (neutral editorial) · `rentos` (RentRemote / RentOS olive editorial,
Instrument Serif headings) · `mono` (greyscale, print-safe, texture forced on).

All three pass the computable colour checks. Verify with
`python3 scripts/ig.py validate --all`, and preview a theme across the whole
vocabulary with `python3 scripts/ig.py catalog --sheet out/sheet.pdf --theme X`.

A new brand theme is a JSON file, not code. Do not hand-pick a slot order:
enumerate orderings and keep only those that clear the gates. See
[color-and-type.md](references/color-and-type.md).

## Worked examples

`fixtures/specs/` holds five complete, rendering documents. Read one before
writing your first spec:

- **`scroll-architecture.json`**: the reference for authored work. A continuous
  page with three drawings the catalog could not do: hostnames converging on
  one door, a blast radius on a full-bleed dark field, a request beam narrowing
  through four layers. Plus a stack, a swimlane and a chip grid on rails.
- **`architecture-explainer.json`**: A4, rentos. The reference for paginated
  graphic-first work: 117 words per page across four pages.
- `concept-explainer.json`: A4 explainer, default theme, teaches a concept
- `data-report.json`: A4 report, rentos theme, findings from data
- `poster-a3.json`: A3 one-page poster, exercises the structure blocks

`python3 scripts/ig.py selftest --render` builds all five.

## Requirements

Python 3.9+ standard library only, and Google Chrome / Chromium / Edge / Brave
for PDF rendering and screenshots (set `CHROME_PATH` if it is not found).
`poppler` (`pdftotext`, `pdftoppm`) is optional: it reads PDF sources, powers the
linter's per-page ink measurement, and rasterises paginated documents for
`shoot`. No pip installs, no npm, no matplotlib.
