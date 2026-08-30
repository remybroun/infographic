"""The ladder: the order a reader has to climb, checked against the page.

This skill could always choose a good form for a fact. What it could not do was
*teach*, and the reason was structural rather than stylistic. The pipeline's
first artifact was a fact ledger: numbers with the sentences they came from.
Its second was a claim, defined as "one sentence the reader should believe by
the end". Both are the frame of an argument. Neither is an explanation, and
nothing downstream ever asked for one, so the document always opened on the
conclusion and worked backwards, which is the inverted pyramid, which is a
document written for someone who already knows what the subject is.

A ladder is the other shape: rungs, in the order a reader has to climb them,
where nothing appears before the thing it depends on.

**Nobody writes a ladder by hand.** It is derived from `brief.json`, where the
order sits in the same file as the pictures, and `meta.ladder` in a spec is the
derived copy. It used to be authored, in its own `ladder.json`, and it drifted:
on the last real run that file held seven rungs against the document's five,
and nothing noticed. → `brief.py`

```json
"meta": {
  "mode": "lesson",
  "ladder": [
    {"asks": "What is a tenant?",
     "introduces": ["tenant"], "at": "what-a-tenant-is"},
    {"asks": "How many tenants share one program?",
     "introduces": ["application"], "at": "one-app-many-sites"}
  ]
}
```

Three keys, and each one is load-bearing:

- `asks` is the question that section answers, in the reader's words. In lesson
  mode it is also the section opener, so it is the one field here a reader ever
  sees. It used to be `says`, a short declarative sentence, and that was a
  mistake worth recording: the clipped register a short-sentence cap trains got
  copied out of the skeleton into every lede on the page. A question cannot be
  pasted into a document as its voice. `says` is still read, for specs written
  before the change.
- `introduces` names the vocabulary this rung teaches. It is what makes the
  order checkable rather than declarative.
- `at` is the block id where the rung lands, which is what makes the ladder a
  claim about the page rather than a note about intentions.

The check that matters is `forward-reference`: a term used in a block that
comes *before* the rung introducing it. That is the insider register, made
measurable. Every other check in this skill measures density, form or geometry,
and a document can pass all of them while opening on a word the reader will not
meet for another four blocks.

**It is a warning, and it was an error once.** As an error it stopped the
build, and the cheapest way past it was always to rewrite the sentence that
tripped it. On the run that changed this, a hero reading "Four fixes to the
RentRemote integrations catalog" was rewritten to "the list of outside software
a customer can connect" to clear a forward reference on the word *catalog*, and
the title lost its subject. The check cannot tell a term of art from the name
of the thing the document is about, so it no longer gets to decide. Titling
blocks are exempt outright.
"""

from __future__ import annotations

import re

from . import density

RUNG_WORDS = 24        # a question a reader would ask, not a summary of the answer
TERM_WORDS = 4         # a term is a name, not a description
MIN_RUNGS = 3          # two rungs is a claim with a preamble, not a ladder


def rung_text(rung: dict) -> str:
    """What this rung is, for a human. `asks` now, `says` in older specs."""
    return str(rung.get("asks") or rung.get("says") or "").strip()

# `alt` and `encodes` describe a drawing for a reader who cannot see it, and a
# table twin restates a graphic that has already been walked. Charging them for
# a forward reference would push an author to write a worse description.
_SKIP = density.SKIP_KEYS | {"alt", "encodes", "table", "id"}


def _strings(node, key=None, out=None):
    """Every string a reader actually sees in a block payload."""
    out = [] if out is None else out
    if isinstance(node, dict):
        for name, value in node.items():
            if name not in _SKIP:
                _strings(value, name, out)
    elif isinstance(node, list):
        for item in node:
            _strings(item, key, out)
    elif isinstance(node, str):
        if key in density.MARKUP_ROLES:
            out.extend(density._SVG_TEXT.findall(node))
        else:
            out.append(node)
    return out


def visible_text(block: dict, registry) -> str:
    """The block's reading matter, flattened. Exempt blocks contribute nothing:
    a citation in `footnotes` and a value in a `table` are reference material,
    reached for deliberately, not the page teaching a word to someone."""
    _key, entry = registry.resolve(block.get("type"))
    if not entry or entry.get("text_exempt") or block.get("skip"):
        return ""
    return " ".join(_strings(block))


def _term_pattern(term: str):
    """Match a term as words, tolerating a trailing plural and any run of
    whitespace between its parts."""
    parts = [re.escape(p) for p in str(term).split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"(?:s|es)?\b", re.I)


def audit(spec: dict, registry) -> tuple:
    """(errors, warnings) for the ladder declared in `meta.ladder`.

    Returns rather than raises so every problem is reported at once. Fixing an
    ordering fault one rebuild at a time is how an author stops declaring a
    ladder at all.
    """
    meta = spec.get("meta", {}) or {}
    mode = str(meta.get("mode", "argument")).lower()
    rungs = meta.get("ladder") or []
    errors, warnings = [], []

    if mode not in ("argument", "lesson"):
        errors.append(f"meta.mode must be 'lesson' or 'argument' (got {mode!r})")
        return errors, warnings

    if not rungs:
        if mode == "lesson":
            errors.append(
                "meta.mode is 'lesson' and there is no meta.ladder.\n"
                "      A lesson is an ordered explanation or it is a pile of "
                "correct pictures.\n"
                "      Do not write the rungs here. Point the spec at the brief "
                "that already holds\n      the order, and they are derived every "
                "build:\n"
                '        "meta": {"brief": "out/brief.json"}\n'
                "      → references/teaching.md")
        return errors, warnings

    if not isinstance(rungs, list):
        errors.append("meta.ladder must be a list of rungs")
        return errors, warnings

    # An authored page has no blocks to land on, so a rung lands on any element
    # in the markup that carries an `id`, and the text belonging to that rung is
    # everything up to the next one. The check is unchanged and so is the
    # question it asks: does a word appear before the thing that teaches it? Only
    # the definition of "before" moves, from block order to document order.
    body = str(spec.get("body") or "").strip()
    if body:
        from . import authored as authored_mod
        # A placed catalog block is an empty placeholder in the source, so its
        # payload has to be handed in or the ladder cannot see a single word of
        # it: a term it introduces reads as never used, and a forward reference
        # inside it passes the build.
        placed = {}
        for block in spec.get("blocks", []) or []:
            if isinstance(block, dict) and block.get("id"):
                placed[str(block["id"])] = visible_text(block, registry)
        marks = authored_mod.landmarks(body, placed)
        positions = {}
        for index, (name, _text) in enumerate(marks):
            positions.setdefault(name, index)
        blocks = [{"type": "authored", "id": name} for name, _ in marks]
        _authored_texts = [text for _, text in marks]
    else:
        blocks = spec.get("blocks", []) or []
        _authored_texts = None
        positions = {}
        for index, block in enumerate(blocks):
            if isinstance(block, dict) and block.get("id"):
                positions.setdefault(str(block["id"]), index)

    if mode == "lesson" and len(rungs) < MIN_RUNGS:
        errors.append(
            f"meta.ladder has {len(rungs)} rung(s); a lesson needs at least "
            f"{MIN_RUNGS}.\n"
            f"      Fewer than three is a claim with a preamble. If the subject "
            f"really is\n      that shallow, it is not a lesson: set "
            f'meta.mode to "argument".')

    # -- shape of each rung ------------------------------------------------
    landed = []
    for number, rung in enumerate(rungs, 1):
        where = f"ladder[{number - 1}]"
        if not isinstance(rung, dict):
            errors.append(f"{where} is not an object")
            continue
        says = rung_text(rung)
        if not says:
            errors.append(f"{where} has no `asks`: a rung is the question that "
                          f"section answers, in the reader's words")
        elif density.words(says) > RUNG_WORDS:
            errors.append(
                f"{where}: {density.words(says)} words, cap is {RUNG_WORDS}.\n"
                f'      "{says[:72]}…"\n'
                f"      → that is not a question a reader would ask, it is a "
                f"summary of the answer.\n         Ask the shorter question and "
                f"let the section do the answering.")

        for term in rung.get("introduces", []) or []:
            if density.words(term) > TERM_WORDS:
                errors.append(
                    f'{where}: "{term}" is {density.words(term)} words. A term '
                    f"is a name the reader\n      has to learn, not a "
                    f"description of one (cap {TERM_WORDS}).")

        at = rung.get("at")
        if not at:
            warnings.append(
                f"ladder-unlanded: {where} names no block (`at`). A rung with "
                f"nowhere to land is a note about intentions; the ladder can "
                f"only be checked against the page.")
            continue
        # A ladder is written at step 2.5, before a spec exists. With no blocks
        # to point at, an unresolvable `at` is not a fault, it is the normal
        # state of a ladder that has not been built yet. Failing here made the
        # step impossible to run at the moment it is supposed to be run.
        if not blocks:
            continue
        if str(at) not in positions:
            errors.append(
                f'{where}: `at` points at block id "{at}", which no block has.\n'
                f"      Give that block an `id`, or point the rung at the block "
                f"that really teaches it.")
            continue
        landed.append((number, rung, positions[str(at)]))

    if errors:
        return errors, warnings

    # -- the ladder is climbed in the order it is written ------------------
    for (n1, r1, p1), (n2, r2, p2) in zip(landed, landed[1:]):
        if p2 <= p1:
            errors.append(
                f"ladder-order: rung {n2} lands at blocks[{p2}] but rung {n1} "
                f'lands at blocks[{p1}].\n      "{rung_text(r1)[:56]}"\n'
                f'      "{rung_text(r2)[:56]}"\n'
                f"      → the ladder says one order and the page delivers "
                f"another. A reader\n         meets the page's order, not "
                f"yours. Move the blocks, or renumber the\n         rungs to "
                f"the order the reader will actually climb them.")

    # -- nothing appears before the rung that teaches it -------------------
    texts = _authored_texts if _authored_texts is not None else [
        visible_text(b, registry) if isinstance(b, dict) else "" for b in blocks]
    for number, rung, position in landed:
        for term in rung.get("introduces", []) or []:
            pattern = _term_pattern(term)
            early = [i for i in range(position)
                     if pattern.search(texts[i]) and not _titling(blocks[i])]
            if not early:
                if not any(pattern.search(t) for t in texts[position:]):
                    warnings.append(
                        f'ladder-unused: rung {number} introduces "{term}", '
                        f"which never appears on the page. The fix is on the "
                        f"page: use the word where it is taught. Deleting the "
                        f"term from the brief clears this warning and teaches "
                        f"the reader nothing.")
                continue
            first = early[0]
            warnings.append(
                f'forward-reference: "{term}" is used at blocks[{first}] '
                f"({blocks[first].get('type')}), but rung {number} teaches it "
                f"at blocks[{position}].\n"
                f'      "{_excerpt(texts[first], pattern)}"\n'
                f"      → the reader may meet the word before the picture that "
                f"gives it a meaning.\n         Move that rung earlier, or "
                f"draw the word where it first lands. Do NOT reword\n"
                f"         blocks[{first}] into something vaguer: if the term "
                f"is the name of the\n         subject, saying it early is "
                f"correct and this warning is closed.")

    return errors, warnings


# A hero, a section opener and a document title exist to name the subject. A
# forward reference inside one is not the insider register, it is a document
# saying what it is about, and charging for it buys a vaguer title every time.
_TITLING = {"hero", "section", "bridge"}


def _titling(block) -> bool:
    return isinstance(block, dict) and str(block.get("type", "")) in _TITLING


def _excerpt(text: str, pattern, width: int = 64) -> str:
    match = pattern.search(text)
    if not match:
        return text[:width]
    start = max(0, match.start() - width // 2)
    flat = re.sub(r"\s+", " ", text[start:start + width]).strip()
    return ("…" if start else "") + flat + "…"


def check(spec: dict, registry) -> list:
    """Warnings only, for a document that is not declared a lesson.

    A ladder on an `argument` document is a courtesy the author volunteered, so
    a fault in it is reported rather than fatal. In `lesson` mode the same fault
    stops the build, because there the ordering *is* the document.
    """
    errors, warnings = audit(spec, registry)
    mode = str((spec.get("meta") or {}).get("mode", "argument")).lower()
    if mode == "lesson":
        return warnings
    return warnings + [f"ladder: {e.splitlines()[0]}" for e in errors]


def enforce(spec: dict, registry) -> None:
    mode = str((spec.get("meta") or {}).get("mode", "argument")).lower()
    errors, _warnings = audit(spec, registry)
    if not errors or mode != "lesson":
        return
    lines = "\n".join(f"  {e}" for e in errors)
    raise SystemExit(
        f"[ladder] {len(errors)} fault(s) in the explanation order.\n\n{lines}\n\n"
        f"  A lesson is not a set of correct pictures in any order. It is the "
        f"one order\n  in which each idea can be understood using only the ones "
        f"before it.\n  See references/teaching.md."
    )


def summary(spec: dict) -> str:
    """The ladder as a reader climbs it, for `ig.py brief` and the handoff."""
    meta = spec.get("meta", {}) or {}
    rungs = meta.get("ladder") or []
    if not rungs:
        return "  (no ladder declared)"
    out = []
    for number, rung in enumerate(rungs, 1):
        if not isinstance(rung, dict):
            continue
        terms = ", ".join(rung.get("introduces", []) or [])
        out.append(f"  {number}. {rung_text(rung)}")
        if terms:
            out.append(f"     teaches: {terms}")
    return "\n".join(out)
