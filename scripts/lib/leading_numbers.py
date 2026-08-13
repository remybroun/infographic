"""Does a number the document leads with actually carry anything?

A `kpi` row is the easiest block in the catalog to write and the easiest to
write badly. Four labelled integers above the fold look like a summary, cost
almost no effort, and require no argument, so they get added by reflex, and
`narrative.md` used to make it worse by listing "Scale" as slot 2 of a spine
that "works for almost everything". A slot in a template gets filled.

The failure is specific and measurable: **every number in the row is explained
properly somewhere further down**, in a chart that gives it a denominator, a
comparison or a shape. The row is then not a summary, it is the same facts
stripped of the context that made them mean anything, printed first. Removing it
changes nothing the reader concludes, which is this skill's own test for cutting
a block.

So the check is: how many of the leading numbers does the document restate?
Not "are there stat tiles" (a genuine headline figure is the right block), and
not "how many" (one is as bad as four when it is the wrong one).

**`kpi` only, deliberately.** A `hero_figure` or a `stat` is a *claim*: one
number that is the finding. A chart below it that gives that number a shape is
evidence for the claim, which is the correct relationship and not a restatement.
A `kpi` row is a *summary*, and the tell is arithmetic: four numbers cannot each
be the finding. Running this over `hero_figure` flagged the poster fixture,
where the hero states 3.1% and the funnel underneath proves it, which is exactly
right and must not warn.
"""
from __future__ import annotations

LEADING = ("kpi",)


def _numbers(node, out):
    """Every number anywhere in a payload, as floats."""
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        out.add(float(node))
    elif isinstance(node, dict):
        for value in node.values():
            _numbers(value, out)
    elif isinstance(node, list):
        for value in node:
            _numbers(value, out)
    elif isinstance(node, str):
        for token in node.replace(",", " ").split():
            stripped = token.strip("%().;:")
            try:
                out.add(float(stripped))
            except ValueError:
                pass


def leading(block: dict) -> list:
    """(label, value) for each figure a leading block puts on the page."""
    found = []
    if block.get("type") == "hero_figure":
        if block.get("value") is not None:
            found.append((block.get("label") or "", block["value"]))
        return found
    for item in block.get("items", []) or []:
        if isinstance(item, dict) and item.get("value") is not None:
            found.append((item.get("label") or "", item["value"]))
    if block.get("type") == "stat" and block.get("value") is not None:
        found.append((block.get("label") or "", block["value"]))
    return found


def check(spec: dict, registry) -> list:
    """Warnings about leading numbers the document explains better elsewhere."""
    blocks = [b for b in spec.get("blocks", [])
              if isinstance(b, dict) and not b.get("skip")]
    warnings = []

    for index, block in enumerate(blocks):
        key, _ = registry.resolve(block.get("type"))
        if key not in LEADING:
            continue
        figures = leading(block)
        if not figures:
            continue

        # Every number the rest of the document contains, including the hero's
        # own text: a figure repeated in the sentence above it is still repeated.
        elsewhere = set()
        for other_index, other in enumerate(blocks):
            if other_index == index:
                continue
            _numbers(other, elsewhere)

        restated = [(lbl, val) for lbl, val in figures
                    if isinstance(val, (int, float)) and float(val) in elsewhere]
        if len(restated) * 2 < len(figures):
            continue

        named = ", ".join(f"{lbl or '?'} {val:g}" for lbl, val in restated)
        warnings.append(
            f"leading-numbers: blocks[{index}] ({key}) restates "
            f"{len(restated)} of {len(figures)} figures the document explains "
            f"elsewhere ({named}). A number is worth leading with when it IS the "
            f"finding; when a chart further down gives it a denominator or a "
            f"comparison, the tile is the same fact with the context removed. "
            f"Cut it, or lead with the one number nothing else says."
        )
    return warnings
