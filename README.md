# infographic

A [Claude Code](https://claude.com/claude-code) skill that turns a document, a
dataset or a topic into a designed visual explainer: a print-ready PDF, or a
continuous scrolling page whose HTML is the deliverable.

It is not a chart library. It is a set of constraints that make a model produce
a graphic document instead of an essay with figures stapled to it, and most of
those constraints fail the build rather than advise.

```
/infographic <a topic, a path, or a pasted document>
```

## What it produces

![Left, a page filled with body text labelled 2,086 words and one chart. An arrow marked budget leads right, to a page carrying a title, a bar chart and two short labels, labelled 150 words a page.](assets/produces.png)

The word budget in `scripts/lib/density.py` runs before anything renders, and a
breach is a build error. That number is not arbitrary: version 1 of this skill
shipped an eight-page explainer carrying **2,086 words and one chart**, and
every paragraph in it was individually defensible. The budget exists because
taste under time pressure always chooses "one more clarifying sentence".

## The vocabulary it draws with

![Six labelled groups, each showing three miniature specimens: bars, lollipops and heatmaps for quantity; lines, slopes and dumbbells for change; rings, waffles and share bars for part-to-whole; chains, trees and venns for structure; layers, lanes and chips for diagram; tiles, callouts and rules for editorial.](assets/forms.png)

52 block types across six families, plus 49 aliases so a spec can be written in
ordinary words (`pie` → `donut`, `waffle` → `unit`, `2x2` → `quadrant`,
`flow` → `process`).

That figure is a map. Below it are the blocks themselves, rendered: three sheets
out of ten in **[the specimen gallery](GALLERY.md)**, which draws every form the
skill has. Every number in it is read out of this repository at build time, from
the registry, the word budget, the five shipped fixtures, the linter's own
checks and `git log`, so it cannot drift from the code it documents and nothing
in it is invented to complete a shape.

![Six part-to-whole blocks rendered: a treemap of the 52 block types by family, a donut of linter checks by what they do to the build, a unit chart of types that draw against types that set text, a funnel from 52 registered types to 14 used by two or more examples, a share bar of the eleven pipeline steps, and a meter of authored figures against a cap of three.](assets/gallery-part.png)

![Five structure blocks rendered: a pyramid of the five principles, a process of the five commands, a cycle of render, look, find, fix, a venn of what an authored figure shares with the built-in blocks, and a tree of the repository.](assets/gallery-structure-1.png)

When the catalog has no shape for an idea, you draw it. A `figure` block takes
authored SVG and keeps every guarantee the built-in blocks make: required `alt`,
a required data twin, refused colour literals, and its labels charged against the
budget. Capped at three per document, because without a cap "draw the shape the
catalog lacks" becomes "hand-draw everything" and the consistency is gone.

![Four diagram blocks rendered: a swimlane of the eleven pipeline steps across a you lane and a tooling lane, a scorecard of colour checks each theme passes, a gauge of 39 of 52 block types demonstrated by a shipped example, and an authored figure of three arguments over one set of facts with the chosen one highlighted.](assets/gallery-diagram.png)

The bottom-left panel there is a `figure`. Three spines over one set of facts is
not a tree (they partition nothing), not a process (they are alternatives, not
steps) and not a quadrant (there are no axes). Naming the closest block type
needs a "well, sort of", which is the test for authoring the shape instead.

## How a document gets made

Steps 1–6 are judgement and cannot be automated. 7–11 mostly are.

1. **Source**: read it, or `ig.py extract source.pdf`
2. **Reader and claim**: who reads this, and which words are they missing?
3. **Three spines**: three arguments over the same facts, then choose one
4. **Target**: paper, poster, slide, or a continuous scrolling page
5. **Scenes**: which images does this live or die by, *before* opening the catalog
6. **Forms**: one per remaining claim
7. **Spec**: `ig.py new out/spec.json`
8. **Theme**: validated, never hand-picked
9. **Render**: `ig.py render out/spec.json --out-dir out`
10. **Look at it**: `ig.py shoot out/doc.html`. The linter never has.
11. **Hand off**: the spec, the document, and how it was made

Two orderings are load-bearing. **Three spines before one is chosen**, because
the first argument to arrive is nearly always the *mechanism*. That is the shape
the source is already in, and it is rarely the one the reader has a stake in.
And **scenes named before the catalog is opened**, because once it is open the
question silently changes from *what does this look like?* to *which of the 52
shapes is closest?*

## What the build refuses to render

![Horizontal bars showing the words allowed in each text field at graphic density: figure text 40, quote 26, callout 24, note 18, subtitle 16, title 14, item detail 12, chart label 6.](assets/budget.png)

Three failures stop the build outright: a breach of the word budget, more than
three hand-drawn figures, and a colour literal inside a drawing. The rest warn.

Every one of these guards is a specific document that shipped and should not
have:

| Guard | The failure that produced it |
|---|---|
| Word budget, enforced in code | Version 1 shipped 2,086 words across eight pages carrying one chart |
| At most three hand-drawn figures | Version 2 fixed the word count and hand-drew everything, losing all consistency |
| Colour literals refused in a drawing | Hand-drawn figures are where computed colour slips first |
| Authored tables count toward the budget | A section retyped as three tables passed as clean; the cells were exempt |
| Identifiers counted, definitions required | A page carried 30 identifiers and no definitions block, and passed |
| Graphic forms compared against the last version | A regeneration came back 93% identical, with every step performed honestly |
| A `kpi` row is measured against the document | Four numbers led a page, and all four were explained better further down |
| `invert` without `bleed` | It flips the ink but paints no ground, so a drawing renders light-on-light |

The pattern is worth stating plainly, because it recurs:

> **When the output is wrong, look for the incentive that made the wrong thing
> cheapest, not for the missing rule.**

The linter rewarded prose, so it got prose. The catalog framed every idea, so
ideas came out catalog-shaped. Table cells were exempt from the budget, so
paragraphs became tables. A six-word label cap makes `skipped_bucket` cheaper
than "the recipient switched that group off", so pages came out labelled in
identifiers only their author could read.

## Themes

`default` (neutral editorial) · `rentos` (olive editorial, Instrument Serif) ·
`mono` (greyscale, print-safe).

All three pass the computable colour checks: contrast, categorical separation,
and colour-vision-deficiency distance. A new brand theme is a JSON file, not
code, and its slot order is found by enumerating orderings and keeping the ones
that clear the gates, never by picking what looks nice. The scorecard in the
diagram sheet above counts those checks per theme; `mono` runs fewer of them
because greyscale has fewer categorical slots to separate, not because it scores
worse.

```bash
python3 scripts/ig.py validate --all
python3 scripts/ig.py catalog --sheet out/sheet.pdf --theme mono
```

## Layout

```
SKILL.md              what Claude loads first
references/           one file per decision; load the one that owns it
  pipeline.md           the eleven steps
  graphic-first.md      the word budget, and why it is code
  scenes.md             deciding what gets drawn by hand
  anti-patterns.md      check every document against this before shipping
  catalog/              the 52 block types, by family
scripts/
  ig.py                 the CLI
  build.py              spec → HTML
  check_document.py     the linter
  lib/density.py        the word budget
  lib/derivation.py     did a regeneration change anything
  lib/leading_numbers.py  is that stat row carrying its weight
fixtures/specs/       five complete, rendering worked examples
GALLERY.md            every form the skill draws, drawn
assets/
  gen_readme.py         the three slides on this page
  gen_gallery.py        the ten specimen sheets, from this repo's own data
  build_gallery.sh      rebuilds every image here in one command
  trim_png.py           crops the blank tail off a rasterised page
```

```bash
python3 scripts/ig.py selftest          # 276 assertions
python3 scripts/ig.py selftest --render # also builds all five fixtures
```

## Requirements

Python 3.9+ standard library, and a Chromium-family browser for rendering and
screenshots (set `CHROME_PATH` if it is not found). `poppler` is optional for
building documents, where it reads PDF sources and measures per-page ink
coverage, and required for rebuilding the images on this page, which rasterise
through `pdftoppm`. No pip installs, no npm, no matplotlib.

## Notes on this page

Every image here was produced by the skill. `sh assets/build_gallery.sh` rebuilds
all thirteen from source in one command.

The three wide ones are 16:9 slides from [`gen_readme.py`](assets/gen_readme.py),
built as a paginated target because a README image is a fixed frame and a
paginated page fills it rather than leaving the dead column a scrolling layout
leaves. The specimen sheets are A4 portrait, and that is deliberate too: a text
label is a fixed size in millimetres, so the page *width* is what decides how
large it lands in GitHub's column. A4 portrait puts an 8pt label at roughly 12px;
the 338mm slide puts the same label at roughly 7px.

The eleven pipeline steps and the guard table are not images. An ordered list and
a table render natively, are searchable and copyable, and follow your theme. An
image earns its place when the idea is spatial.

The three slides are the only place in this repo where `tables: false` is set.
The accessibility twin is a `<details>` element, and inside a raster image that
is a control nobody can operate, so the values it would carry sit in the prose
beside each figure instead. The specimen sheets keep their twins in the HTML.

Two things are still wrong, and neither is faked:

- **The images are light, so they glare in dark mode.** Fixing that properly
  needs a validated dark theme, which does not exist yet.
- **The gallery build reports one warning.** `near-empty-page` fires on the
  change sheet at 6% ink. It is measuring correctly: line and slope charts put
  less ink on a page than filled ones. The check is tuned for documents rather
  than specimen sheets, and it is reported rather than suppressed.

## The one thing the tooling cannot do

The linter checks structure. It has never once looked at a document, and it
cannot tell you that a label collided, that an arrow points at nothing, that the
drawing was the wrong drawing, or that the argument does not land.

`ig.py shoot` exists so that you can.
