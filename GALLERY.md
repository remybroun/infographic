# The specimen gallery

Every form this skill draws, drawn. Nothing on this page is a mock-up or a
sketch of a chart: each sheet is a rendered A4 page out of the same pipeline any
document goes through, and each one is trimmed to its content. Forty-one
specimens over ten sheets, in the `rentos` theme.

**The data is this repository.** Every number here is read at build time from the
block registry, `density.CAPS`, the five shipped fixture specs, the linter's own
`add(...)` calls and `git log`. Nothing was typed in twice, so the gallery cannot
quietly drift from the code it documents, and nothing was invented to complete a
shape. Rebuild the whole page with:

```bash
sh assets/build_gallery.sh
```

**Rows flow, they are not broken per family.** Forcing a page break before each
family left four sheets nearly blank. Letting the rows run means a family's last
half-width specimen shares a sheet with the next family's first, which is what
the compound sheet names below record.

## Quantity

![Six charts. A lollipop chart of the share of blocks that are graphics in each shipped example, 54 to 67 percent. A heatmap of how many blocks each example takes from each family. A horizontal bar chart of printable area for the nine render targets, from 603 cm² for Letter to 2,495 cm² for the A2 poster. A grouped column chart of graphic against text blocks. A scatter plot of blocks against graphic blocks. A diverging bar chart of family use in the poster against the scrolling page.](assets/gallery-quantity.png)

`lollipop` `heatmap` `bar` `column` `scatter` `diverging`. How graphic each
shipped example actually is; which families each draws from; the printable area
of every render target; and whether a longer document is a more graphic one. It
is not: the scatter is close to a straight line through the origin, which is the
finding. Two of the five examples land on the identical point, so they share one
label rather than being nudged apart, because moving a real value to make room
for its own label is the one thing a chart may never do.

The diverging chart is a real signed comparison, not a bar chart with a baseline
moved: two documents of one subject each, reaching for opposite halves of the
catalog.

## Guards, and the start of change

![A matrix of eight guards against what each one needs before it can run, ticked and crossed across four columns. Below it, a line chart of the checks the linter enforced after each commit, 25 rising to 29, and an area chart of repository size after each commit, spiking to 1,201 KB.](assets/gallery-guards-change.png)

`matrix` `line` `area`. The matrix earns its space because the rows genuinely
differ. Its first draft put the nine render targets against four properties and
eight of the nine rows came out identical, which is a table pretending to be a
finding.

The line is the one place in this repository `zero: false` is the honest call:
bars start at zero because length encodes magnitude, but a line encodes
movement, and 25 to 29 against a zero baseline is a flat line that says nothing.
The area chart's spike is four page screenshots landing in the repo and then
being replaced.

## Change, and part-to-whole

![Six blocks. A dumbbell chart of the words allowed in each field at report against graphic density. A slope chart of blocks per family in the poster against the scrolling page. A meter showing three authored figures against a cap of three. A share bar of the eleven pipeline steps split into judgement and tooling. A funnel from 57 registered block types down to those a shipped example uses, and those two or more use. A treemap of the 57 block types by family.](assets/gallery-change-part.png)

`dumbbell` `slope` `meter` `share_bar` `funnel` `treemap`. On the slope chart,
structure and diagram change places, which is what a slope chart is for. The
meter is a value against a real ceiling rather than an arbitrary one: three
authored figures against a cap of three.

## Part-to-whole, and the principles

![A donut of linter checks by what they do to the build, 31 percent fail, 58 percent warn, 12 percent note. A unit chart of block types that draw against those that set text, 77 squares to 23. A pyramid of the five principles in the order they override each other.](assets/gallery-part-principles.png)

`donut` `unit` `pyramid`. Five ways to read one whole appear across these two
sheets, each picked for a different reason: relative area when the sizes are
wildly different, a circle when there are at most six parts, countable squares
when a ratio should stay literal, a stage-by-stage drop, and a split read once.

The unit chart normalises to a hundred squares, so a square is one percent and
not one block type. Its note says the underlying count instead, because a note
that contradicts the legend printed directly above it is worse than no note.

## The principles, and structure

![A pyramid of the five principles in the order they override each other. A venn of what an authored figure shares with the built-in blocks. A vertical process of the five commands the tooling provides. A cycle of render, look at it, find the collision, fix the spec. A quadrant placing the families by whether a claim needs numbers and whether it needs an order. A sankey from 57 block types through the families to whether each draws or sets text.](assets/gallery-principles-structure.png)

`venn` `process` `cycle` `quadrant` `sankey`. The cycle is the loop the linter
cannot close for you: it checks structure, and it has never once looked at a
document. The quadrant's note says what it is: placement is a judgement about
the form, not a measurement. A 2×2 is worth drawing when all four corners are
named, not when the dots are precise.

## Structure, and diagram

![Four blocks. A sankey from 57 block types through the families to whether each draws or sets text. A tree of what is in this repository. An authored figure of three arguments over one set of facts, with the chosen one highlighted. A scorecard of the colour checks each of the three themes passes, and a gauge of how much of the vocabulary a shipped example demonstrates.](assets/gallery-structure-diagram.png)

`sankey` `tree` `figure` `scorecard` `gauge`.

The figure is the one specimen the catalog cannot supply. Three spines over one
set of facts is not a tree (they do not partition anything), not a process (they
are alternatives, not steps) and not a quadrant (there are no axes). Naming the
closest block type needs a "well, sort of", which is the test for authoring the
shape instead.

## Diagram, and teaching

![Four blocks. A swimlane of the eleven pipeline steps across two lanes, you and tooling. A layer stack of what Claude loads in the order it loads it. An analogy putting a recipe beside a ladder, three correspondences mapped row by row. A misconception block with what the pipeline assumed on the left, crossed out, and what a reader needs on the right, ticked.](assets/gallery-diagram-teaching.png)

`swimlane` `stack` `analogy` `misconception`. The swimlane is the argument for
the whole skill: steps two to six sit in the top lane and cannot be automated.

The two teaching blocks are the newest forms here and the only ones whose
subject is this skill's own failure. Every other family draws a relation between
things the reader already accepts, which is an enormous vocabulary for operating
on a subject and none at all for meeting one. The analogy names its own limit in
the note, because an analogy with no boundary is one a reader over-extends.

## Teaching, and editorial

![Four blocks. A progressive built in three stages, each adding one guard against jargon while the parts not yet added stay as empty outlines. A definitions list of spine, scene, twin and budget in four columns. A comparison of the outer two densities, 900 words a page against 150. A do and don't checklist for handing a document over.](assets/gallery-teaching-editorial.png)

`progressive` `definitions` `comparison` `checklist`. The progressive draws the
same three-part picture three times, accenting only what each stage adds: a word
budget, then a jargon scanner because the budget selects for jargon, then a
ladder because plain words can still arrive in the wrong order. Each stage exists
because the one before it left a hole the reader fell into, which is the shape
the block is for and something a finished diagram of all three cannot show.

The definitions block is at span 12 rather than 6. At half width it stacks its
four terms vertically and runs to 444px, which beside the 137px stat left 307px
of blank page, the single worst void in the document.

## Editorial

![A stat reading 2,086 words in the failed first version. A hero figure reading 150 words a page at graphic density. A callout carrying the pattern behind every guard in the repository.](assets/gallery-editorial.png)

`stat` `hero_figure` `callout`. The stat sets `compact: false`, because the block
otherwise renders 2,086 as "2.1K" and the exactness is the entire point of the
number. The checklist on the sheet above is at span 12 for the same reason as the
definitions list: at half width its two columns are about 90px each and every
item wrapped to one word a line, which the render showed and the linter did
not.

## Every alias

![Two chip grids holding all 64 aliases, each chip showing the ordinary word and the block type it resolves to: pie to donut, waffle to unit, 2x2 to quadrant, flow to process, myth to misconception.](assets/gallery-aliases.png)

`chips`. All 64 aliases, so a spec can be written in ordinary words. Split into
two blocks rather than one, and that is not cosmetic: a single grid was 911px at
60 aliases and 1,171px at 67, and `break-inside: avoid` means a block taller than
the 1,005px text area cannot be placed at all. It takes a page to itself,
overflows it, and strands two more. Halving it is what keeps the sheet count
stable as the alias table grows. It is last in the document for the older reason:
wherever it lands it fills a sheet, and at the end that sheet is the one page
allowed to be short.

## How the sheets are packed

A grid row is as tall as its tallest block, so pairing a 444px specimen with a
137px one buys 307px of blank page. Eight such pairs cost 1,400px, an entire
wasted sheet. Specimens are therefore ordered **by rendered height within their
family**, and a family with an odd number of half-width blocks leaves its
*shortest* over to meet the next family, not its tallest.

Those heights are not guessable from the payload, so they are measured:

```bash
python3 assets/measure_blocks.py assets/gallery_spec.json
```

It prints every block's laid-out height and totals the blank left in mismatched
pairs. That total is 344px across the whole document, down from 1,400px, and no
single pair wastes more than 63px.

## What is not on this page, and why

Five forms are missing, and the reason is the same in every case: this
repository has no honest data for them, and principle four says a missing series
stays missing.

| Form | Why it is absent |
|---|---|
| `likert` | Needs a real five-point survey. There isn't one. |
| `timeline` | Wants dates that carry the argument. Every commit here landed on one day. |
| `anatomy` · `image` | Both need a photograph or a screenshot as their subject. |
| `kpi` | Deliberate. It is the block this skill added a guard against, and putting a row of four numbers at the top of a specimen sheet would teach exactly the reflex that guard exists to stop. |
| `bridge` | Deliberate. A bridge is one sentence carrying a reader between two rungs of a ladder, so a bridge with nothing on either side of it is not a specimen of anything. It is drawn in context in the architecture fixture instead. |

## Two honest defects

**The images are light, so they glare in dark mode.** Fixing it properly needs a
validated dark theme, which does not exist yet. A theme is a JSON file, not code,
but it has to clear the contrast, categorical-separation and colour-vision gates
before it can ship.

**The build still reports two warnings.** `near-empty-page` fires on the closing
alias sheet at 3% ink against a 14% median, and once mid-document. It is
measuring correctly and measuring the wrong thing here: the alias sheet is most
of a page by area and almost nothing by ink, because a grid of outlined chips is
mostly the page showing through. The check is tuned for documents rather than
specimen sheets, and it is left reported rather than suppressed.
