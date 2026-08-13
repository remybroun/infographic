# Graphic first

**The picture carries the idea. The words label it.**

That is the whole rule. Everything below is either an explanation of why it is
enforced in code rather than left to judgement, or a procedure for obeying it.

---

## Why this is a budget and not advice

The first version of this skill said "reduce text" in four different reference
files. It then shipped an eight-page A4 architecture explainer carrying **2,086
words**, roughly 261 per page, with one bar chart on page two and pages of
term-and-paragraph rows.

Nothing in that document was indefensible on its own. Each paragraph explained
something real. The failure was structural, and it had three causes:

1. **The linter rewarded prose.** It warned `no-prose` when a chart had no
   sentence beside it, and `chart-dump` when visuals outnumbered "explanatory
   passages" two to one. Both checks pushed in exactly the wrong direction.
2. **The catalog led with the text blocks.** `prose`, `bullets`, `definitions`
   and `checklist` were listed first and described as "where the argument
   lives", so they were reached for first.
3. **Nothing said no.** Word counts were a matter of taste, and taste under time
   pressure always chooses "add one more clarifying sentence".

So the budget now runs in `scripts/lib/density.py`, before anything renders, and
a breach is a build error. The linter's checks were inverted to match. If you
find yourself fighting the budget, the budget is doing its job: what you are
trying to say needs to be drawn.

## The two densities

| | `graphic` (default) | `report` |
|---|---|---|
| Body prose | **refused** | allowed |
| Title | 14 words | 22 |
| Subtitle / lede | 16 | 40 |
| Item detail | 12 | 60 |
| Label | 6 | 12 |
| Note / source | 18 | 60 |
| Callout | 24 | 90 |
| Words per page | 150 | 900 |

The title cap is 14 rather than 9 on purpose. Nine words is not enough to name a
subject, a scope and a period, and a cap that cannot fit a description will be
satisfied by an aphorism instead. The looser cap exists to be spent on being
specific, not on being longer.

`report` exists for documents that genuinely are prose with figures: a written
recommendation, a post-mortem, a methodology appendix. It is opt-in through
`meta.density` or `--density report`. It is **never** the answer to "my text did
not fit". If you reach for it, say why in the document.

Footnotes, table contents and `raw` are exempt from the per-field caps at both
densities. A citation has to stay citable, and table cells are data rather than
argument.

**The exemption is per field, not per document.** A table's cells are never
measured against the 12-word `detail` cap, because a cell is a value. They are
still counted in the document's word total, because the exemption exists for
data and a table of sentences is prose that has been ruled into columns. If you
are moving text into a `table` to get under the budget, you have found the hole
rather than the answer: see
[anti-patterns.md](anti-patterns.md#the-one-that-produced-version-2).

## The procedure

**1. Write the claim as one sentence.** If you cannot, you do not have a block
yet. This has not changed and is still the most important step.

**2. Ask what kind of thing the sentence is.** Not what the data looks like:
what the sentence *is*. This is the step that decides everything.

| The sentence is… | Draw it as |
|---|---|
| a sequence | `process`, `timeline` |
| a sequence that changes hands | `swimlane` |
| things resting on things | `stack`, `pyramid` |
| things containing things | `tree` |
| a comparison of two framings | `comparison` |
| options weighed against criteria | `scorecard`, `matrix` |
| one score against a ceiling | `gauge`, `meter` |
| one number that is the finding | `hero_figure`, `stat` |
| several short parallel facts | `chips` |
| vocabulary the reader lacks | `definitions` |
| a rule and its failure mode | `checklist` |
| a quantity, share, or change | the quantity, part and change families |

**3. Write the label, not the explanation.** The title says, literally and
specifically, what the reader is looking at. The subtitle states the finding in
one flat sentence. Nothing else is needed, because the graphic is already showing
them the evidence.

Both are **sober and descriptive**. A title is a specimen label, not a headline:
it names the subject, the scope and the period, and it survives being read out
loud in a meeting without embarrassing anyone. No aphorisms, no metaphors, no
"X, not Y" antithesis, no verb-phrase slogans. If a title would work as a
chapter epigraph, it is wrong. See
[anti-patterns.md](anti-patterns.md#titles).

**4. Build, and let the budget fail you.** Read the violations as a work list.
Each one names a paragraph that wants to become a picture.

## What the words are for

Text at graphic density does exactly four jobs. Anything else is prose wearing a
small font.

- **Titles** name what the reader is looking at, literally: subject, scope,
  period. Descriptive, never rhetorical.
- **Subtitles** state the conclusion, once, in one plain line.
- **Labels** sit on marks: axis names, chip text, node names, step titles.
- **Indicators** are the small values beside a mark: a delta, a share, a count,
  a status word.

The register to aim for is a **museum wall label**, not an essay. Assume the
reader is scanning, standing up, with the picture already in front of them.

## Writing to the cap

Rewrite, never truncate. These are the four moves that actually work:

- **Delete the throat-clearing.** "It is worth noting that the system will
  typically resolve the tenant from the Host header" becomes "Tenant resolved
  from the Host header". 15 words to 5, nothing lost.
- **Move the number into the graphic.** If the sentence exists to carry a
  figure, the figure belongs on the mark and the sentence disappears.
- **Split one detail into two labels.** A twelve-word step detail is often two
  six-word chips.
- **Cut the justification.** Documents explain *what*, not *why we are allowed
  to say it*. If the caveat is load-bearing, it belongs in `footnotes`, which is
  exempt from the budget for exactly this reason.

## What this does not license

Cutting words is not permission to cut meaning.

- **A graphic still needs its table view.** Every chart ships its accessibility
  twin, and the twin does not count against the word budget. Never pass
  `--no-tables` to buy headroom.
- **Never fabricate to fill a shape.** A missing series stays missing. A
  `scorecard` with invented per-criterion scores is worse than a `bar` of the
  real totals, because it looks like more evidence than you have.
- **Sources survive.** `footnotes` is exempt so that method, caveats and
  provenance are never what gets cut first.
- **A document with no words at all is not the goal.** `no-graphics` and
  `prose-only` are errors, but so is a chart nobody can interpret. The subtitle
  stating the conclusion is the minimum, not an optional extra.

## Checking it landed

```bash
python3 scripts/ig.py render spec.json --out-dir out
```

The linter reports `text-heavy` (over budget per page), `text-heavy-mix` (prose
blocks outnumbering graphics), `near-empty-page` (measured ink coverage) and
`no-graphics`. Then open the PDF and apply the real test:

> **Cover the text. Does the page still teach you anything?**

If it does not, the graphics are decoration and the words are the document. Go
back to step two.
