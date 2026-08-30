# Specificity

**Names, numbers and dates are the content. Everything else on the page is
there to hold them up.**

This file exists because of a measured failure, and it is the one failure
nothing else in this skill can detect. A page that says nothing passes the word
budget, the graphic ratio, the ladder, the colour validator and the linter,
because every one of those measures the shape of a document and none of them
reads it.

---

## The document that produced this file

A branch of four commits was explained as a `lesson` for a reader outside the
team. The reader definition then said the reader is "ignorant of your
vocabulary, your service names and your database columns", and the mode rule
said to demote identifiers to the table twin. Both were obeyed exactly. The
page that came out had:

| On the page | What it was |
|---|---|
| "the company's own channel tool" | Channex |
| "a system added on a Wednesday" | Mews, live since #1197 |
| "the eight kinds a customer would recognise" | eight named categories, none of them named |
| "renamed" (twice, as a chip note) | `smart_locks` → `hardware`, `communication` → `productivity` |
| zero | every quantity: 10 systems, 16 rows, 140 tests, 88 readers of one column |

Three drawings, all `encodes: "concept"`, so no data was drawn either. The only
real nouns in the file were in the glossary, after the document had ended. The
linter reported clean.

**The instruction "write for someone outside the team" had been read as "say
nothing a stranger could look up".** That is the opposite of teaching. A
stranger cannot learn that Mews shipped on Wednesday from a page that will not
tell them Mews exists.

## The substitution test

Take any noun phrase on the page. Could it be swapped for the equivalent thing
at a different company, in a different year, and would the sentence still be
true?

- "a system added recently" → true of everything. **Cut it or name it.**
- "Mews, live since 13 August" → true of one thing. **Keep.**

Run it on the title first. A title that survives substitution is naming a genre,
not a subject.

## Names are cheaper than descriptions

This is worth stating because the caps make the opposite feel true. Under a
six-word `label`, an author reaches for the plainest phrasing and lands on the
vaguest:

```
"the company's own channel tool"   5 words, teaches nothing
"Channex (ours)"                   2 words, teaches the whole point
```

Specific is nearly always **shorter**. When it genuinely is not, the fact wins
and something else on the page is cut: a chip, a note, a whole block. Never the
name.

## What the reader actually lacks

Not the names. The **context around** the names. A reader who has never heard
of Mews needs one drawn sentence saying it is booking software a landlord
already pays for. After that they can hold "Mews" perfectly well, and every
later mention is free.

So the move for an unfamiliar term is always **introduce it**, at the rung that
teaches it, by drawing the thing. It is never to delete it and describe its
silhouette.

## What is legitimately demoted

Machine identifiers, and only those: `delist_deadline`, `PmsFieldSchema`,
`config/pms.php`. Those are lookup keys, they belong in the table twin or the
closing `definitions`, and a page whose labels are column names is the failure
`undefined-vocabulary` was written to catch.

The name of a product, a system, a company, a place, a release or a person is
**not an identifier**. It is what the document is about.

## Where the specifics go

On the drawing. A figure carrying `encodes: "concept"` three times in one
document is usually a document that had data and threw it away. Label the marks
with the real names, put the real counts in the `encodes` twin, date the
timeline with the real dates.

Numbers do the same work. Ten systems, four removals, 140 tests: each one is a
mark that can be drawn, and a drawing of quantities is the thing this skill is
for. A page with no figures on it is a page of boxes.

## Checking it

There is no checker for this and there is not going to be one. The reader ran
it themselves, and this is the version to run before handing anything over:

> **Read it back.** Name three facts from the page: a name, a number, a date.

If you cannot, the document is not finished, whatever the linter said.
→ [anti-patterns.md](anti-patterns.md) · [teaching.md](teaching.md)
