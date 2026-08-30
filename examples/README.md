# Examples

Five complete documents plus a proof sheet. Read a spec before writing your
first one: they are the fastest way to see how a claim becomes blocks.

```bash
cd ~/.claude/skills/infographic
python3 scripts/ig.py selftest --render       # builds all five to examples/out/
python3 scripts/ig.py catalog --sheet examples/out/catalog-default.pdf
```

Start with the first two. One is the reference for authored drawings, the other
for teaching a subject to somebody who has never met it; the rest exercise
breadth.

| Spec | Shape | Theme | What it demonstrates |
|---|---|---|---|
| [`scroll-architecture.json`](../fixtures/specs/scroll-architecture.json) | continuous | `rentos` | **The reference for authored work.** Three drawings the catalog could not do: hostnames converging on one door, a blast radius on a full-bleed dark field, a request beam narrowing through four layers. Plus `stack`, `swimlane` and `chips` on rails. |
| [`architecture-explainer.json`](../fixtures/specs/architecture-explainer.json) | A4, 4pp | `rentos` | **The reference for `lesson` mode, and the only fixture built from a brief.** Read [`fixtures/briefs/architecture-explainer.json`](../fixtures/briefs/architecture-explainer.json) first: it is the document, and the spec is what it compiled to. An `analogy` before any mechanism, a `progressive` adding one part at a time, one figure, and the glossary kept deliberately last. Uses `analogy`, `progressive`, `figure`, `bridge`, `stack`, `process`, `swimlane`, `checklist`, `definitions`. |
| [`concept-explainer.json`](../fixtures/specs/concept-explainer.json) | A4 explainer | `default` | Teaching a concept: process → evidence → comparison → caveats. Uses `process`, `line`, `stat`, `comparison`, `bar` with a reversed ordinal ramp, `unit`, `dumbbell`, `checklist`, `definitions`. |
| [`data-report.json`](../fixtures/specs/data-report.json) | A4 report | `rentos` | Findings from data, on brand: Instrument Serif headings, olive palette, warm paper. Uses `hero` with embedded stats, `dumbbell`, `column` with emphasis, `meter`, `share_bar`, `funnel`, `heatmap`, `matrix`. |
| [`poster-a3.json`](../fixtures/specs/poster-a3.json) | A3 poster | `default` | A single scannable sheet with a dominant figure and three named zones. Exercises the structure family: `sankey`, `process`, `timeline`, `cycle`, `quadrant`, `venn`, `tree`, `pyramid`, `treemap`, `slope`, `likert`, `lollipop`, `diverging`. |

**None of the five opens with a `kpi` row.** Two of them used to, which is how
that habit spread; see [narrative.md](../references/narrative.md#the-spine-that-works-for-almost-every-argument).

**The architecture explainer used to be the opposite of what it now is.** It
opened on a score of 66 out of 75, compared two proposed designs in its second
block, put a glossary fourth, and titled its third section "Custom domains and
TLS certificate issuance". Every block was correct, it passed every check in this
repository, and nobody outside the team could read a line of it. It is kept as
the worked example of the fix rather than of the failure, and the failure is
described in [teaching.md](../references/teaching.md).

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
a deliberately mixed document for exercising the extractor: a periods table, a
shares table, a before/after pair, negative values, dated sentences, ordering
language, contrast language, pros/cons, and headline figures in prose.

```bash
python3 scripts/ig.py extract fixtures/sources/support-review.md
```

It should surface `line`, `share_bar`, `dumbbell`, `diverging`, `bar`,
`timeline`, `process`, `cycle`, `comparison`, `checklist`, `stat` and `unit`,
each with the evidence that suggested it. That list is **evidence, not a
design**: take it to `references/choosing-a-visual.md` and decide there.

## A note on the outputs

`examples/out/` is generated. Delete it freely; any of the commands above
rebuild it.
