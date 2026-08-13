# The block catalog

Every visual this skill can draw, grouped by the reader's job. The registry in
`scripts/lib/registry.py` is the machine-readable twin of these files, if they
disagree, the registry is right and the doc needs fixing.

Run `python3 scripts/ig.py catalog` for the live list, or
`python3 scripts/ig.py catalog --sheet out/catalog.pdf` to render a proof sheet
showing every block drawn with sample data in the current theme.

**Start with [diagram.md](diagram.md).** It holds the forms that absorb what
would otherwise become paragraphs, which is the commonest failure this catalog
exists to prevent.

| File | Family | Blocks |
|---|---|---|
| **[diagram.md](diagram.md)** | **The forms that absorb paragraphs** | `stack` `swimlane` `scorecard` `gauge` `chips` |
| [quantity.md](quantity.md) | How much, and how items compare | `bar` `column` `lollipop` `diverging` `likert` `scatter` `heatmap` `matrix` |
| [change.md](change.md) | Movement over time or between two states | `line` `area` `dumbbell` `slope` `timeline` |
| [part-to-whole.md](part-to-whole.md) | Share, composition, proportion | `share_bar` `unit` `donut` `treemap` `funnel` `pyramid` `meter` |
| [process-and-time.md](process-and-time.md) | Sequence and flow | `process` `cycle` `funnel` `timeline` `sankey` |
| [structure-and-relation.md](structure-and-relation.md) | Hierarchy, overlap, position | `tree` `venn` `quadrant` `matrix` `sankey` `anatomy` |
| [editorial.md](editorial.md) | Claim, framing, figures | `hero` `section` `quote` `callout` `stat` `kpi` `hero_figure` `table` `checklist` `definitions` `comparison` `image` `footnotes` · plus `prose` and `bullets`, **report density only** |

## Shared payload keys

Every block accepts these; block-specific keys are documented per family.

| Key | Type | Meaning |
|---|---|---|
| `type` | string | registry name or alias (required) |
| `id` | string | anchor id, and what warnings are reported against |
| `span` | 1-12 | grid columns; defaults to the registry's value for the type |
| `title` | string | figure caption above the visual |
| `subtitle` | string | one line under the title; say what the reader should notice |
| `note` | string | small print under the visual: method, caveat, definition |
| `source` | string | rendered as "Source: …" under the note |
| `frame` | `card` \| `tint` | draw the block as a bordered card or a tinted panel |
| `break` | `before` \| `after` | force a page break |
| `allow_break` | bool | permit the block to split across pages (default: never) |
| `class` | string | extra CSS class |
| `skip` | bool | keep the block in the spec but do not render it |
| `options` | object | per-block overrides merged over `spec.options` |

## Shared value-formatting keys

Accepted by every block that prints a number.

| Key | Default | Effect |
|---|---|---|
| `currency` | `""` | prefix, e.g. `"$"`, `"£"`, `"€"` |
| `unit` | `""` | suffix, e.g. `"%"`, `"h"`, `"kg"` |
| `decimals` | `0` | decimal places |
| `compact` | `false` | 1284 → 1.3K, 4200000 → 4.2M |
| `table` | `true` | emit the table-view twin (turning this off is an accessibility regression) |
| `value_label` | `"Value"` | column header in the table view |
| `category_label` | `"Category"` | first column header in the table view |

## Shared colour keys

| Key | Effect |
|---|---|
| `emphasis` | index or category name, that one takes the accent, everything else the de-emphasis gray |
| `ordinal` | `true` when the categories are genuinely ordered: takes the one-hue ramp |
| `ordinal_reverse` | put the dark end of the ramp at the start of the sequence |
| `palette` | explicit list of hex values; you own the validation if you use it |
| `alt_hue` | use the theme's second sequential hue (for a second ramp on one page) |

## The four rules no block may break

1. **One axis.** Never two y-scales on one plot.
2. **Fixed slot order, never cycled.** A ninth series folds into "Other", facets,
   or changes form.
3. **The gap and the ring do the separating.** Never a stroke drawn around a mark.
4. **Every value stays reachable.** Direct labels or the table view, never a
   value that exists only inside a mark too small to label.
