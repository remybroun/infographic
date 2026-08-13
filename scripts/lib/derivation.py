"""Did a regeneration re-derive anything, or edit the last one?

This module exists because of a measured failure. A document was regenerated
"from the top", with every reasoning step written down honestly, and it came out
with a 93% identical block sequence and an identical set of graphic forms. The
reasoning was real. It converged on the previous answer because the previous
answer was open in the author's context while they did it.

`scenes.md` names the weak form of this: open the catalog and the question
becomes "which of the 52 shapes is closest?" rather than "what does this look
like?". The strong form is that **once a prior document exists, it is the
catalog**, and it is a far tighter frame than the catalog ever was, because it
has already made every decision.

Nothing else in this skill can see that. The linter reads one finished document
and asks whether it is well made; it has no way to ask whether a different
document would have been better, because no different document is ever built.
So the comparison has to be explicit: a spec that supersedes another declares
it, and the build measures how much actually moved.

Only *graphic* blocks are compared. The editorial scaffolding (hero, section,
footnotes) recurs in every document ever written and carries no signal.
"""
from __future__ import annotations

import json
import os

# Fewer than a third of the graphic forms changed means the argument did not
# change; it was re-skinned. A warning rather than an error, because two
# genuinely similar arguments over the same facts are possible, and because the
# author is the only one who can say which happened.
SAME_ENOUGH = 0.70


def graphic_forms(spec: dict, registry) -> list:
    """The block types that carry the argument, in document order."""
    forms = []
    for block in spec.get("blocks", []):
        if not isinstance(block, dict) or block.get("skip"):
            continue
        key, entry = registry.resolve(block.get("type"))
        if entry and entry.get("graphic"):
            forms.append(key)
    return forms


def overlap(previous: list, current: list) -> float:
    """Multiset Jaccard over two lists of block types, 0.0 to 1.0.

    A multiset rather than a set on purpose: three `figure` blocks and one are
    different documents, and a set would call them identical.
    """
    if not previous and not current:
        return 0.0
    kinds = set(previous) | set(current)
    shared = sum(min(previous.count(k), current.count(k)) for k in kinds)
    total = sum(max(previous.count(k), current.count(k)) for k in kinds)
    return shared / total if total else 0.0


def resolve_supersedes(spec: dict, spec_path: str = None) -> str:
    """Absolute path to the superseded spec, or None."""
    named = (spec.get("meta") or {}).get("supersedes")
    if not named:
        return None
    if os.path.isabs(named):
        return named
    base = os.path.dirname(os.path.abspath(spec_path)) if spec_path else os.getcwd()
    return os.path.join(base, named)


def check(spec: dict, registry, spec_path: str = None) -> list:
    """Warnings about a regeneration that did not diverge from what it replaces."""
    path = resolve_supersedes(spec, spec_path)
    if not path:
        return []
    if not os.path.exists(path):
        return [f"meta.supersedes points at {path}, which does not exist; "
                f"the derivation check did not run"]
    try:
        with open(path, encoding="utf-8") as fh:
            previous = json.load(fh)
    except (OSError, ValueError) as exc:
        return [f"meta.supersedes could not be read ({exc}); "
                f"the derivation check did not run"]

    before, after = graphic_forms(previous, registry), graphic_forms(spec, registry)
    if not before:
        return []
    ratio = overlap(before, after)
    if ratio < SAME_ENOUGH:
        return []

    same = sorted({f for f in after if f in before})
    return [
        f"derivation: {ratio * 100:.0f}% of the graphic forms are unchanged from "
        f"{os.path.basename(path)} ({', '.join(same)}). "
        f"A re-derivation that lands on the same forms is an edit. Either say so, "
        f"or go back to the spines: the previous document was probably open while "
        f"you chose."
    ]
