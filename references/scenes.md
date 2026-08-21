# Scenes: deciding what gets drawn before opening the catalog

**The catalog is a floor, not a ceiling.** When a claim has a shape the catalog
does not, draw the shape.

That line exists because of a specific, repeatable failure, and it is worth
describing precisely, because it does not feel like a failure while it is
happening.

> **The stronger form of this failure: a previous version of the document.**
> Everything below is about the catalog framing your ideas. A finished document
> frames them far harder, because it has already made every decision, and
> re-deriving in front of it reproduces it while feeling like fresh work. The
> measured case: a regeneration that named the reader, rewrote the claim and
> re-derived the scenes, and came out with a 93% identical block sequence and an
> identical set of graphic forms. Every step was performed. None of it was free
> to land anywhere new. See [pipeline.md](pipeline.md) step 1 for the rule, and
> declare `meta.supersedes` so the build measures it rather than trusting you.

## The failure

An architecture explainer went out. Every block in it was a legitimate choice.
The request path was a `process`. The layers were a `stack`. The event fan-out
was a `tree`. The recommendation scored 66 out of 75 and got a `gauge`. Nothing
in it was wrong, the linter was clean, and it was airless.

The cause was not a missing block type. Version 1 of this skill had 46 forms and
version 2 had 51, and adding five more changed nothing, because the failure is
not coverage. It is a **reflex**: instead of asking *what does this idea look
like?*, the question became *which of the 51 shapes is closest?* Once that
substitution happens, every answer is a defensible near-miss, and a document of
defensible near-misses is exactly what that PDF was.

Look at what it cost on that one document:

| The idea | What it actually looks like | What got shipped |
|---|---|---|
| One app wearing 500 faces | hostnames fanning into one door | nothing; there is no block for it |
| Blast radius under a breach | a shockwave through shared code | a two-column bullet list |
| 100 requests in, 2 reaching the core | a beam visibly narrowing | a `sankey`, which is generic plumbing |
| Tenant scope binding at the Host header | containment, drawn as nested boundaries | a `definitions` card |

Three of those four are **spatial**, and the catalog has no spatial forms. It
never will: a catalog of shapes is a catalog of shapes that have recurred, and
the image a specific document lives on is usually specific to that document.

## The fix: name the scenes first

Before you open [catalog/](catalog/README.md), before you pick a single block
type, answer one question:

> **Which two or three images does this document live or die by?**

Write them down as *pictures*, not as chart types. "A shockwave spreading through
shared code." "A beam that thins as it goes deeper." "Five hundred hostnames
converging on one door." If you find yourself writing "a comparison of isolation
models", you have already fallen back into the catalog and are naming a form
rather than an image.

Those are the **scenes**. They get authored, as [`figure`](catalog/diagram.md)
blocks. Everything else is supporting material, and supporting material belongs
on rails: it stays consistent, it re-themes, it gets its table twin free, and it
does not need reviewing pixel by pixel.

## The cap is three, and it is a build error

`build.py` refuses a document with more than three authored figures. That number
is not a token budget, it is the ranking exercise made mandatory.

Without a cap, "draw the shape the catalog lacks" becomes "hand-draw
everything", and then every output stops resembling its siblings, the colour
discipline erodes one figure at a time, and the consistency the catalog buys is
gone. With a cap, you have to decide what actually matters, which is the
decision that produces a good document anyway.

If all four of your figures feel load-bearing, the honest reading is usually that
this is two documents.

**A figure also spends the page's words.** Every label inside its `<text>` is
charged as `figure_text`, capped at 40, and an A4 page only has 150 in total. Two
authored figures can eat most of a sheet's allowance in labels alone, which then
gets paid for by deleting the sentence that explained the subject. Count that
cost when you rank them, not after the third redraw.

## How to tell a scene from a block

A claim wants an authored figure when **the geometry is the argument**. Some
signals, in rough order of reliability:

| Signal | Example |
|---|---|
| The idea is spatial and the space means something | containment, distance, spread, depth, convergence |
| Position, not length or angle, carries the meaning | "inside", "beyond", "between", "downstream of" |
| The shape changes along its length | a beam narrowing, a funnel that is not a funnel |
| It is one image, and you can describe it in a sentence | "a fan converging on a door" |
| Naming the closest block type makes you add a "well, sort of" | the tell |

A claim wants a catalog block when it is a **comparison of values**, a
**sequence**, a **hierarchy**, a **share**, a **set of states**, or a **score**.
Those recur across every document ever written, which is precisely why they are
in the catalog and why the catalog draws them better than you will by hand.

## Write the rejection down

The last row of that table is the most reliable signal and the easiest to skip,
because a scene named well *feels* obviously unbuildable. From a real run:

> Neither is a catalog shape. Both get authored.

That is an assertion wearing the clothes of a test. It committed two of the
three figure slots in one sentence, before the catalog was opened. One of the
two scenes was a sequence interrupted and picked up by a different worker, which
is most of what `swimlane` already does.

So run the test on paper. For each candidate scene, before it becomes a
`figure`:

1. **Name the nearest catalog block.** A specific type, never "nothing fits".
   Run `python3 scripts/ig.py catalog <type>` and read what it can actually do,
   which is reliably more than you remember.
2. **Finish the sentence:** "`<block>` carries this **completely**, because ___."
3. **If you cannot finish it, the scene gets drawn.**

**The burden is on the block, and it used to be the other way round.** The
earlier version of this test asked you to finish "`<block>` would carry this,
well, sort of, because ___", and let the block win whenever you could. That
sentence is finishable about almost anything: a `swimlane` sort-of carries any
sequence, a `stack` sort-of carries any layering, a `sankey` sort-of carries any
narrowing. So the test resolved to "use the catalog" every time it was run, and
the measured result is in this repository: **four of the five worked examples
shipped with no authored figure in them at all**, including the one the skill
names as its reference for teaching mode. The failure this page was written
about is under-drawing, and the test guarding it was scored for over-drawing.

"Completely" is the whole word. A near-miss is a miss: if the block leaves out a
position, a distance, a containment, or a shape that changes along its length,
it did not carry the scene and the scene gets authored. The cap of three still
holds, and it is what stops this becoming "hand-draw everything": you are
ranking scenes against each other, not against the catalog.

Keep those sentences either way. They are what lets a reviewer disagree with
you, and they are the whole difference between a ranking exercise and a
preference.

## When nothing needed drawing, say so

"Nothing here needs a scene" is a legitimate answer, and for a data report or a
findings summary it is usually the right one. It is legitimate when it was
reached *through* the three images rather than instead of them, and the
difference between those two is invisible in the finished document: both look
like a page with no figure on it.

So it gets declared. One sentence in `meta`, naming what the catalog carried:

```json
"meta": {
  "scenes": "This is findings from data: each block is a share, a distribution
             or a ranking, and the catalog carries every one of them completely."
}
```

The linter's `no-authored-figure` finding goes quiet when it is there. A
document of five or more blocks that authored nothing and declared nothing keeps
the warning, because that is the case that cannot be told apart from never
having asked. The declaration has a floor of eight words for the same reason the
rejection sentence does: `"scenes": "n/a"` is an assertion, and the whole point
is a test.

## Draw it twice

Deciding a claim needs an authored figure settles *that* it gets drawn. It does
not settle *how*, and the how is where the second reflex lives.

The first composition to arrive is nearly always the arrangement the facts came
in: left to right, in the order the source listed them, actors on the left,
outcome on the right, one box per noun. That arrangement is not a decision. It
is the source's own ordering, redrawn, and it is the drawn equivalent of picking
the nearest catalog block. The whole reason a scene is worth a figure slot is
that **the geometry is the argument**, and a geometry inherited from the
paragraph order is not carrying an argument, it is transcribing one.

So draw two, and make them differ in something structural. Not colour, not
spacing, not a rough version and a neat version of the same arrangement. One of
these:

| Axis | The two versions |
|---|---|
| What sits at the centre | the actor, or the thing being acted on |
| Reading direction | left to right, top down, or outward from one point |
| Containment vs adjacency | nested boundaries, or things side by side with an edge between them |
| Where the quantity lives | the shape *is* the amount, or the shape is labelled with it |
| What repeats | one element drawn fifty times, or one drawn once with a count |
| What is absent | the excluded thing drawn outside the boundary, or not drawn at all |

Then look at both, at the size they will really be printed:

```bash
python3 scripts/ig.py sketch out/comps.json
```

`sketch` takes a spec, a single block, or a list of blocks, and renders each one
alone at the width it will really land on. It costs about two seconds, which is
the entire reason this step is affordable: when looking at a drawing means a
full build, a full render and finding the right page, it happens once, and once
means the first composition wins by default. It also prints the viewbox-to-column
scale, so a drawing authored at the wrong size says so instead of quietly
rendering its 12px labels at 7px.

Keep the losing file and one sentence on what it could not show, exactly as with
the rejected block above. Same reason: it is what lets a reviewer disagree with
you, and it is the difference between a choice and a first draft.

**When both versions look equally good, that is information.** It usually means
the drawing is illustrating the claim rather than making it, and neither
composition is load-bearing because there is nothing structural to be right or
wrong about. Check it against the cover-the-picture test before spending the
slot.

## Two failure modes on the other side

Naming this step creates two new ways to be wrong. Both are worth watching for.

**Authoring something the catalog already draws well.** A hand-drawn bar chart is
strictly worse than `bar`: no axis maths, no label-fit logic, no table twin, no
ordinal ramp, and it will drift from every other chart in the document. If the
catalog has it, use the catalog.

**Mistaking a picture of the subject for a scene.** There is a library of
silhouettes in [drawing.md](drawing.md#pictograms-when-the-subject-has-a-shape),
and a chart that counts in little houses is still a chart. It spends no figure
slot, needs no rejection written down, and does not answer the question this
page is asking. "Which images does this document live or die by?" is about the
*argument*, and a house is a noun.

**Drawing that carries no information.** Decoration that costs a scene slot is a
worse outcome than the near-miss it replaced, because it also takes the space.
Apply the same test as everything else in this skill: cover the picture. If
nothing was lost, it was decoration.

The reliable tell is **the quantities sitting next to the drawing instead of on
it**: a figure of three paths with two empty boxes at either end, and a `stat`
row above it holding the three numbers those paths carry. Split that way,
neither block works. The drawing says only "things move from here to there",
which the subtitle already said, and the numbers have lost the thing they are
quantities *of*. Put them on the paths. A box with nothing in it is a box you
have not finished drawing, and if the figure has no room for the numbers, the
figure is the wrong size or the wrong drawing.

## Where this sits in the pipeline

It sits between the claims and the forms:

```
3 · write three spines, then choose one
4 · pick the target
5 · SCENES: which 2-3 images does this live on?      ← here
6 · pick a form for every remaining claim
7 · write the spec, and draw every figure twice      ← and here
```

The ordering is the point. Run step 6 first and the catalog frames every idea
before you have decided what the ideas are, which is the reflex this whole
document exists to interrupt.

→ [drawing.md](drawing.md) for the kit · [catalog/diagram.md](catalog/diagram.md)
for the `figure` payload · [graphic-first.md](graphic-first.md) for the budget
that applies to all of it
