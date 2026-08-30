# The pipeline, end to end

Thirteen steps. Steps 1 to 6.5 are judgement and cannot be automated; 7 to 11
are mechanical and mostly are. The rules themselves live in `SKILL.md`; this file
is the procedure and the commands.

Read [anti-patterns.md](anti-patterns.md#before-you-write) now, not at step 10.
Its first half is the ways this pipeline gets run and still produces the wrong
document, and by review time none of them can be fixed.

**Everything judged between steps 2 and 6 goes in one file, `brief.json`, and
that file is checked before anything is built.** It used to be six steps of
judgement with no artifact between them, so every decision was made in a
reasoning buffer, re-made on the next pass, and reconstructed from memory at
handoff. The brief is what makes a decision survive the turn it was made in, and
it is what a per-section worker is briefed from.

Three orderings are load-bearing, and all three exist to stop something else
framing the work before you have decided what the work is:

- **Step 2.5 before step 3.** A spine is *a claim plus the argument that carries
  it*, which is the frame of a document for someone who already has the concept.
  Write it first and the document opens on its conclusion no matter how
  carefully everything downstream is done. → [teaching.md](teaching.md)
- **Step 6.5 before step 7.** The brief is checked before a line is drawn,
  because every fault in it is cheaper here than after the drawing, and a
  drawing that exists is a drawing that gets argued for.
- **Step 3 before step 4.** Three candidates before one is chosen, because the
  first spine to occur to you always wins otherwise.
- **Step 5 before step 6.** Which images the document lives on is decided
  **before** the catalog is opened, because once it is open the question
  silently changes from *what does this look like?* to *which of the 56 shapes
  is closest?* → [scenes.md](scenes.md)

One economy rule spans the whole pipeline: **build cheap, then look, then
spend.** Steps 1 to 9 are one improvised pass, made without re-reading
references already read and without polishing a page nobody has seen. The
effort belongs after step 10, where the shots are compared against the goal
the document must explain and the page is modified until it does.

---

## 1 · Establish the source

```bash
python3 scripts/ig.py extract source.pdf -o out/ledger.json
```

If the request is a topic rather than a document ("explain how X works"), the
source is your own knowledge; write the claims down first anyway, because step 2
needs something to point at. Say so in the handoff, and do not present recalled
figures as if they came from a document.

**If a version of this document already exists, it is not a source.** Keep the
previous spec closed until the scenes are named in step 5, and declare what it
replaces so the build can measure whether the argument actually moved:

```json
{"meta": {"supersedes": "spec_v1.json"}}
```

An edit is not a regeneration; call it an edit and skip the ceremony.

→ [extraction.md](extraction.md) ·
[anti-patterns.md](anti-patterns.md#before-you-write)

## 2 · Name the reader, then pick the mode

**Who reads this, and what do they already know?** One line, written down,
before anything else. "A provider-operations lead who has never seen the
codebase" produces a different document from "the engineer who wrote the
branch", and the difference is not tone, it is which words are allowed to appear
at all. When the request names no reader, the reader is the curious educated
stranger: intelligent, outside the team, owning none of your vocabulary.

**Then pick the mode, and say which.** `argument` if the reader has the concept
and wants a finding; `lesson` if they do not have it. It follows from the
reader, not the subject: the same facts about a billing system are a lesson for
the support team and an argument for the engineer who owns it.

Then, in the same breath, **list the terms the reader does not already have**
and give each one a destination: drawn at the rung that teaches it, or
`definitions` as the fallback. Skip this and the word budget decides for you, in
favour of jargon.

Only a **machine identifier** is demoted to the twin: a column, a function, a
config key. The name of a product, a system, a company or a release is not a
term to be worked around, it is the subject, and it stays on the page in full.
The list you are writing is of things to **introduce**, never of things to
remove. → [specificity.md](specificity.md)

**In `argument` mode, write the claim now**: one sentence the reader should
believe by the end. Not a topic, a claim. If you cannot write it, nothing
downstream will rescue the document.

**In `lesson` mode, do not write a claim.** Go to step 2.5. A learner does not
need to believe a sentence, they need to hold a model, and a claim written here
becomes a hero block stating the conclusion before the subject has a name.

## 2.5 · Open the brief

```bash
python3 scripts/ig.py brief out/brief.json --new
```

**This file is the document.** Everything decided between here and step 7 goes
in it and nowhere else. Steps 2 to 6 used to be five steps of judgement with no
artifact between them, and the cost was measured: in one session the same
analogy decision was reopened thirteen times, a close-up was designed six times
and shipped nowhere, and the block order the model reasoned its way to was not
the order it built. None of it survived the turn it was decided in.

Fill `meta` now, from step 2: the reader, the mode, and in `lesson` mode
`contradicts`, one line naming what the reader already believes that this page
has to take on. The sections get filled in over steps 3, 5 and 6, and step 6.5
checks the whole thing before anything is drawn.

**In `lesson` mode, write the questions and the order now.** One section per
question a reader has to get answered, in the order they have to be answered,
where nothing appears before the thing it depends on. `asks` is the question in
the reader's words and it becomes the section opener; `teaches` names the words
that section is allowed to introduce.

```json
{"id": "one-program", "asks": "How many programs are actually running?",
 "teaches": ["application"], "form": "figure"}
```

The ladder the build checks is derived from this, every build. There is no
second place to write it, which is the point: it used to live in its own file
beside a spec that carried its own copy, and on the last real run those two
disagreed without anything noticing.

→ [teaching.md](teaching.md)

## 3 · Write three spines, then choose one

A spine is a claim plus the argument that carries it: what leads, what the
document is *about*. Write **three**, one line each, and for each name the two
or three images it would live on. If all three produce the same pictures, they
are one spine wearing three titles; try again. **Then choose one, and say which.**

**In `lesson` mode this step is different, and smaller.** A lesson has one true
order, which step 2.5 already found. Write instead **the one thing a newcomer
reliably gets wrong about this subject**, and only if you have genuinely heard
someone say it. That goes in `meta.contradicts`, and it is where a lesson gets
its tension: a document that never contradicts anything reads as marketing.

**It is a job, not a block.** Where it lands is your choice and the brief
records it: a drawing of the assumed thing beside the real one, a note under an
analogy, a callout. What it may not be is a two-column list of what people
assume against what is true. That shape turns any thought into a listicle, it
restates whatever picture sits next to it, and the block that used to exist for
it has been removed. Then skip to step 4.

Then write the three to six supporting claims under the chosen spine. Each
becomes a block or a section. **That list is the document.** Everything after it
is execution.

→ [narrative.md](narrative.md)

## 4 · Choose the target

Explainer, report, poster, one-pager, deck page, or a continuous scrolling page.
That sets `meta.page`, which sets type scale, margins and block heights. Choose
`scroll` when the document will be read on a screen and at least one section
earns going edge to edge; choose paper when it will be printed, attached, or
read as a reference sheet.

**The HTML file is the deliverable for every target.** A paginated target
still emits a PDF during `render`, because the linter measures pages with it,
but that file is a byproduct: hand it over, and spend time in
[print-pdf.md](print-pdf.md), only when the user asked for a PDF or for print.

→ [continuous.md](continuous.md) · [print-pdf.md](print-pdf.md)

## 4.5 · An improvised page, with a library at hand

The document is improvised for its subject; the catalog is the library it
borrows from, never the plan. Run the step 5 test on the page instead of one
block: finish "the 12-column grid carries this document **completely**, because
___". A report, a data poster, a findings summary, easily. An explainer that
lives on two or three images, not at the point where the third of them wants to
overlap the second, fill the sheet, or be the layout rather than sit in a cell.
Past that point, blocks are word art pasted into a page you write, where a
claim happens to have their shape, and custom HTML carries everything else.

→ [authored.md](authored.md)

## 5 · Name the scenes

**Before opening the catalog.** Which two or three images does this document
live or die by? Write them as pictures, not chart types: "a shockwave through
shared code", "a beam that thins as it goes deeper".

The step is done when **three images are written down and you have said, per
image, whether it is a scene or supporting material.** Not before. "Nothing here
needs a scene" is a legitimate answer, and it is reached *through* those three,
never instead of them. Whatever survives gets authored, capped at three in block
mode; everything else goes on rails in step 6.

**Every scene that survives names the block it beat**, read first with `python3
scripts/ig.py catalog <type>`. Writing the rejection down also catches the
failure in the other direction: a scene committed to a figure slot that was a
`swimlane` all along.

Each surviving scene becomes a section in the brief with `form: "figure"`, and
carries four things:

```json
{"form": "figure", "rank": 1, "view": "many-inputs-one-box",
 "shows": "a column of typed addresses, lines converging into one box",
 "instead_of": {"block": "sankey", "because": "there is no quantity flowing"}}
```

`rank` is what makes the cap of three a ranking instead of an arrival order: the
fourth-best image used to lose to whichever three were thought of first.

**`view` names the viewpoint, and no two figures may share one.** It is a build
error at the brief, before any drawing exists. This is the check the file was
added for: the document that produced it spent three figure slots on the same
object, face on, and nothing in the skill could see it because figures were only
ever compared after they were drawn, by which time they were sunk cost. Moving a
figure means changing where the reader stands: closer in, cut away, from the
side, or beside something they already own.

→ [scenes.md](scenes.md#write-the-rejection-down) · [drawing.md](drawing.md)

## 6 · Choose a form per remaining claim

For each claim: what must the reader *do*: **meet it for the first time**,
compare, follow, locate, weigh? Run the decision procedure, and check the
disqualifiers before settling.

The other four presume the reader already has the concept and is now operating
on it. When the answer is "meet it for the first time", the form is in the
teaching family, and the next question is *what do they already own that has
this shape?* → [catalog/teaching.md](catalog/teaching.md)

Ask, for each: is it even a chart? A stat tile, a callout or a definitions list
is often the honest answer, and concept documents usually need more non-chart
blocks than chart blocks.

Each answer becomes that section's `form` in the brief, and a `shows` saying
what is on screen. Nothing here is copy: `shows` is a note to whoever draws the
block, and a block that reprints it is a page reading out its own outline.

→ [choosing-a-visual.md](choosing-a-visual.md) · [catalog/](catalog/README.md)

## 6.5 · Check the brief, then hand it to a stranger

```bash
python3 scripts/ig.py brief out/brief.json           # legal? in order? two of the same picture?
python3 scripts/ig.py brief out/brief.json --read    # hand the skeleton to a stranger
```

Every fault found here is cheaper than the same fault found after the drawing,
which is the whole reason the file is written first. `--read` asks the
blind-reader question of the skeleton alone: it costs one turn, renders nothing,
and the answer arrives while the order is still free to change. `ig.py blind` at
step 10 asks the same question of a built page, where the verdict costs a
rebuild and therefore gets rationalised away.

## 7 · Build it one section at a time

```bash
python3 scripts/ig.py brief out/brief.json --order how-it-knows
python3 scripts/ig.py new out/spec.json
```

`--order` prints a self-contained work order for one section: the question, the
form, the block it beat, the viewpoint, the width, the word allowance, and **the
vocabulary that is legal at that point in the ladder** along with the terms that
are not yet. Send it to a subagent verbatim and nothing else. What comes back is
one block's JSON.

The word list is the half of the forward-reference check that runs before the
writing rather than after it. Caught late, its only remedy is to delete the
sentence that used the word, and that is a real edit that has really been made.

A worker sees one section and never the sequence, so left alone every one of
them draws the whole subject from the front. What stops that is not the worker's
judgement, it is that the brief already fixed the viewpoint and checked it for
collisions. **Workers may not change the claim, the form or the view, and may
not introduce a term.** Any of those is a change to the brief, and the brief
gets re-checked.

Then point the spec at the brief, and the ladder is derived every build:

```json
"meta": {"brief": "brief.json"}
```

**The spec is the file you edit.** When a figure's geometry is computed (arcs, a
scale, a repeated element), script *that figure* and paste the SVG in. Do not
generate the whole document from a program: every title fix then becomes a code
edit, and the JSON the linter reports line numbers against is a file nobody
reads.

Blocks in reading order. For each: the `title` names what is shown, the
`subtitle` says what to notice, the `note` carries method and caveats. Put the
prose between the charts as you go; retrofitting it later never works, because
by then you have forgotten why each chart was there.

**Draw every figure twice:** two compositions differing in something structural,
looked at side by side, one kept, one sentence on what the loser could not show.

```bash
python3 scripts/ig.py sketch out/comps.json          # both, at the real column width
python3 scripts/ig.py sketch out/spec.json --id beam # one block from a finished spec
```

`sketch` renders one block alone as a PNG at the width it will really land on,
in about two seconds. It also computes the viewbox-to-column scale, which is the
one figure defect with no other detector.

→ [spec-schema.md](spec-schema.md) · [scenes.md](scenes.md#draw-it-twice) ·
[drawing.md](drawing.md)

## 8 · Pick the theme

`iris` for anything of our own. `default` when it must look unbranded. `rentos`
for RentRemote / RentOS. `mono`
when it will be photocopied. A new brand theme is a data file, not code, and it
must pass the checks before it ships. → [color-and-type.md](color-and-type.md)

## 9 · Build and render

```bash
python3 scripts/ig.py render out/spec.json --out-dir out
```

Compiles, renders with headless Chrome, and lints. Read the warnings: they name
real problems (too many series, tiles that will not fit, a scatter past its
cap). A `scroll` document skips the PDF unless you ask for one, and shoots its
sections automatically. A paginated document emits one as the linter's
measuring stick; it becomes the deliverable only when the user asked for it.

→ [print-pdf.md](print-pdf.md) · [continuous.md](continuous.md)

## 10 · Look at it

```bash
python3 scripts/ig.py shoot out/doc.html
```

PNGs: pages for a paginated document, sections for a continuous one. **Then open
them and look, and form your verdict before re-reading the linter.** Its
findings are defect evidence, not a quality score; read first, they anchor what
you then see, and a clean lint proves nothing about whether the page explains.
Be honest about what looking catches: geometry. It cannot tell you the drawing
was the wrong drawing.

- every chart's point stated in words nearby;
- no clipped or overlapping labels;
- no page more than half empty without a reason;
- the squint test still shows a clear primary element per page;
- it survives `--theme mono`.

### Then give it to someone who has not seen it

```bash
python3 scripts/ig.py blind out/doc.html --claim "the sentence from step 2"
```

You are the one reader who cannot read this document: you know what every label
means and what the page was supposed to say, so you see the intended document
rather than the printed one. No amount of care fixes that.

`blind` renders the shots if they are missing and prints a brief to hand to a
subagent with no context: what is this about, what is it claiming, which words
could you not define, what did you look at first, what did you have to read,
which image would stay with you.
Send it **verbatim**, with no source, no spec, no claim, and no summary of any
of them.

What comes back is evidence, not a change request. A term they could not define
needed `definitions` or a rewrite. A first-look landing on the wrong picture is
a hierarchy problem. A summary describing the layout rather than the subject
means the spine never made it onto the page, and polish will not put it there.
A reader who would remember no image an hour later, or only "a nice diagram",
is telling you the spine landed on no picture.
If no subagent is available, say in the handoff that this check did not run.

→ [anti-patterns.md](anti-patterns.md#before-you-ship) · [integrity.md](integrity.md)

## 11 · Iterate, then hand off

Fix in this order, and bring the whole page up one level before perfecting any
corner of it: wrong or misleading encodings; comprehension blockers (an
undefined term, a forward reference, a first look that lands on the wrong
picture); hierarchy and layout; cosmetics. Re-render, look again. Then say, in
the handoff:

```bash
python3 scripts/ig.py brief out/brief.json --handoff
```

**Do not write the decisions from memory.** The mode, the reader, the claim, the
figures in rank order with the viewpoint and the block each one beat, and what
went on rails: all of it is already in the brief and `--handoff` prints it. It
used to be nine bullets asking the author to recall choices made six steps
earlier, and what that produced was a confident, checkable, false account of
work that had not been done.

Then add the four things no file holds:

- **what the blind reader said the document was about**, and every term they
  could not define, or a line saying the check did not run;
- what the stranger who read the skeleton at step 6.5 said;
- what the source did not contain, and where you left a gap rather than filling
  it;
- any warning you decided to accept, and why.

That last section is what makes the output reviewable rather than something the
user has to re-derive from scratch.

---

## Quick reference

```bash
ig.py extract  <src>            source → ledger + candidate forms
ig.py brief    <brief.json>     THE DESIGN: sections, forms, viewpoints, order
ig.py brief    <b> --new        write a starter brief
ig.py brief    <b> --read       hand the skeleton alone to a stranger
ig.py brief    <b> --order <id> a work order for ONE section, for one subagent
ig.py brief    <b> --handoff    the decisions, generated rather than remembered
ig.py brief    <b> --against <spec>   what got built, against what was promised
ig.py new      <spec.json>      starter spec
ig.py build    <spec.json>      spec → HTML
ig.py render   <spec.json>      spec → HTML → PDF → lint
ig.py check    <doc.html>       lint a built document
ig.py shoot    <doc.html>       render it to PNGs so you can LOOK at it
ig.py sketch   <blocks.json>    ONE block alone, at its real width, in 2 seconds
ig.py blind    <doc.html>       the brief for a reader who has not seen the source
ig.py measure  <spec.json>      per-block height and words, before rendering
ig.py catalog                   list every block type
ig.py catalog  <type>           one block: payload example, every key, its docs
ig.py catalog --sheet out.pdf   draw every block, in a theme
ig.py themes                    list themes
ig.py validate --all            run the colour checks
ig.py selftest                  assertion suite, only when the tooling looks wrong
```

Why each of these rules exists, and the document that produced it:
[../HISTORY.md](../HISTORY.md).
