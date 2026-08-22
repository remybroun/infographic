# The document spec

The spec is the contract between deciding and drawing. It is plain JSON, so it
can be diffed, reviewed, regenerated and re-themed without touching a renderer.

```bash
python3 scripts/ig.py new out/spec.json        # starter
python3 scripts/ig.py render out/spec.json     # spec -> HTML -> PDF -> lint
```

---

## Shape

```json
{
  "meta":    { ... },
  "options": { ... },
  "blocks":  [ { "type": "...", ... } ]
}
```

Or, when the page is authored rather than assembled:

```json
{
  "meta":    { ..., "encodes": "concept" },
  "style":   "…the document's CSS…",
  "body":    "…its markup, inline SVG and all…",
  "blocks":  [ { "id": "…", "type": "…" } ]
}
```

**A spec is authored when it carries `body`**, and then the 12-column grid is
not emitted at all. `blocks` stays optional and holds catalog blocks the page
places itself, with `<div data-block="the-id"></div>`.
→ [authored.md](authored.md)

## `meta`

| Key | Default | Meaning |
|---|---|---|
| `title` | `"Infographic"` | browser/PDF title; a literal description of the subject and scope, never a slogan |
| `theme` | `"default"` | `default` · `iris` · `rentos` · `mono`, or a path to a theme JSON |
| `page` | `"a4"` | `a4` `a4-land` `letter` `letter-land` `a3` `a3-land` `slide` `poster` |
| `mode` | `"argument"` | `argument` for a reader who has the concept; `lesson` for one who does not, which makes `ladder` required and enforced. See [teaching.md](teaching.md) |
| `ladder` | none | the explanation, as ordered rungs. Required in `lesson` mode, checked in both. See below |
| `density` | `"graphic"` | `graphic` enforces the text budget and refuses body prose; `lesson` keeps the refusal with room to teach; `report` allows prose. See [graphic-first.md](graphic-first.md) |
| `scenes` | none | one sentence, 8 words minimum, saying what the catalog carried when the document draws nothing by hand. Clears the linter's `no-authored-figure`. See [scenes.md](scenes.md) |
| `encodes` | none | **required on an authored spec.** `"concept"` (no data drawn), or `{columns, rows}`, or a list of those, each rendered as a table twin. See [authored.md](authored.md) |
| `paper` | `"panel"` | `panel` · `none` · `bleed`, see [print-pdf.md](print-pdf.md) |
| `spacing` | `"normal"` | `tight` · `normal` · `airy`. Scales the gutter, the row gap and the padding inside a framed block together. Reach for `tight` only when the blocks ARE the subject (a specimen sheet, a dashboard, a reference card); in a document that argues, the gap is what tells a reader one idea has finished |
| `lang` | `"en"` | document language, for screen readers and hyphenation |
| `tables` | `true` | emit table-view twins |
| `texture` | `false` | turn on the texture channel for CVD / mono print |
| `footer_left` | `title` | running footer, left |
| `footer_right` | `date` | running footer, right |
| `date`, `author`, `source` | none | available to `hero` |

Page choice is not cosmetic: type scale, margins, gutters and default block
heights all derive from it. A poster is not an A4 document printed larger.

### `meta.ladder`

The explanation, written before any form is chosen, as an ordered list of rungs.

```json
"ladder": [
  {"says": "One program can run many separate company websites.",
   "introduces": ["application"], "at": "one-program"}
]
```

| Key | Meaning |
|---|---|
| `says` | the rung in plain words. **Capped at 24 words** |
| `introduces` | the terms this rung teaches. Each capped at 4 words |
| `at` | the `id` of the block where the rung lands |

The build refuses a `lesson` whose rungs land out of order (`ladder-order`) or
whose terms appear in an earlier block (`forward-reference`). Both are warnings
in `argument` mode. Check it without building:

```bash
python3 scripts/ig.py ladder out/spec.json
```

## `options`

Free-form object merged into every block's `options`, then overridden by that
block's own `options`. Use it for document-wide formatting defaults.

## `blocks`

An ordered list. Each entry names a `type` from the
[catalog](catalog/README.md) and carries that type's payload plus the shared
keys documented in [catalog/README.md](catalog/README.md#shared-payload-keys).

Blocks flow through a 12-column grid in order. A block occupies `span` columns
and the next one continues on the same row if it fits.

```json
{"type": "line",  "span": 8, "title": "Trend",  "x": [...], "series": [...]},
{"type": "stat",  "span": 4, "label": "...", "value": 31},
{"type": "prose", "span": 12, "text": "What the chart above means."}
```

## Worked minimum

```json
{
  "meta": {"title": "Enquiry conversion by first-reply time", "theme": "default", "page": "a4"},
  "blocks": [
    {"type": "hero",
     "kicker": "Analysis",
     "title": "Enquiry conversion by first-reply time, 214 operators, H1",
     "subtitle": "Operators replying within an hour convert at 9.1%, against 1.4% after 24 hours."},

    {"type": "stat", "span": 4,
     "label": "Enquiries never answered", "value": 33, "unit": "%",
     "compact": false,
     "note": "A tile because nothing below explains it. The conversion figures
              are not tiled: the bar carries them properly."},

    {"type": "prose", "span": 12,
     "text": "Price sensitivity is real but second order. The chart below holds "
             "price constant and varies only reply time."},

    {"type": "bar", "span": 8,
     "title": "Bookings per 100 enquiries by first-reply time",
     "subtitle": "Conversion more than halves between the 1-4h and 4-24h bands.",
     "categories": ["Under 1h", "1-4h", "4-24h", "Over 24h"],
     "values": [9.1, 7.8, 3.2, 1.4],
     "unit": "%", "decimals": 1, "sort": null,
     "ordinal": true, "ordinal_reverse": true,
     "note": "Bookings per 100 enquiries. Same price band throughout."},

    {"type": "callout", "span": 4, "tone": "key",
     "title": "What this does not say",
     "text": "Fast repliers may simply be better operators overall. This is a "
             "correlation across 214 operators, not a controlled test."},

    {"type": "footnotes",
     "items": ["Source: platform enquiry log, H1.",
               "Excludes enquiries auto-declined for unavailable dates."]}
  ]
}
```

## Validation

The compiler fails loudly on an unknown `type`, `theme`, `page`, `paper` or
`spacing`, and warns (without failing) on the design problems it can detect:

- more series than the palette has slots;
- a scatter with more than three series;
- a donut past six segments, a venn past three sets;
- KPI tiles that will not fit the block's width;
- `paper: bleed` on a document that looks multi-page;
- a theme declaring `@font-face` files that are not on disk, which Chrome would
  otherwise substitute silently.

Warnings print to stderr and are surfaced by `ig.py render`. They are advice from
the checks, not the design review, that is still yours.

## Programmatic use

```python
import sys; sys.path.insert(0, "scripts")
from build import build

spec = {"meta": {...}, "blocks": [...]}
html, warnings = build(spec, "out/doc.html", theme="rentos")
```

`build()` accepts a path or a dict, so a spec can be generated in code without
ever touching disk. Individual blocks render standalone too:

```python
from lib.registry import render_block
from lib.theme import Ctx, Theme

svg = render_block({"type": "bar", "categories": ["A"], "values": [1]},
                   Ctx(Theme.load("default"), width=672))
```
