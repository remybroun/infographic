# Layout & the grid

Twelve columns, a fixed gutter, and blocks that never split. Everything else
follows from those three facts.

---

## The grid

```
content width = trim − 2 × side margin
column        = (content − 11 × 20px) / 12
span(n)       = column × n + 20px × (n − 1)
```

A block's SVG is authored at **exactly** its rendered width, so nothing is scaled
and no text is optically distorted. That is why `span` is a real layout decision
rather than a hint: a `bar` at span 6 is drawn differently from the same bar at
span 12, not the same drawing shrunk.

Blocks flow in order. A block continues on the current row if it fits, otherwise
it starts a new one.

## Choosing spans

| Intent | Spans |
|---|---|
| The section's argument | 12 |
| Evidence plus its reading | 8 + 4 |
| Two parallel comparisons | 6 + 6 |
| Three peers | 4 + 4 + 4 |
| A figure beside its context | 4 + 8 |
| Dense poster row | 6 + 6, or 7 + 5 |

Every block has a sensible default from the registry, so `span` is worth setting
only when you want something other than that.

**A page of 12-spans has no hierarchy.** Vary the spans so the reader can tell
which block carries the section.

## Minimum widths that actually matter

Some blocks stop working below a width, and the compiler tells you rather than
letting them collapse:

- **`kpi`** needs about 132px per tile. Below that it stacks to one column and
  warns. Three tiles want span 6+; four want span 8+.
- **`bar` / `lollipop`** reserve up to 38% of their width for category labels.
  Long names at span 4 leave almost nothing for the bars.
- **`matrix`** needs roughly 90px per column plus the row-label gutter.
- **`sankey`** reserves right-hand space for its terminal labels; below span 8 the
  ribbons become too thin to trace.
- **`treemap`** hides labels in cells under 54 × 30px. At small spans, most cells
  go unlabelled and the table view does all the work.
- **`process`** switches to vertical automatically past four steps or ~90
  characters of step text, the horizontal cards collapse to about twenty
  characters per line otherwise.

## Blocks never split

`.ig-block` sets `break-inside: avoid`, so a chart is never cut in half. The
consequence is the one thing to design around: **a tall row moves to the next
page whole**, leaving a gap behind it.

When a page looks half empty:

1. Reduce the tallest block's `height`.
2. Split a 12-span into two 6-spans, the row can break between them.
3. Reorder so a short block fills the gap.
4. Set `allow_break: true` on a long `table` or `prose`, which genuinely can
   split across pages.
5. Delete an unnecessary `break: before`.

`check_document.py` reports the blocks-per-page ratio as `sparse-pages`.

## Framing

Blocks are unframed by default, which reads as one continuous page. Reach for a
frame when a block is genuinely a separate object:

- `frame: "card"`: bordered surface. Use for a block that stands apart from the
  page's argument, like a worked example.
- `frame: "tint"`: filled panel, no border. Quieter; good for a supporting
  block beside a main one.

**Do not frame everything.** Same-size cards of icon-plus-heading-plus-text as
the page structure is the lazy container, and nested cards are always wrong. If
every block is a card, the frames have stopped carrying information.

## Vertical rhythm

Row gap is 26px, column gutter 20px, deliberately unequal, so rows read as
separate bands while blocks within a row read as grouped.

Use `divider` sparingly. A `section` block already sets a strong rule; adding a
divider next to one double-marks the boundary. `spacer` exists for the rare case
where a page needs air that content cannot supply, not as a layout tool.

## The squint test

Blur the page until the text is unreadable. You should still be able to identify:

- which block is the primary one;
- which blocks are grouped;
- where each section begins.

If everything reads at the same weight, the spans are too uniform, the frames are
doing too much, or there is no dominant element. Fix the structure, not the
colours.
