# Process, sequence & flow

Blocks that answer *what happens, in what order*. These are the blocks that make
a document explain a **concept** rather than report a number, and concept
documents usually need more of them than they need charts.

The three questions that separate these forms:

1. **Does it end?** Yes → `process`. No, the last step feeds the first → `cycle`.
2. **Are the dates load-bearing?** Yes → `timeline`. No → `process`.
3. **Does the quantity split or merge?** Yes → `sankey`. It only shrinks → `funnel`.

---

## `process`: a linear sequence

```json
{"type": "process", "orientation": "horizontal", "numbered": true,
 "steps": [{"title": "Start with a balance", "text": "Whatever you already hold."},
           {"title": "Apply the rate", "text": "Interest on the whole balance."},
           {"title": "Add it back", "text": "So next period it earns interest too."}]}
```

| Key | Default | Notes |
|---|---|---|
| `orientation` | auto | `vertical` when >4 steps or any step's text exceeds ~90 chars |
| `numbered` | `true` | numbered discs; turn off when order is obvious from content |
| `ordinal` | `true` | ramp the steps by position |

**The automatic orientation switch matters.** Horizontal cards look good with
three short steps and become unreadable with six long ones, the measure
collapses to about twenty characters per line. Vertical takes real prose per
step and survives a page break. Override only when you have checked the render.

**Use it when** the order *is* the explanation. **Not when** the steps are
merely a list of parallel things, that is `bullets`.

## `cycle`: a process with no end

```json
{"type": "cycle", "center_label": "The reply loop",
 "steps": [{"title": "Reply is slow"}, {"title": "Guest messages more operators"},
           {"title": "Operators see more enquiries"}, {"title": "Each gets less attention"}]}
```

Nodes on a ring with arc arrows between them, including the closing arrow from
the last step to the first.

**The closing arrow is the whole point.** If the last step does not actually feed
the first, this is a `process` drawn in a circle, which is worse than a
`process`. Warns below three steps, where a ring reads as a two-way arrow.

Step titles wrap to three lines inside the node, so keep them to three or four
words and put the detail in prose beside the block.

**A cycle is square: its height is its width, and it wants a full-width span.**
`size` is a ceiling, not a size, so a narrow column does not make the ring
shorter, it shrinks the nodes while the label text stays put. At a half column
on A4 that is a 326px-tall square holding 38px nodes with three-line labels in
them, which is both illegible and a third of the sheet. The build warns when the
column squeezes the ring below what it asked for. Below a full span, a `process`
carries the same sequence and reads at any width; you lose the closing arrow, so
say the loop closes in the title.

## `funnel`: drop-off through stages

See [part-to-whole.md](part-to-whole.md#funnel-stage-to-stage-drop-off). Listed
here because it is a sequence form too: use `process` when the *steps* are the
message, `funnel` when the *losses* are, and both when you need each.

## `timeline`: events located in time

See [change.md](change.md#timeline-events-in-sequence).

The distinction people get wrong: a timeline marks **moments**, not durations.
Bars of duration are a `bar` with a non-zero baseline, or a table. And a
`process` is a timeline whose dates do not matter, if you find yourself writing
"Step 1, Step 2, Step 3" in the date column, use `process`.

## `sankey`: a quantity moving between stages

```json
{"type": "sankey", "height": 260,
 "links": [{"source": "Searches", "target": "Viewed a listing", "value": 1000},
           {"source": "Searches", "target": "Left immediately", "value": 620},
           {"source": "Viewed a listing", "target": "Enquired", "value": 140}]}
```

Nodes are inferred from the links and placed in columns by depth; band heights
are proportional to the flow. Link colour follows the **source** node, so the
reader can trace where a quantity went.

**Only worth the ink when the splitting and merging is the message.** A quantity
that simply declines through stages is a `funnel`, which is far easier to read.
Sankeys also degrade fast past about three columns or a dozen links: the ribbons
start crossing and nothing is traceable. At that point, a table of source →
target → value tells the truth better.

Keep the values consistent: if the outflows from a node do not sum to its
inflows, the diagram implies a leak the data may not contain. Add an explicit
"Other" or "Lost" target rather than letting the arithmetic silently disagree.
