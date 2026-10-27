"""The register check: the one linter here that reads the words.

Every other check in this skill measures shape. `density.py` counts words,
`check_document.py` counts blocks, twins, hues and ink, `ladder.py` checks the
order terms arrive in. A document passes all of them while every sentence on it
is the generated-prose cadence: "not just X, but Y", "the detail that makes it
work: a separate agent grades it", "underscoring the team's commitment to
better workflows". `anti-patterns.md` says so in as many words, and said it
without a way to act on it: *all of them measure shape*.

This module is the shapes, as regular expressions. It is deliberately the LAST
thing that runs. Wired into the build it would become one more warning to be
cleared by deletion, which is the failure `Rewriting the copy to clear a
warning` already names. Run against a finished document it is the opposite: a
warning here is always closed by rewriting the sentence, because the sentence
is the only thing it measured.

    python3 scripts/ig.py copy out/doc.html

It is a linter, not a judge. Some of these words have a literal use (a climbing
`harness`, `robust` standard errors, an `intricate` mechanism you have drawn).
A warning you have read and rejected is closed business.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------- words --

# Banned outright. Not a taste list: these are the words that survive when a
# model writes to a word cap with nothing specific to say, so their presence is
# evidence that a sentence went abstract rather than short.
BANNED = (
    "delve", "foster", "leverage", "utilize", "utilise", "facilitate",
    "empower", "streamline", "robust", "cutting-edge", "paradigm shift",
    "game changer", "game-changer", "tapestry", "realm", "beacon",
    "multifaceted", "meticulous", "intricate", "paramount", "transformative",
    "elevate", "embark", "supercharge", "harness", "ever-evolving",
    "seamless", "seamlessly", "unlock", "unleash", "powerful", "effortless",
    "revolutionize", "revolutionise", "best-in-class", "world-class",
    "next-generation", "holistic", "synergy", "vibrant", "bespoke",
)

# Adverbs that are usually load-bearing in speech and never in a specimen label.
# On a page whose caps are 6 and 14 words, one of these is a word not spent on
# the subject.
EMPTY_ADVERBS = (
    "just", "literally", "honestly", "simply", "actually", "truly",
    "fundamentally", "importantly", "crucially", "inherently", "inevitably",
    "arguably", "essentially", "basically", "ultimately", "notably",
)

EMPTY_PHRASES = (
    "it's worth noting", "it is worth noting", "it's important to note",
    "it is important to note", "at the end of the day", "when it comes to",
    "at its core", "in today's world", "in the age of", "in the world of",
    "the reality is", "the truth is", "in terms of", "with regard to",
    "going forward", "in this article", "let's dive in", "needless to say",
    "that being said", "first and foremost",
)

# --------------------------------------------------------------------- shapes --

# (code, compiled pattern, what to do instead). The message is the fix, not the
# diagnosis: by the time this runs, naming the pattern is not useful on its own.
SHAPES = (
    ("binary-contrast",
     r"\bnot (?:just|only|merely)\b[^.;]{1,60}?\bbut\b"
     r"|\b(?:it'?s|it is|this is|that'?s) not\b[^.;]{1,60}[.;]\s*(?:it'?s|it is|this is)\b"
     r"|\bthe question is ?n'?t\b"
     r"|,\s+not\s+(?:a|an|the)?\s*\w+\s*$",
     "state the second half directly and drop the first"),

    ("colon-reveal",
     r"^[A-Z][^:.!?]{6,60}:\s+[a-z]",
     "a noun phrase, a colon and a lowercase reveal is manufactured drama; "
     "write it as a plain sentence, or keep the colon for a label or a list"),

    ("superficial-analysis",
     r",\s+(?:highlight|underscor|underlin|reflect|showcas|emphasi[sz]|"
     r"signal|demonstrat|illustrat)\w*\b",
     "a trailing -ing clause pretends to explain; replace it with the "
     "consequence for the reader"),

    ("importance-puffery",
     r"\bstands as a testament\b|\bis a testament to\b"
     r"|\bmarks a (?:pivotal|watershed|turning|defining)\b"
     r"|\bplays? a (?:vital|key|crucial|critical|pivotal|central) role\b"
     r"|\b(?:solidif|cement)\w+ its\b"
     r"|\bunderscores? (?:its|the) (?:significance|importance)\b",
     "state the fact and let the reader decide whether it matters"),

    ("weasel-attribution",
     r"\bexperts (?:agree|say)\b|\bstudies (?:show|suggest)\b"
     r"|\bresearch (?:shows|suggests)\b|\bindustry reports?\b"
     r"|\bmany (?:argue|believe|say)\b|\bsome (?:argue|say)\b"
     r"|\bwidely (?:regarded|considered|seen|believed)\b"
     r"|\bit is (?:widely )?believed\b",
     "name the source in `footnotes` or cut the claim; never invent one"),

    ("fake-strong-verb",
     r"\b(?:serves?|acts?) as (?:a|an|the)\b|\bhas the ability to\b"
     r"|\bis able to\b|\bmakes? a decision\b|\bprovides? the ability\b"
     r"|\bcentrali[sz]ed hub\b|\bone-stop\b",
     "use the direct verb: `serves as a hub for` is `tracks`, "
     "`has the ability to` is `can`"),

    ("metadiscourse",
     r"\bas you can see\b|\bthe key (?:point|takeaway) is\b"
     r"|\bthis (?:distinction|difference|point|part) matters\b"
     r"|\bin other words\b|(?:^|[.;]\s+)note that\b|\bkeep in mind\b"
     r"|\bmatters more than it (?:sounds|looks)\b",
     "telling the reader what to notice is the job of the picture; "
     "delete the aside or replace it with the fact it was pointing at"),

    ("rhetorical-setup",
     r"\bwhat if (?:I|we) told you\b|(?:^|[.!?]\s+)think about it\b|\bplot twist\b"
     r"|\bhere'?s (?:the thing|what|why)\b|\blet'?s be clear\b"
     r"|\bI'?ll be honest\b|\bthe uncomfortable truth\b"
     r"|\bwhat (?:most|many) people (?:get wrong|miss)\b"
     r"|\bnobody tells you\b|\bmost people (?:skip|miss|don'?t)\b",
     "the setup flatters the author; make the claim stand on its own"),

    ("recap-ending",
     r"^(?:In conclusion|Ultimately|Overall|To sum up|In summary|All in all)\b",
     "the reader was just there; end on the implication or the next action"),

    ("dramatic-fragment",
     r"\bthat'?s it\b|\bthat'?s the whole\b|\bfull stop\b"
     r"|(?:^|[.!?]\s+)period\.\s*$",
     "write the complete sentence"),

    ("slogan-cadence",
     r"^\s*[A-Z][\w'-]+ (?:is|are) (?:a|an|the) [\w'-]+, not (?:a|an|the) \b",
     "antithesis is the title register this skill forbids; name the subject, "
     "the scope and the period, and move the finding to the subtitle"),
)

_SHAPES = tuple((code, re.compile(pat, re.I | re.M), fix) for code, pat, fix in SHAPES)

# Vague stand-ins for the subject. Three or more distinct ones on a page is the
# tell for synonym cycling, which is invisible to `forward-reference`: it tracks
# a term, never the four different words a document renames it to afterwards.
STAND_INS = ("the system", "the tool", "the platform", "the service",
             "the solution", "the product", "the application", "the framework")

# --------------------------------------------------------------------- reading --

_NODE = re.compile(r"<[^>]+>|[^<]+")
_CLASS = re.compile(r'class="([^"]*)"')
_ENTITY = re.compile(r"&(?:[a-z]+|#\d+);")
_DETAILS = re.compile(r"<details\b.*?</details>", re.S | re.I)
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

# Where the words are scarce, and therefore where a wasted one is a decision.
TIGHT = ("title", "subtitle", "lede", "hero", "kicker", "label", "chip", "step")

# A label, a source line and a list all take a colon legitimately. Only a
# title, a lede or a line of prose can stage a reveal with one.
LOOSE = ("note", "footnote", "source", "legend", "axis", "table")


def text_runs(body: str) -> list:
    """Every visible string in the document, as (role, text) pairs.

    Node by node rather than as one blob, because `colon-reveal` is a claim
    about a whole title and `recap-ending` a claim about the start of one.
    Flattening the page first would lose both anchors.

    The role is the last class attribute seen, carried forward across tags that
    have none. It exists because half of these patterns are failures in only
    some fields: "Operator survey: the reply burden" is a broken title and
    "Reversed ordinal ramp: the earliest deposit holds the dark end" is a
    correctly written method note, and the two are the same string shape. A
    check that cannot tell them apart gets ignored, which is worse than absent.

    Table twins are dropped. They duplicate a graphic that has already been
    read, and their cells are values rather than sentences.
    """
    body = _DETAILS.sub(" ", body)
    runs = []
    role = ""
    for m in _NODE.finditer(body):
        chunk = m.group(0)
        if chunk.startswith("<"):
            found = _CLASS.search(chunk)
            if found:
                role = found.group(1)
            continue
        flat = re.sub(r"\s+", " ", _ENTITY.sub(" ", chunk)).strip()
        if len(flat) > 2 and re.search(r"[A-Za-z]", flat):
            runs.append((role, flat))
    return runs


def scan(runs: list) -> list:
    """Findings, as (level, code, quoted line, fix) tuples."""
    out = []

    def add(level, code, line, fix):
        out.append((level, code, line if len(line) <= 88 else line[:85] + "...", fix))

    joined = "  ".join(text for _, text in runs).lower()

    for role, run in runs:
        low = run.lower()

        for word in BANNED:
            if re.search(rf"\b{re.escape(word)}\b", low):
                add("warn", "banned-word", run,
                    f"`{word}` is marketing register; say what the thing does")
                break

        for phrase in EMPTY_PHRASES:
            if phrase in low:
                add("warn", "empty-phrase", run,
                    f"`{phrase}` delays the point; delete it")
                break

        # Only where the cap bites. In a footnote an adverb costs nothing and
        # "simply" may be the honest word; in a six-word label it is the word
        # that was not spent on the subject.
        # LOOSE wins: `ig-footnotes-title` contains "title" and is not a
        # capped field.
        if any(k in role for k in TIGHT) and not any(k in role for k in LOOSE):
            adverbs = [a for a in EMPTY_ADVERBS if re.search(rf"\b{a}\b", low)]
            if adverbs:
                add("note", "empty-adverb", run,
                    f"`{'`, `'.join(adverbs)}` in a capped field; cut unless it "
                    f"carries contrast or uncertainty")

        for code, pattern, fix in _SHAPES:
            if code == "colon-reveal" and any(k in role for k in LOOSE):
                continue
            if pattern.search(run):
                add("warn", code, run, fix)

        if "—" in run or "–" in run:
            add("warn", "em-dash", run,
                "a comma, a period or a colon says the same thing without the "
                "rhythm crutch")

        if _EMOJI.search(run):
            add("error", "emoji", run,
                "an icon is SVG, drawn in the page's own visual language, "
                "or absent")

    seen = [s for s in STAND_INS if s in joined]
    if len(seen) >= 3:
        add("warn", "synonym-cycling", ", ".join(seen),
            "the subject is being renamed; if the clear word is right, repeat "
            "it. `forward-reference` tracks the term, never its synonyms")

    return out


# The residue: what no regular expression can reach. Printed after the findings
# so that a clean scan does not read as a finished document, which is the exact
# mistake `linter clean is not a result` was written about.
JUDGEMENT = """\
  Then read the page yourself, once, for the four things no pattern can see:

  · SUBSTITUTION. Take every noun phrase. Could it be swapped for the
    equivalent thing at another company in another year and stay true? Run it
    on the title first.                             → specificity.md
  · ACTIVE VOICE. Every sentence has someone doing something. "The team
    shipped it Tuesday", never "the decision emerged". Nothing inanimate
    performs a human verb.
  · SHOW, DON'T TELL. No line labels a point important, surprising or subtle
    instead of demonstrating it. The picture is the demonstration; a caption
    saying the picture is interesting has replaced it with an opinion.
  · RHYTHM. Read three subtitles in a row out loud. If they share a shape,
    the cap has trained an aphorism and the third one is filler.

  A warning above that you have read and rejected is closed business. A page
  that scans clean is not finished; it is unmeasured.\
"""
