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

## Two failure modes on the other side

Naming this step creates two new ways to be wrong. Both are worth watching for.

**Authoring something the catalog already draws well.** A hand-drawn bar chart is
strictly worse than `bar`: no axis maths, no label-fit logic, no table twin, no
ordinal ramp, and it will drift from every other chart in the document. If the
catalog has it, use the catalog.

**Drawing that carries no information.** Decoration that costs a scene slot is a
worse outcome than the near-miss it replaced, because it also takes the space.
Apply the same test as everything else in this skill: cover the picture. If
nothing was lost, it was decoration.

## Where this sits in the pipeline

It sits between the claims and the forms:

```
2 · write the claim
3 · SCENES: which 2-3 images does this live on?      ← here
4 · pick a form for every remaining claim
5 · write the spec
```

The ordering is the point. Run step 4 first and the catalog frames every idea
before you have decided what the ideas are, which is the reflex this whole
document exists to interrupt.

→ [drawing.md](drawing.md) for the kit · [catalog/diagram.md](catalog/diagram.md)
for the `figure` payload · [graphic-first.md](graphic-first.md) for the budget
that applies to all of it
