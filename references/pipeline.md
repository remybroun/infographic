# The pipeline, end to end

Ten steps. Steps 1-5 are judgement and cannot be automated; 6-10 are mechanical
and mostly are.

The ordering of steps 4 and 5 is load-bearing. Deciding which images the document
lives on has to happen **before** the catalog is opened, because once it is open
it frames every idea and the question silently changes from *what does this look
like?* to *which of the 51 shapes is closest?* → [scenes.md](scenes.md)

---

## 1 · Establish the source

Read what you were given. If it is a file, extract it:

```bash
python3 scripts/ig.py extract source.pdf -o out/ledger.json
```

If the request is a topic rather than a document ("explain how X works"), the
source is your own knowledge, write the claims down first anyway, because
step 2 needs something to point at. Say so in the handoff, and do not present
recalled figures as if they came from a document.

→ [extraction.md](extraction.md)

## 2 · Name the reader, then write the claim

**Who reads this, and what do they already know?** One line, written down, before
the claims. "A provider-operations lead who has never seen the codebase" produces
a different document from "the engineer who wrote the branch", and the difference
is not tone, it is which words are allowed to appear at all.

Then, in the same breath: **list the terms this document will use that the reader
does not already have.** Domain nouns, invented vocabulary, and anything shaped
like an identifier. That list has exactly two legal destinations, and picking one
is not optional:

- a `definitions` block, placed **before** the first section that uses the term;
- a rewrite of the label into words, with the identifier demoted to the table twin.

Skip this and the word budget will decide for you, in favour of jargon: under a
6-word label cap `skipped_bucket` costs one word and "the recipient switched that
group off" costs six. The cheapest label is almost always the one only you can
read. `undefined-vocabulary` catches the worst of it, but it counts identifiers,
and it cannot see a plain English word you have quietly redefined.

Now the claim: one sentence the reader should believe by the end. Not a topic, a
claim. This becomes the `hero.title`, and if you cannot write it, nothing
downstream will rescue the document.

Then write the three to six supporting claims. Each one becomes a block or a
section. **This list is the document.** Everything after it is execution.

→ [narrative.md](narrative.md)

## 3 · Choose the target

Explainer, report, poster, one-pager, deck page, or a continuous scrolling page.
That sets `meta.page`, which sets type scale, margins and block heights.

`a4` and friends are paginated and print. `scroll` is not paginated: it gives you
full-bleed sections and real vertical air, and its deliverable is the HTML.
Choose `scroll` when the document will be read on a screen and at least one
section earns going edge to edge. Choose paper when it will be printed, attached,
or read as a reference sheet.

→ [continuous.md](continuous.md) · [print-pdf.md](print-pdf.md)

## 4 · Name the scenes

**Before opening the catalog.** Which two or three images does this document live
or die by? Write them as pictures, not chart types: "a shockwave through shared
code", "a beam that thins as it goes deeper".

Those get authored as `figure` blocks, capped at three. Everything else is
supporting material and goes on rails in step 5. If nothing in the document has a
shape the catalog lacks, this step takes ten seconds and produces nothing, which
is a perfectly good outcome.

→ [scenes.md](scenes.md) · [drawing.md](drawing.md)

## 5 · Choose a form per remaining claim

For each claim: what must the reader *do*: compare, follow, locate, weigh? Run
the decision procedure, and check the disqualifiers before settling.

Ask, for each: is it even a chart? A stat tile, a callout or a definitions list
is often the honest answer, and concept documents usually need more non-chart
blocks than chart blocks.

→ [choosing-a-visual.md](choosing-a-visual.md) · [catalog/](catalog/README.md)

## 6 · Write the spec

```bash
python3 scripts/ig.py new out/spec.json
```

Blocks in reading order. For each: the `title` names what is shown, the
`subtitle` says what to notice, the `note` carries method and caveats. Put the
prose between the charts as you go, retrofitting it later never works, because
by then you have forgotten why each chart was there.

→ [spec-schema.md](spec-schema.md)

## 7 · Pick the theme

`default` unless the work is branded. `rentos` for RentRemote / RentOS.
`mono` when it will be photocopied. A new brand theme is a data file, not code,
and it must pass the checks before it ships.

→ [color-and-type.md](color-and-type.md)

## 8 · Build and render

```bash
python3 scripts/ig.py render out/spec.json --out-dir out
```

This compiles, renders with headless Chrome, and lints. Read the warnings: they
name real problems (too many series, tiles that will not fit, a scatter past its
cap). A `scroll` document skips the PDF unless you ask for one, and shoots its
sections automatically.

→ [print-pdf.md](print-pdf.md) · [continuous.md](continuous.md)

## 9 · Look at it

```bash
python3 scripts/ig.py shoot out/doc.html
```

That renders the document to PNGs: pages for a paginated document, sections for
a continuous one. **Then open them and look.** The linter checks structure; it
has never once looked at the document, and it cannot tell you whether a label
collided, an arrow points at nothing, or the argument lands.

Be honest about what this catches: geometry. It cannot tell you the drawing was
the wrong drawing.

Check specifically:

- every chart's point stated in words nearby;
- no clipped or overlapping labels;
- no page more than half empty without a reason;
- the squint test still shows a clear primary element per page;
- it survives `--theme mono`.

→ [anti-patterns.md](anti-patterns.md) · [integrity.md](integrity.md)

## 10 · Iterate, then hand off

Fix, re-render, look again. Then say, in the handoff:

- what the claim is;
- which scenes you authored, and what you demoted to the catalog to stay inside
  the cap of three;
- which forms you chose and **what you rejected**, with the reason;
- what the source did not contain, and where you left a gap rather than filling
  it;
- any warning you decided to accept, and why.

That last section is what makes the output reviewable rather than something the
user has to re-derive from scratch.

---

## Quick reference

```bash
ig.py extract  <src>            source → ledger + candidate forms
ig.py new      <spec.json>      starter spec
ig.py build    <spec.json>      spec → HTML
ig.py render   <spec.json>      spec → HTML → PDF → lint
ig.py check    <doc.html>       lint a built document
ig.py shoot    <doc.html>       render it to PNGs so you can LOOK at it
ig.py catalog                   list every block type
ig.py catalog --sheet out.pdf   draw every block, in a theme
ig.py themes                    list themes
ig.py validate --all            run the colour checks
ig.py selftest                  assertion suite
```
