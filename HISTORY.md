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

## v3.4: the document that drew the same picture four times

A gear-bearing explainer, built end to end without a single design decision ever
being written to a file. It shipped three authored figure slots holding one
object seen from one angle, face on, four times over. Nothing in the skill could
see it, because figures were only ever compared *after* they were drawn, and by
then each one was work already done.

Reading the session back showed why. **Steps 2 to 6 of the pipeline were the
entire design of the document, and not one of them had an artifact.**
`pipeline.md` said "written down" eight times and never said where. So the reader,
the mode, the order, the scenes and the form of every claim lived in a reasoning
buffer: the analogy decision was reopened thirteen times and shipped as whichever
version happened to be in the buffer at the end, a mesh close-up was designed six
times and shipped nowhere, the block order the model reasoned its way to was not
the order it built, and step 11's handoff, which asked the author to *report*
every step 5 and step 6 decision, became reconstruction from memory. What that
produced was a confident, checkable, false account of work that had not been
done: "every figure was drawn twice" about figures that were drawn once.

The one artifact that did exist made the case on its own. `ladder.json` was
written at step 2.5 and then copied into the spec at step 7, and by the end the
file held seven rungs against the document's five. The single persisted design
artifact disagreed with the document, and nothing noticed, because the build only
ever read the copy in the spec.

**Produced:** `brief.json`, one file holding the whole design, written before
anything is built and checked by `ig.py brief`. One entry per section, carrying
the question it answers, the terms it teaches, the form it takes, the block that
form beat, and for a drawing the **viewpoint** it is drawn from.

- **No two figures may share a `view`.** An error, at the skeleton, before a line
  of SVG exists. This check alone catches the document above.
- **`rank` makes the cap of three a ranking** instead of an arrival order. The
  close-up that was designed six times lost to a duplicate because it was fourth
  in writing order, not because it was worse.
- **`ig.py brief --order <id>`** prints a self-contained work order for one
  section, including the vocabulary legal at that point in the ladder. That is
  the half of the forward-reference check that runs *before* the writing; caught
  late, its only remedy is to delete the sentence that used the word, and that is
  a real edit that was really made.
- **`--handoff` generates the decisions** that used to be nine bullets of recall,
  and the build refuses a page that does not deliver what the brief promised.
- **The ladder is derived, never authored.** `ladder.json` is gone and so is
  `ig.py ladder`; `meta.brief` points at the brief and the rungs come from it
  every build. One file cannot disagree with itself.

Two removals came out of the same review.

**`says` became `asks`.** A rung used to be one short declarative sentence capped
at 24 words, on the reasoning that a skeleton written out in full is an essay
with pictures added afterwards. The reasoning was right and the cap was the wrong
instrument: what a short-declarative cap trains is a register, and the register
is the clipped aphorism. Having written six of them to plan the document, the
author wrote eleven more into it, and every lede on the page came out sounding
like a fortune cookie. A question cannot be pasted into a document as its voice,
and it does the skeleton's job better, because a section is finished when its
question is answered. `brief-echo` now warns when a block reprints its own
`shows` or `because`: the brief is a note to yourself, not the page's voice.

**`misconception` was removed from the catalog.** It rendered as two columns,
what people assume against what is actually true, one ✕ and one ✓ per row. That
shape turns any thought into a listicle, and it reliably restates whatever
picture sits beside it. The transcript has the model judging the block redundant
with the adjacent figure three times and keeping it anyway, because `pipeline.md`
mandated it: *"They become the `misconception` block."* It was then filled with a
restatement of that figure with device names in the column heads, which was the
worst line on the page. A mandated block will always be filled. The job survives
as `meta.contradicts`, one line naming what the reader believes, landing wherever
it lands best; the block that guaranteed it landed badly does not.

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

## v3.5: the page about nothing

A branch of four commits was explained as a `lesson`. Every rule was obeyed and
the linter reported clean, and the page that came out named nothing at all:
Channex was "the company's own channel tool", Mews was "a system added on a
Wednesday", the eight categories were "the eight kinds a customer would
recognise" with none of the eight named, and the whole document carried not one
number. The only real nouns in the file sat in the glossary, after it had
ended.

Two instructions produced it, both working exactly as written. The reader was
defined as "ignorant of your vocabulary, your **service names** and your
database columns", so the service names went. And lesson mode said every term is
introduced by being drawn "or rewritten into words with the identifier demoted
to the table twin", so every remaining name went to the twin. Neither rule
distinguished a lookup key from the name of the thing the document is about.

The second half was the checkers writing the copy. `forward-reference` was a
build error, and it fired on the word *catalog* in a hero reading "Four fixes to
the RentRemote integrations catalog". The cheapest way past a build error is
always to reword the sentence that tripped it, so the hero became "the list of
outside software a customer can connect" and the title lost its subject. Four
`ladder-unused` warnings were then cleared by deleting the terms from the brief
rather than putting the words on the page. The document got vaguer and the build
got quieter in the same edit, and "linter clean" was reported as a result.

**Produced:** [specificity.md](references/specificity.md), the substitution test,
and a fourth cover-test ("read it back: name three facts"). The reader is now
ignorant of the vocabulary but not of the names, which are introduced rather
than removed. Only machine identifiers are demoted to the twin.

**Produced in code:** `forward-reference` is a warning, never a build error, and
titling blocks are exempt outright, because the check cannot tell a term of art
from the subject's own name and should not get to decide. `ladder-unused` now
says the fix is on the page. `brief.py` refuses an `asks` that names nothing:
the starter file shipped `"What is it?"`, and in lesson mode `asks` becomes the
section heading verbatim, which is how a document went out titled "What is the
thing being fixed?" three times over.

**Also removed:** two rules that spent a session before any content existed.
Every figure drawn twice with an epitaph for the loser, and three spines written
out in full. One alternative, named, is enough to stop the first angle winning
by default; the rest was ceremony, and ceremony is what the run had time for
instead of facts.

## v3.6: the page that measured clean and read like a machine

Every check in the skill measured shape. `density.py` counted words,
`check_document.py` counted blocks, twins, hues and ink, `ladder.py` checked the
order terms arrived in, and `anti-patterns.md` said so plainly without a way to
act on it: *all of them measure shape*. So a document could pass the whole
apparatus while every sentence in it was the generated cadence, and two shipped
fixtures did. `poster-a3` carried a block titled "Operator survey: the reply
burden" and `scroll-architecture` one titled "Patch surface: a site each against
one tenant-aware app". Both are the colon reveal, both were written after the
title rule was in force, and nothing in the repo could see them.

The cause is the same one that produced `undefined-vocabulary`: **the word cap
selects for these shapes.** With six words to spend and nothing specific to say,
antithesis, the colon reveal, the trailing `-ing` clause and importance puffery
are what fits. They are correctly sized strings, so the budget is satisfied by
the exact register the skill forbids.

**Produced:** `copy_register.py` and `ig.py copy`, the one check here that reads
sentences. It is deliberately not in the build. Every upstream check is closed
by deleting something, which is why `Rewriting the copy to clear a warning` is
an anti-pattern; this one is closed only by writing a better line, so it runs
last, against a finished document, after `shoot` and `blind`.

**Role-awareness is the whole design.** "Operator survey: the reply burden" is a
broken title and "Reversed ordinal ramp: the earliest deposit holds the dark
end" is a correctly written method note, and the two are the same string shape.
The first draft could not tell them apart and fired on four legitimate notes and
footnotes out of six fixtures. A check that cries wolf gets ignored, which is
worse than absent, so every finding is scoped to the fields where it is actually
a failure.

**Also produced:** the direct-verb move in the budget's rewrite list ("serves as
a centralized hub for" is "tracks"), which is the only rewrite that shortens and
sharpens at once; hedged sourcing as an integrity rule, because "studies show"
is a citation's shape with the citation removed; and synonym cycling named in
`teaching.md`, because `forward-reference` tracks a term and never the four
words a document renames it to afterwards.

## v3.7: the skeleton that was read as the plan

Nine versions of "improvise", and the documents kept arriving in one shape:
a comparison of the subject with something familiar, then the mechanism, then
the limits. The last one to ship was an options-strategy explainer that opened
on an insurance analogy for a reader who had asked what the strategy *was*. The
prose said the opposite in six places. `SKILL.md` said "the document is
improvised for its subject", "the catalog is the library it borrows from, never
the plan", and "custom HTML is not a fallback, it is the medium". None of it
moved anything, and the reason is that **the instruction was prose and the
default was a file**.

`brief.py`'s `STARTER` shipped three sections already written: `what-it-is`,
viewpoint `beside-something-the-reader-owns`; `how-it-works`; `what-it-is-not`.
It was written to illustrate the schema and it was read as the design, every
time, because a skeleton with slots gets filled and never replaced. Its first
section is a side-by-side comparison, so every document's first section was a
side-by-side comparison. `fixtures/briefs/architecture-explainer.json`, the one
worked example built from a brief, opened on an `analogy` too, and `SKILL.md`
advertised that as the thing to copy.

Three more defaults pointed the same way and nothing measured any of them:

- **The establishing shot was advice.** "A document whose subject can be drawn
  opens on a drawing of the subject" was written down and never checked, so the
  opener was whatever the catalog offered first for an unfamiliar subject, which
  is two columns comparing it with something else. That teaches the comparison
  and never the subject.
- **The figure cap had no floor.** `MAX_FIGURES = 3` and nothing underneath it.
  A catalog block costs one line and trips no check; a figure costs a viewpoint,
  an `alt`, an `encodes`, a colour whitelist and a rejection in writing. So the
  document that drew nothing was the risk-free document, and the flagship
  fixture proved it: **eight sections, one drawing.** v2 had already found this
  once and answered it with a warning, and a warning cleared by an eight-word
  sentence is not a cost.
- **The one table that "decides everything" had no drawing in it.**
  `graphic-first.md`'s sentence-kind lookup maps fifteen kinds of sentence onto
  catalog blocks and not one onto `figure`. A lookup answers in a second and a
  question about what a thing looks like takes a minute, so the lookup won every
  time, and a mind map, a route, a map of anything, or an object with a body had
  nowhere on it to land.

**Produced:** a starter with no sections in it at all. `ig.py brief --new`
writes `meta` and an empty `sections`, and prints the section shape plus eight
orders a document could take, none of them a default. Anything printed has to
be retyped, and retyping is where a decision happens.

**Also produced:** `meta.spine` and `meta.spine_rejected`, both required, which
turns "name a second spine before you commit to the first" from advice into the
file's own precondition; `brief-opens-on-a-block`, which refuses a first section
that is not drawn unless `meta.opens_on` says in writing that the subject has no
picturable body; `brief-nothing-drawn`, the floor the cap never had, cleared
only by naming in `meta.scenes` what the catalog carried completely; a cap that
scales with the document (three, or half its sections) because a flat three on a
twelve-section scroll reads as *draw three and paste nine*; and three rows at
the bottom of the sentence-kind table that resolve to `figure` and to nothing
else, because the catalog is 56 shapes and the world is not.

**Also produced:** the reference fixture redrawn. `architecture-explainer` now
opens on two drawings, one fanning in and one fanning out, and the `analogy`
that used to come first is gone. The teaching family did not lose a rule; it
lost the worked example that was being copied as an opening move.

**Found by the first run under these rules**, a Sonnet agent explaining what a
datacenter is. It opened on a drawn cutaway of the building and wrote a spine
nothing in the starter could have suggested, which is the change working. It
also hit two defects the skill had been carrying:

- **`sketch` dragged the whole document's brief onto one block.** `cmd_sketch`
  strips `ladder` and `mode` from its stub spec with a comment explaining that
  they are claims about a document and one block is not one; `brief` is the same
  kind of claim and was not on the list. With no spec path on a stub, it
  resolved against the working directory, so it either failed to find the brief
  or found it and re-derived the entire ladder onto the single block, printing a
  rung-by-rung wall of `which no block has`. The command advertised as "the
  block alone, in two seconds" was the command the run stopped using.
- **`stat` rounded a measured value to nothing.** `"value": 1.09` for a PUE
  reached the page as `1`, because the plain path defaulted to zero decimals.
  `fmt_compact` had already been fixed once for this exact class of failure (an
  author's 8,231 shown as "8.2K"). **Produced:** `svg.natural_decimals`, so a
  number prints at the precision it was written with, and rounding is something
  an author asks for rather than something that happens to them.

**And the third defect from the same run, reported by the reader rather than a
check: the page arrived chaptered `01` to `11`.** `editorial.md` has carried
"numbers only when the sequence is information the reader needs" since v1, and
the code sample printed directly beneath that sentence numbered its own section.
Five of the six fixtures numbered every section too. A model copies the example,
not the paragraph above it, which is the same failure as the starter brief and
the same fix: **the rule was prose and the default was a file.** Eleven numbered
headings with a rule over each is a textbook contents page standing in front of
a document whose whole claim is that it is drawn.

**Produced:** `numbered-throughout`, which fires when a document of four or more
sections numbers all of them; `number` gone from the doc example and from every
fixture, so what gets copied is the unnumbered form; and the rule rewritten to
say where the ordinals actually belong.

