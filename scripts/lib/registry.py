"""The block registry: the single source of truth for what this skill can draw.

Each entry carries the renderer plus the metadata the decision docs and
`ig.py catalog` read, so the reference material and the code cannot drift apart.
`use_when` is deliberately written as the reader's job, not the data's shape, picking a form starts from what the reader must be able to do.

Three keys drive the text budget in `density.py`, and they are the reason a
document cannot quietly turn back into an essay:

- `text_roles` overrides which budget a payload key is charged against, so
  `prose.text` is `body` (refused at graphic density) while `callout.text` gets
  a real, small allowance.
- `text_exempt` skips the budget entirely. Exactly three blocks qualify:
  footnotes and tables, whose contents are citations and data rather than
  argument, and `raw`, which is already outside every other guarantee.
- `graphic` marks a block as carrying its idea in a picture. The linter's
  graphic-ratio check counts these against the rest, which is the measurement
  that would have caught the eight-page text document this budget was written
  in response to.
"""

from __future__ import annotations

from . import blocks_diagram as dia
from . import blocks_editorial as ed
from . import blocks_figure as fig
from . import blocks_part as part
from . import blocks_quantity as qty
from . import blocks_structure as st
from . import blocks_teaching as teach
from . import blocks_time as tm

FAMILIES = {
    "editorial": "Claim and framing, kept deliberately small",
    "quantity": "How much, and how items compare",
    "change": "Movement over time or between two states",
    "part": "Share, composition and proportion",
    "structure": "Sequence, hierarchy, overlap and trade-off",
    "diagram": "The forms that absorb what would otherwise be paragraphs",
    "teaching": "Meeting a subject for the first time",
}

REGISTRY = {
    # -- editorial ---------------------------------------------------------
    # `owns` lists the payload keys a renderer consumes itself. The compiler
    # must not also emit its figure chrome for those, or the text prints twice.
    "hero": {
        "fn": ed.hero, "family": "editorial", "span": 12,
        "owns": ["title", "subtitle", "note"],
        "text_roles": {"title": "hero_title"},
        "use_when": "the document opens and one claim must land before anything else",
        "instead_of": "a title slide that names a topic rather than stating a finding",
    },
    "section": {
        "fn": ed.section, "family": "editorial", "span": 12,
        "owns": ["title", "subtitle"],
        "use_when": "a new argument begins and the reader needs a fresh mental frame",
    },
    "heading": {"fn": ed.heading, "family": "editorial", "span": 12, "owns": ["title"],
                "text_roles": {"text": "title"},
                "use_when": "a sub-part needs a name but not a full section opener"},
    "prose": {"fn": ed.prose, "family": "editorial", "span": 12,
              "text_roles": {"text": "body", "body": "body"},
              "use_when": "REPORT DENSITY ONLY, reasoning that genuinely cannot be drawn",
              "instead_of": "nothing at graphic density; the picture carries the idea"},
    "bullets": {"fn": ed.bullets, "family": "editorial", "span": 6,
                "text_roles": {"items": "detail"},
                "use_when": "items are parallel, short, and a chip grid would over-format them",
                "instead_of": "prefer `chips`, a bullet list is a paragraph wearing a disc"},
    "quote": {"fn": ed.quote, "family": "editorial", "span": 12,
              "text_roles": {"text": "quote"},
              "use_when": "a human voice carries the point better than a restatement"},
    "callout": {"fn": ed.callout, "family": "editorial", "span": 12, "owns": ["title"],
                "text_roles": {"text": "callout"},
                "use_when": "one caveat, risk or key idea must not be skimmed past"},
    "stat": {"fn": ed.stat, "family": "editorial", "span": 4, "owns": ["note"],
             "graphic": True,
             "use_when": "a single current value is the whole message",
             "instead_of": "a one-bar bar chart"},
    "kpi": {"fn": ed.kpi, "family": "editorial", "span": 12, "graphic": True,
            "use_when": "numbers nothing else explains; never a slot to fill",
            "instead_of": "a row restating figures the charts below carry properly"},
    "hero_figure": {"fn": ed.hero_figure, "family": "editorial", "span": 4,
                    "owns": ["note", "label"], "graphic": True,
                    "use_when": "one number is the entire finding; exactly one per view"},
    "table": {"fn": ed.table, "family": "editorial", "span": 12, "text_exempt": True,
              "use_when": "more than about seven classes all carry meaning, or exact values matter",
              "instead_of": "more colors"},
    "checklist": {"fn": ed.checklist, "family": "editorial", "span": 12, "graphic": True,
                  "text_roles": {"do": "detail", "dont": "detail"},
                  "use_when": "the reader must act, and the failure modes are as useful as the advice"},
    "definitions": {"fn": ed.definitions, "family": "editorial", "span": 12, "graphic": True,
                    "use_when": "the concept depends on terms the reader may not share"},
    "comparison": {"fn": ed.comparison, "family": "editorial", "span": 12, "graphic": True,
                   "text_roles": {"points": "detail"},
                   "use_when": "two framings compete and you are arguing for one"},
    "image": {"fn": ed.image, "family": "editorial", "span": 6, "graphic": True,
              "use_when": "the subject is image-native: a place, a product, a screen, a person"},
    "footnotes": {"fn": ed.footnotes, "family": "editorial", "span": 12, "owns": ["title"],
                  "text_exempt": True,
                  "use_when": "always, when the document carries numbers"},
    "divider": {"fn": ed.divider, "family": "editorial", "span": 12, "use_when": "a beat is needed"},
    "spacer": {"fn": ed.spacer, "family": "editorial", "span": 12, "use_when": "a page needs air"},
    "raw": {"fn": ed.raw, "family": "editorial", "span": 12, "text_exempt": True,
            "use_when": "you need arbitrary HTML, a form, an embed, markup from elsewhere",
            "instead_of": "a drawing: use `figure`, which keeps theming, alt and the twin"},

    # -- quantity ----------------------------------------------------------
    "bar": {
        "fn": qty.bar, "family": "quantity", "span": 12,
        "use_when": "magnitudes are compared across named categories",
        "instead_of": "a column chart with rotated labels",
    },
    "column": {"fn": qty.column, "family": "quantity", "span": 12,
               "use_when": "the x axis is genuinely ordered, periods, stages, buckets"},
    "lollipop": {"fn": qty.lollipop, "family": "quantity", "span": 12,
                 "use_when": "many categories, and solid bars would flood the page with ink"},
    "diverging": {"fn": qty.diverging, "family": "quantity", "span": 12,
                  "use_when": "values sit above and below a meaningful baseline"},
    "likert": {"fn": qty.likert, "family": "quantity", "span": 12,
               "use_when": "responses run along an ordered scale from disagree to agree"},
    "scatter": {"fn": qty.scatter, "family": "quantity", "span": 8,
                "use_when": "the relationship between two measures is the finding"},
    "heatmap": {"fn": qty.heatmap, "family": "quantity", "span": 12,
                "use_when": "magnitude varies across a grid of two dimensions"},
    "matrix": {"fn": st.matrix, "family": "quantity", "span": 12,
               "use_when": "options are scored against criteria and no axis is numeric"},

    # -- change ------------------------------------------------------------
    "line": {"fn": tm.line, "family": "change", "span": 12,
             "use_when": "a value moves over time and the shape of the movement matters"},
    "area": {"fn": tm.area, "family": "change", "span": 12,
             "use_when": "a single total over time, or a composition that grows"},
    "dumbbell": {"fn": qty.dumbbell, "family": "change", "span": 12,
                 "use_when": "each item has a before and an after, and the gap is the story",
                 "instead_of": "two grouped bars per item"},
    "slope": {"fn": qty.slope, "family": "change", "span": 8,
              "use_when": "two time points, many items, and rank change matters"},
    "timeline": {"fn": tm.timeline, "family": "change", "span": 12,
                 "use_when": "events happen in sequence and the dates are load-bearing"},

    # -- part-to-whole -----------------------------------------------------
    "share_bar": {"fn": part.share_bar, "family": "part", "span": 12,
                  "use_when": "a whole splits into parts and the split is read once",
                  "instead_of": "a pie chart"},
    "unit": {"fn": part.unit, "family": "part", "span": 8,
             "use_when": "a ratio should stay literally countable, 3 in 10"},
    "pictogram": {"fn": part.pictogram, "family": "part", "span": 12,
                  "use_when": "a few quantities are counted in a unit the reader "
                              "should feel, one symbol standing for a fixed amount",
                  "instead_of": "a bar chart whose axis label is the only thing "
                                "saying what is being counted"},
    "donut": {"fn": part.donut, "family": "part", "span": 5,
              "use_when": "the brief demands a circle and there are at most six parts",
              "instead_of": "nothing, prefer share_bar unless asked"},
    "treemap": {"fn": part.treemap, "family": "part", "span": 12,
                "use_when": "many items, wildly different sizes, and relative area is enough"},
    "funnel": {"fn": part.funnel, "family": "part", "span": 12,
               "use_when": "a population drops off stage by stage"},
    "pyramid": {"fn": part.pyramid, "family": "part", "span": 8,
                "use_when": "levels rest on each other, needs, maturity, evidence"},
    "meter": {"fn": part.meter, "family": "part", "span": 6,
              "use_when": "one value is measured against a limit or target"},

    # -- structure ---------------------------------------------------------
    "process": {"fn": st.process, "family": "structure", "span": 12,
                "use_when": "steps happen in order and the order is the explanation"},
    "cycle": {"fn": st.cycle, "family": "structure", "span": 7,
              "use_when": "the last step feeds the first and the loop never ends"},
    "quadrant": {"fn": st.quadrant, "family": "structure", "span": 8,
                 "use_when": "two independent axes produce four named positions"},
    "venn": {"fn": st.venn, "family": "structure", "span": 6,
             "use_when": "two or three sets overlap and the overlap is the point"},
    "tree": {"fn": st.tree, "family": "structure", "span": 12,
             "use_when": "things contain or report to other things, at most three levels"},
    "sankey": {"fn": st.sankey, "family": "structure", "span": 12,
               "use_when": "a quantity splits and merges as it moves between stages"},
    "anatomy": {"fn": st.anatomy, "family": "structure", "span": 12,
                "use_when": "a real image needs numbered callouts to be understood"},

    # -- diagram -----------------------------------------------------------
    # Each of these exists because a document tried to explain something in
    # prose and should have drawn it. Reach here first when you catch yourself
    # writing a paragraph.
    #
    # `figure` leads the family on purpose. The catalog is a floor, not a
    # ceiling: when a claim has a shape the catalog does not, the answer is to
    # draw the shape, not to ship the nearest existing one. Capped at three per
    # document by build.py, which is what keeps that from becoming "hand-draw
    # everything".
    "figure": {"fn": fig.figure, "family": "diagram", "span": 12, "graphic": True,
               "use_when": "the idea has a shape no catalog block has, draw it",
               "instead_of": "the nearest catalog block, shipped because it was nearest"},
    "stack": {"fn": dia.stack, "family": "diagram", "span": 12,
              "use_when": "layers rest on each other and you need to show what sits in which",
              "instead_of": "a paragraph naming the components of each tier"},
    "chips": {"fn": dia.chips, "family": "diagram", "span": 12,
              "text_roles": {"items": "label"},
              "use_when": "several short facts, states or names must be scannable at a glance",
              "instead_of": "a bullet list, which is a paragraph wearing a disc"},
    "scorecard": {"fn": dia.scorecard, "family": "diagram", "span": 12,
                  "use_when": "options are scored against criteria and the totals are the punchline",
                  "instead_of": "a bar chart of totals plus a paragraph explaining the criteria"},
    "gauge": {"fn": dia.gauge, "family": "diagram", "span": 4,
              "use_when": "one score against a real ceiling, 66 of 75",
              "instead_of": "a stat tile, when the ceiling is part of the claim"},
    "swimlane": {"fn": dia.swimlane, "family": "diagram", "span": 12,
                 "use_when": "a sequence changes hands and the hand-off is the explanation",
                 "instead_of": "a process diagram whose steps each name a different owner"},

    # -- teaching ----------------------------------------------------------
    # Every family above draws a relation between things the reader already
    # accepts. These three draw the moment before that, which is why a catalog
    # of 53 correct forms could still only produce documents for insiders.
    "analogy": {"fn": teach.analogy, "family": "teaching", "span": 12,
                "text_roles": {"known": "label", "new": "label"},
                "use_when": "the reader owns nothing yet, and something they do own "
                            "has the same shape",
                "instead_of": "`comparison`, which argues one side is better; an "
                              "analogy claims both sides are the same shape"},
    "progressive": {"fn": teach.progressive, "family": "teaching", "span": 12,
                    "text_roles": {"parts": "label"},
                    "use_when": "the finished picture has too many parts to meet at "
                                "once, and each one exists because of the last",
                    "instead_of": "one complete diagram, which shows what a system "
                                  "contains and never how to think about it"},
    "misconception": {"fn": teach.misconception, "family": "teaching", "span": 12,
                      # The role of a payload string comes from the last named
                      # key on its path, so `items[0].assumed` is charged as
                      # `assumed`, not as `items`. Mapping the container key
                      # would leave both columns uncapped.
                      "text_roles": {"assumed": "detail", "actual": "detail",
                                     "assumed_title": "label",
                                     "actual_title": "label"},
                      "use_when": "newcomers reliably arrive with a wrong model and "
                                  "the document has to displace it",
                      "instead_of": "stating the correct version and hoping it "
                                    "overwrites what the reader already believes"},
    "bridge": {"fn": teach.bridge, "family": "teaching", "span": 12,
               # The one block in this family that is not a picture. It is here
               # rather than in editorial because it only means anything as part
               # of a ladder, and because listing it beside `prose` is how it
               # would get reached for as prose.
               "graphic": False,
               "text_roles": {"text": "bridge"},
               "use_when": "LESSON DENSITY ONLY, one sentence carrying the reader "
                           "from one rung of the ladder to the next",
               "instead_of": "cramming it into the next block's subtitle, which "
                             "then stops stating what the picture shows"},
}

# Charts and diagrams carry their idea in a picture by construction. The
# editorial family is the exception and opts in per entry above, because that is
# where the distinction between a graphic and a wall of text actually lives.
for _entry in REGISTRY.values():
    _entry.setdefault("graphic", _entry["family"] in
                      ("quantity", "change", "part", "structure", "diagram",
                       "teaching"))

ALIASES = {
    "barchart": "bar", "hbar": "bar", "columns": "column", "vbar": "column",
    "stat_tile": "stat", "kpis": "kpi", "stats": "kpi", "big_number": "hero_figure",
    "pie": "donut", "waffle": "unit", "isotype": "unit", "stacked100": "share_bar",
    "share": "share_bar", "steps": "process", "flow": "process", "loop": "cycle",
    "orgchart": "tree", "hierarchy": "tree", "twobytwo": "quadrant", "2x2": "quadrant",
    "text": "prose", "paragraph": "prose", "list": "chips", "note": "callout",
    "grid": "matrix", "compare": "comparison", "sources": "footnotes",
    "before_after": "dumbbell", "gantt": "timeline",
    "layers": "stack", "tiers": "stack", "architecture": "stack",
    "tags": "chips", "pills": "chips", "badges": "chips", "facts": "chips",
    "criteria": "scorecard", "evaluation": "scorecard", "tradeoff": "scorecard",
    "dial": "gauge", "score": "gauge", "lanes": "swimlane", "handoff": "swimlane",
    "pictograph": "pictogram", "picto": "pictogram", "symbol_chart": "pictogram",
    "draw": "figure", "scene": "figure", "drawing": "figure", "svg": "figure",
    "diagram": "figure", "illustration": "figure",
    "like": "analogy", "metaphor": "analogy", "is_like": "analogy",
    "buildup": "progressive", "build_up": "progressive", "stages": "progressive",
    "myth": "misconception", "myths": "misconception",
    "assumption": "misconception", "corrections": "misconception",
    "transition": "bridge", "so_far": "bridge",
}


def resolve(name: str):
    key = str(name or "").strip().lower().replace("-", "_")
    key = ALIASES.get(key, key)
    return key, REGISTRY.get(key)


def render_block(block: dict, ctx) -> str:
    key, entry = resolve(block.get("type"))
    if not entry:
        known = ", ".join(sorted(REGISTRY))
        raise SystemExit(f"[build] unknown block type {block.get('type')!r}.\nKnown types: {known}")
    return entry["fn"](block, ctx)


def default_span(block: dict) -> int:
    key, entry = resolve(block.get("type"))
    return int(entry.get("span", 12)) if entry else 12


def is_graphic(block: dict) -> bool:
    """True when the block carries its idea in a picture rather than in words."""
    _, entry = resolve(block.get("type"))
    return bool(entry) and bool(entry.get("graphic"))


def owns(block: dict, key: str) -> bool:
    """True when the renderer consumes this payload key itself, so the compiler
    must not also emit figure chrome for it."""
    _, entry = resolve(block.get("type"))
    return bool(entry) and key in entry.get("owns", ())


def by_family():
    grouped = {}
    for name, entry in REGISTRY.items():
        grouped.setdefault(entry["family"], []).append((name, entry))
    for family in grouped:
        grouped[family].sort()
    return grouped
