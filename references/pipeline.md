# The pipeline, end to end

Twelve steps. Steps 1 to 6 are judgement and cannot be automated; 7 to 11 are
mechanical and mostly are. The rules themselves live in `SKILL.md`; this file is
the procedure and the commands.

Read [anti-patterns.md](anti-patterns.md#before-you-write) now, not at step 10.
Its first half is the ways this pipeline gets run and still produces the wrong
document, and by review time none of them can be fixed.

Three orderings are load-bearing, and all three exist to stop something else
framing the work before you have decided what the work is:

- **Step 2.5 before step 3.** A spine is *a claim plus the argument that carries
  it*, which is the frame of a document for someone who already has the concept.
  Write it first and the document opens on its conclusion no matter how
  carefully everything downstream is done. → [teaching.md](teaching.md)
- **Step 3 before step 4.** Three candidates before one is chosen, because the
  first spine to occur to you always wins otherwise.
- **Step 5 before step 6.** Which images the document lives on is decided
  **before** the catalog is opened, because once it is open the question
  silently changes from *what does this look like?* to *which of the 57 shapes
  is closest?* → [scenes.md](scenes.md)

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
at all.

**Then pick the mode, and say which.** `argument` if the reader has the concept
and wants a finding; `lesson` if they do not have it. It follows from the
reader, not the subject: the same facts about a billing system are a lesson for
the support team and an argument for the engineer who owns it.

Then, in the same breath, **list the terms the reader does not already have**
and give each one a destination: drawn at the rung that teaches it, rewritten
into words with the identifier demoted to the twin, or `definitions` as the
fallback. Skip this and the word budget decides for you, in favour of jargon.

**In `argument` mode, write the claim now**: one sentence the reader should
believe by the end. Not a topic, a claim. If you cannot write it, nothing
downstream will rescue the document.

**In `lesson` mode, do not write a claim.** Go to step 2.5. A learner does not
need to believe a sentence, they need to hold a model, and a claim written here
becomes a hero block stating the conclusion before the subject has a name.

## 2.5 · Write the ladder (`lesson` mode: required)

**Write the explanation before choosing a single form.** Rungs, one line each,
in the order a reader has to climb them, where nothing appears before the thing
it depends on. Each rung is capped at 24 words: a ladder is a skeleton, not a
draft. If a rung will not fit in a line, it is two rungs.

```json
"meta": {"mode": "lesson", "ladder": [
  {"says": "One program can run many separate company websites.",
   "introduces": ["application"], "at": "one-program"},
  {"says": "The web address is what tells it which company you want.",
   "introduces": ["web address"], "at": "address-picks"}
]}
```

```bash
python3 scripts/ig.py ladder out/ladder.json            # legal? in order?
python3 scripts/ig.py ladder out/ladder.json --brief    # hand it to a stranger
```

A bare JSON list of rungs is legal input, because the spec does not exist yet.
**Hand it to a stranger now**, before anything is built: `--brief` asks the
blind-reader question of the ladder alone, costs one turn, and arrives while the
order is still free to change.

→ [teaching.md](teaching.md)

## 3 · Write three spines, then choose one

A spine is a claim plus the argument that carries it: what leads, what the
document is *about*. Write **three**, one line each, and for each name the two
or three images it would live on. If all three produce the same pictures, they
are one spine wearing three titles; try again. **Then choose one, and say which.**

**In `lesson` mode this step is different, and smaller.** A lesson has one true
order, which step 2.5 already found. Write instead **three things a newcomer
reliably gets wrong about this subject**, and keep the ones you have genuinely
heard someone say. They become the `misconception` block, and they are where a
lesson gets its tension: a document that never contradicts anything reads as
marketing. Then skip to step 4.

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

→ [continuous.md](continuous.md) · [print-pdf.md](print-pdf.md)

## 4.5 · Blocks, or author the page

Run the step 5 test on the page instead of one block: finish "the 12-column grid
carries this document **completely**, because ___". A report, a data poster, a
findings summary, easily. An explainer that lives on two or three images, not at
the point where the third of them wants to overlap the second, fill the sheet,
or be the layout rather than sit in a cell.

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

→ [choosing-a-visual.md](choosing-a-visual.md) · [catalog/](catalog/README.md)

## 7 · Write the spec

```bash
python3 scripts/ig.py new out/spec.json
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

`default` unless the work is branded. `rentos` for RentRemote / RentOS. `mono`
when it will be photocopied. A new brand theme is a data file, not code, and it
must pass the checks before it ships. → [color-and-type.md](color-and-type.md)

## 9 · Build and render

```bash
python3 scripts/ig.py render out/spec.json --out-dir out
```

Compiles, renders with headless Chrome, and lints. Read the warnings: they name
real problems (too many series, tiles that will not fit, a scatter past its
cap). A `scroll` document skips the PDF unless you ask for one, and shoots its
sections automatically.

→ [print-pdf.md](print-pdf.md) · [continuous.md](continuous.md)

## 10 · Look at it

```bash
python3 scripts/ig.py shoot out/doc.html
```

PNGs: pages for a paginated document, sections for a continuous one. **Then open
them and look.** Be honest about what this catches: geometry. It cannot tell you
the drawing was the wrong drawing.

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
could you not define, what did you look at first, what did you have to read.
Send it **verbatim**, with no source, no spec, no claim, and no summary of any
of them.

What comes back is evidence, not a change request. A term they could not define
needed `definitions` or a rewrite. A first-look landing on the wrong picture is
a hierarchy problem. A summary describing the layout rather than the subject
means the spine never made it onto the page, and polish will not put it there.
If no subagent is available, say in the handoff that this check did not run.

→ [anti-patterns.md](anti-patterns.md#before-you-ship) · [integrity.md](integrity.md)

## 11 · Iterate, then hand off

Fix, re-render, look again. Then say, in the handoff:

- **which mode you chose and why**, in one line, naming the reader it follows
  from. A lesson that should have been an argument is obvious to the person who
  asked and invisible to you;
- in `lesson` mode, **the ladder**, and what the stranger who read it said;
- the claim, and **which spine carries it**, with the two you did not build
  named in a clause each;
- which scenes you authored, and what you demoted to the catalog;
- for each figure, **the composition you kept and what the other could not
  show**;
- which forms you chose and **what you rejected**, with the reason;
- **what the blind reader said the document was about**, and every term they
  could not define, or a line saying the check did not run;
- what the source did not contain, and where you left a gap rather than filling
  it;
- any warning you decided to accept, and why.

That last section is what makes the output reviewable rather than something the
user has to re-derive from scratch.

---

## Quick reference

```bash
ig.py extract  <src>            source → ledger + candidate forms
ig.py ladder   <file>           the explanation ORDER, before anything is drawn
ig.py ladder   <file> --brief   hand the ladder alone to a stranger
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
