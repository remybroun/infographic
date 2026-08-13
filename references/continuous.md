# The continuous target (`page: scroll`)

A document that is not cut into sheets. One page, read on a screen, as long as it
needs to be.

## Why it exists

Everything else in this skill serves paper: `@page`, the margin box, the ink
measurement, the row-gap fix, `break-inside: avoid`. That machinery is correct
and it should stay. But a page box cannot give you a **full-bleed section**, and
a full-bleed section is often the single move that makes a document read as
designed rather than as laid out. It also rations vertical space, because every
millimetre of air is a millimetre closer to a page break, so a paginated document
is always slightly compressed in a way a screen document never has to be.

Choosing it:

| Choose `scroll` when | Choose paper when |
|---|---|
| it will be read on a screen | it will be printed, attached, or filed |
| at least one section earns going edge to edge | it is a reference sheet |
| the argument benefits from vertical air | page count is part of the brief |
| you want one dark, arresting section | it must survive a photocopier |

If nothing in the document earns a bleed, `page: a4` is the honest choice and it
prints properly. The linter says so, as a note.

## What changes

```json
{"meta": {"page": "scroll", "theme": "rentos"}}
```

- **Measure** is 1080px with 40px side margins, and the 12-column grid works
  exactly as it does on paper.
- **Type scale** goes up: 16px body, 66px hero, 36px section. Screen reading
  takes more size than paper at the same apparent scale.
- **Row spacing** goes from 26px to 40px.
- **`break-inside: avoid` is dropped**, because there is nothing to break inside.
- **Below 860px** every block collapses to a full row. At that width a 4-span
  tile is 180px and its labels stop fitting, so the grid is doing damage rather
  than work.

## Bleed

```json
{"type": "figure", "bleed": true, "invert": true, "…": "…"}
```

`bleed` runs the block the full viewport width. `invert` puts it on ink and flips
the drawing kit's tokens so the same classes keep working on a dark field.
Together they are the arresting section. **Use it once.** A document with three
dark bleeds has no emphasis, only stripes.

Two implementation notes worth not re-deriving:

- The escape is `margin-left: calc(50% - 50vw)`, not `width: 100vw`. The latter
  overflows by the scrollbar width and gives the whole document a horizontal
  scrollbar.
- Inner padding is `max(margin, calc(50vw - measure/2 + margin))`, so the
  content inside a bleed stays aligned with the rest of the document instead of
  running to the window edge.

`bleed` on a paginated document is a build warning, not an error: inside a page
box there is no viewport to break out of, so it is ignored.

## Linting

Paper checks do not follow the document off paper. `sparse-pages`,
`near-empty-page`, `long` and the per-page word budget are all skipped, because
on a continuous document they would fire on behaviour that is exactly correct.

The word budget still applies, charged **per block** instead of per page: 45
words at graphic density, 160 at report. That number is derived rather than
picked, title (9) + subtitle (16) + note (18) is the most chrome one block may
legally carry, so a document averaging that much has every block running at
maximum text, which is the signature of an essay wearing block formatting.

## Output

The deliverable is the **HTML**. It is self-contained: fonts, styles and drawings
are all inline, so it opens anywhere with no build step and no network.

```bash
python3 scripts/ig.py render out/spec.json --out-dir out
```

renders the HTML, shoots the sections to PNG, and lints. It does **not** produce
a PDF unless you pass `--pdf`, because producing one by default would be quietly
reintroducing the page box the target exists to escape.

A scroll document still carries a sane `@page` (A4, 14mm margins) and pulls its
bleeds back inside the box when printed, so somebody who hits Cmd-P anyway gets
something reasonable rather than content cropped at the paper edge. That is a
fallback, not the artifact.

## Looking at it

```bash
python3 scripts/ig.py shoot out/doc.html
```

A continuous document has no pages to rasterise, so shots are built by hiding
every block outside a window and screenshotting what is left, one Chrome run per
shot. Shot boundaries follow `section` blocks where the document has them,
because those are the author's own grouping and therefore better boundaries than
an arbitrary block count.

Slower than rasterising a PDF. It is the only way to see a document whose whole
point is not fitting in a page box.
