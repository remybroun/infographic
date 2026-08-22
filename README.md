<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="branding/iris-dark.svg">
    <img src="branding/iris-light.svg" width="132" alt="the infographic mark">
  </picture>
</p>

<h1 align="center">infographic</h1>

<p align="center"><em>Give the world a shape.</em></p>

<p align="center">
<a href="https://github.com/remybroun/infographic/actions/workflows/selftest.yml"><img src="https://github.com/remybroun/infographic/actions/workflows/selftest.yml/badge.svg" alt="selftest"></a>
<a href="SKILL.md"><img src="https://img.shields.io/badge/version-3.2.0-5C6B2E" alt="version 3.2.0"></a>
<a href="#requirements"><img src="https://img.shields.io/badge/python-3.12%2B-5C6B2E" alt="Python 3.12+"></a>
<a href="GALLERY.md"><img src="https://img.shields.io/badge/block%20types-57-5C6B2E" alt="57 block types"></a>
<a href="#requirements"><img src="https://img.shields.io/badge/dependencies-0-5C6B2E" alt="dependencies 0"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-5C6B2E" alt="license MIT"></a>
<a href="branding/"><img src="https://img.shields.io/badge/branding-iris-5C6B2E" alt="branding"></a>
</p>

A skill that turns a document, a dataset or a topic into a designed visual
explainer: a print-ready PDF, or a continuous scrolling page whose HTML is the
deliverable.

It is not a chart library. It is a set of constraints that make a model produce
a graphic document instead of an essay with figures stapled to it, and most of
those constraints fail the build rather than advise.

```
/infographic <a topic, a path, or a pasted document>
```

## Install

```bash
git clone https://github.com/remybroun/infographic.git ~/.claude/skills/infographic
```

That is the whole install: a skill is a directory with a `SKILL.md` in it, and
Claude Code finds it on the next session. To scope it to one project instead of
every project, clone into `<project>/.claude/skills/infographic` instead.

## Verify

```bash
python3 scripts/ig.py selftest          # 409 assertions
python3 scripts/ig.py validate --all    # every theme through the colour checks
python3 scripts/ig.py selftest --render # also builds all six fixtures, to PDF
sh assets/build_gallery.sh              # rebuilds every image on this page
```

The first three are what CI runs on every push, and the badge above is that run.
The fourth is the reproduction command for the figures below: every image on this
page is output of the skill, and one command rebuilds all thirteen from source.

## What it produces

![Left, a page filled with body text labelled 2,086 words and one chart. An arrow marked budget leads right, to a page carrying a title, a bar chart and two short labels, labelled 150 words a page.](assets/produces.png)

The word budget in `scripts/lib/density.py` runs before anything renders, and a
breach is a build error. That number is not arbitrary: version 1 of this skill
shipped an eight-page explainer carrying **2,086 words and one chart**, and
every paragraph in it was individually defensible. The budget exists because
taste under time pressure always chooses "one more clarifying sentence".

## The vocabulary it draws with

![Six labelled groups, each showing three miniature specimens: bars, lollipops and heatmaps for quantity; lines, slopes and dumbbells for change; rings, waffles and share bars for part-to-whole; chains, trees and venns for structure; layers, lanes and chips for diagram; tiles, callouts and rules for editorial.](assets/forms.png)

57 block types across seven families, plus 64 aliases so a spec can be written in
ordinary words (`pie` → `donut`, `waffle` → `unit`, `2x2` → `quadrant`,
`flow` → `process`, `myth` → `misconception`).

That figure is a map. Below it are the blocks themselves, rendered: three sheets
out of ten in **[the specimen gallery](GALLERY.md)**, which draws all 41 forms
this repository has honest data for. Every number in it is read out of the repo
at build time, from the registry, the word budget, the five shipped fixtures,
the linter's own checks and `git log`, so it cannot drift from the code it
documents and nothing in it is invented to complete a shape.

![Six quantity charts rendered: a lollipop of how graphic each shipped example is, a heatmap of blocks per family, a bar chart of printable area for the nine render targets, a grouped column chart of graphic against text blocks, a scatter of blocks against graphic blocks, and a diverging bar chart of family use in the poster against the scrolling page.](assets/gallery-quantity.png)

![Five blocks rendered: a pyramid of the five principles in the order they override each other, a venn of what an authored figure shares with the built-in blocks, a process of the five commands, a cycle of render, look, find, fix, and a quadrant of the families by whether a claim needs numbers and whether it needs an order.](assets/gallery-principles-structure.png)

When the catalog has no shape for an idea, you draw it. A `figure` block takes
authored SVG and keeps every guarantee the built-in blocks make: required `alt`,
a required data twin, refused colour literals, and its labels charged against the
budget. Capped at three per document, because without a cap "draw the shape the
catalog lacks" becomes "hand-draw everything" and the consistency is gone.

![Four blocks rendered: a sankey from 57 block types through the families to whether each draws or sets text, a tree of the repository, an authored figure of three arguments over one set of facts with the chosen one highlighted, and a scorecard of the colour checks each theme passes beside a gauge of how much of the vocabulary a shipped example demonstrates.](assets/gallery-structure-diagram.png)

The authored drawing on that sheet is a `figure`. Three spines over one set of facts is
not a tree (they partition nothing), not a process (they are alternatives, not
steps) and not a quadrant (there are no axes). Naming the closest block type
needs a "well, sort of", which is the test for authoring the shape instead.

## How a document gets made

Steps 1–6 are judgement and cannot be automated. 7–11 mostly are.

1. **Source**: read it, or `ig.py extract source.pdf`
2. **Reader and mode**: who reads this, do they have the concept, which words
   are they missing?
2.5. **The ladder** (`lesson` mode): the explanation, before any form is chosen.
   `ig.py ladder out/ladder.json --brief`
3. **Three spines**: three arguments over the same facts, then choose one
4. **Target**: paper, poster, slide, or a continuous scrolling page
5. **Scenes**: which images does this live or die by, *before* opening the catalog
6. **Forms**: one per remaining claim
7. **Spec**: `ig.py new out/spec.json`, and every authored figure drawn twice,
   both compositions rendered alone with `ig.py sketch`
8. **Theme**: validated, never hand-picked
9. **Render**: `ig.py render out/spec.json --out-dir out`
10. **Look at it**: `ig.py shoot out/doc.html`. The linter never has. Then
    `ig.py blind out/doc.html`, because you cannot read your own document.
11. **Hand off**: the spec, the document, and how it was made

Three orderings are load-bearing. **The explanation before the argument**, because
a spine is a claim plus the reasoning that carries it, which is the frame of a
document for somebody who already knows what the subject is. **Three spines
before one is chosen**, because the first argument to arrive is nearly always the
*mechanism*. That is the shape the source is already in, and it is rarely the one
the reader has a stake in. And **scenes named before the catalog is opened**,
because once it is open the question silently changes from *what does this look
like?* to *which of the 57 shapes is closest?*

## Explaining, as opposed to arguing

For three versions this skill could choose a good form for any fact and could not
teach anything, and the cause was structural. Its first artifact was a fact
ledger. Its second was a claim, defined as *one sentence the reader should
believe by the end*. Both are the frame of an argument, so every document opened
on its conclusion and worked backwards, which is the shape of a page written for
somebody who already knows what the subject is.

```json
{"meta": {"mode": "lesson", "ladder": [
  {"says": "One program can run many separate company websites.",
   "introduces": ["application"], "at": "one-program"},
  {"says": "The web address is what tells it which company you want.",
   "introduces": ["web address"], "at": "address-picks"}
]}}
```

A ladder is the explanation, written before a single form is chosen: rungs in the
order a reader climbs them, each naming the terms it teaches and the block it
lands on. **A term used in a block that comes before the rung teaching it is a
build error.** That is the only check here that can see the insider register.
Every other one measures density, form or geometry, and a document passes all of
them while opening on a word the reader will not meet for four more blocks.

Each rung is capped at 24 words, and the cap is the point. "Reflect completely on
how to explain this before drawing anything" is the instruction that produced the
worst document this skill has shipped. An explanation written out in full before
the drawing starts is an essay, and the pictures get added to illustrate it.

`ig.py ladder --brief` hands the rungs alone to a reader with no context, before
anything is rendered, which is the same test `ig.py blind` runs at the end for
the price of a rebuild.

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
| A term used before the rung that teaches it | An explainer opened on a score and a glossary, and taught nobody anything, while passing every check above |

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

Every image on this page is `rentos`, so what you are looking at is a theme
doing its whole job: the olive lead, terracotta as the warm secondary, blue and
plum as separable companions, and Instrument Serif on the block titles over
Inter everywhere else. The serif is opt-in per theme (`type.block_title`), since
a theme whose display face *is* its sans gains nothing from it.

All three pass the computable colour checks: contrast, categorical separation,
and colour-vision-deficiency distance. A new brand theme is a JSON file, not
code, and its slot order is found by enumerating orderings and keeping the ones
that clear the gates, never by picking what looks nice. Brand olive and
terracotta are deliberately not adjacent slots: that pair measures a CVD ΔE of
4.5, so a protanope cannot separate them. The scorecard in the sheet above counts
the checks per theme; `mono` runs fewer of them because greyscale has fewer
categorical slots to separate, not because it scores worse.

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
  teaching.md           the ladder, and the mode that enforces it
  catalog/              the 57 block types, by family
scripts/
  ig.py                 the CLI
  build.py              spec → HTML
  check_document.py     the linter
  lib/density.py        the word budget
  lib/ladder.py         is anything explained before the thing it depends on
  lib/derivation.py     did a regeneration change anything
  lib/leading_numbers.py  is that stat row carrying its weight
fixtures/specs/       six complete, rendering worked examples
GALLERY.md            every form the skill draws, drawn
assets/
  gen_readme.py         the three slides on this page
  gen_gallery.py        the ten specimen sheets, from this repo's own data
  build_gallery.sh      rebuilds every image here in one command
  measure_blocks.py     how tall does each block lay out, so rows can be paired
  trim_png.py           crops the blank tail off a rasterised page
```

## Requirements

Python 3.12+ standard library, and a Chromium-family browser for rendering and
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

The sheets set `meta.spacing: "tight"`, which scales the gutter, the row gap and
the padding inside a framed block together. Scaling only the gap does not read as
tighter: two framed charts are held apart by pad + gap + pad, and at the default
that is 62px of which the gap is 26. `tight` is not the default, because in a
document that argues, the gap is what tells a reader one idea has finished.

The eleven pipeline steps and the guard table are not images. An ordered list and
a table render natively, are searchable and copyable, and follow your theme. An
image earns its place when the idea is spatial.

The three slides are the only place in this repo where `tables: false` is set.
The accessibility twin is a `<details>` element, and inside a raster image that
is a control nobody can operate, so the values it would carry sit in the prose
beside each figure instead. The specimen sheets keep their twins in the HTML.

Three things are still wrong, and none of them is faked:

- **The images are light, so they glare in dark mode.** Fixing that properly
  needs a validated dark theme, which does not exist yet.
- **The gallery build reports two warnings.** `near-empty-page` fires on the
  closing alias sheet at 3% ink. It is measuring correctly and measuring the
  wrong thing: that sheet is mostly full by area and almost empty by ink, because
  a grid of outlined chips is mostly the page showing through. The check is tuned
  for documents rather than specimen sheets, and it is reported rather than
  suppressed.
- **The `rentos` theme's fonts live outside this repo.** Its `fonts_dir` points
  at a sibling brand directory, so a fresh clone renders it in Georgia and Helvetica
  instead of Instrument Serif and Inter. The build now warns when a declared font
  file is missing rather than falling back in silence, but the assets are still
  not vendored here.

## The one thing the tooling cannot do

The linter checks structure. It has never once looked at a document, and it
cannot tell you that a label collided, that an arrow points at nothing, that the
drawing was the wrong drawing, or that the argument does not land.

`ig.py shoot` exists so that you can, and `ig.py sketch` so that looking at one
drawing costs two seconds rather than a full render, which is the difference
between a composition chosen and a composition settled for.

Then there is the part you cannot do either. The skill's whole claim is that a
stranger understands the page by looking at it, and the author is the one reader
who is not a stranger: you know what every label means and what the page was
meant to say, so you see the intended document rather than the printed one.
`ig.py blind` prints a brief for a reader with no context at all. What they say
it is about is what it is about.

## Branding

<img src="branding/iris-light.svg" width="76" align="left" alt="">

The mark at the top of this page is the **iris**: a disc split down the middle,
an ordered colour ramp in each half, and the two halves running that ramp in
opposite directions, so the disc inverts across its own axis. It is drawn after
two Hilma af Klint paintings, *The Swan* (1915) for the structure and Series
VIII *Utgångsbild* (1920) for the fill.

<br clear="left">

The duality is carried by lightness rather than hue, which is why the one-colour
version is not a degraded copy of it and why it still reads at 16px. Its eight
ramp steps pass the same validator this skill points at every theme, run in
`--ordinal` mode because a ramp is not a set of categories.

Files, usage rules and the exact gate commands are in
[branding/](branding/README.md). Everything there is generated:

```bash
python3 branding/gen_brand.py
```

## License

MIT. See [LICENSE](LICENSE).
