# Graphic first

**The picture carries the idea. The words label it.**

That is the whole rule. Everything below is either an explanation of why it is
enforced in code rather than left to judgement, or a procedure for obeying it.

---

## Why this is a budget and not advice

Version 1 said "reduce text" in four reference files and shipped an eight-page A4
explainer carrying **2,086 words**, 261 a page, with one bar chart. Every
paragraph in it was individually defensible. Three mechanisms produced it: a
linter that warned when prose was *absent*, a catalog that listed the text blocks
first as "where the argument lives", and word counts left to taste, which under
time pressure always chooses one more clarifying sentence.

So the budget now runs in `scripts/lib/density.py` before anything renders, and a
breach is a build error. The linter's checks were inverted to match. If you find
yourself fighting the budget, it is doing its job: what you are trying to say
needs to be drawn.

## The three densities

| | `graphic` (default) | `lesson` | `report` |
|---|---|---|---|
| Body prose | **refused** | **refused** | allowed |
| `bridge` | **refused** | 40 words | 90 |
| Title | 14 words | 16 | 22 |
| Subtitle / lede | 16 | 24 | 40 |
| Item detail | 12 | 18 | 60 |
| Label | 6 | 8 | 12 |
| Note / source | 18 | 24 | 60 |
| Callout | 24 | 32 | 90 |
| Words per page | 150 | 260 | 900 |

`lesson` exists because the budget and the instruction "explain this to someone
who has never met the subject" were in direct conflict, and the budget won every
time: it is enforced in code and the instruction was a paragraph of prose. The
label cap is the conflict in miniature. Under six words, `skipped_bucket` costs
one and "the recipient switched that group off" costs six, so the cheapest
accurate label is always the one only the author can read; at eight there is
room for the ordinary words plus the qualifier that makes them exact.

It is **graphic density with room to teach, not a step towards `report`**. Body
prose stays refused, the picture still carries the idea, and 260 is a measured
floor rather than a compromise: the smallest allowance that fits a four-rung
ladder's bridges, its longer labels and one definition on a page that is still
mostly picture. A lesson page over 260 words has stopped teaching and started
narrating. → [teaching.md](teaching.md)

The title cap is 14 rather than 9 on purpose. Nine words is not enough to name a
subject, a scope and a period, and a cap that cannot fit a description will be
satisfied by an aphorism instead. The looser cap exists to be spent on being
specific, not on being longer.

`report` exists for documents that genuinely are prose with figures: a written
recommendation, a post-mortem, a methodology appendix. It is opt-in through
`meta.density` or `--density report`. It is **never** the answer to "my text did
not fit". If you reach for it, say why in the document.

Footnotes, table contents and `raw` are exempt from the per-field caps at every
density. A citation has to stay citable, and table cells are data rather than
argument.

**The exemption is per field, not per document.** A table's cells are never
measured against the 12-word `detail` cap, because a cell is a value. They are
still counted in the document's word total, because the exemption exists for
data and a table of sentences is prose that has been ruled into columns. If you
are moving text into a `table` to get under the budget, you have found the hole
rather than the answer: see
[anti-patterns.md](anti-patterns.md#before-you-write).

## The procedure

**1. Write the claim as one sentence.** If you cannot, you do not have a block
yet. This has not changed and is still the most important step.

**2. Ask what kind of thing the sentence is.** Not what the data looks like:
what the sentence *is*. This is the step that decides everything.

This is the table. Everywhere else in the skill that says **draw the paragraph**
means this table; it is not repeated, so that it stays one edit.

| The sentence is… | Sounds like | Draw it as |
|---|---|---|
| a sequence | "first A, then B, then C" | `process`, `timeline` |
| a sequence that changes hands | "first they do A, then we do B" | `swimlane` |
| things resting on things | "the edge handles X, the app handles Y" | `stack`, `pyramid` |
| things containing things | "each region owns four teams" | `tree` |
| a comparison of two framings | "before, we…; now, we…" | `comparison` |
| options weighed against criteria | "five options against fifteen criteria" | `scorecard`, `matrix` |
| one score against a ceiling | "it scored 66 out of 75" | `gauge`, `meter` |
| one number that is the finding | "the whole thing is 2.5×" | `hero_figure`, `stat` |
| several short parallel facts | "the states are draft, pending, live" | `chips` |
| vocabulary the reader lacks | "a *bucket* is…" | `definitions` |
| a rule and its failure mode | "always X; never Y" | `checklist` |
| a quantity, share, or change | "X is bigger / fell / is made of" | the quantity, part and change families |
| something the reader already owns | "it works a bit like a hotel" | `analogy` |
| a wrong belief being corrected | "people think X, but actually Y" | `misconception` |
| parts that accumulate | "then you also need a second one, because…" | `progressive` |
| the hand-off between two rungs | "so far we have seen A; now B" | `bridge`, lesson density only |

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

The one exception is a `section` opener in `lesson` mode, which is the question
that section answers. It is narrow and it is not a loosening: a question is
still literal and still specific, it simply admits that the reader arrived
without the vocabulary a specimen label assumes.
→ [teaching.md](teaching.md#the-register)

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
- **Expand the term, cut the sentence.** The one move that runs against the
  count, and the one to make anyway. **An identifier is not a free word.**
  `skipped_bucket` costs one word and buys nothing from a reader who does not
  have the codebase; "recipient opted out" costs three and is the actual
  meaning. When the budget is tight, the sentence explaining a label is what to
  cut, and the label itself is what to spend on. A page nobody outside the team
  can read has not passed the budget, it has evaded it.

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

Then run it the other way, because the first test cannot fail on jargon:

> **Cover the graphics. Can a reader outside the team define every word left on
> the page?**

A diagram labelled `skipped_cooldown`, `is_active`, `AccountPrimary` passes the
first test perfectly. The shapes really do carry the argument, so covering the
text really does leave something that teaches. The reader simply has no idea
what any node is called. That failure is invisible to every check in this file
except this one, because the words are few, correct, and unreadable.

If a term survives the second test only because *you* know it, it is not a label,
it is a lookup key. Define it or rename it.

Then the third, which neither of the first two can fail on:

> **Read it in order. Does anything appear before the thing it depends on?**

A page can pass both cover-tests with every label in plain English and still be
unreadable, because the third block relies on an idea the seventh introduces.
That failure is invisible to a word count and to a jargon scanner, and it is the
one a reader experiences as "this was written for someone who already knows".
`meta.ladder` makes it checkable. → [teaching.md](teaching.md)
