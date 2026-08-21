# Narrative: how the document is built

A collection of correct charts is not an infographic. What makes it one is that
the blocks are in an order that changes the reader's mind. This file is about
that order.

---

## Pick the document shape first

| Shape | Page | Blocks | The reader | Structure |
|---|---|---|---|---|
| **Lesson** | a4, scroll | 10-18 | has never met the subject | what it is → why it exists → one rung at a time |
| **Explainer** | a4 | 8-16 | has the concept, wants it deepened | claim → mechanism → implication → caveats |
| **Report** | a4 | 12-25 | wants to know what happened | headline → where it came from → why → what to do |
| **Poster** | a3 | 12-20 | is scanning a wall or a screenshot | one dominant figure, then three named zones |
| **One-pager** | a4, 1 page | 5-9 | has 60 seconds before a meeting | claim, evidence, ask |
| **Deck page** | slide | 3-6 | is being presented to | one idea, one visual, one sentence |

Set the page in `meta.page`. The type scale, margins and default block heights
all follow from it, a poster is not an A4 document printed larger.

**A lesson is not an explainer with simpler words.** The row above it in this
table opens on a claim and works outward; a lesson opens on what the thing is
and works up. That is a different order, not a different register, and it is set
in `meta.mode`, which the build enforces. The lesson spine lives in
[teaching.md](teaching.md#the-lesson-spine); everything below this line is the
argument spine.

## The spine that works for almost every argument

1. **Claim.** `hero`. One sentence the reader should believe by the end. Work it
   out before anything else; the document has no spine without it. It is then
   written down in the **subtitle**, plainly. The `title` above it stays a
   literal description of the subject and scope, never the claim dressed up as a
   slogan. See [anti-patterns.md](anti-patterns.md#titles).
2. **Scale, and only when a number is itself the finding.** `hero_figure` for
   the one number the document is about; `stat` when a single current value is
   the whole message. **This is not a step, and it is listed second only because
   that is where it lands when it is earned.** A `kpi` row of four labelled
   integers is the cheapest block in the catalog to write: it looks like a
   summary, needs no argument, and gets added by reflex. If a chart further down
   explains any of those numbers properly, the tile is that fact with its
   denominator and its comparison removed, printed first. Cut it. Four numbers
   cannot each be the finding. `leading-numbers` measures this and warns, and it
   fired on two of the five shipped fixtures, which is how the habit spread.
3. **Mechanism.** `process`, `cycle`, `tree`, or one chart with its sentence.
   *How* the thing works. Reports often skip straight to 4.
4. **Evidence.** The charts. Each one supports one sentence you have already
   written.
5. **Tension.** `comparison`, `diverging`, `matrix`, `callout`. Where the obvious
   reading is wrong, or where the options genuinely conflict. **An argument with
   no tension reads as marketing.** In a lesson the same job is done by
   `misconception`, and the thing being contradicted is what the reader already
   wrongly believes rather than a rival position.
6. **Implication.** `checklist`, `callout`, or a closing `prose` block. What
   follows for the reader.
7. **Method.** `footnotes`. Sources, period, exclusions, what not to conclude.

**Most documents do not need all seven, and the list is not a checklist.** The
*order* is robust: mechanism before evidence, tension before implication. The
presence of each step is a judgement every time. A slot left empty because
nothing earned it is a better document, not an incomplete one, and step 2 is the
one that gets filled by reflex.

## Rhythm

- **Alternate register.** Chart, then what it means, then chart. Two charts
  adjacent with nothing between them makes the reader do the connecting, and
  they will connect them differently from how you intended.
- **Vary the family.** Six bar charts in a row is a data dump. If every block
  comes from one catalog family, the argument is probably one-note too.
- **Vary the span.** A page of 12-span blocks has no hierarchy. Give the block
  that carries the section its full width and pair the supporting ones at 6+6 or
  8+4.
- **One dominant element per spread.** Exactly one `hero_figure` per view, and
  one visual that is obviously the biggest. If everything is emphasised, nothing
  is.
- **Leave air.** A crowded page reads as noise regardless of how good the
  individual blocks are. If you cannot fit it, the answer is to cut a block, not
  to shrink them all.

## Section openers

Use `section` when the *argument* turns, not every time the subject changes.
Three or four sections in an A4 explainer; two or three on a poster. Give each
one a `lede` that states what the section will establish, the reader should be
able to read only the hero and the section ledes and still get the argument.

**In a lesson, a section title is the question that section answers**, in the
reader's words, and the `lede` is where the answer goes. "Why does one program
serve a hundred addresses?" with a lede reading "The answer is the only thing a
visitor actually types". A noun phrase with no verb ("Tenant resolution") is the
tell that the insider register has come back: nobody has ever asked a question
in that shape. → [teaching.md](teaching.md#the-register)

Number them only when the sequence is information the reader needs. Numbering
because it looks tidy is grammar you did not choose.

## Where the words go

Every chart needs a sentence somewhere near it saying what to conclude. That
sentence lives in one of three places, in order of preference:

1. **The block `subtitle`**: best for a specific reading: "The gap comes from
   step three being repeated, not from the rate."
2. **A `prose` block before it**: best when the reasoning takes more than a
   line.
3. **The block `note`**: for method, caveats and definitions, not for the point.

The `title` names what is plotted, literally and specifically. The `subtitle`
says what to notice, in one flat sentence. Do not make the title do both, and do
not compress the two into an aphorism that does neither.

## Length discipline

Cut a block when:

- it repeats a point another block already makes;
- you cannot write its one-sentence claim;
- it is there because the data existed, not because the argument needed it;
- removing it would not change what the reader concludes.

The last one is the real test. Most first drafts lose a third of their blocks to
it and get better.

## Closing

End on the implication, not on a chart. A document that stops at its last chart
leaves the reader holding evidence and no conclusion, and they will supply one
of their own.
