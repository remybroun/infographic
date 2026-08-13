# Examples

Three complete documents plus a proof sheet. Read a spec before writing your
first one — they are the fastest way to see how a claim becomes blocks.

```bash
cd ~/.claude/skills/infographic
python3 scripts/selftest.py --render          # builds all three to examples/out/
python3 scripts/ig.py catalog --sheet examples/out/catalog-default.pdf
```

| Spec | Shape | Theme | What it demonstrates |
|---|---|---|---|
| [`concept-explainer.json`](../fixtures/specs/concept-explainer.json) | A4 explainer | `default` | Teaching a concept: process → evidence → comparison → caveats. Charts serve paragraphs. Uses `process`, `line`, `kpi`, `comparison`, `bar` with a reversed ordinal ramp, `unit`, `dumbbell`, `checklist`, `definitions`. |
| [`data-report.json`](../fixtures/specs/data-report.json) | A4 report | `rentos` | Findings from data, on brand: Instrument Serif headings, olive palette, warm paper. Uses `hero` with embedded KPIs, `dumbbell`, `column` with emphasis, `meter`, `share_bar`, `funnel`, `heatmap`, `matrix`. |
| [`poster-a3.json`](../fixtures/specs/poster-a3.json) | A3 poster | `default` | A single scannable sheet with a dominant figure and three named zones. Exercises the structure family: `sankey`, `process`, `timeline`, `cycle`, `quadrant`, `venn`, `tree`, `pyramid`, `treemap`, `slope`, `likert`, `lollipop`, `diverging`. |

## The catalog sheet

`ig.py catalog --sheet out.pdf --theme X` draws **every** registered block with
sample data in one document. Two uses:

- **Vet a new theme** across the whole vocabulary at once, rather than
  discovering at page four that the ordinal ramp is unreadable.
- **Browse the forms** when you are unsure what a block looks like.

It is also how the narrow-`stat` bug was found: seeing every block at its
minimum span makes sizing failures obvious in a way that no assertion did.

## Sources

[`fixtures/sources/support-review.md`](../fixtures/sources/support-review.md) is
a deliberately mixed document for exercising the extractor — a periods table, a
shares table, a before/after pair, negative values, dated sentences, ordering
language, contrast language, pros/cons, and headline figures in prose.

```bash
python3 scripts/ig.py extract fixtures/sources/support-review.md
```

It should surface `line`, `share_bar`, `dumbbell`, `diverging`, `bar`,
`timeline`, `process`, `cycle`, `comparison`, `checklist`, `stat` and `unit`,
each with the evidence that suggested it. That list is **evidence, not a
design** — take it to `references/choosing-a-visual.md` and decide there.

## A note on the outputs

`examples/out/` is generated. Delete it freely; any of the commands above
rebuild it.
