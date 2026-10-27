"""The brief: the whole design of the document, in one file, before it is built.

Steps 2 to 6 of the pipeline *are* the design of the document, and until this
file existed not one of them had an artifact. `pipeline.md` said "written down"
eight times and never said where, so the reader, the mode, the order, the
scenes and the form of every claim lived in a reasoning buffer and died with it.
The measured cost, from one 993 KB session: the same analogy decision reopened
thirteen times, a close-up designed six times and shipped nowhere, a block order
reasoned out and then not used, and a handoff that reconstructed six-step-old
decisions from memory and got them wrong.

The brief is that missing file. One section per section of the page:

```json
{
  "meta": {"reader": "...", "mode": "lesson", "page": "scroll"},
  "sections": [
    {"id": "what-it-is",
     "asks": "What is a gear bearing?",
     "teaches": ["gear bearing"],
     "form": "figure", "rank": 1,
     "view": "two-bearings-side-by-side",
     "shows": "the same bearing twice, balls in one and toothed gears in the other",
     "instead_of": {"block": "analogy", "because": "the mapping is one image"}}
  ]
}
```

`asks` / `teaches` / `id` are the old ladder, absorbed. It used to live in its
own `ladder.json`, and it drifted: on the last real run that file held seven
rungs while the shipped document held five different ones, and nothing noticed,
because the build only ever read the copy embedded in the spec. One file cannot
disagree with itself.

`form`, `view`, `shows`, `rank` and `instead_of` are new, and `view` is the one
that earns the file. It names the **viewpoint** a figure is drawn from, and no
two figures may share one. That single check catches the failure this was built
after: a document whose three figure slots all held the same object, face on,
drawn four times, which nothing in the skill could see because figures were only
ever compared after they were drawn, and by then they were sunk cost.

**Nothing in this file is copy.** `shows` describes a picture to whoever draws
it and `because` records a decision; neither may appear on the page, and
`--against` checks that they do not. The predecessor of this file got that
wrong: it asked for a one-line sentence per rung, capped short, and the register
that cap trains (clipped, declarative, aphoristic) leaked straight into every
lede on the page. `asks` is a question because a question is the one thing here
that is *supposed* to reach the reader, as the section opener, in lesson mode.
"""

from __future__ import annotations

import json
import re

from . import density

ASK_WORDS = 16          # a section question, not a summary of the section
TERM_WORDS = 4          # a term is a name the reader learns, not a description
SHOWS_WORDS = 40        # a picture described to whoever draws it
MIN_FIGURES = 2         # the floor: nothing drawn is the failure, not the safe option
MAX_FIGURES = 3         # the ranking exercise, made mandatory; the cap's own floor
ECHO_RATIO = 0.7        # how much of a brief note may resurface as page copy

# The page's furniture: blocks that carry no claim of their own, so they need no
# entry in the brief and their absence from it is not filler arriving late. A
# `section` opener is generated from its section's `asks`, a `bridge` is the
# sentence between two rungs, and a glossary or a method note is reference
# material a reader reaches for rather than reads.
FURNITURE = {"hero", "section", "bridge", "definitions", "footnotes"}

# An escape hatch is a sentence, never a flag, and it is the same length
# everywhere: long enough that writing it is a decision. `build.py` uses the
# same figure for `meta.scenes`.
ESCAPE_WORDS = 8


def _written(meta: dict, key: str) -> bool:
    """True when `meta[key]` holds a real written reason rather than a
    placeholder or a shrug. Every hard rule below can be overridden by one, and
    by nothing else."""
    text = str(meta.get(key) or "").strip()
    return "<" not in text and density.words(text) >= ESCAPE_WORDS


def figure_cap(count: int) -> int:
    """How many drawings a document of `count` sections may carry.

    Three was flat, and on a twelve-section scroll a flat three reads as "draw
    three things and paste nine". The cap is a ranking exercise, so it scales
    with how much there is to rank: half the sections, never fewer than three.
    """
    return max(MAX_FIGURES, (count + 1) // 2)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or "sections" not in data:
        raise SystemExit(
            f"[brief] {path} is not a brief: it needs `meta` and `sections`.\n"
            f"  Write one with: ig.py brief --new {path}")
    return data


def sections(brief: dict) -> list:
    return [s for s in (brief.get("sections") or []) if isinstance(s, dict)]


def is_figure(section: dict) -> bool:
    return str(section.get("form", "")).strip().lower() in ("figure", "authored")


def _graphic(form: str, registry) -> bool:
    return registry.is_graphic({"type": form})


def _norm(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


# ----------------------------------------------------------------- checking --

# Narrow on purpose. This is not a style checker; it catches the one shape
# that shipped, which is a question whose only subject is a pronoun or the
# word "thing". Anything longer would be another jig for a document to be
# filed down to fit.
_UNNAMED = re.compile(
    r"\b(?:the |a |this |that )?(?:thing|things|stuff|item|element)\b", re.I)


def _unnamed(asks: str) -> bool:
    return bool(_UNNAMED.search(asks))


def audit(brief: dict, registry) -> tuple:
    """(errors, warnings) for the design, before a line of it is built.

    Returns rather than raises, because fixing a skeleton one fault per run is
    how an author stops writing skeletons.
    """
    errors, warnings = [], []
    meta = brief.get("meta") or {}
    mode = str(meta.get("mode", "argument")).lower()
    rows = sections(brief)

    if mode not in ("argument", "lesson"):
        errors.append(f"meta.mode must be 'lesson' or 'argument' (got {mode!r})")
    if not str(meta.get("reader", "")).strip():
        errors.append(
            "meta.reader is empty. Who reads this, and what do they already "
            "know?\n      It decides which words are allowed to appear at all, "
            "so it cannot be\n      deferred to the writing.")
    if mode == "lesson" and not str(meta.get("contradicts", "")).strip():
        warnings.append(
            "brief-uncontested: meta.contradicts is empty. A lesson that never "
            "contradicts anything the reader believes reads as marketing. Name "
            "the belief here, and the section that takes it on gets to earn its "
            "place.")
    # The starter file used to ship three filled-in sections and every document
    # built from it came out in their order, opening on the same side-by-side
    # comparison. A skeleton with slots in it gets filled, never replaced. So
    # the starter ships no sections at all, and the order is a field the author
    # has to write, against an alternative they had to reject in writing.
    if not _written(meta, "spine"):
        errors.append(
            "meta.spine is empty or unwritten. Name the order THIS subject has "
            "to be met in,\n      in one line. Not the order of the source, "
            "and not what-it-is / how-it-works /\n      what-it-is-not, which "
            "is the shape every document takes when nobody chose one.")
    if not _written(meta, "spine_rejected"):
        errors.append(
            "meta.spine_rejected is empty or unwritten. Name the second spine "
            "you considered\n      and why it lost, in one line. Deciding is "
            "the job; an order arrived at by\n      default is the one this "
            "skill keeps shipping.")
    if mode == "argument" and not str(meta.get("claim", "")).strip():
        errors.append(
            "meta.claim is empty and the mode is 'argument'. One sentence the "
            "reader should\n      believe by the end. If you cannot write it, "
            "nothing downstream rescues the document.")
    if not rows:
        errors.append("`sections` is empty. The brief is the document.")
        return errors, warnings

    seen_ids, figures = {}, []
    for index, section in enumerate(rows):
        where = f"sections[{index}]"
        sid = str(section.get("id", "")).strip()
        if not sid:
            errors.append(f"{where} has no `id`. The id is what the built block "
                          f"is checked against.")
        elif sid in seen_ids:
            errors.append(f'{where}: id "{sid}" is already used at '
                          f"sections[{seen_ids[sid]}].")
        else:
            seen_ids[sid] = index
        label = sid or where

        # -- form ------------------------------------------------------------
        form = str(section.get("form", "")).strip()
        if not form:
            errors.append(
                f"{label}: no `form`. Every section names what it is: a block "
                f"type, or `figure`\n      for something drawn. Run `ig.py "
                f"catalog` for the list.")
            continue
        key, entry = registry.resolve(form)
        if not entry:
            errors.append(
                f'{label}: `form` is "{form}", which is not a block type.\n'
                f"      `ig.py catalog` lists all of them.")
            continue

        # -- the rejected block ----------------------------------------------
        rejected = section.get("instead_of") or {}
        if is_figure(section):
            block = str(rejected.get("block", "")).strip()
            because = str(rejected.get("because", "")).strip()
            if not block or not because:
                errors.append(
                    f"{label}: a drawn figure names the block it beat.\n"
                    f'      "instead_of": {{"block": "<type>", "because": '
                    f'"<what it could not show>"}}\n'
                    f"      Read the candidate first with `ig.py catalog "
                    f"<type>`, then finish\n      \"<block> carries this "
                    f"completely, because ___\". If you can finish it,\n"
                    f"      the answer is that block and not a figure.")
            else:
                rkey, rentry = registry.resolve(block)
                if not rentry:
                    errors.append(f'{label}: instead_of.block is "{block}", '
                                  f"which is not a block type.")
                elif rkey == key:
                    errors.append(
                        f"{label}: instead_of.block is the form itself. The "
                        f"sentence has to name\n      something specific that "
                        f"was genuinely considered and lost.")

        # -- the picture ------------------------------------------------------
        shows = str(section.get("shows", "")).strip()
        if _graphic(key, registry) or is_figure(section):
            if not shows:
                errors.append(
                    f"{label}: no `shows`. Write the picture, not the chart "
                    f"type: what is on\n      screen, and what the reader's eye "
                    f"lands on first.")
            elif density.words(shows) > SHOWS_WORDS:
                warnings.append(
                    f"brief-long-shows: {label} describes the picture in "
                    f"{density.words(shows)} words. Past about "
                    f"{SHOWS_WORDS} it stops being a picture and starts being "
                    f"the block's copy, written early.")

        if is_figure(section):
            figures.append((index, label, section))

        # -- the question -----------------------------------------------------
        asks = str(section.get("asks", "")).strip()
        if mode == "lesson" and not asks:
            errors.append(
                f"{label}: no `asks`. In lesson mode every section is the "
                f"question it answers,\n      in the reader's words, and that "
                f"question is the section opener.")
        elif asks and density.words(asks) > ASK_WORDS:
            warnings.append(
                f"brief-long-ask: {label} asks a {density.words(asks)}-word "
                f"question (soft cap {ASK_WORDS}). A question a reader would "
                f"actually ask is short; a long one is usually two.")
        # In lesson mode `asks` IS the section opener, so a placeholder here
        # is not a note to yourself, it is a heading. The starter file shipped
        # "What is it?" and a document went out titled "What is the thing being
        # fixed?" across three sections. A question that names nothing is not a
        # question a reader would ask.
        if asks and ("<" in asks or _unnamed(asks)):
            errors.append(
                f"brief-unnamed-ask: {label} asks \"{asks}\", which names "
                f"nothing.\n      In lesson mode this string becomes the "
                f"section heading, verbatim. Put the\n      subject in it by "
                f"name: not \"What is the thing being fixed?\" but \"What is "
                f"the\n      integrations catalog?\". Vague here is vague on "
                f"the page.")
        if asks and not asks.rstrip().endswith("?"):
            warnings.append(
                f"brief-not-a-question: {label} has an `asks` that is not a "
                f"question. Write what the reader wants to know, not a summary "
                f"of the answer.")

        for term in section.get("teaches", []) or []:
            if "<" in str(term):
                errors.append(
                    f'{label}: `teaches` still holds the placeholder "{term}". '
                    f"Name the term this\n      section teaches, or delete the "
                    f"entry: an unfilled slot becomes a rung the\n      build "
                    f"then checks the page against.")
            elif density.words(term) > TERM_WORDS:
                errors.append(
                    f'{label}: "{term}" is {density.words(term)} words. A term '
                    f"is a name the reader\n      has to learn, not a "
                    f"description of one (cap {TERM_WORDS}).")

    # -- the establishing shot, checked rather than recommended ---------------
    # The rule was already written down: a document whose subject can be drawn
    # opens on a drawing of the subject. Nothing checked it, so the opener was
    # whatever the catalog offered first, and what the catalog offers first for
    # a subject the reader has never met is a two-column comparison.
    # The page's furniture is not the opening: a `hero` is the title, and a
    # `section` opener is a heading. The rule is about the first thing that
    # carries a claim, which is the first thing a reader has to understand.
    opener = next((r for r in rows
                   if registry.resolve(r.get("form"))[0] not in FURNITURE),
                  None)
    if opener is not None and not is_figure(opener) \
            and not _written(meta, "opens_on"):
        errors.append(
            f'brief-opens-on-a-block: the first section ("{opener.get("id")}") '
            f'is `{opener.get("form")}`.\n'
            f"      A reader who has not met the subject meets a chart of it "
            f"instead, and the\n      commonest thing to put there is two "
            f"columns comparing it with something else,\n      which teaches "
            f"the comparison and never the subject. Open on the subject "
            f"itself,\n      drawn, wide rather than tall. If it genuinely has "
            f"no picturable body, say so\n      in `meta.opens_on` "
            f"({ESCAPE_WORDS} words or more) and open on the claim.")

    # -- the figures, as a ranking rather than a queue -----------------------
    cap = figure_cap(len(rows))
    if len(figures) > cap:
        named = ", ".join(label for _i, label, _s in figures)
        errors.append(
            f"{len(figures)} figures, and the cap is {cap}: {named}.\n"
            f"      The cap is a ranking exercise, not a budget. Which "
            f"{cap} images does this\n      document live or die by? "
            f"The rest go on rails. Rank them and cut from\n      the bottom, "
            f"not from whichever came fourth in writing order.")

    # The cap had no counterpart, so nothing drawn was always the cheap option:
    # a catalog block costs one line and risks nothing, a figure costs a
    # viewpoint, an `alt`, an `encodes` and a rejection in writing. The
    # risk-free document was the one that drew nothing, and it shipped every
    # time, which is why every subject came out looking like the last one.
    if len(rows) >= MIN_FIGURES + 1 and len(figures) < MIN_FIGURES \
            and not _written(meta, "scenes"):
        errors.append(
            f"brief-nothing-drawn: {len(figures)} of {len(rows)} sections is "
            f"drawn, and the floor is {MIN_FIGURES}.\n"
            f"      A page assembled entirely from catalog shapes is a page "
            f"whose form was chosen\n      before its subject was, and it "
            f"arrives looking like every other one. Draw the\n      two images "
            f"this document lives or dies by.\n"
            f"      If the catalog really did carry every claim completely, "
            f"name what it carried\n      in `meta.scenes` ({ESCAPE_WORDS} "
            f"words or more). → references/scenes.md")

    ranks = {}
    for _index, label, section in figures:
        rank = section.get("rank")
        if not isinstance(rank, int) or not 1 <= rank <= cap:
            errors.append(
                f"{label}: a figure needs `rank`, an integer 1 to "
                f"{cap}.\n      Ranking is what makes the cap a "
                f"judgement instead of an arrival order.")
        elif rank in ranks:
            errors.append(f"{label}: rank {rank} is already held by "
                          f"{ranks[rank]}.")
        else:
            ranks[rank] = label

    # -- the check the file exists for ---------------------------------------
    views = {}
    for _index, label, section in figures:
        view = str(section.get("view", "")).strip().lower()
        if not view:
            errors.append(
                f"{label}: no `view`. Name the viewpoint this is drawn from, as "
                f"a slug:\n      \"face-on-whole\", \"one-tooth-enlarged\", "
                f"\"cutaway-side\", \"beside-a-ball-bearing\".\n"
                f"      It is what stops the document drawing the same picture "
                f"three times.")
            continue
        if view in views:
            if not str(section.get("view_repeats", "")).strip():
                errors.append(
                    f'view-repeats: {label} is drawn from "{view}", and so is '
                    f"{views[view]}.\n      Two figures from one viewpoint are "
                    f"one figure and a redraw. The reader\n      learns nothing "
                    f"from the second, because their eye has already been "
                    f"there.\n      Move this one: closer in, cut away, from "
                    f"the side, or beside something\n      the reader already "
                    f"owns. If it genuinely has to repeat, say why in\n"
                    f"      `view_repeats` and this becomes a warning.")
            else:
                warnings.append(
                    f'view-repeats: {label} repeats the viewpoint "{view}" from '
                    f'{views[view]}: "{section["view_repeats"]}"')
        else:
            views[view] = label

    # -- two text blocks in a row --------------------------------------------
    previous = None
    for section in rows:
        key, entry = registry.resolve(section.get("form"))
        graphic = bool(entry) and (_graphic(key, registry) or is_figure(section))
        if previous is not None and not graphic and not previous[1]:
            warnings.append(
                f"brief-text-run: {section.get('id')} and {previous[0]} are both "
                f"text forms, back to back. Two in a row is where a graphic "
                f"document turns into an article with decorations.")
        previous = (section.get("id"), graphic)

    return errors, warnings


# ------------------------------------------------------------------ ladder --

def to_ladder(brief: dict) -> list:
    """The brief's order, in the shape `meta.ladder` wants.

    The ladder is no longer authored anywhere. It is derived, every build, from
    the one file that also holds the pictures, which is the only arrangement in
    which the two cannot disagree.
    """
    rungs = []
    for section in sections(brief):
        asks = str(section.get("asks", "")).strip()
        teaches = [t for t in (section.get("teaches") or []) if str(t).strip()]
        if not asks and not teaches:
            continue
        rungs.append({"asks": asks, "introduces": teaches,
                      "at": str(section.get("id", ""))})
    return rungs


def vocabulary(brief: dict, section_id: str) -> tuple:
    """(legal, not yet legal) terms at one section, for its work order.

    Handing a worker the words it may use is the cheap half of the forward
    reference check. The expensive half runs after the block exists, and its
    only remedy at that point is to delete the sentence that used the word.
    """
    legal, later, reached = [], [], False
    for section in sections(brief):
        terms = [str(t) for t in (section.get("teaches") or []) if str(t).strip()]
        if reached:
            later.extend(terms)
        else:
            legal.extend(terms)
        if str(section.get("id", "")) == section_id:
            reached = True
    return legal, later


# ----------------------------------------------------------------- against --

def against(brief: dict, spec: dict, registry) -> tuple:
    """(errors, warnings): what the brief promised, against what got built."""
    errors, warnings = [], []
    blocks = {str(b.get("id")): b for b in (spec.get("blocks") or [])
              if isinstance(b, dict) and b.get("id")}
    order = [str(b.get("id")) for b in (spec.get("blocks") or [])
             if isinstance(b, dict) and b.get("id")]

    from . import ladder as ladder_mod

    promised = []
    for section in sections(brief):
        sid = str(section.get("id", ""))
        block = blocks.get(sid)
        if block is None:
            errors.append(
                f'brief-unbuilt: the brief has a section "{sid}" and the spec '
                f"has no block with that id.\n      Either build it, or take it "
                f"out of the brief and say why it went.")
            continue
        promised.append(sid)
        form = str(section.get("form", "")).strip()
        want, _ = registry.resolve(form)
        got, _ = registry.resolve(block.get("type"))
        if want != got:
            errors.append(
                f'brief-form-changed: "{sid}" was briefed as `{want}` and built '
                f"as `{got}`.\n      A form that changed during the drawing is "
                f"a decision that got made twice.\n      Change the brief and "
                f"say why, or build what the brief says.")

        # Nothing in the brief is copy. `shows` is a description written for
        # whoever draws the block, and `because` is a decision record. Both
        # arriving on the page is the failure mode this file was written to
        # stop: the skeleton's register becoming the document's voice.
        seen = ladder_mod.visible_text(block, registry)
        page = _norm(seen)
        for field, text in (("shows", section.get("shows")),
                            ("instead_of.because",
                             (section.get("instead_of") or {}).get("because"))):
            note = _norm(text)
            if len(note) >= 5 and len(note & page) / len(note) >= ECHO_RATIO:
                warnings.append(
                    f'brief-echo: "{sid}" reprints its `{field}` on the page.\n'
                    f"      The brief is scaffolding written to yourself. Its "
                    f"sentences are notes about\n      a picture, not the "
                    f"page's voice, and pasting them is how a document ends "
                    f"up\n      sounding like its own outline.")

    extra = [i for i in order if i not in promised
             and registry.resolve(blocks[i].get("type"))[0] not in FURNITURE]
    for sid in extra:
        warnings.append(
            f'brief-unbriefed: the spec has a block "{sid}" that the brief '
            f"never named. It arrived during the drawing, which is where "
            f"filler arrives.")

    positions = {sid: order.index(sid) for sid in promised}
    ranked = [positions[s] for s in promised]
    if ranked != sorted(ranked):
        errors.append(
            "brief-order-changed: the page delivers the sections in a different "
            "order than\n      the brief. The reader meets the page's order. "
            "Move the blocks back, or\n      re-check the brief in the new "
            "order and let the ladder be re-derived.")
    return errors, warnings


# ------------------------------------------------------------------ starter --

# The starter used to ship three filled-in sections: `what-it-is` (viewpoint
# "beside-something-the-reader-owns"), `how-it-works`, `what-it-is-not`. It was
# written as an illustration of the schema and it was read as the plan, every
# time, because a skeleton with slots in it gets filled rather than replaced.
# Nine documents in a row opened on the same side-by-side comparison of the
# subject with something familiar, and no amount of "improvise" in SKILL.md
# moved it, because the instruction was prose and the template was a file.
#
# So the starter ships no sections. The schema is printed instead, once, as
# text, next to eight orders a document could take, none of which is a default.

STARTER = {
    "meta": {
        "reader": "who reads this, and what do they already know",
        "mode": "lesson",
        "page": "scroll",
        "theme": "default",
        "contradicts": "what the reader believes that this page takes on",
        "spine": "<the order this subject has to be met in, one line>",
        "spine_rejected": "<the other order you considered, and why it lost>",
        "source": "out/ledger.json",
    },
    "sections": [],
}


# Printed by `ig.py brief --new`, never written into the file. Anything that
# lands in the file gets filled in; anything printed has to be retyped, and
# retyping is where a decision happens.
STARTER_NOTE = """\
  `sections` is empty on purpose, and the brief will refuse itself until you
  write it. It used to arrive with three sections already in it and every
  document came out in their order, because a skeleton with slots gets filled,
  not replaced.

  Write `meta.spine` first: the order THIS subject has to be met in. Eight that
  are not the default, so that none of them is:

    the loop           it runs forever; open on the cycle, not on a first step
    the money          follow one unit of the quantity from where it enters
    the failure        open on the case that breaks, then on what stops it
    the map            everything at once, laid out in space, then one route
    one instance       one named example end to end, then the general rule
    the clock          one day, one release, one request, in real time
    the cast           the actors first, then what passes between them
    the wrong picture  what the reader already draws in their head, redrawn

  Then one entry per section, in the order the reader meets them:

    {"id": "...", "asks": "...?", "teaches": ["..."],
     "form": "figure", "rank": 1,
     "view": "the-viewpoint-it-is-drawn-from",
     "shows": "what is on screen, and what the eye lands on first",
     "instead_of": {"block": "the catalog block it beat",
                    "because": "what that block could not show"}}

  `form` is a catalog block type or `figure` for something drawn. The first
  section is drawn: the reader meets the subject before they meet a chart of
  it. At least two sections are drawn, and at most half of them.

  The reader comes first; it decides which words may appear at all. Then:

    ig.py brief {path}"""
