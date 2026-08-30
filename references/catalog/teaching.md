# Teaching

**The family for the moment before the reader has the concept.**

Every other family in this catalog draws a relation between things the reader
already accepts: a quantity against a category, a stage after a stage, a part of
a whole. That is an enormous vocabulary for *operating* on a subject and it has
no shape at all for *meeting* one. A skill with 53 correct forms and none of
these produces documents that are formally faultless and read like minutes of a
meeting you were not at.

| You are about to write… | Draw |
|---|---|
| "it works a bit like a hotel: one building, many rooms" | `analogy` |
| "the whole thing has six parts, and here they all are" | `progressive` |
| "so far we have seen A; here is why B has to exist" | `bridge` |

These are the blocks a lesson is built from, and they are the ones to reach for
when `meta.mode` is `lesson`. They are legal in any document.
→ [teaching.md](../teaching.md) for the ladder they hang on.

---

## `analogy`

Something the reader already owns, beside the new thing, part for part.

```json
{
  "type": "analogy",
  "title": "What a shared application is",
  "known": {"label": "A hotel", "glyph": "building"},
  "new":   {"label": "One application, many sites", "glyph": "server"},
  "pairs": [
    {"known": "One building", "new": "One running program"},
    {"known": "Many rooms",   "new": "Many customer sites"},
    {"known": "The front desk sends you to yours",
     "new":   "The web address picks yours"}
  ]
}
```

| Key | Meaning |
|---|---|
| `known` | the familiar side: `label`, optional `glyph` from the pictogram library |
| `new` | the side being taught, same shape |
| `pairs` | the mapping, in order. Each row is one correspondence |

**Draw both sides with `scene`.** The block stages the two subjects and numbers
the parts across them, exploded-drawing style: same number, same order, same
height on both sides, so the correspondence is *seen* rather than read.

```json
"known": {
  "label": "A hotel",
  "scene": {
    "viewbox": "0 0 260 140",
    "alt": "One building, many numbered doors off a single corridor.",
    "svg": "<rect class=\"ig-fig-node-mute\" …/>"
  }
}
```

A `scene` is authored SVG held to a [`figure`](diagram.md)'s rules: `viewbox`,
`alt`, and no colour literal. Its `<text>` is charged against the word budget.

**Draw both sides in the same composition, with one object swapped.** Same
framing, same arrows, same positions, different subject. That is the whole claim
of the block made visible, and it lands before a single pair is read.

`glyph` names one of the 52 library silhouettes and is the **fallback, not the
recommendation**: a library symbol names a category, and an analogy is never
about a category. It shows none of the parts the pairs are about, and it is
wrong in a way the reader cannot detect. With neither key a side falls back to
its label set large, which is honest and plain.

**Use when the reader owns nothing yet** and something they do own has the same
shape. It is the most reliable teaching move there is, and the catalog's nearest
neighbour is its opposite: `comparison` exists to argue that the right-hand side
is *better*, and an analogy claims the two sides are the *same shape*. Reaching
for `comparison` here produces a document that appears to be arguing against
something the reader has never heard of.

**Every pair must be a real correspondence.** An analogy with no `pairs` is a
mood, and a mood is what makes analogies deservedly suspect: it invites the
reader to import everything else they know about hotels, including the parts
that are wrong. Naming the mapping row by row is what bounds it.

**Name the place it breaks.** The `note` is for that: "unlike a hotel, two
customers never see each other's rooms at all". An analogy the document never
limits is one the reader will over-extend, and the failure lands later, in
something they conclude on their own.

## `progressive`

One picture, drawn two to four times, gaining a part each time.

```json
{
  "type": "progressive",
  "title": "How the parts arrive, one at a time",
  "parts": ["A visitor", "The front door", "The application", "The database"],
  "stages": [
    {"label": "1. One site",     "adds": ["A visitor", "The application"],
     "detail": "One program, one address"},
    {"label": "2. Many sites",   "adds": "The front door",
     "detail": "Something has to pick"},
    {"label": "3. Shared store", "adds": "The database"}
  ]
}
```

| Key | Meaning |
|---|---|
| `parts` | the full vocabulary, in the order it will be built up |
| `stages` | 2 to 4. Each has a `label`, an optional `detail`, and `adds` |
| `adds` | one part name or a list of them. Must appear in `parts` |
| `ghost` | draw the not-yet parts as dashed outlines. Default true |

Parts added earlier stay, drawn plainly. The part added *in this stage* is the
only thing wearing the accent, which is what makes the row read as growth rather
than as four similar diagrams.

**Use when the finished picture has too many parts to meet at once**, and each
one exists because of the one before it. A complete architecture diagram tells a
reader what a system contains; it can never tell them how to think about it,
because every part arrives simultaneously and nothing says which were there
first or what problem the rest were added to solve.

**Each stage must answer "why is this here".** That is what `detail` is for. A
`progressive` whose stages add parts without saying what forced them is an
animation of a diagram, which is a diagram with extra steps.

## `bridge`

One sentence carrying the reader from one rung of the ladder to the next.

```json
{
  "type": "bridge",
  "text": "So far every visitor has arrived at the same place. Next: what happens when two companies want different front pages."
}
```

**`lesson` density only.** At graphic density the cap is zero and the build
refuses it, because a `bridge` there would be body prose with a different key.
→ [graphic-first.md](../graphic-first.md#the-three-densities)

| Constraint | Value |
|---|---|
| Word cap | 40 at `lesson` density, 0 at `graphic` |
| Per document | one per `section`, minimum 3 |
| Adjacency | two in a row is a build error |

Those limits are the whole design. A concession with no ceiling is the old
failure with a new key: six bridges and the document is prose again, with the
pictures illustrating it rather than carrying it. Two adjacent bridges are
always a paragraph that has been split in half to get under the word cap.

**Use it for the hand-off, not for the content.** A bridge says *why the next
picture is coming*; it never says what the next picture says. If cutting a
bridge would remove information from the document, that information belonged in
a block.

**Each bridge you cannot cut is a rung whose picture does not stand on its own.**
That is the useful reading of a build that fails the cap: not "I am allowed
three", but "three of my pictures need a sentence to work".
