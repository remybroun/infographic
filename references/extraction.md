# Extraction: source → fact ledger

Before anything is designed, the source has to become **evidence you can point
at**. That is what the ledger is: a record of what the document actually says,
with every number still attached to the sentence it came from.

```bash
python3 scripts/ig.py extract report.pdf -o out/ledger.json
```

Supported: `.txt .md .csv .tsv .json .html .pdf .docx`, or `-` for stdin. PDFs
need `pdftotext` (poppler); DOCX is read with the standard library.

---

## The two rules

**1. Every number keeps its sentence.** The ledger stores `context` for every
figure it finds. A number without its context is how an infographic ends up
asserting something the source never said, "revenue grew 40%" turns out to have
been "revenue grew 40% in the pilot region only".

**2. Nothing is invented.** The extractor never computes a total, a rate, or a
trend that the source did not state. If you derive a value later, mark it as
derived in the block's `note`. A figure the reader cannot trace back is a figure
they cannot check.

## What comes out

```json
{
  "source":   {"path": "...", "kind": "pdf", "words": 4210, "tables": 3},
  "sections": [{"heading": "Method", "level": 2, "text": "..."}],
  "tables":   [{"columns": [...], "rows": [[...]], "origin": "markdown"}],
  "numbers":  [{"raw": "$4.2M", "value": 4200000, "unit": "currency",
                "currency": "$", "context": "Revenue grew to $4.2M in 2024."}],
  "dates":    ["2023", "Q1 2024"],
  "candidates": [{"form": "line", "ref": "table[0]", "confidence": "high",
                  "why": "...", "watch": "...", "alternatives": [...]}],
  "text": "..."
}
```

## Candidates are evidence, not a decision

`candidates` is the extractor's first pass at what the content *could* support.
Each entry carries the evidence that suggested it and, often, a `watch` note
naming the way that form goes wrong.

**Never build straight from the candidate list.** It reads shapes, not meaning:
it cannot tell whether your five rows are ordered stages or unordered products,
whether the parts of your 100% are mutually exclusive, or whether the story is
one item rather than eight. Take the candidates to
[choosing-a-visual.md](choosing-a-visual.md) and decide there.

What it detects today:

| Signal | Suggests |
|---|---|
| one numeric column, named rows | `bar`, plus `lollipop` past 12 rows |
| a numeric column summing to ~100 | `share_bar`, `unit`, `donut` |
| values on both sides of zero | `diverging` |
| monotonically falling ordered rows | `funnel` (with a warning to check it is one population) |
| column headers that read as periods | `line`, plus `slope` at exactly two |
| a before/after header pair | `dumbbell` |
| many numeric columns × many rows | `heatmap`, or `table` |
| ≥3 sentences carrying a date | `timeline` |
| ordering language (first / then / step N) | `process` |
| ordering language + loop vocabulary | `cycle` |
| contrast language (versus / whereas / instead of) | `comparison`, `matrix` |
| containment language (consists of / reports to) | `tree` |
| percentages in prose | `unit`, `share_bar`, `stat` |
| headline figures in prose | `stat` |
| an existing pros/cons split | `checklist` |

## The ledger is facts. A lesson needs the other inventory.

**The extractor cannot find what the source never says**, and what a source
never says is the thing a newcomer most needs: what the subject *is*, and why
anyone built it. A design document, a spec, a codebase and a post-mortem all
open from the assumption that the subject exists, is worth having, and is
understood. That assumption is invisible in the text, so it survives extraction
intact and lands in the document unexamined.

So when `meta.mode` is `lesson`, read the source a second time for a different
list:

- **What does this source assume I already know?** Every one of those is a
  candidate rung, and the source will never mark them.
- **What did the world look like before this existed, and what was wrong with
  it?** That is the "why it exists" beat, and it is almost never written down
  anywhere, because the people who wrote the source lived through it.
- **Which term is used from the first line as though it were ordinary English?**
  Those are the most dangerous, more so than the obvious identifiers: an
  "audience" that is not the people who read something but a rule for computing
  an address. → [teaching.md](teaching.md)

That inventory is what step 2.5 turns into the ladder. Neither `candidates` nor
`numbers` can contribute a single entry to it.

## Reading a source the extractor cannot help with

Plenty of sources are pure narrative and produce almost no candidates. That is
information, not a failure: it usually means the document explains a **concept**,
and concepts are carried by `process`, `cycle`, `tree`, `venn`, `quadrant`,
`comparison`, `definitions` and prose, none of which the extractor can infer
from arithmetic.

When the candidate list is thin, read the source yourself and ask:

- What does the reader have to **believe** by the end? That is the hero claim.
- What has to be **true first** for that to make sense? Those are the definitions
  and the setup.
- Where does the source **argue** rather than report? Those are the comparison
  and callout blocks.
- What does the source **admit**, limits, caveats, unknowns? Those belong in
  callouts and footnotes, not buried.
- What is the source **silent** about that a reader will ask? Say so explicitly
  rather than letting the design imply completeness.

## Gaps and how to handle them

You will routinely find the source states a conclusion without the series behind
it: "bookings grew steadily since 2021" with no yearly numbers.

- **Do not invent the series to draw the line.** A fabricated shape is worse than
  no chart, because it looks like evidence.
- Use what the source actually gives you, here, a `stat` or a `callout` quoting
  the claim.
- Note the gap in your handoff so the user can supply the data if they have it.

Same for totals that do not add up, percentages of unstated bases, and medians
presented as if they were means. Record the discrepancy in the block's `note`
rather than smoothing it over: see [integrity.md](integrity.md).

## Working the ledger by hand

The ledger is plain JSON and is meant to be read. A practical loop:

1. `ig.py extract source.pdf -o out/ledger.json`
2. Read the summary it prints. Skim `sections` for the document's own structure.
3. Open `tables` and decide, per table, what claim it supports, many support
   none and should be left out.
4. Grep `numbers` for the figures that would make good `stat` tiles, and read
   their `context` before using any of them.
5. Write the spec against [spec-schema.md](spec-schema.md), citing sources in
   `note` / `source` / `footnotes` as you go, while you still remember where
   each figure came from.
