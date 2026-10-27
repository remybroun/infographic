"""Checks on how a leading block is set up.

This module used to hold `leading-numbers`, the warning for a `kpi` row whose
figures a chart further down already explained. The `kpi` block was deleted:
a row of numbers drew nothing and passed as a graphic, so there is no row left
to check. What remains is the one check that was always unrelated to it.
"""
from __future__ import annotations


def inverted_without_ground(spec: dict) -> list:
    """`invert` paints no background of its own, so it needs a dark ground.

    `.ig-fig-invert` redefines the ink and surface tokens and nothing else. On a
    continuous page the dark field comes from `bleed`, which paints the section.
    Set `invert` without it and the kit draws light ink on a light page: the
    labels, rules and hairline shapes vanish and only the accent-filled marks
    survive, which looks like a half-finished drawing rather than a broken one.

    Caught by looking at a rendered README slide where six family headings had
    simply disappeared. The linter's `near-empty-page` also fired at 4% ink,
    which is the same fact measured from the other side.
    """
    out = []
    for index, block in enumerate(spec.get("blocks", [])):
        if not isinstance(block, dict) or block.get("skip"):
            continue
        if block.get("invert") and not block.get("bleed"):
            out.append(
                f"figure-invert: blocks[{index}] sets invert without bleed. "
                f"invert only flips the ink tokens; the dark ground comes from "
                f"bleed, so on a light page this draws light-on-light and the "
                f"labels disappear. Add bleed (continuous targets only), or drop "
                f"invert."
            )
    return out
