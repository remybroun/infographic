# Why the rules are the rules

Every constraint in `SKILL.md` was added to stop a specific document. This file
holds that record so the instructions do not have to carry it. Nothing here is
needed to produce a document; read it before changing a rule, not before using
one.

## v1: the essay with charts

The budget shipped as advice, and advice lost. The reference docs said "reduce
text", the linter warned when prose was *absent*, and the result was an
eight-page A4 document carrying **2,086 words and one bar chart** at the bottom
of page two. Every paragraph in it was individually defensible. That is the
failure mode: nothing said no.

**Produced:** `density.py`, the word budget in code, running before a pixel is
drawn. 150 words a page at graphic density. A block over its role's cap is a
build error naming the block, the role, the count and the cap, with no
truncation, because silently cutting a sentence changes what the document
claims.

**Also produced:** the linter's inverted checks. `check_document.py` used to
warn when prose was missing; it now measures the opposite.

## v2: the airless document

The word count was fixed and the document went dead. The catalog had quietly
become the boundary of imagination: one drawing per grid cell, capped at three,
no CSS of its own, and `raw` scored as prose for daring to be arbitrary. With
no way to compose a page, an agent stops treating the catalog as inspiration and
starts treating it as an instruction set. It emits valid input.

**Produced:** `figure`, the authored drawing inside block mode.

**Not enough.** The figure cap is a hard error, `alt`, `viewbox`, `encodes` and
the colour whitelist are hard errors, a figure's labels are charged against the
page budget, and it costs two compositions and a `sketch` run to author one. A
catalog block costs one line and risks nothing. So the document that authored
nothing was the risk-free document, and the skill reliably shipped it: **four of
its own five worked examples had no figure in them at all.** Absence had to cost
something or step 5 would never run.

**Produced:** the `no-authored-figure` warning, cleared by writing down what the
catalog carried instead. An assertion is not a test; a written rejection is.

## v3: the document nobody outside the team could read

Every step was convergent on a *claim*, which is the frame of an argument, so
the document opened on its conclusion and worked backwards. That is the inverted
pyramid, and it is the shape of a document written for someone who already knows
what the subject is.

The reference case: `architecture-explainer.json`'s previous version explained
the same system as an argument, opened on a score of 66/75 and a comparison of
two proposals, and **passed every check in the skill** while being unreadable by
anyone outside the team.

**Produced:** `meta.mode: "lesson"`, `meta.ladder`, the teaching family
(`analogy` `progressive` `misconception` `bridge`), and the `forward-reference`
build error. The ladder check is the only one in this skill that can see the
insider register: every other check measures density, form or geometry, and a
document passes all of them while opening on a word the reader will not meet for
four more blocks.

**The 24-word rung cap.** "Reflect completely on how to explain this before
drawing anything" is, word for word, the instruction that produced the v1 essay.
An explanation written out in full before the drawing starts *is* an essay, and
the pictures then get added to illustrate it.

**The 260-word `lesson` budget** is not a compromise between 150 and 900. It is
the smallest allowance that fits a four-rung ladder's bridges, its longer labels
and one definition, on a page that is still mostly picture.

## v3.1: authored composition

`figure` was the escape hatch and it is one drawing in one grid cell. Between it
and `raw` there was no way to compose a page: no layered arrangement, no
per-scene layout, no full-bleed art on paper, no drawing that spans two ideas.

**Produced:** authored mode. The spec carries `body` and `style`; the skill
stops being the compiler and keeps four things it is better at than the model,
the palette, the accessibility floor, inertness, and the tooling.

## v3.2: the page that opened on a shape nobody could name

Two failures on one lesson-mode explainer, and they were the same failure at
different scales.

`analogy` rendered as two columns of filled cells with a `≡` between them: a
table wearing a diagram's name. It made the reader *read* a mapping they should
have been able to see, it silently truncated any label too long for its 30px
row, and the two things being likened never appeared on the page at all, which
is a strange outcome for the one block whose whole job is to put something you
can already picture beside something you cannot. Its documented example filled
that hole with `"glyph": "building"`, so the recommended way to use the skill's
most important teaching block was to insert clip art, six files after
`drawing.md` says clip-art infographics are "a real genre with real conventions,
all of them bad".

Then the page opened on a mechanism. The reader had not seen an aeroplane before
being shown a cross-section of one.

**Produced:** `analogy` redrawn as two staged subjects with the parts numbered
across both, exploded-drawing style, so position carries the correspondence and
no arrow claims a direction the block does not have. A `scene` key, authored SVG
per side, held to a `figure`'s rules; `glyph` demoted from recommendation to
fallback in the code and in the docs. And [the establishing
shot](references/teaching.md#the-establishing-shot): a lesson opens on a title
saying exactly what the document is about, a question worth answering, and one
big custom drawing of the subject itself, wide rather than tall. Good practice
rather than a rule, because plenty of lessons do not need one and a rule would
force it on all of them.

## Rules whose reason is not obvious

- **Title caps were 10 and 9 words.** What fits in nine words is an aphorism, so
  aphorisms are what got produced: "Corroboration saturates", "The channel
  narrows, swells, then narrows again". The cap was selecting for the one
  register the skill forbids. Now 14 and 16.
- **The jargon trap.** Under a 6-word label cap, `skipped_bucket` costs one word
  and "the recipient switched that group off" costs six, so the identifier is
  always the cheapest accurate label and jargon wins by construction. `lesson`
  density's 8-word label cap is that conflict resolved in the author's favour;
  `undefined-vocabulary` catches the residue, but it counts identifiers and
  cannot see a plain English word you have quietly redefined.
- **"Name the block you rejected."** The earlier test asked whether a block
  would carry a scene "well, sort of", which is finishable about anything, so
  the catalog won every time. The burden now sits on the block.
- **Three spines.** From a branch that centralized partner email: the mechanism
  spine (one checkpoint, six gates, a registry), the recipient spine (what one
  partner receives and can stop), the exposure spine (37 kinds nobody could
  switch off). Only the first was ever built, twice, because nothing required
  the other two to be written down.
- **`sketch` exists because speed is the point.** A loop this cheap gets run
  five times; a loop that costs a full render gets run once.
- **Send the `blind` brief verbatim.** A brief retold in your own words leaks
  the answer into the question. Re-reading a document yourself is not a weaker
  version of the blind check, it is a different thing that always passes.
- **`ig-defs` is stripped before counting graphics**, or a document with no
  drawings passes `no-graphics` on the strength of an arrowhead marker.
- **A real `table` block counts against the word budget.** The twins live inside
  `<details>` and are already excluded, so a blanket exemption only ever covered
  authored tables, which is a hole the size of the whole budget: an author who
  cannot fit a paragraph retypes it as three columns.
- **`analogy` ships no table twin unless asked.** Its pairs are already
  selectable, reflowable text in the page, so the twin is a verbatim second
  copy, which is why `misconception` and `checklist` have never had one. It also
  costs height nothing can see: twins are collapsed on screen and forced open in
  print, so `ig.py measure` reports an authored one-pager as fitting and
  `ig.py render` then puts it on two sheets. **That trap is only closed for this
  block.** Any block still shipping a twin measures short by its printed height.
