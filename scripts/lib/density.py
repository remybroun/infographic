"""The text budget: what stops this skill from producing an essay with charts.

The first version of this skill shipped the budget as advice, and advice lost.
The reference docs said "reduce text", the linter warned when prose was *absent*,
and the natural result was an eight-page A4 document carrying 2,086 words with a
bar chart at the bottom of page two. Every paragraph in it was individually
defensible. That is exactly the failure mode: nothing says no.

So the budget lives here, in code, and it runs before a single pixel is drawn.
A block whose text exceeds its role's cap is a build error naming the block, the
role, the count and the cap. There is no truncation, because silently cutting a
sentence in half changes what the document claims. The author has to make the
choice the budget is forcing: say it shorter, or draw it instead.

Three densities:

- `graphic` (the default): titles and indicators only. The picture carries the
  idea. Body prose is refused outright.
- `lesson`: graphic density with room to teach. The same refusal of body prose,
  slightly longer labels, and one sanctioned channel for connective tissue: the
  `bridge` block, capped at 40 words and refused everywhere else. It exists
  because the graphic budget and the instruction "explain it to someone who has
  never met this subject" were in direct conflict, and the budget won every
  time: it is enforced in code and the instruction was a paragraph of prose. A
  6-word label cap makes `skipped_bucket` cost one word and "the recipient
  switched that group off" cost six, so the cheapest accurate label is always
  the one only the author can read. This density is that conflict resolved in
  the author's favour, with a ceiling low enough that it cannot become an essay.
- `report`: the old behaviour, for when a real prose document is genuinely
  wanted. Opt in explicitly with `meta.density` or `--density report`; it is
  never the fallback for "the text did not fit".

`lesson` is not the fallback either. The order to try is: draw it, then rewrite
it shorter, then `lesson` if the subject genuinely has to be taught from zero.
"""

from __future__ import annotations

import re

DENSITIES = ("graphic", "lesson", "report")

# Caps are in WORDS, not characters, because words are what a reader parses and
# what an author can act on. "Cut three words" is a real instruction; "cut 18
# characters" is not.
CAPS = {
    "graphic": {
        # Titles are LITERAL DESCRIPTIONS of what is shown, so they need room for
        # a subject, a scope and a period. These caps were 10 and 9, which is not
        # enough to write "Baseline confidence assigned to a claim by the kind of
        # source it came from" (14 words). What *does* fit in nine words is an
        # aphorism, so nine words is what kept getting produced: "Corroboration
        # saturates", "The channel narrows, swells, then narrows again". The cap
        # was quietly selecting for the one register the skill forbids.
        "hero_title": 16,   # what the document covers, stated plainly
        "title": 14,        # block, section and step titles
        "subtitle": 16,     # the single line under a title, and section ledes
        "label": 6,         # anything sitting beside a mark: chips, terms, axes
        "detail": 12,       # the one supporting line an item may carry
        "note": 18,         # footers, sources, methodology one-liners
        "callout": 24,      # the one thing that must not be skimmed past
        "quote": 26,        # a human voice, trimmed to the part that lands
        "body": 0,          # 0 means refused: there is no body prose here
        # Text inside an authored figure's own SVG. Without this the budget has
        # a hole exactly the size of a `<text>` element: hand-drawing is the one
        # place an author can write a paragraph and have it counted as a
        # picture. 40 is a third of a whole page's allowance (see
        # WORDS_PER_PAGE), because one drawing must never be the page's text.
        "figure_text": 40,
        # The connective sentence between two rungs of a ladder, refused here.
        # A `bridge` at graphic density would be body prose with a different
        # key, which is exactly the hole `body: 0` exists to close.
        "bridge": 0,
    },
    # Every cap here is the graphic cap plus room for one ordinary word where a
    # jargon term would otherwise have fit. `label` at 8 rather than 6 is the
    # whole point in miniature: "recipient switched this off" is five words and
    # does not fit under 6 once a qualifier is needed, so the identifier wins.
    # `body` stays refused, because a lesson is still carried by its pictures.
    "lesson": {
        "hero_title": 18, "title": 16, "subtitle": 24, "label": 8,
        "detail": 18, "note": 24, "callout": 32, "quote": 30, "body": 0,
        "figure_text": 55,
        # One line of connective tissue: "so far, every request went to one
        # place. Here is what happens when there are two." A lesson needs it and
        # graphic density has nowhere to put it, which is how the connective
        # sentence ends up crammed into a subtitle that then stops stating the
        # finding. 40 words is a sentence or two, not a paragraph.
        "bridge": 40,
    },
    "report": {
        "hero_title": 24, "title": 22, "subtitle": 40, "label": 12,
        "detail": 60, "note": 60, "callout": 90, "quote": 60, "body": 1_000_000,
        "figure_text": 120, "bridge": 90,
    },
}

# Words per page, checked by the linter once the real page count is known.
# 150 is about one column-inch of body text per A4 page: enough for literal
# titles, labels and indicators, not enough for an argument made in sentences.
# It was 130 when titles were capped at 9; raising the title cap without raising
# this would buy the longer title by taking the words out of the subtitle, which
# is exactly where the finding lives.
#
# 260 for `lesson`, which is not a compromise between 150 and 900 but a measured
# floor: the smallest allowance that fits a four-rung ladder's bridges, its
# longer labels and one definition, on a page that is still mostly picture. A
# lesson page over 260 words has stopped teaching and started narrating.
WORDS_PER_PAGE = {"graphic": 150, "lesson": 260, "report": 900}

# The same budget for a document with no pages to divide by (`page: scroll`).
# Charged per block instead, and derived from the caps above rather than picked:
# title (14) + subtitle (16) + note (18) is the most chrome a single block may
# legally carry, so a document averaging that much has every block running at
# maximum text, which is the signature of an essay wearing block formatting.
WORDS_PER_BLOCK = {"graphic": 48, "lesson": 78, "report": 160}

# Which role a payload key carries, when the block does not override it.
# Anything absent from this map is data (values, colours, ids) and is not text.
DEFAULT_ROLES = {
    "title": "title",
    "subtitle": "subtitle",
    "lede": "subtitle",
    "headline": "subtitle",
    "kicker": "label",
    "label": "label",
    "term": "label",
    "name": "label",
    "stage": "label",
    "attribution": "label",
    "author": "label",
    "unit": "label",
    "unit_label": "label",
    "axis_x": "label",
    "axis_y": "label",
    "low_label": "label",
    "high_label": "label",
    "do_title": "label",
    "dont_title": "label",
    "text": "detail",
    "detail": "detail",
    "note": "note",
    "source": "note",
    "caption": "note",
    "method": "note",
}

# Keys that are never prose: raw markup, data arrays, identifiers, geometry.
SKIP_KEYS = {
    "html", "src", "id", "class", "type", "options", "values", "value", "data",
    "series", "trend", "rows", "columns", "align", "span", "height", "width",
    "frame", "break", "allow_break", "skip", "colors", "color", "palette",
    "ratio", "fit", "decimals", "currency", "compact", "ordinal", "numbered",
    "orientation", "level", "tone", "vs", "number", "delta", "delta_unit",
    "delta_period", "delta_decimals", "up_is_good", "target", "max", "min",
    "table", "reverse", "alt_ramp", "emphasis", "lead", "ordered",
    # Pictogram names are identifiers pointing at a shape, not words a reader
    # reads. Listed rather than left to fall through the role map, because a
    # drawing costing nothing against the budget is the argument for drawing.
    "glyph", "icon", "unit_value", "per", "size", "gap", "row_gap",
    "show_values", "vary_color",
    # Authored figures: geometry, declarations, and the accessibility twin.
    # `alt` is exempt for the same reason a table is, it is a duplicate of
    # what the drawing already says, and charging it would push an author to
    # write a worse description to stay inside the budget.
    "viewbox", "encodes", "alt", "bleed", "defs",
}

# Keys whose text is not the string itself. `svg` is markup: the words a reader
# sees are the ones inside its `<text>` elements, and they are charged as
# `figure_text`. Without this the budget has a hole exactly the size of a
# `<text>` element.
MARKUP_ROLES = {"svg": "figure_text"}

_MARKUP = re.compile(r"\*\*|[*`]|\[(.+?)\]\((?:https?://[^)\s]+)\)")
_SVG_TEXT = re.compile(r"<(?:text|tspan)\b[^>]*>(.*?)</(?:text|tspan)>", re.S | re.I)
_TAG = re.compile(r"<[^>]*>")


def svg_words(markup) -> int:
    """Words a reader sees inside SVG markup: the contents of `<text>` and
    `<tspan>` only. Attribute values, path data and element names are geometry,
    not reading matter."""
    if not markup:
        return 0
    visible = " ".join(_TAG.sub(" ", m) for m in _SVG_TEXT.findall(str(markup)))
    return len([w for w in re.split(r"\s+", visible.strip()) if w])


def words(text) -> int:
    """Word count of a payload string, with the inline markup subset removed so
    `**one**` costs one word rather than three."""
    if text is None:
        return 0
    cleaned = _MARKUP.sub(r"\1", str(text))
    return len([w for w in re.split(r"\s+", cleaned.strip()) if w])


class Violation:
    __slots__ = ("block", "path", "role", "count", "cap", "sample")

    def __init__(self, block, path, role, count, cap, sample):
        self.block, self.path, self.role = block, path, role
        self.count, self.cap, self.sample = count, cap, sample

    def __str__(self) -> str:
        where = f"{self.block}.{self.path}"
        if self.role == "figure_text":
            return (f"  {where}: {self.count} words of `<text>` inside the drawing, "
                    f"cap is {self.cap}.\n"
                    f"      {self.sample}\n"
                    f"      → a drawing labels, it does not narrate. Move the sentences "
                    f"into the block's own `title` and `subtitle`, cut the labels to "
                    f"nouns, or split the drawing in two.")
        if self.cap == 0 and self.role == "bridge":
            return (f"  {where}: `bridge` is not available at this density "
                    f"({self.count} words).\n"
                    f"      {self.sample}\n"
                    f"      → a bridge is the one connective sentence a lesson "
                    f"is allowed between\n        two rungs of its ladder, and "
                    f"it exists at `lesson` density only. Set\n        "
                    f'meta.density to "lesson" if this document teaches a '
                    f"subject from zero;\n        otherwise the sentence belongs "
                    f"in the next block's `subtitle`, or drawn.")
        if self.cap == 0:
            return (f"  {where}: body prose is not available at graphic density "
                    f"({self.count} words).\n"
                    f"      {self.sample}\n"
                    f"      → draw it. If this paragraph is a sequence use `process`, a "
                    f"comparison use `comparison` or `scorecard`, a structure use `stack` "
                    f"or `tree`, a set of facts use `chips` or `kpi`. If it is one "
                    f"sentence linking two rungs of a lesson, it is a `bridge` at "
                    f"--density lesson. If it is genuinely an essay, --density report.")
        return (f"  {where}: {self.count} words as a `{self.role}`, cap is {self.cap}.\n"
                f"      {self.sample}\n"
                f"      → cut to {self.cap}, or move the idea into the graphic beside it.")


def _sample(text, limit: int = 76) -> str:
    flat = re.sub(r"\s+", " ", str(text)).strip()
    return f'"{flat[:limit]}…"' if len(flat) > limit else f'"{flat}"'


def _scan(node, roles, caps, block_label, path, out, exempt):
    """Walk a block payload, charging every string against its role's cap."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in SKIP_KEYS or key in exempt:
                continue
            _scan(value, roles, caps, block_label,
                  f"{path}.{key}" if path else key, out, exempt)
        return

    if isinstance(node, list):
        for index, value in enumerate(node):
            _scan(value, roles, caps, block_label, f"{path}[{index}]", out, exempt)
        return

    if not isinstance(node, str) or not node.strip():
        return

    # The role comes from the last named key on the path: `steps[2].text` is a
    # `detail`, and a bare list of strings (`items[0]`) inherits its list's key.
    key = re.sub(r"\[\d+\]$", "", path).rsplit(".", 1)[-1]
    role = MARKUP_ROLES.get(key) or roles.get(key)
    if role is None:
        return
    cap = caps.get(role)
    if cap is None:
        return
    count = svg_words(node) if key in MARKUP_ROLES else words(node)
    sample = _sample(" ".join(_TAG.sub(" ", m) for m in _SVG_TEXT.findall(node))
                     if key in MARKUP_ROLES else node)
    if count > cap:
        out.append(Violation(block_label, path, role, count, cap, sample))


def block_words(block: dict, registry) -> int:
    """Words one block contributes, charged exactly as `audit` charges them.

    Public because the alternative is every caller that wants to know *where*
    the words are re-implementing the SKIP_KEYS walk, which is how a budget
    report drifts from the budget it reports on.
    """
    _key, entry = registry.resolve(block.get("type"))
    if not entry or entry.get("text_exempt") or block.get("skip"):
        return 0
    exempt = set(entry.get("text_free", ()))
    total = 0

    def walk(node, key=None):
        nonlocal total
        if isinstance(node, dict):
            for name, value in node.items():
                if name not in SKIP_KEYS and name not in exempt:
                    walk(value, name)
        elif isinstance(node, list):
            for item in node:
                walk(item, key)
        elif isinstance(node, str):
            total += svg_words(node) if key in MARKUP_ROLES else words(node)

    walk(block)
    return total


def audit(spec: dict, density: str, registry) -> list:
    """Every text-budget violation in a spec, in document order.

    Returns rather than raises, so the caller can report all of them at once.
    Fixing an eight-page document one error per rebuild is how an author gives
    up and reaches for `--density report`.
    """
    caps = CAPS.get(density, CAPS["graphic"])
    violations = []
    for index, block in enumerate(spec.get("blocks", [])):
        if not isinstance(block, dict) or block.get("skip"):
            continue
        key, entry = registry.resolve(block.get("type"))
        if not entry or entry.get("text_exempt"):
            continue
        roles = dict(DEFAULT_ROLES)
        roles.update(entry.get("text_roles", {}))
        label = f'blocks[{index}] ({key}{"#" + block["id"] if block.get("id") else ""})'
        _scan(block, roles, caps, label, "", violations,
              exempt=set(entry.get("text_free", ())))
    return violations


def enforce(spec: dict, density: str, registry) -> None:
    violations = audit(spec, density, registry)
    if not violations:
        return
    lines = "\n".join(str(v) for v in violations)
    raise SystemExit(
        f"[density] {len(violations)} text-budget violation(s) at "
        f"`{density}` density.\n\n{lines}\n\n"
        f"  The budget is the point: at graphic density the picture carries the "
        f"idea and\n  the words are titles and indicators. See "
        f"references/graphic-first.md."
    )


def resolve(meta_value, override=None) -> str:
    value = str(override or meta_value or "graphic").lower()
    if value not in DENSITIES:
        raise SystemExit(f"[density] meta.density must be one of "
                         f"{', '.join(DENSITIES)} (got {value!r})")
    return value
