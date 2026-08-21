# Print & PDF

The output is a PDF, so the page is a real constraint rather than a scroll with
a border. Everything here is verified behaviour of headless Chrome, which is the
renderer this skill uses.

```bash
python3 scripts/ig.py render spec.json --out-dir out
python3 scripts/render_pdf.py out/doc.html -o out/doc.pdf --wait 3000
```

---

## Why Chrome

It is the only engine on an ordinary machine that handles the whole feature set
this skill's CSS depends on: `@page`, CSS grid, `break-inside`,
`print-color-adjust`, `text-wrap: balance`, and modern colour. WeasyPrint and
wkhtmltopdf each drop several of those **silently**, which produces a PDF that is
subtly wrong rather than one that fails.

`render_pdf.py` finds Chrome, Chromium, Edge or Brave automatically; override
with `CHROME_PATH` or `--chrome`.

## The rules that actually bite

**1. Backgrounds vanish unless you force them.** Chrome drops background colours
when printing unless `print-color-adjust: exact` is set. `document.css` sets it
on `html`. Every fill in this skill depends on it.

**2. Paper cannot be full-bleed and correctly margined at once.** Verified: the
canvas background paints the `@page` **content box** and stops at the margins, no
matter which element carries it. The obvious fix, `@page { margin: 0 }` plus
padding) gives a top margin on the first page only, because padding applies once
to a block, not once per page. So `meta.paper` is an explicit three-way choice:

| `paper` | Effect | Use for |
|---|---|---|
| `panel` (default) | tinted content box inside a white margin frame | multi-page documents |
| `none` | nothing painted; the printer's paper shows | plain, ink-frugal output |
| `bleed` | `@page` margin 0, margins simulated as padding | **single sheets only**, posters |

`bleed` warns when the document looks multi-page, because pages after the first
would start hard against the paper edge.

**3. A grid row moves whole.** `.ig-block` sets `break-inside: avoid`, so a block
never splits mid-chart. The consequence is that a tall row jumps entirely to the
next page and leaves a gap behind it. This is the single most common reason an
output looks sparse.

**Measure before you guess**: `python3 scripts/ig.py measure spec.json` prints
every block's real laid-out height and word count, and how far the stack runs
past a sheet. Block height is not guessable from the payload, it comes out of
text wrapping, legend rows and the theme's type scale. Fixes, in order of
preference:

- reduce the block's `height` so the row fits;
- split a 12-span into two 6-spans, which can break between them;
- move the block earlier or later;
- set `allow_break: true` on a long `table` or `prose` block, which genuinely can
  split;
- remove an unnecessary `break: before`.

`check_document.py` reports this as `sparse-pages` with the block-per-page ratio.

**4. Row spacing is a block margin, never `row-gap`.** A grid row-gap is
unbreakable. When one lands on a page boundary Chrome spends an entire page on
it, and a `break: before` on the next block then adds its own page, so the
document gets a sheet carrying nothing but the running footer. Measured on the
architecture fixture: `row-gap: 26px` gave 5 pages with page 4 blank; moving the
same 26px to `margin-bottom` on `.ig-block` gave 4 pages with none blank, and
the visible spacing is identical because every block in a row carries the same
margin. `document.css` does it the margin way. Do not change it back.

The linter measures this directly. `page_ink()` rasterises each page at 12dpi
and reports `near-empty-page` when a page falls under 10% coverage and under 62%
of the median page. For calibration: a healthy A4 page in this skill's output
runs 11-19% covered, a stranded-block page runs 6-8%, and a blank one runs
under 2%.

**5. Fixed elements repeat per page.** That is how the running footer works, and
it is out of flow, content runs underneath it unless space is reserved. The
document reserves it with `padding-bottom` when a footer exists. If you add your
own fixed furniture, reserve its space too.

**6. `details` must be forced open in print.** Table-view twins are collapsed on
screen and force-opened under `@media print`, because a sheet of paper cannot
perform a disclosure interaction. Never ship `--no-tables` for a document that
will be printed or read by assistive technology.

**7. Absolute paths for assets.** Chrome renders from a temporary profile;
relative image paths will not resolve. Use `file:///abs/path` or a data URI.

**8. Raise `--wait` when assets are heavy.** The default virtual-time budget is
1800ms. Embedded fonts and large rasters may need 3000-5000ms. A PDF with
fallback fonts or missing images usually means the budget was too short.

**9. Never pass `--user-data-dir`.** Measured on macOS with Chrome 151: passing
any user-data-dir (a fresh temp directory *or* a reused persistent one) while
the desktop Chrome is running makes headless hang indefinitely, even on a
one-line document. The same documents export in 2-3 seconds without it. Chrome
already keeps the headless profile separate from the GUI one, so the flag buys
nothing.

`render_pdf.py` therefore omits it. The `--profile` option exists for containers
and CI-as-root, and carries the same warning. If a render ever takes minutes,
this is the first thing to check, a normal document is a few seconds, and the
timeout message says so.

## Page geometry

| Page | Trim | Margins (T/S/B) | Content width | Body |
|---|---|---|---|---|
| `a4` | 210 × 297mm | 16/16/15 | 672px | 13.4px |
| `a4-land` | 297 × 210 | 14/16/13 | 1002px | 13.0px |
| `letter` | 215.9 × 279.4 | 16/16/15 | 694px | 13.4px |
| `a3` | 297 × 420 | 20/20/18 | 972px | 15.5px |
| `a3-land` | 420 × 297 | 18/20/16 | 1436px | 15.0px |
| `slide` | 338 × 190 | 14/16/12 | 1156px | 14.5px |
| `poster` | A2, 420 × 594 | 24/24/22 | 1406px | 18px |

Columns are `(content − 11 × 20px gutter) / 12`. A block's SVG is authored at its
exact rendered width, so nothing is scaled and no text is distorted.

## Fonts

System fonts need no embedding and are the default. A theme with a `fonts_css`
block (like `rentos`) embeds real font files by absolute `file://` path; Chrome
subsets and embeds them in the PDF.

If headings come out in the wrong face, check in this order: the font file
exists at the path the theme resolves; `--wait` is long enough; the CSS family
name matches the `@font-face` family exactly.

## Verifying the output

Render, then **look at it**. The linter checks structure, not whether the
argument lands:

```bash
python3 scripts/ig.py render spec.json --out-dir out   # renders and lints
python3 scripts/check_document.py out/doc.html --pdf out/doc.pdf
```

Then open the PDF and read it end to end at 100%. Specifically check:

- no label is clipped or overlapping another;
- no page is more than half empty without a reason, and none is blank;
- the running footer sits below the content, not over it;
- **cover the text: does the page still teach you anything?** If not, the
  graphics are decoration and the words are the document;
- the document still makes sense printed in black and white. If it does not,
  build it again with `--theme mono` and see what breaks.
