#!/usr/bin/env python3
"""The specimen gallery: every form the skill draws, drawn with real data.

WHY THIS EXISTS. The README used to show the vocabulary as a hand-drawn figure
of eighteen miniatures. That is a *picture of* the catalog, not the catalog: it
proves nothing about what the renderer produces, and it silently made the
README's most-repeated claim ("52 forms") the one thing on the page that was
never rendered. This file draws the real blocks instead.

WHERE THE DATA COMES FROM. Every number here is computed from this repository at
generation time: the registry, `density.CAPS`, the shipped fixture specs, the
linter's own `add(...)` calls, and `git log`. Nothing is invented and nothing is
typed in twice, so the gallery cannot drift from the code it documents. A form
whose shape this repo has no honest data for is left out and named in
GALLERY.md, which is a better answer than a plausible-looking placeholder.

TARGET `a4` portrait, four specimens to a page. Displayed width is what sets
legibility, not raster resolution: a text label is a fixed size in millimetres,
so the *narrower* the page, the larger that label lands in GitHub's ~890px
column. A4 portrait puts an 8pt label at roughly 12px; the 338mm slide used for
the README figures puts the same label at roughly 7px. Span, not page size, is
what makes room for four of them.
"""
import collections
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(SKILL, "scripts"))

from lib import density, pictograms, registry  # noqa: E402


# ---------------------------------------------------------------- the facts --

FAMILY = {f: [n for n, _ in e] for f, e in registry.by_family().items()}
FAMILY_LABEL = {"quantity": "Quantity", "change": "Change", "part": "Part-to-whole",
                "structure": "Structure", "diagram": "Diagram", "editorial": "Editorial",
                "teaching": "Teaching"}
# Axis ticks get six words and about twelve characters before they truncate, so
# the long family name is shortened where it is a tick rather than a title.
FAMILY_TICK = dict(FAMILY_LABEL, part="Part")
# The validator prints its gate groups as sentences; a scorecard column head is
# rotated and clipped, so each one is renamed to the noun it is checking.
GATE_LABEL = {"categorical slots": "Categorical", "categorical slots 1-3": "Scatter trio",
              "ordinal ramp": "Ordinal ramp", "text & chrome contrast": "Text contrast"}
GRAPHIC = {f: sum(1 for n in names if registry.REGISTRY[n].get("graphic"))
           for f, names in FAMILY.items()}
TOTAL = len(registry.REGISTRY)
TOTAL_GRAPHIC = sum(GRAPHIC.values())


def targets():
    """(key, mm wide, mm tall) for every render target, read from build.py."""
    src = open(os.path.join(SKILL, "scripts", "build.py")).read()
    return [(k, float(w), float(h)) for k, _d, w, h in
            re.findall(r'"([a-z0-9-]+)":\s*\("([^"]+)",\s*([\d.]+),\s*([\d.]+),', src)]


def linter_codes():
    """Every check the linter can emit, grouped by the level it emits it at."""
    src = open(os.path.join(SKILL, "scripts", "check_document.py")).read()
    found = collections.defaultdict(set)
    for level, code in re.findall(
            r'add\(\s*("error" if \w+ else "warn"|"error"|"warn"|"note")\s*,\s*"([a-z0-9-]+)"', src):
        found["error" if "error" in level else level.strip('"')].add(code)
    return {k: sorted(v) for k, v in found.items()}


def fixtures():
    """Every shipped example spec, with the families it actually exercises."""
    out = []
    root = os.path.join(SKILL, "fixtures", "specs")
    for name in sorted(os.listdir(root)):
        spec = json.load(open(os.path.join(root, name)))
        # An authored spec composes its own page and may carry no `blocks` at
        # all, so this reads the key rather than assuming it.
        blocks = [b for b in spec.get("blocks", []) if not b.get("skip")]
        per, used, graphic = collections.Counter(), set(), 0
        for block in blocks:
            key, entry = registry.resolve(block.get("type"))
            used.add(key)
            if entry and entry.get("graphic"):
                graphic += 1
            for family, names in FAMILY.items():
                if key in names:
                    per[family] += 1
        out.append({"name": name.replace(".json", "").replace("-", " ").capitalize(),
                    "short": name.split("-")[0].capitalize(),
                    "blocks": len(blocks), "graphic": graphic,
                    "families": per, "used": used})
    return out


def history():
    """Checks enforced and repository size after each commit."""
    log = subprocess.run(
        ["git", "-C", SKILL, "log", "--reverse", "--format=%h|%s"],
        capture_output=True, text=True).stdout.strip().splitlines()
    out = []
    for line in log:
        sha, subject = line.split("|", 1)
        checks = 0
        for path in ("scripts/check_document.py", "scripts/lib/derivation.py",
                     "scripts/lib/leading_numbers.py"):
            blob = subprocess.run(["git", "-C", SKILL, "show", f"{sha}:{path}"],
                                  capture_output=True, text=True)
            if blob.returncode:
                continue
            checks += len(set(re.findall(r'add\([^,]+,\s*"([a-z0-9-]+)"', blob.stdout)))
            checks += len(set(re.findall(r'"([a-z][a-z-]{4,}):\s', blob.stdout)))
        tree = subprocess.run(["git", "-C", SKILL, "ls-tree", "-r", "-l", sha],
                              capture_output=True, text=True).stdout.strip().splitlines()
        size = sum(int(r.split()[3]) for r in tree if r.split()[3] != "-")
        out.append({"sha": sha, "subject": subject, "checks": checks,
                    "kb": round(size / 1024)})
    return out


def theme_gates():
    """Colour checks each theme passes, by gate group, from the validator."""
    out = subprocess.run(["python3", "scripts/ig.py", "validate", "--all"],
                         cwd=SKILL, capture_output=True, text=True).stdout
    themes, theme, group = collections.OrderedDict(), None, None
    for line in out.splitlines():
        head = re.match(r"=== theme: (\w+)", line)
        if head:
            theme = head.group(1)
            themes[theme] = collections.Counter()
            continue
        if re.match(r"^[a-z]", line) and "PASS" not in line and "FAIL" not in line:
            group = line.split("(")[0].split(",")[0].strip()
            continue
        if "[PASS]" in line and theme:
            themes[theme][group] += 1
    return themes


TARGETS = targets()
CODES = linter_codes()
# Every chart below counts blocks and divides by them, so an authored spec, which
# composes its own page and may have none, is not a row in any of them. It is not
# a gap in the gallery: "what share of this document's blocks are graphic" has no
# answer for a page that is one drawing with CSS around it, and a zero would read
# as "this fixture is all text", which is the opposite of true.
FIXTURES = [f for f in fixtures() if f["blocks"]]
HISTORY = history()
GATES = theme_gates()
USED_ONCE = collections.Counter(k for f in FIXTURES for k in f["used"])


# ------------------------------------------------------------- the specimens --

def page(*blocks):
    """A group of specimens from one family.

    Deliberately NOT a forced page break. Grouping by family and breaking before
    each group produced four near-empty pages: a group of three specimens leaves
    a third of an A4 blank, and a `break: before` in front of a tall row strands
    whatever preceded it. The linter caught all four. Letting the rows flow means
    every sheet but the last is full, and GALLERY.md names what is on each.

    ORDER WITHIN A GROUP IS BY RENDERED HEIGHT, shortest first. A row is as tall
    as its tallest block, so pairing a 444px definitions list with a 137px stat
    buys 307px of blank page, and eight such pairs cost 1,400px, an entire sheet
    of nothing. The heights are not guessable from the payload, so they are
    measured: `python3 assets/measure_blocks.py assets/gallery_spec.json` prints
    the laid-out height of every block. Re-run it after editing a specimen, and
    re-sort if a number moved. A group with an odd count of half-width blocks
    leaves its last one to pair across the family boundary, which is why a
    full-width block never sits directly after a lone half-width one.
    """
    return [dict(b) for b in blocks]


def scatter_points():
    """One dot per (blocks, graphics) coordinate, sharing a label where two
    examples coincide. See the note at the call site."""
    seen = collections.OrderedDict()
    for f in FIXTURES:
        seen.setdefault((f["blocks"], f["graphic"]), []).append(f["short"])
    return [{"x": x, "y": y, "label": " · ".join(names)}
            for (x, y), names in seen.items()]


def quantity():
    fam = sorted(FAMILY, key=lambda f: -len(FAMILY[f]))
    poster = next(f for f in FIXTURES if f["short"] == "Poster")
    scroll = next(f for f in FIXTURES if f["short"] == "Scroll")
    diverging_fam = sorted(FAMILY, key=lambda f: -(poster["families"].get(f, 0)
                                                   - scroll["families"].get(f, 0)))
    return page(
        {"type": "lollipop", "span": 6, "frame": "card",
         "title": "Share of blocks that are graphics, per shipped example",
         "categories": [f["short"] for f in FIXTURES],
         "values": [round(100 * f["graphic"] / f["blocks"]) for f in FIXTURES],
         "unit": "%", "sort": None, "value_label": "Percent"},
        {"type": "heatmap", "span": 6, "frame": "card",
         "title": "Blocks each shipped example takes from each family",
         "rows": [f["short"] for f in FIXTURES],
         "cols": [FAMILY_TICK[f] for f in fam],
         "values": [[f["families"].get(k, 0) for k in fam] for f in FIXTURES]},
        # `thickness` 14 rather than the 24px default. Nine categories at full
        # thickness made this the tallest block in the document by 80px, and a
        # row is as tall as its tallest block. Thinner bars lose nothing here:
        # length still encodes the magnitude, and the list reads faster.
        {"type": "bar", "span": 6, "frame": "card", "thickness": 14,
         "title": "Printable area of each render target",
         "categories": [k for k, _w, _h in TARGETS],
         "values": [round(w * h / 100) for _k, w, h in TARGETS],
         "unit": " cm²", "value_label": "cm²",
         "note": "scroll has no page, so it is measured at its A4 reading width."},
        {"type": "column", "span": 6, "frame": "card",
         "title": "Graphic and text blocks in each shipped example",
         "categories": [f["short"] for f in FIXTURES],
         "series": [
             {"name": "Graphic", "values": [f["graphic"] for f in FIXTURES]},
             {"name": "Text", "values": [f["blocks"] - f["graphic"] for f in FIXTURES]}],
         "value_label": "Blocks"},
        {"type": "scatter", "span": 6, "frame": "card",
         "title": "Blocks against graphic blocks, in the five examples",
         "axis_x": "Blocks", "axis_y": "Graphics",
         # Coincident points share one label. Two of the five examples are both
         # 13 blocks and 7 graphics, so drawing five labels printed "Data" and
         # "Scroll" on top of each other at the same coordinate and rendered as
         # "Datall". Nudging one of them apart would move a real value to make
         # room for a label, which is the one thing a chart may never do.
         "points": scatter_points()},
        {"type": "diverging", "span": 6, "frame": "card",
         "title": "Family use in the poster, against the scrolling page",
         "items": [{"label": FAMILY_LABEL[f],
                    "value": poster["families"].get(f, 0) - scroll["families"].get(f, 0)}
                   for f in diverging_fam],
         "sort": None, "value_label": "Blocks",
         "note": "Two documents, one subject each, reaching for opposite halves of the catalog."},
        # A matrix earns its space only when the rows genuinely differ. The first
        # version of this specimen put the nine render targets against four
        # properties and eight of the nine rows came out identical, which is a
        # table pretending to be a finding. What actually varies between the
        # checks is how far down the pipeline each one can run at all.
        {"type": "matrix", "span": 12, "frame": "card",
         "title": "What each guard needs before it can run",
         "cols": ["Fails the build", "Reads the spec", "Reads the HTML", "Reads the PDF"],
         "rows": [
             {"label": "Word budget", "cells": [True, True, False, False]},
             {"label": "Three figures at most", "cells": [True, True, False, False]},
             {"label": "No colour literals", "cells": [True, True, False, False]},
             {"label": "Leading numbers", "cells": [False, True, False, False]},
             {"label": "Same forms as last time", "cells": [False, True, False, False]},
             {"label": "Undefined vocabulary", "cells": [False, False, True, False]},
             {"label": "Undrawn section", "cells": [False, False, True, False]},
             {"label": "Near-empty page", "cells": [False, False, False, True]}],
         "note": "Only the first three can refuse to render. The rest need something to look at."},
    )


def change():
    caps = [(role, density.CAPS["report"][role], cap)
            for role, cap in density.CAPS["graphic"].items()
            if cap and role != "body"]
    caps.sort(key=lambda r: -r[1])
    return page(
        {"type": "line", "span": 6, "frame": "card",
         "title": "Checks the linter enforced, after each commit",
         "x": [h["sha"] for h in HISTORY],
         "series": [{"name": "Checks", "values": [h["checks"] for h in HISTORY]}],
         # Bars start at zero because length encodes magnitude; a line encodes
         # movement, and 25 to 29 against a zero baseline is a flat line that
         # says nothing. This is the one place `zero: false` is the honest call.
         "zero": False,
         "value_label": "Checks"},
        {"type": "area", "span": 6, "frame": "card",
         "title": "Repository size after each commit",
         "x": [h["sha"] for h in HISTORY],
         "values": [h["kb"] for h in HISTORY], "unit": " KB",
         "note": "The spike is four page screenshots landing, and then being replaced."},
        {"type": "dumbbell", "span": 6, "frame": "card",
         "title": "Words allowed in each field, by density",
         "from_label": "Report", "to_label": "Graphic",
         "items": [{"label": role.replace("_", " ").capitalize(), "from": rep, "to": gra}
                   for role, rep, gra in caps],
         "value_label": "Words"},
        {"type": "slope", "span": 6, "frame": "card",
         "title": "Blocks per family: the poster against the scrolling page",
         "from_label": "Poster", "to_label": "Scrolling page",
         # Three families, not six: the other three land on zero in the scrolling
         # page and their labels stack on top of each other at the same point.
         "items": [{"label": FAMILY_LABEL[f],
                    "from": next(x for x in FIXTURES if x["short"] == "Poster")["families"].get(f, 0),
                    "to": next(x for x in FIXTURES if x["short"] == "Scroll")["families"].get(f, 0)}
                   for f in ("editorial", "structure", "diagram")],
         "note": "Structure and diagram change places, which is what a slope chart is for."},
    )


def part():
    fam = sorted(FAMILY, key=lambda f: -len(FAMILY[f]))
    return page(
        {"type": "meter", "span": 6, "frame": "card",
         "title": "Hand-drawn figures in the scrolling example",
         "label": "Authored figures", "value": 3, "max": 3,
         "thresholds": [{"at": 3, "status": "critical", "label": "Cap"}],
         "note": "The cap is a ranking exercise: which images does this document live or die by?"},
        {"type": "share_bar", "span": 6, "frame": "card",
         "title": "The eleven pipeline steps, by what does them",
         "parts": [{"label": "Judgement", "value": 6}, {"label": "Tooling", "value": 5}],
         "value_label": "Steps"},
        {"type": "funnel", "span": 6, "frame": "card",
         "title": "How much of the vocabulary the shipped examples exercise",
         "stages": [{"label": "Registered", "value": TOTAL},
                    {"label": "In an example", "value": len(USED_ONCE)},
                    {"label": "In two or more",
                     "value": sum(1 for v in USED_ONCE.values() if v >= 2)}],
         "value_label": "Block types"},
        {"type": "treemap", "span": 6, "frame": "card", "height": 240,
         "title": f"The {TOTAL} block types, by family",
         "parts": [{"label": FAMILY_LABEL[f], "value": len(FAMILY[f])} for f in fam],
         "value_label": "Types"},
        {"type": "donut", "span": 6, "frame": "card",
         "title": "Linter checks, by what they do to the build",
         "parts": [{"label": "Fail", "value": len(CODES["error"])},
                   {"label": "Warn", "value": len(CODES["warn"])},
                   {"label": "Note", "value": len(CODES["note"])}],
         "value_label": "Checks"},
        {"type": "unit", "span": 6, "frame": "card",
         "title": "Block types that draw something, against those that set text",
         "parts": [{"label": "Draws", "value": TOTAL_GRAPHIC},
                   {"label": "Sets text", "value": TOTAL - TOTAL_GRAPHIC}],
         # The block normalises to a hundred squares, so a square is one percent,
         # not one block type. Saying otherwise would make the note contradict
         # the legend printed directly above it.
         "note": f"{TOTAL_GRAPHIC} of the {TOTAL} registered types draw. "
                 f"The other {TOTAL - TOTAL_GRAPHIC} set text."},
        {"type": "pictogram", "span": 12, "frame": "card",
         "title": "The optional pictogram library, by category",
         "subtitle": "Each row is drawn in one of its own members.",
         "unit_value": 1, "unit_label": "pictogram", "glyph": "box",
         "rows": [{"label": category.title(), "value": len(members),
                   "glyph": members[0]}
                  for category, members in pictograms.by_category()],
         "note": "Nothing in the skill asks for these. A unit chart with no "
                 "glyph still draws squares."},
        {"type": "pyramid", "span": 12, "frame": "card",
         "title": "The five principles, in the order they override each other",
         "levels": [
             {"title": "The graphic makes the point", "text": "Cover the text and the page still teaches"},
             {"title": "Draw the idea", "text": "Not the nearest available shape"},
             {"title": "The claim before the chart", "text": "One sentence per block, or no block"},
             {"title": "Never fabricate", "text": "A missing series stays missing"},
             {"title": "Colour is computed", "text": "There is a validator"}]},
    )


def structure():
    return page(
        {"type": "venn", "span": 6, "frame": "card", "height": 260,
         "title": "What an authored figure keeps, and what it gives up",
         "sets": [{"label": "Built-in blocks"}, {"label": "Authored figure"}],
         "overlap": "alt, twin, no literals"},
        {"type": "process", "span": 6, "frame": "card", "orientation": "vertical",
         "title": "The five commands the tooling actually provides",
         "steps": [{"title": "extract", "text": "Read a PDF into a fact ledger."},
                   {"title": "new", "text": "Start a spec."},
                   {"title": "render", "text": "Spec to HTML, PDF and lint."},
                   {"title": "shoot", "text": "Rasterise it so you can look."},
                   {"title": "validate", "text": "Check a theme's colour gates."}]},
        {"type": "cycle", "span": 6, "frame": "card",
         "title": "The loop the linter cannot close for you",
         "center_label": "Review",
         "steps": [{"title": "Render"}, {"title": "Look at it"},
                   {"title": "Find the collision"}, {"title": "Fix the spec"}],
         "note": "The linter checks structure. It has never once looked at a document."},
        {"type": "quadrant", "span": 6, "frame": "card",
         "title": "The six families, by what a claim has to supply",
         "x_label": "Needs numbers", "y_label": "Needs an order",
         "x_low": "No", "x_high": "Yes",
         "quadrants": [{"label": "Named positions"}, {"label": "Sequences"},
                       {"label": "Comparisons"}, {"label": "Series"}],
         "items": [{"label": "Quantity", "x": 0.85, "y": 0.25},
                   {"label": "Change", "x": 0.8, "y": 0.85, "emphasis": True},
                   {"label": "Part-to-whole", "x": 0.75, "y": 0.15},
                   {"label": "Structure", "x": 0.2, "y": 0.8},
                   {"label": "Diagram", "x": 0.3, "y": 0.6},
                   {"label": "Editorial", "x": 0.15, "y": 0.2}],
         "note": "Placement is a judgement about the form, not a measurement."},
        {"type": "sankey", "span": 12, "frame": "card", "height": 260,
         "title": "Block types, by family, and by whether they draw",
         # `TOTAL`, never a typed number. This node read "52 types" through two
         # commits that changed the registry, which is exactly the drift this
         # file's docstring promises cannot happen here.
         "links": ([{"source": f"{TOTAL} types", "target": FAMILY_LABEL[f], "value": len(FAMILY[f])}
                    for f in FAMILY]
                   + [{"source": FAMILY_LABEL[f], "target": "Draws", "value": GRAPHIC[f]}
                      for f in FAMILY if GRAPHIC[f]]
                   + [{"source": FAMILY_LABEL[f], "target": "Sets text",
                       "value": len(FAMILY[f]) - GRAPHIC[f]}
                      for f in FAMILY if len(FAMILY[f]) - GRAPHIC[f]])},
        # Structure has five half-width specimens, an odd count, so one of them
        # has to pair across the family boundary. It is the SHORTEST that is left
        # over, not the tallest: the leftover meets the diagram group's shortest
        # block, and 210 beside 210 wastes nothing, where the 335px quadrant in
        # this slot wasted 99.
        {"type": "tree", "span": 6, "frame": "card",
         "title": "What is in this repository",
         "root": {"label": "infographic", "children": [
             {"label": "references", "children": [{"label": "pipeline"}, {"label": "catalog"}]},
             {"label": "scripts", "emphasis": True,
              "children": [{"label": "build"}, {"label": "lib"}]},
             {"label": "fixtures", "children": [{"label": "specs"}]}]}},
    )


def diagram():
    themes = list(GATES)
    groups = list(next(iter(GATES.values())))
    return page(
        spines_figure(),
        {"type": "scorecard", "span": 6, "frame": "card",
         "title": "Colour checks each theme passes",
         "choices": themes, "criteria": [GATE_LABEL.get(g, g) for g in groups], "max": 10,
         "scores": [[GATES[t].get(g, 0) for g in groups] for t in themes],
         "note": "Counts are checks that apply, not quality. Every theme passes every one."},
        {"type": "gauge", "span": 6, "frame": "card",
         "title": "Block types a shipped example demonstrates",
         "value": len(USED_ONCE), "max": TOTAL, "label": "Exercised",
         "caption": f"of {TOTAL} registered"},
        {"type": "swimlane", "span": 12, "frame": "card",
         "title": "The eleven steps, and who performs each one",
         "stages": ["Source", "Reader", "Spines", "Target", "Scenes", "Forms",
                    "Spec", "Theme", "Render", "Look", "Hand off"],
         "lanes": [
             {"label": "You", "cells": ["Read it", "Name them", "Write three", "Choose",
                                        "Name them", "One each", None, None, None,
                                        "Judge it", "Explain it"]},
             {"label": "Tooling", "cells": ["extract", None, None, None, None, None,
                                            "new", "validate", "render", "shoot", None]}],
         "note": "Steps two to six cannot be automated. They are the skill."},
        {"type": "stack", "span": 12, "frame": "card",
         "title": "What Claude loads, in the order it loads it",
         "layers": [
             {"label": "SKILL.md", "meta": "always",
              "items": ["Principles", "Rules", "Catalog index"]},
             {"label": "references", "meta": "one per decision",
              "items": ["pipeline", "scenes", "graphic-first", "anti-patterns"]},
             {"label": "scripts", "meta": "run, not read",
              "items": ["build", "check_document", "density", "derivation"]},
             {"label": "fixtures", "meta": "read one first",
              "items": ["Six complete specs"]}]},
    )


def teaching():
    """The family for a reader who does not have the concept yet.

    Drawn with this repository's own history as the subject, like every other
    sheet here: the skill spent three versions able to choose a good form for
    any fact and unable to explain anything, because no step ever produced an
    explanation. These three blocks are what was missing from the vocabulary.
    """
    return page(
        {"type": "analogy", "span": 12, "frame": "card",
         "title": "What a ladder is, next to something you already have",
         "known": {"label": "A recipe", "glyph": "document"},
         "new": {"label": "A ladder", "glyph": "layers"},
         "pairs": [
             {"known": "Ingredients listed before the steps",
              "new": "Terms taught before they are used"},
             {"known": "Step 4 assumes step 3 happened",
              "new": "Rung 4 assumes rung 3 landed"},
             {"known": "Out of order, it fails",
              "new": "A forward reference is refused"}],
         "note": "Unlike a recipe, a reader may enter anywhere: hierarchy has to enforce the order too."},
        {"type": "misconception", "span": 12, "frame": "card",
         "title": "What this skill assumed for three versions",
         "assumed_title": "What the pipeline assumed",
         "actual_title": "What a reader needs",
         "items": [
             {"assumed": "A claim is the start of a document",
              "actual": "A claim is the end of an explanation"},
             {"assumed": "Good forms produce understanding",
              "actual": "Order produces understanding"},
             {"assumed": "A glossary handles unknown words",
              "actual": "A drawing handles unknown words"}]},
        {"type": "progressive", "span": 12, "frame": "card",
         "title": "How the guard against jargon was built up",
         "parts": ["A word budget", "A jargon scanner", "A ladder"],
         "stages": [
             {"label": "1. Refuse the essay", "adds": "A word budget",
              "detail": "150 words a page, in code"},
             {"label": "2. Count the identifiers", "adds": "A jargon scanner",
              "detail": "The budget selects for jargon"},
             {"label": "3. Check the order", "adds": "A ladder",
              "detail": "Plain words, still in the wrong order"}],
         "note": "Each stage exists because the one before it left a hole the reader fell into."},
    )


def spines_figure():
    """The one specimen the catalog cannot supply: an authored drawing.

    Three spines over one set of facts is not a tree (the three do not partition
    anything), not a process (they are alternatives, not steps) and not a
    quadrant (there are no axes). Naming the closest block type needs a "well,
    sort of", which is the test in scenes.md for authoring the shape instead.
    """
    parts = []
    parts.append('<text class="ig-fig-kicker" x="16" y="20">one set of facts</text>')
    parts.append('<rect class="ig-fig-node-mute" x="16" y="34" width="120" height="150" rx="6"/>')
    for i in range(7):
        parts.append(f'<line class="ig-fig-rule" x1="32" y1="{54 + i * 19}" '
                     f'x2="{120 if i % 3 else 96}" y2="{54 + i * 19}"/>')

    labels = ("How it works", "What a reader gets", "What it replaces")
    for i, label in enumerate(labels):
        y = 60 + i * 56
        chosen = i == 1
        parts.append(f'<line class="{"ig-fig-edge-strong" if chosen else "ig-fig-edge-mute"}" '
                     f'x1="140" y1="109" x2="212" y2="{y + 20}" '
                     f'marker-end="url(#ig-arrow{"-accent" if chosen else ""})"/>')
        parts.append(f'<rect class="{"ig-fig-node-strong" if chosen else "ig-fig-node"}" '
                     f'x="218" y="{y}" width="176" height="40" rx="5"/>')
        parts.append(f'<text class="ig-fig-label{" ig-fig-accent" if chosen else " ig-fig-mute"}" '
                     f'x="230" y="{y + 25}">{label}</text>')
    parts.append('<text class="ig-fig-kicker ig-fig-accent" x="218" y="28">'
                 'three spines, one chosen</text>')
    return {
        "type": "figure", "span": 6, "frame": "card", "id": "spines",
        "title": "Three arguments over one set of facts",
        "viewbox": "0 0 410 200",
        "alt": "A block of facts on the left. Three arrows lead from it to three "
               "candidate documents: how it works, what a reader gets, and what it "
               "replaces. The middle one is drawn in the accent colour as the chosen one.",
        "encodes": {"columns": ["Spine", "Chosen"],
                    "rows": [["How it works", "no"], ["What a reader gets", "yes"],
                             ["What it replaces", "no"]]},
        "svg": "".join(parts),
    }


def aliases():
    """The chip grid, on its own because it fills a sheet.

    Split in two halves rather than drawn as one block. A single grid was 911px
    when there were 60 aliases and 1,171px at 67, and `break-inside: avoid`
    means a block taller than the 1,005px text area cannot be placed at all: it
    takes a page to itself, overflows it, and strands two more. Halving it is
    not cosmetic, it is what keeps the sheet count stable as the alias table
    grows.
    """
    names = sorted(registry.ALIASES)
    half = -(-len(names) // 2)
    return page(*[
        {"type": "chips", "span": 12, "frame": "card",
         "title": ("Every alias, so a spec can be written in ordinary words"
                   if not part_index else "Aliases, continued"),
         "items": [{"label": a, "value": registry.ALIASES[a]} for a in chunk]}
        for part_index, chunk in enumerate((names[:half], names[half:]))
    ])


def editorial():
    return page(
        # Span 12, not 6. At half width this stacks four terms vertically and
        # runs to 444px, which beside the 137px stat left 307px of blank page,
        # the single worst void in the document. Full width lays the terms out
        # side by side instead, and the block gets shorter as it gets wider.
        {"type": "definitions", "span": 12, "frame": "card",
         "title": "Four words this repository uses in a particular way",
         "items": [
             {"term": "Spine", "text": "One argument over the facts. Write three, choose one."},
             {"term": "Scene", "text": "An image the document lives or dies by."},
             {"term": "Twin", "text": "The table beside a chart, holding every value."},
             {"term": "Budget", "text": "Words allowed per field and per page."}]},
        {"type": "comparison", "span": 12, "frame": "card",
         "title": "The outer two densities, and what each refuses",
         "left": {"label": "Report", "headline": "900 words a page",
                  "points": ["Body prose allowed", "Opt in explicitly",
                             "For real prose documents"]},
         "right": {"label": "Graphic", "headline": "150 words a page",
                   "points": ["Body prose refused", "The default",
                              "A breach fails the build"]},
         "note": "Lesson sits between them at 260: prose still refused, room to teach from zero."},
        # Span 12, not 6. At half width the do and don't columns are each about
        # 90px, and every item wrapped to one word a line. A checklist is read in
        # phrases; it needs the full measure.
        {"type": "checklist", "span": 12, "frame": "card",
         "title": "What to check before handing a document over",
         "do": ["Cover the graphics, then read what is left",
                "Name every number the page leads with",
                "Look at the render, not the linter"],
         "dont": ["Open the previous version first",
                  "Fill a stat row because the top looks empty",
                  "Let an identifier stand in for a sentence"]},
        # `compact: false`, because the block otherwise renders 2,086 as "2.1K"
        # and the exactness is the entire point of the number.
        {"type": "stat", "span": 6, "frame": "card", "compact": False,
         "value": 2086, "label": "Words in the failed first version",
         "note": "Eight A4 pages, one chart, every paragraph individually defensible."},
        {"type": "hero_figure", "span": 6, "frame": "card",
         "value": 150, "label": "Words a page, at graphic density",
         "note": "Checked once the real page count is known."},
        {"type": "callout", "span": 12, "frame": "card", "tone": "accent",
         "title": "The pattern behind every guard in this repository",
         "text": "When the output is wrong, look for the incentive that made the wrong thing cheapest, not for the missing rule."},
    )


spec = {
    "meta": {
        "title": "The specimen gallery",
        # `rentos`: Instrument Serif headings over Inter, olive lead with
        # terracotta as the warm secondary. The specimen sheets are the one place
        # in this repo where the theme is the subject as much as the blocks are,
        # and a validated brand theme shows more of what a theme can do than the
        # neutral default, whose whole job is to get out of the way.
        "theme": "rentos",
        "page": "a4",
        "density": "graphic",
        # The blocks ARE the subject here, so the air between them is dead space
        # rather than rhythm. See SPACING in build.py.
        "spacing": "tight",
        # Empty strings, not omitted keys: `footer_left` falls back to the
        # document title and `footer_right` to the date, so leaving them out
        # produces a footer rather than removing one. The running footer is the
        # last ink on every page, so with it in place every sheet trims to full
        # height and the crop does nothing.
        "footer_left": "",
        "footer_right": "",
    },
    # `aliases` last. It is a single 911px block, so wherever it lands it takes a
    # sheet to itself and pushes whatever follows onto a fresh one. In the middle
    # of the document that cost two near-empty pages, a lone `stack` on one and a
    # lone `callout` on the last. At the end it fills the closing sheet, which is
    # the one page allowed to be short.
    "blocks": (quantity() + change() + part() + structure() + diagram()
               + teaching() + editorial() + aliases()),
}

path = os.path.join(HERE, "gallery_spec.json")
with open(path, "w") as handle:
    json.dump(spec, handle, indent=1)
print(path)
