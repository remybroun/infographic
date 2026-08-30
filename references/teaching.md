# Teaching: the ladder, and the mode that enforces it

**A reader who has to be told what a thing is cannot be shown why it matters
first.** Everything in this file follows from that.

This skill spent three versions being good at choosing a form for a fact and bad
at explaining anything, and the cause was structural rather than stylistic. The
pipeline's first artifact was a fact ledger. Its second was a claim, defined as
*one sentence the reader should believe by the end*. Both are the frame of an
argument. Neither is an explanation, and no step ever asked for one, so the
document opened on its conclusion and worked backwards, which is the inverted
pyramid, which is the shape of a document written for someone who already knows
what the subject is.

The measured version: an architecture explainer whose second block was a
comparison of two designs, whose fourth was a glossary, and whose section titles
were "Custom domains and TLS certificate issuance". Every block was correct.
Nobody outside the team could read a line of it.

---

## Two modes

```json
{"meta": {"mode": "lesson"}}
```

`argument` (the default) is everything this skill did before: a claim, evidence,
tension, an implication. It is right for a reader who has the concept and needs
a finding.

`lesson` is for a reader who does not have the concept. It changes four things,
and three of them are enforced:

| | `argument` | `lesson` |
|---|---|---|
| Opens on | the claim | what the thing **is** |
| Order | strongest first | nothing before what it depends on |
| a `brief.json` order | optional | **required**, and checked |
| Density | `graphic` | usually `lesson` |
| Tension from | a `callout`, a `matrix` where nothing wins | `meta.contradicts`, landed somewhere |

**Choose the mode at step 2, when you name the reader, and say which you chose.**
It follows from the reader, not from the subject: the same facts about a billing
system are a lesson for the support team and an argument for the engineer who
owns it. When the request says "explain X", it is a lesson.

`lesson` is not automatically better. Dragging a reader who works on the subject
daily through first principles is its own insult, and a report of last month's
numbers has no ladder to climb. Making pedagogy universal would break those
documents, which is exactly why this is a mode and not a new law.

## The ladder

**Write the explanation before choosing a single form.** Not the document: the
explanation. A sequence of rungs, in the order a reader has to climb them, where
nothing appears before the thing it depends on.

**It is not a file of its own, and it is not written by hand.** It is the order
of `brief.json`, which is the same file that holds the pictures, so a section
that moves takes its rung with it. It used to be authored separately, in its own
`ladder.json`, beside a spec that carried its own copy; on the last real run
those two disagreed, seven rungs against five, and nothing noticed because the
build only ever read the copy in the spec.

```json
"sections": [
  {"id": "one-program", "asks": "How many programs are actually running?",
   "teaches": ["application"], "form": "figure"},
  {"id": "address-picks", "asks": "How does it know whose site to show?",
   "teaches": ["web address"], "form": "progressive"}
]
```

- **`asks`** is the question that section answers, in the reader's words. In
  lesson mode it is also the section opener, so it is the one field here a
  reader ever sees.
- **`teaches`** names the vocabulary this section introduces. It is what makes
  the order checkable rather than declarative.
- **`id`** is the block the section lands on, which is what makes the ladder a
  claim about the page rather than a note about intentions.

Run it before anything is built:

```bash
python3 scripts/ig.py brief out/brief.json          # legal? in order?
python3 scripts/ig.py brief out/brief.json --read   # hand it to a stranger
```

Then point the spec at it, and `meta.ladder` is derived every build:

```json
"meta": {"brief": "brief.json"}
```

### Why it is a question and not a sentence

`asks` used to be `says`: one short declarative sentence per rung, capped at 24
words, on the reasoning that a skeleton written out in full is an essay with
pictures added afterwards. That reasoning was right and the cap was the wrong
instrument. What a short-declarative cap trains is a register, and the register
it trains is the clipped aphorism: "Start with the whole thing, before its
parts." "The answer is the difference between rolling and wedging." Having just
written six of those to plan the document, the author wrote eleven more into it,
and every lede on the page came out sounding like a fortune cookie.

A question does not have that failure mode. It cannot be pasted into a document
as its voice, because it is not a voice, it is a request. And it does the
skeleton's actual job better: a section is finished when its question is
answered, which is a test, where "does the page say the sentence" is not.

### What the build checks

| Check | Fires when |
|---|---|
| `forward-reference` | a term is used in a block **before** the rung that teaches it |
| `ladder-order` | the rungs land on the page in a different order than they are written |
| `ladder-unlanded` | a rung names no block (warning) |
| `ladder-unused` | a rung teaches a term the page never uses (warning) |

In `lesson` mode the first two stop the build. In `argument` mode a declared
ladder is a courtesy, so they are warnings.

`forward-reference` is the one that matters, and it is the only check in this
skill that can see the insider register. Every other check measures density,
form or geometry, and a document passes all of them while opening on a word the
reader will not meet for another four blocks. It is also the check most likely
to fire on your first build, and the correct reaction is almost never to delete
the rung: it is to move it earlier, or to say the thing in words the reader
already owns at the earlier block and keep the term for where it is taught.

### Hand the skeleton to a stranger, before you build

`ig.py blind` is the only honest test in this skill and it runs at step 10,
against a built document, where its verdict costs a rebuild and therefore gets
rationalised away. `ig.py brief --read` asks the same question of the skeleton
alone. It costs one turn, it renders nothing, and the answer arrives while the
order is still free to change.

Send the brief verbatim. What comes back is evidence:

- **"I lost it at 4"** → rung 4 is doing two jobs. Split it.
- **A term in their answer 3 you did not plan to teach** → a missing rung.
- **Anything in their answer 5** → a forward reference the build cannot see
  yet, because the term is still in your head rather than in `teaches`.
- **Two pictures that sound like one picture in their answer 6** → they are one
  picture. The `view` check catches the exact repeats; a stranger catches the
  ones that differ on paper and land the same way.

## The lesson spine

`narrative.md` holds the argument spine. This is the other one, and the
difference is not decoration: it inverts the first two beats.

1. **What it is.** `hero`, and the title names the subject in words the reader
   already owns. The `subtitle` is what it is *for*, not what you concluded
   about it. In a lesson, make it **a question the reader would actually ask**:
   they arrived without the vocabulary a statement assumes, and a question is
   the one opening that works before they have any.
2. **The whole, before the parts. Draw the subject itself, big, at the top.**
   See [the establishing shot](#the-establishing-shot) below. `analogy` comes
   after it, not instead of it: an analogy says what the thing is *like*, and a
   reader who has not yet seen the thing has nothing to hang the likeness on.
   This is principle 1 of the skill, and it is the beat that gets skipped.
3. **Why it exists.** What was true before this thing, and what was wrong with
   it. A subject with no motivation is a set of facts to memorise.
4. **The rungs.** One per section, in dependency order, each with its picture.
   `progressive` when the parts accumulate.
5. **What people get wrong.** This is where a lesson gets its tension, and
   without it the document reads as marketing. Name it in `meta.contradicts` and
   land it wherever it lands best: the assumed thing drawn beside the real one,
   a note under the analogy, a callout. **Not a two-column list of assumed
   against actual.** That shape turns any thought into a listicle and reliably
   restates whichever picture sits next to it; the block that used to exist for
   it was removed for that reason.
6. **What it means for you.** `checklist`, or a closing `callout`.

**Steps 1 to 3 are what an argument document skips**, every time, because the
source material never contains them: a design document, a spec or a codebase all
begin from the assumption that the subject exists and is worth having.

## The establishing shot

**Good practice, not a rule, and not only for lessons.** Any document whose
subject can be drawn may open this way, in either mode. A subject with no
picturable body (a policy, a ratio, an abstraction) is not given a forced one:
that document opens on the claim instead. Reach for it whenever the reader may
not be able to picture the subject.

> The reader does not know what they are about to open. Before anything is
> explained, show them **the thing**, drawn large enough that they recognise it
> without reading a word.

A lesson is opened by someone who cannot yet picture the subject. Give them a
title that says exactly what the document is about, a question worth answering
underneath it, and then one **big custom drawing of the subject itself**: not a
diagram of its mechanism, not a chart, not an icon standing in for its category.
The thing. Recognition first, mechanism afterwards. Every rung after this one is
landing on a picture the reader already has in their head, which is the whole
reason the beat exists.

Three properties, and the first is the one that gets lost:

- **Wide, not tall.** It should own most of the page's *width* and a modest
  band of its *height*. A sheet has one screenful of vertical room and the
  sections still have to fit under it. Spending 500px of height on the opener is
  how a one-page explainer becomes three pages.
- **Custom, and drawn to be looked at.** This is the one drawing on the page
  worth real effort: proportions, a strut, a wheel, a window. A subject drawn
  carelessly says the document was made carelessly, and it is the first thing
  seen. [`authored.md`](authored.md) is the mode for it, or a `figure`.
- **The subject, not a symbol of it.** A library pictogram names a category. It
  is the right size and the wrong picture, and reaching for one here is how this
  beat gets skipped while looking like it was done.

**It can carry the whole, too.** The strongest establishing shots do double
duty: the subject drawn plainly, with the two or three things it does labelled
directly on it. That is beat 2 finished in one picture, and it earns its height.
Keep the labels to nouns, and keep any term the ladder teaches later off it.

## The register

**Section titles in a lesson are the question the section answers**, in the
reader's words: "Why does one program serve a hundred addresses?" rather than
"Custom domains and TLS certificate issuance".

This is a deliberate exception to the journal-caption rule in
[anti-patterns.md](anti-patterns.md#titles), and it is narrow. The rule is
right and stays in force for **chart titles**: a chart of data names its
subject, its scope and its period, and "would this work as a caption in a
journal paper?" is exactly the correct test. Applied to a *section* opener in a
lesson, that same test selects for the voice of a specialist writing for peers,
which is the failure this mode exists to correct. A journal caption is written
by someone who has already been introduced.

The three tells of the wrong register in a lesson:

- **A noun phrase with no verb.** "Tenant resolution", "Certificate issuance".
  Nobody has ever asked a question in that shape.
- **A term in the title that the ladder teaches later.** The build catches this
  one.
- **A title that answers rather than asks.** "The address picks the site" is the
  finding; it belongs in the `lede`. The title is the question it answers.

## What this does not license

- **Not more words.** `lesson` density raises the page budget from 150 to 260,
  which is the smallest allowance that fits a four-section ladder's bridges and its
  longer labels. It is not a step towards `report`. Body prose is still refused.
- **Not simplifying to the point of being wrong.** The target is an intelligent
  adult who lacks *this domain*, not a child. "Explain it to a five-year-old" is
  a useful instinct about *register* and a terrible instruction about *content*:
  it produces condescension and false simplification, and both cost you the
  reader you actually have. Assume nothing about the subject, everything about
  the reader.
- **Not a licence to skip the pictures.** A ladder is not the document. Every
  rung still has to land on something drawn, and a rung whose block is a
  paragraph is a rung you have not finished. `undrawn-section` counts `bridge`
  as prose for exactly this reason.
- **Not linear reading.** Nobody reads an infographic top to bottom; they land
  on the biggest thing and wander. A ladder that exists only in block order does
  not exist. Enforce it visually: number the sections, and make rung 1 the
  largest thing on the page. → [narrative.md](narrative.md#rhythm)
